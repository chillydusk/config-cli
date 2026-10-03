# config-cli

> 配置文件驱动的 DeepSeek 命令行助手 —— 换模型、换语气、换场景，只改配置，不动代码。

## 功能

- `ask` 子命令：向 DeepSeek 提问；裸跑显示当前生效的配置
- 行为全部由 `config.json` 驱动（模型 / temperature / 输出上限 / system prompt）
- 出错说人话（key 无效 / 网络不通 / 配置写错），退出码规范
- 运行记录写入 `config-cli.log`，排查有据可依

## 快速开始

 1. 环境要求：Python 3.13+ 与 uv（[uv 文档](https://docs.astral.sh/uv/)）
 2. 克隆仓库：`git clone https://github.com/chillydusk/config-cli.git && cd config-cli`（[GitHub 主页](https://github.com/chillydusk/config-cli)）
 3. 安装依赖：`uv sync`（自动创建虚拟环境）
 4. 配置密钥：`cp .env.example .env`，然后打开 `.env` 填入自己的 Key（[申请地址](https://platform.deepseek.com/)）
 5. 运行：`uv run config-cli ask "你好"`（预期输出见下方「用法示例」）

## 配置说明

配置文件 `config.json` 的字段（由 pydantic 模型 `LlmConfig` 定义）：

| 字段 | 类型 | 默认值 | 约束 |
|---|---|---|---|
| `model` | str | `deepseek-flash` | —— |
| `temperature` | float | 0.7 | 0 ~ 2 |
| `max_tokens` | int | 1024 | 1 ~ 4096 |
| `system_prompt` | str | 你是一个有帮助的助手。 | —— |

> 没有 `config.json` 时，全部字段使用默认值启动。

## 用法示例

```bash
$ uv run config-cli ask "测试"
你问：测试
回答：收到，测试正常。有什么需要帮忙的，直接说就行。
```

## 设计说明（为什么这么做）

- pydantic 进门校验（缺省补全、无损转换），坏数据到不了业务逻辑
- 两层错误说人话，便于理解
- 日志现场入档，便于日后排查定位问题
- AskError 翻译层，用“人话”给用户提供看得懂的报错提示
- 秘密与设置分离，确保隐私不泄露

## 项目结构

```
config-cli/
├── src/config_cli/__init__.py   # 全部代码（约 130 行，一个文件）
├── config.json                  # 运行配置（模型 / 温度 / 输出上限 / system prompt）
├── .env.example                 # 环境变量模板（复制为 .env 填入自己的 Key）
├── demo.py                      # 学习练习场（pydantic 实验，可忽略）
├── pyproject.toml               # 项目定义、依赖、入口点
└── README.md
```

