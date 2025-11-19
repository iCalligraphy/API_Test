# 看典古籍OCR API 测试

本文件夹包含看典古籍OCR API的测试和应用程序。

## 文件说明

### 主要程序

- **ocr_test.py** - 古籍OCR识别测试程序
  - 读取`images/`文件夹中的字帖图片
  - 调用看典古籍OCR API进行文字识别
  - 将识别结果保存到`outputs/`文件夹

- **extract_characters.py** - 单字分割提取程序
  - 基于OCR识别结果从字帖图片中提取每个单字
  - 将单字保存为独立图片到`characters/`文件夹

- **visualize_ocr.py** - OCR识别结果可视化程序
  - 读取JSON识别结果
  - 在原始图片上绘制每个字的边界框
  - 可视化展示识别效果

### 目录结构

```
kandian_ocr/
├── images/          # 输入：待识别的古籍字帖图片
├── outputs/         # 输出：OCR识别结果（JSON格式）
├── characters/      # 输出：提取的单字图片
├── ocr_test.py      # OCR识别测试
├── extract_characters.py  # 单字提取
└── visualize_ocr.py # 结果可视化
```

## 使用方法

### 1. 配置API密钥

在根目录的`.env`文件中配置看典古籍OCR的Token和Email：

```bash
Token="your-kandian-token-here"
Email="your-email-or-phone-here"
```

### 2. 准备图片

将待识别的古籍字帖图片放入`images/`文件夹。

### 3. 运行OCR识别

```bash
cd kandian_ocr
python ocr_test.py
```

识别结果将保存到`outputs/`文件夹，每个图片对应一个JSON文件。

### 4. 提取单字（可选）

```bash
python extract_characters.py
```

从识别结果中提取单字图片，保存到`characters/`文件夹。

### 5. 可视化结果（可选）

```bash
python visualize_ocr.py
```

在原图上绘制识别框，可视化查看识别效果。

## API 文档

详细的API文档请参考：
- [看典古籍OCR API使用文档](../Docs/看典古籍OCR%20API使用文档.md)
- [看点古籍OCR API](../Docs/看点古籍OCR%20API.md)

## 注意事项

- 识别前请确保已在[看典古籍网站](https://ocr.kandianguji.com)申请API Token
- 每日免费额度最多2000次，超过需付费（每2000次 20元）
- 机器识别结果仅供参考，不具权威性
