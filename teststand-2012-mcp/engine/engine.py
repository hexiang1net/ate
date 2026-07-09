"""TestStand Engine interface."""
from abc import ABC, abstractmethod
from typing import Optional, Any


class ITestStandEngine(ABC):
    """抽象 TestStand 引擎接口。

    不同平台/传输（pywin32 COM、gRPC 桥接、Linux 实现等）的实现必须实现所有方法。
    COM 句柄相关字段（engine / sequence_file）保持 Any 类型，
    抽象粒度只到「引擎生命周期 + 序列文件读写」，
    Sequence/Step/PropertyObject 等对象的属性抽象是后续工作。
    """

    @property
    @abstractmethod
    def engine(self) -> Optional[Any]:
        """获取底层 TestStand 引擎句柄。"""
        ...

    @property
    @abstractmethod
    def sequence_file(self) -> Optional[Any]:
        """获取当前打开的序列文件句柄。"""
        ...

    @sequence_file.setter
    @abstractmethod
    def sequence_file(self, value: Any) -> None:
        """设置序列文件句柄。"""
        ...

    @property
    @abstractmethod
    def current_file_path(self) -> Optional[str]:
        """获取当前打开的序列文件路径。"""
        ...

    @property
    @abstractmethod
    def is_file_open(self) -> bool:
        """检查是否已打开序列文件。"""
        ...

    @abstractmethod
    def is_initialized(self) -> bool:
        """检查引擎是否已初始化。"""
        ...

    @abstractmethod
    def open_file(self, file_path: str) -> None:
        """打开序列文件。"""
        ...

    @abstractmethod
    def create_new_file(self, file_path: str) -> None:
        """创建新的序列文件。"""
        ...

    @abstractmethod
    def save_file(self, file_path: Optional[str] = None) -> None:
        """保存当前序列文件。"""
        ...

    @abstractmethod
    def close_file(self) -> None:
        """关闭当前序列文件，不释放引擎。"""
        ...

    @abstractmethod
    def get_sequence_file(self, file_path: str) -> Any:
        """打开序列文件并返回引用，不替换当前文件。

        用于跨文件操作。调用者负责通过 release_file_ref() 释放返回的引用。
        """
        ...

    @abstractmethod
    def release_file_ref(self, seq_file: Any) -> None:
        """释放通过 get_sequence_file() 获取的序列文件引用。"""
        ...

    @abstractmethod
    def release(self) -> None:
        """释放所有资源。"""
        ...

    @abstractmethod
    def close(self) -> None:
        """关闭并释放资源（release 的别名）。"""
        ...
