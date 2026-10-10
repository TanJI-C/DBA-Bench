# PD Control config show and set scheduling options

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-control.md`
- Source Title: `PD Control User Guide`
- Source Heading Path: `PD Control User Guide > Command > `config [show | set <option> <value> | placement-rules]``
- Source Line Ranges: `124-264`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tidb`, `tikv`
- Topic Tags: `config`, `scheduling`, `replication`, `placement-rules`, `region-merge`, `store-timeouts`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0133_7150238865`
- Source ID: `tidb-docs-8.1:pd-control.md#config-show-set-option-value-placement-rules`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66b8196501a5e65ee3df65928c274e9ff07547da750ae95a3fccee0fecf4339e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-control#config-show-set-option-value-placement-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-control.md

## Retrieval Guidance

- Use When: Use this chunk when looking for PD Control `config show` or `config set` syntax and the meanings of scheduling, replication, merge, key type, or store timeout options.
- Retrieval Keywords: config [show | set <option> <value> | placement-rules], config show, config show all, config show replication, config show cluster-version, config set, max-snapshot-count, max-pending-peer-count, max-merge-region-size, max-merge-region-keys, split-merge-interval, enable-one-way-merge, enable-cross-table-merge, key-type, region-score-formula-version, patrol-region-interval, max-store-down-time, max-store-preparing-time, leader-schedule-limit, region-schedule-limit, enable-placement-rules
- Follow-up Guidance: The chunk includes example `config set` commands and explains what each option controls, including `cluster-version` as the current minimum version of TiKV nodes in the cluster.
- Classification Note: This chunk is classified as configuration because the official content focuses on viewing and modifying PD scheduling and replication configuration through PD Control.

## Official Source Content

### `config [show | set <option> <value> | placement-rules]`

Use this command to view or modify the configuration information.

Usage:

```bash
>> config show                                // Display the config information of the scheduling
{
  "replication": {
    "enable-placement-rules": "true",
    "isolation-level": "",
    "location-labels": "",
    "max-replicas": 3,
    "strictly-match-label": "false"
  },
  "schedule": {
    "enable-cross-table-merge": "true",
    "high-space-ratio": 0.7,
    "hot-region-cache-hits-threshold": 3,
    "hot-region-schedule-limit": 4,
    "leader-schedule-limit": 4,
    "leader-schedule-policy": "count",
    "low-space-ratio": 0.8,
    "max-merge-region-keys": 200000,
    "max-merge-region-size": 20,
    "max-pending-peer-count": 64,
    "max-snapshot-count": 64,
    "max-store-down-time": "30m0s",
    "merge-schedule-limit": 8,
    "patrol-region-interval": "10ms",
    "region-schedule-limit": 2048,
    "region-score-formula-version": "v2",
    "replica-schedule-limit": 64,
    "scheduler-max-waiting-operator": 5,
    "split-merge-interval": "1h0m0s",
    "tolerant-size-ratio": 0
  }
}
>> config show all                            // Display all config information
>> config show replication                    // Display the config information of replication
{
  "max-replicas": 3,
  "location-labels": "",
  "isolation-level": "",
  "strictly-match-label": "false",
  "enable-placement-rules": "true"
}

>> config show cluster-version                // Display the current version of the cluster, which is the current minimum version of TiKV nodes in the cluster and does not correspond to the binary version.
"5.2.2"
```

- `max-snapshot-count` controls the maximum number of snapshots that a single store receives or sends out at the same time. The scheduler is restricted by this configuration to avoid taking up normal application resources. When you need to improve the speed of adding replicas or balancing, increase this value.

    ```bash
    config set max-snapshot-count 64  // Set the maximum number of snapshots to 64
    ```

- `max-pending-peer-count` controls the maximum number of pending peers in a single store. The scheduler is restricted by this configuration to avoid producing a large number of Regions without the latest log in some nodes. When you need to improve the speed of adding replicas or balancing, increase this value. Setting it to 0 indicates no limit.

    ```bash
    config set max-pending-peer-count 64  // Set the maximum number of pending peers to 64
    ```

