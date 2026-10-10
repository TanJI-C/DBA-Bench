# Compatibility changes in system variables for TiDB 7.1.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-7.1.0.md`
- Source Title: `TiDB 7.1.0 Release Notes`
- Source Heading Path: `TiDB 7.1.0 Release Notes > Compatibility changes > System variables`
- Source Line Ranges: `306-343`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tiflash`, `ticdc`
- Topic Tags: `system-variables`, `compatibility-changes`, `deprecated`, `deleted`, `modified`, `newly-added`, `ldap-authentication`, `plan-cache`, `optimizer`, `dxf`, `tiflash`, `ticdc`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0448_c81903aba5`
- Source ID: `tidb-docs-8.1:releases/release-7.1.0.md#system-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `06b0a1886e34e8b839e5fbaba88e38234eed7bd9536c08b48a7106ffaab38dfa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-7.1.0#system-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-7.1.0.md

## Retrieval Guidance

- Use When: Use this chunk when checking TiDB 7.1.0 system variable compatibility changes, including deprecated, deleted, modified, and newly added variables for TiDB, TiFlash, TiCDC, LDAP authentication, plan cache, optimizer, and DXF.
- Retrieval Keywords: TiDB 7.1.0 system variables compatibility changes, tidb_enable_tiflash_read_for_write_stmt, tidb_non_prepared_plan_cache_size, tidb_prepared_plan_cache_size, tidb_session_plan_cache_size, tidb_ddl_distribute_reorg, tidb_enable_dist_task, default_authentication_plugin, authentication_ldap_sasl, authentication_ldap_simple, tidb_load_based_replica_read_threshold, tidb_opt_enable_late_materialization, authentication_ldap_sasl_auth_method_name, authentication_ldap_sasl_bind_base_dn, authentication_ldap_sasl_bind_root_dn, authentication_ldap_sasl_bind_root_pwd, authentication_ldap_sasl_ca_path, authentication_ldap_sasl_init_pool_size, authentication_ldap_sasl_max_pool_size, authentication_ldap_sasl_server_host, authentication_ldap_sasl_server_port, authentication_ldap_sasl_tls, authentication_ldap_simple_auth_method_name, authentication_ldap_simple_bind_base_dn, authentication_ldap_simple_bind_root_dn, authentication_ldap_simple_bind_root_pwd, authentication_ldap_simple_ca_path, authentication_ldap_simple_init_pool_size, authentication_ldap_simple_max_pool_size, authentication_ldap_simple_server_host, authentication_ldap_simple_server_port, authentication_ldap_simple_tls, tidb_enable_non_prepared_plan_cache_for_dml, tidb_enable_row_level_checksum, tidb_opt_fix_control, tidb_plan_cache_invalidation_on_fresh_stats, tidb_plan_cache_max_plan_size, tidb_prefer_broadcast_join_by_exchange_data_size, Broadcast Hash Join, Shuffled Hash Join
- Follow-up Guidance: This chunk also states that `tidb_ddl_distribute_reorg` is renamed to `tidb_enable_dist_task`, and that `tidb_non_prepared_plan_cache_size` and `tidb_prepared_plan_cache_size` are deprecated in favor of `tidb_session_plan_cache_size`.
- Classification Note: The content is classified as a release note for TiDB because it is the TiDB 7.1.0 release section listing system variable compatibility changes and their exact change types.

## Official Source Content

