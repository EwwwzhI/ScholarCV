import os
from PIL import Image, ImageChops

class ImageProcessor:
    @staticmethod
    def process_avatar(input_path, output_path="processed_avatar.jpg", target_ratio=2.6/3.6):
        """
        对证件照进行无损的“智能中心裁切 (Center Crop)”。
        确保无论用户提供的照片多长多宽，都会被裁切成目标排版比例。
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"❌ [图片丢失] 找不到证件照文件：{input_path}")
            
        img = Image.open(input_path)
        img_w, img_h = img.size
        current_ratio = img_w / img_h
        
        if current_ratio > target_ratio:
            # 图片偏宽：裁切左右两边
            new_w = int(img_h * target_ratio)
            left = (img_w - new_w) // 2
            right = left + new_w
            top = 0
            bottom = img_h
        else:
            # 图片偏长：裁切上下。权重分配为保留上方头部，裁切下方衣物
            new_h = int(img_w / target_ratio)
            left = 0
            right = img_w
            top = int((img_h - new_h) * 0.15) 
            bottom = top + new_h
            
        cropped_img = img.crop((left, top, right, bottom))
        
        if cropped_img.mode in ("RGBA", "P"):
            cropped_img = cropped_img.convert("RGB")
            
        cropped_img.save(output_path, quality=95)
        return output_path

    @staticmethod
    def process_logo(input_path, output_path="processed_logo.png", target_height=300):
        """
        对校徽进行“边界吸附裁切 (Auto-Crop)”与分辨率控制。
        1. 自动消除图片四周多余的白边或透明边，确保 LaTeX 的 height 绝对精准。
        2. 限制最高分辨率，防止 PDF 导致体积过大。
        """
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"❌ [图片丢失] 找不到校徽文件：{input_path}")
            
        img = Image.open(input_path)
        
        # 统一转换为 RGBA，方便处理透明或纯白背景
        img = img.convert("RGBA")
        
        # 透明图优先按 alpha 裁切；纯白背景图按 RGB 差异裁切。
        # 不能直接对 RGBA 差异图 getbbox，否则 alpha 差异全为 0 时会漏裁。
        alpha = img.getchannel("A")
        if alpha.getextrema()[0] < 255:
            bbox = alpha.getbbox()
        else:
            bg = Image.new("RGB", img.size, (255, 255, 255))
            diff = ImageChops.difference(img.convert("RGB"), bg)
            bbox = diff.getbbox()
        
        if bbox:
            # 根据真实边界进行精确裁切，彻底抛弃四周无用的留白
            img = img.crop(bbox)
            
        # 尺寸控制：排版中 1.4cm 对应打印约 150-300 像素即可，太大会造成 PDF 冗余
        img_w, img_h = img.size
        if img_h > target_height:
            ratio = target_height / img_h
            new_w = int(img_w * ratio)
            new_h = int(img_h * ratio)
            
            # 兼容不同版本的 Pillow 重采样属性
            resample_filter = getattr(Image, 'Resampling', Image).LANCZOS
            img = img.resize((new_w, new_h), resample_filter)
            
        # 必须存为 PNG 格式，以保留校徽可能的透明背景
        img.save(output_path, "PNG")
        return output_path
