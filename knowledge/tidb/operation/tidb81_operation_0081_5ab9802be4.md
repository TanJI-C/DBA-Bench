# DM deployment prerequisites, TiUP installation, and topology configuration

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/deploy-a-dm-cluster-using-tiup.md`
- Source Title: `Deploy a DM Cluster Using TiUP`
- Source Heading Path: `Deploy a DM Cluster Using TiUP | Deploy a DM Cluster Using TiUP > Prerequisites | Deploy a DM Cluster Using TiUP > Step 1: Install TiUP on the control machine | Deploy a DM Cluster Using TiUP > Step 2: Edit the initialization configuration file`
- Source Line Ranges: `5-149`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `deployment`, `prerequisites`, `tiup-installation`, `topology`, `configuration`, `selinux`, `resource-planning`, `password-encryption`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0081_5ab9802be4`
- Source ID: `tidb-docs-8.1:dm/deploy-a-dm-cluster-using-tiup.md#deploy-a-dm-cluster-using-tiup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3d4c889f2b4d441c4ac8324d60f06f5b4b7682165dbd7836591694157481da29`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-tiup#deploy-a-dm-cluster-using-tiup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/deploy-a-dm-cluster-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official prerequisites, TiUP installation steps, or topology.yaml configuration details for deploying a self-managed DM cluster with TiUP.
- Retrieval Keywords: Deploy a DM Cluster Using TiUP, Prerequisites, SELinux is disabled, hardware and software requirements, DM-worker is bound with only one upstream database, secret-key-path, dmctl encrypt, Install TiUP on the control machine, tiup install dm dmctl, tiup dm template > topology.yaml, topology.yaml, master_servers, worker_servers, monitoring_servers, grafana_servers, alertmanager_servers, peer_port 8291, DM-master 8261, DM-worker 8262
- Follow-up Guidance: The next steps in the source cover `tiup dm deploy`, `tiup dm list`, `tiup dm display`, `tiup dm start`, dmctl usage, and database password encryption.
- Classification Note: This is classified as an operation chunk because the content gives deployment prerequisites, installation commands, and initialization topology configuration for DM and TiUP.

## Official Source Content

# Deploy a DM Cluster Using TiUP

