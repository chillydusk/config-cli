import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class Todo(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str
    done: bool = False
    priority: int = Field(default=1, ge=1, le=5)


class LlmConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = "deepseek-flash"
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1024, ge=1, le=4096)
    system_prompt: str = "你是一个有帮助的助手。"


print("=== 正常创建 ===")
t = Todo(title="学Python")
print(t)
print("转成字典:", t.model_dump())
print("点号取字段:", t.title, "|", t.done, "|", t.priority)

print()
print("=== 键名写错 ===")
try:
    Todo(titl="学Python")
except ValidationError as e:
    for err in e.errors():
        print(err["loc"][0], "→", err["msg"])

print()
print("=== 类型自动转换 ===")
t2 = Todo(title="x", done="false")
print("传进去的是字符串 'false'，出来是:", type(t2.done).__name__, "=", t2.done)

print()
print("=== 超出范围 ===")
try:
    Todo(title="x", priority=99)
except ValidationError as e:
    for err in e.errors():
        print(err["loc"][0], "→", err["msg"])

print("=== LlmConfig() 什么都不传 ===")
llm_config = LlmConfig()
print(llm_config)
print("=== 传 temperature=1.5, max_tokens=4096,system_prompt='你是大肥鱼' ===")
llm_config2 = LlmConfig(temperature=1.5, max_tokens=4096, system_prompt="你是大肥鱼")
print(llm_config2)
print("=== 传 temperature=5 ===")
try:
    LlmConfig(temperature=5)
except ValidationError as e:
    for err in e.errors():
        print(err["loc"][0], "→", err["msg"])

print("=== 传 max_tokens=0 ===")
try:
    LlmConfig(max_tokens=0)
except ValidationError as e:
    for err in e.errors():
        print(err["loc"][0], "→", err["msg"])
print("=== 传 字符串 ===")
try:
    LlmConfig(temperature="0.5")
except ValidationError as e:
    for err in e.errors():
        print(err["loc"][0], "→", err["msg"])
print("=== 传 汉字 ===")
try:
    LlmConfig(temperature="热")
except ValidationError as e:
    for err in e.errors():
        print(err["loc"][0], "→", err["msg"])
print("=== 传字符串5 ===")
try:
    LlmConfig(temperature="5")
except ValidationError as e:
    for err in e.errors():
        print(err["loc"][0], "→", err["msg"])
print("=== model_validate 小演示 ===")
data = {"temperature": 1.5}  # 假装这是从 json 读出来的字典
config = LlmConfig.model_validate(data)  # 校验 + 转换
print(config.temperature)
CONFIG_FILE = Path("config.json")


def load_config() -> LlmConfig | None:
    if not CONFIG_FILE.exists():
        print("没找到 config.json,使用默认配置")
        return LlmConfig()  # 返回默认配置
    try:
        text = CONFIG_FILE.read_text(encoding="utf-8")
        return LlmConfig.model_validate(json.loads(text))
    except ValidationError as e:
        for err in e.errors():
            print(err["loc"][0], "→", err["msg"])
        return None
    except json.JSONDecodeError as e:
        print(f"JSON 解码错误: {e.msg} (第 {e.lineno} 行, 第 {e.colno} 列)")
        return None


print("=== 读 config.json ===")
config = load_config()
print(config)

# ==== 四小件 · 练习 1：推导式 ====
nums = [3, -1, 7, 0, 4, -2]
# 1a) 一行得到 [9, 49, 16]（正数的平方）
squares = [x**2 for x in nums if x > 0]
print(squares)
errs = [
    {"loc": ("temperature",), "msg": "超出范围"},
    {"loc": ("model",), "msg": "不能为空"},
]
# 1b) 一行得到 {"temperature": "超出范围", "model": "不能为空"}
err_dict = {err["loc"][0]: err["msg"] for err in errs}
print(err_dict)

records = [
    {"model": "flash", "ok": True, "tokens": 120},
    {"model": "pro", "ok": True, "tokens": 400},
    {"model": "flash", "ok": False, "tokens": 0},
    {"model": "flash", "ok": True, "tokens": 80},
]
# 1c) 一行算出成功记录的总 token（提示：sum(…) —— 这里藏了个下一轮的主角）
total_tokens = sum(record["tokens"] for record in records if record["ok"])
print(total_tokens)
# 1d) 一行列出成功记录里用过的模型（提示：想要"去重"的那种括号）
unique_models = {record["model"] for record in records if record["ok"]}
print(unique_models)

