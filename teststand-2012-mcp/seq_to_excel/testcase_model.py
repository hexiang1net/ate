"""Test case data models for ATE test plan generation."""
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ModuleParameterInfo:
    """Minimal module parameter info for test case model."""
    name: str = ""
    type: str = "Unknown"
    direction: str = "0"
    value_expr: str = ""
    default_value: str = ""
    use_default_value: bool = False
    type_description: str = ""
    enum_values: List[str] = field(default_factory=list)  # 枚举常量名列表，索引=枚举值


@dataclass
class TestCase:
    """ATE test case corresponding to one row in the template.

    Maps to columns in "ATE test item check list" sheet.
    """
    # Step identification
    step_no: str = ""           # "1_1", "2_2_1" format - Step_N0 column
    step: str = ""              # "startup"/"main"/"cleanup" - Step column
    sub_step: str = ""          # Sub_Step column

    # Test project info
    test_project: str = ""      # Test project items - 步骤名称
    step_type: str = ""         # step type column (call/flow/action/etc)
    limits: str = ""            # limits column (expression only)
    unit: str = ""              # unit column
    format: str = ""            # format column
    run_mode: str = ""          # run mode column (e.g., Skip, Normal)
    wait_seconds: str = ""         # wait(s) column
    additional_results: str = "" # additional results column
    settings: str = ""          # settings column
    comments: str = ""          # comments column
    description: str = ""       # Describition of Test Requirments - 步骤 comment

    # Signal info (from step parameters)
    input_signals: str = ""
    output_loads: str = ""
    precondition: str = ""

    # VI info
    vi_path: str = ""            # Command column - VI full path (manual entry)
    instrument_vi: str = ""      # instrument_vi column - VI filename

    # Test limits (from step parameters or module parameters)
    test_point: str = ""
    usl: str = ""                # Upper spec limit
    lsl: str = ""                # Lower spec limit
    measurement_value: str = ""
    precision: str = ""          # 精度(%)

    # Method and equipment
    method_check: str = ""
    equipment: str = ""          # Equipment Solution - device address
    parameter: str = ""          # Parameter column

    # Additional info
    logfile_confirm: str = ""
    te_comments: str = ""
    remarks: str = ""

    # Raw data for reference
    module_parameters: List[ModuleParameterInfo] = field(default_factory=list)
    adapter: str = ""

    def get_step_group_code(self) -> str:
        """Convert step group to template code."""
        mapping = {"Main": "main", "Setup": "startup", "Cleanup": "cleanup"}
        return mapping.get(self.step, self.step)


@dataclass
class ViParameter:
    """VI parameter record for vi_parameter_table sheet."""
    step_no: str = ""
    instrument_vi_name: str = ""
    parameters: List[str] = field(default_factory=list)


@dataclass
class VariableInfo:
    """Variable information for the variable table sheet."""
    name: str = ""
    value: str = ""
    type: str = ""
    container: str = ""  # "FileGlobals", "Locals", "StationGlobals", etc.


@dataclass
class TestCaseReport:
    """Complete test case report for a sequence file."""
    file_path: str = ""
    test_cases: List[TestCase] = field(default_factory=list)
    vi_parameters: List[ViParameter] = field(default_factory=list)
    sequence_name: str = ""
    variables: List[VariableInfo] = field(default_factory=list)

    def get_main_step_count(self) -> int:
        """Get count of main step entries."""
        return len([tc for tc in self.test_cases if tc.step == "main"])

    def get_startup_step_count(self) -> int:
        """Get count of startup step entries."""
        return len([tc for tc in self.test_cases if tc.step == "startup"])