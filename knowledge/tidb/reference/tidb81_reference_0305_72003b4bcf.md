# TiKV expression pushdown overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/expressions-pushed-down.md`
- Source Title: `List of Expressions for Pushdown`
- Source Heading Path: `List of Expressions for Pushdown | List of Expressions for Pushdown > Supported expressions for pushdown to TiKV`
- Source Line Ranges: `5-17`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiflash`, `sql`
- Topic Tags: `expression-pushdown`, `functions`, `operators`, `tikv`, `tiflash`, `window-functions`, `blocklist`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0305_72003b4bcf`
- Source ID: `tidb-docs-8.1:functions-and-operators/expressions-pushed-down.md#list-of-expressions-for-pushdown`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e1d635f1a8c72271a8fd68ca75a54fea056867a70f605e1aba40f0387b3100d7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/expressions-pushed-down#list-of-expressions-for-pushdown
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/expressions-pushed-down.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about what expression pushdown means in TiDB, whether functions or operators can be pushed down to TiKV, or where TiFlash pushdown support is referenced.
- Retrieval Keywords: List of Expressions for Pushdown, Supported expressions for pushdown to TiKV, expression pushdown, push down some expressions, functions or operators, TiDB reads data from TiKV, blocklist, prohibit specific expressions from being pushed down, TiFlash supported pushdown calculations, Aggregate functions do not support pushdown to TiKV when used as window functions
- Follow-up Guidance: The source also points to TiFlash supported pushdown calculations and notes that aggregate functions do not support pushdown to TiKV when used as window functions.
- Classification Note: This is reference content because it gives an overview of expression pushdown behavior, scope, and related limitations rather than a step-by-step procedure.

## Official Source Content

# List of Expressions for Pushdown

When TiDB reads data from TiKV, TiDB tries to push down some expressions (including calculations of functions or operators) to be processed to TiKV. This reduces the amount of transferred data and offloads processing from a single TiDB node. This document introduces the expressions that TiDB already supports pushing down and how to prohibit specific expressions from being pushed down using blocklist.

TiFlash also supports pushdown for the functions and operators [listed on this page](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations).

> **Note:**
>
> The Aggregate functions do not support pushdown to TiKV when used as [window functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions).
## Supported expressions for pushdown to TiKV
