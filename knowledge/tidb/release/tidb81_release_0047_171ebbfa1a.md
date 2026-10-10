# PD release features and fixes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1-rc.1.md`
- Source Title: `TiDB 2.1 RC1 Release Notes`
- Source Heading Path: `TiDB 2.1 RC1 Release Notes > PD`
- Source Line Ranges: `102-128`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: none
- Topic Tags: `version control`, `rolling update`, `region merge`, `batch split`, `scheduling`, `hotspot statistics`, `pd-ctl`, `etcd`, `bug fixes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0047_171ebbfa1a`
- Source ID: `tidb-docs-8.1:releases/release-2.1-rc.1.md#pd`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2d7e7e58537c3c8ed2552d93fd0b1ff4fd620463897a5cd037c4f9502d27360d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1-rc.1#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1-rc.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for PD changes in TiDB 2.1 RC1 such as rolling update compatibility, region merge, batch Region split, scheduling controls, hotspot statistics, pd-ctl capabilities, etcd metrics, and PD bug fixes.
- Retrieval Keywords: PD, TiDB 2.1 RC1, version control mechanism, rolling update, compatibility, region merge, GetPrevRegion, splitting Regions in batch, GC safepoint, TSO allocation, system clock going backwards, Region heartbeats, Region tree, hotspot statistics, error code of API interface, controlling scheduling strategies, special characters in label, scheduling simulator, pd-ctl, splitting Regions using statistics, jq, JSON output, etcd Raft state machine, namespace is not reloaded after switching Leader, namespace scheduling exceeds the schedule limit, hotspot scheduling exceeds the schedule limit, wrong logs are output when the PD client closes, wrong statistics of Region heartbeat latency
- Follow-up Guidance: The same source section distinguishes PD content into Features, Improvements, and Bug fixes for TiDB 2.1 RC1.
- Classification Note: This is a PD release-note chunk for self-managed TiDB 2.1 RC1 covering newly introduced features, performance and scheduling improvements, metrics additions, and fixed PD issues.

## Official Source Content

## PD

- Features
    - Introduce the version control mechanism and support rolling update of the cluster with compatibility
    - Enable the `region merge` feature
    - Support the `GetPrevRegion` interface
    - Support splitting Regions in batch
    - Support storing the GC safepoint
- Improvements
    - Optimize the issue that TSO allocation is affected by the system clock going backwards
    - Optimize the performance of handling Region heartbeats
    - Optimize the Region tree performance
    - Optimize the performance of computing hotspot statistics
    - Optimize returning the error code of API interface
    - Add options of controlling scheduling strategies
    - Prohibit using special characters in `label`
    - Improve the scheduling simulator
    - Support splitting Regions using statistics in pd-ctl
    - Support formatting JSON output by calling `jq` in pd-ctl
    - Add metrics about etcd Raft state machine
- Bug fixes
    - Fix the issue that the namespace is not reloaded after switching Leader
    - Fix the issue that namespace scheduling exceeds the schedule limit
    - Fix the issue that hotspot scheduling exceeds the schedule limit
    - Fix the issue that wrong logs are output when the PD client closes
    - Fix the wrong statistics of Region heartbeat latency
