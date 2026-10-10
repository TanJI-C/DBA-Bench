# Operate and inspect DM data sources

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-manage-source.md`
- Source Title: `Manage Data Source Configurations in TiDB Data Migration`
- Source Heading Path: `Manage Data Source Configurations in TiDB Data Migration > Operate data source | Manage Data Source Configurations in TiDB Data Migration > Operate data source > Flags description | Manage Data Source Configurations in TiDB Data Migration > Operate data source > Usage example | Manage Data Source Configurations in TiDB Data Migration > Operate data source > Check data source configurations`
- Source Line Ranges: `28-152`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `operate-source`, `create-source`, `stop-source`, `show-source`, `config-inspection`, `source-id`, `dmctl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0095_bddcb66ca0`
- Source ID: `tidb-docs-8.1:dm/dm-manage-source.md#operate-data-source`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0efa6ac772eb29b8463631827cb8e562fabaf9edeac5e49afc722a160e947497`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-manage-source#operate-data-source
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-manage-source.md

## Retrieval Guidance

- Use When: Use this chunk when searching for dmctl commands to create, stop, show, or inspect DM data source configurations and source-id information.
- Retrieval Keywords: operate-source, operate-source create, operate-source stop, operate-source show, config source, get-config, --print-sample-config, source.yaml, MySQL Source ID, mysql-replica-01, source is added but there is no free worker to bound
- Follow-up Guidance: If the source-id is unknown, the source says to run operate-source show first to list all data sources before using config source <source-id>.
- Classification Note: This is classified as operation because it describes dmctl operational commands for loading, listing, removing, and checking DM data source configurations.

## Official Source Content

## Operate data source

You can use the `operate-source` command to load, list or remove the data source configurations to the DM cluster.

```bash
help operate-source
```

```
`create`/`stop`/`show` upstream MySQL/MariaDB source.

Usage:
  dmctl operate-source <operate-type> [config-file ...] [--print-sample-config] [flags]

Flags:
  -h, --help                  help for operate-source
  -p, --print-sample-config   print sample config file of source

Global Flags:
  -s, --source strings   MySQL Source ID
```
### Flags description

+ `create`: Creates one or more upstream database sources. When creating multiple data sources fails, DM rolls back to the state where the command was not executed.

+ `stop`: Stops one or more upstream database sources. When stopping multiple data sources fails, some data sources might be stopped.

+ `show`: Shows the added data source and the corresponding DM-worker.

+ `config-file`: Specifies the file path of `source.yaml` and can pass multiple file paths.

+ `--print-sample-config`: Prints the sample configuration file. This parameter ignores other parameters.
### Usage example

Use the following `operate-source` command to create a source configuration file:

```bash
operate-source create ./source.yaml
```

For the configuration of `source.yaml`, refer to [Upstream Database Configuration File Introduction](https://docs.pingcap.com/tidb/stable/dm/dm-source-configuration-file).

The following is an example of the returned result:

```
{
    "result": true,
    "msg": "",
    "sources": [
        {
            "result": true,
            "msg": "",
            "source": "mysql-replica-01",
            "worker": "dm-worker-1"
        }
    ]
}
```
### Check data source configurations

> **Note:**
>
> The `config` command is only supported in DM v6.0 and later versions. For earlier versions, you must use the `get-config` command.

If you know the `source-id`, you can run `dmctl --master-addr <master-addr> config source <source-id>` to get the data source configuration.

```bash
config source mysql-replica-01
```

```
{
  "result": true,
    "msg": "",
    "cfg": "enable-gtid: false
      flavor: mysql
      source-id: mysql-replica-01
      from:
        host: 127.0.0.1
        port: 8407
        user: root
        password: '******'
}
```

If you don't know the `source-id`, you can run `dmctl --master-addr <master-addr> operate-source show` to list all data sources first.

```bash
operate-source show
```

```
{
    "result": true,
    "msg": "",
    "sources": [
        {
            "result": true,
            "msg": "source is added but there is no free worker to bound",
            "source": "mysql-replica-02",
            "worker": ""
        },
        {
            "result": true,
            "msg": "",
            "source": "mysql-replica-01",
            "worker": "dm-worker-1"
        }
    ]
}
```
