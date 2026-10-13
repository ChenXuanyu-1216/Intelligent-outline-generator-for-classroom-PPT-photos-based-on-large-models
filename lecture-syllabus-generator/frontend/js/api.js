const API = {
    async createTask(files, order) {
        const formData = new FormData();
        files.forEach(f => formData.append("files", f));
        if (order) formData.append("order", order);
        const resp = await fetch("/api/tasks", { method: "POST", body: formData });
        return resp;
    },
    async getTask(taskId) {
        const resp = await fetch(`/api/tasks/${taskId}`);
        return resp;
    },
    async getPages(taskId) {
        const resp = await fetch(`/api/tasks/${taskId}/pages`);
        return resp;
    },
    async recognize(taskId, pageNo) {
        const url = pageNo ? `/api/tasks/${taskId}/recognize?page_no=${pageNo}` : `/api/tasks/${taskId}/recognize`;
        const resp = await fetch(url, { method: "POST" });
        return resp;
    },
    async runPipeline(taskId) {
        const resp = await fetch(`/api/tasks/${taskId}/pipeline`, { method: "POST" });
        return resp;
    },
    async getOutline(taskId) {
        const resp = await fetch(`/api/tasks/${taskId}/outline`);
        return resp;
    },
    async updateOutline(taskId, markdown) {
        const resp = await fetch(`/api/tasks/${taskId}/outline`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ markdown }),
        });
        return resp;
    },
    async regenerate(taskId) {
        const resp = await fetch(`/api/tasks/${taskId}/regenerate`, { method: "POST" });
        return resp;
    },
    async exportWord(taskId) {
        const resp = await fetch(`/api/tasks/${taskId}/export`);
        return resp;
    },
    async listTasks() {
        const resp = await fetch("/api/tasks");
        return resp;
    },
    async getMeta() {
        const resp = await fetch("/api/meta");
        return resp;
    },
};