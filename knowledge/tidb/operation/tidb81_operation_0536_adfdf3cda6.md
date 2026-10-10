# Update ctl tool version after cluster upgrade

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/upgrade-tidb-using-tiup.md`
- Source Title: `Upgrade TiDB Using TiUP`
- Source Heading Path: `Upgrade TiDB Using TiUP > FAQ > How to update the version of tools such as pd-ctl after upgrading the TiDB cluster?`
- Source Line Ranges: `365-373`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `pd`
- Topic Tags: `upgrade`, `tooling`, `ctl`, `pd-ctl`, `version-management`, `faq`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0536_adfdf3cda6`
- Source ID: `tidb-docs-8.1:upgrade-tidb-using-tiup.md#how-to-update-the-version-of-tools-such-as-pd-ctl-after-upgrading-the-tidb-cluster`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `89dacbabec99fa59799734eab589251c0f4739b839420d4db903f57ce38d0508`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup#how-to-update-the-version-of-tools-such-as-pd-ctl-after-upgrading-the-tidb-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/upgrade-tidb-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when asking how to update pd-ctl or similar tools to the corresponding version after upgrading a TiDB cluster with TiUP.
- Retrieval Keywords: tiup install ctl:v8.1.2, update pd-ctl after upgrading TiDB cluster, ctl component, tool version, install the ctl component of the corresponding version, pd-ctl
- Follow-up Guidance: The content shows upgrading the tool version by installing the ctl component of the corresponding version with TiUP.
- Classification Note: This is an operation-focused FAQ item for self-managed TiUP tooling version management related to the ctl component and pd-ctl.

## Official Source Content

### How to update the version of tools such as pd-ctl after upgrading the TiDB cluster?

You can upgrade the tool version by using TiUP to install the `ctl` component of the corresponding version:

```shell
tiup install ctl:v8.1.2
```
