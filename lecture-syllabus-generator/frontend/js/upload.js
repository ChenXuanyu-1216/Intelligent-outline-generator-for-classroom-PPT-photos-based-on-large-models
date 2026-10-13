let selectedFiles = [];

const dropZone = document.getElementById("drop-zone");
const fileInput = document.getElementById("file-input");
const fileList = document.getElementById("file-list");
const generateBtn = document.getElementById("generate-btn");

dropZone.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("dragover", (e) => { e.preventDefault(); dropZone.classList.add("dragover"); });
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", (e) => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    handleFiles(e.dataTransfer.files);
});
fileInput.addEventListener("change", (e) => handleFiles(e.target.files));

function handleFiles(files) {
    selectedFiles = Array.from(files);
    renderFileList();
    generateBtn.disabled = selectedFiles.length === 0;
}

function renderFileList() {
    fileList.innerHTML = "";
    selectedFiles.forEach((file, index) => {
        const item = document.createElement("div");
        item.className = "file-item";
        item.innerHTML = `
            <span class="file-order">P${index + 1}</span>
            <span class="file-name">${file.name}</span>
            <div class="move-btns">
                <button onclick="moveFile(${index}, -1)">↑</button>
                <button onclick="moveFile(${index}, 1)">↓</button>
                <button onclick="removeFile(${index})">✕</button>
            </div>
        `;
        fileList.appendChild(item);
    });
}

window.moveFile = function(index, dir) {
    const newIndex = index + dir;
    if (newIndex < 0 || newIndex >= selectedFiles.length) return;
    [selectedFiles[index], selectedFiles[newIndex]] = [selectedFiles[newIndex], selectedFiles[index]];
    renderFileList();
};

window.removeFile = function(index) {
    selectedFiles.splice(index, 1);
    renderFileList();
    generateBtn.disabled = selectedFiles.length === 0;
};

generateBtn.addEventListener("click", async () => {
    if (selectedFiles.length === 0) return;
    generateBtn.disabled = true;
    generateBtn.textContent = "上传中...";
    const order = selectedFiles.map((_, i) => i + 1).join(",");
    try {
        const resp = await API.createTask(selectedFiles, order);
        const data = await resp.json();
        if (resp.status === 201) {
            window.location.href = `/progress.html?task_id=${data.task_id}`;
        } else {
            alert(`上传失败：${data.message || "未知错误"}`);
            generateBtn.disabled = false;
            generateBtn.textContent = "生成大纲";
        }
    } catch (e) {
        alert("网络错误，请重试。");
        generateBtn.disabled = false;
        generateBtn.textContent = "生成大纲";
    }
});