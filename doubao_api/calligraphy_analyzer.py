#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
书法单字分析工具 - 使用豆包视觉理解模型分析书法单字
功能：
1. 自动调整图片大小（确保边长>300px）
2. 使用豆包视觉模型分析单字结构
3. 返回1-5个关键坐标点及临摹注意事项
4. 保存分析结果为JSON格式
"""

import os
import sys
import json
import base64
import time
from datetime import datetime
from pathlib import Path
from PIL import Image
from openai import OpenAI
from dotenv import load_dotenv


class CalligraphyAnalyzer:
    """书法单字分析器"""
    
    def __init__(self):
        """初始化分析器"""
        # 加载环境变量
        load_dotenv()
        
        # 获取API配置
        self.api_key = os.getenv("ARK_API_KEY")
        self.base_url = os.getenv("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        self.vision_model = os.getenv("ARK_VISION_MODEL", "doubao-1.5-vision-pro-32k-250115")
        
        if not self.api_key:
            raise ValueError("未找到 ARK_API_KEY，请检查 .env 文件")
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
        
        print(f"✓ 豆包视觉模型初始化成功: {self.vision_model}")
    
    def resize_image_if_needed(self, image_path):
        """
        检查并调整图片大小，确保边长大于300px
        
        Args:
            image_path: 输入图片路径
            
        Returns:
            调整后的图片对象和实际路径
        """
        img = Image.open(image_path)
        width, height = img.size
        
        print(f"原始图片尺寸: {width}x{height}px")
        
        # 检查是否需要调整大小
        min_side = min(width, height)
        
        if min_side < 300:
            # 计算缩放比例
            scale = 300 / min_side
            new_width = int(width * scale)
            new_height = int(height * scale)
            
            # 调整图像大小
            img = img.resize((new_width, new_height), Image.LANCZOS)
            print(f"✓ 图片已调整至: {new_width}x{new_height}px")
        else:
            print(f"✓ 图片尺寸符合要求，无需调整")
        
        return img
    
    def image_to_base64(self, image):
        """
        将PIL图像转换为base64编码
        
        Args:
            image: PIL Image对象
            
        Returns:
            base64编码的字符串
        """
        import io
        
        # 将图像保存到字节流
        buffer = io.BytesIO()
        image.save(buffer, format='PNG')
        buffer.seek(0)
        
        # 编码为base64
        img_base64 = base64.b64encode(buffer.read()).decode('utf-8')
        return img_base64
    
    def analyze_character(self, image_path, character_name=None):
        """
        分析书法单字
        
        Args:
            image_path: 图片路径
            character_name: 字的名称（可选）
            
        Returns:
            分析结果字典
        """
        print(f"\n开始分析: {image_path}")
        
        # 1. 调整图片大小
        img = self.resize_image_if_needed(image_path)
        
        # 2. 转换为base64
        img_base64 = self.image_to_base64(img)
        
        # 3. 构建提示词
        prompt = """请仔细分析这个书法单字，并提供以下信息：

1. 根据这个字的复杂程度，标注1-5个关键位置的坐标点（简单的字1-2个点，复杂的字3-5个点）
2. 对每个坐标点，说明在临摹时需要注意的事项

要求：
- 坐标以图片左上角为原点(0,0)，单位为像素
- 坐标格式为相对坐标，x和y的值都在0-1之间（例如图片中心点为(0.5, 0.5)）
- 标注的位置应该是临摹时需要特别注意的关键点，如：笔画交叉点、重要转折点、结构关键点等
- 每个点的注意事项要具体且实用，帮助初学者临摹

