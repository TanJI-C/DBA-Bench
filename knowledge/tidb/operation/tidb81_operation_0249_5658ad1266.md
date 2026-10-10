# TiCDC changefeed management interfaces

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-changefeed-overview.md`
- Source Title: `Changefeed Overview`
- Source Heading Path: `Changefeed Overview > Operate changefeeds`
- Source Line Ranges: `41-47`
- Source Scope: `shared`
- Primary Component: `ticdc`
- Related Components: `tiup`
- Topic Tags: `cdc-cli`, `openapi`, `management`, `changefeed`, `cluster-operations`, `tiup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0249_5658ad1266`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-changefeed-overview.md#operate-changefeeds`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5836cb2db30370bab075b86038cc61ad7f1de9e67bd773198d3bd8162a0f52b2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-overview#operate-changefeeds
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-changefeed-overview.md

## Retrieval Guidance

- Use When: Use this chunk when asking which interfaces can manage TiCDC clusters and changefeeds or how to start `cdc cli` in a TiUP deployment.
- Retrieval Keywords: Operate changefeeds, cdc cli, TiCDC OpenAPI, HTTP interface, manage TiCDC cluster, manage replication tasks, tiup cdc:v<CLUSTER_VERSION> cli, v8.1.2, Manage TiCDC changefeeds
- Follow-up Guidance: It directs readers to the `Manage TiCDC changefeeds` and `TiCDC OpenAPI` documentation for details.
- Classification Note: This is classified as operation because it lists the supported management interfaces and the TiUP command form for running `cdc cli`.

## Official Source Content

## Operate changefeeds

You can manage a TiCDC cluster and its replication tasks using the command-line tool `cdc cli`. For details, see [Manage TiCDC changefeeds](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed).

You can also use the HTTP interface (the TiCDC OpenAPI feature) to manage a TiCDC cluster and its replication tasks. For details, see [TiCDC OpenAPI](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api).

If your TiCDC is deployed using TiUP, you can start `cdc cli` by running the `tiup cdc:v<CLUSTER_VERSION> cli` command. Replace `v<CLUSTER_VERSION>` with the TiCDC cluster version, such as `v8.1.2`. You can also run `cdc cli` directly.
