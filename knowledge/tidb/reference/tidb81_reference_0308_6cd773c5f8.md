# Function and Operator Reference overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/functions-and-operators-overview.md`
- Source Title: `Function and Operator Reference`
- Source Heading Path: `Function and Operator Reference`
- Source Line Ranges: `5-15`
- Source Scope: `shared`
- Primary Component: `sql`
- Related Components: `tikv`, `tiflash`
- Topic Tags: `functions`, `operators`, `expressions`, `pushdown`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0308_6cd773c5f8`
- Source ID: `tidb-docs-8.1:functions-and-operators/functions-and-operators-overview.md#function-and-operator-reference`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7bef5d53c442cc2ba8b28349f5b75d6c7832753f7b22d43a43b7a721a54a93a7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/functions-and-operators-overview#function-and-operator-reference
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/functions-and-operators-overview.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks for the overall scope of TiDB function and operator usage in SQL expressions, including where expressions can appear and where to find pushdown support references.
- Retrieval Keywords: Function and Operator Reference, Functions and Operators in MySQL, expressions, ORDER BY, HAVING, SELECT, WHERE, DELETE, UPDATE, SET, built-in functions, operators, NULL, List of expressions for pushdown, TiKV, TiFlash, Push-down expressions
- Follow-up Guidance: It points to the list of expressions for pushdown to TiKV and the TiFlash push-down expressions documentation for supported pushdown details.
- Classification Note: This is reference content because it summarizes expression usage in TiDB SQL and links to authoritative function, operator, and pushdown support references.

## Official Source Content

# Function and Operator Reference

The usage of the functions and operators in TiDB is similar to MySQL. See [Functions and Operators in MySQL](https://dev.mysql.com/doc/refman/8.0/en/functions.html).

In SQL statements, expressions can be used on the `ORDER BY` and `HAVING` clauses of the [`SELECT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select) statement, the `WHERE` clause of [`SELECT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select)/[`DELETE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-delete)/[`UPDATE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-update) statements, and [`SET`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-variable) statements.

You can write expressions using literals, column names, `NULL`, built-in functions, operators, and so on. 

- For expressions that TiDB supports pushing down to TiKV, see [List of expressions for pushdown](https://docs.pingcap.com/tidb/stable/functions-and-operators/expressions-pushed-down). 
- For expressions that TiDB supports pushing down to [TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview), see [Push-down expressions](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations#push-down-expressions).
