class LayoutConfig:
    # ==========================================
    # 1. 纸张与边距绝对物理尺寸 (单位: mm)
    # ==========================================
    A4_HEIGHT = 297.0
    A4_WIDTH = 210.0

    # 严格对应 LaTeX 模板中的 \geometry 设置
    MARGIN_TOP = 6.0
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
    LOGO_HEIGHT_MM = 18.0
    AVATAR_WIDTH_MM = 36.0
    AVATAR_HEIGHT_MM = 48.0
    LOGO_INFO_SEP_BASE = 0.0
    BASIC_INFO_TITLE_HEIGHT_MM = 6.0
    BASIC_INFO_TABLE_GAP_MM = 0.6
    BASIC_INFO_TABLE_HEIGHT_MM = 15.0
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

    # 一级大模块标题高度 (如：\section*{教育背景})
    # 只包含标题字体、标题到横线的 2pt 和横线本身，不包含上下模块间距
    SECTION_TITLE_HEIGHT = 6.0 
    SECTION_BODY_SEP = 2.0
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
