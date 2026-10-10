# TiUP deployment overview, prerequisites, and online installation

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/production-deployment-using-tiup.md`
- Source Title: `Deploy a TiDB Cluster Using TiUP`
- Source Heading Path: `Deploy a TiDB Cluster Using TiUP | Deploy a TiDB Cluster Using TiUP > Step 1. Prerequisites and precheck | Deploy a TiDB Cluster Using TiUP > Step 2. Deploy TiUP on the control machine | Deploy a TiDB Cluster Using TiUP > Step 2. Deploy TiUP on the control machine > Deploy TiUP online`
- Source Line Ranges: `5-82`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tiflash`, `ticdc`, `shared`
- Topic Tags: `deployment`, `prerequisites`, `precheck`, `control-machine`, `online-installation`, `environment-variables`, `component-installation`, `version-verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0195_2c6bed8632`
- Source ID: `tidb-docs-8.1:production-deployment-using-tiup.md#deploy-a-tidb-cluster-using-tiup`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a41a78bff562f3717b4fbde0055fc2342924c1b21bc863ad967de48fdef5fd1c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#deploy-a-tidb-cluster-using-tiup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/production-deployment-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the TiUP deployment overview, prerequisite references, and the online installation steps on the control machine for TiUP cluster.
- Retrieval Keywords: TiUP, TiUP cluster, control machine, Deploy TiUP online, hardware and software requirements, Environment and system configuration check, curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh, source .bash_profile, which tiup, tiup cluster, tiup update --self && tiup update cluster, Updated successfully!, tiup --binary cluster, deploying starting stopping destroying scaling upgrading
- Follow-up Guidance: If the TiUP environment switches to offline, the source says to refer to Deploy TiUP offline; otherwise, TiUP cannot work properly.
- Classification Note: The official content classifies this as an operation topic for the self-managed TiUP component because it describes prerequisites and control-machine installation, update, and version verification steps for cluster management.

## Official Source Content

# Deploy a TiDB Cluster Using TiUP

[TiUP](https://github.com/pingcap/tiup) is a cluster operation and maintenance tool introduced in TiDB 4.0. TiUP provides [TiUP cluster](https://github.com/pingcap/tiup/tree/master/components/cluster), a cluster management component written in Golang. By using TiUP cluster, you can easily perform daily database operations, including deploying, starting, stopping, destroying, scaling, and upgrading a TiDB cluster, and manage TiDB cluster parameters.

TiUP supports deploying TiDB, TiFlash, TiDB Binlog, TiCDC, and the monitoring system. This document introduces how to deploy TiDB clusters of different topologies.
## Step 1. Prerequisites and precheck

Make sure that you have read the following documents:

- [Hardware and software requirements](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements)
- [Environment and system configuration check](https://docs.pingcap.com/tidb/stable/check-before-deployment)
## Step 2. Deploy TiUP on the control machine

You can deploy TiUP on the control machine in either of the two ways: online deployment and offline deployment.
### Deploy TiUP online

> **Note:**
>
> If the TiUP environment switches to offline, refer to [Deploy TiUP offline](#deploy-tiup-offline) for deployment. Otherwise, TiUP cannot work properly.

Log in to the control machine using a regular user account (take the `tidb` user as an example). Subsequent TiUP installation and cluster management can be performed by the `tidb` user.

1. Install TiUP by running the following command:

    ```shell
    curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
    ```

2. Set TiUP environment variables:

    1. Redeclare the global environment variables:

        ```shell
        source .bash_profile
        ```

    2. Confirm whether TiUP is installed:

        ```shell
        which tiup
        ```

3. Install the TiUP cluster component:

    ```shell
    tiup cluster
    ```

4. If TiUP is already installed, update the TiUP cluster component to the latest version:

    ```shell
    tiup update --self && tiup update cluster
    ```

    If `Updated successfully!` is displayed, the TiUP cluster is updated successfully.

5. Verify the current version of your TiUP cluster:

    ```shell
    tiup --binary cluster
    ```
