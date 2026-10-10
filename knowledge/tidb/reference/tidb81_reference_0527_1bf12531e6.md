# ALTER RESOURCE GROUP examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-alter-resource-group.md`
- Source Title: `ALTER RESOURCE GROUP`
- Source Heading Path: `ALTER RESOURCE GROUP > Examples`
- Source Line Ranges: `93-174`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `resource-groups`, `examples`, `ddl`, `query-limit`, `background-tasks`, `information-schema`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0527_1bf12531e6`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-alter-resource-group.md#examples`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `27ce54af13fb4e803af78ff9590e4ba09b19ddfbb6bec3fa4827f7390929046f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-alter-resource-group#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-alter-resource-group.md

## Retrieval Guidance

- Use When: Use this chunk when you need concrete ALTER RESOURCE GROUP examples, including changing RU_PER_SEC, PRIORITY, QUERY_LIMIT, modifying BACKGROUND on the default resource group, and verifying results in information_schema.resource_groups.
- Retrieval Keywords: ALTER RESOURCE GROUP rg1, CREATE RESOURCE GROUP IF NOT EXISTS rg1, DROP RESOURCE GROUP IF EXISTS rg1, information_schema.resource_groups, SELECT * FROM information_schema.resource_groups WHERE NAME ='rg1', SELECT * FROM information_schema.resource_groups WHERE NAME ='default', RU_PER_SEC = 200, PRIORITY = LOW, QUERY_LIMIT = (EXEC_ELAPSED='1s' ACTION=COOLDOWN WATCH=EXACT DURATION '30s'), ALTER RESOURCE GROUP default BACKGROUND = (TASK_TYPES = "br,ddl"), TASK_TYPES='br,ddl'
- Follow-up Guidance: The examples show the resulting rows in information_schema.resource_groups for rg1 and default after the ALTER RESOURCE GROUP statements are executed.
- Classification Note: This is reference content because it provides official SQL examples and their observed outputs for altering resource group properties and checking them in information_schema.resource_groups.

## Official Source Content

## Examples

Create a resource group named `rg1` and modify its properties.

```sql
DROP RESOURCE GROUP IF EXISTS rg1;
```

```
Query OK, 0 rows affected (0.22 sec)
```

```sql
CREATE RESOURCE GROUP IF NOT EXISTS rg1
  RU_PER_SEC = 100
  BURSTABLE;
```

```sql
Query OK, 0 rows affected (0.08 sec)
```

```sql
SELECT * FROM information_schema.resource_groups WHERE NAME ='rg1';
```

```sql
+------+------------+----------+-----------+-------------+------------+
| NAME | RU_PER_SEC | PRIORITY | BURSTABLE | QUERY_LIMIT | BACKGROUND |
+------+------------+----------+-----------+-------------+------------+
| rg1  | 100        | MEDIUM   | NO        | NULL        | NULL       |
+------+------------+----------+-----------+-------------+------------+
1 rows in set (1.30 sec)
```

```sql
ALTER RESOURCE GROUP rg1
  RU_PER_SEC = 200
  PRIORITY = LOW
  QUERY_LIMIT = (EXEC_ELAPSED='1s' ACTION=COOLDOWN WATCH=EXACT DURATION '30s');
```

```sql
Query OK, 0 rows affected (0.08 sec)
```

```sql
SELECT * FROM information_schema.resource_groups WHERE NAME ='rg1';
```

```sql
+------+------------+----------+-----------+----------------------------------------------------------------+------------+
| NAME | RU_PER_SEC | PRIORITY | BURSTABLE | QUERY_LIMIT                                                    | BACKGROUND |
+------+------------+----------+-----------+----------------------------------------------------------------+------------+
| rg1  | 200        | LOW      | NO        | EXEC_ELAPSED='1s', ACTION=COOLDOWN, WATCH=EXACT DURATION='30s' | NULL       |
+------+------------+----------+-----------+----------------------------------------------------------------+------------+
1 rows in set (1.30 sec)
```

Modify the `BACKGROUND` option for the `default` resource group.

```sql
ALTER RESOURCE GROUP default BACKGROUND = (TASK_TYPES = "br,ddl");
```

```sql
Query OK, 0 rows affected (0.08 sec)
```

```sql
SELECT * FROM information_schema.resource_groups WHERE NAME ='default';
```

```sql
+---------+------------+----------+-----------+-------------+---------------------+
| NAME    | RU_PER_SEC | PRIORITY | BURSTABLE | QUERY_LIMIT | BACKGROUND          |
+---------+------------+----------+-----------+-------------+---------------------+
| default | UNLIMITED  | MEDIUM   | YES       | NULL        | TASK_TYPES='br,ddl' |
+---------+------------+----------+-----------+-------------+---------------------+
1 rows in set (1.30 sec)
```
