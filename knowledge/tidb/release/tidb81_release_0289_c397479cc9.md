# Compatibility changes for configuration file parameters

## Knowledge Metadata

- Knowledge Type: `release`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/releases/release-6.0.0-dmr.md`
- Source Title: `TiDB 6.0.0 Release Notes`
- Source Heading Path: `TiDB 6.0.0 Release Notes > Compatibility changes > Configuration file parameters`
- Source Line Ranges: `379-538`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `tiflash`, `dm`, `ticdc`, `lightning`
- Topic Tags: `compatibility`, `configuration`, `parameters`, `defaults`, `deprecation`, `system-behavior`, `import-mode`, `kafka-timeout`, `collation`, `compression`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_release_0289_c397479cc9`
- Source ID: `tidb-docs-8.1:releases/release-6.0.0-dmr.md#configuration-file-parameters`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8c72cbdb39c53f90565da34911677b07625b8650972fecde17cf0805a6aa9ade`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/releases/release-6.0.0-dmr#configuration-file-parameters
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/releases/release-6.0.0-dmr.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB 6.0.0 compatibility changes to configuration file parameters, including deleted, modified, and newly added settings across TiDB, TiKV, TiFlash, DM, and TiCDC.
- Retrieval Keywords: Configuration file parameters, Compatibility changes, TiDB 6.0.0 Release Notes, stmt-summary.enable, stmt-summary.enable-internal-query, stmt-summary.history-size, stmt-summary.max-sql-length, stmt-summary.max-stmt-count, stmt-summary.refresh-interval, statement summary tables, SQL variables, new_collations_enabled_on_first_bootstrap, backup.num-threads, raftstore.apply-max-batch-size, raftstore.raft-max-size-per-msg, raftstore.store-max-batch-size, readpool.unified.max-thread-count, rocksdb.enable-pipelined-write, rocksdb.max-background-flushes, rocksdb.max-background-jobs, profiles.default.dt_enable_logical_split, profiles.default.enable_elastic_threadpool, storage.format_version, pessimistic-txn.pessimistic-auto-commit, pessimistic-txn.in-memory, quota, foreground-cpu-time, foreground-write-bandwidth, foreground-read-bandwidth, max-delay-duration, profiles.default.dt_compression_method, profiles.default.dt_compression_level, loaders.<name>.import-mode, loaders.<name>.on-duplicate, dial-timeout, read-timeout, write-timeout, Kafka timeout, import-mode, new collation, Pipelined Commit
- Follow-up Guidance: The chunk also points to related official topics such as statement summary tables, TiDB, TiKV, and TiFlash configuration files, the DM task configuration file template advanced section, and TiCDC Kafka sink URI configuration.
- Classification Note: This is a release-note compatibility section that classifies configuration changes by component and change type, such as Deleted, Modified, and Newly added.

## Official Source Content

### Configuration file parameters

<table>
<thead>
  <tr>
    <th>Configuration file</th>
    <th>Configuration</th>
    <th>Change type</th>
    <th>Description</th>
  </tr>
</thead>
<tbody>
  <tr>
    <td>TiDB</td>
    <td>
      <code>stmt-summary.enable</code><br/>
      <code>stmt-summary.enable-internal-query</code><br/>
      <code>stmt-summary.history-size</code><br/>
      <code>stmt-summary.max-sql-length</code><br/>
      <code>stmt-summary.max-stmt-count</code><br/>
      <code>stmt-summary.refresh-interval</code>
    </td>
    <td>Deleted</td>
    <td>Configuration related to the <a href="https://docs.pingcap.com/tidb/dev/statement-summary-tables">statement summary tables</a>. All these configuration items are removed. You need to use SQL variables to control the statement summary tables.</td>
  </tr>
  <tr>
    <td>TiDB</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tidb-configuration-file#new_collations_enabled_on_first_bootstrap"><code>new_collations_enabled_on_first_bootstrap</code></a></td>
    <td>Modified</td>
    <td>Controls whether to enable support for the new collation. Since v6.0, the default value is changed from <code>false</code> to <code>true</code>. This configuration item only takes effect when the cluster is initialized for the first time. After the first bootstrap, you cannot enable or disable the new collation framework using this configuration item.</td>
  </tr>
  <tr>
    <td>TiKV</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tikv-configuration-file#num-threads-1"><code>backup.num-threads</code></a></td>
    <td>Modified</td>
    <td>The value range is modified to <code>[1, CPU]</code>.</td>
  </tr>
  <tr>
    <td>TiKV</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tikv-configuration-file#apply-max-batch-size"><code>raftstore.apply-max-batch-size</code></a></td>
    <td>Modified</td>
    <td>The maximum value is changed to <code>10240</code>.</td>
  </tr>
  <tr>
    <td>TiKV</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tikv-configuration-file#raft-max-size-per-msg"><code>raftstore.raft-max-size-per-msg</code></a></td>
    <td>Modified</td>
    <td>The minimum value is changed from <code>0</code> to larger than <code>0</code>.<br/>The maximum value is set to <code>3GB</code>.<br/>The unit is changed from <code>MB</code> to <code>KB|MB|GB</code>.</td>
  </tr>
  <tr>
    <td>TiKV</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tikv-configuration-file#store-max-batch-size"><code>raftstore.store-max-batch-size</code></a></td>
    <td>Modified</td>
    <td>The maximum value is set to <code>10240</code>.</td>
  </tr>
  <tr>
    <td>TiKV</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tikv-configuration-file#max-thread-count"><code>readpool.unified.max-thread-count</code></a></td>
    <td>Modified</td>
    <td>The adjustable range is changed to <code>[min-thread-count, MAX(4, CPU)]</code>.</td>
  </tr>
  <tr>
    <td>TiKV</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tikv-configuration-file#enable-pipelined-write"><code>rocksdb.enable-pipelined-write</code></a></td>
    <td>Modified</td>
    <td>The default value is changed from <code>true</code> to <code>false</code>. When this configuration is enabled, the previous Pipelined Write is used. When this configuration is disabled, the new Pipelined Commit mechanism is used.</td>
  </tr>
  <tr>
    <td>TiKV</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tikv-configuration-file#max-background-flushes"><code>rocksdb.max-background-flushes</code></a></td>
    <td>Modified</td>
    <td>When the number of CPU cores is 10, the default value is <code>3</code>.<br/>When the number of CPU cores is 8, the default value is <code>2</code>.</td>
  </tr>
  <tr>
    <td>TiKV</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tikv-configuration-file#max-background-jobs"><code>rocksdb.max-background-jobs</code></a></td>
    <td>Modified</td>
    <td>When the number of CPU cores is 10, the default value is <code>9</code>.<br/>When the number of CPU cores is 8, the default value is <code>7</code>.</td>
  </tr>
  <tr>
    <td>TiFlash</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tiflash-configuration#configure-the-tiflashtoml-file"><code>profiles.default.dt_enable_logical_split</code></a></td>
    <td>Modified</td>
    <td>Determines whether the segment of DeltaTree Storage Engine uses logical split. The default value is changed from <code>true</code> to <code>false</code>.</td>
  </tr>
  <tr>
    <td>TiFlash</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tiflash-configuration#configure-the-tiflashtoml-file"><code>profiles.default.enable_elastic_threadpool</code></a></td>
    <td>Modified</td>
    <td>Controls whether to enable the elastic thread pool. The default value is changed from <code>false</code> to <code>true</code>.</td>
  </tr>
  <tr>
    <td>TiFlash</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tiflash-configuration#configure-the-tiflashtoml-file"><code>storage.format_version</code></a></td>
    <td>Modified</td>
    <td>Controls the data validation feature of TiFlash. The default value is changed from <code>2</code> to <code>3</code>.<br/>When <code>format_version</code> is set to <code>3</code>, consistency check is performed on the read operations for all TiFlash data to avoid incorrect read due to hardware failure.<br/>Note that the new format version cannot be downgraded in place to versions earlier than v5.4.</td>
  </tr>
  <tr>
    <td>TiDB</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tidb-configuration-file#pessimistic-auto-commit-new-in-v600"><code>pessimistic-txn.pessimistic-auto-commit</code></a></td>
    <td>Newly added</td>
    <td>Determines the transaction mode that the auto-commit transaction uses when the pessimistic transaction mode is globally enabled (<code>tidb_txn_mode='pessimistic'</code>).</td>
  </tr>
  <tr>
    <td>TiKV</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tikv-configuration-file#in-memory-new-in-v600"><code>pessimistic-txn.in-memory</code></a></td>
    <td>Newly added</td>
    <td>Controls whether to enable the in-memory pessimistic lock. With this feature enabled, pessimistic transactions store pessimistic locks in TiKV memory as much as possible, instead of writing pessimistic locks to disks or replicating to other replicas. This improves the performance of pessimistic transactions; however, there is a low probability that a pessimistic lock will be lost, which might cause the pessimistic transaction to fail to commit. The default value is <code>true</code>.</td>
  </tr>
  <tr>
    <td>TiKV</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tikv-configuration-file#quota"><code>quota</code></a></td>
    <td>Newly added</td>
    <td>Add configuration items related to Quota Limiter, which limit the resources occupied by frontend requests. Quota Limiter is an experimental feature and is disabled by default. New quota-related configuration items are <code>foreground-cpu-time</code>, <code>foreground-write-bandwidth</code>, <code>foreground-read-bandwidth</code>, and <code>max-delay-duration</code>.</td>
  </tr>
  <tr>
    <td>TiFlash</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tiflash-configuration#configure-the-tiflashtoml-file"><code>profiles.default.dt_compression_method</code></a></td>
    <td>Newly added</td>
    <td>Specifies the compression algorithm for TiFlash. The optional values are <code>LZ4</code>, <code>zstd</code> and <code>LZ4HC</code>, all case insensitive. The default value is <code>LZ4</code>.</td>
  </tr>
  <tr>
    <td>TiFlash</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/tiflash-configuration#configure-the-tiflashtoml-file"><code>profiles.default.dt_compression_level</code></a></td>
    <td>Newly added</td>
    <td>Specifies the compression level of TiFlash. The default value is <code>1</code>.</td>
  </tr>
  <tr>
    <td>DM</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/task-configuration-file-full#task-configuration-file-template-advanced"><code>loaders.&lt;name&gt;.import-mode</code></a></td>
    <td>Newly added</td>
    <td>The import mode during the full import phase. Since v6.0, DM uses TiDB Lightning's TiDB-backend mode to import data during the full import phase; the previous Loader component is no longer used. This is an internal replacement and has no obvious impact on daily operations.<br/>The default value is set to <code>sql</code>, which means using tidb-backend mode. In some rare cases, tidb-backend might not be fully compatible. You can fall back to Loader mode by configuring this parameter to <code>loader</code>.</td>
  </tr>
  <tr>
    <td>DM</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/task-configuration-file-full#task-configuration-file-template-advanced"><code>loaders.&lt;name&gt;.on-duplicate</code></a></td>
    <td>Newly added</td>
    <td>Specifies the methods to resolve conflicts during the full import phase. The default value is <code>replace</code>, which means using the new data to replace the existing data.</td>
  </tr>
  <tr>
    <td>TiCDC</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/ticdc-sink-to-kafka#configure-sink-uri-for-kafka"><code>dial-timeout</code></a></td>
    <td>Newly added</td>
    <td>The timeout in establishing a connection with the downstream Kafka. The default value is <code>10s</code>.</td>
  </tr>
  <tr>
    <td>TiCDC</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/ticdc-sink-to-kafka#configure-sink-uri-for-kafka"><code>read-timeout</code></a></td>
    <td>Newly added</td>
    <td>The timeout in getting a response returned by the downstream Kafka. The default value is <code>10s</code>.</td>
  </tr>
  <tr>
    <td>TiCDC</td>
    <td><a href="https://docs.pingcap.com/tidb/dev/ticdc-sink-to-kafka#configure-sink-uri-for-kafka"><code>write-timeout</code></a></td>
    <td>Newly added</td>
    <td>The timeout in sending a request to the downstream Kafka. The default value is <code>10s</code>.</td>
  </tr>
</tbody>
</table>
