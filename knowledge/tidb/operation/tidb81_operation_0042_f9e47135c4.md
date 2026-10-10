# Estimate RU capacity in Resource Manager

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-resource-manager.md`
- Source Title: `TiDB Dashboard Resource Manager Page`
- Source Heading Path: `TiDB Dashboard Resource Manager Page > Estimate Capacity`
- Source Line Ranges: `35-69`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tidb`, `tikv`
- Topic Tags: `capacity-estimation`, `request-unit`, `hardware-calibration`, `workload-calibration`, `privileges`, `cpu-metrics`, `alerts`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0042_f9e47135c4`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-resource-manager.md#estimate-capacity`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `498deb150476b9e8a0b18f8a57f8c096311362fe3e00290508dbefbd7f74d8e6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-resource-manager#estimate-capacity
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-resource-manager.md

## Retrieval Guidance

- Use When: Use this chunk when you need the Resource Manager Estimate Capacity options for RU, supported workload types, privilege requirements, or the exact calibration errors and monitoring metrics used for actual-workload estimation.
- Retrieval Keywords: Estimate Capacity, Request Unit, RU, CALIBRATE RESOURCE, estimate capacity based on hardware deployment, estimate capacity based on actual workload, tpcc, oltp_write_only, oltp_read_write, oltp_read_only, Total RU of user resource groups, default resource group, ERROR 1105 (HY000): the duration of calibration is too short, Error 1105 (HY000): There is no CPU quota metrics, metrics 'tikv_cpu_quota' is empty, Error 1105 (HY000): The workload in selected time window is too low, tikv_cpu_quota, tidb_server_maxprocs, resource_manager_resource_unit, process_cpu_usage, SUPER, RESOURCE_GROUP_ADMIN, CPU Usage
- Follow-up Guidance: The current login user must have the `SUPER` or `RESOURCE_GROUP_ADMIN` privilege and the `SELECT` privilege for some system tables, and you can use **CPU Usage** in the Metrics section to choose an appropriate time range.
- Classification Note: This is operational content because it explains how capacity estimation works in the Resource Manager page, including selectable methods, workload types, time-window constraints, required privileges, and runtime error conditions.

## Official Source Content

## Estimate Capacity

Before resource planning, you need to know the overall capacity of the cluster. TiDB provides two methods to estimate the capacity of [Request Unit (RU)](https://docs.pingcap.com/tidb/stable/tidb-resource-control#what-is-request-unit-ru#what-is-request-unit-ru) in the current cluster:

- [Estimate capacity based on hardware deployment](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-calibrate-resource#estimate-capacity-based-on-hardware-deployment)
    
    TiDB accepts the following workload types:
    
    - `tpcc`: applies to workloads with heavy data write. It is estimated based on a workload model similar to `TPC-C`.
    - `oltp_write_only`: applies to workloads with heavy data write. It is estimated based on a workload model similar to `sysbench oltp_write_only`.
    - `oltp_read_write`: applies to workloads with even data read and write. It is estimated based on a workload model similar to `sysbench oltp_read_write`.
    - `oltp_read_only`: applies to workloads with heavy data read. It is estimated based on a workload model similar to `sysbench oltp_read_only`.

  ![Calibrate by Hardware](/media/dashboard/dashboard-resource-manager-calibrate-by-hardware.png)

    The **Total RU of user resource groups** represents the total amount of RU for all user resource groups, excluding the `default` resource group. If this value is more than the estimated capacity, the system triggers an alert. By default, the system allocates unlimited usage to the predefined `default` resource group. When all users belong to the `default` resource group, resources are allocated in the same way as when resource control is disabled.

- [Estimate capacity based on actual workload](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-calibrate-resource#estimate-capacity-based-on-actual-workload)

    ![Calibrate by Workload](/media/dashboard/dashboard-resource-manager-calibrate-by-workload.png)

    You can select a time range for estimation within the range of 10 minutes to 24 hours. The time zone used is the same as that of the front-end user.

    - When the time window range does not fall between 10 minutes and 24 hours, the following error is displayed `ERROR 1105 (HY000): the duration of calibration is too short, which could lead to inaccurate output. Please make the duration between 10m0s and 24h0m0s`.

    - The monitoring metrics for the [capacity estimation based on the actual workload](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-calibrate-resource#estimate-capacity-based-on-actual-workload) feature include `tikv_cpu_quota`, `tidb_server_maxprocs`, `resource_manager_resource_unit`, and `process_cpu_usage`. If the CPU quota monitoring data is empty, there will be an error with the corresponding monitoring metric name, for example, `Error 1105 (HY000): There is no CPU quota metrics, metrics 'tikv_cpu_quota' is empty`.

    - If the workload in the time window is too low, or the `resource_manager_resource_unit` and `process_cpu_usage` monitoring data is missing, an error will be reported `Error 1105 (HY000): The workload in selected time window is too low, with which TiDB is unable to reach a capacity estimation; please select another time window with higher workload, or calibrate resource by hardware instead`. In addition, because TiKV does not monitor CPU utilization on macOS, it does not support capacity estimation based on the actual workload, and will also report this error.

  You can select an appropriate time range using **CPU Usage** in the [Metrics](#metrics) section.

> **Note:**
>
> To use the capacity estimation feature, the current login user must have the `SUPER` or `RESOURCE_GROUP_ADMIN` privilege and the `SELECT` privilege for some system tables. Before using this feature, ensure the current user has these privileges. Otherwise, some features might not work properly. For more information, see [`CALIBRATE RESOURCE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-calibrate-resource#privileges).
