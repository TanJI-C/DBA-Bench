# Start manual profiling and review results

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-profiling.md`
- Source Title: `TiDB Dashboard Instance Profiling - Manual Profiling`
- Source Heading Path: `TiDB Dashboard Instance Profiling - Manual Profiling > Start Profiling | TiDB Dashboard Instance Profiling - Manual Profiling > View profiling status | TiDB Dashboard Instance Profiling - Manual Profiling > Download performance data | TiDB Dashboard Instance Profiling - Manual Profiling > View profiling history`
- Source Line Ranges: `44-78`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`, `tidb`, `tikv`, `tiflash`
- Topic Tags: `start profiling`, `duration`, `progress`, `background task`, `download results`, `raw data`, `history`, `continuous profiling`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0041_3e7636ce79`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-profiling.md#start-profiling`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `be74b338b0f8a47595af9d074ca19d8ec0e7e51037c07daa64822409fc8342c3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-profiling#start-profiling
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-profiling.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about starting Manual Profiling, changing profiling duration, checking progress, downloading results or raw data, or viewing on-demand profiling history in TiDB Dashboard.
- Retrieval Keywords: Start Profiling, choose at least one target instance, profiling duration, 30 seconds by default, View profiling status, profiling runs in the background, Refreshing or exiting the current page does not stop the profiling task, Download Profiling Result, download all performance data, download raw data, individual instance, View profiling history, on-demand profiling history, Continuous Profiling enabled
- Follow-up Guidance: The source also states that Manual Profiling cannot be initiated on clusters that have Continuous Profiling enabled, and that current-moment performance data can be viewed from the most recent profiling result in the Continuous Profiling page.
- Classification Note: This is classified as operation because the content explains how to initiate profiling tasks, monitor their execution, and access their results and history.

## Official Source Content

## Start Profiling

In the instance profiling page, choose at least one target instance and click **Start Profiling** to start the instance profiling.

![Start instance profiling](/media/dashboard/dashboard-profiling-start.png)

You can modify the profiling duration before starting the profiling. This duration is determined by the time needed for the profiling, which is 30 seconds by default. The 30-second duration takes 30 seconds to complete.

Manual Profiling cannot be initiated on clusters that have [Continuous Profiling](https://docs.pingcap.com/tidb/stable/dashboard/continuous-profiling) enabled. To view the performance data at the current moment, click on the most recent profiling result in the [Continuous Profiling page](https://docs.pingcap.com/tidb/stable/dashboard/continuous-profiling#access-the-page).
## View profiling status

After a profiling is started, you can view the profiling status and progress in real time.

![Profiling detail](/media/dashboard/dashboard-profiling-view-progress.png)

The profiling runs in the background. Refreshing or exiting the current page does not stop the profiling task that is running.
## Download performance data

After the profiling of all instances is completed, you can click **Download Profiling Result** in the upper right corner to download all performance data.

![Download profiling result](/media/dashboard/dashboard-profiling-download.png)

You can also click an individual instance in the table to view its profiling result. Alternatively, you can hover on ... to download raw data.

![Single instance result](/media/dashboard/dashboard-profiling-view-single.png)
## View profiling history

The on-demand profiling history is listed on the page. Click a row to view details.

![View profiling history](/media/dashboard/dashboard-profiling-history.png)

For detailed operations on the profiling status page, see [View Profiling Status](#view-profiling-status).
