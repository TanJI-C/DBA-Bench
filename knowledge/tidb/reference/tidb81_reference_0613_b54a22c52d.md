# SQL statement overview: DDL, DML, transaction, and prepared statements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-overview.md`
- Source Title: `SQL Statement Overview`
- Source Heading Path: `SQL Statement Overview | SQL Statement Overview > Schema management / Data definition statements (DDL) | SQL Statement Overview > Data manipulation statements (DML) | SQL Statement Overview > Transaction statements | SQL Statement Overview > Prepared statements`
- Source Line Ranges: `5-82`
- Source Scope: `shared`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `sql statements`, `ddl`, `dml`, `transactions`, `prepared statements`, `schema management`, `data definition`, `data manipulation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0613_b54a22c52d`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-overview.md#sql-statement-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e3a17b43f54eee8ec4ed780941840ce95b0c5292ac06e79e89463d43c3e0c5b5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-overview#sql-statement-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-overview.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs an overview of TiDB SQL statement categories and wants to find the exact statement name for schema management, data manipulation, transaction control, or prepared statements.
- Retrieval Keywords: SQL Statement Overview, Schema management / Data definition statements (DDL), Data manipulation statements (DML), Transaction statements, Prepared statements, ALTER DATABASE, ALTER TABLE, CREATE DATABASE, CREATE TABLE, CREATE INDEX, DROP TABLE, SHOW TABLES, SHOW CREATE TABLE, SHOW TABLE REGIONS, TRUNCATE, BATCH, DELETE, INSERT, REPLACE, SELECT, TABLE, UPDATE, WITH, BEGIN, COMMIT, ROLLBACK, SAVEPOINT, SET TRANSACTION, START TRANSACTION, DEALLOCATE, EXECUTE, PREPARE
- Follow-up Guidance: The source groups statements into DDL, DML, transaction statements, and prepared statements, with each entry pointing to a dedicated statement page.
- Classification Note: This is a reference chunk because it enumerates SQL statements and brief descriptions across the sql component rather than describing a task workflow.

## Official Source Content

# SQL Statement Overview

TiDB uses SQL statements that aim to follow ISO/IEC SQL standards, with extensions for MySQL and TiDB-specific statements where necessary.
## Schema management / Data definition statements (DDL)

| SQL Statement | Description |
|---------------|-------------|
| [`ALTER DATABASE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-database) | Modifies a database. |
| [`ALTER SEQUENCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-sequence) | Modifies a sequence. |
| [`ALTER TABLE ... ADD COLUMN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-column) | Adds a column to an existing table. |
| [`ALTER TABLE ... ADD INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index) | Adds an index to an existing table. |
| [`ALTER TABLE ... ALTER INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-index) | Changes an index definition. |
| [`ALTER TABLE ... CHANGE COLUMN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-change-column) | Changes a column definition. |
| [`ALTER TABLE ... COMPACT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table-compact) | Compacts a table. |
| [`ALTER TABLE ... DROP COLUMN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-column) | Drops a column from a table. |
| [`ALTER TABLE ... MODIFY COLUMN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-modify-column) | Modifies a column definition. |
| [`ALTER TABLE ... RENAME INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rename-index) | Renames an index. |
| [`ALTER TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table) | Changes a table definition. |
| [`CREATE DATABASE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-database) | Creates a new database. |
| [`CREATE INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index) | Creates a new index on a table. |
| [`CREATE SEQUENCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-sequence) | Creates a new sequence object. |
| [`CREATE TABLE LIKE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table-like) | Copies the definition of an existing table, without copying any data. |
| [`CREATE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-table) | Creates a new table. |
| [`CREATE VIEW`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-view) | Creates a new view. |
| [`DROP DATABASE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-database) | Drops an existing database. |
| [`DROP INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-index) | Drops an index from a table. |
| [`DROP SEQUENCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-sequence) | Drops a sequence object. |
| [`DROP TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-table) | Drops an existing table. |
| [`DROP VIEW`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-view) | Drops an existing view. |
| [`RENAME TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rename-table) | Renames a table. |
| [`SHOW COLUMNS FROM`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-columns-from) | Shows the columns from a table. |
| [`SHOW CREATE DATABASE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-database) | Shows the CREATE statement for a database. |
| [`SHOW CREATE SEQUENCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-sequence) | Shows the CREATE statement for a sequence. |
| [`SHOW CREATE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table) | Shows the CREATE statement for a table. |
| [`SHOW DATABASES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-databases) | Shows a list of databases that the current user has privileges to. |
| [`SHOW FIELDS FROM`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-fields-from) | Shows columns of a table. |
| [`SHOW INDEXES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-indexes) | Shows indexes of a table. |
| [`SHOW SCHEMAS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-schemas) | An alias to `SHOW DATABASES`, which shows a list of databases that the current user has privileges to. |
| [`SHOW TABLE NEXT_ROW_ID`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-table-next-rowid) | Shows the next row ID for a table. |
| [`SHOW TABLE REGIONS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-table-regions) | Shows the Region information of a table in TiDB. |
| [`SHOW TABLE STATUS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-table-status) | Shows various statistics about tables in TiDB. |
| [`SHOW TABLES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-tables) | Shows tables in a database. |
| [`TRUNCATE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-truncate) | Truncates all data from a table. |
## Data manipulation statements (DML)

| SQL Statement | Description |
|---------------|-------------|
| [`BATCH`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-batch) | Splits a DML statement into multiple statements in TiDB for execution. |
| [`DELETE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-delete) | Deletes rows from a table. |
| [`INSERT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-insert) | Inserts new rows into a table. |
| [`REPLACE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-replace) | Replaces existing rows or inserts new rows. |
| [`SELECT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select) | Reads data from a table. |
| [`TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-table) | Retrieves rows from a table. |
| [`UPDATE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-update) | Updates existing rows in a table. |
| [`WITH`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-with) | Defines common table expressions. |
## Transaction statements

| SQL Statement | Description |
|---------------|-------------|
| [`BEGIN`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-begin) | Begins a new transaction. |
| [`COMMIT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-commit) | Commits the current transaction. |
| [`ROLLBACK`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-rollback) | Rolls back the current transaction. |
| [`SAVEPOINT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-savepoint) | Sets a savepoint within a transaction. |
| [`SET TRANSACTION`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-set-transaction) | Changes the current isolation level on a `GLOBAL` or `SESSION` basis. |
| [`START TRANSACTION`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-start-transaction) | Starts a new transaction. |
## Prepared statements

| SQL Statement | Description |
|---------------|-------------|
| [`DEALLOCATE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-deallocate) | Deallocates a prepared statement, freeing associated resources. |
| [`EXECUTE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-execute) | Executes a prepared statement with specific parameter values. |
| [`PREPARE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-prepare) | Creates a prepared statement with placeholders. |
