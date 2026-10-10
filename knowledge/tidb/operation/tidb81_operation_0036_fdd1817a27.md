# Using Key Visualizer settings, zoom, metrics, refresh, and bucket details

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dashboard/dashboard-key-visualizer.md`
- Source Title: `Key Visualizer Page`
- Source Heading Path: `Key Visualizer Page > Use Key Visualizer | Key Visualizer Page > Use Key Visualizer > Settings | Key Visualizer Page > Use Key Visualizer > Observe a certain period of time or Region range | Key Visualizer Page > Use Key Visualizer > Adjust brightness | Key Visualizer Page > Use Key Visualizer > Select metrics | Key Visualizer Page > Use Key Visualizer > Refresh and automatic refresh | Key Visualizer Page > Use Key Visualizer > See Bucket details`
- Source Line Ranges: `61-141`
- Source Scope: `self_managed`
- Primary Component: `dashboard`
- Related Components: `pd`
- Topic Tags: `feature enablement`, `data collection`, `zoom`, `time range`, `region range`, `brightness`, `metrics`, `refresh`, `bucket details`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0036_fdd1817a27`
- Source ID: `tidb-docs-8.1:dashboard/dashboard-key-visualizer.md#use-key-visualizer`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `34dc44a70dd553d2d24d67cfcd770123b0d927130cd641f45ff7ade9cdbabe97`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dashboard/dashboard-key-visualizer#use-key-visualizer
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dashboard/dashboard-key-visualizer.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how to enable or operate Key Visualizer, including settings, zooming, brightness, metric selection, refresh behavior, and Bucket detail viewing.
- Retrieval Keywords: enable Key Visualizer, Settings page, Open Settings, start data collection, Save, Select & Zoom, Reset, time selection box, 6 hour, Brightness, metrics selection box, Write (bytes), Read (bytes), Read (keys), Write (keys), All, Refresh, automatic refresh, Bucket details, copy to the clipboard
- Follow-up Guidance: It notes that adjusting the time range or Region range disables automatic refresh, and that redrawn heatmaps can differ because Region compression granularity or the basis of hotness changes.
- Classification Note: This is classified as operation because the content gives the page usage steps and controls for enabling data collection and interacting with the heatmap.

## Official Source Content

## Use Key Visualizer

This section introduces how to use Key Visualizer.
### Settings

To use the Key Visualizer page for the first time, you need to manually enable this feature on the **Settings** page. Follow the page guide and click **Open Settings** to open the settings page:

![Feature disabled](/media/dashboard/dashboard-keyviz-not-enabled.png)

After this feature is enabled, you can open the settings page by clicking the **Settings** icon in the upper right corner:

![Settings icon](/media/dashboard/dashboard-keyviz-settings-button.png)

The settings page is shown as follows:

![Settings page](/media/dashboard/dashboard-keyviz-settings.png)

Set whether to start data collection through the switch, and click **Save** to take effect. After enabling the feature, you can see that the toolbar is available:

![Toolbar](/media/dashboard/dashboard-keyviz-toolbar.png)

After this feature is enabled, data collection is going on at the backend. You can see the heatmap shortly.
### Observe a certain period of time or Region range

When you open Key Visualizer, the heatmap of the entire database over the recent six hours is displayed by default. In this heatmap, the closer to the right side (current time), the shorter the time interval corresponding to each column of Buckets. If you want to observe a specific time period or a specific Region range, you can zoom in to get more details. The specific instructions are as follows:

1. Scroll up or down in the heatmap.
2. Click and drag one of the following buttons to select the range.
    + Click the **Select & Zoom** button. Then click and drag this button to select the area to zoom in.

    ![Selection box](/media/dashboard/dashboard-keyviz-select-zoom.gif)

    + Click the **Reset** button to reset the Region range to the entire database.
    + Click the **time selection box** (at the position of `6 hour` on the preceding interface) and select the observation time period again.

    ![Select time](/media/dashboard/dashboard-keyviz-select-time.png)

> **Note:**
>
> If you follow step 2 in the instruction above, the heatmap is redrawn, which might be very different from the original heatmap. This difference is normal because if you observe in more detail, the granularity of the Region compression has changed, or the basis of `hot` in a specific range has changed.
### Adjust brightness

The heatmap uses colors of different brightnesses to indicate the Bucket traffic. Colder colors in the heatmap indicate lower read and write traffic of the Region in that period of time. Hotter (brighter) colors indicate higher traffic. If the color is too cold or too hot, it is difficult to observe in details. In this situation, you can click the **Brightness** button and then use the slider to adjust the brightness of the page.

> **Note:**
>
> When Key Visualizer displays the heatmap of an area, it defines the basis of being cold and hot according to the traffic of this area. When the traffic in the entire area is relatively even, even if the overall traffic is low in value, you might still see a large bright-colored area. Remember to include the value into your analysis.
### Select metrics

![Select metrics](/media/dashboard/dashboard-keyviz-select-type.png)

You can view a metric you are interested in by selecting this metric in the **metrics selection box** (at the `Write (bytes)` position in the interface above):

* `Read (bytes)`: Read traffic.
* `Write (bytes)`: Write traffic.
* `Read (keys)`: The number of read rows.
* `Write (keys)`: The number of written rows.
* `All`: The sum of read and write traffic.
### Refresh and automatic refresh

To regain a heatmap based on the current time, click the **Refresh** button. If you need to observe the traffic distribution of the database in real time, click the down arrow on the right side of the **Refresh** button and select a fixed time interval for the heatmap to automatically refresh at this interval.

> **Note:**
>
> If you adjust the time range or Region range, the automatic refresh is disabled.
### See Bucket details

You can hover your mouse over the Bucket you are interested in to view the detailed information of this Region range. The image below is an example of this information:

![Bucket details](/media/dashboard/dashboard-keyviz-tooltip.png)

If you want to copy this information, click a Bucket. Then, the page with relevant details is temporarily pinned. Click on the information, and you have copied it to the clipboard.

![Copy Bucket details](/media/dashboard/dashboard-keyviz-tooltip-copy.png)
