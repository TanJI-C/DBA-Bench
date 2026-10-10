# Replication workflow and external storage selection

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dr-secondary-cluster.md`
- Source Title: `DR Solution Based on Primary and Secondary Clusters`
- Source Heading Path: `DR Solution Based on Primary and Secondary Clusters > Set up primary and secondary clusters based on TiCDC > Replicate data from the primary cluster to the secondary cluster | DR Solution Based on Primary and Secondary Clusters > Set up primary and secondary clusters based on TiCDC > Replicate data from the primary cluster to the secondary cluster > Select an external storage`
- Source Line Ranges: `106-145`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `br`, `tikv`
- Topic Tags: `replication`, `data-migration`, `incremental-replication`, `external-storage`, `minio`, `s3`, `nfs`, `backup-storage`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0017_d4a8036c3d`
- Source ID: `tidb-docs-8.1:dr-secondary-cluster.md#replicate-data-from-the-primary-cluster-to-the-secondary-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e6b352b69511d03dc09d132193671a6d12c8ffb3329a621ca9cbd250977f3114`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dr-secondary-cluster#replicate-data-from-the-primary-cluster-to-the-secondary-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dr-secondary-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the replication workflow from the primary cluster to the secondary cluster and the external storage options used for data migration and real-time change data replication.
- Retrieval Keywords: Replicate data from the primary cluster to the secondary cluster, Select an external storage, external storage, Amazon S3, MinIO, NFS, NAS, br command-line tool, TiKV, TiCDC, backup storage, S3 protocol, POSIX file system interface, redo, backup, endpoint, access-key, secret-access-key, force-path-style=true, s3://backup
- Follow-up Guidance: The source includes a MinIO example with endpoint http://10.0.1.10:6060/, access-key minio, secret-access-key miniostorage, and bucket names redo and backup.
- Classification Note: This chunk is classified as data_pipeline because it explains the sequence of migrating existing data first and then creating a replication task for real-time change data, along with the storage systems used in that process.

## Official Source Content

### Replicate data from the primary cluster to the secondary cluster

After setting up the TiDB primary and secondary clusters, first migrate the data from the primary cluster to the secondary cluster, and then create a replication task to replicate real-time change data from the primary cluster to the secondary cluster.
#### Select an external storage

An external storage is used when migrating data and replicating real-time change data. Amazon S3 is a recommended choice. If the TiDB cluster is deployed in a self-built data center, the following methods are recommended:

* Build [MinIO](https://docs.min.io/docs/minio-quickstart-guide.html) as the backup storage system, and use the S3 protocol to back up data to MinIO.
* Mount Network File System (NFS, such as NAS) disks to br command-line tool, TiKV, and TiCDC instances, and use the POSIX file system interface to write backup data to the corresponding NFS directory.

The following example uses MinIO as the storage system and is for reference only. Note that you need to prepare a separate server to deploy MinIO in region 1 or region 2.

```shell
wget https://dl.min.io/server/minio/release/linux-amd64/minio
chmod +x minio
# Configure access-key and access-secret-id to access MinIO
export HOST_IP='10.0.1.10' # Replace it with the IP address of MinIO
export MINIO_ROOT_USER='minio'
export MINIO_ROOT_PASSWORD='miniostorage'
# Create the redo and backup directories. `backup` and `redo` are bucket names.
mkdir -p data/redo
mkdir -p data/backup
# Start minio at port 6060
nohup ./minio server ./data --address :6060 &
```

The preceding command starts a MinIO server on one node to simulate Amazon S3 services. Parameters in the command are configured as follows:

* `endpoint`: `http://10.0.1.10:6060/`
* `access-key`: `minio`
* `secret-access-key`: `miniostorage`
* `bucket`: `redo`/`backup`

The link is as follows:

```
s3://backup?access-key=minio&secret-access-key=miniostorage&endpoint=http://10.0.1.10:6060&force-path-style=true
```
