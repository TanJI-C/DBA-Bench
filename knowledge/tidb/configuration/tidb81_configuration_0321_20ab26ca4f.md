# TCP behavior and cross join execution control

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > performance > `tcp-keep-alive` | TiDB Configuration File > performance > `tcp-no-delay` | TiDB Configuration File > performance > `cross-join``
- Source Line Ranges: `541-559`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `tcp`, `keepalive`, `nagle`, `latency`, `join-behavior`, `startup-warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0321_20ab26ca4f`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#tcp-keep-alive`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9ce97e35303979933271dac9e4057fdf2e1c5baef0f52d0ad026fa2cf7ef2dde`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#tcp-keep-alive
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB TCP keepalive or TCP_NODELAY settings, Nagle algorithm behavior, or the `cross-join` configuration and its startup warning.
- Retrieval Keywords: tcp-keep-alive, tcp-no-delay, TCP_NODELAY, Nagle algorithm, keepalive, cross-join, JOIN without any condition, server refuses to execute, cluster will fail to start up
- Follow-up Guidance: It includes the note that setting `cross-join` to `false` when creating a cluster causes the cluster to fail to start up.
- Classification Note: This is classified as configuration content because it documents TiDB performance configuration flags for TCP behavior and cross join execution control.

## Official Source Content

### `tcp-keep-alive`

- Determines whether to enable `keepalive` in the TCP layer.
- Default value: `true`
### `tcp-no-delay`

- Determines whether to enable TCP_NODELAY at the TCP layer. After it is enabled, TiDB disables the Nagle algorithm in the TCP/IP protocol and allows sending small data packets to reduce network latency. This is suitable for latency-sensitive applications with a small transmission volume of data.
- Default value: `true`
### `cross-join`

- Default value: `true`
- TiDB supports executing the `JOIN` statement without any condition (the `WHERE` field) of both sides tables by default; if you set the value to `false`, the server refuses to execute when such a `JOIN` statement appears.

> **Note:**
>
> When creating a cluster, **DO NOT** set `cross-join` to false. Otherwise, the cluster will fail to start up.
