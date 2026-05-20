# ATE 硬件测试用例 - 测试计划映射文档

## 概述

本文档建立 ATETestPlan.md 中定义的测试项目到 TestStand 序列文件(.seq)对应测试用例的映射关系。

本项目的测试通过 **aa.vi** 作为程序文件，使用 DMM (Fluke8810A) 进行电压测量，通过 D-BUS 进行通信控制和数据读写，通过继电器控制进行负载和信号切换。

---

## 测试用例映射

### 1. 电源测试组 (TEST-HW-001 ~ TEST-HW-011)

**测试脚本**: `tests/test-ate-hardware-power.sh`

| 测试用例 | ATETestPlan 编号 | 测试项目 | 测试点 | 设备方案 | 程序文件 |
|---------|-----------------|---------|--------|---------|---------|
| TEST-HW-001 | 1.1 | 230V 电源开关 | P1000/P1006 | DMM (Fluke8810A) | aa.vi |
| TEST-HW-002 | 1.2 | +320V 中间电路 | P2002/P2001 | DMM (Fluke8810A) | aa.vi |
| TEST-HW-003 | 1.3 | +24V DC | P2304/P2503 | DMM (Fluke8810A) | aa.vi |
| TEST-HW-004 | 1.4 | +12V DC | P2406/P2503 | DMM (Fluke8810A) | aa.vi |
| TEST-HW-005 | 1.5 | +5V_SW DCDC | P3004/P2503 | DMM (Fluke8810A) | aa.vi |
| TEST-HW-006 | 1.6 | +5V_DLINE DBUS | P3101/P2503 | DMM (Fluke8810A) | aa.vi |
| TEST-HW-007 | 1.7 | +3.3V_SW MCU | P3100/P2503 | DMM (Fluke8810A) | aa.vi |
| TEST-HW-008 | 综合 | 测量设备验证 | - | DMM (Fluke8810A) | - |
| TEST-HW-009 | 综合 | 程序文件引用 | - | - | aa.vi |
| TEST-HW-010 | 综合 | USL/LSL 完整性 | - | - | - |
| TEST-HW-011 | 综合 | 测试计划结构 | - | - | - |

---

### 2. 通信与标识测试组 (TEST-HW-020 ~ TEST-HW-031)

**测试脚本**: `tests/test-ate-hardware-communication.sh`

| 测试用例 | ATETestPlan 编号 | 测试项目 | 测试点 | 设备方案 | 程序文件 |
|---------|-----------------|---------|--------|---------|---------|
| TEST-HW-020 | 2.1 | HW 标识符和版本写入 | - | D-BUS | aa.vi |
| TEST-HW-021 | 2.2 | 追踪 ID 写入 | - | D-BUS | aa.vi |
| TEST-HW-022 | 2.3 | 生产数据写入 | - | D-BUS | aa.vi |
| TEST-HW-023 | 2.4 | 主控 MCU 复位 | - | D-BUS | aa.vi |
| TEST-HW-024 | 3.1 | D-BUS 通信建立 | X655 | D-BUS | aa.vi |
| TEST-HW-025 | 16.1 | 读取 HW/FW ID | - | D-BUS | aa.vi |
| TEST-HW-026 | 16.2 | 读取追踪 ID | - | D-BUS | aa.vi |
| TEST-HW-027 | 16.3 | 读取生产时间 | - | D-BUS | aa.vi |
| TEST-HW-028 | 综合 | D-BUS 设备方案覆盖 | - | D-BUS | - |
| TEST-HW-029 | 综合 | 写入-读取双向验证 | - | D-BUS | aa.vi |
| TEST-HW-030 | 综合 | 程序文件引用验证 | - | - | aa.vi |
| TEST-HW-031 | 4.1 | 主输入电压软件读取 | - | DMM | aa.vi |

---

### 3. 外设测试组 (TEST-HW-040 ~ TEST-HW-079)

**测试脚本**: `tests/test-ate-hardware-peripheral.sh`

#### 3.1 继电器准备 (TEST-HW-040 ~ TEST-HW-042)

| 测试用例 | ATETestPlan 编号 | 测试项目 | 测试点 | 设备方案 |
|---------|-----------------|---------|--------|---------|
| TEST-HW-040 | 3.2 | PT1000 测试准备 | X651.1/X651.3 | Relay control |
| TEST-HW-041 | 3.3 | MPS 通道1 准备 | X19 -> GND | Relay control |
| TEST-HW-042 | 3.4 | MPS 通道2 准备 | X20 -> GND | Relay control |

