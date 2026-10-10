# SET TRANSACTION syntax, examples, and compatibility

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-set-transaction.md`
- Source Title: `SET TRANSACTION | TiDB SQL Statement Reference`
- Source Heading Path: `SET TRANSACTION | SET TRANSACTION > Synopsis | SET TRANSACTION > Examples | SET TRANSACTION > MySQL compatibility | SET TRANSACTION > See also`
- Source Line Ranges: `5-73`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `set transaction`, `transaction isolation`, `session scope`, `global scope`, `read only`, `read write`, `mysql compatibility`, `sql syntax`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0638_bccd631c4f`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-set-transaction.md#set-transaction`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7796afad71e027094180d323359bace7e269c530c98442fd936cd02b65c5d62f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-transaction#set-transaction
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-set-transaction.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about the SET TRANSACTION statement syntax, changing transaction isolation at GLOBAL or SESSION scope, or MySQL compatibility of transaction isolation and read-only/read-write clauses in TiDB.
- Retrieval Keywords: SET TRANSACTION, SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED, SET transaction_isolation, transaction_isolation, GLOBAL TRANSACTION, SESSION TRANSACTION, READ ONLY, READ WRITE, AS OF TIMESTAMP, REPEATABLE-READ, READ-COMMITTED, READ-UNCOMMITTED, SERIALIZABLE, SHOW SESSION VARIABLES LIKE 'transaction_isolation', MySQL compatibility, snapshot isolation
- Follow-up Guidance: See also `SET [GLOBAL|SESSION] <variable>` and Isolation Levels for related details.
- Classification Note: This is reference content because it provides SQL syntax, EBNF, examples, and compatibility notes for `SET TRANSACTION`.

## Official Source Content

# SET TRANSACTION

The `SET TRANSACTION` statement can be used to change the current isolation level on a `GLOBAL` or `SESSION` basis. This syntax is an alternative to `SET transaction_isolation='new-value'` and is included for compatibility with both MySQL, and the SQL standards.
## Synopsis

```ebnf+diagram
SetStmt ::=
    'SET' ( VariableAssignmentList |
    'PASSWORD' ('FOR' Username)? '=' PasswordOpt |
    ( 'GLOBAL'| 'SESSION' )? 'TRANSACTION' TransactionChars |
    'CONFIG' ( Identifier | stringLit) ConfigItemName EqOrAssignmentEq SetExpr )

TransactionChars ::=
    ( 'ISOLATION' 'LEVEL' IsolationLevel | 'READ' 'WRITE' | 'READ' 'ONLY' AsOfClause? )

IsolationLevel ::=
    ( 'REPEATABLE' 'READ' | 'READ' ( 'COMMITTED' | 'UNCOMMITTED' ) | 'SERIALIZABLE' )

AsOfClause ::=
    ( 'AS' 'OF' 'TIMESTAMP' Expression)
```
## Examples

```sql
mysql> SHOW SESSION VARIABLES LIKE 'transaction_isolation';
+-----------------------+-----------------+
| Variable_name         | Value           |
+-----------------------+-----------------+
| transaction_isolation | REPEATABLE-READ |
+-----------------------+-----------------+
1 row in set (0.00 sec)

mysql> SET SESSION TRANSACTION ISOLATION LEVEL READ COMMITTED;
Query OK, 0 rows affected (0.00 sec)

mysql> SHOW SESSION VARIABLES LIKE 'transaction_isolation';
+-----------------------+----------------+
| Variable_name         | Value          |
+-----------------------+----------------+
| transaction_isolation | READ-COMMITTED |
+-----------------------+----------------+
1 row in set (0.01 sec)

mysql> SET SESSION transaction_isolation = 'REPEATABLE-READ';
Query OK, 0 rows affected (0.00 sec)

mysql> SHOW SESSION VARIABLES LIKE 'transaction_isolation';
+-----------------------+-----------------+
| Variable_name         | Value           |
+-----------------------+-----------------+
| transaction_isolation | REPEATABLE-READ |
+-----------------------+-----------------+
1 row in set (0.00 sec)
```
## MySQL compatibility

* TiDB supports the ability to set a transaction as read-only in syntax only.
* The isolation levels `READ-UNCOMMITTED` and `SERIALIZABLE` are not supported.
* The `REPEATABLE-READ` isolation level is achieved through using the snapshot isolation technology, which is partly compatible with MySQL.
* In pessimistic transactions, TiDB supports two isolation levels compatible with MySQL: `REPEATABLE-READ` and `READ-COMMITTED`. For a detailed description, see [Isolation Levels](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels).
## See also

* [`SET [GLOBAL|SESSION] <variable>`](/sql-statements/sql-statement-set-variable.md)
* [Isolation Levels](https://docs.pingcap.com/tidb/stable/transaction-isolation-levels)
