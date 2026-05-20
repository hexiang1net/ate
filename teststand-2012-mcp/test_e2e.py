"""端到端测试：创建 TestStand 序列文件"""
import sys
sys.path.insert(0, r"E:\agent\teststand-2012-mcp")
from sequence_builder import SequenceBuilder

builder = SequenceBuilder()
builder.create_file()
print("1. 创建序列文件: OK")

builder.set_sequence_step_group("setup")
builder.add_message_popup("开始测试...", name="提示开始")
builder.add_wait(1, name="预热等待")
print("2. Setup 步骤: OK")

builder.set_sequence_step_group("main")
builder.add_numeric_limit_test("电压测试", low=4.5, high=5.5)
builder.add_numeric_limit_test("电流测试", low=0.1, high=2.0)
builder.add_string_value_test("型号验证", expected="ABC-123")
print("3. Main 步骤: OK")

builder.set_sequence_step_group("cleanup")
builder.add_statement("清理", '"清理完成"')
builder.add_message_popup("测试完成", name="提示结束")
print("4. Cleanup 步骤: OK")

builder.add_file_global("SerialNumber", "String", "")
print("5. 全局变量: OK")

print("6. 序列列表:", builder.get_sequence_names())
print("7. 步骤统计:", builder.get_step_count())

builder.save(r"C:\Temp\test_demo.seq")
print("8. 保存成功: C:\\Temp\\test_demo.seq")

builder.close()
print("9. 关闭完成")
