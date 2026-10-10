/* Browser adapter for every tool schema supplied by the active environment. */
"use strict";
const $ = (id) => document.getElementById(id);
const el = (tag, text, cls) => {
  const node = document.createElement(tag);
  if (text !== undefined) node.textContent = text;
  if (cls) node.className = cls;
  return node;
};
const pretty = (v) => (typeof v === "string" ? v : JSON.stringify(v, null, 2));
const stateNames = {
  ready: "可以操作",
  busy: "执行中",
  evaluating: "评估与清理中",
  completed: "已完成",
  failed: "运行失败",
};
let session,
  selectedTool,
  readFields,
  lastHistory = "",
  catalog = [],
  pendingJobId = null,
  loading = false,
  drafts = {};
async function api(path, body) {
  const response = await fetch(
    "/api/human" + path,
    body === undefined
      ? {}
      : {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(body),
        },
  );
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || response.statusText);
  return data;
}
function error(err) {
  $("notice").textContent = err.message;
  $("notice").hidden = false;
}
function download(name, text, type = "application/json") {
  const a = el("a");
  a.href = URL.createObjectURL(new Blob([text], { type }));
  a.download = name;
  a.click();
  setTimeout(() => URL.revokeObjectURL(a.href), 1000);
}
function persistDraft() {
  if (!selectedTool || !readFields) return;
  try {
    drafts[selectedTool.name] = {
      args: readFields(),
      thinking: $("thinking").value,
    };
    localStorage.setItem("human-drafts-" + session.id, JSON.stringify(drafts));
  } catch (err) {
    if (!(err instanceof SyntaxError)) throw err;
  } // Preserve an incomplete JSON edit until valid.
}
function field(schema, name, required, value) {
  const wrap = el("div"),
    type = Array.isArray(schema.type)
      ? schema.type.find((t) => t !== "null")
      : schema.type;
  const title =
    name +
    (/timestamp/.test(name) ? "（UTC）" : "") +
    (required ? " *" : "（选填）");
  if (type === "object" && schema.properties) {
    const box = el("fieldset"),
      legend = el("legend", title);
    box.className = "fields-grid";
    wrap.className = "wide";
    box.append(legend);
    wrap.append(box);
    const reads = Object.entries(schema.properties).map(([key, child]) => [
      key,
      field(child, key, (schema.required || []).includes(key), value?.[key]),
    ]);
    reads.forEach(([, f]) => box.append(f.node));
    return {
      node: wrap,
      read: () =>
        Object.fromEntries(
          reads
            .map(([k, f]) => [k, f.read()])
            .filter(([, v]) => v !== undefined),
        ),
    };
  }
  if (type === "array" && schema.items?.type === "object") {
    wrap.className = "wide";
    const box = el("fieldset"),
      items = [],
      content = el("div"),
      add = el("button", "添加一条条件");
    add.type = "button";
    box.append(el("legend", title), content, add);
    wrap.append(box);
    const append = (v) => {
      const item = field(schema.items, "诊断条件", true, v),
        section = el("div"),
        remove = el("button", "删除条件");
      remove.type = "button";
      section.append(item.node, remove);
      content.append(section);
      items.push(item);
      remove.onclick = () => {
        items.splice(items.indexOf(item), 1);
        section.remove();
      };
    };
    (value || []).forEach(append);
    add.onclick = () => append({});
    return { node: wrap, read: () => items.map((item) => item.read()) };
  }
  const label = el("label", title);
  wrap.append(label);
  let input;
  if (schema.enum) {
    input = el("select");
    if (!required) input.add(new Option("不设置", ""));
    schema.enum
      .filter((v) => v !== null)
      .forEach((v) => input.add(new Option(String(v), String(v))));
  } else if (type === "boolean") {
    input = el("select");
    if (!required) input.add(new Option("不设置", ""));
    input.add(new Option("是", "true"));
    input.add(new Option("否", "false"));
  } else if (
    ["object", "array"].includes(type) ||
    /sql|query|summary|content|evidence|verification|changes|text/i.test(name)
  ) {
    input = el("textarea");
    input.rows = name === "sql_query" ? 9 : 3;
    if (name === "sql_query") input.className = "sql";
  } else {
    input = el("input");
    input.type = ["integer", "number"].includes(type) ? "number" : "text";
    if (type === "number") input.step = "any";
  }
  input.dataset.field = name;
  input.setAttribute("aria-label", name);
  input.required = required && !["array", "object"].includes(type);
  if (schema.minimum !== undefined) input.min = schema.minimum;
  if (schema.maximum !== undefined) input.max = schema.maximum;
  if (/timestamp/.test(name)) {
    input.type = "datetime-local";
    input.step = "1";
  } else if (type === "array") input.placeholder = "每行一项";
  else if (type === "object") input.placeholder = "JSON 对象，例如 {}";
  else if (name === "target")
    input.placeholder = "按工具帮助填写目标；留空使用工具默认目标";
  if (
    value === undefined &&
    schema.default !== undefined &&
    schema.default !== null
  )
    value = schema.default;
  if (value !== undefined && value !== null)
    input.value =
      type === "array"
        ? value.join("\n")
        : type === "object"
          ? JSON.stringify(value, null, 2)
          : String(value);
  if (/timestamp/.test(name) && value !== undefined && value !== null)
    input.value = String(value).replace(" ", "T");
  label.append(input);
  if (schema.description)
    label.append(el("span", schema.description, "field-help"));
  if (input.tagName === "TEXTAREA" || type === "object")
    wrap.className = "wide";
  return {
    node: wrap,
    read: () => {
      const v = input.value;
      if (!v.trim() && !required) return undefined;
      if (/timestamp/.test(name))
        return v.replace("T", " ") + (v.length === 16 ? ":00" : "");
      if (type === "array") return v.split("\n").filter((line) => line.trim());
      if (type === "object") return JSON.parse(v);
      if (type === "boolean") return v === "true";
      if (["integer", "number"].includes(type)) return Number(v);
      return v;
    },
  };
}
const tips = {
  execute_sql:
    "支持多行 SQL，Ctrl / ⌘ + Enter 执行。结果可筛选、排序、导出 CSV；含时间列时可直接绘图。",
  query_metrics:
    "选择指标后填写目标；时间窗口使用 UTC，开始与结束时间需成对填写。结果支持多条曲线、悬停采样值、缩放与图例切换。",
  read_log:
    "按目标、时间窗口或关键字读取日志。结果区域可再次搜索，原始返回始终保留。",
  manage_cluster:
    "先选择资源与操作。参数表单随操作变化，可点击「发现可用目标」查询稳定实例标识。",
  query_knowledge_base:
    "输入你的问题，可限制返回条数与每条长度。结果保留来源信息，方便核对与引用。",
  search_knowledge:
    "按问题、知识类型、组件与来源范围检索；可以从下拉框直接选择过滤条件。",
  manage_instance:
    "执行前核对动作与目标。重启、停止等操作会影响当前题目的真实环境。",
  submit:
    "填写诊断条件、证据、实际改动和验证结果。每行一条证据。提交后开始评估，不能继续操作本题。",
  exit: "终止当前作答并清理环境；此次运行记为中断失败。",
  help: "查看环境实际提供的工具、参数和使用约束。",
};
function renderTools() {
  const filter = $("tool-search").value.toLowerCase();
  $("tool-list").replaceChildren();
  session.tools.forEach(({ function: t }) => {
    if (!`${t.name} ${t.description}`.toLowerCase().includes(filter)) return;
    const b = el(
      "button",
      t.name,
      selectedTool?.name === t.name ? "active" : "",
    );
    b.type = "button";
    b.append(
      el(
        "small",
        {
          execute_sql: "SQL 工作区",
          query_metrics: "时序指标",
          read_log: "日志浏览",
          submit: "提交作答",
          help: "工具帮助",
          exit: "结束运行",
        }[t.name] || "参数表单",
      ),
    );
    b.onclick = () => {
      persistDraft();
      selectTool(t);
    };
    $("tool-list").append(b);
  });
}
function parameterSchema(p) {
  return {
    type: Array.isArray(p.type) ? p.type[0] : p.type.split("|")[0],
    description: p.description,
    enum: p.allowed_values,
    default: p.default,
    ...p.constraints,
  };
}
function clusterFields(definition, args = {}) {
  const wrap = el("div"),
    resource = el("select"),
    operation = el("select"),
    detail = el("div");
  const resources = definition.capabilities.resources;
  const label = (name, node) => {
    const l = el("label", name);
    l.append(node);
    wrap.append(l);
  };
  resources.forEach((r) =>
    resource.add(new Option(r.name + " · " + r.description, r.name)),
  );
  label("resource *", resource);
  label("operation *", operation);
  wrap.append(detail);
  let readTarget, readParameters, current;
  function chooseOperation() {
    current = resources
      .find((r) => r.name === resource.value)
      .operations.find((o) => o.name === operation.value);
    detail.replaceChildren(el("p", current.description));
    const target = field(
      {
        type: "string",
        description: [current.target.description, current.target.format]
          .filter(Boolean)
          .join("\n"),
      },
      "target",
      current.target.required,
      args.target,
    );
    readTarget = target.read;
    if (current.target.type !== "none") detail.append(target.node);
    const discovery = current.target.discovery;
    if (discovery) {
      const button = el("button", "发现可用目标");
      button.type = "button";
      button.onclick = () =>
        sendAction("manage_cluster", {
          resource: discovery.resource_name,
          operation: discovery.operation_name,
        }).catch(error);
      detail.append(button);
    }
    const params = {
      type: "object",
      properties: Object.fromEntries(
        current.parameters.map((p) => [p.name, parameterSchema(p)]),
      ),
      required: current.parameters.filter((p) => p.required).map((p) => p.name),
    };
    const f = field(params, "parameters", false, args.parameters);
    readParameters = f.read;
    if (current.parameters.length) detail.append(f.node);
    const constraints = [
      ...current.constraints.preconditions,
      ...current.constraints.parameter_rules,
    ];
    if (constraints.length)
      detail.append(el("p", constraints.join("\n"), "tip"));
  }
  function chooseResource() {
    const r = resources.find((r) => r.name === resource.value);
    operation.replaceChildren();
    r.operations.forEach((o) =>
      operation.add(new Option(o.name + " · " + o.description, o.name)),
    );
    if (r.operations.some((o) => o.name === args.operation))
      operation.value = args.operation;
    chooseOperation();
  }
  if (args.resource) resource.value = args.resource;
  resource.onchange = chooseResource;
  operation.onchange = chooseOperation;
  chooseResource();
  return {
    node: wrap,
    read: () => {
      const result = { resource: resource.value, operation: operation.value },
        target = readTarget(),
        parameters = readParameters();
      if (current.target.type !== "none" && target !== undefined)
        result.target = target;
      if (Object.keys(parameters).length) result.parameters = parameters;
      return result;
    },
  };
}

