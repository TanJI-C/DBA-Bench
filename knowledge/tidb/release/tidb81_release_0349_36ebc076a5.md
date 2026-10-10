# Security and observability new features

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.4.0.md`
- Source Title: `TiDB 6.4.0 Release Notes`
- Source Heading Path: `TiDB 6.4.0 Release Notes > New features > Security | TiDB 6.4.0 Release Notes > New features > Observability`
- Source Line Ranges: `60-75`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiflash`, `dashboard`
- Topic Tags: `security`, `encryption-at-rest`, `sm4`, `observability`, `cluster-diagnostics`, `diagnostic-report`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0349_36ebc076a5`
- Source ID: `tidb-docs-8.1:releases/release-6.4.0.md#security`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5bb78b5d94994d607e97454df59ea28548e6306e3f717c9f07558106eaa8ae8f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.4.0#security
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 6.4.0 security or observability additions involving TiFlash encryption at rest or TiDB Dashboard cluster diagnostics.
- Retrieval Keywords: Security, Observability, TiFlash supports the SM4 algorithm for encryption at rest, data-encryption-method, sm4-ctr, tiflash-learner.toml, Cluster diagnostics becomes GA, TiDB Dashboard, diagnostic report, dashboard-diagnostics-access, dashboard-diagnostics-report, diagnostic information
- Follow-up Guidance: The source says cluster diagnostics in TiDB Dashboard can diagnose problems within a specified time range and summarize results and load monitoring information into an offline-browsable diagnostic report.
- Classification Note: This chunk is classified as shared because it covers cross-cutting release features in security and observability rather than a single SQL or storage interface.

## Official Source Content

### Security

* TiFlash supports the SM4 algorithm for encryption at rest [#5953](https://github.com/pingcap/tiflash/issues/5953) @[lidezhu](https://github.com/lidezhu)

    Add the SM4 algorithm for TiFlash encryption at rest. When you configure encryption at rest, you can enable the SM4 encryption capacity by setting the value of the `data-encryption-method` configuration to `sm4-ctr` in the `tiflash-learner.toml` configuration file.

    For more information, see [User document](https://docs.pingcap.com/tidb/stable/encryption-at-rest#tiflash).
### Observability

* Cluster diagnostics becomes GA [#1438](https://github.com/pingcap/tidb-dashboard/issues/1438) @[Hawkson-jee](https://github.com/Hawkson-jee)

    The [cluster diagnostics](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-diagnostics-access) feature in TiDB Dashboard diagnoses the problems that might exist in a cluster within a specified time range, and summarizes the diagnostic results and the cluster-related load monitoring information into [a diagnostic report](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-diagnostics-report). This diagnostic report is in the form of a web page. You can browse the page offline and circulate this page link after saving the page from a browser.

    With the diagnostic reports, you can quickly understand the basic health information of the cluster, including the load, component status, time consumption, and configurations. If the cluster has some common problems, you can locate the causes in the result of the built-in automatic diagnosis in the [diagnostic information](https://docs.pingcap.com/tidb/stable/dashboard/dashboard-diagnostics-report#diagnostic-information) section.