请严格按照以下JSON格式返回（不要有任何其他文字说明）：
{
    "character": "字的名称",
    "complexity": "简单/中等/复杂",
    "keypoints": [
        {
            "id": 1,
            "x": 0.5,
            "y": 0.3,
            "description": "这是什么位置",
            "tips": "临摹时需要注意什么"
        }
    ],
    "overall_tips": "整体临摹建议"
}"""
        
        try:
            # 4. 调用视觉理解模型
            print("正在调用豆包视觉理解模型...")
            
            response = self.client.chat.completions.create(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{img_base64}"
                                }
                            },
                            {
                                "type": "text",
                                "text": prompt
                            }
                        ]
                    }
                ],
                temperature=0.7,
            )
            
            # 5. 解析响应
            content = response.choices[0].message.content
            print(f"\n模型返回内容:\n{content}\n")
            
            # 尝试解析JSON
            # 移除可能的markdown代码块标记
            content = content.strip()
            if content.startswith("```json"):
                content = content[7:]
            elif content.startswith("```"):
                content = content[3:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            result = json.loads(content)
            
            # 6. 添加元数据
            result["metadata"] = {
                "image_path": str(image_path),
                "image_size": f"{img.size[0]}x{img.size[1]}",
                "analysis_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "model": self.vision_model
            }
            
            if character_name:
                result["character"] = character_name
            
            print(f"✓ 分析完成，找到 {len(result['keypoints'])} 个关键点")
            
            return result
            
        except json.JSONDecodeError as e:
            print(f"✗ JSON解析失败: {e}")
            print(f"原始内容: {content}")
            raise
        except Exception as e:
            print(f"✗ 分析失败: {e}")
            raise
    
    def save_result(self, result, output_path=None):
        """
        保存分析结果为JSON文件
        
        Args:
            result: 分析结果字典
            output_path: 输出文件路径（可选）
            
        Returns:
            保存的文件路径
        """
        if output_path is None:
            # 创建outputs目录
            output_dir = Path(__file__).parent / "outputs"
            output_dir.mkdir(exist_ok=True)
            
            # 生成文件名
            character = result.get("character", "unknown")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"{character}_analysis_{timestamp}.json"
        
        # 保存JSON
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"✓ 结果已保存至: {output_path}")
        return output_path
    
    def analyze_and_save(self, image_path, character_name=None, output_path=None):
        """
        分析书法单字并保存结果
        
        Args:
            image_path: 图片路径
            character_name: 字的名称（可选）
            output_path: 输出文件路径（可选）
            
        Returns:
            分析结果和保存路径
        """
        result = self.analyze_character(image_path, character_name)
        saved_path = self.save_result(result, output_path)
        return result, saved_path


def batch_process_characters_test():
    """批量处理 characters_test 目录下的所有图片"""
    # 获取 characters_test 目录路径
    script_dir = Path(__file__).parent
    input_dir = script_dir / "characters_test"
    output_dir = script_dir / "outputs"
    
    if not input_dir.exists():
        print(f"✗ 错误: characters_test 目录不存在 - {input_dir}")
        sys.exit(1)
    
    # 查找所有图片文件
    image_extensions = ['.png', '.jpg', '.jpeg', '.bmp', '.gif']
    image_files = []
    
    for ext in image_extensions:
        image_files.extend(input_dir.glob(f"*{ext}"))
        image_files.extend(input_dir.glob(f"*{ext.upper()}"))
    
    # 去重（Windows系统不区分大小写，会重复匹配）
    image_files = list(set(image_files))
    
    # 排除 resize_image.py
    image_files = [f for f in image_files if f.suffix.lower() in image_extensions]
    
    if not image_files:
        print(f"✗ 错误: 在 {input_dir} 中未找到图片文件")
        sys.exit(1)
    
    print("=" * 60)
    print("批量书法单字分析 - 使用豆包视觉理解模型")
    print("=" * 60)
    print(f"输入目录: {input_dir}")
    print(f"输出目录: {output_dir}")
    print(f"找到 {len(image_files)} 个图片文件")
    print("=" * 60)
    print()
    
    # 确保输出目录存在
    output_dir.mkdir(exist_ok=True)
    
    # 创建分析器
    analyzer = CalligraphyAnalyzer()
    
    # 统计信息
    success_count = 0
    fail_count = 0
    
    # 批量处理
    for i, img_file in enumerate(image_files, 1):
        character_name = img_file.stem
        output_file = output_dir / f"{character_name}_analysis.json"
        
        print(f"[{i}/{len(image_files)}] 处理: {character_name}")
        print(f"  文件: {img_file.name}")
        
        try:
            # 分析并保存
            result, saved_path = analyzer.analyze_and_save(
                image_path=str(img_file),
                character_name=character_name,
                output_path=str(output_file)
            )
            
            success_count += 1
            
            # 打印结果摘要
            print(f"  ✓ 成功: {result.get('complexity', '未知')} - {len(result.get('keypoints', []))}个关键点")
            print(f"  保存至: {saved_path.name}")
            
        except Exception as e:
            fail_count += 1
            print(f"  ✗ 失败: {e}")
        
        print()
        
        # API调用延迟，避免限流
        if i < len(image_files):
            delay = 1.5
            print(f"  等待 {delay} 秒...\n")
            time.sleep(delay)
    
    # 打印总结
    print("=" * 60)
    print("批量处理完成")
    print("=" * 60)
    print(f"总计: {len(image_files)} 个文件")
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    print(f"成功率: {success_count/len(image_files)*100:.1f}%")
    print(f"结果保存至: {output_dir}")
    print("=" * 60)


def main():
    """主函数"""
    # 如果没有参数，自动批量处理 characters_test 目录
    if len(sys.argv) < 2:
        print("未指定参数，将自动批量处理 characters_test 目录下的所有图片\n")
        batch_process_characters_test()
        return
    
    # 单个文件处理模式
    print("=" * 60)
    print("书法单字分析工具 - 使用豆包视觉理解模型")
    print("=" * 60)
    
    # 解析参数
    image_path = sys.argv[1]
    character_name = sys.argv[2] if len(sys.argv) > 2 else None
    output_path = sys.argv[3] if len(sys.argv) > 3 else None
    
    # 检查文件是否存在
    if not os.path.exists(image_path):
        print(f"✗ 错误: 文件不存在 - {image_path}")
        sys.exit(1)
    
    try:
        # 创建分析器并执行分析
        analyzer = CalligraphyAnalyzer()
        result, saved_path = analyzer.analyze_and_save(
            image_path, 
            character_name, 
            output_path
        )
        
        # 打印分析结果摘要
        print("\n" + "=" * 60)
        print("分析结果摘要")
        print("=" * 60)
        print(f"字: {result.get('character', '未知')}")
        print(f"复杂度: {result.get('complexity', '未知')}")
        print(f"关键点数量: {len(result.get('keypoints', []))}")
        print(f"\n关键点详情:")
        for kp in result.get('keypoints', []):
            print(f"  点{kp['id']}: ({kp['x']:.2f}, {kp['y']:.2f}) - {kp['description']}")
            print(f"       提示: {kp['tips']}")
        print(f"\n整体建议: {result.get('overall_tips', '')}")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n✗ 程序执行失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
