# TiDB tool selection use cases

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ecosystem-tool-user-case.md`
- Source Title: `TiDB Tools Use Cases`
- Source Heading Path: `TiDB Tools Use Cases | TiDB Tools Use Cases > Deploy and operate TiDB on physical or virtual machines | TiDB Tools Use Cases > Deploy and operate TiDB on Kubernetes | TiDB Tools Use Cases > Import data from CSV to TiDB | TiDB Tools Use Cases > Import full data from MySQL/Aurora | TiDB Tools Use Cases > Migrate data from MySQL/Aurora | TiDB Tools Use Cases > Back up and restore TiDB cluster | TiDB Tools Use Cases > Migrate data to TiDB | TiDB Tools Use Cases > TiDB incremental data subscription`
- Source Line Ranges: `5-46`
- Source Scope: `self_managed`
- Primary Component: `ecosystem`
- Related Components: `tiup`, `operator`, `lightning`, `dumpling`, `dm`, `br`, `ticdc`, `tidb`, `pd`, `tikv`
- Topic Tags: `tool-selection`, `deployment`, `kubernetes`, `csv-import`, `full-import`, `migration`, `backup`, `restore`, `incremental-backup`, `incremental-restore`, `incremental-replication`, `subscription`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0240_4941ad90db`
- Source ID: `tidb-docs-8.1:ecosystem-tool-user-case.md#tidb-tools-use-cases`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dcca87c416172646c57d6414986afda260a9b6e6c59d68f09d42eee34465eb5c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ecosystem-tool-user-case#tidb-tools-use-cases
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ecosystem-tool-user-case.md

## Retrieval Guidance

- Use When: Use this chunk when choosing the TiDB ecosystem tool for scenarios such as deploying and operating TiDB, importing CSV or MySQL/Aurora full data, migrating full and incremental data, backup and restore, or subscribing to TiDB incremental changes.
- Retrieval Keywords: TiDB Tools Use Cases, tool selection, TiUP, TiDB Operator, TiDB Lightning, Dumpling, DM, TiDB Data Migration, BR, Backup & Restore, TiCDC, deploy and operate TiDB on physical or virtual machines, deploy and operate TiDB on Kubernetes, import data from CSV to TiDB, import full data from MySQL/Aurora, migrate data from MySQL/Aurora, back up and restore TiDB cluster, incremental backup, incremental restore, migrate data to TiDB, TiDB incremental data subscription, subscribe to TiDB's incremental changes
- Follow-up Guidance: The content distinguishes when to use TiUP, TiDB Operator, TiDB Lightning, Dumpling, DM, BR, and TiCDC for full data import, incremental migration, backup and restore, and incremental data subscription.
- Classification Note: This is a reference chunk because it maps common operational and migration scenarios to the corresponding TiDB ecosystem tools without giving procedural steps.

## Official Source Content

# TiDB Tools Use Cases

This document introduces the common use cases of TiDB tools and how to choose the right tool for your scenario.
## Deploy and operate TiDB on physical or virtual machines

If you need to deploy and operate TiDB on physical or virtual machines, you can install [TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-overview), and then use TiUP to manage TiDB components such as TiDB, PD, and TiKV.
## Deploy and operate TiDB on Kubernetes

If you need to deploy and operate TiDB on Kubernetes, you can deploy a Kubernetes cluster, and then deploy [TiDB Operator](https://docs.pingcap.com/tidb-in-kubernetes/stable). After that, you can use TiDB Operator to deploy and operate a TiDB cluster.
## Import data from CSV to TiDB

If you need to import the compatible CSV files exported by other tools to TiDB, use [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview).
## Import full data from MySQL/Aurora

If you need to import full data from MySQL/Aurora, use [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) first to export data as SQL dump files, and then use [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) to import data into the TiDB cluster.
## Migrate data from MySQL/Aurora

If you need to migrate both full data and incremental data from MySQL/Aurora, use [TiDB Data Migration](https://docs.pingcap.com/tidb/stable/dm/dm-overview) (DM) to perform the [Migrate Data from Amazon Aurora to TiDB](https://docs.pingcap.com/tidb/stable/migrate-aurora-to-tidb).

If the full data volume is large (at the TB level), you can first use [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) and [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) to perform the full data migration, and then use DM to perform the incremental data migration.
## Back up and restore TiDB cluster

If you need to back up a TiDB cluster or restore backed up data to the cluster, use [BR](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview) (Backup & Restore).

In addition, BR can also be used to perform [incremental backup](https://docs.pingcap.com/tidb/stable/br/br-incremental-guide#back-up-incremental-data) and [incremental restore](https://docs.pingcap.com/tidb/stable/br/br-incremental-guide#restore-incremental-data) of TiDB cluster data.
## Migrate data to TiDB

If you need to migrate data from a TiDB cluster to another TiDB cluster, use [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) to export full data from TiDB as SQL dump files, and then use [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) to import data to another TiDB cluster.

If you also need to migrate incremental data, you can use [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview).
## TiDB incremental data subscription

If you need to subscribe to TiDB's incremental changes, you can use [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview).
