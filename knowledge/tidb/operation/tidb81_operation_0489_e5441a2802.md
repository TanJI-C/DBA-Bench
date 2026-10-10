# TiUP cluster deployment and basic operations

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster.md`
- Source Title: `Deploy and Maintain an Online TiDB Cluster Using TiUP`
- Source Heading Path: `Deploy and Maintain an Online TiDB Cluster Using TiUP | Deploy and Maintain an Online TiDB Cluster Using TiUP > Deploy the cluster | Deploy and Maintain an Online TiDB Cluster Using TiUP > View the cluster list | Deploy and Maintain an Online TiDB Cluster Using TiUP > Start the cluster | Deploy and Maintain an Online TiDB Cluster Using TiUP > Check the cluster status`
- Source Line Ranges: `5-234`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tidb`, `tikv`, `tiflash`, `tiproxy`, `dashboard`
- Topic Tags: `deployment`, `topology`, `yaml`, `cluster list`, `start`, `status`, `systemd`, `production`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0489_e5441a2802`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster.md#deploy-and-maintain-an-online-tidb-cluster-using-tiup`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7d97f4fe7127e597f5886bd60c1886c0d239fe48bb11fba19305943ffa5adf32`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster#deploy-and-maintain-an-online-tidb-cluster-using-tiup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs TiUP cluster basics for deploying a production TiDB cluster, listing clusters, starting a cluster, or checking component status from a topology.yaml file.
- Retrieval Keywords: tiup cluster deploy <cluster-name> <version> <topology.yaml>, topology.yaml, yaml syntax, tiup cluster list, tiup cluster start, tiup cluster display, systemd, Status column Up Down, pd |L, pd |UI, global arch arm64, tiproxy_servers, tiflash_servers, monitoring_servers, grafana_servers, prod-cluster, v8.1.2
- Follow-up Guidance: The content also shows that `tiup cluster display prod-cluster` reports each component status and explains that PD status can include `|L` for Leader and `|UI` for TiDB Dashboard.
- Classification Note: This is classified as an operation chunk because it documents TiUP cluster deployment and routine management commands such as deploy, list, start, and display for a self-managed cluster.

## Official Source Content

# Deploy and Maintain an Online TiDB Cluster Using TiUP

This document focuses on how to use the TiUP cluster component. For the complete steps of online deployment, refer to [Deploy a TiDB Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup).

Similar to [the TiUP playground component](https://docs.pingcap.com/tidb/stable/tiup/tiup-playground) used for a local test deployment, the TiUP cluster component quickly deploys TiDB for production environment. Compared with playground, the cluster component provides more powerful production cluster management features, including upgrading, scaling, and even operation and auditing.

For the help information of the cluster component, run the following command:

```bash
tiup cluster
```

```
Starting component `cluster`: /home/tidb/.tiup/components/cluster/v1.12.3/cluster
Deploy a TiDB cluster for production

Usage:
  tiup cluster [command]

Available Commands:
  check       Precheck a cluster
  deploy      Deploy a cluster for production
  start       Start a TiDB cluster
  stop        Stop a TiDB cluster
  restart     Restart a TiDB cluster
  scale-in    Scale in a TiDB cluster
  scale-out   Scale out a TiDB cluster
  destroy     Destroy a specified cluster
  clean       (Experimental) Clean up a specified cluster
  upgrade     Upgrade a specified TiDB cluster
  display     Display information of a TiDB cluster
  list        List all clusters
  audit       Show audit log of cluster operation
  import      Import an existing TiDB cluster from TiDB-Ansible
  edit-config Edit TiDB cluster config
  reload      Reload a TiDB cluster's config and restart if needed
  patch       Replace the remote package with a specified package and restart the service
  help        Help about any command

Flags:
  -c, --concurrency int     Maximum number of concurrent tasks allowed (defaults to `5`)
      --format string       (EXPERIMENTAL) The format of output, available values are [default, json] (default "default")
  -h, --help                help for tiup
      --ssh string          (Experimental) The executor type. Optional values are 'builtin', 'system', and 'none'.
      --ssh-timeout uint    Timeout in seconds to connect a host via SSH. Operations that don't need an SSH connection are ignored. (default 5)
  -v, --version            TiUP version
      --wait-timeout uint   Timeout in seconds to wait for an operation to complete. Inapplicable operations are ignored. (defaults to `120`)
  -y, --yes                 Skip all confirmations and assumes 'yes'
