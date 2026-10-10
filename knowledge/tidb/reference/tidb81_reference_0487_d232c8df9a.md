# Compatibility changes for system variables in TiDB 5.4

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-5.4.0.md`
- Source Title: `TiDB 5.4 Release Notes`
- Source Heading Path: `TiDB 5.4 Release Notes > Compatibility changes > System variables`
- Source Line Ranges: `32-100`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `tikv`
- Topic Tags: `system-variables`, `compatibility`, `upgrade`, `configuration`, `statistics`, `stale-read`, `index-merge`, `top-sql`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0487_d232c8df9a`
- Source ID: `tidb-docs-8.1:releases/release-5.4.0.md#system-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8e40eb23a7332bfe85271dd29689d6766c4dcfc8c5a5b6a2e5048ce21cc5fb1d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-5.4.0#system-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-5.4.0.md

## Retrieval Guidance

- Use When: Use this chunk when the user asks about TiDB 5.4 system variable additions or modifications, especially upgrade-related default changes and statistics, stale read, Index Merge, paging, Top SQL, or store limit behavior.
- Retrieval Keywords: System variables, tidb_enable_column_tracking, tidb_enable_paging, IndexLookUp, IndexLookup, Limit, unified read pool, tidb_enable_top_sql, tidb_persist_analyze_options, ANALYZE configuration persistence, tidb_read_staleness, tidb_regard_null_as_point, tidb_stats_load_sync_wait, tidb_stats_load_pseudo_timeout, tidb_backoff_lock_fast, tidb_enable_index_merge, tidb_store_limit, default value changed from OFF to ON, only supports global configuration
- Follow-up Guidance: This chunk includes upgrade-specific behavior for tidb_enable_index_merge, distinguishing clusters upgraded from versions earlier than v4.0.0, from v4.0.0 or later, and newly created clusters of v5.4.0 and later.
- Classification Note: This is a reference chunk because it tabulates TiDB 5.4 system variables with change type and descriptions, including newly added variables and modified defaults or scope.

## Official Source Content

### System variables

<table>
<thead>
  <tr>
    <th>Variable name</th>
    <th>Change type</th>
    <th>Description</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_enable_column_tracking-new-in-v540"><code>tidb_enable_column_tracking</code></a></td>
    <td>Newly added</td>
    <td>Controls whether to allow TiDB to collect <code>PREDICATE COLUMNS</code>. The default value is <code>OFF.</code></td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_enable_paging-new-in-v540"><code>tidb_enable_paging</code></a></td>
    <td>Newly added</td>
    <td>Controls whether to use the method of paging to send coprocessor requests in <code>IndexLookUp</code> operator. The default value is <code>OFF</code>.<br/>For read queries that use <code>IndexLookup</code> and <code>Limit</code> and that <code>Limit</code> cannot be pushed down to <code>IndexScan</code>, there might be high latency for the read queries and high CPU usage for TiKV's <code>unified read pool</code>. In such cases, because the <code>Limit</code> operator only requires a small set of data, if you set <code>tidb_enable_paging</code> to <code>ON</code>, TiDB processes less data, which reduces query latency and resource consumption.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_enable_top_sql-new-in-v540"><code>tidb_enable_top_sql</code></a></td>
    <td>Newly added</td>
    <td>Controls whether to enable the Top SQL feature. The default value is <code>OFF</code>.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_persist_analyze_options-new-in-v540"><code>tidb_persist_analyze_options</code></a></td>
    <td>Newly added</td>
    <td>Controls whether to enable the <a href="https://docs.pingcap.com/tidb/dev/statistics#persist-analyze-configurations">ANALYZE configuration persistence</a> feature. The default value is <code>ON</code>.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_read_staleness-new-in-v540"><code>tidb_read_staleness</code></a></td>
    <td>Newly added</td>
    <td>Controls the range of historical data that can be read in the current session. The default value is <code>0</code>.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_regard_null_as_point-new-in-v540"><code>tidb_regard_null_as_point</code></a></td>
    <td>Newly added</td>
    <td>Controls whether the optimizer can use a query condition including null equivalence as a prefix condition for index access.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_stats_load_sync_wait-new-in-v540"><code>tidb_stats_load_sync_wait</code></a></td>
    <td>Newly added</td>
    <td>Controls whether to enable the synchronously loading statistics feature. The default value <code>0</code> means that the feature is disabled and that the statistics is asynchronously loaded. When the feature is enabled, this variable controls the maximum time that SQL optimization can wait for synchronously loading statistics before timeout.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_stats_load_pseudo_timeout-new-in-v540"><code>tidb_stats_load_pseudo_timeout</code></a></td>
    <td>Newly added</td>
    <td>Controls when synchronously loading statistics reaches timeout, whether SQL fails (<code>OFF</code>) or falls back to using pseudo statistics (<code>ON</code>). The default value is <code>OFF</code>.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_backoff_lock_fast"><code>tidb_backoff_lock_fast</code></a></td>
    <td>Modified</td>
    <td>The default value is changed from <code>100</code> to <code>10</code>.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_enable_index_merge-new-in-v40"><code>tidb_enable_index_merge</code></a></td>
    <td>Modified</td>
    <td>The default value is changed from <code>OFF</code> to <code>ON</code>.<ul><li>If you upgrade a TiDB cluster from versions earlier than v4.0.0 to v5.4.0 or later, this variable is <code>OFF</code> by default.</li><li>If you upgrade a TiDB cluster from v4.0.0 or later to v5.4.0 or later, this variable remains the same as before the upgrade.</li><li>For the newly created TiDB clusters of v5.4.0 and later, this variable is <code>ON</code> by default.</li></ul></td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_store_limit-new-in-v304-and-v40"><code>tidb_store_limit</code></a></td>
    <td>Modified</td>
    <td>Before v5.4.0, this variable can be configured at instance level and globally. Starting from v5.4.0, this variable only supports global configuration.</td>
  </tr>
</tbody>
</table>
