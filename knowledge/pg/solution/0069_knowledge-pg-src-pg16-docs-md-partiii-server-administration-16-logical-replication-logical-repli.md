# Examples

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/16_logical_replication.md`
- Source Title: `Logical Replication`
- Source Heading Path: `Logical Replication > Row Filters > Examples`
- Source Line Ranges: `220-411, 412-537, 538-1046, 1112-1209`
- Chunk ID: `pg16_solution_0069_1235360ce8`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `eb95fc41d9e63b7867cf8da2bb597920047775f84daacac554bd85c4ebd121be`

## Retrieval Guidance

- Use When: 需要按示例验证 row filter 配置和 subscriber 数据结果。
- Retrieval Keywords: row filter examples, \dRp+, \d table publications, filtered replication example, partition filter example
- Follow-up Guidance: 用 \dRp+ 和 \d 检查 publication 对表的实际过滤条件。
- Classification Note: 通过 psql 示例演示 row filter、组合过滤和分区过滤的验证方式。

## Official Source Content

### Examples: Set Up Logical Replication

Create some test tables on the publisher.

```
test_pub=# CREATE TABLE t1(a int, b text, PRIMARY KEY(a));
CREATE TABLE
test_pub=# CREATE TABLE t2(c int, d text, PRIMARY KEY(c));
CREATE TABLE
test_pub=# CREATE TABLE t3(e int, f text, PRIMARY KEY(e));
CREATE TABLE
```

Create the same tables on the subscriber.

```
test_sub=# CREATE TABLE t1(a int, b text, PRIMARY KEY(a));
CREATE TABLE
test_sub=# CREATE TABLE t2(c int, d text, PRIMARY KEY(c));
CREATE TABLE
test_sub=# CREATE TABLE t3(e int, f text, PRIMARY KEY(e));
CREATE TABLE
```

Insert data to the tables at the publisher side.

```
test_pub=# INSERT INTO t1 VALUES (1, 'one'), (2, 'two'), (3, 'three');
INSERT 0 3
test_pub=# INSERT INTO t2 VALUES (1, 'A'), (2, 'B'), (3, 'C');
INSERT 0 3
test_pub=# INSERT INTO t3 VALUES (1, 'i'), (2, 'ii'), (3, 'iii');
INSERT 0 3
```

Create publications for the tables. The publications `pub2`
and `pub3a` disallow some
[`publish`](#sql-createpublication-with-publish)
operations. The publication `pub3b` has a row filter (see
[logical-replication-row-filter](#logical-replication-row-filter)).

```
test_pub=# CREATE PUBLICATION pub1 FOR TABLE t1;
CREATE PUBLICATION
test_pub=# CREATE PUBLICATION pub2 FOR TABLE t2 WITH (publish = 'truncate');
CREATE PUBLICATION
test_pub=# CREATE PUBLICATION pub3a FOR TABLE t3 WITH (publish = 'truncate');
CREATE PUBLICATION
test_pub=# CREATE PUBLICATION pub3b FOR TABLE t3 WHERE (e > 5);
CREATE PUBLICATION
```

Create subscriptions for the publications. The subscription
`sub3` subscribes to both `pub3a` and
`pub3b`. All subscriptions will copy initial data by default.

```
test_sub=# CREATE SUBSCRIPTION sub1
test_sub-# CONNECTION 'host=localhost dbname=test_pub application_name=sub1'
test_sub-# PUBLICATION pub1;
CREATE SUBSCRIPTION
test_sub=# CREATE SUBSCRIPTION sub2
test_sub-# CONNECTION 'host=localhost dbname=test_pub application_name=sub2'
test_sub-# PUBLICATION pub2;
CREATE SUBSCRIPTION
test_sub=# CREATE SUBSCRIPTION sub3
test_sub-# CONNECTION 'host=localhost dbname=test_pub application_name=sub3'
test_sub-# PUBLICATION pub3a, pub3b;
CREATE SUBSCRIPTION
```

Observe that initial table data is copied, regardless of the
`publish` operation of the publication.

```
test_sub=# SELECT * FROM t1;
a |   b
---+-------
1 | one
2 | two
3 | three
(3 rows)

