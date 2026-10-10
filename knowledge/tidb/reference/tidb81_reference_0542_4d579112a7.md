# CALIBRATE RESOURCE syntax, prerequisites, estimation methods, and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-calibrate-resource.md`
- Source Title: `CALIBRATE RESOURCE`
- Source Heading Path: ``CALIBRATE RESOURCE` | `CALIBRATE RESOURCE` > Synopsis | `CALIBRATE RESOURCE` > Privileges | `CALIBRATE RESOURCE` > Methods for estimating capacity | `CALIBRATE RESOURCE` > Methods for estimating capacity > Estimate capacity based on actual workload | `CALIBRATE RESOURCE` > Methods for estimating capacity > Estimate capacity based on hardware deployment | `CALIBRATE RESOURCE` > Examples`
- Source Line Ranges: `5-131`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `tiflash`, `shared`
- Topic Tags: `calibrate resource`, `request unit`, `ru capacity`, `syntax`, `privileges`, `resource control`, `actual workload`, `hardware deployment`, `time window`, `workload types`, `metrics`, `errors`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0542_4d579112a7`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-calibrate-resource.md#calibrate-resource`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d91bbeb40754e4f7f02a39b34d1ce895be298b6205eaa67b9a695768f046ed7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-calibrate-resource#calibrate-resource
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-calibrate-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the `CALIBRATE RESOURCE` syntax, required privileges, estimation methods for RU capacity, supported `WORKLOAD` values, example SQL, or the documented calibration errors and metric names.
- Retrieval Keywords: CALIBRATE RESOURCE, Request Unit, RU capacity, tidb_enable_resource_control, SUPER, RESOURCE_GROUP_ADMIN, SELECT privilege, METRICS_SCHEMA, START_TIME, END_TIME, DURATION, WORKLOAD, TPCC, OLTP_READ_WRITE, OLTP_READ_ONLY, OLTP_WRITE_ONLY, TPCH_10, QUOTA, tikv_cpu_quota, tidb_server_maxprocs, resource_manager_resource_unit, process_cpu_usage, tiflash_cpu_quota, tiflash_resource_manager_resource_unit, tiflash_process_cpu_usage, the duration of calibration is too long, the duration of calibration is too short, There is no CPU quota metrics, The workload in selected time window is too low
- Follow-up Guidance: The source also states that actual-workload estimation uses a time window from 10 minutes to 24 hours, defaults the end time to the current time, and is not supported on macOS for actual-workload estimation because TiKV does not monitor CPU usage metrics there.
- Classification Note: This is reference content because it defines `CALIBRATE RESOURCE` statement syntax, privileges, workload options, estimation behavior, example outputs, and exact error messages from the official documentation.

## Official Source Content

# `CALIBRATE RESOURCE`

