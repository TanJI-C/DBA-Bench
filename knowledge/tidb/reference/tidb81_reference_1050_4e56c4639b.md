# Repeatable Read and TiDB differences from ANSI and MySQL

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/transaction-isolation-levels.md`
- Source Title: `TiDB Transaction Isolation Levels`
- Source Heading Path: `TiDB Transaction Isolation Levels | TiDB Transaction Isolation Levels > Repeatable Read isolation level | TiDB Transaction Isolation Levels > Repeatable Read isolation level > Difference between TiDB and ANSI Repeatable Read | TiDB Transaction Isolation Levels > Repeatable Read isolation level > Difference between TiDB and MySQL Repeatable Read`
- Source Line Ranges: `5-63`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`, `sql`
- Topic Tags: `transaction-isolation`, `repeatable-read`, `snapshot-isolation`, `optimistic-transactions`, `pessimistic-transactions`, `transaction-retry`, `phantom-reads`, `write-skew`, `row-locks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1050_4e56c4639b`
- Source ID: `tidb-docs-8.1:transaction-isolation-levels.md#tidb-transaction-isolation-levels`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8f332621f78c2895587ff9d0c904b17d7368f2295b0843308a518bffbe27e6c0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/transaction-isolation-levels#tidb-transaction-isolation-levels
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/transaction-isolation-levels.md

## Retrieval Guidance

- Use When: Use this chunk when comparing TiDB `REPEATABLE-READ` with ANSI Repeatable Read or MySQL Repeatable Read, including Snapshot Isolation behavior, phantom and write skew semantics, and optimistic versus pessimistic transaction outcomes on concurrent row updates.
- Retrieval Keywords: REPEATABLE-READ, Repeatable Read isolation level, Snapshot Isolation, Difference between TiDB and ANSI Repeatable Read, Difference between TiDB and MySQL Repeatable Read, phantom reads, write skews, broad phantoms (P3), strict phantoms (A3), optimistic transaction, pessimistic transaction, for update, row lock, PD timestamp, transaction retry
- Follow-up Guidance: The source also notes that automatic retry is disabled by default starting from TiDB v3.0 and that current read (`for update` read) in pessimistic transaction mode is non-repeatable read.
- Classification Note: This is reference content because it defines TiDB Repeatable Read semantics and contrasts them with ANSI and MySQL behavior using exact isolation terminology and transaction conflict outcomes.

## Official Source Content

# TiDB Transaction Isolation Levels

Transaction isolation is one of the foundations of database transaction processing. Isolation is one of the four key properties of a transaction (commonly referred as [ACID](https://docs.pingcap.com/tidb/stable/glossary#acid)).

Transaction isolation is one of the foundations of database transaction processing. Isolation is one of the four key properties of a transaction (commonly referred as [ACID](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-glossary#acid)).

The SQL-92 standard defines four levels of transaction isolation: Read Uncommitted, Read Committed, Repeatable Read, and Serializable. See the following table for details:

| Isolation Level  | Dirty Write   | Dirty Read | Fuzzy Read     | Phantom |
| :----------- | :------------ | :------------- | :----------| :-------- |
| READ UNCOMMITTED | Not Possible | Possible     | Possible     | Possible     |
| READ COMMITTED   | Not Possible | Not possible | Possible     | Possible     |
| REPEATABLE READ  | Not Possible | Not possible | Not possible | Possible     |
| SERIALIZABLE     | Not Possible | Not possible | Not possible | Not possible |

TiDB implements Snapshot Isolation (SI) consistency, which it advertises as `REPEATABLE-READ` for compatibility with MySQL. This differs from the [ANSI Repeatable Read isolation level](#difference-between-tidb-and-ansi-repeatable-read) and the [MySQL Repeatable Read level](#difference-between-tidb-and-mysql-repeatable-read).

> **Note:**
>
> Starting from TiDB v3.0, the automatic retry of transactions is disabled by default. It is not recommended to enable the automatic retry because it might **break the transaction isolation level**. Refer to [Transaction Retry](https://docs.pingcap.com/tidb/stable/optimistic-transaction#automatic-retry) for details.
>
> Starting from TiDB v3.0.8, newly created TiDB clusters use the [pessimistic transaction mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction) by default. The current read (`for update` read) is **non-repeatable read**. Refer to [pessimistic transaction mode](https://docs.pingcap.com/tidb/stable/pessimistic-transaction) for details.
## Repeatable Read isolation level

The Repeatable Read isolation level only sees data committed before the transaction begins, and it never sees either uncommitted data or changes committed during transaction execution by concurrent transactions. However, the transaction statement does see the effects of previous updates executed within its own transaction, even though they are not yet committed.

For transactions running on different nodes, the start and commit order depends on the order that the timestamp is obtained from PD.

Transactions of the Repeatable Read isolation level cannot concurrently update a same row. When committing, if the transaction finds that the row has been updated by another transaction after it starts, then the transaction rolls back. For example:

```sql
create table t1(id int);
insert into t1 values(0);

start transaction;              |               start transaction;
select * from t1;               |               select * from t1;
update t1 set id=id+1;          |               update t1 set id=id+1; -- In pessimistic transactions, the `update` statement executed later waits for the lock until the transaction holding the lock commits or rolls back and releases the row lock.
commit;                         |
                                |               commit; -- The transaction commit fails and rolls back. Pessimistic transactions can commit successfully.
```
### Difference between TiDB and ANSI Repeatable Read

The Repeatable Read isolation level in TiDB differs from ANSI Repeatable Read isolation level, though they sharing the same name. According to the standard described in the [A Critique of ANSI SQL Isolation Levels](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-95-51.pdf) paper, TiDB implements the Snapshot Isolation level. This isolation level does not allow strict phantoms (A3) but allows broad phantoms (P3) and write skews. In contrast, the ANSI Repeatable Read isolation level allows phantom reads but does not allow write skews.
### Difference between TiDB and MySQL Repeatable Read

The Repeatable Read isolation level in TiDB differs from that in MySQL. The MySQL Repeatable Read isolation level does not check whether the current version is visible when updating, which means it can continue to update even if the row has been updated after the transaction starts. In contrast, if the row has been updated after the transaction starts, the TiDB optimistic transaction is rolled back and retried. Transaction retries in TiDB's optimistic concurrency control might fail, leading to a final failure of the transaction, while in TiDB's pessimistic concurrency control and MySQL, the updating transaction can be successful.
