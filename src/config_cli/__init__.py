import json
import os
import sys
from pathlib import Path

import openai
from dotenv import load_dotenv
from openai import OpenAI
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


def get_api_key() -> str:
    load_dotenv()  # 从 .env 文件加载环境变量
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("没找到 DEEPSEEK_API_KEY，检查 .env 文件")
    return api_key


def ask_model(question: str, config: LlmConfig) -> str:
    client = OpenAI(
        api_key=get_api_key(),
        base_url="https://api.deepseek.com",
    )

    resp = client.chat.completions.create(
        model=config.model,  # ← 映射表
        messages=[
            {"role": "system", "content": config.system_prompt},
            {"role": "user", "content": question},
        ],
        temperature=config.temperature,  # ← 映射表
        max_tokens=config.max_tokens,  # ← 映射表
    )
    return resp.choices[0].message.content


def main() -> None:
    config = load_config()
    if config is None:
        raise SystemExit(1)  # 退出码 != 0：告诉外面"这次运行失败了"
    args = sys.argv[1:]

    if not args:
        print("当前配置：")
        print(f"  model         = {config.model}")
        print(f"  temperature   = {config.temperature}")
        print(f"  max_tokens    = {config.max_tokens}")
        print(f"  system_prompt = {config.system_prompt}")
    elif args[0] == "ask":
        question = " ".join(args[1:])
        if not question:
            print("请提供一个问题。")
            print("用法：config-cli ask '你的问题'")
            raise SystemExit(1)  # 退出码 != 0：告诉外面"这次运行失败了"
        # api_key = get_api_key()
        # print(f"API key 已读取（{len(api_key)} 个字符）")API key读取检验
        print(f"你问：{question}")
        try:
            answer = ask_model(question, config)
        except openai.AuthenticationError:
            print("API key 验证失败，请检查 DEEPSEEK_API_KEY 是否正确。")
            raise SystemExit(1)
        except openai.APIConnectionError:
            print("无法连接到 API，请检查网络连接。")
            raise SystemExit(1)
        except openai.APIStatusError as e:
            print(f"API 返回错误状态码 {e.status_code}.")
            raise SystemExit(1)
        print(f"回答：{answer}")
    else:
        print(f"未知命令: {args[0]}")
        print("用法：config-cli ask '你的问题'")
        raise SystemExit(1)
