# Dashboard NgMonitoring startup and browser cache issues

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-faq.md`
- Source Title: `TiDB Dashboard FAQs`
- Source Heading Path: `TiDB Dashboard FAQs > UI-related FAQ > A `required component NgMonitoring is not started` error is shown | TiDB Dashboard FAQs > UI-related FAQ > An `unknown field` error is shown on the **Slow Queries** page`
- Source Line Ranges: `61-165`
- Source Scope: `shared`
- Primary Component: `dashboard`
- Related Components: `tiup`, `operator`, `tidb`
- Topic Tags: `ui`, `ngmonitoring`, `continuous-profiling`, `top-sql`, `version-check`, `reload`, `browser-cache`, `slow-queries`, `compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0016_c5f2f14ace`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-faq.md#a-required-component-ngmonitoring-is-not-started-error-is-shown`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `397e38312aed04c0515d751596ff1a16f0bcf1aba068317bbad5ed27c8ad8de8`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-faq#a-required-component-ngmonitoring-is-not-started-error-is-shown
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-faq.md

## Retrieval Guidance

- Use When: Use this chunk when TiDB Dashboard reports `required component NgMonitoring is not started` for features such as Continuous Profiling or Top SQL, or when the Slow Queries page shows an `unknown field` error after a cluster upgrade.
- Retrieval Keywords: required component NgMonitoring is not started, NgMonitoring, Continuous Profiling, Top SQL, TiUP v1.9.0 or later, tiup cluster --version, tiup update --all, tiup cluster edit-config ${cluster-name}, monitoring_servers, ng_port: 12020, tiup cluster reload ${cluster-name} --role prometheus, TiDB Operator, Enable Continuous Profiling, TiUP Playground >= v1.8.0, tiup update playground, unknown field, Slow Queries page, browser cache, Developer Tools, Application panel, Local Storage, Clear All, v5.0.3, v4.0.14
- Follow-up Guidance: The source provides TiUP version checks and reload steps for NgMonitoring, points TiDB Operator users to Enable Continuous Profiling, and describes clearing Local Storage in browser Developer Tools for the `unknown field` error on earlier than v5.0.3 or v4.0.14 clusters.
- Classification Note: This is classified as diagnosis because the content focuses on troubleshooting NgMonitoring startup and browser cache compatibility issues that surface as Dashboard UI errors.

## Official Source Content

### A `required component NgMonitoring is not started` error is shown

NgMonitoring is an advanced monitoring component built in TiDB clusters of v5.4.0 and later versions to support TiDB Dashboard features such as **Continuous Profiling** and **Top SQL**. NgMonitoring is automatically deployed when you deploy or upgrade a cluster with a newer version of TiUP. For clusters deployed using TiDB Operator, you can deploy NgMonitoring manually by referring to [Enable Continuous Profiling](https://docs.pingcap.com/tidb-in-kubernetes/v1.6/access-dashboard/#enable-continuous-profiling).

If the web page shows `required component NgMonitoring is not started`, you can troubleshoot the deployment issue as follows:

<details>
  <summary>Clusters Deployed using TiUP</summary>

Step 1. Check versions

1. Check the TiUP cluster version. NgMonitoring is deployed only when TiUP is v1.9.0 or later.

    ```shell
    tiup cluster --version
    ```

    The command output shows the TiUP version. For example:

    ```
    tiup version 1.9.0 tiup
    Go Version: go1.17.2
    Git Ref: v1.9.0
    ```

2. If the TiUP cluster version is earlier than v1.9.0, upgrade TiUP and TiUP cluster to the latest version:

    ```shell
    tiup update --all
    ```

Step 2. Add the ng_port configuration item on the control machine by using TiUP. Then reload Prometheus.

1. Open the cluster configuration file in editing mode:

    ```shell
    tiup cluster edit-config ${cluster-name}
    ```

2. Under `monitoring_servers`, add the `ng_port:12020` parameter:

    ```
    monitoring_servers:
    - host: 172.16.6.6
      ng_port: 12020
    ```

3. Reload Prometheus:

    ```shell
    tiup cluster reload ${cluster-name} --role prometheus
    ```

If the error message is still prompted after performing steps above, [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.

</details>

<details>
  <summary>Clusters Deployed using TiDB Operator</summary>

Deploy the NgMonitoring component by following instructions in the [Enable Continuous Profiling](https://docs.pingcap.com/tidb-in-kubernetes/v1.6/access-dashboard/#enable-continuous-profiling) section in TiDB Operator documentation.

</details>

<details>
  <summary>Clusters Started using TiUP Playground</summary>

When starting the cluster, TiUP Playground (>= v1.8.0) automatically starts the NgMonitoring component. To update TiUP Playground to the latest version, run the following command:

```shell
tiup update --self
tiup update playground
```

</details>
### An `unknown field` error is shown on the **Slow Queries** page

If the `unknown field` error appears on the **Slow Queries** page after the cluster upgrade, the error is related to a compatibility issue caused by the difference between TiDB Dashboard server fields (which might be updated) and user preferences fields (which are in the browser cache). This issue has been fixed. If your cluster is earlier than v5.0.3 or v4.0.14, perform the following steps to clear your browser cache:

1. Open TiDB Dashboard page.

2. Open Developer Tools. Different browsers have different ways of opening Developer Tools. After clicking the **Menu Bar**:

    - Firefox: **Menu** > **Web Developer** > **Toggle Tools**, or **Tools** > **Web Developer** > **Toggle Tools**.
    - Chrome: **More tools** > **Developer tools**.
    - Safari: **Develop** > **Show Web Inspector**. If you can't see the **Develop** menu, go to **Safari** > **Preferences** > **Advanced**, and check the **Show Develop** menu in menu bar checkbox.

    In the following example, Chrome is used.

    ![Opening DevTools from Chrome's main menu](/media/dashboard/dashboard-faq-devtools.png)

3. Select the **Application** panel, expand the **Local Storage** menu and select the **TiDB Dashboard page domain**. Click the **Clear All** button.

    ![Clear the Local Storage](/media/dashboard/dashboard-faq-devtools-application.png)
