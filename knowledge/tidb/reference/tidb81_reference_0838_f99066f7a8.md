# Row ID generation attributes and hotspot mitigation

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/sql-concepts.md`
- Source Title: `SQL`
- Source Heading Path: `SQL > Row ID generation attributes | SQL > Row ID generation attributes > AUTO_INCREMENT | SQL > Row ID generation attributes > AUTO_RANDOM | SQL > Row ID generation attributes > SHARD_ROW_ID_BITS`
- Source Line Ranges: `36-69`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `row-id`, `auto-increment`, `auto-random`, `shard-row-id-bits`, `hotspot-mitigation`, `insert`, `primary-key`, `region-distribution`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0838_f99066f7a8`
- Source ID: `tidb-docs-8.1:tidb-cloud/sql-concepts.md#row-id-generation-attributes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ac9425a8c46902a86bddb879a58986efb30d1251fbbb975be9e6482c1dcb72f1`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/sql-concepts#row-id-generation-attributes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/sql-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks how TiDB Cloud generates row IDs, how AUTO_INCREMENT, AUTO_RANDOM, and SHARD_ROW_ID_BITS differ, or how these attributes relate to hotspot mitigation.
- Retrieval Keywords: Row ID generation attributes, AUTO_INCREMENT, AUTO_RANDOM, SHARD_ROW_ID_BITS, implicit auto-increment row ID, write hotspot, single Region, multiple different Regions, BIGINT, primary key, non-clustered primary key, INSERT, ALTER TABLE t MODIFY COLUMN id BIGINT AUTO_RANDOM(5);, MySQL compatibility mode
- Follow-up Guidance: The source notes that AUTO_INCREMENT values are unique but only monotonic per TiDB server by default, and it links to AUTO_INCREMENT, AUTO_RANDOM, and SHARD_ROW_ID_BITS for more details.
- Classification Note: This is reference content because it explains the purpose and behavior of row ID generation attributes and their relation to data distribution.

## Official Source Content

## Row ID generation attributes

TiDB provides three SQL attributes to optimize row ID generation and data distribution.

- AUTO_INCREMENT

- AUTO_RANDOM

- SHARD_ROW_ID_BITS
### AUTO_INCREMENT

`AUTO_INCREMENT` is a column attribute that is used to automatically fill in default column values. When the `INSERT` statement does not specify values for the `AUTO_INCREMENT` column, the system automatically assigns values to this column.

For performance reasons, `AUTO_INCREMENT` numbers are allocated in a batch of values (30 thousand by default) to each TiDB server. This means that while `AUTO_INCREMENT` numbers are guaranteed to be unique, values assigned to an `INSERT` statement will only be monotonic on a per TiDB server basis.

If you want the `AUTO_INCREMENT` numbers to be monotonic on all TiDB servers and your TiDB version is v6.5.0 or later, it is recommended to enable the [MySQL compatibility mode](https://docs.pingcap.com/tidb/stable/auto-increment#mysql-compatibility-mode).

For more information, see [AUTO_INCREMENT](https://docs.pingcap.com/tidb/stable/auto-increment).
### AUTO_RANDOM

`AUTO_RANDOM` is a column attribute that is used to automatically assign values to a `BIGINT` column. Values assigned automatically are random and unique. Since the value of `AUTO_RANDOM` is random and unique, `AUTO_RANDOM` is often used in place of [`AUTO_INCREMENT`](https://docs.pingcap.com/tidb/stable/auto-increment) to avoid write hotspots in a single storage node caused by TiDB assigning consecutive IDs.

Since the value of `AUTO_RANDOM` is random and unique, `AUTO_RANDOM` is often used in place of [`AUTO_INCREMENT`](https://docs.pingcap.com/tidb/stable/auto-increment) to avoid write hotspots in a single storage node caused by TiDB assigning consecutive IDs. If the current `AUTO_INCREMENT` column is a primary key and the type is `BIGINT`, you can execute the `ALTER TABLE t MODIFY COLUMN id BIGINT AUTO_RANDOM(5);` statement to switch from `AUTO_INCREMENT` to `AUTO_RANDOM`.

For more information, see [AUTO_RANDOM](https://docs.pingcap.com/tidb/stable/auto-random).
### SHARD_ROW_ID_BITS

For the tables with a non-clustered primary key or no primary key, TiDB uses an implicit auto-increment row ID. When a large number of `INSERT` operations are performed, the data is written into a single Region, causing a write hot spot.

To mitigate the hot spot issue, you can configure [`SHARD_ROW_ID_BITS`](https://docs.pingcap.com/tidb/stable/shard-row-id-bits). The row IDs are scattered, and the data are written into multiple different Regions.
