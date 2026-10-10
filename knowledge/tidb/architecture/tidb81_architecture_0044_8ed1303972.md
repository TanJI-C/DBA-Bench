# Greedy Join Reorder example

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/join-reorder.md`
- Source Title: `Introduction to Join Reorder`
- Source Heading Path: `Introduction to Join Reorder > Example: the greedy algorithm of Join Reorder`
- Source Line Ranges: `30-47`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: none
- Topic Tags: `greedy algorithm`, `join order`, `row count`, `result set`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0044_8ed1303972`
- Source ID: `tidb-docs-8.1:join-reorder.md#example-the-greedy-algorithm-of-join-reorder`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `60f68f8a1ac9d3ba2954c9d6c99ead84a64de80eafb2f5d7a53ec025db1cee42`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/join-reorder#example-the-greedy-algorithm-of-join-reorder
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/join-reorder.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how the greedy Join Reorder algorithm works step by step for tables such as t1, t2, and t3.
- Retrieval Keywords: greedy Join Reorder, t1 t2 t3, ascending order of row numbers, table with the least rows, output result sets, smaller result set, next round of selection
- Follow-up Guidance: It states that TiDB first sorts participating join nodes by row count, then joins the table with the least rows to others and picks the pair with the smaller output result set.
- Classification Note: This is architecture content because it describes the internal execution logic of the greedy join-order selection process.

## Official Source Content

## Example: the greedy algorithm of Join Reorder

Take the preceding three tables (t1, t2, and t3) as an example.

First, TiDB obtains all the nodes that participates in the join operation, and sorts the nodes in the ascending order of row numbers.

![join-reorder-1](/media/join-reorder-1.png)

After that, the table with the least rows is selected and joined with other two tables respectively. By comparing the sizes of the output result sets, TiDB selects the pair with a smaller result set.

![join-reorder-2](/media/join-reorder-2.png)

Then TiDB enters the next round of selection. If you try to join four tables, TiDB continues to compare the sizes of the output result sets and selects the pair with a smaller result set.

In this case only three tables are joined, so TiDB gets the final join result.

![join-reorder-3](/media/join-reorder-3.png)
