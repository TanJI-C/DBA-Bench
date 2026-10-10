# Troubleshoot and inspect SQL binding usage and cache

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-management.md`
- Source Title: `SQL Plan Management (SPM)`
- Source Heading Path: `SQL Plan Management (SPM) > SQL binding > Troubleshoot a binding | SQL Plan Management (SPM) > SQL binding > Cache bindings`
- Source Line Ranges: `401-479`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `sql-binding`, `troubleshooting`, `execution-plan`, `show-warnings`, `binding-cache`, `lru-cache`, `system-variable`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0062_e10032046a`
- Source ID: `tidb-docs-8.1:sql-plan-management.md#troubleshoot-a-binding`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4ff95b5153874934ca5961f8b1906177965f9b1cde4609f1ba1700d80684676a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-management#troubleshoot-a-binding
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-management.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether a SQL statement used a binding and when inspecting binding cache status on a TiDB instance.
- Retrieval Keywords: last_plan_from_binding, @@last_plan_from_binding, CREATE GLOBAL BINDING, explain format = 'verbose', show warnings, Using the bindSQL, binding_cache, SHOW binding_cache status, tidb_mem_quota_binding_cache, LRU cache, bindings_in_cache, bindings_in_table, memory_usage, memory_quota
- Follow-up Guidance: The source also shows that `SHOW binding_cache status` returns `bindings_in_cache`, `bindings_in_table`, `memory_usage`, and `memory_quota` with GLOBAL scope by default and not modifiable.
- Classification Note: This is classified as diagnosis because the content explains how to verify binding usage with `last_plan_from_binding`, `explain format = 'verbose'`, and `show warnings`, and how to inspect cached bindings.

## Official Source Content

### Troubleshoot a binding

You can use either of the following methods to troubleshoot a binding:

- Use the system variable [`last_plan_from_binding`](https://docs.pingcap.com/tidb/stable/system-variables#last_plan_from_binding-new-in-v40) to show whether the execution plan used by the last executed statement is from the binding.

    ```sql
    -- Create a global binding
    CREATE GLOBAL BINDING for
        SELECT * FROM t
    USING
        SELECT /*+ USE_INDEX(t, idx_a) */ * FROM t;

    SELECT * FROM t;
    SELECT @@[SESSION.]last_plan_from_binding;
    ```

    ```sql
    +--------------------------+
    | @@last_plan_from_binding |
    +--------------------------+
    |                        1 |
    +--------------------------+
    1 row in set (0.00 sec)
    ```

- Use the `explain format = 'verbose'` statement to view the query plan of a SQL statement. If the SQL statement uses a binding, you can run `show warnings` to check which binding is used in the SQL statement.

    ```sql
    -- Create a global binding

    CREATE GLOBAL BINDING for
        SELECT * FROM t
    USING
        SELECT /*+ USE_INDEX(t, idx_a) */ * FROM t;

    -- Use explain format = 'verbose' to view the execution plan of a SQL statement

    explain format = 'verbose' SELECT * FROM t;

    -- Run `show warnings` to view the binding used in the query.

    show warnings;
    ```

    ```sql
    +-------+------+--------------------------------------------------------------------------+
    | Level | Code | Message                                                                  |
    +-------+------+--------------------------------------------------------------------------+
    | Note  | 1105 | Using the bindSQL: SELECT /*+ USE_INDEX(`t` `idx_a`)*/ * FROM `test`.`t` |
    +-------+------+--------------------------------------------------------------------------+
    1 row in set (0.01 sec)

    ```
### Cache bindings

Each TiDB instance has a least recently used (LRU) cache for bindings. The cache capacity is controlled by the system variable [`tidb_mem_quota_binding_cache`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_mem_quota_binding_cache-new-in-v600). You can view bindings that are cached in the TiDB instance.

To view the cache status of bindings, run the `SHOW binding_cache status` statement. In this statement, the effective scope is GLOBAL by default and cannot be modified. This statement returns the number of available bindings in the cache, the total number of available bindings in the system, memory usage of all cached bindings, and the total memory for the cache.

```sql

SHOW binding_cache status;
```

```sql
+-------------------+-------------------+--------------+--------------+
| bindings_in_cache | bindings_in_table | memory_usage | memory_quota |
+-------------------+-------------------+--------------+--------------+
|                 1 |                 1 | 159 Bytes    | 64 MB        |
+-------------------+-------------------+--------------+--------------+
1 row in set (0.00 sec)
```
