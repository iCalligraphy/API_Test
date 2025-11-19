#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
豆包大模型API测试程序
测试豆包API的基本功能：非流式调用和流式调用
"""

import os
from openai import OpenAI
from dotenv import load_dotenv


class DoubaoClient:
    """豆包大模型API客户端"""
    
    def __init__(self):
        """初始化豆包客户端，从环境变量读取配置"""
        # 加载环境变量
        load_dotenv()
        
        # 获取配置
        self.api_key = os.environ.get("ARK_API_KEY")
        self.base_url = os.environ.get("ARK_BASE_URL", "https://ark.cn-beijing.volces.com/api/v3")
        self.model = os.environ.get("ARK_MODEL", "doubao-1-5-thinking-pro-250415")
        
        # 验证配置
        if not self.api_key:
            raise ValueError("ARK_API_KEY 未设置，请在.env文件中配置")
        
        # 初始化OpenAI客户端
        self.client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
    
    def chat(self, messages: list, stream: bool = False):
        """
        发送对话请求
        
        Args:
            messages: 对话消息列表，格式：[{"role": "user", "content": "..."}]
            stream: 是否使用流式返回
            
        Returns:
            非流式：返回完整响应文本
            流式：返回生成器对象
        """
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                stream=stream,
            )
            
            if stream:
                return response
            else:
                return response.choices[0].message.content
                
        except Exception as e:
            print(f"API调用错误: {e}")
            return None


def test_standard_chat():
    """测试非流式对话"""
    print("=" * 60)
    print("测试1: 非流式对话")
    print("=" * 60)
    
    client = DoubaoClient()
    
    messages = [
        {"role": "system", "content": "你是一个古籍书法专家助手"},
        {"role": "user", "content": "请简单介绍一下王羲之的《兰亭序》"}
    ]
    
    print("\n发送请求中...")
    response = client.chat(messages, stream=False)
    
    if response:
        print("\n回复内容：")
        print(response)
    
    print("\n" + "=" * 60)


def test_streaming_chat():
    """测试流式对话"""
    print("=" * 60)
    print("测试2: 流式对话")
    print("=" * 60)
    
    client = DoubaoClient()
    
    messages = [
        {"role": "system", "content": "你是一个古籍书法专家助手"},
        {"role": "user", "content": "请用三句话介绍楷书的特点"}
    ]
    
    print("\n流式输出中：")
    print("-" * 60)
    
    stream = client.chat(messages, stream=True)
    
    if stream:
        for chunk in stream:
            if chunk.choices and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print()  # 换行
    
    print("-" * 60)
    print("\n" + "=" * 60)


def test_calligraphy_analysis():
    """测试书法分析应用场景"""
    print("=" * 60)
    print("测试3: 书法分析应用")
    print("=" * 60)
    
    client = DoubaoClient()
    
    # 模拟OCR识别结果
    ocr_text = "永和九年，歲在癸丑，暮春之初，會於會稽山陰之蘭亭"
    
    messages = [
        {"role": "system", "content": "你是一个古籍文本分析专家"},
        {"role": "user", "content": f"这是从古籍中OCR识别出的文字：\n\n{ocr_text}\n\n请分析：\n1. 这段文字出自哪部作品？\n2. 简要说明其文化价值"}
    ]
    
    print("\n发送请求中...")
    response = client.chat(messages, stream=False)
    
    if response:
        print("\n分析结果：")
        print(response)
    
    print("\n" + "=" * 60)


def main():
    """主函数"""
    print("\n豆包大模型API测试程序")
    print("开始测试...\n")
    
    try:
        # 测试1: 非流式对话
        test_standard_chat()
        
        # 测试2: 流式对话
        test_streaming_chat()
        
        # 测试3: 书法分析应用
        test_calligraphy_analysis()
        
        print("\n✓ 所有测试完成！")
        
    except ValueError as e:
        print(f"\n✗ 配置错误: {e}")
        print("请检查.env文件中的API配置")
    except Exception as e:
        print(f"\n✗ 测试失败: {e}")


if __name__ == "__main__":
    main()
