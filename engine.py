import unicodedata
import math
from config import LayoutConfig

# ==========================================
# 算法 1：中英文精准计重与行数推演
# ==========================================
def get_equivalent_char_count(text):
    """
    计算字符串的“等效中文字符数”。
    全角字符（汉字、中文标点）权重为 1.0
    半角字符（英文、数字、半角标点、空格）权重为 0.5
    """
    weight = 0.0
    for char in text:
        # 获取字符的东亚宽度属性
        # 'W' (Wide) / 'F' (Fullwidth) -> 宽字符
        # 'A' (Ambiguous) -> 视作宽字符以防万一
        width_type = unicodedata.east_asian_width(char)
        if width_type in ('W', 'F', 'A'):
            weight += 1.0
        else:
            weight += 0.5
    return weight

def calculate_text_lines(text, max_chars=LayoutConfig.MAX_CHARS_PER_LINE):
    """
    推演一段文本在特定行宽下需要占据的绝对行数
    """
    equiv_count = get_equivalent_char_count(text)
    # 哪怕只超了 0.1 个字，物理上也会变成两行，所以必须向上取整
    return math.ceil(equiv_count / max_chars)

def calculate_max_chars_for_width(width_mm, config=LayoutConfig):
    """根据实际可用物理宽度推算单行可容纳的等效中文字符数。"""
    return max(1, int(width_mm / config.CHAR_WIDTH_MM))

def format_mm(value):
    """把数值毫米转换为 LaTeX 可直接使用的尺寸字符串。"""
    return f"{value:g}mm"

# ==========================================
# 算法 2：模块绝对高度估算器
# ==========================================
def estimate_block_height(
    section_name,
    items,
    config=LayoutConfig,
    top_sep=None,
    module_sep=None,
    item_sep=None,
    line_stretch=None,
):
    """
    估算一个完整大模块（如“科研经历”）的总高度 (单位: mm)
    items: 从 parser 解析出来的列表，包含多个深度或扁平字典
    """
    if module_sep is None:
        module_sep = config.MODULE_SEP_BASE
    if item_sep is None:
        item_sep = config.ITEM_SEP_BASE
    if line_stretch is None:
        line_stretch = config.LINE_STRETCH
    if top_sep is None:
        top_sep = module_sep

    # 初始高度 = 模块上边距 + 大标题本身高度 + 标题到首个项目的固定下边距
    section_title_height = (
        config.section_title_height_mm(section_name)
        if hasattr(config, "section_title_height_mm")
        else config.SECTION_TITLE_HEIGHT
    )
    total_height = top_sep + section_title_height + config.SECTION_BODY_SEP
    line_height = config.CHAR_WIDTH_MM * line_stretch
    item_max_chars = calculate_max_chars_for_width(
        config.VALID_WIDTH - config.ITEMIZE_INDENT_MM,
        config
    )
    
    for item in items:
        # 如果是深度结构（带 ### 的三段式字典）
        if isinstance(item, dict):
            # 1. 加上三级子标题的高度
            total_height += config.SUBTITLE_HEIGHT
            
            # 2. 累加下属正文列表 (- xxx) 的高度
            if item["details"]:
                total_height += config.ITEMIZE_TOPSEP_MM * 2
                for index, detail_text in enumerate(item["details"]):
                    lines = calculate_text_lines(detail_text, item_max_chars)
                    # 文本高度 = 行数 * 当前 profile 单行高度
                    total_height += (lines * line_height)
                    # itemsep 只出现在列表项之间
                    if index < len(item["details"]) - 1:
                        total_height += item_sep
            else:
                total_height += 2.0 * config.PT_TO_MM
                
            # 加上子项目之间的大间距
            total_height += module_sep
            
        # 如果是扁平结构（只有字符串，如“综合素质”）
        elif isinstance(item, str):
            lines = calculate_text_lines(item, item_max_chars)
            total_height += config.ITEMIZE_TOPSEP_MM * 2
            total_height += (lines * line_height)

    # 减去最后多加的一个多余间距，追求绝对精准
    return total_height - module_sep

