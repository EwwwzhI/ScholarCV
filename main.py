import os
import subprocess
import time

from parser import parse_resume_md
from engine import optimize_layout_spacing
from render import LatexRenderer
from image_processor import ImageProcessor

def clean_up_junk_files(base_name="output_resume"):
    """
    清理 LaTeX 编译产生的中间文件。
    """
    junk_extensions = ['.aux', '.log', '.out', '.toc', '.synctex.gz']
    print("🧹 正在清理编译产生的临时文件...")
    for ext in junk_extensions:
        file_path = f"{base_name}{ext}"
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception:
                pass

    for temp_img in ["processed_avatar.jpg", "processed_logo.png"]:
        if os.path.exists(temp_img):
            os.remove(temp_img)

def build_resume(md_file="resume_config.md", output_name="output_resume"):
    tex_file = f"{output_name}.tex"
    
    print("🚀 [Step 1/5] 启动自动化排版引擎...")
    try:
        resume_data = parse_resume_md(md_file)
        print("✅ Markdown 字典结构剥离与校验完毕。")
    except Exception as e:
        print(f"\n🚨 数据解析失败：{e}")
        return

    print("\n✂️ [Step 2/5] 正在进行图像资产清洗与自动裁切...")
    header = resume_data["header"]
    try:
        header["证件照"] = ImageProcessor.process_avatar(header.get("证件照", ""))
        header["校徽"] = ImageProcessor.process_logo(header.get("校徽", ""))
        print("✅ 证件照(2.6x3.6)与校徽(去边透明)规范化完成。")
    except Exception as e:
        print(f"\n🚨 图像预处理失败：{e}")
        return

    print("\n⚖️ [Step 3/5] 启动物理空间预推演...")
    try:
        best_spacing = optimize_layout_spacing(resume_data)
        print(f"✅ 高度推演完毕，注入 LaTeX 间距调优参数：{best_spacing}")
    except Exception as e:
        print(f"\n🚨 物理空间预计算失败：{e}")
        return

    print("\n🧬 [Step 4/5] 正在进行 LaTeX 源码拼装...")
    try:
        renderer = LatexRenderer(resume_data, best_spacing)
        final_tex = renderer.render()
        with open(tex_file, "w", encoding="utf-8") as f:
            f.write(final_tex)
        print("✅ 底层 .tex 源码生成完毕。")
    except Exception as e:
        print(f"\n🚨 LaTeX 渲染失败：{e}")
        return

    print("\n🖨️ [Step 5/5] 唤起 xelatex 引擎进行静默编译...")
    try:
        # 使用 subprocess 调用系统的 xelatex，并隐藏长篇大论的输出信息
        start_time = time.time()
        # -interaction=nonstopmode 保证遇到小警告不会卡住等待用户输入
        result = subprocess.run(
            ["xelatex", "-interaction=nonstopmode", tex_file],
            stdout=subprocess.PIPE, 
            stderr=subprocess.PIPE,
            text=True
        )
        
        if result.returncode == 0:
            compile_time = time.time() - start_time
            print(f"✅ 编译成功！耗时: {compile_time:.2f} 秒。")
        else:
            print("\n🚨 LaTeX 编译遇到严重错误，请检查你的文字中是否含有未转义的极其特殊的符号。")
            print("下面是底层报错信息：\n")
            print(result.stdout[-1000:]) # 打印最后 1000 个字符的报错方便排查
            return
            
    except FileNotFoundError:
        print("\n🚨 系统未检测到 'xelatex' 环境！请确保你已经安装了 TeX Live 或 MiKTeX。")
        return

    # 收尾工作
    clean_up_junk_files(output_name)
    
    print("\n🎉 =========================================")
    print(f"🎉 学术简历已生成：{output_name}.pdf")
    print("🎉 =========================================\n")

if __name__ == "__main__":
    build_resume()
