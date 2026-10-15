let selectedFiles = [];
let isUploading = false;

const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const fileList = document.getElementById("file-list");
const fileCount = document.getElementById("file-count");
const generateBtn = document.getElementById("generate-btn");

dropZone.addEventListener("dragover", (e) => {
    e.preventDefault();
    if (!isUploading) dropZone.classList.add("dragover");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    handleFiles(e.dataTransfer.files);
});
fileInput.addEventListener("change", (e) => handleFiles(e.target.files));

function handleFiles(files) {
    if (isUploading) return;
    selectedFiles = Array.from(files);
    fileInput.value = "";
    renderFileList();
}

function renderFileList() {
    fileList.replaceChildren();
    fileCount.textContent = `${selectedFiles.length} 张`;
    generateBtn.disabled = isUploading || selectedFiles.length === 0;
    generateBtn.textContent = isUploading ? "上传中..." : "生成大纲";
    fileInput.disabled = isUploading;
    dropZone.setAttribute("aria-disabled", String(isUploading));
    if (selectedFiles.length === 0) {
        const empty = document.createElement("p");
        empty.className = "kf-empty";
        empty.textContent = "还没有添加照片";
        fileList.appendChild(empty);
    }
    selectedFiles.forEach((file, index) => {
        const item = document.createElement("div");
        item.className = "kf-file-row";
        const order = document.createElement("span");
        order.className = "file-order";
        order.textContent = `P${index + 1}`;
        const name = document.createElement("span");
        name.className = "file-name";
        name.textContent = file.name;
        const controls = document.createElement("div");
        controls.className = "move-btns";
        const actions = [
            ["↑", `上移第 ${index + 1} 张照片`, () => moveFile(index, -1), index === 0],
            ["↓", `下移第 ${index + 1} 张照片`, () => moveFile(index, 1), index === selectedFiles.length - 1],
            ["✕", `删除第 ${index + 1} 张照片`, () => removeFile(index), false],
        ];
        actions.forEach(([text, label, handler, disabled]) => {
            const button = document.createElement("button");
            button.type = "button";
            button.textContent = text;
            button.setAttribute("aria-label", label);
            button.disabled = isUploading || disabled;
            button.addEventListener("click", handler);
            controls.appendChild(button);
        });
        item.append(order, name, controls);
        fileList.appendChild(item);
    });
}

window.moveFile = function(index, dir) {
    if (isUploading) return;
    const newIndex = index + dir;
    if (newIndex < 0 || newIndex >= selectedFiles.length) return;
    [selectedFiles[index], selectedFiles[newIndex]] = [selectedFiles[newIndex], selectedFiles[index]];
    renderFileList();
};

window.removeFile = function(index) {
    if (isUploading) return;
    selectedFiles.splice(index, 1);
    renderFileList();
};

renderFileList();

generateBtn.addEventListener("click", async () => {
    if (isUploading || selectedFiles.length === 0) return;
    isUploading = true;
    dropZone.classList.remove("dragover");
    renderFileList();
    const order = selectedFiles.map((_, i) => i + 1).join(",");
    try {
        const resp = await API.createTask(selectedFiles, order);
        const data = await resp.json();
        if (resp.status === 201) {
            window.location.href = `/progress.html?task_id=${data.task_id}`;
            return;
        } else {
            alert(`上传失败：${data.message || "未知错误"}`);
        }
    } catch (e) {
        alert("网络错误，请重试。");
    }
    isUploading = false;
    renderFileList();
});
