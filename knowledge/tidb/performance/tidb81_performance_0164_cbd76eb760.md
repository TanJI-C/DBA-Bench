# Cross-database SQL bindings creation, verification, and removal

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-management.md`
- Source Title: `SQL Plan Management (SPM)`
- Source Heading Path: `SQL Plan Management (SPM) > Cross-database binding`
- Source Line Ranges: `526-640`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `sql-binding`, `cross-database-binding`, `fuzzy-binding`, `plan-stability`, `binding-priority`, `show-global-bindings`, `sql-digest`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0164_cbd76eb760`
- Source ID: `tidb-docs-8.1:sql-plan-management.md#cross-database-binding`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d301e0e5fc6e189cc52ffadd3af3b53af1262f459836b62ceddd71ca106a51cb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-management#cross-database-binding
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-management.md

## Retrieval Guidance

- Use When: Use this chunk when searching for how TiDB creates, verifies, prioritizes, shows, or removes cross-database SQL bindings that use `*` as the database name.
- Retrieval Keywords: cross-database binding, fuzzy binding, tidb_opt_enable_fuzzy_binding, CREATE GLOBAL BINDING USING, SHOW GLOBAL BINDINGS, DROP GLOBAL BINDING FOR SQL DIGEST, @@LAST_PLAN_FROM_BINDING, Default_db, Original_sql, Bind_sql, Sql_digest, SESSION scope standard bindings > SESSION scope cross-database bindings > GLOBAL scope standard bindings > GLOBAL scope cross-database bindings, select * from *.t, use_index
- Follow-up Guidance: The source also shows that `SHOW GLOBAL BINDINGS` displays cross-database bindings with an empty `Default_db` and `*` in `Original_sql` and `Bind_sql`, and that `@@LAST_PLAN_FROM_BINDING` can be checked after queries.
- Classification Note: This is classified as performance for the SQL component because the content describes SQL Plan Management bindings used to fix execution plans and mitigate SQL performance issues across databases.

## Official Source Content

## Cross-database binding

Starting from v7.6.0, you can create cross-database bindings in TiDB by using the wildcard `*` to represent a database name in the binding creation syntax. Before creating cross-database bindings, you need to first enable the [`tidb_opt_enable_fuzzy_binding`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_fuzzy_binding-new-in-v760) system variable.

You can use cross-database bindings to simplify the process of fixing execution plans in scenarios where data is categorized and stored across different databases, and each database maintains identical object definitions and executes similar application logic. The following are some common use cases:

* When you run SaaS or PaaS services on TiDB, where the data of each tenant is stored in separate databases for easier data maintenance and management
* When you performed database sharding in a single instance and retained the original database schema after migrating to TiDB, that is, the data in the original instance is categorized and stored by database

In these scenarios, cross-database binding can effectively mitigate SQL performance issues caused by uneven distribution and rapid changes in user data and workload. SaaS providers can use cross-database bindings to fix execution plans validated by applications with large data volumes, thereby avoiding potential performance issues due to the rapid growth of applications with small data volumes.

To create a cross-database binding, you only need to use `*` to represent the database name when creating a binding. For example:

```sql
CREATE GLOBAL BINDING USING SELECT /*+ use_index(t, idx_a) */ * FROM t; -- Create a GLOBAL scope standard binding.
CREATE GLOBAL BINDING USING SELECT /*+ use_index(t, idx_a) */ * FROM *.t; -- Create a GLOBAL scope cross-database binding.
SHOW GLOBAL BINDINGS;
```

The output is as follows:

```sql
+----------------------------+---------------------------------------------------+------------+---------+-------------------------+-------------------------+---------+-----------------+--------+------------------------------------------------------------------+-------------+
| Original_sql               | Bind_sql                                          | Default_db | Status  | Create_time             | Update_time             | Charset | Collation       | Source | Sql_digest                                                       | Plan_digest |
+----------------------------+---------------------------------------------------+------------+---------+-------------------------+-------------------------+---------+-----------------+--------+------------------------------------------------------------------+-------------+
| select * from `test` . `t` | SELECT /*+ use_index(`t` `idx_a`)*/ * FROM `test`.`t` | test       | enabled | 2023-12-29 14:19:01.332 | 2023-12-29 14:19:01.332 | utf8    | utf8_general_ci | manual | 8b193b00413fdb910d39073e0d494c96ebf24d1e30b131ecdd553883d0e29b42 |             |
| select * from `*` . `t`    | SELECT /*+ use_index(`t` `idx_a`)*/ * FROM `*`.`t`    |            | enabled | 2023-12-29 14:19:02.232 | 2023-12-29 14:19:02.232 | utf8    | utf8_general_ci | manual | 8b193b00413fdb910d39073e0d494c96ebf24d1e30b131ecdd553883d0e29b42 |             |
+----------------------------+---------------------------------------------------+------------+---------+-------------------------+-------------------------+---------+-----------------+--------+------------------------------------------------------------------+-------------+
```

