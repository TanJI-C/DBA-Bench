# Diagnose slow timestamp acquisition and outdated Region metadata

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/analyze-slow-queries.md`
- Source Title: `Analyze Slow Queries`
- Source Heading Path: `Analyze Slow Queries > Analyze system issues > Other key stages are slow | Analyze Slow Queries > Analyze system issues > Other key stages are slow > Slow in getting timestamps | Analyze Slow Queries > Analyze system issues > Other key stages are slow > Outdated Region information`
- Source Line Ranges: `113-133`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `slow-queries`, `timestamps`, `wait-ts`, `region-miss`, `cop-backoff`, `pd-lookup`, `region-metadata`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0003_5a7950ef1b`
- Source ID: `tidb-docs-8.1:analyze-slow-queries.md#other-key-stages-are-slow`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `02bd478636c7950abce586c870dd849211742e7391be82668f4da23bb29c7bec`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/analyze-slow-queries#other-key-stages-are-slow
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/analyze-slow-queries.md

## Retrieval Guidance

- Use When: Use this chunk when a slow query appears to spend time in non-operator stages and you need the official indicators for slow timestamp acquisition or outdated Region information.
- Retrieval Keywords: Other key stages are slow, Slow in getting timestamps, Wait_TS, Query_time, Outdated Region information, regionMiss, Cop_backoff_regionMiss_total_times, Cop_backoff_rpcPD_total_times, rpcPD, PD again
- Follow-up Guidance: The content says that outdated Region information on the TiDB side can lead TiKV to return regionMiss, after which TiDB gets Region information from PD again and this appears in Cop_backoff fields.
- Classification Note: This is classified as diagnosis because the content provides slow log fields and error-related indicators to identify slow timestamp fetching and stale Region metadata as causes of slow queries.

## Official Source Content

### Other key stages are slow
#### Slow in getting timestamps

You can compare `Wait_TS` and `Query_time` in the slow log. The timestamps are prefetched, so generally `Wait_TS` should be low.

```
# Query_time: 0.0300000
...
# Wait_TS: 0.02500000
```
#### Outdated Region information

Region information on the TiDB side might be outdated. In this situation, TiKV might return the `regionMiss` error. Then TiDB gets the Region information from PD again, which is reflected in the `Cop_backoff` information. Both the failed times and the total duration are recorded.

```
# Cop_backoff_regionMiss_total_times: 200 Cop_backoff_regionMiss_total_time: 0.2 Cop_backoff_regionMiss_max_time: 0.2 Cop_backoff_regionMiss_max_addr: 127.0.0.1 Cop_backoff_regionMiss_avg_time: 0.2 Cop_backoff_regionMiss_p90_time: 0.2
# Cop_backoff_rpcPD_total_times: 200 Cop_backoff_rpcPD_total_time: 0.2 Cop_backoff_rpcPD_max_time: 0.2 Cop_backoff_rpcPD_max_addr: 127.0.0.1 Cop_backoff_rpcPD_avg_time: 0.2 Cop_backoff_rpcPD_p90_time: 0.2
```
