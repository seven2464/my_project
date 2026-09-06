# 板探智眸（玻影智鉴）— AI 板材缺陷智能检测系统

> **仓库地址**：https://github.com/seven2464/my_project
> **项目全称**：板探智眸 / 玻影智鉴 —— AI 板材缺陷智能检测系统
> **文档说明**：主要介绍系统的**使用方法**与**技术实现**。

---

## 1. 项目简介

本项目是一套基于深度学习的**工业板材（玻璃面板/人造板）表面缺陷智能检测系统**，面向生产线的质检场景，实现：

- 对板材表面的 **5 大类缺陷**（崩边、溢胶、油污、坑洞、划痕）进行自动检测与分割；
- 自动完成 **ABC 板材等级判定**与**损伤程度评估**；
- 检测结果**实时写入 MySQL 数据库**，并通过 **Excel / Word / PDF** 多渠道导出；
- 调用**讯飞星火大模型**对检测数据进行 AI 分析，自动生成带改进建议的检测报告；
- 提供**桌面客户端**（PyQt5）与 **Web 数据看板**（Flask + ECharts）双端展示；
- 支持**语音播报**检测结果。

---

## 2. 功能特性一览

| 功能模块 | 说明 | 对应文件 |
|---------|------|---------|
| 用户登录 | 基于 MySQL 的用户校验登录界面 | `Login.py` |
| 图像检测 | 单张/文件夹批量检测，支持翻页浏览、标注图保存 | `imageDetect.py` |
| 实时检测 | 摄像头实时采集、定时抓帧检测、截图保存 | `camera.py` + `Main.py` |
| 视频检测 | 上传 mp4/avi 视频逐帧检测 | `VideoDetect.py` |
| 缺陷识别 | YOLOv5 目标检测 5 类缺陷（mAP 90.7%+） | `model/yolov5-master` |
| 缺陷分割 | U-Net 分割缺陷区域，计算面积/周长 | `unet/` |
| 等级判定 | A/B/C 级板材判定 + 完好/轻微/中等/严重损伤评估 | `VideoDetect.py`、`imageDetect.py` |
| AI 分析 | 讯飞星火 Spark Max v3.5 生成优化建议 | `ai.py`、`sparkAPI.py` |
| 报告生成 | 模板填充 Word 报告并转 PDF（自动含 AI 附注） | `pdf.py`、`imagePDF.py`、`videoPDF.py` |
| 语音播报 | pyttsx3 播报检测结论 | `speak.py` |
| Web 看板 | Flask 7 个 API + ECharts 可视化大屏 | `app.py`、`templates/`、`static/` |
| 数据存储 | MySQL 8.0，检测结果实时入库 | `plank_innovate` 库 |

---

## 3. 使用方法

### 3.1 环境准备

| 依赖 | 版本（来自 requirements.txt / 研发文档） |
|------|------|
| 操作系统 | Windows（代码含 `ctypes.windll`、`os.system("start ...")` 等 Windows 专用调用，建议 Windows 环境运行） |
| Python | 3.8（研发文档标注） |
| PyTorch | 2.0.1 + cu117（GPU 版；无 GPU 时自动回退 CPU） |
| 检测框架 | YOLOv5（仓库内置源码）+ ultralytics 8.0.100 |
| GUI | PyQt5 5.15.11、PyQtWebEngine |
| Web | Flask 1.1.4、Jinja2 |
| 数据库 | MySQL 8.0 + mysql-connector-python 8.1.0 / PyMySQL |
| 其他 | OpenCV 4.10、openpyxl、pandas、python-docx、docx2pdf、pyttsx3、sparkai 等 |

> 说明：`requirements.txt` 由 Windows 构建机生成，包含个别本地路径条目（如 `inputs @ file:///D:/bld/inputs...`）。执行 `pip install -r requirements.txt` 时如报错，可将这些本地路径行删除后再安装。

### 3.2 安装依赖

```bash
# 建议创建虚拟环境
python -m venv venv
venv\Scripts\activate        # Windows

pip install -r requirements.txt
```

核心依赖也可按需单独安装：

```bash
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu117
pip install PyQt5 opencv-python numpy pillow openpyxl pandas
pip install flask flask-sqlalchemy pymysql mysql-connector-python
pip install python-docx docx2pdf pyttsx3 sparkai websocket-client
```

### 3.3 准备模型权重（⚠️ 重要）

**仓库中不包含训练好的模型权重文件**，代码运行前需手动放置以下两个文件：

