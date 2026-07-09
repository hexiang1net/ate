"""Generate TestStand sequence file from parsed Excel data."""

import os
import re
from typing import List, Dict, Optional

import win32com.client

from engine.teststand_engine import TestStandEngine
from engine.constants import STEP_GROUP_API, STEP_TYPE_SEQUENCE_CALL
from .excel_to_seq_model import ParsedTestCase, ParsedViParameter, ParsedVariable
from .excel_parser import group_by_parent_step


# Step types that are flow control (don't need VI path)
FLOW_CONTROL_TYPES = {"NI_Flow_If", "NI_Flow_Else", "NI_Flow_End", "NI_Wait"}

# Settings property mappings: setting_key -> (property_path, flags)
SETTINGS_PROPERTY_MAP = {
    "PreExpr": ("TS.PreExpr", 0),
    "StatusExpr": ("TS.StatusExpr", 0),
    "PostExpr": ("TS.PostExpr", 0),
    "ConditionExpr": ("ConditionExpr", 0),
    "LoadOpt": ("TS.LoadOpt", 0),
    "Mode": ("TS.Mode", 0),
    "Wait": ("TimeExpr", 0),
    "LoopType": ("TS.LoopType", 0),
    "LoopWhile": ("TS.LoopWhile", 0),
    "LoopCount": ("TS.LoopCount", 0),
    "LoopInitialize": ("TS.LoopInitialize", 0),
    "NameOrRefExpr": ("NameOrRefExpr", 0),
    "Operation": ("Operation", 0),
    "Lifetime": ("Lifetime", 0),
    "LockLifetime": ("LockLifetime", 0),
    "CreateIfDoesNotExist": ("CreateIfDoesNotExist", 0),
    "TimeoutEnabled": ("TimeoutEnabled", 0),
    "TimeoutExpr": ("TimeoutExpr", 0),
    "ErrorOnTimeout": ("ErrorOnTimeout", 0),
}


