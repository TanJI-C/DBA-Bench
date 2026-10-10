# High availability and OOM risk improvements

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0.md`
- Source Title: `What's New in TiDB 5.0`
- Source Heading Path: `What's New in TiDB 5.0 > High availability and disaster recovery | What's New in TiDB 5.0 > High availability and disaster recovery > Improve system availability during Region membership change | What's New in TiDB 5.0 > High availability and disaster recovery > Optimize the memory management module to reduce system OOM risks | What's New in TiDB 5.0 > High availability and disaster recovery > Improve the system availability during network partition`
- Source Line Ranges: `358-375`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `pd`, `tikv`, `tidb`, `sql`
- Topic Tags: `high-availability`, `disaster-recovery`, `region-membership`, `joint-consensus`, `oom-risk`, `memory-management`, `network-partition`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0204_07a9f83e24`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0.md#high-availability-and-disaster-recovery`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f7998869ce7e0af0fd7ff7436a4b23fe9bcd6687c4ee37b51f0ad7dfecfe7d97`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0#high-availability-and-disaster-recovery
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 5.0 high availability changes for Region membership change, Joint Consensus, aggregate-function memory tracking, or OOM behavior controlled by mem-quota-query and oom-action.
- Retrieval Keywords: High availability and disaster recovery, enable-joint-consensus, pd-ctl config set enable-joint-consensus, Raft Joint Consensus, Region membership change, adding a member, deleting a member, mem-quota-query, oom-action, aggregate functions, memory management module, network partition
- Follow-up Guidance: The content references the PD configuration document for enable-joint-consensus.
- Classification Note: This is classified as a release chunk because it introduces TiDB 5.0 availability and memory-management behavior changes, including a default-enabled Joint Consensus feature and aggregate memory tracking.

## Official Source Content

## High availability and disaster recovery
### Improve system availability during Region membership change

[User document](https://docs.pingcap.com/tidb/stable/pd-configuration-file#enable-joint-consensus-new-in-v50), [#18079](https://github.com/pingcap/tidb/issues/18079), [#7587](https://github.com/tikv/tikv/issues/7587), [#2860](https://github.com/tikv/pd/issues/2860)

In the process of Region membership changes, "adding a member" and "deleting a member" are two operations performed in two steps. If a failure occurs when the membership change finishes, the Regions will become unavailable and an error of foreground application is returned.

The introduced Raft Joint Consensus algorithm can improve the system availability during Region membership change. "adding a member" and "deleting a member" operations during the membership change are combined into one operation and sent to all members. During the change process, Regions are in an intermediate state. If any modified member fails, the system is still available.

This feature is enabled by default. You can disable it by running the `pd-ctl config set enable-joint-consensus` command to set the `enable-joint-consensus` value to `false`.
### Optimize the memory management module to reduce system OOM risks

Track the memory usage of aggregate functions. This feature is enabled by default. When SQL statements with aggregate functions are executed, if the total memory usage of the current query exceeds the threshold set by `mem-quota-query`, the system automatically performs operations defined by `oom-action`.
### Improve the system availability during network partition
