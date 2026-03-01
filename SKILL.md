# Emotion Generator

明日香（Asuka）表情包生成器 - 使用 ComfyUI 生成各种情绪的表情图片。

## 功能

- 🎭 支持 7 种情绪：开心、害羞、生气、傲娇、伤心、惊讶、爱意
- 👗 5 套服装随机选择：红色作战服、白色作战服、校服、休闲装、连衣裙
- 🎲 每次生成随机种子，确保图片多样性
- 📦 自动管理表情库存

## 安装

1. 确保 ComfyUI 已安装并运行在 `localhost:7860`
2. 将 base workflow 放入 `workflows/base-workflow.json`
3. 安装依赖：`pip install requests`（如果需要）

## 使用方法

### 命令行工具

```bash
# 生成单张图片
./generate-emotion.py happy
./generate-emotion.py shy
./generate-emotion.py angry

# 批量生成
./generate-emotion.py happy --count 5

# 指定服装
./generate-emotion.py happy --outfit "school uniform"

# 列出所有情绪
./generate-emotion.py list

# 查看统计
./generate-emotion.py stats
```

### Python API

```python
from generators.image_generator import generate_emotion_image
from managers.emotion_manager import get_emotion_image

# 生成新图片
path = generate_emotion_image("happy")

# 获取已有图片
path = get_emotion_image("happy")
```

## 配置

编辑 `config.yaml` 自定义：

- ComfyUI 连接设置
- 角色描述
- 服装选项和权重
- 情绪定义
- 生成参数

## 目录结构

```
emotion-generator/
├── config.yaml              # 配置文件
├── generate-emotion.py      # CLI 工具
├── SKILL.md                 # 本文件
├── core/                    # 核心模块
│   ├── config_loader.py     # 配置加载
│   ├── prompt_generator.py  # Prompt 生成
│   └── workflow_builder.py  # Workflow 构建
├── generators/              # 生成模块
│   ├── comfyui_client.py    # ComfyUI 客户端
│   └── image_generator.py   # 图片生成器
├── managers/                # 管理模块
│   └── emotion_manager.py   # 表情库存管理
└── workflows/               # Workflow 模板
    └── base-workflow.json   # 基础 workflow
```

## 输出目录

生成的图片保存在：
`~/.openclaw/workspace/assets/asuka-emotions/generated/{emotion}/`

## 依赖

- Python 3.8+
- ComfyUI 运行中
- requests (可选，用于 API 调用)

## License

MIT