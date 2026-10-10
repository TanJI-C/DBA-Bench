# Dashboard cluster diagnostics access and report generation

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-diagnostics-access.md`
- Source Title: `TiDB Dashboard Cluster Diagnostic Page`
- Source Heading Path: `TiDB Dashboard Cluster Diagnostics Page | TiDB Dashboard Cluster Diagnostics Page > Access the page | TiDB Dashboard Cluster Diagnostics Page > Generate diagnostic report | TiDB Dashboard Cluster Diagnostics Page > Generate comparison report`
- Source Line Ranges: `5-61`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tiup`, `shared`
- Topic Tags: `cluster-diagnostics`, `report-generation`, `comparison-report`, `baseline`, `prometheus-dependency`, `offline-browsing`, `historical-reports`, `access-paths`, `time-range`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0013_58a3316ead`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-diagnostics-access.md#tidb-dashboard-cluster-diagnostics-page`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `19fdba7f5bba79e60371ee0aba2fdcc5dceb020337e848e9a8a17acc20f21285`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-diagnostics-access#tidb-dashboard-cluster-diagnostics-page
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-diagnostics-access.md

## Retrieval Guidance

- Use When: Use this content when someone needs TiDB Dashboard cluster diagnostics page access, diagnostic report generation for a specified time range, comparison report generation with a baseline, or historical diagnostic report viewing.
- Retrieval Keywords: TiDB Dashboard Cluster Diagnostics, Cluster Diagnostics, cluster diagnostics page, http://127.0.0.1:2379/dashboard/#/diagnose, PD address and port number, Generate diagnostic report, Generate comparison report, Compare by Baseline, Baseline Range Start Time, Range Start Time, Range Duration, View Full Report, Progress, historical diagnostic report, Prometheus deployed in the cluster, offline browse report
- Follow-up Guidance: The source also states that the cluster diagnostics feature depends on Prometheus deployed in the cluster, and if no monitoring component is deployed, the generated diagnostic report will indicate a failure.
- Classification Note: The classification is diagnosis for the dashboard component in a self-managed deployment because the content explains how TiDB Dashboard diagnoses cluster problems within a specified time range and generates diagnostic and comparison reports.

## Official Source Content

# TiDB Dashboard Cluster Diagnostics Page

The cluster diagnostics feature in TiDB Dashboard diagnoses the problems that might exist in a cluster within a specified time range, and summarizes the diagnostic results and the cluster-related load monitoring information into a diagnostic report. This diagnostic report is in the form of a web page. You can browse the page offline and circulate this page link after saving the page from a browser.

> **Note:**
>
> The cluster diagnostics feature depends on Prometheus deployed in the cluster. For details about how to deploy this monitoring component, see the [TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-overview) deployment document. If no monitoring component is deployed in the cluster, the generated diagnostic report will indicate a failure.
## Access the page

You can use one of the following methods to access the cluster diagnostics page:

* After logging in to TiDB Dashboard, click **Cluster Diagnostics** in the left navigation menu.

  ![Access Cluster Diagnostics page](/media/dashboard/dashboard-diagnostics-access-v650.png)

* Visit `http://127.0.0.1:2379/dashboard/#/diagnose` in your browser. Replace `127.0.0.1:2379` with the actual PD address and port number.
## Generate diagnostic report

To diagnose a cluster within a specified time range and check the cluster load, you can take the following steps to generate a diagnostic report:

1. Set the **Range Start Time**, such as `2022-05-21 14:40:00`.
2. Set the **Range Duration**, such as `10 min`.
3. Click **Start**.

![Generate diagnostic report](/media/dashboard/dashboard-diagnostics-gen-report-v650.png)

> **Note:**
>
> It is recommended that the **Range Duration** of the report is between 1 minute and 60 minutes. This **Range Duration** cannot exceed 60 minutes.

The preceding steps generate a diagnostic report for the time range from `2022-05-21 14:40:00` to `2022-05-21 14:50:00`. After clicking **Start**, you can see the interface below. **Progress** is the progress bar of the diagnostic report. After the report is generated, click **View Full Report**.

![Report progress](/media/dashboard/dashboard-diagnostics-gen-process-v650.png)
## Generate comparison report

If a system exception occurs at a certain point, for example, QPS jitter or higher latency, a diagnostic report can be generated. Particularly, this report compares the system in the abnormal time range with the system in the normal time range. For example:

- Abnormal time range: `2022-05-21 14:40:00`-`2022-05-21 14:45:00`. Within this time range, the system is abnormal.
- Normal time range: `2022-05-21 14:30:00` - `2022-05-21 14:35:00`. Within this time range, the system is normal.

You can take the following steps to generate a comparison report for the preceding two time ranges:

1. Set the **Range Start Time**, which is the start time of the range in which the system becomes abnormal, such as `2022-05-21 14:40:00`.
2. Set the **Range Duration**. Generally, this duration is the duration of system anomalies, such as 5 minutes.
3. Enable **Compare by Baseline**.
4. Set the **Baseline Range Start Time**, which is the start time of the range (to be compared with) in which the system is normal, such as `2022-05-21 14:30:00`.
5. Click **Start**.

![Generate comparison report](/media/dashboard/dashboard-diagnostics-gen-compare-report-v650.png)

Then wait for the report to be generated and click **View Full Report**.

In addition, the historical diagnostic report is displayed in the list on the main page of the diagnostic report. You can click to view these historical reports directly.
