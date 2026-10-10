# Grafana panel analysis and visualization tips

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/grafana-monitor-best-practices.md`
- Source Title: `Best Practices for Monitoring TiDB Using Grafana`
- Source Heading Path: `Best Practices for Monitoring TiDB Using Grafana > Grafana tips | Best Practices for Monitoring TiDB Using Grafana > Grafana tips > Tip 1: Check all dimensions and edit the query expression | Best Practices for Monitoring TiDB Using Grafana > Grafana tips > Tip 2: Switch the scale of the Y-axis | Best Practices for Monitoring TiDB Using Grafana > Grafana tips > Tip 3: Modify the baseline of the Y-axis to amplify changes | Best Practices for Monitoring TiDB Using Grafana > Grafana tips > Tip 4: Use Shared crosshair or Tooltip | Best Practices for Monitoring TiDB Using Grafana > Grafana tips > Tip 5: Enter `IP address:port number` to check the metrics in history | Best Practices for Monitoring TiDB Using Grafana > Grafana tips > Tip 6: Use the `Avg` function`
- Source Line Ranges: `69-146`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `shared`
- Topic Tags: `grafana`, `dimensions`, `legend-format`, `y-axis`, `linear-scale`, `baseline`, `shared-crosshair`, `tooltip`, `history`, `avg`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0010_ee91e01292`
- Source ID: `tidb-docs-8.1:best-practices/grafana-monitor-best-practices.md#grafana-tips`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6b38d831ec7d9109cf3330110a15307a8160a14c9041346c6a7f7872a2012c4f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/grafana-monitor-best-practices#grafana-tips
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/grafana-monitor-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when you need Grafana panel techniques for analyzing TiDB metrics, including checking available dimensions, changing Y-axis scale or baseline, correlating panels with shared tooltip options, querying historical PD leader metrics, or adding average summaries.
- Retrieval Keywords: Grafana tips, Only keep the metric name on the query expression, Legend format field blank, instance job type, add the instance dimension after type, {{instance}}, Switch the scale of the Y-axis, binary logarithmic scale, linear scale, sql_type, Modify the baseline of the Y-axis, baseline 0 to auto, Store size, Graph Tooltip, Shared crosshair, Shared Tooltip, IP address:2379, PD's dashboard only shows the metrics of the current leader, Avg function, Max, Current
- Follow-up Guidance: It notes that you can manually enter `IP address:2379` to view historical metrics for a PD leader that no longer appears in the `instance` drop-down list.
- Classification Note: This chunk is classified under the dashboard component because it focuses on Grafana panel configuration and visualization methods for interpreting monitoring data.

## Official Source Content

## Grafana tips

This section introduces seven tips for efficiently using Grafana to monitor and analyze the metrics of TiDB.
### Tip 1: Check all dimensions and edit the query expression

In the example shown in the [source and display of monitoring data](#source-and-display-of-monitoring-data) section, the data is grouped by type. If you want to know whether you can group by other dimensions and quickly check which dimensions are available, you can use the following method: **Only keep the metric name on the query expression, no calculation, and leave the `Legend format` field blank**. In this way, the original metrics are displayed. For example, the following figure shows that there are three dimensions (`instance`, `job` and `type`):

![Edit query expression and check all dimensions](/media/best-practices/edit-expression-check-dimensions.jpg)

Then you can modify the query expression by adding the `instance` dimension after `type`, and adding `{{instance}}` to the `Legend format` field. In this way, you can check the QPS of different types of SQL statements that are executed on each TiDB server:

![Add an instance dimension to the query expression](/media/best-practices/add-instance-dimension.jpeg)
### Tip 2: Switch the scale of the Y-axis

Take Query Duration as an example, the Y-axis defaults to be on a binary logarithmic scale (log<sub>2</sub>n), which narrows the gap in display. To amplify changes, you can switch it to a linear scale. Comparing the following two figures, you can easily notice the difference in display, and locate the time when an SQL statement runs slowly.

Of course, a linear scale is not suitable for all situations. For example, if you observe the performance trend for the duration of a month, there might be noises with a linear scale, making it hard to observe.

The Y-axis uses a binary logarithmic scale by default:

![The Y-axis uses a binary logarithmic scale](/media/best-practices/default-axes-scale.jpg)

Switch the Y-axis to a linear scale:

![Switch to a linear scale](/media/best-practices/axes-scale-linear.jpg)

> **Tip:**
>
> Combining tip 2 with tip 1, you can find a `sql_type` dimension to help you immediately analyze whether the `SELECT` statement or the `UPDATE` statement is slow; you can even locate the instance with slow SQL statements.
### Tip 3: Modify the baseline of the Y-axis to amplify changes

You might still cannot see the trend after switching to the linear scale. For example, in the following figure, you want to observe the real-time change of `Store size` after scaling the cluster, but due to the large baseline, small changes are not visible. In this situation, you can modify the baseline of the Y-axis from `0` to `auto` to zoom in the upper part. Check the two figures below, you can see data migration begins.

The baseline defaults to `0`:

![Baseline defaults to 0](/media/best-practices/default-y-min.jpeg)

Change the baseline to `auto`:

![Change the baseline to auto](/media/best-practices/y-min-auto.jpg)
### Tip 4: Use Shared crosshair or Tooltip

In the **Settings** panel, there is a **Graph Tooltip** panel option which defaults to **Default**.

![Graphic presentation tools](/media/best-practices/graph-tooltip.jpeg)

You can use **Shared crosshair** and **Shared Tooltip** respectively to test the effect as shown in the following figures. Then, the scales are displayed in linkage, which is convenient to confirm the correlation of two metrics when diagnosing problems.

Set the graphic presentation tool to **Shared crosshair**:

![Set the graphical presentation tool to Shared crosshair](/media/best-practices/graph-tooltip-shared-crosshair.jpeg)

Set the graphical presentation tool to **Shared Tooltip**:

![Set the graphic presentation tool to Shared Tooltip](/media/best-practices/graph-tooltip-shared-tooltip.jpg)
### Tip 5: Enter `IP address:port number` to check the metrics in history

PD's dashboard only shows the metrics of the current leader. If you want to check the status of a PD leader in history and it no longer exists in the drop-down list of the `instance` field, you can manually enter `IP address:2379` to check the data of the leader.

![Check the metrics in history](/media/best-practices/manually-input-check-metric.jpeg)
### Tip 6: Use the `Avg` function

Generally, only `Max` and `Current` functions are available in the legend by default. When the metrics fluctuate greatly, you can add other summary functions such as the `Avg` function to the legend to check the overall trend for the duration of time.

Add summary functions such as the `Avg` function:

![Add summary functions such as Avg](/media/best-practices/add-avg-function.jpeg)

Then check the overall trend:

![Add Avg function to check the overall trend](/media/best-practices/add-avg-function-check-trend.jpg)
