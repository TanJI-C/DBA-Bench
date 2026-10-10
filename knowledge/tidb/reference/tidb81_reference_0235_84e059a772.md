# TiDB Toolkit download links, requirements, and offline package mapping

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/download-ecosystem-tools.md`
- Source Title: `Download TiDB Tools`
- Source Heading Path: `Download TiDB Tools | Download TiDB Tools > Environment requirements | Download TiDB Tools > Download link | Download TiDB Tools > TiDB Toolkit description`
- Source Line Ranges: `5-54`
- Source Scope: `self_managed`
- Primary Component: `ecosystem`
- Related Components: `br`, `dm`, `dumpling`, `lightning`, `pd`, `ticdc`, `tiup`
- Topic Tags: `download`, `offline-packages`, `toolkit`, `environment-requirements`, `linux`, `amd64`, `arm64`, `versioning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0235_84e059a772`
- Source ID: `tidb-docs-8.1:download-ecosystem-tools.md#download-tidb-tools`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c6a6ac558990ac083b6564ca6eef8a730d80b47537518dfd8583aa40226acc55`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/download-ecosystem-tools#download-tidb-tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/download-ecosystem-tools.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs TiDB Toolkit download links, Linux amd64 or arm64 environment requirements, or the offline package names for TiDB tools such as Dumpling, TiDB Lightning, BR, DM, TiCDC, TiUP, and PD Recover.
- Retrieval Keywords: Download TiDB Tools, TiDB Toolkit, Environment requirements, Operating system: Linux, Architecture: amd64 or arm64, https://download.pingcap.com/tidb-community-toolkit-{version}-linux-{arch}.tar.gz, tidb-community-toolkit-v8.1.2-linux-amd64.tar.gz, pd-ctl, https://download.pingcap.com/tidb-community-server-{version}-linux-{arch}.tar.gz, TiDB Toolkit description, offline package name, tiup-linux-{arch}.tar.gz, tiup-{tiup-version}-linux-{arch}.tar.gz, dm-{tiup-version}-linux-{arch}.tar.gz, server-{version}-linux-{arch}.tar.gz, dumpling-{version}-linux-{arch}.tar.gz, tidb-lightning-{version}-linux-{arch}.tar.gz, tidb-lightning-ctl, dm-worker-{version}-linux-{arch}.tar.gz, dm-master-{version}-linux-{arch}.tar.gz, dmctl-{version}-linux-{arch}.tar.gz, cdc-{version}-linux-{arch}.tar.gz, pump-{version}-linux-{arch}.tar.gz, drainer-{version}-linux-{arch}.tar.gz, binlogctl, reparo, br-{version}-linux-{arch}.tar.gz, sync_diff_inspector, pd-recover-{version}-linux-{arch}.tar
- Follow-up Guidance: If the deployment environment has internet access, the content notes that a TiDB tool can be deployed using a single TiUP command, and for Kubernetes it points to TiDB Operator offline installation instead of downloading the TiDB Toolkit.
- Classification Note: The official content is reference material because it lists fixed download URL patterns, environment requirements, and exact offline package mappings for TiDB ecosystem tools.

## Official Source Content

# Download TiDB Tools

This document describes how to download the TiDB Toolkit.

TiDB Toolkit contains frequently used TiDB tools, such as data export tool Dumpling, data import tool TiDB Lightning, and backup and restore tool BR.

> **Tip:**
>
> - If your deployment environment has internet access, you can deploy a TiDB tool using a single [TiUP command](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-management), so there is no need to download the TiDB Toolkit separately.
> - If you need to deploy and maintain TiDB on Kubernetes, instead of downloading the TiDB Toolkit, follow the steps in [TiDB Operator offline installation](https://docs.pingcap.com/tidb-in-kubernetes/stable/deploy-tidb-operator#offline-installation).
## Environment requirements

- Operating system: Linux
- Architecture: amd64 or arm64
## Download link

You can download TiDB Toolkit from the following link:

```
https://download.pingcap.com/tidb-community-toolkit-{version}-linux-{arch}.tar.gz
```

`{version}` in the link indicates the version number of TiDB and `{arch}` indicates the architecture of the system, which can be `amd64` or `arm64`. For example, the download link for `v8.1.2` in the `amd64` architecture is `https://download.pingcap.com/tidb-community-toolkit-v8.1.2-linux-amd64.tar.gz`.

> **Note:**
>
> If you need to download the [PD Control](https://docs.pingcap.com/tidb/stable/pd-control) tool `pd-ctl`, download the TiDB installation package separately from `https://download.pingcap.com/tidb-community-server-{version}-linux-{arch}.tar.gz`.
## TiDB Toolkit description

Depending on which tools you want to use, you can install the corresponding offline packages as follows:

| Tool | Offline package name |
|:------|:----------|
| [TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-overview)  | `tiup-linux-{arch}.tar.gz` <br/>`tiup-{tiup-version}-linux-{arch}.tar.gz` <br/>`dm-{tiup-version}-linux-{arch}.tar.gz` <br/> `server-{version}-linux-{arch}.tar.gz` |
| [Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview)  | `dumpling-{version}-linux-{arch}.tar.gz`  |
| [TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview)  | `tidb-lightning-ctl` <br/>`tidb-lightning-{version}-linux-{arch}.tar.gz`  |
| [TiDB Data Migration (DM)](https://docs.pingcap.com/tidb/stable/dm/dm-overview)  | `dm-worker-{version}-linux-{arch}.tar.gz` <br/>`dm-master-{version}-linux-{arch}.tar.gz` <br/>`dmctl-{version}-linux-{arch}.tar.gz`  |
| [TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview)  | `cdc-{version}-linux-{arch}.tar.gz`  |
| [TiDB Binlog](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview)  | `pump-{version}-linux-{arch}.tar.gz` <br/>`drainer-{version}-linux-{arch}.tar.gz` <br/>`binlogctl` <br/>`reparo`  |
| [Backup & Restore (BR)](https://docs.pingcap.com/tidb/stable/br/backup-and-restore-overview)  | `br-{version}-linux-{arch}.tar.gz`  |
| [sync-diff-inspector](https://docs.pingcap.com/tidb/stable/sync-diff-inspector/sync-diff-inspector-overview)  | `sync_diff_inspector`  |
| [PD Recover](https://docs.pingcap.com/tidb/stable/pd-recover)  | `pd-recover-{version}-linux-{arch}.tar` |

> **Note:**
>
> `{version}` depends on the version of the tool you are installing. `{arch}` depends on the architecture of the system, which can be `amd64` or `arm64`.
