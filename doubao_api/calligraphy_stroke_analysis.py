#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
书法汉字笔迹流程图生成工具
使用豆包大模型视觉API分析书法汉字，并通过图像生成API生成笔迹流程图

注意事项：
1. 必须使用支持视觉输入的模型（如 doubao-1.5-vision-pro-32k-250115）
2. 必须配置图像生成模型（如 doubao-seedream-4-0-250828）
3. 在 .env 文件中配置：
   ARK_API_KEY="your-api-key"
   ARK_VISION_MODEL="doubao-1.5-vision-pro-32k-250115"  # 可选
   ARK_IMAGE_MODEL="doubao-seedream-4-0-250828"  # 可选

可用的视觉模型：
- doubao-1.5-vision-pro-250328
- doubao-1.5-vision-pro-32k-250115 (推荐，更大上下文)

可用的图像生成模型：
- doubao-seedream-4-0-250828
"""

import os
import base64
import requests
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from PIL import Image


class CalligraphyStrokeAnalyzer:
    """书法笔迹分析器，用于生成汉字笔迹流程图"""
    
    def __init__(self, vision_model: str = None, image_model: str = None):
        """初始化分析器，从环境变量读取配置
        
        Args:
            vision_model: 视觉模型名称，默认使用 doubao-1.5-vision-pro-32k-250115
            image_model: 图像生成模型名称，默认使用 doubao-seedream-4-0-250828
        """
        # 加载环境变量
        load_dotenv()
        
        # 获取配置
        self.api_key = os.environ.get("ARK_API_KEY")
        self.base_url = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        
        # 使用视觉模型，优先使用参数，其次环境变量，最后默认值
        if vision_model:
            self.vision_model = vision_model
        else:
            self.vision_model = os.environ.get("ARK_VISION_MODEL", "doubao-1.5-vision-pro-32k-250115")
        
        # 使用图像生成模型
        if image_model:
            self.image_model = image_model
        else:
            self.image_model = os.environ.get("ARK_IMAGE_MODEL", "doubao-seedream-4-0-250828")
        
        # 验证配置
        if not self.api_key:
            raise ValueError("ARK_API_KEY 未设置，请在.env文件中配置")
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
    
    def encode_image_to_base64(self, image_path: str) -> str:
        """
        将图片文件编码为base64字符串
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            base64编码的图片字符串
        """
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
    
    def analyze_stroke_with_vision(self, image_path: str, character_name: str = None) -> str:
        """
        使用视觉模型分析书法汉字笔迹结构
        
        Args:
            image_path: 书法汉字图片路径
            character_name: 汉字名称（可选）
            
        Returns:
            笔迹结构分析描述（用于生成图片提示词）
        """
        # 编码图片
        base64_image = self.encode_image_to_base64(image_path)
        image_url = f"data:image/png;base64,{base64_image}"
        
        # 构建提示词
        char_info = f"'{character_name}'字" if character_name else "这个书法汉字"
        
        prompt = f"""请分析{char_info}的笔迹结构，用简洁的语言描述：

1. 有哪些笔画（如：横、竖、撇、捺、点等）
2. 正确的笔顺是什么
3. 每一笔的书写特点（起笔、行笔、收笔）
4. 整体书法风格特征

请用1-2段话概括，简洁明了。"""

        try:
            # 调用视觉API
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一位专业的书法教师，擅长分析书法作品的笔画结构。"
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": image_url
                                }
                            }
                        ]
                    }
                ],
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            print(f"视觉分析API调用错误: {e}")
            return None
    
    def generate_stroke_diagram_image(self, analysis_text: str, character_name: str = None) -> bytes:
        """
        使用图像生成API创建笔迹流程图
        
        Args:
            analysis_text: 笔迹分析文本
            character_name: 汉字名称（可选）
            
        Returns:
            生成的图片二进制数据
        """
        # 构建图片生成提示词
        char_info = f"'{character_name}'字" if character_name else "这个书法汉字"
        
        prompt = f"""创建一张书法教学图解，展示{char_info}的笔画流程：

要求：
- 白色背景，清晰简洁
- 上方展示完整的汉字
- 下方用多个步骤图展示每一笔的书写过程
- 用数字标注笔顺（1、2、3...）
- 用箭头标注笔画方向
- 标注起笔、行笔、收笔的位置
- 整体布局清晰，适合教学使用
- 采用中国传统书法教学图解风格

笔画分析：
{analysis_text}