| 文件 | 用途 | 代码中加载位置 |
|------|------|--------------|
| `best.pt` | YOLOv5 目标检测权重（5 类缺陷，置信度阈值 0.907） | `model/weights/best.pt` |
| `U_net_best.pth` | U-Net 分割权重（3 通道输入、2 类输出） | `model/weights/U_net_best.pth` |

需自行创建 `model/weights/` 目录并将权重文件放入，否则程序启动时 `load_models()` / `segmentation()` 会报错。

### 3.4 配置 MySQL 数据库

代码默认使用以下连接信息（`Login.py` / `VideoDetect.py` / `imageDetect.py` / `app.py` 中写死，可按需修改）：

```
host: localhost   port: 3306
user: root        password: 123456
```

需要准备两个数据库：

| 数据库 | 用途 | 主要数据表 |
|--------|------|-----------|
| `simpleui` | 登录校验 | `demo_employe`（字段 name、phone 等） |
| `plank_innovate` | 检测结果存储 | `detection_result`（Web 看板读取）、`video_detection_results`（视频检测）、`images_detection_results`（图片批量检测） |

说明：
- 登录时查询 `simpleui.demo_employe` 中 **姓名 + 手机号** 匹配的用户；
- 检测结果表由代码自动 `CREATE TABLE IF NOT EXISTS` 创建，无需手工建表。

### 3.5 配置讯飞星火大模型

AI 分析功能基于讯飞星火 Spark Max（v3.5）。在 `ai.py` 中配置密钥：

```python
SPARKAI_URL = 'wss://spark-api.xf-yun.com/v3.5/chat'
SPARKAI_APP_ID = '你的APPID'
SPARKAI_API_SECRET = '你的APISecret'
SPARKAI_API_KEY = '你的APIKey'
SPARKAI_DOMAIN = 'generalv3.5'
```

密钥可在讯飞开放平台控制台获取（https://console.xfyun.cn/services/bm35）。`sparkAPI.py` 提供了基于 WebSocket + HMAC-SHA256 鉴权的备用调用实现。

### 3.6 启动系统

```bash
# 方式一：从登录界面进入（推荐，含加载动画）
python Login.py

# 方式二：直接启动主程序
python Main.py

# 方式三：启动 Web 数据看板（自动打开浏览器 http://127.0.0.1:5000）
python app.py
```

桌面端主程序启动时会先加载两个模型（YOLOv5 + U-Net），加载完成后进入主界面。也可使用 `Main.spec` / `Login.spec` 通过 PyInstaller 打包为 exe。

---

## 4. 使用指南

### 4.1 登录界面（Login.py）

- 无边框、带加载动效的登录窗口；
- 输入**用户名**和**手机号**（对应数据库 `demo_employe` 表），点击“安全登录”；
- 校验通过后自动进入主窗口；失败会弹出提示；
- 界面左下角可跳转**项目官网**（https://wangsuhang123.github.io/btzm/index.html）与**管理后台**（http://127.0.0.1:8000）。

### 4.2 主界面与三种检测模式

主窗口左侧导航栏提供三个页面（`stackedWidget` 切换）：

| 页面 | 入口按钮 | 功能 |
|------|---------|------|
| 图像检测 | 图像图标 | 单张/批量图片检测 |
| 实时检测 | 实时监测图标 | 摄像头实时检测 |
| 视频检测 | 视频图标 | 视频文件检测 |

右上角齿轮按钮（`pushButton_14`）打开**参数设置**窗口。

### 4.3 图像检测模式

操作流程：

1. 点击 **载入图片**（选择单张 jpg/png/jpeg）或 **载入文件夹**（批量导入目录内图片）；
2. 使用 **上一页 / 下一页** 切换图片；
3. 点击 **开始检测**：YOLOv5 检出缺陷框，U-Net 分割缺陷区域并计算面积/周长；
4. 界面同步显示：缺陷类别、缺陷数量、检测时间、准确率（固定显示 100%）、缺陷位置（中心/边缘）、损伤程度、板材等级、ABC 数量、缺陷面积、面积占比、A 级占比等；
5. 点击 **保存图片** 将标注图存至 `photo/save/`；
6. 批量检测完成后可选择**生成 AI 报告**（Word + PDF）；
7. 检测明细自动写入 `images_detection_results` 表，并支持导出 Excel（`图片检测结果.xlsx`）。

### 4.4 实时检测模式（摄像头）

