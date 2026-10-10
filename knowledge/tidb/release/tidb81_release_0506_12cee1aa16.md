# Reliability and resource control changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.4.0.md`
- Source Title: `TiDB 7.4.0 Release Notes`
- Source Heading Path: `TiDB 7.4.0 Release Notes > Feature details > Reliability`
- Source Line Ranges: `125-178`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tidb`, `tikv`
- Topic Tags: `query spilling`, `read timeout`, `optimizer hints`, `resource control`, `pipeline execution`, `background tasks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0506_12cee1aa16`
- Source ID: `tidb-docs-8.1:releases/release-7.4.0.md#reliability`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e59042a59f63a5137f6623fd1c2bbc0050f4f6e750d9e4301a7d94389aee628a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.4.0#reliability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.4.0 reliability changes covering TiFlash spilling, TiKV read timeout, optimizer hints, resource control, pipeline execution, optimizer mode, or background task management.
- Retrieval Keywords: TiDB 7.4.0 Reliability, TiFlash query-level data spilling, tiflash_mem_quota_query_per_node, tiflash_query_spill_ratio, GROUP BY ORDER BY JOIN spilling, TiKV read timeout, tikv_client_read_timeout, SET_VAR(TIKV_CLIENT_READ_TIMEOUT=N), optimizer hint SET_VAR(), TiFlash resource control, enable_resource_control, pipeline execution model, tidb_enable_tiflash_pipeline_model removed, tidb_enable_resource_control, tidb_opt_objective, moderate, determinate, background tasks, resource groups
- Follow-up Guidance: The source points to related documentation for TiFlash spilling, tikv_client_read_timeout, optimizer hints, TiDB resource control, TiFlash pipeline model, and tidb_opt_objective.
- Classification Note: This is a self-managed TiDB 7.4.0 release-notes chunk for reliability features affecting TiFlash, TiDB, and TiKV, including new variables, optimizer hints, and resource-control behavior.

## Official Source Content

### Reliability

