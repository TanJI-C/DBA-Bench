# Stale Read, safe-ts, and resolved-ts concepts

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/troubleshoot-stale-read.md`
- Source Title: `Understanding Stale Read and safe-ts in TiKV`
- Source Heading Path: `Understanding Stale Read and safe-ts in TiKV | Understanding Stale Read and safe-ts in TiKV > Overview of Stale Read and safe-ts | Understanding Stale Read and safe-ts in TiKV > Understand safe-ts and resolved-ts | Understanding Stale Read and safe-ts in TiKV > Understand safe-ts and resolved-ts > What is safe-ts? | Understanding Stale Read and safe-ts in TiKV > Understand safe-ts and resolved-ts > What is resolved-ts? | Understanding Stale Read and safe-ts in TiKV > Understand safe-ts and resolved-ts > The maintenance of safe-ts | Understanding Stale Read and safe-ts in TiKV > Understand safe-ts and resolved-ts > The maintenance of resolved-ts`
- Source Line Ranges: `5-35`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`
- Topic Tags: `stale-read`, `safe-ts`, `resolved-ts`, `region`, `leader`, `follower`, `regionreadprogress`, `resolver`, `raft`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0119_f02697af8a`
- Source ID: `tidb-docs-8.1:troubleshoot-stale-read.md#understanding-stale-read-and-safe-ts-in-tikv`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1444c5d490115c126f3ea019d6c47b9e4f42a9e04d8792000cd768b0d8dfa136`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/troubleshoot-stale-read#understanding-stale-read-and-safe-ts-in-tikv
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/troubleshoot-stale-read.md

## Retrieval Guidance

- Use When: Use this chunk when explaining how Stale Read depends on safe-ts and resolved-ts in a TiKV Region leader and follower context.
- Retrieval Keywords: Stale Read, safe-ts, resolved-ts, RegionReadProgress, CheckLeader RPC, resolver, LOCK CF, apply index, Region leader, follower, Raft applies, local Stale Read
- Follow-up Guidance: It also states that the Region leader sends resolved-ts, the minimum required apply index, and the Region to all replicas through the CheckLeader RPC so peers can update safe-ts.
- Classification Note: This chunk is classified as architecture because it defines the concepts of safe-ts and resolved-ts and describes how RegionReadProgress and the resolver maintain them in TiKV.

## Official Source Content

# Understanding Stale Read and safe-ts in TiKV

In this guide, you can learn about Stale Read and safe-ts in TiKV and how to diagnose common issues related to Stale Read.
## Overview of Stale Read and safe-ts

[Stale Read](https://docs.pingcap.com/tidb/stable/stale-read)  is a mechanism that TiDB applies to read historical versions of data stored in TiDB. In TiKV, Stale Read relies on [safe-ts](/#what-is-safe-ts). If a read request on a Region peer has a timestamp (ts) that is less than or equal to the Region's safe-ts, TiDB can safely read the data from the peer. TiKV implements this safety guarantee by ensuring that safe-ts is always less than or equal to [resolved-ts](#what-is-resolved-ts).
## Understand safe-ts and resolved-ts

This section explains the concepts and maintenance of safe-ts and resolved-ts.
### What is safe-ts?

The safe-ts is a timestamp that each peer in a Region maintains. It ensures that all transactions with a timestamp less than this value have been applied locally, which enables local Stale Read.
### What is resolved-ts?

The resolved-ts is a timestamp that guarantees all transactions with a timestamp less than this value have been applied by the leader. Unlike safe-ts, which is a peer concept, resolved-ts is only maintained by the Region leader. Followers might have a smaller apply index than the leader, so resolved-ts cannot be directly treated as safe-ts in followers.
### The maintenance of safe-ts

The `RegionReadProgress` module maintains safe-ts. The Region leader maintains resolved-ts and periodically sends its resolved-ts, the minimum required apply index (which validates this resolved-ts), and the Region itself to the `RegionReadProgerss` modules of all replicas via the CheckLeader RPC.

When a peer applies data, it updates the apply index and checks if any pending resolved-ts can become the new safe-ts.
### The maintenance of resolved-ts

The Region leader uses a resolver to manage resolved-ts. This resolver tracks locks in the LOCK CF (Column Family) by receiving change logs when Raft applies. When initialized, the resolver scans the entire Region to track locks.
