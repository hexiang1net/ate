#!/bin/bash
# ATE 硬件测试 - 外设测试验证
# 覆盖 ATETestPlan.md 中: 继电器准备(3.2~3.4)、PEC/门触点(5.1~5.2)、阀门(6.1)、
# 传感器(7.1~7.2)、PT1000(8.1~8.2)、通道电阻(9.1~9.6)、BLDC(10.1~10.7)、
# 晶体管开关(11.1)、Cavity-LED(12.1)、继电器/TRIAC(13.1~14.5)、功耗(15.1)、
# DUT OFF(17.1)、标签打印(18.1)
# 用法: bash tests/test-ate-hardware-peripheral.sh

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
echo "ATE 硬件测试 - 外设测试验证"
echo "============================================"
echo ""

TEST_PLAN="ATETestPlan.md"

# ===========================
# 继电器准备测试 (3.2~3.4)
# ===========================
echo "[TEST-HW-040] PT1000 测试准备 (1k1 1% 电阻)"
check_contains "$TEST_PLAN" "Prepare PT1000"
check_contains "$TEST_PLAN" "1k1 1%"
check_contains "$TEST_PLAN" "X651.1/X651.3"
echo ""

echo "[TEST-HW-041] MPS 通道1 测试准备 (7.5k 1% 电阻)"
check_contains "$TEST_PLAN" "Prepare MPS 1"
check_contains "$TEST_PLAN" "7.5kOhm 1%"
check_contains "$TEST_PLAN" "X19"
echo ""

echo "[TEST-HW-042] MPS 通道2 测试准备"
check_contains "$TEST_PLAN" "Prepare MPS 2"
check_contains "$TEST_PLAN" "X20 -> GND"
echo ""

# ===========================
# PEC/门触点测试 (5.1~5.2)
# ===========================
echo "[TEST-HW-043] PEC1&2 开关测试"
check_contains "$TEST_PLAN" "Switch on PEC1&2"
check_contains "$TEST_PLAN" "P3220"
check_contains "$TEST_PLAN" "25 DCV"
check_contains "$TEST_PLAN" "23 DCV"
echo ""

echo "[TEST-HW-044] 门触点测试 (短路/开路检测)"
check_contains "$TEST_PLAN" "Test door contact"
check_contains "$TEST_PLAN" "Open/Short"
check_contains "$TEST_PLAN" "X9_1.2&3/X9_1.1"
check_contains "$TEST_PLAN" "Low.*High"
echo ""

# ===========================
# 阀门/传感器测试 (6.1~7.2)
# ===========================
echo "[TEST-HW-045] 阀门接触测试 (短路/开路)"
check_contains "$TEST_PLAN" "Test Valve contact"
check_contains "$TEST_PLAN" "X9_1.2&3/X9_1.1"
echo ""

echo "[TEST-HW-046] 满传感器测试"
check_contains "$TEST_PLAN" "Test full sensor"
check_contains "$TEST_PLAN" "X650.2/X652.3"
check_contains "$TEST_PLAN" "Low.*High"
echo ""

echo "[TEST-HW-047] 空传感器测试"
check_contains "$TEST_PLAN" "Test empty sensor"
check_contains "$TEST_PLAN" "X650.4/X652.3"
echo ""

# ===========================
# PT1000 测试 (8.1~8.2)
# ===========================
echo "[TEST-HW-048] PT1000 参考通道 AD 值读取"
check_contains "$TEST_PLAN" "PT1000 – Reference channel"
check_contains "$TEST_PLAN" "1.2 kOhm 1%"
check_contains "$TEST_PLAN" "Read AD value"
echo ""

echo "[TEST-HW-049] PT1000 AD 值读取"
check_contains "$TEST_PLAN" "PT1000 AD-Value 1"
echo ""

# ===========================
# 通道电阻测试 (9.1~9.6)
# ===========================
echo "[TEST-HW-050] 通道1 电阻接入"
check_contains "$TEST_PLAN" "Channel 1 Resistor"
check_contains "$TEST_PLAN" "7.5 kOhm 1%"
check_contains "$TEST_PLAN" "X19"
echo ""

echo "[TEST-HW-051] 通道1 AD 值读取 (MS11/MS12)"
check_contains "$TEST_PLAN" "Channel 1 Values"
check_contains "$TEST_PLAN" "MS11"
check_contains "$TEST_PLAN" "MS12"
echo ""

