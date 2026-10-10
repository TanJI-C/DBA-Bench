# UUID primary key storage and hotspot avoidance practices

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/uuid.md`
- Source Title: `UUID Best Practices`
- Source Heading Path: `UUID Best Practices | UUID Best Practices > Overview of UUIDs | UUID Best Practices > Best practices | UUID Best Practices > Best practices > Store as binary | UUID Best Practices > Best practices > UUID format binary order and a clustered PK | UUID Best Practices > MySQL compatibility`
- Source Line Ranges: `5-74`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `dashboard`, `sql`
- Topic Tags: `uuid`, `primary-key`, `binary-storage`, `uuid_to_bin`, `bin_to_uuid`, `clustered-index`, `hotspots`, `key-visualizer`, `mysql-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0068_e911fe2112`
- Source ID: `tidb-docs-8.1:best-practices/uuid.md#uuid-best-practices`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e0ad8e37336f74bb7950334c2db53f0b9807d9cfdf65add0e5a2b92fff3ce7f7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/uuid#uuid-best-practices
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/uuid.md

## Retrieval Guidance

- Use When: Use this chunk when answering questions about storing UUID primary keys in TiDB, converting UUID text to binary with UUID_TO_BIN()/BIN_TO_UUID(), and avoiding hotspots with clustered UUID primary keys.
- Retrieval Keywords: UUID Best Practices, UUID primary key, AUTO_INCREMENT, UUID_TO_BIN(), BIN_TO_UUID(), BINARY(16), varbinary(16), swap_flag, CLUSTERED, PRIMARY KEY (`uuid`) CLUSTERED, hotspots, Key Visualizer, uuid_demo_1, uuid_demo_2, MySQL compatibility, UUID()
- Follow-up Guidance: The source also notes that BIN_TO_UUID() and UUID_TO_BIN() were introduced in MySQL 8.0, and that UUID() is available in earlier MySQL versions.
- Classification Note: This chunk is classified as performance for TiDB because it describes binary UUID storage, clustered primary keys, and avoiding hotspot writes caused by UUID binary order choices visible in Key Visualizer.

## Official Source Content

# UUID Best Practices
## Overview of UUIDs

When used as a primary key, instead of an [`AUTO_INCREMENT`](https://docs.pingcap.com/tidb/stable/auto-increment) integer value, a universally unique identifier (UUID) delivers the following benefits:

- UUIDs can be generated on multiple systems without risking conflicts. In some cases, this means that the number of network trips to TiDB can be reduced, leading to improved performance.
- UUIDs are supported by most programming languages and database systems.
- When used as a part of a URL, a UUID is not vulnerable to enumeration attacks. In comparison, with an `AUTO_INCREMENT` number, it is possible to guess the invoice IDs or user IDs.
## Best practices
### Store as binary

The textual UUID format looks like this: `ab06f63e-8fe7-11ec-a514-5405db7aad56`, which is a string of 36 characters. By using [`UUID_TO_BIN()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/miscellaneous-functions#uuid_to_bin), the textual format can be converted into a binary format of 16 bytes. This allows you to store the text in a [`BINARY(16)`](https://docs.pingcap.com/tidb/stable/data-type-string#binary-type) column. When retrieving the UUID, you can use the [`BIN_TO_UUID()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/miscellaneous-functions#bin_to_uuid) function to get back to the textual format.
### UUID format binary order and a clustered PK

The `UUID_TO_BIN()` function can be used with one argument, the UUID or with two arguments where the second argument is a `swap_flag`.

It is recommended to not set the `swap_flag` with TiDB to avoid [hotspots](https://docs.pingcap.com/tidb/stable/best-practices/high-concurrency-best-practices).

It is recommended to not set the `swap_flag` with TiDB to avoid hotspots.

You can also explicitly set the [`CLUSTERED` option](https://docs.pingcap.com/tidb/stable/clustered-indexes) for UUID based primary keys to avoid hotspots.

To demonstrate the effect of the `swap_flag`, here are two tables with an identical structure. The difference is that the data inserted into `uuid_demo_1` uses `UUID_TO_BIN(?, 0)` and `uuid_demo_2` uses `UUID_TO_BIN(?, 1)`.

In the screenshot of the [Key Visualizer](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-key-visualizer) below, you can see that writes are concentrated in a single region of the `uuid_demo_2` table that has the order of the fields swapped in the binary format.

In the screenshot of the [Key Visualizer](https://docs.pingcap.com/tidb/stable/tidb-cloud/tune-performance#key-visualizer) below, you can see that writes are concentrated in a single region of the `uuid_demo_2` table that has the order of the fields swapped in the binary format.

![Key Visualizer](/media/best-practices/uuid_keyviz.png)

```sql
CREATE TABLE `uuid_demo_1` (
  `uuid` varbinary(16) NOT NULL,
  `c1` varchar(255) NOT NULL,
  PRIMARY KEY (`uuid`) CLUSTERED
)
```

```sql
CREATE TABLE `uuid_demo_2` (
  `uuid` varbinary(16) NOT NULL,
  `c1` varchar(255) NOT NULL,
  PRIMARY KEY (`uuid`) CLUSTERED
)
```
## MySQL compatibility

UUIDs can be used in MySQL as well. The `BIN_TO_UUID()` and `UUID_TO_BIN()` functions were introduced in MySQL 8.0. The `UUID()` function is available in earlier MySQL versions as well.
