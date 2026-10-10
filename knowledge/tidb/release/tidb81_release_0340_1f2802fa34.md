# TiCDC replication and upgrade features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.3.0.md`
- Source Title: `TiDB 6.3.0 Release Notes`
- Source Heading Path: `TiDB 6.3.0 Release Notes > New features > TiDB data share subscription | TiDB 6.3.0 Release Notes > Compatibility changes`
- Source Line Ranges: `194-209`
- Source Scope: `all`
- Primary Component: `ticdc`
- Related Components: `tiup`, `operator`
- Topic Tags: `geo-distributed-replication`, `sync-point`, `disaster-recovery`, `graceful-upgrade`, `replication-latency`, `compatibility-changes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0340_1f2802fa34`
- Source ID: `tidb-docs-8.1:releases/release-6.3.0.md#tidb-data-share-subscription`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c6daa8ef91c71cb788c27bbc883c7b3dad5d30c3c3874a5428d69b68b0188f20`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.3.0#tidb-data-share-subscription
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.3.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.3.0 TiCDC features for geo-distributed replication, sync point consistency, or graceful upgrade behavior with TiUP or TiDB Operator.
- Retrieval Keywords: TiDB 6.3.0 TiCDC, multiple geo-distributed data sources, deploy TiCDC in multiple IDCs, geo-distributed data replication, sync point, upstream downstream snapshot consistent, disaster recovery, ticdc-upstream-downstream-check, graceful upgrade, TiUP >=v1.11.0, TiDB Operator >=v1.3.8, replication latency as low as 30 seconds, latency-sensitive applications
- Follow-up Guidance: The content specifies that graceful upgrade applies when TiCDC is deployed using TiUP (>=v1.11.0) or TiDB Operator (>=v1.3.8), and that replication latency is kept as low as 30 seconds during the upgrade.
- Classification Note: This is a release-note chunk for TiCDC new features and compatibility context, focused on replication topology, snapshot consistency, and upgrade behavior.

## Official Source Content

### TiDB data share subscription

* TiCDC supports a deployment topology that can replicate data from multiple geo-distributed data sources [#5301](https://github.com/pingcap/tiflow/issues/5301) @[sdojjy](https://github.com/sdojjy)

    To support replicating data from a single TiDB cluster to multiple geo-distributed data systems, starting from v6.3.0, [you can deploy TiCDC in multiple IDCs](https://docs.pingcap.com/tidb/stable/ticdc/deploy-ticdc) to replicate data for each IDC. This feature helps deliver the capability of geo-distributed data replication and deployment topology.

* TiCDC supports keeping the snapshots consistent between the upstream and the downstream (sync point) [#6977](https://github.com/pingcap/tiflow/issues/6977) @[asddongmen](https://github.com/asddongmen)

    In the scenarios of data replication for disaster recovery, TiCDC supports [periodically maintaining a downstream data snapshot](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-upstream-downstream-check) so that the downstream snapshot is consistent with the upstream snapshot. With this feature, TiCDC can better support the scenarios where reads and writes are separate, and help you lower the cost.

* TiCDC supports graceful upgrade [#4757](https://github.com/pingcap/tiflow/issues/4757) @[overvenus](https://github.com/overvenus) @[3AceShowHand](https://github.com/3AceShowHand)

    When TiCDC is deployed using [TiUP](https://docs.pingcap.com/tidb/stable/ticdc/deploy-ticdc#upgrade-cautions) (>=v1.11.0) or [TiDB Operator](https://docs.pingcap.com/tidb-in-kubernetes/v1.3/configure-a-tidb-cluster#configure-graceful-upgrade-for-ticdc-cluster) (>=v1.3.8), you can gracefully upgrade the TiCDC cluster. During the upgrade, data replication latency is kept as low as 30 seconds. This improves stability, empowering TiCDC to better support latency-sensitive applications.
## Compatibility changes