echo "[TEST-HW-052] 通道1 电阻移除"
check_contains "$TEST_PLAN" "Channel 1 Res. Rem."
echo ""

echo "[TEST-HW-053] 通道2 电阻接入"
check_contains "$TEST_PLAN" "Channel 2 Resistor"
check_contains "$TEST_PLAN" "X20 -> GND"
echo ""

echo "[TEST-HW-054] 通道2 AD 值读取 (MS21/MS22)"
check_contains "$TEST_PLAN" "Channel 2 Values"
check_contains "$TEST_PLAN" "MS21"
check_contains "$TEST_PLAN" "MS22"
echo ""

echo "[TEST-HW-055] 通道2 电阻移除"
check_contains "$TEST_PLAN" "Channel 2 Res. Rem."
echo ""

# ===========================
# BLDC 测试 (10.1~10.7)
# ===========================
echo "[TEST-HW-056] +24V_BLDC 电压测试"
check_contains "$TEST_PLAN" "+24V_BLDC"
check_contains "$TEST_PLAN" "P3314/P2503"
check_contains "$TEST_PLAN" "23 VDC"
echo ""

echo "[TEST-HW-057] BLDC 输入开路检测"
check_contains "$TEST_PLAN" "BLDC input contact open"
check_contains "$TEST_PLAN" "X22.4 -> X22.3 (open)"
check_contains "$TEST_PLAN" "BLDC-CF"
echo ""

echo "[TEST-HW-058] BLDC 输入短路检测"
check_contains "$TEST_PLAN" "BLDC inputs contact closed"
check_contains "$TEST_PLAN" "X22.4 -> X22.3 (short)"
echo ""

echo "[TEST-HW-059] BLDC 输出设置"
check_contains "$TEST_PLAN" "Set BLDC outputs"
check_contains "$TEST_PLAN" "PWM-Out static"
check_contains "$TEST_PLAN" "4.80 VDC"
echo ""

echo "[TEST-HW-060] BLDC 输出复位"
check_contains "$TEST_PLAN" "Reset BLDC outputs"
check_contains "$TEST_PLAN" "0.1 VDC"
echo ""

# ===========================
# 晶体管开关/ LED 测试 (11.1, 12.1)
# ===========================
echo "[TEST-HW-061] 晶体管开关测试"
check_contains "$TEST_PLAN" "Test transistor switch"
check_contains "$TEST_PLAN" "78R/10W"
check_contains "$TEST_PLAN" "X70.1 -> X70.3"
check_contains "$TEST_PLAN" "25 VDC"
echo ""

echo "[TEST-HW-062] Cavity-LED 功率测试"
check_contains "$TEST_PLAN" "Cavity-LED Power"
check_contains "$TEST_PLAN" "24R-5%"
check_contains "$TEST_PLAN" "X25.2 -> X25.3"
check_contains "$TEST_PLAN" "R6000"
echo ""

# ===========================
# 继电器/TRIAC 测试组1 (13.1~13.7)
# ===========================
echo "[TEST-HW-063] 继电器组1 PEC开关验证"
check_contains "$TEST_PLAN" "13.1"
check_contains "$TEST_PLAN" "P3220"
echo ""

echo "[TEST-HW-064] 继电器组1 门触点短路验证"
check_contains "$TEST_PLAN" "13.2"
check_contains "$TEST_PLAN" "X65.2&3 -> X65.1"
check_contains "$TEST_PLAN" "25 VDC"
check_contains "$TEST_PLAN" "23 VDC"
echo ""

echo "[TEST-HW-065] 继电器 K5100 开关测试"
check_contains "$TEST_PLAN" "K5100"
check_contains "$TEST_PLAN" "230 VAC"
check_contains "$TEST_PLAN" "253 VAC / 105 mA"
check_contains "$TEST_PLAN" "207 / 20"
echo ""

echo "[TEST-HW-066] 继电器组1 接触负载测试"
check_contains "$TEST_PLAN" "13.4"
check_contains "$TEST_PLAN" "25Ω/2500W"
check_contains "$TEST_PLAN" "X30 -> X71"
echo ""

echo "[TEST-HW-067] TRIAC 组1 测试"
check_contains "$TEST_PLAN" "Test triac"
check_contains "$TEST_PLAN" "TH5100"
check_contains "$TEST_PLAN" "P5121/P5117"
check_contains "$TEST_PLAN" "253 VAC / 1.5 VAC"
echo ""