| Variable name | Change type | Description |
|--------|------------------------------|------|
| [`tidb_enable_tiflash_read_for_write_stmt`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_tiflash_read_for_write_stmt-new-in-v630) | Deprecated | Changes the default value from `OFF` to `ON`. When [`tidb_allow_mpp = ON`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_allow_mpp-new-in-v50), the optimizer intelligently decides whether to push a query down to TiFlash based on the [SQL mode](https://docs.pingcap.com/tidb/stable/sql-mode) and the cost estimates of the TiFlash replica. |
| [`tidb_non_prepared_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_non_prepared_plan_cache_size) | Deprecated | Starting from v7.1.0, this system variable is deprecated. You can use [`tidb_session_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_session_plan_cache_size-new-in-v710) to control the maximum number of plans that can be cached. |
| [`tidb_prepared_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_prepared_plan_cache_size-new-in-v610) | Deprecated | Starting from v7.1.0, this system variable is deprecated. You can use [`tidb_session_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_session_plan_cache_size-new-in-v710) to control the maximum number of plans that can be cached. |
| `tidb_ddl_distribute_reorg` | Deleted | This variable is renamed to [`tidb_enable_dist_task`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_dist_task-new-in-v710). |
| [`default_authentication_plugin`](https://docs.pingcap.com/tidb/stable/system-variables#default_authentication_plugin) | Modified | Introduces two new value options: `authentication_ldap_sasl` and `authentication_ldap_simple`. |
| [`tidb_load_based_replica_read_threshold`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_load_based_replica_read_threshold-new-in-v700) | Modified | Takes effect starting from v7.1.0 and controls the threshold for triggering load-based replica read. Changes the default value from `"0s"` to `"1s"` after further tests. |
| [`tidb_opt_enable_late_materialization`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_enable_late_materialization-new-in-v700) | Modified | Changes the default value from `OFF` to `ON`, meaning that the TiFlash late materialization feature is enabled by default. |
| [`authentication_ldap_sasl_auth_method_name`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_sasl_auth_method_name-new-in-v710) | Newly added | Specifies the authentication method name in LDAP SASL authentication. |
| [`authentication_ldap_sasl_bind_base_dn`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_sasl_bind_base_dn-new-in-v710) | Newly added | Limits the search scope within the search tree in LDAP SASL authentication. If a user is created without `AS ...` clause, TiDB automatically searches the `dn` in LDAP server according to the user name. |
| [`authentication_ldap_sasl_bind_root_dn`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_sasl_bind_root_dn-new-in-v710) | Newly added | Specifies the `dn` used to login to the LDAP server to search users in LDAP SASL authentication. |
| [`authentication_ldap_sasl_bind_root_pwd`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_sasl_bind_root_pwd-new-in-v710) | Newly added | Specifies the password used to login to the LDAP server to search users in LDAP SASL authentication. |
| [`authentication_ldap_sasl_ca_path`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_sasl_ca_path-new-in-v710) | Newly added | Specifies the absolute path of the certificate authority file for StartTLS connections in LDAP SASL authentication. |
| [`authentication_ldap_sasl_init_pool_size`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_sasl_init_pool_size-new-in-v710) | Newly added | Specifies the initial connections in the connection pool to the LDAP server in LDAP SASL authentication. |
| [`authentication_ldap_sasl_max_pool_size`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_sasl_max_pool_size-new-in-v710) | Newly added | Specifies the maximum connections in the connection pool to the LDAP server in LDAP SASL authentication. |
| [`authentication_ldap_sasl_server_host`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_sasl_server_host-new-in-v710) | Newly added | Specifies the LDAP server host in LDAP SASL authentication. |
| [`authentication_ldap_sasl_server_port`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_sasl_server_port-new-in-v710) | Newly added | Specifies the LDAP server TCP/IP port number in LDAP SASL authentication. |
| [`authentication_ldap_sasl_tls`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_sasl_tls-new-in-v710) | Newly added | Specifies whether connections by the plugin to the LDAP server are protected with StartTLS in LDAP SASL authentication. |
| [`authentication_ldap_simple_auth_method_name`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_simple_auth_method_name-new-in-v710) | Newly added | Specifies the authentication method name in LDAP simple authentication. It only supports `SIMPLE`. |
| [`authentication_ldap_simple_bind_base_dn`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_simple_bind_base_dn-new-in-v710) | Newly added | Limits the search scope within the search tree in LDAP simple authentication. If a user is created without `AS ...` clause, TiDB will automatically search the `dn` in LDAP server according to the user name. |
| [`authentication_ldap_simple_bind_root_dn`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_simple_bind_root_dn-new-in-v710) | Newly added | Specifies the `dn` used to login to the LDAP server to search users in LDAP simple authentication. |
| [`authentication_ldap_simple_bind_root_pwd`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_simple_bind_root_pwd-new-in-v710) | Newly added | Specifies the password used to login to the LDAP server to search users in LDAP simple authentication. |
| [`authentication_ldap_simple_ca_path`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_simple_ca_path-new-in-v710) | Newly added | Specifies the absolute path of the certificate authority file for StartTLS connections in LDAP simple authentication. |
| [`authentication_ldap_simple_init_pool_size`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_simple_init_pool_size-new-in-v710) | Newly added | Specifies the initial connections in the connection pool to the LDAP server in LDAP simple authentication. |
| [`authentication_ldap_simple_max_pool_size`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_simple_max_pool_size-new-in-v710) | Newly added | Specifies the maximum connections in the connection pool to the LDAP server in LDAP simple authentication. |
| [`authentication_ldap_simple_server_host`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_simple_server_host-new-in-v710) | Newly added | Specifies the LDAP server host in LDAP simple authentication. |
| [`authentication_ldap_simple_server_port`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_simple_server_port-new-in-v710) | Newly added | Specifies the LDAP server TCP/IP port number in LDAP simple authentication. |
| [`authentication_ldap_simple_tls`](https://docs.pingcap.com/tidb/stable/system-variables#authentication_ldap_simple_tls-new-in-v710) | Newly added | Specifies whether connections by the plugin to the LDAP server are protected with StartTLS in LDAP simple authentication. |
| [`tidb_enable_dist_task`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_dist_task-new-in-v710) | Newly added | Controls whether to enable the Distributed eXecution Framework (DXF). After enabling the DXF, DDL, import, and other supported DXF tasks will be jointly completed by multiple TiDB nodes in the cluster. This variable was renamed from `tidb_ddl_distribute_reorg`. |
| [`tidb_enable_non_prepared_plan_cache_for_dml`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_non_prepared_plan_cache_for_dml-new-in-v710) | Newly added | Controls whether to enable the [Non-prepared plan cache](https://docs.pingcap.com/tidb/stable/sql-non-prepared-plan-cache) feature for DML statements. |
| [`tidb_enable_row_level_checksum`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_enable_row_level_checksum-new-in-v710) | Newly added | Controls whether to enable the TiCDC data integrity validation for single-row data feature.|
| [`tidb_opt_fix_control`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_opt_fix_control-new-in-v653-and-v710) | Newly added | This variable provides more fine-grained control over the optimizer and helps to prevent performance regression after upgrading caused by behavior changes in the optimizer. |
| [`tidb_plan_cache_invalidation_on_fresh_stats`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_plan_cache_invalidation_on_fresh_stats-new-in-v710) | Newly added | Controls whether to invalidate the plan cache automatically when statistics on related tables are updated. |
| [`tidb_plan_cache_max_plan_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_plan_cache_max_plan_size-new-in-v710) | Newly added | Controls the maximum size of a plan that can be cached in prepared or non-prepared plan cache. |
| [`tidb_prefer_broadcast_join_by_exchange_data_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_prefer_broadcast_join_by_exchange_data_size-new-in-v710) | Newly added | Controls whether to use the algorithm with the minimum overhead of network transmission. If this variable is enabled, TiDB estimates the size of the data to be exchanged in the network using `Broadcast Hash Join` and `Shuffled Hash Join` respectively, and then chooses the one with the smaller size. [`tidb_broadcast_join_threshold_count`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_count-new-in-v50) and [`tidb_broadcast_join_threshold_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_broadcast_join_threshold_size-new-in-v50) will not take effect after this variable is enabled. |
| [`tidb_session_plan_cache_size`](https://docs.pingcap.com/tidb/stable/system-variables#tidb_session_plan_cache_size-new-in-v710) | Newly added | Controls the maximum number of plans that can be cached. Prepared plan cache and non-prepared plan cache share the same cache. |
