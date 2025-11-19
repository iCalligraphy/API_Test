#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
书法汉字结构分析图生成工具
使用豆包大模型视觉API分析书法汉字的结构组成，并通过图像编辑API在原图上添加结构标注

注意事项：
1. 必须使用支持视觉输入的模型（如 doubao-1.5-vision-pro-32k-250115）
2. 必须配置图像编辑模型（如 doubao-seededit-3-0-i2i-250628）
3. 在 .env 文件中配置：
   ARK_API_KEY="your-api-key"
   ARK_VISION_MODEL="doubao-1.5-vision-pro-32k-250115"  # 可选
   ARK_IMAGE_MODEL="doubao-seededit-3-0-i2i-250628"  # 可选

可用的视觉模型：
- doubao-1.5-vision-pro-250328
- doubao-1.5-vision-pro-32k-250115 (推荐，更大上下文)

可用的图像编辑模型：
- doubao-seededit-3-0-i2i-250628
"""

import os
import base64
import requests
from io import BytesIO
from openai import OpenAI
from dotenv import load_dotenv
from pathlib import Path
from PIL import Image


class CalligraphyStructureAnalyzer:
    """书法结构分析器，用于生成汉字结构分析图"""
    
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
        
        # 使用图像编辑模型
        if image_model:
            self.image_model = image_model
        else:
            self.image_model = os.environ.get("ARK_IMAGE_MODEL", "doubao-seededit-3-0-i2i-250628")
        
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
    
    def analyze_structure_with_vision(self, image_path: str, character_name: str = None) -> str:
        """
        使用视觉模型分析书法汉字结构组成
        
        Args:
            image_path: 书法汉字图片路径
            character_name: 汉字名称（可选）
            
        Returns:
            结构组成分析描述（用于生成图片提示词）
        """
        # 编码图片
        base64_image = self.encode_image_to_base64(image_path)
        image_url = f"data:image/png;base64,{base64_image}"
        
        # 构建提示词
        char_info = f"'{character_name}'字" if character_name else "这个书法汉字"
        
        prompt = f"""请分析{char_info}的结构组成，用简洁的语言描述：

1. 汉字的整体结构类型（如：左右结构、上下结构、左中右结构、上中下结构、半包围结构、全包围结构、独体字等）
2. 主要组成部分（如：偏旁部首、主体部分等）
3. 各部分之间的位置关系和比例关系
4. 各部分的高低、宽窄、大小关系
5. 结构的穿插避让关系
6. 整体重心和平衡特点

请用2-3段话概括，详细描述各部分的结构关系，便于用箭头标注。"""

        try:
            # 调用视觉API
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一位专业的书法教师，擅长分析汉字的结构组成和空间布局。"
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
    
    def generate_structure_diagram_image(self, analysis_text: str, image_path: str, character_name: str = None) -> bytes:
        """
        使用图像编辑API在原图上添加结构分析标注
        
        Args:
            analysis_text: 结构分析文本
            image_path: 原始书法汉字图片路径
            character_name: 汉字名称（可选）
            
        Returns:
            生成的图片二进制数据
        """
        # 编码原始图片为base64
        base64_image = self.encode_image_to_base64(image_path)
        image_data_url = f"data:image/png;base64,{base64_image}"
        
        # 构建图像编辑提示词
        char_info = f"'{character_name}'字" if character_name else "这个书法汉字"
        
        prompt = f"""【重要】请基于提供的原始书法汉字图片，直接在原图上添加结构分析标注。

核心要求 - 必须严格遵守：
1. **必须使用原始书法汉字图片作为底图** - 不要重新绘制或生成新的汉字
2. **保持原图书法字的完整性和真实性** - 原有的笔画、墨迹、风格必须完全保留
3. **所有标注都添加在原图之上** - 包括箭头、文字说明、辅助线等

标注内容：
- 用不同颜色的半透明边框或高亮区域标识不同的组成部分（如左右、上下等部首）
- 用清晰的彩色箭头标注各部分之间的关系：
  * 双向箭头标注位置和比例关系
  * 单向箭头指示穿插避让关系
  * 箭头旁边用清晰字体标注说明（如"左窄右宽"、"上下均分"、"左伸右让"等）
- 用彩色辅助线（虚线或实线）标注重心、中线、对齐线等关键结构线
- 在适当位置标注各部分的名称（如"偏旁"、"部首"等）
- 在图片角落标注整体结构类型（如"左右结构"等）

视觉风格：
- 标注颜色鲜明但不遮挡原字（使用红色、蓝色、绿色等）
- 文字标注清晰可读，字号适中
- 整体风格符合中国书法教学图解传统
- 白色或浅色背景，确保原书法字清晰可见

结构分析参考：
{analysis_text}

