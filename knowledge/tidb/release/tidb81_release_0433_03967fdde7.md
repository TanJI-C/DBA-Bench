# Availability feature: prefer-leader replica read option

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.0.0.md`
- Source Title: `TiDB 7.0.0 Release Notes`
- Source Heading Path: `TiDB 7.0.0 Release Notes > Feature details > Availability`
- Source Line Ranges: `206-213`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `release-notes`, `availability`, `replica-read`, `prefer-leader`, `read-routing`, `system-variables`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0433_03967fdde7`
- Source ID: `tidb-docs-8.1:releases/release-7.0.0.md#availability`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6dd12665a64582684716788c095050106d64305303ab8eb691fdacfcce074e1d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.0.0#availability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 7.0.0 availability release notes for the new prefer-leader replica read behavior controlled by a system variable.
- Retrieval Keywords: TiDB 7.0.0 Availability, prefer-leader, tidb_replica_read, replica read, leader replica, follower replicas, read operations, higher availability, reduces response latency, unstable network conditions
- Follow-up Guidance: The content points to the follower read documentation for more information about using prefer-leader with tidb_replica_read.
- Classification Note: This is a release-notes availability section describing the new prefer-leader option of tidb_replica_read for read routing behavior.

## Official Source Content

### Availability

* Support the `prefer-leader` option, which provides higher availability for read operations and reduces response latency in unstable network conditions [#40905](https://github.com/pingcap/tidb/issues/40905) @[LykxSassinator](https://github.com/LykxSassinator)

    You can control TiDB's data reading behavior through the system variable [`tidb_replica_read`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_replica_read-new-in-v40). In v7.0.0, this variable adds the `prefer-leader` option. When the variable is set to `prefer-leader`, TiDB prioritizes selecting the leader replica to perform read operations. When the processing speed of the leader replica slows down significantly, such as due to disk or network performance fluctuations, TiDB selects other available follower replicas to perform read operations, providing higher availability and reducing response latency.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/develop/dev-guide-use-follower-read).
