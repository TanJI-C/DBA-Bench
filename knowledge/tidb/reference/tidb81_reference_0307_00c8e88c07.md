# Blocklist specific expressions for pushdown

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/expressions-pushed-down.md`
- Source Title: `List of Expressions for Pushdown`
- Source Heading Path: `List of Expressions for Pushdown > Blocklist specific expressions`
- Source Line Ranges: `34-36`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `expression-pushdown`, `blocklist`, `functions`, `operators`, `data-types`, `enum`, `bit`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0307_00c8e88c07`
- Source ID: `tidb-docs-8.1:functions-and-operators/expressions-pushed-down.md#blocklist-specific-expressions`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bfcdddcd75a180d0cf56456052cfbd16f4a440f1c7b66edc2fef0b4922b4d776`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/expressions-pushed-down#blocklist-specific-expressions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/expressions-pushed-down.md

## Retrieval Guidance

- Use When: Use this chunk when looking for official guidance on disabling pushdown for specific supported expressions or the ENUM and BIT data types after unexpected calculation behavior during pushdown.
- Retrieval Keywords: Blocklist specific expressions, expression pushdown, supported expressions for pushdown to TiKV, unexpected behavior occurs in the calculation process, ENUM type, BIT type, mysql.expr_pushdown_blacklist, prohibit the pushdown of specific expressions, functions operators or data types
- Follow-up Guidance: The source points to adding entries to the blocklist and refers to Add to the blocklist for details on disabling the pushdown of specific expressions.
- Classification Note: This is reference content because it identifies the exact blocklist table and the specific expression and data type categories that can be prohibited from pushdown.

## Official Source Content

## Blocklist specific expressions

If unexpected behavior occurs in the calculation process when pushing down the [supported expressions](#supported-expressions-for-pushdown-to-tikv) or specific data types (**only** the [`ENUM` type](https://docs.pingcap.com/tidb/stable/data-type-string#enum-type) and the [`BIT` type](https://docs.pingcap.com/tidb/stable/data-type-numeric#bit-type)), you can restore the application quickly by prohibiting the pushdown of the corresponding functions, operators, or data types. Specifically, you can prohibit the functions, operators, or data types from being pushed down by adding them to the blocklist `mysql.expr_pushdown_blacklist`. For details, refer to [Add to the blocklist](https://docs.pingcap.com/tidb/stable/blocklist-control-plan#disable-the-pushdown-of-specific-expressions).
