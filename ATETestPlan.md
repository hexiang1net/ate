# ATE Test Plan

## Product Information

| 项目 | 内容 |
|------|------|
| **Product Type** | FCT |
| **EAU** | PCS/Y |
| **ATE QTY** | — |
| **Test time** | S/Unit |
| **Version** | — |

---

## Test Item Check List

| No. | 测试项目 | 测试要求描述 | Command / 控制命令 | 测试点 | USL (上限) | LSL (下限) | 检测方法 | 设备方案 |
|-----|---------|-------------|-------------------|--------|-----------|-----------|---------|---------|
| 1.1 | Switch ON power supply | Set 230V to X201 and measure @ test points | — | P1000/P1006 | 253 VAC | 207 VAC | Measure voltage with DMM | DMM (Fluke8810A) |
| 1.2 | Measure +320V | Measure intermediate circuit voltage | — | P2002/P2001 | 357 VDC | 292 VDC | Measure voltage with DMM | DMM (Fluke8810A) |
| 1.3 | Measure +24V | Measure 24V DC | — | P2304/P2503 | 26 VDC | 20 VDC | Measure voltage with DMM | DMM (Fluke8810A) |
| 1.4 | Measure +12V | Test of 12V DC | — | P2406/P2503 | 14 VDC | 10 VDC | Measure voltage with DMM | DMM (Fluke8810A) |
| 1.5 | Measure +5V_SW | Test of 5V DCDC | — | P3004/P2503 | 5.5 VDC | 4.5 VDC | Measure voltage with DMM | DMM (Fluke8810A) |
| 1.6 | Measure +5V_DLINE | Test of 5V DBUS | — | P3101/P2503 | 5.5 VDC | 4.5 VDC | Measure voltage with DMM | DMM (Fluke8810A) |
| 1.7 | Measure +3.3V_SW | Test of 3.3V MCU | — | P3100/P2503 | 3.6 VDC | 3.0 VDC | Measure voltage with DMM | DMM (Fluke8810A) |
| 2.1 | Write HW Identifier and Version | Structure of HW & SW ID see Related document 02 "BSH General Bus Specification D-Bus-2.2" | Partlist Complete / In Line: "PCB assy", Column: "PARTNUMBER". Convert all Parameter from BOM in .hex Format. HW-ID: 00000000000000013487, HW-Version: 00004.00000.00000.0000000003. Convert to: 00 00 00 00 00 00 34 AF / 00 4 00 00 00 00 00 00 00 03 | — | — | — | Write via D-BUS | D-BUS |
| 2.2 | Tracing ID | See step 2.1 | In Line: "Cust. Mat.Nr.". All Parameter BCD Coded. Example: Materialnumber: 9001466291, Supplier ID: 0000429251, Counter: 999 | — | — | — | Write via D-BUS | D-BUS |
| 2.3 | Production data | See step 2.1 | All Parameter BCD Coded. Example: Date: 25.06.2020, Time: 12:04 | — | — | — | Write via D-BUS | D-BUS |
| 2.4 | Reset main uC | Reset uC via D-Bus, wait 500ms, reset uC again, release reset | Wait at least 300ms | — | — | — | Reset uC via D-Bus | D-BUS |
| 3.1 | Setup communication | D-Bus-communication | Check for ACK, refer to Doc | X655 | — | — | via D-Bus | D-BUS |
| 3.2 | Prepare PT1000 for Test | Control resistor of 1k1 1% to GND | — | X651.1/X651.3 | — | — | Relay | Relay control |
| 3.3 | Prepare MPS 1 | Control a resistor of 7.5kOhm 1% to GND | — | X19 -> GND | — | — | Relay | Relay control |
| 3.4 | Prepare MPS 2 | Control a resistor of 7.5kOhm 1% to GND | — | X20 -> GND | — | — | Relay | Relay control |
| 4.1 | Check mains input voltage | Read input by Test SW | — | — | — | — | Measure voltage with DMM | DMM (Fluke8810A) |
| 5.1 | Switch on PEC1&2 | Read input by Test SW | — | P3220 | 25 DCV | 23 DCV | Measure voltage with DMM | DMM (Fluke8810A) |
| 5.2 | Test door contact | Read I/O port, short door contact, read I/O port, remove short at door contact | Open/Short | X9_1.2&3/X9_1.1 | Low | High | Read via D-BUS | D-BUS |
| 6.1 | Test Valve contact | Read I/O port, short door contact, read I/O port, remove short at door contact | Open/Short | X9_1.2&3/X9_1.1 | Low | High | Read via D-BUS | D-BUS |
| 7.1 | Test full sensor | Read I/O port, short door contact, read I/O port, remove short at door contact | Open/Short | X650.2/X652.3 | Low | High | Read via D-BUS | D-BUS |
| 7.2 | Test empty sensor | Read I/O port, short door contact, read I/O port, remove short at door contact | Open/Short | X650.4/X652.3 | Low | High | Read via D-BUS | D-BUS |
| 8.1 | PT1000 – Reference channel | Read AD value | — | 1.2 kOhm 1% Int. | tbd | tbd | Read via D-BUS | D-BUS |
| 8.2 | PT1000 AD-Value 1 | Read AD value | — | — | tbd | tbd | Read via D-BUS | D-BUS |
| 9.1 | Channel 1 Resistor | Control a resistor of 7.5kOhm 1% to GND | — | 7.5 kOhm 1% | — | — | Relay | Relay control |
| 9.2 | Channel 1 Values | Read AD value of MS11, Read AD value of MS12 | — | — | tbd | tbd | Read via D-BUS | D-BUS |
| 9.3 | Channel 1 Res. Rem. | Remove resistor from X19 | — | — | — | — | Relay | Relay control |
| 9.4 | Channel 2 Resistor | Control a resistor of 7.5kOhm 1% to GND | — | X20 -> GND | — | — | Relay | Relay control |
| 9.5 | Channel 2 Values | Read AD value of MS21, Read AD value of MS22 | — | — | tbd | tbd | Read via D-BUS | D-BUS |
| 9.6 | Channel 2 Res. Rem. | Remove resistor from X20 | — | — | — | — | Relay | Relay control |
| 10.1 | +24V_BLDC | Turn +24V_BLDC on, measure +24V_BLDC | — | P3314/P2503 | 23 VDC | — | Measure voltage with DMM | DMM (Fluke8810A) |
| 10.2 | BLDC input contact open | Read I/O port. BLDC-CF/CiF/MWCF State IN | — | X22.4 -> X22.3 (open) | HIGH | — | Read via D-BUS | D-BUS |
| 10.3 | BLDC inputs contact closed | Short at BLDC contact, BLDC-CF State IN | — | X22.4 -> X22.3 (short) | HIGH | — | Read via D-BUS | D-BUS |
| — | BLDC inputs | Read I/O port. BLDC-CF/CiF/MWCF State IN | — | — | — | — | Read via D-BUS | D-BUS |
| 10.5 | BLDC inputs contact open | Remove short at BLDC contact | — | X22.4 -> X22.3 (open) | — | — | Relay | Relay control |
| 10.6 | Set BLDC outputs | Set output CF, measure voltage | CF/CiF/MWCF PWM-Out static | X22.5 | 4.80 VDC | — | Measure voltage with DMM | DMM (Fluke8810A) |
| 10.7 | Reset BLDC outputs | Reset output to BLDC interface, measure voltage | CF/CiF/MWCF PWM-Out static | X22.5 | 0.1 VDC | — | Measure voltage with DMM | DMM (Fluke8810A) |
| 11.1 | Test transistor switch | Connect a 78R/10W 5% resistor, measure voltage, Switch ON valve, measure voltage, Switch valve OFF | — | X70.1 -> X70.3 | 25 VDC | 0.2/22.8 | — | — |
| 12.1 | Cavity-LED Power | Connect a 24R-5% resistor to LED-interface, measure voltage @ R6000 | — | X25.2 -> X25.3 | 0.14 VDC | 0.08 VDC | Measure voltage with DMM | DMM (Fluke8810A) |
| 13.1 | Switch on PEC1&2 | — | — | P3220 | — | — | D-Bus | — |
| 13.2 | Short at door contact | Short door contact X652 | — | X65.2&3 -> X65.1 | 25 VDC | 23 VDC | Measure voltage with DMM | DMM (Fluke8810A) |
| 13.3 | Relay test | Switch ON Relay K5100, check ON/OFF state, switch OFF Relay K5100, check ON/OFF state | — | 230 VAC 20–100mA | 253 VAC / 105 mA | 207 / 20 | Measure voltage with DMM | DMM (Fluke8810A) |
| 13.4 | Contact loads | Connect a 230V load, 25Ω/2500W resistor | — | X30 -> X71 | — | — | Relay | Relay control |
| 13.5 | Test triac | Switch Triac OFF, measure voltage @ TH5100; Switch Triac ON, measure voltage @ TH51001 | — | P5121/P5117 | 253 VAC / 1.5 VAC | 1.5 / 0.5 | Measure voltage with DMM | DMM (Fluke8810A) |
| 13.6 | Current Transformer | Read input by Test SW | — | — | — | — | — | — |
| 13.7 | Load relay safety pulse | Turn off PEC 1&2, check OFF state of all relays, remove short at door contact | — | — | — | — | Measure voltage with DMM | DMM (Fluke8810A) |
| 14.1 | Switch on PEC1&2 | — | — | P3220 | 25 VDC | 23 VDC | D-BUS | — |
| 14.2 | Relay test | Switch ON Relay K5000, check ON/OFF state, switch OFF Relay K5000, check ON/OFF state | — | 230 VAC 20–100mA | 253 VAC / 1.5 VAC | 207 / 0.5 | Measure voltage with DMM | DMM (Fluke8810A) |
| 14.3 | Contact loads | Connect a 230V load, 5KΩ/50W resistor | — | X519 -> X1028 | — | — | Relay | Relay control |
| 14.4 | Test triac | Switch Triac OFF, measure voltage @ U5000; Switch Triac ON, measure voltage @ U5000 | — | P1010/P5015 | 253 VAC / 1.5 VAC | 207 / 0.5 | Measure voltage with DMM | DMM (Fluke8810A) |
| 14.5 | Load relay safety pulse | Turn off PEC 1&2, check OFF state of all relays | — | — | — | — | Measure voltage with DMM | DMM (Fluke8810A) |
| 15.1 | Power consumption during Power Saving mode | Send D-Bus message for defined state of µC, measure active power, Send D-Bus message | — | X201.1 -> X201.2 | 0.25 W | 0.15 W | — | D-Bus |
| 16.1 | Read HW and FW ID | — | — | — | — | — | — | D-Bus |
| 16.2 | Read Tracing ID | — | — | — | — | — | — | D-Bus |
| 16.3 | Read Production Time | — | — | — | — | — | — | D-Bus |
| 17.1 | DUT OFF | — | — | — | — | — | Relay | Relay control |
| 18.1 | Print label and attach | — | — | — | — | — | Printer | Printer |

---

> **TE:** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **QE\R&D:** &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; **Date:**
