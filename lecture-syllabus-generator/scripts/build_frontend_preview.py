"""Build a self-contained, offline UI preview from the current frontend assets."""
from pathlib import Path
import re

APP_DIR = Path(__file__).resolve().parents[1]
FRONTEND = APP_DIR / "frontend"


def build_preview() -> Path:
    history = (FRONTEND / "history.html").read_text(encoding="utf-8")
    upload = (FRONTEND / "index.html").read_text(encoding="utf-8")
    main = re.search(r"  <main\b[\s\S]*?</main>", upload).group()
    main = main.replace('<main class="kf-main">', '<main class="kf-main" id="preview-upload" hidden>')
    history = history.replace('<main class="kf-main">', '<main class="kf-main" id="preview-history">')
    tools = '''<div class="kf-preview-tools">
      <p>样式预览 · 示例记录，打开与导出请使用运行中的系统。</p>
      <button id="preview-empty" type="button">查看空记录</button>
      <p id="preview-message" role="status"></p>
    </div>'''
    history = history.replace("</main>", tools + "</main>\n" + main, 1)
    history = re.sub(r'\s*<link rel="stylesheet"[^>]+>', "", history)
    history = re.sub(r'\s*<script src="[^"]+"></script>', "", history)
    history = history.replace("<title>整理记录 · 课堂大纲</title>", "<title>课堂大纲 · 离线预览</title>")
    css = "\n".join((FRONTEND / "css" / name).read_text(encoding="utf-8") for name in ["home.css", "history.css"])
    css += '''
    #knowledge-flow-home .kf-preview-tools { margin: 20px 0; text-align: center; color: var(--kf-muted); font-size: 12px; }
    #knowledge-flow-home .kf-preview-tools button { margin-top: 8px; border: 0; padding: 8px 14px; border-radius: 7px; background: var(--kf-wash); color: var(--kf-ink); }
    '''
    csp = '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; script-src \'unsafe-inline\'; style-src \'unsafe-inline\'; img-src data:; connect-src \'none\'; base-uri \'none\'; form-action \'none\'">'
    history = history.replace("</head>", csp + "\n<style>" + css + "</style>\n</head>")
    renderer = (FRONTEND / "js" / "history.js").read_text(encoding="utf-8")
    motion = (FRONTEND / "js" / "knowledge-flow.js").read_text(encoding="utf-8")
    behavior = '''
    let empty = false;
    const samples = [
      {task_id: 3, title: '高等数学：微积分', status: 'success', page_count: 12, created_at: '2026-10-17T03:20:00Z'},
      {task_id: 2, title: '数据结构：树与遍历', status: 'partial', page_count: 8, created_at: '2026-10-16T07:45:00Z'},
      {task_id: 1, title: '大学物理：电磁学', status: 'success', page_count: 16, created_at: '2026-10-15T01:10:00Z'}
    ];
    const API = { listTasks: async () => ({ok: true, json: async () => ({tasks: empty ? [] : samples})}) };
    function renderHistory() { HISTORY_RENDERER }
    renderHistory();
    const root = document.getElementById('knowledge-flow-home');
    const historyPage = document.getElementById('preview-history');
    const uploadPage = document.getElementById('preview-upload');
    document.addEventListener('click', event => {
      const link = event.target.closest('a');
      if (!link) return;
      event.preventDefault();
      const target = link.getAttribute('href');
      if (target === '/' || target === '/history.html') {
        const showHistory = target === '/history.html';
        historyPage.hidden = !showHistory;
        uploadPage.hidden = showHistory;
        root.classList.toggle('kf-history-view', showHistory);
        root.querySelectorAll('.kf-nav-item').forEach(nav => {
          const current = nav.getAttribute('href') === target;
          nav.classList.toggle('kf-current', current);
          if (current) nav.setAttribute('aria-current', 'page'); else nav.removeAttribute('aria-current');
        });
      } else document.getElementById('preview-message').textContent = '这里是示例记录，请启动后端后使用打开与导出。';
    });
    document.getElementById('preview-empty').addEventListener('click', event => {
      empty = !empty;
      event.target.textContent = empty ? '查看示例记录' : '查看空记录';
      renderHistory();
    });
    function displayFiles(files) {
      const list = document.getElementById('file-list');
      list.replaceChildren();
      Array.from(files).forEach((file, index) => {
        const row = document.createElement('div'); row.className = 'kf-file-row';
        row.textContent = (index + 1) + '. ' + file.name; list.appendChild(row);
      });
      document.getElementById('file-count').textContent = files.length + ' 张';
    }
    document.getElementById('file-input').addEventListener('change', event => displayFiles(event.target.files));
    const drop = document.getElementById('drop-zone');
    drop.addEventListener('dragover', event => event.preventDefault());
    drop.addEventListener('drop', event => { event.preventDefault(); displayFiles(event.dataTransfer.files); });
    document.getElementById('generate-btn').textContent = '预览不提交任务';
    '''.replace("HISTORY_RENDERER", renderer)
    history = history.replace("</body>", "<script>\n" + behavior + "\n" + motion + "\n</script>\n</body>")
    destination = APP_DIR.parent / "frontend-preview.html"
    destination.write_text("\n".join(line.rstrip() for line in history.splitlines()) + "\n", encoding="utf-8")
    return destination


if __name__ == "__main__":
    print(build_preview())
