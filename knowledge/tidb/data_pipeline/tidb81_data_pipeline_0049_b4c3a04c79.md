# Load DM data sources and configure shard merge task

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-small-mysql-shards-to-tidb.md`
- Source Title: `Migrate and Merge MySQL Shards of Small Datasets to TiDB`
- Source Heading Path: `Migrate and Merge MySQL Shards of Small Datasets to TiDB > Step 1. Load data sources | Migrate and Merge MySQL Shards of Small Datasets to TiDB > Step 2. Configure the migration task`
- Source Line Ranges: `68-187`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tidb`, `tiup`
- Topic Tags: `source-loading`, `dmctl`, `gtid`, `task-configuration`, `route-rules`, `filter-rules`, `block-allow-list`, `shard-mode`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0049_b4c3a04c79`
- Source ID: `tidb-docs-8.1:migrate-small-mysql-shards-to-tidb.md#step-1-load-data-sources`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `47141a78dea96f96b0820ead7dcf1e12fe531c19234fcbd08951d7cb4c80293e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-small-mysql-shards-to-tidb#step-1-load-data-sources
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-small-mysql-shards-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the exact DM source loading command and a minimal shard merge task configuration with route rules, filter rules, block-allow-list, GTID, and shard-mode settings.
- Retrieval Keywords: Step 1. Load data sources, source1.yaml, source-id: "mysql-01", enable-gtid: true, tiup dmctl --master-addr ${advertise-addr} operate-source create source1.yaml, operate-source create, Step 2. Configure the migration task, task1.yaml, name: "shard_merge", task-mode: all, shard-mode: "pessimistic", meta-schema: "dm_meta", ignore-checking-items: ["auto_increment_ID"], target-database, mysql-instances, route-rules, filter-rules, block-allow-list, sale-route-rule, store-filter-rule, sale-filter-rule, schema-pattern: "store_*", table-pattern: "sale_*", target-schema: "store", target-table: "sale", events: ["truncate table", "drop table", "delete"], events: ["drop database"], action: Ignore, do-dbs: ["store_*"], DM Advanced Task Configuration File, Table routing, Block & Allow Table Lists, Binlog event filter
- Follow-up Guidance: The source provides follow-up references for DM Advanced Task Configuration File, Table routing, Block & Allow Table Lists, Binlog event filter, and Filter Certain Row Changes Using SQL Expressions.
- Classification Note: Classified as data_pipeline for the dm component because the content is a DM task setup example covering source registration and migration task YAML for shard merge into TiDB.

## Official Source Content

## Step 1. Load data sources

Create a new data source file called `source1.yaml`, which configures an upstream data source into DM, and add the following content:

```yaml
# Configuration.
source-id: "mysql-01" # Must be unique.
# Specifies whether DM-worker pulls binlogs with GTID (Global Transaction Identifier).
# The prerequisite is that you have already enabled GTID in the upstream MySQL.
# If you have configured the upstream database service to switch master between different nodes automatically, you must enable GTID.
enable-gtid: true
from:
  host: "${host}"           # For example: 172.16.10.81
  user: "root"
  password: "${password}"   # Plaintext passwords are supported but not recommended. It is recommended that you use dmctl encrypt to encrypt plaintext passwords.
  port: ${port}             # For example: 3306
```

Run the following command in a terminal. Use `tiup dmctl` to load the data source configuration into the DM cluster:

```shell
tiup dmctl --master-addr ${advertise-addr} operate-source create source1.yaml
```

The parameters are described as follows.

|Parameter      | Description |
|-              |-            |
|`--master-addr`         | `{advertise-addr}` of any DM-master node in the cluster that dmctl connects to. For example: 172.16.10.71:8261|
|`operate-source create` | Load data sources to the DM clusters. |

Repeat the above steps until all data sources are added to the DM cluster.
## Step 2. Configure the migration task

Create a task configuration file named `task1.yaml` and writes the following content to it:

