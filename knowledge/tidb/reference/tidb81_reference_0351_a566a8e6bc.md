# Resource group, stale read, TSO, and binary plan functions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/tidb-functions.md`
- Source Title: `TiDB Specific Functions`
- Source Heading Path: `TiDB Specific Functions > CURRENT_RESOURCE_GROUP | TiDB Specific Functions > TIDB_BOUNDED_STALENESS | TiDB Specific Functions > TIDB_CURRENT_TSO | TiDB Specific Functions > TIDB_DECODE_BINARY_PLAN`
- Source Line Ranges: `54-166`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`, `pd`
- Topic Tags: `resource-control`, `resource-group`, `stale-read`, `as-of-timestamp`, `tso`, `transaction`, `statement-summary`, `binary-plan`, `system-variable`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0351_a566a8e6bc`
- Source ID: `tidb-docs-8.1:functions-and-operators/tidb-functions.md#current-resource-group`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ce7f290d316ca2124417ec348a3cdfca69b2e9a3d1b300b8e74e8ff0f2402ef6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/tidb-functions#current-resource-group
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/tidb-functions.md

## Retrieval Guidance

- Use When: Use this chunk when you need exact behavior and examples for `CURRENT_RESOURCE_GROUP()`, `TIDB_BOUNDED_STALENESS()`, `TIDB_CURRENT_TSO()`, or `TIDB_DECODE_BINARY_PLAN()`.
- Retrieval Keywords: CURRENT_RESOURCE_GROUP(), SET RESOURCE GROUP, ALTER USER RESOURCE GROUP, default resource group, resource control, TIDB_BOUNDED_STALENESS(), AS OF TIMESTAMP, TIDB_CURRENT_TSO(), TSO for the current transaction, tidb_current_ts, @@tidb_current_ts, TIDB_DECODE_BINARY_PLAN(binary_plan), BINARY_PLAN, STATEMENTS_SUMMARY, information_schema.STATEMENTS_SUMMARY, tidb_generate_binary_plan, SELECT BINARY_PLAN,TIDB_DECODE_BINARY_PLAN(BINARY_PLAN)
- Follow-up Guidance: The examples show checking the current session resource group, comparing `TIDB_CURRENT_TSO()` with `@@tidb_current_ts`, and decoding the `BINARY_PLAN` column from `information_schema.STATEMENTS_SUMMARY` when `tidb_generate_binary_plan` is `ON`.
- Classification Note: This is a reference chunk because it defines four specific functions and includes their exact SQL syntax, related identifiers, and example outputs from the official content.

## Official Source Content

## CURRENT_RESOURCE_GROUP

The `CURRENT_RESOURCE_GROUP()` function is used to show the resource group name that the current session is bound to. When the [Resource control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) feature is enabled, the available resources that can be used by SQL statements are restricted by the resource quota of the bound resource group.

When a session is established, TiDB binds the session to the resource group that the login user is bound to by default. If the user is not bound to any resource groups, the session is bound to the `default` resource group. Once the session is established, the bound resource group will not change by default, even if the bound resource group of the user is changed via [modifying the resource group bound to the user](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-user#modify-basic-user-information). To change the bound resource group of the current session, you can use [`SET RESOURCE GROUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-resource-group).

Examples:

Create a user `user1`, create two resource groups `rg1` and `rg2`, and bind the user `user1` to the resource group `rg1`:

```sql
CREATE USER 'user1';
CREATE RESOURCE GROUP rg1 RU_PER_SEC = 1000;
CREATE RESOURCE GROUP rg2 RU_PER_SEC = 2000;
ALTER USER 'user1' RESOURCE GROUP `rg1`;
```

Use `user1` to log in and view the resource group bound to the current user:

```sql
SELECT CURRENT_RESOURCE_GROUP();
```

```
+--------------------------+
| CURRENT_RESOURCE_GROUP() |
+--------------------------+
| rg1                      |
+--------------------------+
1 row in set (0.00 sec)
```

Execute `SET RESOURCE GROUP` to set the resource group for the current session to `rg2`, and then view the resource group bound to the current user:

```sql
SET RESOURCE GROUP `rg2`;
SELECT CURRENT_RESOURCE_GROUP();
```

```
+--------------------------+
| CURRENT_RESOURCE_GROUP() |
+--------------------------+
| rg2                      |
+--------------------------+
1 row in set (0.00 sec)
```
## TIDB_BOUNDED_STALENESS

The `TIDB_BOUNDED_STALENESS()` function is used as part of [`AS OF TIMESTAMP`](https://docs.pingcap.com/tidb/stable/as-of-timestamp) syntax.
## TIDB_CURRENT_TSO

The `TIDB_CURRENT_TSO()` function returns the [TSO](https://docs.pingcap.com/tidb/stable/tso) for the current transaction. This is similar to the [`tidb_current_ts`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_current_ts) system variable.

```sql
BEGIN;
```

```
Query OK, 0 rows affected (0.00 sec)
```

```sql
SELECT TIDB_CURRENT_TSO();
```

```
+--------------------+
| TIDB_CURRENT_TSO() |
+--------------------+
| 450456244814610433 |
+--------------------+
1 row in set (0.00 sec)
```

```sql
SELECT @@tidb_current_ts;
```

```
+--------------------+
| @@tidb_current_ts  |
+--------------------+
| 450456244814610433 |
+--------------------+
1 row in set (0.00 sec)
```
## TIDB_DECODE_BINARY_PLAN

The `TIDB_DECODE_BINARY_PLAN(binary_plan)` function decodes binary plans, like the ones in the `BINARY_PLAN` column of the [`STATEMENTS_SUMMARY`](https://docs.pingcap.com/tidb/stable/statement-summary-tables) table.

The [`tidb_generate_binary_plan`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_generate_binary_plan-new-in-v620) variable must be set to `ON` for the binary plans to be available.

Example:

```sql
SELECT BINARY_PLAN,TIDB_DECODE_BINARY_PLAN(BINARY_PLAN) FROM information_schema.STATEMENTS_SUMMARY LIMIT 1\G
```

```
*************************** 1. row ***************************
                         BINARY_PLAN: lQLwPgqQAgoMUHJvamVjdGlvbl8zEngKDk1lbVRhYmxlU2Nhbl80KQAAAAAAiMNAMAM4AUABSioKKAoSaW5mb3JtYQU00HNjaGVtYRISU1RBVEVNRU5UU19TVU1NQVJZWhV0aW1lOjI5LjPCtXMsIGxvb3BzOjJw////CQIEAXgJCBD///8BIQFnDOCb+EA6cQCQUjlDb2x1bW4jOTIsIHRpZGJfZGVjb2RlX2JpbmFyeV9wbGFuKBUjCCktPg0MEDEwM1oWBYAIMTA4NoEAeGINQ29uY3VycmVuY3k6NXDIZXj///////////8BGAE=
TIDB_DECODE_BINARY_PLAN(BINARY_PLAN):
| id               | estRows  | estCost   | actRows | task | access object            | execution info                       | operator info                                             | memory  | disk  |
| Projection_3     | 10000.00 | 100798.00 | 3       | root |                          | time:108.3µs, loops:2, Concurrency:5 | Column#92, tidb_decode_binary_plan(Column#92)->Column#103 | 12.7 KB | N/A   |
| └─MemTableScan_4 | 10000.00 | 0.00      | 3       | root | table:STATEMENTS_SUMMARY | time:29.3µs, loops:2                 |                                                           | N/A     | N/A   |

1 row in set (0.00 sec)
```
