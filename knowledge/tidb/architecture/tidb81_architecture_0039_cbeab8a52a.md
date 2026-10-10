# Follower Read implementation, consistency, and follower selection

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/follower-read.md`
- Source Title: `Follower Read`
- Source Heading Path: `Follower Read > Implementation mechanism | Follower Read > Implementation mechanism > Strongly consistent reads | Follower Read > Implementation mechanism > Follower replica selection strategy`
- Source Line Ranges: `59-73`
- Source Scope: `self_managed`
- Primary Component: `tikv`
- Related Components: `tidb`
- Topic Tags: `raft`, `readindex`, `linearizability`, `snapshot-isolation`, `load-balancing`, `round-robin`, `coprocessor-requests`, `point-queries`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0039_cbeab8a52a`
- Source ID: `tidb-docs-8.1:follower-read.md#implementation-mechanism`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4044e965437bb96690077ec357895f33196db46b5a23af7f28e7b27ffb8b3897`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/follower-read#implementation-mechanism
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/follower-read.md

## Retrieval Guidance

- Use When: Use this chunk when retrieving how Follower Read preserves strong consistency with Raft `ReadIndex` and how TiDB selects follower replicas for coprocessor and non-coprocessor requests.
- Retrieval Keywords: Implementation mechanism, strongly consistent reads, linearizability, Snapshot Isolation, Raft, ReadIndex, latest commit index, round-robin, follower replica selection strategy, coprocessor requests, non-coprocessor requests, point query, connection level, transaction level
- Follow-up Guidance: The source further explains that if a transaction contains both point queries and coprocessor requests, TiDB schedules the two request types separately even for the same Region.
- Classification Note: This is classified as architecture because the content explains the internal consistency mechanism and request scheduling strategy behind Follower Read in TiKV and TiDB.

## Official Source Content

## Implementation mechanism

Before the Follower Read feature was introduced, TiDB applied the strong leader principle and submitted all read and write requests to the leader node of a Region to handle. Although TiKV can distribute Regions evenly on multiple physical nodes, for each Region, only the leader can provide external services. The other followers can do nothing to handle read requests but receive the data replicated from the leader at all times and prepare for voting to elect a leader in case of a failover.

To allow data reading in the follower node without violating linearizability or affecting Snapshot Isolation in TiDB, the follower node needs to use `ReadIndex` of the Raft protocol to ensure that the read request can read the latest data that has been committed on the leader. At the TiDB level, the Follower Read feature simply needs to send the read request of a Region to a follower replica based on the load balancing policy.
### Strongly consistent reads

When the follower node processes a read request, it first uses `ReadIndex` of the Raft protocol to interact with the leader of the Region, to obtain the latest commit index of the current Raft group. After the latest commit index of the leader is applied locally to the follower, the processing of a read request starts.
### Follower replica selection strategy

Because the Follower Read feature does not affect TiDB's Snapshot Isolation transaction isolation level, TiDB adopts the round-robin strategy to select the follower replica. Currently, for the coprocessor requests, the granularity of the Follower Read load balancing policy is at the connection level. For a TiDB client connected to a specific Region, the selected follower is fixed, and is switched only when it fails or the scheduling policy is adjusted.

However, for the non-coprocessor requests, such as a point query, the granularity of the Follower Read load balancing policy is at the transaction level. For a TiDB transaction on a specific Region, the selected follower is fixed, and is switched only when it fails or the scheduling policy is adjusted. If a transaction contains both point queries and coprocessor requests, the two types of requests are scheduled for reading separately according to the preceding scheduling policy. In this case, even if a coprocessor request and a point query are for the same Region, TiDB processes them as independent events.
