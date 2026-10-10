# TiUP cluster listing, startup, and status display

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/maintain-tidb-using-tiup.md`
- Source Title: `TiUP Common Operations`
- Source Heading Path: `TiUP Common Operations | TiUP Common Operations > View the cluster list | TiUP Common Operations > Start the cluster | TiUP Common Operations > View the cluster status`
- Source Line Ranges: `5-78`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`, `tikv`, `tidb`, `tiflash`, `ticdc`, `shared`
- Topic Tags: `cluster-list`, `start-order`, `component-start`, `role-filtering`, `node-filtering`, `status-check`, `display-command`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0157_424034fa9c`
- Source ID: `tidb-docs-8.1:maintain-tidb-using-tiup.md#tiup-common-operations`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7434aaff0ab8bdbed30107ca569862482c21e4abe62839f43c62ad48bb674290`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/maintain-tidb-using-tiup#tiup-common-operations
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/maintain-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this when you need the TiUP commands for listing a cluster, starting it, or checking component status after startup.
- Retrieval Keywords: tiup cluster list, tiup cluster start ${cluster-name}, tiup cluster display ${cluster-name}, -R pd, -N 1.2.3.4:2379,1.2.3.5:2379, PD > TiKV > Pump > TiDB > TiFlash > Drainer > TiCDC > Prometheus > Grafana > Alertmanager
- Follow-up Guidance: If you forget the cluster name, check it with `tiup cluster list`.
- Classification Note: This chunk is about TiUP common operations for viewing the cluster list, starting the cluster, and displaying cluster status.

## Official Source Content

# TiUP Common Operations

This document describes the following common operations when you operate and maintain a TiDB cluster using TiUP.

- View the cluster list
- Start the cluster
- View the cluster status
- Modify the configuration
- Stop the cluster
- Destroy the cluster
## View the cluster list

You can manage multiple TiDB clusters using the TiUP cluster component. When a TiDB cluster is deployed, the cluster appears in the TiUP cluster list.

To view the list, run the following command:

```bash
tiup cluster list
```
## Start the cluster

The components in the TiDB cluster are started in the following order:

**PD > TiKV > Pump > TiDB > TiFlash > Drainer > TiCDC > Prometheus > Grafana > Alertmanager**

To start the cluster, run the following command:

```bash
tiup cluster start ${cluster-name}
```

> **Note:**
>
> Replace `${cluster-name}` with the name of your cluster. If you forget the cluster name, check it by running `tiup cluster list`.

You can start only some of the components by adding the `-R` or `-N` parameters in the command. For example:

- This command starts only the PD component:

    ```bash
    tiup cluster start ${cluster-name} -R pd
    ```

- This command starts only the PD components on the `1.2.3.4` and `1.2.3.5` hosts:

    ```bash
    tiup cluster start ${cluster-name} -N 1.2.3.4:2379,1.2.3.5:2379
    ```

> **Note:**
>
> If you start the specified component by using the `-R` or `-N` parameters, make sure the starting order is correct. For example, start the PD component before the TiKV component. Otherwise, the start might fail.
## View the cluster status

After starting the cluster, check the status of each component to ensure that they work normally. TiUP provides the `display` command, so you do not have to log in to every machine to view the component status.

```bash
tiup cluster display ${cluster-name}
```