test_sub=# SELECT * FROM t2;
c | d
---+---
1 | A
2 | B
3 | C
(3 rows)
```

Furthermore, because the initial data copy ignores the `publish`
operation, and because publication `pub3a` has no row filter,
it means the copied table `t3` contains all rows even when
they do not match the row filter of publication `pub3b`.

```
test_sub=# SELECT * FROM t3;
e |  f
---+-----
1 | i
2 | ii
3 | iii
(3 rows)
```

Insert more data to the tables at the publisher side.

```
test_pub=# INSERT INTO t1 VALUES (4, 'four'), (5, 'five'), (6, 'six');
INSERT 0 3
test_pub=# INSERT INTO t2 VALUES (4, 'D'), (5, 'E'), (6, 'F');
INSERT 0 3
test_pub=# INSERT INTO t3 VALUES (4, 'iv'), (5, 'v'), (6, 'vi');
INSERT 0 3
```

Now the publisher side data looks like:

```
test_pub=# SELECT * FROM t1;
a |   b
---+-------
1 | one
2 | two
3 | three
4 | four
5 | five
6 | six
(6 rows)

test_pub=# SELECT * FROM t2;
c | d
---+---
1 | A
2 | B
3 | C
4 | D
5 | E
6 | F
(6 rows)

test_pub=# SELECT * FROM t3;
e |  f
---+-----
1 | i
2 | ii
3 | iii
4 | iv
5 | v
6 | vi
(6 rows)
```

Observe that during normal replication the appropriate
`publish` operations are used. This means publications
`pub2` and `pub3a` will not replicate the
`INSERT`. Also, publication `pub3b` will
only replicate data that matches the row filter of `pub3b`.
Now the subscriber side data looks like:

```
test_sub=# SELECT * FROM t1;
a |   b
---+-------
1 | one
2 | two
3 | three
4 | four
5 | five
6 | six
(6 rows)

test_sub=# SELECT * FROM t2;
c | d
---+---
1 | A
2 | B
3 | C
(3 rows)

