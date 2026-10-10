# BR backup storage overview, credential forwarding, and URI usage

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/backup-and-restore-storages.md`
- Source Title: `Backup Storages`
- Source Heading Path: `Backup Storages | Backup Storages > Send credentials to TiKV | Backup Storages > URI format | Backup Storages > URI format > URI format description | Backup Storages > URI format > URI examples`
- Source Line Ranges: `5-99`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`, `sql`, `cloud`
- Topic Tags: `backup-storage`, `credentials`, `tikv`, `uri-format`, `s3`, `gcs`, `azure`, `nfs`, `backup`, `restore`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0009_efcac01f68`
- Source ID: `tidb-docs-8.1:br/backup-and-restore-storages.md#backup-storages`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `af7dd54bca7fcd56142827b9a4236a8d119793dfb9215845725c51040703e2b1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/backup-and-restore-storages#backup-storages
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/backup-and-restore-storages.md

## Retrieval Guidance

- Use When: Use this chunk when you need the BR backup storage overview, the `--send-credentials-to-tikv` or `SEND_CREDENTIALS_TO_TIKV = FALSE` setting, or example `--storage` URI formats for S3, GCS, Azure Blob Storage, and NFS.
- Retrieval Keywords: Backup Storages, --send-credentials-to-tikv, -c, SEND_CREDENTIALS_TO_TIKV = FALSE, --storage, -s, URI format, [scheme]://[host]/[path]?[parameters], s3://bucket-name/prefix, BACKUP DATABASE * TO 's3://bucket-name/prefix' SEND_CREDENTIALS_TO_TIKV = FALSE, tiup br backup full, tiup br restore full, gcs://external/backup-20220915?credentials-file=${credentials-file-path}, azure://external/backup-20220915?account-name=${account-name}&account-key=${account-key}, Amazon S3, Google Cloud Storage, Azure Blob Storage, NFS
- Follow-up Guidance: The source also points to authentication details for external storage services and server-side encryption.
- Classification Note: This is classified as configuration because it describes BR storage parameters, credential forwarding behavior, and external storage URI usage.

## Official Source Content

# Backup Storages

TiDB supports storing backup data to Amazon S3, Google Cloud Storage (GCS), Azure Blob Storage, and NFS. Specifically, you can specify the URI of backup storage in the `--storage` or `-s` parameter of `br` commands. This document introduces the [URI format](#uri-format) and [authentication](#authentication) of different external storage services, and [server-side encryption](#server-side-encryption).
## Send credentials to TiKV

| CLI parameter                | Description                                                  | Default value |
|:-----------------------------|:-------------------------------------------------------------|:--------------|
| `--send-credentials-to-tikv` | Controls whether to send credentials obtained by BR to TiKV. | `true`        |

By default, BR sends a credential to each TiKV node when using Amazon S3, GCS, or Azure Blob Storage as the storage system. This behavior simplifies the configuration and is controlled by the parameter `--send-credentials-to-tikv`(or `-c` in short).

Note that this operation is not applicable to cloud environments. If you use IAM Role authorization, each node has its own role and permissions. In this case, you need to configure `--send-credentials-to-tikv=false` (or `-c=0` in short) to disable sending credentials:

```bash
tiup br backup full -c=0 -u pd-service:2379 --storage 's3://bucket-name/prefix'
```

If you back up or restore data using the [`BACKUP`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-backup) and [`RESTORE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-restore) statements, you can add the `SEND_CREDENTIALS_TO_TIKV = FALSE` option:

```sql
BACKUP DATABASE * TO 's3://bucket-name/prefix' SEND_CREDENTIALS_TO_TIKV = FALSE;
```
## URI format
### URI format description

The URI format of the external storage service is as follows:

```shell
[scheme]://[host]/[path]?[parameters]
```

For more information about the URI format, see [URI Formats of External Storage Services](https://docs.pingcap.com/tidb/stable/external-storage-uri).
### URI examples

This section provides some URI examples by using `external` as the `host` parameter (`bucket name` or `container name` in the preceding sections).

<div label="Amazon S3" value="amazon">

**Back up snapshot data to Amazon S3**

```shell
tiup br backup full -u "${PD_IP}:2379" \
--storage "s3://external/backup-20220915?access-key=${access-key}&secret-access-key=${secret-access-key}"
```

**Restore snapshot data from Amazon S3**

```shell
tiup br restore full -u "${PD_IP}:2379" \
--storage "s3://external/backup-20220915?access-key=${access-key}&secret-access-key=${secret-access-key}"
```

</div>
<div label="GCS" value="gcs">

**Back up snapshot data to GCS**

```shell
tiup br backup full --pd "${PD_IP}:2379" \
--storage "gcs://external/backup-20220915?credentials-file=${credentials-file-path}"
```

**Restore snapshot data from GCS**

```shell
tiup br restore full --pd "${PD_IP}:2379" \
--storage "gcs://external/backup-20220915?credentials-file=${credentials-file-path}"
```

</div>
<div label="Azure Blob Storage" value="azure">

**Back up snapshot data to Azure Blob Storage**

```shell
tiup br backup full -u "${PD_IP}:2379" \
--storage "azure://external/backup-20220915?account-name=${account-name}&account-key=${account-key}"
```

**Restore the `test` database from snapshot backup data in Azure Blob Storage**

```shell
tiup br restore db --db test -u "${PD_IP}:2379" \
--storage "azure://external/backup-20220915account-name=${account-name}&account-key=${account-key}"
```

</div>
