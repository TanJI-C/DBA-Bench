# DM compatibility levels and source/target database matrix

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-compatibility-catalog.md`
- Source Title: `Compatibility Catalog of TiDB Data Migration`
- Source Heading Path: `Compatibility Catalog of TiDB Data Migration | Compatibility Catalog of TiDB Data Migration > Data sources | Compatibility Catalog of TiDB Data Migration > Target databases`
- Source Line Ranges: `5-46`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `sql`
- Topic Tags: `compatibility`, `data-sources`, `target-databases`, `version-matrix`, `migration`, `gtid`, `relay-log`, `warnings`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0214_374f3150ad`
- Source ID: `tidb-docs-8.1:dm/dm-compatibility-catalog.md#compatibility-catalog-of-tidb-data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5ca6f03af42480f3d7f933c84f1197977e97681ff0fd6b6c3b802cec90e0f447`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-compatibility-catalog#compatibility-catalog-of-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-compatibility-catalog.md

## Retrieval Guidance

- Use When: Use this chunk when checking DM compatibility levels for specific source databases or target databases, including MySQL, MariaDB, and TiDB version matrix details.
- Retrieval Keywords: DM compatibility catalog, Data sources, Target databases, Generally available (GA), Experimental, Not tested, Incompatible, MySQL ≤ 5.5, MySQL 5.6, MySQL 5.7, MySQL 8.0, Transaction_payload_event, MariaDB < 10.1.2, MariaDB 10.1.2 ~ 10.5.10, MariaDB > 10.5.10, TiDB 8.x, TiDB 7.x, TiDB 6.x, TiDB 5.4, TiDB 5.3, TiDB 5.2, TiDB 5.1, TiDB 5.0, TiDB 4.x, TiDB 3.x, GTID replication, relay log, DM v5.3.0
- Follow-up Guidance: The chunk also includes a warning that DM v5.3.0 is not recommended because when GTID replication is enabled but relay log is not enabled, data replication fails with low probability.
- Classification Note: This is reference content because it provides an official compatibility matrix and definitions of compatibility levels for DM source and target databases.

## Official Source Content

# Compatibility Catalog of TiDB Data Migration

DM supports migrating data from different sources to TiDB clusters. Based on the data source type, DM has four compatibility levels:

- **Generally available (GA)**: The application scenario has been verified and passed the GA test.
- **Experimental**: Although the application scenario has been verified, the test does not cover all scenarios or involves only a limited number of users. The application scenario might encounter problems occasionally.
- **Not tested**: DM is expected to be always compatible with MySQL during iteration. However, due to resource constraints, not all MySQL forks are tested with DM. Therefore, the *not tested* source or target is technically compatible with DM, but is not fully tested, which means you need to verify its compatibility before you use.
- **Incompatible**: DM is proved to be incompatible with the data source and the application is not recommended for use in production environments.
## Data sources

|Data source|Compatibility level|Remarks|
|-|-|-|
|MySQL ≤ 5.5|Not tested||
|MySQL 5.6|GA||
|MySQL 5.7|GA||
|MySQL 8.0|GA|Does not support binlog transaction compression [Transaction_payload_event](https://dev.mysql.com/doc/refman/8.0/en/binary-log-transaction-compression.html)|
|MariaDB < 10.1.2|Incompatible|Incompatible with binlog of the time type|
|MariaDB 10.1.2 ~ 10.5.10|Experimental||
|MariaDB > 10.5.10|Incompatible|Permission errors reported in the check procedure|
## Target databases

> **Warning:**
>
> DM v5.3.0 is not recommended. If you have enabled GTID replication but do not enable relay log in DM v5.3.0, data replication fails with low probability.

|Target database|Compatibility level|DM version|
|-|-|-|
|TiDB 8.x|GA|≥ 5.3.1|
|TiDB 7.x|GA|≥ 5.3.1|
|TiDB 6.x|GA|≥ 5.3.1|
|TiDB 5.4|GA|≥ 5.3.1|
|TiDB 5.3|GA|≥ 5.3.1|
|TiDB 5.2|GA|≥ 2.0.7, recommended: 5.4|
|TiDB 5.1|GA|≥ 2.0.4, recommended: 5.4|
|TiDB 5.0|GA|≥ 2.0.4, recommended: 5.4|
|TiDB 4.x|GA|≥ 2.0.1, recommended: 2.0.7|
|TiDB 3.x|GA|≥ 2.0.1, recommended: 2.0.7|
|MySQL|Experimental||
|MariaDB|Experimental||