class SeqGenerator:
    """Generate TestStand .seq file from parsed Excel test cases."""

    ADAPTER_LV = "G Flexible VI Adapter"
    ADAPTER_NONE = "None Adapter"
    ADAPTER_SEQUENCE = "Sequence Adapter"
    ADAPTER_AUTOMATION = "Automation Adapter"
    ADAPTER_DLL = "DLL Flexible Prototype Adapter"
    STEP_TYPE_ACTION = "Action"

    def __init__(self):
        self._engine = None

    def generate(self, test_cases: List[ParsedTestCase],
                vi_params: List[ParsedViParameter],
                output_path: str,
                sequence_name: str = "MainSequence",
                variables: List[ParsedVariable] = None) -> None:
        """Generate sequence file from test cases.

        Creates separate sub-sequences for nested steps (e.g. 2_4_1 -> parent 2_4).
        Each sub-sequence group becomes its own sequence, and the parent step
        in the main sequence becomes a SequenceCall step.
        """
        self._engine = TestStandEngine()

        with self._engine:
            self._engine.create_new_file(output_path)

            # Build VI param lookup by step_no
            vi_param_map = self._build_vi_param_map(vi_params)

            # Separate top-level from nested (sub-sequence) steps
            top_level, sub_sequence_groups, parent_names = group_by_parent_step(test_cases)

            # Build lookup: parent_no -> parent ParsedTestCase
            parent_case_map = {tc.step_no: tc for tc in top_level}

            # Create sub-sequences FIRST (they need to exist before SequenceCall can reference them)
            for parent_no, child_cases in sub_sequence_groups.items():
                parent_tc = parent_case_map.get(parent_no)
                seq_name = parent_tc.test_project if parent_tc else f"SubSeq_{parent_no}"
                self._create_sub_sequence(seq_name, child_cases, vi_param_map)

            # Create main sequence (auto-created with NewSequenceFile)
            if self._engine.sequence_file.NumSequences > 0:
                main_seq = self._engine.sequence_file.GetSequence(0)
                main_seq.Name = sequence_name
            else:
                main_seq = self._engine.engine.NewSequence()
                main_seq.Name = sequence_name
                self._engine.sequence_file.InsertSequenceEx(0, main_seq)

            # Create top-level steps in main sequence - route each to its proper group
            # Enforce fixed order: startup → main → cleanup
            from collections import defaultdict
            by_group = defaultdict(list)
            for tc in top_level:
                by_group[tc.step_group].append(tc)
            for group_name in ("startup", "main", "cleanup"):
                group_cases = by_group.get(group_name)
                if group_cases:
                    self._create_steps_in_sequence(main_seq, group_cases, vi_param_map, group_name,
                                                   sub_sequence_groups=sub_sequence_groups)

            # Create variables (FileGlobals and Locals)
            if variables:
                self._create_variables(variables)

            self._engine.save_file(output_path)

    def _build_vi_param_map(self, vi_params: List[ParsedViParameter]) -> Dict[str, ParsedViParameter]:
        """Build lookup map for VI parameters by step_no."""
        return {vp.step_no: vp for vp in vi_params}

    # PropertyValueTypes constants
    PROP_TYPE_CONTAINER = 0
    PROP_TYPE_STRING = 1
    PROP_TYPE_BOOLEAN = 2
    PROP_TYPE_NUMBER = 3

    def _prop_type_from_str(self, type_str: str) -> int:
        """Convert type string to PropertyValueTypes constant."""
        t = type_str.lower()
        if t == "string":
            return self.PROP_TYPE_STRING
        if t == "boolean":
            return self.PROP_TYPE_BOOLEAN
        if t == "number":
            return self.PROP_TYPE_NUMBER
        # Array and others default to container
        return self.PROP_TYPE_CONTAINER

    def _set_prop_value(self, container, name: str, value: str, var_type: str) -> None:
        """Set a property value on a PropertyObject container."""
        try:
            t = var_type.lower()
            if t == "number":
                container.SetValNumber(name, 0, float(value))
            elif t == "boolean":
                container.SetValBoolean(name, 0, value.lower() == "true")
            elif t == "string":
                container.SetValString(name, 0, value)
        except Exception:
            pass

    def _create_variables(self, variables: List[ParsedVariable]) -> None:
        """Create FileGlobals and Locals variables in the sequence file."""
        file_globals = []
        locals_groups = {}  # seq_name -> [ParsedVariable, ...]

        for v in variables:
            if v.container == "FileGlobals":
                file_globals.append(v)
            elif v.container.startswith("Locals."):
                seq_name = v.container[7:]
                locals_groups.setdefault(seq_name, []).append(v)

        # Create FileGlobals
        if file_globals:
            try:
                fg = self._engine.sequence_file.FileGlobalsDefaultValues
                for v in file_globals:
                    value_type = self._prop_type_from_str(v.var_type)
                    is_array = v.var_type.lower() == "array"
                    try:
                        fg.NewSubProperty(v.name, value_type, is_array, "", 0)
                    except Exception:
                        pass
                    if not is_array and v.value:
                        self._set_prop_value(fg, v.name, v.value, v.var_type)
                del fg
            except Exception:
                pass

        # Create Locals — match by sequence name
        if locals_groups:
            try:
                num_seqs = self._engine.sequence_file.NumSequences
                for seq_idx in range(num_seqs):
                    seq = self._engine.sequence_file.GetSequence(seq_idx)
                    seq_name = seq.Name
                    if seq_name in locals_groups:
                        try:
                            loc = seq.Locals
                            for v in locals_groups[seq_name]:
                                value_type = self._prop_type_from_str(v.var_type)
                                is_array = v.var_type.lower() == "array"
                                try:
                                    loc.NewSubProperty(v.name, value_type, is_array, "", 0)
                                except Exception:
                                    pass
                                if not is_array and v.value:
                                    self._set_prop_value(loc, v.name, v.value, v.var_type)
                            del loc
                        except Exception:
                            pass
                    del seq
            except Exception:
                pass

    def _create_sub_sequence(self, seq_name: str, cases: List[ParsedTestCase],
                             vi_param_map: Dict[str, ParsedViParameter]) -> None:
        """Create a sub-sequence for a group of child steps."""
        sub_seq = self._engine.engine.NewSequence()
        sub_seq.Name = seq_name

        # Insert at end of sequence file
        insert_pos = self._engine.sequence_file.NumSequences
        self._engine.sequence_file.InsertSequenceEx(insert_pos, sub_seq)
        # After InsertSequenceEx, sub_seq belongs to the file - don't del it

        # Group child cases by step group and route each to its proper group
        by_group = self._group_cases_by_step_group(cases)
        for group_name in ("startup", "main", "cleanup"):
            group_cases = by_group.get(group_name)
            if group_cases:
                self._create_steps_in_sequence(sub_seq, group_cases, vi_param_map, group_name)

    def _create_steps_in_sequence(self, sequence, cases: List[ParsedTestCase],
                                  vi_param_map: Dict[str, ParsedViParameter],
                                  group_name: str,
                                  sub_sequence_groups: Dict[str, List[ParsedTestCase]] = None) -> None:
        """Create steps within a sequence.

        For top-level steps that have sub-sequence children, creates a SequenceCall
        step instead of an Action step.
        """
        api_group = STEP_GROUP_API[self._group_name_to_idx(group_name)]
        count = sequence.GetNumSteps(api_group)

        for tc in cases:
            step = None
            try:
                # Check if this step has sub-sequence children
                if sub_sequence_groups and len(tc.step_no.split("_")) == 2:
                    parent_no = tc.step_no
                    if parent_no in sub_sequence_groups:
                        # Create SequenceCall step to call the sub-sequence
                        step = self._create_sequence_call_step(tc, parent_no)
                    else:
                        step = self._create_normal_step(tc, vi_param_map)
                else:
                    step = self._create_normal_step(tc, vi_param_map)

                # Mark step as skipped if run_mode is "Skip"
                if tc.run_mode.lower() == "skip":
                    try:
                        prop = step.AsPropertyObject()
                        prop.SetValString("TS.Mode", 0, "Skip")
                        del prop
                    except Exception:
                        pass

                sequence.InsertStep(step, count, api_group)
                self._engine.sequence_file.IncChangeCount()
                count += 1
            except Exception as e:
                print(f"Warning: failed to create step {tc.step_no} ({tc.test_project}): {e}")
            finally:
                if step is not None:
                    del step

    def _create_normal_step(self, tc: ParsedTestCase, vi_param_map: Dict[str, ParsedViParameter] = None):
        """Create a normal (non-SequenceCall) step."""
        adapter = self._get_adapter_for_step(tc)
        step = self._engine.engine.NewStep(adapter, tc.step_type)
        step.Name = tc.test_project

        # Set comment from comments field, or fallback to description
        comment = tc.comments if tc.comments else tc.description
        if comment:
            step.Comment = comment

        # Register type with the file's type usage list
        self._engine.sequence_file.AsPropertyObjectFile().TypeUsageList.AddUsedTypes(
            step.AsPropertyObject()
        )

        # Build effective settings (merge additional_results column into settings)
        effective_settings = tc.settings
        if tc.additional_results:
            ar_part = tc.additional_results
            if ar_part.startswith("AR.Parms["):
                if effective_settings:
                    effective_settings = effective_settings + "; " + ar_part
                else:
                    effective_settings = ar_part
            elif not effective_settings or "AdditionalResults=" not in effective_settings:
                effective_settings = (effective_settings + "; " if effective_settings else "") + "AdditionalResults=" + ar_part

        # Set VI path if applicable
        if tc.vi_path and adapter != self.ADAPTER_NONE:
            self._set_module_vi_path(step, tc.vi_path, tc.step_no, vi_param_map, effective_settings, tc.adapter)

        # Apply step-type-specific properties (pass effective_settings for AR processing)
        self._apply_step_properties(step, tc, effective_settings)

        return step

    def _create_sequence_call_step(self, tc: ParsedTestCase, parent_no: str):
        """Create a SequenceCall step that calls a sub-sequence."""
        step = self._engine.engine.NewStep("Sequence Adapter", "SequenceCall")
        step.Name = tc.test_project
        if tc.description:
            step.Comment = tc.description

        # Register type
        self._engine.sequence_file.AsPropertyObjectFile().TypeUsageList.AddUsedTypes(
            step.AsPropertyObject()
        )

        # Set which sequence to call via TS.SData.SeqName
        try:
            prop_obj = step.AsPropertyObject()
            ts = prop_obj.GetPropertyObject("TS", 0)
            sdata = ts.GetPropertyObject("SData", 0)
            # Sub-sequence name matches parent test_project (e.g., "2.0 Check DC Voltage Test")
            seq_name = tc.test_project
            sdata.SetValString("SeqName", 0, seq_name)
            sdata.SetValBoolean("UseCurFile", 0, True)
            del sdata
            del ts
            del prop_obj
        except Exception:
            pass

        # Apply settings if any
        if tc.settings:
            prop_obj = step.AsPropertyObject()
            if prop_obj:
                self._apply_settings_expressions(prop_obj, tc.settings, step)
                del prop_obj

        return step

    def _get_adapter_for_step(self, tc: ParsedTestCase) -> str:
        """Determine the adapter for a step based on its type and VI path."""
        # First check adapter column (K column)
        if tc.adapter:
            return tc.adapter

        # Then check if adapter is specified in settings
        if tc.settings:
            for part in tc.settings.split(';'):
                if part.startswith('Adapter='):
                    adapter = part[8:].strip()
                    if adapter:
                        return adapter

        # Fallback logic
        if tc.step_type in FLOW_CONTROL_TYPES:
            return self.ADAPTER_NONE
        if tc.vi_path:
            return self.ADAPTER_LV
        return self.ADAPTER_NONE

    def _set_module_vi_path(self, step, vi_path: str, step_no: str = None, vi_param_map: Dict[str, ParsedViParameter] = None, settings: str = None, adapter: str = None) -> None:
        """Set VI path on step's module and load prototype to compile.

        Also sets VI parameters from vi_param_map if provided.
        Applies VI parameter-level AdditionalResult.CheckedState from settings.
        For ActiveX/COM adapter steps, sets Call properties instead of VI path.
        """
        # Detect ActiveX/COM adapter — check both adapter column (K) and settings (M)
        is_activex = (adapter and "Automation" in adapter) or (settings and "Adapter=Automation Adapter" in settings)

        if is_activex:
            self._setup_activex_module(step, settings, step_no, vi_param_map)
            return

        # Try to resolve VI path if it doesn't exist
        resolved_vi_path = vi_path
        if vi_path and not os.path.exists(vi_path):
            resolved_vi_path = self._search_vi_near_seq_file(vi_path)

        try:
            module = step.Module
            if module is not None:
                module.VIPath = resolved_vi_path if resolved_vi_path else vi_path
                # Load prototype to compile the VI and validate parameters
                module.LoadPrototype()

                # Set VI parameters from vi_parameter_table if available
                if step_no and vi_param_map and step_no in vi_param_map:
                    self._set_vi_parameters(module, vi_param_map[step_no])

                # Apply VI parameter-level AdditionalResult.CheckedState
                if settings:
                    self._apply_vi_param_additional_results(module, settings)

                del module
        except Exception:
            pass

    def _setup_activex_module(self, step, settings: str, step_no: str = None, vi_param_map: Dict[str, ParsedViParameter] = None) -> None:
        """Set up ActiveX/COM adapter module properties.

        Sets TS.SData.Call properties: ServerName, InterfaceName, CoClassName, MemberName.
        Loads the COM module prototype, then sets COM method parameters from vi_param_map.
        """
        prop_obj = None
        try:
            prop_obj = step.AsPropertyObject()
            if prop_obj is None:
                return

            # Parse ActiveX settings
            ax_settings = {}
            for part in settings.split(';'):
                part = part.strip()
                for key in ('Server=', 'ServerGuid=', 'Interface=', 'InterfaceGuid=',
                            'CoClass=', 'Member=', 'MemberId=', 'MemberType='):
                    if part.startswith(key):
                        ax_settings[key[:-1]] = part[len(key):].strip()

            # Set TS.SData.Call properties
            ts = prop_obj.GetPropertyObject("TS", 0)
            if ts:
                sdata = ts.GetPropertyObject("SData", 0)
                if sdata:
                    call = sdata.GetPropertyObject("Call", 0)
                    if call:
                        # ObjectVariable is required for COM object instantiation
                        try:
                            call.SetValString("ObjectVariable", 0, "RunState.Thread")
                        except Exception:
                            pass
                        if "Server" in ax_settings:
                            try:
                                call.SetValString("ServerName", 0, ax_settings["Server"])
                            except Exception:
                                pass
                        if "ServerGuid" in ax_settings:
                            try:
                                call.SetValString("Server", 0, ax_settings["ServerGuid"])
                            except Exception:
                                pass
                        if "Interface" in ax_settings:
                            try:
                                call.SetValString("InterfaceName", 0, ax_settings["Interface"])
                            except Exception:
                                pass
                        if "InterfaceGuid" in ax_settings:
                            try:
                                call.SetValString("Interface", 0, ax_settings["InterfaceGuid"])
                            except Exception:
                                pass
                        if "CoClass" in ax_settings:
                            try:
                                call.SetValString("CoClassName", 0, ax_settings["CoClass"])
                            except Exception:
                                pass
                        if "Member" in ax_settings:
                            try:
                                call.SetValString("MemberName", 0, ax_settings["Member"])
                            except Exception:
                                pass
                        if "MemberId" in ax_settings:
                            try:
                                call.SetValNumber("Member", 0, int(ax_settings["MemberId"]))
                            except Exception:
                                pass
                        if "MemberType" in ax_settings:
                            try:
                                call.SetValNumber("MemberType", 0, int(ax_settings["MemberType"]))
                            except Exception:
                                pass
                        del call
                    del sdata
                del ts

            # Set parameters AFTER Call properties are configured
            # (LoadPrototype needs Server/Interface GUIDs to enumerate COM method params)
            if step_no and vi_param_map and step_no in vi_param_map:
                vi_param = vi_param_map[step_no]
                if not self._set_activex_params_via_module(step, vi_param):
                    # Fallback: try TS.SData.Call.Parameters
                    self._set_activex_call_parameters(prop_obj, vi_param)

        except Exception:
            pass
        finally:
            if prop_obj is not None:
                del prop_obj

    def _set_activex_call_parameters(self, prop_obj, vi_param: ParsedViParameter) -> None:
        """Set ActiveX/COM method parameters via TS.SData.Call.Parameters.

        Parameters are stored in Call.Parameters[n] with Name and ArgVal.
        If the Parameters container is empty, creates entries for each parameter.
        """
        try:
            ts = prop_obj.GetPropertyObject("TS", 0)
            if not ts:
                return
            sdata = ts.GetPropertyObject("SData", 0)
            if not sdata:
                del ts
                return
            call = sdata.GetPropertyObject("Call", 0)
            if not call:
                del sdata
                del ts
                return

            # Filter out empty parameter names
            valid_params = [(n, v) for n, v in zip(vi_param.param_names, vi_param.param_values) if n]

            params = call.GetPropertyObject("Parameters", 0)
            if params:
                count = params.GetNumElements()
                if count == 0 and valid_params:
                    # Parameters container is empty - create entries
                    params.SetNumElements(len(valid_params))
                    for i, (name, value) in enumerate(valid_params):
                        try:
                            elem = params.GetPropertyObject(f"[{i}]", 0)
                            if elem:
                                elem.SetValString("Name", 0, name)
                                if value:
                                    final_value = self._format_activex_param_value(value)
                                    elem.SetValString("ArgVal", 0, final_value)
                                del elem
                        except Exception:
                            pass
                else:
                    # Parameters exist - update matching ones
                    for i in range(count):
                        try:
                            elem = params.GetPropertyObject(f"[{i}]", 0)
                            if elem:
                                name = elem.GetValString("Name", 0) or ""
                                if name in vi_param.param_names:
                                    idx = vi_param.param_names.index(name)
                                    value = vi_param.param_values[idx]
                                    if value:
                                        final_value = self._format_activex_param_value(value)
                                        elem.SetValString("ArgVal", 0, final_value)
                                del elem
                        except Exception:
                            pass
                del params

            del call
            del sdata
            del ts
        except Exception:
            pass

    def _format_activex_param_value(self, value: str) -> str:
        """Format an ActiveX parameter value with appropriate quoting."""
        if value.startswith('"') and value.endswith('"'):
            return value
        # TestStand expression prefixes — never quote these
        for prefix in ('RunState.', 'FileGlobals.', 'Locals.', 'Step.', 'ThisContext'):
            if value.startswith(prefix):
                return value
        if value in ('True', 'False'):
            return value
        if value.replace('.', '').replace('-', '').isdigit():
            return value
        # Expressions containing operators — not string literals
        if any(op in value for op in ('+', '-', '*', '/', '(', ')', '%')):
            return value
        return f'"{value}"'

    def _set_activex_params_via_module(self, step, vi_param: ParsedViParameter) -> bool:
        """Set ActiveX parameters via ActiveXModule.Parameters API.

        Uses dynamic Dispatch on step.Module to access ActiveXModule interface,
        calls LoadPrototype, then sets ActiveXParameter.ValueExpr for matched parameters.
        Returns True if successful, False to trigger fallback.
        """
        try:
            module = step.Module
            if module is None:
                return False
            mod_dyn = win32com.client.dynamic.Dispatch(module._oleobj_)
            mod_dyn.LoadPrototype(0)
            params = mod_dyn.Parameters
            if not params or params.Count == 0:
                del module
                return False

            for i in range(params.Count):
                try:
                    item = params.Item(i)
                    item_dyn = win32com.client.dynamic.Dispatch(item._oleobj_)
                    param_name = item_dyn.ParameterName or ""

                    matched_idx = -1
                    if param_name in vi_param.param_names:
                        matched_idx = vi_param.param_names.index(param_name)

                    if matched_idx >= 0:
                        value = vi_param.param_values[matched_idx]
                        if value:
                            final_value = self._format_activex_param_value(value)
                            item_dyn.UseDefault = False
                            item_dyn.ValueExpr = final_value
                except Exception:
                    pass

            del module
            return True
        except Exception:
            return False

    def _search_vi_near_seq_file(self, vi_path: str) -> Optional[str]:
        """Search for VI file near the sequence file location.

        Handles encoded/corrupted paths and relative paths.
        """
        if not vi_path or not self._engine or not self._engine.current_file_path:
            return None

        # Extract VI filename from path
        if ".vi" not in vi_path.lower():
            return None

        vi_filename = None
        parts = vi_path.replace("/", os.sep).split(os.sep)
        for part in reversed(parts):
            if ".vi" in part.lower():
                vi_filename = part
                break

        if not vi_filename:
            return None

        # Search near sequence file location
        search_base = os.path.dirname(self._engine.current_file_path)
        if not search_base:
            return None

        return self._search_for_vi_impl(search_base, vi_filename, max_depth=5)

    def _search_for_vi_impl(self, base_dir: str, vi_filename: str, max_depth: int, current_depth: int = 0) -> Optional[str]:
        """Recursively search for VI file with depth limit."""
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

        # Check subdirectories with common VI folder names
        vi_subdirs = ["VIs for U-1 Test module", "Sub VIs", "VIs", "Modules", "LabVIEW VIs"]

        try:
            dirs = os.listdir(base_dir)
            for d in dirs:
                if d in vi_subdirs:
                    subdir = os.path.join(base_dir, d)
                    if os.path.isdir(subdir):
                        result = self._search_for_vi_impl(subdir, vi_filename, max_depth, current_depth + 1)
                        if result:
                            return result
        except PermissionError:
            pass

        return None

    def _set_vi_parameters(self, module, vi_param: ParsedViParameter) -> None:
        """Set VI parameters from ParsedViParameter.

        Uses LabVIEWModule.Parameters to set parameter value expressions.
        Must call LoadPrototype before accessing parameters.
        Per API docs, UseDefaultValue must be False for ValueExpr to be used.

        Note: param_names from Excel may match either ParameterName or ParameterCaption.
        For enum parameters, GetEnumValues() returns valid constant names - use these directly.
        For string parameters with embedded quotes (from Excel display), strip outer quotes.
        """
        try:
            # Get the LabVIEW parameters collection
            params = module.Parameters
            if params is None:
                return

            count = params.Count
            # Match parameters by name or caption and set value expression
            for i in range(count):
                param = params.Item(i)
                if param is None:
                    continue

                param_name = param.ParameterName
                param_caption = param.ParameterCaption if hasattr(param, 'ParameterCaption') else ""

                # Find matching parameter - try name first, then caption
                matched_idx = -1
                if param_name and param_name in vi_param.param_names:
                    matched_idx = vi_param.param_names.index(param_name)
                elif param_caption and param_caption in vi_param.param_names:
                    matched_idx = vi_param.param_names.index(param_caption)

                if matched_idx >= 0:
                    value = vi_param.param_values[matched_idx]
                    if value:
                        # Output parameters are always expressions — never quote them.
                        # Input parameters: quote string literals, but not expressions/numbers/booleans.
                        direction = int(param.Direction) if hasattr(param, 'Direction') else 0
                        if direction == 1:  # Output
                            needs_quotes = False
                        else:  # Input or Input/Output
                            needs_quotes = True
                            if value.startswith('"') and value.endswith('"'):
                                needs_quotes = False  # Already quoted from Excel
                            elif value.startswith('RunState.') or value.startswith('FileGlobals.') or value.startswith('Step.') or value.startswith('Locals.'):
                                needs_quotes = False  # TestStand expressions
                            elif value in ('True', 'False'):
                                needs_quotes = False  # Boolean
                            elif value.replace('.', '').replace('-', '').isdigit():
                                needs_quotes = False  # Numeric

                        final_value = f'"{value}"' if needs_quotes else value

                        # Per API docs: UseDefaultValue must be False for ValueExpr to be used
                        param.UseDefaultValue = False
                        param.ValueExpr = final_value
                del param
            del params
        except Exception:
            pass

    def _apply_vi_param_additional_results(self, module, settings: str) -> None:
        """Apply VI parameter-level AdditionalResult.CheckedState from settings.

        Parses AR entries like: AR.Parms[4](Data out).CheckedState=2
        Matches parameters by label (e.g., "Data out") and sets CheckedState
        on the module parameter's AdditionalResult sub-property.
        """
        # Parse AR entries from settings
        ar_entries = []  # [(label, checked_state), ...]
        for part in settings.split(';'):
            part = part.strip()
            if part.startswith('AR.Parms[') and '.CheckedState=' in part:
                match = re.match(r'AR\.Parms\[\d+\]\(([^)]+)\)\.CheckedState=(\d+)', part)
                if match:
                    label = match.group(1)
                    checked_state = int(match.group(2))
                    ar_entries.append((label, checked_state))

        if not ar_entries:
            return

        try:
            params = module.Parameters
            if params is None:
                return

            count = params.Count
            for i in range(count):
                param = params.Item(i)
                if param is None:
                    continue

                param_name = param.ParameterName or ""
                param_caption = ""
                try:
                    param_caption = param.ParameterCaption or ""
                except Exception:
                    pass

                for label, checked_state in ar_entries:
                    if label == param_name or label == param_caption:
                        try:
                            ar = param.GetPropertyObject("AdditionalResult", 0)
                            if ar:
                                ar.SetValNumber("CheckedState", 0, checked_state)
                                del ar
                        except Exception:
                            pass
                        break

                del param
            del params
        except Exception:
            pass

    def _apply_step_properties(self, step, tc: ParsedTestCase, effective_settings: str = None) -> None:
        """Apply step-type-specific properties from parsed data."""
        prop_obj = None
        try:
            prop_obj = step.AsPropertyObject()
            if prop_obj is None:
                return

            # Handle limits for NumericLimitTest
            if tc.step_type == "NumericLimitTest" and tc.limits:
                self._apply_numeric_limits(prop_obj, tc.limits, tc.unit, tc.format)

            # Handle settings expressions (PreExpr, StatusExpr, PostExpr, etc.)
            settings = effective_settings if effective_settings is not None else tc.settings
            if settings:
                self._apply_settings_expressions(prop_obj, settings, step)

            # Handle NI_Wait special case - extract from vi_path if not in settings
            if tc.step_type == "NI_Wait":
                self._apply_wait(prop_obj, tc)

        finally:
            if prop_obj is not None:
                del prop_obj

    def _apply_numeric_limits(self, prop_obj, limits_str: str, unit_str: str = "", format_str: str = "") -> None:
        """Parse and apply NumericLimitTest limits.

        Args:
            prop_obj: Step property object
            limits_str: Limit expression (e.g., "4.50<=x<=5.50", "x==0xaa")
            unit_str: Unit string (e.g., "Vdc", "VAC")
            format_str: Numeric format (e.g., "%.2f", "%u", "%#x")
        """
        limits_str = limits_str.strip()
        if not limits_str:
            return

        # Extract numeric values from the expression
        nums = re.findall(r"0x[0-9a-fA-F]+|[-+]?\d*\.?\d+", limits_str)
        nums_converted = []
        for n in nums:
            if n.startswith('0x') or n.startswith('0X'):
                nums_converted.append(int(n, 16))
            else:
                nums_converted.append(float(n) if n else 0.0)

        if not nums_converted:
            return

        # Determine low/high values
        expr_only = limits_str
        if "<=x<=" in expr_only or "<=x<=" in limits_str.replace(" ", ""):
            if len(nums_converted) >= 2:
                low_val, high_val = nums_converted[0], nums_converted[1]
            else:
                low_val, high_val = nums_converted[0], nums_converted[0]
        elif "x==" in expr_only or "x==" in limits_str:
            val = nums_converted[0] if nums_converted else 0
            low_val, high_val = val, val
        elif "x<" in expr_only or "x<" in limits_str:
            high_val = nums_converted[0] if nums_converted else 0
            low_val = float('-inf')
        elif "x>" in expr_only or "x>" in limits_str:
            low_val = nums_converted[0] if nums_converted else 0
            high_val = float('inf')
        else:
            low_val, high_val = nums_converted[0], nums_converted[0]

        try:
            prop_obj.SetValNumber("Limits.Low", 0, low_val)
        except Exception:
            pass
        try:
            prop_obj.SetValNumber("Limits.High", 0, high_val)
        except Exception:
            pass
        # For x== comparison, set Comp to 'EQ' (equality)
        if "x==" in expr_only or "x==" in limits_str:
            try:
                prop_obj.SetValString("Comp", 0, "EQ")
            except Exception:
                pass

        # Set Units if present - must be set via Result.Units (not Limits.Units)
        if unit_str:
            try:
                prop_obj.SetValString("Result.Units", 0, unit_str)
            except Exception:
                pass
            try:
                result = prop_obj.GetPropertyObject("Result", 0)
                result.SetValString("Units", 0, unit_str)
                del result
            except Exception:
                pass

        # Set NumericFormat if present - must be set via Limits.High, Limits.Low, and Result.Numeric
        # per StepProperties.md: "set the numeric format using PropertyObject.NumericFormat property
        # of the following step properties: Limits.High, Limits.Low, and Result.Numeric"
        if format_str:
            # Set on Limits.High
            try:
                limits_high = prop_obj.GetPropertyObject("Limits.High", 0)
                if limits_high:
                    limits_high.NumericFormat = format_str
                    del limits_high
            except Exception:
                pass
            try:
                prop_obj.SetValString("Limits.High.NumericFormat", 0, format_str)
            except Exception:
                pass

            # Set on Limits.Low
            try:
                limits_low = prop_obj.GetPropertyObject("Limits.Low", 0)
                if limits_low:
                    limits_low.NumericFormat = format_str
                    del limits_low
            except Exception:
                pass
            try:
                prop_obj.SetValString("Limits.Low.NumericFormat", 0, format_str)
            except Exception:
                pass

            # Set on Result.Numeric
            try:
                result_num = prop_obj.GetPropertyObject("Result.Numeric", 0)
                if result_num:
                    result_num.NumericFormat = format_str
                    del result_num
            except Exception:
                pass
            try:
                prop_obj.SetValString("Result.Numeric.NumericFormat", 0, format_str)
            except Exception:
                pass

    def _is_format_strifier(self, s: str) -> bool:
        """Check if string looks like a C printf format specifier."""
        if not s:
            return False
        # Format specifiers: %[flags][width][.precision][length]specifier
        # flags: #, 0, -, +, space
        # width: digits
        # precision: .digits
        # length: hh, h, l, ll, j, z, t, L
        # specifier: d, i, u, o, x, X, f, F, e, E, g, G, a, A, c, s, p, n, %
        return bool(re.match(r'^%[#0\-+ ]?([0-9]+|\*)?(\.[0-9]+|\.*\*)?(hh|h|l|ll|j|z|t|L)?[diuooxXfFeEgGcCaAnpsSp%]$', s))

    def _looks_like_units(self, s: str) -> bool:
        """Check if string looks like a unit of measurement (not a number or format)."""
        if not s:
            return False
        # Units are typically alphabetic strings like Vdc, VAC, mV, Hz, MHz, Ohm, kOhm
        # Not a number (int or float)
        try:
            float(s)
            return False  # It's a number, not units
        except ValueError:
            pass
        # Not a format specifier
        if self._is_format_strifier(s):
            return False
        # Not hex
        if s.startswith('0x') or s.startswith('0X'):
            return False
        # Looks like units if it contains only letters (possibly with common prefix/suffix like 'm', 'k', 'M')
        return bool(re.match(r'^[a-zA-Z]+$', s)) or bool(re.match(r'^[a-zA-Z]+[a-zA-Z0-9]*$', s))

    def _apply_settings_expressions(self, prop_obj, settings_str: str, step=None) -> None:
        """Apply settings from settings column.

        Settings format: "Key=Value; Key2=Value2; ..."
        Supported keys: PreExpr, StatusExpr, PostExpr, ConditionExpr,
                        LoadOpt, Mode, Wait, LoopType, LoopWhile, LoopCount,
                        LoopInitialize, AdditionalResults, Breakpoint
        """
        settings_str = settings_str.strip()
        if not settings_str:
            return

        parts = self._split_settings(settings_str)

        for part in parts:
            part = part.strip()
            if not part:
                continue

            # Check for AdditionalResults first (has complex value)
            if part.startswith("AdditionalResults="):
                self._apply_additional_results(prop_obj, part)
                continue

            # Check for Breakpoint (uses Step.SetBreakSettings, not SetValString)
            if part.startswith("Breakpoint=") and step is not None:
                self._apply_breakpoint(step, part[len("Breakpoint="):])
                continue

            # Check against known settings keys
            matched = False
            for key, (prop_path, flags) in SETTINGS_PROPERTY_MAP.items():
                prefix = f"{key}="
                if part.startswith(prefix):
                    value = part[len(prefix):].strip()
                    if value:
                        try:
                            prop_obj.SetValString(prop_path, flags, value)
                        except Exception:
                            pass
                    matched = True
                    break

            # Handle unrecognized settings silently

    def _apply_additional_results(self, prop_obj, part: str) -> None:
        """Apply AdditionalResults from settings.

        AdditionalResults contains comma-separated result names.
        e.g., AdditionalResults=ResStr("NI_WAIT_STEP_TYPE", "TIME_TO_WAIT")
        """
        results_str = part[20:].strip()  # "AdditionalResults=" is 20 chars
        if not results_str:
            return
        try:
            hints = prop_obj.GetPropertyObject("TS.AdditionalResultsHints", 0)
            if not hints:
                return
            result_names = self._split_comma_results(results_str)
            hints.SetNumElements(len(result_names))
            for i, name in enumerate(result_names):
                try:
                    elem = hints.GetPropertyObject(f"[{i}]", 0)
                    elem.SetValString("Name", 0, name)
                    elem.SetValString("ValueToLog", 0, name)
                    del elem
                except Exception:
                    pass
            del hints
        except Exception:
            pass

    def _apply_breakpoint(self, step, value_str: str) -> None:
        """Apply breakpoint settings via Step.SetBreakSettings.

        Format: "isSet,enabled,passCount,condition"
        e.g., "1,1,0," or "1,1,3,x>100"
        """
        parts = value_str.split(",", 3)
        if len(parts) < 2:
            return
        try:
            is_set = parts[0].strip() == "1"
            enabled = parts[1].strip() == "1"
            pass_count = int(parts[2].strip()) if len(parts) > 2 and parts[2].strip() else 0
            condition = parts[3].strip() if len(parts) > 3 else ""
            step.SetBreakSettings(is_set, enabled, pass_count, condition)
        except Exception:
            pass

    def _split_settings(self, settings_str: str) -> List[str]:
        """Split settings string by semicolons, handling nested parentheses."""
        parts = []
        current = ""
        depth = 0
        for ch in settings_str:
            if ch == '(':
                depth += 1
                current += ch
            elif ch == ')':
                depth -= 1
                current += ch
            elif ch == ';' and depth == 0:
                if current.strip():
                    parts.append(current.strip())
                current = ""
            else:
                current += ch
        if current.strip():
            parts.append(current.strip())
        return parts

    def _split_comma_results(self, results_str: str) -> List[str]:
        """Split comma-separated results, respecting parentheses."""
        parts = []
        current = ""
        depth = 0
        for ch in results_str:
            if ch == '(':
                depth += 1
                current += ch
            elif ch == ')':
                depth -= 1
                current += ch
            elif ch == ',' and depth == 0:
                if current.strip():
                    parts.append(current.strip())
                current = ""
            else:
                current += ch
        if current.strip():
            parts.append(current.strip())
        return parts

    def _apply_wait(self, prop_obj, tc: ParsedTestCase) -> None:
        """Apply NI_Wait time expression."""
        time_expr = ""
        if tc.settings and "SeqCallName=" not in tc.settings:
            for part in tc.settings.split(";"):
                if "TimeExpr=" in part:
                    time_expr = part.split("TimeExpr=", 1)[1].strip()
                    break

        if not time_expr and tc.vi_path:
            match = re.search(r"Wait\s+(\d+\.?\d*)([ms])", tc.vi_path, re.IGNORECASE)
            if match:
                value = float(match.group(1))
                unit = match.group(2).lower()
                seconds = value if unit == "s" else value / 1000.0
                time_expr = str(seconds)

        if not time_expr and tc.wait_time:
            time_expr = tc.wait_time

        if time_expr:
            try:
                prop_obj.SetValString("TimeExpr", 0, time_expr)
            except Exception:
                pass

    def _group_cases_by_step_group(self, cases: List[ParsedTestCase]) -> Dict[str, List[ParsedTestCase]]:
        """Group cases by step group name."""
        groups = {"startup": [], "main": [], "cleanup": []}
        for tc in cases:
            group_key = tc.step_group if tc.step_group in groups else "main"
            groups[group_key].append(tc)
        return groups

    @staticmethod
    def _group_name_to_idx(group_name: str) -> int:
        """Convert group name to user index."""
        mapping = {"startup": 1, "main": 0, "cleanup": 2}
        return mapping.get(group_name, 0)