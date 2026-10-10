# Feature enhancements in TiKV and TiDB Dashboard

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.14.md`
- Source Title: `TiDB 4.0.14 Release Notes`
- Source Heading Path: `TiDB 4.0.14 Release Notes > Feature enhancements`
- Source Line Ranges: `24-35`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `dashboard`
- Topic Tags: `metric`, `s3-compatible storage`, `oidc sso`, `debug api`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0170_533a3181dc`
- Source ID: `tidb-docs-8.1:releases/release-4.0.14.md#feature-enhancements`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `29069f5261f91536b7848e1b9f56eb04be3cc3e03d7be127dd2e03d71bd85c55`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.14#feature-enhancements
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.14.md

## Retrieval Guidance

- Use When: Use this chunk when searching for new feature enhancements in TiDB 4.0.14 related to TiKV metrics, BR S3-compatible storage support, OIDC SSO, or the TiDB Dashboard Debug API.
- Retrieval Keywords: Feature enhancements, TiKV pending metric, pending PD heartbeats, slow PD threads, virtual-host addressing mode, BR support the S3-compatible storage, OIDC SSO, Okta, Auth0, TiDB Dashboard, Debug API, common TiDB and PD internal APIs, advanced debugging
- Follow-up Guidance: The chunk notes that OIDC-compatible SSO services such as Okta and Auth0 can be set for TiDB Dashboard login without entering the SQL password.
- Classification Note: This is classified as a release feature section because the official content lists newly added capabilities in TiKV and TiDB Dashboard.

## Official Source Content

## Feature enhancements

+ TiKV

    - Add a metric `pending` to monitor the number of pending PD heartbeats, which helps locate the issue of slow PD threads [#10008](https://github.com/tikv/tikv/pull/10008)
    - Support using the virtual-host addressing mode to make BR support the S3-compatible storage [#10242](https://github.com/tikv/tikv/pull/10242)

+ TiDB Dashboard

    - Support OIDC SSO. By setting the OIDC-compatible SSO services (such as Okta and Auth0), users can log into TiDB Dashboard without entering the SQL password. [#960](https://github.com/pingcap/tidb-dashboard/pull/960)
    - Add the **Debug API** UI, which is an alternative method to the command line to call several common TiDB and PD internal APIs for advanced debugging [#927](https://github.com/pingcap/tidb-dashboard/pull/927)
