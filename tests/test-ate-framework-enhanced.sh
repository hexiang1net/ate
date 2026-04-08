#!/bin/bash
# ATE Framework 增强验证测试 - 扩展覆盖范围
# 用法: bash tests/test-ate-framework-enhanced.sh

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

check_not_contains() {
    if ! grep -q "$2" "$1" 2>/dev/null; then
        pass "文件 $1 不包含(预期): $2"
    else
        fail "文件 $1 不应包含: $2"
    fi
}

echo "============================================"
echo "ATE Framework 增强验证测试"
echo "============================================"
echo ""

# TEST-007: 命令文件 YAML frontmatter 完整性
echo "[TEST-007] 命令文件 YAML frontmatter 完整性"
CMD_FILE=".claude/commands/ate-test.md"
check_file_exists "$CMD_FILE"
check_contains "$CMD_FILE" "name: ate-test"
check_contains "$CMD_FILE" "description:"
check_contains "$CMD_FILE" "type: command"
# 验证命令引用了 ate-tester 代理
check_contains "$CMD_FILE" "ate-tester"
check_contains "$CMD_FILE" "ate-test-workflow"
echo ""

# TEST-008: 代理文件 YAML frontmatter 完整性
echo "[TEST-008] 代理文件 YAML frontmatter 完整性"
AGENT_FILE=".claude/agents/ate-tester.md"
check_file_exists "$AGENT_FILE"
check_contains "$AGENT_FILE" "name: ate-tester"
check_contains "$AGENT_FILE" "description:"
check_contains "$AGENT_FILE" "model:"
check_contains "$AGENT_FILE" "when to use:"
# 验证代理包含完整的6步执行流程
check_contains "$AGENT_FILE" "步骤 1"
check_contains "$AGENT_FILE" "步骤 2"
check_contains "$AGENT_FILE" "步骤 3"
check_contains "$AGENT_FILE" "步骤 4"
check_contains "$AGENT_FILE" "步骤 5"
check_contains "$AGENT_FILE" "步骤 6"
echo ""

# TEST-009: 技能文件内容正确性
echo "[TEST-009] 技能文件内容正确性"
SKILL_FILE=".claude/skills/ate-test-workflow.md"
check_file_exists "$SKILL_FILE"
check_contains "$SKILL_FILE" "name: ate-test-workflow"
check_contains "$SKILL_FILE" "type: skill"
check_contains "$SKILL_FILE" "description:"
# 验证测试用例编写规范
check_contains "$SKILL_FILE" "测试用例编写规范"
check_contains "$SKILL_FILE" "AAA"
check_contains "$SKILL_FILE" "Arrange"
check_contains "$SKILL_FILE" "Act"
check_contains "$SKILL_FILE" "Assert"
# 验证 Git 操作流程
check_contains "$SKILL_FILE" "Git 操作流程"
check_contains "$SKILL_FILE" "github.com/hexiang1net/ate.git"
# 验证测试覆盖要求
check_contains "$SKILL_FILE" "happy path"
check_contains "$SKILL_FILE" "边界"
check_contains "$SKILL_FILE" "错误"
echo ""

# TEST-010: 测试脚本可执行性
echo "[TEST-010] 测试脚本可执行性"
TEST_SCRIPT="tests/test-ate-framework.sh"
check_file_exists "$TEST_SCRIPT"
if [ -x "$TEST_SCRIPT" ]; then
    pass "测试脚本具有可执行权限"
else
    fail "测试脚本缺少可执行权限"
fi
check_contains "$TEST_SCRIPT" "#!/bin/bash"
check_contains "$TEST_SCRIPT" "set -e"
echo ""

# TEST-011: 测试计划文档完整性
echo "[TEST-011] 测试计划文档完整性"
TEST_PLAN="ATETestPlan.md"
check_file_exists "$TEST_PLAN"
check_contains "$TEST_PLAN" "ATE Test Plan"
check_contains "$TEST_PLAN" "Product Information"
check_contains "$TEST_PLAN" "Test Item Check List"
# 验证测试计划包含关键测试项目
check_contains "$TEST_PLAN" "DMM"
check_contains "$TEST_PLAN" "D-BUS"
check_contains "$TEST_PLAN" "Relay"
echo ""

# TEST-012: 架构引用链验证
echo "[TEST-012] Command -> Agent -> Skill 双向引用链"
# 命令 -> 代理
check_contains "$CMD_FILE" "ate-tester"
# 代理 -> 技能
check_contains "$AGENT_FILE" "ate-test-workflow"
# 技能 -> 远程仓库
check_contains "$SKILL_FILE" "github.com/hexiang1net/ate.git"
# 命令中的提交格式
check_contains "$CMD_FILE" "test: ate test cases for"
# 代理中的提交格式
check_contains "$AGENT_FILE" "test: ate test cases for"
echo ""

