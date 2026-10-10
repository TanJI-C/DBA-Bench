# Deprecated batch commit and batch DML variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_batch_commit | System Variables > Variable reference > tidb_batch_delete | System Variables > Variable reference > tidb_batch_insert`
- Source Line Ranges: `1286-1321`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `batch-commit`, `batch-dml`, `delete`, `insert`, `deprecated`, `non-atomic-commit`, `data-corruption-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0162_89dd3e7646`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-batch-commit`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0aa2213e116d98c6a7f3343868402a06010b8c8ba200df3eddbf9ba693658621`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-batch-commit
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when searching for deprecated TiDB batch commit or batch DML session variables and their non-atomic commit or data corruption warnings for DELETE and INSERT.
- Retrieval Keywords: tidb_batch_commit, tidb_batch_delete, tidb_batch_insert, deprecated batch-commit feature, deprecated batch-dml feature, DELETE statements might be split into multiple transactions, INSERT statements might be split into multiple transactions, committed non-atomically, tidb_enable_batch_dml, tidb_dml_batch_size, non-transactional DML
- Follow-up Guidance: The content states that tidb_batch_delete and tidb_batch_insert require tidb_enable_batch_dml and a positive tidb_dml_batch_size to work, and it points to non-transactional DML instead.
- Classification Note: This is classified as configuration because it documents SESSION-scope TiDB system variables and their warnings, defaults, and behavior.

## Official Source Content

### tidb_batch_commit

> **Warning:**
>
> It is **NOT** recommended to enable this variable.

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- The variable is used to control whether to enable the deprecated batch-commit feature. When this variable is enabled, a transaction might be split into multiple transactions by grouping a few statements and committed non-atomically, which is not recommended.
### tidb_batch_delete

> **Warning:**
>
> This variable is associated with the deprecated batch-dml feature, which might cause data corruption. Therefore, it is not recommended to enable this variable for batch-dml. Instead, use [non-transactional DML](https://docs.pingcap.com/tidb/stable/non-transactional-dml).

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to control whether to enable the batch-delete feature, which is a part of the deprecated batch-dml feature. When this variable is enabled, `DELETE` statements might be split into multiple transactions and committed non-atomically. To make it work, you also need to enable `tidb_enable_batch_dml` and set a positive value for `tidb_dml_batch_size`, which is not recommended.
### tidb_batch_insert

> **Warning:**
>
> This variable is associated with the deprecated batch-dml feature, which might cause data corruption. Therefore, it is not recommended to enable this variable for batch-dml. Instead, use [non-transactional DML](https://docs.pingcap.com/tidb/stable/non-transactional-dml).

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable is used to control whether to enable the batch-insert feature, which is a part of the deprecated batch-dml feature. When this variable is enabled, `INSERT` statements might be split into multiple transactions and committed non-atomically. To make it work, you also need to enable `tidb_enable_batch_dml` and set a positive value for `tidb_dml_batch_size`, which is not recommended.
