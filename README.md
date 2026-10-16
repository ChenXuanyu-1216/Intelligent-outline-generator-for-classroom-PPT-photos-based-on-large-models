<a name="language-navigation"></a>

[简体中文](#chinese) | [English](#english)

<a name="chinese"></a>

# 课堂 PPT 照片智能大纲生成器

基于多模态大模型的课堂 PPT 照片整理工具，用于将课堂照片整理为可编辑、可追溯来源的学习大纲，并导出 Word 文档。本项目是软件工程课程的工程实践项目，工程代号为 `lecture-syllabus-generator`。

当前版本提供本地运行的前后端及模拟数据流程，包含多模态模型调用入口。默认使用 `mock` 模式，无需 API 密钥即可演示完整流程；模拟结果是预设的数据库课程内容，不代表上传图片的真实识别结果。

本轮交付阶段为 EXP03：完成可运行工程、模拟业务闭环、异常恢复、自动化验证与交付文档。EXP04 仅整理接口和后续接入要求，本轮不新增真实 AI 服务。阶段范围与验收依据见 [EXP03 工程交付](docs/exp03-delivery.md)，后续工作见 [EXP04 准备说明](docs/exp04-readiness.md)。

## 功能与当前实现

| 功能 | 当前实现 |
| --- | --- |
| 批量上传 | 上传课堂图片、调整顺序，以逻辑页码组织内容 |
| 内容识别 | 提供 `mock`、`multimodal`、`fallback` 三种识别模式 |
| 知识点抽取 | 从结构化结果或文本行提取知识点，按规范化文本跨页去重 |
| 模块组织 | 默认按来源页组织；可启用模型按主题跨页分组，仅返回模块名与已有知识点 ID |
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
├── frontend-preview.html             # 可直接打开的独立前端预览
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

Windows 可直接双击 `lecture-syllabus-generator/scripts/start_backend.bat`：脚本优先使用 `backend/.venv/Scripts/python.exe`，没有项目虚拟环境时才调用当前环境的 `python`。缺少依赖或启动失败时会保留窗口并显示提示。macOS/Linux 可激活已安装依赖的 Python 环境后，从应用目录执行 `bash scripts/start_backend.sh`，该脚本使用当前环境中的 `python`。

### 前端页面与离线预览

上传首页与整理记录页采用统一的暖纸配色、衬线标题和留白布局，并跟随系统切换深浅主题。背景中的数学公式与代码缓慢向上流动，默认清晰度为 30%。首页继续使用原有的文件选择、顺序调整、删除和任务提交功能；整理记录以列表展示标题、状态、页数和创建时间，并提供打开与导出入口。

仅查看样式时，直接用浏览器打开仓库根目录的 [`frontend-preview.html`](frontend-preview.html)，无需启动后端或联网。该文件默认展示整理记录的样式示例，可切换为空记录状态，也可点击“新建整理”查看上传页。预览支持选择文件并展示文件名，但不提交任务；示例不代表真实记录，实际打开与导出请使用启动后的系统。

页面默认遵循系统的“减少动态效果”设置。背景静止时，可点击右上角“播放背景”主动开启，再次点击“暂停背景”停止，无需修改系统设置。两页共用 `frontend/css/home.css` 与 `frontend/js/knowledge-flow.js`；记录列表的补充样式位于 `frontend/css/history.css`，不依赖前端构建工具或外部 CDN。

点击右上角“速度”可展开滑杆，在 0.25×–3× 之间调整公式向上流动的速度，也可用方向键微调。暂停时调速仍保持暂停；所选速度在浏览器允许本地存储时跨刷新与首页／历史页保留。离线预览同样提供这套控件，使用当前前端源码生成；修改界面后可从仓库根目录执行：

```powershell
.\lecture-syllabus-generator\backend\.venv\Scripts\python.exe lecture-syllabus-generator/scripts/build_frontend_preview.py
```

进度页打开时先检查已保存结果；已有大纲不会因刷新自动重新识别或生成。失败页重试前重新读取任务与页面状态，运行中的任务只检查状态。重新生成失败时保留旧稿；请求响应丢失时先查询服务器结果，避免未经确认覆盖新修改。

## 模型与上传配置

编辑 `lecture-syllabus-generator/backend/.env`：

```dotenv
APP_MODEL_PROVIDER=mock
APP_CLUSTER_PROVIDER=rule
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

### 按主题聚类并保留原文与来源

`APP_CLUSTER_PROVIDER` 独立控制聚类方式，修改配置后重启后端：

- `rule`（默认）：沿用按首个来源页分组的规则，不调用聚类模型。
- `model`：使用上述 `APP_MODEL_*` 连接配置调用模型，根据知识点内容跨页归组。服务商需要支持 Chat Completions 的文本输入及 `response_format: {"type": "json_object"}`。

真实图片识别和主题聚类同时启用的配置为：

```dotenv
APP_MODEL_PROVIDER=multimodal
APP_CLUSTER_PROVIDER=model
# 同时配置 APP_MODEL_API_KEY、APP_MODEL_BASE_URL 和 APP_MODEL_NAME
```

也可以使用 `APP_MODEL_PROVIDER=mock` 加 `APP_CLUSTER_PROVIDER=model`，单独验证聚类接口；此时聚类输入仍是预设课程内容，不能用来评价真实图片识别质量。模型聚类始终需要有效密钥，不会因识别模式为 `mock` 而免除真实调用。

程序在去重后为本次聚类输入分配 `kp_1`、`kp_2` 等临时 ID，模型只能返回以下结构：

```json
{"modules": [{"title": "索引与查询优化", "point_ids": ["kp_1", "kp_3"]}, {"title": "事务", "point_ids": ["kp_2"]}]}
```

每个输入 ID 必须恰好出现一次。未知、重复或遗漏 ID，空模块、无效标题、额外字段、无效 JSON 和截断结果都会被拒绝。标题为最多 120 个字符的单行文本。程序使用 ID 恢复原始知识点对象，正文、知识点类型、来源类型和全部来源页码均不由模型重写；模块来源页码由程序求并集。同文但不同来源类型的知识点继续分别保留。临时 ID 只对本次聚类有效，不写入数据库，也不作为跨版本引用。

缺密钥、提示词缺失或损坏返回 `CLUSTER_CONFIG_ERROR`；聚类响应无效或服务失败返回 `CLUSTERING_FAILED`，超时返回 `MODEL_TIMEOUT`。仅对超时、连接故障和 HTTP 408、429、5xx 按 `APP_MODEL_MAX_RETRY` 有限重试，格式与 ID 校验失败不自动重试。失败时保留原有大纲和知识点，任务标记失败，不自动降级为规则结果；需要时将配置改为 `rule` 并重启。聚类提示词位于 `backend/prompts/cluster.yaml`，修改后也需重启以刷新缓存。

### 上传与任务创建约定

`POST /api/tasks` 保持 `task_id`、`page_count`、`rejected` 的成功响应结构。允许部分接收：不支持的扩展名、空文件和超限文件进入拒绝列表，有效文件按指定顺序保存，并从 1 开始连续编号；`page_count` 与实际保存的页面数量一致。全部被拒绝时返回 400，不创建空任务。

`order` 为空时采用上传顺序；非空时必须完整包含本批原始上传文件的编号（从 1 开始），每个编号只能出现一次。缺失、重复、越界、非整数和过长参数返回 `INVALID_FILE_ORDER`，不写入任务或文件。被拒绝文件会在排序后过滤，因此有效页面不会出现页码空洞。

业务层按最多 64 KiB 分块读取，并使用实际字节数校验大小。文件先在存储目录内独占暂存、刷新，再整体移动到唯一目录；Task 和 Page 通过一次数据库提交保存。普通读取、写入、发布和数据库失败会回滚并清理本次目录，不清理已有任务文件。新任务目录为 `task-<任务ID>-<随机值>`，旧任务继续按数据库中的 `file_path` 访问，无需迁移文件。

数据库提交报错后会使用独立连接核对：确认已提交则保留文件并返回成功；无法确认时保留文件并返回 `UPLOAD_STATE_UNCERTAIN`（`retryable=false`），应先检查历史记录和服务日志，避免重复上传。清理失败返回 `UPLOAD_CLEANUP_ERROR`，需要维护者核对残留目录；普通保存故障返回可重试的 `UPLOAD_PERSISTENCE_ERROR`。

这些保证覆盖请求处理期间的普通异常。强制结束进程、断电后的残留目录恢复、请求进入业务层之前的传输限流，以及图片/PDF 内容解码校验不在本轮范围内；类型目前仍按扩展名判断。验证过程与边界见[上传可靠性验证记录](docs/verification/2026-10-16-upload-reliability.md)。

## 测试

测试覆盖健康信息、上传格式校验、来源标签解析、分阶段识别与生成中的来源保留、跨页去重、编辑保存后重新打开和 Word 内容比对，以及超时、断连、部分失败、重试和异常恢复。

**pytest 会在导入应用之前创建独立临时数据库和上传目录，强制使用模拟识别和默认规则聚类；测试不会清空日常使用的 `backend/data/app.db`。** 每个用例重置临时数据库，整轮结束后清理测试目录。模型识别与聚类测试使用本地模拟传输，不发送真实 API 请求。

聚类测试覆盖跨页分组、完整且唯一的 ID 分配、拒绝模型改写字段、来源保留、有限重试、保存后重新打开和 Word 内容比对，以及重新生成失败时保留旧数据。

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

前端交互逻辑可在仓库根目录使用 Node.js 检查，无需安装 npm 依赖：

```powershell
node --test lecture-syllabus-generator/frontend/tests/*.test.cjs
```

这些用例覆盖记录展示、空状态、网络失败与重试、时间转换、背景调速、进度恢复、编辑草稿保留与结果未知时的只读恢复，不调用真实接口。编辑中禁止导出尚未保存的内容；重新生成的响应或新结果读取失败时，先重新加载当前结果，再开放修改和导出。

安装测试依赖与 Node.js 后，也可从仓库根目录一次运行全部工程检查：

```powershell
pwsh -NoProfile -File lecture-syllabus-generator/scripts/verify_exp03.ps1
```

### 已有数据库升级与来源保留

启动时会为旧 SQLite 数据库的 `page` 表补加可空的 `recognized_structured` 字段，保留原有记录，并可重复启动。新识别结果会将标题、知识点和来源类型一并保存；后续生成和重新生成复用这些数据。没有保存来源类型的旧记录无法自动恢复真实来源，重新生成时显示“来源待核对”。历史上已保存的大纲不会被批量改写。

相同文字但来源类型不同的条目分开保留；相同文字且来源类型相同的条目才合并来源页码。部分页面失败时仍处理成功页，全部失败时返回明确错误；重新生成失败时保留此前已保存的大纲与知识点。

## 当前限制

- 知识点去重仍使用文本规则；模型聚类只做主题归组，不做语义去重或知识点改写。默认仍使用来源页规则；模型聚类的真实课程质量与性能需要实测。
- 真实模型返回内容目前按文本行解析；未提供结构化来源时标记“来源待核对”，置信度仍使用固定值，识别质量与来源归因需要后续验证。
- 上传配置包含 PDF，但当前未实现多页 PDF 拆页；识别请求使用 `image_url` 格式，PDF 能否处理取决于服务端兼容性。演示时建议使用 JPG、JPEG 或 PNG。
- 默认绑定 `127.0.0.1:8000`，当前工程面向本地课堂演示，未提供用户认证或多用户数据隔离。

## 工程文档

- [EXP03 工程交付与验收](docs/exp03-delivery.md)
- [EXP03 本轮验证记录](docs/verification/2026-10-17-exp03-delivery.md)
- [EXP04 工程准备与接入待办](docs/exp04-readiness.md)
- [暖纸界面验证与分支整理决定](docs/verification/2026-10-16-warm-paper-and-branch-audit.md)
- [项目初始化与工程基线记录](doc1_text.txt)
- [开发任务清单与实现计划](doc2_text.txt)
- [模型聚类与来源保留验证记录](docs/verification/2026-10-15-model-clustering.md)

两份文档记录了课程工程基线和开发计划，其中的历史验证结果以文档编制时的记录为准，当前运行情况应以实际测试为准。

---

<a name="english"></a>

# Classroom PPT Photo Outline Generator

[简体中文](#chinese) | **English**

A classroom slide photo organizer built around multimodal large language models. It turns classroom photos into editable study outlines with traceable sources and exports them as Word documents. This repository is a software engineering course project, with the internal project name `lecture-syllabus-generator`.

The current version includes a locally runnable backend and frontend, a mock workflow, and prototype entry points for multimodal model calls. The default `mock` mode demonstrates the complete workflow without an API key. Its output is predefined database course content, not a recognition result derived from the uploaded photos.

The current delivery stage is EXP03: a runnable application, a complete mock workflow, error recovery, automated verification, and delivery documentation. EXP04 preparation covers interfaces and future integration requirements; this delivery adds no new live AI service. See [EXP03 engineering delivery and acceptance](docs/exp03-delivery.md) for the agreed scope and acceptance criteria, and [EXP04 readiness](docs/exp04-readiness.md) for the next stage.

## Features and current implementation

| Feature | Current implementation |
| --- | --- |
| Batch upload | Upload classroom images, adjust their order, and organize content by logical page number |
| Content recognition | Three recognition modes: `mock`, `multimodal`, and `fallback` |
| Knowledge point extraction | Extract points from structured results or text lines; deduplicate across pages using normalized text |
| Module organization | Group by source page by default; optionally use a model for topic grouping across pages, returning only module titles and existing knowledge point IDs |
| Outline generation and review | Generate Markdown outlines, edit them online, save changes, and record versions |
| Source display | Store and display source page numbers and source types; mark missing source information as “来源待核对” (source needs verification) |
| Word export | Export outlines as `.docx` files |
| History | View existing tasks, reopen outlines, and export them again |

Workflow: upload photos → adjust order → recognize and extract content → generate an outline → review and save → export to Word.

## Technology stack

- Backend: Python, FastAPI, Uvicorn, and Pydantic.
- Storage: SQLAlchemy and SQLite; uploaded files are stored locally.
- Frontend: plain HTML, CSS, and JavaScript served by FastAPI, with no Node.js build step.
- Model calls: HTTPX with a multimodal API compatible with Chat Completions.
- Document export and testing: python-docx and pytest.

## Repository layout

```text
.
├── README.md                         # Repository documentation
├── frontend-preview.html             # Standalone frontend preview
├── .gitignore                        # Local configuration, caches, and runtime data
├── doc1_text.txt                      # Project initialization and engineering baseline
├── doc2_text.txt                      # Development tasks and implementation plan
└── lecture-syllabus-generator/
    ├── README.md                     # Application directory guide
    ├── backend/
    │   ├── app/
    │   │   ├── main.py               # FastAPI entry point
    │   │   ├── config.py             # Environment variables and configuration
    │   │   ├── db.py                 # Database connection and initialization
    │   │   ├── models.py             # Data models
    │   │   ├── schemas.py            # API data schemas
    │   │   ├── errors.py             # Shared error handling
    │   │   ├── prompts_loader.py     # Prompt loader
    │   │   ├── routers/              # Task, outline, export, and metadata APIs
    │   │   └── services/             # Recognition, extraction, grouping, and export
    │   ├── db/schema.sql             # Reference database schema
    │   ├── prompts/                  # Recognition, extraction, and clustering prompts
    │   ├── tests/                    # Tests
    │   ├── .env.example              # Configuration template
    │   ├── requirements.txt          # Runtime dependencies
    │   ├── requirements-dev.txt      # Test dependencies
    │   └── run.py                    # Local startup entry point
    ├── frontend/                     # Upload, progress, outline, and history pages
    └── scripts/                      # Windows / macOS / Linux startup scripts
```

`backend/data/` and `backend/storage/` are created at runtime for the database and uploaded files. They are excluded from version control.

## Quick start

Install Git and Python 3.10 or later. The commands below use the repository's default directory name.

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

If `.env` is already configured, keep the existing file. Start the application from the `backend` directory because the database path and environment configuration use the working directory. On subsequent runs, use the Python interpreter in the same virtual environment; dependencies do not need to be reinstalled.

After startup, open:

| Entry point | URL |
| --- | --- |
| Upload page | http://127.0.0.1:8000/ |
| History | http://127.0.0.1:8000/history.html |
| API documentation | http://127.0.0.1:8000/docs |
| Health check | http://127.0.0.1:8000/api/health |
| Engineering baseline metadata | http://127.0.0.1:8000/api/meta |

On Windows, you can double-click `lecture-syllabus-generator/scripts/start_backend.bat`. The script first uses `backend/.venv/Scripts/python.exe`; it uses `python` from the current environment only if the project virtual environment is absent. If dependencies are missing or startup fails, the window stays open and displays a message. On macOS/Linux, activate a Python environment with the dependencies installed, then run `bash scripts/start_backend.sh` from the application directory. That script uses `python` from the current environment.

### Frontend pages and offline preview

The upload and history pages share a warm paper palette, serif headings, and spacious layouts, following the system's light or dark theme. Mathematical formulas and code slowly move upward in the background, with a default opacity of 30%. The upload page retains file selection, reordering, removal, and task submission. History lists task titles, statuses, page counts, and creation times, with open and export actions.

To preview the design, open [`frontend-preview.html`](frontend-preview.html) at the repository root in a browser. No backend or network connection is required. It initially displays sample history records, can switch to an empty state, and offers “新建整理” (new outline) to show the upload page. You can select files and see their names, but the preview does not submit tasks. Sample records are not real task data; use the running application to open or export actual outlines.

The pages respect the system's reduced motion setting by default. If the background is still, click “播放背景” (play background) in the upper right to start it, then “暂停背景” (pause background) to stop it. No system setting needs to be changed. Both pages share `frontend/css/home.css` and `frontend/js/knowledge-flow.js`; additional history styles are in `frontend/css/history.css`. No frontend build tool or external CDN is required.

Click “速度” (speed) in the upper right to expand a slider and adjust the upward movement between 0.25× and 3×. Arrow keys provide finer control. Adjusting speed while paused keeps the background paused. When browser local storage is available, the selected speed persists across reloads and between the upload and history pages. The offline preview includes the same controls and is generated from the current frontend source. After changing the interface, rebuild it from the repository root:

```powershell
.\lecture-syllabus-generator\backend\.venv\Scripts\python.exe lecture-syllabus-generator/scripts/build_frontend_preview.py
```

The progress page first checks for saved results. Reloading an existing outline does not automatically recognize images or generate it again. Retrying failed pages first reloads task and page states; a running task is only checked for status. Failed regeneration preserves the previous outline. If a response is lost, the page queries the server before allowing another operation to overwrite newer edits.

## Model and upload configuration

Edit `lecture-syllabus-generator/backend/.env`:

```dotenv
APP_MODEL_PROVIDER=mock
APP_CLUSTER_PROVIDER=rule
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

These are the project template defaults. When integrating a service, use the actual provider's endpoint and the name of a model that supports image input.

- `mock`: demonstrate the local workflow using predefined results.
- `multimodal`: send requests to `/chat/completions` under `APP_MODEL_BASE_URL`. A valid key is required for live calls; the current implementation falls back to mock results if the key is missing.
- `fallback`: return fallback content indicating that recognition is unavailable.

For live model recognition, set `APP_MODEL_PROVIDER` to `multimodal`, then configure the key, model name, and endpoint. `.env` is ignored by Git; only `.env.example`, with an empty key, is tracked.

### Topic clustering with original text and sources preserved

`APP_CLUSTER_PROVIDER` controls clustering independently. Restart the backend after changing it:

- `rule` (default): group by the first source page without calling a clustering model.
- `model`: use the `APP_MODEL_*` connection settings above to group knowledge points across pages by topic. The provider must support Chat Completions text input and `response_format: {"type": "json_object"}`.

To enable live image recognition and model-based topic clustering together:

```dotenv
APP_MODEL_PROVIDER=multimodal
APP_CLUSTER_PROVIDER=model
# Also configure APP_MODEL_API_KEY, APP_MODEL_BASE_URL, and APP_MODEL_NAME
```

You can also combine `APP_MODEL_PROVIDER=mock` with `APP_CLUSTER_PROVIDER=model` to test clustering independently. Its input is still predefined course content, so this combination cannot evaluate real image recognition quality. Model clustering always requires a valid key and makes a real call even when recognition is set to `mock`.

After deduplication, the application assigns temporary IDs such as `kp_1` and `kp_2` to the current clustering input. The model may return only this structure:

```json
{"modules": [{"title": "索引与查询优化", "point_ids": ["kp_1", "kp_3"]}, {"title": "事务", "point_ids": ["kp_2"]}]}
```

Each input ID must appear exactly once. Unknown, duplicate, or missing IDs, empty modules, invalid titles, extra fields, invalid JSON, and truncated results are rejected. Titles must be single-line text with no more than 120 characters. The application restores the original knowledge point objects by ID; the model does not rewrite their text, knowledge point types, source types, or source page numbers. Module source pages are computed as the union of their points' source pages. Identical text with different source types remains separate. Temporary IDs are valid only for the current clustering request; they are neither stored in the database nor used as references across versions.

A missing key or a missing or damaged prompt returns `CLUSTER_CONFIG_ERROR`. Invalid clustering output or service failure returns `CLUSTERING_FAILED`; a timeout returns `MODEL_TIMEOUT`. Retries are bounded by `APP_MODEL_MAX_RETRY` and apply only to timeouts, connection failures, and HTTP 408, 429, or 5xx responses. Format and ID validation failures are not automatically retried. On failure, the application preserves existing outlines and knowledge points, marks the task as failed, and does not silently switch to rule-based grouping. To use rules instead, set the provider to `rule` and restart. The clustering prompt is in `backend/prompts/cluster.yaml`; restart after editing it to refresh the prompt cache.

### Upload and task creation contract

`POST /api/tasks` retains the successful response fields `task_id`, `page_count`, and `rejected`. Partial acceptance is supported: unsupported extensions, empty files, and oversized files enter the rejection list. Valid files are saved in the specified order and receive consecutive logical page numbers starting at 1. `page_count` matches the number of saved pages. If all files are rejected, the endpoint returns 400 without creating an empty task.

When `order` is empty, upload order is used. Otherwise, it must contain every original file index in the batch, starting at 1, exactly once. Missing, duplicate, out-of-range, non-integer, or excessively long values return `INVALID_FILE_ORDER` without writing a task or files. Rejected files are filtered after ordering, so accepted pages have no gaps in their page numbers.

The service reads files in chunks of at most 64 KiB and validates their actual byte counts. Files are first written to an exclusive staging directory within storage, flushed, and then moved together to a unique directory. Task and Page records are saved in one database commit. Ordinary read, write, publication, and database failures roll back the request and clean up its directories without touching existing task files. New task directories use `task-<task ID>-<random value>`; older tasks continue to use their stored `file_path` values, without file migration.

If a database commit reports an error, an independent connection checks the outcome. A confirmed commit preserves the files and returns success. If the outcome cannot be confirmed, files are preserved and the endpoint returns `UPLOAD_STATE_UNCERTAIN` with `retryable=false`; check history and service logs before retrying to avoid duplicate uploads. Cleanup failure returns `UPLOAD_CLEANUP_ERROR` and requires a maintainer to inspect residual directories. Ordinary persistence failure returns the retryable `UPLOAD_PERSISTENCE_ERROR`.

These guarantees cover ordinary exceptions during request handling. Recovery of residual directories after forced process termination or power loss, transport limits before the request reaches the service, and image/PDF content decoding are outside this delivery. File type is currently checked by extension. See the [upload reliability verification record](docs/verification/2026-10-16-upload-reliability.md) for the checks and boundaries.

## Testing

Tests cover health metadata, upload validation, source tag parsing, source preservation across staged recognition and generation, cross-page deduplication, saved edits after reopening, Word content comparison, timeouts, disconnections, partial failures, retries, and error recovery.

**Before importing the application, pytest creates an isolated temporary database and upload directory and forces mock recognition with default rule-based clustering. Tests do not clear the everyday database at `backend/data/app.db`.** Each test resets the temporary database, and the test directory is removed at the end of the run. Recognition and clustering tests use simulated HTTP transports without making real API requests.

Clustering tests cover cross-page grouping, complete and unique ID assignment, rejection of model-rewritten fields, source preservation, saving and reopening, Word content comparison, bounded retries, and preservation of old data when regeneration fails.

Install dependencies and run tests from the `backend` directory:

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

Create the virtual environment using the quick start instructions before the first run. Tests configure their isolated environment automatically; `.env` does not need to be changed. These tests do not establish real model recognition quality or replace manual browser acceptance checks.

Frontend interaction tests can run from the repository root using Node.js, without installing npm dependencies:

```powershell
node --test lecture-syllabus-generator/frontend/tests/*.test.cjs
```

These cases cover history rendering, empty states, network failures and retries, time conversion, background speed controls, progress recovery, preservation of editing drafts, and read-only recovery when a result is unconfirmed. They do not call real APIs. Export is disabled while editing unsaved content. If regeneration's response or the subsequent result fetch fails, the current result must be reloaded before editing and export are enabled again.

After installing the test dependencies and Node.js, you can run all engineering checks from the repository root with:

```powershell
pwsh -NoProfile -File lecture-syllabus-generator/scripts/verify_exp03.ps1
```

### Existing database upgrades and source preservation

At startup, older SQLite databases receive a nullable `recognized_structured` column in the `page` table. Existing records are preserved, and initialization can run repeatedly. New recognition results store titles, knowledge points, and source types together, and subsequent generation reuses them. The actual source types of older records that never stored this information cannot be recovered automatically; regeneration marks them as “来源待核对” (source needs verification). Previously saved outlines are not rewritten in bulk.

Points with identical text but different source types remain separate. Source page numbers are merged only when both the normalized text and source type match. If some pages fail, successful pages can still be processed. If all pages fail, the application returns an explicit error. Failed regeneration preserves the previously saved outline and knowledge points.

## Current limitations

- Deduplication still uses text rules. Model clustering only groups topics; it does not perform semantic deduplication or rewrite points. The default remains source-page grouping. Model clustering quality and performance on real courses require measurement.
- Live model output is currently parsed as text lines. Missing structured source information is marked as “来源待核对” (source needs verification), and confidence values are fixed. Recognition quality and source attribution still need validation.
- Upload settings include PDF, but multi-page PDF splitting is not implemented. Recognition requests use `image_url`, so PDF handling depends on provider compatibility. Use JPG, JPEG, or PNG for demonstrations.
- The default address is `127.0.0.1:8000`. The application is intended for local classroom demonstrations and does not provide user authentication or data isolation between multiple users.

## Engineering documentation

The linked engineering records are currently in Chinese.

- [EXP03 engineering delivery and acceptance](docs/exp03-delivery.md)
- [EXP03 verification record](docs/verification/2026-10-17-exp03-delivery.md)
- [EXP04 readiness and integration backlog](docs/exp04-readiness.md)
- [Warm paper UI verification and branch audit decisions](docs/verification/2026-10-16-warm-paper-and-branch-audit.md)
- [Project initialization and engineering baseline](doc1_text.txt)
- [Development tasks and implementation plan](doc2_text.txt)
- [Model clustering and source preservation verification](docs/verification/2026-10-15-model-clustering.md)

The two baseline documents record the course project's engineering baseline and development plan. Historical verification results reflect the state when those documents were written; use current test results to assess the application today.

[Back to language navigation](#language-navigation)
