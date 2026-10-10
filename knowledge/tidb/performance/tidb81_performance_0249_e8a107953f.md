# TiFlash slow analysis due to unsupported MPP functions

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/troubleshoot-tiflash.md`
- Source Title: `Troubleshoot a TiFlash Cluster`
- Source Heading Path: `Troubleshoot a TiFlash Cluster > TiFlash analysis is slow`
- Source Line Ranges: `149-173`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `sql`
- Topic Tags: `mpp`, `explain`, `show-warnings`, `pushdown`, `unsupported-functions`, `query-analysis`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0249_e8a107953f`
- Source ID: `tidb-docs-8.1:tiflash/troubleshoot-tiflash.md#tiflash-analysis-is-slow`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `036b0ba456696b044a1f570218a46b747f0061172e2c74fa7f4f6aa9d26ae3c1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/troubleshoot-tiflash#tiflash-analysis-is-slow
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/troubleshoot-tiflash.md

## Retrieval Guidance

- Use When: Use this chunk when analyzing slow TiFlash queries that might not use MPP because the SQL contains operators or functions unsupported in MPP mode.
- Retrieval Keywords: TiFlash analysis is slow, MPP mode, EXPLAIN, show warnings, tidb_enforce_mpp, set @@session.tidb_enforce_mpp=1, subtime, not supported to push down to tiflash now, Scalar function 'subtime', unsupported functions, push down to tiflash, create table t(a datetime), alter table t set tiflash replica 1
- Follow-up Guidance: The example shows using `EXPLAIN` and `show warnings` to identify the unsupported function that prevents TiDB from selecting MPP mode.
- Classification Note: The content is classified as performance because it explains a query slowdown caused by TiDB not selecting MPP mode when unsupported functions cannot be pushed down to TiFlash.

## Official Source Content

## TiFlash analysis is slow

If a statement contains operators or functions not supported in the MPP mode, TiDB does not select the MPP mode. Therefore, the analysis of the statement is slow. In this case, you can execute the `EXPLAIN` statement to check for operators or functions not supported in the MPP mode.

```sql
create table t(a datetime);
alter table t set tiflash replica 1;
insert into t values('2022-01-13');
set @@session.tidb_enforce_mpp=1;
explain select count(*) from t where subtime(a, '12:00:00') > '2022-01-01' group by a;
show warnings;
```

In this example, the warning message shows that TiDB does not select the MPP mode because TiDB 5.4 and earlier versions do not support the `subtime` function.

```
+---------+------+-----------------------------------------------------------------------------+
> | Level   | Code | Message                                                                     |
+---------+------+-----------------------------------------------------------------------------+
| Warning | 1105 | Scalar function 'subtime'(signature: SubDatetimeAndString, return type: datetime) is not supported to push down to tiflash now.       |
+---------+------+-----------------------------------------------------------------------------+
```