[TiUP](https://github.com/pingcap/tiup) is a cluster operation and maintenance tool introduced in TiDB 4.0. TiUP provides [TiUP DM](https://docs.pingcap.com/tidb/stable/dm/maintain-dm-using-tiup), a cluster management component written in Golang. By using TiUP DM, you can easily perform daily TiDB Data Migration (DM) operations, including deploying, starting, stopping, destroying, scaling, and upgrading a DM cluster, and manage DM cluster parameters.

TiUP supports deploying DM v2.0 or later DM versions. This document introduces how to deploy DM clusters of different topologies.

> **Note:**
>
> If your target machine's operating system supports SELinux, make sure that SELinux is **disabled**.
## Prerequisites

- When DM performs a full data replication task, the DM-worker is bound with only one upstream database. The DM-worker first exports the full amount of data locally, and then imports the data into the downstream database. Therefore, the worker's host space must be large enough to store all upstream tables to be exported. The storage path is specified later when you create the task.

- You need to meet the [hardware and software requirements](https://docs.pingcap.com/tidb/stable/dm/dm-hardware-and-software-requirements) when deploying a DM cluster.

- Starting from v8.0.0, if you need to [encrypt database passwords](https://docs.pingcap.com/tidb/stable/dm/dm-manage-source#encrypt-the-database-password), you must store [a key file used for encrypting and decrypting database passwords](https://docs.pingcap.com/tidb/stable/dm/dm-customized-secret-key) in the DM-master in advance, and configure [`secret-key-path`](https://docs.pingcap.com/tidb/stable/dm/dm-master-configuration-file) for DM-master before using the `dmctl encrypt` command.
## Step 1: Install TiUP on the control machine

Log in to the control machine using a regular user account (take the `tidb` user as an example). All the following TiUP installation and cluster management operations can be performed by the `tidb` user.

1. Install TiUP by executing the following command:

    ```shell
    curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
    ```

    After the installing, `~/.bashrc` has been modified to add TiUP to PATH, so you need to open a new terminal or redeclare the global environment variables `source ~/.bashrc` to use it.

2. Install the TiUP DM component:

    ```shell
    tiup install dm dmctl
    ```
## Step 2: Edit the initialization configuration file

According to the intended cluster topology, you need to manually create and edit the cluster initialization configuration file.

You need to create a YAML configuration file (named `topology.yaml` for example) according to the [configuration file template](https://github.com/pingcap/tiup/blob/master/embed/examples/dm/topology.example.yaml). For other scenarios, edit the configuration accordingly.

You can use the command `tiup dm template > topology.yaml` to generate a configuration file template quickly.

The configuration of deploying three DM-masters, three DM-workers, and one monitoring component instance is as follows:

```yaml
# The global variables apply to all other components in the configuration. If one specific value is missing in the component instance, the corresponding global variable serves as the default value.
global:
  user: "tidb"
  ssh_port: 22
  deploy_dir: "/dm-deploy"
  data_dir: "/dm-data"

server_configs:
  master:
    log-level: info
    # rpc-timeout: "30s"
    # rpc-rate-limit: 10.0
    # rpc-rate-burst: 40
  worker:
    log-level: info

master_servers:
  - host: 10.0.1.11
    name: master1
    ssh_port: 22
    port: 8261
    # peer_port: 8291
    # deploy_dir: "/dm-deploy/dm-master-8261"
    # data_dir: "/dm-data/dm-master-8261"
    # log_dir: "/dm-deploy/dm-master-8261/log"
    # numa_node: "0,1"
    # The following configs are used to overwrite the `server_configs.master` values.
    config:
      log-level: info
      # rpc-timeout: "30s"
      # rpc-rate-limit: 10.0
      # rpc-rate-burst: 40
  - host: 10.0.1.18
    name: master2
    ssh_port: 22
    port: 8261
  - host: 10.0.1.19
    name: master3
    ssh_port: 22
    port: 8261
# If you do not need to ensure high availability of the DM cluster, deploy only one DM-master node, and the number of deployed DM-worker nodes must be no less than the number of upstream MySQL/MariaDB instances to be migrated.
# To ensure high availability of the DM cluster, it is recommended to deploy three DM-master nodes, and the number of deployed DM-worker nodes must exceed the number of upstream MySQL/MariaDB instances to be migrated (for example, the number of DM-worker nodes is two more than the number of upstream instances).
worker_servers:
  - host: 10.0.1.12
    ssh_port: 22
    port: 8262
    # deploy_dir: "/dm-deploy/dm-worker-8262"
    # log_dir: "/dm-deploy/dm-worker-8262/log"
    # numa_node: "0,1"
    # The following configs are used to overwrite the `server_configs.worker` values.
    config:
      log-level: info
  - host: 10.0.1.19
    ssh_port: 22
    port: 8262

monitoring_servers:
  - host: 10.0.1.13
    ssh_port: 22
    port: 9090
    # deploy_dir: "/tidb-deploy/prometheus-8249"
    # data_dir: "/tidb-data/prometheus-8249"
    # log_dir: "/tidb-deploy/prometheus-8249/log"

grafana_servers:
  - host: 10.0.1.14
    port: 3000
    # deploy_dir: /tidb-deploy/grafana-3000

alertmanager_servers:
  - host: 10.0.1.15
    ssh_port: 22
    web_port: 9093
    # cluster_port: 9094
    # deploy_dir: "/tidb-deploy/alertmanager-9093"
    # data_dir: "/tidb-data/alertmanager-9093"
    # log_dir: "/tidb-deploy/alertmanager-9093/log"

```

> **Note:**
> 
> - It is not recommended to run too many DM-workers on one host. Each DM-worker should be allocated at least 2 core CPU and 4 GiB memory.
>
> - Make sure that the ports among the following components are interconnected:
>     - The `peer_port` (`8291` by default) among the DM-master nodes are interconnected.
>     - Each DM-master node can connect to the `port` of all DM-worker nodes (`8262` by default).
>     - Each DM-worker node can connect to the `port` of all DM-master nodes (`8261` by default).
>     - The TiUP nodes can connect to the `port` of all DM-master nodes (`8261` by default).
>     - The TiUP nodes can connect to the `port` of all DM-worker nodes (`8262` by default).

For more `master_servers.host.config` parameter description, refer to [master parameter](https://github.com/pingcap/tiflow/blob/release-8.1/dm/master/dm-master.toml). For more `worker_servers.host.config` parameter description, refer to [worker parameter](https://github.com/pingcap/tiflow/blob/release-8.1/dm/worker/dm-worker.toml).