* TiFlash supports query-level data spilling [#7738](https://github.com/pingcap/tiflash/issues/7738) @[windtalker](https://github.com/windtalker)

    Starting from v7.0.0, TiFlash supports controlling data spilling for three operators: `GROUP BY`, `ORDER BY`, and `JOIN`. This feature prevents issues such as query termination or system crashes when the data size exceeds the available memory. However, managing spilling for each operator individually can be cumbersome and ineffective for overall resource control.

    In v7.4.0, TiFlash introduces the query-level data spilling. By setting the memory limit for a query on a TiFlash node using [`tiflash_mem_quota_query_per_node`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_mem_quota_query_per_node-new-in-v740) and the memory ratio that triggers data spilling using [`tiflash_query_spill_ratio`](https://docs.pingcap.com/tidb/stable/system-variables#tiflash_query_spill_ratio-new-in-v740), you can conveniently manage the memory usage of a query and have better control over TiFlash memory resources.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-spill-disk).

* Support user-defined TiKV read timeout [#45380](https://github.com/pingcap/tidb/issues/45380) @[crazycs520](https://github.com/crazycs520)

    Normally, TiKV processes requests very quickly, in a matter of milliseconds. However, when a TiKV node encounters disk I/O jitter or network latency, the request processing time can increase significantly. In versions earlier than v7.4.0, the timeout limit for TiKV requests is fixed and unadjustable. Hence, TiDB has to wait for a fixed-duration timeout response when a TiKV node encounters issues, which results in a noticeable impact on application query performance during jitter.

    TiDB v7.4.0 introduces a new system variable [`tikv_client_read_timeout`](https://docs.pingcap.com/tidb/stable/system-variables#tikv_client_read_timeout-new-in-v740), which lets you customize the timeout for RPC read requests that TiDB sends to TiKV in a query. It means that when the request sent to a TiKV node is delayed due to disk or network issues, TiDB can time out faster and resend the request to other TiKV nodes, thus reducing query latency. If timeouts occur for all TiKV nodes, TiDB will retry using the default timeout. Additionally, you can also use the optimizer hint `/*+ SET_VAR(TIKV_CLIENT_READ_TIMEOUT=N) */` in a query to set the timeout for TiDB to send a TiKV RPC read request. This enhancement gives TiDB the flexibility to adapt to unstable network or storage environments, improving query performance and enhancing the user experience.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tikv_client_read_timeout-new-in-v740).

* Support temporarily modifying some system variable values using an optimizer hint [#45892](https://github.com/pingcap/tidb/issues/45892) @[winoros](https://github.com/winoros)

    TiDB v7.4.0 introduces the optimizer hint `SET_VAR()`, which is similar to that of MySQL 8.0. By including the hint `SET_VAR()` in SQL statements, you can temporarily modify the value of system variables during statement execution. This helps you set the environment for different statements. For example, you can actively increase the parallelism of resource-intensive SQL statements or change the optimizer behavior through variables.

    You can find the system variables that can be modified using the hint `SET_VAR()` in [system variables](https://docs.pingcap.com/tidb/stable/system-variables). It is strongly recommended not to modify variables that are not explicitly supported, as this might cause unpredictable behavior.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/optimizer-hints).

* TiFlash supports resource control [#7660](https://github.com/pingcap/tiflash/issues/7660) @[guo-shaoge](https://github.com/guo-shaoge)

    In TiDB v7.1.0, the resource control feature becomes generally available and provides resource management capabilities for TiDB and TiKV. In v7.4.0, TiFlash supports the resource control feature, improving the overall resource management capabilities of TiDB. The resource control of TiFlash is fully compatible with the existing TiDB resource control feature, and the existing resource groups will manage the resources of TiDB, TiKV, and TiFlash at the same time.

    To control whether to enable the TiFlash resource control feature, you can configure the TiFlash parameter `enable_resource_control`. After enabling this feature, TiFlash performs resource scheduling and management based on the resource group configuration of TiDB, ensuring the reasonable allocation and use of overall resources.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-resource-control).

* TiFlash supports the pipeline execution model (GA) [#6518](https://github.com/pingcap/tiflash/issues/6518) @[SeaRise](https://github.com/SeaRise)

    Starting from v7.2.0, TiFlash introduces a pipeline execution model. This model centrally manages all thread resources and schedules task execution uniformly, maximizing the utilization of thread resources while avoiding resource overuse. In v7.4.0, TiFlash improves the statistics of thread resource usage, and the pipeline execution model becomes a GA feature and is enabled by default. Since this feature is mutually dependent with the TiFlash resource control feature, TiDB v7.4.0 removes the variable `tidb_enable_tiflash_pipeline_model` used to control whether to enable the pipeline execution model in previous versions. Instead, you can enable or disable the pipeline execution model and the TiFlash resource control feature by configuring the TiFlash parameter `tidb_enable_resource_control`.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-pipeline-model).

* Add the option of optimizer mode [#46080](https://github.com/pingcap/tidb/issues/46080) @[time-and-fate](https://github.com/time-and-fate)

    In v7.4.0, TiDB introduces a new system variable [`tidb_opt_objective`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_objective-new-in-v740), which controls the estimation method used by the optimizer. The default value `moderate` maintains the previous behavior of the optimizer, where it uses runtime statistics to adjust estimations based on data changes. If this variable is set to `determinate`, the optimizer generates execution plans solely based on statistics without considering runtime corrections.

    For long-term stable OLTP applications or situations where you are confident in the existing execution plans, it is recommended to switch to `determinate` mode after testing. This reduces potential plan changes.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_objective-new-in-v740).

* TiDB resource control supports managing background tasks (experimental) [#44517](https://github.com/pingcap/tidb/issues/44517) @[glorv](https://github.com/glorv)

    Background tasks, such as data backup and automatic statistics collection, are low-priority but consume many resources. These tasks are usually triggered periodically or irregularly. During execution, they consume a lot of resources, thus affecting the performance of online high-priority tasks. Starting from v7.4.0, the TiDB resource control feature supports managing background tasks. This feature reduces the performance impact of low-priority tasks on online applications, enabling rational resource allocation, and greatly improving cluster stability.

    TiDB supports the following types of background tasks:
