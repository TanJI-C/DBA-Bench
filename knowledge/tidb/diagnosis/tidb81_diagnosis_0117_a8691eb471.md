# TiFlash startup, replica availability, and region unavailable troubleshooting

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiflash/troubleshoot-tiflash.md`
- Source Title: `Troubleshoot a TiFlash Cluster`
- Source Heading Path: `Troubleshoot a TiFlash Cluster | Troubleshoot a TiFlash Cluster > TiFlash fails to start | Troubleshoot a TiFlash Cluster > TiFlash replica is always unavailable | Troubleshoot a TiFlash Cluster > Some queries return the `Region Unavailable` error`
- Source Line Ranges: `5-81`
- Source Scope: `self_managed`
- Primary Component: `tiflash`
- Related Components: `pd`, `tidb`, `tikv`, `tiup`
- Topic Tags: `startup`, `replica-availability`, `placement-rules`, `pd-ctl`, `disk-space`, `region-unavailable`, `load-balancing`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0117_a8691eb471`
- Source ID: `tidb-docs-8.1:tiflash/troubleshoot-tiflash.md#troubleshoot-a-tiflash-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d9f32236432d377d265216c404fdf6f8d4ef23e6e9081577a73f22d8e8fa201a`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiflash/troubleshoot-tiflash#troubleshoot-a-tiflash-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiflash/troubleshoot-tiflash.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting TiFlash startup failures, TiFlash replicas that stay unavailable, or queries that return the `Region Unavailable` error in a self-managed cluster.
- Retrieval Keywords: TiFlash fails to start, libnsl.so, RedHat Enterprise Linux 8, dnf install libnsl, ulimit -n 1000000, PD Control tool, pd-ctl, TiFlash replica is always unavailable, Placement Rules, config show replication, tiup ctl:nightly pd -u http://${pd-ip}:${pd-port} store, store.labels, engine tiflash, config placement-rules show, default: count, low-space-ratio, TiFlash-Summary, UpTime, Region Unavailable, load pressure, adding more TiFlash nodes
- Follow-up Guidance: If these startup checks do not resolve the issue, the source says to save the TiFlash log files and get support from PingCAP or the community.
- Classification Note: The content is classified as diagnosis because it provides checks and causes for startup failure, unavailable TiFlash replicas, placement rule and disk space issues, and `Region Unavailable` query errors.

## Official Source Content

# Troubleshoot a TiFlash Cluster

This section describes some commonly encountered issues when using TiFlash, the reasons, and the solutions.
## TiFlash fails to start

The issue might occur due to different reasons. It is recommended that you troubleshoot it following the steps below:

1. Check whether your system is RedHat Enterprise Linux 8.

    RedHat Enterprise Linux 8 does not have the `libnsl.so` system library. You can manually install it via the following command:

    ```shell
    dnf install libnsl
    ```

2. Check your system's `ulimit` parameter setting.

    ```shell
    ulimit -n 1000000
    ```

3. Use the PD Control tool to check whether there is any TiFlash instance that failed to go offline on the node (same IP and Port) and force the instance(s) to go offline. For detailed steps, refer to [Scale in a TiFlash cluster](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-in-a-tiflash-cluster).

If the above methods cannot resolve your issue, save the TiFlash log files and [get support](https://docs.pingcap.com/tidb/stable/support) from PingCAP or the community.
## TiFlash replica is always unavailable

This is because TiFlash is in an abnormal state caused by configuration errors or environment issues. Take the following steps to identify the faulty component:

1. Check whether PD enables the `Placement Rules` feature:

    ```shell
    echo 'config show replication' | /path/to/pd-ctl -u http://${pd-ip}:${pd-port}
    ```

    - If `true` is returned, go to the next step.
    - If `false` is returned, [enable the Placement Rules feature](https://docs.pingcap.com/tidb/stable/configure-placement-rules#enable-placement-rules) and go to the next step.

2. Check whether the TiFlash process is working correctly by viewing `UpTime` on the TiFlash-Summary monitoring panel.

3. Check whether the TiFlash proxy status is normal through `pd-ctl`.

    ```shell
    tiup ctl:nightly pd -u http://${pd-ip}:${pd-port} store
    ```

    The TiFlash proxy's `store.labels` includes information such as `{"key": "engine", "value": "tiflash"}`. You can check this information to confirm a TiFlash proxy.

4. Check whether the number of configured replicas is less than or equal to the number of TiKV nodes in the cluster. If not, PD cannot replicate data to TiFlash.

    ```shell
    tiup ctl:nightly pd -u http://${pd-ip}:${pd-port} config placement-rules show | grep -C 10 default
    ```

    Reconfirm the value of `default: count`.

    > **Note:**
    >
    > - When [Placement Rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules) are enabled and multiple rules exist, the previously configured [`max-replicas`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#max-replicas), [`location-labels`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#location-labels), and [`isolation-level`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#isolation-level) no longer take effect. To adjust the replica policy, use the interface related to Placement Rules.
    > - When [Placement Rules](https://docs.pingcap.com/tidb/stable/configure-placement-rules) are enabled and only one default rule exists, TiDB will automatically update this default rule when `max-replicas`, `location-labels`, or `isolation-level` configurations are changed.

5. Check whether the remaining disk space of the machine (where `store` of the TiFlash node is) is sufficient. By default, when the remaining disk space is less than 20% of the `store` capacity (which is controlled by the [`low-space-ratio`](https://docs.pingcap.com/tidb/stable/pd-configuration-file#low-space-ratio) parameter), PD cannot schedule data to this TiFlash node.
## Some queries return the `Region Unavailable` error

If the load pressure on TiFlash is too heavy and it causes that TiFlash data replication falls behind, some queries might return the `Region Unavailable` error.

In this case, you can balance the load pressure by adding more TiFlash nodes.
