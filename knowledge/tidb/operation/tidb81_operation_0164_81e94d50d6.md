# Service cutover and changefeed stop

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migrate-from-tidb-to-mysql.md`
- Source Title: `Migrate Data from TiDB to MySQL-compatible Databases`
- Source Heading Path: `Migrate Data from TiDB to MySQL-compatible Databases > Step 4. Migrate services`
- Source Line Ranges: `204-231`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tidb`
- Topic Tags: `service-migration`, `cutover`, `read-traffic`, `write-traffic`, `changefeed-pause`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0164_81e94d50d6`
- Source ID: `tidb-docs-8.1:migrate-from-tidb-to-mysql.md#step-4-migrate-services`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5d6bdb3fb70c0b3b6fdefa42ec0ac2cc1598886ede6565f7491b5a1c73519037`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migrate-from-tidb-to-mysql#step-4-migrate-services
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migrate-from-tidb-to-mysql.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented service cutover procedure after TiCDC replication is running, including gradual read migration, stopping upstream writes, pausing the changefeed, and verifying the stopped state and checkpoint time.
- Retrieval Keywords: Step 4. Migrate services, migrate read traffic gradually, migrate write traffic, Stop write services in the upstream cluster, tiup cdc cli changefeed pause -c "upstream-to-downstream" --pd=http://172.16.6.122:2379, tiup cdc cli changefeed list, state": "stopped", checkpoint, This time should be later than the time of stopping writing, discard the upstream cluster
- Follow-up Guidance: After migrating writing services to the downstream cluster, the document says to observe for a period and, if the downstream cluster is stable, discard the upstream cluster.
- Classification Note: This is classified as an operation chunk because it describes the service migration and cutover procedure, including traffic migration and changefeed stop verification.

## Official Source Content

## Step 4. Migrate services

After creating a changefeed, data written to the upstream cluster is replicated to the downstream cluster with low latency. You can migrate read traffic to the downstream cluster gradually. Observe the read traffic for a period. If the downstream cluster is stable, you can migrate write traffic to the downstream cluster as well in the following steps:

1. Stop write services in the upstream cluster. Make sure that all upstream data are replicated to downstream before stopping the changefeed.

    ```shell
    # Stop the changefeed from the upstream cluster to the downstream cluster
    tiup cdc cli changefeed pause -c "upstream-to-downstream" --pd=http://172.16.6.122:2379
    # View the changefeed status
    tiup cdc cli changefeed list
    ```

    ```
    [
      {
        "id": "upstream-to-downstream",
        "summary": {
        "state": "stopped",  # Ensure that the status is stopped
        "tso": 434218657561968641,
        "checkpoint": "2022-06-28 18:38:45.685", # This time should be later than the time of stopping writing
        "error": null
        }
      }
    ]
    ```

2. After migrating writing services to the downstream cluster, observe for a period. If the downstream cluster is stable, you can discard the upstream cluster.
