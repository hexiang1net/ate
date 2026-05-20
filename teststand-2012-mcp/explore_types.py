"""探查 TestStand 2012 实际注册的步骤类型 —— GetTypeNames tuple"""
import sys
sys.path.insert(0, r"E:\agent\teststand-2012-mcp")
from ts_engine import get_engine

engine = get_engine().engine

# GetTypeNames 返回 tuple
print("=== engine.GetTypeNames() ===")
names = engine.GetTypeNames()
print(f"Type: {type(names)}, Length: {len(names)}")
for i, name in enumerate(names):
    print(f"  [{i}] {name}")

# GetTypes 返回的 CDispatch
print("\n=== engine.GetTypes() (通过 for in) ===")
types = engine.GetTypes()
print(f"Type: {type(types)}")
try:
    it = iter(types)
    for i, t in enumerate(it):
        try:
            print(f"  [{i}] {t.Name}")
        except Exception as e2:
            print(f"  [{i}] {t} (no .Name: {e2})")
except Exception as e:
    print(f"Cannot iterate: {e}")

# 测试 NewStep 需要 adapter 的 key name?
print("\n=== 测试 NewStep 使用 KeyName ===")
adapter_keys = []
for i in range(engine.NumAdapters):
    a = engine.GetAdapter(i)
    adapter_keys.append(a.KeyName)
    print(f"  Adapter[{i}]: Name={a.Name}, KeyName={a.KeyName}")

# 用正确的 key name 测试 NewStep
test_cases = [
    ("None Adapter", "Wait"),
    ("None Adapter", "If"),
    ("Sequence Adapter", "SequenceCall"),
    ("None Adapter", "Action"),
]
print("\n=== NewStep 测试 ===")
for adapter, step_type in test_cases:
    try:
        step = engine.NewStep(adapter, step_type)
        print(f"  OK: adapter='{adapter}', type='{step_type}'")
    except Exception as e:
        err = str(e)[:120]
        print(f"  FAIL: adapter='{adapter}', type='{step_type}' -> {err}")

print("\n=== 完成 ===")
