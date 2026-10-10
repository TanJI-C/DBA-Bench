# Optional DM incremental replication prerequisites and data source creation

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-aurora-to-tidb.md`
- Source Title: `Migrate Data from Amazon Aurora to TiDB`
- Source Heading Path: `Migrate Data from Amazon Aurora to TiDB > Replicate incremental data to TiDB (optional) | Migrate Data from Amazon Aurora to TiDB > Replicate incremental data to TiDB (optional) > Prerequisites | Migrate Data from Amazon Aurora to TiDB > Replicate incremental data to TiDB (optional) > Step 1: Create the data source`
- Source Line Ranges: `177-213`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `shared`
- Topic Tags: `incremental-replication`, `binlog`, `source-config`, `dmctl`, `privileges`, `gtid`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0030_f073052e3a`
- Source ID: `tidb-docs-8.1:migrate-aurora-to-tidb.md#replicate-incremental-data-to-tidb-optional`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6644a7607649002393f098ef72738fa3ffe4781f89fb6cabd4d1e63d2ff851c1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-aurora-to-tidb#replicate-incremental-data-to-tidb-optional
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-aurora-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the optional incremental replication prerequisites for Aurora-to-TiDB migration and the exact DM source configuration and dmctl command to create a data source.
- Retrieval Keywords: Replicate incremental data to TiDB (optional), Install DM, source1.yaml, source-id: "mysql-01", enable-gtid: false, from.host, from.user, from.password, dmctl encrypt, tiup dmctl --master-addr ${advertise-addr} operate-source create source1.yaml, operate-source create, DM-master, DM-worker, GTID
- Follow-up Guidance: The content notes that GTID mode is required if the upstream MySQL service is configured to switch master between different nodes automatically, and that plaintext password is supported but `dmctl encrypt` is recommended.
- Classification Note: This is classified under data_pipeline with primary component dm because the content covers DM installation prerequisites and creating an upstream source definition for incremental binlog replication.

## Official Source Content

## Replicate incremental data to TiDB (optional)
### Prerequisites

- [Install DM](https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-tiup).
- [Get the source database and target database privileges required for DM](https://docs.pingcap.com/tidb/stable/dm/dm-worker-intro).
### Step 1: Create the data source

1. Create the `source1.yaml` file as follows:

    ```yaml
    # Must be unique.
    source-id: "mysql-01"
    # Configures whether DM-worker uses the global transaction identifier (GTID) to pull binlogs. To enable this mode, the upstream MySQL must also enable GTID. If the upstream MySQL service is configured to switch master between different nodes automatically, GTID mode is required.
    enable-gtid: false

    from:
      host: "${host}"         # e.g.: 172.16.10.81
      user: "root"
      password: "${password}" # Supported but not recommended to use plaintext password. It is recommended to use `dmctl encrypt` to encrypt the plaintext password before using it.
      port: 3306
    ```

2. Load the data source configuration to the DM cluster using `tiup dmctl` by running the following command:

    ```shell
    tiup dmctl --master-addr ${advertise-addr} operate-source create source1.yaml
    ```

    The parameters used in the command above are described as follows:

    |Parameter              |Description    |
    |-                      |-              |
    |`--master-addr`        |The `{advertise-addr}` of any DM-master in the cluster where `dmctl` is to be connected, e.g.: 172.16.10.71:8261|
    |`operate-source create`|Loads the data source to the DM cluster.|