#### 3.2 PEC/门触点 (TEST-HW-043 ~ TEST-HW-044)

| 测试用例 | ATETestPlan 编号 | 测试项目 | 测试点 | 设备方案 |
|---------|-----------------|---------|--------|---------|
| TEST-HW-043 | 5.1 | PEC1&2 开关 | P3220 | DMM |
| TEST-HW-044 | 5.2 | 门触点 | X9_1.2&3/X9_1.1 | D-BUS |

#### 3.3 阀门/传感器 (TEST-HW-045 ~ TEST-HW-047)

| 测试用例 | ATETestPlan 编号 | 测试项目 | 测试点 | 设备方案 |
|---------|-----------------|---------|--------|---------|
| TEST-HW-045 | 6.1 | 阀门接触 | X9_1.2&3/X9_1.1 | D-BUS |
| TEST-HW-046 | 7.1 | 满传感器 | X650.2/X652.3 | D-BUS |
| TEST-HW-047 | 7.2 | 空传感器 | X650.4/X652.3 | D-BUS |

#### 3.4 PT1000 (TEST-HW-048 ~ TEST-HW-049)

| 测试用例 | ATETestPlan 编号 | 测试项目 | 测试点 | 设备方案 |
|---------|-----------------|---------|--------|---------|
| TEST-HW-048 | 8.1 | PT1000 参考通道 | 1.2 kOhm 1% Int. | D-BUS |
| TEST-HW-049 | 8.2 | PT1000 AD 值 | - | D-BUS |

#### 3.5 通道电阻 (TEST-HW-050 ~ TEST-HW-055)

| 测试用例 | ATETestPlan 编号 | 测试项目 | 测试点 | 设备方案 |
|---------|-----------------|---------|--------|---------|
| TEST-HW-050 | 9.1 | 通道1 电阻接入 | X19 7.5 kOhm 1% | Relay control |
| TEST-HW-051 | 9.2 | 通道1 AD 值 | MS11/MS12 | D-BUS |
| TEST-HW-052 | 9.3 | 通道1 电阻移除 | X19 | Relay control |
| TEST-HW-053 | 9.4 | 通道2 电阻接入 | X20 -> GND | Relay control |
| TEST-HW-054 | 9.5 | 通道2 AD 值 | MS21/MS22 | D-BUS |
| TEST-HW-055 | 9.6 | 通道2 电阻移除 | X20 | Relay control |

#### 3.6 BLDC (TEST-HW-056 ~ TEST-HW-060)

| 测试用例 | ATETestPlan 编号 | 测试项目 | 测试点 | 设备方案 |
|---------|-----------------|---------|--------|---------|
| TEST-HW-056 | 10.1 | +24V_BLDC 电压 | P3314/P2503 | DMM |
| TEST-HW-057 | 10.2 | BLDC 输入开路 | X22.4 -> X22.3 (open) | D-BUS |
| TEST-HW-058 | 10.3 | BLDC 输入短路 | X22.4 -> X22.3 (short) | D-BUS |
| TEST-HW-059 | 10.6 | BLDC 输出设置 | X22.5 4.80 VDC | DMM |
| TEST-HW-060 | 10.7 | BLDC 输出复位 | X22.5 0.1 VDC | DMM |

#### 3.7 晶体管/LED (TEST-HW-061 ~ TEST-HW-062)

| 测试用例 | ATETestPlan 编号 | 测试项目 | 测试点 | 设备方案 |
|---------|-----------------|---------|--------|---------|
| TEST-HW-061 | 11.1 | 晶体管开关 | X70.1 -> X70.3 | - |
| TEST-HW-062 | 12.1 | Cavity-LED 功率 | X25.2 -> X25.3 / R6000 | DMM |

#### 3.8 继电器/TRIAC 组1 (TEST-HW-063 ~ TEST-HW-068)

