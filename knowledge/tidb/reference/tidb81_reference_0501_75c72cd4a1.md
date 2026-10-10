# Create bindings for normalized IN predicates and upgraded binding forms

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-management.md`
- Source Title: `SQL Plan Management (SPM)`
- Source Heading Path: `SQL Plan Management (SPM) > SQL binding > Create a binding > Create a binding according to a SQL statement`
- Source Line Ranges: `115-173`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `sql-binding`, `create-binding`, `normalization`, `in-predicate`, `plan-binding`, `upgrade-behavior`, `show-bindings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0501_75c72cd4a1`
- Source ID: `tidb-docs-8.1:sql-plan-management.md#create-a-binding-according-to-a-sql-statement`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e1e2a103525f931b14c800a682676b31216bd5dc174e90880c7a6e6ec07a9d72`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-management#create-a-binding-according-to-a-sql-statement
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-management.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how SQL binding normalization treats IN predicates of different lengths and how existing bindings are shown after an upgrade.
- Retrieval Keywords: IN predicate normalization, ? normalized as ..., CREATE BINDING FOR SELECT * FROM t WHERE a IN (?), SELECT @@LAST_PLAN_FROM_BINDING, SHOW GLOBAL BINDINGS, Original_sql in ( ... ), bindings created earlier than v7.4.0, IN (?) modified to IN (...)
- Follow-up Guidance: The examples show checking binding usage with SELECT @@LAST_PLAN_FROM_BINDING and viewing upgraded binding text with SHOW GLOBAL BINDINGS.
- Classification Note: This is reference content because it documents exact normalization behavior, SQL examples, and the displayed binding form for IN predicates.

## Official Source Content

> **Note:**
>
> In the normalization process, `?` in the `IN` predicate is normalized as `...`.
>
> For example:
>
> ```sql
> SELECT * FROM books WHERE type IN ('Novel')
> SELECT * FROM books WHERE type IN ('Novel','Life','Education')
> -- After normalization, the above statements are as follows:
> SELECT * FROM bookshop . books WHERE type IN ( ... )
> SELECT * FROM bookshop . books WHERE type IN ( ... )
> ```
>
> After normalization, `IN` predicates of different lengths are recognized as the same statement, so you only need to create one binding that applies to all these predicates.
>
> For example:
>
> ```sql
> CREATE TABLE t (a INT, KEY(a));
> CREATE BINDING FOR SELECT * FROM t WHERE a IN (?) USING SELECT /*+ use_index(t, idx_a) */ * FROM t WHERE a in (?);
> 
> SELECT * FROM t WHERE a IN (1);
> SELECT @@LAST_PLAN_FROM_BINDING;
> +--------------------------+
> | @@LAST_PLAN_FROM_BINDING |
> +--------------------------+
> |                        1 |
> +--------------------------+
>
> SELECT * FROM t WHERE a IN (1, 2, 3);
> SELECT @@LAST_PLAN_FROM_BINDING;
> +--------------------------+
> | @@LAST_PLAN_FROM_BINDING |
> +--------------------------+
> |                        1 |
> +--------------------------+
> ```
>
> Bindings created in TiDB clusters earlier than v7.4.0 might contain `IN (?)`. After the upgrade to v7.4.0 or a later version, these bindings will be modified to `IN (...)`.
>
> For example:
>
> ```sql
> -- Create a binding on v7.3.0
> mysql> CREATE GLOBAL BINDING FOR SELECT * FROM t WHERE a IN (1) USING SELECT /*+ use_index(t, idx_a) */ * FROM t WHERE a IN (1);
> mysql> SHOW GLOBAL BINDINGS;
> +-----------------------------------------------+------------------------------------------------------------------------+------------+---------+-------------------------+-------------------------+---------+--------------------+--------+------------------------------------------------------------------+-------------+
> | Original_sql                                  | Bind_sql                                                               | Default_db | Status  | Create_time             | Update_time             | Charset | Collation          | Source | Sql_digest                                                       | Plan_digest |
> +-----------------------------------------------+------------------------------------------------------------------------+------------+---------+-------------------------+-------------------------+---------+--------------------+--------+------------------------------------------------------------------+-------------+
> | select * from `test` . `t` where `a` in ( ? ) | SELECT /*+ use_index(`t` `idx_a`)*/ * FROM `test`.`t` WHERE `a` IN (1) | test       | enabled | 2024-09-03 15:39:02.695 | 2024-09-03 15:39:02.695 | utf8mb4 | utf8mb4_general_ci | manual | 8b9c4e6ab8fad5ba29b034311dcbfc8a8ce57dde2e2d5d5b65313b90ebcdebf7 |             |
> +-----------------------------------------------+------------------------------------------------------------------------+------------+---------+-------------------------+-------------------------+---------+--------------------+--------+------------------------------------------------------------------+-------------+
>
> -- After the upgrade to v7.4.0 or a later version
> mysql> SHOW GLOBAL BINDINGS;
> +-------------------------------------------------+------------------------------------------------------------------------+------------+---------+-------------------------+-------------------------+---------+--------------------+--------+------------------------------------------------------------------+-------------+
> | Original_sql                                    | Bind_sql                                                               | Default_db | Status  | Create_time             | Update_time             | Charset | Collation          | Source | Sql_digest                                                       | Plan_digest |
> +-------------------------------------------------+------------------------------------------------------------------------+------------+---------+-------------------------+-------------------------+---------+--------------------+--------+------------------------------------------------------------------+-------------+
> | select * from `test` . `t` where `a` in ( ... ) | SELECT /*+ use_index(`t` `idx_a`)*/ * FROM `test`.`t` WHERE `a` IN (1) | test       | enabled | 2024-09-03 15:35:59.861 | 2024-09-03 15:35:59.861 | utf8mb4 | utf8mb4_general_ci | manual | da38bf216db4a53e1a1e01c79ffa42306419442ad7238480bb7ac510723c8bdf |             |