function selectTool(tool, args) {
  selectedTool = tool;
  const definition = session.tool_help?.[tool.name]?.definition;
  $("tool-title").textContent = tool.name;
  $("tool-description").textContent =
    definition?.description || tool.description;
  $("tool-tip").textContent =
    tips[tool.name] ||
    "表单来自当前环境的实际工具接口；参数说明与完整帮助可随时查看。";
  const draft = drafts[tool.name];
  const schema = structuredClone(tool.parameters);
  for (const p of definition?.parameters || [])
    if (schema.properties[p.name])
      Object.assign(schema.properties[p.name], {
        ...parameterSchema(p),
        type: schema.properties[p.name].type,
      });
  if (tool.name === "manage_instance")
    schema.properties.action.enum = [
      "restart",
      "start",
      "stop",
      "reboot",
      "get_config",
      "set_config",
      "reset_config",
      "terminate_process",
      "validate_backup",
      "pgbouncer_show_pools",
      "pgbouncer_show_config",
      "pgbouncer_show_stats",
      "pgbouncer_set_config",
      "pgbouncer_reload",
    ];
  if (tool.name === "read_log" && schema.properties.log_type)
    schema.properties.log_type.enum = [
      "dmesg",
      "docker_logs",
      "pg_log",
      "operation_event",
    ];
  const f =
    tool.name === "manage_cluster"
      ? clusterFields(definition, args || draft?.args)
      : field(schema, "参数", true, args || draft?.args);
  $("fields").replaceChildren(f.node);
  readFields = f.read;
  $("thinking").value = draft?.thinking || "";
  $("execute").textContent =
    tool.name === "submit"
      ? "提交作答并评估"
      : tool.name === "exit"
        ? "结束当前运行"
        : "执行工具";
  renderTools();
  updateState();
}
function updateState() {
  $("state").textContent = stateNames[session.state];
  $("state").className = "state " + (session.state === "failed" ? "error" : "");
  const disabled = session.state !== "ready";
  $("execute").disabled = disabled;
  $("tool-help").disabled = disabled || selectedTool?.name === "help";
  $("action-status").textContent = disabled
    ? stateNames[session.state] + "；所有操作记录已保留。"
    : "";
  $("elapsed").textContent =
    "已用时 " +
    Math.floor((Date.now() / 1000 - session.created) / 60) +
    " 分钟";
  if (session.error) {
    $("action-status").textContent = session.error;
    $("action-status").className = "error";
  }
  if (session.evaluation) {
    $("evaluation").hidden = false;
    $("verdicts").replaceChildren();
    [
      ["DiagnosisPass", "诊断"],
      ["OutcomePass", "结果"],
      ["SafePass", "安全"],
    ].forEach(([k, n]) => {
      const v = session.evaluation[k];
      $("verdicts").append(
        el(
          "span",
          n + "：" + (v === null ? "不适用" : v ? "通过" : "未通过"),
          v === false ? "error" : "success",
        ),
      );
    });
    $("evaluation-detail").textContent = pretty(session.evaluation);
  }
}
function tableView(container, columns, rows) {
  const toolbar = el("div", undefined, "result-toolbar"),
    search = el("input"),
    csv = el("button", "导出 CSV"),
    count = el("span");
  search.type = "search";
  search.placeholder = "搜索结果行";
  csv.type = "button";
  toolbar.append(search, csv, count);
  const scroll = el("div", undefined, "table-scroll"),
    table = el("table"),
    thead = el("thead"),
    tbody = el("tbody");
  table.append(thead, tbody);
  scroll.append(table);
  container.append(toolbar, scroll);
  let sorted = rows.map((row) =>
      Array.isArray(row) ? row : columns.map((c) => row[c]),
    ),
    direction = 1;
  const header = el("tr");
  columns.forEach((c, i) => {
    const th = el("th", c);
    th.tabIndex = 0;
    const sort = () => {
      direction *= -1;
      sorted.sort(
        (a, b) =>
          direction *
          String(a[i] ?? "").localeCompare(String(b[i] ?? ""), undefined, {
            numeric: true,
          }),
      );
      paint();
    };
    th.onclick = sort;
    th.onkeydown = (e) => {
      if (e.key === "Enter") sort();
    };
    header.append(th);
  });
  thead.append(header);
  const filtered = () =>
    sorted.filter((r) =>
      pretty(r).toLowerCase().includes(search.value.toLowerCase()),
    );
  function paint() {
    const visible = filtered();
    count.textContent = `${visible.length} / ${rows.length} 行`;
    tbody.replaceChildren();
    visible.forEach((row) => {
      const tr = el("tr");
      row.forEach((v) =>
        tr.append(
          el(
            "td",
            v === null ? "NULL" : typeof v === "object" ? pretty(v) : String(v),
            v === null ? "null" : "",
          ),
        ),
      );
      tbody.append(tr);
    });
  }
  search.oninput = paint;
  csv.onclick = () => {
    const encode = (v) =>
      '"' +
      String(
        v === null ? "" : typeof v === "object" ? pretty(v) : v,
      ).replaceAll('"', '""') +
      '"';
    download(
      "result.csv",
      "\ufeff" +
        [columns, ...filtered()]
          .map((r) => r.map(encode).join(","))
          .join("\r\n"),
      "text/csv",
    );
  };
  paint();
}
function helpView(container, definition) {
  container.append(el("h3", definition.name), el("p", definition.description));
  if (definition.parameters.length)
    tableView(
      container,
      ["参数", "类型", "必填", "说明", "可选值"],
      definition.parameters.map((p) => [
        p.name,
        p.type,
        p.required ? "是" : "否",
        p.description,
        p.allowed_values?.join(", ") || "",
      ]),
    );
  for (const resource of definition.capabilities.resources) {
    const detail = el("details");
    detail.append(el("summary", resource.name + " · " + resource.description));
    for (const op of resource.operations) {
      detail.append(
        el("h4", op.name),
        el("p", op.description),
        el(
          "p",
          "目标：" +
            (op.target.format || op.target.type) +
            (op.target.required ? "（必填）" : ""),
        ),
      );
      if (op.parameters.length)
        tableView(
          detail,
          ["参数", "类型", "必填", "说明"],
          op.parameters.map((p) => [
            p.name,
            p.type,
            p.required ? "是" : "否",
            p.description,
          ]),
        );
    }
    container.append(detail);
  }
  const metrics = definition.capabilities.metrics;
  if (metrics.length)
    tableView(
      container,
      ["指标", "说明", "目标范围"],
      metrics.map((m) => [
        m.name,
        m.description,
        typeof m.target_scope === "string"
          ? m.target_scope
          : pretty(m.target_scope),
      ]),
    );
}

