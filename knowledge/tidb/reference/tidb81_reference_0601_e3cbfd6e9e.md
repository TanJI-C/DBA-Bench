# IMPORT INTO syntax and parameter descriptions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-import-into.md`
- Source Title: `IMPORT INTO`
- Source Heading Path: `IMPORT INTO > Synopsis | IMPORT INTO > Parameter description | IMPORT INTO > Parameter description > ColumnNameOrUserVarList | IMPORT INTO > Parameter description > SetClause`
- Source Line Ranges: `67-111`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `syntax`, `ebnf`, `parameters`, `column-mapping`, `user-variables`, `set-clause`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0601_e3cbfd6e9e`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-import-into.md#synopsis`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `387774b08f0eb6e3aa9a6d6085c2fbb6e3b41b84b040203c5dcb463293142232`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into#synopsis
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-import-into.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the formal `IMPORT INTO` syntax or the exact rules for `ColumnNameOrUserVarList` and `SET` column mapping expressions.
- Retrieval Keywords: IMPORT INTO synopsis, ImportIntoStmt, ColumnNameOrUserVarList, ColumnNameList, SetClause, SetItem, FORMAT "CSV", FORMAT "SQL", FORMAT "PARQUET", WithOptions, OptionItem, ColumnNameOrUserVar, user variables, field corresponds to columns, SET expression invalid
- Follow-up Guidance: The same source also contains restrictions and prerequisites for `IMPORT INTO`, including differences between `FROM FILE` and `FROM SELECT`.
- Classification Note: This is reference content because it defines the EBNF-style syntax and parameter semantics for `IMPORT INTO` statements and column-mapping behavior.

## Official Source Content

## Synopsis

```ebnf+diagram
ImportIntoStmt ::=
    'IMPORT' 'INTO' TableName ColumnNameOrUserVarList? SetClause? FROM fileLocation Format? WithOptions?
    |
    'IMPORT' 'INTO' TableName ColumnNameList? FROM SelectStatement WithOptions?

ColumnNameOrUserVarList ::=
    '(' ColumnNameOrUserVar (',' ColumnNameOrUserVar)* ')'

ColumnNameList ::=
    '(' ColumnName (',' ColumnName)* ')'

SetClause ::=
    'SET' SetItem (',' SetItem)*

SetItem ::=
    ColumnName '=' Expr

Format ::=
    'FORMAT' ('"CSV"' | '"SQL"' | '"PARQUET"')

WithOptions ::=
    'WITH' OptionItem (',' OptionItem)*

OptionItem ::=
    optionName '=' optionVal | optionName
```
## Parameter description
### ColumnNameOrUserVarList

It specifies how each field in the data file corresponds to the columns in the target table. You can also use it to map fields to variables to skip certain fields for the import, or use it in `SetClause`.

- If this parameter is not specified, the number of fields in each row of the data file must match the number of columns in the target table, and the fields will be imported to the corresponding columns in order.
- If this parameter is specified, the number of specified columns or variables must match the number of fields in each row of the data file.
### SetClause

It specifies how the values of target columns are calculated. In the right side of the `SET` expression, you can reference the variables specified in `ColumnNameOrUserVarList`.

In the left side of the `SET` expression, you can only reference a column name that is not included in `ColumnNameOrUserVarList`. If the target column name already exists in `ColumnNameOrUserVarList`, the `SET` expression is invalid.
