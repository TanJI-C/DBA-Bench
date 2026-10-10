# Bug fixes for TiCDC and TiDB Lightning

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.5.6.md`
- Source Title: `TiDB 7.5.6 Release Notes`
- Source Heading Path: `TiDB 7.5.6 Release Notes > Bug fixes`
- Source Line Ranges: `126-137`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `ticdc`, `lightning`, `tikv`, `pd`
- Topic Tags: `bug-fixes`, `changefeed`, `kafka`, `avro`, `rename-table`, `checkpoint-ts`, `pd-scale-in`, `small-tables`, `log-desensitization`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0551_a14c52c6f3`
- Source ID: `tidb-docs-8.1:releases/release-7.5.6.md#bug-fixes`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d28156d379c0c8e90510efaa99e95b07b941cf3ea78dee4aa6ec654025a2eca6`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.5.6#bug-fixes
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.5.6.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 7.5.6 bug fixes for TiCDC or TiDB Lightning involving many small tables, Kafka Sarama message ordering, `RENAME TABLE` filtering, `--overwrite-checkpoint-ts`, Avro `default NULL`, PD scale-in connectivity, or Lightning log desensitization.
- Retrieval Keywords: TiDB 7.5.6 TiCDC bug fixes, enabling TiCDC many small tables might cause TiKV to restart, Sarama client out-of-order messages Kafka message order incorrect, TiCDC incorrect table names filtering during `RENAME TABLE`, goroutines leak after a changefeed is deleted, `changefeed pause` `--overwrite-checkpoint-ts` changefeed stuck, TiCDC replicating `default NULL` SQL statements Avro protocol errors, TiCDC fails to properly connect to PD after PD scale-in, TiDB Lightning logs are not properly desensitized
- Follow-up Guidance: This chunk also includes a TiDB Lightning fix for logs not being properly desensitized.
- Classification Note: The official content is a TiDB 7.5.6 release-note bug-fix section specifically for TiCDC and TiDB Lightning issues.

## Official Source Content

- Fix the issue that enabling TiCDC in scenarios with many small tables might cause TiKV to restart [#18142](https://github.com/tikv/tikv/issues/18142) @[hicqu](https://github.com/hicqu)
        - Fix the issue that after the default value of a newly added column in the upstream is changed from `NOT NULL` to `NULL`, the default values of that column in the downstream are incorrect [#12037](https://github.com/pingcap/tiflow/issues/12037) @[wk989898](https://github.com/wk989898)
        - Fix the issue that out-of-order messages resent by the Sarama client cause Kafka message order to be incorrect [#11935](https://github.com/pingcap/tiflow/issues/11935) @[3AceShowHand](https://github.com/3AceShowHand)
        - Fix the issue that TiCDC uses incorrect table names for filtering during `RENAME TABLE` operations [#11946](https://github.com/pingcap/tiflow/issues/11946) @[wk989898](https://github.com/wk989898)
        - Fix the issue that goroutines leak occurs after a changefeed is deleted [#11954](https://github.com/pingcap/tiflow/issues/11954) @[hicqu](https://github.com/hicqu)
        - Fix the issue that using the `--overwrite-checkpoint-ts` parameter in the `changefeed pause` command might cause the changefeed to be stuck [#12055](https://github.com/pingcap/tiflow/issues/12055) @[hongyunyan](https://github.com/hongyunyan)
        - Fix the issue that TiCDC reports errors when replicating `default NULL` SQL statements via the Avro protocol [#11994](https://github.com/pingcap/tiflow/issues/11994) @[wk989898](https://github.com/wk989898)
        - Fix the issue that TiCDC fails to properly connect to PD after PD scale-in [#12004](https://github.com/pingcap/tiflow/issues/12004) @[lidezhu](https://github.com/lidezhu)

    + TiDB Lightning

        - Fix the issue that logs are not properly desensitized [#59086](https://github.com/pingcap/tidb/issues/59086) @[GMHDBJD](https://github.com/GMHDBJD)