def estimate_resume_total_height(parsed_data, config=LayoutConfig, profile=None):
    """
    给整份简历“称重”，返回总物理高度
    """
    if profile is None:
        profile = {
            "module_sep": config.MODULE_SEP_BASE,
            "item_sep": config.ITEM_SEP_BASE,
            "line_stretch": config.LINE_STRETCH,
            "header_body_sep": config.HEADER_BODY_SEP_BASE,
            "first_module_top_sep": config.FIRST_MODULE_TOP_SEP_BASE,
        }

    # 头部区域按实际模板尺寸估算，再接一个很小的正文起始间距
    header_height = (
        config.header_height_mm(profile["line_stretch"])
        if hasattr(config, "header_height_mm")
        else config.HEADER_HEIGHT
    )
    total_mm = header_height + profile["header_body_sep"]
    
    visible_sections = [
        (section_name, items)
        for section_name, items in parsed_data["sections"].items()
        if items
    ]

    for index, (section_name, items) in enumerate(visible_sections):
        top_sep = (
            profile["first_module_top_sep"]
            if index == 0
            else profile["module_sep"]
        )
        block_height = estimate_block_height(
            section_name,
            items,
            config,
            top_sep=top_sep,
            module_sep=profile["module_sep"],
            item_sep=profile["item_sep"],
            line_stretch=profile["line_stretch"],
        )
        total_mm += block_height
        
    return total_mm

def get_layout_profiles(config=LayoutConfig):
    """按视觉优先级定义布局方案，估算和渲染共享同一组数值。"""
    return [
        {
            "name": "airy",
            "label": "舒展排版",
            "module_sep": config.MODULE_SEP_BASE * 1.25,
            "item_sep": config.ITEM_SEP_BASE * 1.35,
            "line_stretch": 1.26,
            "header_body_sep": config.HEADER_BODY_SEP_BASE + 0.5,
            "first_module_top_sep": config.FIRST_MODULE_TOP_SEP_BASE,
        },
        {
            "name": "full",
            "label": "饱满排版",
            "module_sep": config.MODULE_SEP_BASE * 1.1,
            "item_sep": config.ITEM_SEP_BASE * 1.15,
            "line_stretch": 1.22,
            "header_body_sep": config.HEADER_BODY_SEP_BASE + 0.2,
            "first_module_top_sep": config.FIRST_MODULE_TOP_SEP_BASE,
        },
        {
            "name": "relaxed",
            "label": "宽松排版",
            "module_sep": config.MODULE_SEP_BASE * 1.05,
            "item_sep": config.ITEM_SEP_BASE * 1.05,
            "line_stretch": 1.21,
            "header_body_sep": config.HEADER_BODY_SEP_BASE + 0.1,
            "first_module_top_sep": config.FIRST_MODULE_TOP_SEP_BASE,
        },
        {
            "name": "standard",
            "label": "标准排版",
            "module_sep": config.MODULE_SEP_BASE,
            "item_sep": config.ITEM_SEP_BASE,
            "line_stretch": config.LINE_STRETCH,
            "header_body_sep": config.HEADER_BODY_SEP_BASE,
            "first_module_top_sep": config.FIRST_MODULE_TOP_SEP_BASE,
        },
        {
            "name": "slightly_compact",
            "label": "微紧凑排版",
            "module_sep": config.MODULE_SEP_BASE * 0.9,
            "item_sep": 1.25,
            "line_stretch": 1.18,
            "header_body_sep": 1.0,
            "first_module_top_sep": 0.0,
        },
        {
            "name": "compact",
            "label": "紧凑排版",
            "module_sep": config.MODULE_SEP_BASE * 0.8,
            "item_sep": 1.0,
            "line_stretch": 1.15,
            "header_body_sep": 0.8,
            "first_module_top_sep": 0.0,
        },
        {
            "name": "ultra_compact",
            "label": "极紧凑排版",
            "module_sep": config.MODULE_SEP_BASE * 0.68,
            "item_sep": 0.7,
            "line_stretch": 1.12,
            "header_body_sep": 0.6,
            "first_module_top_sep": 0.0,
        },
    ]

