# UNIQUE KEY in optimistic transactions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/constraints.md`
- Source Title: `Constraints`
- Source Heading Path: `Constraints > UNIQUE KEY | Constraints > UNIQUE KEY > Optimistic transactions`
- Source Line Ranges: `140-230`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `unique-key`, `optimistic-transactions`, `constraint-checking`, `commit-phase`, `duplicate-key`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0065_66e3158ea5`
- Source ID: `tidb-docs-8.1:constraints.md#unique-key`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `357ff6556a258d96be1e23979c2ea8226a8cb3195105a52fe75f3c4e929f26e1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/constraints#unique-key
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/constraints.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about how TiDB enforces UNIQUE KEY constraints in optimistic transactions and when duplicate key errors appear.
- Retrieval Keywords: UNIQUE KEY, optimistic transactions, lazy check of constraints, commit phase, execution phase, tidb_constraint_check_in_place, tidb_constraint_check_in_place_pessimistic, BEGIN OPTIMISTIC, COMMIT, ERROR 1062 (23000): Duplicate entry 'bill' for key 'users.username', duplicate key error, users.username, SET tidb_constraint_check_in_place = ON
- Follow-up Guidance: The content also notes that enabling tidb_constraint_check_in_place checks uniqueness during statement execution and can add network communication overhead and reduce insert throughput.
- Classification Note: This is reference content because it explains documented UNIQUE KEY checking behavior and related system variables for optimistic transactions with exact SQL examples and errors.

## Official Source Content

## UNIQUE KEY

Unique constraints mean that all non-null values in a unique index and a primary key column are unique.
### Optimistic transactions

By default, for optimistic transactions, TiDB checks unique constraints [lazily](https://docs.pingcap.com/tidb/stable/transaction-overview#lazy-check-of-constraints) in the execution phase and strictly in the commit phase, which helps reduce network overhead and improve performance.

For example:

```sql
DROP TABLE IF EXISTS users;
CREATE TABLE users (
 id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
 username VARCHAR(60) NOT NULL,
 UNIQUE KEY (username)
);
INSERT INTO users (username) VALUES ('dave'), ('sarah'), ('bill');
```

With optimistic locking and `tidb_constraint_check_in_place=OFF`:

```sql
BEGIN OPTIMISTIC;
INSERT INTO users (username) VALUES ('jane'), ('chris'), ('bill');
```

```
Query OK, 3 rows affected (0.00 sec)
Records: 3  Duplicates: 0  Warnings: 0
```

```sql
INSERT INTO users (username) VALUES ('steve'),('elizabeth');
```

```
Query OK, 2 rows affected (0.00 sec)
Records: 2  Duplicates: 0  Warnings: 0
```

```sql
COMMIT;
```

```
ERROR 1062 (23000): Duplicate entry 'bill' for key 'users.username'
```

In the preceding optimistic example, the unique check was deferred until the transaction is committed. This resulted in a duplicate key error, because the value `bill` was already present.

You can disable this behavior by setting [`tidb_constraint_check_in_place`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_constraint_check_in_place) to `ON`. When `tidb_constraint_check_in_place=ON`, the unique constraint is checked when a statement is executed. Note that this variable is only applicable to optimistic transactions. For pessimistic transactions, you can control this behavior using the [`tidb_constraint_check_in_place_pessimistic`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_constraint_check_in_place_pessimistic-new-in-v630) variable.

For example:

```sql
DROP TABLE IF EXISTS users;
CREATE TABLE users (
 id INT NOT NULL PRIMARY KEY AUTO_INCREMENT,
 username VARCHAR(60) NOT NULL,
 UNIQUE KEY (username)
);
INSERT INTO users (username) VALUES ('dave'), ('sarah'), ('bill');
```

```sql
SET tidb_constraint_check_in_place = ON;
```

```
Query OK, 0 rows affected (0.00 sec)
```

```sql
BEGIN OPTIMISTIC;
```

```
Query OK, 0 rows affected (0.00 sec)
```

```sql
INSERT INTO users (username) VALUES ('jane'), ('chris'), ('bill');
```

```
ERROR 1062 (23000): Duplicate entry 'bill' for key 'users.username'
```

The first `INSERT` statement caused a duplicate key error. This causes additional network communication overhead and may reduce the throughput of insert operations.
