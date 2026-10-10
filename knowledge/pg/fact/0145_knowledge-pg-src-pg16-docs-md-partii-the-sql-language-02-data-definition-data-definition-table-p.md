# Overview; Declarative Partitioning; Best Practices for Declarative Partitioning

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/02_data_definition.md`
- Source Title: `Data Definition`
- Source Heading Path: `Data Definition > Table Partitioning > Overview; Declarative Partitioning; Best Practices for Declarative Partitioning`
- Source Line Ranges: `2563-3168`
- Chunk ID: `pg16_fact_0145_b4e7a5ce0a`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9ecd77a124e82813a6204404a385779628ea467fca16bb576535cd7b209dc8de`

## Retrieval Guidance

- Use When: Need facts about partitioning semantics and DDL structure.
- Retrieval Keywords: partitioned table, range partition, list partition, hash partition, partition bounds, partition key
- Follow-up Guidance: Use partition maintenance solution records for attach, detach, drop, and load workflows.
- Classification Note: Explains partitioned table concepts, range/list/hash partitioning, partition bounds, indexes and constraints on partitioned tables, and modeling limits.

## Official Source Content

## Table Partitioning

PostgreSQL supports basic table
partitioning. This section describes why and how to implement
partitioning as part of your database design.

### Overview

Partitioning refers to splitting what is logically one large table into
smaller physical pieces.  Partitioning can provide several benefits:

- Query performance can be improved dramatically in certain situations,
particularly when most of the heavily accessed rows of the table are in a
single partition or a small number of partitions.  Partitioning
effectively substitutes for the upper tree levels of indexes,
making it more likely that the heavily-used parts of the indexes
fit in memory.
- When queries or updates access a large percentage of a single
partition, performance can be improved by using a
sequential scan of that partition instead of using an
index, which would require random-access reads scattered across the
whole table.
- Bulk loads and deletes can be accomplished by adding or removing
partitions, if the usage pattern is accounted for in the
partitioning design.  Dropping an individual partition
using `DROP TABLE`, or doing `ALTER TABLE
DETACH PARTITION`, is far faster than a bulk
operation.  These commands also entirely avoid the
`VACUUM` overhead caused by a bulk `DELETE`.
- Seldom-used data can be migrated to cheaper and slower storage media.

These benefits will normally be worthwhile only when a table would
otherwise be very large. The exact point at which a table will
benefit from partitioning depends on the application, although a
rule of thumb is that the size of the table should exceed the physical
memory of the database server.

PostgreSQL offers built-in support for the
following forms of partitioning:

**Range Partitioning**
: The table is partitioned into "ranges" defined
by a key column or set of columns, with no overlap between
the ranges of values assigned to different partitions.  For
example, one might partition by date ranges, or by ranges of
identifiers for particular business objects.
Each range's bounds are understood as being inclusive at the
lower end and exclusive at the upper end.  For example, if one
partition's range is from `1`
to `10`, and the next one's range is
from `10` to `20`, then
value `10` belongs to the second partition not
the first.

**List Partitioning**
: The table is partitioned by explicitly listing which key value(s)
appear in each partition.

**Hash Partitioning**
: The table is partitioned by specifying a modulus and a remainder for
each partition. Each partition will hold the rows for which the hash
value of the partition key divided by the specified modulus will
produce the specified remainder.

If your application needs to use other forms of partitioning not listed
above, alternative methods such as inheritance and
`UNION ALL` views can be used instead.  Such methods
offer flexibility but do not have some of the performance benefits
of built-in declarative partitioning.

### Declarative Partitioning

PostgreSQL allows you to declare
that a table is divided into partitions.  The table that is divided
is referred to as a *partitioned table*.  The
declaration includes the *partitioning method*
as described above, plus a list of columns or expressions to be used
as the *partition key*.

The partitioned table itself is a "virtual" table having
no storage of its own.  Instead, the storage belongs
to *partitions*, which are otherwise-ordinary
tables associated with the partitioned table.
Each partition stores a subset of the data as defined by its
*partition bounds*.
All rows inserted into a partitioned table will be routed to the
appropriate one of the partitions based on the values of the partition
key column(s).
Updating the partition key of a row will cause it to be moved into a
different partition if it no longer satisfies the partition bounds
of its original partition.

