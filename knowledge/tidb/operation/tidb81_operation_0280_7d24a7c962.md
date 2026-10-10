# Manually upgrade TiDB Binlog Pump and Drainer

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/upgrade-tidb-binlog.md`
- Source Title: `Upgrade TiDB Binlog`
- Source Heading Path: `Upgrade TiDB Binlog | Upgrade TiDB Binlog > Upgrade TiDB Binlog deployed manually | Upgrade TiDB Binlog > Upgrade TiDB Binlog deployed manually > Upgrade Pump | Upgrade TiDB Binlog > Upgrade TiDB Binlog deployed manually > Upgrade Drainer`
- Source Line Ranges: `5-33`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `manual-upgrade`, `pump`, `drainer`, `deployment`, `deprecation`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0280_7d24a7c962`
- Source ID: `tidb-docs-8.1:tidb-binlog/upgrade-tidb-binlog.md#upgrade-tidb-binlog`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0586085250a18c7e10e18264b401b882937e0dda4ca5cfa54cb2c1dc2d200a5a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/upgrade-tidb-binlog#upgrade-tidb-binlog
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/upgrade-tidb-binlog.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the documented manual upgrade sequence for TiDB Binlog Pump and Drainer and the notes about compatibility, deprecation, and alternatives.
- Retrieval Keywords: Upgrade TiDB Binlog, Upgrade TiDB Binlog deployed manually, Upgrade Pump, Upgrade Drainer, manually upgrade TiDB Binlog, replace the original file with the new version of pump, restart the Pump process, replace the original file with the new version of drainer, restart the Drainer process, upgrade each Pump instance in the cluster one by one, TiDB Binlog is not compatible with some features introduced in TiDB v5.0, Starting from TiDB v7.5.0, TiCDC, PITR
- Follow-up Guidance: The content states to upgrade each Pump instance in the cluster one by one so that there are always Pump instances in the cluster that can receive binlogs from TiDB.
- Classification Note: This is classified as an operation chunk because the official content gives the manual upgrade procedure for Pump and Drainer in a self-managed deployment.

## Official Source Content

# Upgrade TiDB Binlog

This document introduces how to upgrade TiDB Binlog that is deployed manually to the latest [cluster](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview) version. There is also a section on how to upgrade TiDB Binlog from an earlier incompatible version (Kafka/Local version) to the latest version.

> **Note:**
>
> - TiDB Binlog is not compatible with some features introduced in TiDB v5.0 and they cannot be used together. For details, see [Notes](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview#notes).
> - Starting from TiDB v7.5.0, technical support for the data replication feature of TiDB Binlog is no longer provided. It is strongly recommended to use [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) as an alternative solution for data replication.
> - Although TiDB v7.5.0 still supports the real-time backup and restoration feature of TiDB Binlog, this component will be completely deprecated in future versions. It is recommended to use [PITR](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) as an alternative solution for data recovery.
## Upgrade TiDB Binlog deployed manually

Follow the steps in this section if you deploy TiDB Binlog manually.
### Upgrade Pump

First, upgrade each Pump instance in the cluster one by one. This ensures that there are always Pump instances in the cluster that can receive binlogs from TiDB. The steps are as below:

1. Replace the original file with the new version of `pump`.
2. Restart the Pump process.
### Upgrade Drainer

Second, upgrade the Drainer component:

1. Replace the original file with the new version of `drainer`.
2. Restart the Drainer process.
