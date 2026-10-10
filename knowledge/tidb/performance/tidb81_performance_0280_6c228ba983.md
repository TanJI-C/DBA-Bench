# OS performance analysis methods and tools

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tune-operating-system.md`
- Source Title: `Tune Operating System Performance`
- Source Heading Path: `Tune Operating System Performance | Tune Operating System Performance > Performance analysis methods | Tune Operating System Performance > Performance analysis methods > In 60 seconds | Tune Operating System Performance > Performance analysis methods > perf | Tune Operating System Performance > Performance analysis methods > BCC/bpftrace`
- Source Line Ranges: `5-43`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: none
- Topic Tags: `linux`, `os-tuning`, `performance-analysis`, `troubleshooting`, `perf`, `bpf`, `bcc`, `bpftrace`, `centos-7`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0280_6c228ba983`
- Source ID: `tidb-docs-8.1:tune-operating-system.md#tune-operating-system-performance`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4fdbf4321ef012d530cb87cfc1335c98afbcad04148bea117008a48cfa709283`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tune-operating-system#tune-operating-system-performance
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tune-operating-system.md

## Retrieval Guidance

- Use When: Use this chunk when looking for CentOS 7 operating system performance analysis methods and Linux tools for troubleshooting common performance issues.
- Retrieval Keywords: Tune Operating System Performance, Performance analysis methods, In 60 seconds, Linux Performance Analysis in 60,000 Milliseconds, uptime, dmesg | tail, vmstat 1, mpstat -P ALL 1, pidstat 1, iostat -xz 1, free -m, sar -n DEV 1, sar -n TCP,ETCP 1, top, perf, perf Examples, BCC, bpftrace, BPF Compiler Collection, Berkeley Packet Filter, CentOS 7.6, Brendan Gregg
- Follow-up Guidance: The source notes that system tuning should be based on performance analysis results and refers to man pages, perf Examples, and the BCC toolkit documentation for detailed usage.
- Classification Note: This is classified as performance for the shared component because it describes general Linux and CentOS 7 analysis methods such as perf and BPF-based tools rather than a single TiDB component.

## Official Source Content

# Tune Operating System Performance

This document introduces how to tune each subsystem of CentOS 7.

> **Note:**
>
> + The default configuration of the CentOS 7 operating system is suitable for most services running under moderate workloads. Adjusting the performance of a particular subsystem might negatively affect other subsystems. Therefore, before tuning the system, back up all the user data and configuration information.
> + Fully test all the changes in the test environment before applying them to the production environment.
## Performance analysis methods

System tuning must be based on the results of system performance analysis. This section lists common methods for performance analysis.
### In 60 seconds

[*Linux Performance Analysis in 60,000 Milliseconds*](http://www.brendangregg.com/Articles/Netflix_Linux_Perf_Analysis_60s.pdf) is published by the author Brendan Gregg and the Netflix Performance Engineering team. All tools used can be obtained from the official release of Linux. You can analyze outputs of the following list items to troubleshoot most common performance issues.

+ `uptime`
+ `dmesg | tail`
+ `vmstat 1`
+ `mpstat -P ALL 1`
+ `pidstat 1`
+ `iostat -xz 1`
+ `free -m`
+ `sar -n DEV 1`
+ `sar -n TCP,ETCP 1`
+ `top`

For detailed usage, see the corresponding `man` instructions.
### perf

perf is an important performance analysis tool provided by the Linux kernel, which covers hardware level (CPU/PMU, performance monitoring unit) features and software features (software counters, trace points). For detailed usage, see [perf Examples](http://www.brendangregg.com/perf.html#Background).
### BCC/bpftrace

Starting from CentOS 7.6, the Linux kernel has supported Berkeley Packet Filter (BPF). Therefore, you can choose proper tools to conduct an in-depth analysis based on the results in [In 60 seconds](#in-60-seconds). Compared with perf/ftrace, BPF provides programmability and smaller performance overhead. Compared with kprobe, BPF provides higher security and is more suitable for the production environments. For detailed usage of the BCC toolkit, see [BPF Compiler Collection (BCC)](https://github.com/iovisor/bcc/blob/master/README.md).
