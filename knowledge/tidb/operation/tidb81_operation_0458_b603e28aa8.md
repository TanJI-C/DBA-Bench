# Conflict detection in logical import mode

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-logical-import-mode-usage.md`
- Source Title: `Use Logical Import Mode`
- Source Heading Path: `Use Logical Import Mode > Conflict detection`
- Source Line Ranges: `48-62`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`
- Topic Tags: `conflict detection`, `primary key`, `unique key`, `conflict strategy`, `conflict threshold`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0458_b603e28aa8`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-logical-import-mode-usage.md#conflict-detection`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `375f684918d9778d282199fe6e78831526372f774133f7debe58f04d4d6f3347`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-logical-import-mode-usage#conflict-detection
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-logical-import-mode-usage.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how TiDB Lightning logical import mode handles conflicting data in PK or UK columns and which SQL statements correspond to each conflict strategy.
- Retrieval Keywords: Conflict detection, conflict.strategy, conflict.threshold, conflict.max-record-rows, replace, ignore, error, REPLACE INTO, INSERT INTO, INSERT IGNORE INTO, conflict_records table, PK or UK column
- Follow-up Guidance: When the strategy is "ignore", conflicting data is recorded in the downstream conflict_records table, and starting from v8.1.0 conflict.threshold is used because max-record-rows is automatically assigned from threshold.
- Classification Note: This is classified as operation because the content explains runtime conflict handling behavior and the effects of conflict strategy settings during import.

## Official Source Content

## Conflict detection

Conflicting data refers to two or more records with the same data in the PK or UK column. In the logical import mode, you can configure the strategy for handling conflicting data by setting the [`conflict.strategy`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) configuration item. Based on the strategy, TiDB Lightning imports data with different SQL statements.

| Strategy | Default behavior of conflicting data | The corresponding SQL statement |
| :-- | :-- | :-- |
| `"replace"` | Replacing existing data with new data. | `REPLACE INTO ...` |
| `"ignore"` | Keeping existing data and ignoring new data. | If `conflict.threshold` is greater than 0, `INSERT INTO` is used; if `conflict.threshold` is `0`, `INSERT IGNORE INTO ...` is used |
| `"error"` | Terminating the import when conflicting data is detected. | `INSERT INTO ...` |
|  `""`  | Converted to `"error"`, which means terminating the import when conflicting data is detected.  |  None   |

When the strategy is `"error"`, errors caused by conflicting data directly terminate the import task. When the strategy is `"replace"` or `"ignore"`, you can control the maximum tolerant conflicts by configuring [`conflict.threshold`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task). The default value is `10000`, which means that 10000 errors are tolerant.

When the strategy is `"ignore"`, conflicting data is recorded in the downstream `conflict_records` table. For further details, see [Error report](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-error-resolution#error-report). Before v8.1.0, you can limit the records by configuring [`conflict.max-record-rows`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task), and conflicting data that exceeds the limit is skipped and not recorded. Starting from v8.1.0, you need to configure [`conflict.threshold`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) instead, because TiDB Lightning automatically assigns the value of `max-record-rows` with the value of `threshold`, regardless of the user input.