test_sub=# SELECT * FROM t3;
e |  f
---+-----
1 | i
2 | ii
3 | iii
6 | vi
(4 rows)
```

### Examples: Deferred Replication Slot Creation

There are some cases (e.g.
[logical-replication-subscription-slot](#logical-replication-subscription-slot)) where, if the
remote replication slot was not created automatically, the user must create
it manually before the subscription can be activated. The steps to create
the slot and activate the subscription are shown in the following examples.
These examples specify the standard logical decoding output plugin
(`pgoutput`), which is what the built-in logical
replication uses.

First, create a publication for the examples to use.

```
test_pub=# CREATE PUBLICATION pub1 FOR ALL TABLES;
CREATE PUBLICATION
```

Example 1: Where the subscription says `connect = false`

- Create the subscription.

```
test_sub=# CREATE SUBSCRIPTION sub1
test_sub-# CONNECTION 'host=localhost dbname=test_pub'
test_sub-# PUBLICATION pub1
test_sub-# WITH (connect=false);
WARNING:  subscription was created, but is not connected
HINT:  To initiate replication, you must manually create the replication slot, enable the subscription, and refresh the subscription.
CREATE SUBSCRIPTION
```
- On the publisher, manually create a slot. Because the name was not
specified during `CREATE SUBSCRIPTION`, the name of the
slot to create is same as the subscription name, e.g. "sub1".

```
test_pub=# SELECT * FROM pg_create_logical_replication_slot('sub1', 'pgoutput');
slot_name |    lsn
-----------+-----------
sub1      | 0/19404D0
(1 row)
```
- On the subscriber, complete the activation of the subscription. After
this the tables of `pub1` will start replicating.

```
test_sub=# ALTER SUBSCRIPTION sub1 ENABLE;
ALTER SUBSCRIPTION
test_sub=# ALTER SUBSCRIPTION sub1 REFRESH PUBLICATION;
ALTER SUBSCRIPTION
```

Example 2: Where the subscription says `connect = false`,
but also specifies the
[`slot_name`](#sql-createsubscription-with-slot-name)
option.

- Create the subscription.

```
test_sub=# CREATE SUBSCRIPTION sub1
test_sub-# CONNECTION 'host=localhost dbname=test_pub'
test_sub-# PUBLICATION pub1
test_sub-# WITH (connect=false, slot_name='myslot');
WARNING:  subscription was created, but is not connected
HINT:  To initiate replication, you must manually create the replication slot, enable the subscription, and refresh the subscription.
CREATE SUBSCRIPTION
```
- On the publisher, manually create a slot using the same name that was
specified during `CREATE SUBSCRIPTION`, e.g. "myslot".

```
test_pub=# SELECT * FROM pg_create_logical_replication_slot('myslot', 'pgoutput');
slot_name |    lsn
-----------+-----------
myslot    | 0/19059A0
(1 row)
```
- On the subscriber, the remaining subscription activation steps are the
same as before.

```
test_sub=# ALTER SUBSCRIPTION sub1 ENABLE;
ALTER SUBSCRIPTION
test_sub=# ALTER SUBSCRIPTION sub1 REFRESH PUBLICATION;
ALTER SUBSCRIPTION
```

Example 3: Where the subscription specifies `slot_name = NONE`

- Create the subscription. When `slot_name = NONE` then
`enabled = false`, and
`create_slot = false` are also needed.

```
test_sub=# CREATE SUBSCRIPTION sub1
test_sub-# CONNECTION 'host=localhost dbname=test_pub'
test_sub-# PUBLICATION pub1
test_sub-# WITH (slot_name=NONE, enabled=false, create_slot=false);
CREATE SUBSCRIPTION
```
- On the publisher, manually create a slot using any name, e.g. "myslot".

```
test_pub=# SELECT * FROM pg_create_logical_replication_slot('myslot', 'pgoutput');
slot_name |    lsn
-----------+-----------
myslot    | 0/1905930
(1 row)
```
- On the subscriber, associate the subscription with the slot name just
created.

```
test_sub=# ALTER SUBSCRIPTION sub1 SET (slot_name='myslot');
ALTER SUBSCRIPTION
```
- The remaining subscription activation steps are same as before.

```
test_sub=# ALTER SUBSCRIPTION sub1 ENABLE;
ALTER SUBSCRIPTION
test_sub=# ALTER SUBSCRIPTION sub1 REFRESH PUBLICATION;
ALTER SUBSCRIPTION
```

## Row Filters

By default, all data from all published tables will be replicated to the
appropriate subscribers. The replicated data can be reduced by using a
*row filter*. A user might choose to use row filters
for behavioral, security or performance reasons. If a published table sets a
row filter, a row is replicated only if its data satisfies the row filter
expression. This allows a set of tables to be partially replicated. The row
filter is defined per table. Use a `WHERE` clause after the
table name for each published table that requires data to be filtered out.
The `WHERE` clause must be enclosed by parentheses. See
[sql-createpublication](#sql-createpublication) for details.

### Row Filter Rules

Row filters are applied *before* publishing the changes.
If the row filter evaluates to `false` or `NULL`
then the row is not replicated. The `WHERE` clause expression
is evaluated with the same role used for the replication connection (i.e.
the role specified in the
[`CONNECTION`](#sql-createsubscription-connection)
clause of the [sql-createsubscription](#sql-createsubscription)). Row filters have
no effect for `TRUNCATE` command.

### Expression Restrictions

The `WHERE` clause allows only simple expressions. It
cannot contain user-defined functions, operators, types, and collations,
system column references or non-immutable built-in functions.

If a publication publishes `UPDATE` or
`DELETE` operations, the row filter `WHERE`
clause must contain only columns that are covered by the replica identity
(see [sql-altertable-replica-identity](#sql-altertable-replica-identity)). If a publication
publishes only `INSERT` operations, the row filter
`WHERE` clause can use any column.

### UPDATE Transformations

Whenever an `UPDATE` is processed, the row filter
expression is evaluated for both the old and new row (i.e. using the data
before and after the update). If both evaluations are `true`,
it replicates the `UPDATE` change. If both evaluations are
`false`, it doesn't replicate the change. If only one of
the old/new rows matches the row filter expression, the `UPDATE`
is transformed to `INSERT` or `DELETE`, to
avoid any data inconsistency. The row on the subscriber should reflect what
is defined by the row filter expression on the publisher.

If the old row satisfies the row filter expression (it was sent to the
subscriber) but the new row doesn't, then, from a data consistency
perspective the old row should be removed from the subscriber.
So the `UPDATE` is transformed into a `DELETE`.

If the old row doesn't satisfy the row filter expression (it wasn't sent
to the subscriber) but the new row does, then, from a data consistency
perspective the new row should be added to the subscriber.
So the `UPDATE` is transformed into an `INSERT`.

[logical-replication-row-filter-transformations-summary](#logical-replication-row-filter-transformations-summary)
summarizes the applied transformations.

| Old row | New row | Transformation |
| --- | --- | --- |
| no match | no match | don't replicate |
| no match | match | `INSERT` |
| match | no match | `DELETE` |
| match | match | `UPDATE` |

### Partitioned Tables

If the publication contains a partitioned table, the publication parameter
[`publish_via_partition_root`](#sql-createpublication-with-publish-via-partition-root)
determines which row filter is used. If `publish_via_partition_root`
is `true`, the *root partitioned table's*
row filter is used. Otherwise, if `publish_via_partition_root`
is `false` (default), each *partition's*
row filter is used.

### Initial Data Synchronization

If the subscription requires copying pre-existing table data
and a publication contains `WHERE` clauses, only data that
satisfies the row filter expressions is copied to the subscriber.

If the subscription has several publications in which a table has been
published with different `WHERE` clauses, rows that satisfy
*any* of the expressions will be copied. See
[logical-replication-row-filter-combining](#logical-replication-row-filter-combining) for details.

> **Warning:**

> Because initial data synchronization does not take into account the
> [`publish`](#sql-createpublication-with-publish)
> parameter when copying existing table data, some rows may be copied that
> would not be replicated using DML. Refer to
> [logical-replication-snapshot](#logical-replication-snapshot), and see
> [logical-replication-subscription-examples](#logical-replication-subscription-examples) for examples.
>

> **Note:**

> If the subscriber is in a release prior to 15, copying pre-existing data
> doesn't use row filters even if they are defined in the publication.
> This is because old releases can only copy the entire table data.
>

### Combining Multiple Row Filters

If the subscription has several publications in which the same table has
been published with different row filters (for the same
[`publish`](#sql-createpublication-with-publish)
operation), those expressions get ORed together, so that rows satisfying
*any* of the expressions will be replicated. This means all
the other row filters for the same table become redundant if:

- One of the publications has no row filter.
- One of the publications was created using
[`FOR ALL TABLES`](#sql-createpublication-for-all-tables).
This clause does not allow row filters.
- One of the publications was created using
[`FOR TABLES IN SCHEMA`](#sql-createpublication-for-tables-in-schema)
and the table belongs to the referred schema. This clause does not allow
row filters.

### Examples

Create some tables to be used in the following examples.

```
test_pub=# CREATE TABLE t1(a int, b int, c text, PRIMARY KEY(a,c));
CREATE TABLE
test_pub=# CREATE TABLE t2(d int, e int, f int, PRIMARY KEY(d));
CREATE TABLE
test_pub=# CREATE TABLE t3(g int, h int, i int, PRIMARY KEY(g));
CREATE TABLE
```

Create some publications. Publication `p1` has one table
(`t1`) and that table has a row filter. Publication
`p2` has two tables. Table `t1` has no row
filter, and table `t2` has a row filter. Publication
`p3` has two tables, and both of them have a row filter.

```
test_pub=# CREATE PUBLICATION p1 FOR TABLE t1 WHERE (a > 5 AND c = 'NSW');
CREATE PUBLICATION
test_pub=# CREATE PUBLICATION p2 FOR TABLE t1, t2 WHERE (e = 99);
CREATE PUBLICATION
test_pub=# CREATE PUBLICATION p3 FOR TABLE t2 WHERE (d = 10), t3 WHERE (g = 10);
CREATE PUBLICATION
```

`psql` can be used to show the row filter expressions (if
defined) for each publication.

```
test_pub=# \dRp+
Publication p1
Owner   | All tables | Inserts | Updates | Deletes | Truncates | Via root
----------+------------+---------+---------+---------+-----------+----------
postgres | f          | t       | t       | t       | t         | f
Tables:
"public.t1" WHERE ((a > 5) AND (c = 'NSW'::text))

