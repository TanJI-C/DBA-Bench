# Upgrade TiDB Binlog from Kafka or Local to cluster version

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/upgrade-tidb-binlog.md`
- Source Title: `Upgrade TiDB Binlog`
- Source Heading Path: `Upgrade TiDB Binlog > Upgrade TiDB Binlog from Kafka/Local version to the cluster version | Upgrade TiDB Binlog > Upgrade TiDB Binlog from Kafka/Local version to the cluster version > Upgrade process`
- Source Line Ranges: `34-75`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `version-upgrade`, `kafka`, `local-storage`, `cluster-version`, `checkpoint`, `replication`, `pump`, `drainer`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0281_7e63c7aa55`
- Source ID: `tidb-docs-8.1:tidb-binlog/upgrade-tidb-binlog.md#upgrade-tidb-binlog-from-kafka-local-version-to-the-cluster-version`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c05268d6589ce295feac0f39994c6f4e1b52ff3e693e655e9bab34dfdbcc1fc5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/upgrade-tidb-binlog#upgrade-tidb-binlog-from-kafka-local-version-to-the-cluster-version
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/upgrade-tidb-binlog.md

## Retrieval Guidance

- Use When: Use this chunk when searching for how to upgrade TiDB Binlog from the Kafka or Local version to the cluster version while preserving replication from the original checkpoint.
- Retrieval Keywords: Upgrade TiDB Binlog from Kafka/Local version to the cluster version, Kafka version, Local version, cluster version, v2.0.8-binlog, v2.1.0-rc.5 or later, Upgrade process, resume replication from the original checkpoint, Deploy the new version of Pump, Stop the TiDB cluster service, Start the new version of Drainer, curl http://172.16.10.49:8249/status, status interface of Drainer, Synced true, Close the Pump and Drainer of the old versions, Kafka and ZooKeeper
- Follow-up Guidance: The content says that if the return value of `Synced` is True in the Drainer `status` interface, Drainer has replicated the data in the old version of Pump to the downstream completely.
- Classification Note: This is classified as an operation chunk because the official content provides the upgrade process, version mapping, and checkpoint-based replication transition steps from Kafka or Local TiDB Binlog to the cluster version.

## Official Source Content

## Upgrade TiDB Binlog from Kafka/Local version to the cluster version

The new TiDB versions (v2.0.8-binlog, v2.1.0-rc.5 or later) are not compatible with the Kafka version or Local version of TiDB Binlog. If TiDB is upgraded to one of the new versions, it is required to use the cluster version of TiDB Binlog. If the Kafka or local version of TiDB Binlog is used before upgrading, you need to upgrade your TiDB Binlog to the cluster version.

The corresponding relationship between TiDB Binlog versions and TiDB versions is shown in the following table:

| TiDB Binlog version | TiDB version                              | Note                                                                                       |
|---------------------|-------------------------------------------|--------------------------------------------------------------------------------------------|
| Local               | TiDB 1.0 or earlier                       |                                                                                            |
| Kafka               | TiDB 1.0 ~ TiDB 2.1 RC5                   | TiDB 1.0 supports both the local and Kafka versions of TiDB Binlog.                        |
| Cluster             | TiDB v2.0.8-binlog, TiDB 2.1 RC5 or later | TiDB v2.0.8-binlog is a special 2.0 version supporting the cluster version of TiDB Binlog. |
### Upgrade process

> **Note:**
>
> If importing the full data is acceptable, you can abandon the old version and deploy TiDB Binlog following [TiDB Binlog Cluster Deployment](https://docs.pingcap.com/tidb/stable/tidb-binlog/deploy-tidb-binlog).

If you want to resume replication from the original checkpoint, perform the following steps to upgrade TiDB Binlog:

1. Deploy the new version of Pump.
2. Stop the TiDB cluster service.
3. Upgrade TiDB and the configuration, and write the binlog data to the new Pump cluster.
4. Reconnect the TiDB cluster to the service.
5. Make sure that the old version of Drainer has replicated the data in the old version of Pump to the downstream completely;

    Query the `status` interface of Drainer, command as below:

    ```bash
    curl 'http://172.16.10.49:8249/status'
    ```

    ```
    {"PumpPos":{"172.16.10.49:8250":{"offset":32686}},"Synced": true ,"DepositWindow":{"Upper":398907800202772481,"Lower":398907799455662081}}
    ```

    If the return value of `Synced` is True, it means Drainer has replicated the data in the old version of Pump to the downstream completely.

6. Start the new version of Drainer.
7. Close the Pump and Drainer of the old versions and the dependent Kafka and ZooKeeper.
