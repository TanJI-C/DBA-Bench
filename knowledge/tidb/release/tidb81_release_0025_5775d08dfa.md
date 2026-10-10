# TiDB 2.0 RC4 release notes

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.0-rc.4.md`
- Source Title: `TiDB 2.0 RC4 Release Notes`
- Source Heading Path: `TiDB 2.0 RC4 Release Notes | TiDB 2.0 RC4 Release Notes > TiDB | TiDB 2.0 RC4 Release Notes > PD | TiDB 2.0 RC4 Release Notes > TiKV`
- Source Line Ranges: `5-38`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `pd`, `tikv`, `sql`
- Topic Tags: `release-notes`, `mysql-compatibility`, `sql-optimization`, `stability`, `region-splitting`, `memory-usage`, `snapshot`, `coprocessor`, `pdctl`, `bug-fixes`, `performance`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0025_5775d08dfa`
- Source ID: `tidb-docs-8.1:releases/release-2.0-rc.4.md#tidb-2-0-rc4-release-notes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8be6b6de8451d2d3b7a850f685e87bc3295b69731a5b271f90a0e31d8ad802b5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.0-rc.4#tidb-2-0-rc4-release-notes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.0-rc.4.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 2.0 RC4 release-note items covering MySQL compatibility, SQL optimization, stability, or specific fixes and features in TiDB, PD, and TiKV.
- Retrieval Keywords: TiDB 2.0 RC4 Release Notes, SHOW GRANTS FOR CURRENT_USER(), SET TRANSACTION, UnionScan, copIterator, admin check table, unique index including null, CREATE VIEW, ORDER BY and LIMIT 0, LIMIT 0 to TableDual, DecodeBytes, PD, pdctl config show all, config show all, splitting Region manually, hot spot in a single Region, TiKV, receiving snapshots, OOM in extreme conditions, Coprocessor warnings, importing the data pattern in TiKV, splitting Region in the middle, crossbeam channel, leader missing when TiKV is isolated
- Follow-up Guidance: The source groups the changes by component under TiDB, PD, and TiKV release-note sections.
- Classification Note: This is a self-managed release-notes chunk that enumerates version-specific improvements, supported SQL syntax, optimizations, and bug fixes across shared components including TiDB, PD, and TiKV.

## Official Source Content

# TiDB 2.0 RC4 Release Notes

On March 30, 2018, TiDB 2.0 RC4 is released. This release has great improvement in MySQL compatibility, SQL optimization and stability.
## TiDB

- Support `SHOW GRANTS FOR CURRENT_USER();`
- Fix the issue that the `Expression` in `UnionScan` is not cloned
- Support the `SET TRANSACTION` syntax
- Fix the potential goroutine leak issue in `copIterator`
- Fix the issue that `admin check table` misjudges the unique index including null
- Support displaying floating point numbers using scientific notation
- Fix the type inference issue during binary literal computing
- Fix the issue in parsing the `CREATE VIEW` statement
- Fix the panic issue when one statement contains both `ORDER BY` and `LIMIT 0`
- Improve the execution performance of `DecodeBytes`
- Optimize `LIMIT 0` to `TableDual`, to avoid building useless execution plans
## PD

- Support splitting Region manually to handle the hot spot in a single Region
- Fix the issue that the label property is not displayed when `pdctl` runs `config show all`
- Optimize metrics and code structure
## TiKV

- Limit the memory usage during receiving snapshots, to avoid OOM in extreme conditions
- Support configuring the behavior of Coprocessor when it encounters warnings
- Support importing the data pattern in TiKV
- Support splitting Region in the middle
- Increase the speed of CI test
- Use `crossbeam channel`
- Fix the issue that too many logs are output caused by leader missing when TiKV is isolated