Publication p2
Owner   | All tables | Inserts | Updates | Deletes | Truncates | Via root
----------+------------+---------+---------+---------+-----------+----------
postgres | f          | t       | t       | t       | t         | f
Tables:
"public.t1"
"public.t2" WHERE (e = 99)

Publication p3
Owner   | All tables | Inserts | Updates | Deletes | Truncates | Via root
----------+------------+---------+---------+---------+-----------+----------
postgres | f          | t       | t       | t       | t         | f
Tables:
"public.t2" WHERE (d = 10)
"public.t3" WHERE (g = 10)
```

`psql` can be used to show the row filter expressions (if
defined) for each table. See that table `t1` is a member
of two publications, but has a row filter only in `p1`.
See that table `t2` is a member of two publications, and
has a different row filter in each of them.

```
test_pub=# \d t1
Table "public.t1"
Column |  Type   | Collation | Nullable | Default
--------+---------+-----------+----------+---------
a      | integer |           | not null |
b      | integer |           |          |
c      | text    |           | not null |
Indexes:
"t1_pkey" PRIMARY KEY, btree (a, c)
Publications:
"p1" WHERE ((a > 5) AND (c = 'NSW'::text))
"p2"

test_pub=# \d t2
Table "public.t2"
Column |  Type   | Collation | Nullable | Default
--------+---------+-----------+----------+---------
d      | integer |           | not null |
e      | integer |           |          |
f      | integer |           |          |
Indexes:
"t2_pkey" PRIMARY KEY, btree (d)
Publications:
"p2" WHERE (e = 99)
"p3" WHERE (d = 10)

