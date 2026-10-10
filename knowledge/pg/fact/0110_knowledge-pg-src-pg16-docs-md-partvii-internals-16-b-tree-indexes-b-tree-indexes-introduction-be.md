# Introduction; Behavior; Deduplication; Bottom-up Index Deletion; Equalimage; Implementation

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVII_internals/16_b-tree_indexes.md`
- Source Title: `B-Tree Indexes`
- Source Heading Path: `B-Tree Indexes > Introduction; Behavior; Deduplication; Bottom-up Index Deletion; Equalimage; Implementation`
- Source Line Ranges: `3-19, 20-111, 279-405`
- Chunk ID: `pg16_fact_0110_9006636f27`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bff08ce7c1ed37517ec953ddf98e3ee158df1e9a00638544f5f5847d934ce689`

## Retrieval Guidance

- Use When: Understand PostgreSQL B-tree index internals, operator classes, or storage behavior.
- Retrieval Keywords: B-tree index, deduplication, bottom-up index deletion, equalimage, operator class, nbtree
- Follow-up Guidance: Use amcheck or pageinspect records when confirming corruption or page-level symptoms.
- Classification Note: The chapter explains B-tree access-method semantics and internal implementation details.

## Official Source Content

## Introduction

PostgreSQL includes an implementation of the
standard btree (multi-way balanced tree) index data
structure.  Any data type that can be sorted into a well-defined linear
order can be indexed by a btree index.  The only limitation is that an
index entry cannot exceed approximately one-third of a page (after TOAST
compression, if applicable).

Because each btree operator class imposes a sort order on its data type,
btree operator classes (or, really, operator families) have come to be
used as PostgreSQL's general representation
and understanding of sorting semantics.  Therefore, they've acquired
some features that go beyond what would be needed just to support btree
indexes, and parts of the system that are quite distant from the
btree AM make use of them.

## Behavior of B-Tree Operator Classes

