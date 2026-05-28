import os

def parse_resume_md(file_path):
    """
    解析 resume_config.md，提取出强结构化的字典数据，并进行极其严格的数据校验。
    """
    # 获取 md 文件所在的目录，用于后续校验图片路径
    base_dir = os.path.dirname(os.path.abspath(file_path))
    
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    resume_data = {
        "header": {},
        "sections": {}
    }

    # --- 1. 寻找 YAML 分界线并解析头部 ---
    yaml_bounds = [i for i, line in enumerate(lines) if line.strip() == '---']
    if len(yaml_bounds) < 2:
        raise ValueError("❌ 解析异常：未找到完整的 YAML 头部 (缺少 --- 边界)")

    yaml_start, yaml_end = yaml_bounds[0], yaml_bounds[1]
    
    for line in lines[yaml_start+1 : yaml_end]:
        line = line.strip()
        if not line or line.startswith('#'):
            continue
            
        if ':' in line:
            key, value = line.split(':', 1)
            key = key.strip()
            value = value.strip()
            if value: # 过滤空值
                resume_data["header"][key] = value

    # ==========================================
    # 🚨 核心拦截网：头部数据强校验模块
    # ==========================================
    header = resume_data["header"]
    
    # 校验项 1：文字必填项不能少
    required_texts = {"姓名", "联系电话", "电子邮箱"}
    missing_texts = required_texts - set(header.keys())
    if missing_texts:
        raise ValueError(f"\n❌ [排版阻断] 基础信息缺失：\n必须填写 {missing_texts}，否则简历头部结构将崩溃！")

    # 校验项 2：双图必填项（不仅检查是否填了，还检查文件物理存不存在）
    required_images = {"证件照", "校徽"}

    # 校验项 3：头部选填项可自定义字段名，但模板最多容纳 1 项
    required_header_keys = required_texts | required_images
    filled_optionals = [key for key in header.keys() if key not in required_header_keys]

    if len(filled_optionals) > 1:
        raise ValueError(
            f"\n❌ [排版阻断] 网格选填项超载：\n"
            f"LaTeX 模板只能容纳 1 项，但你填写了 {filled_optionals}。\n"
            f"请保留 1 个自定义选填字段，或将多余字段留空/删除！"
        )

    # 校验项 4：双图路径检查
    missing_images = required_images - set(header.keys())
    if missing_images:
        raise ValueError(f"\n❌ [排版阻断] 图片信息缺失：\n保研学术简历必须包含 {missing_images}！")
        
    for img_key in required_images:
        img_filename = header[img_key]
        img_path = os.path.join(base_dir, img_filename)
        if not os.path.exists(img_path):
            raise FileNotFoundError(
                f"\n❌ [文件丢失] 找不到 {img_key}：\n"
                f"你在 md 中填写了 '{img_filename}'，但在同级目录下找不到该图片！\n"
                f"请检查文件名是否带上了后缀（如 .jpg/.png）或者文件是否放错了位置。"
            )
    # ==========================================
    
    # --- 2. 状态机解析 Markdown 正文 ---
    current_section = None
    current_deep_item = None

    for line in lines[yaml_end+1 :]:
        line = line.strip()
        if not line:
            continue
            
        if line.startswith('## '):
            current_section = line[3:].strip()
            resume_data["sections"][current_section] = []
            current_deep_item = None 
            continue

        if not current_section:
            continue

        if line.startswith('### '):
            content = line[4:].strip()
            parts = [p.strip() for p in content.split('|')]
            
            if len(parts) not in (1, 3, 4):
                raise ValueError(
                    f"\n❌ [排版阻断] 子标题切分错误：\n"
                    f"在【{current_section}】模块中，三级标题支持 1 段、3 段或 4 段。\n"
                    f"可用格式：'完整标题'、'块A | 块B | 块C'、'块A | 块B | 块C | 块D'。\n"
                    f"-> 你的输入是: {line}\n"
                    f"请检查英文 '|' 符号数量是否正确。"
                )
            
            current_deep_item = {"blocks": parts, "details": []}
            resume_data["sections"][current_section].append(current_deep_item)
            continue

        if line.startswith('- ') or line.startswith('* '):
            text = line[2:].strip()
            if current_deep_item is not None:
                current_deep_item["details"].append(text)
            else:
                resume_data["sections"][current_section].append(text)

    return resume_data

if __name__ == "__main__":
    try:
        data = parse_resume_md("resume_config.md")
        print("✅ 解析与校验通过，数据结构已提取。")
    except Exception as e:
        print(e)
