/* === AiOpsBench unified portal runtime ===
 * Replaces per-page inline nav / theme-toggle / task-switcher / trace-modal.
 * Single source of truth for every page that includes this script.
 *
 * Page contract:
 *   <body>
 *     <div data-portal-slot></div>      ← nav + theme toggle injected here
 *     <main>...</main>                  ← page content
 *     <div data-modal-slot></div>       ← trace-modal injected here (optional)
 *     <script type="application/json" data-task-meta>{...}</script>
 *   </body>
 *
 * data-task-meta.path tells portal.js which nav link is "current".
 * Pages without data-task-meta (e.g. project_dashboard) get no active highlight
 * and no task-switcher.
 */
(function () {
    "use strict";

    const NAV_TPL = (currentPath, hasMeta) => `
<header class="app-header">
  <div class="nav-container">
    <div class="nav-topbar">
      <div class="brand">AiOpsBench</div>
      <nav class="app-nav" aria-label="页面导航">
        <a class="nav-btn${currentPath === "/" ? " active" : ""}" href="/">Trace Viewer</a>
        <a class="nav-btn${currentPath === "/raw-traces" ? " active" : ""}" href="/raw-traces">原始日志</a>
        <a class="nav-btn${currentPath === "/experiments" ? " active" : ""}" href="/experiments">实验运行</a>
        <a class="nav-btn${currentPath === "/human" ? " active" : ""}" href="/human">人类工作台</a>
        <a class="nav-btn${currentPath === "/results" ? " active" : ""}" href="/results">实验结果</a>
        <a class="nav-btn${currentPath === "/datasets" ? " active" : ""}" href="/datasets">Dataset 状态</a>
        <a class="nav-btn${currentPath === "/dashboard" ? " active" : ""}" href="/dashboard">开发总看板</a>
        ${hasMeta ? `<select class="nav-select" id="task-switcher" data-current="${currentPath}" aria-label="切换任务"><option value="">当前任务</option></select>` : ""}
        <button type="button" class="nav-btn theme-toggle" data-theme-toggle title="切换到暗色模式">暗</button>
      </nav>
    </div>
  </div>
</header>`;

    const MODAL_TPL = `
<div id="trace-modal" class="hidden" role="dialog" aria-modal="true" aria-label="Trace viewer">
  <div class="trace-modal-panel" id="trace-modal-panel">
    <div class="trace-modal-toolbar">
      <div class="title" id="trace-modal-title">Trace</div>
      <span id="trace-modal-meta" class="meta"></span>
      <span id="trace-modal-structure" class="structure-badge hidden"></span>
      <div class="status" id="trace-modal-status"></div>
      <div class="tools">
        <button id="trace-modal-fit" type="button" title="Fit to screen">⤢</button>
        <button id="trace-modal-expand-all" type="button" title="Expand all">⊞</button>
        <button id="trace-modal-collapse-all" type="button" title="Collapse all">⊟</button>
        <button id="trace-modal-close" type="button" title="Close">✕</button>
      </div>
    </div>
    <div class="trace-modal-canvas"><svg id="trace-modal-svg"><g id="trace-modal-root"></g></svg></div>
    <div class="trace-modal-side" id="trace-modal-detail" hidden>
      <div class="trace-modal-side-header">
        <div class="trace-modal-side-title" id="trace-modal-detail-title"></div>
        <button id="trace-modal-detail-close" type="button">✕</button>
      </div>
      <div class="trace-modal-side-body" id="trace-modal-detail-body"></div>
    </div>
  </div>
</div>`;

    function readMeta() {
        const el = document.querySelector("script[data-task-meta]");
        if (!el) return null;
        try { return JSON.parse(el.textContent); } catch (e) { return null; }
    }

    function currentPath() {
        return location.pathname.replace(/\/+$/, "") || "/";
    }

    function injectNav(meta) {
        const slot = document.querySelector("[data-portal-slot]");
        if (!slot) return;
        slot.outerHTML = NAV_TPL(currentPath(), !!meta);
    }

    function injectModal() {
        const slot = document.querySelector("[data-modal-slot]");
        if (slot) slot.outerHTML = MODAL_TPL;
    }

    function initTheme() {
        const r = document.documentElement;
        let saved = null;
        try { saved = localStorage.getItem("wc-theme"); } catch (e) {}
        if (saved === "dark" || saved === "light") r.setAttribute("data-theme", saved);
        const btn = document.querySelector("[data-theme-toggle]");
        if (!btn) return;
        const sync = () => {
            const dark = r.getAttribute("data-theme") === "dark";
            btn.textContent = dark ? "明" : "暗";
            btn.title = dark ? "切换到亮色模式" : "切换到暗色模式";
        };
        sync();
        btn.addEventListener("click", () => {
            const n = r.getAttribute("data-theme") === "dark" ? "light" : "dark";
            r.setAttribute("data-theme", n);
            sync();
            try { localStorage.setItem("wc-theme", n); } catch (e) {}
        });
    }

    function initTaskSwitcher() {
        const sel = document.getElementById("task-switcher");
        if (!sel) return;
        const current = sel.dataset.current || "";
        fetch("/api/tasks").then(r => r.ok ? r.json() : []).then(tasks => {
            const seen = new Set();
            tasks.forEach(t => {
                if (!t || !t.path || t.hidden) return;
                if (seen.has(t.path)) return;
                seen.add(t.path);
                const o = document.createElement("option");
                o.value = t.path;
                o.textContent = t.title || t.path.replace(/^.*\//, "").replace(/\.html$/, "");
                if (t.path === current) o.selected = true;
                sel.appendChild(o);
            });
            if (sel.value) sel.classList.add("active");
        }).catch(() => {});
        sel.addEventListener("change", e => {
            const v = e.target.value;
            if (v) location.href = v;
        });
    }

    function initTaskEditor(meta) {
        const root = document.querySelector("[data-task-editor]");
        if (!root || !meta) return;

        const currentPath = location.pathname.replace(/\/+$/, "") || "/";
        const STATUSES = ["todo", "running", "blocked", "waiting", "review", "done", "archived"];
        const STATUS_LABELS = { todo: "todo", running: "running", blocked: "blocked", waiting: "waiting", review: "review", done: "done", archived: "archived" };

        // Replace the in-page status badge (rendered in the .meta header)
        // so it reflects meta.status instead of the build-time string.
        const badge = document.querySelector("[data-task-status-badge]");
        if (badge) {
            const s = meta.status || "running";
            badge.className = "badge " + s;
            badge.textContent = STATUS_LABELS[s] || s;
        }

        // Source of truth: meta.needs_input. Pages no longer carry a static
        // <div class="needs-input"> — migrate_needs_input.py folded those
        // into meta so the editor is the single source.
        const ni = Array.isArray(meta.needs_input) ? meta.needs_input : [];

        // --- status select ---
        const statusSel = document.createElement("select");
        statusSel.className = "task-editor-status";
        STATUSES.forEach(s => {
            const o = document.createElement("option");
            o.value = s; o.textContent = s;
            if ((meta.status || "running") === s) o.selected = true;
            statusSel.appendChild(o);
        });
        statusSel.addEventListener("change", () => updateField("status", statusSel.value));

        // --- needs-input todo list ---
        // Each item renders as <li> with a checkbox, an inline HTML view
        // (preserves <strong>, <code>, etc. from the source list) and a
        // delete button. Double-click the text to switch to an editable
        // <input>; blur or Esc commits and re-renders.
        const list = document.createElement("ul");
        list.className = "task-editor-todo";
        const enterEdit = (wrap, idx) => {
            const current = ni[idx].text || "";
            const input = document.createElement("input");
            input.type = "text";
            input.value = current;
            input.className = "task-editor-todo-edit";
            const commit = () => {
                const next = input.value;
                if (next !== current) {
                    ni[idx].text = next;
                    saveAll();
                }
                renderList();
            };
            input.addEventListener("blur", commit);
            input.addEventListener("keydown", e => {
                if (e.key === "Enter") { e.preventDefault(); input.blur(); }
                else if (e.key === "Escape") { e.preventDefault(); input.value = current; input.blur(); }
            });
            wrap.replaceWith(input);
            input.focus();
            input.select();
        };
        const renderList = () => {
            list.innerHTML = "";
            ni.forEach((item, idx) => {
                const li = document.createElement("li");
                li.className = "task-editor-todo-item" + (item.done ? " done" : "");

                const cb = document.createElement("input");
                cb.type = "checkbox"; cb.checked = !!item.done;
                cb.title = "标记已完成";
                cb.addEventListener("change", () => { ni[idx].done = cb.checked; renderList(); saveAll(); });

                const text = document.createElement("span");
                text.className = "task-editor-todo-text";
                // Trust meta-author HTML (we wrote it via migration); nothing
                // user-typed can land here unless they edit-and-commit, in
                // which case plain text replaces it via .value assignment.
                text.innerHTML = item.text || "";
                text.addEventListener("dblclick", () => enterEdit(text, idx));

                const del = document.createElement("button");
                del.type = "button"; del.textContent = "✕";
                del.title = "删除";
                del.addEventListener("click", () => { ni.splice(idx, 1); renderList(); saveAll(); });

                li.appendChild(cb); li.appendChild(text); li.appendChild(del);
                list.appendChild(li);
            });
        };
        renderList();

        const addBtn = document.createElement("button");
        addBtn.type = "button"; addBtn.className = "task-editor-add";
        addBtn.textContent = "+ 添加";
        addBtn.addEventListener("click", () => {
            ni.push({ text: "", done: false });
            renderList();
            const last = list.querySelectorAll(".task-editor-todo-item");
            const span = last[last.length - 1]?.querySelector(".task-editor-todo-text");
            if (span) enterEdit(span, ni.length - 1);
        });

        // --- notes textarea ---
        const notesArea = document.createElement("textarea");
        notesArea.className = "task-editor-notes";
        notesArea.placeholder = "审核批注（提交后持久化）";
        notesArea.value = meta.notes || "";
        notesArea.rows = 3;
        const notesBtn = document.createElement("button");
        notesBtn.type = "button"; notesBtn.className = "task-editor-submit";
        notesBtn.textContent = "提交批注";

        const status = document.createElement("span");
        status.className = "task-editor-status-text";
        const setStatus = (msg, ok) => { status.textContent = msg; status.dataset.ok = ok ? "1" : "0"; };

        let saveTimer = null;
        function saveAll() {
            clearTimeout(saveTimer);
            saveTimer = setTimeout(async () => {
                try {
                    const r = await fetch("/api/tasks/update", {
                        method: "POST",
                        headers: { "Content-Type": "application/json" },
                        body: JSON.stringify({
                            path: currentPath,
                            status: statusSel.value,
                            needs_input: ni,
                            notes: notesArea.value,
                        }),
                    });
                    setStatus(r.ok ? "✓ 已保存" : "保存失败", r.ok);
                } catch (e) { setStatus("保存失败: " + e.message, false); }
            }, 300);
        }
        notesBtn.addEventListener("click", saveAll);
        notesArea.addEventListener("blur", saveAll);

        // --- assemble ---
        const wrap = document.createElement("div");
        wrap.className = "task-editor";
        const statusRow = document.createElement("div");
        statusRow.className = "task-editor-row";
        const statusLabel = document.createElement("label");
        statusLabel.textContent = "状态：";
        statusRow.appendChild(statusLabel);
        statusRow.appendChild(statusSel);
        statusRow.appendChild(status);

        const niWrap = document.createElement("div");
        niWrap.className = "task-editor-row";
        const niLabel = document.createElement("div");
        niLabel.className = "task-editor-section-label";
        niLabel.textContent = "需要你确认（可勾选 / 编辑 / 删除）：";
        niWrap.appendChild(niLabel);
        niWrap.appendChild(list);
        niWrap.appendChild(addBtn);

        const notesRow = document.createElement("div");
        notesRow.className = "task-editor-row";
        const notesLabel = document.createElement("div");
        notesLabel.className = "task-editor-section-label";
        notesLabel.textContent = "审核批注：";
        notesRow.appendChild(notesLabel);
        notesRow.appendChild(notesArea);
        notesRow.appendChild(notesBtn);

        wrap.appendChild(statusRow);
        wrap.appendChild(niWrap);
        wrap.appendChild(notesRow);

        root.replaceWith(wrap);
        setStatus("", true);
    }

    function initTables() {
        document.querySelectorAll("table").forEach(t => {
            t.querySelectorAll("th[data-sort]").forEach((th, col) => {
                th.addEventListener("click", () => {
                    const tb = t.tBodies[0], rows = [...tb.rows];
                    const num = th.dataset.sort === "num", asc = !th.classList.contains("asc");
                    t.querySelectorAll("th").forEach(h => h.classList.remove("asc", "desc"));
                    th.classList.add(asc ? "asc" : "desc");
                    rows.sort((a, b) => {
                        let x = a.cells[col]?.innerText.trim() || "";
                        let y = b.cells[col]?.innerText.trim() || "";
                        if (num) {
                            x = parseFloat(x.replace(/[^0-9.\-]/g, ""));
                            y = parseFloat(y.replace(/[^0-9.\-]/g, ""));
                            x = isNaN(x) ? -Infinity : x;
                            y = isNaN(y) ? -Infinity : y;
                            return asc ? x - y : y - x;
                        }
                        return asc ? x.localeCompare(y) : x.localeCompare(y);
                    });
                    rows.forEach(r => tb.appendChild(r));
                });
            });
        });
    }

    const meta = readMeta();
    injectNav(meta);
    injectModal();
    initTheme();
    initTables();
    initTaskSwitcher();
    initTaskEditor(meta);

    // trace-modal.js is loaded before portal.js (defer order in HTML),
    // so its DOMContentLoaded handler ran BEFORE we injected the modal HTML
    // and bailed out. Re-init + re-bind now that the modal exists in the DOM
    // so <button.trace-modal-trigger> clicks work.
    if (window.traceModal) {
        if (typeof window.traceModal.init === "function") window.traceModal.init();
        if (typeof window.traceModal.bind === "function") window.traceModal.bind();
    }
})();
