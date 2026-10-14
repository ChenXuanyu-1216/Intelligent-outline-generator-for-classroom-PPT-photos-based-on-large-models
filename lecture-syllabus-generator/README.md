# lecture-syllabus-generator

基于多模态大模型的课堂 PPT 照片智能大纲生成器，包含 FastAPI 后端和原生 HTML/CSS/JavaScript 前端。

完整的功能说明、安装步骤、模型配置、测试方法和当前限制见[仓库 README](../README.md)。

## 应用目录

- `backend/`：后端接口、识别与大纲处理流程、提示词和测试。
- `frontend/`：上传、处理进度、大纲编辑、历史记录四个页面。
- `scripts/`：Windows 和 macOS/Linux 启动脚本。

默认使用 `mock` 模式，返回预设课程内容。真实图片识别需要配置兼容的多模态模型服务。

## 已安装依赖后的启动方式

从当前目录进入 `backend`，使用已安装 `requirements.txt` 的 Python 环境启动：

```powershell
cd backend
.\.venv\Scripts\python.exe run.py
```

macOS / Linux 对应命令为 `.venv/bin/python run.py`。启动后访问 http://127.0.0.1:8000/ 。

运行测试前请阅读[测试说明](../README.md#测试)：pytest 自动使用独立临时数据库和上传目录，不清理日常数据库，也不调用真实模型。
