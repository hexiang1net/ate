"""将 LLM 返回的 JSON 解析为 TestCase 模型。"""
import logging
from typing import List

from ..seq_to_excel.testcase_model import TestCase, TestCaseReport, VariableInfo

logger = logging.getLogger(__name__)

# TestCase 字段映射: JSON key → TestCase 属性名
_FIELD_MAP = {
    "step_no": "step_no",
    "step": "step",
    "test_project": "test_project",
    "description": "",
    "step_type": "step_type",
    "limits": "limits",
    "usl": "usl",
    "lsl": "lsl",
    "unit": "unit",
    "format": "format",
    "run_mode": "run_mode",
    "wait_time": "wait_time",
    "adapter": "adapter",
    "additional_results": "additional_results",
    "settings": "settings",
    "comments": "comments",
    "input_signals": "",
    "output_loads": "",
    "precondition": "",
    "test_point": "",
    "method_check": "",
    "equipment": "equipment",
}


def extract_test_cases(data: dict, doc_path: str = "") -> TestCaseReport:
    """从 LLM 返回的 JSON 数据构建 TestCaseReport。"""
    report = TestCaseReport(file_path=doc_path)

    # 提取测试用例
    for item in data.get("test_cases", []):
        tc = _parse_test_case(item)
        if tc:
            report.test_cases.append(tc)

    # 提取变量
    for var in data.get("variables", []):
        vi = VariableInfo(
            name=var.get("name", ""),
            value=var.get("value", ""),
            type=var.get("type", ""),
            container=var.get("container", "FileGlobals"),
        )
        if vi.name:
            report.variables.append(vi)

    # 修正步骤编号
    _fix_step_numbers(report.test_cases)

    return report


def _parse_test_case(item: dict) -> TestCase:
    """解析单个测试用例。"""
    tc = TestCase()

    for json_key, attr_name in _FIELD_MAP.items():
        value = item.get(json_key)
        if value is not None and value != "":
            setattr(tc, attr_name, str(value))

    # 标准化 step 字段
    tc.step = _normalize_step(tc.step)

    # 标准化 step_type
    tc.step_type = _normalize_step_type(tc.step_type)

    return tc


def _normalize_step(step: str) -> str:
    """标准化阶段名称。"""
    s = step.lower().strip()
    if s in ("startup", "setup", "init", "初始化"):
        return "startup"
    if s in ("cleanup", "teardown", "清理"):
        return "cleanup"
    return "main"


def _normalize_step_type(step_type: str) -> str:
    """标准化步骤类型。"""
    s = step_type.strip()
    type_map = {
        "Action": "Action",
        "action": "Action",
        "NumericLimitTest": "NumericLimitTest",
        "numericlimittest": "NumericLimitTest",
        "numeric_limit_test": "NumericLimitTest",
        "数值测试": "NumericLimitTest",
        "SequenceCall": "SequenceCall",
        "sequencecall": "SequenceCall",
        "sequence_call": "SequenceCall",
        "NI_Wait": "NI_Wait",
        "ni_wait": "NI_Wait",
        "等待": "NI_Wait",
        "NI_Flow_If": "NI_Flow_If",
        "if": "NI_Flow_If",
        "NI_Flow_Else": "NI_Flow_Else",
        "else": "NI_Flow_Else",
        "NI_Flow_End": "NI_Flow_End",
        "end": "NI_Flow_End",
        "Lock": "Lock",
        "NI_Lock": "NI_Lock",
        "Unlock": "Unlock",
        "NI_Unlock": "NI_Unlock",
    }
    return type_map.get(s, s if s else "Action")


def _fix_step_numbers(test_cases: List[TestCase]) -> None:
    """修正步骤编号，确保连续且格式正确。"""
    counters = {"startup": 0, "main": 0, "cleanup": 0}

    for tc in test_cases:
        group = tc.step
        if group not in counters:
            group = "main"

        # 如果没有步骤编号或编号格式不对，自动生成
        if not tc.step_no or not _is_valid_step_no(tc.step_no):
            counters[group] += 1
            prefix = {"startup": "1", "main": "2", "cleanup": "3"}[group]
            tc.step_no = f"{prefix}_{counters[group]}"


def _is_valid_step_no(step_no: str) -> bool:
    """检查步骤编号格式是否有效。"""
    parts = step_no.split("_")
    return all(p.isdigit() for p in parts) and len(parts) >= 2
