# Upgrade preparation checks and topology edits

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/upgrade-tidb-using-tiup.md`
- Source Title: `Upgrade TiDB Using TiUP`
- Source Heading Path: `Upgrade TiDB Using TiUP > Preparations > Step 3: Edit TiUP topology configuration file | Upgrade TiDB Using TiUP > Preparations > Step 4: Check the DDL and backup status of the cluster | Upgrade TiDB Using TiUP > Preparations > Step 5: Check the health status of the current cluster`
- Source Line Ranges: `149-199`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tikv`, `shared`
- Topic Tags: `upgrade`, `preparation`, `topology`, `configuration`, `ddl`, `backup`, `restore`, `health-check`, `regions`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0532_6419c3900a`
- Source ID: `tidb-docs-8.1:upgrade-tidb-using-tiup.md#step-3-edit-tiup-topology-configuration-file`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `350a5f1d0d46fb74925fd519b6cfd8b180236440826c63c33bb12eeba5dd1be3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup#step-3-edit-tiup-topology-configuration-file
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/upgrade-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when preparing a TiUP upgrade and needing the documented checks for topology edits, ongoing DDL or backup activity, and Region health before continuing.
- Retrieval Keywords: tiup cluster edit-config <cluster-name>, server_configs, topology.example.yaml, ADMIN SHOW DDL, ADMIN CANCEL DDL, SHOW BACKUPS, SHOW RESTORES, tiup cluster check <cluster-name> --cluster, Region status, All Regions are healthy, Regions are not fully healthy: m miss-peer, n pending-peer, Please fix unhealthy regions before other operations., Distributed eXecution Framework, DXF, smooth upgrade
- Follow-up Guidance: It also provides the exact healthy and unhealthy Region status messages output by `tiup cluster check <cluster-name> --cluster` for deciding whether to continue the upgrade.
- Classification Note: This is classified as an operation chunk because the content gives pre-upgrade TiUP commands, SQL checks, and topology editing steps to prepare a cluster upgrade.

## Official Source Content

### Step 3: Edit TiUP topology configuration file

> **Note:**
>
> Skip this step if one of the following situations applies:
>
> + You have not modified the configuration parameters of the original cluster. Or you have modified the configuration parameters using `tiup cluster` but no more modification is needed.
> + After the upgrade, you want to use v8.1.2's default parameter values for the unmodified configuration items.

1. Enter the `vi` editing mode to edit the topology file:

    ```shell
    tiup cluster edit-config <cluster-name>
    ```

2. Refer to the format of [topology](https://github.com/pingcap/tiup/blob/master/embed/examples/cluster/topology.example.yaml) configuration template and fill the parameters you want to modify in the `server_configs` section of the topology file.

3. After the modification, enter <kbd>:</kbd> + <kbd>w</kbd> + <kbd>q</kbd> to save the change and exit the editing mode. Enter <kbd>Y</kbd> to confirm the change.

> **Note:**
>
> Before you upgrade the cluster to v6.6.0, make sure that the parameters you have modified in v4.0 are compatible in v8.1.2. For details, see [TiKV Configuration File](https://docs.pingcap.com/tidb/stable/tikv-configuration-file).
### Step 4: Check the DDL and backup status of the cluster

To avoid undefined behaviors or other unexpected problems during the upgrade, it is recommended to check the following items before the upgrade.

- Cluster DDLs:

    - If you use [smooth upgrade](https://docs.pingcap.com/tidb/stable/smooth-upgrade-tidb) to upgrade TiDB to v8.1.0 or later, and the [Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework) is enabled, it is recommended to disable the DXF before upgrading. Otherwise, the indexes added during the upgrade process might be inconsistent with the data, leading to upgrade failures. 
    - If you do not use [smooth upgrade](https://docs.pingcap.com/tidb/stable/smooth-upgrade-tidb), it is recommended to use the [`ADMIN SHOW DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-show-ddl) statement to check whether ongoing DDL jobs exist. If an ongoing DDL job exists, wait for the completion of its execution or cancel it using the [`ADMIN CANCEL DDL`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-admin-cancel-ddl) statement before performing an upgrade.

- Cluster backup: It is recommended to execute the [`SHOW [BACKUPS|RESTORES]`](/sql-statements/sql-statement-show-backups.md) statement to check whether there is an ongoing backup or restore task in the cluster. If yes, wait for its completion before performing an upgrade.
### Step 5: Check the health status of the current cluster

To avoid the undefined behaviors or other issues during the upgrade, it is recommended to check the health status of Regions of the current cluster before the upgrade. To do that, you can use the `check` sub-command.

```shell
tiup cluster check <cluster-name> --cluster
```

After the command is executed, the "Region status" check result will be output.

+ If the result is "All Regions are healthy", all Regions in the current cluster are healthy and you can continue the upgrade.
+ If the result is "Regions are not fully healthy: m miss-peer, n pending-peer" with the "Please fix unhealthy regions before other operations." prompt, some Regions in the current cluster are abnormal. You need to troubleshoot the anomalies until the check result becomes "All Regions are healthy". Then you can continue the upgrade.
