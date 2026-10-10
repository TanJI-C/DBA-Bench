# DM topology file structure, global settings, and server configs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-dm-topology-reference.md`
- Source Title: `Topology Configuration File for DM Cluster Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for DM Cluster Deployment Using TiUP | Topology Configuration File for DM Cluster Deployment Using TiUP > File structure | Topology Configuration File for DM Cluster Deployment Using TiUP > File structure > `global` | Topology Configuration File for DM Cluster Deployment Using TiUP > File structure > `server_configs``
- Source Line Ranges: `5-83`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dm`, `shared`
- Topic Tags: `topology-file`, `file-structure`, `global-configuration`, `server-configs`, `deployment-directories`, `resource-control`, `dm-master`, `dm-worker`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1037_4c81f56568`
- Source ID: `tidb-docs-8.1:tiup/tiup-dm-topology-reference.md#topology-configuration-file-for-dm-cluster-deployment-using-tiup`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3071086c9f2e844a0284eae72d7fecfa32556562c508e1f0231cc0fc0accb5b4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-dm-topology-reference#topology-configuration-file-for-dm-cluster-deployment-using-tiup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-dm-topology-reference.md

## Retrieval Guidance

- Use When: Use this content when identifying the structure and shared configuration fields of a TiUP DM topology file, including how global defaults and server_configs apply to DM-master and DM-worker instances.
- Retrieval Keywords: topology configuration file for DM cluster deployment using TiUP, global, server_configs, master_servers, worker_servers, monitoring_servers, grafana_servers, alertmanager_servers, deploy_dir, data_dir, log_dir, ssh_port, user, group, os, arch, resource_control, memory_limit, cpu_quota, io_read_bandwidth_max, io_write_bandwidth_max, limit_core, server_configs master, server_configs worker, DM-master Configuration File, DM-worker Configuration File
- Follow-up Guidance: The source also provides example YAML for the `global` section and for `server_configs` with `master` and `worker` settings.
- Classification Note: This is reference content because it enumerates the DM topology file sections and defines the supported fields, defaults, and override behavior for `global` and `server_configs`.

## Official Source Content

# Topology Configuration File for DM Cluster Deployment Using TiUP

