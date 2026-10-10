# TiCDC deployment requirements and TiUP deployment or scaling

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/deploy-ticdc.md`
- Source Title: `Deploy and Maintain TiCDC`
- Source Heading Path: `Deploy and Maintain TiCDC | Deploy and Maintain TiCDC > Software and hardware recommendations | Deploy and Maintain TiCDC > Deploy a new TiDB cluster that includes TiCDC using TiUP | Deploy and Maintain TiCDC > Add or scale out TiCDC to an existing TiDB cluster using TiUP | Deploy and Maintain TiCDC > Delete or scale in TiCDC from an existing TiDB cluster using TiUP`
- Source Line Ranges: `5-85`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tiup`, `tidb`
- Topic Tags: `deployment`, `hardware-requirements`, `software-requirements`, `tiup`, `topology`, `scale-out`, `scale-in`, `cluster-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0244_cc2e812d15`
- Source ID: `tidb-docs-8.1:ticdc/deploy-ticdc.md#deploy-and-maintain-ticdc`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `94d3cb751a506c0b0fa04bb92a2d6758512717db17d1f3abf963d2bd8f2f5534`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/deploy-ticdc#deploy-and-maintain-ticdc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/deploy-ticdc.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented TiCDC deployment requirements or TiUP topology and cluster management commands for deploying, scaling out, or scaling in TiCDC in a TiDB cluster.
- Retrieval Keywords: TiCDC deployment requirements, software and hardware recommendations, Red Hat Enterprise Linux 7.3 or later, CentOS 7.3 or later, 16 core+, 64 GB+, 500 GB+ SSD, 10 Gigabit network card, 2 TiCDC cluster instances, cdc_servers, gc-ttl, data_dir, Deploy a new TiDB cluster that includes TiCDC using TiUP, Add or scale out TiCDC to an existing TiDB cluster using TiUP, Delete or scale in TiCDC from an existing TiDB cluster using TiUP, scale-out.yml, tiup cluster scale-out <cluster-name> scale-out.yml, tiup cluster scale-in <cluster-name> --node 10.0.1.4:8300, SSH mutual trust, sudo without password
- Follow-up Guidance: The source also points to the TiUP topology reference for `cdc_servers`, the TiDB deployment guide using TiUP, and TiUP procedures for scaling out or scaling in a TiCDC cluster.
- Classification Note: This is classified as operation for the `ticdc` component because the content covers deployment prerequisites, TiUP topology configuration, and TiCDC node scale-out and scale-in procedures in a self-managed cluster.

## Official Source Content

# Deploy and Maintain TiCDC

This document describes how to deploy and maintain a TiCDC cluster, including the hardware and software recommendations. You can either deploy TiCDC along with a new TiDB cluster or add the TiCDC component to an existing TiDB cluster.
## Software and hardware recommendations

In production environments, the recommendations of software and hardware for TiCDC are as follows:

| Linux OS       | Version         |
| :----------------------- | :----------: |
| Red Hat Enterprise Linux | 7.3 or later versions   |
| CentOS                   | 7.3 or later versions   |

| CPU | Memory | Disk | Network | Number of TiCDC cluster instances (minimum requirements for production environment) |
| :--- | :--- | :--- | :--- | :--- |
| 16 core+ | 64 GB+ | 500 GB+ SSD | 10 Gigabit network card (2 preferred） | 2 |

For more information, see [Software and Hardware Recommendations](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements).
## Deploy a new TiDB cluster that includes TiCDC using TiUP

When you deploy a new TiDB cluster using TiUP, you can also deploy TiCDC at the same time. You only need to add the `cdc_servers` section in the configuration file that TiUP uses to start the TiDB cluster. The following is an example:

```shell
cdc_servers:
  - host: 10.0.1.20
    gc-ttl: 86400
    data_dir: "/cdc-data"
  - host: 10.0.1.21
    gc-ttl: 86400
    data_dir: "/cdc-data"
```

More references:

- For detailed operations, see [Edit the initialization configuration file](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup#step-3-initialize-cluster-topology-file).
- For detailed configurable fields, see [Configure `cdc_servers` using TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#cdc_servers).
- For detailed steps to deploy a TiDB cluster, see [Deploy a TiDB Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup).

> **Note:**
>
> Before installing TiCDC, ensure that you have [manually configured the SSH mutual trust and sudo without password](https://docs.pingcap.com/tidb/stable/check-before-deployment#manually-configure-the-ssh-mutual-trust-and-sudo-without-password) between the TiUP control machine and the TiCDC host.
## Add or scale out TiCDC to an existing TiDB cluster using TiUP

The method of scaling out a TiCDC cluster is similar to that of deploying one. It is recommended to use TiUP to perform the scale-out.

1. Create a `scale-out.yml` file to add the TiCDC node information. The following is an example:

    ```shell
    cdc_servers:
      - host: 10.1.1.1
        gc-ttl: 86400
        data_dir: /tidb-data/cdc-8300
      - host: 10.1.1.2
        gc-ttl: 86400
        data_dir: /tidb-data/cdc-8300
      - host: 10.0.1.4
        gc-ttl: 86400
        data_dir: /tidb-data/cdc-8300
    ```

2. Run the scale-out command on the TiUP control machine:

    ```shell
    tiup cluster scale-out <cluster-name> scale-out.yml
    ```

For more use cases, see [Scale out a TiCDC cluster](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-out-a-ticdc-cluster).
## Delete or scale in TiCDC from an existing TiDB cluster using TiUP

It is recommended that you use TiUP to scale in TiCDC nodes. The following is the scale-in command:

```shell
tiup cluster scale-in <cluster-name> --node 10.0.1.4:8300
```

For more use cases, see [Scale in a TiCDC cluster](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-in-a-ticdc-cluster).
