# Assignment operators and MySQL compatibility note

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/operators.md`
- Source Title: `Operators`
- Source Heading Path: `Operators > Assignment operators | Operators > MySQL compatibility`
- Source Line Ranges: `132-143`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `assignment-operators`, `set-statement`, `update-statement`, `mysql-compatibility`, `ilike`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0331_f086636b9d`
- Source ID: `tidb-docs-8.1:functions-and-operators/operators.md#assignment-operators`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e9f348282c748819f75102b15b1d95a511e7dd687158a35f0cdb50b61e119aa6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/operators#assignment-operators
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/operators.md

## Retrieval Guidance

- Use When: Use this chunk when looking for assignment operator syntax in SQL statements or for the MySQL compatibility note about the ILIKE operator.
- Retrieval Keywords: assignment operators, =, operator_assign-equal, :=, operator_assign-value, SET statement, SET clause in an UPDATE statement, UPDATE statement, MySQL compatibility, ILIKE operator, MySQL does not support the ILIKE operator, Detection of Functional Dependence
- Follow-up Guidance: The source also points to Detection of Functional Dependence for details.
- Classification Note: This is reference content because it lists the assignment operators = and :=, describes their use in SET and UPDATE contexts, and notes that MySQL does not support the ILIKE operator.

## Official Source Content

## Assignment operators

| Name | Description |
| ---------------------------------------- | ---------------------------------------- |
| [=](https://dev.mysql.com/doc/refman/8.0/en/assignment-operators.html#operator_assign-equal) | Assign a value (as part of a [`SET`](https://dev.mysql.com/doc/refman/8.0/en/set-variable.html) statement, or as part of the `SET` clause in an [`UPDATE`](https://dev.mysql.com/doc/refman/8.0/en/update.html) statement) |
| [:=](https://dev.mysql.com/doc/refman/8.0/en/assignment-operators.html#operator_assign-value) | Assign a value |

For details, see [Detection of Functional Dependence](https://dev.mysql.com/doc/refman/8.0/en/group-by-functional-dependence.html).
## MySQL compatibility

* MySQL does not support the `ILIKE` operator.
