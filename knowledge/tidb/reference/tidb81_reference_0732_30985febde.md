# tidb_opt_ordering_index_selectivity_ratio examples and estimation behavior

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_opt_ordering_index_selectivity_ratio <span class="version-mark">New in v8.0.0</span>`
- Source Line Ranges: `4280-4383`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `tikv`
- Topic Tags: `system-variables`, `optimizer`, `order-by`, `limit`, `selectivity`, `estrows`, `index-scan`, `set-var`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0732_30985febde`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-opt-ordering-index-selectivity-ratio-span-class-version-mark-new-in-v8-0-0-span`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1ac96261aa3cc6a6ef65579f1ed926ecc5a86fdd548a855f7a1683316cbd4a3c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-opt-ordering-index-selectivity-ratio-span-class-version-mark-new-in-v8-0-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how tidb_opt_ordering_index_selectivity_ratio affects estRows for ORDER BY ... LIMIT queries where the ordering index does not cover some WHERE filter conditions.
- Retrieval Keywords: tidb_opt_ordering_index_selectivity_ratio, ORDER BY LIMIT, estRows, IndexFullScan, IndexRangeScan, IndexLookUp, TableRowIDScan, Selection_20(Probe), USE INDEX (ia), SET SESSION tidb_opt_ordering_index_selectivity_ratio = -1, SET SESSION tidb_opt_ordering_index_selectivity_ratio = 0, SET SESSION tidb_opt_ordering_index_selectivity_ratio = 0.1, SET SESSION tidb_opt_ordering_index_selectivity_ratio = 1, EXPLAIN SELECT * FROM t USE INDEX (ia) WHERE b <= 9000 ORDER BY a LIMIT 1, EXPLAIN SELECT * FROM t USE INDEX (ia) WHERE a <= 9000 AND b <= 9000 ORDER BY a LIMIT 1, tidb_opt_ordering_index_selectivity_threshold, SET_VAR, keep order:true
- Follow-up Guidance: The source also states that this variable addresses the same query patterns as tidb_opt_ordering_index_selectivity_threshold and that the final plan selection depends on the availability and cost of other plans.
- Classification Note: This is reference content because it defines the tidb_opt_ordering_index_selectivity_ratio system variable, including scope, type, default, range, SET_VAR applicability, and example EXPLAIN outputs showing estimation behavior.

## Official Source Content

### tidb_opt_ordering_index_selectivity_ratio New in v8.0.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Default value: `-1`
- Range: `[-1, 1]`
- This variable controls the estimated number of rows for an index that matches the SQL statement `ORDER BY` when there are `ORDER BY` and `LIMIT` clauses in a SQL statement, but does not cover some filter conditions.
- This addresses the same query patterns as the system variable [tidb_opt_ordering_index_selectivity_threshold](#tidb_opt_ordering_index_selectivity_threshold-new-in-v700).
- It differs in implementation by applying a ratio or percentage of the possible range that the qualified rows will be found.
- A value of `-1` (default) or less than `0` disables this ratio. Any value between `0` and `1` applies a ratio of 0% to 100% (for example, `0.5` corresponds to `50%`).
- In the following examples, the table `t` has a total of 1,000,000 rows. The same query is used, but different values for `tidb_opt_ordering_index_selectivity_ratio` are used. The query in the example contains a `WHERE` clause predicate that qualifies a small percentage of rows (9,000 out of 1,000,000). There is an index that supports the `ORDER BY a` (index `ia`), but the filter on `b` is not included in this index. Depending on the actual data distribution, the rows matching the `WHERE` clause and `LIMIT 1` might be found as the first row accessed when scanning the non-filtering index, or at worst, after nearly all the rows have been processed.
- Each example uses an index hint to demonstrate the impact on estRows. The final plan selection depends on the availability and cost of other plans.
- The first example uses the default value `-1`, which uses the existing estimation formula. By default, a small percentage of rows are scanned for estimation before the qualified rows are found.

    ```sql
    > SET SESSION tidb_opt_ordering_index_selectivity_ratio = -1;

    > EXPLAIN SELECT * FROM t USE INDEX (ia) WHERE b <= 9000 ORDER BY a LIMIT 1;
    +-----------------------------------+---------+-----------+-----------------------+---------------------------------+
    | id                                | estRows | task      | access object         | operator info                   |
    +-----------------------------------+---------+-----------+-----------------------+---------------------------------+
    | Limit_12                          | 1.00    | root      |                       | offset:0, count:1               |
    | └─Projection_22                   | 1.00    | root      |                       | test.t.a, test.t.b, test.t.c    |
    |   └─IndexLookUp_21                | 1.00    | root      |                       |                                 |
    |     ├─IndexFullScan_18(Build)     | 109.20  | cop[tikv] | table:t, index:ia(a)  | keep order:true                 |
    |     └─Selection_20(Probe)         | 1.00    | cop[tikv] |                       | le(test.t.b, 9000)              |
    |       └─TableRowIDScan_19         | 109.20  | cop[tikv] | table:t               | keep order:false                |
    +-----------------------------------+---------+-----------+-----------------------+---------------------------------+
    ```

- The second example uses `0`, which assumes that 0% of rows will be scanned before the qualified rows are found.

    ```sql
    > SET SESSION tidb_opt_ordering_index_selectivity_ratio = 0;

    > EXPLAIN SELECT * FROM t USE INDEX (ia) WHERE b <= 9000 ORDER BY a LIMIT 1;
    +-----------------------------------+---------+-----------+-----------------------+---------------------------------+
    | id                                | estRows | task      | access object         | operator info                   |
    +-----------------------------------+---------+-----------+-----------------------+---------------------------------+
    | Limit_12                          | 1.00    | root      |                       | offset:0, count:1               |
    | └─Projection_22                   | 1.00    | root      |                       | test.t.a, test.t.b, test.t.c    |
    |   └─IndexLookUp_21                | 1.00    | root      |                       |                                 |
    |     ├─IndexFullScan_18(Build)     | 1.00    | cop[tikv] | table:t, index:ia(a)  | keep order:true                 |
    |     └─Selection_20(Probe)         | 1.00    | cop[tikv] |                       | le(test.t.b, 9000)              |
    |       └─TableRowIDScan_19         | 1.00    | cop[tikv] | table:t               | keep order:false                |
    +-----------------------------------+---------+-----------+-----------------------+---------------------------------+
    ```

- The third example uses `0.1`, which assumes that 10% of rows will be scanned before the qualified rows are found. This condition is highly selective, with only 1% of rows meeting the condition. Therefore, in the worst-case scenario, it might be necessary to scan 99% of rows before finding the 1% that qualify. 10% of that 99% is approximately 9.9%, which is reflected in the estRows.

    ```sql
    > SET SESSION tidb_opt_ordering_index_selectivity_ratio = 0.1;

    > EXPLAIN SELECT * FROM t USE INDEX (ia) WHERE b <= 9000 ORDER BY a LIMIT 1;
    +-----------------------------------+----------+-----------+-----------------------+---------------------------------+
    | id                                | estRows  | task      | access object         | operator info                   |
    +-----------------------------------+----------+-----------+-----------------------+---------------------------------+
    | Limit_12                          | 1.00     | root      |                       | offset:0, count:1               |
    | └─Projection_22                   | 1.00     | root      |                       | test.t.a, test.t.b, test.t.c    |
    |   └─IndexLookUp_21                | 1.00     | root      |                       |                                 |
    |     ├─IndexFullScan_18(Build)     | 99085.21 | cop[tikv] | table:t, index:ia(a)  | keep order:true                 |
    |     └─Selection_20(Probe)         | 1.00     | cop[tikv] |                       | le(test.t.b, 9000)              |
    |       └─TableRowIDScan_19         | 99085.21 | cop[tikv] | table:t               | keep order:false                |
    +-----------------------------------+----------+-----------+-----------------------+---------------------------------+
    ```

- The fourth example uses `1.0`, which assumes that 100% of rows will be scanned before the qualified rows are found.
    ```sql
    > SET SESSION tidb_opt_ordering_index_selectivity_ratio = 1;

    > EXPLAIN SELECT * FROM t USE INDEX (ia) WHERE b <= 9000 ORDER BY a LIMIT 1;
    +-----------------------------------+-----------+-----------+-----------------------+---------------------------------+
    | id                                | estRows   | task      | access object         | operator info                   |
    +-----------------------------------+-----------+-----------+-----------------------+---------------------------------+
    | Limit_12                          | 1.00      | root      |                       | offset:0, count:1               |
    | └─Projection_22                   | 1.00      | root      |                       | test.t.a, test.t.b, test.t.c    |
    |   └─IndexLookUp_21                | 1.00      | root      |                       |                                 |
    |     ├─IndexFullScan_18(Build)     | 990843.14 | cop[tikv] | table:t, index:ia(a)  | keep order:true                 |
    |     └─Selection_20(Probe)         | 1.00      | cop[tikv] |                       | le(test.t.b, 9000)              |
    |       └─TableRowIDScan_19         | 990843.14 | cop[tikv] | table:t               | keep order:false                |
    +-----------------------------------+-----------+-----------+-----------------------+---------------------------------+
    ```

- The fifth example also uses `1.0`, but adds a predicate on `a`, limiting the scan range in the worst-case scenario. This is because `WHERE a <= 9000` matches the index, with approximately 9,000 rows would qualify. Given that the filter predicate on `b` is not in the index, all the approximately 9,000 rows are considered to be scanned before finding a row that matches `b <= 9000`.

    ```sql
    > SET SESSION tidb_opt_ordering_index_selectivity_ratio = 1;

    > EXPLAIN SELECT * FROM t USE INDEX (ia) WHERE a <= 9000 AND b <= 9000 ORDER BY a LIMIT 1;
    +------------------------------------+---------+-----------+-----------------------+------------------------------------+
    | id                                 | estRows | task      | access object         | operator info                      |
    +------------------------------------+---------+-----------+-----------------------+------------------------------------+
    | Limit_12                           | 1.00    | root      |                       | offset:0, count:1                  |
    | └─Projection_22                    | 1.00    | root      |                       | test.t.a, test.t.b, test.t.c       |
    |   └─IndexLookUp_21                 | 1.00    | root      |                       |                                    |
    |     ├─IndexRangeScan_18(Build)     | 9074.99 | cop[tikv] | table:t, index:ia(a)  | range:[-inf,9000], keep order:true |
    |     └─Selection_20(Probe)          | 1.00    | cop[tikv] |                       | le(test.t.b, 9000)                 |
    |       └─TableRowIDScan_19          | 9074.99 | cop[tikv] | table:t               | keep order:false                   |
    +------------------------------------+---------+-----------+-----------------------+------------------------------------+
    ```
