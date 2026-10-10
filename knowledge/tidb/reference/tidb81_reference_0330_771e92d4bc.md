# Comparison functions and logical operators

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/operators.md`
- Source Title: `Operators`
- Source Heading Path: `Operators > Comparison functions and operators | Operators > Logical operators`
- Source Line Ranges: `90-131`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `comparison-functions`, `comparison-operators`, `logical-operators`, `pattern-matching`, `null-tests`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0330_771e92d4bc`
- Source ID: `tidb-docs-8.1:functions-and-operators/operators.md#comparison-functions-and-operators`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b1d9038ae50634e707d91f97d7dfa5cecf04c7544f884f6fa3cef6adccf209cb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/operators#comparison-functions-and-operators
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/operators.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for comparison functions, comparison operators, pattern matching operators, NULL tests, or logical operators in TiDB SQL.
- Retrieval Keywords: Comparison functions and operators, Logical operators, BETWEEN ... AND ..., COALESCE(), <=>, IN(), NOT IN(), IS NULL, IS NOT NULL, ISNULL(), LIKE, ILIKE, NOT LIKE, STRCMP(), AND, &&, NOT, !, ||, OR, XOR
- Follow-up Guidance: It includes links for details on comparison operators and logical operators.
- Classification Note: This is reference content because it is a catalog of comparison functions and logical operators with their exact names and short descriptions.

## Official Source Content

## Comparison functions and operators

| Name | Description |
| ---------------------------------------- | ---------------------------------------- |
| [BETWEEN ... AND ...](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_between) | Check whether a value is within a range of values |
| [COALESCE()](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#function_coalesce) | Return the first non-NULL argument |
| [=](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_equal) | Equal operator |
| [`<=>`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_equal-to) | NULL-safe equal to operator |
| [>](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_greater-than) | Greater than operator |
| [>=](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_greater-than-or-equal) | Greater than or equal operator |
| [GREATEST()](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#function_greatest) | Return the largest argument |
| [IN()](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_in) | Check whether a value is within a set of values |
| [INTERVAL()](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#function_interval) | Return the index of the argument that is less than the first argument |
| [IS](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_is) | Test a value against a boolean |
| [IS NOT](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_is-not) | Test a value against a boolean |
| [IS NOT NULL](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_is-not-null) | NOT NULL value test |
| [IS NULL](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_is-null) | NULL value test |
| [ISNULL()](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#function_isnull) | Test whether the argument is NULL |
| [LEAST()](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#function_least) | Return the smallest argument |
| [<](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_less-than) | Less than operator |
| [<=](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_less-than-or-equal) | Less than or equal operator |
| [LIKE](https://dev.mysql.com/doc/refman/8.0/en/string-comparison-functions.html#operator_like) | Simple pattern matching |
| [ILIKE](https://www.postgresql.org/docs/current/functions-matching.html) | Simple pattern matching with case insensitive (Supported in TiDB, but not supported in MySQL) |
| [NOT BETWEEN ... AND ...](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_not-between) | Check whether a value is not within a range of values |
| [!=, `<>`](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_not-equal) | Not equal operator |
| [NOT IN()](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html#operator_not-in) | Check whether a value is not within a set of values |
| [NOT LIKE](https://dev.mysql.com/doc/refman/8.0/en/string-comparison-functions.html#operator_not-like) | Negation of simple pattern matching |
| [STRCMP()](https://dev.mysql.com/doc/refman/8.0/en/string-comparison-functions.html#function_strcmp) | Compare two strings |

For details, see [Comparison Functions and Operators](https://dev.mysql.com/doc/refman/8.0/en/comparison-operators.html).
## Logical operators

| Name | Description |
| ---------------------------------------- | ------------- |
| [AND, &&](https://dev.mysql.com/doc/refman/8.0/en/logical-operators.html#operator_and) | Logical AND |
| [NOT, !](https://dev.mysql.com/doc/refman/8.0/en/logical-operators.html#operator_not) | Negates value |
| [\|\|, OR](https://dev.mysql.com/doc/refman/8.0/en/logical-operators.html#operator_or) | Logical OR |
| [XOR](https://dev.mysql.com/doc/refman/8.0/en/logical-operators.html#operator_xor) | Logical XOR |

For details, see [MySQL Handling of GROUP BY](https://dev.mysql.com/doc/refman/8.0/en/group-by-handling.html).
