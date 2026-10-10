# Check cluster status with TiUP, Dashboard, and Grafana

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/post-installation-check.md`
- Source Title: `Check Cluster Status`
- Source Heading Path: `Check Cluster Status | Check Cluster Status > Check the TiDB cluster status | Check Cluster Status > Check the TiDB cluster status > Use TiUP | Check Cluster Status > Check the TiDB cluster status > Use TiDB Dashboard | Check Cluster Status > Check the TiDB cluster status > Use Grafana`
- Source Line Ranges: `5-43`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `dashboard`, `pd`, `shared`
- Topic Tags: `cluster status`, `post-installation`, `health check`, `tiup`, `dashboard`, `grafana`, `node status`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0193_87e7e61af1`
- Source ID: `tidb-docs-8.1:post-installation-check.md#check-cluster-status`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c680e62daa82779a69e08b69fe70988cf4b5c9ca8af0ecd8d4e3864ba871b4f3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/post-installation-check#check-cluster-status
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/post-installation-check.md

## Retrieval Guidance

- Use When: Use this chunk when checking whether a newly deployed TiDB cluster runs normally through TiUP, TiDB Dashboard, or Grafana.
- Retrieval Keywords: tiup cluster display <cluster-name>, tiup cluster display tidb-test, Status Up, TiDB Dashboard, ${pd-ip}:${pd-port}/dashboard, Grafana, ${Grafana-ip}:3000, Overview, check cluster status, node information, port status, load monitoring information
- Follow-up Guidance: It also states that the TiDB Dashboard username and password are the same as the TiDB root user, and Grafana defaults to username admin and password admin.
- Classification Note: The classification is operation for the tiup component because the content describes post-installation cluster health checking with TiUP commands and related monitoring interfaces.

## Official Source Content

# Check Cluster Status

After a TiDB cluster is deployed, you need to check whether the cluster runs normally. This document introduces how to check the cluster status using TiUP commands, [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro) and Grafana, and how to log into the TiDB database to perform simple SQL operations.
## Check the TiDB cluster status

This section describes how to check the TiDB cluster status using TiUP commands, [TiDB Dashboard](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-intro), and Grafana.
### Use TiUP

Use the `tiup cluster display <cluster-name>` command to check the cluster status. For example:

```shell
tiup cluster display tidb-test
```

Expected output: If the `Status` information of each node is `Up`, the cluster runs normally.
### Use TiDB Dashboard

1. Log in to TiDB Dashboard at `${pd-ip}:${pd-port}/dashboard`. The username and password is the same as that of the TiDB `root` user. If you have modified the `root` password, enter the modified password. The password is empty by default.

    ![TiDB-Dashboard](/media/tiup/tidb-dashboard.png)

2. The home page displays the node information in the TiDB cluster.

    ![TiDB-Dashboard-status](/media/tiup/tidb-dashboard-status.png)
### Use Grafana

1. Log in to the Grafana monitoring at `${Grafana-ip}:3000`. The default username and password are both `admin`.

2. To check the TiDB port status and load monitoring information, click **Overview**.

    ![Grafana-overview](/media/tiup/grafana-overview.png)
