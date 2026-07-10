"""TestStand Engine 封装 —— 通过 ActiveX/COM 连接 TestStand 2012

每个实例调用 CoInitialize / CoUninitialize，可在后台线程中安全使用。
"""

import pythoncom
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
    """TestStand ActiveX Engine 封装，每实例独立 COM 初始化。

    可作为上下文管理器使用，退出时自动释放 COM 资源。
    """

    def __init__(self):
        self._engine: Optional[object] = None
        self._seq_file = None
        self.current_file_path: Optional[str] = None
        self._coinit = False

    def connect(self):
        """连接到 TestStand Engine 并初始化 COM。"""
        if self._engine is not None:
            return
        pythoncom.CoInitialize()
        self._coinit = True
        try:
            self._engine = win32com.client.Dispatch("TestStand.Engine")
            self._engine.LoadTypePaletteFilesEx(CONFLICT_HANDLER_ERROR, 0)
        except Exception as e:
            self._coinit = False
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
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

    @property
    def sequence_file(self):
        """当前打开的序列文件句柄。"""
        return self._seq_file

    def close(self):
        """释放序列文件引用并反初始化 COM。"""
        if self._seq_file is not None:
            try:
                self.release_sequence_file(self._seq_file)
            except Exception:
                pass
            self._seq_file = None
            self.current_file_path = None
        self._engine = None
        if self._coinit:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
            self._coinit = False

    # ── 文件生命周期 ──

    def create_new_file(self, output_path: str = None) -> None:
        """创建新的序列文件对象。"""
        self._seq_file = self.engine.NewSequenceFile()
        if output_path:
            self.current_file_path = output_path

    def save_file(self, path: str) -> None:
        """保存序列文件到指定路径。"""
        if self._seq_file:
            self._seq_file.Save(path)

    # ── 工厂方法 ──

    def new_sequence_file(self):
        """创建新序列文件（兼容 SequenceBuilder 接口）。"""
        return self.engine.NewSequenceFile()

    def new_step(self, adapter: str, step_type: str):
        """创建新步骤。"""
        return self.engine.NewStep(adapter, step_type)

    def new_sequence(self):
        """创建新序列。"""
        return self.engine.NewSequence()

    def new_property_object(self, value_type: int, as_array: bool = False):
        """创建新属性对象。"""
        return self.engine.NewPropertyObject(value_type, as_array, "", 0)

    def release_sequence_file(self, seq_file):
        """释放序列文件引用。"""
        self.engine.ReleaseSequenceFileEx(seq_file)

    # ── 上下文管理器 ──

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


# 全局单例（供 MCP 等单线程长期场景复用）
_engine_instance: Optional[TestStandEngine] = None


def get_engine() -> TestStandEngine:
    """获取 TestStand Engine 全局单例。"""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = TestStandEngine()
        _engine_instance.connect()
    return _engine_instance
