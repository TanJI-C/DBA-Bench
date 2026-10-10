# Convert partitioned and non-partitioned tables

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/partitioned-table.md`
- Source Title: `Partitioning`
- Source Heading Path: `Partitioning > Partition management > Convert a partitioned table to a non-partitioned table | Partitioning > Partition management > Partition an existing table`
- Source Line Ranges: `1164-1203`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `partition-management`, `remove-partitioning`, `alter-table`, `partition-by`, `table-conversion`, `online-index-rebuild`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0178_86081f494a`
- Source ID: `tidb-docs-8.1:partitioned-table.md#convert-a-partitioned-table-to-a-non-partitioned-table`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `042ba7d2dfb782e3398e98fea899d9d8ccacbf92a296e0d44f39729a9c300752`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/partitioned-table#convert-a-partitioned-table-to-a-non-partitioned-table
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/partitioned-table.md

## Retrieval Guidance

- Use When: Use this chunk when looking for ALTER TABLE syntax to remove partitioning from a table or to partition an existing table or change its partition type.
- Retrieval Keywords: REMOVE PARTITIONING, ALTER TABLE <table_name> REMOVE PARTITIONING, ALTER TABLE members REMOVE PARTITIONING, PARTITION BY <new partition type and definitions>, ALTER TABLE <table_name> PARTITION BY, partition an existing table, convert a partitioned table to a non-partitioned table, modify the partition type of an existing partitioned table, ALTER TABLE members PARTITION BY HASH(id) PARTITIONS 10, ALTER TABLE member_level PARTITION BY RANGE(level)
- Follow-up Guidance: The source states that these conversion statements copy all rows and recreate the indexes online according to the new table or partition definitions.
- Classification Note: This is classified as an operation chunk because it describes table conversion operations using ALTER TABLE statements.

## Official Source Content

### Convert a partitioned table to a non-partitioned table

To convert a partitioned table to a non-partitioned table, you can use the following statement, which removes the partitioning, copies all rows of the table, and recreates the indexes online for the table:

```sql
ALTER TABLE <table_name> REMOVE PARTITIONING
```

For example, to convert the `members` partitioned table to the non-partitioned table, you can execute the following statement:

```sql
ALTER TABLE members REMOVE PARTITIONING
```
### Partition an existing table

To partition an existing non-partitioned table or modify the partition type of an existing partitioned table, you can use the following statement, which copies all rows and recreates the indexes online according to the new partition definitions:

```sql
ALTER TABLE <table_name> PARTITION BY <new partition type and definitions>
```

Examples:

To convert the existing `members` table to a HASH partitioned table with 10 partitions, you can execute the following statement:

```sql
ALTER TABLE members PARTITION BY HASH(id) PARTITIONS 10;
```

To convert the existing `member_level` table to a RANGE partitioned table, you can execute the following statement:

```sql
ALTER TABLE member_level PARTITION BY RANGE(level)
(PARTITION pLow VALUES LESS THAN (1),
 PARTITION pMid VALUES LESS THAN (3),
 PARTITION pHigh VALUES LESS THAN (7)
 PARTITION pMax VALUES LESS THAN (MAXVALUE));
```
