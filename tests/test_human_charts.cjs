const assert = require("node:assert/strict");
require("../src/visualization/static/human-charts.js");
const { datasets, timestamp } = globalThis.HumanCharts;
const metric = datasets({
  series: {
    primary: {
      timestamps: ["2026-10-10T00:00:00Z", "2026-10-10T00:00:02Z"],
      cpu: [10, null],
    },
  },
})[0];
assert.equal(metric.rows.length, 2);
assert.equal(metric.rows[1].value, null);
const compact = datasets({
  series: {
    node: {
      timestamps: { start: "2026-10-10T00:00:00Z", step_seconds: 20, count: 2 },
      qps: [1, 2],
    },
  },
})[0];
assert.equal(compact.rows[1].timestamp - compact.rows[0].timestamp, 20000);
assert.equal(timestamp(1791590400), 1791590400000);
assert.ok(Number.isNaN(timestamp(null)));
const sql = datasets({
  columns: ["ts", "latency"],
  result: [["2026-10-10T00:00:00Z", 5]],
});
assert.deepEqual(sql[0].rows, [{ ts: "2026-10-10T00:00:00Z", latency: 5 }]);
assert.equal(datasets({ status: "error", error: "no data" }).length, 0);
console.log("Chart normalization checks passed");
process.env.TZ = "Asia/Shanghai";
assert.equal(timestamp("2026-10-10 00:00:00"), Date.UTC(2026, 9, 10));