```yaml
name: "shard_merge"               # The name of the task. Should be globally unique.
# Task mode. You can set it to the following:
# - full: Performs only full data migration (incremental replication is skipped)
# - incremental: Only performs real-time incremental replication using binlog. (full data migration is skipped)
# - all: Performs both full data migration and incremental replication. For migrating small to medium amount of data here, use this option.
task-mode: all
# Required for the MySQL shards. By default, the "pessimistic" mode is used.
# If you have a deep understanding of the principles and usage limitations of the optimistic mode, you can also use the "optimistic" mode.
# For more information, see [Merge and Migrate Data from Sharded Tables](https://docs.pingcap.com/tidb/dev/feature-shard-merge/)
shard-mode: "pessimistic"
meta-schema: "dm_meta"                        # A schema will be created in the downstream database to store the metadata
ignore-checking-items: ["auto_increment_ID"]  # In this example, there are auto-incremental primary keys upstream, so you do not need to check this item.

target-database:
  host: "${host}"                             # For example: 192.168.0.1
  port: 4000
  user: "root"
  password: "${password}"                     # Plaintext passwords are supported but not recommended. It is recommended that you use dmctl encrypt to encrypt plaintext passwords.

mysql-instances:
  -
    source-id: "mysql-01"                                    # ID of the data source, which is source-id in source1.yaml
    route-rules: ["sale-route-rule"]                         # Table route rules applied to the data source
    filter-rules: ["store-filter-rule", "sale-filter-rule"]  # Binlog event filter rules applied to the data source
    block-allow-list:  "log-bak-ignored"                     # Block & Allow Lists rules applied to the data source
  -
    source-id: "mysql-02"
    route-rules: ["sale-route-rule"]
    filter-rules: ["store-filter-rule", "sale-filter-rule"]
    block-allow-list:  "log-bak-ignored"

# Configurations for merging MySQL shards
routes:
  sale-route-rule:
    schema-pattern: "store_*"                               # Merge schemas store_01 and store_02 to the store schema in the downstream
    table-pattern: "sale_*"                                 # Merge tables sale_01 and sale_02 of schemas store_01 and store_02 to the sale table in the downstream
    target-schema: "store"
    target-table:  "sale"
    # Optional. Used for extracting the source information of sharded schemas and tables and writing the information to the user-defined columns in the downstream. If these options are configured, you need to manually create a merged table in the downstream. For details, see the following table routing setting.
    # extract-table:                                        # Extracts and writes the table name suffix without the sale_ part to the c-table column of the merged table. For example, 01 is extracted and written to the c-table column for the sharded table sale_01.
    #   table-regexp: "sale_(.*)"
    #   target-column: "c_table"
    # extract-schema:                                       # Extracts and writes the schema name suffix without the store_ part to the c_schema column of the merged table. For example, 02 is extracted and written to the c_schema column for the sharded schema store_02.
    #   schema-regexp: "store_(.*)"
    #   target-column: "c_schema"
    # extract-source:                                       # Extracts and writes the source instance information to the c_source column of the merged table. For example, mysql-01 is extracted and written to the c_source column for the data source mysql-01.
    #   source-regexp: "(.*)"
    #   target-column: "c_source"

# Filters out some DDL events.
filters:
  sale-filter-rule:           # Filter name.
    schema-pattern: "store_*" # The binlog events or DDL SQL statements of upstream MySQL instance schemas that match schema-pattern are filtered by the rules below.
    table-pattern: "sale_*"   # The binlog events or DDL SQL statements of upstream MySQL instance tables that match table-pattern are filtered by the rules below.
    events: ["truncate table", "drop table", "delete"]   # The binlog event array.
    action: Ignore                                       # The string (`Do`/`Ignore`). `Do` is the allow list. `Ignore` is the block list.
  store-filter-rule:
    schema-pattern: "store_*"
    events: ["drop database"]
    action: Ignore

# Block and allow list
block-allow-list:           # filter or only migrate all operations of some databases or some tables.
  log-bak-ignored:          # Rule name.
    do-dbs: ["store_*"]     # The allow list of the schemas to be migrated, similar to replicate-do-db in MySQL.
```

The above example is the minimum configuration to perform the migration task. For more information, see [DM Advanced Task Configuration File](https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full).

For more information on `routes`, `filters` and other configurations in the task file, see the following documents:

- [Table routing](https://docs.pingcap.com/tidb/stable/dm/dm-table-routing)
- [Block & Allow Table Lists](https://docs.pingcap.com/tidb/stable/dm/dm-block-allow-table-lists)
- [Binlog event filter](https://docs.pingcap.com/tidb/stable/filter-binlog-event)
- [Filter Certain Row Changes Using SQL Expressions](https://docs.pingcap.com/tidb/stable/filter-dml-event)
