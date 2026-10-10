# BR backup auto-tune overview and enablement

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/br/br-auto-tune.md`
- Source Title: `Backup Auto-Tune`
- Source Heading Path: `Backup Auto-Tune <span class="version-mark">New in v5.4.0</span> | Backup Auto-Tune <span class="version-mark">New in v5.4.0</span> > Usage scenario | Backup Auto-Tune <span class="version-mark">New in v5.4.0</span> > Use auto-tune`
- Source Line Ranges: `5-37`
- Source Scope: `self_managed`
- Primary Component: `br`
- Related Components: `tikv`
- Topic Tags: `backup`, `auto-tune`, `thread-pool`, `ratelimit`, `concurrency`, `dynamic-configuration`, `upgrade-behavior`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0011_5adf7cc28b`
- Source ID: `tidb-docs-8.1:br/br-auto-tune.md#backup-auto-tune-span-class-version-mark-new-in-v5-4-0-span`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bec19227917566522f1ba64c903d908c34ceea9c988c9b7764db7fa9ba47e97d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/br/br-auto-tune#backup-auto-tune-span-class-version-mark-new-in-v5-4-0-span
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/br/br-auto-tune.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how BR backup auto-tune works by default, when it is enabled, and which TiKV settings or commands control backup speed and auto-tune behavior.
- Retrieval Keywords: Backup Auto-Tune, BR auto-tune, backup.enable-auto-tune, backup.num-threads, --ratelimit, concurrency, tikv-ctl modify-tikv-config -n backup.enable-auto-tune -v <true|false>, enabled by default, upgrade from v5.3.x to v5.4.0, offline cluster
- Follow-up Guidance: It also states that when --ratelimit is set, the br concurrency parameter is automatically adjusted to 1, and that backup.enable-auto-tune can be enabled or disabled dynamically without restarting the cluster.
- Classification Note: This is classified as configuration because the content centers on default enablement, manual enablement with backup.enable-auto-tune, dynamic modification with tikv-ctl, and related backup speed controls such as backup.num-threads and --ratelimit.

## Official Source Content

# Backup Auto-Tune New in v5.4.0

Before TiDB v5.4.0, when you back up data using Backup & Restore (BR), the number of threads used for backup makes up 75% of the logical CPU cores. Without a speed limit, the backup process can consume a lot of cluster resources, which has a considerable impact on the performance of the online cluster. Although you can reduce the impact of backup by adjusting the size of the thread pool, it is a tedious task to observe the CPU load and manually adjust the thread pool size.

To reduce the impact of backup tasks on the cluster, TiDB v5.4.0 introduces the auto-tune feature, which is enabled by default. When the cluster resource utilization is high, BR automatically limits the resources used by backup tasks and thereby reduces their impact on the cluster. The auto-tune feature is enabled by default.
## Usage scenario

If you want to reduce the impact of backup tasks on the cluster, you can enable the auto-tune feature. With this feature enabled, TiDB performs backup tasks as fast as possible without excessively affecting the cluster.

Alternatively, you can limit the backup speed by using the TiKV configuration item [`backup.num-threads`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#num-threads-1) or using the parameter `--ratelimit`. When `--ratelimit` is set, to avoid too many tasks causing the speed limit to fail, the `concurrency` parameter of br is automatically adjusted to `1`.
## Use auto-tune

The auto-tune feature is enabled by default, without additional configuration.

> **Note:**
>
> For clusters that upgrade from v5.3.x to v5.4.0 or later versions, the auto-tune feature is disabled by default. You need to manually enable it.

To manually enable the auto-tune feature, you need to set the TiKV configuration item [`backup.enable-auto-tune`](https://docs.pingcap.com/tidb/stable/tikv-configuration-file#enable-auto-tune-new-in-v540) to `true`.

TiKV supports dynamically configuring the auto-tune feature. You can enable or disable the feature without restarting your cluster. To dynamically enable or disable the auto-tune feature, run the following command:

```shell
tikv-ctl modify-tikv-config -n backup.enable-auto-tune -v <true|false>
```

When you perform backup tasks on an offline cluster, to speed up the backup, you can modify the value of `backup.num-threads` to a larger number using `tikv-ctl`.
