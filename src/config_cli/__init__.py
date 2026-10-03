import json
import logging
import os
import sys
from pathlib import Path

import openai
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, ConfigDict, Field, ValidationError

logging.basicConfig(
    filename="config-cli.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    encoding="utf-8",
)
logger = logging.getLogger(__name__)


class AskError(Exception):
    """问模型失败（网络 / 鉴权 / API 拒绝）—— 消息已写成人话，可直接展示给用户。"""


class LlmConfig(BaseModel):
    model_config = ConfigDict(extra="forbid")

    model: str = "deepseek-flash"
    temperature: float = Field(default=0.7, ge=0, le=2)
    max_tokens: int = Field(default=1024, ge=1, le=4096)
    system_prompt: str = "你是一个有帮助的助手。"


CONFIG_FILE = Path("config.json")
USAGE = """用法：
  config-cli ask "你的问题"                   提问
  config-cli ask --model <模型名> "你的问题"   临时指定模型提问
  config-cli config show                      查看当前生效的配置"""


def load_config() -> LlmConfig | None:
    if not CONFIG_FILE.exists():
        logger.warning("没找到 config.json,使用默认配置")
        print("没找到 config.json,使用默认配置")
        return LlmConfig()  # 返回默认配置
    try:
        text = CONFIG_FILE.read_text(encoding="utf-8")
        return LlmConfig.model_validate(json.loads(text))
    except ValidationError as e:
        for err in e.errors():
            location = err["loc"][0] if err["loc"] else "整体"
            logger.error("配置文件验证失败: %s → %s", location, err["msg"])
            print(location, "→", err["msg"])
        return None
    except json.JSONDecodeError as e:
        logger.error("JSON 解码错误: %s (第 %d 行, 第 %d 列)", e.msg, e.lineno, e.colno)
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
    try:
        resp = client.chat.completions.create(
            model=config.model,  # ← 映射表
            messages=[
                {"role": "system", "content": config.system_prompt},
                {"role": "user", "content": question},
            ],
            temperature=config.temperature,  # ← 映射表
            max_tokens=config.max_tokens,  # ← 映射表
        )
    except openai.AuthenticationError:
        logger.exception("API key 验证失败")
        raise AskError("API key 验证失败，请检查 DEEPSEEK_API_KEY 是否正确。") from None
    except openai.APIConnectionError:
        logger.exception("无法连接到 API")
        raise AskError("无法连接到 API，请检查网络连接。") from None
    except openai.APIStatusError as e:
        logger.exception("API 返回错误状态码 %s", e.status_code)
        raise AskError(f"API 返回错误状态码 {e.status_code}.") from None
    return resp.choices[0].message.content


def show_config(config: LlmConfig) -> None:
    # 就是原来那 5 行 print（一模一样），放在 main 上面
    print("当前配置：")
    print(f"  model         = {config.model}")
    print(f"  temperature   = {config.temperature}")
    print(f"  max_tokens    = {config.max_tokens}")
    print(f"  system_prompt = {config.system_prompt}")


def main() -> None:
    config = load_config()
    if config is None:
        raise SystemExit(1)  # 退出码 != 0：告诉外面"这次运行失败了"
    args = sys.argv[1:]
    if not args:
        show_config(config)
    elif args[0] == "config":
        if len(args) > 1 and args[1] == "show":
            show_config(config)
        else:
            print(USAGE)
            raise SystemExit(1)  # 退出码 != 0：告诉外面"这次运行失败了"
    elif args[0] == "ask":
        rest = args[1:]
        if rest and rest[0] == "--model":
            if len(rest) < 2:
                print(USAGE)
                raise SystemExit(1)
            config = config.model_copy(update={"model": rest[1]})
            rest = rest[2:]
        question = " ".join(rest)
        if not question:
            print("请提供一个问题。")
            print("用法：config-cli ask '你的问题'")
            raise SystemExit(1)  # 退出码 != 0：告诉外面"这次运行失败了"
        # api_key = get_api_key()
        # print(f"API key 已读取（{len(api_key)} 个字符）")API key读取检验
        print(f"你问：{question}")
        logger.info("ask:model=%s, question=%s", config.model, question)
        try:
            answer = ask_model(question, config)
        except AskError as e:
            print(e)
            raise SystemExit(1)
        print(f"回答：{answer}")
    else:
        print(f"未知命令: {args[0]}")
        print(USAGE)
        raise SystemExit(1)
