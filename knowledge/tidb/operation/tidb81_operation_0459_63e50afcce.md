# Physical import mode conflict detection

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-lightning/tidb-lightning-physical-import-mode-usage.md`
- Source Title: `Use Physical Import Mode`
- Source Heading Path: `Use Physical Import Mode > Conflict detection | Use Physical Import Mode > Conflict detection > The new version of conflict detection`
- Source Line Ranges: `102-133`
- Source Scope: `self_managed`
- Primary Component: `lightning`
- Related Components: `tidb`, `tikv`
- Topic Tags: `conflict-detection`, `duplicate-keys`, `replace-strategy`, `error-strategy`, `precheck-conflict`, `threshold`, `limitations`, `deprecated-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0459_63e50afcce`
- Source ID: `tidb-docs-8.1:tidb-lightning/tidb-lightning-physical-import-mode-usage.md#conflict-detection`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1fbc00068b3d38ac5f9f4266f7ded67624e4b26e71831a5d1ae0bc842a35f372`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-physical-import-mode-usage#conflict-detection
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-lightning/tidb-lightning-physical-import-mode-usage.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiDB Lightning physical import mode handles conflicting primary key or unique key data with the new conflict detection settings and their limitations.
- Retrieval Keywords: Conflict detection, conflicting data, same primary key or unique key, new version of conflict detection, old version of conflict detection, conflict configuration item, tikv-importer.duplicate-resolution, strategy "replace", strategy "error", strategy "", REPLACE INTO, INSERT INTO, conflict.threshold, conflict errors, precheck-conflict-before-import, tikv-importer.sorted-kv-dir, single node, parallel imports, disk-quota
- Follow-up Guidance: The source states that preprocess conflict detection can be enabled with `precheck-conflict-before-import`, and it describes overhead and limitations such as single-node only operation and no support when `disk-quota` is enabled.
- Classification Note: This is classified as operation because it explains runtime conflict detection behavior, error handling, tolerance, and execution limitations during import.

## Official Source Content

## Conflict detection

Conflicting data refers to two or more records with the same primary key or unique key column data. When the data source contains conflicting data and conflict detection feature is not turned on, the actual number of rows in the table is different from the total number of rows returned by the query using unique index.

There are two versions for conflict detection:

- The new version of conflict detection, controlled by the `conflict` configuration item.
- The old version of conflict detection (deprecated in v8.0.0 and will be removed in a future release), controlled by the `tikv-importer.duplicate-resolution` configuration item.
### The new version of conflict detection

The meanings of configuration values are as follows:

| Strategy | Default behavior of conflicting data | The corresponding SQL statement |
| :-- | :-- | :-- |
| `"replace"` | Retaining the latest data and overwriting the old data | `REPLACE INTO ...` |
| `"error"` | Terminating the import and reporting an error. | `INSERT INTO ...` |
| `""` | TiDB Lightning does not detect or handle conflicting data. If data with primary and unique key conflicts exists, the subsequent checksum step reports an error. |  None   |

> **Note:**
>
> The conflict detection result in the physical import mode might differ from SQL-based import due to internal implementation and limitation of TiDB Lightning.

When the strategy is `"error"` and conflicting data is detected, TiDB Lightning reports an error and exits the import. When the strategy is `"replace"`, conflicting data is treated as [conflict errors](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-error-resolution#conflict-errors). If the [`conflict.threshold`](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-configuration#tidb-lightning-task) value is greater than `0`, TiDB Lightning tolerates the specified number of conflict errors. The default value is `9223372036854775807`, which means that almost all errors are tolerant. For more information, see [error resolution](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-error-resolution).

The new version of conflict detection has the following limitations:

- Before importing, TiDB Lightning prechecks potential conflicting data by reading all data and encoding it. During the detection process, TiDB Lightning uses `tikv-importer.sorted-kv-dir` to store temporary files. After the detection is complete, TiDB Lightning retains the results for import phase. This introduces additional overhead for time consumption, disk space usage, and API requests to read the data.
- The new version of conflict detection only works in a single node, and does not apply to parallel imports and scenarios where the `disk-quota` parameter is enabled.

The new version of conflict detection controls whether to enable preprocess conflict detection via the `precheck-conflict-before-import` parameter. In cases where the original data contains a lot of conflicting data, the total time consumed by conflict detection before and after the import is less than that of the old version. Therefore, it is recommended to enable preprocess conflict detection in scenarios where the ratio of conflict records is greater than or equal to 1% and the local disk space is sufficient.
