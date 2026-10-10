(function () {
    "use strict";

    const COLUMNS = [
        ["scenario_id", "scenario_id"],
        ["agent_id", "agent_id"],
        ["runs", "runs"],
        ["valid_runs", "valid_runs"],
        ["execution_failures", "execution_failures"],
        ["infrastructure_failure_rate", "infrastructure_failure_rate"],
        ["diagnosis_pass_rate", "diagnosis_pass_rate"],
        ["outcome_pass_rate", "outcome_pass_rate"],
        ["safe_pass_rate", "safe_pass_rate"],
    ];
    let datasets = [];
    let payload = null;
    let pinned = loadPinned();
    let sort = { key: "scenario_id", direction: 1 };
    let timer = null;

    document.addEventListener("DOMContentLoaded", init);

    async function init() {
        bind();
        renderPinMenu();
        await loadDatasets();
        const requested = new URLSearchParams(location.search).get("dataset");
        const select = document.getElementById("dataset-select");
        if (requested) select.value = requested;
        if (!select.value && datasets.length) select.value = datasets[0].dataset_id;
        if (select.value) await loadDataset();
    }

    function bind() {
        document.getElementById("dataset-select").addEventListener("change", loadDataset);
        document.getElementById("dataset-refresh").addEventListener("click", refresh);
        document.getElementById("dialog-close").addEventListener("click", () => document.getElementById("run-dialog").close());
        document.getElementById("detail-run-select").addEventListener("change", loadRunDetail);
        const button = document.getElementById("pin-menu-button");
        button.addEventListener("click", () => {
            const menu = document.getElementById("pin-menu");
            menu.hidden = !menu.hidden;
            button.setAttribute("aria-expanded", String(!menu.hidden));
        });
        document.addEventListener("click", event => {
            if (!event.target.closest(".pin-control")) {
                document.getElementById("pin-menu").hidden = true;
                button.setAttribute("aria-expanded", "false");
            }
        });
    }

    async function refresh() {
        await loadDatasets();
        if (document.getElementById("dataset-select").value) await loadDataset();
    }

    async function loadDatasets() {
        const selected = document.getElementById("dataset-select").value;
        datasets = await fetchJson("/api/datasets");
        const select = document.getElementById("dataset-select");
        select.replaceChildren(new Option("选择 dataset_id", ""), ...datasets.map(item => new Option(item.dataset_id, item.dataset_id)));
        if (datasets.some(item => item.dataset_id === selected)) select.value = selected;
    }

    async function loadDataset() {
        clearInterval(timer);
        const datasetId = document.getElementById("dataset-select").value;
        if (!datasetId) return;
        payload = await fetchJson(`/api/datasets/${encodeURIComponent(datasetId)}`);
        renderSummary();
        renderMatrix();
        renderAggregate();
        const url = new URL(location.href);
        url.searchParams.set("dataset", datasetId);
        history.replaceState(null, "", url);
        if (payload.state === "live") timer = setInterval(loadDataset, 15000);
    }

    function renderSummary() {
        const summary = payload.summary;
        setText("summary-state", `${payload.state} / ${payload.data_status}`);
        setText("summary-runs", summary.runs);
        setText("summary-valid", summary.valid_runs);
        setText("summary-failures", summary.execution_failures);
        setText("summary-safe-pass", rate(summary.safe_pass_rate));
        setText("summary-contract", payload.metric_contract);
    }

    function renderMatrix() {
        const head = document.getElementById("matrix-head");
        const body = document.getElementById("matrix-body");
        const columns = payload.scenario_cases;
        const heading = document.createElement("tr");
        const baseline = document.createElement("th");
        baseline.className = "baseline-column";
        baseline.textContent = "Baseline";
        heading.appendChild(baseline);
        columns.forEach(column => {
            const th = document.createElement("th");
            th.className = "scenario-heading";
            th.title = column.label;
            const scenario = document.createElement("span");
            scenario.textContent = column.scenario_id;
            const caseId = document.createElement("small");
            caseId.textContent = column.case_id;
            th.append(scenario, caseId);
            heading.appendChild(th);
        });
        head.replaceChildren(heading);
        body.replaceChildren(...payload.matrix.rows.map(row => {
            const tr = document.createElement("tr");
            const name = document.createElement("td");
            name.className = "baseline-column";
            name.textContent = row.agent_id;
            tr.appendChild(name);
            row.cells.forEach(cell => {
                const td = document.createElement("td");
                td.className = `matrix-cell ${cell.status}`;
                const status = document.createElement("span");
                status.className = "cell-status";
                status.textContent = cell.status;
                const passes = document.createElement("span");
                passes.className = "cell-score";
                passes.textContent = cell.safe_pass_rate === null ? "DP/OP/SP --" : `DP ${rate(cell.diagnosis_pass_rate)} · OP ${rate(cell.outcome_pass_rate)} · SP ${rate(cell.safe_pass_rate)}`;
                const count = document.createElement("span");
                count.className = "cell-count";
                count.textContent = `${cell.runs.length} run${cell.runs.length === 1 ? "" : "s"}`;
                td.append(status, passes, count);
                if (cell.runs.length) {
                    td.tabIndex = 0;
                    td.title = `${row.agent_id} / ${cell.scenario_case_id}`;
                    td.addEventListener("dblclick", () => openCell(row.agent_id, cell));
                    td.addEventListener("keydown", event => {
                        if (event.key === "Enter") openCell(row.agent_id, cell);
                    });
                }
                tr.appendChild(td);
            });
            return tr;
        }));
        document.getElementById("matrix-empty").style.display = payload.matrix.rows.length ? "none" : "block";
    }

    function renderPinMenu() {
        const menu = document.getElementById("pin-menu");
        menu.replaceChildren(...COLUMNS.map(([key, label]) => {
            const row = document.createElement("label");
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkbox.checked = pinned.includes(key);
            checkbox.addEventListener("change", () => {
                pinned = checkbox.checked ? [...pinned, key] : pinned.filter(item => item !== key);
                localStorage.setItem("dataset-pinned-columns", JSON.stringify(pinned));
                renderAggregate();
            });
            row.append(checkbox, document.createTextNode(label));
            return row;
        }));
    }

    function orderedColumns() {
        const pinnedColumns = pinned.map(key => COLUMNS.find(column => column[0] === key)).filter(Boolean);
        return [...pinnedColumns, ...COLUMNS.filter(column => !pinned.includes(column[0]))];
    }

    function renderAggregate() {
        const columns = orderedColumns();
        const rows = [...payload.scenario_agents].sort(compareRows);
        const heading = document.createElement("tr");
        columns.forEach(([key, label]) => {
            const th = document.createElement("th");
            th.dataset.key = key;
            th.textContent = label;
            if (pinned.includes(key)) th.classList.add("pinned-column");
            if (sort.key === key) th.classList.add(sort.direction === 1 ? "sort-asc" : "sort-desc");
            th.addEventListener("click", () => {
                sort = sort.key === key ? { key, direction: -sort.direction } : { key, direction: 1 };
                renderAggregate();
            });
            heading.appendChild(th);
        });
        document.getElementById("aggregate-head").replaceChildren(heading);
        document.getElementById("aggregate-body").replaceChildren(...rows.map(row => {
            const tr = document.createElement("tr");
            columns.forEach(([key]) => {
                const td = document.createElement("td");
                td.dataset.key = key;
                td.textContent = formatField(key, row[key]);
                if (pinned.includes(key)) td.classList.add("pinned-column");
                tr.appendChild(td);
            });
            return tr;
        }));
        document.getElementById("aggregate-empty").style.display = rows.length ? "none" : "block";
        requestAnimationFrame(positionPinnedColumns);
    }

    function positionPinnedColumns() {
        const table = document.getElementById("aggregate-table");
        let left = 0;
        orderedColumns().filter(([key]) => pinned.includes(key)).forEach(([key]) => {
            const cells = table.querySelectorAll(`[data-key="${CSS.escape(key)}"]`);
            cells.forEach(cell => { cell.style.left = `${left}px`; });
            const heading = table.querySelector(`thead [data-key="${CSS.escape(key)}"]`);
            left += heading ? heading.getBoundingClientRect().width : 0;
        });
    }

    function compareRows(a, b) {
        const left = a[sort.key];
        const right = b[sort.key];
        if (left === null || left === undefined) return 1;
        if (right === null || right === undefined) return -1;
        if (typeof left === "number" && typeof right === "number") return (left - right) * sort.direction;
        return String(left).localeCompare(String(right)) * sort.direction;
    }

    function openCell(agentId, cell) {
        setText("dialog-title", `${agentId} / ${cell.scenario_case_id}`);
        setText("dialog-meta", `${cell.status} · ${cell.runs.length} run${cell.runs.length === 1 ? "" : "s"}`);
        const select = document.getElementById("detail-run-select");
        select.replaceChildren(...cell.runs.map(run => new Option(
            `rep ${run.repetition} · attempt ${run.attempt} · ${run.status} · ${run.run_id}`,
            `${run.run_id}::${run.attempt}`,
        )));
        document.getElementById("run-dialog").showModal();
        loadRunDetail();
    }

    async function loadRunDetail() {
        const selected = document.getElementById("detail-run-select").value;
        if (!selected) return;
        const split = selected.lastIndexOf("::");
        const runId = selected.slice(0, split);
        const attempt = selected.slice(split + 2);
        setText("run-json", "Loading...");
        setText("evaluator-json", "Loading...");
        const detail = await fetchJson(`/api/datasets/${encodeURIComponent(payload.dataset_id)}/runs/${encodeURIComponent(runId)}?attempt=${encodeURIComponent(attempt)}`);
        setText("run-json", JSON.stringify(detail.run, null, 2));
        setText("evaluator-title", `evaluator.attempt-${String(attempt).padStart(3, "0")}.json`);
        setText("evaluator-json", detail.evaluator_available ? JSON.stringify(detail.evaluator, null, 2) : "No evaluator artifact for this attempt.");
    }

    function loadPinned() {
        try {
            const value = JSON.parse(localStorage.getItem("dataset-pinned-columns"));
            if (Array.isArray(value)) return value.filter(key => COLUMNS.some(column => column[0] === key));
        } catch (error) {}
        return ["scenario_id", "agent_id"];
    }

    function formatField(key, value) {
        if (value === null || value === undefined) return "--";
        if (key.endsWith("_rate")) return `${(Number(value) * 100).toFixed(1)}%`;
        if (["diagnosis_pass_rate", "outcome_pass_rate", "safe_pass_rate"].includes(key)) return rate(value);
        return String(value);
    }

    function number(value) { return value === null || value === undefined ? "--" : Number(value).toFixed(2); }
    function rate(value) { return value === null || value === undefined ? "--" : `${(Number(value) * 100).toFixed(1)}%`; }
    function setText(id, value) { document.getElementById(id).textContent = String(value); }
    async function fetchJson(url) {
        const response = await fetch(url);
        if (!response.ok) throw new Error(`${url}: ${response.status} ${await response.text()}`);
        return response.json();
    }
}());
