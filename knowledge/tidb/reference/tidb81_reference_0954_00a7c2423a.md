# TiFlash pushdown examples for expressions and unsupported functions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-supported-pushdown-calculations.md`
- Source Title: `Push-down calculations Supported by TiFlash`
- Source Heading Path: `Push-down Calculations Supported by TiFlash > Examples > Example 2: Push expressions down to TiFlash | Push-down Calculations Supported by TiFlash > Examples > Example 3: Restrictions for pushdown`
- Source Line Ranges: `93-158`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `sql`, `tidb`
- Topic Tags: `pushdown`, `mpp`, `expressions`, `operators`, `explain`, `show-warnings`, `restrictions`, `scalar-functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0954_00a7c2423a`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-supported-pushdown-calculations.md#example-2-push-expressions-down-to-tiflash`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `008a2734a2337aeaa3951ed8fda6dbd85d7c9db353e43433164f99d805b2f787`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations#example-2-push-expressions-down-to-tiflash
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-supported-pushdown-calculations.md

## Retrieval Guidance

- Use When: Use this chunk when you need examples showing how to confirm TiFlash expression pushdown in EXPLAIN output and how to identify unsupported scalar functions that prevent full pushdown.
- Retrieval Keywords: TiFlash pushdown examples, EXPLAIN SELECT MAX(id + a) FROM t GROUP BY a, mpp[tiflash], plus(test.t.id, test.t.a), Projection_46, HashAgg_37, ExchangeSender_22, TableFullScan_21, Restrictions for pushdown, EXPLAIN SELECT id FROM t WHERE TIME(now()+ a) < '12:00:00', SHOW WARNINGS, Scalar function 'time' is not supported to push down to storage layer now, Scalar function 'cast' is not supported to push down to tiflash now, TableFullScan on TiFlash only, functions calculated and filtered on root
- Follow-up Guidance: The source also shows that SHOW WARNINGS reports which operators and expressions cannot be pushed down to TiFlash, including unsupported Time and Cast functions.
- Classification Note: This is reference content because it provides concrete EXPLAIN and SHOW WARNINGS examples, exact operator output, and documented pushdown restrictions for TiFlash.

## Official Source Content

### Example 2: Push expressions down to TiFlash

```sql
CREATE TABLE t(id INT PRIMARY KEY, a INT);
ALTER TABLE t SET TIFLASH REPLICA 1;
INSERT INTO t(id,a) VALUES (1,2),(2,4),(11,2),(12,4),(13,4),(14,7);

EXPLAIN SELECT MAX(id + a) FROM t GROUP BY a;

+------------------------------------+---------+--------------+---------------+---------------------------------------------------------------------------+
| id                                 | estRows | task         | access object | operator info                                                             |
+------------------------------------+---------+--------------+---------------+---------------------------------------------------------------------------+
| TableReader_45                     | 4.80    | root         |               | data:ExchangeSender_44                                                    |
| └─ExchangeSender_44                | 4.80    | mpp[tiflash] |               | ExchangeType: PassThrough                                                 |
|   └─Projection_39                  | 4.80    | mpp[tiflash] |               | Column#3                                                                  |
|     └─HashAgg_37                   | 4.80    | mpp[tiflash] |               | group by:Column#9, funcs:max(Column#8)->Column#3                          |
|       └─Projection_46              | 6.00    | mpp[tiflash] |               | plus(test.t.id, test.t.a)->Column#8, test.t.a                             |
|         └─ExchangeReceiver_23      | 6.00    | mpp[tiflash] |               |                                                                           |
|           └─ExchangeSender_22      | 6.00    | mpp[tiflash] |               | ExchangeType: HashPartition, Hash Cols: [name: test.t.a, collate: binary] |
|             └─TableFullScan_21     | 6.00    | mpp[tiflash] | table:t       | keep order:false, stats:pseudo                                            |
+------------------------------------+---------+--------------+---------------+---------------------------------------------------------------------------+
8 rows in set (0.18 sec)
```

In the preceding example, the expression `id + a` is pushed down to TiFlash for calculation in advance. This helps reduce the amount of data to be transferred over the network, thus reducing the network transmission overhead and improving the overall calculation performance. This is indicated by the `mpp[tiflash]` value in the `task` column of the row where the `operator` column has the `plus(test.t.id, test.t.a)` value.
### Example 3: Restrictions for pushdown

```sql
CREATE TABLE t(id INT PRIMARY KEY, a INT);
ALTER TABLE t SET TIFLASH REPLICA 1;
INSERT INTO t(id,a) VALUES (1,2),(2,4),(11,2),(12,4),(13,4),(14,7);

EXPLAIN SELECT id FROM t WHERE TIME(now()+ a) < '12:00:00';

+-----------------------------+---------+--------------+---------------+--------------------------------------------------------------------------------------------------+
| id                          | estRows | task         | access object | operator info                                                                                    |
+-----------------------------+---------+--------------+---------------+--------------------------------------------------------------------------------------------------+
| Projection_4                | 4.80    | root         |               | test.t.id                                                                                        |
| └─Selection_6               | 4.80    | root         |               | lt(cast(time(cast(plus(20230110083056, test.t.a), var_string(20))), var_string(10)), "12:00:00") |
|   └─TableReader_11          | 6.00    | root         |               | data:ExchangeSender_10                                                                           |
|     └─ExchangeSender_10     | 6.00    | mpp[tiflash] |               | ExchangeType: PassThrough                                                                        |
|       └─TableFullScan_9     | 6.00    | mpp[tiflash] | table:t       | keep order:false, stats:pseudo                                                                   |
+-----------------------------+---------+--------------+---------------+--------------------------------------------------------------------------------------------------+
5 rows in set, 3 warnings (0.20 sec)
```

The preceding example only performs `TableFullScan` on TiFlash. Other functions are calculated and filtered on `root` and are not pushed down to TiFlash.

You can identify the operators and expressions that cannot be pushed down to TiFlash by running the following command:

```sql
SHOW WARNINGS;

+---------+------+------------------------------------------------------------------------------------------------------------------------------------+
| Level   | Code | Message                                                                                                                            |
+---------+------+------------------------------------------------------------------------------------------------------------------------------------+
| Warning | 1105 | Scalar function 'time'(signature: Time, return type: time) is not supported to push down to storage layer now.                     |
| Warning | 1105 | Scalar function 'cast'(signature: CastDurationAsString, return type: var_string(10)) is not supported to push down to tiflash now. |
| Warning | 1105 | Scalar function 'cast'(signature: CastDurationAsString, return type: var_string(10)) is not supported to push down to tiflash now. |
+---------+------+------------------------------------------------------------------------------------------------------------------------------------+
3 rows in set (0.18 sec)
```

The expressions in the preceding example cannot be completely pushed down to TiFlash, because the functions `Time` and `Cast` cannot be pushed down to TiFlash.
