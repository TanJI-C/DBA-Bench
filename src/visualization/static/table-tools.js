/**
 * TableTools: click-to-sort on every column plus checkbox-value filtering
 * on columns marked with th[data-filter].
 *
 * Tables opt in via <table data-table-id="...">. Sort/filter state is kept per
 * data-table-id so tables rebuilt by periodic refresh keep their view. enhance()
 * is idempotent: header wiring happens once, row data is recaptured each call.
 * Cell values: td[data-sort-value]/td[data-filter-value] override text content;
 * an empty sort value sorts last in either direction.
 */
window.TableTools = (function () {
    "use strict";

    const stateStore = new Map();
    const contexts = new WeakMap();
    let openPanel = null;

    document.addEventListener("click", event => {
        if (openPanel && !openPanel.panel.contains(event.target) && !openPanel.button.contains(event.target)) {
            closePanel();
        }
    });
    document.addEventListener("scroll", () => openPanel && closePanel(), true);
    window.addEventListener("resize", () => openPanel && closePanel());

    function stateFor(table) {
        const id = table.dataset.tableId;
        let state = stateStore.get(id);
        if (!state) {
            state = { sort: null, hidden: new Map() };
            stateStore.set(id, state);
        }
        return state;
    }

    function enhanceAll(root) {
        root.querySelectorAll("table[data-table-id]").forEach(enhance);
    }

    function enhance(table) {
        const tbody = table.tBodies[0];
        const headRow = table.tHead && table.tHead.rows[0];
        if (!tbody || !headRow) return;
        const state = stateFor(table);

        if (!table.dataset.ttWired) {
            table.dataset.ttWired = "1";
            wireHeaders(table, headRow, state);
        }

        const rows = [...tbody.rows].filter(row => !row.classList.contains("empty-row"));
        if (!rows.length) {
            contexts.delete(table);
            return;
        }
        rows.forEach((row, index) => { row.dataset.rowIndex = String(index); });
        const values = rows.map(row => [...row.cells].map(cell => {
            const td = cell;
            return td.dataset.sortValue !== undefined ? td.dataset.sortValue : td.textContent.trim();
        }));

        const numeric = column => {
            const cleaned = column.map(value => value.replace(/[,%\s]/g, "").replace(/s$/i, "")).filter(v => v !== "");
            return cleaned.length > 0 && cleaned.every(v => !isNaN(Number(v)));
        };
        const comparators = [...headRow.cells].map((_, index) => {
            if (numeric(values.map(row => row[index]))) {
                return (a, b) => Number(a.replace(/[,%\s]/g, "").replace(/s$/i, "")) - Number(b.replace(/[,%\s]/g, "").replace(/s$/i, ""));
            }
            return (a, b) => a.localeCompare(b, undefined, { numeric: true, sensitivity: "base" });
        });

        function applySort() {
            const { sort } = state;
            if (!sort) return;
            const compare = comparators[sort.col];
            if (!compare) return;
            const order = [...rows.keys()].sort((x, y) => {
                const vx = values[x][sort.col], vy = values[y][sort.col];
                if (vx === "" && vy === "") return x - y;
                if (vx === "") return 1;
                if (vy === "") return -1;
                const result = compare(vx, vy);
                return sort.dir === "asc" ? result : (-result || x - y);
            });
            order.forEach(rowIndex => tbody.appendChild(rows[rowIndex]));
        }

        function applyFilter(colIndex) {
            const hiddenValues = state.hidden.get(colIndex);
            rows.forEach((row, index) => {
                row.style.display = hiddenValues && hiddenValues.has(values[index][colIndex]) ? "none" : "";
            });
        }

        contexts.set(table, {
            rows, values,
            cellAt: (rowIndex, colIndex) => values[rowIndex][colIndex],
            applySort,
            applyFilter,
            applyAllFilters() { state.hidden.forEach((_, colIndex) => applyFilter(colIndex)); },
        });

        paintArrows(headRow, state.sort);
        if (state.sort) applySort();
        contexts.get(table).applyAllFilters();
    }

    function wireHeaders(table, headRow, state) {
        [...headRow.cells].forEach((th, colIndex) => {
            th.classList.add("tt-sortable");
            const arrow = document.createElement("span");
            arrow.className = "tt-arrow";
            th.appendChild(arrow);
            th.addEventListener("click", event => {
                if (event.target.closest(".tt-filter-btn")) return;
                const previous = state.sort;
                state.sort = previous && previous.col === colIndex && previous.dir === "asc"
                    ? { col: colIndex, dir: "desc" }
                    : { col: colIndex, dir: "asc" };
                paintArrows(headRow, state.sort);
                const context = contexts.get(table);
                if (context) context.applySort();
            });

            if (th.hasAttribute("data-filter")) {
                th.classList.add("tt-filterable");
                const button = document.createElement("button");
                button.type = "button";
                button.className = "tt-filter-btn";
                button.title = "筛选";
                button.textContent = "▾";
                button.addEventListener("click", event => {
                    event.stopPropagation();
                    if (openPanel && openPanel.button === button) { closePanel(); return; }
                    const context = contexts.get(table);
                    if (context) openFilterPanel(table, colIndex, button, context, state);
                });
                th.appendChild(button);
            }
        });
    }

    function paintArrows(headRow, sort) {
        [...headRow.cells].forEach((th, index) => {
            th.classList.toggle("tt-sorted", !!sort && sort.col === index);
            th.querySelector(".tt-arrow").textContent = sort && sort.col === index ? (sort.dir === "asc" ? "▲" : "▼") : "";
        });
    }

    function openFilterPanel(table, colIndex, button, context, state) {
        closePanel();
        const counts = new Map();
        context.rows.forEach(row => {
            const value = context.cellAt(Number(row.dataset.rowIndex), colIndex);
            counts.set(value, (counts.get(value) || 0) + 1);
        });
        const hiddenValues = state.hidden.get(colIndex) || new Set();
        state.hidden.set(colIndex, hiddenValues);
        const sortedValues = [...counts.keys()].sort((a, b) =>
            a.localeCompare(b, undefined, { numeric: true, sensitivity: "base" }));

        const panel = document.createElement("div");
        panel.className = "tt-filter-panel";
        const head = document.createElement("div");
        head.className = "tt-filter-head";
        const countLabel = document.createElement("span");
        const selectAll = document.createElement("button");
        selectAll.type = "button"; selectAll.textContent = "全选";
        const clearAll = document.createElement("button");
        clearAll.type = "button"; clearAll.textContent = "清空";
        head.append(countLabel, selectAll, clearAll);

        const list = document.createElement("div");
        list.className = "tt-filter-list";
        const checkboxes = sortedValues.map(value => {
            const item = document.createElement("label");
            item.className = "tt-filter-item";
            const box = document.createElement("input");
            box.type = "checkbox";
            box.checked = !hiddenValues.has(value);
            box.addEventListener("change", () => {
                if (box.checked) hiddenValues.delete(value); else hiddenValues.add(value);
                sync();
                context.applyFilter(colIndex);
            });
            const text = document.createElement("span");
            text.textContent = value === "" ? "（空）" : value;
            const count = document.createElement("span");
            count.className = "tt-filter-count";
            count.textContent = String(counts.get(value));
            item.append(box, text, count);
            list.appendChild(item);
            return { box, value };
        });

        function sync() {
            const shown = checkboxes.filter(item => item.box.checked).length;
            countLabel.textContent = `${shown}/${checkboxes.length} 项`;
            selectAll.disabled = shown === checkboxes.length;
            clearAll.disabled = shown === 0;
            button.classList.toggle("tt-filter-active", shown < checkboxes.length);
        }
        selectAll.addEventListener("click", () => {
            checkboxes.forEach(item => { item.box.checked = true; hiddenValues.delete(item.value); });
            sync(); context.applyFilter(colIndex);
        });
        clearAll.addEventListener("click", () => {
            checkboxes.forEach(item => { item.box.checked = false; hiddenValues.add(item.value); });
            sync(); context.applyFilter(colIndex);
        });

        panel.append(head, list);
        document.body.appendChild(panel);
        const rect = button.getBoundingClientRect();
        const panelWidth = panel.offsetWidth, panelHeight = panel.offsetHeight;
        panel.style.left = `${Math.max(8, Math.min(rect.left, window.innerWidth - panelWidth - 8))}px`;
        panel.style.top = `${Math.max(8, Math.min(rect.bottom + 4, window.innerHeight - panelHeight - 8))}px`;
        sync();
        openPanel = { panel, button };
    }

    function closePanel() {
        if (!openPanel) return;
        openPanel.panel.remove();
        openPanel.button.classList.remove("tt-filter-active");
        openPanel = null;
    }

    return { enhanceAll, enhance };
}());
