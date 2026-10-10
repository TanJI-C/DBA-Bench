# MySQL compatibility and safe-mode replication behavior

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-faq.md`
- Source Title: `TiCDC FAQs`
- Source Heading Path: `TiCDC FAQs > The default value of the time type field is inconsistent when replicating a DDL statement to the downstream MySQL 5.7. What can I do? | TiCDC FAQs > Why do `INSERT`/`UPDATE` statements from the upstream become `REPLACE INTO` after being replicated to the downstream if I set `safe-mode` to `true` when I create a TiCDC replication task?`
- Source Line Ranges: `336-367`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `sql`, `tidb`
- Topic Tags: `mysql-compatibility`, `timestamp-defaults`, `ddl-replication`, `safe-mode`, `replace-into`, `version-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0178_12ce429b35`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-faq.md#the-default-value-of-the-time-type-field-is-inconsistent-when-replicating-a-ddl-statement-to-the-downstream-mysql-5-7-what-can-i-do`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `fc75a18bf7ba450465ad637a1d93e13a4feb2edc87d2985d34ef5f3174a6abad`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#the-default-value-of-the-time-type-field-is-inconsistent-when-replicating-a-ddl-statement-to-the-downstream-mysql-5-7-what-can-i-do
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-faq.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing TiCDC differences in downstream MySQL 5.7 timestamp defaults or when INSERT and UPDATE are replicated as REPLACE INTO because of safe-mode behavior.
- Retrieval Keywords: explicit_defaults_for_timestamp, MySQL 5.7, timestamp default CURRENT_TIMESTAMP, show create table test, create table test (id int primary key, ts timestamp), MySQL Compatibility, safe-mode, REPLACE INTO, INSERT UPDATE converted to REPLACE INTO, at least once, v5.0.1, v4.0.13, v6.1.3
- Follow-up Guidance: The content states that TiCDC automatically sets `explicit_defaults_for_timestamp = ON` for replication to MySQL since v5.0.1 or v4.0.13, and that in v6.1.3 and later the default value of `safe-mode` changes to `false`.
- Classification Note: This is classified as configuration because the official content explains replication behavior controlled by `explicit_defaults_for_timestamp` compatibility and the `safe-mode` parameter.

## Official Source Content

## The default value of the time type field is inconsistent when replicating a DDL statement to the downstream MySQL 5.7. What can I do?

Suppose that the `create table test (id int primary key, ts timestamp)` statement is executed in the upstream TiDB. When TiCDC replicates this statement to the downstream MySQL 5.7, MySQL uses the default configuration. The table schema after the replication is as follows. The default value of the `timestamp` field becomes `CURRENT_TIMESTAMP`:

```sql
mysql root@127.0.0.1:test> show create table test;
+-------+----------------------------------------------------------------------------------+
| Table | Create Table                                                                     |
+-------+----------------------------------------------------------------------------------+
| test  | CREATE TABLE `test` (                                                            |
|       |   `id` int(11) NOT NULL,                                                         |
|       |   `ts` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, |
|       |   PRIMARY KEY (`id`)                                                             |
|       | ) ENGINE=InnoDB DEFAULT CHARSET=latin1                                           |
+-------+----------------------------------------------------------------------------------+
1 row in set
```

From the result, you can see that the table schema before and after the replication is inconsistent. This is because the default value of `explicit_defaults_for_timestamp` in TiDB is different from that in MySQL. See [MySQL Compatibility](https://docs.pingcap.com/tidb/stable/mysql-compatibility#default-differences) for details.

Since v5.0.1 or v4.0.13, for each replication to MySQL, TiCDC automatically sets `explicit_defaults_for_timestamp = ON` to ensure that the time type is consistent between the upstream and downstream. For versions earlier than v5.0.1 or v4.0.13, pay attention to the compatibility issue caused by the inconsistent `explicit_defaults_for_timestamp` value when using TiCDC to replicate the time type data.
## Why do `INSERT`/`UPDATE` statements from the upstream become `REPLACE INTO` after being replicated to the downstream if I set `safe-mode` to `true` when I create a TiCDC replication task?

TiCDC guarantees that all data is replicated at least once. When there is duplicate data in the downstream, write conflicts occur. To avoid this problem, TiCDC converts `INSERT` and `UPDATE` statements into `REPLACE INTO` statements. This behavior is controlled by the `safe-mode` parameter.

In versions earlier than v6.1.3, the default value of `safe-mode` is `true`, which means all `INSERT` and `UPDATE` statements are converted into `REPLACE INTO` statements.

In v6.1.3 and later versions, the default value of `safe-mode` changes to `false`, and TiCDC can automatically determine whether the downstream has duplicate data. If no duplicate data is detected, TiCDC directly replicates `INSERT` and `UPDATE` statements without conversion; otherwise, TiCDC converts `INSERT` and `UPDATE` statements into `REPLACE INTO` statements and then replicates them.
