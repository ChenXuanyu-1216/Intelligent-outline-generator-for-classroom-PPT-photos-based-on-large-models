(() => {
    const list = document.getElementById("task-list");
    const count = document.getElementById("task-count");
    const statuses = new Map([
        ["pending", "待处理"], ["running", "处理中"], ["success", "已完成"],
        ["failed", "处理失败"], ["partial", "部分完成"],
    ]);

    function element(tag, className, text) {
        const node = document.createElement(tag);
        node.className = className;
        if (text !== undefined) node.textContent = text;
        return node;
    }

    function showState(title, description, action) {
        const state = element("div", "kf-history-state");
        state.append(element("h3", "", title));
        if (description) state.append(element("p", "", description));
        if (action === "upload") {
            const link = element("a", "kf-history-action kf-history-primary", "新建整理");
            link.href = "/";
            state.append(link);
        } else if (action === "retry") {
            state.setAttribute("role", "alert");
            const retry = element("button", "kf-history-action kf-history-primary", "重新加载");
            retry.type = "button";
            retry.addEventListener("click", async () => {
                const hadFocus = document.activeElement === retry;
                await loadHistory();
                if (hadFocus && document.activeElement === document.body) {
                    const action = list.querySelector("button") || list.querySelector("a");
                    if (action) action.focus();
                }
            });
            state.append(retry);
        }
        list.replaceChildren(state);
    }

    function renderTask(task) {
        const record = element("article", "kf-record");
        const info = element("div", "kf-record-info");
        const heading = element("div", "kf-record-heading");
        const title = task.title && task.title !== "未命名任务" ? task.title : "课堂整理";
        const status = statuses.has(task.status) ? task.status : "unknown";
        heading.append(element("h3", "", title), element("span", `kf-status kf-status-${status}`, statuses.get(status) || "状态未知"));
        const meta = element("div", "kf-record-meta");
        // Existing API timestamps without an offset are stored as UTC.
        const timestamp = String(task.created_at);
        const date = new Date(/(?:Z|[+-]\d{2}:\d{2})$/i.test(timestamp) ? timestamp : `${timestamp}Z`);
        const time = element("time", "", Number.isNaN(date.getTime()) ? "时间未知" : date.toLocaleString("zh-CN", {
            year: "numeric", month: "2-digit", day: "2-digit", hour: "2-digit", minute: "2-digit", hour12: false,
        }));
        if (!Number.isNaN(date.getTime())) time.dateTime = date.toISOString();
        meta.append(element("span", "", `${task.page_count} 页`), time, element("span", "", `任务 #${task.task_id}`));
        info.append(heading, meta);
        const actions = element("div", "kf-record-actions");
        const id = encodeURIComponent(String(task.task_id));
        const open = element("a", "kf-history-action kf-record-open", "打开");
        open.href = `/outline.html?task_id=${id}`;
        open.setAttribute("aria-label", `打开${title}，任务 ${task.task_id}`);
        const exportLink = element("a", "kf-history-action kf-record-export", "导出 Word");
        exportLink.href = `/api/tasks/${id}/export`;
        exportLink.setAttribute("aria-label", `导出${title}为 Word，任务 ${task.task_id}`);
        actions.append(open, exportLink);
        record.append(info, actions);
        return record;
    }

    async function loadHistory() {
        list.setAttribute("aria-busy", "true");
        count.textContent = "读取中";
        showState("正在读取整理记录", "");
        try {
            const response = await API.listTasks();
            if (!response.ok) throw new Error("History request failed");
            const data = await response.json();
            if (!Array.isArray(data.tasks)) throw new Error("Invalid history response");
            const records = data.tasks.map(renderTask);
            count.textContent = `${records.length} 条记录`;
            if (records.length) list.replaceChildren(...records);
            else showState("还没有整理记录", "添加课堂照片后，整理记录会保存在这里。", "upload");
        } catch {
            count.textContent = "未加载";
            showState("暂时无法加载记录", "请检查网络连接，然后重新加载。", "retry");
        } finally {
            list.setAttribute("aria-busy", "false");
        }
    }

    return loadHistory();
})();
