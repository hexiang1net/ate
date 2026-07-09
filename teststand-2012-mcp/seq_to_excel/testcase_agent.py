"""Test case generation agent.

Orchestrates parsing of TestStand sequence files and Excel generation.
"""
from typing import List, Dict, Optional, Set
from pathlib import Path

import win32com.client

from ...engine.teststand_engine import TestStandEngine
from ...converter.variant_value_converter import VariantValueConverter
from ...service.sequence_service import SequenceService
from ...service.step_service import StepService
from ...service.parameter_service import ParameterService
from ...engine.constants import STEP_GROUP_API, STEP_GROUP_NAMES
from .testcase_model import TestCase, TestCaseReport, ViParameter
from .excel_generator import ExcelGenerator


class TestCaseAgent:
    """Agent that generates ATE test case Excel reports from sequence files."""

    # Settings property names to extract
    SETTINGS_EXPR_PROPS = ["PreExpr", "PostExpr", "CustExpr"]
    SETTINGS_LOOP_PROPS = ["LoopType", "LoopWhile", "LoopCount", "LoopInitialize"]
    SETTINGS_CONDITIONAL_PROPS = ["Condition", "TargetLabel", "SeqCallName", "ConditionExpr"]
    SETTINGS_SKIP_VALUES = ["NoLooping", "Normal"]

    # ResultOption enum mapping
    RESULT_OPTION_MAP = {
        0: "Default",
        1: "LogAlways",
        2: "LogIfFail",
        3: "LogNever"
    }

    def __init__(self):
        self.engine = None
        self.value_converter = None
        self.sequence_service = None
        self.step_service = None
        self.parameter_service = None
        self.excel_generator = ExcelGenerator()
        self._step_counter: Dict[str, int] = {}
        self._sub_step_counter: Dict[str, int] = {}  # For sub-sequence steps
        self._vi_enum_cache: Dict[str, Dict[str, List[str]]] = {}  # vi_path -> {param_name -> enum_values}
        self._visiting: Set[str] = set()  # sequence names currently being expanded (cycle detection)

    def generate_report(self, seq_file_path: str, output_xlsx: str) -> TestCaseReport:
        """Generate test case report from sequence file.

        Args:
            seq_file_path: Path to .seq file
            output_xlsx: Output Excel file path

        Returns:
            TestCaseReport with all extracted test cases
        """
        self._init_services()
        self._reset_counters()

        report = TestCaseReport(file_path=seq_file_path)

        with self.engine:
            self.engine.open_file(seq_file_path)

            num_sequences = self.sequence_service.get_num_sequences()
            if num_sequences == 0:
                return report

            sequences = self.sequence_service.get_all_sequences()
            if sequences:
                report.sequence_name = sequences[0].name

            # Process main sequence (sequence 0) with sub-sequence expansion
            self._process_main_sequence(report)

            # Extract all variables
            self._extract_variables(report)

        self.excel_generator.generate(report, output_xlsx)
        return report

    def _init_services(self):
        """Initialize engine and services."""
        self.engine = TestStandEngine()
        self.value_converter = VariantValueConverter()
        self.sequence_service = SequenceService(self.engine)
        self.step_service = StepService(self.engine, self.value_converter)
        self.parameter_service = ParameterService(self.engine, self.value_converter)

    def _reset_counters(self):
        """Reset step counters."""
        self._step_counter = {"startup": 0, "main": 0, "cleanup": 0}
        self._sub_step_counter = {}  # {parent_step_key: counter}
        self._vi_enum_cache = {}  # {vi_path -> {param_name -> enum_values}}

    def _extract_variables(self, report):
        """Extract all variables from the sequence file.

        Extracts: FileGlobals, Locals (per sequence), Parameters (per sequence).
        RunState is only available during execution and cannot be read from file.
        """
        # 1. FileGlobals
        try:
            fg = self.engine.sequence_file.FileGlobalsDefaultValues
            self._enumerate_properties(fg, "", "FileGlobals", report)
            del fg
        except Exception:
            pass

        # 2. Locals for each sequence
        try:
            num_seqs = self.engine.sequence_file.NumSequences
            for seq_idx in range(num_seqs):
                seq = self.engine.sequence_file.GetSequence(seq_idx)
                seq_name = seq.Name
                try:
                    locals_obj = seq.Locals
                    self._enumerate_properties(locals_obj, "", f"Locals.{seq_name}", report)
                    del locals_obj
                except Exception:
                    pass
                del seq
        except Exception:
            pass

    # PropertyValueTypes constants
    _VALTYPE_CONTAINER = 0
    _VALTYPE_STRING = 1
    _VALTYPE_BOOLEAN = 2
    _VALTYPE_NUMBER = 3
    _VALTYPE_REFERENCE = 5
    _VALTYPE_ARRAY = 6

    def _enumerate_properties(self, prop_obj, prefix, container_name, report, depth=0):
        """Recursively enumerate properties with proper type detection."""
        from .testcase_model import VariableInfo
        if depth > 5:
            return
        try:
            num_props = prop_obj.GetNumSubProperties(prefix)
            for i in range(num_props):
                try:
                    var_name = prop_obj.GetNthSubPropertyName(prefix, i, 0)
                    if not var_name:
                        continue
                    full_path = f"{prefix}.{var_name}" if prefix else var_name

                    # Get sub-property object for type inspection
                    sub_prop = prop_obj.GetNthSubProperty(prefix, i, 0)
                    val_type = sub_prop.Type.ValueType
                    type_name = sub_prop.Type.TypeName

                    val = ""
                    var_type = ""

                    if val_type == self._VALTYPE_CONTAINER:
                        # Recurse into containers, don't add container itself as a row
                        self._enumerate_properties(prop_obj, full_path, container_name, report, depth + 1)
                        del sub_prop
                        continue
                    elif val_type == self._VALTYPE_STRING:
                        var_type = "String"
                        try:
                            val = sub_prop.GetValString("", 0)
                        except Exception:
                            val = ""
                    elif val_type == self._VALTYPE_NUMBER:
                        var_type = type_name or "Number"
                        try:
                            val = str(sub_prop.GetValNumber("", 0))
                        except Exception:
                            try:
                                val = sub_prop.GetFormattedValue("", 0)
                            except Exception:
                                val = ""
                    elif val_type == self._VALTYPE_BOOLEAN:
                        var_type = "Boolean"
                        try:
                            val = str(sub_prop.GetValBoolean("", 0))
                        except Exception:
                            val = ""
                    elif val_type == self._VALTYPE_ARRAY:
                        var_type = type_name or "Array"
                        try:
                            val = sub_prop.GetFormattedValue("", 0)
                        except Exception:
                            val = ""
                    elif val_type == self._VALTYPE_REFERENCE:
                        var_type = type_name or "Reference"
                        try:
                            val = sub_prop.GetFormattedValue("", 0)
                        except Exception:
                            val = ""
                    else:
                        var_type = type_name or f"Unknown({val_type})"
                        try:
                            val = sub_prop.GetFormattedValue("", 0)
                        except Exception:
                            val = ""

                    report.variables.append(VariableInfo(
                        name=full_path, value=val, type=var_type, container=container_name
                    ))

                    del sub_prop
                except Exception:
                    continue
        except Exception:
            pass

    def _process_main_sequence(self, report: TestCaseReport):
        """Process main sequence (sequence 0) with sub-sequence expansion."""
        sequence = None
        try:
            sequence = self.engine.sequence_file.GetSequence(0)
            seq_name = sequence.Name

            # Process in order: Main (2_x) -> Setup (1_x) -> Cleanup (3_x)
            # User idx: 0=Main, 1=Setup, 2=Cleanup
            # API idx:   0=Setup, 1=Main, 2=Cleanup
            for user_group_idx in [1, 0, 2]:  # Main, Setup, Cleanup order
                api_group = STEP_GROUP_API[user_group_idx]
                group_name = STEP_GROUP_NAMES[user_group_idx]  # "Main", "Setup", "Cleanup"

                num_steps = sequence.GetNumSteps(api_group)
                for step_idx in range(num_steps):
                    step = None
                    try:
                        step = sequence.GetStep(step_idx, api_group)

                        # Check if this is a SequenceCall
                        step_type_name = self._get_step_type_name(step)

                        if step_type_name == "SequenceCall" and group_name == "Main":
                            # First add the SequenceCall step itself
                            tc = self._create_test_case(
                                step, 0, user_group_idx, step_idx, seq_name, group_name
                            )
                            if tc:
                                report.test_cases.append(tc)
                            # Then expand sub-sequence
                            self._process_sequence_call(step, report, group_name)
                        else:
                            # Normal step or non-Main SequenceCall
                            tc = self._create_test_case(
                                step, 0, user_group_idx, step_idx, seq_name, group_name
                            )
                            if tc:
                                report.test_cases.append(tc)

                    except Exception:
                        pass
                    finally:
                        if step is not None:
                            try:
                                step.UnloadModules()
                            except Exception:
                                pass
                            del step
        except Exception:
            pass
        finally:
            if sequence is not None:
                del sequence

    def _process_sequence_call(self, step, report: TestCaseReport, parent_group_name: str):
        """Process a SequenceCall step, expanding the called sub-sequence."""
        import re

        called_seq_idx = -1
        called_seq_name = ""

        # First try: read sequence name from TS.SData.SeqName
        try:
            prop = step.AsPropertyObject()
            ts = prop.GetPropertyObject("TS", 0)
            sdata = ts.GetPropertyObject("SData", 0)
            called_seq_name = sdata.GetValString("SeqName", 0)
        except Exception:
            called_seq_name = ""

        # Cycle detection: refuse to expand a sequence we are already inside.
        # Without this, a self-calling step (or any mutual recursion between
        # sequences) would recurse until Python hit its recursion limit.
        if called_seq_name and called_seq_name in self._visiting:
            tc = self._create_test_case(step, 0, 1, 0, "Main", "Main")
            if tc:
                report.test_cases.append(tc)
            return

        # Find sequence index by name
        if called_seq_name:
            try:
                num_sequences = self.engine.sequence_file.NumSequences
                for i in range(num_sequences):
                    seq = self.engine.sequence_file.GetSequence(i)
                    if seq.Name == called_seq_name:
                        called_seq_idx = i
                        break
                    del seq
            except Exception:
                pass

        # Fallback: match by normalized step name if SeqName didn't work
        if called_seq_idx < 0:
            step_name = step.Name or ""
            step_norm = self._normalize_step_name(step_name)
            try:
                num_sequences = self.engine.sequence_file.NumSequences
                for i in range(num_sequences):
                    seq = self.engine.sequence_file.GetSequence(i)
                    seq_norm = self._normalize_step_name(seq.Name)
                    if step_norm == seq_norm:
                        called_seq_idx = i
                        called_seq_name = seq.Name
                        break
                    del seq
            except Exception:
                pass

        # Get current step number as parent reference (e.g., "2_4")
        parent_step_key = self._get_current_step_key()
        self._sub_step_counter[parent_step_key] = 0

        if called_seq_idx < 0:
            # Sequence not found, treat as normal step
            tc = self._create_test_case(step, 0, 1, 0, "Main", "Main")
            if tc:
                report.test_cases.append(tc)
            return

        # Process sub-sequence in order: Setup (1_x) -> Main (2_x) -> Cleanup (3_x)
        sub_sequence = None
        try:
            sub_sequence = self.engine.sequence_file.GetSequence(called_seq_idx)
            sub_seq_name = sub_sequence.Name
            # Mark this sequence as in-progress so a step that calls back into it
            # (directly or transitively) is treated as a leaf instead of recursing.
            self._visiting.add(sub_seq_name)

            for user_group_idx in [1, 0, 2]:  # Main, Setup, Cleanup order
                api_group = STEP_GROUP_API[user_group_idx]
                group_name = STEP_GROUP_NAMES[user_group_idx]

                num_steps = sub_sequence.GetNumSteps(api_group)
                for step_idx in range(num_steps):
                    sub_step = None
                    try:
                        sub_step = sub_sequence.GetStep(step_idx, api_group)
                        tc = self._create_test_case(
                            sub_step, called_seq_idx, user_group_idx,
                            step_idx, sub_seq_name, group_name,
                            parent_step_key=parent_step_key
                        )
                        if tc:
                            report.test_cases.append(tc)
                    except Exception:
                        pass
                    finally:
                        if sub_step is not None:
                            try:
                                sub_step.UnloadModules()
                            except Exception:
                                pass
                            del sub_step
        except Exception:
            pass
        finally:
            if 'sub_seq_name' in locals():
                self._visiting.discard(sub_seq_name)
            if sub_sequence is not None:
                del sub_sequence

    def _get_current_step_key(self) -> str:
        """Get current step key for sub-sequence numbering."""
        main_count = self._step_counter.get("main", 0)
        return f"2_{main_count}"

    @staticmethod
    def _normalize_step_name(name: str) -> str:
        """Normalize step/sequence name for matching."""
        import re
        s = name.lower()
        s = re.sub(r'\s+', ' ', s)  # normalize whitespace
        s = re.sub(r'\s*\([^)]*\)\s*', ' ', s)  # remove parenthetical text
        s = s.strip()  # strip before testing for trailing words
        s = re.sub(r'\s+test\s+step$', '', s)  # remove 'test step' at end
        s = re.sub(r'\s+step$', '', s)  # remove trailing 'step'
        s = re.sub(r'\s+test$', '', s)  # remove trailing 'test'
        s = s.strip()
        return s

    def _get_step_type_name(self, step) -> str:
        """Get step type name."""
        try:
            step_type = step.StepType
            if step_type:
                return step_type.Name
        except Exception:
            pass
        return ""

    def _get_activex_call_info(self, step) -> dict:
        """Get ActiveX/COM call info from step.

        For Automation Adapter steps, retrieves the server name and member name
        from TS.SData.Call properties when VIPath is not available.
        """
        try:
            prop_obj = step.AsPropertyObject()
            if prop_obj is None:
                return {}

            ts = prop_obj.GetPropertyObject("TS", 0)
            if ts is None:
                return {}

            sdata = ts.GetPropertyObject("SData", 0)
            if sdata is None:
                return {}

            call = sdata.GetPropertyObject("Call", 0)
            if call is None:
                return {}

            info = {}

            # Get server name
            try:
                server_name = call.GetValString("ServerName", 0)
                if server_name:
                    info["server"] = server_name
            except Exception:
                pass

            # Get member name
            try:
                member_name = call.GetValString("MemberName", 0)
                if member_name:
                    info["member"] = member_name
            except Exception:
                pass

            del call
            del sdata
            del ts
            del prop_obj

            return info if info else {}
        except Exception:
            return {}

    def _create_test_case(self, step, seq_idx: int, user_group_idx: int,
                          step_idx: int, seq_name: str, group_name: str,
                          parent_step_key: str = None) -> Optional[TestCase]:
        """Create TestCase from a step."""
        tc = TestCase()

        # Normalize group name: "Setup" -> "startup"
        group_key = group_name.lower()
        if group_key == "setup":
            group_key = "startup"

        # Get step type name
        step_type_name = self._get_step_type_name(step)
        tc.step_type = step_type_name
        tc.step = group_key

        # Generate step number
        if parent_step_key:
            # Sub-sequence step: parent_step_key + sub_step_counter
            self._sub_step_counter[parent_step_key] = self._sub_step_counter.get(parent_step_key, 0) + 1
            step_code = f"{parent_step_key}_{self._sub_step_counter[parent_step_key]}"
        else:
            step_code = self._generate_step_no(group_key, step_idx)

        # Get step name and description
        try:
            tc.test_project = step.Name or ""
        except Exception:
            tc.test_project = ""

        try:
            tc.comments = step.Comment or ""  # Map to Description column in Excel
        except Exception:
            tc.comments = ""

        # Get adapter
        try:
            tc.adapter = step.AdapterKeyName or ""
        except Exception:
            tc.adapter = ""

        # Get VI path
        module = None
        module_acquired = False
        try:
            module = step.Module
            module_acquired = True
            if module is not None:
                try:
                    tc.vi_path = module.VIPath or ""
                except Exception:
                    tc.vi_path = module.Path or ""

                if tc.vi_path:
                    tc.instrument_vi = Path(tc.vi_path).name
        except Exception:
            pass
        finally:
            if module is not None:
                try:
                    module.Unload()
                except Exception:
                    pass
                del module

        # For ActiveX/COM adapter, try to get server and member info if vi_path is empty
        if not tc.vi_path and tc.adapter == "Automation Adapter":
            call_info = self._get_activex_call_info(step)
            if call_info:
                tc.vi_path = f"{call_info['server']}.{call_info['member']}"
                tc.instrument_vi = f"{call_info['server']}.{call_info['member']}"

        # Get module parameters
        tc.module_parameters = self._get_module_parameters(step)

        # If VI has cached enum values, add them to module_parameters
        if tc.vi_path and tc.vi_path in self._vi_enum_cache:
            param_enums = self._vi_enum_cache[tc.vi_path]
            for mp in tc.module_parameters:
                if mp.name in param_enums:
                    mp.enum_values = param_enums[mp.name]
        # Otherwise, try to fetch enum values for LabVIEW VIs
        elif tc.vi_path and tc.instrument_vi and ".vi" in tc.instrument_vi.lower():
            self._fetch_vi_enum_values(tc.vi_path, tc.module_parameters)

        # Extract test limits and settings
        self._extract_test_limits(tc, step)
        self._extract_step_settings(tc, step)

        tc.step_no = step_code

        return tc

    def _generate_step_no(self, group: str, step_idx: int) -> str:
        """Generate step number in format 'prefix_counter'."""
        self._step_counter[group] += 1
        group_prefix_map = {"startup": "1", "main": "2", "cleanup": "3"}
        prefix = group_prefix_map.get(group, "2")
        return f"{prefix}_{self._step_counter[group]}"

    def _fetch_vi_enum_values(self, vi_path: str, module_parameters: list, seq_file_path: str = None) -> None:
        """Fetch enum values for a VI and cache them.

        Uses ParseViParamsCommand to get parameter enum values via TestStand Engine.
        Results are cached in _vi_enum_cache to avoid repeated VI parsing.

        If vi_path is a relative path or contains encoding issues, tries to find
        the full VI path by searching near the sequence file.
        """
        if vi_path in self._vi_enum_cache:
            # Add cached enum values to module_parameters
            param_enums = self._vi_enum_cache[vi_path]
            for mp in module_parameters:
                if mp.name in param_enums:
                    mp.enum_values = param_enums[mp.name]
            return

        # Use engine's current file path if not provided
        if seq_file_path is None and self.engine:
            seq_file_path = getattr(self.engine, 'current_file_path', None)

        full_vi_path = self._resolve_vi_path(vi_path, seq_file_path)
        if not full_vi_path:
            return

        try:
            from ...command.commands.parse_vi_params_command import ParseViParamsCommand
            cmd = ParseViParamsCommand(self.engine)
            result = cmd._parse_vi_parameters(full_vi_path)

            if "error" in result:
                return

            # Build param_name -> enum_values mapping
            param_enums = {}
            for param in result.get("parameters", []):
                if param.get("enum_values"):
                    param_enums[param["name"]] = param["enum_values"]

            if param_enums:
                self._vi_enum_cache[vi_path] = param_enums

                # Update module_parameters with enum values
                for mp in module_parameters:
                    if mp.name in param_enums:
                        mp.enum_values = param_enums[mp.name]
        except Exception:
            pass

    def _resolve_vi_path(self, vi_path: str, seq_file_path: str = None) -> str:
        """Resolve VI path from possibly relative/encoded path.

        Tries to find the full path by searching near the sequence file location.
        Limits search depth to prevent long searches.
        """
        import os

        if not vi_path:
            return None

        # If it looks like a full path and exists, use it
        if os.path.exists(vi_path):
            return vi_path

        # Extract just the filename from vi_path (handles encoding issues)
        vi_filename = None
        if ".vi" in vi_path.lower():
            # Try to find VI filename from the path (last component after \\)
            parts = vi_path.replace("/", os.sep).split(os.sep)
            for part in reversed(parts):
                if ".vi" in part.lower():
                    vi_filename = part
                    break

        if not vi_filename:
            return None

        # Use seq_file_path's directory as search base
        search_base = None
        if seq_file_path:
            search_base = os.path.dirname(seq_file_path)
        elif self.engine and hasattr(self.engine, 'current_file_path'):
            search_base = os.path.dirname(self.engine.current_file_path or '')

        if not search_base:
            return None

        # Limit search depth: only check within 3 levels of sequence file
        max_depth = 3
        found = self._search_for_vi(search_base, vi_filename, max_depth)
        return found

    def _search_for_vi(self, base_dir: str, vi_filename: str, max_depth: int, current_depth: int = 0) -> str:
        """Recursively search for VI file with depth limit."""
        import os

        if current_depth > max_depth:
            return None

        if not os.path.isdir(base_dir):
            return None

        # Check current directory
        try:
            files = os.listdir(base_dir)
            if vi_filename in files:
                return os.path.join(base_dir, vi_filename)
        except PermissionError:
            return None

        # Recursively search all subdirectories
        try:
            dirs = os.listdir(base_dir)
            for d in dirs:
                subdir = os.path.join(base_dir, d)
                if os.path.isdir(subdir):
                    result = self._search_for_vi(subdir, vi_filename, max_depth, current_depth + 1)
                    if result:
                        return result
        except PermissionError:
            pass

        return None

    def _get_module_parameters(self, step):
        """Get module parameters from step using service layer.

        Uses ParameterService with expand_clusters=True to handle cluster types
        by recursively expanding sub-elements with dot notation.
        For example: Limit {Low, High} -> "Limit.Low", "Limit.High"

        For ActiveX/COM adapter steps, also reads values from Call.Parameters
        since module.Parameters returns empty values for COM method params.
        """
        try:
            params = self.parameter_service.get_module_parameters_with_fallback(step, expand_clusters=True)

            # For ActiveX/COM steps, module.Parameters may return empty values
            # Read actual values from TS.SData.Call.Parameters
            if params and self._is_activex_step(step):
                self._enrich_activex_params(step, params)

            return params
        except Exception:
            # Fallback to empty list on error
            return []

    def _is_activex_step(self, step) -> bool:
        """Check if step uses Automation Adapter."""
        try:
            return step.AdapterKeyName == "Automation Adapter"
        except Exception:
            return False

    def _enrich_activex_params(self, step, params) -> None:
        """Enrich ActiveX/COM parameters with values from ActiveXModule.Parameters API.

        Uses the proper TestStand API: step.Module → dynamic Dispatch → ActiveXModule.Parameters.
        Falls back to TS.SData.Call.Parameters if the API approach fails.
        """
        # Try ActiveXModule.Parameters API first
        value_map = self._get_activex_params_via_module(step)
        if not value_map:
            # Fallback: read from Call.Parameters
            value_map = self._get_activex_params_via_call(step)

        if value_map:
            for p in params:
                if not p.value_expr and p.name in value_map:
                    p.value_expr = value_map[p.name]

    def _get_activex_params_via_module(self, step) -> dict:
        """Get ActiveX parameters via ActiveXModule.Parameters API.

        Uses dynamic Dispatch on step.Module to access ActiveXModule interface,
        then reads ActiveXParameter.ParameterName and ActiveXParameter.ValueExpr.
        """
        try:
            module = step.Module
            if module is None:
                return {}
            mod_dyn = win32com.client.dynamic.Dispatch(module._oleobj_)
            mod_dyn.LoadPrototype(0)
            params = mod_dyn.Parameters
            if not params or params.Count == 0:
                del module
                return {}
            value_map = {}
            for i in range(params.Count):
                try:
                    item = params.Item(i)
                    item_dyn = win32com.client.dynamic.Dispatch(item._oleobj_)
                    name = item_dyn.ParameterName or ""
                    val = item_dyn.ValueExpr or ""
                    if name:
                        value_map[name] = val
                except Exception:
                    pass
            del module
            return value_map
        except Exception:
            return {}

    def _get_activex_params_via_call(self, step) -> dict:
        """Fallback: get ActiveX parameter values from TS.SData.Call.Parameters."""
        prop_obj = None
        try:
            prop_obj = step.AsPropertyObject()
            if prop_obj is None:
                return {}
            ts = prop_obj.GetPropertyObject("TS", 0)
            if not ts:
                return {}
            sdata = ts.GetPropertyObject("SData", 0)
            if not sdata:
                del ts
                return {}
            call = sdata.GetPropertyObject("Call", 0)
            if not call:
                del sdata
                del ts
                return {}
            call_params = call.GetPropertyObject("Parameters", 0)
            value_map = {}
            if call_params:
                count = call_params.GetNumElements()
                for i in range(count):
                    try:
                        elem = call_params.GetPropertyObject(f"[{i}]", 0)
                        if elem:
                            name = elem.GetValString("Name", 0) or ""
                            val = elem.GetValString("ArgVal", 0) or ""
                            if name:
                                value_map[name] = val
                            del elem
                    except Exception:
                        pass
                del call_params
            del call
            del sdata
            del ts
            return value_map
        except Exception:
            return {}
        finally:
            if prop_obj is not None:
                del prop_obj

    def _extract_cluster_params(self, param_obj, prefix):
        """Recursively extract cluster parameters.

        For cluster types, expands sub-elements like:
        - Cluster/Limit {Low, High} -> "Limit.Low", "Limit.High"

        Returns list of ModuleParameterInfo if cluster, empty list if not a cluster.
        """
        from ...model.module_parameter_info import ModuleParameterInfo

        try:
            # Check if this parameter is a cluster by trying to get sub-properties
            prop_obj = param_obj.GetValAsPropertyObject()
            if prop_obj is None:
                return []

            num_sub = prop_obj.GetNumSubProperties("")
            if num_sub == 0:
                del prop_obj
                return []

            # It's a cluster - recursively extract sub-elements
            cluster_params = []
            for i in range(num_sub):
                try:
                    sub_name = prop_obj.GetNthSubPropertyName("", i, 0)
                    sub_prop = prop_obj.GetNthSubProperty("", i, 0)

                    full_name = f"{prefix}.{sub_name}" if prefix else sub_name

                    # Try to get value from sub-property
                    sub_val = ""
                    try:
                        sub_val = sub_prop.GetValString("ValueExpr", 0)
                    except:
                        pass
                    if not sub_val:
                        try:
                            sub_val = sub_prop.GetValString("Val", 0)
                        except:
                            pass

                    # Try to get direction
                    sub_dir = "0"
                    try:
                        sub_dir = str(int(sub_prop.GetValInteger64("Direction", 0)))
                    except:
                        pass

                    # Recursively check for nested clusters
                    nested_params = self._extract_cluster_params(sub_prop, full_name)
                    if nested_params:
                        cluster_params.extend(nested_params)
                    else:
                        param_info = ModuleParameterInfo()
                        param_info.name = full_name
                        param_info.direction = sub_dir
                        param_info.value_expr = sub_val
                        cluster_params.append(param_info)

                    del sub_prop
                except Exception:
                    pass

            del prop_obj
            return cluster_params

        except Exception:
            return []

    def _get_params_from_property_object(self, step):
        """Fallback: read parameters via PropertyObject when VI cannot be loaded."""
        params = []

        try:
            prop_obj = step.AsPropertyObject()
            if prop_obj is None:
                return params

            # Try to find ViCall or Call sub-property for VI parameters
            vi_call = None
            try:
                vi_call = prop_obj.GetPropertyObject("ViCall", 0)
            except Exception:
                pass

            if vi_call is None:
                try:
                    vi_call = prop_obj.GetPropertyObject("Call", 0)
                except Exception:
                    pass

            container = vi_call if vi_call else prop_obj

            # Try to read from Parms
            try:
                parms_array = container.GetPropertyObject("Parms", 0)
                if parms_array:
                    params = self._read_parms_from_property_object(parms_array)
                    del parms_array
                    if params:
                        return params
            except Exception:
                pass

            # Read sub-properties as parameters
            num_props = container.GetNumSubProperties("")
            for i in range(num_props):
                try:
                    prop_name = container.GetNthSubPropertyName("", i, 0)

                    # Skip meta properties
                    if prop_name.startswith("__") or prop_name.startswith("Type"):
                        continue
                    if prop_name in ["Id", "Icon", "SData", "PreCond", "LoadOpt", "UnloadOpt",
                                     "Mode", "WindowActivation", "ResultOption", "StepFCSeqF",
                                     "IgnoreRTE", "UseMutex", "MutexNameOrRef", "BatchSyncOpt",
                                     "SwitchEnabled", "VirtualDeviceName", "SwitchOperation",
                                     "RouteGroupConnect", "RouteGroupDisconnect", "MulticonnectMode",
                                     "OperationOrder", "ConnectionLifetime", "WaitForDebounce",
                                     "PassAct", "FailAct", "PassActTarget", "FailActTarget",
                                     "CustExpr", "CustTrueAct", "CustFalseAct", "CustTrueActTarget",
                                     "CustFalseActTarget", "LoopType", "LoopWhile", "LoopStatus",
                                     "LoopIncrement", "LoopInitialize", "LoopOpt", "PreExpr",
                                     "PostExpr", "StatusExpr", "CanSpecifyModule", "CanEditCode",
                                     "CanEditModulePrototype", "CanEditParameterAdditionalResults",
                                     "PrecondIntExe", "Requirements", "CustomResults",
                                     "AdditionalResultsHints"]:
                        continue

                    sub_prop = container.GetNthSubProperty("", i, 0)
                    if sub_prop is None:
                        continue

                    from ...model.module_parameter_info import ModuleParameterInfo
                    param_info = ModuleParameterInfo()
                    param_info.name = prop_name

                    try:
                        param_info.value_expr = sub_prop.GetValString("ValueExpr", 0)
                    except Exception:
                        param_info.value_expr = ""

                    try:
                        param_info.default_value = sub_prop.GetValString("DefaultValue", 0)
                    except Exception:
                        param_info.default_value = ""

                    try:
                        param_info.direction = str(int(sub_prop.GetValInteger64("Direction", 0)))
                    except Exception:
                        param_info.direction = "0"

                    params.append(param_info)
                    del sub_prop

                except Exception:
                    pass

            if vi_call:
                del vi_call

        except Exception:
            pass

        return params

    def _read_parms_from_property_object(self, parms_obj):
        """Read parameters from Parms array."""
        params = []

        try:
            num_elements = parms_obj.GetNumElements()
            for i in range(num_elements):
                try:
                    elem = parms_obj.GetPropertyObject(f"Parms[{i}]", 0)
                    if elem is None:
                        continue

                    from ...model.module_parameter_info import ModuleParameterInfo
                    param_info = ModuleParameterInfo()

                    try:
                        param_info.name = elem.GetValString("Label", 0)
                    except Exception:
                        param_info.name = f"Param{i}"

                    try:
                        caption = elem.GetValString("Caption", 0)
                        if caption:
                            param_info.name = f"{param_info.name} ({caption})"
                    except Exception:
                        pass

                    try:
                        param_info.value_expr = elem.GetValString("ArgVal", 0)
                    except Exception:
                        param_info.value_expr = ""

                    try:
                        param_info.direction = str(int(elem.GetValNumber("Direction", 0)))
                    except Exception:
                        param_info.direction = "0"

                    params.append(param_info)
                    del elem

                except Exception:
                    pass

        except Exception:
            pass

        return params

    def _format_limit_value(self, value: str, fmt_val: str) -> str:
        """Format a limit value according to NumericFormat (printf syntax).

        Supported format specifiers:
          %f, %.Nf  -> float with N decimal places (default 6)
          %d, %u, %i -> integer
          %#x, %x   -> hexadecimal (with 0x prefix for %#x)
          %o        -> octal
          %b        -> binary
          %e, %E    -> scientific notation
          %g, %G    -> shortest of %f/%e
        """
        import re as _re
        if not value:
            return value
        try:
            num = float(value)
        except (ValueError, TypeError):
            return value

        if not fmt_val:
            # No format - use integer if no fractional part, else keep as-is
            return str(int(num)) if num == int(num) else str(num)

        # Parse printf format: %[flags][width][.precision][length]specifier
        m = _re.match(r'^%([#0\- +]*?)(\*|\d+)?(?:\.(\*|\d+))?(hh|h|l|ll|j|z|t|L)?([diuoxXfFeEgGaAcspn%b])$', fmt_val)
        if not m:
            return value

        flags, width, precision, length, specifier = m.groups()

        try:
            if specifier in ('f', 'F'):
                p = int(precision) if precision else 6
                return f"{num:.{p}f}"
            elif specifier in ('e', 'E'):
                p = int(precision) if precision else 6
                return f"{num:.{p}{specifier}}"
            elif specifier in ('g', 'G'):
                p = int(precision) if precision else 6
                return f"{num:.{p}{specifier}}"
            elif specifier in ('d', 'i', 'u'):
                return str(int(num))
            elif specifier in ('x', 'X'):
                h = int(num)
                if '#' in (flags or ''):
                    return f"0x{h:x}" if specifier == 'x' else f"0X{h:X}"
                return f"{h:{specifier}}"
            elif specifier == 'o':
                h = int(num)
                if '#' in (flags or ''):
                    return f"0o{oct(h)[2:]}"
                return oct(h)[2:]
            elif specifier == 'b':
                return bin(int(num))[2:]
            else:
                return value
        except (ValueError, OverflowError):
            return value

    def _extract_test_limits(self, tc: TestCase, step):
        """Extract test limits from step properties."""
        prop_obj = None
        try:
            prop_obj = step.AsPropertyObject()
            if prop_obj is None:
                return

            low_val = ""
            high_val = ""
            time_val = ""
            comp_val = ""
            unit_val = ""
            fmt_val = ""

            # Get comparison operator
            try:
                comp_val = prop_obj.GetValString("Comp", 0)
            except Exception:
                pass

            # Try to get Limits object for numeric limit tests
            try:
                limits = prop_obj.GetPropertyObject("Limits", 0)
                if limits:
                    # Low and High are numeric values
                    try:
                        low_val = str(limits.GetValNumber("Low", 0))
                    except Exception:
                        pass
                    try:
                        high_val = str(limits.GetValNumber("High", 0))
                    except Exception:
                        pass
                    del limits
            except Exception:
                pass

            # Get units and format from Result object
            try:
                result = prop_obj.GetPropertyObject("Result", 0)
                unit_val = result.GetValString("Units", 0) or ""
                result_num = result.GetPropertyObject("Numeric", 0)
                fmt_val = result_num.NumericFormat or ""
                del result_num
                del result
            except Exception:
                pass

            # Fallback: string-based limit properties
            if not low_val or not high_val:
                str_limit_props = ["Limits.Low", "Limits.High", "Limits.LSL", "Limits.USL",
                                  "TimeLimit", "LowLimit", "HighLimit"]
                for prop_name in str_limit_props:
                    try:
                        value = prop_obj.GetValString(prop_name, 0)
                        if value:
                            if "Low" in prop_name or "LSL" in prop_name or "LowLimit" in prop_name:
                                low_val = value
                            elif "High" in prop_name or "USL" in prop_name or "HighLimit" in prop_name:
                                high_val = value
                            elif "Time" in prop_name:
                                time_val = value
                    except Exception:
                        pass

            # Set USL/LSL (leave empty for now as per user request)
            # tc.lsl = low_val
            # tc.usl = high_val
            if time_val:
                tc.precision = time_val

            # Build limits string for LimitTest step types
            # Format: "表达式,单位,数据格式" or "表达式,数据格式"
            step_type = tc.step_type or ""
            if "Limit" in step_type or "Test" in step_type:
                parts = []

                # Add comparison expression
                # TestStand Comp constants (StepProperties.md):
                #   EQ  x==v         GE  x>=v         GT  x>v
                #   LE  x<=v         LT  x<v          NE  x!=v
                #   GELE low<=x<=high   GELT low<=x<high
                #   GTLE low<x<=high    GTLT low<x<high
                #   LOG  logarithmic
                if comp_val:
                    fmt_low = self._format_limit_value(low_val, fmt_val) if low_val else ""
                    fmt_high = self._format_limit_value(high_val, fmt_val) if high_val else ""
                    if comp_val == "EQ":
                        if fmt_low:
                            parts.append(f"x=={fmt_low}")
                    elif comp_val == "NE":
                        if fmt_low:
                            parts.append(f"x!={fmt_low}")
                    elif comp_val == "GE":
                        if fmt_low:
                            parts.append(f"x>={fmt_low}")
                    elif comp_val == "GT":
                        if fmt_low:
                            parts.append(f"x>{fmt_low}")
                    elif comp_val == "LE":
                        if fmt_high:
                            parts.append(f"x<={fmt_high}")
                    elif comp_val == "LT":
                        if fmt_low:
                            parts.append(f"x<{fmt_low}")
                    elif comp_val == "GELE":
                        if fmt_low and fmt_high:
                            parts.append(f"{fmt_low}<=x<={fmt_high}")
                    elif comp_val == "GELT":
                        if fmt_low and fmt_high:
                            parts.append(f"{fmt_low}<=x<{fmt_high}")
                    elif comp_val == "GTLE":
                        if fmt_low and fmt_high:
                            parts.append(f"{fmt_low}<x<={fmt_high}")
                    elif comp_val == "GTLT":
                        if fmt_low and fmt_high:
                            parts.append(f"{fmt_low}<x<{fmt_high}")
                    elif comp_val == "LOG":
                        if fmt_low and fmt_high:
                            parts.append(f"{fmt_low}<=log(x)<={fmt_high}")
                    else:
                        if fmt_low:
                            parts.append(f"x{comp_val}{fmt_low}")

                # Add units (from Result.Units)
                if unit_val:
                    tc.unit = unit_val

                # Add numeric format (raw format string from step)
                if fmt_val:
                    tc.format = fmt_val

                if parts:
                    tc.limits = ",".join(parts)
        except Exception:
            pass
        finally:
            if prop_obj is not None:
                del prop_obj

    def _extract_step_settings(self, tc: TestCase, step):
        """Extract step settings from step properties.

        Settings include: Adapter, LoadOpt, Expressions, Loop, AdditionalResults, etc.
        """
        prop_obj = None
        try:
            prop_obj = step.AsPropertyObject()
            if prop_obj is None:
                return

            settings_parts = []
            ts = prop_obj.GetPropertyObject("TS", 0)

            # Adapter info → tc.adapter (separate column)

            # LoadOpt (skip mode)
            self._add_ts_string_setting(settings_parts, ts, "LoadOpt", "LoadOpt",
                                        filter_val="Preload")

            # Expression settings - PreExpr, PostExpr, etc.
            for prop_name in self.SETTINGS_EXPR_PROPS:
                self._add_ts_string_setting(settings_parts, ts, prop_name, prop_name)

            # Loop settings - strip leading '=' if present
            for prop_name in self.SETTINGS_LOOP_PROPS:
                value = self._get_ts_string_value(ts, prop_name)
                if value:
                    if value.startswith('='):
                        value = value[1:]
                    if value and value not in ("RunState.LoopIndex += 1", "RunState.LoopIndex = 0"):
                        settings_parts.append(f"{prop_name}={value}")

            # Conditional/SequenceCall settings
            for prop_name in self.SETTINGS_CONDITIONAL_PROPS:
                self._add_property_string_setting(settings_parts, prop_obj, prop_name, prop_name)

            # Additional Results → tc.additional_results (separate column)
            ar_val = self._extract_additional_results(prop_obj)
            if ar_val:
                tc.additional_results = ar_val

            # VI Parameter-level AdditionalResult (CheckedState)
            ar_vi_val = self._extract_vi_parameter_additional_results(prop_obj)
            if ar_vi_val:
                tc.additional_results = (tc.additional_results + "," + ar_vi_val).strip(",") if tc.additional_results else ar_vi_val

            # ActiveX/COM adapter module settings
            if tc.adapter == "Automation Adapter":
                self._extract_activex_module_settings(settings_parts, prop_obj)

            # Lock/Unlock step settings (NI_Lock)
            if tc.step_type in ("Lock", "NI_Lock", "Unlock", "NI_Unlock"):
                lock_props = ["NameOrRefExpr", "Operation", "Lifetime", "LockLifetime",
                              "CreateIfDoesNotExist", "TimeoutEnabled", "TimeoutExpr",
                              "ErrorOnTimeout"]
                for prop_name in lock_props:
                    self._add_property_string_setting(settings_parts, prop_obj, prop_name, prop_name)

            # Mode → tc.run_mode (separate column)
            mode_val = self._get_ts_string_value(ts, "Mode")
            if mode_val and mode_val != "Normal":
                tc.run_mode = mode_val

            # Wait time → tc.wait_time (separate column)
            if tc.step_type == "NI_Wait":
                try:
                    wait_val = prop_obj.GetValString("TimeExpr", 0)
                    if wait_val:
                        tc.wait_time = wait_val
                except Exception:
                    pass

            # Breakpoint settings
            try:
                bp_result = step.GetBreakSettings()
                if bp_result is not None and bool(bp_result[0]):
                    bp_enabled = int(bool(bp_result[1]))
                    bp_pass = int(bp_result[2]) if len(bp_result) > 2 else 0
                    bp_cond = str(bp_result[3]) if len(bp_result) > 3 else ""
                    settings_parts.append(f"Breakpoint=1,{bp_enabled},{bp_pass},{bp_cond}")
            except Exception:
                pass

            # Filter and build settings string
            settings_parts = [p for p in settings_parts
                            if not any(p.endswith(f"={v}") for v in self.SETTINGS_SKIP_VALUES)]
            if settings_parts:
                tc.settings = "; ".join(settings_parts)

        except Exception:
            pass
        finally:
            if prop_obj is not None:
                del prop_obj

    def _get_ts_string_value(self, ts, prop_name: str) -> str:
        """Get a string property value from TS object."""
        try:
            return ts.GetValString(prop_name, 0) or ""
        except Exception:
            return ""

    def _add_ts_string_setting(self, settings_parts: list, ts, prop_name: str,
                               setting_name: str, filter_val: str = None) -> None:
        """Add a TS string property to settings if it has a value."""
        value = self._get_ts_string_value(ts, prop_name)
        if value and (filter_val is None or filter_val not in value):
            settings_parts.append(f"{setting_name}={value}")

    def _add_property_string_setting(self, settings_parts: list, prop_obj,
                                    prop_name: str, setting_name: str) -> None:
        """Add a PropertyObject string property to settings if it has a value."""
        try:
            value = prop_obj.GetValString(prop_name, 0)
            if value:
                settings_parts.append(f"{setting_name}={value}")
        except Exception:
            pass

    def _extract_additional_results(self, prop_obj) -> str:
        """Extract AdditionalResults from Step.AdditionalResults.

        Uses the correct API path:
        - Step.AdditionalResults → StepAdditionalResults
        - Step.AdditionalResults.CustomResults → AdditionalResults collection
        - Step.AdditionalResults.ParameterResults → AdditionalResults collection

        Each AdditionalResult has:
        - Name: result name expression
        - ValueToLog: value expression
        - Kind: 1=Custom, 2=InParameter, 3=OutParameter, 4=Call
        """
        result_names = []

        try:
            # Access Step.AdditionalResults (StepAdditionalResults object)
            additional_results = prop_obj.GetPropertyObject("AdditionalResults", 0)
            if additional_results is None:
                return ""

            # Extract CustomResults
            try:
                custom_results = additional_results.GetPropertyObject("CustomResults", 0)
                if custom_results:
                    count = custom_results.GetNumElements()
                    for i in range(count):
                        try:
                            elem = custom_results.GetPropertyObject(f"[{i}]", 0)
                            if elem:
                                name = elem.GetValString("Name", 0)
                                if name:
                                    result_names.append(name)
                                del elem
                        except Exception:
                            pass
                    del custom_results
            except Exception:
                pass

            # Extract ParameterResults
            try:
                param_results = additional_results.GetPropertyObject("ParameterResults", 0)
                if param_results:
                    count = param_results.GetNumElements()
                    for i in range(count):
                        try:
                            elem = param_results.GetPropertyObject(f"[{i}]", 0)
                            if elem:
                                name = elem.GetValString("Name", 0)
                                if name:
                                    result_names.append(name)
                                del elem
                        except Exception:
                            pass
                    del param_results
            except Exception:
                pass

            del additional_results

        except Exception:
            pass

        # Also check AdditionalResultsHints (via TS object)
        try:
            ts = prop_obj.GetPropertyObject("TS", 0)
            if ts:
                hints = ts.GetPropertyObject("AdditionalResultsHints", 0)
                if hints:
                    count = hints.GetNumElements()
                    for i in range(count):
                        try:
                            elem = hints.GetPropertyObject(f"[{i}]", 0)
                            if elem:
                                name = elem.GetValString("Name", 0)
                                if name:
                                    result_names.append(name)
                                del elem
                        except Exception:
                            pass
                    del hints
                del ts
        except Exception:
            pass

        if result_names:
            return ','.join(result_names)
        return ""

    def _extract_vi_parameter_additional_results(self, prop_obj) -> str:
        """Extract VI parameter-level AdditionalResult (CheckedState).

        For LabVIEW VI steps, each parameter in TS.SData.ViCall.Parms can have
        an AdditionalResult sub-property with a CheckedState value indicating
        whether the parameter is logged as a test result.

        Path: TS.SData.ViCall.Parms[K].AdditionalResult.CheckedState
        - CheckedState=0: not logged (default, skipped)
        - CheckedState=2: logged as result

        Returns: comma-separated AR entries like AR.Parms[4](Data out).CheckedState=2
        """
        vi_call = None
        try:
            # Access ViCall directly from prop_obj (same as _get_module_parameters)
            vi_call = prop_obj.GetPropertyObject("ViCall", 0)
        except Exception:
            pass

        if vi_call is None:
            # Try through TS.SData.ViCall path
            try:
                ts = prop_obj.GetPropertyObject("TS", 0)
                if ts:
                    sdata = ts.GetPropertyObject("SData", 0)
                    if sdata:
                        vi_call = sdata.GetPropertyObject("ViCall", 0)
                        del sdata
                    del ts
            except Exception:
                pass

        if vi_call is None:
            return ""

        ar_values = []
        try:
            parms = vi_call.GetPropertyObject("Parms", 0)
            if parms is None:
                return ""

            num_elements = parms.GetNumElements()
            for i in range(num_elements):
                try:
                    # Use [{i}] not Parms[{i}] for COM API access
                    elem = parms.GetPropertyObject(f"[{i}]", 0)
                    if elem is None:
                        continue
                    ar_name = self._extract_ar_from_elem(elem, i)
                    if ar_name:
                        ar_values.append(ar_name)
                    del elem
                except Exception:
                    pass

            del parms

        except Exception:
            pass
        finally:
            if vi_call is not None:
                del vi_call

        return ",".join(ar_values) if ar_values else ""

    def _extract_ar_from_elem(self, elem, i: int) -> str:
        """Extract AdditionalResult.CheckedState from a VI parameter element.

        Only logs CheckedState=2 (output parameters logged as test results).
        CheckedState=1 is the default checked state and not included.
        Returns: full AR string like "AR.Parms[4](Data out).CheckedState=2", else empty.
        """
        try:
            label = ""
            try:
                label = elem.GetValString("Label", 0) or ""
            except Exception:
                pass

            ar = elem.GetPropertyObject("AdditionalResult", 0)
            if ar:
                checked_state = int(ar.GetValNumber("CheckedState", 0))
                if checked_state == 2:
                    param_ref = f"Parms[{i}]({label})" if label else f"Parms[{i}]"
                    del ar
                    return f"AR.{param_ref}.CheckedState={checked_state}"
                del ar
        except Exception:
            pass
        return ""

    def _extract_activex_module_settings(self, settings_parts: list, prop_obj) -> None:
        """Extract ActiveX/COM module settings from TS.SData.Call.

        Properties:
        - ServerName (Automation Server)
        - InterfaceName (Object Reference)
        - CoClassName (Object Class)
        - MemberName (Call Method)
        """
        try:
            ts = prop_obj.GetPropertyObject("TS", 0)
            if ts is None:
                return

            sdata = ts.GetPropertyObject("SData", 0)
            if sdata is None:
                return

            call = sdata.GetPropertyObject("Call", 0)
            if call is None:
                return

            # Automation Server
            try:
                server_name = call.GetValString("ServerName", 0)
                if server_name:
                    settings_parts.append(f"Server={server_name}")
            except Exception:
                pass

            # Server GUID (CLSID)
            try:
                server_guid = call.GetValString("Server", 0)
                if server_guid:
                    settings_parts.append(f"ServerGuid={server_guid}")
            except Exception:
                pass

            # Object Class (CoClassName)
            try:
                co_class = call.GetValString("CoClassName", 0)
                if co_class:
                    settings_parts.append(f"CoClass={co_class}")
            except Exception:
                pass

            # Object Reference (InterfaceName)
            try:
                interface_name = call.GetValString("InterfaceName", 0)
                if interface_name:
                    settings_parts.append(f"Interface={interface_name}")
            except Exception:
                pass

            # Interface GUID (IID)
            try:
                interface_guid = call.GetValString("Interface", 0)
                if interface_guid:
                    settings_parts.append(f"InterfaceGuid={interface_guid}")
            except Exception:
                pass

            # Call Method (MemberName)
            try:
                member_name = call.GetValString("MemberName", 0)
                if member_name:
                    settings_parts.append(f"Member={member_name}")
            except Exception:
                pass

            # Member DISPID
            try:
                member_id = int(call.GetValNumber("Member", 0))
                if member_id:
                    settings_parts.append(f"MemberId={member_id}")
            except Exception:
                pass

            # MemberType: 1=CallMethod, 2=GetProperty, 4=SetProperty, 8=SetPropertyByRef
            try:
                member_type = int(call.GetValNumber("MemberType", 0))
                if member_type:
                    settings_parts.append(f"MemberType={member_type}")
            except Exception:
                pass

            del call
            del sdata
            del ts
        except Exception:
            pass

    def _add_result_option(self, settings_parts: list, ts) -> None:
        """Add ResultOption setting if not Default."""
        try:
            result_option_num = ts.GetValNumber("ResultOption", 0)
            result_option = self.RESULT_OPTION_MAP.get(int(result_option_num),
                                                       str(int(result_option_num)))
            if result_option != "Default":
                settings_parts.append(f"ResultOption={result_option}")
        except Exception:
            pass