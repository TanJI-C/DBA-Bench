# Prerequisites for TiFlash disaggregated deployment with S3

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/tiflash-disaggregated-and-s3.md`
- Source Title: `TiFlash Disaggregated Storage and Compute Architecture and S3 Support`
- Source Heading Path: `TiFlash Disaggregated Storage and Compute Architecture and S3 Support > Prerequisites`
- Source Line Ranges: `41-71`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `tiup`, `sql`
- Topic Tags: `prerequisites`, `s3-permissions`, `bucket`, `object-storage`, `replica-removal`, `scale-in`, `tombstone`, `cluster-prune`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0477_f20da35462`
- Source ID: `tidb-docs-8.1:tiflash/tiflash-disaggregated-and-s3.md#prerequisites`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8e9b83bdf3924119cdb576b37014a8ca04d264fbeb26064047648eb82a16017d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/tiflash-disaggregated-and-s3#prerequisites
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/tiflash-disaggregated-and-s3.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs prerequisites for deploying TiFlash with disaggregated storage and compute on S3, including required S3 permissions and removal of existing coupled TiFlash nodes.
- Retrieval Keywords: Prerequisites, S3 bucket, S3-compatible object storage, MinIO, PutObject, GetObject, CopyObject, DeleteObject, ListObjectsV2, GetObjectTagging, PutBucketLifecycle, INFORMATION_SCHEMA.TIFLASH_REPLICA, ALTER TABLE table_name SET TIFLASH REPLICA 0, tiup cluster scale-in, tiup cluster display, Tombstone state, tiup cluster prune
- Follow-up Guidance: The source gives example SQL and TiUP commands for querying TiFlash replicas, setting replica count to 0, removing TiFlash nodes, waiting for Tombstone state, and pruning them.
- Classification Note: This chunk is classified as operation because it lists deployment prerequisites, permission requirements, and cluster cleanup steps before enabling the new architecture.

## Official Source Content

## Prerequisites

1. Prepare an Amazon S3 bucket for storing the TiFlash data.

    You can also use an existing bucket, but you need to reserve dedicated key prefixes for each TiDB cluster. For more information about S3 buckets, see [AWS documentation](https://docs.aws.amazon.com/en_us/AmazonS3/latest/userguide/creating-buckets-s3.html).

    You can also use other S3-compatible object storage, such as [MinIO](https://min.io/).

    TiFlash needs to use the following S3 APIs for accessing data. Make sure that TiFlash nodes in your TiDB cluster have the necessary permissions for these APIs.

    - PutObject
    - GetObject
    - CopyObject
    - DeleteObject
    - ListObjectsV2
    - GetObjectTagging
    - PutBucketLifecycle

2. Make sure that your TiDB cluster has no TiFlash nodes deployed using the coupled storage and compute architecture. If any, set the TiFlash replica count of all tables to `0` and then remove all TiFlash nodes. For example:

    ```sql
    SELECT * FROM INFORMATION_SCHEMA.TIFLASH_REPLICA; # Query all tables with TiFlash replicas
    ALTER TABLE table_name SET TIFLASH REPLICA 0;     # Set the TiFlash replica count of all tables to `0`
    ```

    ```shell
    tiup cluster scale-in mycluster -N 'node0,node1...' # Remove all TiFlash nodes
    tiup cluster display mycluster                     # Wait for all TiFlash nodes to enter the Tombstone state
    tiup cluster prune mycluster                       # Remove all TiFlash nodes in the Tombstone state
    ```