function resultView(container, result) {
  const toolbar = el("div", undefined, "result-toolbar"),
    copy = el("button", "复制原始结果"),
    save = el("button", "下载 JSON");
  copy.type = save.type = "button";
  copy.onclick = () => {
    // The workbench is served over HTTP, where navigator.clipboard is unavailable.
    const text = el("textarea");
    text.value = pretty(result);
    text.readOnly = true;
    text.style.position = "fixed";
    text.style.opacity = "0";
    document.body.append(text);
    text.select();
    try {
      if (!document.execCommand("copy"))
        throw new Error("浏览器拒绝复制结果，请使用下载 JSON 保存结果。");
      copy.textContent = "已复制";
    } catch (err) {
      error(err);
    } finally {
      text.remove();
    }
  };
  save.onclick = () => download("result.json", JSON.stringify(result, null, 2));
  toolbar.append(copy, save);
  container.append(toolbar);
  if (result?.error) container.append(el("pre", pretty(result.error), "error"));
  if (result?.definition) helpView(container, result.definition);
  if (result?.window)
    container.append(el("p", "返回窗口（UTC）：" + pretty(result.window)));
  if (result?.truncated)
    container.append(
      el(
        "p",
        result.truncation?.hint || "返回内容已被工具截断，请缩小查询窗口。",
        "error",
      ),
    );
  const tables = result?.definition ? [] : HumanCharts.datasets(result);
  if (result?.columns && Array.isArray(result.result)) {
    tableView(container, result.columns, result.result);
    if (result.truncated)
      container.append(
        el(
          "p",
          result.truncation_hint ||
            "工具结果已截断，请缩小查询范围或添加 LIMIT。",
        ),
      );
  } else if (
    Array.isArray(result?.results) &&
    result.results.some((r) => typeof r.content === "string")
  ) {
    result.results.forEach((r, i) => {
      const card = el("details");
      card.append(
        el(
          "summary",
          `${r.rank || i + 1}. ${r.title || r.source || "检索结果"}`,
        ),
      );
      card.append(
        el(
          "p",
          [r.source, r.version, r.kb_type, r.component]
            .filter(Boolean)
            .join(" · "),
        ),
        el("pre", r.content),
      );
      card.open = i === 0;
      container.append(card);
    });
  } else if (tables.length && !result?.series)
    tables.forEach((t) => {
      container.append(el("h3", t.name));
      tableView(container, Object.keys(t.rows[0]), t.rows);
    });
  if (tables.length) {
    const details = el("details"),
      chart = el("div");
    details.append(el("summary", "绘制时序 / 数据图"), chart);
    let mounted = false;
    details.ontoggle = () => {
      if (details.open && !mounted) {
        HumanCharts.mount(chart, result);
        mounted = true;
      }
    };
    container.append(details);
    if (result?.series) details.open = true;
  }
  const log = result?.logs ?? result?.log ?? result?.content;
  if (
    typeof result === "string" ||
    typeof log === "string" ||
    (Array.isArray(log) && log.every((v) => typeof v === "string"))
  ) {
    const text =
      typeof result === "string"
        ? result
        : Array.isArray(log)
          ? log.join("\n")
          : log;
    const search = el("input"),
      pre = el("pre", text, "log-lines");
    search.placeholder = "搜索日志行";
    search.oninput = () =>
      (pre.textContent = text
        .split("\n")
        .filter((l) => l.toLowerCase().includes(search.value.toLowerCase()))
        .join("\n"));
    container.append(search, pre);
  }
  const raw = el("details");
  raw.append(el("summary", "原始返回（完整内容）"), el("pre", pretty(result)));
  if (!tables.length && !log) raw.open = true;
  container.append(raw);
}
function renderHistory() {
  const query = $("history-search").value.toLowerCase(),
    signature = JSON.stringify(session.actions) + query;
  if (signature === lastHistory) return;
  lastHistory = signature;
  $("history").replaceChildren();
  $("empty-history").hidden = session.actions.length > 0;
  session.actions.forEach((a, index) => {
    if (!pretty(a).toLowerCase().includes(query)) return;
    const item = el("details", undefined, "history-item"),
      summary = el("summary"),
      finished = a.finished !== undefined;
    const bad =
      a.result?.status === "error" ||
      a.result?.status === "failed" ||
      a.result?.success === false ||
      a.result?.error;
    summary.append(
      el("strong", `#${index + 1} ${a.api}`),
      el("span", new Date(a.started * 1000).toLocaleTimeString()),
      el(
        "span",
        finished ? (bad ? "失败" : "已返回") : "执行中",
        bad ? "error" : finished ? "success" : "busy-indicator",
      ),
    );
    item.append(summary);
    if (a.thinking) item.append(el("p", a.thinking));
    item.append(el("pre", pretty(a.args)));
    const rerun = el("button", "填入参数再次使用");
    rerun.type = "button";
    rerun.onclick = () => {
      const t = session.tools.find((t) => t.function.name === a.api).function;
      persistDraft();
      selectTool(t, a.args);
      $("tool-title").scrollIntoView({ behavior: "smooth" });
    };
    item.append(rerun);
    const body = el("div", undefined, "result-body");
    item.append(body);
    if (finished) {
      body.append(el("p", `耗时 ${(a.finished - a.started).toFixed(2)} 秒`));
      resultView(body, a.result);
    }
    item.open = index === session.actions.length - 1;
    $("history").prepend(item);
  });
}
async function loadSession(id) {
  session = await api("/sessions/" + id);
  localStorage.setItem("human-session", id);
  drafts = JSON.parse(localStorage.getItem("human-drafts-" + id) || "{}");
  selectedTool = null;
  lastHistory = "";
  $("workspace").hidden = false;
  $("launcher").open = false;
  $("evaluation").hidden = true;
  $("identity").textContent =
    `${session.scenario_id} / ${session.case_id} · ${session.participant}`;
  $("prompt").textContent = session.user_prompt;
  $("system-prompt").textContent = session.system_prompt;
  selectTool(
    session.tools.find((t) => t.function.name === "execute_sql")?.function ||
      session.tools[0].function,
  );
  renderHistory();
}
async function sendAction(apiName, args, thinking = "") {
  $("notice").hidden = true;
  await api("/sessions/" + session.id + "/actions", {
    api: apiName,
    args,
    thinking,
  });
  await refresh();
}
$("tool-form").onsubmit = async (e) => {
  e.preventDefault();
  try {
    const args = readFields();
    if (
      (["submit", "exit"].includes(selectedTool.name) ||
        (selectedTool.name === "manage_instance" &&
          [
            "restart",
            "stop",
            "reboot",
            "set_config",
            "reset_config",
            "terminate_process",
            "pgbouncer_set_config",
            "pgbouncer_reload",
          ].includes(args.action)) ||
        (selectedTool.name === "manage_cluster" &&
          !["list", "get", "show", "status", "inspect"].includes(
            args.operation,
          ))) &&
      !confirm(
        selectedTool.name === "submit"
          ? "提交后将开始评估并结束本题，确认提交？"
          : "确认执行 " + selectedTool.name + "？\n" + pretty(args),
      )
    )
      return;
    persistDraft();
    $("execute").disabled = true;
    await sendAction(selectedTool.name, args, $("thinking").value);
  } catch (err) {
    error(err);
    updateState();
  }
};
$("tool-form").oninput = persistDraft;
$("tool-form").onkeydown = (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    if (!$("execute").disabled) $("tool-form").requestSubmit();
  }
  if (e.key === "Tab" && e.target.classList.contains("sql")) {
    e.preventDefault();
    e.target.setRangeText(
      "  ",
      e.target.selectionStart,
      e.target.selectionEnd,
      "end",
    );
  }
};
$("tool-help").onclick = () =>
  sendAction("help", { tool_name: selectedTool.name }).catch(error);
