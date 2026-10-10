# DM configuration files, task creation, and core identifiers

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-config-overview.md`
- Source Title: `Data Migration Configuration File Overview`
- Source Heading Path: `Data Migration Configuration File Overview | Data Migration Configuration File Overview > DM process configuration files | Data Migration Configuration File Overview > DM migration task configuration | Data Migration Configuration File Overview > DM migration task configuration > Data migration task creation | Data Migration Configuration File Overview > DM migration task configuration > Important concepts`
- Source Line Ranges: `5-34`
- Source Scope: `shared`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `configuration-files`, `dm-master`, `dm-worker`, `source-config`, `task-config`, `task-creation`, `dmctl`, `source-id`, `identifiers`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0070_1d21d19a4c`
- Source ID: `tidb-docs-8.1:dm/dm-config-overview.md#data-migration-configuration-file-overview`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a297ae5bdb10bf3610f5364465317bc8d8ecdcadd9e374f98da3886503bdd3b4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-config-overview#data-migration-configuration-file-overview
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-config-overview.md

## Retrieval Guidance

- Use When: Use this chunk when identifying which DM configuration files define DM-master, DM-worker, upstream source, and task settings, or when looking up how task creation with dmctl relates to source.yaml and your_task.yaml.
- Retrieval Keywords: dm-master.toml, dm-worker.toml, source.yaml, your_task.yaml, dmctl, DM migration task configuration, Data migration task creation, source-id, source_id, master-addr, worker-addr, DM-master ID, DM-worker ID, Upstream Database Configuration File, Task Configuration Guide
- Follow-up Guidance: The content points to the DM-master Configuration File, DM-worker Configuration File, Upstream Database Configuration File, Task Configuration Guide, operate-data-source, and dm-create-task pages for more details.
- Classification Note: This is configuration content because it describes DM process configuration files, migration task configuration, task creation steps, and identifier fields such as source-id, master-addr, and worker-addr.

## Official Source Content

# Data Migration Configuration File Overview

This document gives an overview of configuration files of DM (Data Migration).
## DM process configuration files

- `dm-master.toml`: The configuration file of running the DM-master process, including the topology information and the logs of the DM-master. For more details, refer to [DM-master Configuration File](https://docs.pingcap.com/tidb/stable/dm/dm-master-configuration-file).
- `dm-worker.toml`: The configuration file of running the DM-worker process, including the topology information and the logs of the DM-worker. For more details, refer to [DM-worker Configuration File](https://docs.pingcap.com/tidb/stable/dm/dm-worker-configuration-file).
- `source.yaml`: The configuration of the upstream database such as MySQL and MariaDB. For more details, refer to [Upstream Database Configuration File](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file).
## DM migration task configuration
### Data migration task creation

You can take the following steps to create a data migration task:

1. [Load the data source configuration into the DM cluster using dmctl](https://docs.pingcap.com/tidb/stable/dm/dm-manage-source#operate-data-source).
2. Refer to the description in the [Task Configuration Guide](https://docs.pingcap.com/tidb/stable/dm/dm-task-configuration-guide) and create the configuration file `your_task.yaml`.
3. [Create the data migration task using dmctl](https://docs.pingcap.com/tidb/stable/dm/dm-create-task).
### Important concepts

This section shows description of some important concepts.

| Concept  | Description  | Configuration File  |
| :------ | :--------- | :------------- |
| `source-id`  | Uniquely represents a MySQL or MariaDB instance, or a migration group with the primary-secondary structure. The maximum length of `source-id` is 32. | `source_id` of `source.yaml`;<br/> `source-id` of `task.yaml` |
| DM-master ID | Uniquely represents a DM-master (by the `master-addr` parameter of `dm-master.toml`) | `master-addr` of `dm-master.toml` |
| DM-worker ID | Uniquely represents a DM-worker (by the `worker-addr` parameter of `dm-worker.toml`) | `worker-addr` of `dm-worker.toml` |
