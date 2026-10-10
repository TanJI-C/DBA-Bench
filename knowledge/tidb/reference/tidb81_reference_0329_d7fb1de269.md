# Operators overview, unsupported operators, and precedence

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/operators.md`
- Source Title: `Operators`
- Source Heading Path: `Operators | Operators > Unsupported operators | Operators > Operator precedence`
- Source Line Ranges: `5-89`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `operators`, `operator-precedence`, `unsupported-operators`, `comparison`, `logical-operators`, `assignment-operators`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0329_d7fb1de269`
- Source ID: `tidb-docs-8.1:functions-and-operators/operators.md#operators`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `41456f8f398f2db6d411fa1590f707dcd75fd4ca58e41c7c64cd922d13186db9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/operators#operators
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/operators.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for the SQL operator list, unsupported operators, or operator precedence in TiDB.
- Retrieval Keywords: Operators, Unsupported operators, Operator precedence, SOUNDS LIKE, ILIKE, <=>, ->, ->>, AND, &&, ||, OR, = (assignment), :=, INTERVAL, BINARY, COLLATE, BETWEEN, CASE, WHEN, THEN, ELSE
- Follow-up Guidance: It also points to the comparison functions and operators, logical operators, and assignment operators sections for more detailed operator categories.
- Classification Note: This is reference content because it enumerates supported operators, names one unsupported operator, and lists the precedence order from highest to lowest.

## Official Source Content

# Operators

This document describes the operators precedence, comparison functions and operators, logical operators, and assignment operators.

- [Operator precedence](#operator-precedence)
- [Comparison functions and operators](#comparison-functions-and-operators)
- [Logical operators](#logical-operators)
- [Assignment operators](#assignment-operators)

| Name | Description |
| ---------------------------------------- | ---------------------------------------- |
| [AND, &&](https://dev.mysql.com/doc/refman/8.0/en/logical-operators.html#operator_and) | Logical AND |
| [=](https://dev.mysql.com/doc/refman/8.0/en/assignment-operators.html#operator_assign-equal) | Assign a value (as part of a [`SET`](https://dev.mysql.com/doc/refman/8.0/en/set-variable.html) statement, or as part of the `SET` clause in an [`UPDATE`](https://dev.mysql.com/doc/refman/8.0/en/update.html) statement) |
| [:=](https://dev.mysql.com/doc/refman/8.0/en/assignment-operators.html#operator_assign-value) | Assign a value |
| [BETWEEN ... AND ...](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_between) | Check whether a value is within a range of values |
| [BINARY](https://dev.mysql.com/doc/refman/8.0/en/cast-functions.html#operator_binary) | Cast a string to a binary string |
| [&](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_bitwise-and) | Bitwise AND |
| [~](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_bitwise-invert) | Bitwise inversion |
| [\|](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_bitwise-or) | Bitwise OR |
| [^](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_bitwise-xor) | Bitwise XOR |
| [CASE](https://dev.mysql.com/doc/refman/8.0/en/flow-control-functions.html#operator_case) | Case operator |
| [DIV](https://dev.mysql.com/doc/refman/8.0/en/arithmetic-functions.html#operator_div) | Integer division |
| [/](https://dev.mysql.com/doc/refman/8.0/en/arithmetic-functions.html#operator_divide) | Division operator |
| [=](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_equal) | Equal operator |
| [`<=>`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_equal-to) | NULL-safe equal to operator |
| [>](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_greater-than) | Greater than operator |
| [>=](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_greater-than-or-equal) | Greater than or equal operator |
| [IS](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_is) | Test a value against a boolean |
| [IS NOT](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_is-not) | Test a value against a boolean |
| [IS NOT NULL](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_is-not-null) | NOT NULL value test |
| [IS NULL](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_is-null) | NULL value test |
| [->](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#operator_json-column-path) | Return value from JSON column after evaluating path; equivalent to `JSON_EXTRACT()` |
| [->>](https://dev.mysql.com/doc/refman/8.0/en/json-search-functions.html#operator_json-inline-path) | Return value from JSON column after evaluating path and unquoting the result; equivalent to `JSON_UNQUOTE(JSON_EXTRACT())` |
| [<<](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_left-shift) | Left shift |
| [<](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_less-than) | Less than operator |
| [<=](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_less-than-or-equal) | Less than or equal operator |
| [LIKE](https://dev.mysql.com/doc/refman/8.0/en/string-comparison-functions.html#operator_like) | Simple pattern matching |
| [ILIKE](https://www.postgresql.org/docs/current/functions-matching.html) | Simple pattern matching with case insensitive (Supported in TiDB, but not supported in MySQL) |
| [-](https://dev.mysql.com/doc/refman/8.0/en/arithmetic-functions.html#operator_minus) | Minus operator |
| [%, MOD](https://dev.mysql.com/doc/refman/8.0/en/arithmetic-functions.html#operator_mod) | Modulo operator |
| [NOT, !](https://dev.mysql.com/doc/refman/8.0/en/logical-operators.html#operator_not) | Negates value |
| [NOT BETWEEN ... AND ...](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_not-between) | Check whether a value is not within a range of values |
| [!=, `<>`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_not-equal) | Not equal operator |
| [NOT LIKE](https://dev.mysql.com/doc/refman/8.0/en/string-comparison-functions.html#operator_not-like) | Negation of simple pattern matching |
| [NOT REGEXP](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#operator_not-regexp) | Negation of REGEXP |
| [\|\|, OR](https://dev.mysql.com/doc/refman/8.0/en/logical-operators.html#operator_or) | Logical OR |
| [+](https://dev.mysql.com/doc/refman/8.0/en/arithmetic-functions.html#operator_plus) | Addition operator |
| [REGEXP](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#operator_regexp) | Pattern matching using regular expressions |
| [>>](https://dev.mysql.com/doc/refman/8.0/en/bit-functions.html#operator_right-shift) | Right shift |
| [RLIKE](https://dev.mysql.com/doc/refman/8.0/en/regexp.html#operator_regexp) | Synonym for REGEXP |
| [*](https://dev.mysql.com/doc/refman/8.0/en/arithmetic-functions.html#operator_times) | Multiplication operator |
| [-](https://dev.mysql.com/doc/refman/8.0/en/arithmetic-functions.html#operator_unary-minus) | Change the sign of the argument |
| [XOR](https://dev.mysql.com/doc/refman/8.0/en/logical-operators.html#operator_xor) | Logical XOR |
## Unsupported operators

* [`SOUNDS LIKE`](https://dev.mysql.com/doc/refman/8.0/en/string-functions.html#operator_sounds-like)
## Operator precedence

Operator precedences are shown in the following list, from highest precedence to the lowest. Operators that are shown together on a line have the same precedence.

```sql
INTERVAL
BINARY, COLLATE
!
- (unary minus), ~ (unary bit inversion)
^
*, /, DIV, %, MOD
-, +
<<, >>
&
|
= (comparison), <=>, >=, >, <=, <, <>, !=, IS, LIKE, REGEXP, IN
BETWEEN, CASE, WHEN, THEN, ELSE
NOT
AND, &&
XOR
OR, ||
= (assignment), :=
```

For details, see [Operator Precedence](https://dev.mysql.com/doc/refman/8.0/en/operator-precedence.html).
