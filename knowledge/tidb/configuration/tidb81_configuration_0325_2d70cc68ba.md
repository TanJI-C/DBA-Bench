# Pessimistic transaction defaults and isolation-read engines

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > pessimistic-txn > pessimistic-auto-commit <span class="version-mark">New in v6.0.0</span> | TiDB Configuration File > pessimistic-txn > constraint-check-in-place-pessimistic <span class="version-mark">New in v6.4.0</span> | TiDB Configuration File > isolation-read | TiDB Configuration File > isolation-read > `engines``
- Source Line Ranges: `885-907`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiflash`
- Topic Tags: `pessimistic-transactions`, `autocommit`, `constraint-checking`, `read-isolation`, `engine-selection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0325_2d70cc68ba`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#pessimistic-auto-commit-span-class-version-mark-new-in-v6-0-0-span`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `33a9fc3f5eb958e80f4d3450518d3ac7582fa86c956a21a885b2a0a137212c95`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#pessimistic-auto-commit-span-class-version-mark-new-in-v6-0-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiDB configuration details for pessimistic-auto-commit, constraint-check-in-place-pessimistic, or isolation-read engines selection.
- Retrieval Keywords: pessimistic-auto-commit, tidb_txn_mode='pessimistic', auto-commit transaction uses pessimistic mode, global lock-waiting management, deadlocks, latency spike, INSERT INTO SELECT, tidb_dml_type, bulk, constraint-check-in-place-pessimistic, tidb_constraint_check_in_place_pessimistic, isolation-read, engines, tikv, tiflash, tidb, optimizer automatically selected
- Follow-up Guidance: The content also states that when tidb_dml_type is set to "bulk", the effect of pessimistic-auto-commit in the session is equivalent to setting it to false.
- Classification Note: This is classified as configuration because it defines TiDB configuration items and their default values for transaction behavior and read engine selection.

## Official Source Content

### pessimistic-auto-commit New in v6.0.0

+ Determines the transaction mode that the auto-commit transaction uses when the pessimistic transaction mode is globally enabled (`tidb_txn_mode='pessimistic'`). By default, even if the pessimistic transaction mode is globally enabled, the auto-commit transaction still uses the optimistic transaction mode. After enabling `pessimistic-auto-commit` (set to `true`), the auto-commit transaction also uses pessimistic mode, which is consistent with the other explicitly committed pessimistic transactions.
+ For scenarios with conflicts, after enabling this configuration, TiDB includes auto-commit transactions into the global lock-waiting management, which avoids deadlocks and mitigates the latency spike brought by deadlock-causing conflicts.
+ For scenarios with no conflicts, if there are many auto-commit transactions (the specific number is determined by the real scenarios. For example, the number of auto-commit transactions accounts for more than half of the total number of applications), and a single transaction operates a large data volume, enabling this configuration causes performance regression. For example, the auto-commit `INSERT INTO SELECT` statement.
+ When the session-level system variable [`tidb_dml_type`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_dml_type-new-in-v800) is set to `"bulk"`, the effect of this configuration in the session is equivalent to setting it to `false`.
+ Default value: `false`
### constraint-check-in-place-pessimistic New in v6.4.0

+ Controls the default value of the system variable [`tidb_constraint_check_in_place_pessimistic`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_constraint_check_in_place_pessimistic-new-in-v630).
+ Default value: `true`
## isolation-read

Configuration items related to read isolation.
### `engines`

- Controls from which engine TiDB allows to read data.
- Default value: ["tikv", "tiflash", "tidb"], indicating that the engine is automatically selected by the optimizer.
- Value options: Any combinations of "tikv", "tiflash", and "tidb", for example, ["tikv", "tidb"] or ["tiflash", "tidb"]