test_pub=# \d t3
Table "public.t3"
Column |  Type   | Collation | Nullable | Default
--------+---------+-----------+----------+---------
g      | integer |           | not null |
h      | integer |           |          |
i      | integer |           |          |
Indexes:
"t3_pkey" PRIMARY KEY, btree (g)
Publications:
"p3" WHERE (g = 10)
```

On the subscriber node, create a table `t1` with the same
definition as the one on the publisher, and also create the subscription
`s1` that subscribes to the publication `p1`.

```
test_sub=# CREATE TABLE t1(a int, b int, c text, PRIMARY KEY(a,c));
CREATE TABLE
test_sub=# CREATE SUBSCRIPTION s1
test_sub-# CONNECTION 'host=localhost dbname=test_pub application_name=s1'
test_sub-# PUBLICATION p1;
CREATE SUBSCRIPTION
```

Insert some rows. Only the rows satisfying the `t1 WHERE`
clause of publication `p1` are replicated.

```
test_pub=# INSERT INTO t1 VALUES (2, 102, 'NSW');
INSERT 0 1
test_pub=# INSERT INTO t1 VALUES (3, 103, 'QLD');
INSERT 0 1
test_pub=# INSERT INTO t1 VALUES (4, 104, 'VIC');
INSERT 0 1
test_pub=# INSERT INTO t1 VALUES (5, 105, 'ACT');
INSERT 0 1
test_pub=# INSERT INTO t1 VALUES (6, 106, 'NSW');
INSERT 0 1
test_pub=# INSERT INTO t1 VALUES (7, 107, 'NT');
INSERT 0 1
test_pub=# INSERT INTO t1 VALUES (8, 108, 'QLD');
INSERT 0 1
test_pub=# INSERT INTO t1 VALUES (9, 109, 'NSW');
INSERT 0 1

test_pub=# SELECT * FROM t1;
a |  b  |  c
---+-----+-----
2 | 102 | NSW
3 | 103 | QLD
4 | 104 | VIC
5 | 105 | ACT
6 | 106 | NSW
7 | 107 | NT
8 | 108 | QLD
9 | 109 | NSW
(8 rows)
```

```
test_sub=# SELECT * FROM t1;
a |  b  |  c
---+-----+-----
6 | 106 | NSW
9 | 109 | NSW
(2 rows)
```

Update some data, where the old and new row values both
satisfy the `t1 WHERE` clause of publication
`p1`. The `UPDATE` replicates
the change as normal.

```
test_pub=# UPDATE t1 SET b = 999 WHERE a = 6;
UPDATE 1

test_pub=# SELECT * FROM t1;
a |  b  |  c
---+-----+-----
2 | 102 | NSW
3 | 103 | QLD
4 | 104 | VIC
5 | 105 | ACT
7 | 107 | NT
8 | 108 | QLD
9 | 109 | NSW
6 | 999 | NSW
(8 rows)
```

```
test_sub=# SELECT * FROM t1;
a |  b  |  c
---+-----+-----
9 | 109 | NSW
6 | 999 | NSW
(2 rows)
```

Update some data, where the old row values did not satisfy
the `t1 WHERE` clause of publication `p1`,
but the new row values do satisfy it. The `UPDATE` is
transformed into an `INSERT` and the change is replicated.
See the new row on the subscriber.

```
test_pub=# UPDATE t1 SET a = 555 WHERE a = 2;
UPDATE 1

