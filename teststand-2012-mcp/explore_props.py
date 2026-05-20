"""探查步骤属性的正确 API 调用方式"""
import sys
sys.path.insert(0, r"E:\agent\teststand-2012-mcp")
from ts_engine import get_engine

engine = get_engine().engine

def explore_step(adapter, step_type, known_props):
    """测试能设置哪些属性"""
    print(f"\n=== {step_type} ===")
    step = engine.NewStep(adapter, step_type)
    step_obj = step.AsPropertyObject()
    for prop_name in known_props:
        try:
            step_obj.SetValNumber(prop_name, 0, 42.0)
            print(f"  SetNumber OK: {prop_name}")
        except:
            try:
                step_obj.SetValString(prop_name, 0, "test_value")
                print(f"  SetString OK: {prop_name}")
            except Exception as e:
                err = str(e)[:80]
                print(f"  FAIL: {prop_name} -> {err}")

# NumericLimitTest — 测试可能的数据表达式属性
numeric_props = [
    "Limits.Low", "Limits.High", "Limits.String",
    "DataExpr", "Data", "DataSourcExpr",
    "Step.Result.Numeric",
    "Module.DataExpr", "Module.Data",
    "Result.Numeric",
]
explore_step("None Adapter", "NumericLimitTest", numeric_props)

# NI_Wait
wait_props = [
    "TimeExpr", "Time", "WaitTime",
    "Module.TimeExpr", "Module.Time",
    "Step.TimeExpr", "Step.Time",
]
explore_step("None Adapter", "NI_Wait", wait_props)

# MessagePopup
msg_props = [
    "MessageExpr", "Message", "MsgExpr",
    "Module.MessageExpr", "Module.Message",
    "ButtonExpr", "TitleExpr",
]
explore_step("None Adapter", "MessagePopup", msg_props)

# Statement
stmt_props = [
    "Expr", "Expression",
    "Module.Expr", "Module.Expression",
]
explore_step("None Adapter", "Statement", stmt_props)

# StringValueTest
str_props = [
    "Limits.String", "Limits.Low", "Limits.High",
    "Result.String", "DataExpr",
    "String", "ExpectedString",
]
explore_step("None Adapter", "StringValueTest", str_props)

# SequenceCall
seq_props = [
    "Module.SequenceName", "Module.AsSequenceCallModule.SequenceName",
    "Module.UseCurFile",
    "SequenceName",
]
explore_step("Sequence Adapter", "SequenceCall", seq_props)

# LabVIEW Action (G Flexible VI Adapter)
action_props = [
    "ModulePath", "Module",
    "Module.LabVIEWPath", "Module.VIPath",
]
explore_step("G Flexible VI Adapter", "Action", action_props)

print("\n=== 完成 ===")
