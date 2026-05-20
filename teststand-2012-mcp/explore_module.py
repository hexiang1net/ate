"""查找步骤计数和序列访问的正确方法"""
import sys
sys.path.insert(0, r"E:\agent\teststand-2012-mcp")
from ts_engine import get_engine

ts = get_engine()
engine = ts.engine
seq_file = ts.new_sequence_file()
main_seq = seq_file.GetSequenceByName("MainSequence")

# 添加几个步骤
for i, (adapter, stype) in enumerate([
    ("None Adapter", "MessagePopup"),
    ("None Adapter", "NI_Wait"),
    ("None Adapter", "NumericLimitTest"),
]):
    step = ts.new_step(adapter, stype)
    step.Name = f"Step{i}"
    seq_file.AsPropertyObjectFile().TypeUsageList.AddUsedTypes(step.AsPropertyObject())
    main_seq.InsertStep(step, 0, 2)  # Main group

# 步骤计数方法测试
print("=== 步骤计数 ===")
for method in ["NumSteps", "StepCount", "get_NumSteps", "get_StepCount"]:
    try:
        attr = getattr(main_seq, method, None)
        if attr is not None:
            print(f"  {method}: {attr}")
    except Exception as e:
        print(f"  {method}: {str(e)[:50]}")

# 遍历所有步骤
print("\n=== 遍历步骤 ===")
idx = 0
while True:
    try:
        step = main_seq.GetStep(idx, 2)
        print(f"  Step[{idx}]: {step.Name}")
        idx += 1
    except:
        print(f"  (Stop at index {idx})")
        break

# GetSequence 按索引
print("\n=== 序列列表 ===")
for i in range(seq_file.NumSequences):
    try:
        seq = seq_file.GetSequence(i)
        print(f"  [{i}] {seq.Name}")
    except Exception as e:
        print(f"  [{i}] {str(e)[:50]}")

# Save 测试
print("\n=== 保存测试 ===")
try:
    seq_file.Save(r"C:\Temp\test_save.seq")
    print("  Save OK")
except Exception as e:
    print(f"  Save error: {str(e)[:80]}")

print("\n=== 完成 ===")
