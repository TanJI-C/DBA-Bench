# Patch components, import clusters, audit operations, exec commands, and use controllers

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster.md`
- Source Title: `Deploy and Maintain an Online TiDB Cluster Using TiUP`
- Source Heading Path: `Deploy and Maintain an Online TiDB Cluster Using TiUP > Update component | Deploy and Maintain an Online TiDB Cluster Using TiUP > Import TiDB Ansible cluster | Deploy and Maintain an Online TiDB Cluster Using TiUP > View the operation log | Deploy and Maintain an Online TiDB Cluster Using TiUP > Run commands on a host in the TiDB cluster | Deploy and Maintain an Online TiDB Cluster Using TiUP > Cluster controllers`
- Source Line Ranges: `464-660`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tidb`, `tikv`, `shared`
- Topic Tags: `patch`, `hotfix`, `import`, `ansible`, `audit`, `logs`, `exec`, `ssh`, `controllers`, `ctl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0492_0e8d6c1354`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster.md#update-component`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9b4bfad881e62222f6e50f4b375f286c2b9e03c01e8782e7ee7b7aa969da8ea0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster#update-component
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster.md

## Retrieval Guidance

- Use When: Use this when looking for TiUP cluster operational commands for patching components, importing a TiDB Ansible cluster, viewing audit logs, running remote commands with exec, or using integrated controller tools through `tiup ctl`.
- Retrieval Keywords: tiup cluster patch --help, cluster patch <cluster-name> <package-path>, --offline, --overwrite, --transfer-timeout, tiup cluster patch test-cluster /tmp/tidb-hotfix.tar.gz -R tidb, tiup cluster patch test-cluster /tmp/tidb-hotfix.tar.gz -N 172.16.4.5:4000, tiup cluster import --help, tiup cluster import --dir=/path/to/tidb-ansible, inventory.ini, --no-backup, --rename, TiSpark experimental, tiup cluster audit, audit-id, tiup cluster audit 4BLhr0, cluster exec <cluster-name>, --command, --sudo, tiup cluster exec test-cluster --command='ls /tmp', tiup ctl:v<CLUSTER_VERSION>, tidb-ctl, pd-ctl, tikv-ctl, binlogctl, etcdctl, tiup ctl:v<CLUSTER_VERSION> pd -u http://127.0.0.1:2379 store
- Follow-up Guidance: The content includes command usage, flags, and examples for each operation, including the note that importing a TiDB Ansible cluster with TiSpark enabled is not supported.
- Classification Note: The classification is operation because the content focuses on operational lifecycle and administration commands such as patch, import, audit, exec, and controller access rather than configuration editing.

## Official Source Content

## Update component

For normal upgrade, you can use the `upgrade` command. But in some scenarios, such as debugging, you might need to replace the currently running component with a temporary package. To achieve this, use the `patch` command:

```bash
tiup cluster patch --help
```

```
Replace the remote package with a specified package and restart the service

Usage:
  cluster patch <cluster-name> <package-path> [flags]

Flags:
  -h, --help                    help for patch
  -N, --node strings            Specify the nodes
      --offline                 Patch a stopped cluster
      --overwrite               Use this package in the future scale-out operations
  -R, --role strings            Specify the roles
      --transfer-timeout uint   Timeout in seconds when transferring PD and TiKV store leaders, also for TiCDC drain one capture (default 600)

Global Flags:
  -c, --concurrency int     max number of parallel tasks allowed (default 5)
      --format string       (EXPERIMENTAL) The format of output, available values are [default, json] (default "default")
      --ssh string          (EXPERIMENTAL) The executor type: 'builtin', 'system', 'none'.
      --ssh-timeout uint    Timeout in seconds to connect host via SSH, ignored for operations that don't need an SSH connection. (default 5)
      --wait-timeout uint   Timeout in seconds to wait for an operation to complete, ignored for operations that don't fit. (default 120)
  -y, --yes                 Skip all confirmations and assumes 'yes'
```

If a TiDB hotfix package is in `/tmp/tidb-hotfix.tar.gz` and you want to replace all the TiDB packages in the cluster, run the following command:

```bash
tiup cluster patch test-cluster /tmp/tidb-hotfix.tar.gz -R tidb
```

You can also replace only one TiDB package in the cluster:

```bash
tiup cluster patch test-cluster /tmp/tidb-hotfix.tar.gz -N 172.16.4.5:4000
```
## Import TiDB Ansible cluster

> **Note:**
>
> Currently, TiUP cluster's support for TiSpark is still **experimental**. It is not supported to import a TiDB cluster with TiSpark enabled.

