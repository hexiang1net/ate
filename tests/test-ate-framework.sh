#!/bin/bash
# ATE Framework 自动化验证测试
# 用法: bash tests/test-ate-framework.sh

set -e

PASS=0
FAIL=0
TOTAL=0

pass() {
    PASS=$((PASS + 1))
    TOTAL=$((TOTAL + 1))
    echo "  PASS: $1"
}

fail() {
    FAIL=$((FAIL + 1))
    TOTAL=$((TOTAL + 1))
    echo "  FAIL: $1"
}

check_file_exists() {
    if [ -f "$1" ]; then
        pass "文件存在: $1"
    else
        fail "文件不存在: $1"
    fi
}

check_contains() {
    if grep -q "$2" "$1" 2>/dev/null; then
        pass "文件 $1 包含: $2"
    else
        fail "文件 $1 不包含: $2"
    fi
}

echo "============================================"
echo "ATE Framework 自动化验证测试"
echo "============================================"
echo ""

# TEST-001: 命令文件结构
echo "[TEST-001] 命令文件结构验证"
CMD_FILE=".claude/commands/ate-test.md"
check_file_exists "$CMD_FILE"
check_contains "$CMD_FILE" "name: ate-test"
check_contains "$CMD_FILE" "type: command"
check_contains "$CMD_FILE" "执行步骤"
echo ""

# TEST-002: 代理文件结构
echo "[TEST-002] 代理文件结构验证"
AGENT_FILE=".claude/agents/ate-tester.md"
check_file_exists "$AGENT_FILE"
check_contains "$AGENT_FILE" "name: ate-tester"
check_contains "$AGENT_FILE" "description"
check_contains "$AGENT_FILE" "执行流程"
echo ""

# TEST-003: 技能文件结构
echo "[TEST-003] 技能文件结构验证"
SKILL_FILE=".claude/skills/ate-test-workflow.md"
check_file_exists "$SKILL_FILE"
check_contains "$SKILL_FILE" "name: ate-test-workflow"
check_contains "$SKILL_FILE" "type: skill"
check_contains "$SKILL_FILE" "测试用例编写规范"
check_contains "$SKILL_FILE" "Git 操作流程"
echo ""

# TEST-004: 架构完整性
echo "[TEST-004] Command -> Agent -> Skill 架构完整性"
check_contains "$CMD_FILE" "ate-tester"
check_contains "$AGENT_FILE" "ate-test-workflow"
check_contains "$SKILL_FILE" "github.com/hexiang1net/ate.git"
check_contains "$CMD_FILE" "test: ate test cases for"
echo ""

# TEST-005: Git 操作流程
echo "[TEST-005] Git 操作流程正确性"
check_contains "$AGENT_FILE" "git fetch origin"
check_contains "$AGENT_FILE" "git status"
check_contains "$AGENT_FILE" "git diff"
check_contains "$AGENT_FILE" "git add -A"
check_contains "$AGENT_FILE" "git push origin"
echo ""

# TEST-006: 测试覆盖规范
echo "[TEST-006] 测试覆盖规范"
check_contains "$SKILL_FILE" "Arrange"
check_contains "$SKILL_FILE" "Act"
check_contains "$SKILL_FILE" "Assert"
check_contains "$SKILL_FILE" "happy path"
check_contains "$SKILL_FILE" "边界"
check_contains "$SKILL_FILE" "错误"
echo ""

# 汇总
echo "============================================"
echo "测试结果汇总"
echo "============================================"
echo "  总计: $TOTAL"
echo "  通过: $PASS"
echo "  失败: $FAIL"
echo ""

if [ "$FAIL" -eq 0 ]; then
    echo "所有测试通过!"
    exit 0
else
    echo "有 $FAIL 个测试失败，请检查上述问题。"
    exit 1
fi
