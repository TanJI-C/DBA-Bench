# Deployment, monitoring, configuration, and cloud support FAQs

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/deploy-and-maintain-faq.md`
- Source Title: `TiDB Deployment FAQs`
- Source Heading Path: `TiDB Deployment FAQs > Installation and deployment | TiDB Deployment FAQs > Installation and deployment > Why the modified `toml` configuration for TiKV/PD does not take effect? | TiDB Deployment FAQs > Installation and deployment > Should I deploy the TiDB monitoring framework (Prometheus + Grafana) on a standalone machine or on multiple machines? What is the recommended CPU and memory? | TiDB Deployment FAQs > Installation and deployment > Why the monitor cannot display all metrics? | TiDB Deployment FAQs > Installation and deployment > What is the function of supervise/svc/svstat service? | TiDB Deployment FAQs > Installation and deployment > Description of inventory.ini variables | TiDB Deployment FAQs > Installation and deployment > How to separately record the slow query log in TiDB? How to locate the slow query SQL statement? | TiDB Deployment FAQs > Installation and deployment > How to add the `label` configuration if `label` of TiKV was not configured when I deployed the TiDB cluster for the first time? | TiDB Deployment FAQs > Installation and deployment > Why does the `dd` command for the disk test use the `oflag=direct` option? | TiDB Deployment FAQs > Installation and deployment > How to use the `fio` command to test the disk performance of the TiKV instance? | TiDB Deployment FAQs > What public cloud vendors are currently supported by TiDB?`
- Source Line Ranges: `36-118`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `tiup`, `pd`, `tikv`, `tidb`, `cloud`
- Topic Tags: `deployment`, `configuration-files`, `monitoring`, `time-synchronization`, `process-supervision`, `inventory-variables`, `slow-query-log`, `labels`, `disk-benchmark`, `fio`, `public-cloud`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0141_8fdaa488b1`
- Source ID: `tidb-docs-8.1:faq/deploy-and-maintain-faq.md#installation-and-deployment`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66ab6a13bea06162ee086eec7725bcea53ab3e35b39a91f85903bdc65d4b3d8e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/deploy-and-maintain-faq#installation-and-deployment
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/deploy-and-maintain-faq.md

## Retrieval Guidance

- Use When: Use this chunk when the question involves TiDB deployment with TiUP, Binary deployment configuration behavior, monitoring setup and missing metrics, inventory.ini variables, slow query logging, TiKV label configuration, disk benchmarking commands, or supported public cloud vendors.
- Retrieval Keywords: TiUP, Deploy a TiDB Cluster Using TiUP, --config parameter, modified toml configuration for TiKV/PD does not take effect, Binary deployment, pd-ctl, Prometheus + Grafana, standalone deployment, 8 core CPU with 16 GB+ memory and a 500 GB+ hard disk, monitor cannot display all metrics, time difference between the machine time of the monitor and the time within the cluster, supervise, svc, svstat, inventory.ini, cluster_name, tidb_version, deployment_method, process_supervision, enable_ntpd, machine_benchmark, enable_slow_query_log, deploy_without_tidb, tidb_slow_log_threshold: 300, ADMIN SHOW SLOW, label configuration, location-labels, config set location-labels "zone,rack,host", oflag=direct, fio, randread, randrw, Google Cloud GKE, AWS EKS, Alibaba Cloud ACK, JD Cloud, UCloud
- Follow-up Guidance: For PD configuration changes after initial startup and for adding location labels, the content refers to the PD Control User Guide and also points to the ADMIN SHOW SLOW command documentation for slow query inspection.
- Classification Note: This is operation content because it covers deployment methods, configuration effectiveness, monitoring behavior, process supervision, runtime logging, benchmarking, and supported cloud deployment targets.

## Official Source Content

## Installation and deployment

For the production environment, it is recommended to use [TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-overview) to deploy your TiDB cluster. See [Deploy a TiDB Cluster Using TiUP](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup).
### Why the modified `toml` configuration for TiKV/PD does not take effect?

