# TiCDC bidirectional replication deployment prerequisites and setup

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-bidirectional-replication.md`
- Source Title: `Bidirectional Replication`
- Source Heading Path: `Bidirectional Replication | Bidirectional Replication > Deploy bi-directional replication`
- Source Line Ranges: `5-36`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `dumpling`, `lightning`, `tidb`
- Topic Tags: `bidirectional replication`, `bdr mode`, `changefeed`, `start-ts`, `incremental replication`, `initial data import`, `topology`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0174_7c8f0551a1`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-bidirectional-replication.md#bidirectional-replication`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `485d40cbcca3a57f02c9d9975988d4642cb2996e1cb28054b2192fca027d9ee9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-bidirectional-replication#bidirectional-replication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-bidirectional-replication.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to deploy TiCDC bidirectional replication between two TiDB clusters, including initial data import, topology, start timestamp selection, and enabling BDR mode.
- Retrieval Keywords: Bidirectional Replication, Deploy bi-directional replication, TiCDC only replicates incremental data changes, Dumpling, TiDB Lightning, two TiCDC clusters, --start-ts, tso, --config, bdr-mode = true, multi-active TiDB solution
- Follow-up Guidance: The source explains that when creating the changefeed, you set the upstream cluster `--start-ts` to the corresponding `tso` for the time point where the two clusters are consistent.
- Classification Note: This is classified as configuration because the content describes prerequisite setup, changefeed `--start-ts` selection, TiCDC cluster topology, and the `bdr-mode = true` configuration required to enable bidirectional replication.

## Official Source Content

# Bidirectional Replication

TiCDC supports bi-directional replication (BDR) among two TiDB clusters. Based on this feature, you can create a multi-active TiDB solution using TiCDC.

This section describes how to use bi-directional replication taking two TiDB clusters as an example.
## Deploy bi-directional replication

TiCDC only replicates incremental data changes that occur after a specified timestamp to the downstream cluster. Before starting the bi-directional replication, you need to take the following steps:

1. (Optional) According to your needs, import the data of the two TiDB clusters into each other using the data export tool [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview) and data import tool [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview).

2. Deploy two TiCDC clusters between the two TiDB clusters. The cluster topology is as follows. The arrows in the diagram indicate the directions of data flow.

    ![TiCDC bidirectional replication](/media/ticdc/ticdc-bidirectional-replication.png)

3. Specify the starting time point of data replication for the upstream and downstream clusters.

    1. Check the time point of the upstream and downstream clusters. In the case of two TiDB clusters, make sure that data in the two clusters are consistent at certain time points. For example, the data of TiDB A at `ts=1` and the data of TiDB B at `ts=2` are consistent.

    2. When you create the changefeed, set the `--start-ts` of the changefeed for the upstream cluster to the corresponding `tso`. That is, if the upstream cluster is TiDB A, set `--start-ts=1`; if the upstream cluster is TiDB B, set `--start-ts=2`.

4. In the configuration file specified by the `--config` parameter, add the following configuration:

    ```toml
    # Whether to enable the bi-directional replication mode
    bdr-mode = true
    ```

After the configuration takes effect, the clusters can perform bi-directional replication.
