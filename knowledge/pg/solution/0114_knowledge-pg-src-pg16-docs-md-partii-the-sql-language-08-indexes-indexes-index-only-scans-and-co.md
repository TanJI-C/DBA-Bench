# Index-Only Scans and Covering Indexes

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/08_indexes.md`
- Source Title: `Indexes`
- Source Heading Path: `Indexes > Index-Only Scans and Covering Indexes`
- Source Line Ranges: `758-864`
- Chunk ID: `pg16_solution_0114_07e3a75a27`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `144427f03d294e669c5eecd4c89e429bacd4b2d712854928ba9dbc673092d55b`

## Retrieval Guidance

- Use When: Root cause is excessive heap access for read-heavy queries that could be served from indexes.
- Retrieval Keywords: index-only scan, covering index, INCLUDE, visibility map, heap fetch, payload column
- Follow-up Guidance: Check VACUUM/visibility-map state and EXPLAIN output for Heap Fetches.
- Classification Note: Explains covering indexes with INCLUDE columns, visibility-map dependency, payload-column tradeoffs, and how to enable index-only scans.

## Official Source Content

## Index-Only Scans and Covering Indexes

All indexes in PostgreSQL
are *secondary* indexes, meaning that each index is
stored separately from the table's main data area (which is called the
table's *heap*
in PostgreSQL terminology).  This means that
in an ordinary index scan, each row retrieval requires fetching data from
both the index and the heap.  Furthermore, while the index entries that
match a given indexable `WHERE` condition are usually
close together in the index, the table rows they reference might be
anywhere in the heap.  The heap-access portion of an index scan thus
involves a lot of random access into the heap, which can be slow,
particularly on traditional rotating media.  (As described in
[indexes-bitmap-scans](#indexes-bitmap-scans), bitmap scans try to alleviate
this cost by doing the heap accesses in sorted order, but that only goes
so far.)

To solve this performance problem, PostgreSQL
supports *index-only scans*, which can answer
queries from an index alone without any heap access.  The basic idea is
to return values directly out of each index entry instead of consulting
the associated heap entry.  There are two fundamental restrictions on
when this method can be used:

1. The index type must support index-only scans.  B-tree indexes always
do.  GiST and SP-GiST indexes support index-only scans for some
operator classes but not others.  Other index types have no support.
The underlying requirement is that the index must physically store, or
else be able to reconstruct, the original data value for each index
entry.  As a counterexample, GIN indexes cannot support index-only
scans because each index entry typically holds only part of the
original data value.
2. The query must reference only columns stored in the index.  For
example, given an index on columns `x`
and `y` of a table that also has a
column `z`, these queries could use index-only scans:

```
SELECT x, y FROM tab WHERE x = 'key';
SELECT x FROM tab WHERE x = 'key' AND y `, or `>=` comparisons
to use an index.  Such queries cannot use the
``xxx`_pattern_ops`
operator classes.  (Ordinary equality comparisons can use these
operator classes, however.)  It is possible to create multiple
indexes on the same column with different operator classes.
If you do use the C locale, you do not need the
``xxx`_pattern_ops`
operator classes, because an index with the default operator class
is usable for pattern-matching queries in the C locale.

The following query shows all defined operator classes:

```
SELECT am.amname AS index_method,
opc.opcname AS opclass_name,
opc.opcintype::regtype AS indexed_type,
opc.opcdefault AS is_default
FROM pg_am am, pg_opclass opc
WHERE opc.opcmethod = am.oid
ORDER BY index_method, opclass_name;
```

An operator class is actually just a subset of a larger structure called an
*operator family*.  In cases where several data types have
similar behaviors, it is frequently useful to define cross-data-type
operators and allow these to work with indexes.  To do this, the operator
classes for each of the types must be grouped into the same operator
family.  The cross-type operators are members of the family, but are not
associated with any single class within the family.

This expanded version of the previous query shows the operator family
each operator class belongs to:

```
SELECT am.amname AS index_method,
opc.opcname AS opclass_name,
opf.opfname AS opfamily_name,
opc.opcintype::regtype AS indexed_type,
opc.opcdefault AS is_default
FROM pg_am am, pg_opclass opc, pg_opfamily opf
WHERE opc.opcmethod = am.oid AND
opc.opcfamily = opf.oid
ORDER BY index_method, opclass_name;
```

This query shows all defined operator families and all
the operators included in each family:

```
SELECT am.amname AS index_method,
opf.opfname AS opfamily_name,
amop.amopopr::regoperator AS opfamily_operator
FROM pg_am am, pg_opfamily opf, pg_amop amop
WHERE opf.opfmethod = am.oid AND
amop.amopfamily = opf.oid
ORDER BY index_method, opfamily_name, opfamily_operator;
```

> **Tip:**

> [app-psql](#app-psql) has
> commands `\dAc`, `\dAf`,
> and `\dAo`, which provide slightly more sophisticated
> versions of these queries.
>
