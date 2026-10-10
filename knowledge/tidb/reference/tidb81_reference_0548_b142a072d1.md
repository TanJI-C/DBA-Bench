# CREATE BINDING overview and syntax

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-binding.md`
- Source Title: `CREATE [GLOBAL|SESSION] BINDING`
- Source Heading Path: `CREATE [GLOBAL|SESSION] BINDING | CREATE [GLOBAL|SESSION] BINDING > Synopsis | CREATE [GLOBAL|SESSION] BINDING > Examples`
- Source Line Ranges: `5-37`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `plan-binding`, `sql-syntax`, `plan-baselines`, `session-binding`, `global-binding`, `optimizer-hints`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0548_b142a072d1`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-binding.md#create-global-session-binding`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b5c2dfeac46c1178457af811904557b716324e370447dc20907cc0ac8dd1ade6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-binding#create-global-session-binding
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-binding.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the purpose, scope, syntax, or prerequisites of CREATE [GLOBAL|SESSION] BINDING in TiDB.
- Retrieval Keywords: CREATE BINDING, CREATE GLOBAL BINDING, CREATE SESSION BINDING, execution plan binding, plan baselines, optimizer hint, tidb_use_plan_baselines, CreateBindingStmt, FOR BindableStmt USING BindableStmt, FROM HISTORY USING PLAN DIGEST, PlanDigest, GLOBAL or SESSION basis, parameterized SQL statement, system table
- Follow-up Guidance: The examples section states that you can create a binding according to a SQL statement or a historical execution plan.
- Classification Note: This is reference content because it defines what CREATE [GLOBAL|SESSION] BINDING does, its syntax, and the conditions under which a stored binding is used.

## Official Source Content

# CREATE [GLOBAL|SESSION] BINDING

This statement creates a new execution plan binding in TiDB. Binding can be used to inject a hint into a statement without requiring changes to the underlying query.

A `BINDING` can be on either a `GLOBAL` or `SESSION` basis. The default is `SESSION`.

The bound SQL statement is parameterized and stored in the system table. When a SQL query is processed, as long as the parameterized SQL statement and a bound one in the system table are consistent and the system variable `tidb_use_plan_baselines` is set to `ON` (default), the corresponding optimizer hint is available. If multiple execution plans are available, the optimizer chooses to bind the plan with the least cost. For more information, see [Create a binding](https://docs.pingcap.com/tidb/stable/sql-plan-management#create-a-binding).
## Synopsis

```ebnf+diagram
CreateBindingStmt ::=
    'CREATE' GlobalScope 'BINDING' ( 'FOR' BindableStmt 'USING' BindableStmt
|   'FROM' 'HISTORY' 'USING' 'PLAN' 'DIGEST' PlanDigest )

GlobalScope ::=
    ( 'GLOBAL' | 'SESSION' )?

BindableStmt ::=
    ( SelectStmt | UpdateStmt | InsertIntoStmt | ReplaceIntoStmt | DeleteStmt )
```

****
## Examples

You can create a binding according to a SQL statement or a historical execution plan.

The following example shows how to create a binding according to a SQL statement.
