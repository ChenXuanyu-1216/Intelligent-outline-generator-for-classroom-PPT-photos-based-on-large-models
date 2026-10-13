const params = new URLSearchParams(window.location.search);
const taskId = params.get("task_id");

if (!taskId) {
    window.location.href = "/";
}

const outlineView = document.getElementById("outline-view");
const outlineEditor = document.getElementById("outline-editor");
const editBtn = document.getElementById("edit-btn");
const saveBtn = document.getElementById("save-btn");
const cancelEditBtn = document.getElementById("cancel-edit-btn");
const regenerateBtn = document.getElementById("regenerate-btn");
const exportBtn = document.getElementById("export-btn");

let currentMarkdown = "";

async function loadOutline() {
    const resp = await API.getOutline(taskId);
    if (!resp.ok) {
        const err = await resp.json();
        outlineView.innerHTML = `<p class="error">加载失败：${err.message}</p>`;
        return;
    }
    const data = await resp.json();
    currentMarkdown = data.markdown;
    renderMarkdown(currentMarkdown);
}

function renderMarkdown(md) {
    const lines = md.split("\n");
    let html = "";
    let inList = false;
    for (const line of lines) {
        const trimmed = line.trim();
        if (!trimmed) { if (inList) { html += "</ul>"; inList = false; } continue; }
        if (trimmed.startsWith("# ")) {
            if (inList) { html += "</ul>"; inList = false; }
            html += `<h1>${escapeHtml(trimmed.slice(2))}</h1>`;
        } else if (trimmed.startsWith("## ")) {
            if (inList) { html += "</ul>"; inList = false; }
            html += `<h2>${escapeHtml(trimmed.slice(3))}</h2>`;
        } else if (trimmed.startsWith("- ")) {
            if (!inList) { html += "<ul>"; inList = true; }
            html += `<li>${renderSourceTags(trimmed.slice(2))}</li>`;
        } else {
            if (inList) { html += "</ul>"; inList = false; }
            html += `<p>${escapeHtml(trimmed)}</p>`;
        }
    }
    if (inList) html += "</ul>";
    outlineView.innerHTML = html;
}

function renderSourceTags(text) {
    let result = escapeHtml(text);
    result = result.replace(/（来源：([^）]+)）/g, '<span class="source-tag">（来源：$1）</span>');
    result = result.replace(/【课堂原话】/g, '<span class="type-original">【课堂原话】</span>');
    result = result.replace(/【AI推断】/g, '<span class="type-ai">【AI推断】</span>');
    return result;
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text;
    return div.innerHTML;
}

editBtn.addEventListener("click", () => {
    outlineView.classList.add("hidden");
    outlineEditor.classList.remove("hidden");
    outlineEditor.value = currentMarkdown;
    editBtn.classList.add("hidden");
    saveBtn.classList.remove("hidden");
    cancelEditBtn.classList.remove("hidden");
});

saveBtn.addEventListener("click", async () => {
    const resp = await API.updateOutline(taskId, outlineEditor.value);
    if (!resp.ok) {
        const err = await resp.json();
        alert(`保存失败：${err.message}`);
        return;
    }
    currentMarkdown = outlineEditor.value;
    renderMarkdown(currentMarkdown);
    outlineView.classList.remove("hidden");
    outlineEditor.classList.add("hidden");
    editBtn.classList.remove("hidden");
    saveBtn.classList.add("hidden");
    cancelEditBtn.classList.add("hidden");
});

cancelEditBtn.addEventListener("click", () => {
    outlineView.classList.remove("hidden");
    outlineEditor.classList.add("hidden");
    editBtn.classList.remove("hidden");
    saveBtn.classList.add("hidden");
    cancelEditBtn.classList.add("hidden");
});

regenerateBtn.addEventListener("click", async () => {
    if (!confirm("重新生成将覆盖当前大纲，是否继续？")) return;
    const resp = await API.regenerate(taskId);
    if (!resp.ok) {
        const err = await resp.json();
        alert(`重新生成失败：${err.message}`);
        return;
    }
    await loadOutline();
});

exportBtn.addEventListener("click", async () => {
    const resp = await API.exportWord(taskId);
    if (!resp.ok) {
        const err = await resp.json();
        alert(`导出失败：${err.message}`);
        return;
    }
    const blob = await resp.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `outline_${taskId}.docx`;
    a.click();
    URL.revokeObjectURL(url);
});

loadOutline();