test_pub=# SELECT * FROM t1;
a  |  b  |  c
-----+-----+-----
3 | 103 | QLD
4 | 104 | VIC
5 | 105 | ACT
7 | 107 | NT
8 | 108 | QLD
9 | 109 | NSW
6 | 999 | NSW
555 | 102 | NSW
(8 rows)
```

```
test_sub=# SELECT * FROM t1;
a  |  b  |  c
-----+-----+-----
9 | 109 | NSW
6 | 999 | NSW
555 | 102 | NSW
(3 rows)
```

Update some data, where the old row values satisfied
the `t1 WHERE` clause of publication `p1`,
but the new row values do not satisfy it. The `UPDATE` is
transformed into a `DELETE` and the change is replicated.
See that the row is removed from the subscriber.

```
test_pub=# UPDATE t1 SET c = 'VIC' WHERE a = 9;
UPDATE 1

test_pub=# SELECT * FROM t1;
a  |  b  |  c
-----+-----+-----
3 | 103 | QLD
4 | 104 | VIC
5 | 105 | ACT
7 | 107 | NT
8 | 108 | QLD
6 | 999 | NSW
555 | 102 | NSW
9 | 109 | VIC
(8 rows)
```

```
test_sub=# SELECT * FROM t1;
a  |  b  |  c
-----+-----+-----
6 | 999 | NSW
555 | 102 | NSW
(2 rows)
```

The following examples show how the publication parameter
[`publish_via_partition_root`](#sql-createpublication-with-publish-via-partition-root)
determines whether the row filter of the parent or child table will be used
in the case of partitioned tables.

Create a partitioned table on the publisher.

```
test_pub=# CREATE TABLE parent(a int PRIMARY KEY) PARTITION BY RANGE(a);
CREATE TABLE
test_pub=# CREATE TABLE child PARTITION OF parent DEFAULT;
CREATE TABLE
```

Create the same tables on the subscriber.

```
test_sub=# CREATE TABLE parent(a int PRIMARY KEY) PARTITION BY RANGE(a);
CREATE TABLE
test_sub=# CREATE TABLE child PARTITION OF parent DEFAULT;
CREATE TABLE
```

Create a publication `p4`, and then subscribe to it. The
publication parameter `publish_via_partition_root` is set
as true. There are row filters defined on both the partitioned table
(`parent`), and on the partition (`child`).

```
test_pub=# CREATE PUBLICATION p4 FOR TABLE parent WHERE (a = 5)
test_pub-# WITH (publish_via_partition_root=true);
CREATE PUBLICATION
```

```
test_sub=# CREATE SUBSCRIPTION s4
test_sub-# CONNECTION 'host=localhost dbname=test_pub application_name=s4'
test_sub-# PUBLICATION p4;
CREATE SUBSCRIPTION
```

Insert some values directly into the `parent` and
`child` tables. They replicate using the row filter of
`parent` (because `publish_via_partition_root`
is true).

```
test_pub=# INSERT INTO parent VALUES (2), (4), (6);
INSERT 0 3
test_pub=# INSERT INTO child VALUES (3), (5), (7);
INSERT 0 3

test_pub=# SELECT * FROM parent ORDER BY a;
a
---
2
3
4
5
6
7
(6 rows)
```

```
test_sub=# SELECT * FROM parent ORDER BY a;
a
---
2
3
4
(3 rows)
```

Repeat the same test, but with a different value for `publish_via_partition_root`.
The publication parameter `publish_via_partition_root` is
set as false. A row filter is defined on the partition (`child`).

```
test_pub=# DROP PUBLICATION p4;
DROP PUBLICATION
test_pub=# CREATE PUBLICATION p4 FOR TABLE parent, child WHERE (a >= 5)
test_pub-# WITH (publish_via_partition_root=false);
CREATE PUBLICATION
```

```
test_sub=# ALTER SUBSCRIPTION s4 REFRESH PUBLICATION;
ALTER SUBSCRIPTION
```

Do the inserts on the publisher same as before. They replicate using the
row filter of `child` (because
`publish_via_partition_root` is false).

```
test_pub=# TRUNCATE parent;
TRUNCATE TABLE
test_pub=# INSERT INTO parent VALUES (2), (4), (6);
INSERT 0 3
test_pub=# INSERT INTO child VALUES (3), (5), (7);
INSERT 0 3

test_pub=# SELECT * FROM parent ORDER BY a;
a
---
2
3
4
5
6
7
(6 rows)
```

```
test_sub=# SELECT * FROM child ORDER BY a;
a
---
5
6
7
(3 rows)
```

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
