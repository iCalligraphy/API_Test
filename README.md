# API_Test

古籍OCR API测试工具，用于识别字帖图片中的文字。

## 功能

- **OCR识别** (`ocr_test.py`): 批量识别`images/`目录中的字帖图片，调用OCR API进行文字识别
- **结果可视化** (`visualize_ocr.py`): 在原始图片上绘制识别文字的边界框，生成可视化结果

## 输出

识别结果保存在`outputs/`目录：`*_result.txt`（文本）、`*_result.json`（JSON）、`*_visualized.png`（可视化图片）

## 使用

1. 配置`.env`文件，设置`Token`和`Email`
2. 将测试图片放入`images/`目录
3. 运行`python ocr_test.py`进行识别
4. 运行`python visualize_ocr.py`生成可视化结果