$("tool-search").oninput = renderTools;
$("history-search").oninput = renderHistory;
$("sessions").onchange = () => loadSession($("sessions").value).catch(error);
$("export-session").onclick = () =>
  download(session.run_id + ".json", JSON.stringify(session, null, 2));
function renderScenarios() {
  const s = $("system").value;
  $("scenario").replaceChildren();
  catalog
    .filter((r) => r.system === s)
    .forEach((r) =>
      $("scenario").add(new Option(r.scenario_id, r.scenario_id)),
    );
  renderCases();
}
function renderCases() {
  const r = catalog.find((r) => r.scenario_id === $("scenario").value);
  $("case").replaceChildren();
  r?.cases.forEach((c) =>
    $("case").add(new Option(c.case_id + " · " + c.title, c.case_id)),
  );
}
$("system").onchange = () => {
  renderScenarios();
  $("launch-form").elements.port_base.value =
    $("system").value === "postgresql" ? 25432 : 24500;
};
$("scenario").onchange = renderCases;
$("launch-form").onsubmit = async (e) => {
  e.preventDefault();
  const button = e.submitter;
  button.disabled = true;
  try {
    $("notice").hidden = true;
    const body = Object.fromEntries(new FormData(e.target));
    body.scenario_id = $("scenario").value;
    body.case_id = $("case").value;
    pendingJobId = (await api("/runs", body)).id;
    await refresh();
  } catch (err) {
    error(err);
  } finally {
    button.disabled = false;
  }
};
async function refresh() {
  if (loading) return;
  loading = true;
  try {
    const [sessions, jobs] = await Promise.all([
      api("/sessions"),
      api("/runs"),
    ]);
    const selected = session?.id || localStorage.getItem("human-session");
    $("sessions").replaceChildren(new Option("选择会话", ""));
    sessions.forEach((s) =>
      $("sessions").add(
        new Option(
          `${s.participant} · ${s.case_id} · ${stateNames[s.state]}`,
          s.id,
        ),
      ),
    );
    if (selected) $("sessions").value = selected;
    $("jobs").replaceChildren();
    jobs.forEach((j) => {
      $("jobs").append(
        el(
          "p",
          `${j.scenario_id} / ${j.case_id}：${j.state === "running" ? "运行中，正在准备或作答" : j.state === "completed" ? "运行完成" : "运行失败"}`,
        ),
      );
      if (j.state === "running") {
        const stop = el("button", "终止运行并清理");
        stop.type = "button";
        stop.onclick = () => {
          if (confirm("终止当前运行并清理环境？"))
            api("/runs/" + j.id + "/cancel", {}).catch(error);
        };
        $("jobs").append(stop);
      }
      if (j.error) $("jobs").append(el("pre", j.error, "error"));
    });
    const newest = sessions.find((s) =>
      jobs.some((j) => j.state === "running" && s.run_id.startsWith(j.id)),
    );
    if (!session && sessions.length)
      await loadSession(
        (newest || sessions.find((s) => s.id === selected) || sessions[0]).id,
      );
    else if (
      pendingJobId &&
      sessions.some((s) => s.run_id.startsWith(pendingJobId))
    ) {
      await loadSession(
        sessions.find((s) => s.run_id.startsWith(pendingJobId)).id,
      );
      pendingJobId = null;
    } else if (session) {
      if (
        sessions.find((s) => s.id === session.id)?.revision !== session.revision
      )
        session = await api("/sessions/" + session.id);
      updateState();
      renderHistory();
    }
  } finally {
    loading = false;
  }
}
(async () => {
  try {
    catalog = await api("/catalog");
    renderScenarios();
    await refresh();
  } catch (err) {
    error(err);
  }
  setInterval(() => refresh().catch(error), 1500);
})();
