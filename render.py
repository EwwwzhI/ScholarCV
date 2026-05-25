import os
import re
from config import LayoutConfig
from style_config import StyleConfig
from typography import TypographyMetrics

# ==========================================
# 0. 全局排版物理常量区 (在此统一调节图片尺寸与高度)
# ==========================================
class RenderConfig:
    MARGIN_TOP = f"{LayoutConfig.MARGIN_TOP:g}mm"
    MARGIN_BOTTOM = f"{LayoutConfig.MARGIN_BOTTOM:g}mm"
    MARGIN_LEFT = f"{LayoutConfig.MARGIN_LEFT:g}mm"
    MARGIN_RIGHT = f"{LayoutConfig.MARGIN_RIGHT:g}mm"

    # 校徽高度 (宽度会等比例自动缩放)
    LOGO_HEIGHT = f"{LayoutConfig.LOGO_HEIGHT_MM / 10:g}cm"
    LOGO_INFO_SEP = f"{LayoutConfig.LOGO_INFO_SEP_BASE / 10:g}cm"
    BASIC_INFO_TABLE_GAP = f"{LayoutConfig.BASIC_INFO_TABLE_GAP_MM:g}mm"
    
    # 证件照固定尺寸 (这里直接决定 LaTeX 渲染的照片大小)
    AVATAR_WIDTH = f"{LayoutConfig.AVATAR_WIDTH_MM / 10:g}cm"
    AVATAR_HEIGHT = f"{LayoutConfig.AVATAR_HEIGHT_MM / 10:g}cm"
    HEADER_LEFT_SHORT_MAX = f"{LayoutConfig.HEADER_LEFT_SHORT_MAX_MM:g}mm"
    HEADER_LEFT_MEDIUM_MAX = f"{LayoutConfig.HEADER_LEFT_MEDIUM_MAX_MM:g}mm"
    HEADER_RIGHT_PADDING_SHORT_LEFT = f"{LayoutConfig.HEADER_RIGHT_PADDING_SHORT_LEFT_MM:g}mm"
    HEADER_RIGHT_PADDING_MEDIUM_LEFT = f"{LayoutConfig.HEADER_RIGHT_PADDING_MEDIUM_LEFT_MM:g}mm"
    HEADER_RIGHT_PADDING_LONG_LEFT = f"{LayoutConfig.HEADER_RIGHT_PADDING_LONG_LEFT_MM:g}mm"
    SECTION_BODY_SEP = f"{LayoutConfig.SECTION_BODY_SEP:g}mm"
    TITLE_LEFT_WIDTH = f"{LayoutConfig.TITLE_LEFT_WIDTH_MM:g}mm"
    TITLE_MIDDLE_WIDTH = f"{LayoutConfig.TITLE_MIDDLE_WIDTH_MM:g}mm"
    TITLE_RIGHT_WIDTH = f"{LayoutConfig.TITLE_RIGHT_WIDTH_MM:g}mm"
    TITLE_FULL_WIDTH = f"{LayoutConfig.VALID_WIDTH:g}mm"
    SECTION_ICON_SIZE = StyleConfig.SECTION_ICON_SIZE
    SECTION_ICON_TEXT_GAP = StyleConfig.SECTION_ICON_TEXT_GAP
    PAGE_BALANCE_GLUE = (
        r"\vspace*{\fill}"
        if getattr(LayoutConfig, "BALANCE_VERTICAL_WHITESPACE", False)
        else ""
    )

