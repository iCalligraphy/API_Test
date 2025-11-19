# 豆包大模型 API 测试

本文件夹用于豆包（Doubao）大模型API的测试和应用开发。

## 简介

豆包是字节跳动推出的AI大模型，通过火山方舟平台提供API服务。本文件夹包含豆包API的测试代码和示例应用。

## 配置说明

### 1. 获取API密钥

1. 访问[火山方舟控制台](https://console.volcengine.com/ark)
2. 创建推理接入点，获取接入点ID
3. 生成API Key

### 2. 配置环境变量

在根目录的`.env`文件中配置豆包API密钥：

```bash
# 豆包 API Key
ARK_API_KEY="your-ark-api-key-here"

# API Base URL（可选，默认值）
ARK_BASE_URL="https://ark.cn-beijing.volces.com/api/v3"

# 模型ID（推理接入点ID）
ARK_MODEL="doubao-1-5-thinking-pro-250415"
```

## 使用示例

### 基础对话测试

```python
import os
from openai import OpenAI

# 初始化客户端
client = OpenAI(
    base_url=os.environ.get("ARK_BASE_URL"),
    api_key=os.environ.get("ARK_API_KEY"),
)

# 非流式调用
completion = client.chat.completions.create(
    model=os.environ.get("ARK_MODEL"),
    messages=[
        {"role": "system", "content": "你是一个古籍书法专家助手"},
        {"role": "user", "content": "请介绍一下王羲之的书法特点"}
    ],
)
print(completion.choices[0].message.content)
```

### 流式对话测试

```python
# 流式调用
stream = client.chat.completions.create(
    model=os.environ.get("ARK_MODEL"),
    messages=[
        {"role": "system", "content": "你是一个古籍书法专家助手"},
        {"role": "user", "content": "请介绍一下王羲之的书法特点"}
    ],
    stream=True,
)

for chunk in stream:
    if chunk.choices:
        print(chunk.choices[0].delta.content, end="")
```

## API 文档

详细的API文档请参考：
- [豆包API官方文档](../Docs/豆包API.md)
- [火山方舟官方文档](https://www.volcengine.com/docs/82379/1263512)

## 应用场景

在古籍书法项目中，豆包API可用于：

1. **字体分析** - 分析书法字体特点和风格
2. **内容理解** - 理解古籍文本内容和含义
3. **智能问答** - 回答关于古籍和书法的问题
4. **文本生成** - 生成书法练习指导和评价
5. **OCR后处理** - 对OCR识别结果进行校对和优化

## 注意事项

- 使用前请确保已在火山方舟平台开通服务
- API调用会产生费用，请注意用量控制
- 妥善保管API密钥，不要提交到版本控制系统
