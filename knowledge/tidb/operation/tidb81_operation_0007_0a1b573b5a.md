# Google Cloud live migration mitigation for TiDB clusters

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/best-practices-on-public-cloud.md`
- Source Title: `TiDB Best Practices on Public Cloud`
- Source Heading Path: `TiDB Best Practices on Public Cloud > Mitigate live migration maintenance events on Google Cloud`
- Source Line Ranges: `141-154`
- Source Scope: `kubernetes`
- Primary Component: `cloud`
- Related Components: `operator`, `tidb`, `tikv`, `pd`
- Topic Tags: `google-cloud`, `live-migration`, `maintenance-events`, `node-cordon`, `leader-eviction`, `pd-leader-resign`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0007_0a1b573b5a`
- Source ID: `tidb-docs-8.1:best-practices/best-practices-on-public-cloud.md#mitigate-live-migration-maintenance-events-on-google-cloud`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b3b092cf290db2cb0ff44f46dbd55ba2a38262cdc5e95ddb0f0f01ea40d9b09b`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/best-practices-on-public-cloud#mitigate-live-migration-maintenance-events-on-google-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/best-practices-on-public-cloud.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks about mitigating Google Cloud live migration maintenance events for TiDB clusters deployed with TiDB Operator on Kubernetes.
- Retrieval Keywords: Live Migration feature, Google Cloud, maintenance events, watching script, tidb-google-maintenance, Google metadata example, TiDB Operator, Kubernetes, node cordon, delete the TiDB pod, TiKV leader eviction, PD leader resign, cordoned node, auto-scale, dedicated to TiDB
- Follow-up Guidance: The source also states the script can be deployed on TiDB, TiKV, and PD nodes and describes the automatic action for each component when a maintenance event is detected.
- Classification Note: This is classified as operation content because it describes detecting Google Cloud maintenance events and the component-specific mitigation behavior during cluster operation.

## Official Source Content

## Mitigate live migration maintenance events on Google Cloud

The [Live Migration feature](https://cloud.google.com/compute/docs/instances/live-migration-process) of Google Cloud enables VMs to be seamlessly migrated between hosts without causing downtime. However, these migration events, although infrequent, can significantly impact the performance of VMs, including those running in a TiDB cluster. During such events, affected VMs might experience reduced performance, leading to longer query processing times in the TiDB cluster.

To detect live migration events initiated by Google Cloud and mitigate the performance impact of these events, TiDB provides a [watching script](https://github.com/PingCAP-QE/tidb-google-maintenance) based on Google's metadata [example](https://github.com/GoogleCloudPlatform/python-docs-samples/blob/master/compute/metadata/main.py). You can deploy this script on TiDB, TiKV, and PD nodes to detect maintenance events. When a maintenance event is detected, appropriate actions can be taken automatically as follows to minimize disruption and optimize the cluster behavior:

- TiDB: Takes the TiDB node offline by cordoning it and deleting the TiDB pod. This assumes that the node pool of the TiDB instance is set to auto-scale and dedicated to TiDB. Other pods running on the node might experience interruptions, and the cordoned node is expected to be reclaimed by the auto-scaler.
- TiKV: Evicts leaders on the affected TiKV store during maintenance.
- PD: Resigns a leader if the current PD instance is the PD leader.

It is important to note that this watching script is specifically designed for TiDB clusters deployed using [TiDB Operator](https://docs.pingcap.com/tidb-in-kubernetes/v1.6/tidb-operator-overview), which offers enhanced management functionalities for TiDB in Kubernetes environments.

By utilizing the watching script and taking necessary actions during maintenance events, TiDB clusters can better handle live migration events on Google Cloud and ensure smoother operations with minimal impact on query processing and response times.
