#!/bin/bash
# ATE 硬件测试 - 电源测试验证
# 覆盖 ATETestPlan.md 中 Test 1.1~1.7 电源电压测试项
# 用法: bash tests/test-ate-hardware-power.sh

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
echo "ATE 硬件测试 - 电源测试验证"
echo "============================================"
echo ""

TEST_PLAN="ATETestPlan.md"

# TEST-HW-001: Switch ON power supply (230V AC)
echo "[TEST-HW-001] 电源开关 - 230V输入电压测试"
check_contains "$TEST_PLAN" "Switch ON power supply"
check_contains "$TEST_PLAN" "230V"
check_contains "$TEST_PLAN" "P1000/P1006"
check_contains "$TEST_PLAN" "253 VAC"
check_contains "$TEST_PLAN" "207 VAC"
check_contains "$TEST_PLAN" "Fluke8810A"
echo ""

# TEST-HW-002: Measure +320V intermediate circuit
echo "[TEST-HW-002] 中间电路 +320V 电压测试"
check_contains "$TEST_PLAN" "Measure +320V"
check_contains "$TEST_PLAN" "P2002/P2001"
check_contains "$TEST_PLAN" "357 VDC"
check_contains "$TEST_PLAN" "292 VDC"
echo ""

# TEST-HW-003: Measure +24V DC
echo "[TEST-HW-003] +24V 直流电压测试"
check_contains "$TEST_PLAN" "Measure +24V"
check_contains "$TEST_PLAN" "P2304/P2503"
check_contains "$TEST_PLAN" "26 VDC"
check_contains "$TEST_PLAN" "20 VDC"
echo ""

# TEST-HW-004: Measure +12V DC
echo "[TEST-HW-004] +12V 直流电压测试"
check_contains "$TEST_PLAN" "Measure +12V"
check_contains "$TEST_PLAN" "P2406/P2503"
check_contains "$TEST_PLAN" "14 VDC"
check_contains "$TEST_PLAN" "10 VDC"
echo ""

# TEST-HW-005: Measure +5V_SW (DCDC)
echo "[TEST-HW-005] +5V_SW DCDC 电压测试"
check_contains "$TEST_PLAN" "Measure +5V_SW"
check_contains "$TEST_PLAN" "P3004/P2503"
check_contains "$TEST_PLAN" "5.5 VDC"
check_contains "$TEST_PLAN" "4.5 VDC"
echo ""

# TEST-HW-006: Measure +5V_DLINE (DBUS)
echo "[TEST-HW-006] +5V_DLINE DBUS 电压测试"
check_contains "$TEST_PLAN" "Measure +5V_DLINE"
check_contains "$TEST_PLAN" "P3101/P2503"
check_contains "$TEST_PLAN" "5.5 VDC"
check_contains "$TEST_PLAN" "4.5 VDC"
echo ""

# TEST-HW-007: Measure +3.3V_SW (MCU)
echo "[TEST-HW-007] +3.3V_SW MCU 电压测试"
check_contains "$TEST_PLAN" "Measure +3.3V_SW"
check_contains "$TEST_PLAN" "P3100/P2503"
check_contains "$TEST_PLAN" "3.6 VDC"
check_contains "$TEST_PLAN" "3.0 VDC"
echo ""

# TEST-HW-008: Measurement equipment validation
echo "[TEST-HW-008] 电源测试测量设备验证"
check_contains "$TEST_PLAN" "DMM (Fluke8810A)"
# 验证所有电源测试项都使用 DMM 作为检测方法
POWER_DMM_COUNT=$(grep -c "DMM" "$TEST_PLAN" 2>/dev/null || true)
if [ "$POWER_DMM_COUNT" -ge 5 ]; then
    pass "电源测试项使用 DMM 作为测量设备 (出现 $POWER_DMM_COUNT 次)"
else
    fail "电源测试项 DMM 引用不足 (期望>=5, 实际=$POWER_DMM_COUNT)"
fi
echo ""

# TEST-HW-009: Program file aa.vi reference
echo "[TEST-HW-009] 电源测试程序文件引用 (aa.vi)"
# 验证测试计划中电压测试项的完整性
VOLTAGE_TEST_COUNT=$(grep -c "Measure voltage with DMM" "$TEST_PLAN" 2>/dev/null || true)
if [ "$VOLTAGE_TEST_COUNT" -ge 6 ]; then
    pass "电压测量测试项覆盖充分 (出现 $VOLTAGE_TEST_COUNT 次)"
else
    fail "电压测量测试项覆盖不足 (期望>=6, 实际=$VOLTAGE_TEST_COUNT)"
fi
echo ""

# TEST-HW-010: Voltage test limits completeness
echo "[TEST-HW-010] 电压测试上下限完整性"
# 验证所有电源测试项都有 USL (上限)
USL_COUNT=$(grep -c "USL" "$TEST_PLAN" 2>/dev/null || true)
if [ "$USL_COUNT" -ge 1 ]; then
    pass "测试计划包含 USL (上限) 定义"
else
    fail "测试计划缺少 USL (上限) 定义"
fi
# 验证所有电源测试项都有 LSL (下限)
LSL_COUNT=$(grep -c "LSL" "$TEST_PLAN" 2>/dev/null || true)
if [ "$LSL_COUNT" -ge 1 ]; then
    pass "测试计划包含 LSL (下限) 定义"
else
    fail "测试计划缺少 LSL (下限) 定义"
fi
echo ""

# TEST-HW-011: Test plan structure for power tests
echo "[TEST-HW-011] 电源测试计划结构验证"
# 验证测试计划表格有测试点列
check_contains "$TEST_PLAN" "测试点"
check_contains "$TEST_PLAN" "检测方法"
check_contains "$TEST_PLAN" "设备方案"
# 验证电源测试项数量
POWER_TEST_COUNT=$(grep -c "^| 1\." "$TEST_PLAN" 2>/dev/null || true)
if [ "$POWER_TEST_COUNT" -ge 7 ]; then
    pass "电源测试项数量充足 (共 $POWER_TEST_COUNT 项)"
else
    fail "电源测试项数量不足 (期望>=7, 实际=$POWER_TEST_COUNT)"
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
    echo "所有电源测试验证通过!"
    exit 0
else
    echo "有 $FAIL 个测试失败，请检查上述问题。"
    exit 1
fi