To deploy or scale a TiDB Data Migration (DM) cluster, you need to provide a topology file ([sample](https://github.com/pingcap/tiup/blob/master/embed/examples/dm/topology.example.yaml)) to describe the cluster topology.

Similarly, to modify the cluster topology, you need to modify the topology file. The difference is that, after the cluster is deployed, you can only modify a part of the fields in the topology file. This document introduces each section of the topology file and each field in each section.
## File structure

A topology configuration file for DM cluster deployment using TiUP might contain the following sections:

- [global](#global): the cluster's global configuration. Some of the configuration items use the default values of the cluster, and you can configure them separately in each instance.
- [server_configs](#server_configs): the components' global configuration. You can configure each component separately. If an instance has a configuration item with the same key, the instance's configuration item will take effect.
- [master_servers](#master_servers): the configuration of the DM-master instance. The configuration specifies the machines to which the master service of the DM component is deployed.
- [worker_servers](#worker_servers): the configuration of the DM-worker instance. The configuration specifies the machines to which the worker service of the DM component is deployed.
- [monitoring_servers](#monitoring_servers): specifies the machines to which the Prometheus instances are deployed. TiUP supports deploying multiple Prometheus instances but only the first instance is used.
- [grafana_servers](#grafana_servers): the configuration of the Grafana instances. The configuration specifies the machines to which the Grafana instances are deployed.
- [alertmanager_servers](#alertmanager_servers): the configuration of the Alertemanager instances. The configuration specifies the machines to which the Alertmanager instances are deployed.
### `global`

The `global` section corresponds to the cluster's global configuration and has the following fields:

- `user`: the user to start the deployed cluster. The default value is "tidb". If the user specified in the `<user>` field does not exist on the target machine, TiUP will automatically try to create the user.
- `group`: the user group to which a user belongs when the user is automatically created. The default value is the same as the `<user>` field. If the specified group does not exist, it will be created automatically.
- `ssh_port`: the SSH port to connect to the target machine for operations. The default value is "22".
- `deploy_dir`: the deployment directory for each component. The default value is "deploy". The construction rules are as follows:
    - If the absolute path `deploy_dir` is configured at the instance level, the actual deployment directory is the `deploy_dir` configured for the instance.
    - For each instance, if you do not configure `deploy_dir`, the default value is the relative path `<component-name>-<component-port>`.
    - If `global.deploy_dir` is set to an absolute path, the component is deployed to the `<global.deploy_dir>/<instance.deploy_dir>` directory.
    - If `global.deploy_dir` is set to a relative path, the component is deployed to the `/home/<global.user>/<global.deploy_dir>/<instance.deploy_dir>` directory.
- `data_dir`: the data directory. The default value is "data". The construction rules are as follows.
    - If the absolute path `data_dir` is configured at the instance level, the actual data directory is the `data_dir` configured for the instance.
    - For each instance, if `data_dir` is not configured, the default value is `<global.data_dir>`.
    - If `data_dir` is set to a relative path, the component data is stored in `<deploy_dir>/<data_dir>`. For the construction rules of `<deploy_dir>`, see the construction rules of the `deploy_dir` field.
- `log_dir`: the data directory. The default value is "log". The construction rules are as follows.
    - If the absolute path of `log_dir` is configured at the instance level, the actual log directory is the `log_dir` configured for the instance.
    - For each instance, if `log_dir` is not configured by the user, the default value is `<global.log_dir>`.
    - If `log_dir` is a relative path, the component logs will be stored in `<deploy_dir>/<log_dir>`. For the construction rules of `<deploy_dir>`, see the construction rules of the `deploy_dir` field.
- `os`: the operating system of the target machine. The field controls which operating system to adapt to for the components pushed to the target machine. The default value is "linux".
- `arch`: the CPU architecture of the target machine. The field controls which platform to adapt to for the binary packages pushed to the target machine. The supported values are "amd64" and "arm64". The default value is "amd64".
- `resource_control`: runtime resource control. All configurations in this field are written to the service file of systemd. There is no limit by default. The resources that can be controlled are as follows:
    - `memory_limit`: limits the maximum memory at runtime. For example, "2G" means that the maximum memory of 2 GB can be used.
    - `cpu_quota`: limits the maximum CPU usage at runtime. For example, "200%".
    - `io_read_bandwidth_max`: limits the maximum I/O bandwidth for disk reads. For example, `"/dev/disk/by-path/pci-0000:00:1f.2-scsi-0:0:0:0:0 100M"`.
    - `io_write_bandwidth_max`: limits the maximum I/O bandwidth for disk writes. For example, `"/dev/disk/by-path/pci-0000:00:1f.2-scsi-0:0:0:0:0 100M"`.
    - `limit_core`: controls the size of core dump.

A `global` configuration example:

```yaml
global:
  user: "tidb"
  resource_control:
    memory_limit: "2G"
```

In the example, the configuration specifies that the `tidb` user is used to start the cluster, and that each component is limited to a maximum of 2 GB of memory when it is running.
### `server_configs`

`server_configs` is used to configure services and to generate configuration files for each component. Similar to the `global` section, the configurations in the `server_configs` section can be overwritten by the configurations with the same keys in an instance. `server_configs` mainly contains the following fields:

- `master`: the configuration related to the DM-master service. For all the supported configuration items, see [DM-master Configuration File](https://docs.pingcap.com/tidb/stable/dm/dm-master-configuration-file).
- `worker`: the configuration related to the DM-worker service, For all the supported configuration items, see [DM-worker Configuration File](https://docs.pingcap.com/tidb/stable/dm/dm-worker-configuration-file).

A `server_configs` configuration example is as follows:

```yaml
server_configs:
  master:
    log-level: info
    rpc-timeout: "30s"
    rpc-rate-limit: 10.0
    rpc-rate-burst: 40
  worker:
    log-level: info
```
