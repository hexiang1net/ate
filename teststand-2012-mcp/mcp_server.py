"""TestStand 2012 MCP Server —— 通过 MCP 协议创建和管理 TestStand 序列文件"""

import asyncio
import json
import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from ts_engine import get_engine, TestStandEngine
from sequence_builder import SequenceBuilder
from step_types import list_step_types, list_adapters, get_step_type_info, STEP_GROUP_NAMES

server = Server("teststand-2012")

# 当前会话的 Builder（每次创建新文件时重置）
_builder: SequenceBuilder = None


def _get_builder() -> SequenceBuilder:
    """获取当前 Builder，不存在则抛出异常"""
    global _builder
    if _builder is None:
        raise RuntimeError(
            "尚未创建序列文件。"
            "请先调用 create_sequence_file 创建新文件，"
            "或调用 load_sequence_file 加载已有文件。"
        )
    return _builder


# ═══════════════════════════════════════════════════════════
# 工具定义
# ═══════════════════════════════════════════════════════════

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        # ── 文件操作 ──
        Tool(
            name="ts_create_sequence_file",
            description="创建一个新的 TestStand 序列文件（.seq）。这是所有操作的起点，必须先调用此工具才能进行后续操作。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="ts_load_sequence_file",
            description="加载已有的 TestStand 序列文件进行修改。",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "序列文件路径（.seq）",
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="ts_save_sequence_file",
            description="保存当前序列文件到指定路径。保存后仍可继续编辑。",
            inputSchema={
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "保存路径（绝对路径），例如 C:\\Tests\\MySequence.seq",
                    },
                },
                "required": ["path"],
            },
        ),
        Tool(
            name="ts_close_sequence_file",
            description="关闭当前序列文件并释放资源。完成后如需新建文件，请重新调用 ts_create_sequence_file。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),

        # ── 步骤操作 ──
        Tool(
            name="ts_add_step",
            description="向当前序列当前步骤组添加一个步骤。\n\n常用步骤类型:\n- Action: 调用代码模块（VI/DLL/.NET）\n- NumericLimitTest: 数值比较测试\n- StringValueTest: 字符串比较测试\n- MessagePopup: 消息弹窗\n- SequenceCall: 调用子序列\n- Statement: 执行表达式\n- Wait: 等待指定秒数\n- If/Else/While/For: 流程控制\n\n如需绑定代码模块，请使用 ts_add_action。",
            inputSchema={
                "type": "object",
                "properties": {
                    "step_type": {
                        "type": "string",
                        "description": "步骤类型名",
                    },
                    "name": {
                        "type": "string",
                        "description": "步骤名称（可选，默认自动生成）",
                    },
                    "adapter": {
                        "type": "string",
                        "description": "适配器名（可选，根据步骤类型自动选择）",
                    },
                    "properties": {
                        "type": "object",
                        "description": "步骤属性 JSON 对象。键为属性路径（如 Limits.Low），值为属性值。例如 {\"MessageExpr\": '\"Hello World\"', \"TimeExpr\": \"5\"}",
                    },
                },
                "required": ["step_type"],
            },
        ),
        Tool(
            name="ts_add_message_popup",
            description="添加一个弹出消息框步骤。用于向操作员显示提示信息。",
            inputSchema={
                "type": "object",
                "properties": {
                    "message": {
                        "type": "string",
                        "description": "要显示的消息文本",
                    },
                    "name": {
                        "type": "string",
                        "description": "步骤名称（可选，默认 'Message'）",
                    },
                },
                "required": ["message"],
            },
        ),
        Tool(
            name="ts_add_numeric_limit_test",
            description="添加数值限制测试步骤。测量值与上下限比较，自动判定 PASS/FAIL。",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "步骤名称",
                    },
                    "low": {
                        "type": "number",
                        "description": "下限值",
                    },
                    "high": {
                        "type": "number",
                        "description": "上限值",
                    },
                    "measurement_expr": {
                        "type": "string",
                        "description": "测量值表达式（可选，默认 'Step.Result.Numeric'）",
                    },
                    "properties": {
                        "type": "object",
                        "description": "其他属性 JSON 对象",
                    },
                },
                "required": ["name", "low", "high"],
            },
        ),
        Tool(
            name="ts_add_string_value_test",
            description="添加字符串比较测试步骤。比较测量字符串与期望字符串。",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "步骤名称",
                    },
                    "expected": {
                        "type": "string",
                        "description": "期望的字符串值",
                    },
                    "measurement_expr": {
                        "type": "string",
                        "description": "测量值表达式（可选）",
                    },
                },
                "required": ["name", "expected"],
            },
        ),
        Tool(
            name="ts_add_action",
            description="添加 Action 步骤并绑定代码模块。代码模块是实现具体测试逻辑的外部程序（LabVIEW VI、C DLL、.NET 程序集等）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "步骤名称",
                    },
                    "adapter": {
                        "type": "string",
                        "description": "适配器名: LabVIEW Adapter / C/C++ DLL Adapter / .NET Adapter / ActiveX/COM Adapter",
                    },
                    "module_path": {
                        "type": "string",
                        "description": "代码模块文件路径",
                    },
                    "parameters": {
                        "type": "object",
                        "description": "模块参数 JSON 对象",
                    },
                },
                "required": ["name", "adapter", "module_path"],
            },
        ),
        Tool(
            name="ts_add_sequence_call",
            description="添加子序列调用步骤。跳转到另一个序列执行。",
            inputSchema={
                "type": "object",
                "properties": {
                    "sequence_name": {
                        "type": "string",
                        "description": "要调用的子序列名称",
                    },
                    "name": {
                        "type": "string",
                        "description": "步骤名称（可选）",
                    },
                },
                "required": ["sequence_name"],
            },
        ),
        Tool(
            name="ts_add_statement",
            description="添加表达式语句步骤。执行 TestStand 表达式。",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "步骤名称",
                    },
                    "expression": {
                        "type": "string",
                        "description": "TestStand 表达式，例如 'Locals.Result = 1 + 1'",
                    },
                },
                "required": ["name", "expression"],
            },
        ),
        Tool(
            name="ts_add_wait",
            description="添加等待步骤。暂停执行指定秒数。",
            inputSchema={
                "type": "object",
                "properties": {
                    "seconds": {
                        "type": "number",
                        "description": "等待时间（秒）",
                    },
                    "name": {
                        "type": "string",
                        "description": "步骤名称（可选，默认 'Wait'）",
                    },
                },
                "required": ["seconds"],
            },
        ),

        # ── 序列操作 ──
        Tool(
            name="ts_set_step_group",
            description="设置后续 ts_add_step 操作的目标步骤组。TestStand 每个序列有三个步骤组: Setup（初始化）、Main（主体测试）、Cleanup（清理）。默认在 Main 组中操作。",
            inputSchema={
                "type": "object",
                "properties": {
                    "group": {
                        "type": "string",
                        "description": "步骤组名: setup / main / cleanup",
                    },
                },
                "required": ["group"],
            },
        ),
        Tool(
            name="ts_add_sequence",
            description="向当前序列文件添加一个新的子序列。可用于封装可复用的测试逻辑。",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "子序列名称",
                    },
                },
                "required": ["name"],
            },
        ),
        Tool(
            name="ts_use_sequence",
            description="切换到指定序列，后续添加的步骤将作用于该序列。默认操作 MainSequence。",
            inputSchema={
                "type": "object",
                "properties": {
                    "sequence_name": {
                        "type": "string",
                        "description": "序列名称",
                    },
                },
                "required": ["sequence_name"],
            },
        ),

        # ── 变量操作 ──
        Tool(
            name="ts_add_file_global",
            description="添加序列文件全局变量（所有序列共享）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "变量名",
                    },
                    "type": {
                        "type": "string",
                        "description": "变量类型: Number / String / Boolean",
                    },
                    "default_value": {
                        "type": "string",
                        "description": "默认值",
                    },
                },
                "required": ["name", "type", "default_value"],
            },
        ),
        Tool(
            name="ts_add_local_variable",
            description="添加序列局部变量（仅当前序列可见）。",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "变量名",
                    },
                    "type": {
                        "type": "string",
                        "description": "变量类型: Number / String / Boolean",
                    },
                    "default_value": {
                        "type": "string",
                        "description": "默认值",
                    },
                    "sequence_name": {
                        "type": "string",
                        "description": "目标序列名（可选，默认 MainSequence）",
                    },
                },
                "required": ["name", "type", "default_value"],
            },
        ),

        # ── 查询操作 ──
        Tool(
            name="ts_get_info",
            description="获取当前序列文件的摘要信息：序列列表、各步骤组步骤数、全局变量。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="ts_list_step_types",
            description="列出所有可用的内置步骤类型及其说明。用于了解 TestStand 支持的步骤类型。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
        Tool(
            name="ts_list_adapters",
            description="列出所有可用的代码模块适配器。用于了解 TestStand 支持哪些外部代码类型。",
            inputSchema={
                "type": "object",
                "properties": {},
                "required": [],
            },
        ),
    ]


