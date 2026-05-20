"""TestStand 2012 步骤类型定义 — 基于实际 API 探测"""

# 内置步骤类型（以 NewStep(adapter, type_name) 中的 type_name 为准）
STEP_TYPES = {
    # 基础步骤 —— 无前缀
    "Action": {
        "adapter": "None Adapter",
        "description": "调用代码模块执行动作（LabVIEW VI / C DLL / .NET 等）",
    },
    "Statement": {
        "adapter": "None Adapter",
        "description": "执行 TestStand 表达式",
    },
    "MessagePopup": {
        "adapter": "None Adapter",
        "description": "弹出消息对话框",
    },
    "SequenceCall": {
        "adapter": "Sequence Adapter",
        "description": "调用子序列",
    },
    "CallExecutable": {
        "adapter": "None Adapter",
        "description": "调用外部可执行程序",
    },
    "Goto": {
        "adapter": "None Adapter",
        "description": "跳转到指定步骤",
    },
    "Label": {
        "adapter": "None Adapter",
        "description": "跳转目标标签",
    },

    # 测试步骤
    "NumericLimitTest": {
        "adapter": "None Adapter",
        "description": "数值限制测试（PASS/FAIL 判定）",
    },
    "StringValueTest": {
        "adapter": "None Adapter",
        "description": "字符串比较测试",
    },
    "PassFailTest": {
        "adapter": "None Adapter",
        "description": "二元 PASS/FAIL 测试",
    },
    "NI_MultipleNumericLimitTest": {
        "adapter": "None Adapter",
        "description": "多值数值限制测试",
    },

    # 流程控制 —— 使用 NI_Flow_ 前缀
    "NI_Flow_If": {"adapter": "None Adapter", "description": "条件分支"},
    "NI_Flow_Else": {"adapter": "None Adapter", "description": "否则分支"},
    "NI_Flow_ElseIf": {"adapter": "None Adapter", "description": "否则如果分支"},
    "NI_Flow_End": {"adapter": "None Adapter", "description": "结束控制结构"},
    "NI_Flow_While": {"adapter": "None Adapter", "description": "While 循环"},
    "NI_Flow_DoWhile": {"adapter": "None Adapter", "description": "DoWhile 循环"},
    "NI_Flow_For": {"adapter": "None Adapter", "description": "For 循环"},
    "NI_Flow_ForEach": {"adapter": "None Adapter", "description": "ForEach 循环"},
    "NI_Flow_Select": {"adapter": "None Adapter", "description": "多条件选择"},
    "NI_Flow_Case": {"adapter": "None Adapter", "description": "Case 分支"},
    "NI_Flow_Break": {"adapter": "None Adapter", "description": "跳出循环"},
    "NI_Flow_Continue": {"adapter": "None Adapter", "description": "继续下一次循环"},

    # 等待/同步 —— NI_ 前缀
    "NI_Wait": {
        "adapter": "None Adapter",
        "description": "等待指定时间（秒）",
    },
    "NI_Lock": {"adapter": "None Adapter", "description": "互斥锁同步"},
    "NI_Notification": {"adapter": "None Adapter", "description": "通知同步"},
    "NI_Queue": {"adapter": "None Adapter", "description": "队列同步"},
    "NI_Rendezvous": {"adapter": "None Adapter", "description": "集合点同步"},
    "NI_Semaphore": {"adapter": "None Adapter", "description": "信号量同步"},

    # 数据库
    "NI_OpenDatabase": {"adapter": "None Adapter", "description": "打开数据库连接"},
    "NI_CloseDatabase": {"adapter": "None Adapter", "description": "关闭数据库连接"},
    "NI_OpenSQLStatement": {"adapter": "None Adapter", "description": "打开 SQL 语句"},
    "NI_CloseSQLStatement": {"adapter": "None Adapter", "description": "关闭 SQL 语句"},

    # IVI 仪器步骤
    "NI_IviDCPower": {"adapter": "None Adapter", "description": "IVI DC 电源"},
    "NI_IviDmm": {"adapter": "None Adapter", "description": "IVI 数字万用表"},
    "NI_IviFgen": {"adapter": "None Adapter", "description": "IVI 函数发生器"},
    "NI_IviScope": {"adapter": "None Adapter", "description": "IVI 示波器"},
    "NI_IviSwitch": {"adapter": "None Adapter", "description": "IVI 开关"},

    # 其他
    "NI_VariableAndPropertyLoader": {"adapter": "None Adapter", "description": "从文件加载属性/变量"},
    "NI_DataOperation": {"adapter": "None Adapter", "description": "数据操作"},
    "NI_ThreadPriority": {"adapter": "None Adapter", "description": "设置线程优先级"},
    "NI_CPUAffinity": {"adapter": "None Adapter", "description": "设置 CPU 亲和性"},
    "NI_UseResource": {"adapter": "None Adapter", "description": "使用资源"},
    "NI_FileToFTP": {"adapter": "None Adapter", "description": "文件上传 FTP"},
    "NI_AutoSchedule": {"adapter": "None Adapter", "description": "自动调度"},
    "NI_BatchSpec": {"adapter": "None Adapter", "description": "批次规格"},
    "NI_BatchSync": {"adapter": "None Adapter", "description": "批次同步"},
    "NI_LV_RunVIAsynchronously": {"adapter": "None Adapter", "description": "异步运行 LabVIEW VI"},
}

