# Create binding from historical execution plan

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-management.md`
- Source Title: `SQL Plan Management (SPM)`
- Source Heading Path: `SQL Plan Management (SPM) > SQL binding > Create a binding > Create a binding according to a historical execution plan`
- Source Line Ranges: `225-310`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `sql-binding`, `plan-digest`, `statement-summary`, `historical-plan`, `binding-verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0220_6fbe76c579`
- Source ID: `tidb-docs-8.1:sql-plan-management.md#create-a-binding-according-to-a-historical-execution-plan`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1f833fe96f2f756df297e062e5a167474f3238f4fb6420ecebba809fd50d1042`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-management#create-a-binding-according-to-a-historical-execution-plan
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-management.md

## Retrieval Guidance

- Use When: Use this chunk when you need the syntax and prerequisites for creating a SQL binding from a historical execution plan by `plan_digest` and checking whether the binding takes effect.
- Retrieval Keywords: CREATE [GLOBAL | SESSION] BINDING FROM HISTORY USING PLAN DIGEST, plan_digest, historical execution plan, STATEMENTS_SUMMARY, INFORMATION_SCHEMA.STATEMENTS_SUMMARY, tidb_enable_stmt_summary, SHOW BINDINGS, @@LAST_PLAN_FROM_BINDING, binding verification, source history
- Follow-up Guidance: It also shows how to query `INFORMATION_SCHEMA.STATEMENTS_SUMMARY` to get the target `plan_digest`, inspect the created binding with `SHOW BINDINGS`, and confirm effectiveness with `SELECT @@LAST_PLAN_FROM_BINDING`.
- Classification Note: This is classified as an operation because the content provides SQL statements, prerequisites, caveats, and verification steps for creating a binding from history in TiDB.

## Official Source Content

#### Create a binding according to a historical execution plan

To make the execution plan of a SQL statement fixed to a historical execution plan, you can use `plan_digest` to bind that historical execution plan to the SQL statement, which is more convenient than binding it according to a SQL statement.

When using this feature, note the following:

- The feature generates hints according to historical execution plans and uses the generated hints for binding. Because historical execution plans are stored in [Statement Summary Tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables), before using this feature, you need to enable the [`tidb_enable_stmt_summary`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_stmt_summary-new-in-v304) system variable first.
- For TiFlash queries, Join queries with three or more tables, and queries that contain subqueries, the auto-generated hints are not adequate, which might result in the plan not being fully bound. In such cases, a warning will occur when creating a binding.
- If a historical execution plan is for a SQL statement with hints, the hints will be added to the binding. For example, after executing `SELECT /*+ max_execution_time(1000) */ * FROM t`, the binding created with its `plan_digest` will include `max_execution_time(1000)`.

The SQL statement of this binding method is as follows:

```sql
CREATE [GLOBAL | SESSION] BINDING FROM HISTORY USING PLAN DIGEST 'plan_digest';
```

