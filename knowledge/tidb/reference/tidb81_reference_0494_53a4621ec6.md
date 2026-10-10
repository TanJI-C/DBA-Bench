# Runtime Filter type and limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/runtime-filter.md`
- Source Title: `Runtime Filter`
- Source Heading Path: `Runtime Filter > Configure Runtime Filter > Runtime Filter type | Runtime Filter > Limitations`
- Source Line Ranges: `246-258`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `sql`
- Topic Tags: `runtime filter`, `system variable`, `predicate type`, `in predicate`, `mpp`, `tiflash pushdown`, `join limitations`, `explain plan`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0494_53a4621ec6`
- Source ID: `tidb-docs-8.1:runtime-filter.md#runtime-filter-type`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8d226c0e42a6d636518f7e761b495300206b9aaf9232d1c67693ee03ad716c40`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/runtime-filter#runtime-filter-type
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/runtime-filter.md

## Retrieval Guidance

- Use When: Use this chunk when checking which Runtime Filter predicate type is supported, what `tidb_runtime_filter_type` controls, or why Runtime Filter is not generated for an MPP join pushed down to TiFlash.
- Retrieval Keywords: Runtime Filter type, tidb_runtime_filter_type, IN, generated predicate similar to k1 in (xxx), MPP architecture, queries pushed down to TiFlash, Left outer join, Full outer join, Anti join, probe side, equal join expression, probe column, JSON, Blob, Array, complex data types, EXPLAIN statement, execution plan
- Follow-up Guidance: To confirm whether Runtime Filter is generated correctly under these limitations, the source says to use the `EXPLAIN` statement to verify the execution plan.
- Classification Note: This is reference content because it defines the supported Runtime Filter type and lists explicit limitations for join types, probe expressions, data types, and TiFlash MPP applicability from the official documentation.

## Official Source Content

### Runtime Filter type

The type of Runtime Filter is the type of the predicate used by the generated Filter operator. Currently, only one type is supported: `IN`, which means that the generated predicated is similar to `k1 in (xxx)`. The Runtime Filter type is controlled by the system variable [`tidb_runtime_filter_type`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_runtime_filter_type-new-in-v720).

- `IN`: the default type. It means that the generated Runtime Filter uses the `IN` type predicate.
## Limitations

- Runtime Filter is an optimization in the MPP architecture and can only be applied to queries pushed down to TiFlash.
- Join type: Left outer, Full outer, and Anti join (when the left table is the probe side) do not support Runtime Filter. Because Runtime Filter filters the data involved in the join in advance, the preceding types of join do not discard the unmatched data, so Runtime Filter cannot be used.
- Equal join expression: When the probe column in the equal join expression is a complex expression, or when the probe column type is JSON, Blob, Array, or other complex data types, Runtime Filter is not generated. The main reason is that the preceding types of columns are rarely used as the join column. Even if the Filter is generated, the filtering rate is usually low.

For the preceding limitations, if you need to confirm whether Runtime Filter is generated correctly, you can use the [`EXPLAIN` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain) to verify the execution plan.
