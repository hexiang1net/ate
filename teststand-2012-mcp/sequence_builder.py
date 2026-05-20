"""序列文件构建器 —— 提供友好的 Python API 来构建 TestStand 序列"""

import os
from typing import Optional
from ts_engine import (
    TestStandEngine,
    STEP_GROUP_MAIN,
    STEP_GROUP_SETUP,
    STEP_GROUP_CLEANUP,
    EVAL_OPTION_DO_NOT_ALTER_VALUES,
    get_engine,
)
from step_types import STEP_GROUP_NAMES, get_step_type_info, resolve_step_type, resolve_adapter


class SequenceBuilder:
    """TestStand 序列文件构建器"""

    def __init__(self, engine: Optional[TestStandEngine] = None):
        self._engine = engine or get_engine()
        self._seq_file = None
        self._current_step_group = STEP_GROUP_MAIN
        self._step_counts = {}  # {sequence_name: {group_index: count}}
        self._file_globals = []  # [{name, type, default_value}]

    # ── 文件级操作 ──

    def create_file(self) -> "SequenceBuilder":
        """创建新的序列文件"""
        self._seq_file = self._engine.new_sequence_file()
        self._step_counts = {"MainSequence": {0: 0, 1: 0, 2: 0}}
        self._file_globals = []
        return self

    def load_file(self, path: str) -> "SequenceBuilder":
        """加载已有序列文件进行修改"""
        abs_path = os.path.abspath(path)
        self._seq_file = self._engine.engine.GetSequenceFileEx(abs_path, 0)
        if self._seq_file is None:
            raise FileNotFoundError(f"无法加载序列文件: {path}")
        return self

    def save(self, path: str) -> "SequenceBuilder":
        """保存序列文件到磁盘"""
        self._ensure_file()
        abs_path = os.path.abspath(path)
        self._seq_file.Save(abs_path)
        return self

    def close(self) -> "SequenceBuilder":
        """释放序列文件引用"""
        if self._seq_file is not None:
            self._engine.release_sequence_file(self._seq_file)
            self._seq_file = None
        return self

    # ── 序列级操作 ──

    def get_main_sequence(self):
        """获取 MainSequence"""
        self._ensure_file()
        return self._seq_file.GetSequenceByName("MainSequence")

    def add_sequence(self, name: str) -> "SequenceBuilder":
        """添加新的子序列"""
        self._ensure_file()
        seq = self._engine.new_sequence()
        seq.Name = name
        self._seq_file.InsertSequenceEx(
            self._seq_file.NumSequences, seq
        )
        self._step_counts[name] = {0: 0, 1: 0, 2: 0}
        return self

    def set_sequence_step_group(self, step_group: str) -> "SequenceBuilder":
        """设置后续 add_step 操作的目标步骤组: setup/main/cleanup"""
        if step_group not in STEP_GROUP_NAMES:
            raise ValueError(f"无效步骤组: {step_group}，可选: setup/main/cleanup")
        self._current_step_group = STEP_GROUP_NAMES[step_group]
        return self

    def use_sequence(self, sequence_name: str) -> "SequenceBuilder":
        """切换到指定序列进行后续操作"""
        self._current_sequence = sequence_name
        return self

    # ── 步骤操作 ──

    def add_step(
        self,
        step_type: str,
        name: Optional[str] = None,
        adapter: Optional[str] = None,
        **properties,
    ) -> "SequenceBuilder":
        """添加步骤到当前序列的当前步骤组

        Args:
            step_type: 步骤类型名 (如 Action, NumericLimitTest, MessagePopup)
            name: 步骤名称（可选，自动生成默认名称）
            adapter: 适配器名（可选，根据步骤类型自动选择）
            **properties: 步骤属性，键值对
        """
        self._ensure_file()

        # 解析兼容别名
        actual_type = resolve_step_type(step_type)
        if adapter is not None:
            adapter = resolve_adapter(adapter)
        else:
            adapter = get_step_type_info(step_type)["adapter"]
            adapter = resolve_adapter(adapter)

        # 创建步骤
        step = self._engine.new_step(adapter, actual_type)

        # 设置步骤名称
        if name:
            step.Name = name
        else:
            try:
                default_name = step.StepType.AsPropertyObject.EvaluateEx(
                    step.StepType.DefaultNameExpr, EVAL_OPTION_DO_NOT_ALTER_VALUES
                ).GetValString("", 0)
                step.Name = default_name
            except Exception:
                step.Name = step_type

        # 注册步骤类型
        self._seq_file.AsPropertyObjectFile().TypeUsageList.AddUsedTypes(
            step.AsPropertyObject()
        )

        # 插入到序列
        seq_name = getattr(self, '_current_sequence', 'MainSequence')
        seq = self._seq_file.GetSequenceByName(seq_name)
        seq.InsertStep(step, 0, self._current_step_group)

        # 更新内部计数
        if seq_name not in self._step_counts:
            self._step_counts[seq_name] = {0: 0, 1: 0, 2: 0}
        self._step_counts[seq_name][self._current_step_group] += 1

        # 设置步骤属性（必须在 AddUsedTypes + InsertStep 之后）
        self._set_step_properties(step, properties)

        return self

    def add_message_popup(self, message: str, name: str = "Message") -> "SequenceBuilder":
        """添加弹出消息步骤"""
        return self.add_step(
            "MessagePopup",
            name=name,
            MessageExpr=f'"{message}"',
        )

    def add_numeric_limit_test(
        self,
        name: str,
        low: float,
        high: float,
        measurement_expr: str = "Step.Result.Numeric",
        **properties,
    ) -> "SequenceBuilder":
        """添加数值限制测试步骤"""
        return self.add_step(
            "NumericLimitTest",
            name=name,
            **{
                "Limits.Low": str(low),
                "Limits.High": str(high),
                "DataExpr": measurement_expr,
                **properties,
            },
        )

    def add_string_value_test(
        self,
        name: str,
        expected: str,
        measurement_expr: str = '""',
    ) -> "SequenceBuilder":
        """添加字符串比较测试步骤"""
        return self.add_step(
            "StringValueTest",
            name=name,
            **{
                "Limits.String": expected,
                "Result.String": measurement_expr,
            },
        )

    def add_sequence_call(
        self,
        sequence_name: str,
        name: str = "Call SubSequence",
    ) -> "SequenceBuilder":
        """添加子序列调用步骤"""
        return self.add_step(
            "SequenceCall",
            name=name,
            adapter="Sequence Adapter",
            **{
                "Module.AsSequenceCallModule.SequenceName": sequence_name,
                "Module.UseCurFile": "true",
            },
        )

    def add_action(
        self,
        name: str,
        adapter: str,
        module_path: str,
        **parameters,
    ) -> "SequenceBuilder":
        """添加 Action 步骤（绑定代码模块）

        Args:
            name: 步骤名称
            adapter: 适配器名（如 LabVIEW Adapter, C/C++ DLL Adapter）
            module_path: 代码模块路径
            **parameters: 模块参数
        """
        return self.add_step(
            "Action",
            name=name,
            adapter=adapter,
            ModulePath=module_path,
            **parameters,
        )

    def add_statement(self, name: str, expression: str) -> "SequenceBuilder":
        """添加表达式语句步骤"""
        return self.add_step(
            "Statement",
            name=name,
            Expr=expression,
        )

    def add_wait(self, seconds: float, name: str = "Wait") -> "SequenceBuilder":
        """添加等待步骤"""
        return self.add_step(
            "Wait",
            name=name,
            TimeExpr=str(seconds),
        )

    # ── 变量操作 ──

    def add_file_global(
        self, name: str, type_name: str, default_value: str
    ) -> "SequenceBuilder":
        """添加序列文件全局变量

        Args:
            name: 变量名
            type_name: 类型名 (Number, String, Boolean 或自定义类型)
            default_value: 默认值
        """
        self._ensure_file()
        globals_defaults = self._seq_file.FileGlobalsDefaultValues

        if type_name == "Number":
            globals_defaults.SetValNumber(name, 1, float(default_value))  # InsertIfMissing=1
        elif type_name == "Boolean":
            globals_defaults.SetValBoolean(name, 1, default_value.lower() == "true")
        else:
            globals_defaults.SetValString(name, 1, str(default_value))

        self._file_globals.append({
            "name": name, "type": type_name, "defaultValue": str(default_value)
        })
        return self

    def add_local_variable(
        self,
        name: str,
        type_name: str,
        default_value: str,
        sequence_name: str = "MainSequence",
    ) -> "SequenceBuilder":
        """添加序列局部变量"""
        self._ensure_file()
        seq = self._seq_file.GetSequenceByName(sequence_name)
        locals_obj = seq.Locals

        if type_name == "Number":
            locals_obj.SetValNumber(name, 1, float(default_value))
        elif type_name == "Boolean":
            locals_obj.SetValBoolean(name, 1, default_value.lower() == "true")
        else:
            locals_obj.SetValString(name, 1, str(default_value))

        return self

    # ── 查询操作 ──

    def get_step_count(self, sequence_name: str = "MainSequence") -> dict:
        """获取各步骤组的步骤数量"""
        self._ensure_file()
        counts = self._step_counts.get(sequence_name, {0: 0, 1: 0, 2: 0})
        return {
            "Setup": counts.get(0, 0),
            "Main": counts.get(2, 0),
            "Cleanup": counts.get(1, 0),
        }

    def get_sequence_names(self) -> list:
        """获取序列文件中所有序列名称"""
        self._ensure_file()
        names = []
        for i in range(self._seq_file.NumSequences):
            seq = self._seq_file.GetSequence(i)
            names.append(seq.Name)
        return names

    def get_file_globals(self) -> list:
        """获取序列文件全局变量列表"""
        return self._file_globals

    # ── 内部方法 ──

    def _ensure_file(self):
        if self._seq_file is None:
            raise RuntimeError("尚未创建或加载序列文件，请先调用 create_file() 或 load_file()")

    def _set_step_properties(self, step, properties: dict):
        """设置步骤的自定义属性（InsertIfMissing=1 创建新属性）"""
        step_obj = step.AsPropertyObject()
        for lookup_str, value in properties.items():
            try:
                step_obj.SetValNumber(lookup_str, 1, float(value))
            except Exception:
                try:
                    if value.lower() in ("true", "false"):
                        step_obj.SetValBoolean(lookup_str, 1, value.lower() == "true")
                    else:
                        step_obj.SetValString(lookup_str, 1, str(value))
                except Exception:
                    step_obj.SetValString(lookup_str, 1, str(value))
