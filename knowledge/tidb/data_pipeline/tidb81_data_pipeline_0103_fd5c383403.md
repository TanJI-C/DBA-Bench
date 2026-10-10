# DM incremental replication setup for MySQL shards to TiDB Cloud

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-sql-shards.md`
- Source Title: `Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud`
- Source Heading Path: `Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Perform incremental data replication from MySQL to TiDB Cloud | Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Perform incremental data replication from MySQL to TiDB Cloud > Before you begin | Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Perform incremental data replication from MySQL to TiDB Cloud > Step 1. Add the data source`
- Source Line Ranges: `236-339`
- Source Scope: `cloud`
- Primary Component: `dm`
- Related Components: `cloud`, `tiup`
- Topic Tags: `incremental-replication`, `binlog`, `gtid`, `data-source`, `dmctl`, `yaml`, `shard-merge`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0103_fd5c383403`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-sql-shards.md#perform-incremental-data-replication-from-mysql-to-tidb-cloud`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b5a4095a0a64f4d80ee1e04658c0060c015da8a1c2f5aba1162ed8cff8839fc2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-sql-shards#perform-incremental-data-replication-from-mysql-to-tidb-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-sql-shards.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the documented setup for DM incremental replication from MySQL shards to TiDB Cloud, including prerequisite deployment, DM source YAML, GTID settings, and dmctl source creation commands.
- Retrieval Keywords: Perform incremental data replication from MySQL to TiDB Cloud, TiDB Data Migration, DM, binlog, specified position, manually deploy TiDB DM, Deploy a DM Cluster Using TiUP, dm-source1.yaml, dm-source2.yaml, source-id, mysql-replica-01, mysql-replica-02, enable-gtid: true, GTID, from host user password port, tiup dmctl, --master-addr, operate-source create, dmctl encrypt, DM-master node, advertise-addr
- Follow-up Guidance: The source states that before incremental migration and shard merge to TiDB Cloud, you need to manually deploy TiDB DM because TiDB Cloud does not support migrating and merging MySQL shards yet.
- Classification Note: This is classified as a data pipeline chunk because it describes configuring DM data sources and commands for ongoing binlog-based incremental replication from MySQL shards into TiDB Cloud.

## Official Source Content

## Perform incremental data replication from MySQL to TiDB Cloud

To replicate the data changes based on binlog from a specified position in the upstream cluster to TiDB Cloud, you can use TiDB Data Migration (DM) to perform incremental replication.
### Before you begin

If you want to migrate incremental data and merge MySQL shards to TiDB Cloud, you need to manually deploy TiDB DM, because TiDB Cloud does not support migrating and merging MySQL shards yet. For detailed steps, see [Deploy a DM Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/deploy-a-dm-cluster-using-tiup).
### Step 1. Add the data source

1. Create a new data source file `dm-source1.yaml` to configure an upstream data source into DM. Add the following content:

    ```yaml
    # MySQL Configuration.
    source-id: "mysql-replica-01"
    # Specifies whether DM-worker pulls binlogs with GTID (Global Transaction Identifier).
    # The prerequisite is that you have already enabled GTID in the upstream MySQL.
    # If you have configured the upstream database service to switch master between different nodes automatically, you must enable GTID.
    enable-gtid: true
    from:
     host: "${host}"           # For example: 192.168.10.101
     user: "user01"
     password: "${password}"   # Plaintext passwords are supported but not recommended. It is recommended that you use dmctl encrypt to encrypt plaintext passwords.
     port: ${port}             # For example: 3307
    ```

2. Create another new data source file `dm-source2.yaml`, and add the following content:

    ```yaml
    # MySQL Configuration.
    source-id: "mysql-replica-02"
    # Specifies whether DM-worker pulls binlogs with GTID (Global Transaction Identifier).
    # The prerequisite is that you have already enabled GTID in the upstream MySQL.
    # If you have configured the upstream database service to switch master between different nodes automatically, you must enable GTID.
    enable-gtid: true
    from:
     host: "192.168.10.102"
     user: "user02"
     password: "${password}"
     port: 3308
    ```

3. Run the following command in a terminal. Use `tiup dmctl` to load the first data source configuration into the DM cluster:

    ```shell
    [root@localhost ~]# tiup dmctl --master-addr ${advertise-addr} operate-source create dm-source1.yaml
    ```

    The parameters used in the command above are described as follows:

    |Parameter              |Description    |
    |-                      |-              |
    |`--master-addr`        |The `{advertise-addr}` of any DM-master node in the cluster where `dmctl` is to be connected. For example: 192.168.11.110:9261|
    |`operate-source create`|Loads the data source to the DM cluster.|

    The following is an example output:

    ```shell
    tiup is checking updates for component dmctl ...

    Starting component `dmctl`: /root/.tiup/components/dmctl/${tidb_version}/dmctl/dmctl /root/.tiup/components/dmctl/${tidb_version}/dmctl/dmctl --master-addr 192.168.11.110:9261 operate-source create dm-source1.yaml

    {
       "result": true,
       "msg": "",
       "sources": [
           {
               "result": true,
               "msg": "",
               "source": "mysql-replica-01",
               "worker": "dm-192.168.11.111-9262"
           }
       ]
    }

    ```

4. Run the following command in a terminal. Use `tiup dmctl` to load the second data source configuration into the DM cluster:

    ```shell
    [root@localhost ~]# tiup dmctl --master-addr 192.168.11.110:9261 operate-source create dm-source2.yaml
    ```

    The following is an example output:

    ```shell
    tiup is checking updates for component dmctl ...

    Starting component `dmctl`: /root/.tiup/components/dmctl/${tidb_version}/dmctl/dmctl /root/.tiup/components/dmctl/${tidb_version}/dmctl/dmctl --master-addr 192.168.11.110:9261 operate-source create dm-source2.yaml

    {
       "result": true,
       "msg": "",
       "sources": [
           {
               "result": true,
               "msg": "",
               "source": "mysql-replica-02",
               "worker": "dm-192.168.11.112-9262"
           }
       ]
    }
    ```
