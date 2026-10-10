# Hotspot example and Region warm-up cause analysis

## Knowledge Metadata

- Knowledge Type: `diagnosis`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/best-practices/high-concurrency-best-practices.md`
- Source Title: `Highly Concurrent Write Best Practices`
- Source Heading Path: `Highly Concurrent Write Best Practices > Hotspot case | Highly Concurrent Write Best Practices > Hotspot causes`
- Source Line Ranges: `49-131`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `hotspot`, `write-hotspot`, `case-study`, `region-split`, `leader-concentration`, `raftstore-cpu`, `pd-metrics`, `warm-up-phase`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_diagnosis_0008_18f3ddded2`
- Source ID: `tidb-docs-8.1:best-practices/high-concurrency-best-practices.md#hotspot-case`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2035f1db2af50bf5cc0969f1047b43a26d25b58eec8e561b04a9ac3fd3fcc0d4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/best-practices/high-concurrency-best-practices#hotspot-case
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/best-practices/high-concurrency-best-practices.md

## Retrieval Guidance

- Use When: Use this chunk when diagnosing why a supposedly discrete write pattern can still create an initial TiKV write hotspot and a Region warm-up phase.
- Retrieval Keywords: Hotspot case, Hotspot causes, TEST_HOTSPOT, CREATE TABLE IF NOT EXISTS TEST_HOTSPOT, SET SESSION cte_max_recursion_depth = 1000000, INSERT INTO TEST_HOTSPOT, WITH RECURSIVE nr(n), 3K QPS, Raft store CPU, raftstore thread, tikv-3, PD monitoring metrics, only one Region is split by default, [CommonPrefix + TableID, CommonPrefix + TableID + 1), Region split, leader election, Leader migration, Region warm-up phase
- Follow-up Guidance: The source explains that after continuous writes, PD automatically schedules Leaders and possibly migrates Regions so pressure becomes evenly distributed across the TiKV cluster.
- Classification Note: This chunk is classified as diagnosis because it analyzes an observed hotspot case, ties it to Region splitting and leader concentration, and identifies the warm-up phase as the cause.

## Official Source Content

## Hotspot case

The following case explains how a hotspot is generated. Take the table below as an example:

```sql
CREATE TABLE IF NOT EXISTS TEST_HOTSPOT(
      id         BIGINT PRIMARY KEY,
      age        INT,
      user_name  VARCHAR(32),
      email      VARCHAR(128)
)
```

This table is simple in structure. In addition to `id` as the primary key, no secondary index exists. Execute the following statement to write data into this table. `id` is discretely generated as a random number.

```sql
SET SESSION cte_max_recursion_depth = 1000000;
INSERT INTO TEST_HOTSPOT
SELECT
  n,                                       -- ID
  RAND()*80,                               -- Number between 0 and 80
  CONCAT('user-',n),
  CONCAT(
    CHAR(65 + (RAND() * 25) USING ascii),  -- Number between 65 and 65+25, converted to a character, A-Z
    '-user-',
    n,
    '@example.com'
  )
FROM
  (WITH RECURSIVE nr(n) AS 
    (SELECT 1                              -- Start CTE at 1
      UNION ALL SELECT n + 1               -- increase n with 1 every loop
      FROM nr WHERE n < 1000000            -- stop loop at 1_000_000 
    ) SELECT n FROM nr
  ) a;
```

The load comes from executing the above statement intensively in a short time.

In theory, the above operation seems to comply with the TiDB best practices, and no hotspot is caused in the application. The distributed capacity of TiDB can be fully used with adequate machines. To verify whether it is truly in line with the best practices, a test is conducted in the experimental environment, which is described as follows:

For the cluster topology, 2 TiDB nodes, 3 PD nodes and 6 TiKV nodes are deployed. Ignore the QPS performance, because this test is to clarify the principle rather than for benchmark.

![QPS1](/media/best-practices/QPS1.png)

The client starts "intensive" write requests in a short time, which is 3K QPS received by TiDB. In theory, the load pressure should be evenly distributed to 6 TiKV nodes. However, from the CPU usage of each TiKV node, the load distribution is uneven. The `tikv-3` node is the write hotspot.

![QPS2](/media/best-practices/QPS2.png)

![QPS3](/media/best-practices/QPS3.png)

[Raft store CPU](https://docs.pingcap.com/tidb/stable/grafana-tikv-dashboard) is the CPU usage rate for the `raftstore` thread, usually representing the write load. In this scenario, `tikv-3` is the Leader of this Raft Group; `tikv-0` and `tikv-1` are the followers. The loads of other nodes are almost empty.

The monitoring metrics of PD also confirms that hotspot has been caused.

![QPS4](/media/best-practices/QPS4.png)
## Hotspot causes

In the above test, the operation does not reach the ideal performance expected in the best practices. This is because only one Region is split by default to store the data of each newly created table in TiDB, with the following data range:

```
[CommonPrefix + TableID, CommonPrefix + TableID + 1)
```

In a short period of time, a huge volume of data is continuously written to the same Region.

![TiKV Region Split](/media/best-practices/tikv-Region-split.png)

The above diagram illustrates the Region splitting process. As data is continuously written into TiKV, TiKV splits a Region into multiple Regions. Because the leader election is started on the original store where the Region Leader to be split is located, the leaders of the two newly split Regions might be still on the same store. This splitting process might also happen on the newly split Region 2 and Region 3. In this way, write pressure is concentrated on TiKV-Node 1.

During the continuous write process, after finding that hotspot is caused on Node 1, PD evenly distributes the concentrated Leaders to other nodes. If the number of TiKV nodes is more than the number of Region replicas, TiKV will try to migrate these Regions to idle nodes. These two operations during the write process are also reflected in the PD's monitoring metrics:

![QPS5](/media/best-practices/QPS5.png)

After a period of continuous writes, PD automatically schedules the entire TiKV cluster to a state where pressure is evenly distributed. By that time, the capacity of the whole cluster can be fully used.

In most cases, the above process of causing a hotspot is normal, which is the Region warm-up phase of database. However, you need to avoid this phase in highly-concurrent write-intensive scenarios.
