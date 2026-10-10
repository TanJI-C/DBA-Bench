# Publication

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/16_logical_replication.md`
- Source Title: `Logical Replication`
- Source Heading Path: `Logical Replication > Publication`
- Source Line Ranges: `48-107, 1093-1209`
- Chunk ID: `pg16_configuration_0134_bb9f186b23`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `aee9b34ed748741497da88d279972d831d8d378312c083fa0cb51e5f6fc34a55`

## Retrieval Guidance

- Use When: 需要配置发布端复制对象、操作类型或 UPDATE/DELETE 所需 identity。
- Retrieval Keywords: publication, CREATE PUBLICATION, publish insert update delete truncate, replica identity, ALTER PUBLICATION
- Follow-up Guidance: 确保发布 UPDATE/DELETE 的表具备合适 replica identity。
- Classification Note: 解释 publication、publish 操作、replica identity 和表加入/移除语义。

## Official Source Content

## Publication

A *publication* can be defined on any physical
replication primary.  The node where a publication is defined is referred to
as *publisher*.  A publication is a set of changes
generated from a table or a group of tables, and might also be described as
a change set or replication set.  Each publication exists in only one database.

Publications are different from schemas and do not affect how the table is
accessed.  Each table can be added to multiple publications if needed.
Publications may currently only contain tables and all tables in schema.
Objects must be added explicitly, except when a publication is created for
`ALL TABLES`.

Publications can choose to limit the changes they produce to
any combination of `INSERT`, `UPDATE`,
`DELETE`, and `TRUNCATE`, similar to how triggers are fired by
particular event types. By default, all operation types are replicated.
These publication specifications apply only for DML operations; they do not affect the initial
data synchronization copy. (Row filters have no effect for
`TRUNCATE`. See [logical-replication-row-filter](#logical-replication-row-filter)).

A published table must have a *replica identity* configured in
order to be able to replicate `UPDATE`
and `DELETE` operations, so that appropriate rows to
update or delete can be identified on the subscriber side.  By default,
this is the primary key, if there is one.  Another unique index (with
certain additional requirements) can also be set to be the replica
identity.  If the table does not have any suitable key, then it can be set
to replica identity `FULL`, which means the entire row becomes
the key.  When replica identity `FULL` is specified,
indexes can be used on the subscriber side for searching the rows.  Candidate
indexes must be btree, non-partial, and the leftmost index field must be a
column (not an expression) that references the published table column.  These
restrictions on the non-unique index properties adhere to some of the
restrictions that are enforced for primary keys.  If there are no such
suitable indexes, the search on the subscriber side can be very inefficient,
therefore replica identity `FULL` should only be used as a
fallback if no other solution is possible.  If a replica identity other
than `FULL` is set on the publisher side, a replica identity
comprising the same or fewer columns must also be set on the subscriber
side.  See [sql-altertable-replica-identity](#sql-altertable-replica-identity) for details on
how to set the replica identity.  If a table without a replica identity is
added to a publication that replicates `UPDATE`
or `DELETE` operations then
subsequent `UPDATE` or `DELETE`
operations will cause an error on the publisher.  `INSERT`
operations can proceed regardless of any replica identity.

Every publication can have multiple subscribers.

A publication is created using the [`CREATE PUBLICATION`](#sql-createpublication)
command and may later be altered or dropped using corresponding commands.

The individual tables can be added and removed dynamically using
[`ALTER PUBLICATION`](#sql-alterpublication).  Both the `ADD
TABLE` and `DROP TABLE` operations are
transactional; so the table will start or stop replicating at the correct
snapshot once the transaction has committed.

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