# ==== 练习 2：with ====
# 2a) 用 with open 往 with-demo.txt 写三行中文（utf-8）
with open("with-demo.txt", "w", encoding="utf-8") as f:
    f.write("第一行\n")
    f.write("第二行\n")
    f.write("第三行\n")
# 2b) 块结束之后验证 f.closed 是 True，再重新打开读出来打印
print(f.closed)
with open("with-demo.txt", "r", encoding="utf-8") as f:
    print(f.read())
# 2c) 灾难演习：with 块里写一行"写一半"然后 raise RuntimeError；
#     用 try/except 接住后检查：f.closed 还是 True 吗？文件里有没有"写一半"？
try:
    with open("with-demo.txt", "w", encoding="utf-8") as f:
        f.write("写一半")
        raise RuntimeError("灾难演习")
except RuntimeError as e:
    print("捕获到异常:", e)
    print("文件是否关闭:", f.closed)
    with open("with-demo.txt", "r", encoding="utf-8") as f2:
        print("文件内容:", f2.read())

# ==== 练习 3：生成器 ====
# 3a) 写生成器函数 countdown(n)，用 for 打印 countdown(3) → 3 2 1
def countdown1(n):
    while n > 0:
        yield n
        n -= 1
for x in countdown1(3):
    print(x)
# 3b) 惰性眼见为实：在 yield 前加一句 print("生产", n)；
#     先单独拿一个生成器对象（不消费），再跑 for —— 观察"生产"何时冒出来
def countdown2(n):
    while n > 0:
        print("生产", n)
        yield n
        n -= 1
for x in countdown2(3):
    print(x)
# 3c) 第四兄弟身份确认（两行对比）：
#     print(type([x for x in range(3)]))    → ?
#     print(type(x for x in range(3)))      → ?
print(type([x for x in range(3)]))    # 预期：<class 'list'>
print(type(x for x in range(3)))      # 预期：<class 'generator'>
print(len([x for x in range(3)]))     # 预期：3      —— 仓库：能数数
try:
    print(len(x for x in range(3)))       # 预期：TypeError（大意：generator 没有 len）
except TypeError as e:
    print("传送带数不了:", e)
# 传送带上没有"存货"，当然数不了 —— 这就是"惰性"的硬证据

# 3d) 彩蛋·预览 W5 流式（打字机效果）：
#     写生成器 lazy_typing(text)：每个字 yield 一次 + time.sleep(0.15)；
#     for 里 print(ch, end="", flush=True) —— 看字一个个蹦出来
#     （提示：文件顶部 import time；flush=True = "别攒着，立刻显示"）
def lazy_typing(text):
    import time
    for ch in text:
        yield ch
        time.sleep(0.15)
for ch in lazy_typing("打字机效果"):
    print(ch, end="", flush=True)
# ==== 练习 4：装饰器 ====
# 4a) 照抄 my_decorator + hello，跑通
def my_decorator(func):
    def wrapper(*args, **kwargs):
        print("正在调用函数:", func.__name__)
        result = func(*args, **kwargs)
        print("函数调用结束:", func.__name__)
        return result
    return wrapper

@my_decorator
def hello(name):
    print(f"Hello, {name}!")
hello("Alice")
# 4b) 自己写 timer 装饰器：打印"xxx 耗时 0.10 秒"
#     （提示：time.time() 前后各取一次相减；被装饰函数 sleep(0.1) 看得清楚）
def timer(func):
    import time
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"{func.__name__} 耗时 {elapsed_time:.2f} 秒")
        return result
    return wrapper
@timer
def slow_function():
    import time
    time.sleep(0.1)
slow_function()
# 4c) 思考题（先猜再试）：把 timer 用在【带两个参数】的函数上，
#     如果 wrapper 写成 def wrapper(name): 会怎样？为什么必须 *args, **kwargs？
def bad_timer(func):
    def wrapper(name):                 # ← 故意只收一个参数
        import time
        start = time.time()
        result = func(name)
        print(f"耗时 {time.time() - start:.2f} 秒")
        return result
    return wrapper

@bad_timer
def add(a, b):                         # ← 两个参数
    return a + b
try:
    add(1, 2)
except TypeError as e:
    print("实验结论:", e)
# 预期：TypeError（大意：wrapper() takes 1 positional argument but 2 were given）
# 亲眼看一次，然后你就永远懂了：wrapper 不知道未来会被套在什么签名的函数上
# → 唯一安全姿势 = *args, **kwargs 原样转发


