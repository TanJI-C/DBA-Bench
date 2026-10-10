# PD config set options and placement-rules command

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/pd-control.md`
- Source Title: `PD Control User Guide`
- Source Heading Path: `PD Control User Guide > Command > `config [show | set <option> <value> | placement-rules]` | PD Control User Guide > Command > `config [show | set <option> <value> | placement-rules]` > `config placement-rules [disable | enable | load | save | show | rule-group]``
- Source Line Ranges: `265-354`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`, `shared`
- Topic Tags: `pd-ctl`, `configuration`, `scheduling`, `replication`, `placement-rules`, `store-limit`, `cluster-version`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0134_4364cd9a9d`
- Source ID: `tidb-docs-8.1:pd-control.md#config-show-set-option-value-placement-rules`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4366197e25ddb844498e135bb2b60e557d49c0540805b7b4348da2001a67ba70`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/pd-control#config-show-set-option-value-placement-rules
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/pd-control.md

## Retrieval Guidance

- Use When: Use this chunk when looking for pd-ctl configuration options under `config set` or the `config placement-rules` subcommand for PD scheduling, replication, store limit, cluster version, or placement rules.
- Retrieval Keywords: config set region-schedule-limit, replica-schedule-limit, merge-schedule-limit, hot-region-schedule-limit, hot-region-cache-hits-threshold, tolerant-size-ratio, low-space-ratio, high-space-ratio, cluster-version, replication-mode, leader-schedule-policy, scheduler-max-waiting-operator, enable-remove-down-replica, enable-replace-offline-replica, enable-make-up-replica, enable-remove-extra-replica, enable-location-replacement, enable-debug-metrics, balance-tolerant-size, enable-placement-rules, store-limit-mode, store-limit-version, flow-round-by-digit, config placement-rules disable enable load save show rule-group, config set store-limit-version v2
- Follow-up Guidance: For `config placement-rules [disable | enable | load | save | show | rule-group]`, the source points to Configure placement rules for usage details.
- Classification Note: This is classified as configuration because the content lists PD configuration items and exact `config set` commands that control scheduling, replication, metrics, store limit, and placement-rules behavior.

## Official Source Content

```bash
    config set region-schedule-limit 2         // 2 tasks of Region scheduling at the same time at most
    ```

- `replica-schedule-limit` controls the number of tasks scheduling the replica at the same time. This value affects the scheduling speed when the node is down or removed. A larger value means a higher speed and setting the value to 0 closes the scheduling. Usually the replica scheduling has a large load, so do not set a too large value. Note that this configuration item is usually kept at the default value. If you want to change the value, you need to try a few values to see which one works best according to the real situation.

    ```bash
    config set replica-schedule-limit 4        // 4 tasks of replica scheduling at the same time at most
    ```

- `merge-schedule-limit` controls the number of Region Merge scheduling tasks. Setting the value to 0 closes Region Merge. Usually the Merge scheduling has a large load, so do not set a too large value. Note that this configuration item is usually kept at the default value. If you want to change the value, you need to try a few values to see which one works best according to the real situation.

    ```bash
    config set merge-schedule-limit 16       // 16 tasks of Merge scheduling at the same time at most
    ```

- `hot-region-schedule-limit` controls the hot Region scheduling tasks that are running at the same time. Setting its value to `0` means disabling the scheduling. It is not recommended to set a too large value. Otherwise, it might affect the system performance. Note that this configuration item is usually kept at the default value. If you want to change the value, you need to try a few values to see which one works best according to the real situation.

    ```bash
    config set hot-region-schedule-limit 4       // 4 tasks of hot Region scheduling at the same time at most
    ```

- `hot-region-cache-hits-threshold` is used to set the number of minutes required to identify a hot Region. PD can participate in the hotspot scheduling only after the Region is in the hotspot state for more than this number of minutes.

- `tolerant-size-ratio` controls the size of the balance buffer area. When the score difference between the leader or Region of the two stores is less than specified multiple times of the Region size, it is considered in balance by PD.

    ```bash
    config set tolerant-size-ratio 20        // Set the size of the buffer area to about 20 times of the average Region Size
    ```

