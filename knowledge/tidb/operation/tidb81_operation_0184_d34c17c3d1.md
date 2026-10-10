# PD Control installation, usage, flags, and cluster command

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-control.md`
- Source Title: `PD Control User Guide`
- Source Heading Path: `PD Control User Guide | PD Control User Guide > Install PD Control | PD Control User Guide > Install PD Control > Use TiUP command | PD Control User Guide > Install PD Control > Download the installation package | PD Control User Guide > Install PD Control > Compile from source code | PD Control User Guide > Usage | PD Control User Guide > Command line flags | PD Control User Guide > Command line flags > `--cacert` | PD Control User Guide > Command line flags > `--cert` | PD Control User Guide > Command line flags > `--detach` / `-d` | PD Control User Guide > Command line flags > `--help` / `-h` | PD Control User Guide > Command line flags > `--interact` / `-i` | PD Control User Guide > Command line flags > `--key` | PD Control User Guide > Command line flags > `--pd` / `-u` | PD Control User Guide > Command line flags > `--version` / `-V` | PD Control User Guide > Command | PD Control User Guide > Command > `cluster``
- Source Line Ranges: `5-123`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tiup`
- Topic Tags: `installation`, `usage`, `interactive-mode`, `tls`, `command-line-flags`, `cluster-info`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0184_d34c17c3d1`
- Source ID: `tidb-docs-8.1:pd-control.md#pd-control-user-guide`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `56321c93ddddc20faf4a1a3bdeea7a9027ab39294d8bebfdcba7533f1a16d508`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-control#pd-control-user-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-control.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to install or invoke PD Control, its command line flags, TLS parameters, interactive mode, or the `cluster` command that shows basic cluster information.
- Retrieval Keywords: PD Control User Guide, pd-ctl, tiup ctl:v<CLUSTER_VERSION> pd, -u http://<pd_ip>:<pd_port>, --pd, -u, PD_ADDR, --interact, -i, --detach, -d, --cacert, --cert, --key, --version, -V, cluster, To show the cluster information, ctl-{version}-linux-{arch}.tar.gz, make pd-ctl
- Follow-up Guidance: The `cluster` command example shows the returned basic cluster information fields `id` and `max_peer_count`.
- Classification Note: This chunk is classified as operation because the official content covers installation methods, usage modes, command line flags, and the `cluster` command for PD Control.

## Official Source Content

# PD Control User Guide

As a command line tool of PD, PD Control obtains the state information of the cluster and tunes the cluster.
## Install PD Control

> **Note:**
>
> It is recommended that the version of the Control tool you use is consistent with the version of the cluster.
### Use TiUP command

To use PD Control, execute the `tiup ctl:v<CLUSTER_VERSION> pd -u http://<pd_ip>:<pd_port> [-i]` command.
### Download the installation package

To obtain `pd-ctl` of the latest version, download the TiDB server installation package. `pd-ctl` is included in the `ctl-{version}-linux-{arch}.tar.gz` package.

| Installation package                                                                    | OS | Architecture | SHA256 checksum                                                    |
| :------------------------------------------------------------------------ | :------- | :---- | :--------------------------------------------------------------- |
| `https://download.pingcap.com/tidb-community-server-{version}-linux-amd64.tar.gz` (pd-ctl) | Linux | amd64 | `https://download.pingcap.com/tidb-community-server-{version}-linux-amd64.tar.gz.sha256` |
| `https://download.pingcap.com/tidb-community-server-{version}-linux-arm64.tar.gz` (pd-ctl) | Linux | arm64 | `https://download.pingcap.com/tidb-community-server-{version}-linux-arm64.tar.gz.sha256` |

> **Note:**
>
> `{version}` in the link indicates the version number of TiDB. For example, the download link for `v8.1.2` in the `amd64` architecture is `https://download.pingcap.com/tidb-community-server-v8.1.2-linux-amd64.tar.gz`.
### Compile from source code

1. [Go](https://golang.org/) 1.21 or later is required because the Go modules are used.
2. In the root directory of the [PD project](https://github.com/pingcap/pd), use the `make` or `make pd-ctl` command to compile and generate `bin/pd-ctl`.
## Usage

Single-command mode:

```bash
tiup ctl:v<CLUSTER_VERSION> pd store -u http://127.0.0.1:2379
```

Interactive mode:

```bash
tiup ctl:v<CLUSTER_VERSION> pd -i -u http://127.0.0.1:2379
```

Use environment variables:

```bash
export PD_ADDR=http://127.0.0.1:2379
tiup ctl:v<CLUSTER_VERSION> pd
```

Use TLS to encrypt:

```bash
tiup ctl:v<CLUSTER_VERSION> pd -u https://127.0.0.1:2379 --cacert="path/to/ca" --cert="path/to/cert" --key="path/to/key"
```
## Command line flags
### `--cacert`

+ Specifies the path to the certificate file of the trusted CA in PEM format
+ Default: ""
### `--cert`

+ Specifies the path to the certificate of SSL in PEM format
+ Default: ""
### `--detach` / `-d`

+ Uses the single command line mode (not entering readline)
+ Default: true
### `--help` / `-h`

+ Outputs the help information
+ Default: false
### `--interact` / `-i`

+ Uses the interactive mode (entering readline)
+ Default: false
### `--key`

+ Specifies the path to the certificate key file of SSL in PEM format, which is the private key of the certificate specified by `--cert`
+ Default: ""
### `--pd` / `-u`

+ Specifies the PD address
+ Default address: `http://127.0.0.1:2379`
+ Environment variable: `PD_ADDR`
### `--version` / `-V`

+ Prints the version information and exit
+ Default: false
## Command
### `cluster`

Use this command to view the basic information of the cluster.

Usage:

```bash
>> cluster                                     // To show the cluster information
{
  "id": 6493707687106161130,
  "max_peer_count": 3
}
```
