# High availability FAQ overview, consistency, and geo-distributed deployment

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/faq/high-availability-faq.md`
- Source Title: `High Availability FAQs`
- Source Heading Path: `High Availability FAQs | High Availability FAQs > How is TiDB strongly consistent? | High Availability FAQs > What's the recommended solution for the deployment of three geo-distributed data centers?`
- Source Line Ranges: `5-18`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: `tikv`, `tidb`
- Topic Tags: `high-availability`, `strong-consistency`, `raft`, `replication`, `leader-follower`, `geo-distribution`, `multi-activeness`, `network-latency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0037_03bf97de03`
- Source ID: `tidb-docs-8.1:faq/high-availability-faq.md#high-availability-faqs`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ddd4f8d091fb41156bd7328c802de4d7ce9fb8df63c6c1d5880e88b14a3dcbfe`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/faq/high-availability-faq#high-availability-faqs
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/faq/high-availability-faq.md

## Retrieval Guidance

- Use When: Use this chunk when asking how TiDB provides strong consistency with Raft replication or what the FAQ says about deploying TiDB across three geo-distributed data centers.
- Retrieval Keywords: High Availability FAQs, How is TiDB strongly consistent?, Raft consensus algorithm, TiKV, replication log + State Machine, Leader, Followers, majority of nodes, log is committed, What's the recommended solution for the deployment of three geo-distributed data centers?, geo-distribution, multi-activeness, always-on, transparent to your applications, recover automatically, network latency and stability, keep the latency within 5ms, Three Data Centers in Two Cities Deployment
- Follow-up Guidance: The source points to the Three Data Centers in Two Cities Deployment document for more details about similar geo-distributed deployment use cases.
- Classification Note: This chunk is classified as architecture because it explains TiDB strong consistency through TiKV Raft leader-follower replication and describes geo-distributed, multi-active deployment behavior and latency considerations.

## Official Source Content

# High Availability FAQs

This document summarizes the FAQs related to high availability of TiDB.
## How is TiDB strongly consistent?

Data is redundantly replicated between TiKV nodes using the [Raft consensus algorithm](https://raft.github.io/) to ensure recoverability when a node failure occurs.

At the bottom layer, TiKV uses a model of replication log + State Machine to replicate data. For the write requests, the data is written to a Leader and the Leader then replicates the command to its Followers in the form of log. When the majority of nodes in the cluster receive this log, this log is committed and can be applied into the State Machine.
## What's the recommended solution for the deployment of three geo-distributed data centers?

The architecture of TiDB guarantees that it fully supports geo-distribution and multi-activeness. Your data and applications are always-on. All the outages are transparent to your applications and your data can recover automatically. The operation depends on the network latency and stability. It is recommended to keep the latency within 5ms. Currently, TiDB already has similar use cases. For details, see [Three Data Centers in Two Cities Deployment](https://docs.pingcap.com/tidb/stable/three-data-centers-in-two-cities-deployment).
