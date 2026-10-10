# High availability placement policy examples for survival and multi-region replica distribution

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/placement-rules-in-sql.md`
- Source Title: `Placement Rules in SQL`
- Source Heading Path: `Placement Rules in SQL > High availability examples | Placement Rules in SQL > High availability examples > Specify survival preferences | Placement Rules in SQL > High availability examples > Specify a cluster with 5 replicas distributed 2:2:1 across multiple data centers`
- Source Line Ranges: `328-401`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `placement-policies`, `high-availability`, `survival-preferences`, `replica-distribution`, `topology-labels`, `constraints`, `global-range`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0138_3d52f8a16f`
- Source ID: `tidb-docs-8.1:placement-rules-in-sql.md#high-availability-examples`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f64bd3469d54458e65813128b4bc25651d1165b497fd175daeef1307cd6f931c`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/placement-rules-in-sql#high-availability-examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/placement-rules-in-sql.md

## Retrieval Guidance

- Use When: Use this chunk when looking for SQL placement policy examples that use SURVIVAL_PREFERENCES, topology labels, or a 5-replica 2:2:1 cross-region distribution including ALTER RANGE global and SHOW PLACEMENT.
- Retrieval Keywords: SURVIVAL_PREFERENCES, location-labels, CREATE PLACEMENT POLICY multiaz, CREATE PLACEMENT POLICY singleaz, CONSTRAINTS="[+region=us-east-1]", [region, zone, host], singleaz, multiaz, INFORMATION_SCHEMA.TIKV_STORE_STATUS, SELECT store_id,address,label from INFORMATION_SCHEMA.TIKV_STORE_STATUS, deploy221, 2:2:1, 5 replicas distributed 2:2:1, CONSTRAINTS='{"+region=us-east-1":2, "+region=us-east-2": 2, "+region=us-west-1": 1}', ALTER RANGE global PLACEMENT POLICY = "deploy221", SHOW PLACEMENT, RANGE TiDB_GLOBAL
- Follow-up Guidance: The chunk also shows how to inspect store labels with INFORMATION_SCHEMA.TIKV_STORE_STATUS and verify the applied global placement policy with SHOW PLACEMENT.
- Classification Note: This is classified as configuration because the content defines SQL placement policies and constraints that control replica placement and survival goals across regions, zones, and hosts.

## Official Source Content

## High availability examples

Assume that there is a cluster with the following topology, where TiKV nodes are distributed across 3 regions, with each region containing 3 available zones:

```sql
SELECT store_id,address,label from INFORMATION_SCHEMA.TIKV_STORE_STATUS;
+----------+-----------------+--------------------------------------------------------------------------------------------------------------------------+
| store_id | address         | label                                                                                                                    |
+----------+-----------------+--------------------------------------------------------------------------------------------------------------------------+
|        1 | 127.0.0.1:20163 | [{"key": "region", "value": "us-east-1"}, {"key": "zone", "value": "us-east-1a"}, {"key": "host", "value": "host1"}]     |
|        2 | 127.0.0.1:20162 | [{"key": "region", "value": "us-east-1"}, {"key": "zone", "value": "us-east-1b"}, {"key": "host", "value": "host2"}]     |
|        3 | 127.0.0.1:20164 | [{"key": "region", "value": "us-east-1"}, {"key": "zone", "value": "us-east-1c"}, {"key": "host", "value": "host3"}]     |
|        4 | 127.0.0.1:20160 | [{"key": "region", "value": "us-east-2"}, {"key": "zone", "value": "us-east-2a"}, {"key": "host", "value": "host4"}]     |
|        5 | 127.0.0.1:20161 | [{"key": "region", "value": "us-east-2"}, {"key": "zone", "value": "us-east-2b"}, {"key": "host", "value": "host5"}]     |
|        6 | 127.0.0.1:20165 | [{"key": "region", "value": "us-east-2"}, {"key": "zone", "value": "us-east-2c"}, {"key": "host", "value": "host6"}]     |
|        7 | 127.0.0.1:20166 | [{"key": "region", "value": "us-west-1"}, {"key": "zone", "value": "us-west-1a"}, {"key": "host", "value": "host7"}]     |
|        8 | 127.0.0.1:20167 | [{"key": "region", "value": "us-west-1"}, {"key": "zone", "value": "us-west-1b"}, {"key": "host", "value": "host8"}]     |
|        9 | 127.0.0.1:20168 | [{"key": "region", "value": "us-west-1"}, {"key": "zone", "value": "us-west-1c"}, {"key": "host", "value": "host9"}]     |
+----------+-----------------+--------------------------------------------------------------------------------------------------------------------------+

```
### Specify survival preferences

If you are not particularly concerned about the exact data distribution but prioritize fulfilling disaster recovery requirements, you can use the `SURVIVAL_PREFERENCES` option to specify data survival preferences.

As in the preceding example, the TiDB cluster is distributed across 3 regions, with each region containing 3 zones. When creating placement policies for this cluster, assume that you configure the `SURVIVAL_PREFERENCES` as follows:

``` sql
CREATE PLACEMENT POLICY multiaz SURVIVAL_PREFERENCES="[region, zone, host]";
CREATE PLACEMENT POLICY singleaz CONSTRAINTS="[+region=us-east-1]" SURVIVAL_PREFERENCES="[zone]";
```

After creating the placement policies, you can attach them to the corresponding tables as needed:

- For tables attached with the `multiaz` placement policy, data will be placed in 3 replicas in different regions, prioritizing to meet the cross-region survival goal of data isolation, followed by the cross-zone survival goal, and finally the cross-host survival goal.
- For tables attached with the `singleaz` placement policy, data will be placed in 3 replicas in the `us-east-1` region first, and then meet the cross-zone survival goal of data isolation.

> **Note:**
>
> `SURVIVAL_PREFERENCES` is equivalent to `location-labels` in PD. For more information, see [Schedule Replicas by Topology Labels](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels).

> **Note:**
>
> `SURVIVAL_PREFERENCES` is equivalent to `location-labels` in PD. For more information, see [Schedule Replicas by Topology Labels](https://docs.pingcap.com/tidb/stable/schedule-replicas-by-topology-labels).
### Specify a cluster with 5 replicas distributed 2:2:1 across multiple data centers

If you need a specific data distribution, such as a 5-replica distribution in the proportion of 2:2:1, you can specify different numbers of replicas for different constraints by configuring these `CONSTRAINTS` in the [dictionary formats](#constraints-formats):

```sql
CREATE PLACEMENT POLICY `deploy221` CONSTRAINTS='{"+region=us-east-1":2, "+region=us-east-2": 2, "+region=us-west-1": 1}';

ALTER RANGE global PLACEMENT POLICY = "deploy221";

SHOW PLACEMENT;
+-------------------+---------------------------------------------------------------------------------------------+------------------+
| Target            | Placement                                                                                   | Scheduling_State |
+-------------------+---------------------------------------------------------------------------------------------+------------------+
| POLICY deploy221  | CONSTRAINTS="{\"+region=us-east-1\":2, \"+region=us-east-2\": 2, \"+region=us-west-1\": 1}" | NULL             |
| RANGE TiDB_GLOBAL | CONSTRAINTS="{\"+region=us-east-1\":2, \"+region=us-east-2\": 2, \"+region=us-west-1\": 1}" | SCHEDULED        |
+-------------------+---------------------------------------------------------------------------------------------+------------------+
```

After the global  `deploy221` placement policy is set for the cluster, TiDB distributes data according to this policy: placing two replicas in the `us-east-1` region, two replicas in the `us-east-2` region, and one replica in the `us-west-1` region.
