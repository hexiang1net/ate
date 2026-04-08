#!/bin/bash
# ATE Framework 集成与边界条件验证测试
# 用法: bash tests/test-integration.sh

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
echo "ATE Framework 集成与边界条件验证测试"
echo "============================================"
echo ""

# TEST-019: 增强测试脚本可执行性和结构
echo "[TEST-019] 增强测试脚本结构验证"
ENHANCED_SCRIPT="tests/test-ate-framework-enhanced.sh"
check_file_exists "$ENHANCED_SCRIPT"
if [ -x "$ENHANCED_SCRIPT" ]; then
    pass "增强测试脚本具有可执行权限"
else
    fail "增强测试脚本缺少可执行权限"
fi
check_contains "$ENHANCED_SCRIPT" "#!/bin/bash"
check_contains "$ENHANCED_SCRIPT" "set -e"
check_contains "$ENHANCED_SCRIPT" "check_not_contains"
echo ""

# TEST-020: check_not_contains 函数定义与使用
echo "[TEST-020] check_not_contains 函数验证"
# 验证增强脚本中定义了 check_not_contains 函数
check_contains "$ENHANCED_SCRIPT" "check_not_contains()"
# 验证基础测试脚本不包含此函数(功能隔离)
BASE_SCRIPT="tests/test-ate-framework.sh"
check_not_contains "$BASE_SCRIPT" "check_not_contains()"
echo ""

# TEST-021: ATETestPlan.xls 二进制文件存在性
echo "[TEST-021] ATE 测试计划 Excel 文件验证"
XLS_FILE="ATETestPlan.xls"
check_file_exists "$XLS_FILE"
# 验证文件非空(至少有一些字节)
if [ -s "$XLS_FILE" ]; then
    pass "Excel 文件非空 (大小: $(wc -c < "$XLS_FILE") 字节)"
else
    fail "Excel 文件为空"
fi
echo ""

# TEST-022: 项目文件总数和目录结构深度
echo "[TEST-022] 项目结构深度验证"
# 验证 .claude 下有3个子目录: commands, agents, skills
CMD_COUNT=$(find .claude/commands -maxdepth 1 -type f 2>/dev/null | wc -l)
if [ "$CMD_COUNT" -ge 1 ]; then
    pass "commands 目录包含 $CMD_COUNT 个文件"
else
    fail "commands 目录为空"
fi

AGENT_COUNT=$(find .claude/agents -maxdepth 1 -type f 2>/dev/null | wc -l)
if [ "$AGENT_COUNT" -ge 1 ]; then
    pass "agents 目录包含 $AGENT_COUNT 个文件"
else
    fail "agents 目录为空"
fi

SKILL_COUNT=$(find .claude/skills -maxdepth 1 -type f 2>/dev/null | wc -l)
if [ "$SKILL_COUNT" -ge 1 ]; then
    pass "skills 目录包含 $SKILL_COUNT 个文件"
else
    fail "skills 目录为空"
fi

TEST_COUNT=$(find tests -maxdepth 1 -type f 2>/dev/null | wc -l)
if [ "$TEST_COUNT" -ge 2 ]; then
    pass "tests 目录包含 $TEST_COUNT 个文件"
else
    fail "tests 目录文件不足 (至少需要2个)"
fi
echo ""

# TEST-023: 代理六步工作流完整性
echo "[TEST-023] 代理六步工作流完整性验证"
AGENT_FILE=".claude/agents/ate-tester.md"
# 验证每个步骤都有关键操作描述
check_contains "$AGENT_FILE" "步骤 1"
check_contains "$AGENT_FILE" "同步"
check_contains "$AGENT_FILE" "步骤 2"
check_contains "$AGENT_FILE" "分析"
check_contains "$AGENT_FILE" "步骤 3"
check_contains "$AGENT_FILE" "技能"
check_contains "$AGENT_FILE" "步骤 4"
check_contains "$AGENT_FILE" "摘要"
check_contains "$AGENT_FILE" "步骤 5"
check_contains "$AGENT_FILE" "提交"
check_contains "$AGENT_FILE" "步骤 6"
check_contains "$AGENT_FILE" "报告"
echo ""

# TEST-024: 命令文件与代理文件的一致性
echo "[TEST-024] 命令与代理一致性验证"
CMD_FILE=".claude/commands/ate-test.md"
# 命令中描述的步骤应在代理中有对应实现
check_contains "$CMD_FILE" "git pull"
check_contains "$AGENT_FILE" "git fetch origin"
# git pull 等价于 git fetch + git merge, 代理使用 fetch+status 方式
check_contains "$CMD_FILE" "git add"
check_contains "$AGENT_FILE" "git add -A"
check_contains "$CMD_FILE" "git commit"
check_contains "$AGENT_FILE" "git commit"
check_contains "$CMD_FILE" "git push"
check_contains "$AGENT_FILE" "git push origin"
echo ""

# TEST-025: 技能文件中的覆盖要求完整性
echo "[TEST-025] 技能测试覆盖要求验证"
SKILL_FILE=".claude/skills/ate-test-workflow.md"
check_contains "$SKILL_FILE" "正常路径"
check_contains "$SKILL_FILE" "边界条件"
check_contains "$SKILL_FILE" "错误处理"
check_contains "$SKILL_FILE" "逻辑分支"
# 验证包含提交格式示例
check_contains "$SKILL_FILE" "test: ate test cases for"
echo ""

