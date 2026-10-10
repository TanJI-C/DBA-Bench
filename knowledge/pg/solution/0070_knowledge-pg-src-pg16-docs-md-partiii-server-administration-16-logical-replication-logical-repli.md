# Warning: Combining Column Lists from Multiple Publications

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/16_logical_replication.md`
- Source Title: `Logical Replication`
- Source Heading Path: `Logical Replication > Warning: Combining Column Lists from Multiple Publications`
- Source Line Ranges: `1093-1209`
- Chunk ID: `pg16_solution_0070_018978eb7b`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b3afbafff86fb59ded406d4fb2615815afccf6f96444f79ef30fd493c09b19b8`

## Retrieval Guidance

- Use When: 订阅多个 publication 后同表 column list 不一致导致 subscriber 报错。
- Retrieval Keywords: combining column lists, multiple publications column list mismatch, ALTER SUBSCRIPTION DROP PUBLICATION, resume replication
- Follow-up Guidance: 统一 publisher 端 column list，或移除并重新添加 offending publication/重建 subscription。
- Classification Note: 说明不同 column lists 导致订阅错误时恢复复制的修复路径。

## Official Source Content

## Warning: Combining Column Lists from Multiple Publications

There's currently no support for subscriptions comprising several
publications where the same table has been published with different
column lists.  [sql-createsubscription](#sql-createsubscription) disallows
creating such subscriptions, but it is still possible to get into
that situation by adding or altering column lists on the publication
side after a subscription has been created.

This means changing the column lists of tables on publications that are
already subscribed could lead to errors being thrown on the subscriber
side.

If a subscription is affected by this problem, the only way to resume
replication is to adjust one of the column lists on the publication
side so that they all match; and then either recreate the subscription,
or use `ALTER SUBSCRIPTION ... DROP PUBLICATION` to
remove one of the offending publications and add it again.

### Examples

Create a table `t1` to be used in the following example.

```
test_pub=# CREATE TABLE t1(id int, a text, b text, c text, d text, e text, PRIMARY KEY(id));
CREATE TABLE
```

Create a publication `p1`. A column list is defined for
table `t1` to reduce the number of columns that will be
replicated. Notice that the order of column names in the column list does
not matter.

```
test_pub=# CREATE PUBLICATION p1 FOR TABLE t1 (id, b, a, d);
CREATE PUBLICATION
```

`psql` can be used to show the column lists (if defined)
for each publication.

```
test_pub=# \dRp+
Publication p1
Owner   | All tables | Inserts | Updates | Deletes | Truncates | Via root
----------+------------+---------+---------+---------+-----------+----------
postgres | f          | t       | t       | t       | t         | f
Tables:
"public.t1" (id, a, b, d)
```

`psql` can be used to show the column lists (if defined)
for each table.

```
test_pub=# \d t1
Table "public.t1"
Column |  Type   | Collation | Nullable | Default
--------+---------+-----------+----------+---------
id     | integer |           | not null |
a      | text    |           |          |
b      | text    |           |          |
c      | text    |           |          |
d      | text    |           |          |
e      | text    |           |          |
Indexes:
"t1_pkey" PRIMARY KEY, btree (id)
Publications:
"p1" (id, a, b, d)
```

On the subscriber node, create a table `t1` which now
only needs a subset of the columns that were on the publisher table
`t1`, and also create the subscription
`s1` that subscribes to the publication
`p1`.

```
test_sub=# CREATE TABLE t1(id int, b text, a text, d text, PRIMARY KEY(id));
CREATE TABLE
test_sub=# CREATE SUBSCRIPTION s1
test_sub-# CONNECTION 'host=localhost dbname=test_pub application_name=s1'
test_sub-# PUBLICATION p1;
CREATE SUBSCRIPTION
```

On the publisher node, insert some rows to table `t1`.

```
test_pub=# INSERT INTO t1 VALUES(1, 'a-1', 'b-1', 'c-1', 'd-1', 'e-1');
INSERT 0 1
test_pub=# INSERT INTO t1 VALUES(2, 'a-2', 'b-2', 'c-2', 'd-2', 'e-2');
INSERT 0 1
test_pub=# INSERT INTO t1 VALUES(3, 'a-3', 'b-3', 'c-3', 'd-3', 'e-3');
INSERT 0 1
test_pub=# SELECT * FROM t1 ORDER BY id;
id |  a  |  b  |  c  |  d  |  e
----+-----+-----+-----+-----+-----
1 | a-1 | b-1 | c-1 | d-1 | e-1
2 | a-2 | b-2 | c-2 | d-2 | e-2
3 | a-3 | b-3 | c-3 | d-3 | e-3
(3 rows)
```

Only data from the column list of publication `p1` is
replicated.

```
test_sub=# SELECT * FROM t1 ORDER BY id;
id |  b  |  a  |  d
----+-----+-----+-----
1 | b-1 | a-1 | d-1
2 | b-2 | a-2 | d-2
3 | b-3 | a-3 | d-3
(3 rows)
```
