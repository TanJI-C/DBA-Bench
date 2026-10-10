# DROP BINDING example, compatibility, and related statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-drop-binding.md`
- Source Title: `DROP [GLOBAL|SESSION] BINDING`
- Source Heading Path: `DROP [GLOBAL|SESSION] BINDING > Examples | DROP [GLOBAL|SESSION] BINDING > MySQL compatibility | DROP [GLOBAL|SESSION] BINDING > See also`
- Source Line Ranges: `136-206`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `sql-plan-management`, `binding`, `sql-digest`, `plan-digest`, `examples`, `mysql-compatibility`, `optimizer-hints`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0572_df0de3db11`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-drop-binding.md#examples`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66f8afcd4352756db11a0be850e9121887c030107847afaa8d37d2b73a031722`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-binding#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-drop-binding.md

## Retrieval Guidance

- Use When: Use this chunk when looking for an example of removing a SQL binding by `sql_digest`, checking binding status with `SHOW BINDINGS`, or confirming whether `DROP BINDING` is MySQL-compatible.
- Retrieval Keywords: DROP BINDING FOR SQL DIGEST, sql_digest, plan_digest, INFORMATION_SCHEMA.STATEMENTS_SUMMARY, QUERY_SAMPLE_TEXT, CREATE BINDING FROM HISTORY USING PLAN DIGEST, SHOW BINDINGS, @@LAST_PLAN_FROM_BINDING, IGNORE_INDEX(t, a), TiDB extension to MySQL syntax, SQL Plan Management, Optimizer Hints
- Follow-up Guidance: Related statements listed here are `CREATE [GLOBAL|SESSION] BINDING`, `SHOW [GLOBAL|SESSION] BINDINGS`, `ANALYZE TABLE`, `Optimizer Hints`, and `SQL Plan Management`.
- Classification Note: This is reference content because it provides a concrete SQL example, compatibility note, and related statement links for `DROP BINDING` in TiDB SQL.

## Official Source Content

The following example shows how to remove a binding according to `sql_digest`.

```sql
mysql> CREATE TABLE t(id INT PRIMARY KEY , a INT, KEY(a));
Query OK, 0 rows affected (0.06 sec)

mysql> SELECT /*+ IGNORE_INDEX(t, a) */ * FROM t WHERE a = 1;
Empty set (0.01 sec)

mysql> SELECT plan_digest FROM INFORMATION_SCHEMA.STATEMENTS_SUMMARY WHERE QUERY_SAMPLE_TEXT = 'SELECT /*+ IGNORE_INDEX(t, a) */ * FROM t WHERE a = 1';
+------------------------------------------------------------------+
| plan_digest                                                      |
+------------------------------------------------------------------+
| 4e3159169cc63c14b139a4e7d72eae1759875c9a9581f94bb2079aae961189cb |
+------------------------------------------------------------------+
1 row in set (0.01 sec)

mysql> CREATE BINDING FROM HISTORY USING PLAN DIGEST '4e3159169cc63c14b139a4e7d72eae1759875c9a9581f94bb2079aae961189cb';
Query OK, 0 rows affected (0.02 sec)

mysql> SELECT * FROM t WHERE a = 1;
Empty set (0.01 sec)

mysql> SELECT @@LAST_PLAN_FROM_BINDING;
+--------------------------+
| @@LAST_PLAN_FROM_BINDING |
+--------------------------+
|                        1 |
+--------------------------+
1 row in set (0.01 sec)

mysql> SHOW BINDINGS\G
*************************** 1. row ***************************
Original_sql: select * from `test` . `t` where `a` = ?
    Bind_sql: SELECT /*+ use_index(@`sel_1` `test`.`t` ) ignore_index(`t` `a`)*/ * FROM `test`.`t` WHERE `a` = 1
  Default_db: test
      Status: enabled
 Create_time: 2022-12-14 15:26:22.277
 Update_time: 2022-12-14 15:26:22.277
     Charset: utf8mb4
   Collation: utf8mb4_general_ci
      Source: history
  Sql_digest: 6909a1bbce5f64ade0a532d7058dd77b6ad5d5068aee22a531304280de48349f
 Plan_digest: 4e3159169cc63c14b139a4e7d72eae1759875c9a9581f94bb2079aae961189cb
1 row in set (0.02 sec)

ERROR:
No query specified

mysql> DROP BINDING FOR SQL DIGEST '6909a1bbce5f64ade0a532d7058dd77b6ad5d5068aee22a531304280de48349f';
Query OK, 0 rows affected (0.00 sec)

mysql> SHOW BINDINGS\G
Empty set (0.01 sec)

ERROR:
No query specified
```
## MySQL compatibility

This statement is a TiDB extension to MySQL syntax.
## See also

* [CREATE [GLOBAL|SESSION] BINDING](/sql-statements/sql-statement-create-binding.md)
* [SHOW [GLOBAL|SESSION] BINDINGS](/sql-statements/sql-statement-show-bindings.md)
* [ANALYZE TABLE](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-analyze-table)
* [Optimizer Hints](https://docs.pingcap.com/tidb/stable/optimizer-hints)
* [SQL Plan Management](https://docs.pingcap.com/tidb/stable/sql-plan-management)
