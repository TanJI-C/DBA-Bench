# Dynamic programming Join Reorder example

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/join-reorder.md`
- Source Title: `Introduction to Join Reorder`
- Source Heading Path: `Introduction to Join Reorder > Example: the dynamic programming algorithm of Join Reorder`
- Source Line Ranges: `48-57`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `dynamic programming`, `join order`, `statistics`, `enumeration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0045_c231c14b93`
- Source ID: `tidb-docs-8.1:join-reorder.md#example-the-dynamic-programming-algorithm-of-join-reorder`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `611995b0b37fb4a4a537f3b0e232fcf1706a48fcb0492bd29ecfe4a9f1ad8bd3`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/join-reorder#example-the-dynamic-programming-algorithm-of-join-reorder
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/join-reorder.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how the dynamic programming Join Reorder algorithm differs from the greedy algorithm or what trade-offs it has.
- Retrieval Keywords: dynamic programming Join Reorder, enumerate all possibilities, better join order, greedy algorithm, must start with the `t1` table, consumes more time, susceptible to statistics
- Follow-up Guidance: It explains that dynamic programming can choose a better join order than greedy by enumerating all possible join orders, but it consumes more time and is more susceptible to statistics.
- Classification Note: This is architecture content because it explains the optimizer strategy and trade-offs of the dynamic programming join-order algorithm.

## Official Source Content

## Example: the dynamic programming algorithm of Join Reorder

Taking the preceding three tables (t1, t2, and t3) as an example again, the dynamic programming algorithm can enumerate all possibilities. Therefore, comparing with the greedy algorithm, which must start with the `t1` table (the table with the least rows), the dynamic programming algorithm can enumerate a join order as follows:

![join-reorder-4](/media/join-reorder-4.png)

When this choice is better than the greedy algorithm, the dynamic programming algorithm can choose a better join order.

Because all possibilities are enumerated, the dynamic programming algorithm consumes more time and is more susceptible to statistics.
