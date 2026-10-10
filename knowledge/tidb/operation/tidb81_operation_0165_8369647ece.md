# Migration overview and environment setup

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-tidb-to-tidb.md`
- Source Title: `Migrate from one TiDB cluster to another TiDB cluster`
- Source Heading Path: `Migrate from One TiDB Cluster to Another TiDB Cluster | Migrate from One TiDB Cluster to Another TiDB Cluster > Step 1. Set up the environment`
- Source Line Ranges: `5-99`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `ticdc`, `br`, `shared`
- Topic Tags: `migration`, `environment-setup`, `cluster-deployment`, `test-data`, `sysbench`, `external-storage`, `minio`, `s3`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0165_8369647ece`
- Source ID: `tidb-docs-8.1:migrate-from-tidb-to-tidb.md#migrate-from-one-tidb-cluster-to-another-tidb-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2eab472aa753e239ec8d3b975f53eb1b0fa598182f27d8cdf899d312d5a355b4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-tidb-to-tidb#migrate-from-one-tidb-cluster-to-another-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-tidb-to-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the initial environment setup for migrating from one TiDB cluster to another, including TiUP Playground deployment, sysbench test data and workload generation, and Minio-based S3-compatible external storage preparation.
- Retrieval Keywords: Migrate from One TiDB Cluster to Another TiDB Cluster, Step 1. Set up the environment, TiUP Playground, tiup --tag upstream playground, tiup --tag downstream playground, tiup status, sysbench oltp_write_only, tidb-config, prepare, run, sbtest1, sbtest2, sbtest3, Minio, S3-compatible storage service, s3://backup?access-key=minio&secret-access-key=miniostorage&endpoint=http://${HOST_IP}:6060&force-path-style=true, external storage, backup bucket
- Follow-up Guidance: The document continues with full data migration, incremental data migration, and service migration to the new TiDB cluster.
- Classification Note: This is classified as an operation chunk because the content describes environment setup steps and commands for deploying clusters, initializing data, simulating workload, and preparing external storage.

## Official Source Content

# Migrate from One TiDB Cluster to Another TiDB Cluster

This document describes how to migrate data from one TiDB cluster to another TiDB cluster. This function applies to the following scenarios:

- Split databases: You can split databases when a TiDB cluster is excessively large, or you want to avoid impact between services of a cluster.
- Relocate databases: Physically relocate databases, such as changing the data center.
- Migrate data to a TiDB cluster of a newer version: Migrate data to a TiDB cluster of a newer version to satisfy data security and accuracy requirements.

This document exemplifies the whole migration process and contains the following steps:

1. Set up the environment.

2. Migrate full data.

3. Migrate incremental data.

4. Migrate services to the new TiDB cluster.
## Step 1. Set up the environment

1. Deploy TiDB clusters.

    Deploy two TiDB clusters, one upstream and the other downstream by using TiUP Playground. For more information, refer to [Deploy and Maintain an Online TiDB Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster).

    ```shell
    # Create an upstream cluster
    tiup --tag upstream playground --host 0.0.0.0 --db 1 --pd 1 --kv 1 --tiflash 0 --ticdc 1
    # Create a downstream cluster
    tiup --tag downstream playground --host 0.0.0.0 --db 1 --pd 1 --kv 1 --tiflash 0 --ticdc 1
    # View cluster status
    tiup status
    ```

2. Initialize data.

    By default, test databases are created in the newly deployed clusters. Therefore, you can use [sysbench](https://github.com/akopytov/sysbench#linux) to generate test data and simulate data in real scenarios.

    ```shell
    sysbench oltp_write_only --config-file=./tidb-config --tables=10 --table-size=10000 prepare
    ```

    In this document, we use sysbench to run the `oltp_write_only` script. This script generates 10 tables in the test database, each with 10,000 rows. The tidb-config is as follows:

    ```shell
    mysql-host=172.16.6.122 # Replace the value with the IP address of your upstream cluster
    mysql-port=4000
    mysql-user=root
    mysql-password=
    db-driver=mysql         # Set database driver to MySQL
    mysql-db=test           # Set the database as a test database
    report-interval=10      # Set data collection period to 10s
    threads=10              # Set the number of worker threads to 10
    time=0                  # Set the time required for executing the script. O indicates time unlimited
    rate=100                # Set average TPS to 100
    ```

3. Simulate service workload.

    In real scenarios, service data is continuously written to the upstream cluster. In this document, we use sysbench to simulate this workload. Specifically, run the following command to enable 10 workers to continuously write data to three tables, sbtest1, sbtest2, and sbtest3, with a total TPS not exceeding 100.

    ```shell
    sysbench oltp_write_only --config-file=./tidb-config --tables=3 run
    ```

4. Prepare external storage.

    In full data backup, both the upstream and downstream clusters need to access backup files. It is recommended that you use [External storage](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages) to store backup files. In this document, Minio is used to simulate an S3-compatible storage service.

    ```shell
    wget https://dl.min.io/server/minio/release/linux-amd64/minio
    chmod +x minio
    # Configure access-key access-screct-id to access minio
    export HOST_IP='172.16.6.122' # Replace the value with the IP address of your upstream cluster
    export MINIO_ROOT_USER='minio'
    export MINIO_ROOT_PASSWORD='miniostorage'
    # Create the database directory. backup is the bucket name.
    mkdir -p data/backup
    # Start minio at port 6060
    ./minio server ./data --address :6060 &
    ```

    The preceding command starts a minio server on one node to simulate S3 services. Parameters in the command are configured as follows:

    - Endpoint: `http://${HOST_IP}:6060/`
    - Access-key: `minio`
    - Secret-access-key: `miniostorage`
    - Bucket: `backup`

    The access link is as follows:

    ```shell
    s3://backup?access-key=minio&secret-access-key=miniostorage&endpoint=http://${HOST_IP}:6060&force-path-style=true
    ```
