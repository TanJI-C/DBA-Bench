# Security and telemetry changes in v6.6.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.6.0.md`
- Source Title: `TiDB 6.6.0 Release Notes`
- Source Heading Path: `TiDB 6.6.0 Release Notes > Feature details > Security | TiDB 6.6.0 Release Notes > Feature details > Telemetry`
- Source Line Ranges: `313-331`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tiflash`, `lightning`, `tiup`, `dashboard`, `tidb`
- Topic Tags: `tls-certificates`, `certificate-rotation`, `s3-access`, `aws-iam`, `session-tokens`, `telemetry`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0418_8560e0f1c9`
- Source ID: `tidb-docs-8.1:releases/release-6.6.0.md#security`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `159719f32e148430d429d769b21a4e22768b0601c9106e4ae052740767ff6757`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.6.0#security
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.6.0.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB v6.6.0 changes for TiFlash TLS certificate rotation, TiDB Lightning access to Amazon S3 with AWS IAM role keys and session tokens, or telemetry default status in TiDB, TiDB Dashboard, and TiUP.
- Retrieval Keywords: TiDB 6.6.0 Security, TiFlash automatic rotations of TLS certificates, automatic rotations of TiFlash TLS certificates, enable-tls-between-components, TiDB Lightning Amazon S3, AWS IAM role keys, session tokens, role's access keys + session tokens, import data from Amazon S3, Telemetry disabled by default, TiDB Dashboard telemetry, TiUP v1.11.3 telemetry, TiDB Release Timeline
- Follow-up Guidance: The source references documentation for enabling TLS between components, importing data from Amazon S3 with TiDB Lightning, the telemetry feature, and the TiDB Release Timeline.
- Classification Note: This is classified as release content because it summarizes security feature additions and telemetry default-state changes introduced in v6.6.0 and related TiUP behavior.

## Official Source Content

### Security

* TiFlash supports automatic rotations of TLS certificates [#5503](https://github.com/pingcap/tiflash/issues/5503) @[ywqzzy](https://github.com/ywqzzy)

    In v6.6.0, TiDB supports automatic rotations of TiFlash TLS certificates. For a TiDB cluster with encrypted data transmission between components enabled, when a TLS certificate of TiFlash expires and needs to be reissued with a new one, the new TiFlash TLS certificate can be automatically loaded without restarting the TiDB cluster. In addition, the rotation of a TLS certificate between components within a TiDB cluster does not affect the use of the TiDB cluster, which ensures high availability of the cluster.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/enable-tls-between-components).

* TiDB Lightning supports accessing Amazon S3 data via AWS IAM role keys and session tokens [#40750](https://github.com/pingcap/tidb/issues/40750) @[okJiang](https://github.com/okJiang)

    Before v6.6.0, TiDB Lightning only supports accessing S3 data via AWS IAM **user's access keys** (each access key consists of an access key ID and a secret access key) so you cannot use a temporary session token to access S3 data. Starting from v6.6.0, TiDB Lightning supports accessing S3 data via AWS IAM **role's access keys + session tokens** as well to improve the data security.

    For more information, see [documentation](https://docs.pingcap.com/tidb/stable/tidb-lightning/tidb-lightning-data-source#import-data-from-amazon-s3).
### Telemetry

- Starting from February 20, 2023, the [telemetry feature](https://docs.pingcap.com/tidb/stable/telemetry) is disabled by default in new versions of TiDB and TiDB Dashboard (including v6.6.0). If you upgrade from a previous version that uses the default telemetry configuration, the telemetry feature is disabled after the upgrade. For the specific versions, see [TiDB Release Timeline](https://docs.pingcap.com/tidb/stable/releases/release-timeline).
- Starting from v1.11.3, the telemetry feature is disabled by default in newly deployed TiUP. If you upgrade from a previous version of TiUP to v1.11.3 or a later version, the telemetry feature keeps the same status as before the upgrade.