```
## Deploy the cluster

To deploy the cluster, run the `tiup cluster deploy` command. The usage of the command is as follows:

```bash
tiup cluster deploy <cluster-name> <version> <topology.yaml> [flags]
```

This command requires you to provide the cluster name, the TiDB cluster version (such as `v8.1.2`), and a topology file of the cluster.

To write a topology file, refer to [the example](https://github.com/pingcap/tiup/blob/master/embed/examples/cluster/topology.example.yaml). The following file is an example of the simplest topology:

> **Note:**
>
> The topology file used by the TiUP cluster component for deployment and scaling is written using [yaml](https://yaml.org/spec/1.2/spec.html) syntax, so make sure that the indentation is correct.

```yaml
---

pd_servers:
  - host: 172.16.5.134
    name: pd-134
  - host: 172.16.5.139
    name: pd-139
  - host: 172.16.5.140
    name: pd-140

tidb_servers:
  - host: 172.16.5.134
  - host: 172.16.5.139
  - host: 172.16.5.140

tikv_servers:
  - host: 172.16.5.134
  - host: 172.16.5.139
  - host: 172.16.5.140

tiflash_servers:
  - host: 172.16.5.141
  - host: 172.16.5.142
  - host: 172.16.5.143

tiproxy_servers:
  - host: 172.16.5.144

grafana_servers:
  - host: 172.16.5.134

monitoring_servers:
  - host: 172.16.5.134
```

By default, TiUP is deployed as the binary files running on the amd64 architecture. If the target machine is the arm64 architecture, you can configure it in the topology file:

```yaml
global:
  arch: "arm64"           # Configures all machines to use the binary files of the arm64 architecture by default

tidb_servers:
  - host: 172.16.5.134
    arch: "amd64"         # Configures this machine to use the binary files of the amd64 architecture
  - host: 172.16.5.139
    arch: "arm64"         # Configures this machine to use the binary files of the arm64 architecture
  - host: 172.16.5.140    # Machines that are not configured with the arch field use the default value in the global field, which is arm64 in this case.

...
```

Save the file as `/tmp/topology.yaml`. If you want to use TiDB v8.1.2 and your cluster name is `prod-cluster`, run the following command:

```shell
tiup cluster deploy -p prod-cluster v8.1.2 /tmp/topology.yaml
```

During the execution, TiUP asks you to confirm your topology again and requires the root password of the target machine (the `-p` flag means inputting password):

```bash
Please confirm your topology:
TiDB Cluster: prod-cluster
TiDB Version: v8.1.2
Type        Host          Ports                            OS/Arch       Directories
----        ----          -----                            -------       -----------
pd          172.16.5.134  2379/2380                        linux/x86_64  deploy/pd-2379,data/pd-2379
pd          172.16.5.139  2379/2380                        linux/x86_64  deploy/pd-2379,data/pd-2379
pd          172.16.5.140  2379/2380                        linux/x86_64  deploy/pd-2379,data/pd-2379
tiproxy     172.16.5.144  6000/3080                        linux/x86_64  deploy/tiproxy-6000
tikv        172.16.5.134  20160/20180                      linux/x86_64  deploy/tikv-20160,data/tikv-20160
tikv        172.16.5.139  20160/20180                      linux/x86_64  deploy/tikv-20160,data/tikv-20160
tikv        172.16.5.140  20160/20180                      linux/x86_64  deploy/tikv-20160,data/tikv-20160
tidb        172.16.5.134  4000/10080                       linux/x86_64  deploy/tidb-4000
tidb        172.16.5.139  4000/10080                       linux/x86_64  deploy/tidb-4000
tidb        172.16.5.140  4000/10080                       linux/x86_64  deploy/tidb-4000
tiflash     172.16.5.141  9000/8123/3930/20170/20292/8234  linux/x86_64  deploy/tiflash-9000,data/tiflash-9000
tiflash     172.16.5.142  9000/8123/3930/20170/20292/8234  linux/x86_64  deploy/tiflash-9000,data/tiflash-9000
tiflash     172.16.5.143  9000/8123/3930/20170/20292/8234  linux/x86_64  deploy/tiflash-9000,data/tiflash-9000
prometheus  172.16.5.134  9090         deploy/prometheus-9090,data/prometheus-9090
grafana     172.16.5.134  3000         deploy/grafana-3000
Attention:
    1. If the topology is not what you expected, check your yaml file.
    2. Please confirm there is no port/directory conflicts in same host.
