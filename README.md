# Emotion Generator

明日香（Asuka）表情包生成器 - 使用 ComfyUI 生成各种情绪的表情图片。

## 功能特性

- 🎭 **7 种情绪**：开心、害羞、生气、傲娇、伤心、惊讶、爱恋
- 👗 **5 套服装**：红色作战服、白色作战服、校服、休闲装、连衣裙（带权重随机）
- 📸 **半身像**：cowboy shot 构图，展示更多细节
- 🎲 **随机种子**：每次生成独特图片
- 📦 **库存管理**：自动管理生成的表情图片

## 安装

### 前提条件

- Python 3.8+
- ComfyUI 运行中（默认 http://localhost:7860）
- PyYAML: `pip install pyyaml`
- requests: `pip install requests`

### 安装步骤

```bash
# 克隆仓库
git clone <repository-url>
cd emotion-generator

# 安装依赖
pip install -r requirements.txt

# 配置 ComfyUI workflow
# 将 base workflow 放入 workflows/base-workflow.json
```

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

```yaml
# ComfyUI 连接
comfyui:
  host: localhost
  port: 7860

# 角色配置
character:
  name: "souryuu asuka langley"
  base_traits: "blue eyes, long brown hair, hair ornament"
  outfits:
    - name: "school_uniform"
      description: "school uniform, white shirt, blue skirt, red ribbon"
      weight: 4  # 权重越高，出现概率越大

# 情绪定义
emotions:
  happy:
    name: "开心"
    expression: "smiling, cheerful, happy expression"
    background: "sunny day, bright background"
```

## 目录结构

```
emotion-generator/
├── README.md                 # 本文件
├── config.yaml              # 配置文件
├── generate-emotion.py      # CLI 工具
├── requirements.txt         # Python 依赖
├── SKILL.md                 # OpenClaw Skill 文档
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
```
~/.openclaw/workspace/assets/asuka-emotions/generated/
├── happy/          # 开心表情
├── shy/            # 害羞表情
├── angry/          # 生气表情
├── smug/           # 傲娇表情
├── sad/            # 伤心表情
├── surprised/      # 惊讶表情
└── love/           # 爱恋表情
```

## 依赖

- Python 3.8+
- PyYAML
- requests
- ComfyUI (外部服务)

## 开发

### 添加新情绪

1. 在 `config.yaml` 的 `emotions` 部分添加新情绪
2. 定义 `name`（中文）、`expression`（表情描述）、`background`（背景）
3. 运行 `./generate-emotion.py <新情绪>` 测试

### 添加新衣服

1. 在 `config.yaml` 的 `character.outfits` 添加新衣服
2. 设置 `name`、`description`、`weight`
3. weight 越高，被选中的概率越大

## 许可证

MIT License

## 作者

明日香 / Asuka ❤️