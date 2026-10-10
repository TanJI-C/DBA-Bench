# PD follower handling, plugin settings, port, and random seeds

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > pd_enable_follower_handle_region <span class="version-mark">New in v7.6.0</span> | System Variables > Variable reference > plugin_dir | System Variables > Variable reference > plugin_load | System Variables > Variable reference > port | System Variables > Variable reference > rand_seed1 | System Variables > Variable reference > rand_seed2`
- Source Line Ranges: `787-855`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `pd`
- Topic Tags: `system-variables`, `pd-follower`, `plugins`, `network-port`, `random-seed`, `experimental-feature`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0713_b9a817e38c`
- Source ID: `tidb-docs-8.1:system-variables.md#pd-enable-follower-handle-region-span-class-version-mark-new-in-v7-6-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f850d6191b11af2c1b30df4059a39e7cd39b52e450b2416c2a2641b9ab241883`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#pd-enable-follower-handle-region-span-class-version-mark-new-in-v7-6-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables for Active PD Follower Region handling, plugin directory or plugin loading, the MySQL protocol listening port, or RAND() seed variables.
- Retrieval Keywords: pd_enable_follower_handle_region, Active PD Follower, Region information, plugin_dir, plugin_load, port, tidb-server, MySQL protocol, rand_seed1, rand_seed2, RAND() SQL function
- Follow-up Guidance: The content notes that Active PD Follower is experimental and currently only applicable to requests for Region information, and that plugin_dir and plugin_load are not supported on Starter and Essential.
- Classification Note: This is reference content because it defines system variables and their scopes, defaults, support notes, and the exact behavior of PD follower handling, plugin settings, port, and random seed variables.

## Official Source Content

### pd_enable_follower_handle_region New in v7.6.0

> **Warning:**
>
> The [Active PD Follower](https://docs.pingcap.com/tidb/dev/tune-region-performance#use-the-active-pd-follower-feature-to-enhance-the-scalability-of-pds-region-information-query-service) feature is experimental. It is not recommended that you use it in the production environment. This feature might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

- Scope: GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- This variable controls whether to enable the Active PD Follower feature (currently only applicable to requests for Region information). When the value is `OFF`, TiDB only obtains Region information from the PD leader. When the value is `ON`, TiDB evenly distributes requests for Region information to all PD servers, and PD followers can also handle Region requests, thereby reducing the CPU pressure on the PD leader.
- Scenarios for enabling Active PD Follower:
    * In a cluster with a large number of Regions, the PD leader experiences high CPU pressure due to the increased overhead of handling heartbeats and scheduling tasks.
    * In a TiDB cluster with many TiDB instances, the PD leader experiences high CPU pressure due to a high concurrency of requests for Region information.
### plugin_dir

> **Note:**
>
> This variable is not supported on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- Indicates the directory to load plugins as specified by a command-line flag.
### plugin_load

> **Note:**
>
> This variable is not supported on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential).

- Scope: GLOBAL
- Persists to cluster: No, only applicable to the current TiDB instance that you are connecting to.
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Default value: ""
- Indicates the plugins to load when TiDB is started. These plugins are specified by a command-line flag and separated by commas.
### port

- Scope: NONE
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `4000`
- Range: `[0, 65535]`
- The port that the `tidb-server` is listening on when speaking the MySQL protocol.
### rand_seed1

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 2147483647]`
- This variable is used to seed the random value generator used in the `RAND()` SQL function.
- The behavior of this variable is MySQL compatible.
### rand_seed2

- Scope: SESSION
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `0`
- Range: `[0, 2147483647]`
- This variable is used to seed the random value generator used in the `RAND()` SQL function.
- The behavior of this variable is MySQL compatible.
