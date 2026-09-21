(() => {
  "use strict";

  const dropzone = document.getElementById("dropzone");
  const fileInput = document.getElementById("file-input");
  const fileList = document.getElementById("file-list");
  const fileCount = document.getElementById("file-count");
  const runBtn = document.getElementById("run-btn");
  const folderBtn = document.getElementById("process-folder-btn");
  const uploadStatus = document.getElementById("upload-status");
  const resultsEl = document.getElementById("results");
  const resultCount = document.getElementById("result-count");
  const clearBtn = document.getElementById("clear-results");
  const minConf = document.getElementById("min-conf");
  const confVal = document.getElementById("conf-val");
  const langCustom = document.getElementById("lang-custom");
  const deskewChk = document.getElementById("deskew");
  const gpuChk = document.getElementById("use-gpu");
  const tooltip = document.getElementById("tooltip");

  const queue = [];
  let processing = false;

  // ---------- File queue ----------

  function addFiles(files) {
    let added = 0;
    for (const file of files) {
      if (!file.type.startsWith("image/")) continue;
      queue.push({ id: URL.createObjectURL(file), file, preview: URL.createObjectURL(file) });
      added++;
    }
    if (added) {
      renderFileList();
      updateRunState();
    }
  }

  function removeFile(id) {
    const idx = queue.findIndex((q) => q.id === id);
    if (idx === -1) return;
    URL.revokeObjectURL(queue[idx].preview);
    queue.splice(idx, 1);
    renderFileList();
    updateRunState();
  }

  function renderFileList() {
    fileList.innerHTML = "";
    for (const item of queue) {
      const li = document.createElement("li");
      li.innerHTML = `
        <img class="thumb" src="${item.preview}" alt="" />
        <span class="fname" title="${escapeHtml(item.file.name)}">${escapeHtml(item.file.name)}</span>
        <button class="rm" title="Remove" aria-label="Remove ${escapeHtml(item.file.name)}">&times;</button>`;
      li.querySelector(".rm").addEventListener("click", () => removeFile(item.id));
      fileList.appendChild(li);
    }
    fileCount.textContent = queue.length ? `${queue.length} image${queue.length > 1 ? "s" : ""} ready` : "";
    updateRunState();
  }

  function updateRunState() {
    const hasFiles = queue.length > 0;
    runBtn.disabled = processing || !hasFiles;
    folderBtn.disabled = processing;
  }

  // ---------- Dropzone ----------

  dropzone.addEventListener("click", () => fileInput.click());
  dropzone.addEventListener("keydown", (e) => {
    if (e.key === "Enter" || e.key === " ") { e.preventDefault(); fileInput.click(); }
  });
  fileInput.addEventListener("change", () => {
    addFiles(fileInput.files);
    fileInput.value = "";
  });

  ["dragenter", "dragover"].forEach((ev) =>
    dropzone.addEventListener(ev, (e) => {
      e.preventDefault();
      dropzone.classList.add("dragging");
    })
  );
  ["dragleave", "drop"].forEach((ev) =>
    dropzone.addEventListener(ev, (e) => {
      e.preventDefault();
      dropzone.classList.remove("dragging");
    })
  );
  dropzone.addEventListener("drop", (e) => addFiles(e.dataTransfer.files));

  // ---------- Options ----------

  minConf.addEventListener("input", () => { confVal.value = Number(minConf.value).toFixed(2); });

  function getOptions() {
    const langs = [...document.querySelectorAll('#langs input:checked')].map((c) => c.value);
    const extra = langCustom.value
      .split(",")
      .map((s) => s.trim().toLowerCase())
      .filter(Boolean);
    const all = [...new Set([...langs, ...extra])];
    const form = new FormData();
    form.set("min_confidence", minConf.value);
    form.set("languages", all.join(","));
    form.set("deskew", deskewChk.checked ? "true" : "false");
    form.set("use_gpu", gpuChk.checked ? "true" : "false");
    return { form, langs: all.length ? all : ["en"] };
  }

  // ---------- Run ----------

  async function runOcr() {
    if (!queue.length || processing) return;
    processing = true;
    updateRunState();
    setBusy(true);

    const { form, langs } = getOptions();
    for (let i = 0; i < queue.length; i++) {
      const item = queue[i];
      setStatus(`Processing ${i + 1}/${queue.length}: ${item.file.name} (${langs.join(",")})`);
      form.append("images", item.file, item.file.name);
      try {
        const res = await fetch("/api/ocr", { method: "POST", body: form });
        const data = await res.json().catch(() => ({}));
        const entry = data.results && data.results[0] ? data.results[0] : { file: item.file.name, success: false, error: data.error || "Upload failed" };
        entry.originalObjectURL = item.preview;
        addResult(entry);
      } catch (err) {
        addResult({ file: item.file.name, success: false, error: String(err), originalObjectURL: item.preview });
      }
    }
    form.delete("images");

    queue.length = 0;
    renderFileList();
    setBusy(false);
    setStatus("");
    processing = false;
    updateRunState();
  }

  async function processFolder() {
    if (processing) return;
    processing = true;
    updateRunState();
    setBusy(true);
    setStatus("Processing input folder...");
    const { form, langs } = getOptions();
    try {
      const res = await fetch("/api/process-folder", { method: "POST", body: form });
      const data = await res.json().catch(() => ({ results: [] }));
      const entries = data.results || [];
      entries.forEach(addResult);
      if (entries.length === 0) addResult({ file: "(input folder)", success: false, error: "No images found in data/input, or folder is empty." });
    } catch (err) {
      addResult({ file: "(input folder)", success: false, error: String(err) });
    }
    setBusy(false);
    setStatus("");
    processing = false;
    updateRunState();
  }

  runBtn.addEventListener("click", runOcr);
  folderBtn.addEventListener("click", processFolder);

  clearBtn.addEventListener("click", () => {
    resultsEl.innerHTML = "";
    updateCount(0);
  });

  function setBusy(on) {
    runBtn.querySelector(".spin").hidden = !on;
    folderBtn.querySelector(".btn-label").textContent = on ? "Working..." : "Process input folder";
    runBtn.querySelector(".btn-label").textContent = on ? "Working..." : "Run OCR";
  }

  function setStatus(msg) {
    uploadStatus.hidden = !msg;
    uploadStatus.textContent = msg;
  }

  // ---------- Results ----------

  function addResult(entry) {
    const card = document.createElement("article");
    card.className = "card";
    if (!entry.success) {
      card.innerHTML = `
        <div class="card-head">
          <span class="fname">${escapeHtml(entry.file)}</span>
          <span class="badge err">failed</span>
        </div>
        <pre class="card-error error-text">${escapeHtml(entry.error || "Unknown error")}</pre>`;
    } else {
      card.innerHTML = buildCardHtml(entry);
      attachCardBehaviors(card, entry);
    }
    resultsEl.prepend(card);
    updateCount(resultsEl.querySelectorAll(".card").length);
    const empty = resultsEl.querySelector(".empty");
    if (empty) empty.remove();
  }

  function buildCardHtml(entry) {
    const p = entry.payload;
    const lines = p.lines || [];
    const confs = lines.map((l) => l.confidence).filter((c) => c !== undefined && c !== null);
    const avg = confs.length ? (confs.reduce((a, b) => a + b, 0) / confs.length * 100).toFixed(0) : "–";
    const imgSrc = p.original_url ? `src="${p.original_url}"` : `src="${entry.originalObjectURL}"`;
    const lineItems = lines
      .map((l) => `<li><span class="lt">${escapeHtml(l.text)}</span><span class="lc">${(l.confidence * 100).toFixed(0)}%</span></li>`)
      .join("");
    return `
      <div class="card-head">
        <span class="fname" title="${escapeHtml(p.image)}">${escapeHtml(p.image)}</span>
        <span class="badge ok">done</span>
        <div class="stats">
          <span><b>${lines.length}</b> lines</span>
          <span>avg <b>${avg}%</b></span>
          <div class="card-actions">
            <button class="icon-btn copy-btn" type="button">Copy</button>
            <button class="icon-btn dl-btn" type="button">Download .txt</button>
          </div>
        </div>
      </div>
      <div class="card-body">
        <div class="img-panel">
          <div class="image-controls">
            <button class="icon-btn toggle-boxes active" type="button">Boxes</button>
            <button class="icon-btn toggle-preprocess" type="button">Processed</button>
          </div>
          <div class="img-window">
            <img class="base-img" ${imgSrc} alt="" />
            <canvas class="box-canvas"></canvas>
          </div>
          <p class="guide">Hover highlighted boxes to inspect lines</p>
        </div>
        <div class="text-panel">
          <p class="guide">Extracted text (paragraphs)</p>
          <pre class="ocr-text">${escapeHtml(p.text || "")}</pre>
          <details class="line-details">
            <summary>Lines &amp; confidence (${lines.length})</summary>
            <ul class="line-list">${lineItems || "<li class='muted'>no lines above threshold</li>"}</ul>
          </details>
        </div>
      </div>`;
  }

  function attachCardBehaviors(card, entry) {
    const p = entry.payload;
    const img = card.querySelector(".base-img");
    const canvas = card.querySelector(".box-canvas");
    const boxesBtn = card.querySelector(".toggle-boxes");
    const prepBtn = card.querySelector(".toggle-preprocess");

    if (entry.originalObjectURL) {
      img.src = entry.originalObjectURL;
      img.dataset.srcType = "original";
    }

    const overlay = initOverlay(card, img, canvas, p.lines || []);

    boxesBtn.addEventListener("click", () => {
      boxesBtn.classList.toggle("active");
      overlay.setVisible(boxesBtn.classList.contains("active"));
    });
    prepBtn.addEventListener("click", () => {
      const next = prepBtn.classList.contains("active") ? "original" : "processed";
      prepBtn.classList.toggle("active");
      boxesBtn.classList.add("active");
      img.dataset.srcType = next;
      img.src = next === "processed"
        ? p.preprocessed_url
        : (p.original_url || entry.originalObjectURL || p.preprocessed_url);
      overlay.reset();
    });

    card.querySelector(".copy-btn").addEventListener("click", async () => {
      await navigator.clipboard.writeText(p.text).catch(() => {});
      flashCopy(card.querySelector(".copy-btn"));
    });
    card.querySelector(".dl-btn").addEventListener("click", () => {
      const blob = new Blob([p.text], { type: "text/plain;charset=utf-8" });
      const a = document.createElement("a");
      a.href = URL.createObjectURL(blob);
      a.download = `${p.image.replace(/\.[^.]+$/, "")}.txt`;
      a.click();
      setTimeout(() => URL.revokeObjectURL(a.href), 2000);
    });
  }

  function flashCopy(btn) {
    const original = btn.textContent;
    btn.textContent = "Copied!";
    setTimeout(() => { btn.textContent = original; }, 1200);
  }

  // ---------- Bounding box overlay ----------

  function initOverlay(card, img, canvas, lines) {
    const ctx = canvas.getContext("2d");
    let visible = true;
    let active = -1;
    let ready = false;

    function compute() {
      if (!img.naturalWidth || !img.naturalHeight) return;
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      ready = true;
      draw();
    }

    function scale() {
      // Mode A: original image — bboxes were computed after resize to width 1600.
      // Mode B: processed image (itself 1600 wide) — scale is 1.
      if (img.dataset.srcType === "processed") return 1;
      return img.naturalWidth ? img.naturalWidth / 1600 : 1;
    }

    function draw() {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      if (!visible || !ready) return;
      const s = scale();
      lines.forEach((line, i) => {
        const pts = line.bbox.map(([x, y]) => [x * s, y * s]);
        const isActive = i === active;
        ctx.beginPath();
        pts.forEach(([x, y], j) => (j === 0 ? ctx.moveTo(x, y) : ctx.lineTo(x, y)));
        ctx.closePath();
        ctx.fillStyle = isActive ? "rgba(88,166,255,0.32)" : "rgba(63,185,80,0.16)";
        ctx.fill();
        ctx.strokeStyle = isActive ? "#58a6ff" : "#3fb950";
        ctx.lineWidth = isActive ? 2.5 : 1.5;
        ctx.stroke();
      });
    }

    function findLine(clientX, clientY) {
      const rect = canvas.getBoundingClientRect();
      const s = scale();
      const px = (clientX - rect.left) * (canvas.width / rect.width);
      const py = (clientY - rect.top) * (canvas.height / rect.height);
      for (let i = lines.length - 1; i >= 0; i--) {
        const pts = lines[i].bbox.map(([x, y]) => [x * s, y * s]);
        if (pointInPoly(px, py, pts)) return i;
      }
      return -1;
    }

    canvas.addEventListener("mousemove", (e) => {
      if (!ready || !visible) return;
      const idx = findLine(e.clientX, e.clientY);
      if (idx !== active) {
        active = idx;
        draw();
      }
      if (idx >= 0) {
        const line = lines[idx];
        tooltip.hidden = false;
        tooltip.style.left = Math.min(e.clientX + 14, window.innerWidth - tooltip.offsetWidth - 8) + "px";
        tooltip.style.top = (e.clientY + 14) + "px";
        tooltip.innerHTML = `<div>${escapeHtml(line.text)}</div>
          <div class="tt-conf">confidence ${(line.confidence * 100).toFixed(0)}%</div>`;
      } else {
        tooltip.hidden = true;
      }
    });
    canvas.addEventListener("mouseleave", () => {
      active = -1;
      tooltip.hidden = true;
      draw();
    });

    img.addEventListener("load", compute);
    compute();

    return {
      setVisible(v) { visible = v; draw(); },
      reset() { ready = false; compute(); },
    };
  }

  function pointInPoly(px, py, pts) {
    let inside = false;
    for (let i = 0, j = pts.length - 1; i < pts.length; j = i++) {
      const xi = pts[i][0], yi = pts[i][1];
      const xj = pts[j][0], yj = pts[j][1];
      const intersect = (yi > py) !== (yj > py) && px < ((xj - xi) * (py - yi)) / (yj - yi) + xi;
      if (intersect) inside = !inside;
    }
    return inside;
  }

  function updateCount(n) {
    resultCount.textContent = n ? String(n) : "";
    clearBtn.hidden = !n;
  }

  function escapeHtml(str) {
    return String(str ?? "").replace(/[&<>"']/g, (c) => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;",
    }[c]));
  }

  window.OCRStudio = { addFiles };
})();