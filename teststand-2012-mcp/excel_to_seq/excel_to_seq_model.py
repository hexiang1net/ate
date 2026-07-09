"""Data models for Excel to TestStand sequence conversion."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ParsedTestCase:
    """Parsed test case from Excel template.

    Column mapping (Sheet 1: ATE test item check list, data starts at row 5).
    Column order aligned with seq_to_excel (excel_generator.py) as the standard:
        A  step_no            B  step_group         C  test_project
        D  description        E  step_type          F  instrument_vi
        G  limits             H  usl                I  lsl
        J  unit               K  format             L  run_mode
        M  wait_time          N  adapter            O  additional_results
        P  settings           Q  comments           R  input_signals
        S  output_loads       T  precondition       U  vi_path / command
        V  test_point         W  measurement_value  X  precision
        Y  method_check       Z  equipment          AA parameter
        AB logfile_confirm    AC te_comments        AD remarks
    """
    step_no: str                      # A: Step_No
    step_group: str                   # B: startup / main / cleanup
    test_project: str                 # C: Test project items
    step_type: str = "Action"         # E: Action, PassFailTest, NumericLimitTest, NI_Flow_If, etc.
    instrument_vi: str = ""           # F: VI filename or ActiveX identifier
    limits: str = ""                  # G: limit expression, e.g. "241<=x<=261"
    unit: str = ""                    # J: unit, e.g. "Vdc"
    format: str = ""                  # K: format, e.g. "%.2f"
    run_mode: str = ""                # L: run mode, e.g. "Skip"
    wait_time: str = ""               # M: wait(s), e.g. "0.1"
    adapter: str = ""                 # N: adapter name
    additional_results: str = ""      # O: additional results (ResStr, AR.Parms)
    settings: str = ""                # P: PreExpr/StatusExpr/PostExpr/etc.
    comments: str = ""                # Q: comments
    description: str = ""             # D: Description of Test Requirements
    vi_path: str = ""                 # U: VI path (Command - manual entry, usually empty)
    usl: str = ""                     # H: Upper spec limit
    lsl: str = ""                     # I: Lower spec limit
    method_check: str = ""            # Y: Method check
    equipment: str = ""               # Z: Equipment solution


@dataclass
class ParsedViParameter:
    """Parsed VI parameter from Sheet 2 (vi_parameter_table)."""
    step_no: str
    instrument_vi_name: str
    param_names: List[str] = field(default_factory=list)
    param_values: List[str] = field(default_factory=list)


@dataclass
class ParsedVariable:
    """Parsed variable from Sheet 3 (Variables)."""
    container: str        # "FileGlobals" or "Locals.<sequence_name>"
    name: str             # Variable name, supports dot-notation nesting
    value: str            # Default value
    var_type: str         # "Number", "String", "Boolean", "Array"


@dataclass
class SubSequenceInfo:
    """Information about a sub-sequence to be created."""
    parent_step_no: str       # e.g., "2_1"
    seq_name: str             # e.g., "SubSeq_2_1"
    steps: List[ParsedTestCase] = field(default_factory=list)
