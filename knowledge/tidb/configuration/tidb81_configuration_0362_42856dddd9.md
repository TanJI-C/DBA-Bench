# TiFlash MPP mode overview and selection controls

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/use-tiflash-mpp-mode.md`
- Source Title: `Use TiFlash MPP Mode`
- Source Heading Path: `Use TiFlash MPP Mode | Use TiFlash MPP Mode > Control whether to select the MPP mode`
- Source Line Ranges: `5-89`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `mpp`, `query-planning`, `cost-based-optimization`, `session-variables`, `execution-plan`, `warnings`, `tiflash-replica`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0362_42856dddd9`
- Source ID: `tidb-docs-8.1:tiflash/use-tiflash-mpp-mode.md#use-tiflash-mpp-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5c0f9b281d364fa04268c6c89e72c933d278f7f3f786629ac1e4a55ccc476c68`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode#use-tiflash-mpp-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/use-tiflash-mpp-mode.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how TiDB selects or forces TiFlash MPP mode, including the effect of `tidb_allow_mpp`, `tidb_enforce_mpp`, and MPP-blocking warnings in `EXPLAIN` and `show warnings` output.
- Retrieval Keywords: TiFlash MPP mode, Massively Parallel Processing, tidb_allow_mpp, tidb_enforce_mpp, enforce-mpp, set @@session.tidb_allow_mpp=0, set @@session.tidb_allow_mpp=1, set @@session.tidb_enforce_mpp=0, set @@session.tidb_enforce_mpp=1, optimizer selects the MPP mode based on cost estimation, ignores the cost estimation and selects the MPP mode, EXPLAIN, show warnings, MPP mode may be blocked because there aren't tiflash replicas of table, absence of TiFlash replica, unfinished replication of TiFlash replicas, operators or functions that are not supported by the MPP mode
- Follow-up Guidance: If `EXPLAIN` does not use MPP for reasons other than cost estimation while `tidb_enforce_mpp=1`, `show warnings` returns a warning that explains the reason, such as missing TiFlash replicas.
- Classification Note: The official content is classified as configuration because it centers on session variables and the `enforce-mpp` configuration that control whether TiDB can select or forcibly use TiFlash MPP mode.

## Official Source Content

# Use TiFlash MPP Mode

This document introduces the [Massively Parallel Processing (MPP)](https://docs.pingcap.com/tidb/stable/glossary#mpp) mode of TiFlash and how to use it.

This document introduces the [Massively Parallel Processing (MPP)](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#mpp) mode of TiFlash and how to use it.

TiFlash supports using the MPP mode to execute queries, which introduces cross-node data exchange (data shuffle process) into the computation. TiDB automatically determines whether to select the MPP mode using the optimizer's cost estimation. You can change the selection strategy by modifying the values of [`tidb_allow_mpp`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_allow_mpp-new-in-v50) and [`tidb_enforce_mpp`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enforce_mpp-new-in-v51).

The following diagram shows how the MPP mode works.

![mpp-mode](/media/tiflash/tiflash-mpp.png)
## Control whether to select the MPP mode

The `tidb_allow_mpp` variable controls whether TiDB can select the MPP mode to execute queries. The `tidb_enforce_mpp` variable controls whether the optimizer's cost estimation is ignored and the MPP mode of TiFlash is forcibly used to execute queries.

The results corresponding to all values of these two variables are as follows:

|                        | tidb_allow_mpp=off | tidb_allow_mpp=on (by default)              |
| ---------------------- | -------------------- | -------------------------------- |
| tidb_enforce_mpp=off (by default) | The MPP mode is not used. | The optimizer selects the MPP mode based on cost estimation. (by default)|
| tidb_enforce_mpp=on  | The MPP mode is not used.   | TiDB ignores the cost estimation and selects the MPP mode.      |

For example, if you do not want to use the MPP mode, you can execute the following statements:

```sql
set @@session.tidb_allow_mpp=0;
```

If you want TiDB's cost-based optimizer to automatically decide whether to use the MPP mode (by default), you can execute the following statements:

```sql
set @@session.tidb_allow_mpp=1;
set @@session.tidb_enforce_mpp=0;
```

If you want TiDB to ignore the optimizer's cost estimation and to forcibly select the MPP mode, you can execute the following statements:

```sql
set @@session.tidb_allow_mpp=1;
set @@session.tidb_enforce_mpp=1;
```

The initial value of the `tidb_enforce_mpp` session variable is equal to the [`enforce-mpp`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enforce-mpp) configuration value of this tidb-server instance (which is `false` by default). If multiple tidb-server instances in a TiDB cluster only perform analytical queries and you want to make sure that the MPP mode is used on these instances, you can change their [`enforce-mpp`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#enforce-mpp) configuration values to `true`.

> **Note:**
>
> When `tidb_enforce_mpp=1` takes effect, the TiDB optimizer will ignore the cost estimation to choose the MPP mode. However, if other factors block the MPP mode, TiDB will not select the MPP mode. These factors include the absence of TiFlash replica, unfinished replication of TiFlash replicas, and statements containing operators or functions that are not supported by the MPP mode.
>
> If TiDB optimizer cannot select the MPP mode due to reasons other than cost estimation, when you use the `EXPLAIN` statement to check out the execution plan, a warning is returned to explain the reason. For example:
>
> ```sql
> set @@session.tidb_enforce_mpp=1;
> create table t(a int);
> explain select count(*) from t;
> show warnings;
> ```
>
> ```
> +---------+------+-----------------------------------------------------------------------------+
> | Level   | Code | Message                                                                     |
> +---------+------+-----------------------------------------------------------------------------+
> | Warning | 1105 | MPP mode may be blocked because there aren't tiflash replicas of table `t`. |
> +---------+------+-----------------------------------------------------------------------------+
> ```
