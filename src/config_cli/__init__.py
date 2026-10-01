import json
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field, ValidationError


class LlmConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = "deepseek-flash"
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1024, ge=1, le=4096)
    system_prompt: str = "你是一个有帮助的助手。"


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


def main() -> None:
    config = load_config()
    if config is None:
        raise SystemExit(1)  # 退出码 != 0：告诉外面"这次运行失败了"

    print("当前配置：")
    print(f"  model         = {config.model}")
    print(f"  temperature   = {config.temperature}")
    print(f"  max_tokens    = {config.max_tokens}")
    print(f"  system_prompt = {config.system_prompt}")
