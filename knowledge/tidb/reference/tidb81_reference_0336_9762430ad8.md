# SQL set operations: UNION, EXCEPT, INTERSECT, precedence, and ordering

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/set-operators.md`
- Source Title: `Set Operations`
- Source Heading Path: `Set Operations | Set Operations > UNION operator | Set Operations > EXCEPT operator | Set Operations > INTERSECT operator | Set Operations > Parentheses | Set Operations > Use `ORDER BY` and `LIMIT``
- Source Line Ranges: `5-130`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `set-operations`, `union`, `except`, `intersect`, `precedence`, `parentheses`, `order-by`, `limit`, `select`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0336_9762430ad8`
- Source ID: `tidb-docs-8.1:functions-and-operators/set-operators.md#set-operations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `182e0b3fe2f9d94a564750ad527eb06f088b18b87b231f7530821652c7c13bba`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/set-operators#set-operations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/set-operators.md

## Retrieval Guidance

- Use When: Use this when looking for TiDB SQL set operation behavior for `UNION`, `EXCEPT`, and `INTERSECT`, including duplicate handling, operator precedence, parentheses, and placement of `ORDER BY` or `LIMIT`.
- Retrieval Keywords: UNION, UNION DISTINCT, UNION ALL, EXCEPT, INTERSECT, EXCEPT ALL not yet supported, INTERSECT ALL not yet supported, INTERSECT higher precedence over EXCEPT and UNION, parentheses set operations, ORDER BY at end of entire statement, LIMIT at end of entire statement, SELECT statement smallest unit of a set, SELECT * FROM t1 UNION DISTINCT SELECT * FROM t2, SELECT * FROM t1 UNION ALL SELECT * FROM t2, SELECT * FROM t1 EXCEPT SELECT * FROM t2, SELECT * FROM t1 INTERSECT SELECT * FROM t2
- Follow-up Guidance: The source also shows example queries demonstrating how parentheses change precedence and how `ORDER BY a LIMIT 2` applies to the entire set-operation result.
- Classification Note: This is reference content because it defines SQL set operators and documents their supported syntax, defaults, precedence, and clause placement in TiDB.

## Official Source Content

# Set Operations

TiDB supports three set operations using the UNION, EXCEPT, and INTERSECT operators. The smallest unit of a set is a [`SELECT` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select).
## UNION operator

In mathematics, the union of two sets A and B consists of all elements that are in A or in B. For example:

```sql
SELECT 1 UNION SELECT 2;
+---+
| 1 |
+---+
| 2 |
| 1 |
+---+
2 rows in set (0.00 sec)
```

TiDB supports both `UNION DISTINCT` and `UNION ALL` operators. `UNION DISTINCT` removes duplicate records from the result set, while `UNION ALL` keeps all records including duplicates. `UNION DISTINCT` is used by default in TiDB.

```sql
CREATE TABLE t1 (a int);
CREATE TABLE t2 (a int);
INSERT INTO t1 VALUES (1),(2);
INSERT INTO t2 VALUES (1),(3);
```

Examples for `UNION DISTINCT` and `UNION ALL` queries are respectively as follows:

```sql
SELECT * FROM t1 UNION DISTINCT SELECT * FROM t2;
+---+
| a |
+---+
| 1 |
| 2 |
| 3 |
+---+
3 rows in set (0.00 sec)

SELECT * FROM t1 UNION ALL SELECT * FROM t2;
+---+
| a |
+---+
| 1 |
| 2 |
| 1 |
| 3 |
+---+
4 rows in set (0.00 sec)
```
## EXCEPT operator

If A and B are two sets, EXCEPT returns the difference set of A and B which consists of elements that are in A but not in B.

```sql
SELECT * FROM t1 EXCEPT SELECT * FROM t2;
+---+
| a |
+---+
| 2 |
+---+
1 rows in set (0.00 sec)
```

`EXCEPT ALL` operator is not yet supported.
## INTERSECT operator

In mathematics, the intersection of two sets A and B consists of all elements that are both in A and B, and no other elements.

```sql
SELECT * FROM t1 INTERSECT SELECT * FROM t2;
+---+
| a |
+---+
| 1 |
+---+
1 rows in set (0.00 sec)
```

`INTERSECT ALL` operator is not yet supported. INTERSECT operator has higher precedence over EXCEPT and UNION operators.

```sql
SELECT * FROM t1 UNION ALL SELECT * FROM t1 INTERSECT SELECT * FROM t2;
+---+
| a |
+---+
| 1 |
| 1 |
| 2 |
+---+
3 rows in set (0.00 sec)
```
## Parentheses

TiDB supports using parentheses to specify the precedence of set operations. Expressions in parentheses are processed first.

```sql
(SELECT * FROM t1 UNION ALL SELECT * FROM t1) INTERSECT SELECT * FROM t2;
+---+
| a |
+---+
| 1 |
+---+
1 rows in set (0.00 sec)
```
## Use `ORDER BY` and `LIMIT`

TiDB supports using `ORDER BY` or `LIMIT` clause on the entire result of set operations. These two clauses must be at the end of the entire statement.

```sql
(SELECT * FROM t1 UNION ALL SELECT * FROM t1 INTERSECT SELECT * FROM t2) ORDER BY a LIMIT 2;
+---+
| a |
+---+
| 1 |
| 1 |
+---+
2 rows in set (0.00 sec)
```
