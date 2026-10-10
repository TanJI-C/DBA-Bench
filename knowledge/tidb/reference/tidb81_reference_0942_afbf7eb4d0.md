# TiDB Lightning target database privileges and storage requirements

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-requirements.md`
- Source Title: `TiDB Lightning Requirements for the Target Database`
- Source Heading Path: `TiDB Lightning Requirements for the Target Database | TiDB Lightning Requirements for the Target Database > Privileges of the target database | TiDB Lightning Requirements for the Target Database > Storage space of the target database`
- Source Line Ranges: `5-116`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `tikv`, `shared`
- Topic Tags: `prerequisites`, `privileges`, `import-mode`, `sem`, `checkpoint`, `parallel-import`, `disk-space`, `capacity-planning`, `replicas`, `data-size`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0942_afbf7eb4d0`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-requirements.md#tidb-lightning-requirements-for-the-target-database`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3636ec0258a429ff7db8ae922e7b90e977d1e794df68b5965f989b287e9675d2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-requirements#tidb-lightning-requirements-for-the-target-database
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-requirements.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB Lightning target database prerequisites for required privileges by import mode or feature and for TiKV storage capacity sizing before import.
- Retrieval Keywords: TiDB Lightning Requirements for the Target Database, Privileges of the target database, Storage space of the target database, Logical Import Mode, Physical Import Mode, information_schema.columns, mysql.tidb, SUPER, RESTRICTED_VARIABLES_ADMIN, RESTRICTED_TABLES_ADMIN, SEM, lightning.task-info-schema-name, lightning.meta-schema-name, checkpoint.driver = "mysql", checkpoint.schema, tidb-lightning-ctl, checkpoint-destroy-all, CREATE SELECT INSERT UPDATE DELETE DROP ALTER, data source x the number of replicas x 2, information_schema.tables, DATA_LENGTH, INDEX_LENGTH, FORMAT_BYTES
- Follow-up Guidance: The source includes SQL statements on information_schema.tables to estimate schema and table data size using DATA_LENGTH and INDEX_LENGTH.
- Classification Note: This is reference content because it lists exact TiDB Lightning target database privileges for basic functions, import modes, checkpoint and parallel import features, and gives the storage space formula for the target TiKV cluster.

## Official Source Content

# TiDB Lightning Requirements for the Target Database

Before using TiDB Lightning, you need to check whether the environment meets the requirements. This helps reduce errors during import and ensures import success.
## Privileges of the target database

Based on the import mode and features enabled, the target database users should be granted with different privileges. The following table provides a reference.

<table>
   <tr>
      <td></td>
      <td>Feature</td>
      <td>Scope</td>
      <td>Required privilege</td>
      <td>Remarks</td>
   </tr>
   <tr>
      <td rowspan="2">Mandatory</td>
      <td rowspan="2">Basic functions</td>
      <td>Target table</td>
      <td>CREATE, SELECT, INSERT, UPDATE, DELETE, DROP, ALTER</td>
      <td>DROP is required only when tidb-lightning-ctl runs the checkpoint-destroy-all command</td>
   </tr>
   <tr>
      <td>Target database</td>
      <td>CREATE</td>
      <td></td>
   </tr>
   <tr>
      <td rowspan="4">Mandatory</td>
      <td>Logical Import Mode</td>
      <td>information_schema.columns</td>
      <td>SELECT</td>
      <td></td>
   </tr>
   <tr>
      <td rowspan="3">Physical Import Mode</td>
      <td>mysql.tidb</td>
      <td>SELECT</td>
      <td></td>
   </tr>
   <tr>
      <td>-</td>
      <td>SUPER</td>
      <td></td>
   </tr>
   <tr>
      <td>-</td>
      <td>RESTRICTED_VARIABLES_ADMIN,RESTRICTED_TABLES_ADMIN</td>
      <td>Required when the target TiDB enables SEM</td>
   </tr>
   <tr>
      <td>Recommended</td>
      <td>Conflict detection, max-error</td>
      <td>Schema configured for lightning.task-info-schema-name</td>
      <td>SELECT, INSERT, UPDATE, DELETE, CREATE, DROP</td>
      <td>If not required, the value must be set to ""</td>
   </tr>
   <tr>
      <td>Optional</td>
      <td>Parallel import</td>
      <td>Schema configured for lightning.meta-schema-name</td>
      <td>SELECT, INSERT, UPDATE, DELETE, CREATE, DROP</td>
      <td>If not required, the value must be set to ""</td>
   </tr>
   <tr>
      <td>Optional</td>
      <td>checkpoint.driver = "mysql"</td>
      <td>checkpoint.schema setting</td>
      <td>SELECT,INSERT,UPDATE,DELETE,CREATE,DROP</td>
      <td>Required when checkpoint information is stored in databases, instead of files</td>
   </tr>
</table>
## Storage space of the target database

The target TiKV cluster must have enough disk space to store the imported data. In addition to the [standard hardware requirements](https://docs.pingcap.com/tidb/stable/hardware-and-software-requirements), the storage space of the target TiKV cluster must be larger than **the size of the data source x the number of replicas x 2**. For example, if the cluster uses 3 replicas by default, the target TiKV cluster must have a storage space larger than 6 times the size of the data source. The formula has x 2 because:

- Indexes might take extra space.
- RocksDB has a space amplification effect.

It is difficult to calculate the exact data volume exported by Dumpling from MySQL. However, you can estimate the data volume by using the following SQL statement to summarize the `DATA_LENGTH` field in the information_schema.tables table:

```sql
-- Calculate the size of all schemas
SELECT
  TABLE_SCHEMA,
  FORMAT_BYTES(SUM(DATA_LENGTH)) AS 'Data Size',
  FORMAT_BYTES(SUM(INDEX_LENGTH)) 'Index Size'
FROM
  information_schema.tables
GROUP BY
  TABLE_SCHEMA;

-- Calculate the 5 largest tables
SELECT 
  TABLE_NAME,
  TABLE_SCHEMA,
  FORMAT_BYTES(SUM(data_length)) AS 'Data Size',
  FORMAT_BYTES(SUM(index_length)) AS 'Index Size',
  FORMAT_BYTES(SUM(data_length+index_length)) AS 'Total Size'
FROM
  information_schema.tables
GROUP BY
  TABLE_NAME,
  TABLE_SCHEMA
ORDER BY
  SUM(DATA_LENGTH+INDEX_LENGTH) DESC
LIMIT
  5;
```
