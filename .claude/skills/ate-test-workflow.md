---
name: ate-test-workflow
description: 使用 TestStand 2012 MCP 创建 ATE 测试序列文件(.seq)，基于 ATETestPlan.md 测试计划
type: skill
---

# ATE 测试工作流技能

## 用途

使用 TestStand 2012 MCP 服务器创建测试序列文件(.seq)，将 ATETestPlan.md 中定义的测试项目转换为可执行的 TestStand 序列。

## 前置条件

1. MCP 服务器 `teststand-2012` 已配置并运行
2. `ATETestPlan.md` 存在且包含完整测试项目清单
3. 用户已选择程序文件（aa.vi 或 bb.vi）

## TestStand MCP 工具速查

### 文件操作
| 工具 | 说明 |
|------|------|
| `ts_create_sequence_file` | 创建新序列文件（必须先调用） |
| `ts_load_sequence_file` | 加载已有 .seq 文件 |
| `ts_save_sequence_file` | 保存到指定路径 |
| `ts_close_sequence_file` | 关闭并释放资源 |

### 步骤操作
| 工具 | 说明 |
|------|------|
| `ts_add_numeric_limit_test` | 数值限制测试（PASS/FAIL）—— 适合电压、电流、功率测量 |
| `ts_add_string_value_test` | 字符串比较测试 —— 适合 ID 验证、通信检查 |
| `ts_add_action` | 绑定代码模块（VI/DLL/.NET）—— 仪器控制 |
| `ts_add_message_popup` | 操作员提示弹窗 |
| `ts_add_sequence_call` | 调用子序列 |
| `ts_add_statement` | 执行 TestStand 表达式 |
| `ts_add_wait` | 等待指定秒数 |
| `ts_add_step` | 通用步骤（支持 If/Else/While/For 等流程控制） |

### 序列/变量操作
| 工具 | 说明 |
|------|------|
| `ts_set_step_group` | 切换步骤组：setup / main / cleanup |
| `ts_add_sequence` | 添加子序列 |
| `ts_use_sequence` | 切换到指定序列 |
| `ts_add_file_global` | 添加文件全局变量 |
| `ts_add_local_variable` | 添加序列局部变量 |
| `ts_get_info` | 查看当前序列摘要 |

## TestStand 序列结构

每个序列文件包含三个步骤组：

```
Setup（初始化） → Main（主体测试） → Cleanup（清理）
```

### Setup 阶段
- 操作员提示和确认
- 扫码枪等待（记录序列号）
- 仪器初始化（调用 aa.vi / bb.vi 初始化仪器）
- 预热等待

### Main 阶段
- 按 ATETestPlan.md 顺序执行测试项目
- 每个测试项使用 `ts_add_numeric_limit_test` 或 `ts_add_string_value_test`
- 电气测试（电压/电流/功率）→ 通信测试 → 传感器测试 → 继电器测试 → 外设测试

### Cleanup 阶段
- 关闭所有仪器和负载
- 断开继电器
- 记录测试结果计数
- 提示测试完成

## 从 ATETestPlan.md 映射到 TestStand 步骤

ATETestPlan.md 中的每个测试项目映射规则：

| 检测方法 | TestStand 步骤类型 | 示例 |
|---------|-------------------|------|
| Measure voltage with DMM | `ts_add_numeric_limit_test` | USL/LSL 映射为 high/low |
| Read via D-BUS | `ts_add_string_value_test` 或 `ts_add_numeric_limit_test` | 数值读回 |
| Relay control | `ts_add_action` (绑定 VI) | 继电器开关控制 |
| Reset uC via D-Bus | `ts_add_action` (绑定 VI) + `ts_add_wait` | MCU 复位+等待 |
| Write via D-BUS | `ts_add_action` (绑定 VI) | 标识写入 |
| Print label | `ts_add_message_popup` | 提示贴标签 |

## 创建流程

### 1. 创建序列文件

```python
# 步骤 1: 创建文件
ts_create_sequence_file()

# 步骤 2: 添加全局变量
ts_add_file_global(name="SerialNumber", type="String", default_value="")
ts_add_file_global(name="OperatorName", type="String", default_value="")
ts_add_file_global(name="PassCount", type="Number", default_value="0")
ts_add_file_global(name="FailCount", type="Number", default_value="0")
```