def profile_to_spacing(profile):
    """把数值 profile 转成渲染器需要的 LaTeX 字符串参数。"""
    return {
        "module_sep": format_mm(profile["module_sep"]),
        "item_sep": format_mm(profile["item_sep"]),
        "line_stretch": f"{profile['line_stretch']:g}",
        "header_body_sep": format_mm(profile["header_body_sep"]),
        "first_module_top_sep": format_mm(profile["first_module_top_sep"]),
    }

# ==========================================
# 算法 3：动态间距微调阀 (核心排版逻辑)
# ==========================================
def optimize_layout_spacing(parsed_data):
    """
    根据内容总量推演 LaTeX 间距参数
    返回字典，用于后续注入 LaTeX 模板
    """
    profiles = get_layout_profiles(LayoutConfig)
    profile_heights = {
        profile["name"]: estimate_resume_total_height(parsed_data, LayoutConfig, profile)
        for profile in profiles
    }
    standard_profile = next(
        profile for profile in profiles
        if profile["name"] == "standard"
    )
    standard_index = profiles.index(standard_profile)
    base_height = profile_heights[standard_profile["name"]]
    valid_space = LayoutConfig.VALID_HEIGHT
    safe_space = valid_space * LayoutConfig.LAYOUT_SAFETY_RATIO
    
    print(
        f"📊 预计算总高度: {base_height:.1f} mm / "
        f"可用空间: {valid_space:.1f} mm / 安全线: {safe_space:.1f} mm"
    )
    print(
        "📐 候选排版档位: "
        + " / ".join(
            f"{profile['label']} {profile_heights[profile['name']]:.1f}mm"
            for profile in profiles
        )
    )

    # 方案 A：内容实在偏少时，不用夸张拉伸伪装饱满
    if base_height < valid_space * 0.82:
        raise ValueError(
            f"❌ 排版阻断：内容偏少。\n"
            f"标准排版高度为 {base_height:.1f}mm，低于建议下限 {valid_space * 0.82:.1f}mm。\n"
            f"建议：补充科研、竞赛、项目或综合素质内容后再生成。"
        )

    fitting_profiles = [
        profile for profile in profiles
        if profile_heights[profile["name"]] <= safe_space
    ]

    if fitting_profiles:
        chosen_profile = fitting_profiles[0]
        chosen_index = profiles.index(chosen_profile)
        chosen_height = profile_heights[chosen_profile["name"]]

        if chosen_index < standard_index:
            print(f"🔵 状态：内容有余量，使用【{chosen_profile['label']}】。")
        elif chosen_index == standard_index:
            print("✅ 状态：内容饱满，使用【标准排版】。")
        else:
            print(f"⚠️ 状态：接近满页或轻微超页，使用【{chosen_profile['label']}】。")

        print(f"🎚️ 选中档位高度: {chosen_height:.1f} mm")
        return profile_to_spacing(chosen_profile)

    # 方案 D：字太多了，最紧凑排版也无法安全容纳
    tightest_profile = profiles[-1]
    tightest_height = profile_heights[tightest_profile["name"]]
    tightest_line_height = LayoutConfig.CHAR_WIDTH_MM * tightest_profile["line_stretch"]
    raise ValueError(
        f"❌ 排版阻断：内容实在太多了！\n"
        f"{tightest_profile['label']}高度为 {tightest_height:.1f}mm，超过安全线 {safe_space:.1f}mm。\n"
        f"建议：请删减大约 {int(tightest_height - safe_space)} 毫米等效高度的内容"
        f"（约 {math.ceil((tightest_height - safe_space) / tightest_line_height)} 行正文）。"
    )

# ==========================================
# 测试运行代码
# ==========================================
if __name__ == "__main__":
    # 假设你已经把 parser.py 放到了同级目录
    from parser import parse_resume_md
    
    try:
        # 解析数据
        data = parse_resume_md("resume_config.md")
        # 预计算排版
        best_spacing = optimize_layout_spacing(data)
        
        print("\n✨ 最终推演出的 LaTeX 注入参数：")
        print(best_spacing)
        
    except Exception as e:
        print(e)
