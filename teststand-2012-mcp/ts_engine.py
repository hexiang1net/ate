"""TestStand Engine 封装 —— 通过 ActiveX/COM 连接 TestStand 2012"""

import win32com.client
from typing import Optional

# 步骤组常量
STEP_GROUP_SETUP = 0
STEP_GROUP_CLEANUP = 1
STEP_GROUP_MAIN = 2

# EvalOption 常量
EVAL_OPTION_DO_NOT_ALTER_VALUES = 0

# ConflictHandler 常量
CONFLICT_HANDLER_ERROR = 0


class TestStandEngine:
    """TestStand ActiveX Engine 单例封装"""

    def __init__(self):
        self._engine: Optional[object] = None

    def connect(self):
        """连接到 TestStand Engine（进程单例）"""
        if self._engine is not None:
            return
        try:
            self._engine = win32com.client.Dispatch("TestStand.Engine")
            self._engine.LoadTypePaletteFilesEx(CONFLICT_HANDLER_ERROR, 0)
        except Exception as e:
            raise RuntimeError(
                "无法连接 TestStand Engine。\n"
                "请确认:\n"
                "  1. TestStand 2012 已安装\n"
                "  2. 许可证已激活\n"
                f"原始错误: {e}"
            )

    @property
    def engine(self):
        if self._engine is None:
            self.connect()
        return self._engine

    def close(self):
        """释放 Engine 引用"""
        self._engine = None

    def new_sequence_file(self):
        """创建新的序列文件对象"""
        return self.engine.NewSequenceFile()

    def new_step(self, adapter: str, step_type: str):
        """创建新步骤"""
        return self.engine.NewStep(adapter, step_type)

    def new_sequence(self):
        """创建新序列"""
        return self.engine.NewSequence()

    def new_property_object(self, value_type: int, as_array: bool = False):
        """创建新属性对象"""
        return self.engine.NewPropertyObject(value_type, as_array, "", 0)

    def release_sequence_file(self, seq_file):
        """释放序列文件引用"""
        self.engine.ReleaseSequenceFileEx(seq_file)


# 全局单例
_engine_instance: Optional[TestStandEngine] = None


def get_engine() -> TestStandEngine:
    """获取 TestStand Engine 全局单例"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = TestStandEngine()
        _engine_instance.connect()
    return _engine_instance
