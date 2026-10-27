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
let isRestoringFiles = true;
let filePersistenceQueue = Promise.resolve();
const RESTORE_FILES_KEY = "schemanormRestoreFiles";

function openFileDatabase() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open("schemanorm-upload-cache", 1);
    request.onupgradeneeded = () => {
      request.result.createObjectStore("uploads");
    };
    request.onsuccess = () => resolve(request.result);
    request.onerror = () => reject(request.error || new Error("Unable to open browser file storage."));
  });
}

async function writeSelectedFiles() {
  const database = await openFileDatabase();
  try {
    await new Promise((resolve, reject) => {
      const transaction = database.transaction("uploads", "readwrite");
      const store = transaction.objectStore("uploads");
      if (selectedFiles.length) {
        store.put(selectedFiles, "selected");
      } else {
        store.delete("selected");
      }
      transaction.oncomplete = resolve;
      transaction.onerror = () => reject(transaction.error || new Error("Unable to save selected files."));
      transaction.onabort = () => reject(transaction.error || new Error("Saving selected files was interrupted."));
    });
  } finally {
    database.close();
  }
}

async function clearSavedFiles() {
  const database = await openFileDatabase();
  try {
    await new Promise((resolve, reject) => {
      const transaction = database.transaction("uploads", "readwrite");
      transaction.objectStore("uploads").delete("selected");
      transaction.oncomplete = resolve;
      transaction.onerror = () => reject(transaction.error || new Error("Unable to clear saved files."));
      transaction.onabort = () => reject(transaction.error || new Error("Clearing saved files was interrupted."));
    });
  } finally {
    database.close();
  }
}

function queueFilePersistence() {
  filePersistenceQueue = filePersistenceQueue.catch(() => {}).then(writeSelectedFiles);
  filePersistenceQueue.catch((error) => {
    notice.classList.remove("is-success");
    notice.textContent = `Could not save selected files for returning to this page: ${error.message}`;
  });
}

async function initializeSelectedFiles() {
  let shouldRestoreFiles = false;
  try {
    shouldRestoreFiles = sessionStorage.getItem(RESTORE_FILES_KEY) === "true";
    sessionStorage.removeItem(RESTORE_FILES_KEY);

    if (!shouldRestoreFiles) {
      await clearSavedFiles();
      return;
    }

    const database = await openFileDatabase();
    try {
      const savedFiles = await new Promise((resolve, reject) => {
        const transaction = database.transaction("uploads", "readonly");
        const request = transaction.objectStore("uploads").get("selected");
        request.onsuccess = () => resolve(request.result);
        request.onerror = () => reject(request.error || new Error("Unable to restore selected files."));
      });
      if (Array.isArray(savedFiles)) {
        selectedFiles = savedFiles.filter((file) => file instanceof File && isCsv(file));
      }
    } finally {
      database.close();
    }
  } catch (error) {
    notice.classList.remove("is-success");
    notice.textContent = `Unable to initialize selected files: ${error instanceof Error ? error.message : "Browser storage is unavailable."}`;
  } finally {
    isRestoringFiles = false;
    renderFiles();
  }
}

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
  if (isSubmitting || isRestoringFiles) return;

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
  queueFilePersistence();
}

function renderFiles() {
  fileList.replaceChildren();
  selection.hidden = selectedFiles.length === 0;
  profileButton.disabled = selectedFiles.length === 0 || isSubmitting || isRestoringFiles;
  fileInput.disabled = isSubmitting || isRestoringFiles;
  clearButton.disabled = isSubmitting || isRestoringFiles;
  selectionCount.textContent = selectedFiles.length
    ? `${selectedFiles.length} ${selectedFiles.length === 1 ? "file" : "files"} selected`
    : "Select at least one CSV file to begin";

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
      queueFilePersistence();
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
  queueFilePersistence();
});

profileButton.addEventListener("click", async () => {
  if (!selectedFiles.length || isSubmitting) return;

  const formData = new FormData();
  selectedFiles.forEach((file) => formData.append("files", file));
  isSubmitting = true;
  profileButton.classList.add("is-loading");
  profileButton.setAttribute("aria-busy", "true");
  profileButton.textContent = "Analyzing...";
  notice.classList.remove("is-success");
  notice.textContent = "Uploading and profiling CSV files...";
  renderFiles();

  try {
    await filePersistenceQueue;
    const response = await fetch("/api/v1/profile", {
      method: "POST",
      body: formData,
    });
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || "Profiling failed.");
    }

    const analysis = await response.json();
    sessionStorage.setItem("schemanormAnalysis", JSON.stringify(analysis));
    notice.classList.add("is-success");
    notice.textContent = "Analysis complete. Opening the migration dashboard...";
    window.location.assign("/dashboard.html");
  } catch (error) {
    notice.classList.remove("is-success");
    notice.textContent = error instanceof Error ? error.message : "Profiling failed.";
  } finally {
    isSubmitting = false;
    profileButton.classList.remove("is-loading");
    profileButton.removeAttribute("aria-busy");
    profileButton.textContent = "Analyze files";
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

renderFiles();
void initializeSelectedFiles();