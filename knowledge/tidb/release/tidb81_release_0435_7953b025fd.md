# Compatibility and behavior changes in v7.0.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.0.0.md`
- Source Title: `TiDB 7.0.0 Release Notes`
- Source Heading Path: `TiDB 7.0.0 Release Notes > Compatibility changes | TiDB 7.0.0 Release Notes > Compatibility changes > MySQL compatibility | TiDB 7.0.0 Release Notes > Compatibility changes > Behavior changes`
- Source Line Ranges: `279-328`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `sql`, `ticdc`
- Topic Tags: `upgrade`, `mysql-compatibility`, `auto-increment`, `key-partitioning`, `avro`, `schema-registry`, `load-data`, `system-variables`, `behavior-change`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0435_7953b025fd`
- Source ID: `tidb-docs-8.1:releases/release-7.0.0.md#compatibility-changes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b135bd47b399ae268d0f861b27d01deeb4c2ec65c3d04f3f8189ccab4873ceb1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.0.0#compatibility-changes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 7.0.0 upgrade compatibility changes or behavior changes involving auto-increment rules, Key partitions, TiCDC Avro `FLOAT` encoding, or `tidb_dml_batch_size` and `LOAD DATA`.
- Retrieval Keywords: TiDB 7.0.0 compatibility changes, upgrade from v6.6.0 to v7.0.0, MySQL compatibility, auto-increment column must be an index, CREATE TABLE test1, PRIMARY KEY(`k`, `id`), This feature does not affect TiCDC data replication, Key partitions, PARTITION BY KEY(store_id) PARTITIONS 4, PARTITION BY LINEAR KEY, LINEAR keyword, non-linear hash algorithm, empty partition column list, Behavior changes, TiCDC, incorrect encoding of FLOAT data in Avro, Confluent Schema Registry, compatibility policy, None, changefeed will be unable to update the schema and enter an error state, tidb_dml_batch_size, LOAD DATA statement
- Follow-up Guidance: The source notes that compatibility changes are specifically for upgrading from v6.6.0 to v7.0.0 and that upgrades from v6.5.0 or earlier might also require checking intermediate versions.
- Classification Note: This is classified as a release chunk because it summarizes official TiDB 7.0.0 compatibility and behavior changes that affect upgrades and feature semantics.

## Official Source Content

## Compatibility changes

> **Note:**
>
> This section provides compatibility changes you need to know when you upgrade from v6.6.0 to the current version (v7.0.0). If you are upgrading from v6.5.0 or earlier versions to the current version, you might also need to check the compatibility changes introduced in intermediate versions.
### MySQL compatibility

* TiDB removes the constraint that the auto-increment column must be an index [#40580](https://github.com/pingcap/tidb/issues/40580) @[tiancaiamao](https://github.com/tiancaiamao)

    Before v7.0.0, TiDB's behavior is consistent with MySQL, requiring the auto-increment column to be an index or index prefix. Starting from v7.0.0, TiDB removes the constraint that the auto-increment column must be an index or index prefix. Now you can define the primary key of a table more flexibly and use the auto-increment column to implement sorting and pagination more conveniently. This also avoids the write hotspot problem caused by the auto-increment column and improves query performance by using the table with clustered indexes. With the new release, you can create a table using the following syntax:

    ```sql
    CREATE TABLE test1 (
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `k` int(11) NOT NULL DEFAULT '0',
        `c` char(120) COLLATE utf8mb4_unicode_ci NOT NULL DEFAULT '',
        PRIMARY KEY(`k`, `id`)
    );
    ```

    This feature does not affect TiCDC data replication.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/mysql-compatibility#auto-increment-id).

* TiDB supports Key partitions, as shown in the following example:

    ```sql
    CREATE TABLE employees (
    id INT NOT NULL,
    fname VARCHAR(30),
    lname VARCHAR(30),
    hired DATE NOT NULL DEFAULT '1970-01-01',
    separated DATE DEFAULT '9999-12-31',
    job_code INT,
    store_id INT) PARTITION BY KEY(store_id) PARTITIONS 4;
    ```

    Starting from v7.0.0, TiDB supports Key partitions and can parse the MySQL `PARTITION BY LINEAR KEY` syntax. However, TiDB ignores the `LINEAR` keyword and uses a non-linear hash algorithm instead. Currently, the `KEY` partition type does not support partition statements with an empty partition column list.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/partitioned-table#key-partitioning).
### Behavior changes

* TiCDC fixes the issue of incorrect encoding of `FLOAT` data in Avro [#8490](https://github.com/pingcap/tiflow/issues/8490) @[3AceShowHand](https://github.com/3AceShowHand)

    When upgrading the TiCDC cluster to v7.0.0, if a table replicated using Avro contains the `FLOAT` data type, you need to manually adjust the compatibility policy of Confluent Schema Registry to `None` before upgrading so that the changefeed can successfully update the schema. Otherwise, after upgrading, the changefeed will be unable to update the schema and enter an error state.

* Starting from v7.0.0, [`tidb_dml_batch_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_batch_size) system variable no longer takes effect on the [`LOAD DATA` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-data).