The `CALIBRATE RESOURCE` statement is used to estimate and output the ['Request Unit (RU)`](/tidb-resource-control#what-is-request-unit-ru) capacity of the current cluster.

> **Note:**
>
> This feature is only applicable to TiDB Self-Managed and not available on [TiDB Cloud](https://docs.pingcap.com/tidbcloud/).
## Synopsis

```ebnf+diagram
CalibrateResourceStmt ::= 'CALIBRATE' 'RESOURCE' WorkloadOption

WorkloadOption ::=
( 'WORKLOAD' ('TPCC' | 'OLTP_READ_WRITE' | 'OLTP_READ_ONLY' | 'OLTP_WRITE_ONLY') )
| ( 'START_TIME' 'TIMESTAMP' ('DURATION' stringLit | 'END_TIME' 'TIMESTAMP')?)?

```
## Privileges

To execute this command, make sure that the following requirements are met:

- You have enabled [`tidb_enable_resource_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_resource_control-new-in-v660).
- The user has `SUPER` or `RESOURCE_GROUP_ADMIN` privilege.
- To [estimate capacity based on actual workload](#estimate-capacity-based-on-actual-workload), the user must have the `SELECT` privilege for all tables in the `METRICS_SCHEMA` schema.
## Methods for estimating capacity

TiDB provides two methods for estimation:
### Estimate capacity based on actual workload

If your application is already running in a production environment, or you can run actual business tests, it is recommended to use the actual workload over a period of time to estimate the total capacity. To improve the accuracy of the estimation, observe the following constraints:

- Use the `START_TIME` parameter to specify the time point at which the estimation starts, in the format of `2006-01-02 15:04:05`. The default estimation end time is the current time.
- After specifying the `START_TIME` parameter, you can use the `END_TIME` parameter to specify the estimation end time, or use the `DURATION` parameter to specify the estimation time window from `START_TIME`.
- The time window ranges from 10 minutes to 24 hours.
- In the specified time window, if the CPU utilization of TiDB and TiKV is too low, you cannot estimate the capacity.

> **Note:**
>
> TiKV does not monitor CPU usage metrics on macOS. It does not support capacity estimation based on the actual workload on macOS.
### Estimate capacity based on hardware deployment

This method mainly estimates capacity based on the current cluster configuration, combined with the empirical values observed for different workloads. Because different types of workloads require different ratios of hardware, the output capacity of the same configuration of hardware might be different. The `WORKLOAD` parameter here accepts the following different workload types. The default value is `TPCC`.

- `TPCC`: applies to workloads with heavy data write. It is estimated based on a workload model similar to `TPC-C`.
- `OLTP_WRITE_ONLY`: applies to workloads with heavy data write. It is estimated based on a workload model similar to `sysbench oltp_write_only`.
- `OLTP_READ_WRITE`: applies to workloads with even data read and write. It is estimated based on a workload model similar to `sysbench oltp_read_write`.
- `OLTP_READ_ONLY`: applies to workloads with heavy data read. It is estimated based on a workload model similar to `sysbench oltp_read_only`.
- `TPCH_10`: applies to AP queries. It is estimated based on 22 queries from `TPCH-10G`.

> **Note:**
>
> The RU capacity of a cluster varies with the topology of the cluster and the hardware and software configuration of each component. The actual RU that each cluster can provide is also related to the actual workload. The estimated value based on hardware deployment is for reference only and might differ from the actual maximum value. It is recommended to [estimate capacity based on actual workload](#estimate-capacity-based-on-actual-workload).
## Examples

Specify the start time `START_TIME` and the time window `DURATION` to view the RU capacity according to the actual workload.

```sql
CALIBRATE RESOURCE START_TIME '2023-04-18 08:00:00' DURATION '20m';
+-------+
| QUOTA |
+-------+
| 27969 |
+-------+
1 row in set (0.01 sec)
```

Specify the start time `START_TIME` and the end time `END_TIME` to view the RU capacity according to the actual workload.

```sql
CALIBRATE RESOURCE START_TIME '2023-04-18 08:00:00' END_TIME '2023-04-18 08:20:00';
+-------+
| QUOTA |
+-------+
| 27969 |
+-------+
1 row in set (0.01 sec)
```

When the time window range `DURATION` does not fall between 10 minutes and 24 hours, an error occurs.

```sql
CALIBRATE RESOURCE START_TIME '2023-04-18 08:00:00' DURATION '25h';
ERROR 1105 (HY000): the duration of calibration is too long, which could lead to inaccurate output. Please make the duration between 10m0s and 24h0m0s
CALIBRATE RESOURCE START_TIME '2023-04-18 08:00:00' DURATION '9m';
ERROR 1105 (HY000): the duration of calibration is too short, which could lead to inaccurate output. Please make the duration between 10m0s and 24h0m0s
```

The monitoring metrics for the [capacity estimation based on the actual workload](#estimate-capacity-based-on-actual-workload) feature include `tikv_cpu_quota`, `tidb_server_maxprocs`, `resource_manager_resource_unit`, `process_cpu_usage`, `tiflash_cpu_quota`, `tiflash_resource_manager_resource_unit`, and `tiflash_process_cpu_usage`. If the CPU quota monitoring data is empty, there will be an error with the corresponding monitoring metric name, as shown in the following example:

```sql
CALIBRATE RESOURCE START_TIME '2023-04-18 08:00:00' DURATION '60m';
Error 1105 (HY000): There is no CPU quota metrics, metrics 'tikv_cpu_quota' is empty
```

If the workload in the time window is too low, or the `resource_manager_resource_unit` and `process_cpu_usage` monitoring data is missing, the following error will be reported. In addition, because TiKV does not monitor CPU utilization on macOS, it does not support capacity estimation based on the actual workload, and will also report this error.

```sql
CALIBRATE RESOURCE START_TIME '2023-04-18 08:00:00' DURATION '60m';
ERROR 1105 (HY000): The workload in selected time window is too low, with which TiDB is unable to reach a capacity estimation; please select another time window with higher workload, or calibrate resource by hardware instead
```

Specify `WORKLOAD` to view the RU capacity. The default value is `TPCC`.

```sql
CALIBRATE RESOURCE;
+-------+
| QUOTA |
+-------+
| 190470 |
+-------+
1 row in set (0.01 sec)

CALIBRATE RESOURCE WORKLOAD OLTP_WRITE_ONLY;
+-------+
| QUOTA |
+-------+
| 27444 |
+-------+
1 row in set (0.01 sec)
```
