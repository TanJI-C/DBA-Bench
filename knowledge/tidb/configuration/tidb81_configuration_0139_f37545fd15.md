# Leader and follower placement plus data isolation examples

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/placement-rules-in-sql.md`
- Source Title: `Placement Rules in SQL`
- Source Heading Path: `Placement Rules in SQL > High availability examples > Specify the distribution of Leaders and Followers | Placement Rules in SQL > High availability examples > Specify the distribution of Leaders and Followers > Use constraints | Placement Rules in SQL > High availability examples > Specify the distribution of Leaders and Followers > Use `PRIMARY_REGION` | Placement Rules in SQL > Data isolation examples | Placement Rules in SQL > Compatibility`
- Source Line Ranges: `402-454`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `pd`, `tikv`, `tidb`
- Topic Tags: `leader-placement`, `follower-placement`, `primary-region`, `schedule-policy`, `evict-leader`, `data-isolation`, `app-labels`, `constraints`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0139_f37545fd15`
- Source ID: `tidb-docs-8.1:placement-rules-in-sql.md#specify-the-distribution-of-leaders-and-followers`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1b6b3eb8175244fc100d0e1dd08bd1b5b8f852c631ee6a57947e6e857a6429c4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/placement-rules-in-sql#specify-the-distribution-of-leaders-and-followers
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/placement-rules-in-sql.md

## Retrieval Guidance

- Use When: Use this chunk when looking for SQL examples for Leader and Follower placement, PRIMARY_REGION and SCHEDULE options, evict-leader behavior, or app-label-based data isolation policies.
- Retrieval Keywords: LEADER_CONSTRAINTS, FOLLOWER_CONSTRAINTS, CREATE PLACEMENT POLICY deploy221_primary_east1, evict-leader, #evict-leader, PRIMARY_REGION, REGIONS, SCHEDULE, MAJORITY_IN_PRIMARY, EVEN, FOLLOWERS=4, CREATE PLACEMENT POLICY eastandwest, CREATE TABLE t1 (a INT) PLACEMENT POLICY=eastandwest, data isolation, app label, CREATE PLACEMENT POLICY app_order, CREATE PLACEMENT POLICY app_list, [+app=order], [+app=list_collection], {+app=order: 3}, physical data isolation in storage
- Follow-up Guidance: The chunk also notes that service availability takes the highest priority for Leader election and that MAJORITY_IN_PRIMARY does not provide automatic failover if the primary region fails.
- Classification Note: This is classified as configuration because the content uses SQL placement policy options and constraints to control Leader and Follower distribution and isolate table data by TiKV node labels.

## Official Source Content

### Specify the distribution of Leaders and Followers

You can specify a specific distribution of Leaders and Followers using constraints or `PRIMARY_REGION`.
#### Use constraints

If you have specific requirements for the distribution of Raft Leaders among nodes, you can specify the placement policy using the following statement:

```sql
CREATE PLACEMENT POLICY deploy221_primary_east1 LEADER_CONSTRAINTS="[+region=us-east-1]" FOLLOWER_CONSTRAINTS='{"+region=us-east-1": 1, "+region=us-east-2": 2, "+region=us-west-1: 1}';
```

After this placement policy is created and attached to the desired data, the Raft Leader replicas of the data will be placed in the `us-east-1` region specified by the `LEADER_CONSTRAINTS` option, while other replicas of the data will be placed in regions specified by the `FOLLOWER_CONSTRAINTS` option. Note that if the cluster fails, such as a node outage in the `us-east-1` region, a new Leader will still be elected from other regions, even if these regions are specified in `FOLLOWER_CONSTRAINTS`. In other words, ensuring service availability takes the highest priority.

In the event of a failure in the `us-east-1` region, if you do not want to place new Leaders in `us-west-1`, you can configure a special `evict-leader` attribute to evict the newly elected Leaders in that region:

```sql
CREATE PLACEMENT POLICY deploy221_primary_east1 LEADER_CONSTRAINTS="[+region=us-east-1]" FOLLOWER_CONSTRAINTS='{"+region=us-east-1": 1, "+region=us-east-2": 2, "+region=us-west-1,#evict-leader": 1}';
```
#### Use `PRIMARY_REGION`

If the `region` label is configured in your cluster topology, you can also use the `PRIMARY_REGION` and `REGIONS` options to specify a placement policy for Followers:

```sql
CREATE PLACEMENT POLICY eastandwest PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-east-2,us-west-1" SCHEDULE="MAJORITY_IN_PRIMARY" FOLLOWERS=4;
CREATE TABLE t1 (a INT) PLACEMENT POLICY=eastandwest;
```

- `PRIMARY_REGION` specifies the distribution region of the Leaders. You can only specify one region in this option.
- The `SCHEDULE` option specifies how TiDB balances the distribution of Followers.
    - The default `EVEN` scheduling rule ensures a balanced distribution of Followers across all regions.
    - If you want to ensure a sufficient number of Follower replicas are placed in the `PRIMARY_REGION` (that is, `us-east-1`), you can use the `MAJORITY_IN_PRIMARY` scheduling rule. This scheduling rule provides lower latency transactions at the expense of some availability. If the primary region fails, `MAJORITY_IN_PRIMARY` does not provide automatic failover.
## Data isolation examples

As in the following example, when creating placement policies, you can configure a constraint for each policy, which requires data to be placed on TiKV nodes with the specified `app` label.

```sql
CREATE PLACEMENT POLICY app_order CONSTRAINTS="[+app=order]";
CREATE PLACEMENT POLICY app_list CONSTRAINTS="[+app=list_collection]";
CREATE TABLE order (id INT, name VARCHAR(50), purchased DATE)
PLACEMENT POLICY=app_order
CREATE TABLE list (id INT, name VARCHAR(50), purchased DATE)
PLACEMENT POLICY=app_list
```

In this example, the constraints are specified using the list format, such as `[+app=order]`. You can also specify them using the dictionary format, such as `{+app=order: 3}`.

After executing the statements in the example, TiDB will place the `app_order` data on TiKV nodes with the `app` label as `order`, and place the `app_list` data on TiKV nodes with the `app` label as `list_collection`, thus achieving physical data isolation in storage.
## Compatibility
