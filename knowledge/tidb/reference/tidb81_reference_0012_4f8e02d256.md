# Statistics, security, and data movement feature matrices

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/basic-features.md`
- Source Title: `TiDB Features`
- Source Heading Path: `TiDB Features > Statistics | TiDB Features > Security | TiDB Features > Data import and export`
- Source Line Ranges: `170-222`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `sql`, `tidb`, `lightning`, `dumpling`, `dm`, `ticdc`
- Topic Tags: `feature-matrix`, `statistics`, `security`, `data-import`, `data-export`, `authentication`, `encryption`, `migration`, `change-data-capture`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0012_4f8e02d256`
- Source ID: `tidb-docs-8.1:basic-features.md#statistics`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ffb4cf70b4a5c5c155a76abebfa40ac20621a3f02151c9f8ec5f9804e7958d3b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/basic-features#statistics
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/basic-features.md

## Retrieval Guidance

- Use When: Use this chunk when comparing TiDB 8.1 feature matrix availability across statistics, security, and data import and export capabilities, including whether a feature is Y, E, N, Deprecated, or Disabled by default.
- Retrieval Keywords: Statistics feature matrix, Security feature matrix, Data import and export feature matrix, CMSketch Disabled by default, Histograms, Extended statistics, Statistics feedback, Automatically update statistics, Dynamic pruning, Collect statistics for PREDICATE COLUMNS, Control the memory quota for collecting statistics, tidb_enable_fast_analyze, Lock statistics, Lightweight statistics initialization, SHOW ANALYZE STATUS, Transparent layer security TLS, Encryption at rest TDE, Role-based authentication RBAC, Certificate-based authentication, caching_sha2_password authentication, tidb_sm3_password authentication, tidb_auth_token authentication, authentication_ldap_sasl authentication, authentication_ldap_simple authentication, Password management, MySQL compatible GRANT system, Dynamic Privileges, Security Enhanced Mode, tidb_enable_enhanced_security, Redacted Log Files, Fast import using TiDB Lightning, IMPORT INTO, mydumper logical dumper Deprecated, Dumpling logical dumper, Transactional LOAD DATA, Database migration toolkit DM, TiDB Binlog, Change data capture CDC, Stream data to Amazon S3 GCS Azure Blob Storage and NFS through TiCDC, TiCDC supports bidirectional replication between two TiDB clusters, TiCDC OpenAPI v2, DM supports migrating MySQL 8.0
- Follow-up Guidance: The matrices list per-version status for each named feature across 8.1, 7.5, 7.1, 6.5, 6.1, 5.4, 5.3, 5.2, and 5.1.
- Classification Note: This is a reference chunk because the official content is a set of feature matrices summarizing support status by version for statistics, security, and data import and export features.

## Official Source Content

## Statistics

