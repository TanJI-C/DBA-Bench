# PD client connection and forwarding settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tikv-configuration-file.md`
- Source Title: `TiKV Configuration File`
- Source Heading Path: `TiKV Configuration File > pd | TiKV Configuration File > pd > `enable-forwarding` <span class="version-mark">New in v5.0.0</span> | TiKV Configuration File > pd > `endpoints` | TiKV Configuration File > pd > `retry-interval` | TiKV Configuration File > pd > `retry-log-every` | TiKV Configuration File > pd > `retry-max-count``
- Source Line Ranges: `588-618`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `pd-client`, `forwarding`, `endpoints`, `retry`, `network-isolation`, `availability`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0370_7d90809ae1`
- Source ID: `tidb-docs-8.1:tikv-configuration-file.md#pd`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e18655b974428d998d59e8c19995715033ac74991cf7cb9d271178154cd10ceb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tikv-configuration-file#pd
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tikv-configuration-file.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving TiKV PD client settings for `enable-forwarding`, PD `endpoints`, or retry behavior under possible network isolation or connection errors.
- Retrieval Keywords: pd.enable-forwarding, PD client, forward requests to the leader via the followers, possible network isolation, window of service unavailability, endpoints, 127.0.0.1:2379, retry-interval, retry-log-every, retry-max-count, disable the retry, release the limit on the number of retries
- Follow-up Guidance: The source includes the caution that using forwarding when isolation, interruption, or downtime cannot be accurately determined risks misjudgment and reduced availability and performance.
- Classification Note: This is classified as configuration content because it documents PD client connection and forwarding parameters, defaults, and retry semantics in the TiKV configuration file.

## Official Source Content

## pd
### `enable-forwarding` New in v5.0.0

+ Controls whether the PD client in TiKV forwards requests to the leader via the followers in the case of possible network isolation.
+ Default value: `false`
+ If the environment might have isolated network, enabling this parameter can reduce the window of service unavailability.
+ If you cannot accurately determine whether isolation, network interruption, or downtime has occurred, using this mechanism has the risk of misjudgment and causes reduced availability and performance. If network failure has never occurred, it is not recommended to enable this parameter.
### `endpoints`

+ The endpoints of PD. When multiple endpoints are specified, you need to separate them using commas.
+ Default value: `["127.0.0.1:2379"]`
### `retry-interval`

+ The interval for retrying the PD connection.
+ Default value: `"300ms"`
### `retry-log-every`

+ Specified the frequency at which the PD client skips reporting errors when the client observes errors. For example, when the value is `5`, after the PD client observes errors, the client skips reporting errors every 4 times and reports errors every 5th time.
+ To disable this feature, set the value to `1`.
+ Default value: `10`
### `retry-max-count`

+ The maximum number of times to retry to initialize PD connection
+ To disable the retry, set its value to `0`. To release the limit on the number of retries, set the value to `-1`.
+ Default value: `-1`
