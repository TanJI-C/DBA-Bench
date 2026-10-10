# TiKV server management FAQs for placement, replicas, and cluster ID mismatch

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/manage-cluster-faq.md`
- Source Title: `TiDB Cluster Management FAQs`
- Source Heading Path: `TiDB Cluster Management FAQs > TiKV server management | TiDB Cluster Management FAQs > TiKV server management > How to specify the location of data for compliance or multi-tenant applications? | TiDB Cluster Management FAQs > TiKV server management > What is the recommended number of replicas in the TiKV cluster? Is it better to keep the minimum number for high availability? | TiDB Cluster Management FAQs > TiKV server management > The `cluster ID mismatch` message is displayed when starting TiKV`
- Source Line Ranges: `299-318`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `pd`, `shared`
- Topic Tags: `placement-rules`, `data-location`, `replicas`, `high-availability`, `cluster-id`, `startup-error`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0146_1e5f322e2f`
- Source ID: `tidb-docs-8.1:faq/manage-cluster-faq.md#tikv-server-management`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d25b7a49ecaf2e953082877af25e5d655f4f061143de476dfcf6785c5cb881c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/manage-cluster-faq#tikv-server-management
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/manage-cluster-faq.md

## Retrieval Guidance

- Use When: Use this chunk when asking how to control TiKV data placement with Placement Rules, what replica count is discussed for TiKV Regions, or why TiKV shows a cluster ID mismatch at startup.
- Retrieval Keywords: Placement Rules, Placement Rules in SQL, number of replicas, Raft role, placement location, key ranges, 3 replicas for each Region, cluster ID mismatch, PD generates random cluster IDs, local cluster ID, TiKV exits, remove the PD data, new PD cluster
- Follow-up Guidance: The content explains that cluster ID mismatch occurs when the local TiKV cluster ID differs from the cluster ID in PD, such as when TiKV with old data connects to a newly deployed PD cluster.
- Classification Note: This is classified as TiKV operation content because it focuses on TiKV data placement, Region replica discussion, and a TiKV startup error involving PD cluster IDs.

## Official Source Content

## TiKV server management

This section describes common problems you might encounter during TiKV server management, their causes, and solutions.
### How to specify the location of data for compliance or multi-tenant applications?

You can use [Placement Rules](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql) to specify the location of data for compliance or multi-tenant applications.

Placement Rules in SQL is designed to control the attributes of any continuous data range, such as the number of replicas, the Raft role, the placement location, and the key ranges in which the rules take effect.
### What is the recommended number of replicas in the TiKV cluster? Is it better to keep the minimum number for high availability?

3 replicas for each Region is sufficient for a testing environment. However, you should never operate a TiKV cluster with under 3 nodes in a production scenario. Depending on infrastructure, workload, and resiliency needs, you may wish to increase this number. It is worth noting that the higher the copy, the lower the performance, but the higher the security.
### The `cluster ID mismatch` message is displayed when starting TiKV

This is because the cluster ID stored in local TiKV is different from the cluster ID specified by PD. When a new PD cluster is deployed, PD generates random cluster IDs. TiKV gets the cluster ID from PD and stores the cluster ID locally when it is initialized. The next time when TiKV is started, it checks the local cluster ID with the cluster ID in PD. If the cluster IDs don't match, the `cluster ID mismatch` message is displayed and TiKV exits.

If you previously deploy a PD cluster, but then you remove the PD data and deploy a new PD cluster, this error occurs because TiKV uses the old data to connect to the new PD cluster.
