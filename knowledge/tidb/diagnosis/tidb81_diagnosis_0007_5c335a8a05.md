# Common Sysbench performance troubleshooting issues

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/benchmark/benchmark-tidb-using-sysbench.md`
- Source Title: `How to Test TiDB Using Sysbench`
- Source Heading Path: `How to Test TiDB Using Sysbench > Common issues | How to Test TiDB Using Sysbench > Common issues > TiDB and TiKV are both properly configured under high concurrency, why is the overall performance still low? | How to Test TiDB Using Sysbench > Common issues > Under high concurrency, why is the CPU utilization rate of TiKV still low? | How to Test TiDB Using Sysbench > Common issues > Given that TiKV has not yet reached the CPU usage bottleneck under high concurrency, why is TiDB's CPU utilization rate still low?`
- Source Line Ranges: `167-187`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiproxy`, `shared`
- Topic Tags: `troubleshooting`, `high-concurrency`, `proxy`, `haproxy`, `cpu-utilization`, `thread-pool`, `grafana`, `numa`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0007_5c335a8a05`
- Source ID: `tidb-docs-8.1:benchmark/benchmark-tidb-using-sysbench.md#common-issues`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `10c6787052b0c6bcb494613acc149abb92ae325de6840d16d233da0118c6b949`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/benchmark/benchmark-tidb-using-sysbench#common-issues
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/benchmark/benchmark-tidb-using-sysbench.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving official troubleshooting guidance for low overall Sysbench performance or low TiDB or TiKV CPU utilization under high concurrency.
- Retrieval Keywords: overall performance still low, proxy, HAproxy, nbproc, nbthread, cpu-map, TiKV Thread CPU monitor panel, Grafana, storage readpool, coprocessor, gRPC, NUMA architecture, max-procs
- Follow-up Guidance: The source says actual CPU usage can be observed through Grafana's TiKV Thread CPU monitor panel and discusses proxy parameters and NUMA-related `max-procs` settings as relevant factors.
- Classification Note: This is classified as diagnosis because the content is organized as common issues and explains possible causes of low throughput or low CPU utilization during high-concurrency Sysbench tests.

## Official Source Content

## Common issues
### TiDB and TiKV are both properly configured under high concurrency, why is the overall performance still low?

This issue often has things to do with the use of a proxy. You can add pressure on single TiDB server, sum each result up and compare the summed result with the result with proxy.

Take HAproxy as an example. The parameter `nbproc` can increase the number of processes it can start at most. Later versions of HAproxy also support `nbthread` and `cpu-map`. All of these can mitigate the negative impact of proxy use on performance.
### Under high concurrency, why is the CPU utilization rate of TiKV still low?

Although the overall CPU utilization rate is low for TiKV, the CPU utilization rate of some modules in the cluster might be high.

The maximum concurrency limits for other modules on TiKV, such as storage readpool, coprocessor, and gRPC, can be adjusted through the TiKV configuration file.

The actual CPU usage can be observed through Grafana's TiKV Thread CPU monitor panel. If there is a bottleneck on the modules, it can be adjusted by increasing the concurrency of the modules.
### Given that TiKV has not yet reached the CPU usage bottleneck under high concurrency, why is TiDB's CPU utilization rate still low?

CPU of NUMA architecture is used on some high-end equipment where cross-CPU access to remote memory will greatly reduce performance. By default, TiDB will use all CPUs of the server, and goroutine scheduling will inevitably lead to cross-CPU memory access.

Therefore, it is recommended to deploy *n* TiDBs (*n* is the number of NUMA CPUs) on the server of NUMA architecture, and meanwhile set the TiDB parameter `max-procs` to a value that is the same as the number of NUMA CPU cores.