| 测试用例 | ATETestPlan 编号 | 测试项目 | 测试点 | 设备方案 |
|---------|-----------------|---------|--------|---------|
| TEST-HW-063 | 13.1 | PEC 开关 | P3220 | - |
| TEST-HW-064 | 13.2 | 门触点短路 | X65.2&3 -> X65.1 | DMM |
| TEST-HW-065 | 13.3 | 继电器 K5100 | 230 VAC 20-100mA | DMM |
| TEST-HW-066 | 13.4 | 接触负载 | X30 -> X71 | Relay control |
| TEST-HW-067 | 13.5 | TRIAC TH5100 | P5121/P5117 | DMM |
| TEST-HW-068 | 13.7 | 安全脉冲 | - | DMM |

#### 3.9 继电器/TRIAC 组2 (TEST-HW-069 ~ TEST-HW-073)

| 测试用例 | ATETestPlan 编号 | 测试项目 | 测试点 | 设备方案 |
|---------|-----------------|---------|--------|---------|
| TEST-HW-069 | 14.1 | PEC 开关 | P3220 | D-BUS |
| TEST-HW-070 | 14.2 | 继电器 K5000 | 230 VAC 20-100mA | DMM |
| TEST-HW-071 | 14.3 | 接触负载 | X519 -> X1028 | Relay control |
| TEST-HW-072 | 14.4 | TRIAC U5000 | P1010/P5015 | DMM |
| TEST-HW-073 | 14.5 | 安全脉冲 | - | DMM |

#### 3.10 功耗/关机/标签 (TEST-HW-074 ~ TEST-HW-076)

| 测试用例 | ATETestPlan 编号 | 测试项目 | 测试点 | 设备方案 |
|---------|-----------------|---------|--------|---------|
| TEST-HW-074 | 15.1 | 省电模式功耗 | X201.1 -> X201.2 | D-Bus |
| TEST-HW-075 | 17.1 | DUT 断电 | - | Relay control |
| TEST-HW-076 | 18.1 | 标签打印 | - | Printer |

---

## 测量设备汇总

| 设备 | 用途 | 关联测试用例 |
|------|------|-------------|
| DMM (Fluke8810A) | 电压测量 (AC/DC) | TEST-HW-001~007, 043, 056, 059~060, 062, 064~065, 067~068, 070, 072~073 |
| D-BUS | 通信控制/数据读写 | TEST-HW-020~031, 044~049, 051, 054, 057~058, 074 |
| Relay control | 负载/信号切换 | TEST-HW-040~042, 050, 052~053, 055, 066, 071, 075 |
| Printer | 标签打印 | TEST-HW-076 |

---

## 程序文件

所有 TestStand 序列文件(.seq)使用 **aa.vi** 作为 LabVIEW 程序文件，负责：

1. **仪器控制**: DMM (Fluke8810A) 的远程测量控制
2. **D-BUS 通信**: 与 DUT 的 D-BUS 通信协议实现
3. **继电器控制**: 继电器矩阵的开关控制
4. **数据采集**: 电压、电流、AD 值的采集与记录
5. **测试判定**: 基于 USL/LSL 的 PASS/FAIL 判定逻辑

---

## 执行顺序

TestStand 序列文件按照 ATETestPlan.md 中定义的编号顺序依次执行：

```
1.x 电源测试 → 2.x 标识写入 → 3.x 通信准备 → 4.x 输入读取 →
5.x PEC/门触点 → 6.x 阀门 → 7.x 传感器 → 8.x PT1000 →
9.x 通道电阻 → 10.x BLDC → 11.x 晶体管 → 12.x LED →
13.x 继电器组1 → 14.x 继电器组2 → 15.x 功耗 →
16.x 标识读取 → 17.x DUT断电 → 18.x 标签打印
```

---

## 预期结果

- [ ] 所有 TEST-HW-001 ~ TEST-HW-079 测试用例通过
- [ ] ATETestPlan.md 中 18 个测试组全部覆盖
- [ ] 所有测试点 X 编号与实际硬件对应
- [ ] USL/LSL 值在 DMM 测量精度范围内
- [ ] D-BUS 通信 ACK 正常响应

## 实际结果

- [ ] TEST-HW-001 ~ TEST-HW-011 (电源测试): [ ] 通过 / [ ] 失败
- [ ] TEST-HW-020 ~ TEST-HW-031 (通信测试): [ ] 通过 / [ ] 失败
- [ ] TEST-HW-040 ~ TEST-HW-079 (外设测试): [ ] 通过 / [ ] 失败

---

> **创建日期**: 2026-05-20
> **程序文件**: aa.vi
> **版本**: 1.0