【再次强调】务必直接在原始书法汉字图片上进行标注，不要创建新的汉字图像！"""
        
        try:
            # 调用图像编辑API
            url = f"{self.base_url}/images/generations"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            payload = {
                "model": self.image_model,
                "prompt": prompt,
                "image": image_data_url,  # 传递原始图片
                "response_format": "url",
                "size": "adaptive",  # 自适应原图尺寸
                "guidance_scale": 7.5,  # 引导强度，控制编辑效果
                "watermark": False
                # 注意：图像编辑模型不支持 stream 参数
            }
            
            response = requests.post(url, json=payload, headers=headers, timeout=60)
            
            # 打印详细错误信息以便调试
            if response.status_code != 200:
                print(f"API响应状态码: {response.status_code}")
                print(f"API响应内容: {response.text}")
            
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
        将原始汉字图片和生成的结构分析图上下组合
        
        Args:
            original_image_path: 原始汉字图片路径
            diagram_image_data: 生成的结构分析图二进制数据
            character_name: 汉字名称
            
        Returns:
            组合后的图片保存路径
        """
        try:
            # 打开原始图片
            original_img = Image.open(original_image_path)
            
            # 打开生成的分析图（保持高分辨率）
            diagram_img = Image.open(BytesIO(diagram_image_data))
            
            # 创建输出目录
            output_dir = Path(original_image_path).parent.parent / "outputs"
            output_dir.mkdir(exist_ok=True)
            
            # 单独保存高分辨率结构分析图
            diagram_only_path = output_dir / f"{character_name}_structure_diagram_only.png"
            diagram_img.save(diagram_only_path, 'PNG', optimize=True)
            print(f"  → 结构分析图已保存: {diagram_only_path}")
            
            # 调整原图宽度以匹配分析图（放大原图，保持分析图高分辨率）
            if original_img.width != diagram_img.width:
                ratio = diagram_img.width / original_img.width
                new_size = (diagram_img.width, int(original_img.height * ratio))
                original_img = original_img.resize(new_size, Image.Resampling.LANCZOS)
                print(f"  → 原图已放大至: {new_size[0]}x{new_size[1]}px 以匹配分析图")
            
            # 创建新画布（上下组合）
            total_height = original_img.height + diagram_img.height + 20  # 20px间距
            combined_img = Image.new('RGB', (diagram_img.width, total_height), 'white')
            
            # 粘贴原始图片在上方
            combined_img.paste(original_img, (0, 0))
            
            # 粘贴分析图在下方
            combined_img.paste(diagram_img, (0, original_img.height + 20))
            
            # 保存组合图片
            combined_path = output_dir / f"{character_name}_structure_diagram.png"
            combined_img.save(combined_path, 'PNG', optimize=True)
            
            print(f"  → 组合图片尺寸: {combined_img.width}x{combined_img.height}px")
            
            return str(combined_path)
            
        except Exception as e:
            print(f"图片组合失败: {e}")
            return None
    
    def batch_analyze_characters(self, characters_dir: str) -> dict:
        """
        批量分析characters_test目录下的所有汉字并生成结构分析图
        
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
                
                # 步骤1: 分析结构组成
                print("[1/3] 分析结构组成...")
                analysis = self.analyze_structure_with_vision(
                    str(image_file), 
                    character_name
                )
                
                if not analysis:
                    print(f"✗ '{character_name}' 字结构分析失败")
                    continue
                
                print(f"分析结果: {analysis[:100]}...")  # 只显示前100字符
                
                # 步骤2: 在原图上添加结构标注
                print("[2/3] 在原图上添加结构标注...")
                diagram_data = self.generate_structure_diagram_image(
                    analysis,
                    str(image_file),
                    character_name
                )
                
                if not diagram_data:
                    print(f"✗ '{character_name}' 字结构图生成失败")
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
            f.write("# 书法汉字结构分析图生成报告\n\n")
            f.write(f"共生成 {len(results)} 个汉字的结构分析图\n\n")
            f.write("=" * 80 + "\n\n")
            
            for character_name, output_path in results.items():
                f.write(f"## {character_name} 字\n")
                f.write(f"输出图片: {output_path}\n\n")
        
        print(f"\n✓ 结果摘要已保存到: {output_file}")


def main():
    """主函数 - 生成书法结构分析图"""
    print("\n书法汉字结构分析图生成工具")
    print("=" * 60)
    
    try:
        # 创建分析器
        print("\n正在初始化...")
        analyzer = CalligraphyStructureAnalyzer()
        print(f"视觉模型: {analyzer.vision_model}")
        print(f"图像生成模型: {analyzer.image_model}")
        
        # 设置characters_test目录路径
        script_dir = Path(__file__).parent
        characters_dir = script_dir / "characters_test"
        
        if not characters_dir.exists():
            print(f"\n✗ 目录不存在: {characters_dir}")
            print("请确保 characters_test 目录存在且包含书法汉字图片")
            return
        
        # 批量生成结构分析图
        print(f"\n开始处理 {characters_dir} 目录下的书法汉字...\n")
        results = analyzer.batch_analyze_characters(str(characters_dir))
        
        # 保存结果
        if results:
            output_file = script_dir / "structure_diagram_results.txt"
            analyzer.save_results_summary(results, str(output_file))
            print(f"\n✓ 成功生成 {len(results)} 个汉字的结构分析图！")
        else:
            print("\n✗ 没有成功生成任何结构分析图")
        
    except ValueError as e:
        print(f"\n✗ 配置错误: {e}")
        print("请检查.env文件中的API配置")
    except Exception as e:
        print(f"\n✗ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
