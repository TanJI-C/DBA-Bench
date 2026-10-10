# Dashboard deployment and PD serving instance management

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-ops-deploy.md`
- Source Title: `Deploy TiDB Dashboard`
- Source Heading Path: `Deploy TiDB Dashboard | Deploy TiDB Dashboard > Deployment with multiple PD instances | Deploy TiDB Dashboard > Deployment with multiple PD instances > Check the PD instance that actually serves TiDB Dashboard | Deploy TiDB Dashboard > Deployment with multiple PD instances > Switch to another PD instance to serve TiDB Dashboard`
- Source Line Ranges: `5-94`
- Source Scope: `all`
- Primary Component: `dashboard`
- Related Components: `pd`, `tiup`, `operator`
- Topic Tags: `deployment`, `pd-instances`, `serving-instance`, `tiup`, `kubernetes`, `version-support`, `dashboard-address`, `redirects`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0037_862bc255ac`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-ops-deploy.md#deploy-tidb-dashboard`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3e82843db7a2397e176db2a9868bdd45a3d0285750aff8c2936a1e46bc16982c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-ops-deploy#deploy-tidb-dashboard
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-ops-deploy.md

## Retrieval Guidance

- Use When: Use this chunk when you need information about how TiDB Dashboard is deployed with PD, how the serving PD instance is chosen or redirected in a multi-PD cluster, or how to check or switch the serving instance with TiUP.
- Retrieval Keywords: TiDB Dashboard built into PD, v4.0 or higher, cannot deploy TiDB Dashboard earlier than v4.0, multiple PD instances, only one instance serves the TiDB Dashboard, browser redirected automatically, PD instance that serves TiDB Dashboard might not be a PD leader, tiup cluster display CLUSTER_NAME --dashboard, dashboard-address, tiup ctl:v<CLUSTER_VERSION> pd, config set dashboard-address http://9.9.9.9:2379, independent Pod on Kubernetes, TiDB v6.5.0, TiDB Operator v1.4.0
- Follow-up Guidance: The source also states that changing the PD instance that runs TiDB Dashboard causes local data in the previous TiDB Dashboard instance, including Key Visualize history and search history, to be lost.
- Classification Note: This is classified as an operation chunk because the content describes deployment behavior, PD serving instance management, and TiUP commands for checking and changing the TiDB Dashboard serving instance.

## Official Source Content

# Deploy TiDB Dashboard

The TiDB Dashboard UI is built into the PD component for v4.0 or higher versions, and no additional deployment is required. Simply deploy a standard TiDB cluster, and TiDB Dashboard will be there.

> **Note:**
>
> TiDB v6.5.0 (and later) and TiDB Operator v1.4.0 (and later) support deploying TiDB Dashboard as an independent Pod on Kubernetes. For details, see [Deploy TiDB Dashboard independently in TiDB Operator](https://docs.pingcap.com/tidb-in-kubernetes/v1.6/get-started#deploy-tidb-dashboard-independently).

See the following documents to learn how to deploy a standard TiDB cluster:

+ [Quick Start Guide for the TiDB Database Platform](https://docs.pingcap.com/tidb/stable/quick-start-with-tidb)
+ [Deploy TiDB in Production Environment](https://docs.pingcap.com/tidb/stable/production-deployment-using-tiup)
+ [Kubernetes environment deployment](https://docs.pingcap.com/tidb-in-kubernetes/stable/access-dashboard)

> **Note:**
>
> You cannot deploy TiDB Dashboard in a TiDB cluster earlier than v4.0.
## Deployment with multiple PD instances

When multiple PD instances are deployed in the cluster, only one of these instances serves the TiDB Dashboard.

When PD instances are running for the first time, they automatically negotiate with each other to choose one instance to serve the TiDB Dashboard. TiDB Dashboard will not run on other PD instances. The TiDB Dashboard service will always be provided by the chosen PD instance no matter PD instances are restarted or new PD instances are joined. However, there will be a re-negotiation when the PD instance that serves TiDB Dashboard is removed from the cluster (scaled-in). The negotiation process does not need user intervention.

When you access a PD instance that does not serve TiDB Dashboard, the browser will be redirected automatically to guide you to access the PD instance that serves the TiDB Dashboard, so that you can access the service normally. This process is illustrated in the image below.

![Process Schematic](/media/dashboard/dashboard-ops-multiple-pd.png)

> **Note:**
>
> The PD instance that serves TiDB Dashboard might not be a PD leader.
### Check the PD instance that actually serves TiDB Dashboard

For a running cluster deployed using TiUP, you can use the `tiup cluster display` command to see which PD instance serves TiDB Dashboard. Replace `CLUSTER_NAME` with the cluster name.

```bash
tiup cluster display CLUSTER_NAME --dashboard
```

A sample output is as follows:

```bash
http://192.168.0.123:2379/dashboard/
```

> **Note:**
>
> This feature is available only in the later version of the `tiup cluster` deployment tool (v1.0.3 or later).
>
> <details>
> <summary>Upgrade TiUP Cluster</summary>
>
> ```bash
> tiup update --self
> tiup update cluster --force
> ```
>
> </details>
### Switch to another PD instance to serve TiDB Dashboard

For a running cluster deployed using TiUP, you can use the `tiup ctl:v<CLUSTER_VERSION> pd` command to change the PD instance that serves TiDB Dashboard, or re-specify a PD instance to serve TiDB Dashboard when it is disabled:

```bash
tiup ctl:v<CLUSTER_VERSION> pd -u http://127.0.0.1:2379 config set dashboard-address http://9.9.9.9:2379
```

In the command above:

- Replace `127.0.0.1:2379` with the IP and port of any PD instance.
- Replace `9.9.9.9:2379` with the IP and port of the new PD instance that you desire to run the TiDB Dashboard service.

You can use the `tiup cluster display` command to see whether the modification is taking effect (replace `CLUSTER_NAME` with the cluster name):

```bash
tiup cluster display CLUSTER_NAME --dashboard
```

> **Warning:**
>
> If you change the instance to run TiDB Dashboard, the local data stored in the previous TiDB Dashboard instance will be lost, including the Key Visualize history and search history.