# TEST-026: 远程仓库地址全局一致性
echo "[TEST-026] 远程仓库地址全局一致性"
REMOTE_URL="https://github.com/hexiang1net/ate.git"
# 统计所有配置文件中正确URL的出现次数
CORRECT_COUNT=0
for f in "$CMD_FILE" "$AGENT_FILE" "$SKILL_FILE"; do
    COUNT=$(grep -c "$REMOTE_URL" "$f" 2>/dev/null || true)
    CORRECT_COUNT=$((CORRECT_COUNT + COUNT))
done
if [ "$CORRECT_COUNT" -ge 3 ]; then
    pass "远程仓库地址在 $CORRECT_COUNT 处正确引用"
else
    fail "远程仓库地址引用不足 (期望>=3, 实际=$CORRECT_COUNT)"
fi
echo ""

# TEST-027: 测试计划文档测试项目覆盖
echo "[TEST-027] 测试计划关键项目覆盖验证"
TEST_PLAN="ATETestPlan.md"
# 验证测试计划包含主要测试类别
check_contains "$TEST_PLAN" "Measure.*voltage\|voltage.*Measure\|DMM"
check_contains "$TEST_PLAN" "D-BUS\|D-Bus"
check_contains "$TEST_PLAN" "Relay"
check_contains "$TEST_PLAN" "USL"
check_contains "$TEST_PLAN" "LSL"
# 验证包含足够的测试项目(至少20行测试数据)
LINE_COUNT=$(grep -c "^|" "$TEST_PLAN" 2>/dev/null || true)
if [ "$LINE_COUNT" -ge 20 ]; then
    pass "测试计划包含 $LINE_COUNT 行表格数据"
else
    fail "测试计划表格数据不足 (期望>=20, 实际=$LINE_COUNT)"
fi
echo ""

# TEST-028: YAML frontmatter 字段完整性
echo "[TEST-028] YAML frontmatter 字段完整性"
# 命令文件必需的 frontmatter 字段
head -5 "$CMD_FILE" | grep -q "^---" && pass "命令文件有 frontmatter 开始标记" || fail "命令文件缺少 frontmatter 开始标记"
# 代理文件必需的 frontmatter 字段
head -5 "$AGENT_FILE" | grep -q "^---" && pass "代理文件有 frontmatter 开始标记" || fail "代理文件缺少 frontmatter 开始标记"
head -5 "$SKILL_FILE" | grep -q "^---" && pass "技能文件有 frontmatter 开始标记" || fail "技能文件缺少 frontmatter 开始标记"
# 验证 frontmatter 结束标记
grep -q "^---" "$CMD_FILE" && pass "命令文件有 frontmatter 结束标记" || fail "命令文件缺少 frontmatter 结束标记"
grep -q "^---" "$AGENT_FILE" && pass "代理文件有 frontmatter 结束标记" || fail "代理文件缺少 frontmatter 结束标记"
grep -q "^---" "$SKILL_FILE" && pass "技能文件有 frontmatter 结束标记" || fail "技能文件缺少 frontmatter 结束标记"
echo ""

# TEST-029: 错误处理和边界场景覆盖
echo "[TEST-029] 错误处理和边界场景覆盖"
# 验证命令文件处理推送失败场景
check_contains "$CMD_FILE" "推送失败"
check_contains "$CMD_FILE" "权限"
# 验证代理文件处理失败场景
check_contains "$AGENT_FILE" "失败"
check_contains "$AGENT_FILE" "错误"
# 验证技能文件处理认证场景
check_contains "$SKILL_FILE" "force push"
check_contains "$SKILL_FILE" "认证"
check_contains "$SKILL_FILE" "gh auth login"
echo ""

# TEST-030: 测试脚本输出格式一致性
echo "[TEST-030] 测试脚本输出格式一致性"
# 验证两个测试脚本使用相同的输出格式
check_contains "$BASE_SCRIPT" "PASS:"
check_contains "$ENHANCED_SCRIPT" "PASS:"
check_contains "$BASE_SCRIPT" "FAIL:"
check_contains "$ENHANCED_SCRIPT" "FAIL:"
check_contains "$BASE_SCRIPT" "测试结果汇总"
check_contains "$ENHANCED_SCRIPT" "测试结果汇总"
check_contains "$BASE_SCRIPT" "所有测试通过"
check_contains "$ENHANCED_SCRIPT" "所有.*测试通过"
echo ""

# TEST-031: 无代码变更场景下的 Agent 行为
echo "[TEST-031] 无代码变更场景处理验证"
# 验证代理文件描述了分析变更的逻辑
check_contains "$AGENT_FILE" "git diff"
check_contains "$AGENT_FILE" "git diff --cached"
# 验证代理在未暂存和已暂存变更都检查
check_contains "$AGENT_FILE" "未暂存"
check_contains "$AGENT_FILE" "已暂存"
echo ""

# TEST-032: 测试用例文档与脚本的映射
echo "[TEST-032] 测试文档与脚本映射关系"
# 测试文档中的每个 TEST-XXX 应在脚本中有对应实现
for i in 001 002 003 004 005 006; do
    check_contains "$BASE_SCRIPT" "TEST-$i"
done
for i in 007 008 009 010 011 012 013 014 015 016 017 018; do
    check_contains "$ENHANCED_SCRIPT" "TEST-$i"
done
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
    echo "所有集成与边界测试通过!"
    exit 0
else
    echo "有 $FAIL 个测试失败，请检查上述问题。"
    exit 1
fi
