# FLASHBACK CLUSTER overview and syntax

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-flashback-cluster.md`
- Source Title: `FLASHBACK CLUSTER`
- Source Heading Path: `FLASHBACK CLUSTER | FLASHBACK CLUSTER > Syntax | FLASHBACK CLUSTER > Syntax > Synopsis`
- Source Line Ranges: `5-48`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `pd`
- Topic Tags: `flashback`, `syntax`, `timestamp`, `tso`, `warnings`, `storage`, `recovery-point`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0593_98ca07c8bb`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-flashback-cluster.md#flashback-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4962c835ac6b2c0af10c5964f46d555dfee880a3ec3bc638bad518922464c0b9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-flashback-cluster#flashback-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-flashback-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax and warning notes for restoring a TiDB cluster to a specific point in time with `FLASHBACK CLUSTER TO TIMESTAMP` or `FLASHBACK CLUSTER TO TSO`.
- Retrieval Keywords: FLASHBACK CLUSTER, FLASHBACK CLUSTER TO TIMESTAMP, FLASHBACK CLUSTER TO TSO, TSO, restore a cluster to a specific point in time, current TSO, PD, Grafana PD panel, millisecond as the minimum time unit, TiDB extension to MySQL syntax
- Follow-up Guidance: Check the timestamp or TSO validity and ensure enough storage space for the old data and the current data.
- Classification Note: This chunk is a syntax and overview reference for the `FLASHBACK CLUSTER` statement, including timestamp and TSO forms plus the main warnings.

## Official Source Content

# FLASHBACK CLUSTER

TiDB v6.4.0 introduces the `FLASHBACK CLUSTER TO TIMESTAMP` syntax. You can use it to restore a cluster to a specific point in time. When specifying the timestamp, you can either set a datetime value or use a time function. The format of datetime is like '2016-10-08 16:45:26.999', with millisecond as the minimum time unit. But in most cases, specifying the timestamp with second as the time unit is sufficient, for example, '2016-10-08 16:45:26'.

Starting from v6.5.6, v7.1.3, v7.5.1, and v7.6.0, TiDB introduces the `FLASHBACK CLUSTER TO TSO` syntax. This syntax enables you to use [TSO](https://docs.pingcap.com/tidb/stable/tso) to specify a more precise recovery point in time, thereby enhancing flexibility in data recovery.

> **Warning:**
>
> The `FLASHBACK CLUSTER TO [TIMESTAMP|TSO]` syntax is not applicable to [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters. To avoid unexpected results, do not execute this statement on {{{ .starter }}} and {{{ .essential }}} clusters.

> **Warning:**
>
> - When specifying a recovery point in time, make sure to check the validity of your target timestamp or TSO and avoid specifying a future time that exceeds the maximum TSO currently allocated by PD (see `Current TSO` on the Grafana PD panel). Otherwise, concurrent processing linear consistency and transaction isolation levels might be violated, leading to serious data correctness issues.
> - During `FLASHBACK CLUSTER` execution, the data cleanup process does not guarantee transaction consistency. After `FLASHBACK CLUSTER` completes, if you intend to use any historical version reading features in TiDB (such as [Stale Read](https://docs.pingcap.com/tidb/stable/stale-read) or [`tidb_snapshot`](https://docs.pingcap.com/tidb/stable/read-historical-data)), make sure that the specified historical timestamp falls outside the `FLASHBACK CLUSTER` execution period. Reading a historical version that includes data not fully restored by FLASHBACK might violate concurrent processing linear consistency and transaction isolation levels, leading to serious data correctness issues.

> **Warning:**
>
> When you use this feature in TiDB v7.1.0, some Regions might remain in the FLASHBACK process even after the completion of the FLASHBACK operation. It is recommended to avoid using this feature in v7.1.0. For more information, see issue [#44292](https://github.com/pingcap/tidb/issues/44292).
>
> If you have encountered this issue, you can use the [TiDB snapshot backup and restore](https://docs.pingcap.com/tidb/stable/br/br-snapshot-guide) feature to restore data.

> **Note:**
>
> The working principle of `FLASHBACK CLUSTER TO [TIMESTAMP|TSO]` is to write the old data of a specific point in time with the latest timestamp, and will not delete the current data. So before using this feature, you need to ensure that there is enough storage space for the old data and the current data.
## Syntax

```sql
FLASHBACK CLUSTER TO TIMESTAMP '2022-09-21 16:02:50';
FLASHBACK CLUSTER TO TSO 445494839813079041;
```
### Synopsis

```ebnf+diagram
FlashbackToTimestampStmt
         ::= 'FLASHBACK' 'CLUSTER' 'TO' ('TIMESTAMP' stringLit | 'TSO' LengthNum)
```
