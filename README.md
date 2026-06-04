# ScholarCV

ScholarCV 是一个面向中文学术简历的自动排版工具。项目使用 Markdown 维护简历内容，自动生成结构化 LaTeX，并通过 XeLaTeX 编译为单页 PDF。

## 功能特点

- 使用 `resume_config.md` 管理基础信息、教育背景、科研经历、竞赛经历、项目经历等内容。
- 支持 `classic`、`centered` 和 `hybrid` 三种头部模板；`classic` 自动处理证件照和校徽，`hybrid` 使用整行居中信息、左右浮动图片布局。
- 自动估算 A4 页面高度，并连续求解行距与模块间距，让内容落在目标饱满区间。
- 支持中文等效字符宽度估算，减少中英文混排导致的换行误差。
- 支持标题颜色、正文颜色、分割线颜色配置。
- 支持模块标题左侧 PNG 图标；图标缺失时自动回退为纯文字标题。
- 支持 `centered` 头部联系方式前置图标，可按字段开关并自定义 PNG。
- 同一模块内多个三级标题项目支持按标题前置指令自定义间隔，默认使用 1mm 无视觉分隔。

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
2. 使用 `classic` 或 `hybrid` 头部模板时，将证件照、校徽等图片放在项目根目录，并在 `resume_config.md` 中填写文件名。
3. 运行：

```powershell
$env:PYTHONIOENCODING='utf-8'; python main.py
```

生成文件：

- `output_resume.pdf`：最终 PDF 简历
- `output_resume.tex`：中间 LaTeX 源码，便于排查排版问题
- `temp/`：预处理后的证件照和校徽，文件名与原图一致，供 `output_resume.tex` 直接引用

## Markdown 写法

头部使用 YAML 风格配置：

```md
---
头部模板: classic
姓名: 张三
联系电话: 13800000000
电子邮箱: name@example.com
研究方向: 多模态感知
证件照: 证件照.png
校徽: 校徽.png
---
```

`头部模板` 可省略，默认使用 `classic`。`classic` 保持当前图文头部，必须填写 `证件照` 和 `校徽`，且除 `姓名`、`联系电话`、`电子邮箱`、`证件照`、`校徽`、`头部模板` 外最多填写 1 个自定义选填字段。

纯文字居中头部使用 `centered`，不需要证件照和校徽：

```md
---
头部模板: centered
姓名: HIJIANGTAO
联系电话: (+86) 123-4567-8910
电子邮箱: hi@hijiangtao.com
个人主页: https://hijiangtao.github.io/
GitHub: https://github.com/hijiangtao
---
```

`centered` 最多显示 4 个联系方式，会按 YAML 头部中的书写顺序读取这些非空字段：`电子邮箱`、`联系电话`、`个人主页`、`GitHub`。`GitHub主页` 会作为 `GitHub` 的兼容别名，但推荐新配置使用 `GitHub`；如果两个字段都填写，只会渲染先出现的一个。其它头部字段不会自动显示在联系方式行。联系方式前可显示图标，默认使用 Font Awesome 图标；也可以在 `style_config.py` 中改为自定义 PNG。

整行居中姓名信息、左右浮动图片的混合头部使用 `hybrid`：

```md
---
头部模板: hybrid
姓名: 某某某
联系电话: (+86) 138-xxxx-xxxx
性别: 男
电子邮箱: example@email.com
籍贯: 某省某市
校徽: 校徽.png
证件照: 证件照.png
---
```

`hybrid` 必须填写 `姓名` 和 `证件照`。`校徽` 可选；不填写时姓名信息和右侧证件照位置不变。头部外层是一整行内容区：姓名和信息按整行可用宽度水平居中，并在头部高度内垂直居中；校徽以零宽浮动方式贴在左上角，证件照以零宽浮动方式贴在右上角，左右图片都不参与姓名信息的居中计算。整行内容区宽度、右侧证件照宽度和校徽宽度都可在 `config.py` 中调节；校徽和证件照会在各自宽度和头部高度内等比缩放。信息区按 YAML 头部中的书写顺序读取字段，自动排除 `头部模板`、`姓名`、`证件照`、`校徽`，最多显示 4 项，每行最多 2 项、共最多 2 行。标签默认使用字段名，并内置短标签：`联系电话` 显示为 `手机`，`电子邮箱` 显示为 `邮箱`。

正文模块使用二级标题：

```md
## 教育背景

### 学校名称 | 学院 | 专业 | 时间

- **学业成绩：** 内容
- **核心课程：** 内容
```

三级标题支持一段、三段或四段：

```md
### 完整标题
### 左侧标题 | 中间信息 | 右侧信息
### 左侧标题 | 中间信息 1 | 中间信息 2 | 右侧信息
```

