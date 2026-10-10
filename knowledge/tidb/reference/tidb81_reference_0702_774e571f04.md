# Statistics versions and tidb_analyze_version

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/statistics.md`
- Source Title: `Introduction to Statistics`
- Source Heading Path: `Introduction to Statistics > Versions of statistics`
- Source Line Ranges: `368-388`
- Source Scope: `all`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `statistics-version`, `analyze`, `optimizer-estimates`, `version-compatibility`, `topn`, `histogram`, `count-min-sketch`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0702_774e571f04`
- Source ID: `tidb-docs-8.1:statistics.md#versions-of-statistics`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bbea9ac2556711efc80216e5761f5dacf4a7e5e4b59351d4c66dbadf5caaf762`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/statistics#versions-of-statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/statistics.md

## Retrieval Guidance

- Use When: Use this chunk when asking what `tidb_analyze_version` means, how statistics Version 1 and Version 2 differ, or what defaults and upgrade behavior apply to statistics versions.
- Retrieval Keywords: tidb_analyze_version, Versions of statistics, statistics Version 1, statistics Version 2, Count-Min Sketch, Column/Index Top-N, Histogram, optimizer estimates, default value changes from 1 to 2, upgraded from an earlier version
- Follow-up Guidance: It also lists which optimizer estimate information each version collects, including row count, equal or IN predicate estimation, range predicate estimation, NULL predicate estimation, and average length of columns and indexes.
- Classification Note: This is classified as reference because it explains the meaning, defaults, and comparison table for statistics versions controlled by `tidb_analyze_version`.

## Official Source Content

## Versions of statistics

The [`tidb_analyze_version`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_analyze_version-new-in-v510) variable controls the statistics collected by TiDB. Currently, two versions of statistics are supported: `tidb_analyze_version = 1` and `tidb_analyze_version = 2`.

- For TiDB Self-Managed, the default value of this variable changes from `1` to `2` starting from v5.3.0.
- For TiDB Cloud, the default value of this variable changes from `1` to `2` starting from v6.5.0.
- If your cluster is upgraded from an earlier version, the default value of `tidb_analyze_version` does not change after the upgrade.

Version 2 is preferred, and will continue to be enhanced to ultimately replace Version 1 completely. Compared to Version 1, Version 2 improves the accuracy of many of the statistics collected for larger data volumes. Version 2 also improves collection performance by removing the need to collect Count-Min sketch statistics for predicate selectivity estimation, and also supporting automated collection only on selected columns (see [Collecting statistics on some columns](#collect-statistics-on-some-columns)).

The following table lists the information collected by each version for usage in the optimizer estimates:

| Information | Version 1 | Version 2|
| --- | --- | ---|
| The total number of rows in the table | ⎷ | ⎷ |
| Equal/IN predicate estimation | ⎷ (Column/Index Top-N & Count-Min Sketch) | ⎷ (Column/Index Top-N & Histogram) |
| Range predicate estimation | ⎷ (Column/Index Top-N & Histogram) | ⎷ (Column/Index Top-N & Histogram) |
| `NULL` predicate estimation | ⎷ | ⎷ |
| The average length of columns | ⎷ | ⎷ |
| The average length of indexes | ⎷ | ⎷ |
