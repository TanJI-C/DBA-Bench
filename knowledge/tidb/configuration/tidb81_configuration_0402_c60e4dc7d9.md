# Transaction size limits and downstream binlog considerations

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/transaction-overview.md`
- Source Title: `Transactions`
- Source Heading Path: `Transactions > Transaction size limit`
- Source Line Ranges: `289-304`
- Source Scope: `shared`
- Primary Component: `tidb`
- Related Components: `ecosystem`
- Topic Tags: `transaction-size-limit`, `row-size`, `memory-usage`, `configuration-file`, `binlog`, `kafka`, `downstream-limits`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0402_c60e4dc7d9`
- Source ID: `tidb-docs-8.1:transaction-overview.md#transaction-size-limit`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f43ff0d5620f7d665431ed2b845c0a3400a2d76b4959ed71d9f52dadcd54c244`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/transaction-overview#transaction-size-limit
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/transaction-overview.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB transaction size limits, single row size constraints, or how `txn-total-size-limit` interacts with TiDB Binlog and downstream Kafka message limits.
- Retrieval Keywords: transaction size limit, single row no more than 6 MB, txn-total-size-limit, 100 MB default transaction size, maximum value 1 TB, private memory cache, memory usage two to three times, 300,000 key-value pairs restriction removed in TiDB v4.0, TiDB Binlog, Kafka single message processing capability 1 GB, downstream Kafka reports an error
- Follow-up Guidance: The content notes that when `txn-total-size-limit` is set to more than 1 GB, a transaction can succeed in TiDB while downstream Kafka reports an error, so the actual value depends on the limit of the end consumer.
- Classification Note: This is classified as configuration because it centers on the configurable `txn-total-size-limit` and its operational limits for TiDB transactions and downstream consumers.

## Official Source Content

## Transaction size limit

Due to the limitations of the underlying storage engine, TiDB requires a single row to be no more than 6 MB. All columns of a row are converted to bytes according to their data types and summed up to estimate the size of a single row.

TiDB supports both optimistic and pessimistic transactions, and optimistic transactions are the basis for pessimistic transactions. Because optimistic transactions first cache the changes in private memory, TiDB limits the size of a single transaction.

By default, TiDB sets the total size of a single transaction to no more than 100 MB. You can modify this default value via `txn-total-size-limit` in the configuration file. The maximum value of `txn-total-size-limit` is 1 TB. The individual transaction size limit also depends on the size of remaining memory available in the server. This is because when a transaction is executed, the memory usage of the TiDB process is scaled up comparing with the transaction size, up to two to three times or more of the transaction size.

TiDB previously limited the total number of key-value pairs for a single transaction to 300,000. This restriction was removed in TiDB v4.0.

> **Note:**
>
> Usually, TiDB Binlog is enabled to replicate data to the downstream. In some scenarios, message middleware such as Kafka is used to consume binlogs that are replicated to the downstream.
>
> Taking Kafka as an example, the upper limit of Kafka's single message processing capability is 1 GB. Therefore, when `txn-total-size-limit` is set to more than 1 GB, it might happen that the transaction is successfully executed in TiDB, but the downstream Kafka reports an error. To avoid this situation, you need to decide the actual value of `txn-total-size-limit` according to the limit of the end consumer. For example, if Kafka is used downstream, `txn-total-size-limit` must not exceed 1 GB.
