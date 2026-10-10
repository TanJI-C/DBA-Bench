# Expression syntax overview and grammar rules

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/expression-syntax.md`
- Source Title: `Expression Syntax`
- Source Heading Path: `Expression Syntax`
- Source Line Ranges: `5-50`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `expressions`, `sql-syntax`, `grammar`, `parser`, `predicates`, `literals`, `functions`, `window-functions`, `variables`, `case-expressions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0274_c3c4475e03`
- Source ID: `tidb-docs-8.1:expression-syntax.md#expression-syntax`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cc5b39d1eb76cd50d98781be7067653f7d7576f47adf57c2a5eb69b994992c04`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/expression-syntax#expression-syntax
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/expression-syntax.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB SQL expression syntax overview, the grammar categories of expressions, or the EBNF rules for `Expression`, `PredicateExpr`, `BitExpr`, and `SimpleExpr`.
- Retrieval Keywords: Expression Syntax, Expression ::=, PredicateExpr ::=, BitExpr ::=, SimpleExpr ::=, SELECT statement clauses, Group by clause, Where clause, Having clause, Join condition, window function, ParamMarker (`?`), system variables, user variables, CASE expressions, MATCH ... AGAINST, SubSelect, FunctionCallKeyword, WindowFuncCall, Literal, parser.y
- Follow-up Guidance: The source also points to related references for Schema object names, Literal values, Functions and operators overview, and Window functions.
- Classification Note: This is reference content because it defines official expression categories and parser-based grammar rules used by TiDB SQL.

## Official Source Content

# Expression Syntax

An expression is a combination of one or more values, operators, or functions. In TiDB, expressions are mainly used in various clauses of the `SELECT` statement, including Group by clause, Where clause, Having clause, Join condition and window function. In addition, some DDL statements also use expressions, such as the setting of the default values, columns, and partition rules when creating tables.

The expressions can be divided into the following types:

- Identifier. For reference, see [Schema object names](https://docs.pingcap.com/tidb/stable/schema-object-names).

- Predicates, numeric values, strings, date expressions. The [Literal values](https://docs.pingcap.com/tidb/stable/literal-values) of these types are also expressions.

- Function calls and window functions. For reference, see [Functions and operators overview](https://docs.pingcap.com/tidb/stable/functions-and-operators/functions-and-operators-overview) and [Window functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions)

- ParamMarker (`?`), system variables, user variables and CASE expressions.

The following rules are the expression syntax, which is based on the [`parser.y`](https://github.com/pingcap/tidb/blob/release-8.1/pkg/parser/parser.y) rules of TiDB parser.

```ebnf+diagram
Expression ::=
    ( singleAtIdentifier assignmentEq | 'NOT' | Expression ( logOr | 'XOR' | logAnd ) ) Expression
|   'MATCH' '(' ColumnNameList ')' 'AGAINST' '(' BitExpr FulltextSearchModifierOpt ')'
|   PredicateExpr ( IsOrNotOp 'NULL' | CompareOp ( ( singleAtIdentifier assignmentEq )? PredicateExpr | AnyOrAll SubSelect ) )* ( IsOrNotOp ( trueKwd | falseKwd | 'UNKNOWN' ) )?

PredicateExpr ::=
    BitExpr ( BetweenOrNotOp BitExpr 'AND' BitExpr )* ( InOrNotOp ( '(' ExpressionList ')' | SubSelect ) | LikeOrNotOp SimpleExpr LikeEscapeOpt | RegexpOrNotOp SimpleExpr )?

BitExpr ::=
    BitExpr ( ( '|' | '&' | '<<' | '>>' | '*' | '/' | '%' | 'DIV' | 'MOD' | '^' ) BitExpr | ( '+' | '-' ) ( BitExpr | "INTERVAL" Expression TimeUnit ) )
|   SimpleExpr

SimpleExpr ::=
    SimpleIdent ( ( '->' | '->>' ) stringLit )?
|   FunctionCallKeyword
|   FunctionCallNonKeyword
|   FunctionCallGeneric
|   SimpleExpr ( 'COLLATE' CollationName | pipes SimpleExpr )
|   WindowFuncCall
|   Literal
|   paramMarker
|   Variable
|   SumExpr
|   ( '!' | '~' | '-' | '+' | 'NOT' | 'BINARY' ) SimpleExpr
|   'EXISTS'? SubSelect
|   ( ( '(' ( ExpressionList ',' )? | 'ROW' '(' ExpressionList ',' ) Expression | builtinCast '(' Expression 'AS' CastType | ( 'DEFAULT' | 'VALUES' ) '(' SimpleIdent | 'CONVERT' '(' Expression ( ',' CastType | 'USING' CharsetName ) ) ')'
|   'CASE' ExpressionOpt WhenClause+ ElseOpt 'END'
```
