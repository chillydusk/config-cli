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
