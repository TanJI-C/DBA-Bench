# Interpreting common Key Visualizer heatmaps and hotspot guidance

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-key-visualizer.md`
- Source Title: `Key Visualizer Page`
- Source Heading Path: `Key Visualizer Page > Common heatmap types | Key Visualizer Page > Common heatmap types > Evenly distributed workload | Key Visualizer Page > Common heatmap types > Periodically reads and writes | Key Visualizer Page > Common heatmap types > Concentrated reads or writes | Key Visualizer Page > Common heatmap types > Sequential reads or writes | Key Visualizer Page > Address hotspot issues`
- Source Line Ranges: `142-180`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `tikv`, `tidb`
- Topic Tags: `heatmap patterns`, `workload distribution`, `periodic traffic`, `concentrated traffic`, `sequential traffic`, `hotspot diagnosis`, `performance bottleneck`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0017_3fd7de8716`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-key-visualizer.md#common-heatmap-types`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `247b4dd241a3cab9fb4a0aba8aacbb81250b59e226898280524d612b37c08378`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-key-visualizer#common-heatmap-types
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-key-visualizer.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs help interpreting Key Visualizer heatmap patterns such as evenly distributed, periodic, concentrated, or sequential traffic and relating them to hotspot issues.
- Retrieval Keywords: Common heatmap types, Evenly distributed workload, Periodically reads and writes, Concentrated reads or writes, Sequential reads or writes, bright lines, Y-axis, X-axis, hotspot issues, performance bottleneck, auto-increment IDs, importing data, scanning tables and indexes, Highly Concurrent Write Best Practices
- Follow-up Guidance: It explains that sequential bright areas often indicate hotspots and mentions built-in features to mitigate common hotspot issues with a reference to Highly Concurrent Write Best Practices.
- Classification Note: This is classified as diagnosis because the content interprets heatmap patterns to diagnose workload distribution and hotspot-related performance bottlenecks.

## Official Source Content

## Common heatmap types

This section shows and interprets four common types of heatmap in Key Visualizer.
### Evenly distributed workload

![Balanced](/media/dashboard/dashboard-keyviz-well-dist.png)

In the heatmap above, bright and dark colors are a fine-grained mix. This indicates that reads or writes are evenly distributed over time and among key ranges. The workload is evenly distributed to all nodes, which is ideal for a distributed database.
### Periodically reads and writes

![Periodically](/media/dashboard/dashboard-keyviz-period.png)

In the heatmap above, there is an alternating brightness and darkness along the X-axis (time) but the brightness is relatively even along the Y-axis (Region). This indicates that the reads and writes change periodically, which might occur in scenarios of periodically scheduled tasks. For example, the big data platform periodically extracts data from TiDB every day. In this kind of scenarios, pay attention to whether the resources are sufficient during peak usage.
### Concentrated reads or writes

![Concentrated](/media/dashboard/dashboard-keyviz-continue.png)

In the heatmap above, you can see several bright lines. Along the Y-axis, the fringes around the bright lines are dark, which indicates that the Regions corresponding to bright lines have high read and write traffic. You can observe whether the traffic distribution is expected by your application. For example, when all services are associated with the user table, the overall traffic of the user table can be high, so it is reasonable to show bright lines in the heatmap.

In addition, the height of the bright lines (the thickness along the Y-axis) is important. Because TiKV has its own Region-based hotspot balancing mechanism, the more Regions involved in the hotspot, the better it is for balancing traffic across all TiKV instances. The thicker and more bright lines indicate that hotspots are more scattered, and TiKV is better used. The thinner and fewer bright lines indicate that hotspots are more concentrated, and the hotspot issue is more obvious in TiKV, which might requires manual intervention.
### Sequential reads or writes

![Sequential](/media/dashboard/dashboard-keyviz-sequential.png)

In the heatmap above, you can see a bright line. This means that the data reads or writes are sequential. Typical scenarios of sequential data reads or writes are importing data or scanning tables and indexes. For example, you continuously write data to tables with auto-increment IDs.

Regions in the bright areas are the hotspots of read and write traffic, which often become the performance bottleneck of the entire cluster. In this situation, you might need to readjust the primary key for the application. By doing this, you scatter Regions much as possible to spread the pressure across multiple Regions. You can also schedule application tasks during the low-peak period.

> **Note:**
>
> In this section, only the common types of heatmap are shown. Key Visualizer actually displays the heatmap of all schemas and tables in the entire cluster, so you might see different types of heatmap in different areas, or mixed results of multiple heatmap types. Use the heatmap based on the actual situation.
## Address hotspot issues

TiDB has some built-in features to mitigate the common hotspot issue. Refer to [Highly Concurrent Write Best Practices](https://docs.pingcap.com/tidb/stable/best-practices/high-concurrency-best-practices) for details.
