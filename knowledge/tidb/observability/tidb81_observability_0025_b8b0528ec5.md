# Key Visualizer overview, access, interface, and basic concepts

## Knowledge Metadata

- Knowledge Type: `observability`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-key-visualizer.md`
- Source Title: `Key Visualizer Page`
- Source Heading Path: `Key Visualizer Page | Key Visualizer Page > Access Key Visualizer page | Key Visualizer Page > Interface demonstration | Key Visualizer Page > Basic concepts | Key Visualizer Page > Basic concepts > Region | Key Visualizer Page > Basic concepts > Hotspot | Key Visualizer Page > Basic concepts > Heatmap | Key Visualizer Page > Basic concepts > Region compression`
- Source Line Ranges: `5-60`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `key visualizer`, `heatmap`, `region`, `hotspot`, `bucket`, `traffic`, `ui navigation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_observability_0025_b8b0528ec5`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-key-visualizer.md#key-visualizer-page`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dfc99daa9d97d33991786c992fa8825d8a32363c02a17c2568dde9b6ec56acc1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-key-visualizer#key-visualizer-page
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-key-visualizer.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants an overview of the TiDB Dashboard Key Visualizer page, how to access it, and what concepts such as Region, hotspot, heatmap, and Bucket mean.
- Retrieval Keywords: Key Visualizer page, TiDB Dashboard, access Key Visualizer, http://127.0.0.1:2379/dashboard/#/keyviz, PD instance address and port, heatmap, Region, hotspot, Bucket, region compression, traffic hotspots, tables and indexes
- Follow-up Guidance: It also points to the Key Visualizer interface objects and explains that Regions are compressed into 1,500 consecutive ranges called Buckets on the heatmap.
- Classification Note: This is classified as observability because the content describes the dashboard page used to visually analyze cluster traffic and troubleshoot hotspots.

## Official Source Content

# Key Visualizer Page

The Key Visualizer page of TiDB Dashboard is used to analyze the usage of TiDB and troubleshoot traffic hotspots. This page visually shows the traffic of the TiDB cluster over a period of time.
## Access Key Visualizer page

You can use one of the following two methods to access the Key Visualizer page:

* After logging in to TiDB Dashboard, click **Key Visualizer** in the left navigation menu.

    ![Access Key Visualizer](/media/dashboard/dashboard-keyviz-access-v650.png)

* Visit <http://127.0.0.1:2379/dashboard/#/keyviz> in your browser. Replace `127.0.0.1:2379` with the actual PD instance address and port.
## Interface demonstration

The following image is a demonstration of the Key Visualizer page:

![Key Visualizer page](/media/dashboard/dashboard-keyviz-overview.png)

From the preceding interface, you can see the following objects:

+ A large heatmap that shows changes of the overall traffic over time.
+ The detailed information of a certain coordinate point.
+ Information of tables, and indexes (on the left side of the heatmap).
## Basic concepts

This section introduces the basic concepts that relate to Key Visualizer.
### Region

In a TiDB cluster, the stored data is distributed among TiKV instances. Logically, TiKV is a huge and orderly key-value map. The whole key-value space is divided into many segments and each segment consists of a series of adjacent keys. Such segment is called a `Region`.

For detailed introduction of Region, refer to [TiDB Internal (I) - Data Storage](https://www.pingcap.com/blog/tidb-internal-data-storage/).
### Hotspot

When you use the TiDB database, the hotspot issue is typical, where high traffic is concentrated on a small range of data. Because consecutive data ranges are often processed on the same TiKV instance, the TiKV instance on which the hotspot occurs becomes the performance bottleneck of the whole application. The hotspot issue often occurs in the following scenarios:

+ Write adjacent data into a table with the `AUTO_INCREMENT` primary key, which causes a hotspot issue on this table.
+ Write adjacent time data into the time index of a table, which causes a hotspot issue on the table index.

For more details about hotspot, refer to [Highly Concurrent Write Best Practices](https://docs.pingcap.com/tidb/stable/best-practices/high-concurrency-best-practices#hotspot-causes)
### Heatmap

The heatmap is the core part of Key Visualizer, which shows the change of a metric over time. The X-axis of the heatmap indicates the time. The Y-axis of the heatmap indicates the consecutive Regions based on key ranges that cover all schemas and tables of the TiDB cluster.

Colder colors in the heatmap indicate lower read and write traffic of Regions in that period of time. Hotter (brighter) colors indicate higher traffic.
### Region compression

A TiDB cluster might have up to hundreds of thousands of Regions. It is difficult to display so many Regions on screen. Therefore, on each heatmap, these Regions are compressed into 1,500 consecutive ranges, each range called a Bucket. In the heatmap, because hotter instances need more attention, Key Visualizer tends to compress a large number of Regions with lower traffic into one Bucket, and displays the Region with higher traffic also in one Bucket.