Before TiUP is released, TiDB Ansible is often used to deploy TiDB clusters. To enable TiUP to take over the cluster deployed by TiDB Ansible, use the `import` command.

The usage of the `import` command is as follows:

```bash
tiup cluster import --help
```

```
Import an exist TiDB cluster from TiDB-Ansible

Usage:
  cluster import [flags]

Flags:
  -d, --dir string         The path to TiDB-Ansible directory
  -h, --help               help for import
      --inventory string   The name of inventory file (default "inventory.ini")
      --no-backup          Don't backup ansible dir, useful when there're multiple inventory files
  -r, --rename NAME        Rename the imported cluster to NAME

Global Flags:
      --ssh string        (Experimental) The executor type. Optional values are 'builtin', 'system', and 'none'.
      --wait-timeout int  Timeout of waiting the operation
      --ssh-timeout int   Timeout in seconds to connect host via SSH, ignored for operations that don't need an SSH connection. (default 5)
  -y, --yes               Skip all confirmations and assumes 'yes'
```

You can use either of the following commands to import a TiDB Ansible cluster:

```bash
cd tidb-ansible
tiup cluster import
```

```bash
tiup cluster import --dir=/path/to/tidb-ansible
```
## View the operation log

To view the operation log, use the `audit` command. The usage of the `audit` command is as follows:

```bash
Usage:
  tiup cluster audit [audit-id] [flags]

Flags:
  -h, --help   help for audit
```

If the `[audit-id]` flag is not specified, the command shows a list of commands that have been executed. For example:

```bash
tiup cluster audit
```

```
Starting component `cluster`: /home/tidb/.tiup/components/cluster/v1.12.3/cluster audit
ID      Time                       Command
--      ----                       -------
4BLhr0  2024-12-26T23:55:09+08:00  /home/tidb/.tiup/components/cluster/v1.12.3/cluster deploy test v8.1.2 /tmp/topology.yaml
4BKWjF  2024-12-26T23:36:57+08:00  /home/tidb/.tiup/components/cluster/v1.12.3/cluster deploy test v8.1.2 /tmp/topology.yaml
4BKVwH  2024-12-26T23:02:08+08:00  /home/tidb/.tiup/components/cluster/v1.12.3/cluster deploy test v8.1.2 /tmp/topology.yaml
4BKKH1  2024-12-26T16:39:04+08:00  /home/tidb/.tiup/components/cluster/v1.12.3/cluster destroy test
4BKKDx  2024-12-26T16:36:57+08:00  /home/tidb/.tiup/components/cluster/v1.12.3/cluster deploy test v8.1.2 /tmp/topology.yaml
```

The first column is `audit-id`. To view the execution log of a certain command, pass the `audit-id` of a command as the flag as follows:

```bash
tiup cluster audit 4BLhr0
```
## Run commands on a host in the TiDB cluster

To run command on a host in the TiDB cluster, use the `exec` command. The usage of the `exec` command is as follows:

```bash
Usage:
  cluster exec <cluster-name> [flags]

Flags:
      --command string   the command run on cluster host (default "ls")
  -h, --help             help for exec
  -N, --node strings     Only exec on host with specified nodes
  -R, --role strings     Only exec on host with specified roles
      --sudo             use root permissions (default false)

Global Flags:
      --ssh-timeout int   Timeout in seconds to connect host via SSH, ignored for operations that don't need an SSH connection. (default 5)
  -y, --yes               Skip all confirmations and assumes 'yes'
```

For example, to execute `ls /tmp` on all TiDB nodes, run the following command:

```bash
tiup cluster exec test-cluster --command='ls /tmp'
```
## Cluster controllers

Before TiUP is released, you can control the cluster using `tidb-ctl`, `tikv-ctl`, `pd-ctl`, and other tools. To make the tools easier to download and use, TiUP integrates them into an all-in-one component, `ctl`.

```bash
Usage:
  tiup ctl:v<CLUSTER_VERSION> {tidb/pd/tikv/binlog/etcd} [flags]

Flags:
  -h, --help   help for tiup
```

This command has a corresponding relationship with those of the previous tools:

```bash
tidb-ctl [args] = tiup ctl tidb [args]
pd-ctl [args] = tiup ctl pd [args]
tikv-ctl [args] = tiup ctl tikv [args]
binlogctl [args] = tiup ctl bindlog [args]
etcdctl [args] = tiup ctl etcd [args]
```

For example, if you previously view the store by running `pd-ctl -u http://127.0.0.1:2379 store`, now you can run the following command in TiUP:

```bash
tiup ctl:v<CLUSTER_VERSION> pd -u http://127.0.0.1:2379 store
```
