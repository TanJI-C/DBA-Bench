# PD replication and deprecated label properties

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-configuration-file.md`
- Source Title: `PD Configuration File`
- Source Heading Path: `PD Configuration File > `replication` | PD Configuration File > `replication` > `max-replicas` | PD Configuration File > `replication` > `location-labels` | PD Configuration File > `replication` > `isolation-level` | PD Configuration File > `replication` > `strictly-match-label` | PD Configuration File > `replication` > `enable-placement-rules` | PD Configuration File > `label-property` (deprecated) | PD Configuration File > `label-property` (deprecated) > `key` (deprecated) | PD Configuration File > `label-property` (deprecated) > `value` (deprecated)`
- Source Line Ranges: `441-490`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `replication`, `replicas`, `topology-labels`, `isolation`, `placement-rules`, `deprecated`, `labels`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0128_1c1fe0b824`
- Source ID: `tidb-docs-8.1:pd-configuration-file.md#replication`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d72c003fd324bc581a7c244a87a5d3049f3ced9ea48cf16256e39a7b4a16fe43`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-configuration-file#replication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-configuration-file.md

## Retrieval Guidance

- Use When: Use this when looking up PD replication settings for replica count, topology labels, isolation level, strict label matching, placement rules, or deprecated `label-property` settings.
- Retrieval Keywords: PD `replication`, max-replicas, location-labels, isolation-level, strictly-match-label, enable-placement-rules, label-property deprecated, reject-leader, key deprecated, value deprecated, Cluster topology configuration, Placement Rules
- Follow-up Guidance: The source notes that starting from v5.2, configuration items related to labels are deprecated and recommends using Placement Rules to configure the replica policy.
- Classification Note: This is a PD replication configuration section because the content defines replica-related options and also includes deprecated label-based leader rejection settings.

## Official Source Content

## `replication`

Configuration items related to replicas
### `max-replicas`

+ The number of replicas, that is, the sum of the number of leaders and followers. The default value `3` means 1 leader and 2 followers. When this configuration is modified dynamically, PD will schedule Regions in the background so that the number of replicas matches this configuration.
+ Default value: `3`
### `location-labels`

+ The topology information of a TiKV cluster
+ Default value: `[]`
+ [Cluster topology configuration](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels)
### `isolation-level`

+ The minimum topological isolation level of a TiKV cluster
+ Default value: `""`
+ [Cluster topology configuration](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels)
### `strictly-match-label`

+ Enables the strict check for whether the TiKV label matches PD's `location-labels`.
+ Default value: `false`
### `enable-placement-rules`

+ Enables `placement-rules`.
+ Default value: `true`
+ See [Placement Rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules).
## `label-property` (deprecated)

Configuration items related to labels, which only support the `reject-leader` type.

> **Note:**
>
> Starting from v5.2, the configuration items related to labels are deprecated. It is recommended to use [Placement Rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules#scenario-2-place-five-replicas-in-three-data-centers-in-the-proportion-of-221-and-the-leader-should-not-be-in-the-third-data-center) to configure the replica policy.
### `key` (deprecated)

+ The label key for the store that rejected the Leader
+ Default value: `""`
### `value` (deprecated)

+ The label value for the store that rejected the Leader
+ Default value: `""`
