# Handle false positives from MySQL vulnerability scanners

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices-for-security-configuration.md`
- Source Title: `Best Practices for TiDB Security Configuration`
- Source Heading Path: `Best Practices for TiDB Security Configuration > Resolving false positives from third-party MySQL vulnerability scanners`
- Source Line Ranges: `120-124`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `security`, `vulnerability-scanner`, `mysql-compatibility`, `server-version`, `upgrade`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0017_7d39dbde26`
- Source ID: `tidb-docs-8.1:best-practices-for-security-configuration.md#resolving-false-positives-from-third-party-mysql-vulnerability-scanners`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `693734edb66e7bc24440a9e416c302482b26a421851a0c5503d36264cc3c0d33`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices-for-security-configuration#resolving-false-positives-from-third-party-mysql-vulnerability-scanners
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices-for-security-configuration.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving explanation for false positives from third-party MySQL vulnerability scanners against TiDB and the role of the server version string.
- Retrieval Keywords: false positives, third-party MySQL vulnerability scanners, MySQL protocol-compatible, version-based vulnerability scans, principle-based assessments, modify the server version number, server-version, security vulnerability scanning tool, before upgrading, unexpected behavior
- Follow-up Guidance: The content states that before upgrading the TiDB cluster, the `server-version` value should be empty or the actual TiDB version to avoid unexpected behavior.
- Classification Note: This is classified as reference because the content explains how scanner results relate to TiDB's MySQL compatibility and documents the `server-version` identifier and its upgrade caveat.

## Official Source Content

## Resolving false positives from third-party MySQL vulnerability scanners

Most vulnerability scanners detect MySQL vulnerabilities based on version information. Because TiDB is MySQL protocol-compatible but not MySQL itself, version-based vulnerability scans might lead to false positives. It is recommended to focus vulnerability scans on principle-based assessments. If compliance scanning tools require a specific MySQL version, you can [modify the server version number](https://docs.pingcap.com/tidb/stable/faq/high-reliability-faq#does-tidb-support-modifying-the-mysql-version-string-of-the-server-to-a-specific-one-that-is-required-by-the-security-vulnerability-scanning-tool) to meet the requirement.

By changing the server version number, you can avoid false positives from vulnerability scanners. The [`server-version`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#server-version) value is used by TiDB nodes to verify the current TiDB version. Before upgrading the TiDB cluster, ensure that the `server-version` value is either empty or the actual version of TiDB to avoid unexpected behavior.
