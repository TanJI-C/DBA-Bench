# Bug fixes for TiCDC, DM, and TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.0.0.md`
- Source Title: `TiDB 7.0.0 Release Notes`
- Source Heading Path: `TiDB 7.0.0 Release Notes > Bug fixes`
- Source Line Ranges: `481-498`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `ticdc`, `dm`, `lightning`
- Topic Tags: `bug-fixes`, `changefeed`, `data-loss`, `checkpoint`, `kubernetes`, `google-cloud-storage`, `metadata`, `physical-import`, `logical-import`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0440_8b8f6bf54c`
- Source ID: `tidb-docs-8.1:releases/release-7.0.0.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dcaebc544903e24d7718c78bb1719a92954440a9573e493234208da3dbb16b65`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.0.0#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.0.0.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.0.0 bug fixes in TiCDC, DM, or TiDB Lightning involving changefeed restarts, checkpoint issues, downstream compatibility, Kubernetes upgrades, Google Cloud Storage, metadata tables, or import mode behavior.
- Retrieval Keywords: TiDB 7.0.0 Bug fixes TiCDC DM TiDB Lightning, restarting the changefeed might cause data loss or that the checkpoint cannot advance, #8242, DDL sink data race, #8238, changefeed in the stopped status might restart automatically, #8330, TiCDC server panics when all downstream Kafka servers are unavailable, #8523, data might be lost when the downstream is MySQL and the executed statement is incompatible with TiDB, #8453, rolling upgrade might cause TiCDC OOM or that the checkpoint gets stuck, #8329, graceful upgrade for TiCDC clusters fails on Kubernetes, #8484, DM worker node uses Google Cloud Storage request frequency limit, #8482, multiple DM tasks replicate the same downstream data, #8500, downstream metadata table breakpoint information same task ID, #8500, Physical Import Mode auto_random composite primary key, #41454, Logical Import Mode CONFIG permission for the target cluster, #41915
- Follow-up Guidance: The next chunk in the source file is the Contributors section for TiDB 7.0.0.
- Classification Note: This is a release-notes bug-fix chunk focused on TiCDC, DM, and TiDB Lightning items within the TiDB 7.0.0 Bug fixes section.

## Official Source Content

- Fix the issue that restarting the changefeed might cause data loss or that the checkpoint cannot advance [#8242](https://github.com/pingcap/tiflow/issues/8242) @[overvenus](https://github.com/overvenus)
        - Fix the data race issue in DDL sink [#8238](https://github.com/pingcap/tiflow/issues/8238) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that the changefeed in the `stopped` status might restart automatically [#8330](https://github.com/pingcap/tiflow/issues/8330) @[sdojjy](https://github.com/sdojjy)
        - Fix the issue that the TiCDC server panics when all downstream Kafka servers are unavailable [#8523](https://github.com/pingcap/tiflow/issues/8523) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that data might be lost when the downstream is MySQL and the executed statement is incompatible with TiDB [#8453](https://github.com/pingcap/tiflow/issues/8453) @[asddongmen](https://github.com/asddongmen)
        - Fix the issue that rolling upgrade might cause TiCDC OOM or that the checkpoint gets stuck [#8329](https://github.com/pingcap/tiflow/issues/8329) @[overvenus](https://github.com/overvenus)
        - Fix the issue that graceful upgrade for TiCDC clusters fails on Kubernetes [#8484](https://github.com/pingcap/tiflow/issues/8484) @[overvenus](https://github.com/overvenus)

    + TiDB Data Migration (DM)

        - Fix the issue that when a DM worker node uses Google Cloud Storage, due to too frequent breakpoints, the request frequency limit of Google Cloud Storage is reached and the DM worker cannot write the data into Google Cloud Storage, thus causing the full data to fail to load [#8482](https://github.com/pingcap/tiflow/issues/8482) @[maxshuang](https://github.com/maxshuang)
        - Fix the issue that when multiple DM tasks replicate the same downstream data at the same time and all use the downstream metadata table to record the breakpoint information, the breakpoint information of all tasks is written to the same metadata table and uses the same task ID [#8500](https://github.com/pingcap/tiflow/issues/8500) @[maxshuang](https://github.com/maxshuang)

    + TiDB Lightning

        - Fix the issue that when Physical Import Mode is used for importing data, if there is an `auto_random` column in the composite primary key of the target table, but the value of the column is not specified in the source data, TiDB Lightning does not generate data for the `auto_random` column automatically [#41454](https://github.com/pingcap/tidb/issues/41454) @[D3Hunter](https://github.com/D3Hunter)
        - Fix the issue that when Logical Import Mode is used for importing data, the import fails due to lack of the `CONFIG` permission for the target cluster [#41915](https://github.com/pingcap/tidb/issues/41915) @[lichunzhu](https://github.com/lichunzhu)
