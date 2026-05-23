class StyleConfig:
    # 颜色配置：使用 HTML 十六进制色值，不需要写 '#'
    TITLE_COLOR = "000000"
    BODY_COLOR = "000000"
    RULE_COLOR = "000000"

    # 模块标题图标总开关：False 时所有图标都不显示
    ENABLE_SECTION_ICONS = True

    # 单个模块图标开关：可单独关闭某个模块的图标
    SECTION_ICON_ENABLED = {
        "基本信息": True,
        "教育背景": True,
        "科研经历": True,
        "项目经历": True,
        "竞赛经历": True,
        "其他成果": True,
        "综合素质": True,
    }

    # 模块标题图标样式：PNG 文件可选；文件不存在时自动忽略
    SECTION_ICON_SIZE = "0.45cm"
    SECTION_ICON_TEXT_GAP = "0.12cm"

    # 模块标题图标路径：键名需要和 Markdown 中的二级标题一致
    SECTION_ICONS = {
        "基本信息": "icons/basic.png",
        "教育背景": "icons/education.png",
        "科研经历": "icons/research.png",
        "项目经历": "icons/project.png",
        "竞赛经历": "icons/competition.png",
        "其他成果": "icons/award.png",
        "综合素质": "icons/profile.png",
    }
