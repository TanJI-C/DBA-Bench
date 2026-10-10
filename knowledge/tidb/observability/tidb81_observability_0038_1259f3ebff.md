# Configure Grafana data sources, dashboards, and metric views

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/deploy-monitoring-services.md`
- Source Title: `Deploy Monitoring Services for the TiDB Cluster`
- Source Heading Path: `Deploy Monitoring Services for the TiDB Cluster > Configure Grafana | Deploy Monitoring Services for the TiDB Cluster > Configure Grafana > Step 1: Add a Prometheus data source | Deploy Monitoring Services for the TiDB Cluster > Configure Grafana > Step 2: Import a Grafana dashboard | Deploy Monitoring Services for the TiDB Cluster > View component metrics`
- Source Line Ranges: `207-287`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `shared`, `pd`, `tidb`, `tikv`
- Topic Tags: `grafana`, `data-source`, `dashboard-import`, `metrics`, `visualization`, `monitoring`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0038_1259f3ebff`
- Source ID: `tidb-docs-8.1:deploy-monitoring-services.md#configure-grafana`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d4fd5967dd4fea3ef88769535bfd7f7bfa3028d6a2687da4073a1ba634fce50`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/deploy-monitoring-services#configure-grafana
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/deploy-monitoring-services.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how to configure Grafana with a Prometheus data source, import TiDB, TiKV, and PD dashboards, and identify the metrics visible for those components.
- Retrieval Keywords: Configure Grafana, Add a Prometheus data source, Grafana Web interface, http://localhost:3000, admin admin, Data Source, Add data source, Type Prometheus, URL specify the Prometheus address, Import Dashboard, Upload .json File, pingcap/tidb release-8.1 pkg/metrics/grafana, tikv/tikv release-8.1 metrics/grafana, tikv/pd release-8.1 metrics/grafana, tikv_summary.json, tikv_details.json, tikv_trouble_shooting.json, pd.json, tidb.json, tidb_summary.json, View component metrics, New dashboard
- Follow-up Guidance: The source lists example metric views for TiDB server, PD server, and TiKV server dashboards, such as query processing time, DDL monitoring, GC monitoring, and Raft-related metrics.
- Classification Note: The official content is classified as observability because it focuses on Grafana data source setup, dashboard import, and viewing metrics for TiDB cluster components.

## Official Source Content

## Configure Grafana

This section describes how to configure Grafana.
### Step 1: Add a Prometheus data source

1. Log in to the Grafana Web interface.

    - Default address: [http://localhost:3000](http://localhost:3000)
    - Default account: admin
    - Default password: admin

    > **Note:**
    >
    > For the **Change Password** step, you can choose **Skip**.

2. In the Grafana sidebar menu, click **Data Source** within the **Configuration**.

3. Click **Add data source**.

4. Specify the data source information.

    - Specify a **Name** for the data source.
    - For **Type**, select **Prometheus**.
    - For **URL**, specify the Prometheus address.
    - Specify other fields as needed.

5. Click **Add** to save the new data source.
### Step 2: Import a Grafana dashboard

To import a Grafana dashboard for the PD server, the TiKV server, and the TiDB server, take the following steps respectively:

1. Click the Grafana logo to open the sidebar menu.

2. In the sidebar menu, click **Dashboards** -> **Import** to open the **Import Dashboard** window.

3. Click **Upload .json File** to upload a JSON file (Download TiDB Grafana configuration files from [pingcap/tidb](https://github.com/pingcap/tidb/tree/release-8.1/pkg/metrics/grafana), [tikv/tikv](https://github.com/tikv/tikv/tree/release-8.1/metrics/grafana), and [tikv/pd](https://github.com/tikv/pd/tree/release-8.1/metrics/grafana)).

    > **Note:**
    >
    > For the TiKV, PD, and TiDB dashboards, the corresponding JSON files are `tikv_summary.json`, `tikv_details.json`, `tikv_trouble_shooting.json`, `pd.json`, `tidb.json`, and `tidb_summary.json`.

4. Click **Load**.

5. Select a Prometheus data source.

6. Click **Import**. A Prometheus dashboard is imported.
## View component metrics

Click **New dashboard** in the top menu and choose the dashboard you want to view.

![view dashboard](/media/view-dashboard.png)

You can get the following metrics for cluster components:

+ **TiDB server:**

    - Query processing time to monitor the latency and throughput
    - The DDL process monitoring
    - TiKV client related monitoring
    - PD client related monitoring

+ **PD server:**

    - The total number of times that the command executes
    - The total number of times that a certain command fails
    - The duration that a command succeeds
    - The duration that a command fails
    - The duration that a command finishes and returns result

+ **TiKV server:**

    - Garbage Collection (GC) monitoring
    - The total number of times that the TiKV command executes
    - The duration that Scheduler executes commands
    - The total number of times of the Raft propose command
    - The duration that Raft executes commands
    - The total number of times that Raft commands fail
    - The total number of times that Raft processes the ready state