# 代码模块适配器 —— KeyName 为 NewStep() 的第一个参数
ADAPTERS = {
    "None Adapter": "无适配器（内置步骤）",
    "G Flexible VI Adapter": "调用 LabVIEW VI（G 语言）",
    "C/CVI Flexible Prototype Adapter": "调用 C/CVI 代码",
    "DLL Flexible Prototype Adapter": "调用 DLL 函数",
    "DotNet Adapter": "调用 .NET 程序集",
    "Automation Adapter": "调用 ActiveX/COM 组件",
    "HTBasic Adapter": "调用 HTBasic 程序",
    "Sequence Adapter": "调用子序列",
}

# 兼容别名：将旧名称映射到新名称
COMPAT_ALIASES = {
    "Wait": "NI_Wait",
    "If": "NI_Flow_If",
    "Else": "NI_Flow_Else",
    "ElseIf": "NI_Flow_ElseIf",
    "End": "NI_Flow_End",
    "While": "NI_Flow_While",
    "For": "NI_Flow_For",
    "ForEach": "NI_Flow_ForEach",
    "Select": "NI_Flow_Select",
    "Case": "NI_Flow_Case",
    "DefaultCase": "NI_Flow_Case",
    "Break": "NI_Flow_Break",
    "Continue": "NI_Flow_Continue",
    "PropertyLoader": "NI_VariableAndPropertyLoader",
    "Database": "NI_OpenDatabase",
    "IVI": "NI_IviDmm",
    "Switch": "NI_IviSwitch",
    "Synchronization": "NI_Lock",

    # 适配器兼容别名
    "LabVIEW Adapter": "G Flexible VI Adapter",
    "C/C++ DLL Adapter": "DLL Flexible Prototype Adapter",
    ".NET Adapter": "DotNet Adapter",
    "ActiveX/COM Adapter": "Automation Adapter",
}

# 步骤组名称
STEP_GROUP_NAMES = {
    "setup": 0,
    "cleanup": 1,
    "main": 2,
}


def resolve_step_type(step_type: str) -> str:
    """将步骤类型名解析为 TestStand 2012 实际类型名"""
    return COMPAT_ALIASES.get(step_type, step_type)


def resolve_adapter(adapter: str) -> str:
    """将适配器名解析为 TestStand 2012 实际 KeyName"""
    return COMPAT_ALIASES.get(adapter, adapter)


def get_step_type_info(step_type: str) -> dict:
    """获取步骤类型信息（支持兼容别名）"""
    actual = resolve_step_type(step_type)
    return STEP_TYPES.get(actual, {
        "adapter": "None Adapter",
        "description": f"自定义步骤类型: {actual}",
    })


def list_step_types() -> list[dict]:
    """列出所有可用的步骤类型"""
    return [
        {"name": name, **info}
        for name, info in STEP_TYPES.items()
    ]


def list_adapters() -> list[dict]:
    """列出所有可用的适配器"""
    return [
        {"name": name, "description": desc}
        for name, desc in ADAPTERS.items()
    ]
