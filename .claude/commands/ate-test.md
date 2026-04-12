---
name: ate-test
description: 构建 ATE 测试用例并推送到远程仓库
type: command
---

# /ate-test 命令

## 用途

构建 ATE 测试工作流，创建 ATE 测试用例，并提交推送到远程 Git 仓库。

## 架构

遵循 **Command → Agent → Skill** 模式：
1. **本命令** 接收用户意图，触发 ate-tester 代理
2. **ate-tester 代理** 执行测试用例创建和 Git 操作
3. **ate-test-workflow 技能** 提供测试用例编写的具体指导

## 执行步骤

1. 调用 **ate-tester** 代理，委托以下所有操作：
   - 通过 `git pull` 更新当前仓库
   - 分析项目变动，创建或更新 ATE 测试用例
   - 通过 `git add` 添加所有变动文件
   - 通过 `git commit` 提交更改，提交信息格式：`test: ate test cases for <描述>`
   - 通过 `git push` 推送到远程仓库 `https://github.com/hexiang1net/ate.git`
2. 向用户报告执行结果
  - 成功：提交的文件列表

## 注意事项

- 如果远程仓库地址未配置，使用 `https://github.com/hexiang1net/ate.git`
- 提交前展示变更摘要，让用户确认
- 如推送失败（如无权限），明确告知用户具体错误信息
