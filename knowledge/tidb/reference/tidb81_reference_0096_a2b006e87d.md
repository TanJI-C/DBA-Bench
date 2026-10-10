# Table creation guidelines, follow-up, and support

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-create-table.md`
- Source Title: `Create a Table`
- Source Heading Path: `Create a Table > Guidelines to follow when creating a table > Guidelines to follow when selecting primary key | Create a Table > Guidelines to follow when creating a table > Guidelines to follow when selecting clustered index | Create a Table > Guidelines to follow when creating a table > Guidelines to follow when executing the `CREATE TABLE` statement | Create a Table > One more step | Create a Table > Need help?`
- Source Line Ranges: `380-425`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tiflash`
- Topic Tags: `primary-key`, `unique-index`, `clustered-index`, `write-hotspot`, `auto-random`, `auto-increment`, `schema-change`, `orm`, `secondary-indexes`, `support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0096_a2b006e87d`
- Source ID: `tidb-docs-8.1:develop/dev-guide-create-table.md#guidelines-to-follow-when-selecting-primary-key`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e2312979a3243aa04277b220f5e7e7a57f408ee0b22e676fe532cafbb42e4cc3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-table#guidelines-to-follow-when-selecting-primary-key
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-create-table.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about CREATE TABLE design guidelines in TiDB, including primary key or unique index choice, clustered index tradeoffs, write hotspot avoidance, ORM use for schema changes, or where to get follow-up help.
- Retrieval Keywords: CREATE TABLE, primary key, unique index, clustered index, non-clustered indexes, AUTO_RANDOM, AUTO_INCREMENT, SHARD_ROW_ID_BITS, PRE_SPLIT_REGIONS, _tidb_rowid, write hotspot, secondary indexes, tidb_enable_clustered_index, alter-primary-key, MySQL client, ORM, schema changes, Creating Secondary Indexes, Discord, Slack, support ticket
- Follow-up Guidance: The source points to Creating Secondary Indexes for adding secondary indexes and lists Discord, Slack, and support ticket channels for help.
- Classification Note: This is reference content because it provides official table creation guidelines, index selection considerations, schema change tool guidance, and support pointers rather than a task-specific procedure.

## Official Source Content

### Guidelines to follow when selecting primary key

- Define a **primary key** or **unique index** within the table.
- Try to select meaningful **columns** as **primary keys**.
- For performance reasons, try to avoid storing extra-wide tables. It is not recommended that the number of table fields is over `60` and that the total data size of a single row is over `64K`. It is recommended to split fields with too much data length to another table.
- It is not recommended to use complex data types.
- For the fields to be joined, ensure that the data types are consistent and avoid implicit conversion.
- Avoid defining **primary keys** on a single monotonic data column. If you use a single monotonic data column (for example, a column with the `AUTO_INCREMENT` attribute) to define the **primary key**, it might impact the write performance. If possible, use `AUTO_RANDOM` instead of `AUTO_INCREMENT`, which discards the continuous and incremental attribute of the primary key.
- If you really need to create an index on a single monotonic data column at write-intensive scenarios, instead of defining this monotonic data column as the **primary key**, you can use `AUTO_RANDOM` to create the **primary key** for that table, or use [`SHARD_ROW_ID_BITS`](https://docs.pingcap.com/tidb/stable/shard-row-id-bits) and [`PRE_SPLIT_REGIONS`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-split-region#pre_split_regions) to shard `_tidb_rowid`.
### Guidelines to follow when selecting clustered index

- Follow [guidelines for selecting primary key](#guidelines-to-follow-when-selecting-primary-key) to build **clustered indexes**.
- Compared to tables with non-clustered indexes, tables with clustered indexes offer greater performance and throughput advantages in the following scenarios:
    - When data is inserted, the clustered index reduces one write of the index data from the network.
    - When a query with an equivalent condition only involves the primary key, the clustered index reduces one read of index data from the network.
    - When a query with a range condition only involves the primary key, the clustered index reduces multiple reads of index data from the network.
    - When a query with an equivalent or range condition only involves the primary key prefix, the clustered index reduces multiple reads of index data from the network.
- On the other hand, tables with clustered indexes might have the following issues:
    - There might be write hotspot issues when you insert a large number of primary keys with close values. Follow the [guidelines to follow when selecting primary key](#guidelines-to-follow-when-selecting-primary-key).
    - The table data takes up more storage space if the data type of the primary key is larger than 64 bits, especially when there are multiple secondary indexes.

- To control the [default behavior of whether to use clustered indexes](https://docs.pingcap.com/tidb/stable/clustered-indexes#create-a-table-with-clustered-indexes), you can explicitly specify whether to use clustered indexes instead of using the system variable `@@global.tidb_enable_clustered_index` and the configuration `alter-primary-key`.
### Guidelines to follow when executing the `CREATE TABLE` statement

- It is not recommended to use a client-side Driver or ORM to perform database schema changes. It is recommended to use a [MySQL client](https://dev.mysql.com/doc/refman/8.0/en/mysql.html) or use a GUI client to perform database schema changes. In this document, the **MySQL client** is used to pass in SQL files to perform database schema changes in most scenarios.
- Follow the SQL development [specification for creating and deleting tables](https://docs.pingcap.com/tidb/stable/develop/dev-guide-sql-development-specification#create-and-delete-tables). It is recommended to wrap the build and delete statements inside the business application to add judgment logic.
## One more step

Note that all the tables that have been created in this document do not contain secondary indexes. For a guide to add secondary indexes, refer to [Creating Secondary Indexes](https://docs.pingcap.com/tidb/stable/develop/dev-guide-create-secondary-indexes).
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://tidb.support.pingcap.com/).
