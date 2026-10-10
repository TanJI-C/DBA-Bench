# New features for diagnostics, TiCDC impact reduction, and profiling

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.4.0.md`
- Source Title: `TiDB 5.4 Release Notes`
- Source Heading Path: `TiDB 5.4 Release Notes > New features > Diagnostic efficiency | TiDB 5.4 Release Notes > New features > TiDB data share subscription | TiDB 5.4 Release Notes > New features > Deployment and maintenance`
- Source Line Ranges: `324-352`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `dashboard`, `ticdc`, `tiflash`, `operator`, `tiup`
- Topic Tags: `top-sql`, `diagnostics`, `continuous-profiling`, `profiling`, `tiflash`, `ticdc`, `deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0275_e4e94252ef`
- Source ID: `tidb-docs-8.1:releases/release-5.4.0.md#diagnostic-efficiency`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e33b3f08e3f289d19b5e5c88f9293d40d42046aeacfd1a2e50917581b405956b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.4.0#diagnostic-efficiency
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching for TiDB 5.4 features about Top SQL, reduced TiCDC performance impact, or Continuous Profiling support and prerequisites.
- Retrieval Keywords: Top SQL, experimental feature, disabled by default, source-consuming queries, TiCDC impact, performance impact of TiCDC, less than 5%, Continuous Profiling, CPU profiling, TiFlash, Goroutine, flame charts, TiDB Dashboard, TiDB Operator, TiUP v1.9.0 or later, TiDB Operator v1.3.0 or later
- Follow-up Guidance: The source points to user documents for Top SQL and Continuous Profiling on TiDB Dashboard.
- Classification Note: This is a release-note chunk covering new features in diagnostic efficiency, TiCDC impact reduction, and deployment and maintenance profiling support in TiDB 5.4.0.

## Official Source Content

### Diagnostic efficiency

- **Top SQL (experimental feature)**

    A new experimental feature, Top SQL (disabled by default), is introduced to help you easily find source-consuming queries.

    [User document](https://docs.pingcap.com/tidb/stable/dashboard/top-sql)
### TiDB data share subscription

- **Optimize the impact of TiCDC on clusters**

    Significantly reduces the impact on the performance of TiDB clusters when you use TiCDC. In the test environment, the performance impact of TiCDC on TiDB can be reduced to less than 5%.
### Deployment and maintenance

- **Enhance Continuous Profiling (experimental)**

    - More components supported: Besides TiDB, PD, and TiKV, TiDB v5.4.0 also supports CPU profiling of TiFlash.
    - More forms of profiling display: Supports showing CPU profiling and Goroutine results on flame charts.

    - More deployment environments supported: Continuous Profiling can also be used for clusters deployed using TiDB Operator.

   Continuous Profiling is disabled by default and can be enabled on TiDB Dashboard.

    Continuous Profiling is applicable to clusters deployed or upgraded using TiUP of v1.9.0 or later or TiDB Operator of v1.3.0 or later.

    [User document](https://docs.pingcap.com/tidb/stable/dashboard/continuous-profiling)