You need to set the `--config` parameter in TiKV/PD to make the `toml` configuration effective. TiKV/PD does not read the configuration by default. Currently, this issue only occurs when deploying using Binary. For TiKV, edit the configuration and restart the service. For PD, the configuration file is only read when PD is started for the first time, after which you can modify the configuration using pd-ctl. For details, see [PD Control User Guide](https://docs.pingcap.com/tidb/stable/pd-control).
### Should I deploy the TiDB monitoring framework (Prometheus + Grafana) on a standalone machine or on multiple machines? What is the recommended CPU and memory?

The monitoring machine is recommended to use standalone deployment. It is recommended to use an 8 core CPU with 16 GB+ memory and a 500 GB+ hard disk.
### Why the monitor cannot display all metrics?

Check the time difference between the machine time of the monitor and the time within the cluster. If it is large, you can correct the time and the monitor will display all the metrics.
### What is the function of supervise/svc/svstat service?

- supervise: the daemon process, to manage the processes
- svc: to start and stop the service
- svstat: to check the process status
### Description of inventory.ini variables

| Variable        | Description                                                |
| ---- | ------- |
| `cluster_name` | the name of a cluster, adjustable |
| `tidb_version` | the version of TiDB |
| `deployment_method` | the method of deployment, binary by default, Docker optional |
| `process_supervision` | the supervision way of processes, systemd by default, supervise optional |
| `timezone` | the timezone of the managed node, adjustable, `Asia/Shanghai` by default, used with the `set_timezone` variable |
| `set_timezone` | to edit the timezone of the managed node, True by default; False means closing |
| `enable_elk` | currently not supported |
| `enable_firewalld` | to enable the firewall, closed by default |
| `enable_ntpd` | to monitor the NTP service of the managed node, True by default; do not close it |
| `machine_benchmark` | to monitor the disk IOPS of the managed node, True by default; do not close it |
| `set_hostname` | to edit the hostname of the managed node based on the IP, False by default |
| `enable_binlog` | whether to deploy Pump and enable the binlog, False by default, dependent on the Kafka cluster; see the `zookeeper_addrs` variable |
| `zookeeper_addrs` | the ZooKeeper address of the binlog Kafka cluster |
| `enable_slow_query_log` | to record the slow query log of TiDB into a single file: ({{ deploy_dir }}/log/tidb_slow_query.log). False by default, to record it into the TiDB log |
| `deploy_without_tidb` | the Key-Value mode, deploy only PD, TiKV and the monitoring service, not TiDB; set the IP of the tidb_servers host group to null in the `inventory.ini` file |
### How to separately record the slow query log in TiDB? How to locate the slow query SQL statement?

1. The slow query definition for TiDB is in the TiDB configuration file. The `tidb_slow_log_threshold: 300` parameter is used to configure the threshold value of the slow query (unit: millisecond).

2. If a slow query occurs, you can locate the `tidb-server` instance where the slow query is and the slow query time point using Grafana and find the SQL statement information recorded in the log on the corresponding node.

3. In addition to the log, you can also view the slow query using the `ADMIN SHOW SLOW` command. For details, see [`ADMIN SHOW SLOW` command](https://docs.pingcap.com/tidb/stable/identify-slow-queries#admin-show-slow-command).
### How to add the `label` configuration if `label` of TiKV was not configured when I deployed the TiDB cluster for the first time?

The configuration of TiDB `label` is related to the cluster deployment architecture. It is important and is the basis for PD to execute global management and scheduling. If you did not configure `label` when deploying the cluster previously, you should adjust the deployment structure by manually adding the `location-labels` information using the PD management tool `pd-ctl`, for example, `config set location-labels "zone,rack,host"` (you should configure it based on the practical `label` level name).

For the usage of `pd-ctl`, see [PD Control User Guide](https://docs.pingcap.com/tidb/stable/pd-control).
### Why does the `dd` command for the disk test use the `oflag=direct` option?

The Direct mode wraps the Write request into the I/O command and sends this command to the disk to bypass the file system cache and directly test the real I/O Read/Write performance of the disk.
### How to use the `fio` command to test the disk performance of the TiKV instance?

- Random Read test:

    ```bash
    ./fio -ioengine=psync -bs=32k -fdatasync=1 -thread -rw=randread -size=10G -filename=fio_randread_test.txt -name='fio randread test' -iodepth=4 -runtime=60 -numjobs=4 -group_reporting --output-format=json --output=fio_randread_result.json
    ```

- The mix test of sequential Write and random Read:

    ```bash
    ./fio -ioengine=psync -bs=32k -fdatasync=1 -thread -rw=randrw -percentage_random=100,0 -size=10G -filename=fio_randread_write_test.txt -name='fio mixed randread and sequential write test' -iodepth=4 -runtime=60 -numjobs=4 -group_reporting --output-format=json --output=fio_randread_write_test.json
    ```
## What public cloud vendors are currently supported by TiDB?

TiDB supports deployment on [Google Cloud GKE](https://docs.pingcap.com/tidb-in-kubernetes/stable/deploy-on-gcp-gke), [AWS EKS](https://docs.pingcap.com/tidb-in-kubernetes/stable/deploy-on-aws-eks), and [Alibaba Cloud ACK](https://docs.pingcap.com/tidb-in-kubernetes/stable/deploy-on-alibaba-cloud).

In addition, TiDB is currently available on JD Cloud and UCloud.
