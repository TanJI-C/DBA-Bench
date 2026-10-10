# Expression index behavior and multi-valued index overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-create-index.md`
- Source Title: `CREATE INDEX | TiDB SQL Statement Reference`
- Source Heading Path: `CREATE INDEX > Expression index | CREATE INDEX > Multi-valued indexes`
- Source Line Ranges: `104-257`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `create-index`, `expression-index`, `multi-valued-indexes`, `json-arrays`, `index-limitations`, `optimizer`, `show-index`, `generated-columns`, `system-variables`, `configuration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0553_6c4dc20a70`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-create-index.md#expression-index`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0cd380356997baa6f442f9a7371c5dbcf7eb4ccbb54ffc0423d1541a4044d02f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#expression-index
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-create-index.md

## Retrieval Guidance

- Use When: Use this chunk when the query is about CREATE INDEX support for expression indexes or the overview and retrieval concepts of multi-valued indexes on JSON arrays in TiDB SQL.
- Retrieval Keywords: CREATE INDEX expression index, ALTER TABLE ADD INDEX ((LOWER(col1))), LOWER(col1) expression index, expression in an expression index must be surrounded by ( ), DROP INDEX idx1 ON t1, tidb_allow_function_for_expression_index, allow-expression-index = true, expression index limitations, volatile functions RAND() NOW(), tidb_enable_auto_increment_in_generated, SHOW INDEX Expression column, information_schema.tidb_indexes, information_schema.STATISTICS, optimizer hints expression index, generated virtual columns invisible, limitations of virtual generated columns, multi-valued indexes, JSON arrays, secondary index defined on an array column, N:1 index records, zipcode array
- Follow-up Guidance: The source also points to SHOW INDEX, information_schema.tidb_indexes, and information_schema.STATISTICS to inspect the Expression column for expression indexes.
- Classification Note: This is reference content because it defines SQL syntax, allowed functions, limitations, optimizer applicability, metadata inspection points, and the conceptual overview of multi-valued indexes.

## Official Source Content

## Expression index

In some scenarios, the filtering condition of a query is based on a certain expression. In these scenarios, the query performance is relatively poor because ordinary indexes cannot take effect, the query can only be executed by scanning the entire table. The expression index is a type of special index that can be created on an expression. Once an expression index is created, TiDB can use the index for the expression-based query, which significantly improves the query performance.

For example, if you want to create an index based on `LOWER(col1)`, execute the following SQL statement:

```sql
CREATE INDEX idx1 ON t1 ((LOWER(col1)));
```

Or you can execute the following equivalent statement:

```sql
ALTER TABLE t1 ADD INDEX idx1((LOWER(col1)));
```

You can also specify the expression index when you create the table:

```sql
CREATE TABLE t1 (
    col1 CHAR(10), 
    col2 CHAR(10),
    INDEX ((LOWER(col1)))
);
```

> **Note:**
>
> The expression in an expression index must be surrounded by `(` and `)`. Otherwise, a syntax error is reported.

You can drop an expression index in the same way as dropping an ordinary index:

```sql
DROP INDEX idx1 ON t1;
```

Expression index involves various kinds of expressions. To ensure correctness, only some fully tested functions are allowed for creating an expression index. This means that only these functions are allowed in expressions in a production environment. You can get these functions by querying the [`tidb_allow_function_for_expression_index`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_allow_function_for_expression_index-new-in-v520) variable. Currently, the allowed functions are as follows:

