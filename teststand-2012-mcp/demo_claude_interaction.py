"""
演示：在 Claude Code 中通过 MCP 工具对话式创建 TestStand 序列

模拟一次典型的 Claude Code 对话 —— 用户说 "创建一个电源测试序列"，
Claude 自动调用 MCP 工具完成创建。

此脚本通过 stdio JSON-RPC 协议与 MCP 服务器通信，展示实际交互过程。
"""
import subprocess
import json
import sys

MCP_SERVER = [r"D:\Python\Python310-32\python.exe", r"E:\agent\teststand-2012-mcp\mcp_server.py"]


class McpClient:
    """简易 MCP stdio 客户端，模拟 Claude Code 的工具调用"""

    def __init__(self):
        self.proc = subprocess.Popen(
            MCP_SERVER,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
        )
        self._next_id = 1
        self._initialize()

    def _send(self, method, params=None):
        """发送 JSON-RPC 请求"""
        req = {"jsonrpc": "2.0", "id": self._next_id, "method": method, "params": params or {}}
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()
        self._next_id += 1
        return self._recv()

    def _notify(self, method, params=None):
        """发送通知（无 id）"""
        req = {"jsonrpc": "2.0", "method": method, "params": params or {}}
        self.proc.stdin.write(json.dumps(req) + "\n")
        self.proc.stdin.flush()

    def _recv(self):
        """接收响应"""
        line = self.proc.stdout.readline()
        return json.loads(line) if line.strip() else None

    def _initialize(self):
        self._send("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "claude-code-demo", "version": "1.0"},
        })
        self._notify("notifications/initialized")

    def call_tool(self, name, args=None):
        return self._send("tools/call", {"name": name, "arguments": args or {}})

    def close(self):
        self.proc.stdin.close()
        self.proc.wait()


def show(result, indent=0):
    """格式化显示工具返回结果"""
    prefix = " " * indent
    if "result" in result:
        for item in result["result"]["content"]:
            text = item["text"]
            for line in text.split("\n"):
                print(f"{prefix}  → {line}")
    elif "error" in result:
        print(f"{prefix}  [ERROR] {result['error']['message']}")


# ═══════════════════════════════════════════════════════════
# 模拟对话: 用户说 "帮我创建一个电源模块的自动化测试序列"
# ═══════════════════════════════════════════════════════════

print("=" * 70)
print("  Claude Code × TestStand 2012 MCP — 对话式建序列演示")
print("=" * 70)

client = McpClient()

# 用户: "帮我创建一个电源模块的自动化测试序列"
# Claude 的思考: 需要先创建文件，添加变量，然后分 Setup/Main/Cleanup 添加步骤

print("\n[User] 用户: 帮我创建一个电源模块的自动化测试序列，产品型号是 PWR-2026")

# Step 1: 创建序列文件
print("\n[Tool] Claude 调用: ts_create_sequence_file")
r = client.call_tool("ts_create_sequence_file")
show(r)

# Step 2: 添加全局变量
print("\n[Tool] Claude 调用: ts_add_file_global (型号)")
r = client.call_tool("ts_add_file_global", {
    "name": "ProductModel", "type": "String", "default_value": "PWR-2026"
})
show(r)

print("\n[Tool] Claude 调用: ts_add_file_global (序列号)")
r = client.call_tool("ts_add_file_global", {
    "name": "SerialNumber", "type": "String", "default_value": ""
})
show(r)

print("\n[Tool] Claude 调用: ts_add_file_global (测试结果)")
r = client.call_tool("ts_add_file_global", {
    "name": "OverallResult", "type": "String", "default_value": "Pending"
})
show(r)

# Step 3: Setup — 操作员提示 + 等待设备初始化
print("\n[Tool] Claude 调用: ts_set_step_group → setup")
r = client.call_tool("ts_set_step_group", {"group": "setup"})
show(r)

print("\n[Tool] Claude 调用: ts_add_message_popup (初始化提示)")
r = client.call_tool("ts_add_message_popup", {
    "message": "请连接 PWR-2026 电源模块并确认...", "name": "设备初始化"
})
show(r)

print("\n[Tool] Claude 调用: ts_add_wait (等待预热)")
r = client.call_tool("ts_add_wait", {"seconds": 2, "name": "设备预热"})
show(r)

# Step 4: Main — 核心测试项
print("\n[Tool] Claude 调用: ts_set_step_group → main")
r = client.call_tool("ts_set_step_group", {"group": "main"})
show(r)

print("\n[Tool] Claude 调用: ts_add_numeric_limit_test (输入电压)")
r = client.call_tool("ts_add_numeric_limit_test", {
    "name": "输入电压测试",
    "low": 85, "high": 264,
})
show(r)

print("\n[Tool] Claude 调用: ts_add_numeric_limit_test (输出电压)")
r = client.call_tool("ts_add_numeric_limit_test", {
    "name": "12V 输出精度",
    "low": 11.88, "high": 12.12,
})
show(r)

print("\n[Tool] Claude 调用: ts_add_numeric_limit_test (纹波)")
r = client.call_tool("ts_add_numeric_limit_test", {
    "name": "输出纹波测试",
    "low": 0, "high": 120,
    "measurement_expr": "Step.Result.Numeric",
})
show(r)

print("\n[Tool] Claude 调用: ts_add_numeric_limit_test (效率)")
r = client.call_tool("ts_add_numeric_limit_test", {
    "name": "满载效率",
    "low": 85, "high": 100,
})
show(r)

print("\n[Tool] Claude 调用: ts_add_string_value_test (固件版本)")
r = client.call_tool("ts_add_string_value_test", {
    "name": "固件版本检查",
    "expected": "FW-3.2.1",
})
show(r)

# Step 5: Cleanup — 报告 + 清理
print("\n[Tool] Claude 调用: ts_set_step_group → cleanup")
r = client.call_tool("ts_set_step_group", {"group": "cleanup"})
show(r)

print("\n[Tool] Claude 调用: ts_add_statement (设置结果)")
r = client.call_tool("ts_add_statement", {
    "name": "记录测试结论",
    "expression": 'FileGlobals.OverallResult = "PASS"',
})
show(r)

print("\n[Tool] Claude 调用: ts_add_message_popup (完成提示)")
r = client.call_tool("ts_add_message_popup", {
    "message": "PWR-2026 测试完成！请取下设备。", "name": "测试完成"
})
show(r)

# Step 6: 查看摘要
print("\n[Tool] Claude 调用: ts_get_info")
r = client.call_tool("ts_get_info")
show(r)

# Step 7: 保存
print("\n[Tool] Claude 调用: ts_save_sequence_file")
r = client.call_tool("ts_save_sequence_file", {
    "path": r"C:\Temp\PWR-2026_power_test.seq"
})
show(r)

# 关闭
client.call_tool("ts_close_sequence_file")
client.close()

print("\n" + "=" * 70)
print("  [OK] 演示完成！")
print("  文件: C:\\Temp\\PWR-2026_power_test.seq")
print("=" * 70)
