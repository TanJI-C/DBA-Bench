# Column Lists

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/16_logical_replication.md`
- Source Title: `Logical Replication`
- Source Heading Path: `Logical Replication > Column Lists`
- Source Line Ranges: `1047-1092, 1093-1209`
- Chunk ID: `pg16_configuration_0141_a00076200a`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5cfbe0cb86a9de103818255b78880b1989d429119d942619e2a2a5ba2ce96ec5`

## Retrieval Guidance

- Use When: 需要只复制部分列或解释 subscriber 表列匹配/缺列行为。
- Retrieval Keywords: column lists, published columns, CREATE PUBLICATION column list, replica identity columns, publish_via_partition_root
- Follow-up Guidance: UPDATE/DELETE publication 必须包含 replica identity 列。
- Classification Note: 解释 publication column list、replica identity 列要求和分区列列表选择。

## Official Source Content

## Column Lists

Each publication can optionally specify which columns of each table are
replicated to subscribers. The table on the subscriber side must have at
least all the columns that are published. If no column list is specified,
then all columns on the publisher are replicated.
See [sql-createpublication](#sql-createpublication) for details on the syntax.

The choice of columns can be based on behavioral or performance reasons.
However, do not rely on this feature for security: a malicious subscriber
is able to obtain data from columns that are not specifically
published.  If security is a consideration, protections can be applied
at the publisher side.

If no column list is specified, any columns added to the table later are
automatically replicated. This means that having a column list which names
all columns is not the same as having no column list at all.

A column list can contain only simple column references.  The order
of columns in the list is not preserved.

Specifying a column list when the publication also publishes
[`FOR TABLES IN SCHEMA`](#sql-createpublication-for-tables-in-schema)
is not supported.

For partitioned tables, the publication parameter
[`publish_via_partition_root`](#sql-createpublication-with-publish-via-partition-root)
determines which column list is used. If `publish_via_partition_root`
is `true`, the root partitioned table's column list is
used. Otherwise, if `publish_via_partition_root` is
`false` (the default), each partition's column list is used.

If a publication publishes `UPDATE` or
`DELETE` operations, any column list must include the
table's replica identity columns (see
[sql-altertable-replica-identity](#sql-altertable-replica-identity)).
If a publication publishes only `INSERT` operations, then
the column list may omit replica identity columns.

Column lists have no effect for the `TRUNCATE` command.

During initial data synchronization, only the published columns are
copied.  However, if the subscriber is from a release prior to 15, then
all the columns in the table are copied during initial data synchronization,
ignoring any column lists.

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
