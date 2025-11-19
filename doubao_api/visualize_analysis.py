#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
书法单字分析结果可视化工具
将分析结果中的关键点标注在原图上
"""

import os
import sys
import json
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


class AnalysisVisualizer:
    """分析结果可视化器"""
    
    def __init__(self):
        """初始化可视化器"""
        self.point_color = (255, 0, 0)  # 红色关键点
        self.point_radius = 5
        self.text_color = (255, 255, 255)  # 白色文字
        self.text_bg_color = (0, 0, 0, 180)  # 半透明黑色背景
        self.font_size = 14
        self.max_image_size = 300  # 图片最大尺寸
    
    def load_analysis_result(self, json_path):
        """
        加载分析结果JSON文件
        
        Args:
            json_path: JSON文件路径
            
        Returns:
            分析结果字典
        """
        with open(json_path, 'r', encoding='utf-8') as f:
            result = json.load(f)
        
        print(f"✓ 已加载分析结果: {json_path}")
        return result
    
    def visualize(self, image_path, result, output_path=None):
        """
        在图片上可视化标注关键点
        
        Args:
            image_path: 原始图片路径
            result: 分析结果字典
            output_path: 输出图片路径（可选）
            
        Returns:
            输出图片路径
        """
        # 打开图片
        img = Image.open(image_path)
        img = img.convert('RGBA')  # 转换为RGBA以支持透明度
        orig_width, orig_height = img.size
        
        print(f"原图尺寸: {orig_width}x{orig_height}px")
        
        # 缩放图片到300px（长边）
        max_size = self.max_image_size
        if orig_width > max_size or orig_height > max_size:
            if orig_width > orig_height:
                new_width = max_size
                new_height = int(orig_height * max_size / orig_width)
            else:
                new_height = max_size
                new_width = int(orig_width * max_size / orig_height)
            
            img = img.resize((new_width, new_height), Image.LANCZOS)
            print(f"缩放后尺寸: {new_width}x{new_height}px")
        
        width, height = img.size
        
        # 创建绘图对象
        overlay = Image.new('RGBA', img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        
        # 尝试加载中文字体
        try:
            # Windows系统字体路径
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",  # 微软雅黑
                "C:/Windows/Fonts/simsun.ttc",  # 宋体
                "C:/Windows/Fonts/simhei.ttf",  # 黑体
            ]
            font = None
            font_small = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, self.font_size)
                    font_small = ImageFont.truetype(font_path, self.font_size - 2)
                    print(f"✓ 已加载中文字体: {os.path.basename(font_path)}")
                    break
            
            if font is None:
                print("⚠ 未找到中文字体，使用默认字体")
                font = ImageFont.load_default()
                font_small = ImageFont.load_default()
        except Exception as e:
            print(f"⚠ 加载字体失败: {e}，使用默认字体")
            font = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # 标注关键点
        keypoints = result.get('keypoints', [])
        print(f"开始标注 {len(keypoints)} 个关键点...")
        
        for kp in keypoints:
            # 将相对坐标转换为绝对坐标
            abs_x = int(kp['x'] * width)
            abs_y = int(kp['y'] * height)
            
            # 绘制关键点（实心圆）
            draw.ellipse(
                [
                    abs_x - self.point_radius,
                    abs_y - self.point_radius,
                    abs_x + self.point_radius,
                    abs_y + self.point_radius
                ],
                fill=self.point_color,
                outline=(255, 255, 255, 255),
                width=2
            )
            
            # 准备注释文本
            point_id = f"点{kp['id']}"
            description = kp.get('description', '')
            tips = kp.get('tips', '')
            
            # 组合文本，限制长度
            max_text_length = 30
            annotation_lines = [point_id]
            if description:
                if len(description) > max_text_length:
                    description = description[:max_text_length] + "..."
                annotation_lines.append(description)
            if tips:
                if len(tips) > max_text_length:
                    tips = tips[:max_text_length] + "..."
                annotation_lines.append(tips)
            
            # 计算文本框尺寸
            padding = 4
            line_spacing = 2
            max_text_width = 0
            total_text_height = 0
            
            for line in annotation_lines:
                bbox = draw.textbbox((0, 0), line, font=font_small)
                line_width = bbox[2] - bbox[0]
                line_height = bbox[3] - bbox[1]
                max_text_width = max(max_text_width, line_width)
                total_text_height += line_height + line_spacing
            
            total_text_height -= line_spacing  # 移除最后一行的间距
            
            # 确定文本框位置（优先在点的右侧，如果空间不够则放在左侧或下方）
            text_x = abs_x + self.point_radius + 8
            text_y = abs_y - total_text_height // 2
            
            # 边界检查和调整
            if text_x + max_text_width + padding * 2 > width:
                # 右侧空间不够，放在左侧
                text_x = abs_x - self.point_radius - max_text_width - padding * 2 - 8
            if text_y < 0:
                text_y = 0
            if text_y + total_text_height + padding * 2 > height:
                text_y = height - total_text_height - padding * 2
            
            # 绘制文本背景
            draw.rectangle(
                [
                    text_x - padding,
                    text_y - padding,
                    text_x + max_text_width + padding,
                    text_y + total_text_height + padding
                ],
                fill=self.text_bg_color
            )
            
            # 绘制多行文本
            current_y = text_y
            for i, line in enumerate(annotation_lines):
                bbox = draw.textbbox((0, 0), line, font=font_small)
                line_height = bbox[3] - bbox[1]
                
                # 第一行（点ID）使用黄色，其他行使用白色
                text_color = (255, 255, 0) if i == 0 else self.text_color
                
                draw.text(
                    (text_x, current_y),
                    line,
                    fill=text_color,
                    font=font_small
                )
                current_y += line_height + line_spacing
            
            print(f"  点{kp['id']}: ({kp['x']:.2f}, {kp['y']:.2f}) -> ({abs_x}, {abs_y})px - {description}")
        
        # 合并图层
        img = Image.alpha_composite(img, overlay)
        img = img.convert('RGB')  # 转回RGB以保存为JPG
        
        # 确定输出路径
        if output_path is None:
            output_dir = Path(__file__).parent / "outputs"
            output_dir.mkdir(exist_ok=True)
            
            character = result.get('character', 'unknown')
            input_name = Path(image_path).stem
            output_path = output_dir / f"{input_name}_annotated.png"
        
        # 保存图片
        img.save(output_path)
        print(f"✓ 标注图片已保存至: {output_path}")
        
        return output_path
    
    def create_info_image(self, result, output_path=None):
        """
        创建一个包含详细信息的图片
        
        Args:
            result: 分析结果字典
            output_path: 输出图片路径（可选）
            
        Returns:
            输出图片路径
        """
        # 图片尺寸
        width = 800
        line_height = 40
        padding = 20
        
        # 计算需要的高度
        keypoints = result.get('keypoints', [])
        num_lines = 5 + len(keypoints) * 3  # 标题 + 每个关键点3行
        height = num_lines * line_height + padding * 2
        
        # 创建图片
        img = Image.new('RGB', (width, height), color=(255, 255, 255))
        draw = ImageDraw.Draw(img)
        
        # 加载字体
        try:
            font_paths = [
                "C:/Windows/Fonts/msyh.ttc",
                "C:/Windows/Fonts/simsun.ttc",
                "C:/Windows/Fonts/simhei.ttf",
            ]
            font = None
            for font_path in font_paths:
                if os.path.exists(font_path):
                    font = ImageFont.truetype(font_path, 16)
                    break
            
            if font is None:
                font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        # 绘制内容
        y = padding
        
        # 标题
        draw.text((padding, y), f"字: {result.get('character', '未知')}", fill=(0, 0, 0), font=font)
        y += line_height
        
        draw.text((padding, y), f"复杂度: {result.get('complexity', '未知')}", fill=(0, 0, 0), font=font)
        y += line_height
        
        draw.text((padding, y), f"关键点数量: {len(keypoints)}", fill=(0, 0, 0), font=font)
        y += line_height * 2
        
        # 关键点详情
        for kp in keypoints:
            draw.text((padding, y), f"关键点 {kp['id']}: ({kp['x']:.2f}, {kp['y']:.2f})", fill=(255, 0, 0), font=font)
            y += line_height
            
            draw.text((padding * 2, y), f"位置: {kp['description']}", fill=(0, 0, 0), font=font)
            y += line_height
            
            # 处理长文本换行
            tips = kp['tips']
            if len(tips) > 40:
                tips = tips[:40] + "..."
            draw.text((padding * 2, y), f"提示: {tips}", fill=(0, 0, 0), font=font)
            y += line_height * 1.5
        
        # 整体建议
        y += line_height
        draw.text((padding, y), "整体建议:", fill=(0, 0, 255), font=font)
        y += line_height
        
        overall_tips = result.get('overall_tips', '')
        # 简单换行处理
        if len(overall_tips) > 50:
            lines = [overall_tips[i:i+50] for i in range(0, len(overall_tips), 50)]
        else:
            lines = [overall_tips]
        
        for line in lines:
            draw.text((padding * 2, y), line, fill=(0, 0, 0), font=font)
            y += line_height
        
        # 确定输出路径
        if output_path is None:
            output_dir = Path(__file__).parent / "outputs"
            output_dir.mkdir(exist_ok=True)
            
            character = result.get('character', 'unknown')
            output_path = output_dir / f"{character}_info.png"
        
        # 保存图片
        img.save(output_path)
        print(f"✓ 信息图片已保存至: {output_path}")
        
        return output_path


def batch_visualize_outputs():
    """批量可视化 outputs 目录下的所有 JSON 结果"""
    script_dir = Path(__file__).parent
    output_dir = script_dir / "outputs"
    
    if not output_dir.exists():
        print(f"✗ 错误: outputs 目录不存在 - {output_dir}")
        sys.exit(1)
    
    # 查找所有 JSON 文件
    json_files = list(output_dir.glob("*_analysis*.json"))
    
    if not json_files:
        print(f"✗ 错误: 在 {output_dir} 中未找到分析结果 JSON 文件")
        sys.exit(1)
    
    print("=" * 60)
    print("批量可视化分析结果")
    print("=" * 60)
    print(f"找到 {len(json_files)} 个 JSON 文件")
    print("=" * 60)
    print()
    
    # 创建可视化器
    visualizer = AnalysisVisualizer()
    
    success_count = 0
    fail_count = 0
    
    for i, json_file in enumerate(json_files, 1):
        print(f"[{i}/{len(json_files)}] 处理: {json_file.name}")
        
        try:
            # 加载分析结果
            result = visualizer.load_analysis_result(str(json_file))
            
            # 从 metadata 中获取原图路径
            image_path = result.get('metadata', {}).get('image_path', '')
            
            if not image_path or not os.path.exists(image_path):
                # 尝试从 characters_test 目录查找
                character = result.get('character', json_file.stem.replace('_analysis', ''))
                possible_paths = [
                    script_dir / "characters_test" / f"{character}.png",
                    script_dir / "characters_test" / f"{character}.jpg",
                    script_dir / "characters_test" / f"{character}.jpeg",
                ]
                
                image_path = None
                for p in possible_paths:
                    if p.exists():
                        image_path = str(p)
                        break
                
                if not image_path:
                    print(f"  ✗ 跳过: 未找到对应的原图")
                    fail_count += 1
                    continue
            
            # 可视化标注
            annotated_path = visualizer.visualize(image_path, result)
            
            # 创建信息图片
            info_path = visualizer.create_info_image(result)
            
            print(f"  ✓ 成功")
            print(f"    标注图片: {Path(annotated_path).name}")
            print(f"    信息图片: {Path(info_path).name}")
            success_count += 1
            
        except Exception as e:
            print(f"  ✗ 失败: {e}")
            fail_count += 1
        
        print()
    
    print("=" * 60)
    print("批量可视化完成")
    print("=" * 60)
    print(f"总计: {len(json_files)} 个文件")
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print(f"可视化结果保存至: {output_dir}")
    print("=" * 60)


def main():
    """主函数"""
    # 如果没有参数，自动批量处理 outputs 目录
    if len(sys.argv) < 2:
        print("未指定参数，将自动批量可视化 outputs 目录下的所有分析结果\n")
        batch_visualize_outputs()
        return
    
    # 单个文件处理模式
    if len(sys.argv) < 3:
        print("=" * 60)
        print("书法单字分析结果可视化工具")
        print("=" * 60)
        print("\n用法:")
        print("  python visualize_analysis.py <图片路径> <JSON结果路径> [输出路径]")
        print("\n示例:")
        print("  python visualize_analysis.py 永.png outputs/永_analysis.json")
        print("  python visualize_analysis.py 永.png outputs/永_analysis.json output.png")
        print("=" * 60)
        sys.exit(1)
    
    # 解析参数
    image_path = sys.argv[1]
    json_path = sys.argv[2]
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"✗ 错误: 图片文件不存在 - {image_path}")
        sys.exit(1)
    
    if not os.path.exists(json_path):
        print(f"✗ 错误: JSON文件不存在 - {json_path}")
        sys.exit(1)
    
    try:
        # 创建可视化器
        visualizer = AnalysisVisualizer()
        
        # 加载分析结果
        result = visualizer.load_analysis_result(json_path)
        
        # 可视化标注
        annotated_path = visualizer.visualize(image_path, result, output_path)
        
        # 创建信息图片
        info_path = visualizer.create_info_image(result)
        
        print("\n" + "=" * 60)
        print("可视化完成！")
        print("=" * 60)
        print(f"标注图片: {annotated_path}")
        print(f"信息图片: {info_path}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
