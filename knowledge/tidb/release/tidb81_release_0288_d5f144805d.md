# Compatibility changes for system variables in TiDB 6.0.0

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.0.0-dmr.md`
- Source Title: `TiDB 6.0.0 Release Notes`
- Source Heading Path: `TiDB 6.0.0 Release Notes > Compatibility changes > System variables`
- Source Line Ranges: `288-378`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `system-variables`, `compatibility-changes`, `placement-rules`, `memory-quota`, `mutation-checker`, `prepared-statements`, `binding-cache`, `transaction-consistency`, `top-sql`, `table-cache`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0288_d5f144805d`
- Source ID: `tidb-docs-8.1:releases/release-6.0.0-dmr.md#system-variables`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b94a3401f648fe940aff1fd762d98aaea42b98d736ae7020035c98783f479162`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.0.0-dmr#system-variables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.0.0-dmr.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.0.0 system variable compatibility changes, including deleted variables, newly added variables, default values, and notes about placement rules, memory quota, mutation checker, Top SQL, transaction consistency, and table cache.
- Retrieval Keywords: TiDB 6.0.0 system variables, compatibility changes, placement_checks, tidb_placement_mode, tidb_enable_alter_placement, tidb_mem_quota_hashjoin, tidb_mem_quota_indexlookupjoin, tidb_mem_quota_indexlookupreader, tidb_mem_quota_mergejoin, tidb_mem_quota_sort, tidb_mem_quota_topn, tidb_mem_quota_query, tidb_enable_mutation_checker, tidb_ignore_prepared_cache_close_stmt, tidb_mem_quota_binding_cache, tidb_rc_read_check_ts, tidb_replica_read, tidb_sysdate_is_now, tidb_table_cache_lease, tidb_top_sql_max_meta_count, tidb_top_sql_max_time_series_count, tidb_txn_assertion_level, Placement Rules in SQL, Top SQL, table cache, SYSDATE NOW, mutation checker, assertion level
- Follow-up Guidance: The content states that tidb_rc_read_check_ts is not yet compatible with replica-read and that existing clusters upgraded from versions earlier than v6.0.0 have tidb_enable_mutation_checker and tidb_txn_assertion_level disabled by default.
- Classification Note: This is a release-note compatibility table for TiDB system variables in 6.0.0, covering deleted variables, replacements, newly added variables, defaults, and stated compatibility notes.

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
    <td><code>placement_checks</code></td>
    <td>Deleted</td>
    <td>Controls whether the DDL statement validates the placement rules specified by <a href="https://docs.pingcap.com/tidb/dev/placement-rules-in-sql">Placement Rules in SQL</a>. Replaced by <code>tidb_placement_mode</code>.</td>
  </tr>
  <tr>
    <td><code>tidb_enable_alter_placement</code></td>
    <td>Deleted</td>
    <td>Controls whether to enable <a href="https://docs.pingcap.com/tidb/dev/placement-rules-in-sql">placement rules in SQL</a>.</td>
  </tr>
  <tr>
    <td>
      <code>tidb_mem_quota_hashjoin</code><br/>
      <code>tidb_mem_quota_indexlookupjoin</code><br/>
      <code>tidb_mem_quota_indexlookupreader</code><br/>
      <code>tidb_mem_quota_mergejoin</code><br/>
      <code>tidb_mem_quota_sort</code><br/>
      <code>tidb_mem_quota_topn</code>
    </td>
    <td>Deleted</td>
    <td>Since v5.0, these variables have been replaced by <code>tidb_mem_quota_query</code> and removed from the <a href="https://docs.pingcap.com/tidb/dev/system-variables">system variables</a> document. To ensure compatibility, these variables were kept in source code. Since TiDB 6.0.0, these variables are removed from the code, too.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_enable_mutation_checker-new-in-v600"><code>tidb_enable_mutation_checker</code></a></td>
    <td>Newly added</td>
    <td>Controls whether to enable the mutation checker. The default value is <code>ON</code>. For existing clusters that upgrade from versions earlier than v6.0.0, the mutation checker is disabled by default.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_ignore_prepared_cache_close_stmt-new-in-v600"><code>tidb_ignore_prepared_cache_close_stmt</code></a></td>
    <td>Newly added</td>
    <td>Controls whether to ignore the command that closes Prepared Statement. The default value is <code>OFF</code>.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_mem_quota_binding_cache-new-in-v600"><code>tidb_mem_quota_binding_cache</code></a></td>
    <td>Newly added</td>
    <td>Sets the memory usage threshold for the cache holding binding. The default value is <code>67108864</code> (64 MiB).</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_placement_mode-new-in-v600"><code>tidb_placement_mode</code></a></td>
    <td>Newly added</td>
    <td>Controls whether DDL statements ignore the placement rules specified by <a href="https://docs.pingcap.com/tidb/dev/placement-rules-in-sql">Placement Rules in SQL</a>. The default value is <code>strict</code>, which means that DDL statements do not ignore placement rules.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_rc_read_check_ts-new-in-v600"><code>tidb_rc_read_check_ts</code></a></td>
    <td>Newly added</td>
    <td>
      <ul>
        <li>Optimizes read statement latency within a transaction. If read/write conflicts are more severe, turning this variable on will add additional overhead and latency, causing regressions in performance. The default value is <code>off</code>.</li>
        <li>This variable is not yet compatible with <a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_replica_read-new-in-v40">replica-read</a>. If a read request has <code>tidb_rc_read_check_ts</code> on, it might not be able to use replica-read. Do not turn on both variables at the same time.</li>
      </ul>
    </td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_sysdate_is_now-new-in-v600"><code>tidb_sysdate_is_now</code></a></td>
    <td>Newly added</td>
    <td>Controls whether the <code>SYSDATE</code> function can be replaced by the <code>NOW</code> function. This configuration item has the same effect as the MySQL option <a href="https://dev.mysql.com/doc/refman/8.0/en/server-options.html#option_mysqld_sysdate-is-now"><code>sysdate-is-now</code></a>. The default value is <code>OFF</code>.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_table_cache_lease-new-in-v600"><code>tidb_table_cache_lease</code></a></td>
    <td>Newly added</td>
    <td>Controls the lease time of <a href="https://docs.pingcap.com/tidb/dev/cached-tables">table cache</a>, in seconds. The default value is <code>3</code>.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_top_sql_max_meta_count-new-in-v600"><code>tidb_top_sql_max_meta_count</code></a></td>
    <td>Newly added</td>
    <td>Controls the maximum number of SQL statement types collected by <a href="https://docs.pingcap.com/tidb/dev/top-sql">Top SQL</a> per minute. The default value is <code>5000</code>.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_top_sql_max_time_series_count-new-in-v600"><code>tidb_top_sql_max_time_series_count</code></a></td>
    <td>Newly added</td>
    <td>Controls how many SQL statements that contribute the most to the load (that is, top N) can be recorded by <a href="https://docs.pingcap.com/tidb/dev/top-sql">Top SQL</a> per minute. The default value is <code>100</code>.</td>
  </tr>
  <tr>
    <td><a href="https://docs.pingcap.com/tidb/dev/system-variables#tidb_txn_assertion_level-new-in-v600"><code>tidb_txn_assertion_level</code></a></td>
    <td>Newly added</td>
    <td>Controls the assertion level. The assertion is a consistency check between data and indexes, which checks whether a key being written exists in the transaction commit process. By default, the check enables most of the check items, with almost no impact on performance. For existing clusters that upgrade from versions earlier than v6.0.0, the check is disabled by default.</td>
  </tr>
</tbody>
</table>
