# API_Test

古籍OCR API测试工具，用于识别字帖图片中的文字，并提取单字图片。

## 功能

- **OCR识别** (`ocr_test.py`): 批量识别`images/`目录中的字帖图片，调用OCR API进行文字识别
- **结果可视化** (`visualize_ocr.py`): 在原始图片上绘制识别文字的边界框，生成可视化结果
- **单字提取** (`extract_characters.py`): 基于OCR识别结果，从字帖图片中提取每个单字并保存为独立图片

## 输出

- **识别结果** (`outputs/`目录): 
  - `*_result.txt` - 文本结果
  - `*_result.json` - JSON结果（包含位置信息）
  - `*_visualized.png` - 可视化图片

- **单字图片** (`characters/`目录):
  - `图片名_L行号_W字序号_字符_置信度.png` - 每个单字的独立图片

## 使用

1. 配置`.env`文件，设置`Token`和`Email`
2. 将测试图片放入`images/`目录
3. 运行`python ocr_test.py`进行识别
4. 运行`python visualize_ocr.py`生成可视化结果
5. 运行`python extract_characters.py`提取单字图片

## 单字提取参数说明

在`extract_characters.py`的`main()`函数中可以调整以下参数：

- `padding`: 边距（像素），默认5，在字符周围添加的空白边距
- `min_confidence`: 最小置信度（0.0-1.0），默认0.0，过滤低置信度字符
- `min_size`: 最小字符尺寸（像素），默认10，过滤太小的字符
- `output_format`: 输出格式，默认'PNG'，支持PNG、JPEG等
