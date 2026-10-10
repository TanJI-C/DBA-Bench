# TiUP topology reference for TiSpark masters and workers

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-cluster-topology-reference.md`
- Source Title: `Topology Configuration File for TiDB Deployment Using TiUP`
- Source Heading Path: `Topology Configuration File for TiDB Deployment Using TiUP > File structure > `tispark_masters` | Topology Configuration File for TiDB Deployment Using TiUP > File structure > `tispark_workers``
- Source Line Ranges: `674-770`
- Source Scope: `self_managed`
- Primary Component: `ecosystem`
- Related Components: `tiup`, `shared`
- Topic Tags: `topology-file`, `tispark`, `spark-master`, `spark-worker`, `service-configuration`, `deployment-fields`, `immutable-fields`, `java-home`, `spark-config`, `spark-env`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0976_189a197b72`
- Source ID: `tidb-docs-8.1:tiup/tiup-cluster-topology-reference.md#tispark-masters`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `df4614fab705dce3b0605a855aaee69b2a71df17c7888ab0f033e834770992d3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#tispark-masters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-cluster-topology-reference.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiUP topology file fields, defaults, examples, or immutable settings for `tispark_masters` and `tispark_workers`.
- Retrieval Keywords: tispark_masters, tispark_workers, TiSpark master, TiSpark worker, listen_host, ssh_port, port 7077, web_port 8080, deploy_dir, java_home, JAVA_HOME, spark_config, spark_env, spark.driver.memory, spark.eventLog.enabled, spark.tispark.grpc.framesize, spark.tispark.grpc.timeout_in_sec, spark.tispark.meta.reload_period_in_sec, spark.tispark.request.command.priority, spark.tispark.table.scan_concurrency, SPARK_EXECUTOR_CORES, SPARK_EXECUTOR_MEMORY, SPARK_WORKER_CORES, SPARK_WORKER_MEMORY, immutable fields
- Follow-up Guidance: The source includes YAML examples for both `tispark_masters` and `tispark_workers`, including sample `spark_config` and `spark_env` entries for a master node.
- Classification Note: This is a reference section because it lists the topology fields and defaults for TiSpark master and worker nodes and identifies the fields that cannot be modified after deployment.

## Official Source Content

### `tispark_masters`

`tispark_masters` specifies the machines to which the master node of TiSpark is deployed. It also specifies the service configuration on each machine. `tispark_masters` is an array. Each array element contains the following fields:

- `host`: Specifies the machine to which the TiSpark master is deployed. The field value is an IP address and is mandatory.

- `listen_host`: When the machine has multiple IP addresses, `listen_host` specifies the listening IP address of the service. The default value is `0.0.0.0`.

- `ssh_port`: Specifies the SSH port to connect to the target machine for operations. If it is not specified, the `ssh_port` of the `global` section is used.

- `port`: Spark's listening port, used for communication before the node. The default value is `7077`.

- `web_port`: Spark's web port, which provides web services and the task status. The default value is `8080`.

- `deploy_dir`: Specifies the deployment directory. If it is not specified or specified as a relative directory, the directory is generated according to the `deploy_dir` directory configured in `global`.

- `java_home`: Specifies the path of the JRE environment to be used. This parameter corresponds to the `JAVA_HOME` system environment variable.

- `spark_config`: Configures to configure the TiSpark services. Then, a configuration file is generated and sent to the machine specified in `host`.

- `spark_env`: Configures the environment variables when Spark starts.

- `os`: The operating system of the machine specified in `host`. If this field is not specified, the default value is the `os` value in `global`.

- `arch`: The architecture of the machine specified in `host`. If this field is not specified, the default value is the `arch` value in `global`.

For the above fields, you cannot modify these configured fields after the deployment:

- `host`
- `listen_host`
- `port`
- `web_port`
- `deploy_dir`
- `arch`
- `os`

A `tispark_masters` configuration example is as follows:

```yaml
tispark_masters:
  - host: 10.0.1.21
    spark_config:
      spark.driver.memory: "2g"
      spark.eventLog.enabled: "False"
      spark.tispark.grpc.framesize: 2147483647
      spark.tispark.grpc.timeout_in_sec: 100
      spark.tispark.meta.reload_period_in_sec: 60
      spark.tispark.request.command.priority: "Low"
      spark.tispark.table.scan_concurrency: 256
    spark_env:
      SPARK_EXECUTOR_CORES: 5
      SPARK_EXECUTOR_MEMORY: "10g"
      SPARK_WORKER_CORES: 5
      SPARK_WORKER_MEMORY: "10g"
  - host: 10.0.1.22
```
### `tispark_workers`

`tispark_workers` specifies the machines to which the worker nodes of TiSpark are deployed. It also specifies the service configuration on each machine. `tispark_workers` is an array. Each array element contains the following fields:

- `host`: Specifies the machine to which the TiSpark workers are deployed. The field value is an IP address and is mandatory.

- `listen_host`: When the machine has multiple IP addresses, `listen_host` specifies the listening IP address of the service. The default value is `0.0.0.0`.

- `ssh_port`: Specifies the SSH port to connect to the target machine for operations. If it is not specified, the `ssh_port` of the `global` section is used.

- `port`: Spark's listening port, used for communication before the node. The default value is `7077`.

- `web_port`: Spark's web port, which provides web services and the task status. The default value is `8080`.

- `deploy_dir`: Specifies the deployment directory. If it is not specified or specified as a relative directory, the directory is generated according to the `deploy_dir` directory configured in `global`.

- `java_home`: Specifies the path in which the JRE environment to be used is located. This parameter corresponds to the `JAVA_HOME` system environment variable.

- `os`: The operating system of the machine specified in `host`. If this field is not specified, the default value is the `os` value in `global`.

- `arch`: The architecture of the machine specified in `host`. If this field is not specified, the default value is the `arch` value in `global`.

For the above fields, you cannot modify these configured fields after the deployment:

- `host`
- `listen_host`
- `port`
- `web_port`
- `deploy_dir`
- `arch`
- `os`

A `tispark_workers` configuration example is as follows:

```yaml
tispark_workers:
  - host: 10.0.1.22
  - host: 10.0.1.23
```
