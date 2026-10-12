const fileInput = document.querySelector("#csvFiles");
const dropZone = document.querySelector("#dropZone");
const fileList = document.querySelector("#fileList");
const selection = document.querySelector("#selection");
const selectionCount = document.querySelector("#selectionCount");
const clearButton = document.querySelector("#clearFiles");
const notice = document.querySelector("#notice");
const profileButton = document.querySelector("#profileFiles");

let selectedFiles = [];
let isSubmitting = false;

function formatBytes(bytes) {
  if (bytes < 1024 * 1024) {
    return `${Math.max(1, Math.round(bytes / 1024))} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function isCsv(file) {
  return file.name.toLowerCase().endsWith(".csv");
}

function fileIdentity(file) {
  return JSON.stringify([file.name, file.size, file.lastModified]);
}

function setFiles(files) {
  if (isSubmitting) return;

  const incomingFiles = [...files];
  const rejectedFiles = incomingFiles.filter((file) => !isCsv(file));
  const knownFiles = new Set(selectedFiles.map(fileIdentity));
  const addedFiles = incomingFiles.filter((file) => {
    if (!isCsv(file)) return false;

    const identity = fileIdentity(file);
    if (knownFiles.has(identity)) return false;

    knownFiles.add(identity);
    return true;
  });
  selectedFiles = [...selectedFiles, ...addedFiles];
  notice.textContent = rejectedFiles.length
    ? `Choose CSV files only. ${rejectedFiles.map((file) => file.name).join(", ")} ${rejectedFiles.length === 1 ? "was" : "were"} skipped.`
    : "";
  renderFiles();
}

function renderFiles() {
  fileList.replaceChildren();
  selection.hidden = selectedFiles.length === 0;
  profileButton.disabled = selectedFiles.length === 0 || isSubmitting;
  fileInput.disabled = isSubmitting;
  clearButton.disabled = isSubmitting;
  selectionCount.textContent = selectedFiles.length
    ? `${selectedFiles.length} ${selectedFiles.length === 1 ? "file" : "files"} selected`
    : "No files selected";

  selectedFiles.forEach((file) => {
    const row = document.createElement("li");
    row.className = "file-row";

    const mark = document.createElement("span");
    mark.className = "file-mark";
    mark.textContent = "CSV";
    mark.setAttribute("aria-hidden", "true");

    const name = document.createElement("span");
    name.className = "file-name";
    name.textContent = file.name;
    name.title = file.name;

    const size = document.createElement("span");
    size.className = "file-size";
    size.textContent = formatBytes(file.size);

    const removeButton = document.createElement("button");
    removeButton.className = "remove-file-button";
    removeButton.type = "button";
    removeButton.setAttribute("aria-label", `Remove ${file.name}`);
    removeButton.textContent = "×";
    removeButton.disabled = isSubmitting;
    removeButton.addEventListener("click", () => {
      selectedFiles = selectedFiles.filter((selectedFile) => selectedFile !== file);
      fileInput.value = "";
      renderFiles();
    });

    row.append(mark, name, size, removeButton);
    fileList.append(row);
  });
}

fileInput.addEventListener("change", (event) => {
  setFiles(event.target.files);
  fileInput.value = "";
});
clearButton.addEventListener("click", () => {
  selectedFiles = [];
  fileInput.value = "";
  notice.textContent = "";
  renderFiles();
});

profileButton.addEventListener("click", async () => {
  if (!selectedFiles.length || isSubmitting) return;

  const formData = new FormData();
  selectedFiles.forEach((file) => formData.append("files", file));
  isSubmitting = true;
  profileButton.textContent = "Profiling...";
  notice.classList.remove("is-success");
  notice.textContent = "Uploading and profiling CSV files...";
  renderFiles();

  try {
    const response = await fetch("/api/v1/profile", {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Profiling failed.");
    }

    notice.classList.add("is-success");
    notice.textContent = `Profile generated for ${selectedFiles.length} ${selectedFiles.length === 1 ? "CSV file" : "CSV files"}.`;
  } catch (error) {
    notice.classList.remove("is-success");
    notice.textContent = error instanceof Error ? error.message : "Profiling failed.";
  } finally {
    isSubmitting = false;
    profileButton.textContent = "Profile CSVs";
    renderFiles();
  }
});

dropZone.addEventListener("dragover", (event) => {
  event.preventDefault();
  dropZone.classList.add("is-dragging");
});

dropZone.addEventListener("dragleave", () => dropZone.classList.remove("is-dragging"));

dropZone.addEventListener("drop", (event) => {
  event.preventDefault();
  dropZone.classList.remove("is-dragging");
  setFiles(event.dataTransfer.files);
});