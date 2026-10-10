# Unified Sorter behavior and verification

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-manage-changefeed.md`
- Source Title: `Manage Changefeeds`
- Source Heading Path: `Manage Changefeeds > Unified Sorter`
- Source Line Ranges: `273-297`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `pd`
- Topic Tags: `changefeed`, `unified-sorter`, `sort-engine`, `db-sorter`, `oom`, `disk-space`, `checkpoint-ts`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0257_f3eaca4671`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-manage-changefeed.md#unified-sorter`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e71b9a747993df81b35a7fa66ddc81c0efddb49ec86dcc516530ffc907d42cee`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-manage-changefeed#unified-sorter
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-manage-changefeed.md

## Retrieval Guidance

- Use When: Use this chunk when checking Unified Sorter behavior for a TiCDC changefeed, including how to verify whether `sort_engine` is set to `unified` and what storage considerations are documented.
- Retrieval Keywords: Unified Sorter, DB Sorter, sort engine, sort_engine, cdc cli --server, changefeed query, grep 'sort_engine', value of sort_engine is "unified", OOM problems, data_dir, checkpoint-ts, free disk space greater than or equal to 500 GiB
- Follow-up Guidance: The content provides a `cdc cli --server="http://10.0.10.25:8300" changefeed query --changefeed-id=simple-replication-task | grep 'sort_engine'` example and notes that temporary files are stored in `data_dir`.
- Classification Note: This is classified as operation because the content explains runtime sorter behavior, verification of an existing changefeed setting, and operational disk-space considerations.

## Official Source Content

## Unified Sorter

> **Note:**
>
> Starting from v6.0.0, TiCDC uses the DB Sorter engine by default, and no longer uses the Unified Sorter. It is recommended that you do not configure the `sort engine` item.

Unified sorter is the sorting engine in TiCDC. It can mitigate OOM problems caused by the following scenarios:

+ The data replication task in TiCDC is paused for a long time, during which a large amount of incremental data is accumulated and needs to be replicated.
+ The data replication task is started from an early timestamp so it becomes necessary to replicate a large amount of incremental data.

For the changefeeds created using `cdc cli` after v4.0.13, Unified Sorter is enabled by default; for the changefeeds that have existed before v4.0.13, the previous configuration is used.

To check whether or not the Unified Sorter feature is enabled on a changefeed, you can run the following example command (assuming the IP address of the PD instance is `http://10.0.10.25:2379`):

```shell
cdc cli --server="http://10.0.10.25:8300" changefeed query --changefeed-id=simple-replication-task | grep 'sort_engine'
```

In the output of the above command, if the value of `sort_engine` is "unified", it means that Unified Sorter is enabled on the changefeed.

> **Note:**
>
> + If your servers use mechanical hard drives or other storage devices that have high latency or limited bandwidth, the performance of Unified Sorter will be affected significantly.
> + By default, Unified Sorter uses `data_dir` to store temporary files. It is recommended to ensure that the free disk space is greater than or equal to 500 GiB. For production environments, it is recommended to ensure that the free disk space on each node is greater than (the maximum `checkpoint-ts` delay allowed by the business) * (upstream write traffic at business peak hours). In addition, if you plan to replicate a large amount of historical data after `changefeed` is created, make sure that the free space on each node is greater than the amount of the replicated data.
