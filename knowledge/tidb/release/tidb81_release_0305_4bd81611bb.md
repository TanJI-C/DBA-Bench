# TiDB 6.1.1 overview, compatibility changes, and package updates

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.1.1.md`
- Source Title: `TiDB 6.1.1 Release Notes`
- Source Heading Path: `TiDB 6.1.1 Release Notes | TiDB 6.1.1 Release Notes > Compatibility changes | TiDB 6.1.1 Release Notes > Other changes`
- Source Line Ranges: `5-37`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `ecosystem`
- Topic Tags: `release-overview`, `compatibility`, `system-variables`, `continuous-profiling`, `binary-packages`, `platform-support`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0305_4bd81611bb`
- Source ID: `tidb-docs-8.1:releases/release-6.1.1.md#tidb-6-1-1-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4aa09fb047668d011799f430e78c2d84706777947b33967e8b379e2851fa9554`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.1.1#tidb-6-1-1-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.1.1.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.1.1 release-note items about compatibility changes, continuous profiling default behavior, or package and platform support updates.
- Retrieval Keywords: TiDB 6.1.1 Release Notes, SHOW DATABASES LIKE case-insensitive, #34766, tidb_enable_outer_join_reorder, default value from 1 to 0, Join Reorder support for Outer Join, Continuous Profiling disabled by default, TiFlash crash issue, #5687, TiDB-community-toolkit, server-{version}-linux-amd64.tar.gz, grafana-{version}-linux-amd64.tar.gz, alertmanager-{version}-linux-amd64.tar.gz, prometheus-{version}-linux-amd64.tar.gz, blackbox_exporter-{version}-linux-amd64.tar.gz, node_exporter-{version}-linux-amd64.tar.gz, OS and platform requirements, multi-level support for different quality standards
- Follow-up Guidance: The source also points to TiDB Installation Packages and OS and platform requirements for more details.
- Classification Note: This chunk is classified as a release overview because it summarizes 6.1.1 compatibility changes and other release-level packaging and platform updates across shared components.

## Official Source Content

# TiDB 6.1.1 Release Notes

Release date: September 1, 2022

TiDB version: 6.1.1

Quick access: [Quick start](https://docs.pingcap.com/tidb/v6.1/quick-start-with-tidb) | [Production deployment](https://docs.pingcap.com/tidb/v6.1/production-deployment-using-tiup)
## Compatibility changes

+ TiDB

    - Make the `SHOW DATABASES LIKE …` statement case-insensitive [#34766](https://github.com/pingcap/tidb/issues/34766) @[e1ijah1](https://github.com/e1ijah1)
    - Change the default value of [`tidb_enable_outer_join_reorder`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_outer_join_reorder-new-in-v610) from `1` to `0`, which disables Join Reorder's support for Outer Join by default.

+ Diagnosis

    - Disable the Continuous Profiling feature by default, which avoids the possible TiFlash crash issue that occurs when this feature is enabled. For details, see [#5687](https://github.com/pingcap/tiflash/issues/5687) @[mornyx](https://github.com/mornyx)
## Other changes

- Add the following contents in the `TiDB-community-toolkit` binary package. For details, see [TiDB Installation Packages](https://docs.pingcap.com/tidb/stable/binary-package).

    - `server-{version}-linux-amd64.tar.gz`
    - `grafana-{version}-linux-amd64.tar.gz`
    - `alertmanager-{version}-linux-amd64.tar.gz`
    - `prometheus-{version}-linux-amd64.tar.gz`
    - `blackbox_exporter-{version}-linux-amd64.tar.gz`
    - `node_exporter-{version}-linux-amd64.tar.gz`

- Introduce multi-level support for different quality standards on the combination of operating systems and CPU architectures. See [OS and platform requirements](https://docs.pingcap.com/tidb/v6.1/hardware-and-software-requirements#os-and-platform-requirements).
