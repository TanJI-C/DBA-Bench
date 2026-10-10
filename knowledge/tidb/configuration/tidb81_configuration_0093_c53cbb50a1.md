# DM advanced task configuration order and global-instance settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/task-configuration-file-full.md`
- Source Title: `DM Advanced Task Configuration File`
- Source Heading Path: `DM Advanced Task Configuration File > Task configuration file template (advanced) | DM Advanced Task Configuration File > Configuration order | DM Advanced Task Configuration File > Global configuration | DM Advanced Task Configuration File > Global configuration > Basic configuration | DM Advanced Task Configuration File > Global configuration > Feature configuration set | DM Advanced Task Configuration File > Instance configuration`
- Source Line Ranges: `241-287`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `task-configuration`, `global-configuration`, `instance-configuration`, `task-mode`, `routing-rules`, `binlog-filter`, `block-allow-list`, `mydumper`, `loader`, `syncer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0093_c53cbb50a1`
- Source ID: `tidb-docs-8.1:dm/task-configuration-file-full.md#task-configuration-file-template-advanced`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bd7267dc54481fa1b4657bbf892026a99f6d92fc9a543ca0dc635bb76e0157c1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/task-configuration-file-full#task-configuration-file-template-advanced
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/task-configuration-file-full.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how a DM advanced task configuration file is structured, the required configuration order, the meaning of `task-mode`, or how instance options map to global feature configuration sets.
- Retrieval Keywords: DM advanced task configuration file, Configuration order, Global configuration, Instance configuration, task-mode, full, incremental, all, meta, Feature configuration set, routes, filters, block-allow-list, mydumpers, loaders, syncers, route-rules, filter-rules, mydumper-config-name, loader-config-name, syncer-config-name
- Follow-up Guidance: The source also points to the task configuration file template and the related DM pages for Table Routing, Binlog Event Filter, and Block & Allow Lists.
- Classification Note: This is classified as configuration because the content defines the layout, parameter groups, option meanings, and mapping between global and instance settings in a DM task configuration file.

## Official Source Content

## Configuration order

From the sample configuration file, you can see that the configuration file contains two parts: `Global configuration` and `Instance configuration`, where the `Global configuration` contains `Basic configuration` and `Feature configuration set`. The configuration order is as follows:

1. Edit the [global configuration](#global-configuration).
2. Edit the [instance configuration](#instance-configuration) based on the global configuration.
## Global configuration
### Basic configuration

Refer to the comments in the [template](#task-configuration-file-template-advanced) to see more details. Detailed explanations about `task-mode` are as follows:

- Description: the task mode that can be used to specify the data migration task to be executed.
- Value: string (`full`, `incremental`, or `all`).
    - `full` only makes a full backup of the upstream database and then imports the full data to the downstream database.
    - `incremental`: Only replicates the incremental data of the upstream database to the downstream database using the binlog. You can set the `meta` configuration item of the instance configuration to specify the starting position of incremental replication.
    - `all`: `full` + `incremental`. Makes a full backup of the upstream database, imports the full data to the downstream database, and then uses the binlog to make an incremental replication to the downstream database starting from the exported position during the full backup process (binlog position).
### Feature configuration set

Arguments in each feature configuration set are explained in the comments in the [template](#task-configuration-file-template-advanced).

| Parameter        | Description                                    |
| :------------ | :--------------------------------------- |
| `routes` | The routing mapping rule set between the upstream and downstream tables. If the names of the upstream and downstream schemas and tables are the same, this item does not need to be configured. See [Table Routing](https://docs.pingcap.com/tidb/stable/dm/dm-table-routing) for usage scenarios and sample configurations. |
| `filters` | The binlog event filter rule set of the matched table of the upstream database instance. If binlog filtering is not required, this item does not need to be configured. See [Binlog Event Filter](https://docs.pingcap.com/tidb/stable/dm/dm-binlog-event-filter) for usage scenarios and sample configurations. |
| `block-allow-list` | The filter rule set of the block allow list of the matched table of the upstream database instance. It is recommended to specify the schemas and tables that need to be migrated through this item, otherwise all schemas and tables are migrated. See [Binlog Event Filter](https://docs.pingcap.com/tidb/stable/dm/dm-binlog-event-filter) and [Block & Allow Lists](https://docs.pingcap.com/tidb/stable/dm/dm-block-allow-table-lists) for usage scenarios and sample configurations. |
| `mydumpers` | Configuration arguments of dump processing unit. If the default configuration is sufficient for your needs, this item does not need to be configured. Or you can configure `thread` only using `mydumper-thread`. |
| `loaders` | Configuration arguments of load processing unit. If the default configuration is sufficient for your needs, this item does not need to be configured. Or you can configure `pool-size` only using `loader-thread`. |
| `syncers` | Configuration arguments of sync processing unit. If the default configuration is sufficient for your needs, this item does not need to be configured. Or you can configure `worker-count` only using `syncer-thread`. |
## Instance configuration

This part defines the subtask of data migration. DM supports migrating data from one or multiple MySQL instances in the upstream to the same instance in the downstream.

For the configuration details of the above options, see the corresponding part in [Feature configuration set](#feature-configuration-set), as shown in the following table.

| Option | Corresponding part |
| :------ | :------------------ |
| `route-rules` | `routes` |
| `filter-rules` | `filters` |
| `block-allow-list` | `block-allow-list` |
| `mydumper-config-name` | `mydumpers` |
| `loader-config-name` | `loaders` |
| `syncer-config-name` | `syncers`  |
