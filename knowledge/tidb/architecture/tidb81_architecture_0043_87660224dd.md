# Join Reorder overview

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/join-reorder.md`
- Source Title: `Introduction to Join Reorder`
- Source Heading Path: `Introduction to Join Reorder`
- Source Line Ranges: `5-29`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `join reorder`, `join order`, `greedy algorithm`, `dynamic programming`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0043_87660224dd`
- Source ID: `tidb-docs-8.1:join-reorder.md#introduction-to-join-reorder`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `06255d31b4932befd9197ca3b603fbb9dff997fd422f0bf1645f0cf71a57f3a0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/join-reorder#introduction-to-join-reorder
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/join-reorder.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks what Join Reorder is in TiDB, why join order affects performance, or which Join Reorder algorithms TiDB uses.
- Retrieval Keywords: Join Reorder, join order, optimizer, greedy algorithm, dynamic programming algorithm, SELECT * FROM t1, t2, t3 WHERE t1.a=t2.a AND t3.a=t2.a, execution efficiency of join
- Follow-up Guidance: It also introduces that TiDB currently uses the greedy algorithm and the dynamic programming algorithm to determine join order.
- Classification Note: This is architecture content because it explains the optimizer behavior and the high-level algorithms TiDB uses for multi-table join ordering.

## Official Source Content

# Introduction to Join Reorder

In real application scenarios, it is common to join multiple tables. The execution efficiency of join is associated with the order in which each table joins.

For example:

```sql
SELECT * FROM t1, t2, t3 WHERE t1.a=t2.a AND t3.a=t2.a;
```

In this query, tables can be joined in the following two orders:

- t1 joins t2, and then joins t3
- t2 joins t3, and then joins t1

As t1 and t3 have different data volumes and distribution, these two execution orders might show different performances.

Therefore, the optimizer needs an algorithm to determine the join order. Currently, the following two Join Reorder algorithms are used in TiDB:

- The greedy algorithm: among all nodes participating in the join, TiDB selects the table with the least rows to estimate its join result with each of the other tables respectively, and then selects the pair with the smallest join result. After that, TiDB continues the similar process to select and join other nodes for the next round, until all the nodes have completed the join.
- The dynamic programming algorithm: among all nodes participating in the join, TiDB enumerates all possible join orders and selects the optimal join order.
