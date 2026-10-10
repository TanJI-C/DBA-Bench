# TiDB community server and toolkit package contents

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/binary-package.md`
- Source Title: `TiDB Installation Packages`
- Source Heading Path: `TiDB Installation Packages`
- Source Line Ranges: `5-77`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiup`, `tidb`, `tikv`, `pd`, `tiflash`, `tiproxy`, `br`, `lightning`, `dumpling`, `ticdc`, `dm`
- Topic Tags: `binary-packages`, `offline-deployment`, `package-contents`, `architectures`, `versioned-artifacts`, `toolkit`, `server-package`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0022_a55daa5c2d`
- Source ID: `tidb-docs-8.1:binary-package.md#tidb-installation-packages`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bf182b65d606bb4b9e1e4d8471bc408bd90fbedad6315a037a3412839cd1f7a9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/binary-package#tidb-installation-packages
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/binary-package.md

## Retrieval Guidance

- Use When: Use this chunk when identifying what files are included in the `TiDB-community-server` or `TiDB-community-toolkit` binary packages for offline TiUP preparation on `amd64` or `arm64`.
- Retrieval Keywords: TiDB Installation Packages, TiDB-community-server, TiDB-community-toolkit, Prepare the TiUP offline component package, deploy TiUP offline, amd64, arm64, tidb-{version}-linux-{arch}.tar.gz, tikv-{version}-linux-{arch}.tar.gz, tiflash-{version}-linux-{arch}.tar.gz, pd-{version}-linux-{arch}.tar.gz, ctl-{version}-linux-{arch}.tar.gz, grafana-{version}-linux-{arch}.tar.gz, alertmanager-{version}-linux-{arch}.tar.gz, blackbox_exporter_{version}-linux-{arch}.tar.gz, prometheus-{version}-linux-{arch}.tar.gz, node_exporter-{version}-linux-{arch}.tar.gz, tiup-linux-{arch}.tar.gz, tiup-{version}-linux-{arch}.tar.gz, local_install.sh, cluster-{version}-linux-{arch}.tar.gz, insight-{version}-linux-{arch}.tar.gz, diag-{version}-linux-{arch}.tar.gz, influxdb-{version}-linux-{arch}.tar.gz, playground-{version}-linux-{arch}.tar.gz, tiproxy-{version}-linux-{arch}.tar.gz, pd-recover-{version}-linux-{arch}.tar.gz, etcdctl, tidb-lightning-{version}-linux-{arch}.tar.gz, tidb-lightning-ctl, dumpling-{version}-linux-{arch}.tar.gz, cdc-{version}-linux-{arch}.tar.gz, dm-{version}-linux-{arch}.tar.gz, dm-worker-{version}-linux-{arch}.tar.gz, dm-master-{version}-linux-{arch}.tar.gz, dmctl-{version}-linux-{arch}.tar.gz, br-{version}-linux-{arch}.tar.gz, package-{version}-linux-{arch}.tar.gz, bench-{version}-linux-{arch}.tar.gz, errdoc-{version}-linux-{arch}.tar.gz, dba-{version}-linux-{arch}.tar.gz, PCC-{version}-linux-{arch}.tar.gz, pump-{version}-linux-{arch}.tar.gz, drainer-{version}-linux-{arch}.tar.gz, binlogctl, sync_diff_inspector, reparo, server-{version}-linux-{arch}.tar.gz
- Follow-up Guidance: The source also points to `Deploy TiUP offline` and `Prepare the TiUP offline component package` for the related offline deployment context.
- Classification Note: This is reference content because it enumerates the package contents, architectures, and versioned artifact names for the two TiDB binary packages.

## Official Source Content

# TiDB Installation Packages

Before [deploying TiUP offline](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#deploy-tiup-offline), you need to download the binary packages of TiDB as described in [Prepare the TiUP offline component package](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#prepare-the-tiup-offline-component-package).

TiDB binary packages are available in amd64 and arm64 architectures. In either architecture, TiDB provides two binary packages: `TiDB-community-server` and `TiDB-community-toolkit`.

The `TiDB-community-server` package contains the following contents.

| Content | Change history |
|---|---|
| tidb-{version}-linux-{arch}.tar.gz |  |
| tikv-{version}-linux-{arch}.tar.gz |  |
| tiflash-{version}-linux-{arch}.tar.gz |  |
| pd-{version}-linux-{arch}.tar.gz |  |
| ctl-{version}-linux-{arch}.tar.gz |  |
| grafana-{version}-linux-{arch}.tar.gz |  |
| alertmanager-{version}-linux-{arch}.tar.gz |  |
| blackbox_exporter-{version}-linux-{arch}.tar.gz |  |
| prometheus-{version}-linux-{arch}.tar.gz |  |
| node_exporter-{version}-linux-{arch}.tar.gz |  |
| tiup-linux-{arch}.tar.gz |  |
| tiup-{version}-linux-{arch}.tar.gz |  |
| local_install.sh |  |
| cluster-{version}-linux-{arch}.tar.gz |  |
| insight-{version}-linux-{arch}.tar.gz |  |
| diag-{version}-linux-{arch}.tar.gz | New in v6.0.0 |
| influxdb-{version}-linux-{arch}.tar.gz |  |
| playground-{version}-linux-{arch}.tar.gz |  |
| tiproxy-{version}-linux-{arch}.tar.gz | New in v7.6.0 |

> **Note:**
>
> `{version}` depends on the version of the component or server you are installing. `{arch}` depends on the architecture of the system, which can be `amd64` or `arm64`.

The `TiDB-community-toolkit` package contains the following contents.

| Content | Change history |
|---|---|
| pd-recover-{version}-linux-{arch}.tar.gz |  |
| etcdctl | New in v6.0.0 |
| tiup-linux-{arch}.tar.gz |  |
| tiup-{version}-linux-{arch}.tar.gz |  |
| tidb-lightning-{version}-linux-{arch}.tar.gz |  |
| tidb-lightning-ctl |  |
| dumpling-{version}-linux-{arch}.tar.gz |  |
| cdc-{version}-linux-{arch}.tar.gz |  |
| dm-{version}-linux-{arch}.tar.gz |  |
| dm-worker-{version}-linux-{arch}.tar.gz |  |
| dm-master-{version}-linux-{arch}.tar.gz |  |
| dmctl-{version}-linux-{arch}.tar.gz |  |
| br-{version}-linux-{arch}.tar.gz |  |
| package-{version}-linux-{arch}.tar.gz |  |
| bench-{version}-linux-{arch}.tar.gz |  |
| errdoc-{version}-linux-{arch}.tar.gz |  |
| dba-{version}-linux-{arch}.tar.gz |  |
| PCC-{version}-linux-{arch}.tar.gz |  |
| pump-{version}-linux-{arch}.tar.gz |  |
| drainer-{version}-linux-{arch}.tar.gz |  |
| binlogctl | New in v6.0.0 |
| sync_diff_inspector |  |
| reparo |  |
| server-{version}-linux-{arch}.tar.gz | New in v6.2.0 |
| grafana-{version}-linux-{arch}.tar.gz | New in v6.2.0 |
| alertmanager-{version}-linux-{arch}.tar.gz | New in v6.2.0 |
| prometheus-{version}-linux-{arch}.tar.gz | New in v6.2.0 |
| blackbox_exporter-{version}-linux-{arch}.tar.gz | New in v6.2.0  |
| node_exporter-{version}-linux-{arch}.tar.gz | New in v6.2.0  |

> **Note:**
>
> `{version}` depends on the version of the tool you are installing. `{arch}` depends on the architecture of the system, which can be `amd64` or `arm64`.
