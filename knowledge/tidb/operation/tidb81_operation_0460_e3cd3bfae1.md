# Scheduling pause scope and import impact on online traffic

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-physical-import-mode-usage.md`
- Source Title: `Use Physical Import Mode`
- Source Heading Path: `Use Physical Import Mode > Scope of pausing scheduling during import`
- Source Line Ranges: `189-233`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `pd`, `tidb`, `tikv`
- Topic Tags: `scheduling`, `import-impact`, `bandwidth-limit`, `latency`, `online-traffic`, `scope-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0460_e3cd3bfae1`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-physical-import-mode-usage.md#scope-of-pausing-scheduling-during-import`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `71615bcb83527f8ca295e8fc50d5e4b00d7b44ba8b6b5fc0d69437d0b4079404`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#scope-of-pausing-scheduling-during-import
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-physical-import-mode-usage.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about the scope of pausing PD scheduling during physical import, the impact of TiDB Lightning import on online traffic, or import-speed controls that reduce cluster impact.
- Retrieval Keywords: pause-pd-scheduler-scope, table, global, Scope of pausing scheduling during import, pause global scheduling, Region that stores the target table data, store-write-bwlimit, 128MiB, distsql-scan-concurrency, 3, online applications, TPCC, TPM, P99, P90, AVG, TiDB Lightning does not support importing data into a table that already contains data
- Follow-up Guidance: The content also provides example settings for `tikv-importer.store-write-bwlimit` and `tidb.distsql-scan-concurrency`, plus TPCC impact results by concurrency and a note about `pause-pd-scheduler-scope` defaulting to `"table"`.
- Classification Note: This is classified as operation because it describes runtime scheduling scope, operational impact on online applications during import, and related controls for limiting import interference.

## Official Source Content

## Scope of pausing scheduling during import

Starting from v6.2.0, TiDB Lightning implements a mechanism to limit the impact of data import on online applications. With the new mechanism, TiDB Lightning does not pause the global scheduling, but only pauses scheduling for the Region that stores the target table data. This significantly reduces the impact of the import on online applications.

Starting from v7.1.0, you can control the scope of pausing scheduling by using the TiDB Lightning parameter [`pause-pd-scheduler-scope`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration). The default value is `"table"`, which means that the scheduling is paused only for the Region that stores the target table data. When there is no business traffic in the cluster, it is recommended to set this parameter to `"global"` to avoid interference from other scheduling during the import.

> **Note:**
>

TiDB Lightning does not support importing data into a table that already contains data.

The TiDB cluster must be v6.1.0 or later versions. For earlier versions, TiDB Lightning keeps the old behavior, which pauses scheduling globally and severely impacts the online application during the import.

By default, TiDB Lightning pauses the cluster scheduling for the minimum range possible. However, under the default configuration, the cluster performance still might be affected by fast import. To avoid this, you can configure the following options to control the import speed and other factors that might impact the cluster performance:

```toml
[tikv-importer]
# Limits the bandwidth in which TiDB Lightning writes data into each TiKV node in the physical import mode.
store-write-bwlimit = "128MiB"

[tidb]
# Use smaller concurrency to reduce the impact of Checksum and Analyze on the transaction latency.
distsql-scan-concurrency = 3
```

You can measure the impact of data import on TPCC results by simulating the online application using TPCC and importing data into a TiDB cluster using TiDB Lightning. The test result is as follows:

| Concurrency | TPM | P99 | P90 | AVG |
| ----- | --- | --- | --- | --- |
| 1     | 20%~30% | 60%~80% | 30%~50% | 30%~40% |
| 8     | 15%~25% | 70%~80% | 35%~45% | 20%~35% |
| 16    | 20%~25% | 55%~85% | 35%~40% | 20%~30% |
| 64    | No significant impact |
| 256   | No significant impact |

The percentage in the preceding table indicates the impact of data import on TPCC results.

* For the TPM column, the number indicates the percentage of TPM decrease.
* For the P99, P90, and AVG columns, the number indicates the percentage of latency increase.

The test results show that the smaller the concurrency, the larger the impact of data import on TPCC results. When the concurrency is 64 or more, the impact of data import on TPCC results is negligible.

Therefore, if your TiDB cluster has a latency-sensitive application and a low concurrency, it is strongly recommended **not** to use TiDB Lightning to import data into the cluster. This will cause a significant impact on the online application.