1. 点击 **开始检测**：启动摄像头线程（`camera.py`，默认相机编号从全局设置读取），每 6 秒自动抓帧检测一次；
2. 当前帧显示在界面，检测到缺陷会绘制绿色框；
3. 点击 **截图** 将当前帧保存到 `photo/Original/` 并立即执行一次检测；
4. 点击 **停止检测** 停止抓帧；
5. 检测数据实时累加板坯数量与 A/B/C 级计数，累计达到设定检测数量后自动生成报告。

### 4.5 视频检测模式

1. 点击 **上传视频**（支持 mp4/avi）；
2. 点击 **开始检测**：程序每间隔 25 帧执行一次 YOLOv5 检测 + U-Net 分割；
3. 逐帧统计缺陷名称、数量、置信度（固定 100%）、检测耗时、缺陷面积、面积占比、板材等级等；
4. 检测结果实时写入 `video_detection_results` 表；
5. 检测结束自动生成视频检测报告（Word + PDF）；
6. 点击 **停止检测** 可提前终止。

### 4.6 参数设置（Setting.py）

点击主界面齿轮按钮打开设置窗口，可配置：

| 参数 | 说明 |
|------|------|
| 相机编号 | 实时检测使用的摄像头编号 |
| 样品名称 | 报告中的样品名 |
| 检验类别 | 如委托检验/自检检验 |
| 检测批次 | 生产批次号 |
| 板坯规格 / 板坯型号 | 被检板材信息 |
| 检测数量 | 累计检测多少片后生成一次报告（默认 50） |
| 传输速率 | 产线速度信息 |

设置值通过 `global_store.py` 的 `shared_data` 字典在模块间共享，并影响报告内容。

### 4.7 检测报告生成

- **触发方式**：累计检测数量达到设置值（默认 50）时自动生成，也可在图片检测界面手动点击“生成报告”；
- **流程**：汇总缺陷数据 → 组装提问文本 → 调用星火大模型生成 200 字优化建议（固定以“根据检测数据”开头、以“通过以上措施，有望提高生产线的效率和产品质量。”结尾）→ 填充 Word 模板（`file/板探智眸检测报告模板.docx` / `file/玻璃检测报告模板.docx`）→ 转存 PDF 至 `file/检测报告/`；
- **报告内容**：样品名称、检验类别、检测日期、批次、板坯规格/型号、委托单位、生产单位、检测数量、检测地点、检测依据、检测结论、AI 附注。

### 4.8 Web 数据看板

运行 `python app.py` 后浏览器自动打开 http://127.0.0.1:5000，展示“人造板表面缺陷检测系统”可视化大屏（ECharts）。后端提供 7 个 API：

| 接口 | 数据内容 |
|------|---------|
| `/data` | 各类缺陷数量累计 |
| `/accuracy_data` | 各类缺陷检测准确率序列 |
| `/detection_time` | 检测耗时序列 |
| `/abc_judgment` | A/B/C 级板材数量 |
| `/defects_area` | 缺陷面积序列 |
| `/damage_level` | 完好/轻微/中等/严重统计 |
| `/title_data` | 总检测量与 A 级数量 |

`templates/wenda.html` 为智能问答页面（对应 `wenda.py` 目前为空实现，尚未启用）。

---

## 5. 技术介绍

### 5.1 整体架构

系统采用 **Python 单仓库多模块** 架构，按功能分为六层：

```
┌─────────────────────────────────────────────────────────┐
│                    表现层（双端）                         │
│   桌面端：PyQt5（Login.py / Main.py / Ui_MainWindow.py）  │
│   Web端：Flask + Jinja2 + ECharts（app.py / templates/） │
├─────────────────────────────────────────────────────────┤
│                    业务层（三种检测模式）                  │
│   图像检测 imageDetect.py   实时检测 camera.py            │
│   视频检测 VideoDetect.py   参数设置 Setting.py           │
├─────────────────────────────────────────────────────────┤
│                    算法层（双模型）                       │
│   YOLOv5 目标检测（best.pt, conf=0.907）                 │
│   U-Net 缺陷分割（U_net_best.pth, 阈值0.5）              │
│   ABC判定 + 损伤评估 + 面积/位置计算                      │
├─────────────────────────────────────────────────────────┤
│                    智能分析层                            │
│   讯飞星火 Spark Max v3.5（ai.py / sparkAPI.py）         │
│   语音播报 pyttsx3（speak.py）                           │
├─────────────────────────────────────────────────────────┤
│                    数据层                                │
│   MySQL 8.0（plank_innovate / simpleui）                │
│   Excel 导出 openpyxl（实时检测结果.xlsx）               │
│   Word/PDF 报告（python-docx + docx2pdf）               │
├─────────────────────────────────────────────────────────┤
│                    基础设施                              │
│   model/yolov5-master 源码  unet/ 模型  utils/ 工具库    │
│   global_store.py 全局状态  docs/研发文档                │
└─────────────────────────────────────────────────────────┘
```

