# Mitigate TiDB OOM issues with GOMEMLIMIT

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/configure-memory-usage.md`
- Source Title: `TiDB Memory Control`
- Source Heading Path: `TiDB Memory Control > Others | TiDB Memory Control > Others > Mitigate OOM issues by configuring `GOMEMLIMIT``
- Source Line Ranges: `209-227`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: none
- Topic Tags: `oom`, `gomemlimit`, `gc`, `memory-limit`, `grafana`, `runtime-memory`, `version-specific`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0025_915348dc8f`
- Source ID: `tidb-docs-8.1:configure-memory-usage.md#others`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c5ceeab6b724b2ad8cd9db0f06c19e490de472d2c5ab0db947d0802b0faa227c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/configure-memory-usage#others
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/configure-memory-usage.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the documented `GOMEMLIMIT` mitigation for a specific TiDB OOM pattern where Grafana estimate-inuse is only about half of total memory before OOM.
- Retrieval Keywords: GOMEMLIMIT, GO 1.19, memory limit that triggers GC, v6.1.3 <= TiDB < v6.5.0, OOM issues, Grafana, TiDB-Runtime > Memory Usage > estimate-inuse, estimate-inuse, v6.1.2, v6.1.3, 40000 MiB
- Follow-up Guidance: The content states that for `v6.1.3 <= TiDB < v6.5.0`, manually setting `GOMEMLIMIT` can mitigate this typical OOM category and includes a test comparison with `GOMEMLIMIT` set to `40000 MiB`.
- Classification Note: This is classified as TiDB configuration content because it documents the `GOMEMLIMIT` environment variable, the affected TiDB version range, and the observed Grafana memory pattern associated with this OOM mitigation.

## Official Source Content

## Others
### Mitigate OOM issues by configuring `GOMEMLIMIT`

GO 1.19 introduces an environment variable [`GOMEMLIMIT`](https://pkg.go.dev/runtime@go1.19#hdr-Environment_Variables) to set the memory limit that triggers GC.

For v6.1.3 <= TiDB < v6.5.0, you can mitigate a typical category of OOM issues by manually setting `GOMEMLIMIT`. The typical category of OOM issues is: before OOM occurs, the estimated memory in use on Grafana occupies only half of the entire memory (TiDB-Runtime > Memory Usage > estimate-inuse), as shown in the following figure:

![normal OOM case example](/media/configure-memory-usage-oom-example.png)

To verify the performance of `GOMEMLIMIT`, a test is performed to compare the specific memory usage with and without `GOMEMLIMIT` configuration.

- In TiDB v6.1.2, the TiDB server encounters OOM (system memory: about 48 GiB) after the simulated workload runs for several minutes:

    ![v6.1.2 workload oom](/media/configure-memory-usage-612-oom.png)

- In TiDB v6.1.3, `GOMEMLIMIT` is set to 40000 MiB. It is found that the simulated workload runs stably for a long time, OOM does not occur in the TiDB server, and the maximum memory usage of the process is stable at around 40.8 GiB:

    ![v6.1.3 workload no oom with GOMEMLIMIT](/media/configure-memory-usage-613-no-oom.png)
