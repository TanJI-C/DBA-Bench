# TiDB Lightning checkpoints overview, configuration, and storage

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-checkpoints.md`
- Source Title: `TiDB Lightning Checkpoints`
- Source Heading Path: `TiDB Lightning Checkpoints | TiDB Lightning Checkpoints > Enable and configure checkpoints | TiDB Lightning Checkpoints > Checkpoints storage`
- Source Line Ranges: `5-57`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `shared`
- Topic Tags: `checkpoints`, `import-progress`, `configuration`, `storage`, `file-driver`, `mysql-driver`, `dsn`, `checkpoint-schema`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0332_7efbef87c8`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-checkpoints.md#tidb-lightning-checkpoints`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `708c01f2482646a29501d30bb2b845fb5f7c636126cdf474277a5bb5b3896454`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-checkpoints#tidb-lightning-checkpoints
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-checkpoints.md

## Retrieval Guidance

- Use When: Use this chunk when you need checkpoint behavior, [checkpoint] configuration fields, or checkpoint storage details for TiDB Lightning import progress recovery.
- Retrieval Keywords: TiDB Lightning checkpoints, [checkpoint], enable = true, driver = "file", driver = "mysql", schema = "tidb_lightning_checkpoint", dsn, keep-after-success, checkpoint storage, local file, remote MySQL-compatible database, /tmp/CHECKPOINT_SCHEMA.pb, /tmp/tidb_lightning_checkpoint.pb, USER:PASS@tcp(HOST:PORT)/, import progress, restart from where it left off
- Follow-up Guidance: The source also states that using the target database for mysql checkpoint storage puts extra stress on the target database and can lead to communication timeout, so it strongly recommends a temporary MySQL server for storing checkpoints.
- Classification Note: This is classified as configuration because the content defines checkpoint settings such as enable, driver, schema, dsn, keep-after-success, and the supported storage backends.

## Official Source Content

# TiDB Lightning Checkpoints

Importing a large database usually takes hours or days, and if such long running processes spuriously crashes, it can be very time-wasting to redo the previously completed tasks. To solve this, TiDB Lightning uses *checkpoints* to store the import progress, so that `tidb-lightning` continues importing from where it lefts off after restarting.

This document describes how to enable, configure, store, and control *checkpoints*.
## Enable and configure checkpoints

```toml
[checkpoint]
# Whether to enable checkpoints.
# While importing data, TiDB Lightning records which tables have been imported, so
# even if TiDB Lightning or some other component crashes, you can start from a known
# good state instead of restarting from scratch.
enable = true

# Where to store the checkpoints.
#  - file:  store as a local file (requires v2.1.1 or later)
#  - mysql: store into a remote MySQL-compatible database
driver = "file"

# The schema name (database name) to store the checkpoints
# Enabled only when `driver = "mysql"`.
# schema = "tidb_lightning_checkpoint"

# The data source name (DSN) indicating the location of the checkpoint storage.
#
# For the "file" driver, the DSN is a path. If the path is not specified, Lightning would
# default to "/tmp/CHECKPOINT_SCHEMA.pb".
#
# For the "mysql" driver, the DSN is a URL in the form of "USER:PASS@tcp(HOST:PORT)/".
# If the URL is not specified, the TiDB server from the [tidb] section is used to
# store the checkpoints. You should specify a different MySQL-compatible
# database server to reduce the load of the target TiDB cluster.
#dsn = "/tmp/tidb_lightning_checkpoint.pb"

# Whether to keep the checkpoints after all data are imported. If false, the
# checkpoints are deleted. Keeping the checkpoints can aid debugging but
# might leak metadata about the data source.
# keep-after-success = false
```
## Checkpoints storage

TiDB Lightning supports two kinds of checkpoint storage: a local file or a remote MySQL-compatible database.

* With `driver = "file"`, checkpoints are stored in a local file at the path given by the `dsn` setting. Checkpoints are updated rapidly, so we highly recommend placing the checkpoint file on a drive with very high write endurance, such as a RAM disk.

* With `driver = "mysql"`, checkpoints can be saved in any databases compatible with MySQL 5.7 or later, including MariaDB and TiDB. By default, the checkpoints are saved in the target database.

While using the target database as the checkpoints storage, Lightning is importing large amounts of data at the same time. This puts extra stress on the target database and sometimes leads to communication timeout. Therefore, **it is strongly recommended to install a temporary MySQL server to store these checkpoints**. This server can be installed on the same host as `tidb-lightning` and can be uninstalled after the importer progress is completed.
