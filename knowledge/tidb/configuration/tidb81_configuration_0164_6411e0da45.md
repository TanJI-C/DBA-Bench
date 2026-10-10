# DXF and Global Sort system variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_enable_dist_task <span class="version-mark">New in v7.1.0</span> | System Variables > Variable reference > tidb_cloud_storage_uri <span class="version-mark">New in v7.4.0</span>`
- Source Line Ranges: `1619-1645`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `cloud`
- Topic Tags: `system-variables`, `dxf`, `distributed-execution`, `global-sort`, `add-index`, `import-into`, `s3`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0164_6411e0da45`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-enable-dist-task-span-class-version-mark-new-in-v7-1-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `98e7b6871137f723fa6d9e9d4c7431b4248a9efb50f1a6bf0883e1cb88bd8221`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-enable-dist-task-span-class-version-mark-new-in-v7-1-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving information about the system variables that enable TiDB Distributed eXecution Framework (DXF) and configure Global Sort with an Amazon S3 cloud storage URI for ADD INDEX or IMPORT INTO.
- Retrieval Keywords: tidb_enable_dist_task, tidb_cloud_storage_uri, TiDB Distributed eXecution Framework, DXF, Global Sort, Amazon S3 cloud storage URI, ADD INDEX, IMPORT INTO, tidb_ddl_distribute_reorg, tidb_service_scope
- Follow-up Guidance: The content also notes the v8.1.0 upgrade consideration for clusters with DXF enabled and the workload-isolation note involving tidb_service_scope for Global Sort tasks.
- Classification Note: This is classified as configuration because the content defines GLOBAL system variables, their defaults, persistence behavior, rename history, and the statements or framework features they control.

## Official Source Content

### tidb_enable_dist_task New in v7.1.0

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `ON`
- This variable is used to control whether to enable the [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework). After the framework is enabled, the DXF tasks such as DDL and import will be distributedly executed and completed by multiple TiDB nodes in the cluster.
- Starting from TiDB v7.1.0, the DXF supports distributedly executing the [`ADD INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index) statement for partitioned tables.
- Starting from TiDB v7.2.0, the DXF supports distributedly executing the [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into) statement for import jobs.
- Starting from TiDB v8.1.0, this variable is enabled by default. If you want to upgrade a cluster with the DXF enabled to v8.1.0 or later, disable the DXF (by setting `tidb_enable_dist_task` to `OFF`) before the upgrade, which avoids `ADD INDEX` operations during the upgrade causing data index inconsistency. After the upgrade, you can manually enable the DXF.
- This variable is renamed from `tidb_ddl_distribute_reorg`.
### tidb_cloud_storage_uri New in v7.4.0

> **Note:**
>
> Currently, the [Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort) process consumes a large amount of computing and memory resources of TiDB nodes. In scenarios such as adding indexes online while user business applications are running, it is recommended to add new TiDB nodes to the cluster, configure the [`tidb_service_scope`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_service_scope-new-in-v740) variable for these nodes, and connect to these nodes to create tasks. In this way, the distributed framework schedules tasks to these nodes, isolating the workload from other TiDB nodes to reduce the impact of executing backend tasks such as `ADD INDEX` and `IMPORT INTO` on user business applications.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: `""`
- This variable is used to specify the Amazon S3 cloud storage URI to enable [Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort). After enabling the [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework), you can use the Global Sort feature by configuring the URI and pointing it to an appropriate cloud storage path with the necessary permissions to access the storage. For more details, see [Amazon S3 URI format](https://docs.pingcap.com/tidb/stable/external-storage-uri#amazon-s3-uri-format).
- The following statements can use the Global Sort feature.
    - The [`ADD INDEX`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-add-index) statement.
    - The [`IMPORT INTO`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into) statement for import jobs.