- [`JSON_ARRAY()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_ARRAY_APPEND()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_ARRAY_INSERT()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_CONTAINS()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_CONTAINS_PATH()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_DEPTH()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_EXTRACT()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_INSERT()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_KEYS()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_LENGTH()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_MERGE_PATCH()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_MERGE_PRESERVE()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_OBJECT()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_PRETTY()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_QUOTE()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_REMOVE()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_REPLACE()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_SEARCH()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_SET()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_STORAGE_SIZE()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_TYPE()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_UNQUOTE()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`JSON_VALID()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions)
- [`LOWER()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#lower)
- [`MD5()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/encryption-and-compression-functions)
- [`REVERSE()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#reverse)
- [`TIDB_SHARD()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#tidb_shard)
- [`UPPER()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/string-functions#upper)
- [`VITESS_HASH()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions)

For the functions that are not included in the above list, those functions are not fully tested and not recommended for a production environment, which can be seen as experimental. Other expressions such as operators, `CAST`, and `CASE WHEN` are also seen as experimental and not recommended for production.

If you still want to use those expressions, you can make the following configuration in the [TiDB configuration file](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#allow-expression-index-new-in-v400):

```sql
allow-expression-index = true
```

> **Note:**
>
> An expression index cannot be created on a primary key.
>
> The expression in an expression index cannot contain the following content:
>
> - Volatile functions, such as `RAND()` and `NOW()`.
> - [System variables](https://docs.pingcap.com/tidb/stable/system-variables) and [user variables](https://docs.pingcap.com/tidb/stable/user-defined-variables).
> - Subqueries.
> - [`AUTO_INCREMENT`](https://docs.pingcap.com/tidb/stable/auto-increment) columns. You can remove this restriction by setting the value of [`tidb_enable_auto_increment_in_generated`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_auto_increment_in_generated) (system variable) to `true`.
> - [Window functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/window-functions).
> - ROW functions, such as `CREATE TABLE t (j JSON, INDEX k (((j,j))));`.
> - [Aggregate functions](https://docs.pingcap.com/tidb/stable/functions-and-operators/aggregate-group-by-functions).
>
> An expression index implicitly takes up a name (for example, `_V$_{index_name}_{index_offset}`). If you try to create a new expression index with the name that a column has already had, an error occurs. In addition, if you add a new column with the same name, an error also occurs.
>
> Make sure that the number of function parameters in the expression of an expression index is correct.
>
> When the expression of an index contains a string-related function, affected by the returned type and the length, creating the expression index might fail. In this situation, you can use the `CAST()` function to explicitly specify the returned type and the length. For example, to create an expression index based on the `REPEAT(a, 3)` expression, you need to modify this expression to `CAST(REPEAT(a, 3) AS CHAR(20))`.

When the expression in a query statement matches the expression in an expression index, the optimizer can choose the expression index for the query. In some cases, the optimizer might not choose an expression index depending on statistics. In this situation, you can force the optimizer to select an expression index by using optimizer hints.

In the following examples, suppose that you create the expression index `idx` on the expression `LOWER(col1)`:

If the results of the query statement are the same expressions, the expression index applies. Take the following statement as an example:

```sql
SELECT LOWER(col1) FROM t;
```

If the same expression is included in the filtering conditions, the expression index applies. Take the following statements as an example:

```sql
SELECT * FROM t WHERE LOWER(col1) = "a";
SELECT * FROM t WHERE LOWER(col1) > "a";
SELECT * FROM t WHERE LOWER(col1) BETWEEN "a" AND "b";
SELECT * FROM t WHERE LOWER(col1) IN ("a", "b");
SELECT * FROM t WHERE LOWER(col1) > "a" AND LOWER(col1) < "b";
SELECT * FROM t WHERE LOWER(col1) > "b" OR LOWER(col1) < "a";
```

When the queries are sorted by the same expression, the expression index applies. Take the following statement as an example:

```sql
SELECT * FROM t ORDER BY LOWER(col1);
```

If the same expression is included in the aggregate (`GROUP BY`) functions, the expression index applies. Take the following statements as an example:

```sql
SELECT MAX(LOWER(col1)) FROM t;
SELECT MIN(col1) FROM t GROUP BY LOWER(col1);
```
To see the expression corresponding to the expression index, execute [`SHOW INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-indexes), or check the system tables [`information_schema.tidb_indexes`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-tidb-indexes) and the table [`information_schema.STATISTICS`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-statistics). The `Expression` column in the output indicates the corresponded expression. For the non-expression indexes, the column shows `NULL`.

The cost of maintaining an expression index is higher than that of maintaining other indexes, because the value of the expression needs to be calculated whenever a row is inserted or updated. The value of the expression is already stored in the index, so this value does not require recalculation when the optimizer selects the expression index.

Therefore, when the query performance outweighs the insert and update performance, you can consider indexing the expressions.

Expression indexes have the same syntax and limitations as in MySQL. They are implemented by creating indexes on generated virtual columns that are invisible, so the supported expressions inherit all [limitations of virtual generated columns](https://docs.pingcap.com/tidb/stable/generated-columns#limitations).
## Multi-valued indexes

Multi-valued indexes are a kind of secondary index defined on an array column. In a normal index, one index record corresponds to one data record (1:1). In a multi-valued index, multiple index records correspond to one data record (N:1). Multi-valued indexes are used to index JSON arrays. For example, a multi-valued index defined on the `zipcode` field will generate one index record for each element in the `zipcode` array.

```json
{
    "user":"Bob",
    "user_id":31,
    "zipcode":[94477,94536]
}
```
