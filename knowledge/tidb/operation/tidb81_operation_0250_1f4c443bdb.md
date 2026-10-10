# Handling TiCDC compatibility issues across versions

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-compatibility.md`
- Source Title: `TiCDC Compatibility`
- Source Heading Path: `TiCDC Compatibility > Handle compatibility issues > Incompatibility issue caused by using the TiCDC v5.0.0-rc `cdc cli` tool to operate a v4.0.x cluster | TiCDC Compatibility > Handle compatibility issues > Compatibility notes for `sort-dir` and `data-dir` | TiCDC Compatibility > Handle compatibility issues > Compatibility with temporary tables`
- Source Line Ranges: `49-84`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tiup`, `tidb`
- Topic Tags: `compatibility-issues`, `version-mismatch`, `changefeed-removal`, `cluster-restart`, `sort-dir`, `data-dir`, `sort-engine`, `upgrade`, `temporary-tables`, `global-temporary-tables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0250_1f4c443bdb`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-compatibility.md#incompatibility-issue-caused-by-using-the-ticdc-v5-0-0-rc-cdc-cli-tool-to-operate-a-v4-0-x-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `78a66224fcbc81873a7e2996396ad1c840ab67a8f3e32090c8ccf2a88204e097`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-compatibility#incompatibility-issue-caused-by-using-the-ticdc-v5-0-0-rc-cdc-cli-tool-to-operate-a-v4-0-x-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-compatibility.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing TiCDC version mismatch behavior, `sort-dir` or `data-dir` compatibility across versions, or replication issues with global temporary tables.
- Retrieval Keywords: v5.0.0-rc cdc cli, v4.0.x cluster, replication task stuck, old value, unified sorter, tiup cdc:v4.0.9 cli changefeed remove -c xxxx --pd=xxxxx --force, tiup cluster restart <cluster_name> -R cdc, tiup cdc:v4.0.9 cli changefeed create --sink-uri=xxxx --pd=xxx, sort-dir, data-dir, sort-engine, file sorter, unified sorter, cdc server, sorter.sort-dir, /tmp/cdc_sort, /tmp/cdc_data, db sorter, global temporary tables, table definition error, v5.3.0
- Follow-up Guidance: The source says to use the `cdc` executable corresponding to the TiCDC cluster version, remove the changefeed created by the v5.0.0-rc `cdc cli`, restart the TiCDC cluster if the task is stuck, and then re-create the changefeed.
- Classification Note: The official content is operational because it describes abnormal situations from version incompatibility and provides version-specific handling notes for changefeeds, sorter directories, and temporary table replication.

## Official Source Content

### Incompatibility issue caused by using the TiCDC v5.0.0-rc `cdc cli` tool to operate a v4.0.x cluster

When using the `cdc cli` tool of TiCDC v5.0.0-rc to operate a v4.0.x TiCDC cluster, you might encounter the following abnormal situations:

- If the TiCDC cluster is v4.0.8 or an earlier version, using the v5.0.0-rc `cdc cli` tool to create a replication task might cause cluster anomalies and get the replication task stuck.

- If the TiCDC cluster is v4.0.9 or a later version, using the v5.0.0-rc `cdc cli` tool to create a replication task will cause the old value and unified sorter features to be unexpectedly enabled by default.

Solutions:

Use the `cdc` executable file corresponding to the TiCDC cluster version to perform the following operations:

1. Delete the changefeed created using the v5.0.0-rc `cdc cli` tool. For example, run the `tiup cdc:v4.0.9 cli changefeed remove -c xxxx --pd=xxxxx --force` command.
2. If the replication task is stuck, restart the TiCDC cluster. For example, run the `tiup cluster restart <cluster_name> -R cdc` command.
3. Re-create the changefeed. For example, run the `tiup cdc:v4.0.9 cli changefeed create --sink-uri=xxxx --pd=xxx` command.

> **Note:**
>
> This issue exists only when `cdc cli` is v5.0.0-rc. `cdc cli` tool of other v5.0.x versions is compatible with v4.0.x clusters.
### Compatibility notes for `sort-dir` and `data-dir`

The `sort-dir` configuration is used to specify the temporary file directory for the TiCDC sorter. Its functionalities might vary in different versions. The following table lists `sort-dir`'s compatibility changes across versions.

|  Version  |  `sort-engine` functionality  |  Note   |  Recommendation   |
|  :---  |    :---               |  :--    | :-- |
| v4.0.11 or an earlier v4.0 version, v5.0.0-rc | It is a changefeed configuration item and specifies temporary file directory for the `file` sorter and `unified` sorter. | In these versions, `file` sorter and `unified` sorter are **experimental features** and **NOT** recommended for the production environment. <br/><br/> If multiple changefeeds use the `unified` sorter as its `sort-engine`, the actual temporary file directory might be the `sort-dir` configuration of any changefeed, and the directory used for each TiCDC node might be different. | It is not recommended to use `unified` sorter in the production environment. |
| v4.0.12, v4.0.13, v5.0.0, and v5.0.1 |  It is a configuration item of changefeed or of `cdc server`. | By default, the `sort-dir` configuration of a changefeed does not take effect, and the `sort-dir` configuration of `cdc server` defaults to `/tmp/cdc_sort`. It is recommended to only configure `cdc server` in the production environment.<br /><br /> If you use TiUP to deploy TiCDC, it is recommended to use the latest TiUP version and set `sorter.sort-dir` in the TiCDC server configuration.<br /><br /> The `unified` sorter is enabled by default in v4.0.13, v5.0.0, and v5.0.1. If you want to upgrade your cluster to these versions, make sure that you have correctly configured `sorter.sort-dir` in the TiCDC server configuration. | You need to configure `sort-dir` using the `cdc server` command-line parameter (or TiUP). |
|  v4.0.14 and later v4.0 versions, v5.0.3 and later v5.0 versions, later TiDB versions | `sort-dir` is deprecated. It is recommended to configure `data-dir`.  |  You can configure `data-dir` using the latest version of TiUP. In these TiDB versions, `unified` sorter is enabled by default. Make sure that `data-dir` has been configured correctly when you upgrade your cluster. Otherwise, `/tmp/cdc_data` will be used by default as the temporary file directory. <br /><br /> If the storage capacity of the device where the directory is located is insufficient, the problem of insufficient hard disk space might occur. In this situation, the previous `sort-dir` configuration of changefeed will become invalid.| You need to configure `data-dir` using the `cdc server` command-line parameter (or TiUP).  |
| v6.0.0 and later versions | `data-dir` is used for saving the temporary files generated by TiCDC. | Starting from v6.0.0, TiCDC uses `db sorter` as the sort engine by default. `data-dir` is the disk directory for this engine.  | You need to configure `data-dir` using the `cdc server` command-line parameter (or TiUP).  |
### Compatibility with temporary tables

Since v5.3.0, TiCDC supports [global temporary tables](https://docs.pingcap.com/tidb/stable/temporary-tables#global-temporary-tables). Replicating global temporary tables to the downstream using TiCDC of a version earlier than v5.3.0 causes table definition error.

If the upstream cluster contains a global temporary table, the downstream TiDB cluster is expected to be v5.3.0 or a later version. Otherwise, an error occurs during the replication process.
