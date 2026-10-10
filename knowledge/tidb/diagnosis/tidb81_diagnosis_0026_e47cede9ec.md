# Java troubleshooting tools and wrap-up

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/java-app-best-practices.md`
- Source Title: `Best Practices for Developing Java Applications with TiDB`
- Source Heading Path: `Best Practices for Developing Java Applications with TiDB > Misc | Best Practices for Developing Java Applications with TiDB > Misc > Troubleshooting tools | Best Practices for Developing Java Applications with TiDB > Misc > Troubleshooting tools > jstack | Best Practices for Developing Java Applications with TiDB > Misc > Troubleshooting tools > jmap & mat | Best Practices for Developing Java Applications with TiDB > Misc > Troubleshooting tools > trace | Best Practices for Developing Java Applications with TiDB > Misc > Troubleshooting tools > Flame graph | Best Practices for Developing Java Applications with TiDB > Conclusion | Best Practices for Developing Java Applications with TiDB > Need help?`
- Source Line Ranges: `371-414`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `tidb`
- Topic Tags: `java`, `troubleshooting`, `jstack`, `jmap`, `mat`, `trace`, `flame-graph`, `deadlock`, `cpu`, `memory`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0026_e47cede9ec`
- Source ID: `tidb-docs-8.1:develop/java-app-best-practices.md#misc`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e728f7e5476fd948d2656fb401b929f7c28d74cd6c768ba4fd2cae1eede053a2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/java-app-best-practices#misc
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/java-app-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when you need Java troubleshooting tool references for stuck processes, deadlocks, CPU-heavy threads, memory snapshots, dynamic tracing, or flame graphs around TiDB-connected applications.
- Retrieval Keywords: Troubleshooting tools, jstack, jstack pid, -m, stuck issue, deadlock issue, top -p $ PID -H, printf "%x\n" pid, jmap, mat, memory snapshot, MySQL connection objects, young GC issues, Java Flight Recorder, btrace, arthas trace, dynamic instrumentation, Flame graph, Java Flame Graphs Introduction: Fire For Everyone!
- Follow-up Guidance: The chunk also concludes that TiDB is highly compatible with the MySQL protocol, so most best practices for MySQL-based Java applications also apply to TiDB.
- Classification Note: This is classified as diagnosis content because the official text is centered on troubleshooting tools and investigation methods for Java application issues such as stuck threads, CPU use, memory analysis, and tracing.

## Official Source Content

## Misc

This section introduces some useful tools for Java to help you troubleshoot issues.
### Troubleshooting tools

Using the powerful troubleshooting tools of JVM is recommended when an issue occurs in your Java application and you do not know the application logic. Here are a few common tools:
#### jstack

[jstack](https://docs.oracle.com/javase/7/docs/technotes/tools/share/jstack.html) is similar to pprof/goroutine in Go, which can easily troubleshoot the process stuck issue.

By executing `jstack pid`, you can output the IDs and stack information of all threads in the target process. By default, only the Java stack is output. If you want to output the C++ stack in the JVM at the same time, add the `-m` option.

By using jstack multiple times, you can easily locate the stuck issue (for example, a slow query from application's view due to using Batch ExecutorType in Mybatis) or the application deadlock issue (for example, the application does not send any SQL statement because it is preempting a lock before sending it).

In addition, `top -p $ PID -H` or Java swiss knife are common methods to view the thread ID. Also, to locate the issue of "a thread occupies a lot of CPU resources and I don't know what it is executing", do the following steps:

- Use `printf "%x\n" pid` to convert the thread ID to hexadecimal.
- Go to the jstack output to find the stack information of the corresponding thread.
#### jmap & mat

Unlike pprof/heap in Go, [jmap](https://docs.oracle.com/javase/7/docs/technotes/tools/share/jmap.html) dumps the memory snapshot of the entire process (in Go, it is the sampling of the distributor), and then the snapshot can be analyzed by another tool [mat](https://www.eclipse.org/mat/).

Through mat, you can see the associated information and attributes of all objects in the process, and you can also observe the running status of the thread. For example, you can use mat to find out how many MySQL connection objects exist in the current application, and what is the address and status information of each connection object.

Note that mat only handles reachable objects by default. If you want to troubleshoot young GC issues, you can adjust mat configuration to view unreachable objects. In addition, for investigating the memory allocation of young GC issues (or a large number of short-lived objects), using Java Flight Recorder is more convenient.
#### trace

Online applications usually do not support modifying the code, but it is often desired that dynamic instrumentation is performed in Java to locate issues. Therefore, using btrace or arthas trace is a good option. They can dynamically insert trace code without restarting the application process.
#### Flame graph

Obtaining flame graphs in Java applications is tedious. For details, see [Java Flame Graphs Introduction: Fire For Everyone!](http://psy-lob-saw.blogspot.com/2017/02/flamegraphs-intro-fire-for-everyone.html).
## Conclusion

Based on commonly used Java components that interact with databases, this document describes the common problems and solutions for developing Java applications with TiDB. TiDB is highly compatible with the MySQL protocol, so most of the best practices for MySQL-based Java applications also apply to TiDB.
## Need help?

Ask the community on [Discord](https://discord.gg/DQZ2dy3cuc?utm_source=doc) or [Slack](https://slack.tidb.io/invite?team=tidb-community&channel=everyone&ref=pingcap-docs), or [submit a support ticket](https://docs.pingcap.com/tidb/stable/support).
