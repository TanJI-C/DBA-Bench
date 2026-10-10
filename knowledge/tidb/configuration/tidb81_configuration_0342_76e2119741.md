# Physical import mode configuration and usage

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-physical-import-mode-usage.md`
- Source Title: `Use Physical Import Mode`
- Source Heading Path: `Use Physical Import Mode | Use Physical Import Mode > Configure and use the physical import mode`
- Source Line Ranges: `5-101`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `pd`, `tikv`
- Topic Tags: `physical-import`, `configuration-file`, `conflict-strategy`, `backend-local`, `post-restore`, `checksum`, `analyze`, `bandwidth-limit`, `sorted-kv-dir`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0342_76e2119741`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-physical-import-mode-usage.md#use-physical-import-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d3132db66468daecf8e690ef7bf5361f49a7bb1a910b23acac8754dd6a2760d8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#use-physical-import-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-physical-import-mode-usage.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiDB Lightning physical import mode configuration file example, including backend local, conflict strategy, TiDB or PD connection fields, and post-import checksum or analyze settings.
- Retrieval Keywords: Use Physical Import Mode, physical import mode, backend = "local", [conflict], strategy = "", precheck-conflict-before-import, threshold, max-record-rows, [tikv-importer], duplicate-resolution, sorted-kv-dir, store-write-bwlimit, add-index-by-sql, [tidb], status-port, pd-addr, [post-restore], checksum = "required", analyze = "optional", ADMIN CHECKSUM TABLE <table>, ANALYZE TABLE <table>
- Follow-up Guidance: The source also points to the complete configuration file and command line parameters and notes that limitations should be read before using the physical import mode.
- Classification Note: This is classified as configuration because the content is a concrete TOML configuration example and parameter description for running TiDB Lightning in physical import mode.

## Official Source Content

# Use Physical Import Mode

This document introduces how to use the [physical import mode](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode) in TiDB Lightning, including writing the configuration file, tuning performance, and configuring disk quota.

There are limitations on the physical import mode. Before using the physical import mode, make sure to read [Limitations](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode#limitations).
## Configure and use the physical import mode

You can use the following configuration file to execute data import using the physical import mode:

```toml
[lightning]
# log
level = "info"
file = "tidb-lightning.log"
max-size = 128 # MB
max-days = 28
max-backups = 14

# Checks the cluster minimum requirements before start.
check-requirements = true

[mydumper]
# The local data source directory or the URI of the external storage. For more information about the URI of the external storage, see https://docs.pingcap.com/tidb/v6.6/backup-and-restore-storages#uri-format.
data-source-dir = "/data/my_database"

[conflict]
# Starting from v7.3.0, a new version of strategy is introduced to handle conflicting data. The default value is "". Starting from v8.0.0, TiDB Lightning optimizes the conflict strategy for both physical and logical import modes.
# - "": TiDB Lightning does not detect or handle conflicting data. If the source file contains conflicting primary or unique key records, the subsequent step reports an error.
# - "error": when detecting conflicting primary or unique key records in the imported data, TiDB Lightning terminates the import and reports an error.
# - "replace": when encountering conflicting primary or unique key records, TiDB Lightning retains the latest data and overwrites the old data.
#              The conflicting data are recorded in the `lightning_task_info.conflict_error_v2` table (recording conflicting data detected by post-import conflict detection) and the `conflict_records` table (recording conflicting data detected by preprocess conflict detection) of the target TiDB cluster.
#              If you set `conflict.strategy = "replace"` in physical import mode, the conflicting data can be checked in the `lightning_task_info.conflict_view` view.
#              You can manually insert the correct records into the target table based on your application requirements. Note that the target TiKV must be v5.2.0 or later versions.
strategy = ""
# Controls whether to enable preprocess conflict detection, which checks conflicts in data before importing it to TiDB. The default value is false, indicating that TiDB Lightning only checks conflicts after the import. If you set it to true, TiDB Lightning checks conflicts both before and after the import. This parameter can be used only in the physical import mode. In scenarios where the number of conflict records is greater than 1,000,000, it is recommended to set `precheck-conflict-before-import = true` for better performance in conflict detection. In other scenarios, it is recommended to disable it.
# precheck-conflict-before-import = false
# threshold = 10000
# Starting from v8.1.0, there is no need to configure `max-record-rows` manually, because TiDB Lightning automatically assigns the value of `max-record-rows` with the value of `threshold`, regardless of the user input. `max-record-rows` will be deprecated in a future release.
# max-record-rows = 10000

[tikv-importer]
# Import mode. "local" means using the physical import mode.
backend = "local"

# The `duplicate-resolution` parameter is deprecated starting from v8.0.0 and will be removed in a future release. For more information, see <https://docs.pingcap.com/tidb/dev/tidb-lightning-physical-import-mode-usage#the-old-version-of-conflict-detection-deprecated-in-v800>.
# The method to resolve the conflicting data.
duplicate-resolution = 'remove'

# The directory of local KV sorting.
sorted-kv-dir = "./some-dir"

# Limits the bandwidth in which TiDB Lightning writes data into each TiKV
# node in the physical import mode. 0 by default, which means no limit.
# store-write-bwlimit = "128MiB"

# Specifies whether Physical Import Mode adds indexes via SQL. The default value is `false`, which means that TiDB Lightning will encode both row data and index data into KV pairs and import them into TiKV together. This mechanism is consistent with that of the historical versions. If you set it to `true`, it means that TiDB Lightning adds indexes via SQL after importing the row data.
# The benefit of adding indexes via SQL is that you can separately import data and import indexes, and import data more quickly. After the data is imported, even if the indexes fail to be added, it does not affect the consistency of the imported data.
# add-index-by-sql = false

[tidb]
# The information of the target cluster. The address of any tidb-server from the cluster.
host = "172.16.31.1"
port = 4000
user = "root"
# Configure the password to connect to TiDB. Either plaintext or Base64 encoded.
password = ""
# Required. Table schema information is fetched from TiDB via this status-port.
status-port = 10080
# Required. The address of any pd-server from the cluster. Starting from v7.6.0, TiDB supports setting multiple PD addresses.
pd-addr = "172.16.31.4:2379,56.78.90.12:3456"
# tidb-lightning imports the TiDB library, and generates some logs.
# Set the log level of the TiDB library.
log-level = "error"

[post-restore]
# Specifies whether to perform `ADMIN CHECKSUM TABLE <table>` for each table to verify data integrity after importing.
# The following options are available:
# - "required" (default): Perform admin checksum after importing. If checksum fails, TiDB Lightning will exit with failure.
# - "optional": Perform admin checksum. If checksum fails, TiDB Lightning will report a WARN log but ignore any error.
# - "off": Do not perform checksum after importing.
# Note that since v4.0.8, the default value has changed from "true" to "required".
#
# Note:
# 1. Checksum failure usually means import exception (data loss or data inconsistency), so it is recommended to always enable Checksum.
# 2. For backward compatibility, bool values "true" and "false" are also allowed for this field.
# "true" is equivalent to "required" and "false" is equivalent to "off".
checksum = "required"

# Specifies whether to perform `ANALYZE TABLE <table>` for each table after checksum is done.
# Options available for this field are the same as `checksum`. However, the default value for this field is "optional".
analyze = "optional"
```

For the complete configuration file, refer to [the configuration file and command line parameters](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).
