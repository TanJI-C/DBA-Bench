# Hot region redistribution and region merge troubleshooting

## Knowledge Metadata

- Knowledge Type: `performance`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/pd-scheduling-best-practices.md`
- Source Title: `PD Scheduling Best Practices`
- Source Heading Path: `PD Scheduling Best Practices > PD scheduling in common scenarios > Hot regions are not evenly distributed | PD Scheduling Best Practices > PD scheduling in common scenarios > Region merge is slow`
- Source Line Ranges: `244-292`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tidb`, `tikv`
- Topic Tags: `hot-regions`, `traffic-analysis`, `split-region`, `scatter-range-scheduler`, `region-merge`, `merge-schedule-limit`, `cross-table-merge`, `placement-rules`, `version-dependent`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_performance_0062_ebed49a072`
- Source ID: `tidb-docs-8.1:best-practices/pd-scheduling-best-practices.md#hot-regions-are-not-evenly-distributed`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ec1f59bc6ab47a0e8dd22fa3f43248b89945c26b3f8a1d2c64cc4b9b48a0b955`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/pd-scheduling-best-practices#hot-regions-are-not-evenly-distributed
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/pd-scheduling-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when troubleshooting uneven hot region redistribution or slow region merge in PD scheduling.
- Retrieval Keywords: hot-region-schedule-limit, hot-region-cache-hits-threshold, split-region, scatter-range-scheduler, TiDB HTTP API, merge-schedule-limit, region-schedule-limit, max-merge-region-size, max-merge-region-keys, patrol-region-interval, split-region-on-table, key-type, enable-cross-table-merge, config set key-type txn, config set enable-cross-table-merge true, Placement Rules, approximate_keys, hot regions are not evenly distributed, region merge is slow
- Follow-up Guidance: The content also references the FAQ about modified TiKV or PD TOML configuration not taking effect when parameter changes do not work as expected.
- Classification Note: This is classified as performance because the content centers on redistributing hot regions, reducing bottlenecks, and speeding up merge scheduling through PD and TiKV scheduling-related parameters.

## Official Source Content

### Hot regions are not evenly distributed

Hot regions scheduling issues generally fall into the following categories:

- Hot regions can be observed via PD metrics, but the scheduling speed cannot keep up to redistribute hot regions in time.

    **Solution**: adjust `hot-region-schedule-limit` to a larger value, and reduce the limit quota of other schedulers to speed up hot regions scheduling. Or you can adjust `hot-region-cache-hits-threshold` to a smaller value to make PD more sensitive to traffic changes.

- Hotspot formed on a single region. For example, a small table is intensively scanned by a massive amount of requests. This can also be detected from PD metrics. Because you cannot actually distribute a single hotspot, you need to manually add a `split-region` operator to split such a region.

- The load of some nodes is significantly higher than that of other nodes from TiKV-related metrics, which becomes the bottleneck of the whole system. Currently, PD counts hotspots through traffic analysis only, so it is possible that PD fails to identify hotspots in certain scenarios. For example, when there are intensive point lookup requests for some regions, it might not be obvious to detect in traffic, but still the high QPS might lead to bottlenecks in key modules.

    **Solutions**: Firstly, locate the table where hot regions are formed based on the specific business. Then add a `scatter-range-scheduler` scheduler to make all regions of this table evenly distributed. TiDB also provides an interface in its HTTP API to simplify this operation. Refer to [TiDB HTTP API](https://github.com/pingcap/tidb/blob/release-8.1/docs/tidb_http_api.md) for more details.
### Region merge is slow

Similar to slow scheduling, the speed of region merge is most likely limited by the configurations of `merge-schedule-limit` and `region-schedule-limit`, or the region merge scheduler is competing with other schedulers. Specifically, the solutions are:

- If it is known from metrics that there are a large number of empty regions in the system, you can adjust `max-merge-region-size` and `max-merge-region-keys` to smaller values to speed up the merge. This is because the merge process involves replica migration, so the smaller the region to be merged, the faster the merge is. If the merge operators are already generated rapidly, to further speed up the process, you can set `patrol-region-interval` to `10ms` (the default value of this configuration item is `10ms` in v5.3.0 and later versions of TiDB). This makes region scanning faster at the cost of more CPU consumption.

- A lot of tables have been created and then emptied (including truncated tables). These empty Regions cannot be merged if the split table attribute is enabled. You can disable this attribute by adjusting the following parameters:

    - TiKV: Set `split-region-on-table` to `false`. You cannot modify the parameter dynamically.
    - PD: Use PD Control to set the parameters required by your cluster situation.

        - Suppose that your cluster has no TiDB instance, and the value of [`key-type`](https://docs.pingcap.com/tidb/stable/pd-control#config-show--set-option-value--placement-rules) is set to `raw` or `txn`. In this case, PD can merge Regions across tables, regardless of the value of `enable-cross-table-merge setting`. You can modify the `key-type` parameter dynamically.

        ```bash
        config set key-type txn
        ```

        - Suppose that your cluster has a TiDB instance, and the value of `key-type` is set to `table`. In this case, PD can merge Regions across tables only if the value of `enable-cross-table-merge` is set to `true`. You can modify the `key-type` parameter dynamically.

        ```bash
        config set enable-cross-table-merge true
        ```

        If the modification does not take effect, refer to [FAQ - Why the modified `toml` configuration for TiKV/PD does not take effect?](https://docs.pingcap.com/tidb/stable/faq/deploy-and-maintain-faq#why-the-modified-toml-configuration-for-tikvpd-does-not-take-effect).

        > **Note:**
        >
        > After enabling Placement Rules, properly switch the value of `key-type` to avoid the failure of decoding.

For v3.0.4 and v2.1.16 or earlier, the `approximate_keys` of regions are inaccurate in specific circumstances (most of which occur after dropping tables), which makes the number of keys break the constraints of `max-merge-region-keys`. To avoid this problem, you can adjust `max-merge-region-keys` to a larger value.