- `max-merge-region-size` controls the upper limit on the size of Region Merge (the unit is MiB). When `regionSize` exceeds the specified value, PD does not merge it with the adjacent Region. Setting it to 0 indicates disabling Region Merge.

    ```bash
    config set max-merge-region-size 16 // Set the upper limit on the size of Region Merge to 16 MiB
    ```

- `max-merge-region-keys` controls the upper limit on the key count of Region Merge. When `regionKeyCount` exceeds the specified value, PD does not merge it with the adjacent Region.

    ```bash
    config set max-merge-region-keys 50000 // Set the upper limit on keyCount to 50000
    ```

- `split-merge-interval` controls the interval between the `split` and `merge` operations on a same Region. This means the newly split Region won't be merged within a period of time.

    ```bash
    config set split-merge-interval 24h  // Set the interval between `split` and `merge` to one day
    ```

- `enable-one-way-merge` controls whether PD only allows a Region to merge with the next Region. When you set it to `false`, PD allows a Region to merge with the adjacent two Regions.

    ```bash
    config set enable-one-way-merge true  // Enables one-way merging.
    ```

- `enable-cross-table-merge` is used to enable the merging of cross-table Regions. When you set it to `false`, PD does not merge the Regions from different tables. This option only works when key type is "table".

    ```bash
    config set enable-cross-table-merge true  // Enable cross table merge.
    ```

- `key-type` specifies the key encoding type used for the cluster. The supported options are ["table", "raw", "txn"], and the default value is "table".
    - If no TiDB instance exists in the cluster, `key-type` will be "raw" or "txn", and PD is allowed to merge Regions across tables regardless of the `enable-cross-table-merge` setting.
    - If any TiDB instance exists in the cluster, `key-type` should be "table". Whether PD can merge Regions across tables is determined by `enable-cross-table-merge`. If `key-type` is "raw", placement rules do not work.

    ```bash
    config set key-type raw  // Enable cross table merge.
    ```

- `region-score-formula-version` controls the version of the Region score formula. The value options are `v1` and `v2`. The version 2 of the formula helps to reduce redundant balance Region scheduling in some scenarios, such as taking TiKV nodes online or offline.

    ```bash
    config set region-score-formula-version v2
    ```

- `patrol-region-interval` controls the execution frequency that `replicaChecker` checks the health status of Regions. A shorter interval indicates a higher execution frequency. Generally, you do not need to adjust it.

    ```bash
    config set patrol-region-interval 10ms // Set the execution frequency of replicaChecker to 10ms
    ```

- `max-store-down-time` controls the time that PD decides the disconnected store cannot be restored if exceeded. If PD does not receive heartbeats from a store within the specified period of time, PD adds replicas in other nodes.

    ```bash
    config set max-store-down-time 30m  // Set the time within which PD receives no heartbeats and after which PD starts to add replicas to 30 minutes
    ```

- `max-store-preparing-time` controls the maximum waiting time for the store to go online. During the online stage of a store, PD can query the online progress of the store. When the specified time is exceeded, PD assumes that the store has been online and cannot query the online progress of the store again. But this does not prevent Regions from transferring to the new online store. In most scenarios, you do not need to adjust this parameter.

    The following command specifies that the maximum waiting time for the store to go online is 4 hours.

    ```bash
    config set max-store-preparing-time 4h
    ```

- `leader-schedule-limit` controls the number of tasks scheduling the leader at the same time. This value affects the speed of leader balance. A larger value means a higher speed and setting the value to 0 closes the scheduling. Usually the leader scheduling has a small load, and you can increase the value in need.

    ```bash
    config set leader-schedule-limit 4         // 4 tasks of leader scheduling at the same time at most
    ```

- `region-schedule-limit` controls the number of tasks of scheduling Regions at the same time. This value avoids too many Region balance operators being created. The default value is `2048` which is enough for all sizes of clusters, and setting the value to `0` closes the scheduling. Usually, the Region scheduling speed is limited by `store-limit`, but it is recommended that you do not customize this value unless you know exactly what you are doing.
