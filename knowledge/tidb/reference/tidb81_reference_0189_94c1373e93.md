# Sequelize compatibility limitations

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-third-party-tools-compatibility.md`
- Source Title: `Known Incompatibility Issues with Third-Party Tools`
- Source Heading Path: `Known Incompatibility Issues with Third-Party Tools > Compatibility with Sequelize | Known Incompatibility Issues with Third-Party Tools > Compatibility with Sequelize > Modification of integer primary key is not supported | Known Incompatibility Issues with Third-Party Tools > Compatibility with Sequelize > The `READ-UNCOMMITTED` and `SERIALIZABLE` isolation levels are not supported`
- Source Line Ranges: `181-216`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`, `sql`
- Topic Tags: `sequelize`, `orm`, `primary-key`, `clustered-index`, `isolation-levels`, `repeatable-read`, `read-committed`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0189_94c1373e93`
- Source ID: `tidb-docs-8.1:develop/dev-guide-third-party-tools-compatibility.md#compatibility-with-sequelize`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b94987279864fd38083ffc841fd36f68569c8e95d882b58f6afa2f0eaf2fed2a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-third-party-tools-compatibility#compatibility-with-sequelize
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-third-party-tools-compatibility.md

## Retrieval Guidance

- Use When: Use this chunk when verifying Sequelize compatibility with TiDB, especially unsupported integer primary key modification or unsupported READ-UNCOMMITTED and SERIALIZABLE isolation levels.
- Retrieval Keywords: Sequelize v6.32.1, Compatibility with Sequelize, Modification of integer primary key is not supported, Clustered Indexes, Issue #18090, READ-UNCOMMITTED, SERIALIZABLE, REPEATABLE-READ, READ-COMMITTED, tidb_skip_isolation_level_check, transaction_isolation, sequelize.queryInterface.showIndex(Model.tableName);, sequelize.options.databaseVersion, queryInterface.addColumn
- Follow-up Guidance: The content states that TiDB supports REPEATABLE-READ and READ-COMMITTED, and that setting tidb_skip_isolation_level_check to 1 makes TiDB ignore the unsupported isolation level error.
- Classification Note: This is reference content because it lists Sequelize feature compatibility boundaries and names the exact unsupported features and isolation level settings from the official documentation.

## Official Source Content

## Compatibility with Sequelize

The compatibility information described in this section is based on [Sequelize v6.32.1](https://www.npmjs.com/package/sequelize/v/6.32.1).

According to the test results, TiDB supports most of the Sequelize features ([using `MySQL` as the dialect](https://sequelize.org/docs/v6/other-topics/dialect-specific-things/#mysql)).

Unsupported features are:

- [`GEOMETRY`](https://github.com/pingcap/tidb/issues/6347) is not supported.
- Modification of integer primary key is not supported.
- `PROCEDURE` is not supported.
- The `READ-UNCOMMITTED` and `SERIALIZABLE` [isolation levels](https://docs.pingcap.com/tidb/stable/system-variables#transaction_isolation) are not supported.
- Modification of a column's `AUTO_INCREMENT` attribute is not allowed by default.
- `FULLTEXT`, `HASH`, and `SPATIAL` indexes are not supported.
- `sequelize.queryInterface.showIndex(Model.tableName);` is not supported.
- `sequelize.options.databaseVersion` is not supported.
- Adding a foreign key reference using [`queryInterface.addColumn`](https://sequelize.org/api/v6/class/src/dialects/abstract/query-interface.js~queryinterface#instance-method-addColumn) is not supported.
### Modification of integer primary key is not supported

**Description**

Modification of integer primary key is not supported. TiDB uses primary key as an index for data organization if the primary key is integer type. Refer to [Issue #18090](https://github.com/pingcap/tidb/issues/18090) and [Clustered Indexes](https://docs.pingcap.com/tidb/stable/clustered-indexes) for more details.
### The `READ-UNCOMMITTED` and `SERIALIZABLE` isolation levels are not supported

**Description**

TiDB does not support the `READ-UNCOMMITTED` and `SERIALIZABLE` isolation levels. If the isolation level is set to `READ-UNCOMMITTED` or `SERIALIZABLE`, TiDB throws an error.

**Way to avoid**

Use only the isolation level that TiDB supports: `REPEATABLE-READ` or `READ-COMMITTED`.

If you want TiDB to be compatible with other applications that set the `SERIALIZABLE` isolation level but not depend on `SERIALIZABLE`, you can set [`tidb_skip_isolation_level_check`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_skip_isolation_level_check) to `1`. In such case, TiDB ignores the unsupported isolation level error.