# TEST-013: Git 操作命令完整性
echo "[TEST-013] Git 操作命令完整性"
# 代理中定义的完整 Git 流程
check_contains "$AGENT_FILE" "git fetch origin"
check_contains "$AGENT_FILE" "git status"
check_contains "$AGENT_FILE" "git diff"
check_contains "$AGENT_FILE" "git add -A"
check_contains "$AGENT_FILE" "git commit"
check_contains "$AGENT_FILE" "git push origin"
# 命令中定义的 Git 流程
check_contains "$CMD_FILE" "git pull"
check_contains "$CMD_FILE" "git add"
check_contains "$CMD_FILE" "git commit"
check_contains "$CMD_FILE" "git push"
echo ""

# TEST-014: 错误处理机制
echo "[TEST-014] 错误处理机制"
# 命令文件应提及错误处理
check_contains "$CMD_FILE" "推送失败"
check_contains "$CMD_FILE" "权限"
# 代理应提及错误处理
check_contains "$AGENT_FILE" "失败"
check_contains "$AGENT_FILE" "错误信息"
# 技能应提及认证问题
check_contains "$SKILL_FILE" "认证"
check_contains "$SKILL_FILE" "gh auth login"
echo ""

# TEST-015: 测试覆盖率统计
echo "[TEST-015] 测试用例文档覆盖"
TEST_DOC="tests/test-ate-framework.md"
check_file_exists "$TEST_DOC"
# 验证测试文档包含完整的测试用例
check_contains "$TEST_DOC" "TEST-001"
check_contains "$TEST_DOC" "TEST-002"
check_contains "$TEST_DOC" "TEST-003"
check_contains "$TEST_DOC" "TEST-004"
check_contains "$TEST_DOC" "TEST-005"
check_contains "$TEST_DOC" "TEST-006"
# 验证每个测试用例有必需字段
check_contains "$TEST_DOC" "目的"
check_contains "$TEST_DOC" "预期结果"
check_contains "$TEST_DOC" "实际结果"
echo ""

# TEST-016: 项目目录结构完整性
echo "[TEST-016] 项目目录结构完整性"
if [ -d ".claude/commands" ]; then
    pass "目录存在: .claude/commands"
else
    fail "目录不存在: .claude/commands"
fi
if [ -d ".claude/agents" ]; then
    pass "目录存在: .claude/agents"
else
    fail "目录不存在: .claude/agents"
fi
if [ -d ".claude/skills" ]; then
    pass "目录存在: .claude/skills"
else
    fail "目录不存在: .claude/skills"
fi
if [ -d "tests" ]; then
    pass "目录存在: tests"
else
    fail "目录不存在: tests"
fi
echo ""

# TEST-017: 文件编码和格式
echo "[TEST-017] 文件编码和格式验证"
# 验证所有 Markdown 文件以 YAML frontmatter 开头
head -1 "$CMD_FILE" | grep -q "^---" && pass "命令文件以 --- 开头" || fail "命令文件不以 --- 开头"
head -1 "$AGENT_FILE" | grep -q "^---" && pass "代理文件以 --- 开头" || fail "代理文件不以 --- 开头"
head -1 "$SKILL_FILE" | grep -q "^---" && pass "技能文件以 --- 开头" || fail "技能文件不以 --- 开头"
echo ""

# TEST-018: 远程仓库配置一致性
echo "[TEST-018] 远程仓库配置一致性"
# 所有文件中引用的远程仓库地址应一致
check_contains "$SKILL_FILE" "https://github.com/hexiang1net/ate.git"
check_contains "$AGENT_FILE" "https://github.com/hexiang1net/ate.git"
check_contains "$CMD_FILE" "https://github.com/hexiang1net/ate.git"
# 验证没有引用其他错误的仓库地址(除了正确的 hexiang1net/ate.git)
if grep -q "github.com/" "$SKILL_FILE" && ! grep -q "github.com/hexiang1net/ate.git" "$SKILL_FILE"; then
    fail "技能文件引用了错误的 GitHub 仓库地址"
else
    pass "技能文件仓库地址正确"
fi
if grep -q "github.com/" "$AGENT_FILE" && ! grep -q "github.com/hexiang1net/ate.git" "$AGENT_FILE"; then
    fail "代理文件引用了错误的 GitHub 仓库地址"
else
    pass "代理文件仓库地址正确"
fi
if grep -q "github.com/" "$CMD_FILE" && ! grep -q "github.com/hexiang1net/ate.git" "$CMD_FILE"; then
    fail "命令文件引用了错误的 GitHub 仓库地址"
else
    pass "命令文件仓库地址正确"
fi
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
    echo "所有增强测试通过!"
    exit 0
else
    echo "有 $FAIL 个测试失败，请检查上述问题。"
    exit 1
fi
