# Tools and TiDB Ansible release changes in 4.0 beta

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-4.0.0-beta.md`
- Source Title: `TiDB 4.0 Beta Release Notes`
- Source Heading Path: `TiDB 4.0 Beta Release Notes > Tools | TiDB 4.0 Beta Release Notes > TiDB Ansible`
- Source Line Ranges: `103-114`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `lightning`, `tiflash`, `shared`
- Topic Tags: `lightning-password`, `package-checksum`, `systemd-version`, `log-directory`, `custom-port`, `tiflash-deployment`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0150_3f21c816b7`
- Source ID: `tidb-docs-8.1:releases/release-4.0.0-beta.md#tools`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `74a7cb27487d759822aa10efa6809dcef485ef0e3507e52f103b835db4e5acf6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-4.0.0-beta#tools
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-4.0.0-beta.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiDB 4.0 Beta changes for TiDB Lightning and TiDB Ansible involving downstream database password parameter support, package checksum check, systemd version requirement, log directory fixes, customized port fixes, or TiFlash deployment support.
- Retrieval Keywords: Tools, TiDB Lightning, parameter in the command-line tool, set the password of the downstream database, TiDB Ansible, checksum check in the package, downloaded package is incomplete, systemd-219-52 or later, log directory is incorrectly created, customized port of TiDB Lightning is invalid, deploying and maintaining TiFlash
- Follow-up Guidance: The chunk distinguishes one Tools change for TiDB Lightning and several TiDB Ansible changes including TiFlash support.
- Classification Note: This is a release-note chunk for self-managed tooling because the official content records TiDB Lightning and TiDB Ansible feature additions and fixes in TiDB 4.0 Beta.

## Official Source Content

## Tools

+ TiDB Lightning
    - Add the parameter in the command-line tool to set the password of the downstream database [#253](https://github.com/pingcap/tidb-lightning/pull/253)
## TiDB Ansible

+ Add checksum check in the package in case that the downloaded package is incomplete [#1002](https://github.com/pingcap/tidb-ansible/pull/1002)
+ Support checking the systemd version which must be `systemd-219-52` or later [#1020](https://github.com/pingcap/tidb-ansible/pull/1020) [#1074](https://github.com/pingcap/tidb-ansible/pull/1074)
+ Fix the issue that the log directory is incorrectly created when TiDB Lightning is started [#1103](https://github.com/pingcap/tidb-ansible/pull/1103)
+ Fix the issue that the customized port of TiDB Lightning is invalid [#1107](https://github.com/pingcap/tidb-ansible/pull/1107)
+ Support deploying and maintaining TiFlash [#1119](https://github.com/pingcap/tidb-ansible/pull/1119)
