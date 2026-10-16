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
