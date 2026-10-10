# Create, view, modify, and drop placement policies

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/placement-rules-in-sql.md`
- Source Title: `Placement Rules in SQL`
- Source Heading Path: `Placement Rules in SQL > Usage | Placement Rules in SQL > Usage > Create and attach placement policies | Placement Rules in SQL > Usage > View placement policies | Placement Rules in SQL > Usage > Modify placement policies | Placement Rules in SQL > Usage > Drop placement policies | Placement Rules in SQL > Placement option reference`
- Source Line Ranges: `87-203`
- Source Scope: `all`
- Primary Component: `sql`
- Related Components: `pd`, `tidb`
- Topic Tags: `create-placement-policy`, `attach-policy`, `show-placement`, `information-schema`, `alter-placement-policy`, `drop-placement-policy`, `placement-options`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0191_d7305521a4`
- Source ID: `tidb-docs-8.1:placement-rules-in-sql.md#usage`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `baf676e8902aa7269376a776a1a3de98fb069d777600602bb171c258670125ac`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/placement-rules-in-sql#usage
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/placement-rules-in-sql.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how to create, attach, inspect, modify, or drop placement policies with SQL, or how to view policy definitions and attachment status in system metadata.
- Retrieval Keywords: CREATE PLACEMENT POLICY, ALTER PLACEMENT POLICY, DROP PLACEMENT POLICY, SHOW CREATE PLACEMENT POLICY, SHOW CREATE TABLE, SHOW PLACEMENT, INFORMATION_SCHEMA.PLACEMENT_POLICIES, information_schema.tables, information_schema.partitions, tidb_placement_policy_name, PLACEMENT POLICY=myplacementpolicy, PRIMARY_REGION="us-east-1", REGIONS="us-east-1,us-west-1", FOLLOWERS=4, placement option reference, CONSTRAINTS, SCHEDULE
- Follow-up Guidance: It notes that placement policies are applied asynchronously and that `SHOW PLACEMENT` can be used to check scheduling progress.
- Classification Note: This is operation content because it provides the SQL statements and examples for managing placement policies and viewing their effects.

## Official Source Content

## Usage

This section describes how to create, attach, view, modify, and delete placement policies using SQL statements.
### Create and attach placement policies

1. To create a placement policy, use the [`CREATE PLACEMENT POLICY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-create-placement-policy) statement:

    ```sql
    CREATE PLACEMENT POLICY myplacementpolicy PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1";
    ```

    In this statement:

    - The `PRIMARY_REGION="us-east-1"` option means placing Raft Leaders on nodes with the `region` label as `us-east-1`.
    - The `REGIONS="us-east-1,us-west-1"` option means placing Raft Followers on nodes with the `region` label as `us-east-1` and nodes with the `region` label as `us-west-1`.

    For more configurable placement options and their meanings, see the [Placement options](#placement-option-reference).

2. To attach a placement policy to a table or a partitioned table, use the `CREATE TABLE` or `ALTER TABLE` statement to specify the placement policy for that table or partitioned table:

    ```sql
    CREATE TABLE t1 (a INT) PLACEMENT POLICY=myplacementpolicy;
    CREATE TABLE t2 (a INT);
    ALTER TABLE t2 PLACEMENT POLICY=myplacementpolicy;
    ```

   `PLACEMENT POLICY` is not associated with any database schema and can be attached in a global scope. Therefore, specifying a placement policy using `CREATE TABLE` does not require any additional privileges.
### View placement policies

- To view an existing placement policy, you can use the [`SHOW CREATE PLACEMENT POLICY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-placement-policy) statement:

    ```sql
    SHOW CREATE PLACEMENT POLICY myplacementpolicy\G
    *************************** 1. row ***************************
           Policy: myplacementpolicy
    Create Policy: CREATE PLACEMENT POLICY myplacementpolicy PRIMARY_REGION="us-east-1" REGIONS="us-east-1,us-west-1"
    1 row in set (0.00 sec)
    ```

- To view the placement policy attached to a specific table, you can use the [`SHOW CREATE TABLE`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-create-table) statement:

    ```sql
    SHOW CREATE TABLE t1\G
    *************************** 1. row ***************************
           Table: t1
    Create Table: CREATE TABLE `t1` (
      `a` int(11) DEFAULT NULL
    ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin /*T![placement] PLACEMENT POLICY=`myplacementpolicy` */
    1 row in set (0.00 sec)
    ```

- To view the definitions of placement policies in a cluster, you can query the [`INFORMATION_SCHEMA.PLACEMENT_POLICIES`](https://docs.pingcap.com/tidb/stable/information-schema/information-schema-placement-policies) system table:

    ```sql
    SELECT * FROM information_schema.placement_policies\G
    ***************************[ 1. row ]***************************
    POLICY_ID            | 1
    CATALOG_NAME         | def
    POLICY_NAME          | p1
    PRIMARY_REGION       | us-east-1
    REGIONS              | us-east-1,us-west-1
    CONSTRAINTS          |
    LEADER_CONSTRAINTS   |
    FOLLOWER_CONSTRAINTS |
    LEARNER_CONSTRAINTS  |
    SCHEDULE             |
    FOLLOWERS            | 4
    LEARNERS             | 0
    1 row in set
    ```

- To view all tables that are attached with placement policies in a cluster, you can query the `tidb_placement_policy_name` column of the `information_schema.tables` system table:

    ```sql
    SELECT * FROM information_schema.tables WHERE tidb_placement_policy_name IS NOT NULL;
    ```

- To view all partitions that are attached with placement policies in a cluster, you can query the `tidb_placement_policy_name` column of the `information_schema.partitions` system table:

    ```sql
    SELECT * FROM information_schema.partitions WHERE tidb_placement_policy_name IS NOT NULL;
    ```

- Placement policies attached to all objects are applied *asynchronously*. To check the scheduling progress of placement policies, you can use the [`SHOW PLACEMENT`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-show-placement) statement:

    ```sql
    SHOW PLACEMENT;
    ```
### Modify placement policies

To modify a placement policy, you can use the  [`ALTER PLACEMENT POLICY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-placement-policy) statement. The modification will apply to all objects that are attached with the corresponding policy.

```sql
ALTER PLACEMENT POLICY myplacementpolicy FOLLOWERS=4;
```

In this statement, the `FOLLOWERS=4` option means configuring 5 replicas for the data, including 4 Followers and 1 Leader. For more configurable placement options and their meanings, see [Placement option reference](#placement-option-reference).
### Drop placement policies

To drop a policy that is not attached to any table or partition, you can use the [`DROP PLACEMENT POLICY`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-drop-placement-policy) statement:

```sql
DROP PLACEMENT POLICY myplacementpolicy;
```
## Placement option reference

When creating or modifying placement policies, you can configure placement options as needed.

> **Note:**
>
> The `PRIMARY_REGION`, `REGIONS`, and `SCHEDULE` options cannot be specified together with the `CONSTRAINTS` option, or an error will occur.
