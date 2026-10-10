# Comparison with deprecated batch-dml

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/non-transactional-dml.md`
- Source Title: `Non-Transactional DML Statements`
- Source Heading Path: `Non-Transactional DML Statements > Comparison with batch-dml`
- Source Line Ranges: `315-328`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `batch-dml`, `comparison`, `deprecation`, `performance`, `stability`, `shard-column`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0450_963b54d0f1`
- Source ID: `tidb-docs-8.1:non-transactional-dml.md#comparison-with-batch-dml`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `865e337f7cad51893ec3dda98a1f4e58c1b988945c68749f73c515eeae61bd45`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/non-transactional-dml#comparison-with-batch-dml
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/non-transactional-dml.md

## Retrieval Guidance

- Use When: Use this chunk when comparing non-transactional DML statements with deprecated batch-dml in terms of performance, stability, data index inconsistency risk, or shard column efficiency.
- Retrieval Keywords: batch-dml, deprecated batch-dml, non-transactional DML statements, comparison with batch-dml, data index inconsistency, performance, stability, shard column, main differences
- Follow-up Guidance: For unexpected behavior caused by improper use of non-transactional DML statements, see the common issues section about non-transactional DELETE not being equivalent to ordinary DELETE.
- Classification Note: This is reference content because it describes the differences between batch-dml and non-transactional DML statements, including deprecation, performance, and stability characteristics.

## Official Source Content

## Comparison with batch-dml

batch-dml is a mechanism for splitting a transaction into multiple transaction commits during the execution of a DML statement.

> **Note:**
>
> It is not recommended to use batch-dml which has been deprecated. When the batch-dml feature is not properly used, there is a risk of data index inconsistency.

Non-transactional DML statements are not yet a replacement for all batch-dml usage scenarios. Their main differences are as follows:

- Performance: When the [shard column](#how-to-select-a-shard-column) is efficient, the performance of non-transactional DML statements is close to that of batch-dml. When the shard column is less efficient, the performance of non-transactional DML statements is significantly lower than that of batch-dml.

- Stability: batch-dml is prone to data index inconsistencies due to improper use. Non-transactional DML statements do not cause data index inconsistencies. However, when used improperly, non-transactional DML statements are not equivalent to the original statements, and the applications might observe unexpected behavior. See the [common issues section](#non-transactional-delete-has-exceptional-behavior-that-is-not-equivalent-to-ordinary-delete) for details.
