# Single-machine simulated production deployment with TiUP

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/quick-start-with-tidb.md`
- Source Title: `Quick Start Guide for the TiDB Database Platform`
- Source Heading Path: `Quick Start Guide for the TiDB Database Platform > Simulate production deployment on a single machine > Prepare | Quick Start Guide for the TiDB Database Platform > Simulate production deployment on a single machine > Deploy | Quick Start Guide for the TiDB Database Platform > What's next`
- Source Line Ranges: `287-525`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tikv`, `pd`, `tiflash`, `dashboard`, `shared`
- Topic Tags: `deployment`, `single-machine`, `prerequisites`, `topology`, `tiup`, `ssh`, `cluster-start`, `access`, `grafana`, `dashboard`, `next-steps`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0202_ebf9eb4103`
- Source ID: `tidb-docs-8.1:quick-start-with-tidb.md#prepare`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0db399d6c6caaf683b6c12895c0b03d8b6a04c21d1fbdbfe4c668b114f331684`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/quick-start-with-tidb#prepare
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/quick-start-with-tidb.md

## Retrieval Guidance

- Use When: Use this chunk when you need the official quick start for simulating a production deployment of a TiDB cluster on a single machine with TiUP, including prerequisites, topo.yaml, deployment commands, startup, and access endpoints.
- Retrieval Keywords: single-machine simulated production deployment, Quick Start Guide for the TiDB Database Platform, TiUP cluster, topo.yaml, tiup cluster deploy <cluster-name> <version> ./topo.yaml --user root -p, tiup cluster start <cluster-name>, tiup cluster list, tiup cluster display <cluster-name>, source ${your_shell_profile}, tiup update --self && tiup update cluster, MaxSessions 20, service sshd restart, CentOS 7.3 or later, x86_64 (AMD64) and ARM architectures, replication.enable-placement-rules, replication.location-labels, server.labels, mysql -h 10.0.1.1 -P 4000 -u root, Grafana monitoring dashboard, TiDB Dashboard, http://{pd-ip}:2379/dashboard, http://{grafana-ip}:3000, tidb user automatically created during deployment
- Follow-up Guidance: The source also points to next steps for Basic SQL operations in TiDB, Migrate data to TiDB, Deploy TiDB using TiUP, TiDB on Kubernetes, and TiFlash documentation.
- Classification Note: This is classified as a self-managed TiUP operation topic because the content covers machine prerequisites, cluster topology, TiUP installation, SSH settings, cluster deploy and start commands, and access to TiDB, Grafana, and TiDB Dashboard.

## Official Source Content

### Prepare

Before deploying the TiDB cluster, ensure that the target machine meets the following requirements:

- CentOS 7.3 or a later version is installed.
- The Linux OS has access to the internet, which is required to download TiDB and related software installation packages.

The smallest TiDB cluster topology consists of the following instances:

> **Note:**
>
> The IP addresses of the instances are given as examples only. In your actual deployment, replace the IP addresses with your actual IP addresses.

| Instance | Count | IP | Configuration |
|:-- | :-- | :-- | :-- |
| TiKV | 3 | 10.0.1.1 <br/> 10.0.1.1 <br/> 10.0.1.1 | Avoid conflict between the port and the directory |
| TiDB | 1 | 10.0.1.1 | The default port <br/> Global directory configuration |
| PD | 1 | 10.0.1.1 | The default port <br/> Global directory configuration |
| TiFlash | 1 | 10.0.1.1 | The default port <br/> Global directory configuration |
| Monitor | 1 | 10.0.1.1 | The default port <br/> Global directory configuration |

Other requirements for the target machine include:

- The `root` user and its password are required.
- [Stop the firewall service of the target machine](https://docs.pingcap.com/tidb/stable/check-before-deployment#check-the-firewall-service-of-target-machines), or open the ports needed by the TiDB cluster nodes.
- Currently, the TiUP cluster supports deploying TiDB on the x86_64 (AMD64) and ARM architectures:

    - It is recommended to use CentOS 7.3 or later versions on AMD64.
    - It is recommended to use CentOS 7.6 1810 on ARM.
### Deploy

> **Note:**
>
> You can log in to the target machine as a regular user or the `root` user. The following steps use the `root` user as an example.

1. Download and install TiUP:

    ```shell
    curl --proto '=https' --tlsv1.2 -sSf https://tiup-mirrors.pingcap.com/install.sh | sh
    ```

2. Declare the global environment variable.

    > **Note:**
    >
    > After the installation, TiUP displays the absolute path of the corresponding Shell profile file. You need to modify `${your_shell_profile}` in the following `source` command according to the path.

    ```shell
    source ${your_shell_profile}
    ```

3. Install the cluster component of TiUP:

    ```shell
    tiup cluster
    ```

4. If the TiUP cluster is already installed on the machine, update the software version:

    ```shell
    tiup update --self && tiup update cluster
    ```

5. Increase the connection limit of the `sshd` service using the root user privilege. This is because TiUP needs to simulate deployment on multiple machines.

    1. Modify `/etc/ssh/sshd_config`, and set `MaxSessions` to `20`.
    2. Restart the `sshd` service:

        ```shell
        service sshd restart
        ```

6. Create and start the cluster:

    Edit the configuration file according to the following template, and name it as `topo.yaml`:

    ```yaml
    # # Global variables are applied to all deployments and used as the default value of
    # # the deployments if a specific deployment value is missing.
    global:
     user: "tidb"
     ssh_port: 22
     deploy_dir: "/tidb-deploy"
     data_dir: "/tidb-data"

    # # Monitored variables are applied to all the machines.
    monitored:
     node_exporter_port: 9100
     blackbox_exporter_port: 9115

    server_configs:
     tidb:
       instance.tidb_slow_log_threshold: 300
     tikv:
       readpool.storage.use-unified-pool: false
       readpool.coprocessor.use-unified-pool: true
     pd:
       replication.enable-placement-rules: true
       replication.location-labels: ["host"]
     tiflash:
       logger.level: "info"

    pd_servers:
     - host: 10.0.1.1

    tidb_servers:
     - host: 10.0.1.1

    tikv_servers:
     - host: 10.0.1.1
       port: 20160
       status_port: 20180
       config:
         server.labels: { host: "logic-host-1" }

     - host: 10.0.1.1
       port: 20161
       status_port: 20181
       config:
         server.labels: { host: "logic-host-2" }

     - host: 10.0.1.1
       port: 20162
       status_port: 20182
       config:
         server.labels: { host: "logic-host-3" }

    tiflash_servers:
     - host: 10.0.1.1

    monitoring_servers:
     - host: 10.0.1.1

    grafana_servers:
     - host: 10.0.1.1
    ```

    - `user: "tidb"`: Use the `tidb` system user (automatically created during deployment) to perform the internal management of the cluster. By default, use port 22 to log in to the target machine via SSH.
    - `replication.enable-placement-rules`: This PD parameter is set to ensure that TiFlash runs normally.
    - `host`: The IP of the target machine.

7. Execute the cluster deployment command:

    ```shell
    tiup cluster deploy <cluster-name> <version> ./topo.yaml --user root -p
    ```

    - `<cluster-name>`: Set the cluster name
    - `<version>`: Set the TiDB cluster version, such as `v8.1.2`. You can see all the supported TiDB versions by running the `tiup list tidb` command
    - `-p`: Specify the password used to connect to the target machine.

        > **Note:**
        >
        > If you use secret keys, you can specify the path of the keys through `-i`. Do not use `-i` and `-p` at the same time.

    Enter "y" and the `root` user's password to complete the deployment:

    ```log
    Do you want to continue? [y/N]:  y
    Input SSH password:
    ```

8. Start the cluster:

    ```shell
    tiup cluster start <cluster-name>
    ```

9. Access the cluster:

    - Install the MySQL client. If it is already installed, skip this step.

        ```shell
        yum -y install mysql
        ```

    - Access TiDB. The password is empty:

        ```shell
        mysql -h 10.0.1.1 -P 4000 -u root
        ```

    - Access the Grafana monitoring dashboard at <http://{grafana-ip}:3000>. The default username and password are both `admin`.

    - Access the [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro) at <http://{pd-ip}:2379/dashboard>. The default username is `root`, and the password is empty.

    - To view the currently deployed cluster list:

        ```shell
        tiup cluster list
        ```

    - To view the cluster topology and status:

        ```shell
        tiup cluster display <cluster-name>
        ```
## What's next

If you have just deployed a TiDB cluster for the local test environment, here are the next steps:

- Learn about basic SQL operations in TiDB by referring to [Basic SQL operations in TiDB](https://docs.pingcap.com/tidb/stable/basic-sql-operations).
- You can also migrate data to TiDB by referring to [Migrate data to TiDB](https://docs.pingcap.com/tidb/stable/migration-overview).

If you are ready to deploy a TiDB cluster for the production environment, here are the next steps:

- [Deploy TiDB using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup)
- Alternatively, you can deploy TiDB on Cloud using TiDB Operator by referring to the [TiDB on Kubernetes](https://docs.pingcap.com/tidb-in-kubernetes/stable) documentation.

If you are looking for an analytics solution with TiFlash, here are the next steps:

- [Use TiFlash](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#use-tiflash)
- [TiFlash Overview](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview)
