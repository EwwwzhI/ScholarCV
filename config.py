import os
from style_config import StyleConfig


def _latex_length_to_mm(value):
    """把常见 LaTeX 长度字符串转换成毫米。"""
    text = str(value).strip().lower()
    if not text:
        return 0.0

    unit_factors = {
        "mm": 1.0,
        "cm": 10.0,
        "pt": 0.3528,
    }

    for unit, factor in unit_factors.items():
        if text.endswith(unit):
            return float(text[:-len(unit)].strip()) * factor

    return float(text)


def _rendered_icon_height_mm(title):
    """按 render.py 的判断规则估算标题图标实际高度。"""
    if not StyleConfig.ENABLE_SECTION_ICONS:
        return 0.0
    if not StyleConfig.SECTION_ICON_ENABLED.get(title, True):
        return 0.0

    icon_path = StyleConfig.SECTION_ICONS.get(title)
    if not icon_path or not os.path.exists(icon_path):
        return 0.0

    return _latex_length_to_mm(StyleConfig.SECTION_ICON_SIZE)


class LayoutConfig:
    # ==========================================
    # 1. 纸张与边距绝对物理尺寸 (单位: mm)
    # ==========================================
    A4_HEIGHT = 297.0
    A4_WIDTH = 210.0

    # 严格对应 LaTeX 模板中的 \geometry 设置
    MARGIN_TOP = 10.0
    MARGIN_BOTTOM = 6.0
    MARGIN_LEFT = 12.0
    MARGIN_RIGHT = 12.0

    # [核心指标] 绝对可用排版空间
    VALID_HEIGHT = A4_HEIGHT - MARGIN_TOP - MARGIN_BOTTOM
    VALID_WIDTH = A4_WIDTH - MARGIN_LEFT - MARGIN_RIGHT

    # ==========================================
    # 2. 字体度量衡 (基于 11pt 设定)
    # ==========================================
    # 1 pt 约等于 0.3528 mm
    PT_TO_MM = 0.3528
    FONT_SIZE_PT = 11.0
    
    # 中文字符通常是正方形，宽度等于字号大小
    CHAR_WIDTH_MM = FONT_SIZE_PT * PT_TO_MM                # 约 3.88 mm
    
    # 行宽极限：一行最多能容纳的纯中文字符数
    # 180.0 / 3.88 ≈ 46.39，向下取整为 46 个字
    MAX_CHARS_PER_LINE = int(VALID_WIDTH / CHAR_WIDTH_MM)  # 46

    # 默认行距设定 (LaTeX 默认的 \baselineskip 约为 1.2 倍字号)
    LINE_STRETCH = 1.2
    LINE_HEIGHT_MM = CHAR_WIDTH_MM * LINE_STRETCH          # 约 4.66 mm

    # ==========================================
    # 3. 静态结构的高度损耗预估 (单位: mm)
    # ==========================================
    # 头部基本信息区：左侧校徽 + 基本信息，右侧证件照
    # LaTeX minipage 会被更高的一侧撑开，因此按证件照/左侧内容最大值估算
    LOGO_HEIGHT_MM = 14.0
    AVATAR_WIDTH_MM = 30.0
    AVATAR_HEIGHT_MM = 40.0
    LOGO_INFO_SEP_BASE = 0.0

    # 基本信息标题区：标题行高度取文字与图标中的较大值，再加标题后距和分割线
    LARGE_TITLE_TEXT_HEIGHT_MM = 6.0
    TITLE_RULE_HEIGHT_MM = 0.8 * PT_TO_MM
    BASIC_INFO_TITLE_AFTER_SEP_MM = 4.0 * PT_TO_MM
    BASIC_INFO_TITLE_ICON_HEIGHT_MM = _rendered_icon_height_mm("基本信息")
    BASIC_INFO_TITLE_LINE_HEIGHT_MM = max(
        LARGE_TITLE_TEXT_HEIGHT_MM,
        BASIC_INFO_TITLE_ICON_HEIGHT_MM,
    )
    BASIC_INFO_TITLE_HEIGHT_MM = (
        BASIC_INFO_TITLE_LINE_HEIGHT_MM
        + BASIC_INFO_TITLE_AFTER_SEP_MM
        + TITLE_RULE_HEIGHT_MM
    )
    BASIC_INFO_TABLE_GAP_MM = 0.6
    BASIC_INFO_TABLE_ROWS = 2
    BASIC_INFO_TABLE_ARRAY_STRETCH = 1.5
    BASIC_INFO_TABLE_ROW_HEIGHT_MM = LINE_HEIGHT_MM * BASIC_INFO_TABLE_ARRAY_STRETCH
    BASIC_INFO_TABLE_HEIGHT_MM = BASIC_INFO_TABLE_ROWS * BASIC_INFO_TABLE_ROW_HEIGHT_MM

    @classmethod
    def basic_info_table_height_mm(cls, line_stretch=None):
        """估算基本信息表格高度，对应 LaTeX 的 arraystretch=1.5 和两行内容。"""
        if line_stretch is None:
            line_stretch = cls.LINE_STRETCH
        row_height = cls.CHAR_WIDTH_MM * line_stretch * cls.BASIC_INFO_TABLE_ARRAY_STRETCH
        return cls.BASIC_INFO_TABLE_ROWS * row_height

    @classmethod
    def header_left_height_mm(cls, line_stretch=None):
        """按实际头部结构估算左侧高度：校徽 + 标题/图标 + 横线 + 表格。"""
        return (
            cls.LOGO_HEIGHT_MM
            + cls.LOGO_INFO_SEP_BASE
            + cls.BASIC_INFO_TITLE_HEIGHT_MM
            + cls.BASIC_INFO_TABLE_GAP_MM
            + cls.basic_info_table_height_mm(line_stretch)
        )

    @classmethod
    def header_height_mm(cls, line_stretch=None):
        """头部整体高度取左侧内容和右侧证件照中的较大值。"""
        return max(cls.header_left_height_mm(line_stretch), cls.AVATAR_HEIGHT_MM)

    HEADER_LEFT_HEIGHT = (
        LOGO_HEIGHT_MM
        + LOGO_INFO_SEP_BASE
        + BASIC_INFO_TITLE_HEIGHT_MM
        + BASIC_INFO_TABLE_GAP_MM
        + BASIC_INFO_TABLE_HEIGHT_MM
    )
    HEADER_HEIGHT = max(HEADER_LEFT_HEIGHT, AVATAR_HEIGHT_MM)
    HEADER_BODY_SEP_BASE = 1.2
    HEADER_LEFT_SHORT_MAX_MM = 45.0
    HEADER_LEFT_MEDIUM_MAX_MM = 65.0
    HEADER_RIGHT_PADDING_SHORT_LEFT_MM = 20.0
    HEADER_RIGHT_PADDING_MEDIUM_LEFT_MM = 12.0
    HEADER_RIGHT_PADDING_LONG_LEFT_MM = 2.0

    # 一级大模块标题高度：标题行取文字与图标中的较大值，再加 2pt 后距和分割线
    SECTION_TITLE_AFTER_SEP_MM = 2.0 * PT_TO_MM
    SECTION_TITLE_ICON_HEIGHT_MM = (
        _latex_length_to_mm(StyleConfig.SECTION_ICON_SIZE)
        if StyleConfig.ENABLE_SECTION_ICONS
        else 0.0
    )
    SECTION_TITLE_LINE_HEIGHT_MM = max(
        LARGE_TITLE_TEXT_HEIGHT_MM,
        SECTION_TITLE_ICON_HEIGHT_MM,
    )
    SECTION_TITLE_HEIGHT = (
        SECTION_TITLE_LINE_HEIGHT_MM
        + SECTION_TITLE_AFTER_SEP_MM
        + TITLE_RULE_HEIGHT_MM
    )
    SECTION_BODY_SEP = 2.0

    @classmethod
    def section_title_height_mm(cls, section_name):
        """按具体模块是否真的渲染图标，估算该模块标题高度。"""
        title_line_height = max(
            cls.LARGE_TITLE_TEXT_HEIGHT_MM,
            _rendered_icon_height_mm(section_name),
        )
        return title_line_height + cls.SECTION_TITLE_AFTER_SEP_MM + cls.TITLE_RULE_HEIGHT_MM

    FIRST_MODULE_TOP_SEP_BASE = 0.0
    TITLE_LEFT_WIDTH_MM = 96.0
    TITLE_RIGHT_WIDTH_MM = 32.0
    TITLE_MIDDLE_WIDTH_MM = VALID_WIDTH - TITLE_LEFT_WIDTH_MM - TITLE_RIGHT_WIDTH_MM
    TITLE_LEFT_MAX_EQUIV_CHARS = 24

    # 三级子项目标题高度 (如：### 杭州电子科技大学...)
    # 包含粗体字高度和少量下方留白
    SUBTITLE_HEIGHT = 6.0

    # ==========================================
    # 4. 动态间距调节阀 (用于 LaTeX \vspace 注入)
    # ==========================================
    # 这是脚本在发现“页长不足”或“页长溢出”时，用来做加减法的基准值
    # 模块与模块之间的初始大间距
    MODULE_SEP_BASE = 4.0   
    # 列表项 (-) 之间的初始小间距
    ITEM_SEP_BASE = 1.5
    ITEMIZE_INDENT_MM = 7.0
    ITEMIZE_TOPSEP_MM = 2.0 * PT_TO_MM
    LAYOUT_SAFETY_RATIO = 0.985
