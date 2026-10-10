# Reducing write transaction memory usage and transition to other behaviors

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/configure-memory-usage.md`
- Source Title: `TiDB Memory Control`
- Source Heading Path: `TiDB Memory Control > Reduce the memory usage for write transactions in tidb-server | TiDB Memory Control > Other memory control behaviors of tidb-server`
- Source Line Ranges: `132-137`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `write-transactions`, `large-transactions`, `dml`, `bulk-mode`, `memory-usage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0083_ec9b9bd223`
- Source ID: `tidb-docs-8.1:configure-memory-usage.md#reduce-the-memory-usage-for-write-transactions-in-tidb-server`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1f841eb9a06ff11261d4298cb8553c109767be3b5a8d16b3e08e88b576539bb5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/configure-memory-usage#reduce-the-memory-usage-for-write-transactions-in-tidb-server
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/configure-memory-usage.md

## Retrieval Guidance

- Use When: Use this chunk when the need is to find official guidance for reducing TiDB memory usage caused by large write transactions.
- Retrieval Keywords: Reduce the memory usage for write transactions in tidb-server, tidb_dml_type, bulk, Non-transactional DML statements, large transactions, write operations are first cached in memory before being committed
- Follow-up Guidance: The source states that to reduce or avoid high memory usage by large transactions, you can adjust tidb_dml_type to "bulk" or use Non-transactional DML statements.
- Classification Note: This is classified as performance because it discusses transaction write memory as a bottleneck and identifies documented behaviors that reduce memory usage for large write workloads.

## Official Source Content

## Reduce the memory usage for write transactions in tidb-server

The transaction model used by TiDB requires that all write operations of transactions are first cached in memory before being committed. When TiDB writes large transactions, memory usage might increase and become a bottleneck. To reduce or avoid high memory usage by large transactions under various constraints, you can adjust the [`tidb_dml_type`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_type-new-in-v800) system variable to `"bulk"` or use [Non-transactional DML statements](https://docs.pingcap.com/tidb/stable/non-transactional-dml).
## Other memory control behaviors of tidb-server
