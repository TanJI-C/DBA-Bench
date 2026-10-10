# Transaction isolation levels and support boundaries

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-transaction-overview.md`
- Source Title: `Transaction overview`
- Source Heading Path: `Transaction overview > Transaction isolation levels | Transaction overview > Need help?`
- Source Line Ranges: `126-175`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `transaction isolation`, `read committed`, `repeatable read`, `snapshot isolation`, `sql-92`, `unsupported isolation levels`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0193_6aa5a7bdf4`
- Source ID: `tidb-docs-8.1:develop/dev-guide-transaction-overview.md#transaction-isolation-levels`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f37fd7edde416f8d7791b812ed38a422110606e96f35585052e4be658d55d9da`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-transaction-overview#transaction-isolation-levels
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-transaction-overview.md

## Retrieval Guidance

- Use When: Use this chunk when looking for which transaction isolation levels TiDB supports, the SQL errors for unsupported levels, or how TiDB describes repeatable read and snapshot isolation.
- Retrieval Keywords: SET TRANSACTION ISOLATION LEVEL, READ UNCOMMITTED, READ COMMITTED, REPEATABLE READ, SERIALIZABLE, ERROR 8048 (HY000), The isolation level 'READ-UNCOMMITTED' is not supported, The isolation level 'SERIALIZABLE' is not supported, tidb_skip_isolation_level_check, Snapshot Isolation, SI, ANSI Repeatable Read Isolation Level, MySQL Repeatable Read Isolation Level, ACID
- Follow-up Guidance: It also notes that TiDB implements Snapshot Isolation (SI) level consistency, called "repeatable read" for consistency with MySQL, and points to TiDB Transaction Isolation Levels for more details.
- Classification Note: This is reference content because it defines the SQL-92 isolation levels, identifies the levels TiDB supports, and shows the exact SQL behavior for supported and unsupported settings.

## Official Source Content

## Transaction isolation levels

The transaction isolation levels are the basis of database transaction processing. The "I" (Isolation) in **ACID** refers to the isolation of the transactions.

The SQL-92 standard defines four isolation levels:

- read uncommitted (`READ UNCOMMITTED`)
- read committed (`READ COMMITTED`)
- repeatable read (`REPEATABLE READ`)
- serializable (`SERIALIZABLE`).

See the table below for details:

| Isolation Level  | Dirty Write  | Dirty Read   | Fuzzy Read   | Phantom      |
| ---------------- | ------------ | ------------ | ------------ | ------------ |
| READ UNCOMMITTED | Not Possible | Possible     | Possible     | Possible     |
| READ COMMITTED   | Not Possible | Not possible | Possible     | Possible     |
| REPEATABLE READ  | Not Possible | Not possible | Not possible | Possible     |
| SERIALIZABLE     | Not Possible | Not possible | Not possible | Not possible |

TiDB supports the following isolation levels: `READ COMMITTED` and `REPEATABLE READ`:

```sql
mysql> SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
ERROR 8048 (HY000): The isolation level 'READ-UNCOMMITTED' is not supported. Set tidb_skip_isolation_level_check=1 to skip this error
mysql> SET TRANSACTION ISOLATION LEVEL READ COMMITTED;
Query OK, 0 rows affected (0.00 sec)

mysql> SET TRANSACTION ISOLATION LEVEL REPEATABLE READ;
Query OK, 0 rows affected (0.00 sec)

mysql> SET TRANSACTION ISOLATION LEVEL SERIALIZABLE;
ERROR 8048 (HY000): The isolation level 'SERIALIZABLE' is not supported. Set tidb_skip_isolation_level_check=1 to skip this error
```

TiDB implements Snapshot Isolation (SI) level consistency, also known as "repeatable read" for consistency with MySQL. This isolation level is different from [ANSI Repeatable Read Isolation Level](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#difference-between-tidb-and-ansi-repeatable-read) and [MySQL Repeatable Read Isolation Level](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#difference-between-tidb-and-mysql-repeatable-read). For more details, see [TiDB Transaction Isolation Levels](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels).
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