### 5.2 目标检测：YOLOv5

- 通过 `torch.hub.load(repo_or_dir='model/yolov5-master', model='custom', path='model/weights/best.pt', source='local')` 加载本地 YOLOv5 源码与自定义权重；
- 检测 5 类缺陷：`chipping`(崩边)、`glueOverflow`(溢胶)、`greasyDirt`(油污)、`potholes`(坑洞)、`scratches`(划痕)；
- 置信度阈值设为 **0.907**；
- 研发文档标注：YOLOv5m + Transformer 注意力，mAP 90.7%（V2.2 达 91.5%）；
- 推理时自动选择 `cuda`（若可用）否则 `cpu`。

### 5.3 缺陷分割：U-Net

- 自研 U-Net 实现（`unet/unet_model.py`、`unet_parts.py`）：标准 U 型编码-解码结构（DoubleConv → Down ×4 → Up ×4 → OutConv）；
- `UNet(n_channels=3, n_classes=2)`，加载 `U_net_best.pth` 权重（`strict=False`）；
- 推理时双线性插值回原图尺寸，二分类输出经 sigmoid 与 0.5 阈值生成二值掩膜；
- 掩膜经 OpenCV 轮廓检测（`findContours`）计算缺陷的**面积、周长、平均面积**，并按比例（scale_factor = 50/256）换算为真实物理尺寸；
- 研发文档标注：U-Net + CBAM 注意力，IoU 82.5%（V2.2 达 83.8%）。

### 5.4 等级判定与损伤评估规则

| 规则 | 判定逻辑（依据代码） |
|------|----------------------|
| 板材等级 | 缺陷数 = 0 → **A 级**；缺陷数 < 5 → **B 级**；缺陷数 ≥ 5 → **C 级** |
| 损伤程度 | 缺陷数 = 0 → **完好**；≤ 3 → **轻微**；≤ 5 → **中等**；≥ 6 → **严重** |
| 缺陷位置 | 检测框坐标落在阈值框 [(150,100),(500,420)] 内 → **中心**，否则 **边缘** |

### 5.5 AI 分析（讯飞星火）

- `ai.py` 基于 `sparkai` 官方 SDK 调用 **Spark Max v3.5**（`generalv3.5` domain），非流式生成；
- `sparkAPI.py` 为 WebSocket 直连实现（HMAC-SHA256 鉴权，`temperature=0.5, max_tokens=4096`）；
- 分析流程：检测数据 → 拼装固定模板提问（缺陷类别/数量/准确率/耗时/A级占比/损伤程度/缺陷位置/面积等）→ 生成约 200 字生产线优化建议 → 作为报告“附注”填入。

### 5.6 数据存储（MySQL）

- **登录**：查询 `simpleui.demo_employe`（name + phone 匹配）；
- **实时/视频检测**：写入 `plank_innovate.video_detection_results`（缺陷名称、数量、准确率、耗时、面积、面积占比、位置、损伤程度、板材等级）；
- **图片批量检测**：写入 `plank_innovate.images_detection_results`（类别、数量、准确率、耗时、平均面积、总面积）；
- **Web 看板**：读取 `plank_innovate.detection_result` 表进行统计展示；
- 表结构由代码自动创建。

### 5.7 报告生成

- 基于 `python-docx` 读取预置模板（`file/*模板.docx`），按单元格填充 12 项报告字段；
- `docx2pdf` 将 Word 转为 PDF，输出到 `file/检测报告/`，文件名含时间戳；
- 报告触发频率由设置中“检测数量”控制（默认 50 片一次），生成过程在独立线程中执行，避免阻塞 UI。

### 5.8 Web 可视化

- Flask 提供 7 个 JSON 接口聚合 MySQL 统计数据；
- 前端使用 ECharts（`templates/js/echarts.min.js`）构建数据大屏，含缺陷统计、准确率、耗时、等级分布、损伤程度等图表；
- 附带 `wenda.html` 问答页面（后端 `wenda.py` 尚未实现）。

### 5.9 语音播报

- `speak.py` 基于 pyttsx3，将英文缺陷类别转为中文（chipping→崩边 等）后播报“检测完成，缺陷类别为 X，板材级别为 Y”；
- 播放在独立线程执行，不阻塞界面。

---

## 6. 项目目录结构

