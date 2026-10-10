# PingCAP Clinic overview and user scenarios

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/clinic/quick-start-with-clinic.md`
- Source Title: `Quick Start Guide for PingCAP Clinic`
- Source Heading Path: `Quick Start Guide for PingCAP Clinic | Quick Start Guide for PingCAP Clinic > User scenarios`
- Source Line Ranges: `5-21`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiup`, `cloud`
- Topic Tags: `clinic`, `diag`, `diagnostic-data`, `health-report`, `remote-troubleshooting`, `tiup-deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0013_9d50dd8980`
- Source ID: `tidb-docs-8.1:clinic/quick-start-with-clinic.md#quick-start-guide-for-pingcap-clinic`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `817b1332c21a4973926f3bcdd4bde672c9f889d2f2182a89694e2ac9208e64f4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/clinic/quick-start-with-clinic#quick-start-guide-for-pingcap-clinic
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/clinic/quick-start-with-clinic.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants a quick overview of PingCAP Clinic components, supported user scenarios, or the stated deployment applicability for collecting and viewing cluster diagnosis data.
- Retrieval Keywords: PingCAP Clinic, Diag client, Clinic Server, collect diagnostic data, upload diagnostic data, Health Report, remote troubleshooting, TiUP deployed clusters, TiDB Operator on Kubernetes, only used for troubleshooting cluster problems
- Follow-up Guidance: The source points to PingCAP Clinic Overview for component details and to the TiDB Operator clinic guide for Kubernetes environments.
- Classification Note: This is classified as architecture because the content defines PingCAP Clinic as Diag client plus Clinic Server and frames the supported usage scenarios and scope.

## Official Source Content

# Quick Start Guide for PingCAP Clinic

This document describes how to use PingCAP Clinic diagnosis service (PingCAP Clinic) to collect, upload, and view cluster diagnosis data quickly.

PingCAP Clinic consists of two components: [Diag client](https://github.com/pingcap/diag) (shorten as Diag) and Clinic Server cloud service (shorten as Clinic Server). For details of these two components, refer to [PingCAP Clinic Overview](https://docs.pingcap.com/tidb/stable/clinic/clinic-introduction).
## User scenarios

- To accurately identify and quickly resolve problems in your cluster when seeking help remotely from PingCAP technical support, you can collect diagnostic data with Diag, upload the collected data to the Clinic Server, and provide the data access link to the technical support.
- When the cluster is running properly and you need to check the status of the cluster, you can use Diag to collect diagnostic data, upload the data to Clinic Server, and view the results of Health Report.

> **Note:**
>
> - The following methods to collect and upload data are **only** applicable to [clusters deployed using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup). For clusters deployed using TiDB Operator on Kubernetes, see [PingCAP Clinic for TiDB Operator environments](https://docs.pingcap.com/tidb-in-kubernetes/stable/clinic-user-guide).
> - The diagnostic data collected by PingCAP Clinic is **only** used for troubleshooting cluster problems.
