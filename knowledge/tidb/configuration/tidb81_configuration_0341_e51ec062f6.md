# Configure logical import mode

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-logical-import-mode-usage.md`
- Source Title: `Use Logical Import Mode`
- Source Heading Path: `Use Logical Import Mode > Configure and use the logical import mode`
- Source Line Ranges: `10-47`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`
- Topic Tags: `config file`, `backend`, `data source`, `target cluster`, `logging`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0341_e51ec062f6`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-logical-import-mode-usage.md#configure-and-use-the-logical-import-mode`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `542dc82be14a5b512d43b6e84b2b0eff9c4134dd091809a33e3959a41ed0f790`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode-usage#configure-and-use-the-logical-import-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-logical-import-mode-usage.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks for the example configuration file to run TiDB Lightning in logical import mode with backend tidb and target TiDB connection settings.
- Retrieval Keywords: Configure and use the logical import mode, backend = "tidb", [lightning], [mydumper], data-source-dir, [tikv-importer], [tidb], host, port, user, password, log-level, check-requirements, tidb-lightning.log
- Follow-up Guidance: For the complete configuration file, refer to TiDB Lightning Configuration.
- Classification Note: This is classified as configuration because the content is an example TOML file with settings for logging, data source, backend, and target cluster connection.

## Official Source Content

## Configure and use the logical import mode

You can use the logical import mode via the following configuration file to import data:

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

[tikv-importer]
# Import mode. "tidb" means using the logical import mode.
backend = "tidb"

[tidb]
# The information of the target cluster. The address of any tidb-server from the cluster.
host = "172.16.31.1"
port = 4000
user = "root"
# Configure the password to connect to TiDB. Either plaintext or Base64 encoded.
password = ""
# tidb-lightning imports the TiDB library, and generates some logs.
# Set the log level of the TiDB library.
log-level = "error"
```

For the complete configuration file, refer to [TiDB Lightning Configuration](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration).
