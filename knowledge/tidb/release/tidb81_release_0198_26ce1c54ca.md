# High availability during Region membership change and OOM risk reduction

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.0.0-rc.md`
- Source Title: `TiDB 5.0 RC Release Notes`
- Source Heading Path: `TiDB 5.0 RC Release Notes > High availability and disaster recovery | TiDB 5.0 RC Release Notes > High availability and disaster recovery > Improve system availability during Region membership change (experimental) | TiDB 5.0 RC Release Notes > High availability and disaster recovery > Optimize the memory management module to reduce system OOM risks`
- Source Line Ranges: `144-158`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`, `shared`, `dumpling`
- Topic Tags: `high-availability`, `disaster-recovery`, `region-membership`, `raft-joint-consensus`, `pd-ctl`, `experimental`, `oom`, `memory-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0198_26ce1c54ca`
- Source ID: `tidb-docs-8.1:releases/release-5.0.0-rc.md#high-availability-and-disaster-recovery`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6e22b7e1222921f89c0a0fd4a642abee565ace9b7e5e0bd8bdc28fdfc757a66c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.0.0-rc#high-availability-and-disaster-recovery
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.0.0-rc.md

## Retrieval Guidance

- Use When: Use this chunk when searching for release-note details about Region membership change availability, Raft Joint Consensus, `enable-joint-consensus`, or memory consumption reductions related to statistics, Dumpling, and encrypted intermediate results.
- Retrieval Keywords: High availability and disaster recovery, Region membership change, adding a member, deleting a member, Raft Joint Consensus, pd-ctl config set enable-joint-consensus true, enable-joint-consensus, experimental, system availability, foreground application error, memory management module, reduce system OOM risks, caching statistics, Dumpling tool, encrypted intermediate results, store to disk
- Follow-up Guidance: The source provides the exact command `pd-ctl config set enable-joint-consensus true` and links to the user document for `enable-joint-consensus`.
- Classification Note: This is classified as release because it summarizes new high-availability behavior and OOM-risk reduction items introduced in the release notes.

## Official Source Content

## High availability and disaster recovery
### Improve system availability during Region membership change (experimental)

In the process of Region membership changes, "adding a member" and "deleting a member" are two operations performed in two steps. If a failure occurs when the membership change finishes, the Regions will become unavailable and an error of foreground application is returned. The introduced Raft Joint Consensus algorithm can improve the system availability during Region membership change. "adding a member" and "deleting a member" operations during the membership change are combined into one operation and sent to all members. During the change process, Regions are in an intermediate state. If any modified member fails, the system is still available. Users can enable this feature by modifying the membership variable by executing `pd-ctl config set enable-joint-consensus true`. [#7587](https://github.com/tikv/tikv/issues/7587) [#2860](https://github.com/tikv/pd/issues/2860)

+ [User document](https://docs.pingcap.com/tidb/stable/pd-configuration-file#enable-joint-consensus-new-in-v50)
+ Related issue: [#18079](https://github.com/pingcap/tidb/issues/18079)
### Optimize the memory management module to reduce system OOM risks

+ Reduce the memory consumption of caching statistics.
+ Reduce the memory consumption of exporting data using the Dumpling tool.
+ Reduced the memory consumption by storing the encrypted intermediate results of data to the disk.
