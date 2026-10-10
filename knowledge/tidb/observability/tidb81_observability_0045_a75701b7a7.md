# MetricsTool Grafana snapshot export, visualization, and FAQs

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/exporting-grafana-snapshots.md`
- Source Title: `Export Grafana Snapshots`
- Source Heading Path: `Export Grafana Snapshots | Export Grafana Snapshots > Usage | Export Grafana Snapshots > FAQs | Export Grafana Snapshots > FAQs > What is the advantage of this tool compared with screenshot or PDF printing? | Export Grafana Snapshots > FAQs > What are included in the snapshot file? | Export Grafana Snapshots > FAQs > Will the Visualizer save the uploaded snapshot files in PingCAP's servers? | Export Grafana Snapshots > FAQs > Will there be problems to execute the script before all metrics are loaded? | Export Grafana Snapshots > FAQs > Can we share a link to a visualized snapshot?`
- Source Line Ranges: `5-53`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `shared`
- Topic Tags: `grafana`, `metrics`, `snapshots`, `visualization`, `privacy`, `troubleshooting`, `faq`, `export`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0045_a75701b7a7`
- Source ID: `tidb-docs-8.1:exporting-grafana-snapshots.md#export-grafana-snapshots`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `13c0b024d25d0d507fdc0f2adf973d1bc6d5db8bdadff291be070f39a34766c2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/exporting-grafana-snapshots#export-grafana-snapshots
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/exporting-grafana-snapshots.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about exporting Grafana dashboard snapshots with MetricsTool, visualizing snapshot files locally, understanding what snapshot files contain, or checking the documented privacy and sharing limitations of the Visualizer.
- Retrieval Keywords: Export Grafana Snapshots, MetricsTool, metricstool.pingcap.net, Grafana v6.x.x, Export, Visualize, Import, snapshot files, all visible panels, current dashboard, support staff, remote assistance, actual values, toggling series, zooming into a smaller time range, precise value at a given time, does not save the original metrics from the data sources, cannot edit the query expression in the Visualizer, Nothing will be sent to PingCAP, inside your browser, wait for all metrics to be loaded, manually skip waiting, share the snapshot file, world-readable URL, snapshot.raintank.io, PingCAP Clinic diagnostic service
- Follow-up Guidance: The source also states that since TiDB v6.0.0 PingCAP no longer maintains MetricsTool, since v6.1.0 PingCAP no longer maintains the MetricsTool document, and recommends PingCAP Clinic diagnostic service to export monitoring metrics data.
- Classification Note: This chunk is classified under observability and dashboard because it documents a Grafana snapshot export and visualization tool, including usage, FAQ behavior, privacy, and troubleshooting-related sharing context.

## Official Source Content

> **Warning:**
>
> - Since TiDB v6.0.0, PingCAP no longer maintains MetricsTool. Since v6.1.0, PingCAP no longer maintains the MetricsTool document.
> - To export monitoring metrics data, use the [PingCAP Clinic diagnostic service](https://docs.pingcap.com/tidb/stable/clinic/clinic-introduction) to get the information required for diagnosing a TiDB cluster, including the monitoring metrics, logs, cluster topology, configuration, and parameters.

# Export Grafana Snapshots

> **Note:**
>
> Currently, MetricsTool can only be used with Grafana v6.x.x.

Metrics data is important in troubleshooting. When you request remote assistance, sometimes the support staff need to view the Grafana dashboards to diagnose problems. [MetricsTool](https://metricstool.pingcap.net/) can help export snapshots of Grafana dashboards as local files and visualize these snapshots. You can share these snapshots with outsiders and allow them to accurately read out the graphs, without giving out access to other sensitive information on the Grafana server.
## Usage

MetricsTool can be accessed from <https://metricstool.pingcap.net/>. It consists of three sets of tools:

* **Export**: A user script running on the browser's Developer Tool, allowing you to download a snapshot of all visible panels in the current dashboard on any Grafana v6.x.x server.

    ![Screenshot of MetricsTool Exporter after running the user script](/media/metricstool-export.png)

* **Visualize**: A web page visualizing the exported snapshot files. The visualized snapshots can be operated in the same way as live Grafana dashboards.

    ![Screenshot of MetricsTool Visualizer](/media/metricstool-visualize.png)

* **Import**: Instructions to import the exported snapshot back into an actual Grafana instance.
## FAQs
### What is the advantage of this tool compared with screenshot or PDF printing?

The snapshot files exported by MetricsTool contain the actual values when they are taken. And the Visualizer allows you to interact with the rendered graphs as if it is a live Grafana dashboard, supporting operations like toggling series, zooming into a smaller time range, and checking the precise value at a given time. This makes MetricsTool much more powerful than images or PDFs.
### What are included in the snapshot file?

The snapshot file contains the values of all graphs and panels in the selected time range. It does not save the original metrics from the data sources (and thus you cannot edit the query expression in the Visualizer).
### Will the Visualizer save the uploaded snapshot files in PingCAP's servers?

No, the Visualizer parses the snapshot files entirely inside your browser. Nothing will be sent to PingCAP. You are free to view snapshot files received from sensitive sources, and no need to worry about these leaking to third parties through the Visualizer.
### Will there be problems to execute the script before all metrics are loaded?

No, the script UI will notify you to wait for all metrics to be loaded. However, you can manually skip waiting and export the snapshot in case of some metrics loading for too long.
### Can we share a link to a visualized snapshot?

No, but you can share the snapshot file, with instruction on how to use the Visualizer to view it. If you truly need a world-readable URL, you may also try the public `snapshot.raintank.io` service built into Grafana, but make sure all privacy concerns are cleared before doing so.
