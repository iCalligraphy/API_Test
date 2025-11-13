# 看典古籍OCR API使用文档

## 接口一：/ocr_api 文字识别接口

### API接口说明

本接口实现古籍图像文字识别功能

### API接口地址

`https://ocr.kandianguji.com/ocr_api`

### API Token查看

您可以点击此处查看您的API Token信息

### 请求参数

- **token**：您所申请的API Token，点此申请 必传

- **email**：申请API Token的账号，看典古籍网站的注册账号（参数名为email，手机号注册的传手机号） 必传

- **image**：需要识别的古籍图像，base64编码后的字符串类型，您可以在此处转换您的图像为base64编码 必传

- **char_ocr**：是否进行单字符检测识别，不检测文本行，只检测图像上的字符，文本行顺序可能会出错；布尔类型；默认值：False

- **det_mode**：文字内容排版样式，目前有三种可选：auto（自动识别）、sp（竖向排版）、hp（横向排版）；字符串类型，默认值：auto

- **image_size**：识别前图像尺寸调整，图像越小识别速度越快，0为不调整，设置指定值将按照设置对图像最长边进行等比例调整；整数类型，默认值：0

- **return_position**：是否返回文本行坐标信息和字符坐标信息；布尔类型，默认值：False

- **return_choices**：是否返回每个字符的其它候选字；布尔类型，默认值：False

- **version**：指定识别算法版本；字符串类型，可选：default（v1标准版本）、beta（古籍语序优化版本）、v2（最新版本），默认值：default

- **det_layout（v2）**：是否开启版面识别（对图像上的内容进行判断是否是正文、页眉页脚/版心等），对分栏式、多栏式文档识别效果较好；布尔类型（开启True、关闭False），默认值：False

- **only_plain_text（v2）**：是否只识别返回正文内容，仅当版面识别开启时生效，不识别页眉/页脚/版心等；布尔类型（开启True、关闭False），默认值：False

- **return_layout（v2）**：是否返回版面信息，仅当版面识别开启时生效；布尔类型（开启True、关闭False），默认值：False

- **auto_insert_space（v2）**：按照字符间距自动插入空格；布尔类型（开启True、关闭False），默认值：False

- **hp_line_words_angel（v2）**：指定横排句子文字排序方向；字符串类型（从左到右left2right、从右到左right2left），默认值：left2right

- **sp_line_words_angel（v2）**：指定竖排句子文字排序方向；字符串类型（从上到下top2bottom、从下到上bottom2top），默认值：top2bottom

### 请求方式

POST请求，请求体可以为Form Data或JSON两种方式均可接受

### 响应内容

- **message**：当前请求的状态，成功：success；失败：error

- **id**：请求对应的唯一id

- **info**：与message相关联，成功为空，错误时返回具体错误信息

- **data**：识别结果

  - **width**：图像宽度（像素）

  - **height**：图像高度（像素）

  - **text_angel**：图像上文字排版方向，0为横排；1为竖排

  - **text_angel_confidence**：图像上文字排版方向置信度

  - **texts**：文本行列表，通用排序规则：横向排版按照从上到下，从左到左右排序；竖向排版按照从右到左，从上到下排序

  - **text_lines**：每个文本行内容，以下内容当请求参数中return_position为True时返回

    - **position**：文本行位置坐标列表，从左上角开始顺时针四个顶点坐标，[[x1,y1],[x2,y2],[x3,y3],[x4,y4]]

    - **text**：文本行中文字内容

    - **layout_classes_id**：内容属性（0：正文，1：页眉/页脚/版心等），仅当det_layout开启时返回

    - **words**：文本行每个文字的信息

      - **text**：文字内容

      - **choices**：候选字，当请求参数张return_choices为True时返回

      - **confidence**：文字置信度

      - **position**：文字基于全图的位置坐标列表，矩形框，左上角和右下角两点坐标[x1,y1,x2,y2]

      - **det_confidence**：位置检测置信度

      - **layout_classes_id**：内容属性（0：正文，1：页眉/页脚/版心等），仅当det_layout开启时返回

  - **layout**：版面信息，以下内容仅当return_layout开启时返回

    - **position**：版面区域坐标，矩形框，左上角和右下角两点坐标[x1,y1,x2,y2]

    - **classes**：版面类型属性（0：正文，1：页眉/页脚/版心等）

