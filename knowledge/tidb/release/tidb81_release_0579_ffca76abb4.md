# Data migration features in v8.0.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-8.0.0.md`
- Source Title: `TiDB 8.0.0 Release Notes`
- Source Heading Path: `TiDB 8.0.0 Release Notes > Feature details > Data migration`
- Source Line Ranges: `244-287`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dm`, `lightning`, `sql`, `ticdc`, `tidb`, `tikv`
- Topic Tags: `data-migration`, `protocols`, `kafka`, `encryption`, `import-into`, `from-select`, `historical-import`, `conflict-resolution`, `global-sort`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0579_ffca76abb4`
- Source ID: `tidb-docs-8.1:releases/release-8.0.0.md#data-migration`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `07fe8a27bab9f4f66c9e5b8bada543d393680c2f7629d7d29e8048c597fccee8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-8.0.0#data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-8.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 8.0.0 data migration feature additions across TiCDC, DM, IMPORT INTO, TiDB Lightning, and Global Sort.
- Retrieval Keywords: TiDB 8.0.0 Data migration, TiCDC Simple protocol, in-band schema tracking, DDL and BOOTSTRAP events, TiCDC Debezium format protocol, Kafka sink, Debezium style format, DM customized secret key, encrypt and decrypt passwords of source and target databases, IMPORT INTO ... FROM SELECT, AS OF TIMESTAMP, TiDB Lightning conflict.strategy, replace strategy, old version of conflict detection deprecated in v8.0.0, Global Sort GA, IMPORT INTO, Distributed eXecution Framework (DXF), 40 TiB
- Follow-up Guidance: The source links to documentation for TiCDC Simple protocol, TiCDC Debezium, DM customized secret key, SQL statement IMPORT INTO, TiDB Lightning configuration, and TiDB Global Sort.
- Classification Note: This is a release-notes feature summary for self-managed TiDB 8.0.0 data migration capabilities and behavior additions.

## Official Source Content

### Data migration

* TiCDC adds support for the Simple protocol [#9898](https://github.com/pingcap/tiflow/issues/9898) @[3AceShowHand](https://github.com/3AceShowHand)

    TiCDC introduces a new protocol, the Simple protocol. This protocol provides in-band schema tracking capabilities by embedding table schema information in DDL and BOOTSTRAP events.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-simple-protocol).

* TiCDC adds support for the Debezium format protocol [#1799](https://github.com/pingcap/tiflow/issues/1799) @[breezewish](https://github.com/breezewish)

    TiCDC can now publish data change events to a Kafka sink using a protocol that generates event messages in a Debezium style format. This helps to simplify the migration from MySQL to TiDB for users who are currently using Debezium to pull data from MySQL for downstream processing.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-debezium).

* DM supports using a user-provided secret key to encrypt and decrypt passwords of source and target databases [#9492](https://github.com/pingcap/tiflow/issues/9492) @[D3Hunter](https://github.com/D3Hunter)

    In earlier versions, DM uses a built-in fixed secret key with relatively low security. Starting from v8.0.0, you can upload and specify a secret key file for encrypting and decrypting passwords of upstream and downstream databases. In addition, you can replace the secret key file as needed to enhance data security.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/dm/dm-customized-secret-key).

* Supports the `IMPORT INTO ... FROM SELECT` syntax to enhance the `IMPORT INTO` functionality (experimental) [#49883](https://github.com/pingcap/tidb/issues/49883) @[D3Hunter](https://github.com/D3Hunter)

    In earlier TiDB versions, importing query results into a target table could only be done using the `INSERT INTO ... SELECT` statement, which is relatively inefficient in some large dataset scenarios. Starting from v8.0.0, TiDB enables you to use `IMPORT INTO ... FROM SELECT` to import the results of a `SELECT` query into an empty TiDB target table, which achieves up to 8 times the performance of `INSERT INTO ... SELECT` and significantly reduces the import time.

    In addition, you can use `IMPORT INTO ... FROM SELECT` to import historical data queried with [`AS OF TIMESTAMP`](https://docs.pingcap.com/tidb/stable/as-of-timestamp).

   For more information, see [documentation](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into).

* TiDB Lightning simplifies conflict resolution strategies and supports handling conflicting data using the `replace` strategy (experimental) [#51036](https://github.com/pingcap/tidb/issues/51036) @[lyzx2001](https://github.com/lyzx2001)

    In earlier versions, TiDB Lightning has [one data conflict resolution strategy](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode-usage#conflict-detection) for the logical import mode and [two data conflict resolution strategies](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#conflict-detection) for the physical import mode, which are not easy to understand and configure.

    Starting from v8.0.0, TiDB Lightning deprecates the [old version of conflict detection](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#the-old-version-of-conflict-detection-deprecated-in-v800) strategy for the physical import mode, enables you to control the conflict detection strategy for both logical and physical import modes via the [`conflict.strategy`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration) parameter, and simplifies the configuration of this parameter. In addition, in the physical import mode, the `replace` strategy now supports retaining the latest data and overwriting the old data when the import detects data with primary key or unique key conflicts.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).

* Global Sort becomes generally available (GA), improving the performance and stability of  `IMPORT INTO` significantly [#45719](https://github.com/pingcap/tidb/issues/45719) @[lance6716](https://github.com/lance6716)

    Before v7.4.0, when executing `IMPORT INTO` tasks using the [Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework), TiDB only locally sorts part of the data before importing it into TiKV due to limited local storage space. This results in significant overlap of the imported data in TiKV, requiring TiKV to perform additional compaction operations during import and affecting the TiKV performance and stability.

    With the Global Sort experimental feature introduced in v7.4.0, TiDB can temporarily store the data to be imported in an external storage (such as Amazon S3) for global sorting before importing it into TiKV, which eliminates the need for TiKV compaction operations during import. In v8.0.0, Global Sort becomes GA. This feature reduces the resource consumption of TiKV and significantly improves the performance and stability of `IMPORT INTO`. If you enable the Global Sort, each `IMPORT INTO` task supports importing data within 40 TiB.

   For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-global-sort).
