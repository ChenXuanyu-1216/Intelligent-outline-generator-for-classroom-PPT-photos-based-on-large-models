(() => {
    const taskId = new URLSearchParams(window.location.search).get("task_id");
    if (!/^[1-9]\d*$/.test(taskId || "")) { window.location.href = "/"; return; }
    const byId = id => document.getElementById(id);
    const retryButton = byId("retry-btn");
    const continueButton = byId("continue-btn");
    const viewButton = byId("view-outline");
    let busy = false;
    let failedPages = [];
    let hasOutline = false;
    let observedRunning = false;
    let generationPending = false;
    function show(id, visible) { byId(id).classList[visible ? "remove" : "add"]("hidden"); }
    function step(id, state, label) {
        const node = byId(`step-${id}`);
        node.classList.remove("active", "done");
        if (state) node.classList.add(state);
        node.querySelector(".step-status").textContent = label || (state === "done" ? "完成" : "等待中");
    }
    async function read(response) {
        let data;
        try { data = await response.json(); } catch { throw new Error("服务返回的数据无法读取，请重试。"); }
        if (!response.ok) {
            const error = new Error(data.message || "请求失败，请重试。");
            error.retryable = data.retryable !== false;
            throw error;
        }
        return data;
    }
    async function guarded(action) {
        if (busy) return;
        busy = true;
        retryButton.disabled = continueButton.disabled = true;
        show("progress-error", false);
        show("continue-btn", false);
        try { await action(); } catch (error) {
            byId("progress-title").textContent = "处理暂未完成";
            byId("progress-error-message").textContent = error.message || "连接中断，请检查网络后重试。";
            show("progress-error", true);
            show("continue-btn", error.retryable !== false);
            continueButton.textContent = "重新检查并继续";
        } finally {
            busy = false;
            retryButton.disabled = continueButton.disabled = false;
        }
    }
    function displayPages(pages) {
        if (!Array.isArray(pages)) throw new Error("页级数据不完整，请重新检查。");
        failedPages = pages.filter(page => page.failed_flag);
        const lowPages = pages.filter(page => page.low_confidence_flag);
        for (const [id, entries, failed] of [["low-confidence-pages", lowPages, false], ["failed-page-list", failedPages, true]]) {
            const list = byId(id);
            list.replaceChildren();
            for (const page of entries) {
                const item = document.createElement("li");
                item.textContent = `P${page.page_no}（${page.filename}）${failed ? `：${page.error_msg || "识别失败"}` : ""}`;
                list.appendChild(item);
            }
        }
        show("low-confidence-warning", lowPages.length > 0);
        show("failed-pages", failedPages.length > 0);
        show("retry-btn", failedPages.length > 0 && !observedRunning);
    }
    async function refreshPages() {
        const data = await read(await API.getPages(taskId));
        displayPages(data.pages);
        return data.pages;
    }
    function completed() {
        hasOutline = true;
        for (const id of ["recognize", "extract", "cluster", "generate"]) step(id, "done");
        if (failedPages.length) step("recognize", "done", "部分完成");
        byId("progress-title").textContent = failedPages.length ? "部分页面已整理" : "整理完成";
        byId("progress-message").textContent = failedPages.length ? "已保留成功页面的结果，可查看大纲或重试失败页。" : "大纲已保存，可继续校对和导出。";
        viewButton.href = `/outline.html?task_id=${taskId}`;
        show("view-outline", true);
    }
    async function generate() {
        generationPending = true;
        step("recognize", "done");
        // The backend combines these stages and does not report separate progress.
        step("extract", "active", "抽取、归组与生成中…");
        step("cluster", "", "由后端统一处理");
        step("generate", "", "由后端统一处理");
        byId("progress-message").textContent = "正在使用已保存的识别结果生成大纲。";
        await read(await API.runPipeline(taskId));
        generationPending = false;
        completed();
    }
    async function restore(allowRetry = false) {
        const task = await read(await API.getTask(taskId));
        if (!task.status) throw new Error("任务状态无法读取，请重新检查。");
        observedRunning = task.status === "running";
        await refreshPages();
        const outline = await API.getOutline(taskId);
        if (outline.ok) {
            const saved = await read(outline);
            if (typeof saved.markdown !== "string") throw new Error("大纲数据无法读取，请重新检查。");
            hasOutline = true;
            viewButton.href = `/outline.html?task_id=${taskId}`;
            viewButton.textContent = "查看已保存大纲";
            show("view-outline", true);
            if (generationPending && task.status === "success") {
                generationPending = false;
                completed();
                byId("progress-title").textContent = "已恢复服务器保存的大纲";
                byId("progress-message").textContent = "上次响应未确认，现已读取服务器当前版本；需要重新生成时，请在大纲页确认操作。";
                return;
            }
            if (observedRunning || task.status === "failed" || generationPending) {
                byId("progress-title").textContent = observedRunning ? "任务正在处理" : "上次生成未完成或结果未确认";
                byId("progress-message").textContent = (task.error_msg || "请检查处理状态。") + "已有大纲已保留。";
                continueButton.textContent = observedRunning ? "刷新处理状态" : "重试生成";
                show("continue-btn", true);
                if (allowRetry && !observedRunning && confirm("重新生成将覆盖已保存的大纲，是否继续？")) await generate();
                return;
            }
            completed();
            return;
        }
        // Only the explicit existing contract means no outline has been generated.
        const absent = await outline.json();
        if (absent.code !== "PIPELINE_ERROR") {
            const error = new Error(absent.message || "无法查询已有大纲，请重新检查。");
            error.retryable = absent.retryable !== false;
            throw error;
        }
        hasOutline = false;
        show("view-outline", false);
        if (task.status === "running") {
            byId("progress-title").textContent = "任务正在处理";
            byId("progress-message").textContent = "后台处理中，请稍后检查状态。";
            continueButton.textContent = "刷新处理状态";
            show("continue-btn", true);
            return;
        }
        if (failedPages.length) {
            byId("progress-title").textContent = "有页面需要重试";
            byId("progress-message").textContent = "请先重试失败页，再生成大纲。";
            return;
        }
        if (task.status === "failed" && !allowRetry) {
            byId("progress-title").textContent = "上次生成未完成";
            byId("progress-message").textContent = task.error_msg || "已保留页面数据，可手动继续生成。";
            show("continue-btn", true);
            return;
        }
        if (task.status === "pending") {
            step("recognize", "active", "识别中…");
            await read(await API.recognize(taskId));
            const pages = await refreshPages();
            if (pages.every(page => page.failed_flag)) {
                byId("progress-title").textContent = "所有页面识别失败";
                byId("progress-message").textContent = "请检查页面提示并重试。";
                return;
            }
        }
        await generate();
    }
    retryButton.addEventListener("click", () => {
        if (busy) return;
        if (hasOutline && !confirm("重试失败页后将重新生成并覆盖当前大纲，是否继续？")) return;
        return guarded(async () => {
            const task = await read(await API.getTask(taskId));
            if (task.status === "running") {
                observedRunning = true;
                show("retry-btn", false);
                show("continue-btn", true);
                byId("progress-message").textContent = "后台处理中，请稍后检查状态。";
                return;
            }
            observedRunning = false;
            await refreshPages();
            const retryPages = [...failedPages];
            step("recognize", "active", "重试失败页…");
            for (const page of retryPages) await read(await API.recognize(taskId, page.page_no));
            const pages = await refreshPages();
            if (pages.every(page => page.failed_flag)) {
                byId("progress-message").textContent = "页面仍识别失败，请检查提示后再次重试。";
                return;
            }
            await generate();
        });
    });
    continueButton.addEventListener("click", () => guarded(() => restore(true)));
    return guarded(restore);
})();
