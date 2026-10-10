# store request batching and limit variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_store_batch_size | System Variables > Variable reference > tidb_store_limit <span class="version-mark">New in v3.0.4 and v4.0</span>`
- Source Line Ranges: `5608-5627`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `coprocessor`, `indexlookup`, `batching`, `request-limits`, `concurrency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0744_3ab427080a`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-store-batch-size`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `298b715c37d0262985d6a0e7d146ca803471c23c4fb89b1071ffb2c987e5eb15`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-store-batch-size
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up variables that control IndexLookUp coprocessor task batching or limit how many requests TiDB sends to TiKV at the same time.
- Retrieval Keywords: tidb_store_batch_size, tidb_store_limit, Coprocessor Tasks, IndexLookUp, batch size, disable batch, maximum number of requests, TiDB send to TiKV, request limit, SET_VAR
- Follow-up Guidance: The content states that increasing tidb_store_batch_size can optimize the query when the number of tasks is relatively large and slow queries occur.
- Classification Note: This is reference content because it defines the purpose, scope, defaults, and ranges of the tidb_store_batch_size and tidb_store_limit system variables.

## Official Source Content

### tidb_store_batch_size

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `4`
- Range: `[0, 25000]`
- This variable is used to control the batch size of the Coprocessor Tasks of the `IndexLookUp` operator. `0` means to disable batch. When the number of tasks is relatively large and slow queries occur, you can increase this variable to optimize the query.
### tidb_store_limit New in v3.0.4 and v4.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 9223372036854775807]`
- This variable is used to limit the maximum number of requests TiDB can send to TiKV at the same time. 0 means no limit.
