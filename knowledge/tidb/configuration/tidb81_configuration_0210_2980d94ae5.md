# Configure replication filters, data format, flush parameters, and specification

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-cloud-storage.md`
- Source Title: `Sink to Cloud Storage`
- Source Heading Path: `Sink to Cloud Storage > Step 2. Configure replication | Sink to Cloud Storage > Step 3. Configure specification`
- Source Line Ranges: `95-164`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`
- Topic Tags: `changefeed`, `replication`, `table-filter`, `event-filter`, `tso`, `csv`, `canal-json`, `flush-interval`, `file-size`, `rcu`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0210_2980d94ae5`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-cloud-storage.md#step-2-configure-replication`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0e9fbd31ad46d06ec52d664a2502fbe8240010baa6d19c9cb223392d0e5fbfdc`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-cloud-storage#step-2-configure-replication
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-cloud-storage.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs to configure changefeed replication filters, start replication position, output format, flush parameters, or changefeed specification for a cloud storage sink.
- Retrieval Keywords: Configure replication, Table Filter, table filter rules, Filter Rules, *.*, Tables with valid keys, Tables without valid keys, !test.tbl1, Event Filter, Tables matching, Ignore event, Ignore SQL, Ignore insert value expression, Ignore update new value expression, Ignore update old value expression, Ignore delete value expression, Start Replication Position, Start replication from now on, Start replication from a specific TSO, Start replication from a specific time, Data Format, CSV, Canal-JSON, Binary Encode Method, base64, hex, AWS DMS, Date Separator, Delimiter, Quote, Null/Empty Values, Include Commit Ts, commit-ts, Enable TiDB Extension, WATERMARK events, TiDB extension field, Flush Parameters, Flush Interval, 60 seconds, 2 seconds to 10 minutes, File Size, 64 MB, 1 MB to 512 MB, Recovery Point Objective, RPO, Changefeed Specification, Replication Capacity Units, RCUs, Changefeed Name
- Follow-up Guidance: The next step is to configure the changefeed specification by setting the number of Replication Capacity Units (RCUs) and the changefeed name.
- Classification Note: Classified as configuration because the content enumerates the configurable replication rules, replication start options, CSV and Canal-JSON fields, flush settings, and specification fields for a changefeed.

## Official Source Content

## Step 2. Configure replication

1. Customize **Table Filter** to filter the tables that you want to replicate. For the rule syntax, refer to [table filter rules](https://docs.pingcap.com/tidb/stable/ticdc-filter#changefeed-log-filters).

    ![the table filter of changefeed](/media/tidb-cloud/changefeed/sink-to-s3-02-table-filter.jpg)

    - **Filter Rules**: you can set filter rules in this column. By default, there is a rule `*.*`, which stands for replicating all tables. When you add a new rule, TiDB Cloud queries all the tables in TiDB and displays only the tables that match the rules in the box on the right. You can add up to 100 filter rules.
    - **Tables with valid keys**: this column displays the tables that have valid keys, including primary keys or unique indexes.
    - **Tables without valid keys**: this column shows tables that lack primary keys or unique keys. These tables present a challenge during replication because the absence of a unique identifier can result in inconsistent data when handling duplicate events downstream. To ensure data consistency, it is recommended to add unique keys or primary keys to these tables before initiating the replication. Alternatively, you can employ filter rules to exclude these tables. For example, you can exclude the table `test.tbl1` by using the rule `"!test.tbl1"`.

2. Customize **Event Filter** to filter the events that you want to replicate.

    - **Tables matching**: you can set which tables the event filter will be applied to in this column. The rule syntax is the same as that used for the preceding **Table Filter** area. You can add up to 10 event filter rules per changefeed.
    - **Event Filter**: you can use the following event filters to exclude specific events from the changefeed:
        - **Ignore event**: excludes specified event types.
        - **Ignore SQL**: excludes DDL events that match specified expressions. For example, `^drop` excludes statements starting with `DROP`, and `add column` excludes statements containing `ADD COLUMN`.
        - **Ignore insert value expression**: excludes `INSERT` statements that meet specific conditions. For example, `id >= 100` excludes `INSERT` statements where `id` is greater than or equal to 100.
        - **Ignore update new value expression**: excludes `UPDATE` statements where the new value matches a specified condition. For example, `gender = 'male'` excludes updates that result in `gender` being `male`.
        - **Ignore update old value expression**: excludes `UPDATE` statements where the old value matches a specified condition. For example, `age < 18` excludes updates where the old value of `age` is less than 18.
        - **Ignore delete value expression**: excludes `DELETE` statements that meet a specified condition. For example, `name = 'john'` excludes `DELETE` statements where `name` is `'john'`.

3. In the **Start Replication Position** area, select one of the following replication positions:

    - Start replication from now on
    - Start replication from a specific [TSO](https://docs.pingcap.com/tidb/stable/glossary#tso)
    - Start replication from a specific time

4. In the **Data Format** area, select either the **CSV** or **Canal-JSON** format.

    <div label="Configure CSV format">

    To configure the **CSV** format, fill in the following fields:

    - **Binary Encode Method**: The encoding method for binary data. You can choose **base64** (default) or **hex**. If you want to integrate with AWS DMS, use **hex**.
    - **Date Separator**: To rotate data based on the year, month, and day, or choose not to rotate at all.
    - **Delimiter**: Specify the character used to separate values in the CSV file. The comma (`,`) is the most commonly used delimiter.
    - **Quote**: Specify the character used to enclose values that contain the delimiter character or special characters. Typically, double quotes (`"`) are used as the quote character.
    - **Null/Empty Values**: Specify how null or empty values are represented in the CSV file. This is important for proper handling and interpretation of the data.
    - **Include Commit Ts**: Control whether to include [`commit-ts`](https://docs.pingcap.com/tidb/stable/ticdc-sink-to-cloud-storage#replicate-change-data-to-storage-services) in the CSV row.

    </div>
    <div label="Configure Canal-JSON format">

    Canal-JSON is a plain JSON text format. To configure it, fill in the following fields:

    - **Date Separator**: To rotate data based on the year, month, and day, or choose not to rotate at all.
    - **Enable TiDB Extension**: When you enable this option, TiCDC sends [WATERMARK events](https://docs.pingcap.com/tidb/stable/ticdc-canal-json#watermark-event) and adds the [TiDB extension field](https://docs.pingcap.com/tidb/stable/ticdc-canal-json#tidb-extension-field) to Canal-JSON messages.

    </div>

5. In the **Flush Parameters** area, you can configure two items:

    - **Flush Interval**: set to 60 seconds by default, adjustable within a range of 2 seconds to 10 minutes;
    - **File Size**: set to 64 MB by default, adjustable within a range of 1 MB to 512 MB.

    ![Flush Parameters](/media/tidb-cloud/changefeed/sink-to-cloud-storage-flush-parameters.jpg)

    > **Note:**
    >
    > These two parameters will affect the quantity of objects generated in cloud storage for each individual database table. If there are a large number of tables, using the same configuration will increase the number of objects generated and subsequently raise the cost of invoking the cloud storage API. Therefore, it is recommended to configure these parameters appropriately based on your Recovery Point Objective (RPO) and cost requirements.
## Step 3. Configure specification

Click **Next** to configure your changefeed specification.

1. In the **Changefeed Specification** area, specify the number of Replication Capacity Units (RCUs) to be used by the changefeed.
2. In the **Changefeed Name** area, specify a name for the changefeed.
