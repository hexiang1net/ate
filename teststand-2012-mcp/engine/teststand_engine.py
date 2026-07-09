"""TestStand Engine wrapper with sequence file management."""

import os
import sys

import pythoncom
import win32com.client

_current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _current_dir not in sys.path:
    sys.path.insert(0, _current_dir)

from ts_engine import TestStandEngine as _COMEngine


class TestStandEngine:
    """TestStand Engine with sequence file lifecycle management.

    Each instance initializes COM for its own thread, so it is safe
    to use from concurrent background threads.
    """

    def __init__(self):
        self._coinit = False
        pythoncom.CoInitialize()
        self._coinit = True
        self._com = _COMEngine()
        self._com.connect()
        self._seq_file = None
        self.current_file_path = None

    @property
    def engine(self):
        return self._com.engine

    @property
    def sequence_file(self):
        return self._seq_file

    def create_new_file(self, output_path: str) -> None:
        self._seq_file = self.engine.NewSequenceFile()
        self.current_file_path = output_path

    def save_file(self, path: str) -> None:
        if self._seq_file:
            self._seq_file.Save(path)

    def close(self) -> None:
        if self._seq_file:
            try:
                self._com.release_sequence_file(self._seq_file)
            except Exception:
                pass
            self._seq_file = None
            self.current_file_path = None
        # Clean up COM for this thread
        if self._coinit:
            try:
                pythoncom.CoUninitialize()
            except Exception:
                pass
            self._coinit = False

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()
