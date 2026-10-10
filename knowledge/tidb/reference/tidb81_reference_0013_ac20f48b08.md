# Management, observability, and tools feature matrix

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/basic-features.md`
- Source Title: `TiDB Features`
- Source Heading Path: `TiDB Features > Management, observability, and tools`
- Source Line Ranges: `223-274`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `tiup`, `operator`, `br`, `dm`, `pd`, `tikv`, `tidb`, `tiflash`, `sql`
- Topic Tags: `feature-matrix`, `management`, `observability`, `tools`, `dashboard`, `information-schema`, `metrics-schema`, `statement-summary`, `slow-query-log`, `deployment`, `backup`, `resource-control`, `dxf`, `pd-microservices`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0013_ac20f48b08`
- Source ID: `tidb-docs-8.1:basic-features.md#management-observability-and-tools`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3dc53ec414681d685d455266e18ec7c5543e0b31cf51f42d198b7d1c6ead8067`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/basic-features#management-observability-and-tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/basic-features.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiDB 8.1 management, observability, and tools feature matrix and version availability for items such as TiDB Dashboard, Information schema, Metrics schema, backup, resource control, DXF, and PD microservices.
- Retrieval Keywords: Management, observability, and tools, feature matrix, TiDB Dashboard UI, TiDB Dashboard Continuous Profiling, TiDB Dashboard Top SQL, TiDB Dashboard SQL Diagnostics, TiDB Dashboard Cluster Diagnostics, TiKV-FastTune dashboard, Information schema, Metrics schema, Statements summary tables, summary persistence, Slow query log, TiUP deployment, Kubernetes operator, Built-in physical backup, Global Kill, Lock View, SHOW CONFIG, SET CONFIG, DM WebUI, Foreground Quota Limiter, Background Quota Limiter, EBS volume snapshot backup and restore, PITR, Global memory control, Cross-cluster RawKV replication, Green GC, Resource control, Runaway Queries management, Background tasks management, TiFlash Disaggregated Storage and Compute Architecture and S3 Support, Selecting TiDB nodes for the Distributed eXecution Framework tasks, tidb_service_scope, PD Follower Proxy, tidb_enable_tso_follower_proxy, Active PD Follower, pd_enable_follower_handle_region, PD microservices, TiDB Distributed eXecution Framework, Global Sort, 8.1, 7.5, 7.1, 6.5, 6.1, 5.4, 5.3, 5.2, 5.1
- Follow-up Guidance: The table links each listed feature to its dedicated documentation page, such as SQL statements, system variables, Dashboard pages, BR, TiUP, TiDB Operator, and PD microservices.
- Classification Note: This chunk is a reference matrix because the official content is a version-by-version availability table for management, observability, and tools features in self-managed TiDB.

## Official Source Content

## Management, observability, and tools

| Management, observability, and tools | 8.1 | 7.5 | 7.1 | 6.5 | 6.1 | 5.4 | 5.3 | 5.2 | 5.1 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| [TiDB Dashboard UI](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [TiDB Dashboard Continuous Profiling](https://docs.pingcap.com/tidb/stable/dashboard/continuous-profiling) | Y | Y | Y | Y | Y | E | E | N | N |
| [TiDB Dashboard Top SQL](https://docs.pingcap.com/tidb/stable/dashboard/top-sql) | Y | Y | Y | Y | Y | E | N | N | N |
| [TiDB Dashboard SQL Diagnostics](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-sql-diagnostics) | Y | Y | Y | Y | E | E | E | E | E |
| [TiDB Dashboard Cluster Diagnostics](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-diagnostics-access) | Y | Y | Y | Y | E | E | E | E | E |
| [TiKV-FastTune dashboard](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard#tikv-fasttune-dashboard) | E | E | E | E | E | E | E | E | E |
| [Information schema](https://docs.pingcap.com/tidb/stable/information-schema/information-schema) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Metrics schema](https://docs.pingcap.com/tidb/stable/metrics-schema) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Statements summary tables](https://docs.pingcap.com/tidb/stable/statement-summary-tables) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Statements summary tables - summary persistence](https://docs.pingcap.com/tidb/stable/statement-summary-tables#persist-statements-summary) | E | E | E | N | N | N | N | N | N |
| [Slow query log](https://docs.pingcap.com/tidb/stable/identify-slow-queries) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [TiUP deployment](https://docs.pingcap.com/tidb/stable/tiup/tiup-overview) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Kubernetes operator](https://docs.pingcap.com/tidb-in-kubernetes/) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Built-in physical backup](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-use-cases) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Global Kill](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-kill) | Y | Y | Y | Y | Y | E | E | E | E |
| [Lock View](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-data-lock-waits) | Y | Y | Y | Y | Y | Y | Y | Y | E |
| [`SHOW CONFIG`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-config) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [`SET CONFIG`](https://docs.pingcap.com/tidb/stable/dynamic-config) | Y | Y | Y | Y | Y | E | E | E | E |
| [DM WebUI](https://docs.pingcap.com/tidb/stable/dm/dm-webui-guide) | E | E | E | E | E | N | N | N | N |
| [Foreground Quota Limiter](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#foreground-quota-limiter) | Y | Y | Y | Y | E | N | N | N | N |
| [Background Quota Limiter](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#background-quota-limiter) | E | E | E | E | N | N | N | N | N |
| [EBS volume snapshot backup and restore](https://docs.pingcap.com/tidb-in-kubernetes/v1.4/backup-to-aws-s3-by-snapshot) | Y | Y | Y | Y | N | N | N | N | N |
| [PITR](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview) | Y | Y | Y | Y | N | N | N | N | N |
| [Global memory control](https://docs.pingcap.com/tidb/stable/configure-memory-usage#configure-the-memory-usage-threshold-of-a-tidb-server-instance) | Y | Y | Y | Y | N | N | N | N | N |
| [Cross-cluster RawKV replication](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#api-version-new-in-v610) | E | E | E | E | N | N | N | N | N |
| [Green GC](https://docs.pingcap.com/tidb/stable/system-variables#tidb_gc_scan_lock_mode-new-in-v50) | E | E | E | E | E | E | E | E | E |
| [Resource control](https://docs.pingcap.com/tidb/stable/tidb-resource-control) | Y | Y | Y | N | N | N | N | N | N |
| [Runaway Queries management](https://docs.pingcap.com/tidb/stable/tidb-resource-control#manage-queries-that-consume-more-resources-than-expected-runaway-queries) | Y | E | N | N | N | N | N | N | N |
| [Background tasks management](https://docs.pingcap.com/tidb/stable/tidb-resource-control#manage-background-tasks) | E | E | N | N | N | N | N | N | N |
| [TiFlash Disaggregated Storage and Compute Architecture and S3 Support](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3) | Y | Y | E | N | N | N | N | N | N |
| [Selecting TiDB nodes for the Distributed eXecution Framework (DXF) tasks](https://docs.pingcap.com/tidb/stable/system-variables#tidb_service_scope-new-in-v740) | Y | Y | N | N | N | N | N | N | N |
| PD Follower Proxy (controlled by [`tidb_enable_tso_follower_proxy`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_tso_follower_proxy-new-in-v530)) | Y | Y | Y | Y | Y | Y | Y | N | N |
| [Active PD Follower](https://docs.pingcap.com/tidb/stable/tune-region-performance#use-the-active-pd-follower-feature-to-enhance-the-scalability-of-pds-region-information-query-service) (controlled by [`pd_enable_follower_handle_region`](https://docs.pingcap.com/tidb/stable/system-variables#pd_enable_follower_handle_region-new-in-v760)) | E | N | N | N | N | N | N | N | N |
| [PD microservices](https://docs.pingcap.com/tidb/stable/pd-microservices) | E | N | N | N | N | N | N | N | N |
| [TiDB Distributed eXecution Framework (DXF)](https://docs.pingcap.com/tidb/stable/tidb-distributed-execution-framework) | Y | Y | E | N | N | N | N | N | N |
| [Global Sort](https://docs.pingcap.com/tidb/stable/tidb-global-sort) | Y | E | N | N | N | N | N | N | N |

[^1]: TiDB incorrectly treats latin1 as a subset of utf8. See [TiDB #18955](https://github.com/pingcap/tidb/issues/18955) for more details.

[^2]: Starting from v6.5.0, the expression indexes created on the functions listed by the [`tidb_allow_function_for_expression_index`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_allow_function_for_expression_index-new-in-v520) system variable have been tested and can be used in production environments, and more functions will be supported in the future releases. For functions not listed by this variable, the corresponding expression indexes are not recommended for use in production environments. See [expression indexes](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-index#expression-index) for details.

[^3]: See [Statement Reference](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-select) for a full list of SQL statements supported.

[^4]: Starting from [v6.4.0](https://docs.pingcap.com/tidb/stable/releases/release-6.4.0), TiDB supports [high-performance and globally monotonic `AUTO_INCREMENT` columns](https://docs.pingcap.com/tidb/stable/auto-increment#mysql-compatibility-mode)

[^5]: Starting from [TiDB v7.0.0](https://docs.pingcap.com/tidb/stable/releases/release-7.0.0), the new parameter `FIELDS DEFINED NULL BY` and support for importing data from S3 and GCS are experimental features. Starting from [v7.6.0](https://docs.pingcap.com/tidb/stable/releases/release-7.6.0), TiDB processes `LOAD DATA` in transactions in the same way as MySQL. The `LOAD DATA` statement in a transaction no longer automatically commits the current transaction or starts a new transaction. Moreover, you can explicitly commit or roll back the `LOAD DATA` statement in a transaction. Additionally, the `LOAD DATA` statement is affected by the TiDB transaction mode setting (optimistic or pessimistic transaction).

[^6]: Starting from TiDB v7.5.0, technical support for the data replication feature of [TiDB Binlog](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview) is no longer provided. It is strongly recommended to use [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) as an alternative solution for data replication. Although TiDB Binlog v7.5.0 still supports the Point-in-Time Recovery (PITR) scenario, this component will be completely deprecated in future versions. It is recommended to use [PITR](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) as an alternative solution for data recovery.
