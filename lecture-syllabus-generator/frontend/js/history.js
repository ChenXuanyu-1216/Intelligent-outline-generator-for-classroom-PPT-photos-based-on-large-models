async function loadHistory() {
    const resp = await API.listTasks();
    const list = document.getElementById("task-list");
    if (!resp.ok) {
        list.innerHTML = '<p class="error">加载失败</p>';
        return;
    }
    const data = await resp.json();
    if (data.tasks.length === 0) {
        list.innerHTML = '<p class="loading">暂无历史记录</p>';
        return;
    }
    list.innerHTML = "";
    data.tasks.forEach(task => {
        const card = document.createElement("div");
        card.className = "task-card";
        const date = new Date(task.created_at).toLocaleString("zh-CN");
        card.innerHTML = `
            <div class="task-info">
                <h3>任务 #${task.task_id} <span class="status-badge status-${task.status}">${task.status}</span></h3>
                <p>${task.page_count} 页 · ${date}</p>
            </div>
            <div class="task-actions">
                <a class="btn btn-secondary" href="/outline.html?task_id=${task.task_id}">打开</a>
                <a class="btn btn-primary" href="/api/tasks/${task.task_id}/export">导出</a>
            </div>
        `;
        list.appendChild(card);
    });
}

loadHistory();