# Old conflict detection behavior and duplicate handling

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-physical-import-mode-usage.md`
- Source Title: `Use Physical Import Mode`
- Source Heading Path: `Use Physical Import Mode > Conflict detection > The old version of conflict detection (deprecated in v8.0.0)`
- Source Line Ranges: `134-188`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `tikv`
- Topic Tags: `conflict-detection`, `duplicate-resolution`, `deprecated`, `version-behavior`, `checksum`, `manual-reconciliation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0343_dd2fb372bf`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-physical-import-mode-usage.md#the-old-version-of-conflict-detection-deprecated-in-v8-0-0`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3f5cc6ba99b086b32cbda85a7ef1d0827edcae07c4a56c2c20ffc371227d0371`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#the-old-version-of-conflict-detection-deprecated-in-v8-0-0
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-physical-import-mode-usage.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about deprecated old conflict detection in TiDB Lightning, duplicate handling behavior, version-specific behavior of `tikv-importer.duplicate-resolution`, or querying duplicate records after import conflicts.
- Retrieval Keywords: tikv-importer.duplicate-resolution, conflict.strategy, duplicate-resolution remove, duplicate-resolution none, old version of conflict detection, deprecated in v8.0.0, cannot be configured at the same time, conflict_error_v1, lightning_task_info.conflict_error_v1, select table_name,index_name,key_data,row_data from conflict_error_v1 limit 10, checksum step, order_line, PRIMARY
- Follow-up Guidance: If conflicting data is detected during import, the content shows querying `lightning_task_info.conflict_error_v1` and then manually identifying the records to retain before inserting those records into the table.
- Classification Note: This is classified as configuration because it centers on the behavior and compatibility of the `tikv-importer.duplicate-resolution` and `conflict.strategy` parameters, including their version-specific semantics and restrictions.

## Official Source Content

### The old version of conflict detection (deprecated in v8.0.0)

Starting from v8.0.0, the old version of conflict detection (`tikv-importer.duplicate-resolution`) is deprecated. The `tikv-importer.duplicate-resolution` parameter will be removed in a future release. If `tikv-importer.duplicate-resolution` is `remove` and `conflict.strategy` is not configured, TiDB Lightning automatically enables the new version of conflict detection by assigning the value of `conflict.strategy` to `"replace"`. Note that `tikv-importer.duplicate-resolution` and `conflict.strategy` cannot be configured at the same time, as it will result in an error.

- For versions between v7.3.0 and v7.6.0, TiDB Lightning enables the old version of conflict detection when `tikv-importer.duplicate-resolution` is not an empty string.
- For v7.2.0 and earlier versions, TiDB Lightning only supports the old version of conflict detection.

In the old version of conflict detection, TiDB Lightning offers two strategies:

- `remove` (recommended): records and removes all conflicting records from the target table to ensure a consistent state in the target TiDB.
- `none`: does not detect duplicate records. `none` has the best performance in the two strategies, but might lead to inconsistent data in the target TiDB.

Before v5.3, TiDB Lightning does not support conflict detection. If there is conflicting data, the import process fails at the checksum step. When conflict detection is enabled, if there is conflicting data, TiDB Lightning skips the checksum step (because it always fails).

Suppose an `order_line` table has the following schema:

```sql
CREATE TABLE IF NOT EXISTS `order_line` (
  `ol_o_id` int(11) NOT NULL,
  `ol_d_id` int(11) NOT NULL,
  `ol_w_id` int(11) NOT NULL,
  `ol_number` int(11) NOT NULL,
  `ol_i_id` int(11) NOT NULL,
  `ol_supply_w_id` int(11) DEFAULT NULL,
  `ol_delivery_d` datetime DEFAULT NULL,
  `ol_quantity` int(11) DEFAULT NULL,
  `ol_amount` decimal(6,2) DEFAULT NULL,
  `ol_dist_info` char(24) DEFAULT NULL,
  PRIMARY KEY (`ol_w_id`,`ol_d_id`,`ol_o_id`,`ol_number`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
```

If Lightning detects conflicting data during the import, you can query the `lightning_task_info.conflict_error_v1` table as follows:

```sql
mysql> select table_name,index_name,key_data,row_data from conflict_error_v1 limit 10;
+---------------------+------------+----------+-----------------------------------------------------------------------------+
|  table_name         | index_name | key_data | row_data                                                                    |
+---------------------+------------+----------+-----------------------------------------------------------------------------+
| `tpcc`.`order_line` | PRIMARY    | 21829216 | (2677, 10, 10, 11, 75656, 10, NULL, 5, 5831.97, "HT5DN3EVb6kWTd4L37bsbogj") |
| `tpcc`.`order_line` | PRIMARY    | 49931672 | (2677, 10, 10, 11, 75656, 10, NULL, 5, 5831.97, "HT5DN3EVb6kWTd4L37bsbogj") |
| `tpcc`.`order_line` | PRIMARY    | 21829217 | (2677, 10, 10, 12, 76007, 10, NULL, 5, 9644.36, "bHuVoRfidQ0q2rJ6ZC9Hd12E") |
| `tpcc`.`order_line` | PRIMARY    | 49931673 | (2677, 10, 10, 12, 76007, 10, NULL, 5, 9644.36, "bHuVoRfidQ0q2rJ6ZC9Hd12E") |
| `tpcc`.`order_line` | PRIMARY    | 21829218 | (2677, 10, 10, 13, 85618, 10, NULL, 5, 7427.98, "t3rsesgi9rVAKi9tf6an5Rpv") |
| `tpcc`.`order_line` | PRIMARY    | 49931674 | (2677, 10, 10, 13, 85618, 10, NULL, 5, 7427.98, "t3rsesgi9rVAKi9tf6an5Rpv") |
| `tpcc`.`order_line` | PRIMARY    | 21829219 | (2677, 10, 10, 14, 15873, 10, NULL, 5, 133.21, "z1vH0e31tQydJGhfNYNa4ScD")  |
| `tpcc`.`order_line` | PRIMARY    | 49931675 | (2677, 10, 10, 14, 15873, 10, NULL, 5, 133.21, "z1vH0e31tQydJGhfNYNa4ScD")  |
| `tpcc`.`order_line` | PRIMARY    | 21829220 | (2678, 10, 10, 1, 44644, 10, NULL, 5, 8463.76, "TWKJBt5iJA4eF7FIVxnugNmz")  |
| `tpcc`.`order_line` | PRIMARY    | 49931676 | (2678, 10, 10, 1, 44644, 10, NULL, 5, 8463.76, "TWKJBt5iJA4eF7FIVxnugNmz")  |
+---------------------+------------+----------------------------------------------------------------------------------------+
10 rows in set (0.14 sec)
```

You can manually identify the records that need to be retained and insert these records into the table.
