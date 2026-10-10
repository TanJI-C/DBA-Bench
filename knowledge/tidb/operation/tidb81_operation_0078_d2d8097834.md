# DM binary deployment overview and DM-master setup

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/deploy-a-dm-cluster-using-binary.md`
- Source Title: `Deploy Data Migration Using DM Binary`
- Source Heading Path: `Deploy Data Migration Using DM Binary | Deploy Data Migration Using DM Binary > Download DM binary | Deploy Data Migration Using DM Binary > Sample scenario | Deploy Data Migration Using DM Binary > Sample scenario > Deploy DM-master | Deploy Data Migration Using DM Binary > Sample scenario > Deploy DM-master > DM-master command-line parameters | Deploy Data Migration Using DM Binary > Sample scenario > Deploy DM-master > DM-master configuration file`
- Source Line Ranges: `5-131`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`, `ecosystem`
- Topic Tags: `binary-deployment`, `download`, `sample-scenario`, `high-availability`, `network-ports`, `dm-master`, `command-line-parameters`, `configuration-file`, `startup`, `logging`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0078_d2d8097834`
- Source ID: `tidb-docs-8.1:dm/deploy-a-dm-cluster-using-binary.md#deploy-data-migration-using-dm-binary`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `612193af342c1f8a95bf1a70dd0fe30bd374117d6404285e22c70485dbd20d78`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-binary#deploy-data-migration-using-dm-binary
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/deploy-a-dm-cluster-using-binary.md

## Retrieval Guidance

- Use When: Use this chunk when you need the DM binary deployment overview, sample DM-master topology, required inter-node ports, or the exact DM-master command-line parameters and configuration file fields for startup.
- Retrieval Keywords: Deploy Data Migration Using DM Binary, Download DM binary, TiDB Toolkit, DM-master, dm-master --help, master-addr, peer-urls, advertise-peer-urls, initial-cluster, data-dir, log-file, conf/dm-master1.toml, ./dm-master -config conf/dm-master1.toml, tail -f dm-master.log, 8261, 8291, high availability, multiple DM-master nodes, ports are interconnected
- Follow-up Guidance: The source continues with changing `name` and `peer-urls` for `master2` and `master3` and repeating the startup step for those DM-master nodes.
- Classification Note: This is classified as an operation chunk because the content describes self-managed binary deployment steps, startup commands, port connectivity requirements, and DM-master configuration options.

## Official Source Content

# Deploy Data Migration Using DM Binary

This document introduces how to quickly deploy the Data Migration (DM) cluster using DM binary.

> **Note:**
>
> In the production environment, it is recommended to [use TiUP to deploy a DM cluster](https://docs.pingcap.com/tidb/stable/dm/deploy-a-dm-cluster-using-tiup).
## Download DM binary

The DM binary is included in the TiDB Toolkit. To download the TiDB Toolkit, see [Download TiDB Tools](https://docs.pingcap.com/tidb/stable/download-ecosystem-tools).
## Sample scenario

Suppose that you deploy a DM cluster based on this sample scenario:

Two DM-worker nodes and three DM-master nodes are deployed on five servers.

Here is the address of each node:

| Instance | Server address | Port |
| :---------- | :----------- | :-- |
| DM-master1 | 192.168.0.4 | 8261 |
| DM-master2 | 192.168.0.5 | 8261 |
| DM-master3 | 192.168.0.6 | 8261 |
| DM-worker1 | 192.168.0.7 | 8262 |
| DM-worker2 | 192.168.0.8 | 8262 |

Based on this scenario, the following sections describe how to deploy the DM cluster.

> **Note:**
>
> - If you deploy multiple DM-master or DM-worker instances in a single server, the port and working directory of each instance must be unique.
>
> - If you do not need to ensure high availability of the DM cluster, deploy only one DM-master node, and the number of deployed DM-worker nodes must be no less than the number of upstream MySQL/MariaDB instances to be migrated.
>
> - To ensure high availability of the DM cluster, it is recommended to deploy three DM-master nodes, and the number of deployed DM-worker nodes must be greater than the number of upstream MySQL/MariaDB instances to be migrated (for example, the number of DM-worker nodes is two more than the number of upstream instances).
>
> - Make sure that the ports among the following components are interconnected:
>     - The `8291` ports among the DM-master nodes are interconnected.
>     - Each DM-master node can connect to the `8262` ports of all DM-worker nodes.
>     - Each DM-worker node can connect to the `8261` port of all DM-master nodes.
### Deploy DM-master

You can configure DM-master by using [command-line parameters](#dm-master-command-line-parameters) or [the configuration file](#dm-master-configuration-file).
#### DM-master command-line parameters

The following is the description of DM-master command-line parameters:

```bash
./dm-master --help
```

```
Usage of dm-master:
  -L string
        log level: debug, info, warn, error, fatal (default "info")
  -V    prints version and exit
  -advertise-addr string
        advertise address for client traffic (default "${master-addr}")
  -advertise-peer-urls string
        advertise URLs for peer traffic (default "${peer-urls}")
  -config string
        path to config file
  -data-dir string
        path to the data directory (default "default.${name}")
  -initial-cluster string
        initial cluster configuration for bootstrapping, e.g. dm-master=http://127.0.0.1:8291
  -join string
        join to an existing cluster (usage: cluster's "${master-addr}" list, e.g. "127.0.0.1:8261,127.0.0.1:18261"
  -log-file string
        log file path
  -master-addr string
        master API server and status addr
  -name string
        human-readable name for this DM-master member
  -peer-urls string
        URLs for peer traffic (default "http://127.0.0.1:8291")
  -print-sample-config
        print sample config file of dm-worker
```

> **Note:**
>
> In some situations, you cannot use the above method to configure DM-master because some configurations are not exposed to the command line. In such cases, use the configuration file instead.
#### DM-master configuration file

The following is the configuration file of DM-master. It is recommended that you configure DM-master by using this method.

1. Write the following configuration to `conf/dm-master1.toml`:

      ```toml
      # Master Configuration.
      name = "master1"

      # Log configurations.
      log-level = "info"
      log-file = "dm-master.log"

      # The listening address of DM-master.
      master-addr = "192.168.0.4:8261"

      # The peer URLs of DM-master.
      peer-urls = "192.168.0.4:8291"

      # The value of `initial-cluster` is the combination of the `advertise-peer-urls` value of all DM-master nodes in the initial cluster.
      initial-cluster = "master1=http://192.168.0.4:8291,master2=http://192.168.0.5:8291,master3=http://192.168.0.6:8291"
      ```

2. Execute the following command in the terminal to run DM-master:

      ```bash
      ./dm-master -config conf/dm-master1.toml
      ```

      > **Note:**
      >
      > The console does not output logs after this command is executed. If you want to view the runtime log, you can execute `tail -f dm-master.log`.

3. For DM-master2 and DM-master3, change `name` in the configuration file to `master2` and `master3` respectively, and change `peer-urls` to `192.168.0.5:8291` and `192.168.0.6:8291` respectively. Then repeat Step 2.
