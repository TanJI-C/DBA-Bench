# tidb_opt_range_max_size variable reference and usage example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_opt_range_max_size <span class="version-mark">New in v6.4.0</span>`
- Source Line Ranges: `4531-4609`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `system-variables`, `optimizer`, `scan-ranges`, `memory-limit`, `set-var`, `explain`, `warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0735_6e3c3d77bd`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-opt-range-max-size-span-class-version-mark-new-in-v6-4-0-span`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `aa1dc0f26050924f2b3d93724866caed8037c9f860678cb5f84423349b5fedeb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-opt-range-max-size-span-class-version-mark-new-in-v6-4-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about the `tidb_opt_range_max_size` system variable, its memory limit for optimizer scan range building, or why `EXPLAIN` shows relaxed instead of exact index scan ranges.
- Retrieval Keywords: tidb_opt_range_max_size, optimizer build scan ranges, upper limit of memory usage, exact scan ranges, relaxed scan ranges, SET_VAR, SESSION | GLOBAL, 67108864, 64 MiB, 0 no memory limit, EXPLAIN SELECT * FROM t USE INDEX (idx), IndexRangeScan, range:[10 40,10 40], range:[10,10], [20,20], [30,30], SHOW WARNINGS
- Follow-up Guidance: The source also shows checking `SELECT @@tidb_opt_range_max_size`, setting `SET @@tidb_opt_range_max_size = 1500`, comparing the `EXPLAIN` output, and using `SHOW WARNINGS` when exact scan range building exceeds the limit.
- Classification Note: This is reference content because it defines the variable scope, persistence, default value, range, unit, `SET_VAR` applicability, and includes an official usage example with `EXPLAIN` and warnings.

## Official Source Content

### tidb_opt_range_max_size New in v6.4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: `67108864` (64 MiB)
- Scope: `[0, 9223372036854775807]`
- Unit: Bytes
- This variable is used to set the upper limit of memory usage for the optimizer to build scan ranges. When the variable value is `0`, there is no memory limit for building scan ranges. If building exact scan ranges consumes memory that exceeds the limit, the optimizer uses more relaxed scan ranges (such as `[[NULL,+inf]]`). If the execution plan does not use exact scan ranges, you can increase the value of this variable to let the optimizer build exact scan ranges.

The usage example of this variable is as follows:

<details>
<summary><code>tidb_opt_range_max_size</code> usage examples</summary>

View the default value of this variable. From the result, you can see that the optimizer uses up to 64 MiB of memory to build scan ranges.

```sql
SELECT @@tidb_opt_range_max_size;
```

```sql
+----------------------------+
| @@tidb_opt_range_max_size |
+----------------------------+
| 67108864                   |
+----------------------------+
1 row in set (0.01 sec)
```

```sql
EXPLAIN SELECT * FROM t use index (idx) WHERE a IN (10,20,30) AND b IN (40,50,60);
```

In the 64 MiB memory upper limit, the optimizer builds the following exact scan ranges `[10 40,10 40], [10 50,10 50], [10 60,10 60], [20 40,20 40], [20 50,20 50], [20 60,20 60], [30 40,30 40], [30 50,30 50], [30 60,30 60]`, as shown in the following execution plan result.

```sql
+-------------------------------+---------+-----------+--------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| id                            | estRows | task      | access object            | operator info                                                                                                                                                               |
+-------------------------------+---------+-----------+--------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| IndexLookUp_7                 | 0.90    | root      |                          |                                                                                                                                                                             |
| ├─IndexRangeScan_5(Build)     | 0.90    | cop[tikv] | table:t, index:idx(a, b) | range:[10 40,10 40], [10 50,10 50], [10 60,10 60], [20 40,20 40], [20 50,20 50], [20 60,20 60], [30 40,30 40], [30 50,30 50], [30 60,30 60], keep order:false, stats:pseudo |
| └─TableRowIDScan_6(Probe)     | 0.90    | cop[tikv] | table:t                  | keep order:false, stats:pseudo                                                                                                                                              |
+-------------------------------+---------+-----------+--------------------------+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
3 rows in set (0.00 sec)
```

Now set the upper limit of memory usage for the optimizer to build scan ranges to 1500 bytes.

```sql
SET @@tidb_opt_range_max_size = 1500;
```

```sql
Query OK, 0 rows affected (0.00 sec)
```

```sql
EXPLAIN SELECT * FROM t USE INDEX (idx) WHERE a IN (10,20,30) AND b IN (40,50,60);
```

In the 1500-byte memory limit, the optimizer builds more relaxed scan ranges `[10,10], [20,20], [30,30]`, and uses a warning to inform the user that the memory usage required to build exact scan ranges exceeds the limit of `tidb_opt_range_max_size`.

```sql
+-------------------------------+---------+-----------+--------------------------+-----------------------------------------------------------------+
| id                            | estRows | task      | access object            | operator info                                                   |
+-------------------------------+---------+-----------+--------------------------+-----------------------------------------------------------------+
| IndexLookUp_8                 | 0.09    | root      |                          |                                                                 |
| ├─Selection_7(Build)          | 0.09    | cop[tikv] |                          | in(test.t.b, 40, 50, 60)                                        |
| │ └─IndexRangeScan_5          | 30.00   | cop[tikv] | table:t, index:idx(a, b) | range:[10,10], [20,20], [30,30], keep order:false, stats:pseudo |
| └─TableRowIDScan_6(Probe)     | 0.09    | cop[tikv] | table:t                  | keep order:false, stats:pseudo                                  |
+-------------------------------+---------+-----------+--------------------------+-----------------------------------------------------------------+
4 rows in set, 1 warning (0.00 sec)
```

```sql
SHOW WARNINGS;
```
