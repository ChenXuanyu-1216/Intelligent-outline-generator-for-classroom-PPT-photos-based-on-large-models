const params = new URLSearchParams(window.location.search);
const taskId = params.get("task_id");

if (!taskId) {
    window.location.href = "/";
}

function setStepStatus(stepId, status) {
    const step = document.getElementById(stepId);
    step.classList.remove("active", "done");
    if (status === "active") step.classList.add("active");
    if (status === "done") step.classList.add("done");
    step.querySelector(".step-status").textContent =
        status === "active" ? "处理中..." : status === "done" ? "完成" : "等待中";
}

async function runPipeline() {
    setStepStatus("step-recognize", "active");
    const recognizeResp = await API.recognize(taskId);
    if (!recognizeResp.ok) {
        const err = await recognizeResp.json();
        alert(`识别失败：${err.message}`);
        return;
    }
    setStepStatus("step-recognize", "done");

    const pagesResp = await API.getPages(taskId);
    const pagesData = await pagesResp.json();
    const pages = pagesData.pages;

    const lowConfPages = pages.filter(p => p.low_confidence_flag);
    const failedPages = pages.filter(p => p.failed_flag);

    if (lowConfPages.length > 0) {
        document.getElementById("low-confidence-warning").classList.remove("hidden");
        const ul = document.getElementById("low-confidence-pages");
        lowConfPages.forEach(p => {
            const li = document.createElement("li");
            li.textContent = `P${p.page_no}（${p.filename}）`;
            ul.appendChild(li);
        });
    }

    if (failedPages.length > 0) {
        document.getElementById("failed-pages").classList.remove("hidden");
        const ul = document.getElementById("failed-page-list");
        failedPages.forEach(p => {
            const li = document.createElement("li");
            li.textContent = `P${p.page_no}（${p.filename}）：${p.error_msg || "未知错误"}`;
            ul.appendChild(li);
        });
        document.getElementById("retry-btn").classList.remove("hidden");
    }

    setStepStatus("step-extract", "active");
    setStepStatus("step-cluster", "active");
    setStepStatus("step-generate", "active");

    const pipelineResp = await API.runPipeline(taskId);
    if (!pipelineResp.ok) {
        const err = await pipelineResp.json();
        alert(`管道处理失败：${err.message}`);
        return;
    }
    const pipelineData = await pipelineResp.json();

    setStepStatus("step-extract", "done");
    setStepStatus("step-cluster", "done");
    setStepStatus("step-generate", "done");

    const viewBtn = document.getElementById("view-outline");
    viewBtn.href = `/outline.html?task_id=${taskId}`;
    viewBtn.classList.remove("hidden");
}

document.getElementById("retry-btn").addEventListener("click", async () => {
    const pagesResp = await API.getPages(taskId);
    const pagesData = await pagesResp.json();
    const failedPages = pagesData.pages.filter(p => p.failed_flag);
    for (const p of failedPages) {
        await API.recognize(taskId, p.page_no);
    }
    runPipeline();
});

runPipeline();