# ==========================================
# 1. 底层 LaTeX 骨架模板 (底部对齐 + 参数化占位符)
# ==========================================
BASE_TEX_TEMPLATE = r"""
\documentclass[11pt, a4paper]{article}

% --- 页面与排版基础设置 ---
\usepackage[top=[[MARGIN_TOP]], bottom=[[MARGIN_BOTTOM]], left=[[MARGIN_LEFT]], right=[[MARGIN_RIGHT]]]{geometry}
\usepackage{xeCJK}          
\usepackage{graphicx}       
\usepackage{enumitem}       
\usepackage{tabularx}       
\usepackage{array}
\usepackage{calc}           % 提供 \widthof 测距功能
\usepackage{xcolor}

\definecolor{cvTitle}{HTML}{[[TITLE_COLOR]]}
\definecolor{cvBody}{HTML}{[[BODY_COLOR]]}
\definecolor{cvRule}{HTML}{[[RULE_COLOR]]}

\newcolumntype{L}[1]{>{\raggedright\arraybackslash}p{#1}}
\newcolumntype{C}[1]{>{\centering\arraybackslash}p{#1}}
\newcolumntype{R}[1]{>{\raggedleft\arraybackslash}p{#1}}
\newlength{\headerleftinfowidth}
\newlength{\headerlefttempwidth}
\newlength{\headerrightpadding}
\newlength{\headerrightvaluewidth}
\newlength{\headerrighttempwidth}

% --- 引擎动态注入的全局行距 ---
\linespread{[[LINE_STRETCH]]}

% --- 自定义模块标题样式 ---
\newcommand{\cvsection}[2][[[MODULE_SEP]]]{
    \vspace{#1}
    {\Large\textcolor{cvTitle}{\textbf{#2}}} \vspace{2pt}
    {\color{cvRule}\hrule height 0.8pt}
    \vspace{[[SECTION_BODY_SEP]]}
}

\setlength{\parindent}{0pt}
\pagestyle{empty}
\hyphenpenalty=10000
\exhyphenpenalty=10000
\emergencystretch=1.5em

\begin{document}
\thispagestyle{empty}
\color{cvBody}
[[PAGE_TOP_BALANCE_GLUE]]

% ==========================================
% 头部基本信息区
% ==========================================
\noindent
\begin{minipage}[b]{0.74\textwidth}
    % 1. 左上角：注入配置区定义的校徽高度
    \noindent\includegraphics[height=[[LOGO_HEIGHT]]]{[[LOGO_PATH]]} \\[[[LOGO_INFO_SEP]]]
    
    {\Large\textcolor{cvTitle}{\textbf{[[BASIC_INFO_TITLE]]}}} \vspace{4pt}
    {\color{cvRule}\hrule height 0.8pt}
    \vspace{[[BASIC_INFO_TABLE_GAP]]}
    
    {
    \renewcommand{\arraystretch}{1.5}
    \setlength{\tabcolsep}{0pt}
    \settowidth{\headerrightvaluewidth}{[[PHONE]]}
    \settowidth{\headerrighttempwidth}{[[EMAIL]]}
    \ifdim\headerrighttempwidth>\headerrightvaluewidth
        \setlength{\headerrightvaluewidth}{\headerrighttempwidth}
    \fi
    \settowidth{\headerleftinfowidth}{[[NAME_LABEL]]：[[NAME]]}
    \settowidth{\headerlefttempwidth}{[[OPTIONAL_KEY]]：[[OPTIONAL_VALUE]]}
    \ifdim\headerlefttempwidth>\headerleftinfowidth
        \setlength{\headerleftinfowidth}{\headerlefttempwidth}
    \fi
    \ifdim\headerleftinfowidth<[[HEADER_LEFT_SHORT_MAX]]
        \setlength{\headerrightpadding}{[[HEADER_RIGHT_PADDING_SHORT_LEFT]]}
    \else
        \ifdim\headerleftinfowidth<[[HEADER_LEFT_MEDIUM_MAX]]
            \setlength{\headerrightpadding}{[[HEADER_RIGHT_PADDING_MEDIUM_LEFT]]}
        \else
            \setlength{\headerrightpadding}{[[HEADER_RIGHT_PADDING_LONG_LEFT]]}
        \fi
    \fi
    \begin{tabularx}{\linewidth}{@{} l @{\hspace{0.6mm}：\hspace{1.2mm}} l X r @{\hspace{0.6mm}：\hspace{1.2mm}} L{\headerrightvaluewidth} @{\hspace{\headerrightpadding}}}
        [[NAME_LABEL]] & [[NAME]] & & 联系电话 & [[PHONE]] \\
        [[OPTIONAL_KEY]] & [[OPTIONAL_VALUE]] & & 电子邮箱 & [[EMAIL]] \\
    \end{tabularx}
    }
\end{minipage}
\hfill
\begin{minipage}[b]{0.22\textwidth}
    \raggedleft 
    % 2. 右侧证件照：注入配置区定义的宽高
    \includegraphics[width=[[AVATAR_WIDTH]], height=[[AVATAR_HEIGHT]]]{[[AVATAR_PATH]]}
\end{minipage}

\vspace{[[HEADER_BODY_SEP]]}

% ==========================================
% 动态经历正文区
% ==========================================
[[BODY_CONTENT]]
[[PAGE_BOTTOM_BALANCE_GLUE]]

\end{document}
"""

