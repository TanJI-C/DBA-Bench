# Upgrade to 6.2 PageStorage format changes

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash-upgrade-guide.md`
- Source Title: `TiFlash Upgrade Guide`
- Source Heading Path: `TiFlash Upgrade Guide > From v5.x or v6.0 to v6.2 | TiFlash Upgrade Guide > From v5.x or v6.0 to v6.2 > PageStorage | TiFlash Upgrade Guide > From v6.1 to v6.2`
- Source Line Ranges: `83-115`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `sql`, `shared`
- Topic Tags: `upgrade`, `pagestorage`, `storage-format`, `compact`, `restart`, `grafana`, `verification`, `downgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0472_630dcb9cd3`
- Source ID: `tidb-docs-8.1:tiflash-upgrade-guide.md#from-v5-x-or-v6-0-to-v6-2`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `43c8f4cdabf9fe6a3f409e59b2f11de091efd32a428c5311015faab487a1cfc2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash-upgrade-guide#from-v5-x-or-v6-0-to-v6-2
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash-upgrade-guide.md

## Retrieval Guidance

- Use When: Use this chunk when asking about PageStorage format changes when upgrading TiFlash to v6.2, including format_version, COMPACT, restart, Grafana verification, or downgrade workaround.
- Retrieval Keywords: From v5.x or v6.0 to v6.2, From v6.1 to v6.2, PageStorage, PageStorage V3, format_version = 4, ALTER TABLE <table_name> COMPACT tiflash replica;, restart the TiFlash node, TiFlash-Summary, Storage Pool, Storage Pool Run Mode, Only V2, Only V3, Mix Mode
- Follow-up Guidance: The chunk says to run ALTER TABLE <table_name> COMPACT tiflash replica; for each table containing TiFlash replicas, restart the TiFlash node, and check Grafana, and it also provides the scale-in and replicate-from-TiKV workaround for downgrading in special scenarios.
- Classification Note: This is classified as an operation chunk because it describes the v6.2 storage-format upgrade behavior, the SQL and restart steps for conversion, and the validation view in Grafana.

## Official Source Content

## From v5.x or v6.0 to v6.2

In TiDB v6.2, TiFlash upgrades its data storage format to the V3 version. Therefore, when you upgrade TiFlash from v5.x or v6.0 to v6.2, besides functional changes in [TiFlash Proxy](#tiflash-proxy) and [Dynamic pruning](#dynamic-pruning), you also need to pay attention to the functional change in PageStorage.
### PageStorage

By default, TiFlash v6.2.0 uses PageStorage V3 version [`format_version = 4`](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration#configure-the-tiflashtoml-file). This new data format significantly reduces the peak write I/O traffic. In scenarios with high update traffic and high concurrency or heavy queries, it effectively relieves excessive CPU usage caused by TiFlash data GC. Meanwhile, compared with the earlier storage format, the V3 version significantly reduces space amplification and resource consumption.

- After an upgrade to v6.2.0, as new data is written to the existing TiFlash nodes, earlier data will be gradually converted to the new format.
- However, earlier data cannot be completely converted to the new format during the upgrade, because the conversion consumes a certain amount of system overhead (services are not affected, but you still need to pay attention). After the upgrade, it is recommended that you run the [`Compact` command](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-table-compact) to convert the data to the new format. The steps are as follows:

    1. Run the following command for each table containing TiFlash replicas:

        ```sql
        ALTER TABLE <table_name> COMPACT tiflash replica;
        ```

    2. Restart the TiFlash node.

You can check whether tables still use the old data format on Grafana: **TiFlash-Summary** > **Storage Pool** > **Storage Pool Run Mode**.

- Only V2: Number of tables using PageStorage V2 (including partitions)
- Only V3: Number of tables using PageStorage V3 (including partitions)
- Mix Mode: Number of tables with data format converted from PageStorage V2 to PageStorage V3 (including partitions)

**Workaround for downgrading TiFlash in testing or other special scenarios**

You can forcibly scale in the target TiFlash node and then replicate data from TiKV again. For detailed steps, see [Scale in a TiFlash cluster](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-in-a-tiflash-cluster).
## From v6.1 to v6.2

When you upgrade TiFlash from v6.1 to v6.2, pay attention to the change in data storage format. For details, see [PageStorage](#pagestorage).
