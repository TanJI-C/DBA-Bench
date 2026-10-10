# DM cluster basics: help, list, start, and display status

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/maintain-dm-using-tiup.md`
- Source Title: `Maintain a DM Cluster Using TiUP`
- Source Heading Path: `Maintain a DM Cluster Using TiUP | Maintain a DM Cluster Using TiUP > View the cluster list | Maintain a DM Cluster Using TiUP > Start the cluster | Maintain a DM Cluster Using TiUP > Check the cluster status`
- Source Line Ranges: `5-119`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `cluster-management`, `help`, `cluster-list`, `start`, `status-check`, `display`, `connectivity`, `leader`, `worker-state`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0116_7e14cdb631`
- Source ID: `tidb-docs-8.1:dm/maintain-dm-using-tiup.md#maintain-a-dm-cluster-using-tiup`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ea173c643d5071d86666716117c2d51179b6c2a32c127b22a2fd83d43a8ea58f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/maintain-dm-using-tiup#maintain-a-dm-cluster-using-tiup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/maintain-dm-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiUP DM commands to view help, list clusters, start a cluster, or display component status and status meanings in a DM cluster.
- Retrieval Keywords: tiup dm --help, tiup dm list, tiup dm start prod-cluster, tiup dm display prod-cluster, DM cluster status, Healthy|L, Free, Up, Down, peer_port 8291, DM-master leader, DM-worker not bound to an upstream
- Follow-up Guidance: It also notes required port connectivity among DM-master, DM-worker, and TiUP nodes, including `peer_port` `8291`, DM-master `8261`, and DM-worker `8262`.
- Classification Note: This is classified as operation content because it describes cluster management commands for help, listing clusters, starting a cluster, and checking runtime status.

## Official Source Content

# Maintain a DM Cluster Using TiUP

This document introduces how to maintain a DM cluster using the TiUP DM component.

If you have not deployed a DM cluster yet, you can refer to [Deploy a DM Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-tiup) for instructions.

> **Note:**
>
> - Make sure that the ports among the following components are interconnected
>     - The `peer_port` (`8291` by default) among the DM-master nodes are interconnected.
>     - Each DM-master node can connect to the `port` of all DM-worker nodes (`8262` by default).
>     - Each DM-worker node can connect to the `port` of all DM-master nodes (`8261` by default).
>     - The TiUP nodes can connect to the `port` of all DM-master nodes (`8261` by default).
>     - The TiUP nodes can connect to the `port` of all DM-worker nodes (`8262` by default).

For the help information of the TiUP DM component, run the following command:

```bash
tiup dm --help
```

```
Deploy a DM cluster for production

Usage:
  tiup dm [flags]
  tiup dm [command]

Available Commands:
  deploy      Deploy a DM cluster for production
  start       Start a DM cluster
  stop        Stop a DM cluster
  restart     Restart a DM cluster
  list        List all clusters
  destroy     Destroy a specified DM cluster
  audit       Show audit log of cluster operation
  exec        Run shell command on host in the dm cluster
  edit-config Edit DM cluster config
  display     Display information of a DM cluster
  reload      Reload a DM cluster's config and restart if needed
  upgrade     Upgrade a specified DM cluster
  patch       Replace the remote package with a specified package and restart the service
  scale-out   Scale out a DM cluster
  scale-in    Scale in a DM cluster
  import      Import an exist DM 1.0 cluster from dm-ansible and re-deploy 2.0 version
  help        Help about any command

Flags:
  -h, --help               help for tiup-dm
      --native-ssh         Use the native SSH client installed on local system instead of the build-in one.
      --ssh-timeout int    Timeout in seconds to connect host via SSH, ignored for operations that don't need an SSH connection. (default 5)
  -v, --version            version for tiup-dm
      --wait-timeout int   Timeout in seconds to wait for an operation to complete, ignored for operations that don't fit. (default 60)
  -y, --yes                Skip all confirmations and assumes 'yes'
```
## View the cluster list

After the cluster is successfully deployed, view the cluster list by running the following command:

```bash
tiup dm list
```

```
Name  User  Version  Path                                  PrivateKey
----  ----  -------  ----                                  ----------
prod-cluster  tidb  ${version}  /root/.tiup/storage/dm/clusters/test  /root/.tiup/storage/dm/clusters/test/ssh/id_rsa
```
## Start the cluster

After the cluster is successfully deployed, start the cluster by running the following command:

```shell
tiup dm start prod-cluster
```

If you forget the name of your cluster, view the cluster list by running `tiup dm list`.
## Check the cluster status

TiUP provides the `tiup dm display` command to view the status of each component in the cluster. With this command, you do not have to log in to each machine to see the component status. The usage of the command is as follows:

```bash
tiup dm display prod-cluster
```

```
dm Cluster: prod-cluster
dm Version: ${version}
ID                 Role          Host          Ports      OS/Arch       Status     Data Dir                           Deploy Dir
--                 ----          ----          -----      -------       ------     --------                           ----------
172.19.0.101:9093  alertmanager  172.19.0.101  9093/9094  linux/x86_64  Up         /home/tidb/data/alertmanager-9093  /home/tidb/deploy/alertmanager-9093
172.19.0.101:8261  dm-master     172.19.0.101  8261/8291  linux/x86_64  Healthy|L  /home/tidb/data/dm-master-8261     /home/tidb/deploy/dm-master-8261
172.19.0.102:8261  dm-master     172.19.0.102  8261/8291  linux/x86_64  Healthy    /home/tidb/data/dm-master-8261     /home/tidb/deploy/dm-master-8261
172.19.0.103:8261  dm-master     172.19.0.103  8261/8291  linux/x86_64  Healthy    /home/tidb/data/dm-master-8261     /home/tidb/deploy/dm-master-8261
172.19.0.101:8262  dm-worker     172.19.0.101  8262       linux/x86_64  Free       /home/tidb/data/dm-worker-8262     /home/tidb/deploy/dm-worker-8262
172.19.0.102:8262  dm-worker     172.19.0.102  8262       linux/x86_64  Free       /home/tidb/data/dm-worker-8262     /home/tidb/deploy/dm-worker-8262
172.19.0.103:8262  dm-worker     172.19.0.103  8262       linux/x86_64  Free       /home/tidb/data/dm-worker-8262     /home/tidb/deploy/dm-worker-8262
172.19.0.101:3000  grafana       172.19.0.101  3000       linux/x86_64  Up         -                                  /home/tidb/deploy/grafana-3000
172.19.0.101:9090  prometheus    172.19.0.101  9090       linux/x86_64  Up         /home/tidb/data/prometheus-9090    /home/tidb/deploy/prometheus-9090
```

The `Status` column uses `Up` or `Down` to indicate whether the service is running normally.

For the DM-master component, `|L` might be appended to a status, which indicates that the DM-master node is a Leader. For the DM-worker component, `Free` indicates that the current DM-worker node is not bound to an upstream.
