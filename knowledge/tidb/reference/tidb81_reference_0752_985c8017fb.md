# Table filter multiple-rule matching behavior

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/table-filter.md`
- Source Title: `Table Filter`
- Source Heading Path: `Table Filter > Multiple rules`
- Source Line Ranges: `221-273`
- Source Scope: `all`
- Primary Component: `shared`
- Related Components: `cloud`, `dumpling`
- Topic Tags: `multiple-rules`, `match-order`, `blocklist`, `default-reject`, `system-schemas`, `cloud-limitations`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0752_985c8017fb`
- Source ID: `tidb-docs-8.1:table-filter.md#multiple-rules`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3a3dde3dcaf70b6440bb29bb87492e211f1ae1105af8e5af72f3c535459359b7`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/table-filter#multiple-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/table-filter.md

## Retrieval Guidance

- Use When: Use this when looking for how multiple table filter rules are evaluated, including default rejection, block list setup, last-match-wins behavior, and system schema exclusions.
- Retrieval Keywords: multiple rules, default behavior ignore unmatched tables, explicit *.* must be used as the first rule, block list, last match decides the outcome, tiup dumpling -f '!*.Password', tiup dumpling -f '*.*' -f '!*.Password', employees.*, !*.dep*, *.departments, Default (reject), Rule 1 (accept), Rule 2 (reject), Rule 3 (accept), system schemas are always excluded, INFORMATION_SCHEMA, PERFORMANCE_SCHEMA, METRICS_SCHEMA, INSPECTION_SCHEMA, mysql, sys, TiDB Cloud only supports one table filter rule
- Follow-up Guidance: It also notes that this section is not applicable to TiDB Cloud because TiDB Cloud currently supports only one table filter rule.
- Classification Note: This is reference content because it explains the rule evaluation semantics, precedence, defaults, and documented exclusions for table filtering.

## Official Source Content

## Multiple rules

> **Note:**
>
> This section is not applicable to TiDB Cloud. Currently, TiDB Cloud only supports one table filter rule.

When a table name matches none of the rules in the filter list, the default behavior is to ignore such unmatched tables.

To build a block list, an explicit `*.*` must be used as the first rule, otherwise all tables will be excluded.

```bash
# every table will be filtered out
tiup dumpling -f '!*.Password'

# only the "Password" table is filtered out, the rest are included.
tiup dumpling -f '*.*' -f '!*.Password'
```

In a filter list, if a table name matches multiple patterns, the last match decides the outcome. For instance:

```
# rule 1
employees.*
# rule 2
!*.dep*
# rule 3
*.departments
```

The filtered outcome is as follows:

| Table name            | Rule 1 | Rule 2 | Rule 3 | Outcome          |
|-----------------------|--------|--------|--------|------------------|
| irrelevant.table      |        |        |        | Default (reject) |
| employees.employees   | ✓      |        |        | Rule 1 (accept)  |
| employees.dept_emp    | ✓      | ✓      |        | Rule 2 (reject)  |
| employees.departments | ✓      | ✓      | ✓      | Rule 3 (accept)  |
| else.departments      |        | ✓      | ✓      | Rule 3 (accept)  |

> **Note:**
>
> In TiDB tools, the system schemas are always excluded in the default configuration. The system schemas are:
>
> * `INFORMATION_SCHEMA`
> * `PERFORMANCE_SCHEMA`
> * `METRICS_SCHEMA`
> * `INSPECTION_SCHEMA`
> * `mysql`
> * `sys`
