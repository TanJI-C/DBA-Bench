# Dynamic configuration for TiKV RocksDB options and PD shared settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dynamic-config.md`
- Source Title: `Modify Configuration Dynamically`
- Source Heading Path: `Modify Configuration Dynamically > Common Operations > Modify TiKV configuration dynamically | Modify Configuration Dynamically > Common Operations > Modify PD configuration dynamically`
- Source Line Ranges: `243-336`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`, `shared`
- Topic Tags: `dynamic-configuration`, `set-config`, `rocksdb`, `raftdb`, `etcd-persistence`, `shared-configuration`, `scheduling`, `replication`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0100_dfa31c7d86`
- Source ID: `tidb-docs-8.1:dynamic-config.md#modify-tikv-configuration-dynamically`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d6b70e6512a4ea9466f9f6073afa0aca86defbae06023add647cf270f09d1b36`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dynamic-config#modify-tikv-configuration-dynamically
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dynamic-config.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to change PD shared configuration dynamically with SET CONFIG, which PD items are supported, or how TiKV RocksDB and RaftDB dynamic option names use the {db-name} and {db-name}.{cf-name} prefixes.
- Retrieval Keywords: set config pd `log.level`='info', PD does not support the separate configuration for each instance, all PD instances share the same configuration, configuration in etcd will prevail, use backtick for reserved words, `schedule.leader-schedule-limit`, RocksDB {db-name}.{cf-name} prefix, rocksdb, raftdb, defaultcf, writecf, lockcf, raftcf, schedule.max-merge-region-size, schedule.max-snapshot-count, replication.max-replicas, replication.location-labels, pd-server.use-region-storage, replication-mode.dr-auto-sync.pause-region-split
- Follow-up Guidance: The content points to the TiKV Configuration File and PD Configuration File for detailed parameter descriptions.
- Classification Note: This is classified as configuration because the official content lists dynamically modifiable TiKV RocksDB option prefixes and PD configuration items, including shared PD settings persisted in etcd.

## Official Source Content

In the table above, parameters with the `{db-name}` or `{db-name}.{cf-name}` prefix are configurations related to RocksDB. The optional values of `db-name` are `rocksdb` and `raftdb`.

- When `db-name` is `rocksdb`, the optional values of `cf-name` are `defaultcf`, `writecf`, `lockcf`, and `raftcf`.
- When `db-name` is `raftdb`, the value of `cf-name` can be `defaultcf`.

For detailed parameter description, refer to [TiKV Configuration File](https://docs.pingcap.com/tidb/stable/tikv-configuration-file).
### Modify PD configuration dynamically

Currently, PD does not support the separate configuration for each instance. All PD instances share the same configuration.

You can modify the PD configurations using the following statement:

```sql
set config pd `log.level`='info';
```

If the modification is successful, `Query OK` is returned:

```sql
Query OK, 0 rows affected (0.01 sec)
```

If a configuration item is successfully modified, the result is persisted in etcd instead of in the configuration file; the configuration in etcd will prevail in the subsequent operations. The names of some configuration items might conflict with TiDB reserved words. For these configuration items, use backtick `` ` `` to enclose them. For example, `` `schedule.leader-schedule-limit` ``.

The following PD configuration items can be modified dynamically:

