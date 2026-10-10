# PD store status, scheduling, replicas, and cluster health FAQs

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/manage-cluster-faq.md`
- Source Title: `TiDB Cluster Management FAQs`
- Source Heading Path: `TiDB Cluster Management FAQs > PD management > What is the relationship between each status (Up, Disconnect, Offline, Down, Tombstone) of a TiKV store? | TiDB Cluster Management FAQs > PD management > What is the difference between the `leader-schedule-limit` and `region-schedule-limit` scheduling parameters in PD? | TiDB Cluster Management FAQs > PD management > Is the number of replicas in each region configurable? If yes, how to configure it? | TiDB Cluster Management FAQs > PD management > How to check the health status of the whole cluster when lacking command line cluster management tools? | TiDB Cluster Management FAQs > PD management > How to delete the monitoring data of a cluster node that is offline?`
- Source Line Ranges: `160-187`
- Source Scope: `self_managed`
- Primary Component: `pd`
- Related Components: `tikv`
- Topic Tags: `store-status`, `scheduling`, `replicas`, `cluster-health`, `monitoring`, `pd-ctl`, `offline-node`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0144_4d431adc84`
- Source ID: `tidb-docs-8.1:faq/manage-cluster-faq.md#what-is-the-relationship-between-each-status-up-disconnect-offline-down-tombstone-of-a-tikv-store`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1c4cec2298732ed4228339f7c053d5379a00e9718f4ae322e0d4385ccf2d9584`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/manage-cluster-faq#what-is-the-relationship-between-each-status-up-disconnect-offline-down-tombstone-of-a-tikv-store
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/manage-cluster-faq.md

## Retrieval Guidance

- Use When: Use this chunk when asking about TiKV store statuses, PD scheduling limits, region replica count configuration, checking overall cluster health with pd-ctl, or removing monitoring data for an offline node.
- Retrieval Keywords: Up, Disconnect, Offline, Down, Tombstone, TiKV store status, PD Control, pd-ctl, leader-schedule-limit, region-schedule-limit, max-replicas, config set max-replicas $num, config show all, conf/pd.yml, cluster health status, monitor, offline node, node_exporter, Prometheus configuration file
- Follow-up Guidance: The content says you can use pd-ctl or the monitor to determine whether the offline process is finished, and after the node is offline, manually stop the relevant services and delete the corresponding node_exporter data from the Prometheus configuration file.
- Classification Note: This is classified as PD operation content because it explains PD scheduling parameters, pd-ctl usage, replica configuration through PD, and cluster health checks related to TiKV store status.

## Official Source Content

### What is the relationship between each status (Up, Disconnect, Offline, Down, Tombstone) of a TiKV store?

For the relationship between each status, refer to [Relationship between each status of a TiKV store](https://docs.pingcap.com/tidb/stable/tidb-scheduling#information-collection).

You can use PD Control to check the status information of a TiKV store.
### What is the difference between the `leader-schedule-limit` and `region-schedule-limit` scheduling parameters in PD?

- The `leader-schedule-limit` scheduling parameter is used to balance the Leader number of different TiKV servers, affecting the load of query processing.
- The `region-schedule-limit` scheduling parameter is used to balance the replica number of different TiKV servers, affecting the data amount of different nodes.
### Is the number of replicas in each region configurable? If yes, how to configure it?

Yes. Currently, you can only update the global number of replicas. When started for the first time, PD reads the configuration file (conf/pd.yml) and uses the max-replicas configuration in it. If you want to update the number later, use the pd-ctl configuration command `config set max-replicas $num` and view the enabled configuration using `config show all`. The updating does not affect the applications and is configured in the background.

Make sure that the total number of TiKV instances is always greater than or equal to the number of replicas you set. For example, 3 replicas need 3 TiKV instances at least. Additional storage requirements need to be estimated before increasing the number of replicas. For more information about pd-ctl, see [PD Control User Guide](https://docs.pingcap.com/tidb/stable/pd-control).
### How to check the health status of the whole cluster when lacking command line cluster management tools?

You can determine the general status of the cluster using the pd-ctl tool. For detailed cluster status, you need to use the monitor to determine.
### How to delete the monitoring data of a cluster node that is offline?

The offline node usually indicates the TiKV node. You can determine whether the offline process is finished by the pd-ctl or the monitor. After the node is offline, perform the following steps:

1. Manually stop the relevant services on the offline node.
2. Delete the `node_exporter` data of the corresponding node from the Prometheus configuration file.
