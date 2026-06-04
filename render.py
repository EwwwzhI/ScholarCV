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
    HYBRID_LOGO_WIDTH = f"{LayoutConfig.HYBRID_LOGO_WIDTH_MM:g}mm"
    HYBRID_LOGO_HEIGHT = f"{LayoutConfig.HYBRID_LOGO_HEIGHT_MM / 10:g}cm"
    HYBRID_HEADER_CONTENT_WIDTH = f"{LayoutConfig.HYBRID_HEADER_CONTENT_WIDTH_MM:g}mm"
    HYBRID_HEADER_RIGHT_WIDTH = f"{LayoutConfig.HYBRID_HEADER_RIGHT_WIDTH_MM:g}mm"
    HYBRID_HEADER_BOX_HEIGHT = f"{LayoutConfig.HYBRID_HEADER_BOX_HEIGHT_MM / 10:g}cm"
    
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
    TITLE_FOUR_FIRST_WIDTH = f"{LayoutConfig.TITLE_FOUR_FIRST_WIDTH_MM:g}mm"
    TITLE_FOUR_SECOND_WIDTH = f"{LayoutConfig.TITLE_FOUR_SECOND_WIDTH_MM:g}mm"
    TITLE_FULL_WIDTH = f"{LayoutConfig.VALID_WIDTH:g}mm"
    PROJECT_SEP = f"{LayoutConfig.PROJECT_SEP_BASE:g}mm"
    PROJECT_SEPARATOR_AFTER_SEP = f"{LayoutConfig.PROJECT_SEPARATOR_AFTER_SEP_MM:g}mm"
    PROJECT_SEPARATOR_DASH_WIDTH = f"{LayoutConfig.PROJECT_SEPARATOR_DASH_WIDTH_MM:g}mm"
    PROJECT_SEPARATOR_DASH_GAP = f"{LayoutConfig.PROJECT_SEPARATOR_DASH_GAP_MM:g}mm"
    PROJECT_SEPARATOR_THICKNESS = f"{LayoutConfig.PROJECT_SEPARATOR_THICKNESS_PT:g}pt"
    PROJECT_SEPARATOR_NONE = f"{LayoutConfig.PROJECT_SEPARATOR_NONE_MM:g}mm"
    PROJECT_SEPARATOR_SPACE = f"{LayoutConfig.PROJECT_SEPARATOR_SPACE_MM:g}mm"
    ITEMIZE_LEFT_MARGIN = f"{LayoutConfig.ITEMIZE_INDENT_MM:g}mm"
    ITEMIZE_TOPSEP = f"{LayoutConfig.ITEMIZE_TOPSEP_MM:g}mm"
    CENTERED_HEADER_TOP_SEP = f"{LayoutConfig.CENTERED_HEADER_TOP_SEP_MM:g}mm"
    SECTION_ICON_SIZE = StyleConfig.SECTION_ICON_SIZE
    SECTION_ICON_TEXT_GAP = StyleConfig.SECTION_ICON_TEXT_GAP
    CENTERED_HEADER_ICON_SIZE = getattr(
        StyleConfig,
        "CENTERED_HEADER_ICON_SIZE",
        "0.28cm",
    )
    CENTERED_HEADER_ICON_TEXT_GAP = getattr(
        StyleConfig,
        "CENTERED_HEADER_ICON_TEXT_GAP",
        "0.06cm",
    )
    CENTERED_HEADER_ICON_RAISE = getattr(
        StyleConfig,
        "CENTERED_HEADER_ICON_RAISE",
        "-0.035cm",
    )
    PAGE_TOP_BALANCE_GLUE = (
        rf"\vspace*{{\stretch{{{LayoutConfig.BALANCE_VERTICAL_TOP_WEIGHT:g}}}}}"
        if getattr(LayoutConfig, "BALANCE_VERTICAL_WHITESPACE", False)
        else ""
    )
    PAGE_BOTTOM_BALANCE_GLUE = (
        rf"\vspace*{{\stretch{{{LayoutConfig.BALANCE_VERTICAL_BOTTOM_WEIGHT:g}}}}}"
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
[[CENTERED_HEADER_ICON_PACKAGE]]
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
% 动态头部信息区
% ==========================================
[[HEADER_CONTENT]]

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
        self.needs_centered_header_icon_package = False

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
        """判断三级标题第一段是否超出固定左列安全宽度。"""
        return (
            self.typography.measure_text_mm(text, "bold")
            > LayoutConfig.TITLE_LEFT_WIDTH_MM - LayoutConfig.TITLE_LEFT_WIDTH_SAFETY_MM
        )

    def _can_render_subtitle_inline(self, blocks):
        """判断超过左列阈值的标题是否会碰到居中的第二段。"""
        title_width = self.typography.measure_text_mm(blocks[0], "bold")
        middle_width = self.typography.measure_text_mm(blocks[1], "normal")
        middle_left_slack = max(
            0.0,
            (LayoutConfig.TITLE_MIDDLE_WIDTH_MM - middle_width) / 2,
        )
        inline_limit = (
            LayoutConfig.TITLE_LEFT_WIDTH_MM
            + middle_left_slack
            - LayoutConfig.TITLE_CENTER_COLLISION_GAP_MM
        )
        return title_width <= inline_limit

    def _render_single_block_subtitle(self, blocks):
        """渲染单段三级标题，整行加粗并自然换行。"""
        block_a = self._escape_latex(blocks[0])

        return (
            "\\noindent"
            f"\\begin{{tabular}}{{@{{}} L{{{RenderConfig.TITLE_FULL_WIDTH}}} @{{}}}}\n"
            f"\\textbf{{{block_a}}} \\\\\n"
            "\\end{tabular}\\par\n"
        )

    def _render_three_block_subtitle(self, blocks):
        """渲染三段三级标题；边界长标题同排，真正长标题仍独占首行。"""
        if self._should_wrap_subtitle_first_block(blocks[0]):
            if self._can_render_subtitle_inline(blocks):
                block_a = self._escape_latex(blocks[0])
                block_b = self._escape_latex(blocks[1])
                block_c = self._escape_latex(blocks[2])

                return (
                    "\\noindent"
                    f"\\begin{{tabular}}{{@{{}} L{{{RenderConfig.TITLE_LEFT_WIDTH}}} @{{}} "
                    f"C{{{RenderConfig.TITLE_MIDDLE_WIDTH}}} @{{}} "
                    f"R{{{RenderConfig.TITLE_RIGHT_WIDTH}}} @{{}}}}\n"
                    f"\\makebox[{RenderConfig.TITLE_LEFT_WIDTH}][l]{{\\textbf{{{block_a}}}}} & {block_b} & {block_c} \\\\\n"
                    "\\end{tabular}\\par\n"
                )

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

    def _render_four_block_subtitle(self, blocks):
        """渲染四段三级标题：拆分原左列，保留原中列和右列。"""
        block_a = self._escape_latex(blocks[0])
        block_b = self._escape_latex(blocks[1])
        block_c = self._escape_latex(blocks[2])
        block_d = self._escape_latex(blocks[3])

        return (
            "\\noindent"
            f"\\begin{{tabular}}{{@{{}} L{{{RenderConfig.TITLE_FOUR_FIRST_WIDTH}}} @{{}} "
            f"C{{{RenderConfig.TITLE_FOUR_SECOND_WIDTH}}} @{{}} "
            f"C{{{RenderConfig.TITLE_MIDDLE_WIDTH}}} @{{}} "
            f"R{{{RenderConfig.TITLE_RIGHT_WIDTH}}} @{{}}}}\n"
            f"\\textbf{{{block_a}}} & {block_b} & {block_c} & {block_d} \\\\\n"
            "\\end{tabular}\\par\n"
        )

    def _render_subtitle(self, blocks):
        """按三级标题段数分发渲染。"""
        if len(blocks) == 1:
            return self._render_single_block_subtitle(blocks)
        if len(blocks) == 3:
            return self._render_three_block_subtitle(blocks)
        if len(blocks) == 4:
            return self._render_four_block_subtitle(blocks)

        raise ValueError("三级标题仅支持 1 段、3 段或 4 段。")

    def _render_project_separator(self):
        """渲染同一模块内多个三级标题项目之间的虚线分隔。"""
        project_sep_before = self.spacing.get("project_sep", RenderConfig.PROJECT_SEP)
        project_sep_after = RenderConfig.PROJECT_SEPARATOR_AFTER_SEP
        before_vspace = (
            f"\\vspace{{{project_sep_before}}}\n"
            if project_sep_before != "0mm"
            else ""
        )
        after_vspace = (
            f"\\vspace{{{project_sep_after}}}\n"
            if project_sep_after != "0mm"
            else ""
        )
        return (
            before_vspace
            +
            "\\noindent\\raisebox{0pt}[0pt][0pt]{\\hbox to \\linewidth{\\color{cvRule}"
            "\\xleaders\\hbox{"
            f"\\rule{{{RenderConfig.PROJECT_SEPARATOR_DASH_WIDTH}}}"
            f"{{{RenderConfig.PROJECT_SEPARATOR_THICKNESS}}}"
            f"\\hskip{RenderConfig.PROJECT_SEPARATOR_DASH_GAP}"
            "}\\hfill\\kern0pt}}\\par\n"
            f"{after_vspace}"
        )

    def _render_project_gap(self, mode):
        """按三级标题前置指令渲染项目之间的间隔。"""
        if mode == "none":
            return f"\\vspace{{{RenderConfig.PROJECT_SEPARATOR_NONE}}}\n"
        if mode == "dashed":
            return self._render_project_separator()
        if mode == "space":
            return f"\\vspace{{{RenderConfig.PROJECT_SEPARATOR_SPACE}}}\n"
        raise ValueError(f"未知项目间隔模式：{mode}")

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

    def _style_lookup(self, attr_name, key, fallback_key=None, default=None):
        """按实际字段名优先、兼容字段名兜底读取样式配置。"""
        mapping = getattr(StyleConfig, attr_name, {})
        if key in mapping:
            return mapping[key]
        if fallback_key is not None and fallback_key in mapping:
            return mapping[fallback_key]
        return default

    def _centered_header_icon_enabled(self, key, fallback_key=None):
        """判断 centered 头部联系方式字段是否显示图标。"""
        if not getattr(StyleConfig, "ENABLE_CENTERED_HEADER_ICONS", False):
            return False

        return bool(
            self._style_lookup(
                "CENTERED_HEADER_ICON_ENABLED",
                key,
                fallback_key,
                True,
            )
        )

    def _render_centered_header_icon(self, key, fallback_key=None):
        """渲染 centered 头部联系方式字段前的图标。"""
        if not self._centered_header_icon_enabled(key, fallback_key):
            return ""

        icon_path = self._style_lookup(
            "CENTERED_HEADER_ICONS",
            key,
            fallback_key,
            "",
        )
        if icon_path and os.path.exists(icon_path):
            safe_icon_path = icon_path.replace("\\", "/")
            icon_body = (
                f"\\includegraphics[height={RenderConfig.CENTERED_HEADER_ICON_SIZE}]"
                f"{{{safe_icon_path}}}"
            )
        else:
            icon_body = self._style_lookup(
                "CENTERED_HEADER_ICON_COMMANDS",
                key,
                fallback_key,
                "",
            )
            if not icon_body:
                return ""
            self.needs_centered_header_icon_package = True
            icon_body = (
                f"\\resizebox{{!}}{{{RenderConfig.CENTERED_HEADER_ICON_SIZE}}}"
                f"{{{icon_body}}}"
            )

        return (
            f"\\raisebox{{{RenderConfig.CENTERED_HEADER_ICON_RAISE}}}"
            f"{{{icon_body}}}"
            f"\\hspace{{{RenderConfig.CENTERED_HEADER_ICON_TEXT_GAP}}}"
        )

    def _header_template(self):
        """返回当前头部模板 ID。"""
        return self.data["header"].get("头部模板", "classic")

    def _render_classic_header(self):
        """渲染现有图文头部信息，自适应列宽并对齐冒号。"""
        header = self.data["header"]
        header_tex = r"""
\noindent
\begin{minipage}[b]{0.74\textwidth}
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
    \includegraphics[width=[[AVATAR_WIDTH]], height=[[AVATAR_HEIGHT]]]{[[AVATAR_PATH]]}
\end{minipage}
"""

        replacements = {
            "[[BASIC_INFO_TITLE]]": self._render_title_with_icon("基本信息"),
            "[[LOGO_HEIGHT]]": RenderConfig.LOGO_HEIGHT,
            "[[LOGO_INFO_SEP]]": RenderConfig.LOGO_INFO_SEP,
            "[[BASIC_INFO_TABLE_GAP]]": RenderConfig.BASIC_INFO_TABLE_GAP,
            "[[AVATAR_WIDTH]]": RenderConfig.AVATAR_WIDTH,
            "[[AVATAR_HEIGHT]]": RenderConfig.AVATAR_HEIGHT,
            "[[HEADER_LEFT_SHORT_MAX]]": RenderConfig.HEADER_LEFT_SHORT_MAX,
            "[[HEADER_LEFT_MEDIUM_MAX]]": RenderConfig.HEADER_LEFT_MEDIUM_MAX,
            "[[HEADER_RIGHT_PADDING_SHORT_LEFT]]": RenderConfig.HEADER_RIGHT_PADDING_SHORT_LEFT,
            "[[HEADER_RIGHT_PADDING_MEDIUM_LEFT]]": RenderConfig.HEADER_RIGHT_PADDING_MEDIUM_LEFT,
            "[[HEADER_RIGHT_PADDING_LONG_LEFT]]": RenderConfig.HEADER_RIGHT_PADDING_LONG_LEFT,
            "[[NAME]]": self._escape_latex(header.get("姓名", "")),
            "[[PHONE]]": self._escape_latex(header.get("联系电话", "")),
            "[[EMAIL]]": self._escape_latex(header.get("电子邮箱", "")),
            "[[LOGO_PATH]]": header.get("校徽", "").replace("\\", "/"),
            "[[AVATAR_PATH]]": header.get("证件照", "").replace("\\", "/"),
        }
        for placeholder, value in replacements.items():
            header_tex = header_tex.replace(placeholder, value)

        required_keys = {"姓名", "联系电话", "电子邮箱", "证件照", "校徽", "头部模板"}
        optional_keys = [key for key in header.keys() if key not in required_keys]

        if optional_keys:
            opt_key = optional_keys[0]
            opt_value = header[opt_key]
            header_tex = header_tex.replace("[[OPTIONAL_KEY]]", self._escape_latex(opt_key))
            header_tex = header_tex.replace("[[OPTIONAL_VALUE]]", self._escape_latex(opt_value))

            safe_key = self._escape_latex(opt_key)
            if len(opt_key) > 2:
                name_label = f"\\makebox[\\widthof{{{safe_key}}}][s]{{姓\\hfill 名}}"
            else:
                name_label = "姓名"

            header_tex = header_tex.replace("[[NAME_LABEL]]", name_label)
        else:
            header_tex = header_tex.replace("[[OPTIONAL_KEY]] & [[OPTIONAL_VALUE]]", " & ")
            header_tex = header_tex.replace("[[NAME_LABEL]]", "姓名")

        return header_tex

    def _centered_contact_parts(self):
        """按 Markdown 头部字段顺序返回 centered 头部允许展示的联系方式字段。"""
        header = self.data["header"]
        contact_field_fallbacks = {
            "电子邮箱": "电子邮箱",
            "联系电话": "联系电话",
            "个人主页": "个人主页",
            "GitHub": "GitHub",
            "GitHub主页": "GitHub",
        }
        parts = []
        rendered_fallbacks = set()
        for key, value in header.items():
            fallback_key = contact_field_fallbacks.get(key)
            if not fallback_key or fallback_key in rendered_fallbacks:
                continue

            icon = self._render_centered_header_icon(key, fallback_key)
            parts.append(icon + self._escape_latex(value))
            rendered_fallbacks.add(fallback_key)

            if len(parts) >= 4:
                break

        return parts

    def _hybrid_info_items(self):
        """按 YAML 头部字段顺序返回 hybrid 中央信息区字段。"""
        header = self.data["header"]
        excluded_keys = {"头部模板", "姓名", "证件照", "校徽"}
        label_aliases = {
            "联系电话": "手机",
            "电子邮箱": "邮箱",
        }
        max_items = getattr(LayoutConfig, "HYBRID_HEADER_MAX_INFO_ITEMS", 4)

        items = []
        for key, value in header.items():
            if key in excluded_keys:
                continue
            items.append((label_aliases.get(key, key), value))
            if len(items) >= max_items:
                break

        return items

    def _render_hybrid_info_lines(self):
        """渲染 hybrid 中央信息区，最多两行、每行最多两项。"""
        items = self._hybrid_info_items()
        lines = []
        separator = r"\hspace{1.5mm}$\cdot$\hspace{1.5mm}"

        for index in range(0, len(items), 2):
            line_items = items[index:index + 2]
            parts = []
            for label, value in line_items:
                safe_label = self._escape_latex(label)
                safe_value = self._escape_latex(value)
                parts.append(f"\\textbf{{{safe_label}：}}{safe_value}")
            lines.append(f"{{\\normalsize {separator.join(parts)}}}")

        return "\\\\[1mm]\n".join(lines)

    def _render_centered_header(self):
        """渲染纯文字居中头部。"""
        name = self._escape_latex(self.data["header"].get("姓名", ""))
        contact_parts = self._centered_contact_parts()
        contact_line = (
            r"\hspace{1.6mm}$\cdot$\hspace{1.6mm}".join(contact_parts)
            if contact_parts
            else ""
        )
        top_sep = (
            f"\\vspace*{{{RenderConfig.CENTERED_HEADER_TOP_SEP}}}\n"
            if RenderConfig.CENTERED_HEADER_TOP_SEP != "0mm"
            else ""
        )
        return (
            top_sep
            +
            "\\begin{center}\n"
            f"{{\\fontsize{{20pt}}{{24pt}}\\selectfont\\textcolor{{cvTitle}}{{\\textbf{{{name}}}}}}}\\\\[2mm]\n"
            f"{{\\normalsize {contact_line}}}\n"
            "\\end{center}"
        )

    def _render_hybrid_header(self):
        """渲染整行居中信息、左右浮动图片的混合头部。"""
        header = self.data["header"]
        name = self._escape_latex(header.get("姓名", ""))
        info_lines = self._render_hybrid_info_lines()
        info_block = f"\\\\[2mm]\n{info_lines}" if info_lines else ""

        logo_path = header.get("校徽", "").replace("\\", "/")
        avatar_path = header.get("证件照", "").replace("\\", "/")
        logo_overlay = (
            "\\makebox[0pt][l]{"
            "\\raisebox{-\\height}[0pt][0pt]{"
            "\\includegraphics"
            f"[width={RenderConfig.HYBRID_LOGO_WIDTH},height={RenderConfig.HYBRID_HEADER_BOX_HEIGHT},keepaspectratio]"
            f"{{{logo_path}}}"
            "}"
            "}"
            if logo_path
            else ""
        )
        avatar_overlay = (
            "\\makebox[0pt][l]{"
            "\\makebox[\\linewidth][r]{"
            "\\raisebox{-\\height}[0pt][0pt]{"
            "\\includegraphics"
            f"[width={RenderConfig.HYBRID_HEADER_RIGHT_WIDTH},height={RenderConfig.HYBRID_HEADER_BOX_HEIGHT},keepaspectratio]"
            f"{{{avatar_path}}}"
            "}"
            "}"
            "}"
        )

        header_tex = r"""
\noindent
\begin{minipage}[t][[[HYBRID_HEADER_BOX_HEIGHT]]][t]{[[HYBRID_HEADER_CONTENT_WIDTH]]}
    \vspace{0pt}%
    \noindent
    [[LOGO_OVERLAY]]
    [[AVATAR_OVERLAY]]
    \makebox[0pt][l]{\raisebox{0pt}[0pt][0pt]{%
        \begin{minipage}[t][[[HYBRID_HEADER_BOX_HEIGHT]]][c]{\linewidth}
            \centering
            {\fontsize{20pt}{24pt}\selectfont\textcolor{cvTitle}{\textbf{[[NAME]]}}}[[INFO_BLOCK]]\par
        \end{minipage}
    }}
\end{minipage}
"""

        replacements = {
            "[[HYBRID_HEADER_CONTENT_WIDTH]]": RenderConfig.HYBRID_HEADER_CONTENT_WIDTH,
            "[[HYBRID_HEADER_BOX_HEIGHT]]": RenderConfig.HYBRID_HEADER_BOX_HEIGHT,
            "[[LOGO_OVERLAY]]": logo_overlay,
            "[[AVATAR_OVERLAY]]": avatar_overlay,
            "[[NAME]]": name,
            "[[INFO_BLOCK]]": info_block,
        }
        for placeholder, value in replacements.items():
            header_tex = header_tex.replace(placeholder, value)

        return header_tex

    def _render_header(self):
        """按配置模板渲染头部。"""
        template = self._header_template()
        if template == "classic":
            header_tex = self._render_classic_header()
        elif template == "centered":
            header_tex = self._render_centered_header()
        elif template == "hybrid":
            header_tex = self._render_hybrid_header()
        else:
            raise ValueError(f"未知头部模板：{template}")

        self.tex_code = self.tex_code.replace("[[HEADER_CONTENT]]", header_tex)

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
            subtitle_count = 0
            for item in items:
                if isinstance(item, dict):
                    if subtitle_count > 0:
                        body_tex += self._render_project_gap(
                            item.get("project_sep_mode", "none")
                        )

                    blocks = item["blocks"]
                    body_tex += self._render_subtitle(blocks)
                    subtitle_count += 1
                    
                    if item["details"]:
                        body_tex += f"\\vspace{{{item_sep}}}\n"
                        body_tex += f"\\begin{{itemize}}[itemsep={item_sep}, parsep=0pt, topsep={RenderConfig.ITEMIZE_TOPSEP}, partopsep=0pt, leftmargin={RenderConfig.ITEMIZE_LEFT_MARGIN}]\n"
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
                        body_tex += f"\\vspace{{{item_sep}}}\n"
                        body_tex += f"\\begin{{itemize}}[itemsep={item_sep}, parsep=0pt, topsep={RenderConfig.ITEMIZE_TOPSEP}, partopsep=0pt, leftmargin={RenderConfig.ITEMIZE_LEFT_MARGIN}]\n"
                        body_tex += f"    \\item {safe_text}\n\\end{{itemize}}\n\n"

        self.tex_code = self.tex_code.replace("[[BODY_CONTENT]]", body_tex)

    def render(self):
        """执行完整渲染并注入全局间距 (严格保持在类层级，缩进为 4 个空格)"""
        self._render_header()
        self._render_sections()
        self.tex_code = self.tex_code.replace("[[TITLE_COLOR]]", StyleConfig.TITLE_COLOR)
        self.tex_code = self.tex_code.replace("[[BODY_COLOR]]", StyleConfig.BODY_COLOR)
        self.tex_code = self.tex_code.replace("[[RULE_COLOR]]", StyleConfig.RULE_COLOR)
        icon_package = (
            getattr(
                StyleConfig,
                "CENTERED_HEADER_ICON_PACKAGE",
                r"\usepackage{fontawesome5}",
            )
            if self.needs_centered_header_icon_package
            else ""
        )
        self.tex_code = self.tex_code.replace(
            "[[CENTERED_HEADER_ICON_PACKAGE]]",
            icon_package,
        )
        self.tex_code = self.tex_code.replace("[[MARGIN_TOP]]", RenderConfig.MARGIN_TOP)
        self.tex_code = self.tex_code.replace("[[MARGIN_BOTTOM]]", RenderConfig.MARGIN_BOTTOM)
        self.tex_code = self.tex_code.replace("[[MARGIN_LEFT]]", RenderConfig.MARGIN_LEFT)
        self.tex_code = self.tex_code.replace("[[MARGIN_RIGHT]]", RenderConfig.MARGIN_RIGHT)
        self.tex_code = self.tex_code.replace("[[PAGE_TOP_BALANCE_GLUE]]", RenderConfig.PAGE_TOP_BALANCE_GLUE)
        self.tex_code = self.tex_code.replace("[[PAGE_BOTTOM_BALANCE_GLUE]]", RenderConfig.PAGE_BOTTOM_BALANCE_GLUE)
        self.tex_code = self.tex_code.replace("[[LINE_STRETCH]]", self.spacing["line_stretch"])
        self.tex_code = self.tex_code.replace("[[MODULE_SEP]]", self.spacing["module_sep"])
        self.tex_code = self.tex_code.replace("[[SECTION_BODY_SEP]]", RenderConfig.SECTION_BODY_SEP)
        self.tex_code = self.tex_code.replace("[[HEADER_BODY_SEP]]", self.spacing["header_body_sep"])
        return self.tex_code