| Configuration item | Description |
| :--- | :--- |
| `log.level` | The log level |
| `cluster-version` | The cluster version |
| `schedule.max-merge-region-size` | Controls the size limit of `Region Merge` (in MiB) |
| `schedule.max-merge-region-keys` | Specifies the maximum numbers of the `Region Merge` keys |
| `schedule.patrol-region-interval` | Determines the frequency at which the checker inspects the health state of a Region |
| `schedule.split-merge-interval` | Determines the time interval of performing split and merge operations on the same Region |
| `schedule.max-snapshot-count` | Determines the maximum number of snapshots that a single store can send or receive at the same time |
| `schedule.max-pending-peer-count` | Determines the maximum number of pending peers in a single store |
| `schedule.max-store-down-time` | The downtime after which PD judges that the disconnected store cannot be recovered |
| `schedule.max-store-preparing-time` | Controls the maximum waiting time for the store to go online |
| `schedule.leader-schedule-policy` | Determines the policy of Leader scheduling |
| `schedule.leader-schedule-limit` | The number of Leader scheduling tasks performed at the same time |
| `schedule.region-schedule-limit` | The number of Region scheduling tasks performed at the same time |
| `schedule.replica-schedule-limit` | The number of Replica scheduling tasks performed at the same time |
| `schedule.merge-schedule-limit` | The number of the `Region Merge` scheduling tasks performed at the same time |
| `schedule.hot-region-schedule-limit` | The number of hot Region scheduling tasks performed at the same time |
| `schedule.hot-region-cache-hits-threshold` | Determines the threshold at which a Region is considered a hot spot |
| `schedule.high-space-ratio` | The threshold ratio below which the capacity of the store is sufficient |
| `schedule.low-space-ratio` | The threshold ratio above which the capacity of the store is insufficient |
| `schedule.tolerant-size-ratio` | Controls the `balance` buffer size|
| `schedule.enable-remove-down-replica` | Determines whether to enable the feature that automatically removes `DownReplica` |
| `schedule.enable-replace-offline-replica` | Determines whether to enable the feature that migrates `OfflineReplica` |
| `schedule.enable-make-up-replica` | Determines whether to enable the feature that automatically supplements replicas |
| `schedule.enable-remove-extra-replica` | Determines whether to enable the feature that removes extra replicas |
| `schedule.enable-location-replacement` | Determines whether to enable isolation level check |
| `schedule.enable-cross-table-merge` | Determines whether to enable cross-table merge |
| `schedule.enable-one-way-merge` | Enables one-way merge, which only allows merging with the next adjacent Region |
| `schedule.region-score-formula-version` | Controls the version of the Region score formula |
| `schedule.scheduler-max-waiting-operator` | Controls the number of waiting operators in each scheduler |
| `schedule.enable-debug-metrics` | Enables the metrics for debugging |
| `schedule.enable-joint-consensus` | Controls whether to use Joint Consensus for replica scheduling |
| `schedule.hot-regions-write-interval` | The time interval at which PD stores hot Region information |
| `schedule.hot-regions-reserved-days` | Specifies how many days the hot Region information is retained |
| `schedule.max-movable-hot-peer-size` | Controls the maximum Region size that can be scheduled for hot Region scheduling |
| `schedule.store-limit-version` | Controls the version of [store limit](https://docs.pingcap.com/tidb/stable/configure-store-limit) |
| `replication.max-replicas` | Sets the maximum number of replicas |
| `replication.location-labels` | The topology information of a TiKV cluster |
| `replication.enable-placement-rules` | Enables Placement Rules |
| `replication.strictly-match-label` | Enables the label check |
| `replication.isolation-level` | The minimum topological isolation level of a TiKV cluster |
| `pd-server.use-region-storage` | Enables independent Region storage |
| `pd-server.max-gap-reset-ts` | Sets the maximum interval of resetting timestamp (BR) |
| `pd-server.key-type` | Sets the cluster key type |
| `pd-server.metric-storage` | Sets the storage address of the cluster metrics |
| `pd-server.dashboard-address` | Sets the dashboard address |
| `pd-server.flow-round-by-digit` | Specifies the number of lowest digits to round for the Region flow information |
| `pd-server.min-resolved-ts-persistence-interval` | Determines the interval at which the minimum resolved timestamp is persistent to the PD |
| `pd-server.server-memory-limit` | The memory limit ratio for a PD instance |
| `pd-server.server-memory-limit-gc-trigger` | The threshold ratio at which PD tries to trigger GC |
| `pd-server.enable-gogc-tuner` | Controls whether to enable the GOGC Tuner |
| `pd-server.gc-tuner-threshold` | The maximum memory threshold ratio for tuning GOGC |
| `replication-mode.replication-mode` | Sets the backup mode |
| `replication-mode.dr-auto-sync.label-key` | Distinguishes different AZs and needs to match Placement Rules |
| `replication-mode.dr-auto-sync.primary` | The primary AZ |
| `replication-mode.dr-auto-sync.dr` | The disaster recovery (DR) AZ |
| `replication-mode.dr-auto-sync.primary-replicas` | The number of Voter replicas in the primary AZ |
| `replication-mode.dr-auto-sync.dr-replicas` | The number of Voter replicas in the disaster recovery (DR) AZ |
| `replication-mode.dr-auto-sync.wait-store-timeout` | The waiting time for switching to asynchronous replication mode when network isolation or failure occurs |
| `replication-mode.dr-auto-sync.wait-recover-timeout` | The waiting time for switching back to the `sync-recover` status after the network recovers |
| `replication-mode.dr-auto-sync.pause-region-split` | Controls whether to pause Region split operations in the `async_wait` and `async` statuses |

For detailed parameter description, refer to [PD Configuration File](https://docs.pingcap.com/tidb/stable/pd-configuration-file).