# ═══════════════════════════════════════════════════════════
# 工具实现
# ═══════════════════════════════════════════════════════════

@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    global _builder

    try:
        # ── 文件操作 ──
        if name == "ts_create_sequence_file":
            if _builder is not None:
                _builder.close()
            _builder = SequenceBuilder()
            _builder.create_file()
            return _ok("已创建新的序列文件。现在可以使用其他 ts_add_* 工具来构建测试序列。")

        elif name == "ts_load_sequence_file":
            if _builder is not None:
                _builder.close()
            _builder = SequenceBuilder()
            _builder.load_file(arguments["path"])
            return _ok(f"已加载序列文件: {arguments['path']}\n"
                       f"包含序列: {_builder.get_sequence_names()}")

        elif name == "ts_save_sequence_file":
            builder = _get_builder()
            path = arguments["path"]
            builder.save(path)
            return _ok(f"序列文件已保存到: {path}")

        elif name == "ts_close_sequence_file":
            if _builder is not None:
                _builder.close()
                _builder = None
            return _ok("已关闭序列文件并释放资源。")

        # ── 序列操作 ──
        elif name == "ts_set_step_group":
            builder = _get_builder()
            builder.set_sequence_step_group(arguments["group"])
            return _ok(f"当前步骤组已切换到: {arguments['group']}")

        elif name == "ts_add_sequence":
            builder = _get_builder()
            builder.add_sequence(arguments["name"])
            return _ok(f"已添加子序列: {arguments['name']}")

        elif name == "ts_use_sequence":
            builder = _get_builder()
            builder.use_sequence(arguments["sequence_name"])
            return _ok(f"当前操作序列已切换到: {arguments['sequence_name']}")

        # ── 步骤操作 ──
        elif name == "ts_add_step":
            builder = _get_builder()
            step_type = arguments["step_type"]
            step_name = arguments.get("name")
            adapter = arguments.get("adapter")
            props = arguments.get("properties", {})

            builder.add_step(step_type, name=step_name, adapter=adapter, **props)
            group_names = {0: "Setup", 2: "Main", 1: "Cleanup"}
            current_group = group_names.get(builder._current_step_group, "Main")
            return _ok(f"已在 {current_group} 步骤组中添加 {step_type} 步骤"
                       + (f" ({step_name})" if step_name else ""))

        elif name == "ts_add_message_popup":
            builder = _get_builder()
            builder.add_message_popup(
                arguments["message"],
                name=arguments.get("name", "Message"),
            )
            return _ok(f"已添加消息弹窗步骤: {arguments['message']}")

        elif name == "ts_add_numeric_limit_test":
            builder = _get_builder()
            builder.add_numeric_limit_test(
                name=arguments["name"],
                low=float(arguments["low"]),
                high=float(arguments["high"]),
                measurement_expr=arguments.get("measurement_expr", "Step.Result.Numeric"),
                **arguments.get("properties", {}),
            )
            return _ok(
                f"已添加数值限制测试步骤: {arguments['name']} "
                f"(范围: {arguments['low']} ~ {arguments['high']})"
            )

        elif name == "ts_add_string_value_test":
            builder = _get_builder()
            builder.add_string_value_test(
                name=arguments["name"],
                expected=arguments["expected"],
                measurement_expr=arguments.get("measurement_expr", '""'),
            )
            return _ok(f"已添加字符串比较测试步骤: {arguments['name']} (期望: {arguments['expected']})")

        elif name == "ts_add_action":
            builder = _get_builder()
            builder.add_action(
                name=arguments["name"],
                adapter=arguments["adapter"],
                module_path=arguments["module_path"],
                **arguments.get("parameters", {}),
            )
            return _ok(
                f"已添加 Action 步骤: {arguments['name']}\n"
                f"适配器: {arguments['adapter']}\n"
                f"模块: {arguments['module_path']}"
            )

        elif name == "ts_add_sequence_call":
            builder = _get_builder()
            builder.add_sequence_call(
                sequence_name=arguments["sequence_name"],
                name=arguments.get("name", "Call SubSequence"),
            )
            return _ok(f"已添加子序列调用步骤，目标: {arguments['sequence_name']}")

        elif name == "ts_add_statement":
            builder = _get_builder()
            builder.add_statement(arguments["name"], arguments["expression"])
            return _ok(f"已添加 Statement 步骤: {arguments['name']}")

        elif name == "ts_add_wait":
            builder = _get_builder()
            builder.add_wait(
                seconds=float(arguments["seconds"]),
                name=arguments.get("name", "Wait"),
            )
            return _ok(f"已添加等待步骤: {arguments['seconds']} 秒")

        # ── 变量操作 ──
        elif name == "ts_add_file_global":
            builder = _get_builder()
            builder.add_file_global(
                arguments["name"],
                arguments["type"],
                str(arguments["default_value"]),
            )
            return _ok(f"已添加全局变量: {arguments['name']} ({arguments['type']})")

        elif name == "ts_add_local_variable":
            builder = _get_builder()
            builder.add_local_variable(
                arguments["name"],
                arguments["type"],
                str(arguments["default_value"]),
                arguments.get("sequence_name", "MainSequence"),
            )
            return _ok(f"已添加局部变量: {arguments['name']} ({arguments['type']})")

        # ── 查询操作 ──
        elif name == "ts_get_info":
            builder = _get_builder()
            info = {
                "序列列表": builder.get_sequence_names(),
                "步骤统计": builder.get_step_count(),
                "全局变量": builder.get_file_globals(),
            }
            return _ok(json.dumps(info, ensure_ascii=False, indent=2))

        elif name == "ts_list_step_types":
            types = list_step_types()
            lines = ["可用的步骤类型:\n"]
            for t in types:
                lines.append(f"  {t['name']}: {t['description']}")
            return _ok("\n".join(lines))

        elif name == "ts_list_adapters":
            adapters = list_adapters()
            lines = ["可用的代码模块适配器:\n"]
            for a in adapters:
                lines.append(f"  {a['name']}: {a['description']}")
            return _ok("\n".join(lines))

        else:
            return _err(f"未知工具: {name}")

    except Exception as e:
        return _err(f"操作失败: {e}")


# ═══════════════════════════════════════════════════════════
# 辅助函数
# ═══════════════════════════════════════════════════════════

def _ok(message: str) -> list[TextContent]:
    return [TextContent(type="text", text=f"[成功] {message}")]


def _err(message: str) -> list[TextContent]:
    return [TextContent(type="text", text=f"[错误] {message}")]


# ═══════════════════════════════════════════════════════════
# 入口
# ═══════════════════════════════════════════════════════════

async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
