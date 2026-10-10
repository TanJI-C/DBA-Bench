(function () {
    "use strict";

    const state = {
        items: [], filters: {}, total: 0, offset: 0, limit: 100,
        selected: null, parsed: null, raw: "", mode: "pretty",
    };
    let searchTimer = null;

    document.addEventListener("DOMContentLoaded", init);

    function init() {
        bindControls();
        restoreControlsFromUrl();
        loadList(true);
    }

    function bindControls() {
        document.getElementById("trace-search").addEventListener("input", () => {
            clearTimeout(searchTimer);
            searchTimer = setTimeout(() => loadList(true), 220);
        });
        ["scenario-filter", "agent-filter", "evaluation-filter", "sort-filter"].forEach(id => {
            document.getElementById(id).addEventListener("change", () => loadList(true));
        });
        document.getElementById("refresh-list").addEventListener("click", () => loadList(true));
        document.getElementById("clear-filters").addEventListener("click", clearFilters);
        document.querySelectorAll("[data-days]").forEach(button => button.addEventListener("click", () => quickDays(button)));
        document.querySelectorAll("[data-agent]").forEach(button => button.addEventListener("click", () => {
            document.getElementById("agent-filter").value = button.dataset.agent;
            loadList(true);
        }));
        document.querySelectorAll("[data-evaluation]").forEach(button => button.addEventListener("click", () => {
            document.getElementById("evaluation-filter").value = button.dataset.evaluation;
            loadList(true);
        }));
        document.getElementById("load-more").addEventListener("click", () => loadList(false));
        document.getElementById("mode-pretty").addEventListener("click", () => setMode("pretty"));
        document.getElementById("mode-raw").addEventListener("click", () => setMode("raw"));
        document.getElementById("find-json").addEventListener("input", renderJson);
        document.getElementById("wrap-json").addEventListener("change", renderJson);
        document.getElementById("copy-json").addEventListener("click", copyJson);
        document.getElementById("open-trace").addEventListener("click", () => {
            location.href = "/?file=" + encodeURIComponent(state.selected.filename);
        });
    }

    function restoreControlsFromUrl() {
        const params = new URLSearchParams(location.search);
        const controls = {
            q: "trace-search", scenario: "scenario-filter", agent: "agent-filter",
            evaluation: "evaluation-filter", sort: "sort-filter",
        };
        Object.entries(controls).forEach(([name, id]) => {
            if (!params.has(name)) return;
            const control = document.getElementById(id);
            control.dataset.requestedValue = params.get(name);
            control.value = params.get(name);
        });
        if (params.has("file") && !params.has("q")) {
            document.getElementById("trace-search").value = params.get("file");
        }
    }

    function queryParams(offset) {
        const params = new URLSearchParams();
        const values = {
            q: document.getElementById("trace-search").value.trim(),
            scenario: requestedValue("scenario-filter"),
            agent: requestedValue("agent-filter"),
            evaluation: document.getElementById("evaluation-filter").value,
            sort: document.getElementById("sort-filter").value,
        };
        Object.entries(values).forEach(([key, value]) => { if (value) params.set(key, value); });
        const url = new URL(location.href);
        ["from", "to"].forEach(key => { if (url.searchParams.has(key)) params.set(key, url.searchParams.get(key)); });
        params.set("offset", String(offset));
        params.set("limit", String(state.limit));
        return params;
    }

    function requestedValue(id) {
        const control = document.getElementById(id);
        return control.dataset.requestedValue || control.value;
    }

    async function loadList(reset) {
        const offset = reset ? 0 : state.items.length;
        const params = queryParams(offset);
        const response = await fetch("/api/traces?" + params.toString());
        if (!response.ok) throw new Error(`Trace list request failed: ${response.status}`);
        const payload = await response.json();
        state.items = reset ? payload.items : state.items.concat(payload.items);
        state.total = payload.total;
        state.filters = payload.filters;
        populateFilters();
        renderList();
        syncUrl(params);
        if (reset) {
            const requested = new URLSearchParams(location.search).get("file");
            const target = requested && state.items.find(item => item.filename === requested);
            if (target) selectTrace(target);
        }
    }

    function populateFilters() {
        fillSelect("scenario-filter", state.filters.scenarios || [], "全部场景");
        fillSelect("agent-filter", state.filters.agents || [], "全部 Agent");
    }

    function fillSelect(id, values, emptyLabel) {
        const select = document.getElementById(id);
        const current = select.value;
        select.replaceChildren(new Option(emptyLabel, ""), ...values.map(value => new Option(value, value)));
        select.value = select.dataset.requestedValue || current;
        delete select.dataset.requestedValue;
    }

    function renderList() {
        const root = document.getElementById("trace-results");
        root.replaceChildren(...state.items.map(item => {
            const button = document.createElement("button");
            button.type = "button";
            button.className = "trace-result" + (state.selected?.filename === item.filename ? " active" : "");
            const score = item.outcome_pass === null || item.outcome_pass === undefined
                ? "--"
                : `DP:${passMark(item.diagnosis_pass)} OP:${passMark(item.outcome_pass)} SP:${passMark(item.safe_pass)}`;
            const scenario = item.scenario_id || item.scenario || "未识别场景";
            const agent = item.agent_id || item.agent_type || "未识别 Agent";
            button.innerHTML = `<span class="trace-result-top"><span class="trace-result-time">${escapeHtml(formatTime(item.timestamp))}</span><span class="trace-result-agent">${escapeHtml(agent)}</span><span class="trace-result-score">${score}</span></span><span class="trace-result-scenario">${escapeHtml(scenario)}</span><span class="trace-result-file${item.parse_status !== "valid" ? " trace-result-error" : ""}">${escapeHtml(item.filename)}</span>`;
            button.addEventListener("click", () => selectTrace(item));
            return button;
        }));
        document.getElementById("result-count").textContent = `显示 ${state.items.length} / ${state.total} 条`;
        document.getElementById("load-more").classList.toggle("hidden", state.items.length >= state.total);
    }

    async function selectTrace(item) {
        state.selected = item;
        const [parsedResponse, rawResponse] = await Promise.all([
            fetch("/api/traces/" + encodeURIComponent(item.filename)),
            fetch("/api/traces/" + encodeURIComponent(item.filename) + "/raw"),
        ]);
        state.raw = await rawResponse.text();
        state.parsed = parsedResponse.ok ? await parsedResponse.json() : null;
        document.getElementById("empty-state").classList.add("hidden");
        document.getElementById("json-view").classList.remove("hidden");
        document.getElementById("file-name").textContent = item.filename;
        document.getElementById("file-meta").textContent = [
            item.schema || "无 schema", formatBytes(item.size_bytes), formatTime(item.timestamp),
            item.parse_status === "valid" ? "JSON 正常" : item.parse_error,
        ].join(" · ");
        const download = document.getElementById("download-json");
        download.href = "/api/traces/" + encodeURIComponent(item.filename) + "/raw";
        download.download = item.filename;
        renderList();
        renderJson();
        syncSelectedFile();
    }

    function setMode(mode) {
        state.mode = mode;
        document.getElementById("mode-pretty").classList.toggle("active", mode === "pretty");
        document.getElementById("mode-raw").classList.toggle("active", mode === "raw");
        renderJson();
    }

    function renderJson() {
        if (!state.selected) return;
        const text = state.mode === "pretty" && state.parsed ? JSON.stringify(state.parsed, null, 2) : state.raw;
        const needle = document.getElementById("find-json").value;
        const root = document.getElementById("json-code");
        root.classList.toggle("wrap", document.getElementById("wrap-json").checked);
        root.innerHTML = text.split("\n").map(line => `<span class="code-line">${highlight(line, needle)}</span>`).join("");
    }

    function highlight(line, needle) {
        if (!needle) return escapeHtml(line) || " ";
        const lower = line.toLowerCase();
        const target = needle.toLowerCase();
        let cursor = 0;
        let output = "";
        while (true) {
            const index = lower.indexOf(target, cursor);
            if (index < 0) return output + escapeHtml(line.slice(cursor));
            output += escapeHtml(line.slice(cursor, index)) + "<mark>" + escapeHtml(line.slice(index, index + needle.length)) + "</mark>";
            cursor = index + needle.length;
        }
    }

    async function copyJson() {
        await navigator.clipboard.writeText(state.raw);
        const status = document.getElementById("copy-status");
        status.textContent = "已复制";
        setTimeout(() => { status.textContent = ""; }, 1200);
    }

    function quickDays(button) {
        const days = Number(button.dataset.days);
        const date = new Date();
        date.setUTCDate(date.getUTCDate() - days);
        const url = new URL(location.href);
        url.searchParams.set("from", date.toISOString().slice(0, 10));
        url.searchParams.delete("to");
        history.replaceState(null, "", url);
        loadList(true);
    }

    function clearFilters() {
        ["trace-search", "scenario-filter", "agent-filter", "evaluation-filter"].forEach(id => { document.getElementById(id).value = ""; });
        document.getElementById("sort-filter").value = "timestamp_desc";
        const url = new URL(location.href);
        url.search = "";
        history.replaceState(null, "", url);
        loadList(true);
    }

    function syncUrl(params) {
        const url = new URL(location.href);
        const file = url.searchParams.get("file");
        const from = url.searchParams.get("from");
        const to = url.searchParams.get("to");
        url.search = "";
        params.forEach((value, key) => { if (!["offset", "limit"].includes(key)) url.searchParams.set(key, value); });
        if (from) url.searchParams.set("from", from);
        if (to) url.searchParams.set("to", to);
        if (file) url.searchParams.set("file", file);
        history.replaceState(null, "", url);
    }

    function syncSelectedFile() {
        const url = new URL(location.href);
        url.searchParams.set("file", state.selected.filename);
        history.replaceState(null, "", url);
    }

    function formatTime(timestamp) {
        return timestamp ? new Date(timestamp * 1000).toLocaleString() : "无时间";
    }

    function formatBytes(bytes) {
        if (bytes < 1024) return `${bytes} B`;
        if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KiB`;
        return `${(bytes / 1024 / 1024).toFixed(1)} MiB`;
    }

    function passMark(value) {
        return value === null || value === undefined ? "N/A" : value ? "P" : "F";
    }

    function escapeHtml(value) {
        return String(value).replace(/[&<>"']/g, character => ({"&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"})[character]);
    }
}());
