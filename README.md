# 课堂 PPT 照片智能大纲生成器

基于多模态大模型的课堂 PPT 照片整理工具，用于将课堂照片整理为可编辑、可追溯来源的学习大纲，并导出 Word 文档。本项目是软件工程课程的工程实践项目，工程代号为 `lecture-syllabus-generator`。

当前版本提供本地运行的前后端及模拟数据流程，包含多模态模型调用入口。默认使用 `mock` 模式，无需 API 密钥即可演示完整流程；模拟结果是预设的数据库课程内容，不代表上传图片的真实识别结果。

## 功能与当前实现

| 功能 | 当前实现 |
| --- | --- |
| 批量上传 | 上传课堂图片、调整顺序，以逻辑页码组织内容 |
| 内容识别 | 提供 `mock`、`multimodal`、`fallback` 三种识别模式 |
| 知识点抽取 | 从结构化结果或文本行提取知识点，按规范化文本跨页去重 |
| 模块组织 | 当前按知识点的首个来源页及页面标题组织模块 |
| 大纲生成与校对 | 生成 Markdown 大纲，在线编辑、保存并记录版本 |
| 来源展示 | 保存并展示来源页码及来源类型；缺失来源信息时标记“来源待核对” |
| Word 导出 | 将大纲导出为 `.docx` 文件 |
| 历史记录 | 查看已有任务、重新打开大纲并再次导出 |

使用流程：上传照片 → 调整顺序 → 识别与抽取 → 生成大纲 → 校对保存 → 导出 Word。

## 技术栈

- 后端：Python、FastAPI、Uvicorn、Pydantic。
- 数据存储：SQLAlchemy、SQLite；上传文件保存在本地目录。
- 前端：原生 HTML、CSS、JavaScript，由 FastAPI 提供静态页面，无需 Node.js 构建。
- 模型调用：HTTPX，使用兼容 Chat Completions 的多模态接口。
- 文档导出与测试：python-docx、pytest。

## 目录结构

```text
.
├── README.md                         # 仓库说明
├── .gitignore                        # 忽略本地配置、缓存和运行数据
├── doc1_text.txt                      # 项目初始化与工程基线记录
├── doc2_text.txt                      # 开发任务清单与实现计划
└── lecture-syllabus-generator/
    ├── README.md                     # 应用目录入口说明
    ├── backend/
    │   ├── app/
    │   │   ├── main.py               # FastAPI 入口
    │   │   ├── config.py             # 环境变量与应用配置
    │   │   ├── db.py                 # 数据库连接与初始化
    │   │   ├── models.py             # 数据模型
    │   │   ├── schemas.py            # 接口数据结构
    │   │   ├── errors.py             # 统一错误处理
    │   │   ├── prompts_loader.py     # 提示词加载器
    │   │   ├── routers/              # 任务、大纲、导出及元信息接口
    │   │   └── services/             # 识别、抽取、模块组织及导出逻辑
    │   ├── db/schema.sql             # 数据库结构参考
    │   ├── prompts/                  # 识别、抽取、聚类提示词文件
    │   ├── tests/                    # 冒烟测试
    │   ├── .env.example              # 环境配置模板
    │   ├── requirements.txt          # 运行依赖
    │   ├── requirements-dev.txt      # 测试依赖
    │   └── run.py                    # 本地启动入口
    ├── frontend/                     # 上传、进度、大纲和历史记录页面
    └── scripts/                      # Windows / macOS / Linux 启动脚本
```

`backend/data/` 和 `backend/storage/` 在运行时创建，分别保存数据库和上传文件，不纳入版本控制。

## 快速开始

准备 Git 和 Python 3.10 或更高版本。以下命令以仓库默认目录名为例。

### Windows PowerShell

```powershell
git clone https://github.com/ChenXuanyu-1216/Intelligent-outline-generator-for-classroom-PPT-photos-based-on-large-models.git
cd Intelligent-outline-generator-for-classroom-PPT-photos-based-on-large-models/lecture-syllabus-generator/backend
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Copy-Item .env.example .env
.\.venv\Scripts\python.exe run.py
```

### macOS / Linux

```bash
git clone https://github.com/ChenXuanyu-1216/Intelligent-outline-generator-for-classroom-PPT-photos-based-on-large-models.git
cd Intelligent-outline-generator-for-classroom-PPT-photos-based-on-large-models/lecture-syllabus-generator/backend
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
cp .env.example .env
.venv/bin/python run.py
```

已配置过 `.env` 时保留原文件即可。请从 `backend` 目录启动，数据库路径和环境配置使用当前工作目录。后续启动只需运行对应虚拟环境中的 Python，无需重复安装。

