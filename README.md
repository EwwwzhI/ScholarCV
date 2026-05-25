# ScholarCV

ScholarCV 是一个面向中文学术简历的自动排版工具。项目使用 Markdown 维护简历内容，自动生成结构化 LaTeX，并通过 XeLaTeX 编译为单页 PDF。

## 功能特点

- 使用 `resume_config.md` 管理基础信息、教育背景、科研经历、竞赛经历、项目经历等内容。
- 自动处理证件照和校徽：证件照按目标比例裁切，校徽自动去白边并控制分辨率。
- 自动估算 A4 页面高度，并连续求解行距与模块间距，让内容落在目标饱满区间。
- 支持中文等效字符宽度估算，减少中英文混排导致的换行误差。
- 支持标题颜色、正文颜色、分割线颜色配置。
- 支持模块标题左侧 PNG 图标；图标缺失时自动回退为纯文字标题。

## 环境要求

- Python 3.9+
- Pillow
- XeLaTeX（推荐 MiKTeX 或 TeX Live）

安装 Python 依赖：

```powershell
pip install pillow
```

确认本机可以调用 XeLaTeX：

```powershell
xelatex --version
```

## 快速开始

1. 编辑 `resume_config.md`。
2. 将证件照、校徽放在项目根目录，并在 `resume_config.md` 中填写文件名。
3. 运行：

```powershell
$env:PYTHONIOENCODING='utf-8'; python main.py
```

生成文件：

- `output_resume.pdf`：最终 PDF 简历
- `output_resume.tex`：中间 LaTeX 源码，便于排查排版问题

## Markdown 写法

头部使用 YAML 风格配置：

```md
---
姓名: 张三
联系电话: 13800000000
电子邮箱: name@example.com
研究方向: 多模态感知
证件照: 证件照.png
校徽: 校徽.png
---
```

头部除 `姓名`、`联系电话`、`电子邮箱`、`证件照`、`校徽` 外，最多可以额外填写 1 个自定义选填字段；字段名不限定为固定候选项。

正文模块使用二级标题：

```md
## 教育背景

### 学校名称 | 学院专业 | 时间或身份

- **学业成绩：** 内容
- **核心课程：** 内容
```

三级标题必须使用三段式：

```md
### 左侧标题 | 中间信息 | 右侧信息
```

当左侧标题超过单行左栏宽度时，渲染器会自动让左侧标题先独占一行，并在下一行左列继续显示标题剩余部分；中间信息、右侧信息仍保持原来的中列和右列排版。

## 配置说明

### 排版配置

`config.py` 负责纸张、边距、图像尺寸、模块间距、标题列宽、自动排版阈值等物理排版参数。

建议日常只调整这些参数：

- `MARGIN_TOP` / `MARGIN_BOTTOM`：页面上下边距
- `AVATAR_WIDTH_MM` / `AVATAR_HEIGHT_MM`：证件照显示尺寸
- `LOGO_HEIGHT_MM`：校徽显示高度
- `LAYOUT_TARGET_MIN_RATIO` / `LAYOUT_TARGET_MAX_RATIO`：连续排版求解的目标高度区间
- `LAYOUT_SAFETY_MARGIN_MM`：连续求解时预留的页面硬安全冗余

其他参数用于自动排版和内部布局校准，通常不建议频繁调整。

### 视觉配置

`style_config.py` 负责颜色和图标。

颜色使用 HTML 十六进制色值，不需要写 `#`：

```python
TITLE_COLOR = "000000"
BODY_COLOR = "000000"
RULE_COLOR = "000000"
```

图标总开关：

```python
ENABLE_SECTION_ICONS = True
```

单个模块开关：

```python
SECTION_ICON_ENABLED = {
    "基本信息": True,
    "教育背景": True,
}
```

图标路径配置：

```python
SECTION_ICONS = {
    "基本信息": "icons/basic.png",
    "教育背景": "icons/education.png",
}
```

图标 PNG 放入 `icons/` 目录即可。图片不存在时不会报错，会自动使用纯文字标题。

## 连续排版

ScholarCV 会先估算标准排版高度，再在最紧凑和最舒展参数之间连续插值，直接求解一组接近目标高度的排版参数。

默认目标高度区间为可用正文高度的 `95% - 99%`。求解器会优先贴近区间上沿，让页面保持饱满，同时受 `LAYOUT_SAFETY_RATIO` 和 `LAYOUT_SAFETY_MARGIN_MM` 约束，避免估算误差导致超页。

连续求解会同步调整：

- `line_stretch`：正文行距
- `module_sep`：模块间距
- `item_sep`：列表项间距
- `header_body_sep`：头部与正文间距

文字宽度估算由 `typography.py` 统一处理，会区分普通/加粗文本、英文单词、中文、数字、标点和显式空格，用于正文高度估算与标题换行。

如果内容明显过少或过多，程序会阻断生成并给出删减或补充建议。

## 文件结构

```text
main.py              # 构建入口
parser.py            # Markdown 解析与校验
engine.py            # 高度估算与连续排版求解
render.py            # LaTeX 模板渲染
typography.py        # 文字宽度估算与标题断行规则
image_processor.py   # 证件照与校徽预处理
config.py            # 物理排版配置
style_config.py      # 视觉样式与图标配置
resume_config.md     # 简历内容
icons/               # 模块标题图标
```

## 常见问题

### PDF 文字正常，但 PNG 预览中文字缺失

这通常是 Poppler 缺少中文字体映射导致的预览问题，不代表 XeLaTeX 生成的 PDF 内容缺失。

### 图标显示太小

LaTeX 会按 `SECTION_ICON_SIZE` 控制图标高度。如果 PNG 自身有大白边，视觉上会显得小。建议使用透明背景、少留白的线性图标。

### 生成失败并提示内容过少

工具不会用大幅拉伸伪装内容饱满。建议补充科研、竞赛、项目或综合素质内容。
