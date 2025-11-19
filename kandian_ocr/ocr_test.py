#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
古籍OCR识别测试程序
读取images文件夹中的字帖图片，调用API进行文字识别，并将结果保存到outputs文件夹
"""

import os
import base64
import json
import requests
from pathlib import Path
from typing import Dict, Any, Optional


class OCRClient:
    """古籍OCR API客户端"""
    
    def __init__(self, token: str, email: str, api_url: str = "https://ocr.kandianguji.com/ocr_api"):
        """
        初始化OCR客户端
        
        Args:
            token: API Token
            email: 注册邮箱或手机号
            api_url: API接口地址
        """
        self.token = token
        self.email = email
        self.api_url = api_url
    
    def image_to_base64(self, image_path: str) -> str:
        """
        将图片文件转换为base64编码
        
        Args:
            image_path: 图片文件路径
            
        Returns:
            base64编码的字符串
        """
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_str = base64.b64encode(image_data).decode('utf-8')
        return base64_str
    
    def recognize_text(self, image_path: str, **kwargs) -> Dict[str, Any]:
        """
        识别图片中的文字
        
        Args:
            image_path: 图片文件路径
            **kwargs: 其他API参数（如det_mode, version等）
            
        Returns:
            API响应结果
        """
        # 将图片转换为base64
        image_base64 = self.image_to_base64(image_path)
        
        # 准备请求参数
        params = {
            'token': self.token,
            'email': self.email,
            'image': image_base64,
            **kwargs
        }
        
        # 发送POST请求
        try:
            response = requests.post(self.api_url, json=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"API请求失败: {e}")
            return {'message': 'error', 'info': str(e)}
    
    def extract_text(self, api_response: Dict[str, Any]) -> str:
        """
        从API响应中提取识别的文字内容
        
        Args:
            api_response: API响应结果
            
        Returns:
            提取的文字内容
        """
        if api_response.get('message') != 'success':
            return f"识别失败: {api_response.get('info', '未知错误')}"
        
        data = api_response.get('data', {})
        texts = data.get('texts', [])
        
        # 提取所有文本行的内容
        result_lines = []
        for text_line in texts:
            if isinstance(text_line, dict):
                text = text_line.get('text', '')
            else:
                text = str(text_line)
            if text:
                result_lines.append(text)
        
        return '\n'.join(result_lines)


def save_result(output_dir: Path, image_name: str, text_result: str, 
                api_response: Optional[Dict[str, Any]] = None):
    """
    保存识别结果到文件
    
    Args:
        output_dir: 输出目录
        image_name: 图片文件名（不含扩展名）
        text_result: 识别的文字内容
        api_response: 完整的API响应（可选）
    """
    # 保存纯文本结果
    txt_file = output_dir / f"{image_name}_result.txt"
    with open(txt_file, 'w', encoding='utf-8') as f:
        f.write(text_result)
    print(f"✓ 文本结果已保存: {txt_file}")
    
    # 保存完整JSON结果（如果提供了）
    if api_response:
        json_file = output_dir / f"{image_name}_result.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(api_response, f, ensure_ascii=False, indent=2)
        print(f"✓ JSON结果已保存: {json_file}")


def main():
    """主函数"""
    # 获取项目根目录
    project_root = Path(__file__).parent
    
    # 设置路径
    images_dir = project_root / 'images'
    outputs_dir = project_root / 'outputs'
    
    # 确保输出目录存在
    outputs_dir.mkdir(exist_ok=True)
    
    # 从环境变量或.env文件读取配置
    token = os.getenv('Token', '').strip('"').strip("'")
    email = os.getenv('Email', '').strip('"').strip("'")
    
    # 如果环境变量中没有，尝试从.env文件读取
    if not token or not email:
        env_file = project_root / '.env'
        if env_file.exists():
            with open(env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line.startswith('Token='):
                        token = line.split('=', 1)[1].strip('"').strip("'")
                    elif line.startswith('Email='):
                        email = line.split('=', 1)[1].strip('"').strip("'")
    
    # 如果还是没有，提示用户输入
    if not token:
        token = input("请输入API Token: ").strip()
    if not email:
        email = input("请输入注册邮箱或手机号: ").strip()
    
    if not token or not email:
        print("错误: 必须提供Token和Email")
        return
    
    # 创建OCR客户端
    ocr_client = OCRClient(token=token, email=email)
    
    # 获取所有图片文件
    image_extensions = {'.png', '.jpg', '.jpeg', '.bmp', '.gif', '.tiff', '.webp'}
    image_files = [f for f in images_dir.iterdir() 
                   if f.is_file() and f.suffix.lower() in image_extensions]
    
    if not image_files:
        print(f"错误: 在 {images_dir} 目录中未找到图片文件")
        return
    
    print(f"找到 {len(image_files)} 个图片文件，开始识别...\n")
    
    # 处理每个图片
    for image_file in image_files:
        print(f"\n处理图片: {image_file.name}")
        print("-" * 50)
        
        try:
            # 调用API识别
            api_response = ocr_client.recognize_text(
                str(image_file),
                det_mode='auto',  # 自动识别排版
                version='v2',     # 使用最新版本
                return_position=True  # 返回位置信息
            )
            
            # 提取文字内容
            text_result = ocr_client.extract_text(api_response)
            
            # 保存结果
            image_name = image_file.stem  # 不含扩展名的文件名
            save_result(outputs_dir, image_name, text_result, api_response)
            
            # 显示识别结果预览
            if text_result and not text_result.startswith("识别失败"):
                preview = text_result[:200] if len(text_result) > 200 else text_result
                print(f"\n识别结果预览:\n{preview}")
                if len(text_result) > 200:
                    print("... (完整结果已保存到文件)")
            
        except Exception as e:
            print(f"✗ 处理失败: {e}")
            # 保存错误信息
            error_file = outputs_dir / f"{image_file.stem}_error.txt"
            with open(error_file, 'w', encoding='utf-8') as f:
                f.write(f"处理失败: {str(e)}")
    
    print(f"\n\n所有图片处理完成！结果已保存到 {outputs_dir} 目录")


if __name__ == '__main__':
    main()

