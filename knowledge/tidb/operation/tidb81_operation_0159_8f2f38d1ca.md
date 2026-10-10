# TiUP cluster stop, data cleanup, and destruction

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/maintain-tidb-using-tiup.md`
- Source Title: `TiUP Common Operations`
- Source Heading Path: `TiUP Common Operations > Stop the cluster | TiUP Common Operations > Clean up cluster data | TiUP Common Operations > Destroy the cluster`
- Source Line Ranges: `199-291`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tikv`, `tidb`, `tiflash`, `ticdc`, `shared`
- Topic Tags: `stop-order`, `component-stop`, `role-filtering`, `node-filtering`, `data-cleanup`, `log-cleanup`, `ignore-role`, `ignore-node`, `destroy`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0159_8f2f38d1ca`
- Source ID: `tidb-docs-8.1:maintain-tidb-using-tiup.md#stop-the-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `702aa222788298807d09e2f0d31f3d0eafc0bec1e4760add85a81f26ea05e6d5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/maintain-tidb-using-tiup#stop-the-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/maintain-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this when you need the TiUP commands for stopping a cluster, cleaning up data or logs, or destroying the cluster.
- Retrieval Keywords: tiup cluster stop ${cluster-name}, Alertmanager > Grafana > Prometheus > TiCDC > Drainer > TiFlash > TiDB > Pump > TiKV > PD, tiup cluster stop ${cluster-name} -R tidb, tiup cluster stop ${cluster-name} -N 1.2.3.4:4000,1.2.3.5:4000, tiup cluster clean ${cluster-name} --data, tiup cluster clean ${cluster-name} --log, tiup cluster clean ${cluster-name} --all, tiup cluster clean ${cluster-name} --all --ignore-role prometheus, tiup cluster clean ${cluster-name} --all --ignore-node 172.16.13.11:9000, tiup cluster clean ${cluster-name} --all --ignore-node 172.16.13.12, tiup cluster destroy ${cluster-name}
- Follow-up Guidance: Proceed with caution because clean and destroy operations cannot be reverted.
- Classification Note: This chunk is about TiUP cluster stop, cluster clean for data and logs, and cluster destroy.

## Official Source Content

## Stop the cluster

The components in the TiDB cluster are stopped in the following order (The monitoring component is also stopped):

**Alertmanager > Grafana > Prometheus > TiCDC > Drainer > TiFlash > TiDB > Pump > TiKV > PD**

To stop the cluster, run the following command:

```bash
tiup cluster stop ${cluster-name}
```

Similar to the `start` command, the `stop` command supports stopping some of the components by adding the `-R` or `-N` parameters. For example:

- This command stops only the TiDB component:

    ```bash
    tiup cluster stop ${cluster-name} -R tidb
    ```

- This command stops only the TiDB components on the `1.2.3.4` and `1.2.3.5` hosts:

    ```bash
    tiup cluster stop ${cluster-name} -N 1.2.3.4:4000,1.2.3.5:4000
    ```
## Clean up cluster data

The operation of cleaning up cluster data stops all the services and cleans up the data directory or/and log directory. The operation cannot be reverted, so proceed **with caution**.

- Clean up the data of all services in the cluster, but keep the logs:

    ```bash
    tiup cluster clean ${cluster-name} --data
    ```

- Clean up the logs of all services in the cluster, but keep the data:

    ```bash
    tiup cluster clean ${cluster-name} --log
    ```

- Clean up the data and logs of all services in the cluster:

    ```bash
    tiup cluster clean ${cluster-name} --all
    ```

- Clean up the logs and data of all services except Prometheus:

    ```bash
    tiup cluster clean ${cluster-name} --all --ignore-role prometheus
    ```

- Clean up the logs and data of all services except the `172.16.13.11:9000` instance:

    ```bash
    tiup cluster clean ${cluster-name} --all --ignore-node 172.16.13.11:9000
    ```

- Clean up the logs and data of all services except the `172.16.13.12` node:

    ```bash
    tiup cluster clean ${cluster-name} --all --ignore-node 172.16.13.12
    ```
## Destroy the cluster

The destroy operation stops the services and clears the data directory and deployment directory. The operation cannot be reverted, so proceed **with caution**.

```bash
tiup cluster destroy ${cluster-name}
```