This statement binds an execution plan to a SQL statement using `plan_digest`. The default scope is SESSION. The applicable SQL statements, priorities, scopes, and effective conditions of the created bindings are the same as that of [bindings created according to SQL statements](#create-a-binding-according-to-a-sql-statement).

To use this binding method, you need to first get the `plan_digest` corresponding to the target historical execution plan in `statements_summary`, and then create a binding using the `plan_digest`. The detailed steps are as follows:

1. Get the `plan_digest` corresponding to the target execution plan in `statements_summary`.

    For example:

    ```sql
    CREATE TABLE t(id INT PRIMARY KEY , a INT, KEY idx_a(a));
    SELECT /*+ IGNORE_INDEX(t, idx_a) */ * FROM t WHERE a = 1;
    SELECT * FROM INFORMATION_SCHEMA.STATEMENTS_SUMMARY WHERE QUERY_SAMPLE_TEXT = 'SELECT /*+ IGNORE_INDEX(t, idx_a) */ * FROM t WHERE a = 1'\G
    ```

    The following is a part of the example query result of `statements_summary`:

    ```
    SUMMARY_BEGIN_TIME: 2022-12-01 19:00:00
    ...........
          DIGEST_TEXT: select * from `t` where `a` = ?
    ...........
          PLAN_DIGEST: 4e3159169cc63c14b139a4e7d72eae1759875c9a9581f94bb2079aae961189cb
                 PLAN:  id                  task        estRows operator info                           actRows execution info                                                                                                                                             memory      disk
                        TableReader_7       root        10      data:Selection_6                        0       time:4.05ms, loops:1, cop_task: {num: 1, max: 598.6µs, proc_keys: 0, rpc_num: 2, rpc_time: 609.8µs, copr_cache_hit_ratio: 0.00, distsql_concurrency: 15}   176 Bytes   N/A
                        └─Selection_6       cop[tikv]   10      eq(test.t.a, 1)                         0       tikv_task:{time:560.8µs, loops:0}                                                                                                                          N/A         N/A
                          └─TableFullScan_5 cop[tikv]   10000   table:t, keep order:false, stats:pseudo 0       tikv_task:{time:560.8µs, loops:0}                                                                                                                          N/A         N/A
          BINARY_PLAN: 6QOYCuQDCg1UYWJsZVJlYWRlcl83Ev8BCgtTZWxlY3Rpb25fNhKOAQoPBSJQRnVsbFNjYW5fNSEBAAAAOA0/QSkAAQHwW4jDQDgCQAJKCwoJCgR0ZXN0EgF0Uh5rZWVwIG9yZGVyOmZhbHNlLCBzdGF0czpwc2V1ZG9qInRpa3ZfdGFzazp7dGltZTo1NjAuOMK1cywgbG9vcHM6MH1w////CQMEAXgJCBD///8BIQFzCDhVQw19BAAkBX0QUg9lcSgBfCAudC5hLCAxKWrmYQAYHOi0gc6hBB1hJAFAAVIQZGF0YTo9GgRaFAW4HDQuMDVtcywgCbYcMWKEAWNvcF8F2agge251bTogMSwgbWF4OiA1OTguNsK1cywgcHJvY19rZXlzOiAwLCBycGNfBSkAMgkMBVcQIDYwOS4pEPBDY29wcl9jYWNoZV9oaXRfcmF0aW86IDAuMDAsIGRpc3RzcWxfY29uY3VycmVuY3k6IDE1fXCwAXj///////////8BGAE=
    ```

    In this example, you can see that the execution plan corresponding to `plan_digest` is `4e3159169cc63c14b139a4e7d72eae1759875c9a9581f94bb2079aae961189cb`.

2. Use `plan_digest` to create a binding:

    ```sql
    CREATE BINDING FROM HISTORY USING PLAN DIGEST '4e3159169cc63c14b139a4e7d72eae1759875c9a9581f94bb2079aae961189cb';
    ```

To verify whether the created binding takes effect, you can [view bindings](#view-bindings):

```sql
SHOW BINDINGS\G
```

```
*************************** 1. row ***************************
Original_sql: select * from `test` . `t` where `a` = ?
    Bind_sql: SELECT /*+ use_index(@`sel_1` `test`.`t` ) ignore_index(`t` `idx_a`)*/ * FROM `test`.`t` WHERE `a` = 1
       ...........
  Sql_digest: 6909a1bbce5f64ade0a532d7058dd77b6ad5d5068aee22a531304280de48349f
 Plan_digest:
1 row in set (0.01 sec)

ERROR:
No query specified
```

```sql
SELECT * FROM t WHERE a = 1;
SELECT @@LAST_PLAN_FROM_BINDING;
```

```
+--------------------------+
| @@LAST_PLAN_FROM_BINDING |
+--------------------------+
|                        1 |
+--------------------------+
1 row in set (0.00 sec)
```