启动后访问：

| 入口 | 地址 |
| --- | --- |
| 上传首页 | http://127.0.0.1:8000/ |
| 历史记录 | http://127.0.0.1:8000/history.html |
| API 文档 | http://127.0.0.1:8000/docs |
| 健康检查 | http://127.0.0.1:8000/api/health |
| 工程基线信息 | http://127.0.0.1:8000/api/meta |

也可激活已安装依赖的 Python 环境后使用 `scripts/start_backend.bat` 或 `bash scripts/start_backend.sh`（从应用目录执行）。脚本调用当前环境中的 `python`。

## 模型与上传配置

编辑 `lecture-syllabus-generator/backend/.env`：

```dotenv
APP_MODEL_PROVIDER=mock
APP_MODEL_API_KEY=
APP_MODEL_BASE_URL=https://api.openai.com/v1
APP_MODEL_NAME=gpt-4o-mini
APP_MODEL_TIMEOUT_SECONDS=60
APP_MODEL_MAX_RETRY=1
APP_ALLOWED_EXT=.jpg,.jpeg,.png,.pdf
APP_MAX_FILE_MB=10
APP_MAX_FILES_PER_BATCH=20
APP_RECOMMENDED_BATCH=10
APP_LOW_CONFIDENCE_THRESHOLD=0.60
```

以上为项目模板的默认值；接入时应按实际服务商填写接口地址和支持视觉输入的模型名称。

- `mock`：使用预设结果演示本地流程。
- `multimodal`：向 `APP_MODEL_BASE_URL` 下的 `/chat/completions` 发送请求。需要有效密钥；当前实现缺少密钥时会回退到模拟结果。
- `fallback`：返回识别服务不可用的兜底内容。

实际接入模型时，将 `APP_MODEL_PROVIDER` 改为 `multimodal`，再填写密钥、模型名和接口地址。`.env` 已被 Git 忽略，仓库只保留空密钥的 `.env.example`。

## 测试

测试覆盖健康信息、上传格式校验、来源标签解析、分阶段识别与生成中的来源保留、跨页去重、编辑保存后重新打开和 Word 内容比对，以及超时、断连、部分失败、重试和异常恢复。

**pytest 会在导入应用之前创建独立临时数据库和上传目录，强制使用模拟识别；测试不会清空日常使用的 `backend/data/app.db`。** 每个用例重置临时数据库，整轮结束后清理测试目录。模型超时与断连使用本地模拟传输，不发送真实 API 请求。

在 `backend` 目录安装依赖并执行：

```powershell
# Windows PowerShell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt -r requirements-dev.txt
.\.venv\Scripts\python.exe -m pytest -q
```

```bash
# macOS / Linux
.venv/bin/python -m pip install -r requirements.txt -r requirements-dev.txt
.venv/bin/python -m pytest -q
```

首次运行需先按“快速开始”创建虚拟环境。测试默认自行配置隔离环境，不需要修改 `.env`。上述测试不能验证真实模型的识别质量，也不能替代浏览器手工验收。

### 已有数据库升级与来源保留

启动时会为旧 SQLite 数据库的 `page` 表补加可空的 `recognized_structured` 字段，保留原有记录，并可重复启动。新识别结果会将标题、知识点和来源类型一并保存；后续生成和重新生成复用这些数据。没有保存来源类型的旧记录无法自动恢复真实来源，重新生成时显示“来源待核对”。历史上已保存的大纲不会被批量改写。

相同文字但来源类型不同的条目分开保留；相同文字且来源类型相同的条目才合并来源页码。部分页面失败时仍处理成功页，全部失败时返回明确错误；重新生成失败时保留此前已保存的大纲与知识点。

## 当前限制

- 知识点去重使用文本规则，模块组织使用来源页规则，尚未实现模型驱动的语义聚类。
- 真实模型返回内容目前按文本行解析；未提供结构化来源时标记“来源待核对”，置信度仍使用固定值，识别质量与来源归因需要后续验证。
- 上传配置包含 PDF，但当前未实现多页 PDF 拆页；识别请求使用 `image_url` 格式，PDF 能否处理取决于服务端兼容性。演示时建议使用 JPG、JPEG 或 PNG。
- 默认绑定 `127.0.0.1:8000`，当前工程面向本地课堂演示，未提供用户认证或多用户数据隔离。

## 工程文档

- [项目初始化与工程基线记录](doc1_text.txt)
- [开发任务清单与实现计划](doc2_text.txt)

两份文档记录了课程工程基线和开发计划，其中的历史验证结果以文档编制时的记录为准，当前运行情况应以实际测试为准。