As shown in [xindex-btree-strat-table](#xindex-btree-strat-table), a btree operator
class must provide five comparison operators,
`<`,
`<=`,
`=`,
`>=` and
`>`.
One might expect that `<>` should also be part of
the operator class, but it is not, because it would almost never be
useful to use a `<>` WHERE clause in an index
search.  (For some purposes, the planner treats `<>`
as associated with a btree operator class; but it finds that operator via
the `=` operator's negator link, rather than
from `pg_amop`.)

When several data types share near-identical sorting semantics, their
operator classes can be grouped into an operator family.  Doing so is
advantageous because it allows the planner to make deductions about
cross-type comparisons.  Each operator class within the family should
contain the single-type operators (and associated support functions)
for its input data type, while cross-type comparison operators and
support functions are "loose" in the family.  It is
recommendable that a complete set of cross-type operators be included
in the family, thus ensuring that the planner can represent any
comparison conditions that it deduces from transitivity.

There are some basic assumptions that a btree operator family must
satisfy:

- An `=` operator must be an equivalence relation; that
is, for all non-null values `A`,
`B`, `C` of the
data type:

`A` `=`
`A` is true
(*reflexive law*)
- if `A` `=`
`B`,
then `B` `=`
`A`
(*symmetric law*)
- if `A` `=`
`B` and `B`
`=` `C`,
then `A` `=`
`C`
(*transitive law*)

A `<` operator must be a strong ordering relation;
that is, for all non-null values `A`,
`B`, `C`:

- `A` `

Furthermore, the ordering is total; that is, for all non-null
values `A`, `B`:

- exactly one of `A` `

The other three operators are defined in terms of `=`
and `<` in the obvious way, and must act consistently
with them.

For an operator family supporting multiple data types, the above laws must
hold when `A`, `B`,
`C` are taken from any data types in the family.
The transitive laws are the trickiest to ensure, as in cross-type
situations they represent statements that the behaviors of two or three
different operators are consistent.
As an example, it would not work to put `float8`
and `numeric` into the same operator family, at least not with
the current semantics that `numeric` values are converted
to `float8` for comparison to a `float8`.  Because
of the limited accuracy of `float8`, this means there are
distinct `numeric` values that will compare equal to the
same `float8` value, and thus the transitive law would fail.

Another requirement for a multiple-data-type family is that any implicit
or binary-coercion casts that are defined between data types included in
the operator family must not change the associated sort ordering.

It should be fairly clear why a btree index requires these laws to hold
within a single data type: without them there is no ordering to arrange
the keys with.  Also, index searches using a comparison key of a
different data type require comparisons to behave sanely across two
data types.  The extensions to three or more data types within a family
are not strictly required by the btree index mechanism itself, but the
planner relies on them for optimization purposes.

### Deduplication

A duplicate is a leaf page tuple (a tuple that points to a table
row) where *all* indexed key columns have values
that match corresponding column values from at least one other leaf
page tuple in the same index.  Duplicate tuples are quite common in
practice.  B-Tree indexes can use a special, space-efficient
representation for duplicates when an optional technique is
enabled: *deduplication*.

Deduplication works by periodically merging groups of duplicate
tuples together, forming a single *posting list* tuple for each
group.  The column key value(s) only appear once in this
representation.  This is followed by a sorted array of
TIDs that point to rows in the table.  This
significantly reduces the storage size of indexes where each value
(or each distinct combination of column values) appears several
times on average.  The latency of queries can be reduced
significantly.  Overall query throughput may increase
significantly.  The overhead of routine index vacuuming may also be
reduced significantly.

> **Note:**

> B-Tree deduplication is just as effective with
> "duplicates" that contain a NULL value, even though
> NULL values are never equal to each other according to the
> `=` member of any B-Tree operator class.  As far
> as any part of the implementation that understands the on-disk
> B-Tree structure is concerned, NULL is just another value from the
> domain of indexed values.
>

The deduplication process occurs lazily, when a new item is
inserted that cannot fit on an existing leaf page, though only when
index tuple deletion could not free sufficient space for the new
item (typically deletion is briefly considered and then skipped
over).  Unlike GIN posting list tuples, B-Tree posting list tuples
do not need to expand every time a new duplicate is inserted; they
are merely an alternative physical representation of the original
logical contents of the leaf page.  This design prioritizes
consistent performance with mixed read-write workloads.  Most
client applications will at least see a moderate performance
benefit from using deduplication.  Deduplication is enabled by
default.

`CREATE INDEX` and `REINDEX`
apply deduplication to create posting list tuples, though the
strategy they use is slightly different.  Each group of duplicate
ordinary tuples encountered in the sorted input taken from the
table is merged into a posting list tuple
*before* being added to the current pending leaf
page.  Individual posting list tuples are packed with as many
TIDs as possible.  Leaf pages are written out in
the usual way, without any separate deduplication pass.  This
strategy is well-suited to `CREATE INDEX` and
`REINDEX` because they are once-off batch
operations.

Write-heavy workloads that don't benefit from deduplication due to
having few or no duplicate values in indexes will incur a small,
fixed performance penalty (unless deduplication is explicitly
disabled).  The `deduplicate_items` storage
parameter can be used to disable deduplication within individual
indexes.  There is never any performance penalty with read-only
workloads, since reading posting list tuples is at least as
efficient as reading the standard tuple representation.  Disabling
deduplication isn't usually helpful.

It is sometimes possible for unique indexes (as well as unique
constraints) to use deduplication.  This allows leaf pages to
temporarily "absorb" extra version churn duplicates.
Deduplication in unique indexes augments bottom-up index deletion,
especially in cases where a long-running transaction holds a
snapshot that blocks garbage collection.  The goal is to buy time
for the bottom-up index deletion strategy to become effective
again.  Delaying page splits until a single long-running
transaction naturally goes away can allow a bottom-up deletion pass
to succeed where an earlier deletion pass failed.

> **Tip:**

> A special heuristic is applied to determine whether a
> deduplication pass in a unique index should take place.  It can
> often skip straight to splitting a leaf page, avoiding a
> performance penalty from wasting cycles on unhelpful deduplication
> passes.  If you're concerned about the overhead of deduplication,
> consider setting `deduplicate_items = off`
> selectively.  Leaving deduplication enabled in unique indexes has
> little downside.
>

Deduplication cannot be used in all cases due to
implementation-level restrictions.  Deduplication safety is
determined when `CREATE INDEX` or
`REINDEX` is run.

Note that deduplication is deemed unsafe and cannot be used in the
following cases involving semantically significant differences
among equal datums:

- `text`, `varchar`, and `char`
cannot use deduplication when a
*nondeterministic* collation is used.  Case
and accent differences must be preserved among equal datums.
- `numeric` cannot use deduplication.  Numeric display
scale must be preserved among equal datums.
- `jsonb` cannot use deduplication, since the
`jsonb` B-Tree operator class uses
`numeric` internally.
- `float4` and `float8` cannot use
deduplication.  These types have distinct representations for
`-0` and `0`, which are
nevertheless considered equal.  This difference must be
preserved.

There is one further implementation-level restriction that may be
lifted in a future version of
PostgreSQL:

- Container types (such as composite types, arrays, or range
types) cannot use deduplication.

There is one further implementation-level restriction that applies
regardless of the operator class or collation used:

- `INCLUDE` indexes can never use deduplication.
