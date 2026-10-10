# DM daily check methods

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/dm-daily-check.md`
- Source Title: `Daily Check for TiDB Data Migration`
- Source Heading Path: `Daily Check for TiDB Data Migration`
- Source Line Ranges: `5-17`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `dashboard`, `tiup`, `shared`
- Topic Tags: `daily-check`, `query-status`, `monitoring`, `grafana`, `prometheus`, `logs`, `dm-master`, `dm-worker`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0090_556b781f2d`
- Source ID: `tidb-docs-8.1:dm/dm-daily-check.md#daily-check-for-tidb-data-migration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1370be81766c002a7115a503a9276369451cfabdb4d3410bdc77ced213ae7a84`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/dm-daily-check#daily-check-for-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/dm-daily-check.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the documented daily check methods for TiDB Data Migration, including task status, monitoring metrics, and log-based checks.
- Retrieval Keywords: Daily Check for TiDB Data Migration, query-status, Query Status, DM Dashboard, DM Monitoring Metrics, Prometheus, Grafana, DM-master log directory, DM-worker log directory, --log-file, TiUP, running status of the task, error output, log file
- Follow-up Guidance: The source points to Query Status for details on the `query-status` command and to DM Monitoring Metrics for more information about Grafana metrics.
- Classification Note: This chunk is classified as operation because it summarizes daily operational checks for DM through status queries, Grafana monitoring, and DM-master or DM-worker logs.

## Official Source Content

# Daily Check for TiDB Data Migration

This document summarizes how to perform a daily check on TiDB Data Migration (DM).

+ Method 1: Execute the `query-status` command to check the running status of the task and the error output (if any). For details, see [Query Status](https://docs.pingcap.com/tidb/stable/dm/dm-query-status).

+ Method 2: If Prometheus and Grafana are correctly deployed when you deploy the DM cluster using TiUP, you can view DM monitoring metrics in Grafana. For example, suppose that the Grafana's address is `172.16.10.71`, go to <http://172.16.10.71:3000>, enter the Grafana dashboard, and select the DM Dashboard to check monitoring metrics of DM. For more information of these metrics, see [DM Monitoring Metrics](https://docs.pingcap.com/tidb/stable/dm/monitor-a-dm-cluster).

+ Method 3: Check the running status of DM and the error (if any) using the log file.

    - DM-master log directory: It is specified by the `--log-file` DM-master process parameter. If DM is deployed using TiUP, the log directory is `{log_dir}` in the DM-master node.
    - DM-worker log directory: It is specified by the `--log-file` DM-worker process parameter. If DM is deployed using TiUP, the log directory is `{log_dir}` in the DM-worker node.
