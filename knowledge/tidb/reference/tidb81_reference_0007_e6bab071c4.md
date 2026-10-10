# AUTO_INCREMENT MySQL compatibility mode and restrictions

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/auto-increment.md`
- Source Title: `AUTO_INCREMENT`
- Source Heading Path: `AUTO_INCREMENT > MySQL compatibility mode | AUTO_INCREMENT > Restrictions`
- Source Line Ranges: `425-481`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `sql`
- Topic Tags: `auto_increment`, `mysql-compatibility`, `auto_id_cache`, `id-allocation`, `monotonicity`, `uniqueness`, `failover`, `rolling-upgrades`, `version-dependence`, `ddl-restrictions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0007_e6bab071c4`
- Source ID: `tidb-docs-8.1:auto-increment.md#mysql-compatibility-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `784c586a8a8f484694f698444df86edc91ad9ba909573ba780740c2d79bd67b4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/auto-increment#mysql-compatibility-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/auto-increment.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB AUTO_INCREMENT MySQL compatibility mode with AUTO_ID_CACHE 1, ID monotonicity and gaps, or restrictions on defining and altering AUTO_INCREMENT columns.
- Retrieval Keywords: AUTO_ID_CACHE 1, AUTO_ID_CACHE 0, MySQL compatibility mode, strictly increasing IDs, monotonically increasing, unique IDs, minimal gaps, failover, rolling upgrades, centralized allocating service, forceRebase, CREATE TABLE t(a int AUTO_INCREMENT key) AUTO_ID_CACHE 1, AUTO_INCREMENT restrictions, ALTER TABLE ... MODIFY/CHANGE COLUMN, ALTER TABLE ... ADD COLUMN, @@tidb_allow_remove_auto_inc, FORCE option, MAX(<auto_increment_column>), duplicate keys
- Follow-up Guidance: The source also states version-related behavior notes for AUTO_ID_CACHE 1 before v6.4.0, in v6.4.0, and starting from v8.1.0, plus restrictions for removing AUTO_INCREMENT and setting a smaller AUTO_INCREMENT value.
- Classification Note: This is a reference chunk because it defines AUTO_INCREMENT behavior, version notes, and explicit DDL restrictions and conditions in TiDB.

## Official Source Content

## MySQL compatibility mode

TiDB provides a MySQL-compatible mode for auto-increment columns that ensures strictly increasing IDs with minimal gaps. To enable this mode, set `AUTO_ID_CACHE` to `1` when creating a table:

```sql
CREATE TABLE t(a int AUTO_INCREMENT key) AUTO_ID_CACHE 1;
```

When `AUTO_ID_CACHE` is set to `1`, IDs are strictly increasing across all TiDB instances, each ID is guaranteed to be unique, and gaps between IDs are minimal compared to the default cache mode (`AUTO_ID_CACHE 0` with 30000 cached values).

For example, with `AUTO_ID_CACHE 1`, you might see a sequence as follows:

```sql
INSERT INTO t VALUES (); -- Returns ID 1
INSERT INTO t VALUES (); -- Returns ID 2
INSERT INTO t VALUES (); -- Returns ID 3
-- After failover
INSERT INTO t VALUES (); -- Might return ID 5
```

In contrast, with the default cache (`AUTO_ID_CACHE 0`), larger gaps can occur:

```sql
INSERT INTO t VALUES (); -- Returns ID 1
INSERT INTO t VALUES (); -- Returns ID 2
-- New TiDB instance allocates next batch
INSERT INTO t VALUES (); -- Returns ID 30001
```

While IDs are always increasing and without significant gaps like those seen with `AUTO_ID_CACHE 0`, small gaps in the sequence might still occur in the following scenarios. These gaps are necessary to maintain both uniqueness and the strictly increasing property of the IDs.

- During failover when the primary instance exits or crashes

    After you enable the MySQL compatibility mode, the allocated IDs are **unique** and **monotonically increasing**, and the behavior is almost the same as MySQL. Even when accessing across multiple TiDB instances, ID monotonicity is maintained. However, if the primary instance of the centralized service crashes, a few IDs might become non-continuous. This occurs because the secondary instance discards some IDs allocated by the primary instance during failover to ensure ID uniqueness.

- During rolling upgrades of TiDB nodes
- During normal concurrent transactions (similar to MySQL)

> **Note:**
>
> The behavior and performance of `AUTO_ID_CACHE 1` has evolved across TiDB versions:
>
> - Before v6.4.0, each ID allocation requires a TiKV transaction, which affects performance.
> - In v6.4.0, TiDB introduces a centralized allocating service that performs ID allocation as an in-memory operation, significantly improving performance.
> - Starting from v8.1.0, TiDB removes the automatic `forceRebase` operation during primary node exits to enable faster restarts. While this might result in additional non-consecutive IDs during failover, it prevents potential write blocking when many tables use `AUTO_ID_CACHE 1`.
## Restrictions

Currently, `AUTO_INCREMENT` has the following restrictions when used in TiDB:

- For TiDB v6.6.0 and earlier versions, the defined column must be either primary key or index prefixes.
- It must be defined on the column of `INTEGER`, `FLOAT`, or `DOUBLE` type.
- It cannot be specified on the same column with the `DEFAULT` column value.
- `ALTER TABLE` cannot be used to add or modify columns with the `AUTO_INCREMENT` attribute, including using `ALTER TABLE ... MODIFY/CHANGE COLUMN` to add the `AUTO_INCREMENT` attribute to an existing column, or using `ALTER TABLE ... ADD COLUMN` to add a column with the `AUTO_INCREMENT` attribute.
- `ALTER TABLE` can be used to remove the `AUTO_INCREMENT` attribute. However, starting from v2.1.18 and v3.0.4, TiDB uses the session variable `@@tidb_allow_remove_auto_inc` to control whether `ALTER TABLE MODIFY` or `ALTER TABLE CHANGE` can be used to remove the `AUTO_INCREMENT` attribute of a column. By default, you cannot use `ALTER TABLE MODIFY` or `ALTER TABLE CHANGE` to remove the `AUTO_INCREMENT` attribute.
- `ALTER TABLE` requires the `FORCE` option to set the `AUTO_INCREMENT` value to a smaller value.
- Setting the `AUTO_INCREMENT` to a value smaller than `MAX(<auto_increment_column>)` leads to duplicate keys because pre-existing values are not skipped.
