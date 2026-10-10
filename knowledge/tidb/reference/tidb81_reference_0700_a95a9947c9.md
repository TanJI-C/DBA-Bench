# WITH statement syntax, examples, and MySQL compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-with.md`
- Source Title: `WITH | TiDB SQL Statement Reference`
- Source Heading Path: `WITH | WITH > Synopsis | WITH > Examples | WITH > MySQL compatibility | WITH > See also`
- Source Line Ranges: `5-92`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `with`, `common-table-expression`, `cte`, `recursive-cte`, `syntax`, `examples`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0700_a95a9947c9`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-with.md#with`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2db94ed4b9f79cdfd215ea49b569ea3a36eb3875089ac948332419bb3f160cd2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-with#with
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-with.md

## Retrieval Guidance

- Use When: Use this when the question asks about TiDB SQL WITH syntax, Common Table Expressions, recursive CTE examples, or documented MySQL compatibility differences for WITH.
- Retrieval Keywords: WITH, WITH RECURSIVE, Common Table Expression, CTE, WithClause, WithList, CommonTableExpr, IdentListWithParenOpt, non-recursive CTE, recursive CTE, WITH cte AS (SELECT 1, 2) SELECT * FROM cte t1, cte t2, WITH RECURSIVE cte(a) AS (SELECT 1 UNION SELECT a+1 FROM cte WHERE a < 5) SELECT * FROM cte, strict mode, non-strict mode, seed part, UNION, UNION ALL, MySQL compatibility
- Follow-up Guidance: The source also points to related statements and guides including Developer Guide: Common Table Expression, SELECT, INSERT, DELETE, UPDATE, and REPLACE.
- Classification Note: This is reference content because it defines the WITH statement grammar, shows canonical SQL examples, and lists documented TiDB versus MySQL behavior differences.

## Official Source Content

# WITH

A Common Table Expression (CTE) is a temporary result set that can be referred multiple times within a SQL statement to improve the statement's readability and execution efficiency. You can apply the `WITH` statement to use Common Table Expressions.
## Synopsis

**WithClause:**

```ebnf+diagram
WithClause ::=
        "WITH" WithList
|       "WITH" "RECURSIVE" WithList
```

**WithList:**

```ebnf+diagram
WithList ::=
        WithList ',' CommonTableExpr
|       CommonTableExpr
```

**CommonTableExpr:**

```ebnf+diagram
CommonTableExpr ::=
        Identifier IdentListWithParenOpt "AS" SubSelect
```

**IdentListWithParenOpt:**

```ebnf+diagram
IdentListWithParenOpt ::=
( '(' IdentList ')' )?
```
## Examples

Non-recursive CTE:

```sql
WITH cte AS (SELECT 1, 2) SELECT * FROM cte t1, cte t2;
```

```
+---+---+---+---+
| 1 | 2 | 1 | 2 |
+---+---+---+---+
| 1 | 2 | 1 | 2 |
+---+---+---+---+
1 row in set (0.00 sec)
```

Recursive CTE:

```sql
WITH RECURSIVE cte(a) AS (SELECT 1 UNION SELECT a+1 FROM cte WHERE a < 5) SELECT * FROM cte;
```

```
+---+
| a |
+---+
| 1 |
| 2 |
| 3 |
| 4 |
| 5 |
+---+
5 rows in set (0.00 sec)
```
## MySQL compatibility

* In strict mode, when the data length recursively calculated exceeds the data length of the seed part, TiDB returns a warning while MySQL returns an error. In non-strict mode, the behavior of TiDB is consistent with that of MySQL.
* The data type for recursive CTE is determined by the seed part. The data type of the seed part is not completely consistent with MySQL in some cases (such as functions).
* In the case of multiple `UNION` / `UNION ALL` operators, MySQL does not allow `UNION` to be followed by `UNION ALL`, but TiDB does.
* If there is a problem with the definition of a CTE, TiDB will report an error, while MySQL will not if the CTE is not referred.
## See also

* [Developer Guide: Common Table Expression](https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-common-table-expression)
* [SELECT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select)
* [INSERT](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-insert)
* [DELETE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-delete)
* [UPDATE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-update)
* [REPLACE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-replace)
