# TiDB Lightning deployment and upgrade

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/deploy-tidb-lightning.md`
- Source Title: `Deploy TiDB Lightning`
- Source Heading Path: `Deploy TiDB Lightning | Deploy TiDB Lightning > Online deployment using TiUP (recommended) | Deploy TiDB Lightning > Manual deployment | Deploy TiDB Lightning > Manual deployment > Download TiDB Lightning binaries | Deploy TiDB Lightning > Manual deployment > Upgrade TiDB Lightning`
- Source Line Ranges: `5-46`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tiup`, `ecosystem`, `tidb`
- Topic Tags: `deployment`, `installation`, `manual-deployment`, `tiup`, `binaries`, `upgrade`, `restart`, `version-compatibility`, `import-tasks`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0450_296e1d7aa5`
- Source ID: `tidb-docs-8.1:tidb-lightning/deploy-tidb-lightning.md#deploy-tidb-lightning`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d80fb032b9ea60e949cbef8691e4fcb04fcd01dd9f6b8ba17a0f09b0b7907ac2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/deploy-tidb-lightning#deploy-tidb-lightning
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/deploy-tidb-lightning.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to deploy TiDB Lightning with TiUP or manually, including downloading binaries and upgrade or restart considerations.
- Retrieval Keywords: Deploy TiDB Lightning, TiDB Lightning deployment and upgrade, Online deployment using TiUP, tiup install tidb-lightning, Manual deployment, Download TiDB Lightning binaries, Download TiDB Tools, tidb-lightning executable, tar -zxvf tidb-lightning-${version}-linux-amd64.tar.gz, chmod +x tidb-lightning, Upgrade TiDB Lightning, replace the binaries alone, restart TiDB Lightning, checkpoints work across versions, import task is running
- Follow-up Guidance: For restart details after upgrade, see How to properly restart TiDB Lightning.
- Classification Note: This chunk is classified as self-managed Lightning operation content because it describes deployment methods, binary installation, upgrade behavior, and restart notes for TiDB Lightning.

## Official Source Content

# Deploy TiDB Lightning

This document describes the hardware requirements of using TiDB Lightning to import data, and how to deploy it manually. Requirements on hardware resources vary with the import modes. For details, refer to the following docs:

- [Physical Import Mode Requirements and Limitations](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode#requirements-and-restrictions)
- [Logical Import Mode Requirements and Limitations](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode)
## Online deployment using TiUP (recommended)

1. Install TiUP using the following command:

    ```shell
    curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
    ```

    This command automatically adds TiUP to the `PATH` environment variable. You need to start a new terminal session or run `source ~/.bashrc` before you can use TiUP. (According to your environment, you may need to run `source ~/.profile`. For the specific command, check the output of TiUP.)

2. Install TiDB Lightning using TiUP:

    ```shell
    tiup install tidb-lightning
    ```
## Manual deployment
### Download TiDB Lightning binaries

Refer to [Download TiDB Tools](https://docs.pingcap.com/tidb/stable/download-ecosystem-tools) and download TiDB Lightning binaries. TiDB Lightning is completely compatible with early versions of TiDB. It is recommended to use the latest version of TiDB Lightning.

Unzip the TiDB Lightning binary package to obtain the `tidb-lightning` executable file:

```bash
tar -zxvf tidb-lightning-${version}-linux-amd64.tar.gz
chmod +x tidb-lightning
```
### Upgrade TiDB Lightning

You can upgrade TiDB Lightning by replacing the binaries alone without further configurations. After the upgrade, you need to restart TiDB Lightning. For details, see [How to properly restart TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-faq#how-to-properly-restart-tidb-lightning).

If an import task is running, we recommend you to wait until it finishes before upgrading TiDB Lightning. Otherwise, there might be chances that you need to reimport from scratch, because there is no guarantee that checkpoints work across versions.
