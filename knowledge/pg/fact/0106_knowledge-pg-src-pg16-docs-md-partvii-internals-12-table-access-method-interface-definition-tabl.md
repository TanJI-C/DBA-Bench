# Table Access Method Interface Definition

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVII_internals/12_table_access_method_interface_definition.md`
- Source Title: `Table Access Method Interface Definition`
- Source Heading Path: `Table Access Method Interface Definition`
- Source Line Ranges: `1-71`
- Chunk ID: `pg16_fact_0106_2f094c7d7a`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `051685f4f5fc69f1c58d14816b00610d5d6549849a5433ccf811548c991b0d52`

## Retrieval Guidance

- Use When: Implement or understand a PostgreSQL table access method.
- Retrieval Keywords: table access method, TableAmRoutine, heapam, table AM, slot, tuple table
- Follow-up Guidance: Use storage records for physical file layout details.
- Classification Note: The file is an API reference for table access methods and table AM callbacks.

## Official Source Content

# Table Access Method Interface Definition

This chapter explains the interface between the core
PostgreSQL system and *table access
methods*, which manage the storage for tables. The core system
knows little about these access methods beyond what is specified here, so
it is possible to develop entirely new access method types by writing
add-on code.

Each table access method is described by a row in the [`pg_am`](#catalog-pg-am) system
catalog. The `pg_am` entry specifies a name and a
*handler function* for the table access method.  These
entries can be created and deleted using the [sql-create-access-method](#sql-create-access-method) and [sql-drop-access-method](#sql-drop-access-method) SQL commands.

A table access method handler function must be declared to accept a single
argument of type `internal` and to return the pseudo-type
`table_am_handler`.  The argument is a dummy value that simply
serves to prevent handler functions from being called directly from SQL commands.

The result of the function must be a pointer to a struct of type
`TableAmRoutine`, which contains everything that the
core code needs to know to make use of the table access method. The return
value needs to be of server lifetime, which is typically achieved by
defining it as a `static const` variable in global
scope. The `TableAmRoutine` struct, also called the
access method's *API struct*, defines the behavior of
the access method using callbacks. These callbacks are pointers to plain C
functions and are not visible or callable at the SQL level. All the
callbacks and their behavior is defined in the
`TableAmRoutine` structure (with comments inside the
struct defining the requirements for callbacks). Most callbacks have
wrapper functions, which are documented from the point of view of a user
(rather than an implementor) of the table access method.  For details,
please refer to the [
`src/include/access/tableam.h`](https://git.postgresql.org/gitweb/?p=postgresql.git;a=blob;f=src/include/access/tableam.h;hb=HEAD) file.

To implement an access method, an implementor will typically need to
implement an AM-specific type of tuple table slot (see
[
`src/include/executor/tuptable.h`](https://git.postgresql.org/gitweb/?p=postgresql.git;a=blob;f=src/include/executor/tuptable.h;hb=HEAD)), which allows
code outside the access method to hold references to tuples of the AM, and
to access the columns of the tuple.

Currently, the way an AM actually stores data is fairly unconstrained. For
example, it's possible, but not required, to use postgres' shared buffer
cache.  In case it is used, it likely makes sense to use
PostgreSQL's standard page layout as described in
[storage-page-layout](#storage-page-layout).

One fairly large constraint of the table access method API is that,
currently, if the AM wants to support modifications and/or indexes, it is
necessary for each tuple to have a tuple identifier (TID)
consisting of a block number and an item number (see also [storage-page-layout](#storage-page-layout)).  It is not strictly necessary that the
sub-parts of TIDs have the same meaning they e.g., have
for `heap`, but if bitmap scan support is desired (it is
optional), the block number needs to provide locality.

For crash safety, an AM can use postgres' [WAL](#wal), or a custom implementation.
If WAL is chosen, either [Generic WAL Records](#generic-wal) can be used,
or a [Custom WAL Resource Manager](#custom-rmgr) can be
implemented.

To implement transactional support in a manner that allows different table
access methods be accessed within a single transaction, it likely is
necessary to closely integrate with the machinery in
`src/backend/access/transam/xlog.c`.

Any developer of a new `table access method` can refer to
the existing `heap` implementation present in
`src/backend/access/heap/heapam_handler.c` for details of
its implementation.
