# Using TiFlash and related documentation links

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-overview.md`
- Source Title: `TiFlash Overview`
- Source Heading Path: `TiFlash Overview > Use TiFlash | TiFlash Overview > See also`
- Source Line Ranges: `83-140`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `tiup`
- Topic Tags: `replica-creation`, `analytical-processing`, `tispark`, `mpp`, `data-import`, `deployment`, `scaling`, `maintenance`, `configuration`, `monitoring`, `alerts`, `troubleshooting`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0478_19ad5e724f`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-overview.md#use-tiflash`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `76367894021b240d20a6cb586ecdb2156fb3863ef72c273306224f0b2a81322e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#use-tiflash
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-overview.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how to start using TiFlash replicas and which linked documents cover reading methods, deployment, scaling, maintenance, configuration, monitoring, alerts, troubleshooting, validation, and compatibility.
- Retrieval Keywords: Use TiFlash, data replication does not automatically begin, manually specify the tables to be replicated, Create TiFlash Replicas, Use TiDB to Read TiFlash Replicas, Use TiSpark to Read TiFlash Replicas, Use MPP Mode, Quick Start Guide for TiDB HTAP, Deploy a TiDB cluster using TiUP, Scale out a TiFlash cluster, Maintain a TiFlash cluster, Tune TiFlash performance, Configure TiFlash, Monitor the TiFlash cluster, TiFlash alert rules, Troubleshoot a TiFlash cluster, Supported push-down calculations in TiFlash, Data validation in TiFlash, TiFlash compatibility
- Follow-up Guidance: The content directs readers to linked pages for replica creation, TiDB or TiSpark reads, MPP mode, deployment with TiUP, scaling, maintenance, tuning, configuration, monitoring, alert rules, troubleshooting, data validation, and compatibility.
- Classification Note: The classification is operation because the content describes how to use TiFlash after deployment and serves as a navigation hub to operational tasks and related documentation.

## Official Source Content

## Use TiFlash

After TiFlash is deployed, data replication does not automatically begin. You need to manually specify the tables to be replicated.

You can either use TiDB to read TiFlash replicas for medium-scale analytical processing, or use TiSpark to read TiFlash replicas for large-scale analytical processing, which is based on your own needs. See the following sections for details:

You can use TiDB to read TiFlash replicas for analytical processing. See the following sections for details:

- [Create TiFlash Replicas](https://docs.pingcap.com/tidb/stable/tiflash/create-tiflash-replicas)
- [Use TiDB to Read TiFlash Replicas](https://docs.pingcap.com/tidb/stable/tiflash/use-tidb-to-read-tiflash)

- [Use TiSpark to Read TiFlash Replicas](https://docs.pingcap.com/tidb/stable/tiflash/use-tispark-to-read-tiflash)

- [Use MPP Mode](https://docs.pingcap.com/tidb/stable/tiflash/use-tiflash-mpp-mode)

To experience the whole process from importing data to querying in a TPC-H dataset, refer to [Quick Start Guide for TiDB HTAP](https://docs.pingcap.com/tidb/stable/quick-start-with-htap).
## See also

- To deploy a new cluster with TiFlash nodes, see [Deploy a TiDB cluster using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup).
- To add a TiFlash node in a deployed cluster, see [Scale out a TiFlash cluster](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-out-a-tiflash-cluster).
- [Maintain a TiFlash cluster](https://docs.pingcap.com/tidb/stable/tiflash/maintain-tiflash).
- [Tune TiFlash performance](https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance).
- [Configure TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-configuration).
- [Monitor the TiFlash cluster](https://docs.pingcap.com/tidb/stable/tiflash/monitor-tiflash).
- Learn [TiFlash alert rules](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-alert-rules).
- [Troubleshoot a TiFlash cluster](https://docs.pingcap.com/tidb/stable/tiflash/troubleshoot-tiflash).
- [Supported push-down calculations in TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations)
- [Data validation in TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-data-validation)
- [TiFlash compatibility](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-compatibility)

- [Tune TiFlash performance](https://docs.pingcap.com/tidb/stable/tiflash/tune-tiflash-performance).
- [Supported push-down calculations in TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-supported-pushdown-calculations)
- [TiFlash compatibility](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-compatibility)
