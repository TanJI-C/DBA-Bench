# DM config export and import commands for sources and tasks

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-export-import-config.md`
- Source Title: `Export and Import Data Sources and Task Configuration of Clusters`
- Source Heading Path: `Export and Import Data Sources and Task Configuration of Clusters | Export and Import Data Sources and Task Configuration of Clusters > Export the data source and task configuration of clusters | Export and Import Data Sources and Task Configuration of Clusters > Export the data source and task configuration of clusters > Parameter explanation | Export and Import Data Sources and Task Configuration of Clusters > Export the data source and task configuration of clusters > Returned results | Export and Import Data Sources and Task Configuration of Clusters > import the data source and task configuration of clusters | Export and Import Data Sources and Task Configuration of Clusters > import the data source and task configuration of clusters > Parameter explanation | Export and Import Data Sources and Task Configuration of Clusters > import the data source and task configuration of clusters > Returned results`
- Source Line Ranges: `5-93`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `config`, `export`, `import`, `data-sources`, `tasks`, `dmctl`, `relay-log`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0091_8be720d9d9`
- Source ID: `tidb-docs-8.1:dm/dm-export-import-config.md#export-and-import-data-sources-and-task-configuration-of-clusters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `84105ffd1e26780c1379d2da271bbb4892b809e4fa971daf4352dae22da1b769`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-export-import-config#export-and-import-data-sources-and-task-configuration-of-clusters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-export-import-config.md

## Retrieval Guidance

- Use When: Use this chunk when looking for dmctl commands to export or import DM data source and task configuration files, including the directory option and related relay-log note.
- Retrieval Keywords: dmctl config, config export, config import, Export the configurations of sources and tasks, Import the configurations of sources and tasks, --dir directory, ./configs, MySQL Source ID, -s --source, export configs to directory succeed, start creating sources, start creating tasks, import configs from directory succeed, relay worker, start-relay, start relay log
- Follow-up Guidance: The source notes that for clusters later than v2.0.2, configuration related to relay worker is not automatically imported and the `start-relay` command can be used to manually start relay log.
- Classification Note: This is classified as an operation topic because the content documents dmctl `config export` and `config import` command usage, parameters, and returned results for DM clusters.

## Official Source Content

# Export and Import Data Sources and Task Configuration of Clusters

`config` command is used to export and import data sources and task configuration of clusters.

> **Note:**
>
> For clusters earlier than v2.0.5, you can use dmctl (>= v2.0.5 and < v8.0.0) to export and import the data source and task configuration files.

```bash
» help config
Commands to import/export config
Usage:
  dmctl config [command]
Available Commands:
  export      Export the configurations of sources and tasks.
  import      Import the configurations of sources and tasks.
Flags:
  -h, --help   help for config
Global Flags:
  -s, --source strings   MySQL Source ID.
Use "dmctl config [command] --help" for more information about a command.
```
## Export the data source and task configuration of clusters

You can use `export` command to export the data source and task configuration of clusters to specified files.

```bash
config export [--dir directory]
```
### Parameter explanation

- `dir`:
    - optional
    - specifies the file path for exporting
    - the default value is `./configs`
### Returned results

```bash
config export -d /tmp/configs
```

```
export configs to directory `/tmp/configs` succeed
```
## import the data source and task configuration of clusters

You can use `import` command to import the data source and task configuration of clusters from specified files.

```bash
config import [--dir directory]
```

> **Note:**
>
> For clusters later than v2.0.2, currently, it is not supported to automatically import the configuration related to relay worker. You can use `start-relay` command to manually [start relay log](https://docs.pingcap.com/tidb/stable/dm/relay-log#enable-and-disable-relay-log).
### Parameter explanation

- `dir`:
    - optional
    - specifies the file path for importing
    - the default value is `./configs`
### Returned results

```bash
config import -d /tmp/configs
```

```
start creating sources
start creating tasks
import configs from directory `/tmp/configs` succeed
```
