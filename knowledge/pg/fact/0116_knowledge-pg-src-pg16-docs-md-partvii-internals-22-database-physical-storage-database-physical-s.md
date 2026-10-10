# Files and Directories; Forks; Pages; TOAST; Free Space Map; Visibility Map; Database Page Layout

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVII_internals/22_database_physical_storage.md`
- Source Title: `Database Physical Storage`
- Source Heading Path: `Database Physical Storage > Files and Directories; Forks; Pages; TOAST; Free Space Map; Visibility Map; Database Page Layout`
- Source Line Ranges: `149-370, 371-396, 397-425, 434-540`
- Chunk ID: `pg16_fact_0116_1901f4849d`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7ee9609cd156d2eea84f236a54eb1734131f45816c8b3ba1125745b2b152a34f`

## Retrieval Guidance

- Use When: Understand storage files, page layout, and relation storage internals.
- Retrieval Keywords: physical storage, base directory, relation fork, TOAST, free space map, visibility map, page layout, ctid
- Follow-up Guidance: Use pageinspect, pg_freespacemap, or pg_visibility records when inspecting live storage evidence.
- Classification Note: The chapter is a reference for PostgreSQL physical storage layout, relation forks, page structure, TOAST, FSM, and visibility maps.

## Official Source Content

## TOAST

This section provides an overview of TOAST (The
Oversized-Attribute Storage Technique).

PostgreSQL uses a fixed page size (commonly
8 kB), and does not allow tuples to span multiple pages.  Therefore, it is
not possible to store very large field values directly.  To overcome
this limitation, large field values are compressed and/or broken up into
multiple physical rows.  This happens transparently to the user, with only
small impact on most of the backend code.  The technique is affectionately
known as TOAST (or "the best thing since sliced bread").
The TOAST infrastructure is also used to improve handling of
large data values in-memory.