- `low-space-ratio` controls the threshold value that is considered as insufficient store space. When the ratio of the space occupied by the node exceeds the specified value, PD tries to avoid migrating data to the corresponding node as much as possible. At the same time, PD mainly schedules the remaining space to avoid using up the disk space of the corresponding node.

    ```bash
    config set low-space-ratio 0.9              // Set the threshold value of insufficient space to 0.9
    ```

- `high-space-ratio` controls the threshold value that is considered as sufficient store space. This configuration takes effect only when `region-score-formula-version` is set to `v1`. When the ratio of the space occupied by the node is less than the specified value, PD ignores the remaining space and mainly schedules the actual data volume.

    ```bash
    config set high-space-ratio 0.5             // Set the threshold value of sufficient space to 0.5
    ```

- `cluster-version` is the version of the cluster, which is used to enable or disable some features and to deal with the compatibility issues. By default, it is the minimum version of all normally running TiKV nodes in the cluster. You can set it manually only when you need to roll it back to an earlier version.

    ```bash
    config set cluster-version 1.0.8              // Set the version of the cluster to 1.0.8
    ```

- `replication-mode` controls the replication mode of Regions in the dual data center scenario. See [Enable the DR Auto-Sync mode](https://docs.pingcap.com/tidb/stable/two-data-centers-in-one-city-deployment#enable-the-dr-auto-sync-mode) for details.

- `leader-schedule-policy` is used to select the scheduling strategy for the leader. You can schedule the leader according to `size` or `count`.

- `scheduler-max-waiting-operator` is used to control the number of waiting operators in each scheduler.

- `enable-remove-down-replica` is used to enable the feature of automatically deleting DownReplica. When you set it to `false`, PD does not automatically clean up the downtime replicas.

- `enable-replace-offline-replica` is used to enable the feature of migrating OfflineReplica. When you set it to `false`, PD does not migrate the offline replicas.

- `enable-make-up-replica` is used to enable the feature of making up replicas. When you set it to `false`, PD does not add replicas for Regions without sufficient replicas.

- `enable-remove-extra-replica` is used to enable the feature of removing extra replicas. When you set it to `false`, PD does not remove extra replicas for Regions with redundant replicas.

- `enable-location-replacement` is used to enable the isolation level checking. When you set it to `false`, PD does not increase the isolation level of a Region replica through scheduling.

- `enable-debug-metrics` is used to enable the metrics for debugging. When you set it to `true`, PD enables some metrics such as `balance-tolerant-size`.

- `enable-placement-rules` is used to enable placement rules, which is enabled by default in v5.0 and later versions.

- `store-limit-mode` is used to control the mode of limiting the store speed. The optional modes are `auto` and `manual`. In `auto` mode, the stores are automatically balanced according to the load (deprecated).

- `store-limit-version` controls the version of the store limit formula. In v1 mode, you can manually modify the `store limit` to limit the scheduling speed of a single TiKV. The v2 mode is an experimental feature. It is not recommended that you use it in the production environment. In v2 mode, you do not need to manually set the `store limit` value, as PD dynamically adjusts it based on the capability of TiKV snapshots. For more details, refer to [Principles of store limit v2](https://docs.pingcap.com/tidb/stable/configure-store-limit#principles-of-store-limit-v2).

    ```bash
    config set store-limit-version v2       // using store limit v2
    ```

- PD rounds the lowest digits of the flow number, which reduces the update of statistics caused by the changes of the Region flow information. This configuration item is used to specify the number of lowest digits to round for the Region flow information. For example, the flow `100512` will be rounded to `101000` because the default value is `3`. This configuration replaces `trace-region-flow`.

- For example, set the value of `flow-round-by-digit` to `4`:

    ```bash
    config set flow-round-by-digit 4
    ```
#### `config placement-rules [disable | enable | load | save | show | rule-group]`

For the usage of `config placement-rules [disable | enable | load | save | show | rule-group]`, see [Configure placement rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules#configure-rules).