Partitions may themselves be defined as partitioned tables, resulting
in *sub-partitioning*.  Although all partitions
must have the same columns as their partitioned parent, partitions may
have their
own indexes, constraints and default values, distinct from those of other
partitions.  See [sql-createtable](#sql-createtable) for more details on
creating partitioned tables and partitions.

It is not possible to turn a regular table into a partitioned table or
vice versa.  However, it is possible to add an existing regular or
partitioned table as a partition of a partitioned table, or remove a
partition from a partitioned table turning it into a standalone table;
this can simplify and speed up many maintenance processes.
See [sql-altertable](#sql-altertable) to learn more about the
`ATTACH PARTITION` and `DETACH PARTITION`
sub-commands.

Partitions can also be [foreign
tables](#ddl-foreign-data), although considerable care is needed because it is then
the user's responsibility that the contents of the foreign table
satisfy the partitioning rule.  There are some other restrictions as
well.  See [sql-createforeigntable](#sql-createforeigntable) for more
information.

#### Example

Suppose we are constructing a database for a large ice cream company.
The company measures peak temperatures every day as well as ice cream
sales in each region. Conceptually, we want a table like:

```
CREATE TABLE measurement (
city_id         int not null,
logdate         date not null,
peaktemp        int,
unitsales       int
);
```

We know that most queries will access just the last week's, month's or
quarter's data, since the main use of this table will be to prepare
online reports for management.  To reduce the amount of old data that
needs to be stored, we decide to keep only the most recent 3 years
worth of data. At the beginning of each month we will remove the oldest
month's data.  In this situation we can use partitioning to help us meet
all of our different requirements for the measurements table.

To use declarative partitioning in this case, use the following steps:

1. Create the `measurement` table as a partitioned
table by specifying the `PARTITION BY` clause, which
includes the partitioning method (`RANGE` in this
case) and the list of column(s) to use as the partition key.

```
CREATE TABLE measurement (
city_id         int not null,
logdate         date not null,
peaktemp        int,
unitsales       int
) PARTITION BY RANGE (logdate);
```
2. Create partitions.  Each partition's definition must specify bounds
that correspond to the partitioning method and partition key of the
parent.  Note that specifying bounds such that the new partition's
values would overlap with those in one or more existing partitions will
cause an error.

Partitions thus created are in every way normal
PostgreSQL
tables (or, possibly, foreign tables).  It is possible to specify a
tablespace and storage parameters for each partition separately.

For our example, each partition should hold one month's worth of
data, to match the requirement of deleting one month's data at a
time.  So the commands might look like:

```
CREATE TABLE measurement_y2006m02 PARTITION OF measurement
FOR VALUES FROM ('2006-02-01') TO ('2006-03-01');

CREATE TABLE measurement_y2006m03 PARTITION OF measurement
FOR VALUES FROM ('2006-03-01') TO ('2006-04-01');

...
CREATE TABLE measurement_y2007m11 PARTITION OF measurement
FOR VALUES FROM ('2007-11-01') TO ('2007-12-01');

CREATE TABLE measurement_y2007m12 PARTITION OF measurement
FOR VALUES FROM ('2007-12-01') TO ('2008-01-01')
TABLESPACE fasttablespace;

CREATE TABLE measurement_y2008m01 PARTITION OF measurement
FOR VALUES FROM ('2008-01-01') TO ('2008-02-01')
WITH (parallel_workers = 4)
TABLESPACE fasttablespace;
```

(Recall that adjacent partitions can share a bound value, since
range upper bounds are treated as exclusive bounds.)

If you wish to implement sub-partitioning, again specify the
`PARTITION BY` clause in the commands used to create
individual partitions, for example:

```
CREATE TABLE measurement_y2006m02 PARTITION OF measurement
FOR VALUES FROM ('2006-02-01') TO ('2006-03-01')
PARTITION BY RANGE (peaktemp);
```

After creating partitions of `measurement_y2006m02`,
any data inserted into `measurement` that is mapped to
`measurement_y2006m02` (or data that is
directly inserted into `measurement_y2006m02`,
which is allowed provided its partition constraint is satisfied)
will be further redirected to one of its
partitions based on the `peaktemp` column.  The partition
key specified may overlap with the parent's partition key, although
care should be taken when specifying the bounds of a sub-partition
such that the set of data it accepts constitutes a subset of what
the partition's own bounds allow; the system does not try to check
whether that's really the case.

Inserting data into the parent table that does not map
to one of the existing partitions will cause an error; an appropriate
partition must be added manually.

It is not necessary to manually create table constraints describing
the partition boundary conditions for partitions.  Such constraints
will be created automatically.
3. Create an index on the key column(s), as well as any other indexes you
might want, on the partitioned table. (The key index is not strictly
necessary, but in most scenarios it is helpful.)
This automatically creates a matching index on each partition, and
any partitions you create or attach later will also have such an
index.
An index or unique constraint declared on a partitioned table
is "virtual" in the same way that the partitioned table
is: the actual data is in child indexes on the individual partition
tables.

```
CREATE INDEX ON measurement (logdate);
```
4. Ensure that the [guc-enable-partition-pruning](#guc-enable-partition-pruning)
configuration parameter is not disabled in `postgresql.conf`.
If it is, queries will not be optimized as desired.

In the above example we would be creating a new partition each month, so
it might be wise to write a script that generates the required DDL
automatically.

#### Partition Maintenance

Normally the set of partitions established when initially defining the
table is not intended to remain static.  It is common to want to
remove partitions holding old data and periodically add new partitions for
new data. One of the most important advantages of partitioning is
precisely that it allows this otherwise painful task to be executed
nearly instantaneously by manipulating the partition structure, rather
than physically moving large amounts of data around.

The simplest option for removing old data is to drop the partition that
is no longer necessary:

```
DROP TABLE measurement_y2006m02;
```

This can very quickly delete millions of records because it doesn't have
to individually delete every record.  Note however that the above command
requires taking an `ACCESS EXCLUSIVE` lock on the parent
table.

Another option that is often preferable is to remove the partition from
the partitioned table but retain access to it as a table in its own
right.  This has two forms:

```
ALTER TABLE measurement DETACH PARTITION measurement_y2006m02;
ALTER TABLE measurement DETACH PARTITION measurement_y2006m02 CONCURRENTLY;
```

These allow further operations to be performed on the data before
it is dropped. For example, this is often a useful time to back up
the data using `COPY`, pg_dump, or
similar tools. It might also be a useful time to aggregate data
into smaller formats, perform other data manipulations, or run
reports.  The first form of the command requires an
`ACCESS EXCLUSIVE` lock on the parent table.
Adding the `CONCURRENTLY` qualifier as in the second
form allows the detach operation to require only
`SHARE UPDATE EXCLUSIVE` lock on the parent table, but see
[`ALTER TABLE ... DETACH PARTITION`](#sql-altertable-detach-partition)
for details on the restrictions.

Similarly we can add a new partition to handle new data. We can create an
empty partition in the partitioned table just as the original partitions
were created above:

```
CREATE TABLE measurement_y2008m02 PARTITION OF measurement
FOR VALUES FROM ('2008-02-01') TO ('2008-03-01')
TABLESPACE fasttablespace;
```

As an alternative, it is sometimes more convenient to create the
new table outside the partition structure, and attach it as a
partition later. This allows new data to be loaded, checked, and
transformed prior to it appearing in the partitioned table.
Moreover, the `ATTACH PARTITION` operation requires
only `SHARE UPDATE EXCLUSIVE` lock on the
partitioned table, as opposed to the `ACCESS
EXCLUSIVE` lock that is required by `CREATE TABLE
... PARTITION OF`, so it is more friendly to concurrent
operations on the partitioned table.
The `CREATE TABLE ... LIKE` option is helpful
to avoid tediously repeating the parent table's definition:

```
CREATE TABLE measurement_y2008m02
(LIKE measurement INCLUDING DEFAULTS INCLUDING CONSTRAINTS)
TABLESPACE fasttablespace;

ALTER TABLE measurement_y2008m02 ADD CONSTRAINT y2008m02
CHECK ( logdate >= DATE '2008-02-01' AND logdate = 100 AND outletID = DATE '2006-02-01' AND logdate = DATE '2006-03-01' AND logdate = DATE '2007-11-01' AND logdate = DATE '2007-12-01' AND logdate = DATE '2008-01-01' AND logdate = DATE '2006-02-01' AND
NEW.logdate = DATE '2006-03-01' AND
NEW.logdate = DATE '2008-01-01' AND
NEW.logdate

While this function is more complex than the single-month case,
it doesn't need to be updated as often, since branches can be
added in advance of being needed.

> **Note:**
> In practice, it might be best to check the newest child first,
> if most inserts go into that child.  For simplicity, we have
> shown the trigger's tests in the same order as in other parts
> of this example.
>

A different approach to redirecting inserts into the appropriate
child table is to set up rules, instead of a trigger, on the
root table.  For example:

```
CREATE RULE measurement_insert_y2006m02 AS
ON INSERT TO measurement WHERE
( logdate >= DATE '2006-02-01' AND logdate = DATE '2008-01-01' AND logdate

Be aware that `COPY` ignores rules.  If you want to
use `COPY` to insert data, you'll need to copy into the
correct child table rather than directly into the root. `COPY`
does fire triggers, so you can use it normally if you use the trigger
approach.

Another disadvantage of the rule approach is that there is no simple
way to force an error if the set of rules doesn't cover the insertion
date; the data will silently go into the root table instead.
6. Ensure that the [guc-constraint-exclusion](#guc-constraint-exclusion)
configuration parameter is not disabled in
`postgresql.conf`; otherwise
child tables may be accessed unnecessarily.

As we can see, a complex table hierarchy could require a
substantial amount of DDL.  In the above example we would be creating
a new child table each month, so it might be wise to write a script that
generates the required DDL automatically.

#### Maintenance for Inheritance Partitioning

To remove old data quickly, simply drop the child table that is no longer
necessary:

```
DROP TABLE measurement_y2006m02;
```

To remove the child table from the inheritance hierarchy table but retain access to
it as a table in its own right:

```
ALTER TABLE measurement_y2006m02 NO INHERIT measurement;
```

To add a new child table to handle new data, create an empty child table
just as the original children were created above:

```
CREATE TABLE measurement_y2008m02 (
CHECK ( logdate >= DATE '2008-02-01' AND logdate = DATE '2008-02-01' AND logdate = DATE '2008-01-01';
```

Without partition pruning, the above query would scan each of the
partitions of the `measurement` table. With
partition pruning enabled, the planner will examine the definition
of each partition and prove that the partition need not
be scanned because it could not contain any rows meeting the query's
`WHERE` clause.  When the planner can prove this, it
excludes (*prunes*) the partition from the query
plan.

By using the EXPLAIN command and the [guc-enable-partition-pruning](#guc-enable-partition-pruning) configuration parameter, it's
possible to show the difference between a plan for which partitions have
been pruned and one for which they have not.  A typical unoptimized
plan for this type of table setup is:

```
SET enable_partition_pruning = off;
EXPLAIN SELECT count(*) FROM measurement WHERE logdate >= DATE '2008-01-01';
QUERY PLAN
-----------------------------------------------------------------------------------
Aggregate  (cost=188.76..188.77 rows=1 width=8)
->  Append  (cost=0.00..181.05 rows=3085 width=0)
->  Seq Scan on measurement_y2006m02  (cost=0.00..33.12 rows=617 width=0)
Filter: (logdate >= '2008-01-01'::date)
->  Seq Scan on measurement_y2006m03  (cost=0.00..33.12 rows=617 width=0)
Filter: (logdate >= '2008-01-01'::date)
...
->  Seq Scan on measurement_y2007m11  (cost=0.00..33.12 rows=617 width=0)
Filter: (logdate >= '2008-01-01'::date)
->  Seq Scan on measurement_y2007m12  (cost=0.00..33.12 rows=617 width=0)
Filter: (logdate >= '2008-01-01'::date)
->  Seq Scan on measurement_y2008m01  (cost=0.00..33.12 rows=617 width=0)
Filter: (logdate >= '2008-01-01'::date)
```

Some or all of the partitions might use index scans instead of
full-table sequential scans, but the point here is that there
is no need to scan the older partitions at all to answer this query.
When we enable partition pruning, we get a significantly
cheaper plan that will deliver the same answer:

```
SET enable_partition_pruning = on;
EXPLAIN SELECT count(*) FROM measurement WHERE logdate >= DATE '2008-01-01';
QUERY PLAN
-----------------------------------------------------------------------------------
Aggregate  (cost=37.75..37.76 rows=1 width=8)
->  Seq Scan on measurement_y2008m01  (cost=0.00..33.12 rows=617 width=0)
Filter: (logdate >= '2008-01-01'::date)
```

Note that partition pruning is driven only by the constraints defined
implicitly by the partition keys, not by the presence of indexes.
Therefore it isn't necessary to define indexes on the key columns.
Whether an index needs to be created for a given partition depends on
whether you expect that queries that scan the partition will
generally scan a large part of the partition or just a small part.
An index will be helpful in the latter case but not the former.

Partition pruning can be performed not only during the planning of a
given query, but also during its execution.  This is useful as it can
allow more partitions to be pruned when clauses contain expressions
whose values are not known at query planning time, for example,
parameters defined in a `PREPARE` statement, using a
value obtained from a subquery, or using a parameterized value on the
inner side of a nested loop join.  Partition pruning during execution
can be performed at any of the following times:

- During initialization of the query plan.  Partition pruning can be
performed here for parameter values which are known during the
initialization phase of execution.  Partitions which are pruned
during this stage will not show up in the query's
`EXPLAIN` or `EXPLAIN ANALYZE`.
It is possible to determine the number of partitions which were
removed during this phase by observing the
"Subplans Removed" property in the
`EXPLAIN` output.  It's important to note that any
partitions removed by the partition pruning done at this stage are
still locked at the beginning of execution.
- During actual execution of the query plan.  Partition pruning may
also be performed here to remove partitions using values which are
only known during actual query execution.  This includes values
from subqueries and values from execution-time parameters such as
those from parameterized nested loop joins.  Since the value of
these parameters may change many times during the execution of the
query, partition pruning is performed whenever one of the
execution parameters being used by partition pruning changes.
Determining if partitions were pruned during this phase requires
careful inspection of the `loops` property in
the `EXPLAIN ANALYZE` output.  Subplans
corresponding to different partitions may have different values
for it depending on how many times each of them was pruned during
execution.  Some may be shown as `(never executed)`
if they were pruned every time.

Partition pruning can be disabled using the
[guc-enable-partition-pruning](#guc-enable-partition-pruning) setting.

### Partitioning and Constraint Exclusion

*Constraint exclusion* is a query optimization
technique similar to partition pruning.  While it is primarily used
for partitioning implemented using the legacy inheritance method, it can be
used for other purposes, including with declarative partitioning.

Constraint exclusion works in a very similar way to partition
pruning, except that it uses each table's `CHECK`
constraints — which gives it its name — whereas partition
pruning uses the table's partition bounds, which exist only in the
case of declarative partitioning.  Another difference is that
constraint exclusion is only applied at plan time; there is no attempt
to remove partitions at execution time.

The fact that constraint exclusion uses `CHECK`
constraints, which makes it slow compared to partition pruning, can
sometimes be used as an advantage: because constraints can be defined
even on declaratively-partitioned tables, in addition to their internal
partition bounds, constraint exclusion may be able
to elide additional partitions from the query plan.

The default (and recommended) setting of
[guc-constraint-exclusion](#guc-constraint-exclusion) is neither
`on` nor `off`, but an intermediate setting
called `partition`, which causes the technique to be
applied only to queries that are likely to be working on inheritance partitioned
tables.  The `on` setting causes the planner to examine
`CHECK` constraints in all queries, even simple ones that
are unlikely to benefit.

The following caveats apply to constraint exclusion:

- Constraint exclusion is only applied during query planning, unlike
partition pruning, which can also be applied during query execution.
- Constraint exclusion only works when the query's `WHERE`
clause contains constants (or externally supplied parameters).
For example, a comparison against a non-immutable function such as
`CURRENT_TIMESTAMP` cannot be optimized, since the
planner cannot know which child table the function's value might fall
into at run time.
- Keep the partitioning constraints simple, else the planner may not be
able to prove that child tables might not need to be visited.  Use simple
equality conditions for list partitioning, or simple
range tests for range partitioning, as illustrated in the preceding
examples.  A good rule of thumb is that partitioning constraints should
contain only comparisons of the partitioning column(s) to constants
using B-tree-indexable operators, because only B-tree-indexable
column(s) are allowed in the partition key.
- All constraints on all children of the parent table are examined
during constraint exclusion, so large numbers of children are likely
to increase query planning time considerably.  So the legacy
inheritance based partitioning will work well with up to perhaps a
hundred child tables; don't try to use many thousands of children.

### Best Practices for Declarative Partitioning

The choice of how to partition a table should be made carefully, as the
performance of query planning and execution can be negatively affected by
poor design.

One of the most critical design decisions will be the column or columns
by which you partition your data.  Often the best choice will be to
partition by the column or set of columns which most commonly appear in
`WHERE` clauses of queries being executed on the
partitioned table.  `WHERE` clauses that are compatible
with the partition bound constraints can be used to prune unneeded
partitions.  However, you may be forced into making other decisions by
requirements for the `PRIMARY KEY` or a
`UNIQUE` constraint.  Removal of unwanted data is also a
factor to consider when planning your partitioning strategy.  An entire
partition can be detached fairly quickly, so it may be beneficial to
design the partition strategy in such a way that all data to be removed
at once is located in a single partition.

Choosing the target number of partitions that the table should be divided
into is also a critical decision to make.  Not having enough partitions
may mean that indexes remain too large and that data locality remains poor
which could result in low cache hit ratios.  However, dividing the table
into too many partitions can also cause issues.  Too many partitions can
mean longer query planning times and higher memory consumption during both
query planning and execution, as further described below.
When choosing how to partition your table,
it's also important to consider what changes may occur in the future.  For
example, if you choose to have one partition per customer and you
currently have a small number of large customers, consider the
implications if in several years you instead find yourself with a large
number of small customers.  In this case, it may be better to choose to
partition by `HASH` and choose a reasonable number of
partitions rather than trying to partition by `LIST` and
hoping that the number of customers does not increase beyond what it is
practical to partition the data by.

Sub-partitioning can be useful to further divide partitions that are
expected to become larger than other partitions.
Another option is to use range partitioning with multiple columns in
the partition key.
Either of these can easily lead to excessive numbers of partitions,
so restraint is advisable.

It is important to consider the overhead of partitioning during
query planning and execution.  The query planner is generally able to
handle partition hierarchies with up to a few thousand partitions fairly
well, provided that typical queries allow the query planner to prune all
but a small number of partitions.  Planning times become longer and memory
consumption becomes higher when more partitions remain after the planner
performs partition pruning.  Another
reason to be concerned about having a large number of partitions is that
the server's memory consumption may grow significantly over
time, especially if many sessions touch large numbers of partitions.
That's because each partition requires its metadata to be loaded into the
local memory of each session that touches it.

With data warehouse type workloads, it can make sense to use a larger
number of partitions than with an OLTP type workload.
Generally, in data warehouses, query planning time is less of a concern as
the majority of processing time is spent during query execution.  With
either of these two types of workload, it is important to make the right
decisions early, as re-partitioning large quantities of data can be
painfully slow.  Simulations of the intended workload are often beneficial
for optimizing the partitioning strategy.  Never just assume that more
partitions are better than fewer partitions, nor vice-versa.
