#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
OCR识别结果可视化程序
读取JSON识别结果，在原始图片上绘制每个字的边界框
"""

import json
import os
import platform
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import matplotlib.font_manager as fm
from PIL import Image
import numpy as np


def setup_chinese_font():
    """
    设置matplotlib支持中文字体
    """
    system = platform.system()
    
    # Windows系统常见中文字体
    if system == 'Windows':
        chinese_fonts = ['Microsoft YaHei', 'SimHei', 'SimSun', 'KaiTi', 'FangSong']
    # macOS系统常见中文字体
    elif system == 'Darwin':
        chinese_fonts = ['Arial Unicode MS', 'PingFang SC', 'STHeiti', 'STSong']
    # Linux系统常见中文字体
    else:
        chinese_fonts = ['WenQuanYi Micro Hei', 'WenQuanYi Zen Hei', 'Noto Sans CJK SC']
    
    # 尝试设置中文字体
    font_set = False
    for font_name in chinese_fonts:
        try:
            # 检查字体是否可用
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            if font_name in available_fonts:
                plt.rcParams['font.sans-serif'] = [font_name]
                plt.rcParams['axes.unicode_minus'] = False  # 解决负号显示问题
                font_set = True
                print(f"已设置中文字体: {font_name}")
                break
        except Exception as e:
            continue
    
    # 如果找不到字体，尝试使用系统默认字体
    if not font_set:
        try:
            # 获取所有可用字体
            available_fonts = [f.name for f in fm.fontManager.ttflist]
            # 查找包含中文的字体
            chinese_keywords = ['Chinese', 'CJK', 'Hei', 'Song', 'Kai', 'Fang']
            for font in available_fonts:
                if any(keyword in font for keyword in chinese_keywords):
                    plt.rcParams['font.sans-serif'] = [font]
                    plt.rcParams['axes.unicode_minus'] = False
                    font_set = True
                    print(f"已设置中文字体: {font}")
                    break
        except Exception:
            pass
    
    if not font_set:
        print("警告: 未找到合适的中文字体，中文可能显示为方框")
        print("建议安装中文字体（如 Microsoft YaHei 或 SimHei）")


class OCRVisualizer:
    """OCR识别结果可视化器"""
    
    def __init__(self, images_dir: Path, outputs_dir: Path):
        """
        初始化可视化器
        
        Args:
            images_dir: 原始图片目录
            outputs_dir: 识别结果目录
        """
        self.images_dir = images_dir
        self.outputs_dir = outputs_dir
    
    def load_json_result(self, json_file: Path) -> Optional[Dict[str, Any]]:
        """
        加载JSON识别结果
        
        Args:
            json_file: JSON文件路径
            
        Returns:
            JSON数据，如果加载失败返回None
        """
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载JSON文件失败 {json_file}: {e}")
            return None
    
    def find_original_image(self, image_name: str) -> Optional[Path]:
        """
        根据图片名称查找原始图片文件
        
        Args:
            image_name: 图片名称（不含扩展名）
            
        Returns:
            原始图片路径，如果未找到返回None
        """
        # 支持的图片格式
        image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp']
        
        for ext in image_extensions:
            image_path = self.images_dir / f"{image_name}{ext}"
            if image_path.exists():
                return image_path
        
        # 如果找不到，尝试查找包含该名称的文件
        for ext in image_extensions:
            for img_file in self.images_dir.glob(f"*{image_name}*{ext}"):
                return img_file
        
        return None
    
    def extract_word_boxes(self, json_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        从JSON数据中提取所有字的边界框信息
        
        Args:
            json_data: JSON识别结果
            
        Returns:
            字边界框列表，每个元素包含 {text, position, confidence}
        """
        word_boxes = []
        
        if json_data.get('message') != 'success':
            return word_boxes
        
        data = json_data.get('data', {})
        text_lines = data.get('text_lines', [])
        
        for text_line in text_lines:
            words = text_line.get('words', [])
            for word in words:
                text = word.get('text', '')
                position = word.get('position', [])
                confidence = word.get('confidence', 0.0)
                
                if text and len(position) >= 4:
                    word_boxes.append({
                        'text': text,
                        'position': position[:4],  # [x1, y1, x2, y2]
                        'confidence': confidence
                    })
        
        return word_boxes
    
    def draw_word_boxes(self, image_path: Path, word_boxes: List[Dict[str, Any]], 
                       output_path: Path, show_text: bool = True, 
                       box_color: str = 'red', text_color: str = 'yellow',
                       line_width: float = 1.5, font_size: int = 10):
        """
        在图片上绘制字的边界框
        
        Args:
            image_path: 原始图片路径
            word_boxes: 字边界框列表
            output_path: 输出图片路径
            show_text: 是否在框内显示文字
            box_color: 边界框颜色
            text_color: 文字颜色
            line_width: 边界框线宽
            font_size: 字体大小
        """
        # 加载图片
        try:
            img = Image.open(image_path)
            img_array = np.array(img)
        except Exception as e:
            print(f"加载图片失败 {image_path}: {e}")
            return
        
        # 创建图形
        fig, ax = plt.subplots(1, 1, figsize=(16, 12))
        ax.imshow(img_array)
        ax.axis('off')
        
        # 绘制每个字的边界框
        for word_box in word_boxes:
            position = word_box['position']
            text = word_box['text']
            confidence = word_box.get('confidence', 0.0)
            
            if len(position) < 4:
                continue
            
            x1, y1, x2, y2 = position
            
            # 绘制矩形框
            width = x2 - x1
            height = y2 - y1
            rect = patches.Rectangle(
                (x1, y1), width, height,
                linewidth=line_width,
                edgecolor=box_color,
                facecolor='none'
            )
            ax.add_patch(rect)
            
            # 在框内显示文字（可选）
            if show_text:
                # 计算文字显示位置（框的左上角稍微偏移）
                text_x = x1 + 2
                text_y = y1 - 5 if y1 > 20 else y1 + height + 15
                
                # 显示文字和置信度
                display_text = f"{text}"
                if confidence > 0:
                    display_text += f" ({confidence:.2f})"
                
                ax.text(
                    text_x, text_y, display_text,
                    fontsize=font_size,
                    color=text_color,
                    weight='bold',
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='black', alpha=0.7, edgecolor='none')
                )
        
        # 添加标题
        title = f"OCR识别结果可视化 - 共识别 {len(word_boxes)} 个字"
        ax.set_title(title, fontsize=14, pad=10, color='white', 
                    bbox=dict(boxstyle='round', facecolor='black', alpha=0.8))
        
        # 保存图片
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight', facecolor='black')
        plt.close()
        
        print(f"✓ 可视化结果已保存: {output_path}")
    
    def visualize_all_results(self, show_text: bool = True, 
                            box_color: str = 'red', text_color: str = 'yellow'):
        """
        可视化所有JSON识别结果
        
        Args:
            show_text: 是否在框内显示文字
            box_color: 边界框颜色
            text_color: 文字颜色
        """
        # 查找所有JSON文件
        json_files = list(self.outputs_dir.glob("*_result.json"))
        
        if not json_files:
            print(f"在 {self.outputs_dir} 目录中未找到JSON结果文件")
            print("请先运行 ocr_test.py 生成识别结果")
            return
        
        print(f"找到 {len(json_files)} 个JSON结果文件，开始可视化...\n")
        
        # 处理每个JSON文件
        for json_file in json_files:
            # 提取图片名称（去掉 _result.json 后缀）
            image_name = json_file.stem.replace('_result', '')
            print(f"\n处理: {image_name}")
            print("-" * 50)
            
            # 加载JSON数据
            json_data = self.load_json_result(json_file)
            if not json_data:
                continue
            
            # 提取字的边界框
            word_boxes = self.extract_word_boxes(json_data)
            if not word_boxes:
                print(f"  ⚠ 未找到字的边界框信息（可能JSON中未包含位置信息）")
                continue
            
            print(f"  找到 {len(word_boxes)} 个字的边界框")
            
            # 查找原始图片
            original_image = self.find_original_image(image_name)
            if not original_image:
                print(f"  ⚠ 未找到原始图片: {image_name}")
                continue
            
            print(f"  原始图片: {original_image.name}")
            
            # 生成输出路径
            output_image = self.outputs_dir / f"{image_name}_visualized.png"
            
            # 绘制边界框
            try:
                self.draw_word_boxes(
                    original_image, word_boxes, output_image,
                    show_text=show_text,
                    box_color=box_color,
                    text_color=text_color
                )
            except Exception as e:
                print(f"  ✗ 可视化失败: {e}")
        
        print(f"\n\n所有可视化完成！结果已保存到 {self.outputs_dir} 目录")


def main():
    """主函数"""
    # 设置中文字体支持
    setup_chinese_font()
    
    # 获取项目根目录
    project_root = Path(__file__).parent
    
    # 设置路径
    images_dir = project_root / 'images'
    outputs_dir = project_root / 'outputs'
    
    # 检查目录是否存在
    if not images_dir.exists():
        print(f"错误: 图片目录不存在: {images_dir}")
        return
    
    if not outputs_dir.exists():
        print(f"错误: 输出目录不存在: {outputs_dir}")
        print("请先运行 ocr_test.py 生成识别结果")
        return
    
    # 创建可视化器
    visualizer = OCRVisualizer(images_dir, outputs_dir)
    
    # 开始可视化
    print("=" * 60)
    print("OCR识别结果可视化程序")
    print("=" * 60)
    
    # 可以自定义参数
    visualizer.visualize_all_results(
        show_text=True,      # 在框内显示文字
        box_color='red',    # 边界框颜色：red, blue, green, yellow等
        text_color='yellow' # 文字颜色
    )


if __name__ == '__main__':
    main()