| Statistics | 8.1 | 7.5 | 7.1 | 6.5 | 6.1 | 5.4 | 5.3 | 5.2 | 5.1 |
|---|---|---|---|---|---|---|---|---|---|
| [CMSketch](https://docs.pingcap.com/tidb/stable/statistics) | Disabled by default | Disabled by default | Disabled by default | Disabled by default | Disabled by default | Disabled by default | Disabled by default | Y | Y |
| [Histograms](https://docs.pingcap.com/tidb/stable/statistics) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Extended statistics](https://docs.pingcap.com/tidb/stable/extended-statistics) | E | E | E | E | E | E | E | E | E |
| Statistics feedback | N | N | N | N | Deprecated | Deprecated | E | E | E |
| [Automatically update statistics](https://docs.pingcap.com/tidb/stable/statistics#automatic-update) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Dynamic pruning](https://docs.pingcap.com/tidb/stable/partitioned-table#dynamic-pruning-mode) | Y | Y | Y | Y | Y | E | E | E | E |
| [Collect statistics for `PREDICATE COLUMNS`](https://docs.pingcap.com/tidb/stable/statistics#collect-statistics-on-some-columns) | E | E | E | E | E | E | N | N | N |
| [Control the memory quota for collecting statistics](https://docs.pingcap.com/tidb/stable/statistics#the-memory-quota-for-collecting-statistics) | E | E | E | E | N | N | N | N | N |
| [Randomly sample about 10000 rows of data to quickly build statistics](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_fast_analyze) | Deprecated | Deprecated | E | E | E | E | E | E | E |
| [Lock statistics](https://docs.pingcap.com/tidb/stable/statistics#lock-statistics) | Y | Y | E | E | N | N | N | N | N |
| [Lightweight statistics initialization](https://docs.pingcap.com/tidb/stable/statistics#load-statistics) | Y | Y | E | N | N | N | N | N | N |
| [Show the progress of collecting statistics](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-analyze-status) | Y | Y | N | N | N | N | N | N | N |
## Security

| Security | 8.1 | 7.5 | 7.1 | 6.5 | 6.1 | 5.4 | 5.3 | 5.2 | 5.1 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| [Transparent layer security (TLS)](https://docs.pingcap.com/tidb/stable/enable-tls-between-clients-and-servers) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Encryption at rest (TDE)](https://docs.pingcap.com/tidb/stable/encryption-at-rest) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Role-based authentication (RBAC)](https://docs.pingcap.com/tidb/stable/role-based-access-control) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Certificate-based authentication](https://docs.pingcap.com/tidb/stable/certificate-authentication) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [`caching_sha2_password` authentication](https://docs.pingcap.com/tidb/stable/system-variables#default_authentication_plugin) | Y | Y | Y | Y | Y | Y | Y | Y | N |
| [`tidb_sm3_password` authentication](https://docs.pingcap.com/tidb/stable/system-variables#default_authentication_plugin) | Y | Y | Y | Y | N | N | N | N | N |
| [`tidb_auth_token` authentication](https://docs.pingcap.com/tidb/stable/security-compatibility-with-mysql#tidb_auth_token) | Y | Y | Y | Y | N | N | N | N | N |
| [`authentication_ldap_sasl` authentication](https://docs.pingcap.com/tidb/stable/system-variables#default_authentication_plugin) | Y | Y | N | N | N | N | N | N | N |
| [`authentication_ldap_simple` authentication](https://docs.pingcap.com/tidb/stable/system-variables#default_authentication_plugin) | Y | Y | Y | N | N | N | N | N | N |
| [Password management](https://docs.pingcap.com/tidb/stable/password-management) | Y | Y | Y | Y | N | N | N | N | N |
| [MySQL compatible `GRANT` system](https://docs.pingcap.com/tidb/stable/privilege-management) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Dynamic Privileges](https://docs.pingcap.com/tidb/stable/privilege-management#dynamic-privileges) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Security Enhanced Mode](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_enhanced_security) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Redacted Log Files](https://docs.pingcap.com/tidb/stable/log-redaction) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
## Data import and export

| Data import and export | 8.1 | 7.5 | 7.1 | 6.5 | 6.1 | 5.4 | 5.3 | 5.2 | 5.1 |
|---|---|---|---|---|---|---|---|---|---|
| [Fast import using TiDB Lightning](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-overview) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Fast import using the `IMPORT INTO` statement](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-import-into) | Y | Y | N | N | N | N | N | N | N |
| mydumper logical dumper | Deprecated | Deprecated | Deprecated | Deprecated | Deprecated | Deprecated | Deprecated | Deprecated | Deprecated |
| [Dumpling logical dumper](https://docs.pingcap.com/tidb/stable/dumpling-overview) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Transactional `LOAD DATA`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-data) [^5] | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Database migration toolkit (DM)](https://docs.pingcap.com/tidb/stable/migration-overview) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [TiDB Binlog](https://docs.pingcap.com/tidb/stable/tidb-binlog/tidb-binlog-overview) [^6] | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Change data capture (CDC)](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview) | Y | Y | Y | Y | Y | Y | Y | Y | Y |
| [Stream data to Amazon S3, GCS, Azure Blob Storage, and NFS through TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-sink-to-cloud-storage) | Y | Y | Y | E | N | N | N | N | N |
| [TiCDC supports bidirectional replication between two TiDB clusters](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-bidirectional-replication) | Y | Y | Y | Y | N | N | N | N | N |
| [TiCDC OpenAPI v2](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-open-api-v2) | Y | Y | Y | N | N | N | N | N | N |
| [DM](https://docs.pingcap.com/tidb/stable/dm/dm-overview) supports migrating MySQL 8.0 | Y | E | E | E | E | N | N | N | N |
