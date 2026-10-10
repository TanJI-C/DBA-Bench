# Troubleshooting optimizer hints not taking effect

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/optimizer-hints.md`
- Source Title: `Optimizer Hints`
- Source Heading Path: `Optimizer Hints > Troubleshoot common issues that hints do not take effect | Optimizer Hints > Troubleshoot common issues that hints do not take effect > Hints do not take effect because your MySQL command-line client strips hints | Optimizer Hints > Troubleshoot common issues that hints do not take effect > Hints do not take effect because the database name is not specified | Optimizer Hints > Troubleshoot common issues that hints do not take effect > Hints do not take effect because the database name is not explicitly specified in cross-table queries | Optimizer Hints > Troubleshoot common issues that hints do not take effect > Hints do not take effect because they are placed in wrong locations | Optimizer Hints > Troubleshoot common issues that hints do not take effect > `INL_JOIN` hint does not take effect`
- Source Line Ranges: `860-937`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `optimizer-hints`, `troubleshooting`, `mysql-client`, `database-name`, `cross-database-query`, `hint-placement`, `warnings`, `inl-join`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0057_fed814fe61`
- Source ID: `tidb-docs-8.1:optimizer-hints.md#troubleshoot-common-issues-that-hints-do-not-take-effect`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `03a59a6cd3572b88b022b3dc98b6ff5b94bc7cb525f37904988c65605ab20aae`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/optimizer-hints#troubleshoot-common-issues-that-hints-do-not-take-effect
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/optimizer-hints.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting optimizer hints that do not take effect because of client comment stripping, missing database names, cross-database table references, wrong hint placement, or an INL_JOIN issue.
- Retrieval Keywords: hints do not take effect, MySQL command-line client strips hints, --comments, mysql -h 127.0.0.1 -P 4000 -uroot --comments, database name is not specified, SHOW WARNINGS, use_index(t, a), Warning 1815, use_index(.t, a) is inapplicable, check whether the table(.t) exists, cross-table queries, use_index(test1.t1, a), use_index(test2.t1, a) is inapplicable, wrong locations, Optimizer hint can only be followed by certain keywords like SELECT, INSERT, etc., parser:8066, SELECT * /*+ use_index(t, a) */ FROM t, INL_JOIN hint does not take effect
- Follow-up Guidance: The source says to check SHOW WARNINGS, use --comments for MySQL command-line clients earlier than 5.7.7, specify the database name explicitly such as use_index(test1.t1, a), and place hints directly after keywords like SELECT.
- Classification Note: This is a diagnosis entry because the official content enumerates concrete reasons optimizer hints are inapplicable and shows the associated warnings and syntax errors.

## Official Source Content

## Troubleshoot common issues that hints do not take effect
### Hints do not take effect because your MySQL command-line client strips hints

MySQL command-line clients earlier than 5.7.7 strip optimizer hints by default. If you want to use the Hint syntax in these earlier versions, add the `--comments` option when starting the client. For example: `mysql -h 127.0.0.1 -P 4000 -uroot --comments`.
### Hints do not take effect because the database name is not specified

If you do not specify the database name when creating a connection, hints might not take effect. For example:

When connecting to TiDB, you use the `mysql -h127.0.0.1 -P4000 -uroot` command without the `-D` option, and then execute the following SQL statements:

```sql
SELECT /*+ use_index(t, a) */ a FROM test.t;
SHOW WARNINGS;
```

Because TiDB cannot identify the database for table `t`, the `use_index(t, a)` hint does not take effect.

```sql
+---------+------+----------------------------------------------------------------------+
| Level   | Code | Message                                                              |
+---------+------+----------------------------------------------------------------------+
| Warning | 1815 | use_index(.t, a) is inapplicable, check whether the table(.t) exists |
+---------+------+----------------------------------------------------------------------+
1 row in set (0.00 sec)
```
### Hints do not take effect because the database name is not explicitly specified in cross-table queries

When executing cross-table queries, you need to explicitly specify database names. Otherwise, hints might not take effect. For example:

```sql
USE test1;
CREATE TABLE t1(a INT, KEY(a));
USE test2;
CREATE TABLE t2(a INT, KEY(a));
SELECT /*+ use_index(t1, a) */ * FROM test1.t1, t2;
SHOW WARNINGS;
```

In the preceding statements, because table `t1` is not in the current `test2` database, the `use_index(t1, a)` hint does not take effect.

```sql
+---------+------+----------------------------------------------------------------------------------+
| Level   | Code | Message                                                                          |
+---------+------+----------------------------------------------------------------------------------+
| Warning | 1815 | use_index(test2.t1, a) is inapplicable, check whether the table(test2.t1) exists |
+---------+------+----------------------------------------------------------------------------------+
1 row in set (0.00 sec)
```

In this case, you need to specify the database name explicitly by using `use_index(test1.t1, a)` instead of `use_index(t1, a)`.
### Hints do not take effect because they are placed in wrong locations

Hints cannot take effect if they are not placed directly after the specific keywords. For example:

```sql
SELECT * /*+ use_index(t, a) */ FROM t;
SHOW WARNINGS;
```

The warning is as follows:

```sql
+---------+------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Level   | Code | Message                                                                                                                                                                                                                 |
+---------+------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| Warning | 1064 | You have an error in your SQL syntax; check the manual that corresponds to your TiDB version for the right syntax to use [parser:8066]Optimizer hint can only be followed by certain keywords like SELECT, INSERT, etc. |
+---------+------+-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.01 sec)
```

In this case, you need to place the hint directly after the `SELECT` keyword. For more details, see the [Syntax](#syntax) section.
### `INL_JOIN` hint does not take effect