### 2. Setup 阶段

```python
ts_set_step_group(group="setup")
ts_add_message_popup(message="请连接DUT并确认所有接线正确")
ts_add_wait(seconds=3, name="等待扫码枪")
ts_add_action(
    name="初始化仪器",
    adapter="LabVIEW Adapter",
    module_path="<用户选择的vi路径>"  # aa.vi 或 bb.vi
)
```

### 3. Main 阶段（按 ATETestPlan.md 顺序）

**电源测试组 (1.1 - 1.7)**
```python
ts_set_step_group(group="main")

# 1.1 Switch ON power supply
ts_add_numeric_limit_test(name="1.1 输入电压 230V", low=207, high=253)

# 1.2 Measure +320V
ts_add_numeric_limit_test(name="1.2 +320V 中间电路", low=292, high=357)

# 1.3 Measure +24V
ts_add_numeric_limit_test(name="1.3 +24V DC", low=20, high=26)

# 1.4 Measure +12V
ts_add_numeric_limit_test(name="1.4 +12V DC", low=10, high=14)

# 1.5 Measure +5V_SW
ts_add_numeric_limit_test(name="1.5 +5V DCDC", low=4.5, high=5.5)

# 1.6 Measure +5V_DLINE
ts_add_numeric_limit_test(name="1.6 +5V DBUS", low=4.5, high=5.5)

# 1.7 Measure +3.3V_SW
ts_add_numeric_limit_test(name="1.7 +3.3V MCU", low=3.0, high=3.6)
```

**D-BUS 通信组 (2.1 - 4.1, 16.1 - 16.3)**
```python
# 标识写入
ts_add_action(name="2.1 写入 HW ID 和 Version", adapter="LabVIEW Adapter",
    module_path="<vi路径>")

# 通信建立
ts_add_string_value_test(name="3.1 D-Bus 通信检查", expected="ACK")

# 标识读回
ts_add_string_value_test(name="16.1 读回 HW 和 FW ID", expected="OK")
```

**外设测试组 (传感器/继电器/BLDC/阀门 等)**
```python
# 传感器测试
ts_add_string_value_test(name="7.1 满传感器检测", expected="HIGH")
ts_add_string_value_test(name="7.2 空传感器检测", expected="HIGH")

# BLDC 测试
ts_add_numeric_limit_test(name="10.1 +24V_BLDC", low=23, high=26)
ts_add_numeric_limit_test(name="10.6 BLDC PWM 输出", low=4.80, high=5.0)

# 继电器测试
ts_add_numeric_limit_test(name="13.3 继电器 K5100 ON", low=207, high=253)
```

### 4. Cleanup 阶段

```python
ts_set_step_group(group="cleanup")
ts_add_statement(name="更新计数", expression="FileGlobals.PassCount = FileGlobals.PassCount + 1")
ts_add_message_popup(message="测试完成，请取下DUT")
```

### 5. 保存文件

```python
ts_save_sequence_file(path="E:\\agent\\ate\\tests\\output\\<测试名称>.seq")
ts_close_sequence_file()
```

## 变量命名规范

| 变量名 | 类型 | 说明 |
|--------|------|------|
| SerialNumber | String | 产品序列号 |
| OperatorName | String | 操作员工号 |
| ProductModel | String | 产品型号 |
| TestTemperature | Number | 测试环境温度 |
| PassCount | Number | 通过计数 |
| FailCount | Number | 失败计数 |

## 远程仓库

所有生成的 .seq 文件和测试用例提交到：
```
https://github.com/hexiang1net/ate.git
```

## Git 操作流程

```bash
git fetch origin
git status
git diff
git diff --cached
git add <文件>
git commit -m "test: ate test cases for <描述>"
git push origin $(git branch --show-current)
```

如果推送失败（认证问题），引导用户执行：
```bash
gh auth login
```

禁止使用 `--force` 推送。

## 测试用例编写规范

1. **AAA 模式**：Arrange（准备）→ Act（执行）→ Assert（断言）
2. **覆盖要求**：
   - 正常路径（happy path）
   - 边界条件（USL/LSL 临界值）
   - 错误处理路径
   - 变更新增的逻辑分支
3. **命名规范**：`test-ate-<功能模块>-<场景>.sh`
4. **提交格式**：`test: ate test cases for <简要描述>`
