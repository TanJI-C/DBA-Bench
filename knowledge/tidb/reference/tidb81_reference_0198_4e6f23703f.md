# Savepoint support and transaction limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-transaction-restraints.md`
- Source Title: `Transaction Restraints`
- Source Heading Path: `Transaction Restraints > Support for `savepoint` and nested transactions | Transaction Restraints > Large transaction restrictions | Transaction Restraints > Auto-committed `SELECT FOR UPDATE` statements do NOT wait for locks | Transaction Restraints > Need help?`
- Source Line Ranges: `682-744`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `savepoint`, `nested-transactions`, `spring`, `transaction-size`, `row-size`, `select-for-update`, `autocommit`, `compatibility`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0198_4e6f23703f`
- Source ID: `tidb-docs-8.1:develop/dev-guide-transaction-restraints.md#support-for-savepoint-and-nested-transactions`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b94a2535caf97e722366a51a48770680baebf2966ac05103675f2c4695afaa69`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-restraints#support-for-savepoint-and-nested-transactions
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-transaction-restraints.md

## Retrieval Guidance

- Use When: Use this chunk when looking for documented transaction restraints covering `savepoint` support, nested transactions, large transaction size limits, and auto-committed `SELECT FOR UPDATE` lock behavior.
- Retrieval Keywords: Support for `savepoint` and nested transactions, PROPAGATION_NESTED, Spring, SAVEPOINT svp1, ROLLBACK TO SAVEPOINT svp1, RELEASE SAVEPOINT svp1, Large transaction restrictions, maximum single row record size is 120 MiB, performance.txn-entry-size-limit, tidb_txn_entry_size_limit, maximum single transaction size supported is 1 TiB, performance.txn-total-size-limit, Auto-committed `SELECT FOR UPDATE` statements do NOT wait for locks, BEGIN;COMMIT;, known incompatibility issue with MySQL, Need help, Discord, Slack, support ticket
- Follow-up Guidance: The chunk also points readers to Discord, Slack, and support ticket links in the Need help section.
- Classification Note: This is classified as reference because the official content summarizes support boundaries, version-scoped notes, size limits, SQL examples, and compatibility behavior for transactions.

## Official Source Content

## Support for `savepoint` and nested transactions

> **Note:**
>
> Starting from v6.2.0, TiDB supports the [`savepoint`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-savepoint) feature. If your TiDB cluster is earlier than v6.2.0, your TiDB cluster does not support the `PROPAGATION_NESTED` behavior. It is recommended to upgrade to v6.2.0 or a later version. If upgrading TiDB is not possible, and your applications are based on the **Java Spring** framework that uses the `PROPAGATION_NESTED` propagation behavior, you need to adapt it on the application side to remove the logic for nested transactions.

The `PROPAGATION_NESTED` propagation behavior supported by **Spring** triggers a nested transaction, which is a child transaction that is started independently of the current transaction. A `savepoint` is recorded when the nested transaction starts. If the nested transaction fails, the transaction will roll back to the `savepoint` state. The nested transaction is part of the outer transaction and will be committed together with the outer transaction.

The following example demonstrates the `savepoint` mechanism:

```sql
mysql> BEGIN;
mysql> INSERT INTO T2 VALUES(100);
mysql> SAVEPOINT svp1;
mysql> INSERT INTO T2 VALUES(200);
mysql> ROLLBACK TO SAVEPOINT svp1;
mysql> RELEASE SAVEPOINT svp1;
mysql> COMMIT;
mysql> SELECT * FROM T2;
+------+
|  ID   |
+------+
|  100 |
+------+
```
## Large transaction restrictions

The basic principle is to limit the size of the transaction. At the KV level, TiDB has a restriction on the size of a single transaction. At the SQL level, one row of data is mapped to one KV entry, and each additional index will add one KV entry. The restriction is as follows at the SQL level:

- The maximum single row record size is 120 MiB.

    - You can adjust it by using the [`performance.txn-entry-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-entry-size-limit-new-in-v4010-and-v500) configuration parameter of tidb-server for TiDB v4.0.10 and later v4.0.x versions, TiDB v5.0.0 and later versions. The value is `6 MB` for versions earlier than v4.0.10.
    - Starting from v7.6.0, you can use the [`tidb_txn_entry_size_limit`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_txn_entry_size_limit-new-in-v760) system variable to dynamically modify the value of this configuration item.

- The maximum single transaction size supported is 1 TiB. 

    - For TiDB v4.0 and later versions, You can configure it by [`performance.txn-total-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit)). The value is `100 MB` for earlier versions.
    - For TiDB v6.5.0 and later versions, this configuration is no longer recommended. For more information, see [`performance.txn-total-size-limit`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#txn-total-size-limit)).

Note that for both the size restrictions and row restrictions, you should also consider the overhead of encoding and additional keys for the transaction during the transaction execution. To achieve optimal performance, it is recommended to write one transaction every 100 ~ 500 rows.
## Auto-committed `SELECT FOR UPDATE` statements do NOT wait for locks

Currently, locks are not added to auto-committed `SELECT FOR UPDATE` statements. The following screenshot shows the effect in two separate sessions:

![The situation in TiDB](/media/develop/autocommit_selectforupdate_nowaitlock.png)

This is a known incompatibility issue with MySQL. You can solve this issue by using the explicit `BEGIN;COMMIT;` statements.
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
