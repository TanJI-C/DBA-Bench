# Binding scope precedence and create binding requirements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-management.md`
- Source Title: `SQL Plan Management (SPM)`
- Source Heading Path: `SQL Plan Management (SPM) > SQL binding > Create a binding > Create a binding according to a SQL statement`
- Source Line Ranges: `174-224`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `sql-binding`, `global-binding`, `session-binding`, `scope-precedence`, `normalization`, `hint-removal`, `database-context`, `prepare-execute`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0502_ff3978041b`
- Source ID: `tidb-docs-8.1:sql-plan-management.md#create-a-binding-according-to-a-sql-statement`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f11bd57bb5cde7d9e8854130b165c7f494104e0f9e33b455ff94693deba7d655`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-management#create-a-binding-according-to-a-sql-statement
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-management.md

## Retrieval Guidance

- Use When: Use this chunk when looking up binding scope precedence, CREATE BINDING constraints, or normalization requirements for original and bound SQL text.
- Retrieval Keywords: GLOBAL binding SESSION binding precedence, SESSION binding shields GLOBAL binding, CREATE GLOBAL BINDING, CREATE BINDING, merge_join(t1, t2), hash_join(t1, t2), same text after normalization and hint removal, database context use ${database}, PREPARE EXECUTE statements, binary protocols, last created binding is retained
- Follow-up Guidance: The content also states that session and global bindings can coexist, and that for PREPARE / EXECUTE or binary protocol queries, bindings must be created for the real query statements.
- Classification Note: This is reference content because it defines scope behavior, one-binding retention rules, database-context requirements, and exact success or failure conditions for binding creation.

## Official Source Content

> +-------------------------------------------------+------------------------------------------------------------------------+------------+---------+-------------------------+-------------------------+---------+--------------------+--------+------------------------------------------------------------------+-------------+
> ```

When a SQL statement has bound execution plans in both GLOBAL and SESSION scopes, because the optimizer ignores the bound execution plan in the GLOBAL scope when it encounters the SESSION binding, the bound execution plan of this statement in the SESSION scope shields the execution plan in the GLOBAL scope.

For example:

```sql
--  Creates a GLOBAL binding and specifies using `sort merge join` in this binding.
CREATE GLOBAL BINDING for
    SELECT * FROM t1, t2 WHERE t1.id = t2.id
USING
    SELECT /*+ merge_join(t1, t2) */ * FROM t1, t2 WHERE t1.id = t2.id;

-- The execution plan of this SQL statement uses the `sort merge join` specified in the GLOBAL binding.
explain SELECT * FROM t1, t2 WHERE t1.id = t2.id;

-- Creates another SESSION binding and specifies using `hash join` in this binding.
CREATE BINDING for
    SELECT * FROM t1, t2 WHERE t1.id = t2.id
USING
    SELECT /*+ hash_join(t1, t2) */ * FROM t1, t2 WHERE t1.id = t2.id;

-- In the execution plan of this statement, `hash join` specified in the SESSION binding is used, instead of `sort merge join` specified in the GLOBAL binding.
explain SELECT * FROM t1, t2 WHERE t1.id = t2.id;
```

When the first `SELECT` statement is being executed, the optimizer adds the `sm_join(t1, t2)` hint to the statement through the binding in the GLOBAL scope. The top node of the execution plan in the `explain` result is MergeJoin. When the second `SELECT` statement is being executed, the optimizer uses the binding in the SESSION scope instead of the binding in the GLOBAL scope and adds the `hash_join(t1, t2)` hint to the statement. The top node of the execution plan in the `explain` result is HashJoin.

Each standardized SQL statement can have only one binding created using `CREATE BINDING` at a time. When multiple bindings are created for the same standardized SQL statement, the last created binding is retained, and all previous bindings (created and evolved) are marked as deleted. But session bindings and global bindings can coexist and are not affected by this logic.

In addition, when you create a binding, TiDB requires that the session is in a database context, which means that a database is specified when the client is connected or `use ${database}` is executed.

The original SQL statement and the bound statement must have the same text after normalization and hint removal, or the binding will fail. Take the following examples:

- This binding can be created successfully because the texts before and after parameterization and hint removal are the same: `SELECT * FROM test . t WHERE a > ?`

    ```sql
    CREATE BINDING FOR SELECT * FROM t WHERE a > 1 USING SELECT * FROM t use index  (idx) WHERE a > 2
    ```

- This binding will fail because the original SQL statement is processed as `SELECT * FROM test . t WHERE a > ?`, while the bound SQL statement is processed differently as `SELECT * FROM test . t WHERE b > ?`.

    ```sql
    CREATE BINDING FOR SELECT * FROM t WHERE a > 1 USING SELECT * FROM t use index(idx) WHERE b > 2
    ```

> **Note:**
>
> For `PREPARE` / `EXECUTE` statements and for queries executed with binary protocols, you need to create execution plan bindings for the real query statements, not for the `PREPARE` / `EXECUTE` statements.
