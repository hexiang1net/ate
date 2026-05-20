"""
复杂实例：IoT 设备产线测试序列

测试流程:
  Setup:     初始化仪器、预热
  Main:      电压测试 → 电流测试 → 通信测试 → 校准(子序列) → 标签打印
  Cleanup:   关闭仪器、生成报告
"""
import sys
sys.path.insert(0, r"E:\agent\teststand-2012-mcp")
from sequence_builder import SequenceBuilder

builder = SequenceBuilder()
builder.create_file()

# ═══════════════════════════════════════
# 1. 文件级全局变量
# ═══════════════════════════════════════
builder.add_file_global("SerialNumber", "String", "")
builder.add_file_global("OperatorID", "String", "")
builder.add_file_global("TestStationID", "String", "STATION-01")
builder.add_file_global("PassCount", "Number", "0")
builder.add_file_global("FailCount", "Number", "0")

# ═══════════════════════════════════════
# 2. 创建校准子序列
# ═══════════════════════════════════════
builder.add_sequence("CalibrationRoutine")

# 在子序列中添加步骤
builder.use_sequence("CalibrationRoutine")
builder.set_sequence_step_group("main")

builder.add_message_popup("开始自动校准...", name="校准开始提示")
builder.add_numeric_limit_test(
    name="ADC 偏移校准",
    low=-0.01, high=0.01,
    measurement_expr="Step.Result.Numeric",
)
builder.add_numeric_limit_test(
    name="DAC 增益校准",
    low=0.98, high=1.02,
)
builder.add_statement(
    name="记录校准结果",
    expression='Locals.CalibrationOK = (Step.Result.PassFail == "Passed")',
)
builder.add_message_popup("校准完成", name="校准结束提示")

# ═══════════════════════════════════════
# 3. MainSequence
# ═══════════════════════════════════════
builder.use_sequence("MainSequence")

# ── 3.1 Setup 步骤组 ──
builder.set_sequence_step_group("setup")

builder.add_message_popup(
    "请连接 DUT 并扫描序列号...",
    name="操作员提示"
)
builder.add_wait(0.5, name="等待扫码枪输入")
builder.add_statement(
    name="记录操作员",
    expression='FileGlobals.OperatorID = "张三"',
)

# ── 3.2 Main 步骤组 ──
builder.set_sequence_step_group("main")

# 电压测试（含上下限）
builder.add_numeric_limit_test(
    name="5V 电源轨测试",
    low=4.75, high=5.25,
)
builder.add_numeric_limit_test(
    name="3.3V 电源轨测试",
    low=3.14, high=3.47,
)

# 电流测试
builder.add_numeric_limit_test(
    name="待机电流测试",
    low=0.01, high=0.15,
)
builder.add_numeric_limit_test(
    name="满载电流测试",
    low=0.8, high=1.5,
)

# 字符串验证 — 固件版本
builder.add_string_value_test(
    name="固件版本验证",
    expected="v2.1.3",
    measurement_expr='"v2.1.3"',
)

# 通信测试（WiFi MAC 地址读取）
builder.add_string_value_test(
    name="WiFi MAC 地址格式",
    expected="AA:BB:CC:",
    measurement_expr='"AA:BB:CC:DD:EE:FF"',
)

# 调用校准子序列
builder.add_sequence_call(
    sequence_name="CalibrationRoutine",
    name="调用校准流程",
)

# 条件判断：如果校准通过则打印标签
builder.add_step(
    "NI_Flow_If",
    name="校准是否通过?",
    properties={
        "Step.Result.CondExpr": 'Locals.CalibrationOK == True',
    },
)
builder.add_step(
    "MessagePopup",
    name="打印标签",
    properties={
        "MessageExpr": '"正在打印产品标签..."',
    },
)
builder.add_step(
    "NI_Flow_Else",
    name="校准失败",
)
builder.add_message_popup(
    "校准失败！请重新测试。",
    name="校准失败提示",
)
builder.add_step(
    "NI_Flow_End",
    name="结束判断",
)

# ── 3.3 Cleanup 步骤组 ──
builder.set_sequence_step_group("cleanup")

builder.add_statement(
    name="更新计数",
    expression='FileGlobals.PassCount = FileGlobals.PassCount + 1',
)
builder.add_message_popup(
    "测试完成！请取下 DUT。",
    name="测试结束",
)
builder.add_wait(1.0, name="等待取件")

# ═══════════════════════════════════════
# 4. 保存 & 查看摘要
# ═══════════════════════════════════════
output_path = r"C:\Temp\iot_production_test.seq"
builder.save(output_path)

print("=" * 60)
print("   IoT 设备产线测试序列 — 创建完成")
print("=" * 60)
print(f"保存路径: {output_path}")
print(f"\n序列列表: {builder.get_sequence_names()}")

# 各序列步骤统计
for seq_name in builder.get_sequence_names():
    builder.use_sequence(seq_name)
    counts = builder.get_step_count(seq_name)
    print(f"\n[{seq_name}]")
    print(f"  Setup:   {counts['Setup']} 步")
    print(f"  Main:    {counts['Main']} 步")
    print(f"  Cleanup: {counts['Cleanup']} 步")

print(f"\n全局变量: {len(builder.get_file_globals())} 个")
for v in builder.get_file_globals():
    print(f"  {v['name']} ({v['type']}) = {v['defaultValue']}")

builder.close()
print("\n✅ 完成！")
