# TiKV stability and usability release features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.2.0.md`
- Source Title: `TiDB 6.2.0 Release Notes`
- Source Heading Path: `TiDB 6.2.0 Release Notes > New features > Stability | TiDB 6.2.0 Release Notes > New features > Ease of use`
- Source Line Ranges: `143-162`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: none
- Topic Tags: `cpu-usage-tuning`, `background-requests`, `statistics-collection`, `configuration-info`, `command-line-flags`, `experimental`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0325_cfbbf74cb0`
- Source ID: `tidb-docs-8.1:releases/release-6.2.0.md#stability`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f174bcec7a33d3f7bd0af892217cf97c00e2b32609e3c8482f4056156aba33ab`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.2.0#stability
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.2.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.2.0 release-note information about TiKV background CPU usage tuning or the tikv-server flag for listing configuration information.
- Retrieval Keywords: TiDB 6.2.0 Stability, TiDB 6.2.0 Ease of use, TiKV automatically tuning the CPU usage experimental, background requests CPU usage rate, background operations automatically collecting statistics in TiKV, TiKV configuration file background-quota-limiter, automatically adjusting CPU usage disabled by default, tikv-server --config-info, --config-info format, default and current values of all TiKV configuration items, startup parameters of the TiKV process
- Follow-up Guidance: The content links to the TiKV configuration file documentation for background-quota-limiter and the command-line flags documentation for --config-info.
- Classification Note: This is classified as a release chunk because it lists TiKV stability and ease-of-use features newly introduced in TiDB 6.2.0.

## Official Source Content

### Stability

* TiKV supports automatically tuning the CPU usage (experimental)

    Databases usually have background processes to perform internal operations. Statistical information can be collected to help identify performance problems, generate better execution plans, and improve the stability and performance of the database. However, how to more efficiently collect information, and how to balance the resource overhead of background operations and foreground operations without affecting the daily use have always been one of the headaches in the database industry.

    Starting from v6.2.0, TiDB supports setting the CPU usage rate of background requests using the TiKV configuration file, thereby limiting the CPU usage ratio of background operations such as automatically collecting statistics in TiKV, and avoiding the resource preemption of user operations by background operations in extreme cases. This ensures that the operations of the database are stable and efficient.

    At the same time, TiDB also supports automatically adjusting CPU usage. Then, TiKV will adaptively adjust the CPU resources occupied by background requests according to the CPU usage of the instance. This feature is disabled by default.

    [User document](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#background-quota-limiter) [#12503](https://github.com/tikv/tikv/issues/12503) @[BornChanger](https://github.com/BornChanger)
### Ease of use

* TiKV supports listing detailed configuration information using command-line flags

    The TiKV configuration file can be used to manage TiKV instances. However, for instances that run for a long time and are managed by different users, it is difficult to know which configuration item has been modified and what the default value is. This might cause confusion when you upgrade the cluster or migrate data. Since TiDB v6.2.0, tikv-server supports a new command-line flag [`—-config-info`](https://docs.pingcap.com/tidb/stable/command-line-flags-for-tikv-configuration#--config-info-format) that lists default and current values of all TiKV configuration items, helps users to quickly verify the startup parameters of the TiKV process, and improves usability.

    [User document](https://docs.pingcap.com/tidb/stable/command-line-flags-for-tikv-configuration#--config-info-format) [#12492](https://github.com/tikv/tikv/issues/12492) @[glorv](https://github.com/glorv)
