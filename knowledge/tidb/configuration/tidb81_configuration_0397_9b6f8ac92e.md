# Global topology configuration fields

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-topology-reference.md`
- Source Title: `Topology Configuration File for TiDB Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for TiDB Deployment Using TiUP > File structure > `global``
- Source Line Ranges: `37-105`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`, `pd`, `tidb`, `tikv`, `tiflash`, `tiproxy`
- Topic Tags: `global-config`, `user`, `systemd`, `ssh`, `tls`, `directories`, `os`, `architecture`, `resource-control`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0397_9b6f8ac92e`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-topology-reference.md#global`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ef6daa34370e92d4e8a536ae9424c97f5e5fa7466fad0d406ef19c1523c8870e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#global
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-topology-reference.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact fields and default behaviors in the `global` section of a TiUP topology configuration file, including users, directories, TLS, SSH, OS or architecture, and systemd resource control.
- Retrieval Keywords: global section, global.user, group, systemd_mode, ssh_port, enable_tls, listen_host, deploy_dir, data_dir, log_dir, os, arch, resource_control, memory_limit, cpu_quota, io_read_bandwidth_max, io_write_bandwidth_max, limit_core, TiUP no-sudo mode, systemd
- Follow-up Guidance: The chunk includes application rules for `deploy_dir`, `data_dir`, and `log_dir`, plus an example `global` configuration with `user: "tidb"` and `resource_control.memory_limit: "2G"`.
- Classification Note: This is configuration content because it defines configurable `global` fields, their defaults, and how TiUP applies them in the topology file.

## Official Source Content

### `global`

The `global` section corresponds to the cluster's global configuration and has the following fields:

- `user`: The user used to start the deployed cluster. The default value is `"tidb"`. If the user specified in the `<user>` field does not exist on the target machine, this user is automatically created.

- `group`: The user group to which a user belongs. It is specified when the user is created. The value defaults to that of the `<user>` field. If the specified group does not exist, it is automatically created.

- `systemd_mode`: Specifies the `systemd` mode used on the target machine during cluster deployment. The default value is `system`. If set to `user`, sudo permissions are not required on the target machine, meaning [TiUP no-sudo mode](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-no-sudo-mode) is used.

- `ssh_port`: Specifies the SSH port to connect to the target machine for operations. The default value is `22`.

- `enable_tls`: Specifies whether to enable TLS for the cluster. After TLS is enabled, the generated TLS certificate must be used for connections between components or between the client and the component. The default value is `false`.

- `listen_host`: Specifies the default listening IP address. If it is empty, each instance automatically sets it to `::` or `0.0.0.0` based on whether its `host` field contains `:`. This field is introduced in tiup-cluster v1.14.0. 

- `deploy_dir`: The deployment directory of each component. The default value is `"deployed"`. Its application rules are as follows:

    - If the absolute path of `deploy_dir` is configured at the instance level, the actual deployment directory is `deploy_dir` configured for the instance.

    - For each instance, if you do not configure `deploy_dir`, its default value is the relative path `<component-name>-<component-port>`.

    - If `global.deploy_dir` is an absolute path, the component is deployed to the `<global.deploy_dir>/<instance.deploy_dir>` directory.

    - If `global.deploy_dir` is a relative path, the component is deployed to the `/home/<global.user>/<global.deploy_dir>/<instance.deploy_dir>` directory.

- `data_dir`: The data directory. Default value: `"data"`. Its application rules are as follows:

    - If the absolute path of `data_dir` is configured at the instance level, the actual deployment directory is `data_dir` configured for the instance.

    - For each instance, if you do not configure `data_dir`, its default value is `<global.data_dir>`.

    - If `data_dir` is a relative path, the component data is placed in `<deploy_dir>/<data_dir>`. For the calculation rules of `<deploy_dir>`, see the application rules of the `deploy_dir` field.

- `log_dir`: The log directory. Default value: `"log"`. Its application rules are as follows:

    - If the absolute path `log_dir` is configured at the instance level, the actual log directory is the `log_dir` configured for the instance.

    - For each instance, if you not configure `log_dir`, its default value is `<global.log_dir>`.

    - If `log_dir` is a relative path, the component log is placed in `<deploy_dir>/<log_dir>`. For the calculation rules of `<deploy_dir>`, see the application rules of the `deploy_dir` field.

- `os`: The operating system of the target machine. The field controls which operating system to adapt to for the components pushed to the target machine. The default value is "linux".

- `arch`: The CPU architecture of the target machine. The field controls which platform to adapt to for the binary packages pushed to the target machine. The supported values are "amd64" and "arm64". The default value is "amd64".

- `resource_control`: Runtime resource control. All configurations in this field are written into the service file of systemd. There is no limit by default. The resources that can be controlled are as follows:

    - `memory_limit`: Limits the maximum runtime memory. For example, "2G" means that the maximum memory of 2 GB can be used.

    - `cpu_quota`: Limits the maximum CPU usage at runtime. For example, "200%".

    - `io_read_bandwidth_max`: Limits the maximum I/O bandwidth for disk reads. For example, `"/dev/disk/by-path/pci-0000:00:1f.2-scsi-0:0:0:0 100M"`.

    - `io_write_bandwidth_max`: Limits maximum I/O bandwidth for disk writes. For example, `/dev/disk/by-path/pci-0000:00:1f.2-scsi-0:0:0:0 100M`.

    - `limit_core`: Controls the size of core dump.

A `global` configuration example is as follows:

```yaml
global:
  user: "tidb"
  resource_control:
    memory_limit: "2G"
```

In the above configuration, the `tidb` user is used to start the cluster. At the same time, each component is restricted to a maximum of 2 GB of memory when it is running.
