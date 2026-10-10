# Statistics startup and opentracing configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-configuration-file.md`
- Source Title: `TiDB Configuration File`
- Source Heading Path: `TiDB Configuration File > performance > `force-init-stats` <span class="version-mark">New in v6.5.7 and v7.1.0</span> | TiDB Configuration File > opentracing | TiDB Configuration File > opentracing > `enable` | TiDB Configuration File > opentracing > `rpc-metrics` | TiDB Configuration File > opentracing.sampler | TiDB Configuration File > opentracing.sampler > `type` | TiDB Configuration File > opentracing.sampler > `param` | TiDB Configuration File > opentracing.sampler > `sampling-server-url` | TiDB Configuration File > opentracing.sampler > `max-operations` | TiDB Configuration File > opentracing.sampler > `sampling-refresh-interval` | TiDB Configuration File > opentracing.reporter | TiDB Configuration File > opentracing.reporter > `queue-size` | TiDB Configuration File > opentracing.reporter > `buffer-flush-interval` | TiDB Configuration File > opentracing.reporter > `log-spans` | TiDB Configuration File > opentracing.reporter > `local-agent-host-port``
- Source Line Ranges: `633-711`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `statistics`, `startup`, `optimizer`, `opentracing`, `sampling`, `reporting`, `rpc-metrics`, `performance-overhead`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0322_90cba0497b`
- Source ID: `tidb-docs-8.1:tidb-configuration-file.md#force-init-stats-span-class-version-mark-new-in-v6-5-7-and-v7-1-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `075a0178f5c5e85a1ba71073a2aab7656be4f931c265cb87a0ff9b64eb482307`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-configuration-file#force-init-stats-span-class-version-mark-new-in-v6-5-7-and-v7-1-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when the question is about TiDB startup waiting for statistics initialization or configuring opentracing sampler, reporter, and RPC metrics settings.
- Retrieval Keywords: force-init-stats, lite-init-stats, statistics initialization, pseudo statistics, opentracing, opentracing.enable, rpc-metrics, opentracing.sampler, type, param, sampling-server-url, max-operations, sampling-refresh-interval, opentracing.reporter, queue-size, buffer-flush-interval, log-spans, local-agent-host-port, jaeger-agent
- Follow-up Guidance: It also states that enabling opentracing causes some performance loss and that force-init-stats can prolong service startup when there are many tables and partitions and lite-init-stats is false.
- Classification Note: The content is classified as configuration because it defines TiDB configuration items for statistics startup behavior and opentracing options with defaults and value meanings.

## Official Source Content

### `force-init-stats` New in v6.5.7 and v7.1.0

+ Controls whether to wait for statistics initialization to finish before providing services during TiDB startup.
+ Default value: `false` for versions earlier than v7.2.0, `true` for v7.2.0 and later versions.
+ When the value of `force-init-stats` is `true`, TiDB needs to wait until statistics initialization is finished before providing services upon startup. Note that if there are a large number of tables and partitions and the value of [`lite-init-stats`](https://docs.pingcap.com/tidb/stable/tidb-configuration-file#lite-init-stats-new-in-v710) is `false`, setting `force-init-stats` to `true` might prolong the time it takes for TiDB to start providing services.
+ When the value of `force-init-stats` is `false`, TiDB can still provide services before statistics initialization is finished, but the optimizer uses pseudo statistics to make decisions, which might result in suboptimal execution plans.
## opentracing

Configuration items related to opentracing.
### `enable`

+ Enables opentracing to trace the call overhead of some TiDB components. Note that enabling opentracing causes some performance loss.
+ Default value: `false`
### `rpc-metrics`

+ Enables RPC metrics.
+ Default value: `false`
## opentracing.sampler

Configuration items related to opentracing.sampler.
### `type`

+ Specifies the type of the opentracing sampler. The string value is case-insensitive.
+ Default value: `"const"`
+ Value options: `"const"`, `"probabilistic"`, `"ratelimiting"`, `"remote"`
### `param`

+ The parameter of the opentracing sampler.
    - For the `const` type, the value can be `0` or `1`, which indicates whether to enable the `const` sampler.
    - For the `probabilistic` type, the parameter specifies the sampling probability, which can be a float number between `0` and `1`.
    - For the `ratelimiting` type, the parameter specifies the number of spans sampled per second.
    - For the `remote` type, the parameter specifies the sampling probability, which can be a float number between `0` and `1`.
+ Default value: `1.0`
### `sampling-server-url`

+ The HTTP URL of the jaeger-agent sampling server.
+ Default value: `""`
### `max-operations`

+ The maximum number of operations that the sampler can trace. If an operation is not traced, the default probabilistic sampler is used.
+ Default value: `0`
### `sampling-refresh-interval`

+ Controls the frequency of polling the jaeger-agent sampling policy.
+ Default value: `0`
## opentracing.reporter

Configuration items related to opentracing.reporter.
### `queue-size`

+ The queue size with which the reporter records spans in memory.
+ Default value: `0`
### `buffer-flush-interval`

+ The interval at which the reporter flushes the spans in memory to the storage.
+ Default value: `0`
### `log-spans`

+ Determines whether to print the log for all submitted spans.
+ Default value: `false`
### `local-agent-host-port`

+ The address at which the reporter sends spans to the jaeger-agent.
+ Default value: `""`
