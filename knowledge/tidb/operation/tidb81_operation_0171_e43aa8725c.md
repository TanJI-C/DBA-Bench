# Install and update migration tools with TiUP

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/migration-tools.md`
- Source Title: `TiDB Migration Tools Overview`
- Source Heading Path: `TiDB Migration Tools Overview > Install tools using TiUP | TiDB Migration Tools Overview > Install tools using TiUP > Step 1. Install TiUP | TiDB Migration Tools Overview > Install tools using TiUP > Step 2. Install components | TiDB Migration Tools Overview > Install tools using TiUP > Step 3. Update TiUP and its components (optional) | TiDB Migration Tools Overview > See also`
- Source Line Ranges: `88-166`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`, `lightning`, `br`, `ticdc`, `shared`
- Topic Tags: `installation`, `package-management`, `component-install`, `component-list`, `version-selection`, `update`, `offline-deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0171_e43aa8725c`
- Source ID: `tidb-docs-8.1:migration-tools.md#install-tools-using-tiup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3ed0b79312f1c5861d7214a019e0d57499d5e8ae05ad79dfab963a0d938806a7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/migration-tools#install-tools-using-tiup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/migration-tools.md

## Retrieval Guidance

- Use When: Use this section when you need the TiUP commands to install, list, version-pin, or update TiDB migration tool components.
- Retrieval Keywords: Install tools using TiUP, Since TiDB v4.0, tiup list, tiup install dm, tiup install dm tidb-lightning, tiup install <component>[:version], tiup update --self && tiup update dm, curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh, source ~/.bash_profile, available components, dm, dmctl, tidb-lightning, br, cdc, tikv-br, tikv-cdc
- Follow-up Guidance: The source points to Deploy TiUP offline and Download and install tools in binary for related installation methods.
- Classification Note: This chunk is classified as operation because it provides step-by-step commands to install TiUP, install components, and optionally update TiUP and its components.

## Official Source Content

## Install tools using TiUP

Since TiDB v4.0, TiUP acts as a package manager that helps you manage different cluster components in the TiDB ecosystem. Now you can manage any cluster component using a single command.
### Step 1. Install TiUP

```shell
curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
```

Redeclare the global environment variable:

```shell
source ~/.bash_profile
```
### Step 2. Install components

You can use the following command to see the available components:

```shell
tiup list
```

The command outputs the available components:

```bash
Available components:
Name            Owner      Description
----            -----      -----------
PCC             community  A tool used to capture plan changes among different versions of TiDB
bench           pingcap    Benchmark database with different workloads
br              pingcap    TiDB/TiKV cluster backup restore tool.
cdc             pingcap    CDC is a change data capture tool for TiDB
chaosd          community  An easy-to-use Chaos Engineering tool used to inject failures to a physical node
client          pingcap    Client to connect playground
cloud           pingcap    CLI tool to manage TiDB Cloud
cluster         pingcap    Deploy a TiDB cluster for production
ctl             pingcap    TiDB controller suite
dm              pingcap    Data Migration Platform manager
dmctl           pingcap    dmctl component of Data Migration Platform.
errdoc          pingcap    Document about TiDB errors
pd-recover      pingcap    PD Recover is a disaster recovery tool of PD, used to recover the PD cluster which cannot start or provide services normally.
playground      pingcap    Bootstrap a local TiDB cluster for fun
tidb            pingcap    TiDB is an open source distributed HTAP database compatible with the MySQL protocol.
tidb-dashboard  pingcap    TiDB Dashboard is a Web UI for monitoring, diagnosing, and managing the TiDB cluster
tidb-lightning  pingcap    TiDB Lightning is a tool used for fast full import of large amounts of data into a TiDB cluster
tikv-br         pingcap    TiKV cluster backup restore tool
tikv-cdc        pingcap    TiKV-CDC is a change data capture tool for TiKV
tiproxy         pingcap    TiProxy is a database proxy that is based on TiDB.
tiup            pingcap    TiUP is a command-line component management tool that can help to download and install TiDB platform components to the local system
```

Install one or more components that you need. For example:

```shell
tiup install dm
```

```shell
tiup install dm tidb-lightning
```

> **Note:**
>
> To install a component of a specific version, use the `tiup install <component>[:version]` command.
### Step 3. Update TiUP and its components (optional)

It is recommended to see the release log and compatibility notes of the new version.

```shell
tiup update --self && tiup update dm
```
## See also

- [Deploy TiUP offline](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#deploy-tiup-offline)
- [Download and install tools in binary](https://docs.pingcap.com/tidb/stable/download-ecosystem-tools)