一段标题会占满正文宽度并自然换行。三段标题保持左列、中列、右列排版；当左侧标题超过单行左栏宽度时，渲染器会自动让左侧标题先独占一行，并在下一行左列继续显示标题剩余部分；中间信息、右侧信息仍保持原来的中列和右列排版。四段标题会把三段标题中的左列拆成两列，第二段居中显示，第三段和第四段仍沿用原中列、右列位置。

同一二级模块内，非首个三级标题可以在标题前设置和上一个项目之间的间隔模式：

```md
### 第一个项目

<!-- project-sep: dashed -->
### 第二个项目

<!-- project-sep: space -->
### 第三个项目
```

支持 `none`、`dashed`、`space` 三种模式。默认 `none`，不加虚线，仅保留 `1mm` 基础项目间距；`dashed` 使用虚线分隔；`space` 只额外增加 `2mm` 空距。指令只能写在某个二级模块内的非首个三级标题前，只作用于紧随其后的一个三级标题。

## 配置说明

### 排版配置

`config.py` 负责纸张、边距、图像尺寸、模块间距、标题列宽、自动排版阈值等物理排版参数。

建议日常只调整这些参数：

- `MARGIN_TOP` / `MARGIN_BOTTOM`：页面上下边距
- `BALANCE_VERTICAL_WHITESPACE`：是否用弹性空白平衡页面上下剩余空间
- `BALANCE_VERTICAL_TOP_WEIGHT` / `BALANCE_VERTICAL_BOTTOM_WEIGHT`：弹性空白的顶部/底部分配权重，默认 `0.4 / 0.6`
- `AVATAR_WIDTH_MM` / `AVATAR_HEIGHT_MM`：证件照显示尺寸
- `LOGO_HEIGHT_MM`：校徽显示高度
- `CENTERED_HEADER_TOP_SEP_MM`：`centered` 头部上方额外留白，默认 `0mm`
- `HYBRID_HEADER_CONTENT_WIDTH_MM` / `HYBRID_HEADER_RIGHT_WIDTH_MM` / `HYBRID_LOGO_WIDTH_MM`：`hybrid` 头部整行内容区宽度、右侧证件照宽度和左上角浮动校徽宽度。内容区默认等于正文可用宽度；右侧证件照宽度会按证件照比例推导头部高度，校徽和证件照会在各自限制内等比缩放
- `ITEMIZE_INDENT_MM`：列表整体左缩进，渲染端 `leftmargin` 与高度估算端行宽同步
- `ITEMIZE_TOPSEP_MM`：列表环境自身上下间距，当前默认 `0`；标题到列表的入口间距跟随动态 `item_sep`
- `PROJECT_SEP_BASE` / `PROJECT_SEPARATOR_AFTER_SEP_MM`：`project-sep: dashed` 虚线前后额外间距，当前默认不额外叠加；为 `0` 时不会输出多余的 `\vspace{0mm}`
- `PROJECT_SEPARATOR_NONE_MM`：默认 `project-sep: none` 模式的基础项目间距，默认 `1mm`
- `PROJECT_SEPARATOR_SPACE_MM`：`project-sep: space` 模式的额外项目间距，默认 `2mm`
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

`centered` 头部联系方式图标总开关：

```python
ENABLE_CENTERED_HEADER_ICONS = True
```

单个联系方式图标开关：

```python
CENTERED_HEADER_ICON_ENABLED = {
    "电子邮箱": True,
    "联系电话": True,
    "个人主页": True,
    "GitHub": True,
}
```

自定义 PNG 图标路径；留空或文件不存在时使用默认 Font Awesome 图标：

```python
CENTERED_HEADER_ICONS = {
    "电子邮箱": "icons/email.png",
    "联系电话": "icons/phone.png",
    "个人主页": "icons/web.png",
    "GitHub": "icons/github.png",
}
```

默认图标也可以改成其它 LaTeX 命令；如果不想使用默认图标，把对应字段设为空字符串：

```python
CENTERED_HEADER_ICON_COMMANDS = {
    "电子邮箱": r"\faEnvelope",
    "联系电话": r"\faPhone",
    "个人主页": r"\faGlobe",
    "GitHub": r"\faGithub",
}
```

## 连续排版

ScholarCV 会先估算标准排版高度，再在最紧凑和最舒展参数之间连续插值，直接求解一组接近目标高度的排版参数。

默认目标高度区间为可用正文高度的 `98% - 100%`。求解器会优先贴近区间上沿，让页面保持饱满，同时受 `LAYOUT_SAFETY_RATIO` 和 `LAYOUT_SAFETY_MARGIN_MM` 约束，避免估算误差导致超页。

连续求解会同步调整：

- `line_stretch`：正文行距
- `module_sep`：模块间距
- `item_sep`：列表项间距，同时作为标题到列表的入口间距
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
