# Replica read and TiFlash execution variables

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/system-variables.md`
- Source Title: `System Variables`
- Source Heading Path: `System Variables > Variable reference > tidb_adaptive_closest_read_threshold <span class="version-mark">New in v6.3.0</span> | System Variables > Variable reference > tidb_allow_tiflash_cop <span class="version-mark">New in v7.3.0</span> | System Variables > Variable reference > tidb_allow_batch_cop <span class="version-mark">New in v4.0</span> | System Variables > Variable reference > tidb_allow_fallback_to_tikv <span class="version-mark">New in v5.0</span>`
- Source Line Ranges: `1035-1078`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`, `tiflash`
- Topic Tags: `replica-read`, `availability-zone`, `coprocessor`, `batchcop`, `mpp`, `fallback`, `cost-based-optimization`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0715_6fe6354662`
- Source ID: `tidb-docs-8.1:system-variables.md#tidb-adaptive-closest-read-threshold-span-class-version-mark-new-in-v6-3-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8ce57d435df1f8108724ea63cfd643b23ab2ac0d72d9c5edcba8025bb22eb7a3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/system-variables#tidb-adaptive-closest-read-threshold-span-class-version-mark-new-in-v6-3-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/system-variables.md

## Retrieval Guidance

- Use When: Use this chunk when looking up TiDB system variables that control closest-adaptive replica reads, TiFlash Cop or MPP plan generation, BatchCop behavior, or fallback from TiFlash to TiKV on execution failure.
- Retrieval Keywords: tidb_adaptive_closest_read_threshold, tidb_replica_read, closest-adaptive, same availability zone, leader replica, tidb_allow_tiflash_cop, TiFlash Cop, BatchCop, MPP, cost estimation, tidb_allow_batch_cop, coprocessor request to TiFlash, aggregation and join requests are sent in batches, tidb_allow_fallback_to_tikv, tiflash, TiKV, ErrTiFlashServerTimeout, SET_VAR
- Follow-up Guidance: The content states that when `tidb_allow_fallback_to_tikv` is set to `"tiflash"`, a TiFlash timeout error with code `ErrTiFlashServerTimeout` causes TiDB to retry the SQL statement with TiKV.
- Classification Note: This is a reference chunk because it lists TiDB execution and replica-read system variables with their scopes, defaults, ranges, and exact behavior for TiFlash and TiKV.

## Official Source Content

### tidb_adaptive_closest_read_threshold New in v6.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Integer
- Default value: `4096`
- Range: `[0, 9223372036854775807]`
- Unit: Bytes
- This variable is used to control the threshold at which the TiDB server prefers to send read requests to a replica in the same availability zone as the TiDB server when [`tidb_replica_read`](#tidb_replica_read-new-in-v40) is set to `closest-adaptive`. If the estimated result is higher than or equal to this threshold, TiDB prefers to send read requests to a replica in the same availability zone. Otherwise, TiDB sends read requests to the leader replica.
### tidb_allow_tiflash_cop New in v7.3.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): No
- Type: Boolean
- Default value: `OFF`
- When TiDB pushes computation tasks down to TiFlash, there are three methods (or protocols) to choose from: Cop, BatchCop, and MPP. Compared to Cop and BatchCop, the MPP protocol is more mature and offers better task and resource management. Therefore, it is recommended to use the MPP protocol.
    - `0` or `OFF`: the optimizer only generates plans using the TiFlash MPP protocol.
    - `1` or `ON`: the optimizer determines whether to use the Cop, BatchCop, or MPP protocol to generate execution plans based on the cost estimation.
### tidb_allow_batch_cop New in v4.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Type: Integer
- Default value: `1`
- Range: `[0, 2]`
- This variable is used to control how TiDB sends a coprocessor request to TiFlash. It has the following values:

    * `0`: Never send requests in batches
    * `1`: Aggregation and join requests are sent in batches
    * `2`: All coprocessor requests are sent in batches
### tidb_allow_fallback_to_tikv New in v5.0

- Scope: SESSION | GLOBAL
- Persists to cluster: Yes
- Applies to hint [SET_VAR](https://docs.pingcap.com/tidb/stable/optimizer-hints#set_varvar_namevar_value): Yes
- Default value: ""
- This variable is used to specify a list of storage engines that might fall back to TiKV. If the execution of a SQL statement fails due to a failure of the specified storage engine in the list, TiDB retries executing this SQL statement with TiKV. This variable can be set to "" or "tiflash". When this variable is set to "tiflash", if TiFlash returns a timeout error (error code: ErrTiFlashServerTimeout), TiDB retries executing this SQL statement with TiKV.
