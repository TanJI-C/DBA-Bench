# PLAN REPLAYER CONTINUOUS CAPTURE enablement and results

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-plan-replayer.md`
- Source Title: `Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster`
- Source Heading Path: `Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster > Use `PLAN REPLAYER CONTINUOUS CAPTURE` | Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster > Use `PLAN REPLAYER CONTINUOUS CAPTURE` > Enable `PLAN REPLAYER CONTINUOUS CAPTURE` | Use PLAN REPLAYER to Save and Restore the On-Site Information of a Cluster > Use `PLAN REPLAYER CONTINUOUS CAPTURE` > View the capture results`
- Source Line Ranges: `293-303`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`
- Topic Tags: `plan replayer`, `continuous capture`, `system variable`, `sql digest`, `plan digest`, `results`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0066_74ebeaaf10`
- Source ID: `tidb-docs-8.1:sql-plan-replayer.md#use-plan-replayer-continuous-capture`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `181de9634ee5521f65d636910752b1e7943758c424c2e6bfcedc17304b482cf5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-plan-replayer#use-plan-replayer-continuous-capture
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-plan-replayer.md

## Retrieval Guidance

- Use When: Use this when you need the system variable and behavior description for enabling PLAN REPLAYER CONTINUOUS CAPTURE and understanding how its capture results are viewed.
- Retrieval Keywords: PLAN REPLAYER CONTINUOUS CAPTURE, tidb_enable_plan_replayer_continuous_capture, SQL DIGEST, PLAN DIGEST, system variable, set to ON, asynchronously records, does not record repeatedly, view the capture results
- Follow-up Guidance: The content says that viewing the capture results of PLAN REPLAYER CONTINUOUS CAPTURE is the same as viewing the capture results of PLAN REPLAYER CAPTURE.
- Classification Note: This is classified as diagnosis because it describes enabling continuous plan replayer recording by digest and checking the resulting captured records.

## Official Source Content

## Use `PLAN REPLAYER CONTINUOUS CAPTURE`

After `PLAN REPLAYER CONTINUOUS CAPTURE` is enabled, TiDB asynchronously records the applications' SQL statements with the `PLAN REPLAYER` method according to their `SQL DIGEST` and `PLAN DIGEST`. For SQL statements and execution plans that share the same DIGEST, `PLAN REPLAYER CONTINUOUS CAPTURE` does not record them repeatedly.
### Enable `PLAN REPLAYER CONTINUOUS CAPTURE`

`PLAN REPLAYER CONTINUOUS CAPTURE` is controlled by the system variable [`tidb_enable_plan_replayer_continuous_capture`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_plan_replayer_continuous_capture-new-in-v700). To enable `PLAN REPLAYER CONTINUOUS CAPTURE`, set the value of the system variable to `ON`.
### View the capture results

The method of viewing the capture results of `PLAN REPLAYER CONTINUOUS CAPTURE` is the same as that of [Viewing the capture results of `PLAN REPLAYER CAPTURE`](#view-the-capture-results).
