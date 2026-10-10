# Partial Indexes; Setting up a Partial Index to Exclude Common Values; Setting up a Partial Unique Index; Do Not Use Partial Indexes as a Substitute for Partitioning

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/08_indexes.md`
- Source Title: `Indexes`
- Source Heading Path: `Indexes > Partial Indexes; Setting up a Partial Index to Exclude Common Values; Setting up a Partial Unique Index; Do Not Use Partial Indexes as a Substitute for Partitioning`
- Source Line Ranges: `583-601, 602-676, 677-719, 720-757`
- Chunk ID: `pg16_solution_0113_dd64e0e815`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b287bca7f546d69f7555131bef6c96556a0ab4da7b243c492e2dd89709a59bc5`

## Retrieval Guidance

- Use When: Root cause is index bloat or poor selectivity where only a subset of rows should be indexed, or uniqueness applies only conditionally.
- Retrieval Keywords: partial index, predicate index, exclude common values, partial unique index, conditional uniqueness, partitioning substitute
- Follow-up Guidance: Confirm query predicates imply the partial-index predicate; otherwise the planner cannot use it.
- Classification Note: Provides partial-index design patterns for excluding common values, enforcing conditional uniqueness, and avoiding misuse as a partitioning substitute.

## Official Source Content

## Partial Indexes

A *partial index* is an index built over a
subset of a table; the subset is defined by a conditional
expression (called the *predicate* of the
partial index).  The index contains entries only for those table
rows that satisfy the predicate.  Partial indexes are a specialized
feature, but there are several situations in which they are useful.

One major reason for using a partial index is to avoid indexing common
values.  Since a query searching for a common value (one that
accounts for more than a few percent of all the table rows) will not
use the index anyway, there is no point in keeping those rows in the
index at all.  This reduces the size of the index, which will speed
up those queries that do use the index.  It will also speed up many table
update operations because the index does not need to be
updated in all cases.  [indexes-partial-ex1](#indexes-partial-ex1) shows a
possible application of this idea.

## Setting up a Partial Index to Exclude Common Values

Suppose you are storing web server access logs in a database.
Most accesses originate from the IP address range of your organization but
some are from elsewhere (say, employees on dial-up connections).
If your searches by IP are primarily for outside accesses,
you probably do not need to index the IP range that corresponds to your
organization's subnet.

Assume a table like this:

```
CREATE TABLE access_log (
url varchar,
client_ip inet,
...
);
```

To create a partial index that suits our example, use a command
such as this:

```
CREATE INDEX access_log_client_ip_ix ON access_log (client_ip)
WHERE NOT (client_ip > inet '192.168.100.0' AND
client_ip  5000.00;
```

This is not as efficient as a partial index on the
`amount` column would be, since the system has to
scan the entire index.  Yet, if there are relatively few unbilled
orders, using this partial index just to find the unbilled orders
could be a win.

Note that this query cannot use this index:

```
SELECT * FROM orders WHERE order_nr = 3501;
```

The order 3501 might be among the billed or unbilled
orders.

[indexes-partial-ex2](#indexes-partial-ex2) also illustrates that the
indexed column and the column used in the predicate do not need to
match.  PostgreSQL supports partial
indexes with arbitrary predicates, so long as only columns of the
table being indexed are involved.  However, keep in mind that the
predicate must match the conditions used in the queries that
are supposed to benefit from the index.  To be precise, a partial
index can be used in a query only if the system can recognize that
the `WHERE` condition of the query mathematically implies
the predicate of the index.
PostgreSQL does not have a sophisticated
theorem prover that can recognize mathematically equivalent
expressions that are written in different forms.  (Not
only is such a general theorem prover extremely difficult to
create, it would probably be too slow to be of any real use.)
The system can recognize simple inequality implications, for example
"x < 1" implies "x < 2"; otherwise
the predicate condition must exactly match part of the query's
`WHERE` condition
or the index will not be recognized as usable. Matching takes
place at query planning time, not at run time. As a result,
parameterized query clauses do not work with a partial index. For
example a prepared query with a parameter might specify
"x < ?" which will never imply
"x < 2" for all possible values of the parameter.

A third possible use for partial indexes does not require the
index to be used in queries at all.  The idea here is to create
a unique index over a subset of a table, as in [indexes-partial-ex3](#indexes-partial-ex3).  This enforces uniqueness
among the rows that satisfy the index predicate, without constraining
those that do not.

## Setting up a Partial Unique Index

Suppose that we have a table describing test outcomes.  We wish
to ensure that there is only one "successful" entry for
a given subject and target combination, but there might be any number of
"unsuccessful" entries.  Here is one way to do it:

```
CREATE TABLE tests (
subject text,
target text,
success boolean,
...
);

CREATE UNIQUE INDEX tests_success_constraint ON tests (subject, target)
WHERE success;
```

This is a particularly efficient approach when there are few
successful tests and many unsuccessful ones.  It is also possible to
allow only one null in a column by creating a unique partial index
with an `IS NULL` restriction.

Finally, a partial index can also be used to override the system's
query plan choices.  Also, data sets with peculiar
distributions might cause the system to use an index when it really
should not.  In that case the index can be set up so that it is not
available for the offending query.  Normally,
PostgreSQL makes reasonable choices about index
usage (e.g., it avoids them when retrieving common values, so the
earlier example really only saves index size, it is not required to
avoid index usage), and grossly incorrect plan choices are cause
for a bug report.

Keep in mind that setting up a partial index indicates that you
know at least as much as the query planner knows, in particular you
know when an index might be profitable.  Forming this knowledge
requires experience and understanding of how indexes in
PostgreSQL work.  In most cases, the
advantage of a partial index over a regular index will be minimal.
There are cases where they are quite counterproductive, as in [indexes-partial-ex4](#indexes-partial-ex4).

## Do Not Use Partial Indexes as a Substitute for Partitioning

You might be tempted to create a large set of non-overlapping partial
indexes, for example

```
CREATE INDEX mytable_cat_1 ON mytable (data) WHERE category = 1;
CREATE INDEX mytable_cat_2 ON mytable (data) WHERE category = 2;
CREATE INDEX mytable_cat_3 ON mytable (data) WHERE category = 3;
...
CREATE INDEX mytable_cat_`N` ON mytable (data) WHERE category = `N`;
```

This is a bad idea!  Almost certainly, you'll be better off with a
single non-partial index, declared like

```
CREATE INDEX mytable_cat_data ON mytable (category, data);
```

(Put the category column first, for the reasons described in
[indexes-multicolumn](#indexes-multicolumn).)  While a search in this larger
index might have to descend through a couple more tree levels than a
search in a smaller index, that's almost certainly going to be cheaper
than the planner effort needed to select the appropriate one of the
partial indexes.  The core of the problem is that the system does not
understand the relationship among the partial indexes, and will
laboriously test each one to see if it's applicable to the current
query.

If your table is large enough that a single index really is a bad idea,
you should look into using partitioning instead (see
[ddl-partitioning](#ddl-partitioning)).  With that mechanism, the system
does understand that the tables and indexes are non-overlapping, so
far better performance is possible.

More information about partial indexes can be found in [ston89b](#ston89b), [olson93](#olson93), and [seshadri95](#seshadri95).
