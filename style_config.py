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

    # centered 头部联系方式图标总开关：False 时所有联系方式图标都不显示
    ENABLE_CENTERED_HEADER_ICONS = True

    # 单个联系方式图标开关：可单独关闭某个字段前的图标
    CENTERED_HEADER_ICON_ENABLED = {
        "电子邮箱": True,
        "联系电话": True,
        "个人主页": True,
        "GitHub": True,
        "GitHub主页": True,
    }

    # centered 头部联系方式图标样式；PNG 与默认 LaTeX 图标共用这个高度
    CENTERED_HEADER_ICON_SIZE = "0.32cm"
    CENTERED_HEADER_ICON_TEXT_GAP = "0.06cm"
    CENTERED_HEADER_ICON_RAISE = "-0.035cm"

    # 自定义 PNG 图标路径：留空或文件不存在时，会使用下面的默认 LaTeX 图标
    CENTERED_HEADER_ICONS = {
        "电子邮箱": "icons/email.png",
        "联系电话": "icons/telephone.png",
        "个人主页": "",
        "GitHub": "icons/github.png",
        "GitHub主页": "icons/github.png",
    }

    # 默认 LaTeX 图标；如需完全依赖 PNG，可把对应字段设为空字符串
    CENTERED_HEADER_ICON_PACKAGE = r"\usepackage{fontawesome5}"
    CENTERED_HEADER_ICON_COMMANDS = {
        "电子邮箱": r"\faEnvelope",
        "联系电话": r"\faPhone",
        "个人主页": r"\faGlobe",
        "GitHub": r"\faGithub",
        "GitHub主页": r"\faGithub",
    }
