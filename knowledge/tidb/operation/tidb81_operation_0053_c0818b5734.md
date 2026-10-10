# Execute table creation script and follow table design guidelines

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-create-table.md`
- Source Title: `Create a Table`
- Source Heading Path: `Create a Table > Execute the `CREATE TABLE` statement | Create a Table > Guidelines to follow when creating a table | Create a Table > Guidelines to follow when creating a table > Guidelines to follow when naming a table | Create a Table > Guidelines to follow when creating a table > Guidelines to follow when defining columns`
- Source Line Ranges: `325-379`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `create-table`, `initialization`, `show-tables`, `naming`, `columns`, `schema-design`, `constraints`, `clustered-index`, `primary-key`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0053_c0818b5734`
- Source ID: `tidb-docs-8.1:develop/dev-guide-create-table.md#execute-the-create-table-statement`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f45b970999d32b64f9265f6459f821a57fd18e9e0ec06c071a7f20bf9a912317`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table#execute-the-create-table-statement
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-create-table.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the database initialization command, `SHOW TABLES IN `bookshop`;`, or official table and column naming and definition guidelines during table creation.
- Retrieval Keywords: init.sql, mysql -u root -h {host} -P {port} -p {password} < init.sql, SHOW TABLES IN `bookshop`;, Tables_in_bookshop, fully-qualified table name, USE {databasename};, current database in your SQL session, table naming convention, column naming convention, clustered indexes, primary key columns, add column constraints, authors, book_authors, books, orders, ratings, users
- Follow-up Guidance: The source says that if you do not specify the database name, TiDB uses the current database in your SQL session, and if you do not use `USE {databasename};` to specify the database in your SQL session, TiDB returns an error.
- Classification Note: This is operation content because it includes the command to execute the `CREATE TABLE` initialization script, the `SHOW TABLES` statement, and procedural table design guidelines.

## Official Source Content

## Execute the `CREATE TABLE` statement

After creating all the tables as above rules, our [database initialization](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#database-initialization-script-dbinitsql) script should look like this. If you need to see the table information in detail, please refer to [Description of the Tables](https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#description-of-the-tables).

To name the database initialization script `init.sql` and save it, you can execute the following statement to initialize the database.

```shell
mysql
    -u root \
    -h {host} \
    -P {port} \
    -p {password} \
    < init.sql
```

To view all tables under the `bookshop` database, use the [`SHOW TABLES`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-tables#show-full-tables) statement.

```sql
SHOW TABLES IN `bookshop`;
```

Running results:

```
+--------------------+
| Tables_in_bookshop |
+--------------------+
| authors            |
| book_authors       |
| books              |
| orders             |
| ratings            |
| users              |
+--------------------+
```
## Guidelines to follow when creating a table

This section provides guidelines you need to follow when creating a table.
### Guidelines to follow when naming a table

- Use a **fully-qualified** table name (for example, `CREATE TABLE {database_name}. {table_name}`). If you do not specify the database name, TiDB uses the current database in your **SQL session**. If you do not use `USE {databasename};` to specify the database in your SQL session, TiDB returns an error.
- Use meaningful table names. For example, if you need to create a user table, you can use names: `user`, `t_user`,`users`, or follow your company or organization's naming convention. If your company or organization does not have a naming convention, you can refer to the [table naming convention](https://docs.pingcap.com/tidb/stable/develop/dev-guide-object-naming-guidelines#table-naming-convention). Do not use such table names as: `t1`, `table1`.
- Multiple words are separated by an underscore, and it is recommended that the name is no more than 32 characters.
- Create a separate `DATABASE` for tables of different business modules and add comments accordingly.
### Guidelines to follow when defining columns

- Check the [data types](https://docs.pingcap.com/tidb/stable/data-type-overview) supported by columns and organize your data according to the data type restrictions. Select the appropriate type for the data you plan to store in the column.
- Check the [guidelines to follow](#guidelines-to-follow-when-selecting-primary-key) for selecting primary keys and decide whether to use primary key columns.
- Check the [guidelines to follow](#guidelines-to-follow-when-selecting-clustered-index) for selecting clustered indexes and decide whether to specify **clustered indexes**.
- Check [adding column constraints](#add-column-constraints) and decide whether to add constraints to the columns.
- Use meaningful column names. It is recommended that you follow your company or organization's table naming convention. If your company or organization does not have a corresponding naming convention, refer to the [column naming convention](https://docs.pingcap.com/tidb/stable/develop/dev-guide-object-naming-guidelines#column-naming-convention).