In the `SHOW GLOBAL BINDINGS` output, the `Default_db` field value of a cross-database binding is empty, and the database name in the `Original_sql` and `Bind_sql` fields is represented as `*`. This binding applies to `select * from t` queries in all databases, not just in a specific database.

For the same query, both cross-database and standard bindings can coexist. TiDB matches bindings in the following order: SESSION scope standard bindings > SESSION scope cross-database bindings > GLOBAL scope standard bindings > GLOBAL scope cross-database bindings.

Apart from the creation syntax, cross-database bindings share the same deletion and status change syntax as standard bindings. The following is a detailed usage example.

1. Create databases `db1` and `db2`, and create two tables in each database:

    ```sql
    CREATE DATABASE db1;
    CREATE TABLE db1.t1 (a INT, KEY(a));
    CREATE TABLE db1.t2 (a INT, KEY(a));
    CREATE DATABASE db2;
    CREATE TABLE db2.t1 (a INT, KEY(a));
    CREATE TABLE db2.t2 (a INT, KEY(a));
    ```

2. Enable the cross-database binding feature:

    ```sql
    SET tidb_opt_enable_fuzzy_binding=1;
    ```

3. Create a cross-database binding:

    ```sql
    CREATE GLOBAL BINDING USING SELECT /*+ use_index(t1, idx_a), use_index(t2, idx_a) */ * FROM *.t1, *.t2;
    ```

4. Execute queries and verify whether the binding is used:

    ```sql
    SELECT * FROM db1.t1, db1.t2;
    SELECT @@LAST_PLAN_FROM_BINDING;
    +--------------------------+
    | @@LAST_PLAN_FROM_BINDING |
    +--------------------------+
    |                        1 |
    +--------------------------+
    
    SELECT * FROM db2.t1, db2.t2;
    SELECT @@LAST_PLAN_FROM_BINDING;
    +--------------------------+
    | @@LAST_PLAN_FROM_BINDING |
    +--------------------------+
    |                        1 |
    +--------------------------+
    
    SELECT * FROM db1.t1, db2.t2;
    SELECT @@LAST_PLAN_FROM_BINDING;
    +--------------------------+
    | @@LAST_PLAN_FROM_BINDING |
    +--------------------------+
    |                        1 |
    +--------------------------+

    USE db1;
    SELECT * FROM t1, db2.t2;
    SELECT @@LAST_PLAN_FROM_BINDING;
    +--------------------------+
    | @@LAST_PLAN_FROM_BINDING |
    +--------------------------+
    |                        1 |
    +--------------------------+
    ```

5. View the binding:
    ```sql
    SHOW GLOBAL BINDINGS;
    +----------------------------------------------+------------------------------------------------------------------------------------------+------------+---------+-------------------------+-------------------------+---------+--------------------+--------+------------------------------------------------------------------+-------------+
    | Original_sql                                 | Bind_sql                                                                                 | Default_db | Status  | Create_time             | Update_time             | Charset | Collation          | Source | Sql_digest                                                       | Plan_digest |
    +----------------------------------------------+------------------------------------------------------------------------------------------+------------+---------+-------------------------+-------------------------+---------+--------------------+--------+------------------------------------------------------------------+-------------+
    | select * from ( `*` . `t1` ) join `*` . `t2` | SELECT /*+ use_index(`t1` `idx_a`) use_index(`t2` `idx_a`)*/ * FROM (`*` . `t1`) JOIN `*` . `t2` |            | enabled | 2023-12-29 14:22:28.144 | 2023-12-29 14:22:28.144 | utf8    | utf8_general_ci    | manual | ea8720583e80644b58877663eafb3579700e5f918a748be222c5b741a696daf4 |             |
    +----------------------------------------------+------------------------------------------------------------------------------------------+------------+---------+-------------------------+-------------------------+---------+--------------------+--------+------------------------------------------------------------------+-------------+
    ```

6. Delete the cross-database binding:

    ```sql
    DROP GLOBAL BINDING FOR SQL DIGEST 'ea8720583e80644b58877663eafb3579700e5f918a748be222c5b741a696daf4';
    SHOW GLOBAL BINDINGS;
    Empty set (0.00 sec)
    ```