echo "[TEST-HW-068] 继电器组1 安全脉冲验证"
check_contains "$TEST_PLAN" "13.7"
check_contains "$TEST_PLAN" "Load relay safety pulse"
check_contains "$TEST_PLAN" "Turn off PEC 1&2"
echo ""

# ===========================
# 继电器/TRIAC 测试组2 (14.1~14.5)
# ===========================
echo "[TEST-HW-069] 继电器组2 PEC开关验证"
check_contains "$TEST_PLAN" "14.1"
echo ""

echo "[TEST-HW-070] 继电器 K5000 开关测试"
check_contains "$TEST_PLAN" "14.2"
check_contains "$TEST_PLAN" "K5000"
echo ""

echo "[TEST-HW-071] 继电器组2 接触负载测试"
check_contains "$TEST_PLAN" "14.3"
check_contains "$TEST_PLAN" "5KΩ/50W"
check_contains "$TEST_PLAN" "X519 -> X1028"
echo ""

echo "[TEST-HW-072] TRIAC 组2 测试"
check_contains "$TEST_PLAN" "14.4"
check_contains "$TEST_PLAN" "U5000"
check_contains "$TEST_PLAN" "P1010/P5015"
check_contains "$TEST_PLAN" "253 VAC / 1.5 VAC"
check_contains "$TEST_PLAN" "207 / 0.5"
echo ""

echo "[TEST-HW-073] 继电器组2 安全脉冲验证"
check_contains "$TEST_PLAN" "14.5"
echo ""

# ===========================
# 功耗/关机/标签 (15.1, 17.1, 18.1)
# ===========================
echo "[TEST-HW-074] 省电模式功耗测试"
check_contains "$TEST_PLAN" "Power consumption.*Power Saving"
check_contains "$TEST_PLAN" "0.25 W"
check_contains "$TEST_PLAN" "0.15 W"
check_contains "$TEST_PLAN" "X201.1 -> X201.2"
echo ""

echo "[TEST-HW-075] DUT 断电测试"
check_contains "$TEST_PLAN" "17.1"
check_contains "$TEST_PLAN" "DUT OFF"
echo ""

echo "[TEST-HW-076] 标签打印测试"
check_contains "$TEST_PLAN" "Print label and attach"
check_contains "$TEST_PLAN" "Printer"
echo ""

# ===========================
# 外设测试总体覆盖验证
# ===========================
echo "[TEST-HW-077] 外设测试设备方案覆盖验证"
# 验证使用继电器控制的测试项
RELAY_COUNT=$(grep -c "Relay control" "$TEST_PLAN" 2>/dev/null || true)
if [ "$RELAY_COUNT" -ge 4 ]; then
    pass "继电器控制测试项充足 (出现 $RELAY_COUNT 次)"
else
    fail "继电器控制测试项不足 (期望>=4, 实际=$RELAY_COUNT)"
fi
echo ""

echo "[TEST-HW-078] 外设测试程序文件引用 (aa.vi)"
# 验证 BLDC 测试项
BLDC_COUNT=$(grep -c "BLDC" "$TEST_PLAN" 2>/dev/null || true)
if [ "$BLDC_COUNT" -ge 6 ]; then
    pass "BLDC 测试项覆盖充分 (出现 $BLDC_COUNT 次)"
else
    fail "BLDC 测试项覆盖不足 (期望>=6, 实际=$BLDC_COUNT)"
fi

# 验证传感器测试项
SENSOR_COUNT=$(grep -c "sensor" "$TEST_PLAN" 2>/dev/null || true)
if [ "$SENSOR_COUNT" -ge 2 ]; then
    pass "传感器测试项覆盖充分 (出现 $SENSOR_COUNT 次)"
else
    fail "传感器测试项覆盖不足 (期望>=2, 实际=$SENSOR_COUNT)"
fi
echo ""

echo "[TEST-HW-079] 外设测试项 Open/Short 模式验证"
check_contains "$TEST_PLAN" "Open/Short"
check_contains "$TEST_PLAN" "short.*door contact"
check_contains "$TEST_PLAN" "remove short"
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
    echo "所有外设测试验证通过!"
    exit 0
else
    echo "有 $FAIL 个测试失败，请检查上述问题。"
    exit 1
fi
