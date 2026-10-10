# Sink backpressure, healthy neighbors, and closed-loop validation

## Independent sink capacity

A downstream write path can lose capacity because of table-bound work even
when the TiDB, TiKV, PD, and changefeed control services are healthy. Inspect
all triggers or equivalent table-bound hooks using table, event, body, and
observed latency. A trigger name is not a reliable diagnosis key. A healthy
neighboring table or audit path is a useful counterfactual only when its rows
and write behavior are checked separately.

## Data at the failed event boundary

Source writes committed while a sink DDL is retrying remain part of the
business contract. Record a bounded post-event row range and a stable live
writer row, then compare the complete projected rows on both endpoints. A
schema that exists and a checkpoint that is moving are insufficient if a later
recovery start skipped those rows.

## Acceptance and safety

Closed-loop acceptance combines changefeed state, checkpoint and resolved
progress, equivalent downstream DDL, complete business-row equality, sink
write capacity, healthy-neighbor truth, and core service health. The repair
may remove the slow hook on the affected business table, but it must preserve
the neighboring table, its audit hook, seed rows, and all source business
data. A successful control-plane command is not final recovery evidence.
