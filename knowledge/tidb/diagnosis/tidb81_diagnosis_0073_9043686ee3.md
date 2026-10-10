# Operator CLI access and generated column replication limits

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-faq.md`
- Source Title: `TiCDC FAQs`
- Source Heading Path: `TiCDC FAQs > Why can't I use the `cdc cli` command to operate a TiCDC cluster deployed by TiDB Operator? | TiCDC FAQs > Does TiCDC replicate generated columns of DML operations?`
- Source Line Ranges: `421-458`
- Source Scope: `kubernetes`
- Primary Component: `ticdc`
- Related Components: `operator`, `sql`
- Topic Tags: `cdc-cli`, `server-port`, `operator-deployment`, `generated-columns`, `mysql-downstream`, `open-protocol`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0073_9043686ee3`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-faq.md#why-can-t-i-use-the-cdc-cli-command-to-operate-a-ticdc-cluster-deployed-by-tidb-operator`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c4e99a8ddfd44bb023b02f0f02b632fc0d0003f4b5c70c79cd4e27c4ee02f2be`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq#why-can-t-i-use-the-cdc-cli-command-to-operate-a-ticdc-cluster-deployed-by-tidb-operator
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-faq.md

## Retrieval Guidance

- Use When: Use this chunk when `cdc cli` cannot operate a TiCDC cluster deployed by TiDB Operator because of the server port, or when checking whether TiCDC replicates virtual or stored generated columns to MySQL, Kafka, or storage services.
- Retrieval Keywords: cdc cli, TiDB Operator, default port number 8301, default port number 8300, --server, ./cdc cli changefeed list --server "127.0.0.1:8301", generated columns, virtual generated columns, stored generated columns, MySQL-compatible database, Kafka, storage service, Error 3105 (HY000), The value specified for generated column, Open Protocol, bit flags of columns
- Follow-up Guidance: The content notes that when replicating stored generated columns to Kafka or a storage service and then writing them back to MySQL, `Error 3105 (HY000)` might occur, and that Open Protocol output includes bit flags of columns to distinguish generated columns.
- Classification Note: This is classified as diagnosis because the official content explains a CLI connectivity symptom caused by a port mismatch and replication limitations and errors related to generated columns.

## Official Source Content

## Why can't I use the `cdc cli` command to operate a TiCDC cluster deployed by TiDB Operator?

This is because the default port number of the TiCDC cluster deployed by TiDB Operator is `8301`, while the default port number of the `cdc cli` command to connect to the TiCDC server is `8300`. When using the `cdc cli` command to operate the TiCDC cluster deployed by TiDB Operator, you need to explicitly specify the `--server` parameter, as follows:

```shell
./cdc cli changefeed list --server "127.0.0.1:8301"
[
  {
    "id": "4k-table",
    "namespace": "default",
    "summary": {
      "state": "stopped",
      "tso": 441832628003799353,
      "checkpoint": "2023-05-30 22:41:57.910",
      "error": null
    }
  },
  {
    "id": "big-table",
    "namespace": "default",
    "summary": {
      "state": "normal",
      "tso": 441872834546892882,
      "checkpoint": "2023-06-01 17:18:13.700",
      "error": null
    }
  }
]
```
## Does TiCDC replicate generated columns of DML operations?

Generated columns include virtual generated columns and stored generated columns. TiCDC ignores virtual generated columns and only replicates stored generated columns to the downstream. However, stored generated columns are also ignored when the downstream is MySQL or another MySQL-compatible database (rather than Kafka or other storage services).

> **Note:**
>
> When replicating stored generated columns to Kafka or a storage service and then writing them back to MySQL, `Error 3105 (HY000): The value specified for generated column 'xx' in table 'xxx' is not allowed` might occur. To avoid this error, you can use [Open Protocol](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-protocol#ticdc-open-protocol) for replication. The output of this protocol includes [bit flags of columns](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-protocol#bit-flags-of-columns), which can distinguish whether a column is a generated column.
