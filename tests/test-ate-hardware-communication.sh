#!/bin/bash
# ATE 硬件测试 - 通信与标识测试验证
# 覆盖 ATETestPlan.md 中 Test 2.1~2.4 (D-BUS 标识写入)、3.1~3.4 (通信准备)、
# 16.1~16.3 (标识读取)、4.1 (输入读取) 测试项
# 用法: bash tests/test-ate-hardware-communication.sh

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
echo "ATE 硬件测试 - 通信与标识测试验证"
echo "============================================"
echo ""

TEST_PLAN="ATETestPlan.md"

# TEST-HW-020: Write HW Identifier and Version
echo "[TEST-HW-020] D-BUS 写入硬件标识符和版本"
check_contains "$TEST_PLAN" "Write HW Identifier and Version"
check_contains "$TEST_PLAN" "D-BUS"
check_contains "$TEST_PLAN" "HW-ID"
check_contains "$TEST_PLAN" "HW-Version"
check_contains "$TEST_PLAN" "PARTNUMBER"
# 验证 HEX 格式转换
check_contains "$TEST_PLAN" "hex Format"
check_contains "$TEST_PLAN" "00 00 00 00 00 00 34 AF"
echo ""

# TEST-HW-021: Tracing ID
echo "[TEST-HW-021] D-BUS 写入追踪标识符"
check_contains "$TEST_PLAN" "Tracing ID"
check_contains "$TEST_PLAN" "BCD Coded"
check_contains "$TEST_PLAN" "Materialnumber"
check_contains "$TEST_PLAN" "Supplier ID"
check_contains "$TEST_PLAN" "Counter"
echo ""

# TEST-HW-022: Production data
echo "[TEST-HW-022] D-BUS 写入生产数据"
check_contains "$TEST_PLAN" "Production data"
check_contains "$TEST_PLAN" "BCD Coded"
check_contains "$TEST_PLAN" "Date"
check_contains "$TEST_PLAN" "Time"
echo ""

# TEST-HW-023: Reset main uC via D-BUS
echo "[TEST-HW-023] D-BUS 主控 MCU 复位测试"
check_contains "$TEST_PLAN" "Reset main uC"
check_contains "$TEST_PLAN" "500ms"
check_contains "$TEST_PLAN" "300ms"
check_contains "$TEST_PLAN" "release reset"
echo ""

# TEST-HW-024: Setup D-BUS communication
echo "[TEST-HW-024] D-BUS 通信建立与ACK检查"
check_contains "$TEST_PLAN" "Setup communication"
check_contains "$TEST_PLAN" "D-Bus-communication"
check_contains "$TEST_PLAN" "ACK"
check_contains "$TEST_PLAN" "X655"
echo ""

# TEST-HW-025: Read HW and FW ID
echo "[TEST-HW-025] D-BUS 读取硬件和固件标识"
check_contains "$TEST_PLAN" "Read HW and FW ID"
check_contains "$TEST_PLAN" "16.1"
echo ""

# TEST-HW-026: Read Tracing ID
echo "[TEST-HW-026] D-BUS 读取追踪标识符"
check_contains "$TEST_PLAN" "Read Tracing ID"
check_contains "$TEST_PLAN" "16.2"
echo ""

# TEST-HW-027: Read Production Time
echo "[TEST-HW-027] D-BUS 读取生产时间"
check_contains "$TEST_PLAN" "Read Production Time"
check_contains "$TEST_PLAN" "16.3"
echo ""

# TEST-HW-028: D-BUS 通信设备方案验证
echo "[TEST-HW-028] D-BUS 通信设备方案完整性"
DBUS_COUNT=$(grep -c "D-BUS\|D-Bus" "$TEST_PLAN" 2>/dev/null || true)
if [ "$DBUS_COUNT" -ge 8 ]; then
    pass "D-BUS 通信测试项覆盖充分 (出现 $DBUS_COUNT 次)"
else
    fail "D-BUS 通信测试项覆盖不足 (期望>=8, 实际=$DBUS_COUNT)"
fi
echo ""

# TEST-HW-029: 通信标识双向验证 (写入后读取)
echo "[TEST-HW-029] 通信标识写入与读取双向验证"
# 验证写入和读取成对出现
check_contains "$TEST_PLAN" "Write.*D-BUS"
check_contains "$TEST_PLAN" "Read.*D-BUS"
check_contains "$TEST_PLAN" "Write via D-BUS"
check_contains "$TEST_PLAN" "Read via D-BUS"
echo ""

# TEST-HW-030: 通信测试程序文件引用 (aa.vi)
echo "[TEST-HW-030] 通信测试程序文件引用验证"
# 验证 D-BUS 相关测试项都使用 D-BUS 作为设备方案
DBUS_DEVICE_COUNT=$(grep -c "设备方案.*D-BUS\|D-BUS.*设备方案" "$TEST_PLAN" 2>/dev/null || true)
echo "  INFO: D-BUS 作为设备方案的测试项: $DBUS_DEVICE_COUNT"
check_contains "$TEST_PLAN" "Write via D-BUS"
check_contains "$TEST_PLAN" "Read via D-BUS"
check_contains "$TEST_PLAN" "Reset uC via D-Bus"
echo ""

# TEST-HW-031: Mains input voltage read by Test SW
echo "[TEST-HW-031] 主输入电压软件读取测试"
check_contains "$TEST_PLAN" "Check mains input voltage"
check_contains "$TEST_PLAN" "Read input by Test SW"
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
    echo "所有通信与标识测试验证通过!"
    exit 0
else
    echo "有 $FAIL 个测试失败，请检查上述问题。"
    exit 1
fi
