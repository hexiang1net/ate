---
name: ate-test
description: 创建测试序列文件seq文件，通过TestStand
type: command
---

# /ate-test 命令

## 用途

创建测试序列文件seq文件，通过TestStand

## 架构

遵循 **Command → Agent → Skill** 模式：
1. **本命令** 接收用户意图，
2. **ate-test-workflow 技能** 提供创建测试序列文件的具体指导

## 执行步骤
1. 询问用户使用哪个vi
  - 使用 AskUserQuestion 工具询问用户希望使用aa.vi还是bb.vi。
1. 加载 ate-test-workflow 技能
  - 调用 **ate-test-workflow** 技能获取测试序列文件。
2. 向用户报告执行结果
  - 成功：生成的文件列表