---

## 接口二：/get_token_status Token状态查询

### API接口说明

本接口实现查询API Token使用状态功能

### API接口地址

`https://ocr.kandianguji.com/get_token_status`

### API Token查看

您可以点击此处查看您的API Token信息

### 请求参数

- **token**：您所申请的API Token，点此申请 必传

- **email**：您申请API时填写的邮箱地址（默认为您的注册邮箱） 必传

### 请求方式

POST请求，请求体可以为Form Data或JSON两种方式均可接受

### 响应内容

- **message**：当前请求的状态，成功：success；失败：error

- **id**：请求对应的唯一id

- **info**：与message相关联，成功为空，错误时返回具体错误信息

- **data**：数据内容

  - **total_count**：API总额度

  - **used_count**：API已使用额度

  - **is_active**：API状态，0：申请中；1：已通过状态正常；2：申请不通过

---

## 接口三：/api/pdf_ocr_api PDF识别接口

### API接口说明

本接口实现PDF全书识别功能，通过接口上传PDF文件，识别完成后下载识别结果。

### API接口地址

`https://ocr.kandianguji.com/api/pdf_ocr_api`

### API Token查看

您可以点击此处查看您的API Token信息

### 请求参数

- **token**：您所创建的API Token，点此申请 必传

- **email**：创建API Token的账号，看典古籍网站的注册账号 必传

- **file**：PDF文件（单个） 必传

- **det_mode**：文字内容排版样式，目前有三种可选：auto（自动识别）、sp（竖向排版）、hp（横向排版）；字符串类型，默认值：auto

- **image_size**：识别前图像尺寸调整，图像越小识别速度越快，0为不调整，设置指定值将按照设置对图像最长边进行等比例调整；整数类型，默认值：0

- **version**：指定识别系统版本；字符串类型，可选：default（标准识别版本）、beta（古籍语序优化版本），默认值：default

### 请求方式

POST请求，请求体为Form Data

### 响应内容

- **message**：当前请求的状态，成功：success；失败：error

- **info**：与message相关联，成功为空，错误时返回具体错误信息

- **data**：数据内容

  - **task_id**：本次任务ID，后续查询任务状态、下载识别结果需要使用该ID

---

## 接口四：/api/pdf_ocr_api_status PDF识别任务进度查询接口

### API接口说明

本接口使用上一个接口创建任务获取到的task_id来查询任务识别进度。

### API接口地址

`https://ocr.kandianguji.com/api/pdf_ocr_api_status`

### API Token查看

您可以点击此处查看您的API Token信息

### 请求参数

- **token**：您所创建的API Token，点此申请 必传

- **email**：创建API Token的账号，看典古籍网站的注册账号 必传

- **task_id**：PDF识别任务ID 必传

### 请求方式

POST请求，请求体为Form Data

### 响应内容

- **message**：当前请求的状态，成功：success；失败：error

- **info**：与message相关联，成功为空，错误时返回具体错误信息

- **data**：数据内容

  - **task_id**：PDF识别任务ID

  - **created_on**：任务创建时间

  - **pages**：总页数

  - **speed**：识别进度

  - **is_finish**：任务是否完成

  - **finished_on**：任务完成时间（未完成为None）

  - **code**：如果任务识别完成的话返回code，在下载识别结果时使用

---

## 接口五：/api/pdf_ocr_api_download/task_id-xxx PDF识别任务识别结果下载接口

### API接口说明

本接口使用PDF识别任务ID和code下载识别结果压缩包。

### API接口地址

`https://ocr.kandianguji.com/api/pdf_ocr_api_download/task_id-xxx`

### 请求方式

GET请求

### 请求参数

- **code**：接口三获取到的task_id 必传

- **file_type**：下载识别结果文件类型；字符串类型，可选：txt（文本文件）、json（含坐标的json文件）、all（含json、txt、word、分页图像）、word（文档文档），默认值：all

### 响应内容

通过GET请求下载文件即可。