```
my_project/
├── Login.py                 # 登录界面（MySQL 校验）
├── Main.py                  # 主程序（模型加载、三模式切换、实时检测逻辑）
├── Ui_MainWindow.py         # 主界面 UI（pyuic 生成）
├── main.ui / output.ui      # Qt Designer 界面文件
├── Setting.py               # 参数设置窗口
├── imageDetect.py           # 图片检测模块
├── VideoDetect.py           # 视频检测模块
├── camera.py                # 摄像头线程（QThread）
├── pdf.py                   # 实时检测报告生成（Word→PDF + AI）
├── imagePDF.py              # 图片检测报告生成
├── videoPDF.py              # 视频检测报告生成
├── ai.py                    # 讯飞星火大模型调用（sparkai）
├── sparkAPI.py              # 星火 WebSocket 直连实现
├── speak.py                 # 语音播报（pyttsx3）
├── app.py                   # Flask Web 数据看板（7 个 API）
├── global_store.py          # 全局参数共享（shared_data 字典）
├── abcJudgment.py           # ABC 等级判定工具
├── dataShow.py / deleteAll.py  # 界面工具 / 清理脚本
├── wenda.py                 # 问答系统后端（当前为空）
├── requirements.txt         # 依赖清单
├── Login.spec / Main.spec   # PyInstaller 打包配置
├── unet/                    # U-Net 分割模型（unet_model.py / unet_parts.py）
├── model/
│   ├── yolov5-master/       # YOLOv5 源码
│   └── weights/             # ⚠️ 需自行放置 best.pt、U_net_best.pth
├── utils/                   # YOLOv5 工具库（data_loading 等）
├── static/                  # Web 静态资源（css/js/images/font）
├── templates/               # Web 页面（index.html 看板 / wenda.html 问答）
├── file/                    # 报告模板与生成结果（file/检测报告/）
├── photo/                   # 摄像头抓帧（Original）与标注图（save）
├── mysqlProject/            # MySQL 相关（当前为空目录）
├── docs/研发文档/            # 研发文档中心（日志/实验/版本/会议纪要）
└── 实时检测结果.xlsx         # 实时检测 Excel 导出样例
```

---

## 7. 常见问题与注意事项

| 问题 | 说明与处理 |
|------|-----------|
| 启动报找不到模型 | `model/weights/` 目录及 `best.pt`、`U_net_best.pth` 不在仓库内，需自行准备并放置 |
| `pip install -r requirements.txt` 报错 | 删除其中 `inputs @ file:///D:/...` 等本地路径条目后重装 |
| 登录失败 | 需先在 `simpleui` 库 `demo_employe` 表配置用户（name + phone） |
| 数据库连接失败 | 代码默认 root/123456，请按本机 MySQL 修改各文件中连接参数 |
| AI 分析无结果 | 检查 `ai.py` 中星火 APPID/APIKey/APISecret 是否正确、账户是否有额度 |
| 中文路径读取失败 | 历史版本曾出现中文路径下图片读取偶发失败，建议路径避免中文（研发文档已记录修复） |
| docx2pdf 转换失败 | 依赖本机安装的 MS Word/WPS，需确保 Office 可用 |
| wenda 问答页空白 | `wenda.py` 后端尚未实现，仅前端页面 |
| 代码的 Windows 依赖 | `ctypes.windll`、`os.system("start ...")` 等为 Windows 专用，跨平台运行需适配 |
| 准确率恒为 100% | 当前版本在代码中固定填写“100%”，非模型真实置信度输出 |

---

## 8. 版本演进（摘自 docs/研发文档）

| 版本 | 时间 | 里程碑 |
|------|------|--------|
| V1.0 | 2025.01 | 基础检测系统（YOLOv5 图像检测 + PyQt5 GUI + 登录 + MySQL） |
| V1.1 | 2025.02 | 视频检测、U-Net 分割、语音播报、Excel 导出 |
| V1.2 | 2025.03 | Web 可视化平台（Flask + ECharts） |
| V1.3 | 2025.04 | 讯飞星火大模型集成、AI 检测报告 |
| V2.0 | 2025.07 | 生产就绪版本 |
| V2.1 | 2025.09 | 性能与可视化升级 |
| V2.2 | 2025.11 | 正式发布版 |
| V3.0 | 2026Q3 | 平台化架构（规划中） |

核心指标演进（研发文档口径）：检测 mAP 由 87.3% → 91.5%；分割 IoU 由 78.1% → 83.8%；单张推理速度由 85ms → 18ms（边缘端）。

---

*本文档依据仓库源码与 docs/研发文档 整理生成，用于项目使用与技术理解参考。*
