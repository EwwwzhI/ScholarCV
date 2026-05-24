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

def clamp(value, min_value, max_value):
    """把数值限制到闭区间内。"""
    return max(min_value, min(value, max_value))

def interpolate(min_value, max_value, ratio):
    """按 ratio 在 min 和 max 之间线性插值。"""
    return min_value + (max_value - min_value) * ratio

def get_safe_layout_space(config=LayoutConfig):
    """返回连续求解时允许使用的保守安全高度。"""
    ratio_safe_space = config.VALID_HEIGHT * config.LAYOUT_SAFETY_RATIO
    margin_safe_space = config.VALID_HEIGHT - getattr(config, "LAYOUT_SAFETY_MARGIN_MM", 0.0)
    return min(ratio_safe_space, margin_safe_space)

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
    line_height = (
        config.line_height_mm(line_stretch)
        if hasattr(config, "line_height_mm")
        else config.CHAR_WIDTH_MM * line_stretch
    )
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

def profile_from_layout_ratio(ratio, config=LayoutConfig):
    """根据连续排版系数生成参数；0 为最紧凑，1 为最舒展。"""
    ratio = clamp(ratio, 0.0, 1.0)
    return {
        "name": "continuous",
        "label": "连续排版",
        "layout_ratio": ratio,
        "module_sep": interpolate(config.MODULE_SEP_MIN_MM, config.MODULE_SEP_MAX_MM, ratio),
        "item_sep": interpolate(config.ITEM_SEP_MIN_MM, config.ITEM_SEP_MAX_MM, ratio),
        "line_stretch": interpolate(config.LINE_STRETCH_MIN, config.LINE_STRETCH_MAX, ratio),
        "header_body_sep": interpolate(
            config.HEADER_BODY_SEP_MIN_MM,
            config.HEADER_BODY_SEP_MAX_MM,
            ratio,
        ),
        "first_module_top_sep": interpolate(
            config.FIRST_MODULE_TOP_SEP_MIN_MM,
            config.FIRST_MODULE_TOP_SEP_MAX_MM,
            ratio,
        ),
    }

def standard_layout_profile(config=LayoutConfig):
    """返回当前配置基准值对应的 profile，用于日志和内容量判断。"""
    return {
        "name": "standard",
        "label": "标准排版",
        "module_sep": config.MODULE_SEP_BASE,
        "item_sep": config.ITEM_SEP_BASE,
        "line_stretch": config.LINE_STRETCH,
        "header_body_sep": config.HEADER_BODY_SEP_BASE,
        "first_module_top_sep": config.FIRST_MODULE_TOP_SEP_BASE,
    }

def solve_continuous_layout_profile(parsed_data, config=LayoutConfig):
    """通过二分法求出最接近目标高度的连续排版参数。"""
    valid_space = config.VALID_HEIGHT
    safe_space = get_safe_layout_space(config)
    target_max = min(valid_space * config.LAYOUT_TARGET_MAX_RATIO, safe_space)
    target_min = min(valid_space * config.LAYOUT_TARGET_MIN_RATIO, target_max)
    target_height = target_max

    compact_profile = profile_from_layout_ratio(0.0, config)
    airy_profile = profile_from_layout_ratio(1.0, config)
    standard_profile = standard_layout_profile(config)

    compact_height = estimate_resume_total_height(parsed_data, config, compact_profile)
    airy_height = estimate_resume_total_height(parsed_data, config, airy_profile)
    standard_height = estimate_resume_total_height(parsed_data, config, standard_profile)

    if compact_height > safe_space:
        tightest_line_height = (
            config.line_height_mm(compact_profile["line_stretch"])
            if hasattr(config, "line_height_mm")
            else config.CHAR_WIDTH_MM * compact_profile["line_stretch"]
        )
        raise ValueError(
            f"❌ 排版阻断：内容实在太多了！\n"
            f"最紧凑高度为 {compact_height:.1f}mm，超过安全线 {safe_space:.1f}mm。\n"
            f"建议：请删减大约 {int(compact_height - safe_space)} 毫米等效高度的内容"
            f"（约 {math.ceil((compact_height - safe_space) / tightest_line_height)} 行正文）。"
        )

    if airy_height < target_min:
        underfull_block_height = valid_space * config.LAYOUT_UNDERFULL_BLOCK_RATIO
        if standard_height < underfull_block_height:
            raise ValueError(
                f"❌ 排版阻断：内容偏少。\n"
                f"标准排版高度为 {standard_height:.1f}mm，低于建议下限 {underfull_block_height:.1f}mm。\n"
                f"建议：补充科研、竞赛、项目或综合素质内容后再生成。"
            )

        return airy_profile, airy_height, target_height

    if compact_height >= target_height:
        return compact_profile, compact_height, target_height

    low = 0.0
    high = 1.0
    best_profile = compact_profile
    best_height = compact_height
    epsilon = getattr(config, "LAYOUT_SOLVER_EPSILON_MM", 0.1)

    for _ in range(32):
        mid = (low + high) / 2
        candidate_profile = profile_from_layout_ratio(mid, config)
        candidate_height = estimate_resume_total_height(parsed_data, config, candidate_profile)

        best_profile = candidate_profile
        best_height = candidate_height

        if abs(candidate_height - target_height) <= epsilon:
            break

        if candidate_height < target_height:
            low = mid
        else:
            high = mid

    if best_height > safe_space:
        best_profile = profile_from_layout_ratio(low, config)
        best_height = estimate_resume_total_height(parsed_data, config, best_profile)

    return best_profile, best_height, target_height

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
    chosen_profile, chosen_height, target_height = solve_continuous_layout_profile(
        parsed_data,
        LayoutConfig,
    )
    layout_ratio = chosen_profile.get("layout_ratio", 0.0)

    print(
        f"✅ 连续排版：预计 {chosen_height:.1f}mm / 目标 {target_height:.1f}mm，"
        f"系数 {layout_ratio:.3f}"
    )
    return profile_to_spacing(chosen_profile)

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
