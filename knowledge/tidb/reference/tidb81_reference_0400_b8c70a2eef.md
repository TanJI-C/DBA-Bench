# PLACEMENT_POLICIES table schema and SHOW PLACEMENT comparison example

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/information-schema/information-schema-placement-policies.md`
- Source Title: `PLACEMENT_POLICIES`
- Source Heading Path: `PLACEMENT_POLICIES | PLACEMENT_POLICIES > Examples`
- Source Line Ranges: `5-76`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `information_schema`, `placement_policies`, `placement_rules`, `show_placement`, `schema`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0400_b8c70a2eef`
- Source ID: `tidb-docs-8.1:information-schema/information-schema-placement-policies.md#placement-policies`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e898ff776fd572bcddaf5c857bed85d031fe49ac3d9ad8a19fbb4edd6f20547e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/information-schema/information-schema-placement-policies#placement-policies
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/information-schema/information-schema-placement-policies.md

## Retrieval Guidance

- Use When: Use this when you need the schema of information_schema.PLACEMENT_POLICIES or need to compare what PLACEMENT_POLICIES shows versus SHOW PLACEMENT for placement rules and assigned objects.
- Retrieval Keywords: information_schema.PLACEMENT_POLICIES, PLACEMENT_POLICIES table, DESC placement_policies, SHOW PLACEMENT, POLICY_ID, POLICY_NAME, PRIMARY_REGION, REGIONS, CONSTRAINTS, LEADER_CONSTRAINTS, FOLLOWER_CONSTRAINTS, LEARNER_CONSTRAINTS, SCHEDULE, FOLLOWERS, LEARNERS, CREATE PLACEMENT POLICY p1, PLACEMENT POLICY=p1, TABLE test.t3, Scheduling_State, canonical version of placement rules
- Follow-up Guidance: The source notes that SHOW PLACEMENT is the canonical view because it includes all placement policies and objects assigned placement policies, while information_schema.PLACEMENT_POLICIES only shows the placement policies.
- Classification Note: This is reference content because it defines the PLACEMENT_POLICIES table schema and gives a SQL example contrasting its output with SHOW PLACEMENT.

## Official Source Content

# PLACEMENT_POLICIES

The `PLACEMENT_POLICIES` table provides information on all placement policies. For details, refer to [Placement Rules in SQL](https://docs.pingcap.com/tidb/stable/placement-rules-in-sql).

> **Note:**
>
> This table is not available on [{{{ .starter }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#starter) and [{{{ .essential }}}](https://docs.pingcap.com/tidbcloud/select-cluster-tier#essential) clusters.

```sql
USE information_schema;
DESC placement_policies;
```

```sql
+----------------------+---------------+------+-----+---------+-------+
| Field                | Type          | Null | Key | Default | Extra |
+----------------------+---------------+------+-----+---------+-------+
| POLICY_ID            | bigint(64)    | NO   |     | <null>  |       |
| CATALOG_NAME         | varchar(512)  | NO   |     | <null>  |       |
| POLICY_NAME          | varchar(64)   | NO   |     | <null>  |       |
| PRIMARY_REGION       | varchar(1024) | YES  |     | <null>  |       |
| REGIONS              | varchar(1024) | YES  |     | <null>  |       |
| CONSTRAINTS          | varchar(1024) | YES  |     | <null>  |       |
| LEADER_CONSTRAINTS   | varchar(1024) | YES  |     | <null>  |       |
| FOLLOWER_CONSTRAINTS | varchar(1024) | YES  |     | <null>  |       |
| LEARNER_CONSTRAINTS  | varchar(1024) | YES  |     | <null>  |       |
| SCHEDULE             | varchar(20)   | YES  |     | <null>  |       |
| FOLLOWERS            | bigint(64)    | YES  |     | <null>  |       |
| LEARNERS             | bigint(64)    | YES  |     | <null>  |       |
+----------------------+---------------+------+-----+---------+-------+
12 rows in set (0.00 sec)
```
## Examples

The `PLACEMENT_POLICIES` table only shows all placement policies. To view the canonical version of placement rules (including all placement policies and objects assigned placement policies), use the statement `SHOW PLACEMENT` instead:

```sql
CREATE TABLE t1 (a INT); 
CREATE PLACEMENT POLICY p1 primary_region="us-east-1" regions="us-east-1";
CREATE TABLE t3 (a INT) PLACEMENT POLICY=p1;
SHOW PLACEMENT; -- Shows all information, including table t3.
SELECT * FROM information_schema.placement_policies; -- Only shows placement policies, excluding t3.
```

```sql
Query OK, 0 rows affected (0.09 sec)

Query OK, 0 rows affected (0.11 sec)

Query OK, 0 rows affected (0.08 sec)

+---------------+------------------------------------------------+------------------+
| Target        | Placement                                      | Scheduling_State |
+---------------+------------------------------------------------+------------------+
| POLICY p1     | PRIMARY_REGION="us-east-1" REGIONS="us-east-1" | NULL             |
| TABLE test.t3 | PRIMARY_REGION="us-east-1" REGIONS="us-east-1" | PENDING          |
+---------------+------------------------------------------------+------------------+
2 rows in set (0.00 sec)

+-----------+--------------+-------------+----------------+-----------+-------------+--------------------+----------------------+---------------------+----------+-----------+----------+
| POLICY_ID | CATALOG_NAME | POLICY_NAME | PRIMARY_REGION | REGIONS   | CONSTRAINTS | LEADER_CONSTRAINTS | FOLLOWER_CONSTRAINTS | LEARNER_CONSTRAINTS | SCHEDULE | FOLLOWERS | LEARNERS |
+-----------+--------------+-------------+----------------+-----------+-------------+--------------------+----------------------+---------------------+----------+-----------+----------+
| 1         | def          | p1          | us-east-1      | us-east-1 |             |                    |                      |                     |          | 2         | 0        |
+-----------+--------------+-------------+----------------+-----------+-------------+--------------------+----------------------+---------------------+----------+-----------+----------+
1 rows in set (0.00 sec)
```
