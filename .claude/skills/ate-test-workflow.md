---
name: ate-test-workflow
description: ATE 测试用例编写规范和最佳实践
type: skill
---

# ATE 测试工作流技能

## 用途

指导如何编写符合 ATE 项目规范的测试用例。

## 测试用例编写规范

### 测试文件命名

- 格式：`test_<模块名>.py` 或 `<模块名>.test.ts`（根据项目语言）
- 放在项目测试目录下，通常是 `tests/` 或 `__tests__/`

### 测试用例结构

每个测试用例遵循 **AAA 模式**：

1. **Arrange（准备）**：设置测试数据和前置条件
2. **Act（执行）**：调用被测试的功能
3. **Assert（断言）**：验证结果是否符合预期

### 测试覆盖要求

- 正常路径（happy path）
- 边界条件
- 错误处理路径
- 本次变更新增的逻辑分支

### 提交规范

提交信息格式：`test: ate test cases for <描述>`

例如：
- `test: ate test cases for user authentication module`
- `test: ate test cases for payment validation edge cases`

## Git 操作流程

### 推送到远程仓库

远程仓库地址：`https://github.com/hexiang1net/ate.git`

操作顺序：

1. `git fetch origin` — 获取远程最新状态
2. 检查冲突和变更
3. `git add -A` — 添加所有变更文件
4. `git commit` — 提交，使用规范格式
5. `git push origin <分支名>` — 推送到远程

### 注意事项

- 提交前必须确认变更内容合理
- 如果推送被拒绝（如需要 force push），暂停并告知用户
- 遇到认证问题，提示用户使用 `gh auth login` 或配置凭据
