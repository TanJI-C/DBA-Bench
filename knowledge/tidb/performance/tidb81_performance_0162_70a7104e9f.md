# SPM overview and creating SQL bindings from statements

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-management.md`
- Source Title: `SQL Plan Management (SPM)`
- Source Heading Path: `SQL Plan Management (SPM) | SQL Plan Management (SPM) > SQL binding | SQL Plan Management (SPM) > SQL binding > Create a binding | SQL Plan Management (SPM) > SQL binding > Create a binding > Create a binding according to a SQL statement`
- Source Line Ranges: `5-114`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `sql-plan-management`, `sql-binding`, `plan-baselines`, `optimizer-hints`, `binding-scope`, `normalization`, `privileges`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0162_70a7104e9f`
- Source ID: `tidb-docs-8.1:sql-plan-management.md#sql-plan-management-spm`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b88d65435bba714a6118e511afe3f3522cbc746f1711ac40df82770703d23cdd`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-management#sql-plan-management-spm
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-management.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about what SQL Plan Management SQL bindings do, how to create GLOBAL or SESSION bindings from SQL statements, or how bound plans interact with optimizer hints and normalized SQL matching.
- Retrieval Keywords: SQL Plan Management (SPM), SQL binding, CREATE [GLOBAL | SESSION] BINDING, CREATE GLOBAL BINDING USING, CREATE GLOBAL BINDING FOR SELECT * FROM orders USING SELECT /*+ use_index(orders, orders_book_id_idx) */ * FROM orders, BindableStmt, SELECT, DELETE, UPDATE, INSERT / REPLACE with SELECT subqueries, optimizer hints, bindings have higher priority over manually added hints, SUPER privilege, tidb_use_plan_baselines, normalization, normalized statement, system table, Cartesian product JOIN without USING, DELETE statements that contain the USING keyword, use_index(@sel_1 pre_orders, idx_created)
- Follow-up Guidance: The source also explains syntax-conflict cases that cannot be bound directly, equivalent rewrites for those statements, and that for INSERT or REPLACE with SELECT subqueries the optimizer hint must be placed in the SELECT subquery.
- Classification Note: This is classified as performance for TiDB because the official content describes SQL bindings, plan baselines, and optimizer-hint-based manual interference with SQL execution plans.

## Official Source Content

# SQL Plan Management (SPM)

SQL Plan Management is a set of functions that execute SQL bindings to manually interfere with SQL execution plans. These functions include SQL binding, baseline capturing, and baseline evolution.
## SQL binding

An SQL binding is the basis of SPM. The [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints) document introduces how to select a specific execution plan using hints. However, sometimes you need to interfere with execution selection without modifying SQL statements. With SQL bindings, you can select a specified execution plan without modifying SQL statements.

> **Note:**
>
> To use SQL bindings, you need to have the `SUPER` privilege. If TiDB prompts that you do not have sufficient privileges, see [Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management) to add the required privileges.

> **Note:**
>
> To use SQL bindings, you need to have the `SUPER` privilege. If TiDB prompts that you do not have sufficient privileges, see [Privilege Management](https://docs.pingcap.com/tidb/stable/privilege-management) to add the required privileges.
### Create a binding

You can create a binding for a SQL statement according to a SQL statement or a historical execution plan.
#### Create a binding according to a SQL statement

```sql
CREATE [GLOBAL | SESSION] BINDING [FOR BindableStmt] USING BindableStmt;
```

This statement binds SQL execution plans at the GLOBAL or SESSION level. Currently, supported bindable SQL statements (BindableStmt) in TiDB include `SELECT`, `DELETE`, `UPDATE`, and `INSERT` / `REPLACE` with `SELECT` subqueries. The following is an example:

```sql
CREATE GLOBAL BINDING USING SELECT /*+ use_index(orders, orders_book_id_idx) */ * FROM orders;
CREATE GLOBAL BINDING FOR SELECT * FROM orders USING SELECT /*+ use_index(orders, orders_book_id_idx) */ * FROM orders;
```

> **Note:**
>
> Bindings have higher priority over manually added hints. Therefore, when you execute a statement containing a hint while a corresponding binding is present, the hint controlling the behavior of the optimizer does not take effect. However, other types of hints are still effective.

Specifically, two types of these statements cannot be bound to execution plans due to syntax conflicts. A syntax error will be reported during binding creation. See the following examples:

```sql
-- Type one: Statements that get the Cartesian product by using the `JOIN` keyword and not specifying the associated columns with the `USING` keyword.
CREATE GLOBAL BINDING for
    SELECT * FROM orders o1 JOIN orders o2
USING
    SELECT * FROM orders o1 JOIN orders o2;

-- Type two: `DELETE` statements that contain the `USING` keyword.
CREATE GLOBAL BINDING for
    DELETE FROM users USING users JOIN orders ON users.id = orders.user_id
USING
    DELETE FROM users USING users JOIN orders ON users.id = orders.user_id;
```

You can bypass syntax conflicts by using equivalent statements. For example, you can rewrite the above statements in the following ways:

```sql
-- Rewrite of type one statements: Delete the `JOIN` keyword. Replace it with a comma.
CREATE GLOBAL BINDING for
    SELECT * FROM orders o1, orders o2
USING
    SELECT * FROM orders o1, orders o2;

-- Rewrite of type two statements: Remove the `USING` keyword from the `DELETE` statement.
CREATE GLOBAL BINDING for
    DELETE users FROM users JOIN orders ON users.id = orders.user_id
USING
    DELETE users FROM users JOIN orders ON users.id = orders.user_id;
```

> **Note:**
>
> When creating execution plan bindings for `INSERT` / `REPLACE` statements with `SELECT` subqueries, you need to specify the optimizer hints you want to bind in the `SELECT` subquery, not after the `INSERT` / `REPLACE` keyword. Otherwise, the optimizer hints do not take effect as intended.

Here are two examples:

```sql
-- The hint takes effect in the following statement.
CREATE GLOBAL BINDING for
    INSERT INTO orders SELECT * FROM pre_orders WHERE status = 'VALID' AND created <= (NOW() - INTERVAL 1 HOUR)
USING
    INSERT INTO orders SELECT /*+ use_index(@sel_1 pre_orders, idx_created) */ * FROM pre_orders WHERE status = 'VALID' AND created <= (NOW() - INTERVAL 1 HOUR);

-- The hint cannot take effect in the following statement.
CREATE GLOBAL BINDING for
    INSERT INTO orders SELECT * FROM pre_orders WHERE status = 'VALID' AND created <= (NOW() - INTERVAL 1 HOUR)
USING
    INSERT /*+ use_index(@sel_1 pre_orders, idx_created) */ INTO orders SELECT * FROM pre_orders WHERE status = 'VALID' AND created <= (NOW() - INTERVAL 1 HOUR);
```

If you do not specify the scope when creating an execution plan binding, the default scope is SESSION. The TiDB optimizer normalizes bound SQL statements and stores them in the system table. When processing SQL queries, if a normalized statement matches one of the bound SQL statements in the system table and the system variable `tidb_use_plan_baselines` is set to `on` (the default value is `on`), TiDB then uses the corresponding optimizer hint for this statement. If there are multiple matchable execution plans, the optimizer chooses the least costly one to bind.

`Normalization` is a process that converts a constant in an SQL statement to a variable parameter and explicitly specifies the database for tables referenced in the query, with standardized processing on the spaces and line breaks in the SQL statement. See the following example:

```sql
SELECT * FROM users WHERE balance >    100
-- After normalization, the above statement is as follows:
SELECT * FROM bookshop . users WHERE balance > ?
```
