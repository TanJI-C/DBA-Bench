# 2.1 upgrade caveats and downgrade limitation

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-2.1-ga.md`
- Source Title: `TiDB 2.1 GA Release Notes`
- Source Heading Path: `TiDB 2.1 GA Release Notes > Upgrade caveat`
- Source Line Ranges: `265-274`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `upgrade`, `downgrade`, `ddl`, `rolling-update`, `compatibility`, `warning`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0044_7af9f7df97`
- Source ID: `tidb-docs-8.1:releases/release-2.1-ga.md#upgrade-caveat`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3d3cc3d10460109de008465f79138785cf336fd5a01a5b1d22cd5ba82229ce4b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-2.1-ga#upgrade-caveat
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-2.1-ga.md

## Retrieval Guidance

- Use When: Use this chunk when searching TiDB 2.1 GA upgrade limitations, downgrade support, rolling update constraints, or DDL-related upgrade caveats.
- Retrieval Keywords: TiDB 2.1 upgrade caveat, does not support downgrading to v2.0.x or earlier, new storage engine, Parallel DDL, rolling update, clusters with TiDB version earlier than 2.0.1 cannot upgrade to 2.1 using rolling update, Stop the cluster and upgrade to 2.1 directly, Roll update to 2.0.1 or later 2.0.x versions, upgrade from TiDB 2.0.6 or earlier, ongoing DDL operation, Add Index
- Follow-up Guidance: The chunk lists two upgrade paths for clusters earlier than 2.0.1 and notes checking for ongoing DDL operations such as Add Index before rolling update from 2.0.6 or earlier.
- Classification Note: This is a self-managed TiDB release-notes warning chunk because it states downgrade restrictions and upgrade caveats involving Parallel DDL, rolling update compatibility, and ongoing DDL operations.

## Official Source Content

## Upgrade caveat

- TiDB 2.1 does not support downgrading to v2.0.x or earlier due to the adoption of the new storage engine

+ Parallel DDL is enabled in TiDB 2.1, so the clusters with TiDB version earlier than 2.0.1 cannot upgrade to 2.1 using rolling update. You can choose either of the following two options:

    - Stop the cluster and upgrade to 2.1 directly
    - Roll update to 2.0.1 or later 2.0.x versions, and then roll update to the 2.1 version

- If you upgrade from TiDB 2.0.6 or earlier to TiDB 2.1, check if there is any ongoing DDL operation, especially the time consuming `Add Index` operation, because the DDL operations slow down the upgrading process. If there is ongoing DDL operation, wait for the DDL operation finishes and then roll update.
