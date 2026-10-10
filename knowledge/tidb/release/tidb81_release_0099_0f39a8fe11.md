# TiKV, PD, tools, and TiDB Ansible release changes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-3.0.1.md`
- Source Title: `TiDB 3.0.1 Release Notes`
- Source Heading Path: `TiDB 3.0.1 Release Notes > TiKV | TiDB 3.0.1 Release Notes > PD | TiDB 3.0.1 Release Notes > Tools | TiDB 3.0.1 Release Notes > TiDB Ansible`
- Source Line Ranges: `52-91`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tikv`, `pd`, `lightning`
- Topic Tags: `release-notes`, `titan`, `monitoring`, `blob-files`, `deadlocks`, `hot-region-scheduling`, `region-merge`, `grpc-gateway`, `binlog`, `pump-gc`, `import-fix`, `ansible-precheck`, `disk-space`, `dashboards`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0099_0f39a8fe11`
- Source ID: `tidb-docs-8.1:releases/release-3.0.1.md#tikv`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `116125a774adcff7eb00ffe7af926b43d0b4b8fd50f0c498e49e58b5bfe48f96`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-3.0.1#tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-3.0.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 3.0.1 release-note changes in TiKV, PD, TiDB Binlog, TiDB Lightning, or TiDB Ansible, especially Titan, hot Region scheduling, gRPC gateway, Pump GC, import fixes, and monitoring updates.
- Retrieval Keywords: TiKV 3.0.1 release notes, PD 3.0.1 release notes, TiDB Binlog Pump GC, TiDB Lightning lowercase column names import error, Titan engine, blob_run_mode, blob-run-mode, normal read-only fallback, blob files statistics, deadlocks, enable-grpc-gateway, store-balance-rate, hot-region-schedule-limit, hot Region scheduling, Region merge, random-merge, admin-merge-region, Region key hexadecimal notation, ansible precheck, jmespath, jinja2, stop-write-at-available-space, Disk Latency, TiKV details dashboard Titan
- Follow-up Guidance: The chunk also covers PD scheduling fixes and optimizations, TiKV pessimistic transaction read fixes, and TiDB Ansible dashboard and monitoring updates.
- Classification Note: This is classified as a shared release-notes chunk because the official content groups TiKV, PD, Tools, and TiDB Ansible changes from the TiDB 3.0.1 release.

## Official Source Content

## TiKV

- Add the statistics of the size of blob files in statistics information [#5060](https://github.com/tikv/tikv/pull/5060)
- Fix the core dump issue caused by the incorrectly cleaned memory resources when the process exits [#5053](https://github.com/tikv/tikv/pull/5053)
- Add all monitoring metrics related to the Titan engine [#4772](https://github.com/tikv/tikv/pull/4772), [#4836](https://github.com/tikv/tikv/pull/4836)
- Add the number of open file handles for Titan when counting the number of open file handles to avoid the issue that no file handle is available because of inaccurate statistics of file handles [#5026](https://github.com/tikv/tikv/pull/5026)
- Set `blob_run_mode` to decide whether to enable the Titan engine on a specific CF [#4991](https://github.com/tikv/tikv/pull/4991)
- Fix the issue that the read operations cannot get the commit information of pessimistic transactions [#5067](https://github.com/tikv/tikv/pull/5067)
- Add the `blob-run-mode` configuration parameter to control the running mode of the Titan engine, and its value can be `normal`, `read-only` or `fallback` [#4865](https://github.com/tikv/tikv/pull/4865)
- Improve the performance of detecting deadlocks [#5089](https://github.com/tikv/tikv/pull/5089)
## PD

- Fix the issue that the scheduling limit is automatically adjusted to 0 when PD schedules hot Regions [#1552](https://github.com/pingcap/pd/pull/1552)
- Add the `enable-grpc-gateway` configuration option to enable the gRPC gateway feature of etcd [#1596](https://github.com/pingcap/pd/pull/1596)
- Add `store-balance-rate`, `hot-region-schedule-limit` and other statistics related to scheduler configuration [#1601](https://github.com/pingcap/pd/pull/1601)
- Optimize the hot Region scheduling strategy and skip the Regions that lack replicas during scheduling to prevent multiple replicas from being scheduled to the same IDC [#1609](https://github.com/pingcap/pd/pull/1609)
- Optimize the Region merge processing logic and support giving priority to merging the Regions with smaller sizes to speed up Region merging [#1613](https://github.com/pingcap/pd/pull/1613)
- Adjust the default limit of hot Region scheduling in a single time to 64 to prevent too many scheduling tasks from occupying system resources and impacting performance [#1616](https://github.com/pingcap/pd/pull/1616)
- Optimize the Region scheduling strategy and support giving high priority to scheduling Regions in the `Pending` status [#1617](https://github.com/pingcap/pd/pull/1617)
- Fix the issue that `random-merge` and `admin-merge-region` operators cannot be added [#1634](https://github.com/pingcap/pd/pull/1634)
- Adjust the format of the Region key in the log to hexadecimal notation to make it easier to view [#1639](https://github.com/pingcap/pd/pull/1639)
## Tools

TiDB Binlog

- Optimize the Pump GC strategy and remove the restriction that the unconsumed binlog cannot be cleaned to make sure that the resources are not occupied for a long time [#646](https://github.com/pingcap/tidb-binlog/pull/646)

TiDB Lightning

- Fix the import error that happens when the column names specified by the SQL dump are not in lowercase [#210](https://github.com/pingcap/tidb-lightning/pull/210)
## TiDB Ansible

- Add the precheck feature for the ansible command and its `jmespath` and `jinja2` dependency packages [#803](https://github.com/pingcap/tidb-ansible/pull/803), [#813](https://github.com/pingcap/tidb-ansible/pull/813)
- Add the `stop-write-at-available-space` parameter (10 GiB by default) in Pump to stop writing binlog files in Pump when the available disk space is less than the parameter value [#806](https://github.com/pingcap/tidb-ansible/pull/806)
- Update the I/O monitoring items in the TiKV monitoring information and make them compatible with the monitoring components of the new version [#820](https://github.com/pingcap/tidb-ansible/pull/820)
- Update the PD monitoring information, and fix the anomaly that Disk Latency is empty in the disk performance dashboard [#817](https://github.com/pingcap/tidb-ansible/pull/817)
- Add monitoring items for Titan in the TiKV details dashboard [#824](https://github.com/pingcap/tidb-ansible/pull/824)
