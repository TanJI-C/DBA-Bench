# Create and configure Pulsar changefeed

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/changefeed-sink-to-apache-pulsar.md`
- Source Title: `Sink to Apache Pulsar`
- Source Heading Path: `Sink to Apache Pulsar > Step 1. Open the Changefeed page for Apache Pulsar | Sink to Apache Pulsar > Step 2. Configure the changefeed destination`
- Source Line Ranges: `82-107`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ticdc`
- Topic Tags: `console`, `changefeed creation`, `destination`, `authentication`, `batching`, `timeouts`, `connection test`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0286_10c3880e68`
- Source ID: `tidb-docs-8.1:tidb-cloud/changefeed-sink-to-apache-pulsar.md#step-1-open-the-changefeed-page-for-apache-pulsar`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `65d1cf79c3e9aa207a0c6e054e10df7976af1924ae89d3b0f93036605b302c92`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/changefeed-sink-to-apache-pulsar#step-1-open-the-changefeed-page-for-apache-pulsar
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/changefeed-sink-to-apache-pulsar.md

## Retrieval Guidance

- Use When: Use this chunk when configuring a new Apache Pulsar changefeed in the TiDB Cloud console and entering destination, authentication, and advanced connection settings.
- Retrieval Keywords: Create Changefeed, TiDB Cloud console, Data > Changefeed, Destination Pulsar, Destination Protocol Pulsar, Pulsar+SSL, Connectivity Method VPC Peering, Connectivity Method Public, Pulsar Broker example.org:6650, Authentication Auth Type, Advanced Settings, Compression, Max Messages per Batch, Max Publish Delay, Connection Timeout, Operation Timeout, Send Timeout, test the network connection
- Follow-up Guidance: After clicking Next, TiDB Cloud tests the network connection and directs you to the next step if the test succeeds.
- Classification Note: This is operation content because it gives the console workflow and field-level settings to create and test a Pulsar changefeed destination in TiDB Cloud.

## Official Source Content

## Step 1. Open the Changefeed page for Apache Pulsar

1. Log in to the [TiDB Cloud console](https://tidbcloud.com).
2. Navigate to the cluster overview page of the TiDB cluster that will be the source of the changefeed events, and then click **Data** > **Changefeed** in the left navigation pane.
3. Click **Create Changefeed**.
## Step 2. Configure the changefeed destination

1. In the **Destination** section, select **Pulsar**.
2. In the **Connection** section, enter the following information:

    - **Destination Protocol**: select **Pulsar** or **Pulsar+SSL**.
    - **Connectivity Method**: select **VPC Peering** or **Public**, depending on how you plan to connect to your Pulsar endpoint.
    - **Pulsar Broker**: enter the endpoint of your Pulsar broker. Use a colon to separate the port from the domain or IP address, such as `example.org:6650`.

3. In the **Authentication** section, select the **Auth Type** option according to your Pulsar authentication configuration. Enter the requested credential information based on your selection.
4. Optional: In the **Advanced Settings** section, configure additional settings:

    - **Compression**: select an optional compression algorithm for the data in this changefeed.
    - **Max Messages per Batch** and **Max Publish Delay**: specify the batching of event messages sent to Pulsar. **Max Messages per Batch** sets the maximum number of messages per batch, while **Max Publish Delay** sets the maximum wait time before sending a batch.
    - **Connection Timeout**: adjust the timeout for establishing a TCP connection to Pulsar.
    - **Operation Timeout**: adjust the timeout for initiating operations using the TiCDC Pulsar client.
    - **Send Timeout**: adjust the timeout for the TiCDC Pulsar producer to send a message.

5. Click **Next** to test the network connection. If the test succeeds, you will be directed to the next step.
