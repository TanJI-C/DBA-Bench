/* Generic time-series and tabular plotting, using the bundled D3 runtime. */
(function (root) {
  "use strict";
  const numeric = (v) =>
    v !== null &&
    v !== "" &&
    (typeof v === "number" || typeof v === "string") &&
    Number.isFinite(Number(v));
  const timestamp = (v) => {
    if (v === null || v === "") return NaN;
    if (numeric(v)) return Number(v) * (Math.abs(Number(v)) < 1e11 ? 1000 : 1);
    const text = String(v).replace(" ", "T");
    return Date.parse(
      /^\d{4}-\d{2}-\d{2}T/.test(text) && !/(Z|[+-]\d{2}:?\d{2})$/i.test(text)
        ? text + "Z"
        : text,
    );
  };
  function datasets(payload) {
    const found = [],
      metricRows = [];
    function walk(value, path) {
      if (!value || typeof value !== "object") return;
      if (
        !Array.isArray(value) &&
        value.timestamps &&
        (Array.isArray(value.timestamps) ||
          typeof value.timestamps === "object")
      ) {
        const times = Array.isArray(value.timestamps)
          ? value.timestamps
          : Array.from(
              { length: value.timestamps.count },
              (_, i) =>
                timestamp(value.timestamps.start) +
                i * value.timestamps.step_seconds * 1000,
            );
        for (const [key, values] of Object.entries(value)) {
          if (
            key === "timestamps" ||
            !Array.isArray(values) ||
            values.length !== times.length
          )
            continue;
          if (!values.some(numeric)) continue;
          values.forEach((v, i) =>
            metricRows.push({
              timestamp: times[i],
              series: `${path} · ${key}`,
              value: v,
            }),
          );
        }
        return;
      }
      if (Array.isArray(value.columns) && Array.isArray(value.result)) {
        found.push({
          name: path || "SQL 结果",
          rows: value.result.map((row) =>
            Array.isArray(row)
              ? Object.fromEntries(value.columns.map((c, i) => [c, row[i]]))
              : row,
          ),
        });
      }
      if (Array.isArray(value)) {
        if (
          value.length &&
          value.every(
            (row) => row && typeof row === "object" && !Array.isArray(row),
          )
        )
          found.push({ name: path, rows: value });
        else if (
          value.length &&
          value.every((row) => Array.isArray(row) && row.length === 2)
        )
          found.push({
            name: path,
            rows: value.map(([time, v]) => ({ timestamp: time, value: v })),
          });
        return;
      }
      for (const [key, child] of Object.entries(value))
        if (!(key === "result" && Array.isArray(value.columns)))
          walk(child, path ? `${path}.${key}` : key);
    }
    walk(payload, "");
    if (metricRows.length)
      found.unshift({ name: "指标时序（全部目标）", rows: metricRows });
    return found;
  }
  function mount(container, payload) {
    const sets = datasets(payload).filter((s) => s.rows.length > 0);
    if (!sets.length) {
      container.textContent = "没有发现可绘图的表格或时序数组。";
      return;
    }
    const controls = document.createElement("div");
    controls.className = "chart-controls";
    const select = (label, items) => {
      const wrap = document.createElement("label");
      wrap.append(label);
      const el = document.createElement("select");
      items.forEach((v) => el.add(new Option(v, v)));
      wrap.append(el);
      controls.append(wrap);
      return el;
    };
    const source = select(
      "数据表",
      sets.map((s, i) => `${i + 1}. ${s.name}`),
    );
    const x = select("时间 / X 列", []),
      y = select("数值 / Y 列", []),
      group = select("分组列", []);
    const mode = select("X 轴类型", ["时间", "数值"]);
    const reset = document.createElement("button");
    reset.textContent = "重置缩放";
    controls.append(reset);
    const hint = document.createElement("p");
    hint.textContent =
      "时间轴按 UTC 显示；滚轮缩放、拖动平移，悬停查看采样值。缺失值保留为断点。";
    const legend = document.createElement("div");
    legend.className = "legend";
    const svg = d3
      .create("svg")
      .attr("class", "chart")
      .attr("viewBox", "0 0 900 300")
      .attr("role", "img")
      .attr("aria-label", "时序图");
    const tooltip = document.createElement("div");
    tooltip.className = "chart-tooltip";
    tooltip.textContent = "移动鼠标查看数据";
    container.replaceChildren(controls, hint, legend, svg.node(), tooltip);
    let rows,
      hidden = new Set();
    function choose() {
      rows = sets[source.selectedIndex].rows;
      const keys = [...new Set(rows.flatMap(Object.keys))];
      const ns = keys.filter((k) => rows.some((r) => numeric(r[k])));
      [x, y, group].forEach((el) => el.replaceChildren());
      keys.forEach((k) => x.add(new Option(k, k)));
      ns.forEach((k) => y.add(new Option(k, k)));
      group.add(new Option("不分组", ""));
      keys.forEach((k) => group.add(new Option(k, k)));
      const timeKey =
        keys.find((k) => /time|date|时间|日期/i.test(k)) ||
        keys.find((k) =>
          rows.some(
            (r) =>
              typeof r[k] === "string" &&
              /^\d{4}-\d{2}-\d{2}[T ]/.test(r[k]) &&
              Number.isFinite(timestamp(r[k])),
          ),
        );
      if (timeKey) x.value = timeKey;
      mode.value = timeKey ? "时间" : "数值";
      y.value = ns.find((k) => k !== x.value) || ns[0] || "";
      if (keys.includes("series")) group.value = "series";
      hidden = new Set();
      draw();
    }
    function draw() {
      svg.selectAll("*").remove();
      legend.replaceChildren();
      const points = rows
        .map((r) => ({
          x:
            mode.value === "时间"
              ? timestamp(r[x.value])
              : numeric(r[x.value])
                ? Number(r[x.value])
                : NaN,
          y: numeric(r[y.value]) ? Number(r[y.value]) : null,
          group: group.value ? String(r[group.value]) : y.value,
        }))
        .filter((p) => Number.isFinite(p.x));
      const valid = points.filter((p) => p.y !== null);
      if (!valid.length) {
        tooltip.textContent =
          "所选列没有有效的时间与数值组合，请调整列或 X 轴类型。";
        return;
      }
      const groups = d3.group(points, (p) => p.group),
        color = d3.scaleOrdinal([...groups.keys()], d3.schemeTableau10);
      groups.forEach((_, name) => {
        const label = document.createElement("label"),
          checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = !hidden.has(name);
        checkbox.onchange = () => {
          checkbox.checked ? hidden.delete(name) : hidden.add(name);
          draw();
        };
        label.style.color = color(name);
        label.append(checkbox, name);
        legend.append(label);
      });
      const visible = valid.filter((p) => !hidden.has(p.group));
      if (!visible.length) return;
      const extent = d3.extent(visible, (p) => p.x);
      if (extent[0] === extent[1]) {
        extent[0] -= 1000;
        extent[1] += 1000;
      }
      const xs = (mode.value === "时间" ? d3.scaleUtc() : d3.scaleLinear())
        .domain(extent)
        .range([75, 870]);
      const ys = d3
        .scaleLinear()
        .domain(d3.extent(visible, (p) => p.y))
        .nice()
        .range([250, 20]);
      if (ys.domain()[0] === ys.domain()[1])
        ys.domain([ys.domain()[0] - 1, ys.domain()[1] + 1]);
      const xAxis = svg.append("g").attr("transform", "translate(0,250)");
      svg
        .append("g")
        .attr("transform", "translate(75,0)")
        .call(d3.axisLeft(ys).ticks(6));
      svg.append("text").attr("x", 75).attr("y", 12).text(y.value);
      svg
        .append("text")
        .attr("x", 870)
        .attr("y", 294)
        .attr("text-anchor", "end")
        .text(x.value + (mode.value === "时间" ? " · UTC" : ""));
      const clipId = "clip-" + Math.random().toString(36).slice(2);
      svg
        .append("defs")
        .append("clipPath")
        .attr("id", clipId)
        .append("rect")
        .attr("x", 75)
        .attr("y", 20)
        .attr("width", 795)
        .attr("height", 230);
      const plot = svg.append("g").attr("clip-path", `url(#${clipId})`);
      let currentX = xs;
      function paint(scale) {
        currentX = scale;
        xAxis.call(d3.axisBottom(scale).ticks(6));
        plot.selectAll("*").remove();
        groups.forEach((data, name) => {
          if (hidden.has(name)) return;
          const sorted = [...data].sort((a, b) => a.x - b.x);
          plot
            .append("path")
            .datum(sorted)
            .attr("fill", "none")
            .attr("stroke", color(name))
            .attr("stroke-width", 2)
            .attr(
              "d",
              d3
                .line()
                .defined((p) => p.y !== null)
                .x((p) => scale(p.x))
                .y((p) => ys(p.y)),
            );
          if (sorted.length < 150)
            plot
              .selectAll(null)
              .data(sorted.filter((p) => p.y !== null))
              .enter()
              .append("circle")
              .attr("cx", (p) => scale(p.x))
              .attr("cy", (p) => ys(p.y))
              .attr("r", 2.5)
              .attr("fill", color(name));
        });
      }
      const zoom = d3
        .zoom()
        .scaleExtent([1, 100])
        .extent([
          [75, 20],
          [870, 250],
        ])
        .translateExtent([
          [75, 20],
          [870, 250],
        ])
        .on("zoom", (e) => paint(e.transform.rescaleX(xs)));
      svg.call(zoom).on("mousemove.inspect", (e) => {
        const [px] = d3.pointer(e, svg.node()),
          at = Number(currentX.invert(px));
        const nearest = d3.least(visible, (p) => Math.abs(p.x - at));
        tooltip.textContent = `${mode.value === "时间" ? new Date(nearest.x).toISOString() : nearest.x}\n${nearest.group}: ${nearest.y}`;
      });
      reset.onclick = () => svg.call(zoom.transform, d3.zoomIdentity);
      paint(xs);
    }
    source.onchange = choose;
    [x, y, group, mode].forEach(
      (el) =>
        (el.onchange = () => {
          hidden = new Set();
          draw();
        }),
    );
    choose();
  }
  root.HumanCharts = { datasets, timestamp, mount };
})(typeof window === "undefined" ? globalThis : window);
