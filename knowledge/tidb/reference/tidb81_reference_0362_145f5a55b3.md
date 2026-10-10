# Generated column index replacement rules and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/generated-columns.md`
- Source Title: `Generated Columns`
- Source Heading Path: `Generated Columns > Generated columns index replacement rule | Generated Columns > Limitations`
- Source Line Ranges: `105-157`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `optimizer`, `index-replacement`, `expression-substitution`, `virtual-columns`, `stored-columns`, `type-conversion`, `system-variables`, `limitations`, `alter-table`, `json-functions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0362_145f5a55b3`
- Source ID: `tidb-docs-8.1:generated-columns.md#generated-columns-index-replacement-rule`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ecfe481a0e5fe94246544b06b068698424a2de7af53f4ad380136ab546796b61`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/generated-columns#generated-columns-index-replacement-rule
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/generated-columns.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how TiDB replaces query expressions with indexed generated columns, or about limitations of generated columns and JSON support.
- Retrieval Keywords: generated columns index replacement rule, strictly equivalent, optimizer, expression substitution, a+1, create table t(a int), alter table t add column b bigint as (a+1) virtual, alter table t add index idx_b(b), desc select a+1 from t where a+1=3, IndexReader, IndexRangeScan, table:t, index:idx_b(b), type conversion rules, tidb_enable_unsafe_substitute, different lengths, string type, ALTER TABLE limitations, cannot add a stored generated column through ALTER TABLE, cannot modify the expression of a stored generated column, JSON functions, NULLIF() function, CASE function, valid only when the generated column is a virtual generated column
- Follow-up Guidance: The source notes that index replacement is currently valid only for virtual generated columns, while stored generated columns can still use the index when the generated column itself is referenced directly.
- Classification Note: This is reference content because it specifies the exact replacement rule, the type and system variable conditions affecting substitution, and enumerates explicit ALTER TABLE, JSON function, and stored-column limitations.

## Official Source Content

## Generated columns index replacement rule

When an expression in a query is strictly equivalent to a generated column with an index, TiDB replaces the expression with the corresponding generated column, so that the optimizer can take that index into account during execution plan construction.

The following example creates a generated column for the expression `a+1` and adds an index. The column type of `a` is int and the column type of `a+1` is bigint. If the type of the generated column is set to int, the replacement will not occur. For type conversion rules, see [Type Conversion of Expression Evaluation](https://docs.pingcap.com/tidb/stable/functions-and-operators/type-conversion-in-expression-evaluation).

```sql
create table t(a int);
desc select a+1 from t where a+1=3;
```

```sql
+---------------------------+----------+-----------+---------------+--------------------------------+
| id                        | estRows  | task      | access object | operator info                  |
+---------------------------+----------+-----------+---------------+--------------------------------+
| Projection_4              | 8000.00  | root      |               | plus(test.t.a, 1)->Column#3    |
| └─TableReader_7           | 8000.00  | root      |               | data:Selection_6               |
|   └─Selection_6           | 8000.00  | cop[tikv] |               | eq(plus(test.t.a, 1), 3)       |
|     └─TableFullScan_5     | 10000.00 | cop[tikv] | table:t       | keep order:false, stats:pseudo |
+---------------------------+----------+-----------+---------------+--------------------------------+
4 rows in set (0.00 sec)
```

```sql
alter table t add column b bigint as (a+1) virtual;
alter table t add index idx_b(b);
desc select a+1 from t where a+1=3;
```

```sql
+------------------------+---------+-----------+-------------------------+---------------------------------------------+
| id                     | estRows | task      | access object           | operator info                               |
+------------------------+---------+-----------+-------------------------+---------------------------------------------+
| IndexReader_6          | 10.00   | root      |                         | index:IndexRangeScan_5                      |
| └─IndexRangeScan_5     | 10.00   | cop[tikv] | table:t, index:idx_b(b) | range:[3,3], keep order:false, stats:pseudo |
+------------------------+---------+-----------+-------------------------+---------------------------------------------+
2 rows in set (0.01 sec)
```

> **Note:**
>
> If the expression to be replaced and the generated column are both the string type but with different lengths, you can still replace the expression by setting the system variable [`tidb_enable_unsafe_substitute`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_unsafe_substitute-new-in-v630) to `ON`. When configuring this system variable, ensure that the value calculated by the generated column strictly satisfies the definition of the generated column. Otherwise, the data might be truncated due to the difference in length, resulting in an incorrect result. See GitHub issue [#35490](https://github.com/pingcap/tidb/issues/35490#issuecomment-1211658886).
## Limitations

The current limitations of JSON and generated columns are as follows:

- You cannot add a stored generated column through `ALTER TABLE`.
- You can neither convert a stored generated column to a normal column through the `ALTER TABLE` statement nor convert a normal column to a stored generated column.
- You cannot modify the expression of a stored generated column through the `ALTER TABLE` statement.
- Not all [JSON functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions) are supported.
- The [`NULLIF()` function](https://docs.pingcap.com/tidb/stable/functions-and-operators/control-flow-functions#nullif) is not supported. You can use the [`CASE` function](https://docs.pingcap.com/tidb/stable/functions-and-operators/control-flow-functions#case) instead.
- Currently, the generated column index replacement rule is valid only when the generated column is a virtual generated column. It is not valid on the stored generated column, but the index can still be used by directly using the generated column itself.
