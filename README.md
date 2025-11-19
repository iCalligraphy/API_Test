# API_Test

古籍书法智能识别与分析工具集，集成看典古籍OCR API和豆包大模型API，用于古籍文字识别、单字提取和智能分析。

## 项目结构

```
API_Test/
├── kandian_ocr/          # 看典古籍OCR API测试
│   ├── images/           # 输入：待识别的字帖图片
│   ├── outputs/          # 输出：OCR识别结果
│   ├── characters/       # 输出：提取的单字图片
│   ├── ocr_test.py       # OCR识别测试程序
│   ├── extract_characters.py  # 单字提取程序
│   ├── visualize_ocr.py  # 结果可视化程序
│   └── README.md         # 详细使用说明
│
├── doubao_api/           # 豆包大模型API测试
│   ├── doubao_test.py    # 豆包API测试程序
│   └── README.md         # 详细使用说明
│
├── Docs/                 # API文档
│   ├── 看典古籍OCR API使用文档.md
│   ├── 看点古籍OCR API.md
│   └── 豆包API.md
│
├── .env                  # 环境变量配置（不提交到Git）
├── .env.example          # 环境变量配置示例
└── requirements.txt      # Python依赖
```

## 快速开始

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置API密钥

复制`.env.example`为`.env`，并填入你的API密钥：

```bash
# 看典古籍OCR API
Token="your-kandian-token-here"
Email="your-email-or-phone-here"

# 豆包大模型API
ARK_API_KEY="your-ark-api-key-here"
```

### 3. 使用看典古籍OCR

进入`kandian_ocr/`文件夹，详见该目录下的[README.md](./kandian_ocr/README.md)。

```bash
cd kandian_ocr
python ocr_test.py          # OCR识别
python visualize_ocr.py     # 结果可视化
python extract_characters.py # 单字提取
```

### 4. 使用豆包大模型API

进入`doubao_api/`文件夹，详见该目录下的[README.md](./doubao_api/README.md)。

```bash
cd doubao_api
python doubao_test.py       # 测试豆包API
```

## 功能特性

### 看典古籍OCR

- ✅ 批量识别古籍字帖图片
- ✅ 支持竖排/横排自动识别
- ✅ 文本行和单字坐标信息
- ✅ 识别结果可视化
- ✅ 单字图片自动提取

### 豆包大模型

- ✅ 古籍内容理解与分析
- ✅ 书法字体风格解析
- ✅ OCR结果智能校对
- ✅ 书法知识问答
- ✅ 流式和非流式调用

## API文档

- [看典古籍OCR API使用文档](./Docs/看典古籍OCR%20API使用文档.md)
- [看点古籍OCR API](./Docs/看点古籍OCR%20API.md)
- [豆包API](./Docs/豆包API.md)

## 应用场景

1. **古籍数字化** - 快速将古籍图像转换为可编辑文本
2. **书法练习** - 提取单字图片用于书法学习
3. **智能分析** - 结合AI大模型分析书法风格和文本内容
4. **数据标注** - 为书法数据集生成标注数据

## 注意事项

- 看典古籍OCR每日免费额度2000次，超过需付费
- 豆包API按调用量计费，请注意用量控制
- 不要将`.env`文件提交到版本控制系统
- 识别结果仅供参考，不具权威性