Do you want to continue? [y/N]:
```

After you enter the password, TiUP cluster downloads the required components and deploy them on the corresponding machines. When you see the following message, the deployment is successful:

```bash
Deployed cluster `prod-cluster` successfully
```
## View the cluster list

After the cluster is successfully deployed, view the cluster list by running the following command:

```bash
tiup cluster list
```

```
Starting /root/.tiup/components/cluster/v1.12.3/cluster list
Name          User  Version    Path                                               PrivateKey
----          ----  -------    ----                                               ----------
prod-cluster  tidb  v8.1.2    /root/.tiup/storage/cluster/clusters/prod-cluster  /root/.tiup/storage/cluster/clusters/prod-cluster/ssh/id_rsa
```
## Start the cluster

After the cluster is successfully deployed, start the cluster by running the following command:

```shell
tiup cluster start prod-cluster
```

If you forget the name of your cluster, view the cluster list by running `tiup cluster list`.

TiUP uses `systemd` to start a daemon process. If the process terminates unexpectedly, it will be pulled up after 15 seconds.
## Check the cluster status

TiUP provides the `tiup cluster display` command to view the status of each component in the cluster. With this command, you don't have to log in to each machine to see the component status. The usage of the command is as follows:

```bash
tiup cluster display prod-cluster
```

```
Starting /root/.tiup/components/cluster/v1.12.3/cluster display prod-cluster
TiDB Cluster: prod-cluster
TiDB Version: v8.1.2
ID                  Role        Host          Ports                            OS/Arch       Status  Data Dir              Deploy Dir
--                  ----        ----          -----                            -------       ------  --------              ----------
172.16.5.134:3000   grafana     172.16.5.134  3000                             linux/x86_64  Up      -                     deploy/grafana-3000
172.16.5.134:2379   pd          172.16.5.134  2379/2380                        linux/x86_64  Up|L    data/pd-2379          deploy/pd-2379
172.16.5.139:2379   pd          172.16.5.139  2379/2380                        linux/x86_64  Up|UI   data/pd-2379          deploy/pd-2379
172.16.5.140:2379   pd          172.16.5.140  2379/2380                        linux/x86_64  Up      data/pd-2379          deploy/pd-2379
172.16.5.134:9090   prometheus  172.16.5.134  9090                             linux/x86_64  Up      data/prometheus-9090  deploy/prometheus-9090
172.16.5.134:4000   tidb        172.16.5.134  4000/10080                       linux/x86_64  Up      -                     deploy/tidb-4000
172.16.5.139:4000   tidb        172.16.5.139  4000/10080                       linux/x86_64  Up      -                     deploy/tidb-4000
172.16.5.140:4000   tidb        172.16.5.140  4000/10080                       linux/x86_64  Up      -                     deploy/tidb-4000
172.16.5.141:9000   tiflash     172.16.5.141  9000/8123/3930/20170/20292/8234  linux/x86_64  Up      data/tiflash-9000     deploy/tiflash-9000
172.16.5.142:9000   tiflash     172.16.5.142  9000/8123/3930/20170/20292/8234  linux/x86_64  Up      data/tiflash-9000     deploy/tiflash-9000
172.16.5.143:9000   tiflash     172.16.5.143  9000/8123/3930/20170/20292/8234  linux/x86_64  Up      data/tiflash-9000     deploy/tiflash-9000
172.16.5.134:20160  tikv        172.16.5.134  20160/20180                      linux/x86_64  Up      data/tikv-20160       deploy/tikv-20160
172.16.5.139:20160  tikv        172.16.5.139  20160/20180                      linux/x86_64  Up      data/tikv-20160       deploy/tikv-20160
172.16.5.140:20160  tikv        172.16.5.140  20160/20180                      linux/x86_64  Up      data/tikv-20160       deploy/tikv-20160
172.16.5.144:6000   tiproxy     172.16.5.144  6000/3080                        linux/x86_64  Up      -                     deploy/tiproxy-6000
```

The `Status` column uses `Up` or `Down` to indicate whether the service is running normally.

For the PD component, `|L` or `|UI` might be appended to `Up` or `Down`. `|L` indicates that the PD node is a Leader, and `|UI` indicates that [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro) is running on the PD node.
