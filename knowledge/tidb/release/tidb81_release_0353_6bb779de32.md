# MySQL compatibility features and SQL behavior changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.4.0.md`
- Source Title: `TiDB 6.4.0 Release Notes`
- Source Heading Path: `TiDB 6.4.0 Release Notes > New features > MySQL compatibility`
- Source Line Ranges: `168-223`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `shared`
- Topic Tags: `mysql-compatibility`, `linear-hash-partitioning`, `auto_increment`, `auto_id_cache`, `json`, `range-selection`, `create-user`, `alter-user`, `user-attributes`, `experimental`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0353_6bb779de32`
- Source ID: `tidb-docs-8.1:releases/release-6.4.0.md#mysql-compatibility`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6766f7609852e0b17ccd944d76f98372a1b730797b6ef8346c56179bac5ef767`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.4.0#mysql-compatibility
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.4.0 SQL and MySQL compatibility changes such as Linear Hash partitioning syntax, `AUTO_INCREMENT` compatibility mode, JSON array range selection, or user comments and attributes.
- Retrieval Keywords: MySQL compatibility, Linear Hash partitioning, Hash partition, AUTO_INCREMENT, AUTO_ID_CACHE = 1, MySQL compatibility mode, JSON range selection syntax, $[0 to 2], $[last-2 to last], CREATE USER, ALTER USER, COMMENT, ATTRIBUTE, INFORMATION_SCHEMA.USER_ATTRIBUTES, USER_ATTRIBUTES
- Follow-up Guidance: The content links to user documents for Linear Hash partition handling, `AUTO_INCREMENT` MySQL compatibility mode, and the `CREATE USER`, `ALTER USER`, and `USER_ATTRIBUTES` references.
- Classification Note: This is classified as a release note for SQL because it summarizes new TiDB 6.4.0 MySQL compatibility features and SQL behavior additions.

## Official Source Content

### MySQL compatibility

* Be compatible with the Linear Hash partitioning syntax [#38450](https://github.com/pingcap/tidb/issues/38450) @[mjonss](https://github.com/mjonss)

    In the earlier version, TiDB has supported the Hash, Range, and List partitioning. Starting from v6.4.0, TiDB can also be compatible with the syntax of [MySQL Linear Hash partitioning](https://dev.mysql.com/doc/refman/5.7/en/partitioning-linear-hash.html).

    In TiDB, you can execute the existing DDL statements of your MySQL Linear Hash partitions directly, and TiDB will create the corresponding Hash partition tables (note that there is no Linear Hash partition inside TiDB). You can also execute the existing DML statements of your MySQL Linear Hash partitions directly, and TiDB will return the query result of the corresponding TiDB Hash partitions normally. This feature ensures the TiDB syntax compatibility with MySQL Linear Hash partitions and facilitates seamless migration from MySQL-based applications to TiDB.

    If the number of partitions is a power of 2, the rows in a TiDB Hash partitioned table are distributed the same as that in the MySQL Linear Hash partitioned table. Otherwise, the distribution of these rows in TiDB is different from MySQL.

    For more information, see [User document](https://docs.pingcap.com/tidb/stable/partitioned-table#how-tidb-handles-linear-hash-partitions).

* Support a high-performance and globally monotonic `AUTO_INCREMENT` (experimental) [#38442](https://github.com/pingcap/tidb/issues/38442) @[tiancaiamao](https://github.com/tiancaiamao)

    TiDB v6.4.0 introduces the `AUTO_INCREMENT` MySQL compatibility mode. This mode introduces a centralized auto-increment ID allocating service that ensures IDs monotonically increase on all TiDB instances. This feature makes it easier to sort query results by auto-increment IDs. To use the MySQL compatibility mode, you need to set `AUTO_ID_CACHE` to `1` when creating a table. The following is an example:

    ```sql
    CREATE TABLE t (a INT AUTO_INCREMENT PRIMARY KEY) AUTO_ID_CACHE = 1;
    ```

    For more information, see [User document](https://docs.pingcap.com/tidb/stable/auto-increment#mysql-compatibility-mode).

* Support range selection of array data in the JSON type [#13644](https://github.com/tikv/tikv/issues/13644) @[YangKeao](https://github.com/YangKeao)

    Starting from v6.4.0, you can use the MySQL-compatible [range selection syntax](https://dev.mysql.com/doc/refman/8.0/en/json.html#json-paths) in TiDB.

    - With the keyword `to`, you can specify the start and end positions of array elements and select elements of a continuous range in an array. With `0`, you can specify the position of the first element in an array. For example, using `$[0 to 2]`, you can select the first three elements of an array.

    - With the keyword `last`, you can specify the position of the last element in an array, which allows you to set the position from right to left. For example, using `$[last-2 to last]`, you can select the last three elements of an array.

   This feature simplifies the process of writing SQL statements, further improves the JSON type compatibility, and reduces the difficulty of migrating MySQL applications to TiDB.

* Support adding additional descriptions for database users [#38172](https://github.com/pingcap/tidb/issues/38172) @[CbcWestwolf](https://github.com/CbcWestwolf)

    In TiDB v6.4, you can use the [`CREATE USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-user) or [`ALTER USER`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-user) to add additional descriptions for database users. TiDB provides two description formats. You can add a text comment using `COMMENT` and add a set of structured attributes in JSON format using `ATTRIBUTE`.

    In addition, TiDB v6.4.0 adds the [`USER_ATTRIBUTES`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-user-attributes) table, where you can view the information of user comments and user attributes.

    ```sql
    CREATE USER 'newuser1'@'%' COMMENT 'This user is created only for test';
    CREATE USER 'newuser2'@'%' ATTRIBUTE '{"email": "user@pingcap.com"}';
    SELECT * FROM INFORMATION_SCHEMA.USER_ATTRIBUTES;
    ```

    ```sql
    +-----------+------+---------------------------------------------------+
    | USER      | HOST | ATTRIBUTE                                         |
    +-----------+------+---------------------------------------------------+
    | newuser1  | %    | {"comment": "This user is created only for test"} |
    | newuser1  | %    | {"email": "user@pingcap.com"}                     |
    +-----------+------+---------------------------------------------------+
    2 rows in set (0.00 sec)
    ```

    This feature improves TiDB compatibility with MySQL syntax and makes it easier to integrate TiDB into tools or platforms in the MySQL ecosystem.