请生成专业的书法笔迹流程图。"""
        
        try:
            # 调用图像生成API
            url = f"{self.base_url}/images/generations"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "model": self.image_model,
                "prompt": prompt,
                "response_format": "url",
                "size": "1K",
                "stream": False,
                "watermark": False
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            response.raise_for_status()
            
            result = response.json()
            
            # 获取图片URL
            if 'data' in result and len(result['data']) > 0:
                image_url = result['data'][0]['url']
                
                # 下载图片
                img_response = requests.get(image_url, timeout=30)
                img_response.raise_for_status()
                
                return img_response.content
            else:
                print(f"图像生成失败: 响应中没有图片数据")
                return None
                
        except Exception as e:
            print(f"图像生成API调用错误: {e}")
            return None
    
    def combine_images(self, original_image_path: str, diagram_image_data: bytes, character_name: str) -> str:
        """
        将原始汉字图片和生成的笔迹流程图上下组合
        
        Args:
            original_image_path: 原始汉字图片路径
            diagram_image_data: 生成的笔迹流程图二进制数据
            character_name: 汉字名称
            
        Returns:
            组合后的图片保存路径
        """
        try:
            # 打开原始图片
            original_img = Image.open(original_image_path)
            
            # 打开生成的流程图
            diagram_img = Image.open(BytesIO(diagram_image_data))
            
            # 调整原始图片大小（如果太大）
            max_width = 800
            if original_img.width > max_width:
                ratio = max_width / original_img.width
                new_size = (max_width, int(original_img.height * ratio))
                original_img = original_img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 调整流程图宽度与原图一致
            if diagram_img.width != original_img.width:
                ratio = original_img.width / diagram_img.width
                new_size = (original_img.width, int(diagram_img.height * ratio))
                diagram_img = diagram_img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 创建新画布（上下组合）
            total_height = original_img.height + diagram_img.height + 20  # 20px间距
            combined_img = Image.new('RGB', (original_img.width, total_height), 'white')
            
            # 粘贴原始图片在上方
            combined_img.paste(original_img, (0, 0))
            
            # 粘贴流程图在下方
            combined_img.paste(diagram_img, (0, original_img.height + 20))
            
            # 保存组合图片
            output_dir = Path(original_image_path).parent.parent / "outputs"
            output_dir.mkdir(exist_ok=True)
            output_path = output_dir / f"{character_name}_stroke_diagram.png"
            combined_img.save(output_path, 'PNG')
            
            return str(output_path)
            
        except Exception as e:
            print(f"图片组合失败: {e}")
            return None
    
    def batch_analyze_characters(self, characters_dir: str) -> dict:
        """
        批量分析characters_test目录下的所有汉字并生成笔迹流程图
        
        Args:
            characters_dir: 汉字图片目录路径
            
        Returns:
            结果字典 {文件名: 输出图片路径}
        """
        results = {}
        characters_path = Path(characters_dir)
        
        # 支持的图片格式
        image_extensions = ['.png', '.jpg', '.jpeg']
        
        # 遍历目录下的所有图片
        for image_file in characters_path.iterdir():
            if image_file.suffix.lower() in image_extensions:
                character_name = image_file.stem  # 使用文件名作为字名
                print(f"\n正在处理 '{character_name}' 字...")
                print("=" * 60)
                
                # 步骤1: 分析笔迹结构
                print("[1/3] 分析笔迹结构...")
                analysis = self.analyze_stroke_with_vision(
                    str(image_file), 
                    character_name
                )
                
                if not analysis:
                    print(f"✗ '{character_name}' 字分析失败")
                    continue
                
                print(f"分析结果: {analysis[:100]}...")  # 只显示前100字符
                
                # 步骤2: 生成笔迹流程图
                print("[2/3] 生成笔迹流程图...")
                diagram_data = self.generate_stroke_diagram_image(
                    analysis,
                    character_name
                )
                
                if not diagram_data:
                    print(f"✗ '{character_name}' 字流程图生成失败")
                    continue
                
                # 步骤3: 组合图片
                print("[3/3] 组合图片...")
                output_path = self.combine_images(
                    str(image_file),
                    diagram_data,
                    character_name
                )
                
                if output_path:
                    results[character_name] = output_path
                    print(f"✓ 成功！输出路径: {output_path}")
                    print("=" * 60)
                else:
                    print(f"✗ '{character_name}' 字图片组合失败")
        
        return results
    
    def save_results_summary(self, results: dict, output_file: str):
        """
        保存生成结果摘要到文件
        
        Args:
            results: 结果字典 {字名: 输出图片路径}
            output_file: 输出文件路径
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# 书法汉字笔迹流程图生成报告\n\n")
            f.write(f"共生成 {len(results)} 个汉字的笔迹流程图\n\n")
            f.write("=" * 80 + "\n\n")
            
            for character_name, output_path in results.items():
                f.write(f"## {character_name} 字\n")
                f.write(f"输出图片: {output_path}\n\n")
        
        print(f"\n✓ 结果摘要已保存到: {output_file}")


def main():
    """主函数 - 生成书法笔迹流程图"""
    print("\n书法汉字笔迹流程图生成工具")
    print("=" * 60)
    
    try:
        # 创建分析器
        print("\n正在初始化...")
        analyzer = CalligraphyStrokeAnalyzer()
        print(f"视觉模型: {analyzer.vision_model}")
        print(f"图像生成模型: {analyzer.image_model}")
        
        # 设置characters_test目录路径
        script_dir = Path(__file__).parent
        characters_dir = script_dir / "characters_test"
        
        if not characters_dir.exists():
            print(f"\n✗ 目录不存在: {characters_dir}")
            print("请确保 characters_test 目录存在且包含书法汉字图片")
            return
        
        # 批量生成笔迹流程图
        print(f"\n开始处理 {characters_dir} 目录下的书法汉字...\n")
        results = analyzer.batch_analyze_characters(str(characters_dir))
        
        # 保存结果
        if results:
            output_file = script_dir / "stroke_diagram_results.txt"
            analyzer.save_results_summary(results, str(output_file))
            print(f"\n✓ 成功生成 {len(results)} 个汉字的笔迹流程图！")
        else:
            print("\n✗ 没有成功生成任何笔迹流程图")
        
    except ValueError as e:
        print(f"\n✗ 配置错误: {e}")
        print("请检查.env文件中的API配置")
    except Exception as e:
        print(f"\n✗ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
