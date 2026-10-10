# Basic examples for cluster, database, table, and partition placement policies

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/placement-rules-in-sql.md`
- Source Title: `Placement Rules in SQL`
- Source Heading Path: `Placement Rules in SQL > Basic examples | Placement Rules in SQL > Basic examples > Specify the number of replicas globally for a cluster | Placement Rules in SQL > Basic examples > Specify a default placement policy for a database | Placement Rules in SQL > Basic examples > Specify a placement policy for a table | Placement Rules in SQL > Basic examples > Specify a placement policy for a partitioned table`
- Source Line Ranges: `242-327`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `placement-policies`, `replicas`, `alter-range`, `database-policy`, `table-policy`, `partition-policy`, `policy-inheritance`, `constraints`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0192_fe0b5ae67e`
- Source ID: `tidb-docs-8.1:placement-rules-in-sql.md#basic-examples`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `db6dee033886644a3123299bb151a9fb7cd3de05bb316145ddeb301d248e70aa`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/placement-rules-in-sql#basic-examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/placement-rules-in-sql.md

## Retrieval Guidance

- Use When: Use this chunk when you need SQL examples for applying placement policies at the cluster, database, table, partitioned table, or partition level and understanding how policy inheritance works.
- Retrieval Keywords: ALTER RANGE global PLACEMENT POLICY five_replicas, CREATE PLACEMENT POLICY five_replicas FOLLOWERS=4, default number of replicas is 3, ALTER DATABASE test PLACEMENT POLICY=p2, ALTER DATABASE test PLACEMENT POLICY=p3, ALTER PLACEMENT POLICY p3 FOLLOWERS=3, CREATE TABLE t (a INT) PLACEMENT POLICY=five_replicas, ALTER TABLE t PLACEMENT POLICY=default, PARTITION BY RANGE, ALTER TABLE t1 PARTITION p1 PLACEMENT POLICY=storageforhisotrydata, policy inheritance, database default placement policy, partition placement policy, global default policy, CONSTRAINTS="[+node=history]", CONSTRAINTS="[+node=new]"
- Follow-up Guidance: This chunk explains that database default policy changes do not apply to existing tables, while changing a table default policy also applies to partitions in that table.
- Classification Note: This is operation content because it demonstrates concrete SQL statements and outcomes for attaching and inheriting placement policies across cluster objects.

## Official Source Content

## Basic examples
### Specify the number of replicas globally for a cluster

After a cluster is initialized, the default number of replicas is `3`. If a cluster needs more replicas, you can increase this number by configuring a placement policy, and then apply the policy at the cluster level using [`ALTER RANGE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-range). For example:

```sql
CREATE PLACEMENT POLICY five_replicas FOLLOWERS=4;
ALTER RANGE global PLACEMENT POLICY five_replicas;
```

Note that because TiDB defaults the number of Leaders to `1`, `five replicas` means `4` Followers and `1` Leader.
### Specify a default placement policy for a database

You can specify a default placement policy for a database. This works similarly to setting a default character set or collation for a database. If no other placement policy is specified for a table or partition in the database, the placement policy for the database will apply to the table and partition. For example:

```sql
CREATE PLACEMENT POLICY p1 PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-east-2";  -- Creates a placement policy

CREATE PLACEMENT POLICY p2 FOLLOWERS=4;

CREATE PLACEMENT POLICY p3 FOLLOWERS=2;

CREATE TABLE t1 (a INT);  -- Creates a table t1 without specifying any placement policy.

ALTER DATABASE test PLACEMENT POLICY=p2;  -- Changes the default placement policy of the database to p2, which does not apply to the existing table t1.

CREATE TABLE t2 (a INT);  -- Creates a table t2. The default placement policy p2 applies to t2.

CREATE TABLE t3 (a INT) PLACEMENT POLICY=p1;  -- Creates a table t3. Because this statement has specified another placement rule, the default placement policy p2 does not apply to table t3.

ALTER DATABASE test PLACEMENT POLICY=p3;  -- Changes the default policy of the database again, which does not apply to existing tables.

CREATE TABLE t4 (a INT);  -- Creates a table t4. The default placement policy p3 applies to t4.

ALTER PLACEMENT POLICY p3 FOLLOWERS=3; -- `FOLLOWERS=3` applies to the table attached with policy p3 (that is, table t4).
```

Note that the policy inheritance from a table to its partitions differs from the policy inheritance in the preceding example. When you change the default policy of a table, the new policy also applies to partitions in that table. However, a table inherits the policy from the database only if it is created without any policy specified. Once a table inherits the policy from the database, modifying the default policy of the database does not apply to that table.
### Specify a placement policy for a table

You can specify a default placement policy for a table. For example:

```sql
CREATE PLACEMENT POLICY five_replicas FOLLOWERS=4;

CREATE TABLE t (a INT) PLACEMENT POLICY=five_replicas;  -- Creates a table t and attaches the 'five_replicas' placement policy to it.

ALTER TABLE t PLACEMENT POLICY=default; -- Removes the placement policy 'five_replicas' from the table t and resets the placement policy to the default one.
```
### Specify a placement policy for a partitioned table

You can also specify a placement policy for a partitioned table or a partition. For example:

```sql
CREATE PLACEMENT POLICY storageforhisotrydata CONSTRAINTS="[+node=history]";
CREATE PLACEMENT POLICY storagefornewdata CONSTRAINTS="[+node=new]";
CREATE PLACEMENT POLICY companystandardpolicy CONSTRAINTS="";

CREATE TABLE t1 (id INT, name VARCHAR(50), purchased DATE)
PLACEMENT POLICY=companystandardpolicy
PARTITION BY RANGE( YEAR(purchased) ) (
  PARTITION p0 VALUES LESS THAN (2000) PLACEMENT POLICY=storageforhisotrydata,
  PARTITION p1 VALUES LESS THAN (2005),
  PARTITION p2 VALUES LESS THAN (2010),
  PARTITION p3 VALUES LESS THAN (2015),
  PARTITION p4 VALUES LESS THAN MAXVALUE PLACEMENT POLICY=storagefornewdata
);
```

If no placement policy is specified for a partition in a table, the partition attempts to inherit the policy (if any) from the table. In the preceding example:

- The `p0` partition will apply the `storageforhisotrydata` policy.
- The `p4` partition will apply the `storagefornewdata` policy.
- The `p1`, `p2`, and `p3` partitions will apply the `companystandardpolicy` placement policy inherited from the table `t1`.
- If no placement policy is specified for the table `t1`, the `p1`, `p2`, and `p3` partitions will inherit the database default policy or the global default policy.

After placement policies are attached to these partitions, you can change the placement policy for a specific partition as in the following example:

```sql
ALTER TABLE t1 PARTITION p1 PLACEMENT POLICY=storageforhisotrydata;
```
