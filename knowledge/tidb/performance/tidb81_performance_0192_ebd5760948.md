# String match selectivity estimation variable

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_default_string_match_selectivity <span class="version-mark">New in v6.2.0</span>`
- Source Line Ranges: `1735-1748`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `system-variables`, `optimizer`, `selectivity`, `statistics`, `topn`, `like`, `regexp`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0192_ebd5760948`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-default-string-match-selectivity-span-class-version-mark-new-in-v6-2-0-span`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c9141c3c988800cc70067f529a588b4291585e07ce7d6589342c3c113989e705`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-default-string-match-selectivity-span-class-version-mark-new-in-v6-2-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving the system variable that controls default selectivity estimation for like, rlike, and regexp predicates and whether TopN is used for estimation.
- Retrieval Keywords: tidb_default_string_match_selectivity, like selectivity, rlike selectivity, regexp selectivity, TopN, statistics, row estimation, tidb_analyze_version, not like, not rlike, not regexp
- Follow-up Guidance: The content explains that setting the variable to 0 makes TiDB try TopN-based evaluation with statistics collected when tidb_analyze_version is set to 2, which might slightly affect performance.
- Classification Note: This is classified as performance because the content describes an optimizer estimation variable that affects cardinality estimation behavior for string-matching predicates.

## Official Source Content

### tidb_default_string_match_selectivity New in v6.2.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Float
- Default value: `0.8`
- Range: `[0, 1]`
- This variable is used to set the default selectivity of `like`, `rlike`, and `regexp` functions in the filter condition when estimating the number of rows. This variable also controls whether to enable TopN to help estimate these functions.
- TiDB tries to estimate `like` in the filter condition using statistics. But when `like` matches a complex string, or when using `rlike` or `regexp`, TiDB often fails to fully use statistics, and the default value `0.8` is set as the selectivity rate instead, resulting in inaccurate estimation.
- This variable is used to change the preceding behavior. If the variable is set to a value other than `0`, the selectivity rate is the specified variable value instead of `0.8`.
- If the variable is set to `0`, TiDB tries to evaluate using TopN in statistics to improve the accuracy and consider the NULL number in statistics when estimating the preceding three functions. The prerequisite is that statistics are collected when [`tidb_analyze_version`](#tidb_analyze_version-new-in-v510) is set to `2`. Such evaluation might slightly affect the performance.
- If the variable is set to a value other than the `0.8`, TiDB adjusts the estimation for `not like`, `not rlike`, and `not regexp` accordingly.