# ==========================================
# 2. 核心渲染器类
# ==========================================
class LatexRenderer:
    def __init__(self, resume_data, spacing_config):
        self.data = resume_data
        self.spacing = spacing_config
        self.tex_code = BASE_TEX_TEMPLATE
        self.typography = TypographyMetrics(LayoutConfig.CHAR_WIDTH_MM)

    def _escape_latex(self, text, preserve_visible_spaces=True):
        """转义用户文本中的 LaTeX 特殊字符"""
        text = str(text)
        if preserve_visible_spaces:
            text = self.typography.protect_visible_cjk_spaces(text)

        escape_map = {
            '%': r'\%',
            '$': r'\$',
            '&': r'\&',
            '#': r'\#',
            '_': r'\_',
        }
        for char, escaped in escape_map.items():
            text = text.replace(char, escaped)
        
        # 粗体处理
        text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
        return text

    def _should_wrap_subtitle_first_block(self, text):
        """判断三级标题第一段是否需要独占一行。"""
        return (
            self.typography.measure_text_mm(text, "bold")
            > LayoutConfig.TITLE_LEFT_WIDTH_MM - LayoutConfig.TITLE_LEFT_WIDTH_SAFETY_MM
        )

    def _render_subtitle(self, blocks):
        """渲染三级标题；长第一段独占一行，二三段换到下一行。"""
        if self._should_wrap_subtitle_first_block(blocks[0]):
            block_a_head, block_a_tail = self.typography.split_text_by_width(
                blocks[0],
                LayoutConfig.VALID_WIDTH - LayoutConfig.TITLE_FULL_WIDTH_SAFETY_MM,
                "bold",
            )
            block_a_tail = self.typography.truncate_text_by_width(
                block_a_tail,
                LayoutConfig.TITLE_LEFT_WIDTH_MM - LayoutConfig.TITLE_LEFT_WIDTH_SAFETY_MM,
                "bold",
            )
            block_a = self._escape_latex(block_a_head)
            block_a_tail = self._escape_latex(block_a_tail)
            block_b = self._escape_latex(blocks[1])
            block_c = self._escape_latex(blocks[2])

            return (
                "\\noindent"
                f"\\begin{{tabular}}{{@{{}} L{{{RenderConfig.TITLE_LEFT_WIDTH}}} @{{}} "
                f"C{{{RenderConfig.TITLE_MIDDLE_WIDTH}}} @{{}} "
                f"R{{{RenderConfig.TITLE_RIGHT_WIDTH}}} @{{}}}}\n"
                f"\\multicolumn{{3}}{{@{{}}l@{{}}}}"
                f"{{\\makebox[{RenderConfig.TITLE_FULL_WIDTH}][l]{{\\textbf{{{block_a}}}}}}} \\\\\n"
                f"\\textbf{{{block_a_tail}}} & {block_b} & {block_c} \\\\\n"
                "\\end{tabular}\\par\n"
            )

        block_a_text = self.typography.truncate_text_by_width(
            blocks[0],
            LayoutConfig.TITLE_LEFT_WIDTH_MM - LayoutConfig.TITLE_LEFT_WIDTH_SAFETY_MM,
            "bold",
        )
        block_a = self._escape_latex(block_a_text)
        block_b = self._escape_latex(blocks[1])
        block_c = self._escape_latex(blocks[2])

        return (
            "\\noindent"
            f"\\begin{{tabular}}{{@{{}} L{{{RenderConfig.TITLE_LEFT_WIDTH}}} @{{}} "
            f"C{{{RenderConfig.TITLE_MIDDLE_WIDTH}}} @{{}} "
            f"R{{{RenderConfig.TITLE_RIGHT_WIDTH}}} @{{}}}}\n"
            f"\\textbf{{{block_a}}} & {block_b} & {block_c} \\\\\n"
            "\\end{tabular}\\par\n"
        )

    def _render_title_with_icon(self, title):
        """渲染带可选 PNG 图标的标题内容。"""
        safe_title = self._escape_latex(title)

        if not StyleConfig.ENABLE_SECTION_ICONS:
            return safe_title

        if not StyleConfig.SECTION_ICON_ENABLED.get(title, True):
            return safe_title

        icon_path = StyleConfig.SECTION_ICONS.get(title)

        if icon_path and os.path.exists(icon_path):
            safe_icon_path = icon_path.replace("\\", "/")
            return (
                f"\\raisebox{{-0.08cm}}{{\\includegraphics[height={RenderConfig.SECTION_ICON_SIZE}]"
                f"{{{safe_icon_path}}}}}"
                f"\\hspace{{{RenderConfig.SECTION_ICON_TEXT_GAP}}}{safe_title}"
            )

        return safe_title

    def _render_header(self):
        """渲染头部信息，自适应列宽并对齐冒号。"""
        header = self.data["header"]
        
        # 1. 注入图片尺寸参数
        self.tex_code = self.tex_code.replace("[[BASIC_INFO_TITLE]]", self._render_title_with_icon("基本信息"))
        self.tex_code = self.tex_code.replace("[[LOGO_HEIGHT]]", RenderConfig.LOGO_HEIGHT)
        self.tex_code = self.tex_code.replace("[[LOGO_INFO_SEP]]", RenderConfig.LOGO_INFO_SEP)
        self.tex_code = self.tex_code.replace("[[BASIC_INFO_TABLE_GAP]]", RenderConfig.BASIC_INFO_TABLE_GAP)
        self.tex_code = self.tex_code.replace("[[AVATAR_WIDTH]]", RenderConfig.AVATAR_WIDTH)
        self.tex_code = self.tex_code.replace("[[AVATAR_HEIGHT]]", RenderConfig.AVATAR_HEIGHT)
        self.tex_code = self.tex_code.replace("[[HEADER_LEFT_SHORT_MAX]]", RenderConfig.HEADER_LEFT_SHORT_MAX)
        self.tex_code = self.tex_code.replace("[[HEADER_LEFT_MEDIUM_MAX]]", RenderConfig.HEADER_LEFT_MEDIUM_MAX)
        self.tex_code = self.tex_code.replace("[[HEADER_RIGHT_PADDING_SHORT_LEFT]]", RenderConfig.HEADER_RIGHT_PADDING_SHORT_LEFT)
        self.tex_code = self.tex_code.replace("[[HEADER_RIGHT_PADDING_MEDIUM_LEFT]]", RenderConfig.HEADER_RIGHT_PADDING_MEDIUM_LEFT)
        self.tex_code = self.tex_code.replace("[[HEADER_RIGHT_PADDING_LONG_LEFT]]", RenderConfig.HEADER_RIGHT_PADDING_LONG_LEFT)

        # 2. 注入基本必填信息
        self.tex_code = self.tex_code.replace("[[NAME]]", self._escape_latex(header.get("姓名", "")))
        self.tex_code = self.tex_code.replace("[[PHONE]]", self._escape_latex(header.get("联系电话", "")))
        self.tex_code = self.tex_code.replace("[[EMAIL]]", self._escape_latex(header.get("电子邮箱", "")))
        
        self.tex_code = self.tex_code.replace("[[LOGO_PATH]]", header.get("校徽", "").replace("\\", "/"))
        self.tex_code = self.tex_code.replace("[[AVATAR_PATH]]", header.get("证件照", "").replace("\\", "/"))

        # 3. 处理自定义选填项及拉伸对齐逻辑
        required_keys = {"姓名", "联系电话", "电子邮箱", "证件照", "校徽"}
        optional_keys = [key for key in header.keys() if key not in required_keys]
        
        if optional_keys:
            opt_key = optional_keys[0]
            opt_value = header[opt_key]
            self.tex_code = self.tex_code.replace("[[OPTIONAL_KEY]]", self._escape_latex(opt_key))
            self.tex_code = self.tex_code.replace("[[OPTIONAL_VALUE]]", self._escape_latex(opt_value))
            
            # 🎯 核心拉伸对齐逻辑：利用 \hfill 让 LaTeX 底层自动撑满宽度
            safe_key = self._escape_latex(opt_key)
            if len(opt_key) > 2:
                # 注入带有 \hfill 弹簧的 \makebox，实现分散对齐
                name_label = f"\\makebox[\\widthof{{{safe_key}}}][s]{{姓\\hfill 名}}"
            else:
                name_label = "姓名"
                
            self.tex_code = self.tex_code.replace("[[NAME_LABEL]]", name_label)
        else:
            self.tex_code = self.tex_code.replace("[[OPTIONAL_KEY]] & [[OPTIONAL_VALUE]]", " & ")
            self.tex_code = self.tex_code.replace("[[NAME_LABEL]]", "姓名")

    def _render_sections(self):
        """渲染主体经历模块"""
        body_tex = ""
        item_sep = self.spacing["item_sep"]
        
        visible_sections = [
            (section_name, items)
            for section_name, items in self.data["sections"].items()
            if items
        ]

        for index, (section_name, items) in enumerate(visible_sections):
            section_title = self._render_title_with_icon(section_name)
            if index == 0:
                first_top_sep = self.spacing.get("first_module_top_sep", "0mm")
                body_tex += f"\\cvsection[{first_top_sep}]{{{section_title}}}\n\n"
            else:
                body_tex += f"\\cvsection{{{section_title}}}\n\n"
            
            for item in items:
                if isinstance(item, dict):
                    blocks = item["blocks"]
                    body_tex += self._render_subtitle(blocks)
                    
                    if item["details"]:
                        body_tex += f"\\begin{{itemize}}[itemsep={item_sep}, parsep=0pt, topsep=2pt, partopsep=0pt, leftmargin=*]\n"
                        for detail in item["details"]:
                            safe_detail = self._escape_latex(detail)
                            body_tex += f"    \\item {safe_detail}\n"
                        body_tex += "\\end{itemize}\n\n"
                    else:
                        body_tex += "\\vspace{2pt}\n\n"
                        
                elif isinstance(item, str):
                    if body_tex.endswith("\\end{itemize}\n\n"):
                        body_tex = body_tex[:-15]
                        safe_text = self._escape_latex(item)
                        body_tex += f"    \\item {safe_text}\n\\end{{itemize}}\n\n"
                    else:
                        safe_text = self._escape_latex(item)
                        body_tex += f"\\begin{{itemize}}[itemsep={item_sep}, parsep=0pt, topsep=2pt, partopsep=0pt, leftmargin=*]\n"
                        body_tex += f"    \\item {safe_text}\n\\end{{itemize}}\n\n"

        self.tex_code = self.tex_code.replace("[[BODY_CONTENT]]", body_tex)

    def render(self):
        """执行完整渲染并注入全局间距 (严格保持在类层级，缩进为 4 个空格)"""
        self._render_header()
        self._render_sections()
        self.tex_code = self.tex_code.replace("[[TITLE_COLOR]]", StyleConfig.TITLE_COLOR)
        self.tex_code = self.tex_code.replace("[[BODY_COLOR]]", StyleConfig.BODY_COLOR)
        self.tex_code = self.tex_code.replace("[[RULE_COLOR]]", StyleConfig.RULE_COLOR)
        self.tex_code = self.tex_code.replace("[[MARGIN_TOP]]", RenderConfig.MARGIN_TOP)
        self.tex_code = self.tex_code.replace("[[MARGIN_BOTTOM]]", RenderConfig.MARGIN_BOTTOM)
        self.tex_code = self.tex_code.replace("[[MARGIN_LEFT]]", RenderConfig.MARGIN_LEFT)
        self.tex_code = self.tex_code.replace("[[MARGIN_RIGHT]]", RenderConfig.MARGIN_RIGHT)
        self.tex_code = self.tex_code.replace("[[PAGE_TOP_BALANCE_GLUE]]", RenderConfig.PAGE_BALANCE_GLUE)
        self.tex_code = self.tex_code.replace("[[PAGE_BOTTOM_BALANCE_GLUE]]", RenderConfig.PAGE_BALANCE_GLUE)
        self.tex_code = self.tex_code.replace("[[LINE_STRETCH]]", self.spacing["line_stretch"])
        self.tex_code = self.tex_code.replace("[[MODULE_SEP]]", self.spacing["module_sep"])
        self.tex_code = self.tex_code.replace("[[SECTION_BODY_SEP]]", RenderConfig.SECTION_BODY_SEP)
        self.tex_code = self.tex_code.replace("[[HEADER_BODY_SEP]]", self.spacing["header_body_sep"])
        return self.tex_code
