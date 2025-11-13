#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
单字分割提取程序
基于OCR识别结果，从字帖图片中提取每个单字并保存为独立图片
"""

import json
import os
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple
from PIL import Image
import numpy as np


class CharacterExtractor:
    """单字提取器"""
    
    def __init__(self, images_dir: Path, outputs_dir: Path, chars_dir: Path):
        """
        初始化单字提取器
        
        Args:
            images_dir: 原始图片目录
            outputs_dir: OCR识别结果目录
            chars_dir: 单字图片输出目录
        """
        self.images_dir = images_dir
        self.outputs_dir = outputs_dir
        self.chars_dir = chars_dir
        
        # 确保输出目录存在
        self.chars_dir.mkdir(parents=True, exist_ok=True)
    
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
            字边界框列表，每个元素包含 {text, position, confidence, line_index, word_index}
        """
        word_boxes = []
        
        if json_data.get('message') != 'success':
            return word_boxes
        
        data = json_data.get('data', {})
        text_lines = data.get('text_lines', [])
        
        for line_idx, text_line in enumerate(text_lines):
            words = text_line.get('words', [])
            for word_idx, word in enumerate(words):
                text = word.get('text', '')
                position = word.get('position', [])
                confidence = word.get('confidence', 0.0)
                det_confidence = word.get('det_confidence', 0.0)
                
                if text and len(position) >= 4:
                    word_boxes.append({
                        'text': text,
                        'position': position[:4],  # [x1, y1, x2, y2]
                        'confidence': confidence,
                        'det_confidence': det_confidence,
                        'line_index': line_idx,
                        'word_index': word_idx
                    })
        
        return word_boxes
    
    def expand_bbox(self, x1: int, y1: int, x2: int, y2: int, 
                   padding: int = 5, max_width: int = None, max_height: int = None) -> Tuple[int, int, int, int]:
        """
        扩展边界框，添加边距
        
        Args:
            x1, y1, x2, y2: 原始边界框坐标
            padding: 边距像素数
            max_width: 图片最大宽度（用于边界检查）
            max_height: 图片最大高度（用于边界检查）
            
        Returns:
            扩展后的边界框坐标 (x1, y1, x2, y2)
        """
        new_x1 = max(0, x1 - padding)
        new_y1 = max(0, y1 - padding)
        new_x2 = x2 + padding
        new_y2 = y2 + padding
        
        if max_width:
            new_x2 = min(new_x2, max_width)
        if max_height:
            new_y2 = min(new_y2, max_height)
        
        return new_x1, new_y1, new_x2, new_y2
    
    def extract_character(self, image: Image.Image, word_box: Dict[str, Any], 
                         padding: int = 5, min_size: int = 10) -> Optional[Image.Image]:
        """
        从图片中提取单个字符
        
        Args:
            image: PIL图片对象
            word_box: 字边界框信息
            padding: 边距像素数
            min_size: 最小尺寸（过滤太小的字符）
            
        Returns:
            提取的字符图片，如果提取失败返回None
        """
        position = word_box['position']
        if len(position) < 4:
            return None
        
        x1, y1, x2, y2 = position
        
        # 检查边界框是否有效
        width = x2 - x1
        height = y2 - y1
        if width < min_size or height < min_size:
            return None
        
        # 扩展边界框
        img_width, img_height = image.size
        x1, y1, x2, y2 = self.expand_bbox(x1, y1, x2, y2, padding, img_width, img_height)
        
        # 提取字符区域
        try:
            char_image = image.crop((x1, y1, x2, y2))
            return char_image
        except Exception as e:
            print(f"提取字符失败: {e}")
            return None
    
    def sanitize_filename(self, text: str, max_length: int = 50) -> str:
        """
        清理文件名，移除非法字符
        
        Args:
            text: 原始文本
            max_length: 最大文件名长度
            
        Returns:
            清理后的文件名
        """
        # 移除或替换非法字符
        illegal_chars = ['<', '>', ':', '"', '/', '\\', '|', '?', '*']
        filename = text
        for char in illegal_chars:
            filename = filename.replace(char, '_')
        
        # 限制长度
        if len(filename) > max_length:
            filename = filename[:max_length]
        
        return filename
    
    def save_character(self, char_image: Image.Image, word_box: Dict[str, Any], 
                      image_name: str, output_format: str = 'PNG') -> Path:
        """
        保存提取的字符图片
        
        Args:
            char_image: 字符图片
            word_box: 字边界框信息
            image_name: 原始图片名称
            output_format: 输出格式（PNG, JPEG等）
            
        Returns:
            保存的文件路径
        """
        text = word_box['text']
        line_idx = word_box['line_index']
        word_idx = word_box['word_index']
        confidence = word_box.get('confidence', 0.0)
        
        # 生成文件名：图片名_行号_字序号_字符_置信度.png
        safe_text = self.sanitize_filename(text)
        filename = f"{image_name}_L{line_idx:03d}_W{word_idx:03d}_{safe_text}_C{confidence:.3f}.{output_format.lower()}"
        
        output_path = self.chars_dir / filename
        
        # 保存图片
        if output_format.upper() == 'PNG':
            char_image.save(output_path, 'PNG')
        elif output_format.upper() == 'JPEG' or output_format.upper() == 'JPG':
            # JPEG不支持透明通道，需要转换为RGB
            if char_image.mode in ('RGBA', 'LA', 'P'):
                rgb_image = Image.new('RGB', char_image.size, (255, 255, 255))
                if char_image.mode == 'P':
                    char_image = char_image.convert('RGBA')
                rgb_image.paste(char_image, mask=char_image.split()[-1] if char_image.mode == 'RGBA' else None)
                char_image = rgb_image
            char_image.save(output_path, 'JPEG', quality=95)
        else:
            char_image.save(output_path, output_format.upper())
        
        return output_path
    
    def extract_all_characters(self, image_name: str, padding: int = 5, 
                              min_confidence: float = 0.0, min_size: int = 10,
                              output_format: str = 'PNG') -> Dict[str, Any]:
        """
        从指定图片中提取所有字符
        
        Args:
            image_name: 图片名称（不含扩展名）
            padding: 边距像素数
            min_confidence: 最小置信度阈值（过滤低置信度字符）
            min_size: 最小字符尺寸
            output_format: 输出格式
            
        Returns:
            提取结果统计信息
        """
        # 查找JSON结果文件
        json_file = self.outputs_dir / f"{image_name}_result.json"
        if not json_file.exists():
            print(f"未找到JSON结果文件: {json_file}")
            return {'success': False, 'error': 'JSON文件不存在'}
        
        # 加载JSON数据
        json_data = self.load_json_result(json_file)
        if not json_data:
            return {'success': False, 'error': 'JSON加载失败'}
        
        # 查找原始图片
        original_image_path = self.find_original_image(image_name)
        if not original_image_path:
            print(f"未找到原始图片: {image_name}")
            return {'success': False, 'error': '原始图片不存在'}
        
        # 加载图片
        try:
            image = Image.open(original_image_path)
        except Exception as e:
            print(f"加载图片失败: {e}")
            return {'success': False, 'error': f'图片加载失败: {e}'}
        
        # 提取所有字的边界框
        word_boxes = self.extract_word_boxes(json_data)
        if not word_boxes:
            print(f"未找到字的边界框信息")
            return {'success': False, 'error': '未找到边界框信息'}
        
        print(f"找到 {len(word_boxes)} 个字符，开始提取...")
        
        # 提取并保存每个字符
        extracted_count = 0
        skipped_count = 0
        saved_files = []
        
        for word_box in word_boxes:
            # 过滤低置信度字符
            confidence = word_box.get('confidence', 0.0)
            if confidence < min_confidence:
                skipped_count += 1
                continue
            
            # 提取字符
            char_image = self.extract_character(image, word_box, padding, min_size)
            if not char_image:
                skipped_count += 1
                continue
            
            # 保存字符
            try:
                output_path = self.save_character(char_image, word_box, image_name, output_format)
                saved_files.append(str(output_path))
                extracted_count += 1
            except Exception as e:
                print(f"保存字符失败 {word_box.get('text', '?')}: {e}")
                skipped_count += 1
        
        result = {
            'success': True,
            'image_name': image_name,
            'total_characters': len(word_boxes),
            'extracted_count': extracted_count,
            'skipped_count': skipped_count,
            'output_dir': str(self.chars_dir),
            'saved_files': saved_files
        }
        
        return result
    
    def extract_all_images(self, padding: int = 5, min_confidence: float = 0.0, 
                          min_size: int = 10, output_format: str = 'PNG'):
        """
        提取所有图片中的字符
        
        Args:
            padding: 边距像素数
            min_confidence: 最小置信度阈值
            min_size: 最小字符尺寸
            output_format: 输出格式
        """
        # 查找所有JSON结果文件
        json_files = list(self.outputs_dir.glob("*_result.json"))
        
        if not json_files:
            print(f"在 {self.outputs_dir} 目录中未找到JSON结果文件")
            print("请先运行 ocr_test.py 生成识别结果")
            return
        
        print(f"找到 {len(json_files)} 个JSON结果文件，开始提取字符...\n")
        print("=" * 60)
        
        total_extracted = 0
        total_skipped = 0
        
        # 处理每个JSON文件
        for json_file in json_files:
            # 提取图片名称（去掉 _result.json 后缀）
            image_name = json_file.stem.replace('_result', '')
            print(f"\n处理: {image_name}")
            print("-" * 50)
            
            result = self.extract_all_characters(
                image_name, 
                padding=padding,
                min_confidence=min_confidence,
                min_size=min_size,
                output_format=output_format
            )
            
            if result['success']:
                print(f"  ✓ 成功提取 {result['extracted_count']} 个字符")
                print(f"  ⚠ 跳过 {result['skipped_count']} 个字符")
                total_extracted += result['extracted_count']
                total_skipped += result['skipped_count']
            else:
                print(f"  ✗ 提取失败: {result.get('error', '未知错误')}")
        
        print("\n" + "=" * 60)
        print(f"\n所有图片处理完成！")
        print(f"总共提取: {total_extracted} 个字符")
        print(f"总共跳过: {total_skipped} 个字符")
        print(f"结果已保存到: {self.chars_dir}")


def main():
    """主函数"""
    # 获取项目根目录
    project_root = Path(__file__).parent
    
    # 设置路径
    images_dir = project_root / 'images'
    outputs_dir = project_root / 'outputs'
    chars_dir = project_root / 'characters'  # 单字图片输出目录
    
    # 检查目录是否存在
    if not images_dir.exists():
        print(f"错误: 图片目录不存在: {images_dir}")
        return
    
    if not outputs_dir.exists():
        print(f"错误: 输出目录不存在: {outputs_dir}")
        print("请先运行 ocr_test.py 生成识别结果")
        return
    
    # 创建提取器
    extractor = CharacterExtractor(images_dir, outputs_dir, chars_dir)
    
    # 开始提取
    print("=" * 60)
    print("单字分割提取程序")
    print("=" * 60)
    
    # 可以自定义参数
    extractor.extract_all_images(
        padding=5,              # 边距（像素）
        min_confidence=0.0,     # 最小置信度（0.0-1.0，0表示不过滤）
        min_size=10,            # 最小字符尺寸（像素）
        output_format='PNG'     # 输出格式：PNG, JPEG等
    )


if __name__ == '__main__':
    main()

