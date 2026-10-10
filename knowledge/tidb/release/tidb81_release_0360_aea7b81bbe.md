# 6.4.0 bug fixes across TiDB, TiKV, PD, TiFlash, and tools

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.4.0.md`
- Source Title: `TiDB 6.4.0 Release Notes`
- Source Heading Path: `TiDB 6.4.0 Release Notes > Bug fixes`
- Source Line Ranges: `390-466`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `dashboard`, `br`, `ticdc`, `dm`, `lightning`, `dumpling`
- Topic Tags: `bug fixes`, `sql correctness`, `permissions`, `monitoring`, `system variables`, `performance`, `flashback`, `leader switchover`, `oom`, `restoration`, `log backup`, `kafka sink`, `redo logs`, `checkpoint`, `webui`, `data race`, `deadlock`, `precheck`, `tls`, `parquet`, `export`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0360_aea7b81bbe`
- Source ID: `tidb-docs-8.1:releases/release-6.4.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e806274ae8c55b35f359838ffcb6b4760198f75c957ac303b3dfd3c81f504bd0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.4.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.4.0 bug fix details across TiDB, TiKV, PD, TiFlash, and tools for specific issues, components, tables, variables, metrics, or operational phrases mentioned in the release notes.
- Retrieval Keywords: TiDB 6.4.0 bug fixes, INFORMATION_SCHEMA.TIKV_REGION_STATUS, mysql.tables_priv, grantor, transaction region num, tidb_constraint_check_in_place_pessimistic, SESSION, common table expressions, GROUP_CONCAT, ORDER BY, Join Reorder, tikv_gc_compaction_filtered, delete_files_in_range, FLASHBACK, leader switchover, PageStorage GC, WAL files, Top SQL, NgMonitoring, PD leader switch, log backup, sasl-password, changefeed query, redo logs, Kafka Sink V2, checkpoint ts, DM WebUI, allow-list, secondsBehindMaster, query-status, INFORMATION_SCHEMA, TLS configuration, Apache Parquet, binary encoding format, Dumpling consistency lock
- Follow-up Guidance: Use the issue descriptions in this chunk to match the affected component and the exact identifier such as a table name, system variable, metric, command output field, or feature phrase.
- Classification Note: This is a release-note bug-fix summary for TiDB 6.4.0 covering multiple components and tools, so it is classified as a release chunk.

## Official Source Content

## Bug fixes

+ TiDB

    - Fix the potential issue of index inconsistency that occurs after you create a new index [#38165](https://github.com/pingcap/tidb/issues/38165) @[tangenta](https://github.com/tangenta)
    - Fix a permission issue of the `INFORMATION_SCHEMA.TIKV_REGION_STATUS` table [#38407](https://github.com/pingcap/tidb/issues/38407) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Fix the issue that the `grantor` field is missing in the `mysql.tables_priv` table [#38293](https://github.com/pingcap/tidb/issues/38293) @[CbcWestwolf](https://github.com/CbcWestwolf)
    - Fix the issue that the join result of common table expressions might be wrong [#38170](https://github.com/pingcap/tidb/issues/38170) @[wjhuang2016](https://github.com/wjhuang2016)
    - Fix the issue that the union result of common table expressions might be wrong [#37928](https://github.com/pingcap/tidb/issues/37928) @[YangKeao](https://github.com/YangKeao)
    - Fix the issue that the information in the **transaction region num** monitoring panel is incorrect [#38139](https://github.com/pingcap/tidb/issues/38139) @[jackysp](https://github.com/jackysp)
    - Fix the issue that the system variable [`tidb_constraint_check_in_place_pessimistic`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_constraint_check_in_place_pessimistic-new-in-v630) might affect internal transactions. The variable scope is modified to SESSION. [#38766](https://github.com/pingcap/tidb/issues/38766) @[ekexium](https://github.com/ekexium)
    - Fix the issue that conditions in a query are mistakenly pushed down to projections [#35623](https://github.com/pingcap/tidb/issues/35623) @[Reminiscent](https://github.com/Reminiscent)
    - Fix the issue that the wrong `isNullRejected` check results for `AND` and `OR` cause wrong query results [#38304]( https://github.com/pingcap/tidb/issues/38304) @[Yisaer](https://github.com/Yisaer)
    - Fix the issue that `ORDER BY` in `GROUP_CONCAT` is not considered when the outer join is eliminated, which causes wrong query results [#18216](https://github.com/pingcap/tidb/issues/18216) @[winoros](https://github.com/winoros)
    - Fix the issue of the wrong query result that occurs when the mistakenly pushed-down conditions are discarded by Join Reorder [#38736](https://github.com/pingcap/tidb/issues/38736) @[winoros](https://github.com/winoros)

+ TiKV

    - Fix the issue that TiDB fails to start on Gitpod when there are multiple `cgroup` and `mountinfo` records [#13660](https://github.com/tikv/tikv/issues/13660) @[tabokie](https://github.com/tabokie)
    - Fix the wrong expression of a TiKV metric `tikv_gc_compaction_filtered` [#13537](https://github.com/tikv/tikv/issues/13537) @[Defined2014](https://github.com/Defined2014)
    - Fix the performance issue caused by the abnormal `delete_files_in_range` [#13534](https://github.com/tikv/tikv/issues/13534) @[tabokie](https://github.com/tabokie)
    - Fix abnormal Region competition caused by expired lease during snapshot acquisition [#13553](https://github.com/tikv/tikv/issues/13553) @[SpadeA-Tang](https://github.com/SpadeA-Tang)
    - Fix errors occurred when `FLASHBACK` fails in the first batch [#13672](https://github.com/tikv/tikv/issues/13672) [#13704](https://github.com/tikv/tikv/issues/13704) [#13723](https://github.com/tikv/tikv/issues/13723) @[HuSharp](https://github.com/HuSharp)

+ PD

    - Fix inaccurate Stream timeout and accelerate leader switchover [#5207](https://github.com/tikv/pd/issues/5207) @[CabinfeverB](https://github.com/CabinfeverB)

+ TiFlash

    - Fix the OOM issue due to oversized WAL files that occurs when PageStorage GC does not clear the Page deletion marker properly [#6163](https://github.com/pingcap/tiflash/issues/6163) @[JaySon-Huang](https://github.com/JaySon-Huang)

+ Tools

    + TiDB Dashboard

        - Fix the TiDB OOM issue when querying execution plans of certain complex SQL statements [#1386](https://github.com/pingcap/tidb-dashboard/issues/1386) @[baurine](https://github.com/baurine)
        - Fix the issue that the Top SQL switch might not take effect when NgMonitoring loses the connection to the PD nodes [#164](https://github.com/pingcap/ng-monitoring/issues/164) @[zhongzc](https://github.com/zhongzc)

    + Backup & Restore (BR)

        - Fix the restoration failure issue caused by PD leader switch during the restoration process [#36910](https://github.com/pingcap/tidb/issues/36910) @[MoCuishle28](https://github.com/MoCuishle28)
        - Fix the issue that the log backup task cannot be paused [#38250](https://github.com/pingcap/tidb/issues/38250) @[joccau](https://github.com/joccau)
        - Fix the issue that when BR deletes log backup data, it mistakenly deletes data that should not be deleted [#38939](https://github.com/pingcap/tidb/issues/38939) @[Leavrth](https://github.com/leavrth)
        - Fix the issue that BR fails to delete data when deleting the log backup data stored in Azure Blob Storage or Google Cloud Storage for the first time [#38229](https://github.com/pingcap/tidb/issues/38229) @[Leavrth](https://github.com/leavrth)

    + TiCDC

        - Fix the issue that `sasl-password` in the `changefeed query` result is not masked [#7182](https://github.com/pingcap/tiflow/issues/7182) @[dveeden](https://github.com/dveeden)
        - Fix the issue that TiCDC might become unavailable when too many operations in an etcd transaction are committed [#7131](https://github.com/pingcap/tiflow/issues/7131) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that redo logs might be deleted incorrectly [#6413](https://github.com/pingcap/tiflow/issues/6413) @[asddongmen](https://github.com/asddongmen)
        - Fix performance regression when replicating wide tables in Kafka Sink V2 [#7344](https://github.com/pingcap/tiflow/issues/7344) @[hi-rustin](https://github.com/Rustin170506)
        - Fix the issue that checkpoint ts might be advanced incorrectly [#7274](https://github.com/pingcap/tiflow/issues/7274) @[hi-rustin](https://github.com/Rustin170506)
        - Fix the issue that too many logs are printed due to improper log level of the mounter module [#7235](https://github.com/pingcap/tiflow/issues/7235) @[hi-rustin](https://github.com/Rustin170506)
        - Fix the issue that a TiCDC cluster might have two owners [#4051](https://github.com/pingcap/tiflow/issues/4051) @[asddongmen](https://github.com/asddongmen)

    + TiDB Data Migration (DM)
        - Fix the issue that DM WebUI generates the wrong `allow-list` parameter [#7096](https://github.com/pingcap/tiflow/issues/7096) @[zoubingwu](https://github.com/zoubingwu)
        - Fix the issue that a DM-worker has a certain probability of triggering data race when it starts or stops [#6401](https://github.com/pingcap/tiflow/issues/6401) @[liumengya94](https://github.com/liumengya94)
        - Fix the issue that when DM replicates an `UPDATE` or `DELETE` statement but the corresponding row data does not exist, DM silently ignores the event [#6383](https://github.com/pingcap/tiflow/issues/6383) @[GMHDBJD](https://github.com/GMHDBJD)
        - Fix the issue that the `secondsBehindMaster` field is not displayed after you run the `query-status` command [#7189](https://github.com/pingcap/tiflow/issues/7189) @[GMHDBJD](https://github.com/GMHDBJD)
        - Fix the issue that updating the checkpoint may trigger a large transaction [#5010](https://github.com/pingcap/tiflow/issues/5010) @[lance6716](https://github.com/lance6716)
        - Fix the issue that in full task mode, when a task enters the sync stage and fails immediately, DM may lose upstream table schema information [#7159](https://github.com/pingcap/tiflow/issues/7159) @[lance6716](https://github.com/lance6716)
        - Fix the issue that deadlock may be triggered when the consistency check is enabled [#7241](https://github.com/pingcap/tiflow/issues/7241) @[buchuitoudegou](https://github.com/buchuitoudegou)
        - Fix the issue that task precheck requires the `SELECT` privilege for the `INFORMATION_SCHEMA` table [#7317](https://github.com/pingcap/tiflow/issues/7317) @[lance6716](https://github.com/lance6716)
        - Fix the issue that an empty TLS configuration causes an error [#7384](https://github.com/pingcap/tiflow/issues/7384) @[liumengya94](https://github.com/liumengya94)

    + TiDB Lightning

        - Fix the import performance degradation when importing the Apache Parquet files to the target tables that contain the string type columns in the`binary` encoding format [#38351](https://github.com/pingcap/tidb/issues/38351) @[dsdashun](https://github.com/dsdashun)

    + TiDB Dumpling

        - Fix the issue that Dumpling might time out when exporting a lot of tables [#36549](https://github.com/pingcap/tidb/issues/36549) @[lance6716](https://github.com/lance6716)
        - Fix lock errors reported when consistency lock is enabled but the upstream has no target table [#38683](https://github.com/pingcap/tidb/issues/38683) @[lance6716](https://github.com/lance6716)