Only certain data types support TOAST — there is no need to
impose the overhead on data types that cannot produce large field values.
To support TOAST, a data type must have a variable-length
(*varlena*) representation, in which, ordinarily, the first
four-byte word of any stored value contains the total length of the value in
bytes (including itself).  TOAST does not constrain the rest
of the data type's representation.  The special representations collectively
called *TOASTed values* work by modifying or
reinterpreting this initial length word.  Therefore, the C-level functions
supporting a TOAST-able data type must be careful about how they
handle potentially TOASTed input values: an input might not
actually consist of a four-byte length word and contents until after it's
been *detoasted*.  (This is normally done by invoking
`PG_DETOAST_DATUM` before doing anything with an input value,
but in some cases more efficient approaches are possible.
See [xtypes-toast](#xtypes-toast) for more detail.)

TOAST usurps two bits of the varlena length word (the high-order
bits on big-endian machines, the low-order bits on little-endian machines),
thereby limiting the logical size of any value of a TOAST-able
data type to 1 GB (2^30 - 1 bytes).  When both bits are zero,
the value is an ordinary un-TOASTed value of the data type, and
the remaining bits of the length word give the total datum size (including
length word) in bytes.  When the highest-order or lowest-order bit is set,
the value has only a single-byte header instead of the normal four-byte
header, and the remaining bits of that byte give the total datum size
(including length byte) in bytes.  This alternative supports space-efficient
storage of values shorter than 127 bytes, while still allowing the data type
to grow to 1 GB at need.  Values with single-byte headers aren't aligned on
any particular boundary, whereas values with four-byte headers are aligned on
at least a four-byte boundary; this omission of alignment padding provides
additional space savings that is significant compared to short values.
As a special case, if the remaining bits of a single-byte header are all
zero (which would be impossible for a self-inclusive length), the value is
a pointer to out-of-line data, with several possible alternatives as
described below.  The type and size of such a *TOAST pointer*
are determined by a code stored in the second byte of the datum.
Lastly, when the highest-order or lowest-order bit is clear but the adjacent
bit is set, the content of the datum has been compressed and must be
decompressed before use.  In this case the remaining bits of the four-byte
length word give the total size of the compressed datum, not the
original data.  Note that compression is also possible for out-of-line data
but the varlena header does not tell whether it has occurred —
the content of the TOAST pointer tells that, instead.

The compression technique used for either in-line or out-of-line compressed
data can be selected for each column by setting
the `COMPRESSION` column option in `CREATE
TABLE` or `ALTER TABLE`.  The default for columns
with no explicit setting is to consult the
[guc-default-toast-compression](#guc-default-toast-compression) parameter at the time data is
inserted.

As mentioned, there are multiple types of TOAST pointer datums.
The oldest and most common type is a pointer to out-of-line data stored in
a *TOAST table* that is separate from, but
associated with, the table containing the TOAST pointer datum
itself.  These *on-disk* pointer datums are created by the
TOAST management code (in `access/common/toast_internals.c`)
when a tuple to be stored on disk is too large to be stored as-is.
Further details appear in [storage-toast-ondisk](#storage-toast-ondisk).
Alternatively, a TOAST pointer datum can contain a pointer to
out-of-line data that appears elsewhere in memory.  Such datums are
necessarily short-lived, and will never appear on-disk, but they are very
useful for avoiding copying and redundant processing of large data values.
Further details appear in [storage-toast-inmemory](#storage-toast-inmemory).

### Out-of-Line, On-Disk TOAST Storage

If any of the columns of a table are TOAST-able, the table will
have an associated TOAST table, whose OID is stored in the table's
`pg_class`.`reltoastrelid` entry.  On-disk
TOASTed values are kept in the TOAST table, as
described in more detail below.

Out-of-line values are divided (after compression if used) into chunks of at
most `TOAST_MAX_CHUNK_SIZE` bytes (by default this value is chosen
so that four chunk rows will fit on a page, making it about 2000 bytes).
Each chunk is stored as a separate row in the TOAST table
belonging to the owning table.  Every
TOAST table has the columns `chunk_id` (an OID
identifying the particular TOASTed value),
`chunk_seq` (a sequence number for the chunk within its value),
and `chunk_data` (the actual data of the chunk).  A unique index
on `chunk_id` and `chunk_seq` provides fast
retrieval of the values.  A pointer datum representing an out-of-line on-disk
TOASTed value therefore needs to store the OID of the
TOAST table in which to look and the OID of the specific value
(its `chunk_id`).  For convenience, pointer datums also store the
logical datum size (original uncompressed data length), physical stored size
(different if compression was applied), and the compression method used, if
any.  Allowing for the varlena header bytes,
the total size of an on-disk TOAST pointer datum is therefore 18
bytes regardless of the actual size of the represented value.

The TOAST management code is triggered only
when a row value to be stored in a table is wider than
`TOAST_TUPLE_THRESHOLD` bytes (normally 2 kB).
The TOAST code will compress and/or move
field values out-of-line until the row value is shorter than
`TOAST_TUPLE_TARGET` bytes (also normally 2 kB, adjustable)
or no more gains can be had.  During an UPDATE
operation, values of unchanged fields are normally preserved as-is; so an
UPDATE of a row with out-of-line values incurs no TOAST costs if
none of the out-of-line values change.

The TOAST management code recognizes four different strategies
for storing TOAST-able columns on disk:

- `PLAIN` prevents either compression or
out-of-line storage.  This is the only possible strategy for
columns of non-TOAST-able data types.
- `EXTENDED` allows both compression and out-of-line
storage.  This is the default for most TOAST-able data types.
Compression will be attempted first, then out-of-line storage if
the row is still too big.
- `EXTERNAL` allows out-of-line storage but not
compression.  Use of `EXTERNAL` will
make substring operations on wide `text` and
`bytea` columns faster (at the penalty of increased storage
space) because these operations are optimized to fetch only the
required parts of the out-of-line value when it is not compressed.
- `MAIN` allows compression but not out-of-line
storage.  (Actually, out-of-line storage will still be performed
for such columns, but only as a last resort when there is no other
way to make the row small enough to fit on a page.)

Each TOAST-able data type specifies a default strategy for columns
of that data type, but the strategy for a given table column can be altered
with [`ALTER TABLE ... SET STORAGE`](#sql-altertable).

`TOAST_TUPLE_TARGET` can be adjusted for each table using
[`ALTER TABLE ... SET (toast_tuple_target = N)`](#sql-altertable)

This scheme has a number of advantages compared to a more straightforward
approach such as allowing row values to span pages.  Assuming that queries are
usually qualified by comparisons against relatively small key values, most of
the work of the executor will be done using the main row entry. The big values
of TOASTed attributes will only be pulled out (if selected at all)
at the time the result set is sent to the client. Thus, the main table is much
smaller and more of its rows fit in the shared buffer cache than would be the
case without any out-of-line storage. Sort sets shrink also, and sorts will
more often be done entirely in memory. A little test showed that a table
containing typical HTML pages and their URLs was stored in about half of the
raw data size including the TOAST table, and that the main table
contained only about 10% of the entire data (the URLs and some small HTML
pages). There was no run time difference compared to an un-TOASTed
comparison table, in which all the HTML pages were cut down to 7 kB to fit.

### Out-of-Line, In-Memory TOAST Storage

TOAST pointers can point to data that is not on disk, but is
elsewhere in the memory of the current server process.  Such pointers
obviously cannot be long-lived, but they are nonetheless useful.  There
are currently two sub-cases:
pointers to *indirect* data and
pointers to *expanded* data.

Indirect TOAST pointers simply point at a non-indirect varlena
value stored somewhere in memory.  This case was originally created merely
as a proof of concept, but it is currently used during logical decoding to
avoid possibly having to create physical tuples exceeding 1 GB (as pulling
all out-of-line field values into the tuple might do).  The case is of
limited use since the creator of the pointer datum is entirely responsible
that the referenced data survives for as long as the pointer could exist,
and there is no infrastructure to help with this.

Expanded TOAST pointers are useful for complex data types
whose on-disk representation is not especially suited for computational
purposes.  As an example, the standard varlena representation of a
PostgreSQL array includes dimensionality information, a
nulls bitmap if there are any null elements, then the values of all the
elements in order.  When the element type itself is variable-length, the
only way to find the `N`'th element is to scan through all the
preceding elements.  This representation is appropriate for on-disk storage
because of its compactness, but for computations with the array it's much
nicer to have an "expanded" or "deconstructed"
representation in which all the element starting locations have been
identified.  The TOAST pointer mechanism supports this need by
allowing a pass-by-reference Datum to point to either a standard varlena
value (the on-disk representation) or a TOAST pointer that
points to an expanded representation somewhere in memory.  The details of
this expanded representation are up to the data type, though it must have
a standard header and meet the other API requirements given
in `src/include/utils/expandeddatum.h`.  C-level functions
working with the data type can choose to handle either representation.
Functions that do not know about the expanded representation, but simply
apply `PG_DETOAST_DATUM` to their inputs, will automatically
receive the traditional varlena representation; so support for an expanded
representation can be introduced incrementally, one function at a time.

TOAST pointers to expanded values are further broken down
into *read-write* and *read-only* pointers.
The pointed-to representation is the same either way, but a function that
receives a read-write pointer is allowed to modify the referenced value
in-place, whereas one that receives a read-only pointer must not; it must
first create a copy if it wants to make a modified version of the value.
This distinction and some associated conventions make it possible to avoid
unnecessary copying of expanded values during query execution.

For all types of in-memory TOAST pointer, the TOAST
management code ensures that no such pointer datum can accidentally get
stored on disk.  In-memory TOAST pointers are automatically
expanded to normal in-line varlena values before storage — and then
possibly converted to on-disk TOAST pointers, if the containing
tuple would otherwise be too big.

## Free Space Map

Each heap and index relation, except for hash indexes, has a Free Space Map
(FSM) to keep track of available space in the relation.
It's stored alongside the main relation data in a separate relation fork,
named after the filenode number of the relation, plus a `_fsm`
suffix. For example, if the filenode of a relation is 12345, the
FSM is stored in a file called
`12345_fsm`, in the same directory as the main relation file.

The Free Space Map is organized as a tree of FSM pages. The
bottom level FSM pages store the free space available on each
heap (or index) page, using one byte to represent each such page. The upper
levels aggregate information from the lower levels.

Within each FSM page is a binary tree, stored in an array with
one byte per node. Each leaf node represents a heap page, or a lower level
FSM page. In each non-leaf node, the higher of its children's
values is stored. The maximum value in the leaf nodes is therefore stored
at the root.

See `src/backend/storage/freespace/README` for more details on
how the FSM is structured, and how it's updated and searched.
The [pgfreespacemap](#pgfreespacemap) module
can be used to examine the information stored in free space maps.

## Visibility Map

Each heap relation has a Visibility Map
(VM) to keep track of which pages contain only tuples that are known to be
visible to all active transactions; it also keeps track of which pages contain
only frozen tuples.  It's stored
alongside the main relation data in a separate relation fork, named after the
filenode number of the relation, plus a `_vm` suffix. For example,
if the filenode of a relation is 12345, the VM is stored in a file called
`12345_vm`, in the same directory as the main relation file.
Note that indexes do not have VMs.

The visibility map stores two bits per heap page.  The first bit, if set,
indicates that the page is all-visible, or in other words that the page does
not contain any tuples that need to be vacuumed.
This information can also be used
by [*index-only
scans*](#indexes-index-only-scans) to answer queries using only the index tuple.
The second bit, if set, means that all tuples on the page have been frozen.
That means that even an anti-wraparound vacuum need not revisit the page.

The map is conservative in the sense that we make sure that whenever a bit is
set, we know the condition is true, but if a bit is not set, it might or
might not be true. Visibility map bits are only set by vacuum, but are
cleared by any data-modifying operations on a page.

The [pgvisibility](#pgvisibility) module can be used to examine the
information stored in the visibility map.

## Database Page Layout

This section provides an overview of the page format used within
PostgreSQL tables and indexes. (Note: Actually, use of this page format is not required for either table or
index access methods. The `heap` table access method
always uses this format.  All the existing index methods also use the
basic format, but the data kept on index metapages usually doesn't follow
the item layout rules.)
Sequences and TOAST tables are formatted just like a regular table.

In the following explanation, a
*byte*
is assumed to contain 8 bits.  In addition, the term
*item*
refers to an individual data value that is stored on a page.  In a table,
an item is a row; in an index, an item is an index entry.

Every table and index is stored as an array of *pages* of a
fixed size (usually 8 kB, although a different page size can be selected
when compiling the server).  In a table, all the pages are logically
equivalent, so a particular item (row) can be stored in any page.  In
indexes, the first page is generally reserved as a *metapage*
holding control information, and there can be different types of pages
within the index, depending on the index access method.

[page-table](#page-table) shows the overall layout of a page.
There are five parts to each page.

| Item | Description |
| --- | --- |
| PageHeaderData | 24 bytes long. Contains general information about the page, including free space pointers. |
| ItemIdData | Array of item identifiers pointing to the actual items. Each entry is an (offset,length) pair. 4 bytes per item. |
| Free space | The unallocated space. New item identifiers are allocated from the start of this area, new items from the end. |
| Items | The actual items themselves. |
| Special space | Index access method specific data. Different methods store different data. Empty in ordinary tables. |

The first 24 bytes of each page consists of a page header
(`PageHeaderData`). Its format is detailed in [pageheaderdata-table](#pageheaderdata-table). The first field tracks the most
recent WAL entry related to this page. The second field contains
the page checksum if [app-initdb-data-checksums](#app-initdb-data-checksums) are
enabled.  Next is a 2-byte field containing flag bits. This is followed
by three 2-byte integer fields (`pd_lower`,
`pd_upper`, and
`pd_special`).  These contain byte offsets
from the page start to the start of unallocated space, to the end of
unallocated space, and to the start of the special space.  The next 2
bytes of the page header, `pd_pagesize_version`,
store both the page size and a version indicator.  Beginning with
PostgreSQL 8.3 the version number is 4;
PostgreSQL 8.1 and 8.2 used version number 3;
PostgreSQL 8.0 used version number 2;
PostgreSQL 7.3 and 7.4 used version number 1;
prior releases used version number 0.
(The basic page layout and header format has not changed in most of these
versions, but the layout of heap row headers has.)  The page size
is basically only present as a cross-check; there is no support for having
more than one page size in an installation.
The last field is a hint that shows whether pruning the page is likely
to be profitable: it tracks the oldest un-pruned XMAX on the page.

| Field | Type | Length | Description |
| --- | --- | --- | --- |
| pd_lsn | PageXLogRecPtr | 8 bytes | LSN: next byte after last byte of WAL record for last change    to this page |
| pd_checksum | uint16 | 2 bytes | Page checksum |
| pd_flags | uint16 | 2 bytes | Flag bits |
| pd_lower | LocationIndex | 2 bytes | Offset to start of free space |
| pd_upper | LocationIndex | 2 bytes | Offset to end of free space |
| pd_special | LocationIndex | 2 bytes | Offset to start of special space |
| pd_pagesize_version | uint16 | 2 bytes | Page size and layout version number information |
| pd_prune_xid | TransactionId | 4 bytes | Oldest unpruned XMAX on page, or zero if none |

All the details can be found in
`src/include/storage/bufpage.h`.

Following the page header are item identifiers
(`ItemIdData`), each requiring four bytes.
An item identifier contains a byte-offset to
the start of an item, its length in bytes, and a few attribute bits
which affect its interpretation.
New item identifiers are allocated
as needed from the beginning of the unallocated space.
The number of item identifiers present can be determined by looking at
`pd_lower`, which is increased to allocate a new identifier.
Because an item
identifier is never moved until it is freed, its index can be used on a
long-term basis to reference an item, even when the item itself is moved
around on the page to compact free space.  In fact, every pointer to an
item (`ItemPointer`, also known as
`CTID`) created by
PostgreSQL consists of a page number and the
index of an item identifier.

The items themselves are stored in space allocated backwards from the end
of unallocated space.  The exact structure varies depending on what the
table is to contain. Tables and sequences both use a structure named
`HeapTupleHeaderData`, described below.

The final section is the "special section" which can
contain anything the access method wishes to store.  For example,
b-tree indexes store links to the page's left and right siblings,
as well as some other data relevant to the index structure.
Ordinary tables do not use a special section at all (indicated by setting
`pd_special` to equal the page size).

[storage-page-layout-figure](#storage-page-layout-figure) illustrates how these parts are
laid out in a page.
