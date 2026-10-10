# TiDB Binlog FAQ: performance, latency, privileges, and routine troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/tidb-binlog-faq.md`
- Source Title: `TiDB Binlog FAQs`
- Source Heading Path: `TiDB Binlog FAQs | TiDB Binlog FAQs > What is the impact of enabling TiDB Binlog on the performance of TiDB? | TiDB Binlog FAQs > How high is the replication latency of TiDB Binlog? | TiDB Binlog FAQs > What privileges does Drainer need to replicate data to the downstream MySQL or TiDB cluster? | TiDB Binlog FAQs > What can I do if the Pump disk is almost full? | TiDB Binlog FAQs > What can I do if Drainer replication is interrupted? | TiDB Binlog FAQs > What can I do if Drainer is slow to replicate data to the downstream MySQL or TiDB cluster?`
- Source Line Ranges: `5-74`
- Source Scope: `shared`
- Primary Component: `tidb`
- Related Components: `pd`, `tikv`, `sql`, `shared`
- Topic Tags: `binlog`, `performance`, `latency`, `privileges`, `pump`, `drainer`, `gc`, `disk-usage`, `monitoring`, `replication`, `troubleshooting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0080_f06d21f7f6`
- Source ID: `tidb-docs-8.1:tidb-binlog/tidb-binlog-faq.md#tidb-binlog-faqs`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `36d5f806118c84367908e99f734ab7c71a1a04f0c76e8711f366f39530a6b502`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-faq#tidb-binlog-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/tidb-binlog-faq.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing TiDB Binlog performance impact, replication latency, Drainer privileges, Pump disk usage, interrupted replication, or slow downstream replication.
- Retrieval Keywords: TiDB Binlog FAQs, impact of enabling TiDB Binlog on the performance of TiDB, p-binlog, TiKV prewrite stage, Pump's monitoring panel, replication latency measured in seconds, about 3 seconds during off-peak hours, Drainer privileges, Insert, Update, Delete, Create, Drop, Alter, Execute, Index, Select, Create View, Pump disk is almost full, gc_tso, GC parameter of Pump, add pump instances, Drainer replication is interrupted, binlogctl -cmd pumps, Drainer Event, SQL Query Time, worker-count, primary key, unique index, cross-datacenter replication
- Follow-up Guidance: The content says to check `binlogctl -cmd pumps`, Drainer monitor or log errors, Pump `gc_tso`, and the `Drainer Event` and `SQL Query Time` monitoring metrics depending on the symptom.
- Classification Note: This chunk is classified as diagnosis because it explains observable performance, latency, privilege, disk, interruption, and slow replication symptoms and what to check for each.

## Official Source Content

# TiDB Binlog FAQs

This document collects the frequently asked questions (FAQs) about TiDB Binlog.
## What is the impact of enabling TiDB Binlog on the performance of TiDB?

- There is no impact on the query.

- There is a slight performance impact on `INSERT`, `DELETE` and `UPDATE` transactions. In latency, a p-binlog is written concurrently in the TiKV prewrite stage before the transactions are committed. Generally, writing binlog is faster than TiKV prewrite, so it does not increase latency. You can check the response time of writing binlog in Pump's monitoring panel.
## How high is the replication latency of TiDB Binlog?

The latency of TiDB Binlog replication is measured in seconds, which is generally about 3 seconds during off-peak hours.
## What privileges does Drainer need to replicate data to the downstream MySQL or TiDB cluster?

To replicate data to the downstream MySQL or TiDB cluster, Drainer must have the following privileges:

* Insert
* Update
* Delete
* Create
* Drop
* Alter
* Execute
* Index
* Select
* Create View
## What can I do if the Pump disk is almost full?

1. Check whether Pump's GC works well:

    - Check whether the **gc_tso** time in Pump's monitoring panel is identical with that of the configuration file.

2. If GC works well, perform the following steps to reduce the amount of space required for a single Pump:

    - Modify the **GC** parameter of Pump to reduce the number of days to retain data.

    - Add pump instances.
## What can I do if Drainer replication is interrupted?

Execute the following command to check whether the status of Pump is normal and whether all the Pump instances that are not in the `offline` state are running.

```bash
binlogctl -cmd pumps
```

Then, check whether the Drainer monitor or log outputs corresponding errors. If so, resolve them accordingly.
## What can I do if Drainer is slow to replicate data to the downstream MySQL or TiDB cluster?

Check the following monitoring items:

- For the **Drainer Event** monitoring metric, check the speed of Drainer replicating `INSERT`, `UPDATE` and `DELETE` transactions to the downstream per second.

- For the **SQL Query Time** monitoring metric, check the time Drainer takes to execute SQL statements in the downstream.

Possible causes and solutions for slow replication:

- If the replicated database contains a table without a primary key or unique index, add a primary key to the table.

- If the latency between Drainer and the downstream is high, increase the value of the `worker-count` parameter of Drainer. For cross-datacenter replication, it is recommended to deploy Drainer in the downstream.

- If the load in the downstream is not high, increase the value of the `worker-count` parameter of Drainer.
