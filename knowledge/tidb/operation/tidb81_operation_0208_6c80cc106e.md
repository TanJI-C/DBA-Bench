# Primary-secondary replication overview and environment setup

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/replicate-between-primary-and-secondary-clusters.md`
- Source Title: `Replicate data between primary and secondary clusters`
- Source Heading Path: `Replicate Data Between Primary and Secondary Clusters | Replicate Data Between Primary and Secondary Clusters > Step 1. Set up the environment`
- Source Line Ranges: `5-98`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiup`, `br`, `ticdc`
- Topic Tags: `primary-secondary replication`, `environment setup`, `cluster deployment`, `sysbench`, `external storage`, `minio`, `s3-compatible storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0208_6c80cc106e`
- Source ID: `tidb-docs-8.1:replicate-between-primary-and-secondary-clusters.md#replicate-data-between-primary-and-secondary-clusters`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3ed5aa0ee305ea4cfea8be695ccdd44993764fff4dfef9cae3dbaef03266c237`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/replicate-between-primary-and-secondary-clusters#replicate-data-between-primary-and-secondary-clusters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/replicate-between-primary-and-secondary-clusters.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the overview and environment setup for replicating incremental data from a TiDB primary cluster to a TiDB or MySQL secondary cluster with BR, TiCDC, TiUP Playground, sysbench, and Minio S3-compatible storage.
- Retrieval Keywords: Replicate Data Between Primary and Secondary Clusters, Step 1. Set up the environment, upstream cluster, downstream cluster, primary-secondary replication, incremental data, BR, TiCDC, TiUP Playground, tiup --tag upstream playground, tiup --tag downstream playground, tiup status, sysbench oltp_write_only, tidb-config, sbtest1, sbtest2, sbtest3, external storage, Minio, S3-compatible storage, s3://backup?access-key=minio&secret-access-key=miniostorage&endpoint=http://${HOST_IP}:6060&force-path-style=true, redo bucket, backup bucket
- Follow-up Guidance: The next documented steps are to migrate full data and then replicate incremental data, with redo log used for consistent recovery when the primary cluster is down.
- Classification Note: This is classified as an operation chunk because the content describes environment deployment, test data initialization, workload simulation, and external storage preparation for primary-secondary replication.

## Official Source Content

# Replicate Data Between Primary and Secondary Clusters

This document describes how to configure a TiDB primary (upstream) cluster and a TiDB or MySQL secondary (downstream) cluster, and replicate incremental data from the primary cluster to the secondary cluster. The process includes the following steps:

1. Configure a TiDB primary cluster and a TiDB or MySQL secondary cluster.
2. Replicate incremental data from the primary cluster to the secondary cluster.
3. Recover data consistently by using Redo log when the primary cluster is down.

To replicate incremental data from a running TiDB cluster to its secondary cluster, you can use Backup & Restore [BR](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview) and [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview).
## Step 1. Set up the environment

1. Deploy TiDB clusters.

    Deploy two TiDB clusters, one upstream and the other downstream by using TiUP Playground. For production environments, deploy the clusters by referring to [Deploy and Maintain an Online TiDB Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster).

    In this document, we deploy the two clusters on two machines:

    - Node A: 172.16.6.123, for deploying the upstream TiDB cluster

    - Node B: 172.16.6.124, for deploying the downstream TiDB cluster

    ```shell
    # Create an upstream cluster on Node A
    tiup --tag upstream playground --host 0.0.0.0 --db 1 --pd 1 --kv 1 --tiflash 0 --ticdc 1
    # Create a downstream cluster on Node B
    tiup --tag downstream playground --host 0.0.0.0 --db 1 --pd 1 --kv 1 --tiflash 0 --ticdc 0
    # View cluster status
    tiup status
    ```

2. Initialize data.

    By default, test databases are created in the newly deployed clusters. Therefore, you can use [sysbench](https://github.com/akopytov/sysbench#linux) to generate test data and simulate data in real scenarios.

    ```shell
    sysbench oltp_write_only --config-file=./tidb-config --tables=10 --table-size=10000 prepare
    ```

    In this document, we use sysbench to run the `oltp_write_only` script. This script generates 10 tables in the upstream database, each with 10,000 rows. The tidb-config is as follows:

    ```shell
    mysql-host=172.16.6.122 # Replace it with the IP address of your upstream cluster
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

    In full data backup, both the upstream and downstream clusters need to access backup files. It is recommended that you use [External storage](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages) to store backup files. In this example, Minio is used to simulate an S3-compatible storage service.

    ```shell
    wget https://dl.min.io/server/minio/release/linux-amd64/minio
    chmod +x minio
    # Configure access-key access-screct-id to access minio
    export HOST_IP='172.16.6.123' # Replace it with the IP address of your upstream cluster
    export MINIO_ROOT_USER='minio'
    export MINIO_ROOT_PASSWORD='miniostorage'
    # Create the redo and backup directories. `backup` and `redo` are bucket names.
    mkdir -p data/redo
    mkdir -p data/backup
    # Start minio at port 6060
    nohup ./minio server ./data --address :6060 &
    ```

    The preceding command starts a minio server on one node to simulate S3 services. Parameters in the command are configured as follows:

    - Endpoint: `http://${HOST_IP}:6060/`
    - Access-key: `minio`
    - Secret-access-key: `miniostorage`
    - Bucket: `redo`

    The link is as follows:

    ```shell
    s3://backup?access-key=minio&secret-access-key=miniostorage&endpoint=http://${HOST_IP}:6060&force-path-style=true
    ```
