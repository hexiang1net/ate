"""
通过 MCP JSON-RPC 协议创建「电源模块自动化测试序列」
模拟 Claude Code 实际调用 MCP 工具的完整过程
"""
import subprocess
import json
import os

os.environ["PYTHONIOENCODING"] = "utf-8"

MCP_SERVER = [r"D:\Python\Python310-32\python.exe", r"E:\agent\teststand-2012-mcp\mcp_server.py"]

class McpSession:
    def __init__(self):
        self.proc = subprocess.Popen(
            MCP_SERVER, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
            stderr=subprocess.PIPE, text=True, encoding="utf-8", errors="replace"
        )
        self._id = 1
        self._send("initialize", {"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"claude","version":"1.0"}})
        self._notify("notifications/initialized")

    def _send(self, method, params=None):
        req = {"jsonrpc":"2.0","id":self._id,"method":method,"params":params or {}}
        self.proc.stdin.write(json.dumps(req, ensure_ascii=False)+"\n")
        self.proc.stdin.flush()
        self._id += 1
        return json.loads(self.proc.stdout.readline())

    def _notify(self, method, params=None):
        req = {"jsonrpc":"2.0","method":method,"params":params or {}}
        self.proc.stdin.write(json.dumps(req, ensure_ascii=False)+"\n")
        self.proc.stdin.flush()

    def tool(self, name, args=None):
        r = self._send("tools/call", {"name":name,"arguments":args or {}})
        text = r.get("result",{}).get("content",[{}])[0].get("text","") if "result" in r else r.get("error",{}).get("message","???")
        return text

    def close(self):
        self.proc.stdin.close()
        self.proc.wait()


def step(msg, tool, args=None):
    """执行一个 MCP 工具调用并打印结果"""
    text = session.tool(tool, args)
    status = "[OK]" if text.startswith("[成功]") else "[FAIL]"
    print(f"  {tool:34s} {status}")
    if args:
        for k, v in (args or {}).items():
            if k != "properties":
                print(f"    {k}: {v}")


session = McpSession()

print("=" * 65)
print("  Claude Code x TestStand 2012 MCP")
print("  电源模块自动化测试序列 - 创建过程")
print("=" * 65)

# ═══════════════════════════════════════════════════════════
# Step 1: 创建文件
# ═══════════════════════════════════════════════════════════
print("\n>>> 1. 创建新序列文件")
step("创建文件", "ts_create_sequence_file")

# ═══════════════════════════════════════════════════════════
# Step 2: 全局变量
# ═══════════════════════════════════════════════════════════
print("\n>>> 2. 添加全局变量")
step("产品型号", "ts_add_file_global",
     {"name":"ProductModel","type":"String","default_value":"PWR-9000"})
step("序列号", "ts_add_file_global",
     {"name":"SerialNumber","type":"String","default_value":""})
step("操作员", "ts_add_file_global",
     {"name":"OperatorName","type":"String","default_value":""})
step("测试温度", "ts_add_file_global",
     {"name":"TestTemperature","type":"Number","default_value":"25"})
step("通过计数", "ts_add_file_global",
     {"name":"PassCount","type":"Number","default_value":"0"})
step("失败计数", "ts_add_file_global",
     {"name":"FailCount","type":"Number","default_value":"0"})

# ═══════════════════════════════════════════════════════════
# Step 3: Setup
# ═══════════════════════════════════════════════════════════
print("\n>>> 3. Setup 阶段")
step("切换 Setup", "ts_set_step_group", {"group":"setup"})
step("操作提示", "ts_add_message_popup",
     {"name":"操作提示","message":"请连接 PWR-9000 电源模块，确认接线正确后点击确定"})
step("扫码等待", "ts_add_wait", {"name":"等待扫码枪","seconds":3})
step("记录操作员", "ts_add_statement",
     {"name":"记录操作员","expression":'FileGlobals.OperatorName = "李工"'})

# ═══════════════════════════════════════════════════════════
# Step 4: Main - 核心测试
# ═══════════════════════════════════════════════════════════
print("\n>>> 4. Main 阶段 - 电气性能测试")
step("切换 Main", "ts_set_step_group", {"group":"main"})

# 4.1 电压测试组
print("  --- 电压测试 ---")
step("输入电压范围", "ts_add_numeric_limit_test",
     {"name":"输入电压范围测试","low":85,"high":264})
step("12V输出精度", "ts_add_numeric_limit_test",
     {"name":"12V 主输出精度","low":11.88,"high":12.12})
step("5V待机输出", "ts_add_numeric_limit_test",
     {"name":"5V 待机输出","low":4.85,"high":5.15})
step("3.3V输出", "ts_add_numeric_limit_test",
     {"name":"3.3V 辅助输出","low":3.20,"high":3.40})

# 4.2 电流/功率测试组
print("  --- 电流/功耗测试 ---")
step("待机功耗", "ts_add_numeric_limit_test",
     {"name":"待机功耗测试","low":0,"high":0.5})
step("半载电流", "ts_add_numeric_limit_test",
     {"name":"半载输出电流","low":1.8,"high":2.2})
step("满载电流", "ts_add_numeric_limit_test",
     {"name":"满载输出电流","low":3.8,"high":4.2})
step("满载效率", "ts_add_numeric_limit_test",
     {"name":"满载效率测试","low":88,"high":100})

# 4.3 保护功能测试
print("  --- 保护功能测试 ---")
step("过压保护", "ts_add_numeric_limit_test",
     {"name":"过压保护阈值","low":13.2,"high":13.8})
step("短路保护", "ts_add_string_value_test",
     {"name":"短路保护响应","expected":"PROTECTED"})

# 4.4 通信与标识测试
print("  --- 通信/标识测试 ---")
step("固件版本", "ts_add_string_value_test",
     {"name":"固件版本验证","expected":"PWR-FW-3.2.1"})
step("I2C通信", "ts_add_string_value_test",
     {"name":"I2C 通信检查","expected":"I2C_OK"})

# ═══════════════════════════════════════════════════════════
# Step 5: 子序列 - 老化测试
# ═══════════════════════════════════════════════════════════
print("\n>>> 5. 创建老化测试子序列")
step("创建子序列", "ts_add_sequence", {"name":"BurnInTest"})
step("切换到子序列", "ts_use_sequence", {"sequence_name":"BurnInTest"})
step("(子)切换Main", "ts_set_step_group", {"group":"main"})
step("(子)老化开始", "ts_add_message_popup",
     {"name":"老化开始","message":"开始 2 小时老化测试，请勿断电..."})
step("(子)设时长", "ts_add_statement",
     {"name":"设定时长","expression":"Locals.BurnInHours = 2"})
step("(子)高温测试", "ts_add_numeric_limit_test",
     {"name":"高温满载运行","low":11.5,"high":12.5})
step("(子)老化完成", "ts_add_message_popup",
     {"name":"老化完成","message":"老化测试通过，请进行下一步测试"})

# ═══════════════════════════════════════════════════════════
# Step 6: 回到 MainSequence - 条件判断 + 调用子序列
# ═══════════════════════════════════════════════════════════
print("\n>>> 6. 回 MainSequence - 调用老化 + 条件判断")
step("回 MainSeq", "ts_use_sequence", {"sequence_name":"MainSequence"})
step("切 Main", "ts_set_step_group", {"group":"main"})

# 调用老化子序列
step("调用老化", "ts_add_sequence_call",
     {"name":"执行老化测试","sequence_name":"BurnInTest"})

# 条件判断: 测试结果判定
step("If 条件", "ts_add_step", {
    "step_type":"If",
    "name":"测试结果判定",
    "properties":{"Step.Result.CondExpr":'FileGlobals.FailCount == 0'}
})
step("通过弹窗", "ts_add_message_popup",
     {"name":"测试通过","message":"PWR-9000 全部测试通过！请贴合格标签"})
step("Else", "ts_add_step", {"step_type":"Else","name":"失败分支"})
step("失败弹窗", "ts_add_message_popup",
     {"name":"测试失败","message":"测试失败！请检查模块并重新测试"})
step("End", "ts_add_step", {"step_type":"End","name":"结束判定"})

# ═══════════════════════════════════════════════════════════
# Step 7: Cleanup
# ═══════════════════════════════════════════════════════════
print("\n>>> 7. Cleanup 阶段")
step("切换 Cleanup", "ts_set_step_group", {"group":"cleanup"})
step("更新计数", "ts_add_statement",
     {"name":"更新通过计数","expression":"FileGlobals.PassCount = FileGlobals.PassCount + 1"})
step("完成提示", "ts_add_message_popup",
     {"name":"测试完成","message":"PWR-9000 电源模块测试流程结束，请取下设备"})
step("等待取件", "ts_add_wait", {"name":"等待取件","seconds":1})

# ═══════════════════════════════════════════════════════════
# Step 8: 查看摘要 & 保存
# ═══════════════════════════════════════════════════════════
print("\n>>> 8. 查看摘要")
info = session.tool("ts_get_info")
print(info)

print("\n>>> 9. 保存文件")
result = session.tool("ts_save_sequence_file",
                      {"path": r"D:\TestSequences\PWR9000_PowerTest.seq"})
print(result)

session.tool("ts_close_sequence_file")
session.close()

# 验证文件
if os.path.exists(r"D:\TestSequences\PWR9000_PowerTest.seq"):
    size = os.path.getsize(r"D:\TestSequences\PWR9000_PowerTest.seq")
    print(f"\n文件大小: {size} 字节")
    print("=" * 65)
    print("  创建完成!")
    print("=" * 65)
