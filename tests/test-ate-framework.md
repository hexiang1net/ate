# ATE Test Framework - 测试用例

## 测试范围

本文件记录 ATE 测试框架的测试用例，覆盖 Command -> Agent -> Skill 架构的完整工作流。

---

## TEST-001: 命令文件结构验证

**目的**: 验证 `.claude/commands/ate-test.md` 文件存在且包含必需字段

**前置条件**:
- `.claude/commands/` 目录存在
- `ate-test.md` 文件存在

**测试步骤**:
1. 检查 `.claude/commands/ate-test.md` 文件存在
2. 验证文件包含 `name: ate-test` 字段
3. 验证文件包含 `type: command` 字段
4. 验证文件包含 "执行步骤" 章节

**预期结果**: 所有检查通过

**实际结果**: [ ] 通过 / [ ] 失败

---

## TEST-002: 代理文件结构验证

**目的**: 验证 `.claude/agents/ate-tester.md` 文件存在且包含必需字段

**前置条件**:
- `.claude/agents/` 目录存在
- `ate-tester.md` 文件存在

**测试步骤**:
1. 检查 `.claude/agents/ate-tester.md` 文件存在
2. 验证文件包含 `name: ate-tester` 字段
3. 验证文件包含 `description` 字段
4. 验证文件包含 "执行流程" 章节
5. 验证文件定义了 6 个步骤（同步、分析、技能加载、摘要、提交推送、报告）

**预期结果**: 所有检查通过

**实际结果**: [ ] 通过 / [ ] 失败

---

## TEST-003: 技能文件结构验证

**目的**: 验证 `.claude/skills/ate-test-workflow.md` 文件存在且包含必需字段

**前置条件**:
- `.claude/skills/` 目录存在
- `ate-test-workflow.md` 文件存在

**测试步骤**:
1. 检查 `.claude/skills/ate-test-workflow.md` 文件存在
2. 验证文件包含 `name: ate-test-workflow` 字段
3. 验证文件包含 `type: skill` 字段
4. 验证文件包含 "测试用例编写规范" 章节
5. 验证文件包含 "Git 操作流程" 章节

**预期结果**: 所有检查通过

**实际结果**: [ ] 通过 / [ ] 失败

---

## TEST-004: Command -> Agent -> Skill 架构完整性

**目的**: 验证三个组件之间的引用链完整

**测试步骤**:
1. 验证命令文件引用 `ate-tester` 代理
2. 验证代理文件引用 `ate-test-workflow` 技能
3. 验证技能文件包含远程仓库地址 `https://github.com/hexiang1net/ate.git`
4. 验证提交信息格式规范一致：`test: ate test cases for <描述>`

**预期结果**: 所有引用链完整且一致

**实际结果**: [ ] 通过 / [ ] 失败

---

## TEST-005: Git 操作流程正确性

**目的**: 验证 Agent 中定义的 Git 操作流程

**测试步骤**:
1. 验证步骤 1 包含 `git fetch origin` 和 `git status`
2. 验证步骤 2 包含 `git diff` 和 `git diff --cached`
3. 验证步骤 5 包含 `git add -A`、`git commit`、`git push origin`
4. 验证远程仓库 URL 为 `https://github.com/hexiang1net/ate.git`

**预期结果**: Git 流程完整且正确

**实际结果**: [ ] 通过 / [ ] 失败

---

## TEST-006: 测试覆盖规范

**目的**: 验证技能文件中定义了测试覆盖要求

**测试步骤**:
1. 验证包含 AAA 模式（Arrange/Act/Assert）
2. 验证覆盖正常路径（happy path）
3. 验证覆盖边界条件
4. 验证覆盖错误处理路径
5. 验证覆盖本次变更新增的逻辑分支

**预期结果**: 所有覆盖要求已定义

**实际结果**: [ ] 通过 / [ ] 失败
