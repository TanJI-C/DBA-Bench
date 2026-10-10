# TiDB Lightning physical import mode with log backup and TiCDC

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-compatibility-and-scenarios.md`
- Source Title: `Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup`
- Source Heading Path: `Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup > Scenarios for TiDB Lightning physical import mode | Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup > Scenarios for TiDB Lightning physical import mode > Used with log backup | Compatibility of TiDB Lightning and IMPORT INTO with TiCDC and Log Backup > Scenarios for TiDB Lightning physical import mode > Used with TiCDC`
- Source Line Ranges: `28-55`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `br`, `ticdc`, `tidb`
- Topic Tags: `physical-import`, `log-backup`, `pitr`, `ticdc`, `changefeed`, `precheck`, `snapshot-backup`, `downstream-replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0451_45fdf30d2e`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-compatibility-and-scenarios.md#scenarios-for-tidb-lightning-physical-import-mode`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0637fb1f8b6ba7303fc05bf59b25e93151470d3b82c658779fc7eeaa45326092`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-compatibility-and-scenarios#scenarios-for-tidb-lightning-physical-import-mode
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-compatibility-and-scenarios.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented scenarios for running TiDB Lightning physical import mode with log backup or TiCDC, including compatibility check errors, `Lightning.check-requirements`, and downstream replication handling.
- Retrieval Keywords: TiDB Lightning physical import mode with log backup, TiDB Lightning physical import mode with TiCDC, PITR enabled compatibility check will report an error, Lightning.check-requirements, TiDB Lightning configuration file, table-level snapshot backup, Back up a table, TiCDC changefeed, replicated downstream by TiCDC, restart the import task
- Follow-up Guidance: If imported tables need backup, the source says to perform a table-level snapshot backup after import, and if tables need TiCDC replication, import the same data in the downstream TiDB cluster after the upstream import finishes.
- Classification Note: This is classified as operation because the content describes concrete handling for physical import mode under log backup and TiCDC scenarios, including what happens during compatibility checks.

## Official Source Content

## Scenarios for TiDB Lightning physical import mode

This section describes how to use TiDB Lightning together with [log backup](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide) and [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview).

If TiDB Lightning logical import mode does not meet your application's performance requirements, you have to use TiDB Lightning physical import mode, and imported tables need to be backed up or replicated downstream using TiCDC, then the following scenarios are recommended.
### Used with log backup

In this scenario, if [PITR](https://docs.pingcap.com/tidb/stable/br/br-log-architecture#process-of-pitr) is enabled, the compatibility check will report an error after TiDB Lightning starts. If you are sure that these tables do not need backup, you can change the `Lightning.check-requirements` parameter in the [TiDB Lightning configuration file](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) to `false` and restart the import task.

Data imported using TiDB Lightning physical import mode cannot be backed up via log backup. If you need to back up the table, it is recommended to perform a table-level snapshot backup after the import, as described in [Back up a table](https://docs.pingcap.com/tidb/stable/br/br-snapshot-manual#back-up-a-table). 
### Used with TiCDC

Using TiCDC with physical import mode is not compatible in the short term, because TiCDC cannot keep up with the write speed of TiDB Lightning physical import mode, which might result in increasing cluster replication latency.

You can perform in different scenarios as follows:

- Scenario 1: the table does not need to be replicated downstream by TiCDC.

    In this scenario, if TiCDC changefeed is enabled, the compatibility check will report an error after TiDB Lightning starts. If you are sure that these tables do not need backup or [log backup](https://docs.pingcap.com/tidb/stable/br/br-pitr-guide), you can change the `Lightning.check-requirements` parameter in the [TiDB Lightning configuration file](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) to `false` and restart the import task.

- Scenario 2: the table needs to be replicated downstream by TiCDC.

    In this scenario, if TiCDC changefeed is enabled, the compatibility check will report an error after TiDB Lightning starts. You need to change the `Lightning.check-requirements` parameter in the [TiDB Lightning configuration file](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) in the upstream TiDB cluster to `false` and restart the import task.

    After the import task for the upstream TiDB cluster is finished, use TiDB Lightning to import the same data in the downstream TiDB cluster. If you have databases such as Redshift and Snowflake in the downstream, you can configure them to read CSV, SQL, or Parquet files from a cloud storage service and then write the data to the database.
