# General Functions

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > pg_walinspect - low-level WAL inspection > General Functions`
- Source Line Ranges: `4591-4669, 7632-7804`
- Chunk ID: `pg16_guide_0066_22e25c0a69`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `017c613597895d73c3ca020c0b93063681411c503b52d27e6009c7f02ac9cce7`

## Retrieval Guidance

- Use When: Investigate WAL contents, WAL volume source, or resource-manager-level changes.
- Retrieval Keywords: pg_walinspect, WAL inspection, pg_get_wal_records_info, rmgr, LSN, WAL record
- Follow-up Guidance: Human review is recommended because WAL interpretation is low-level and version-specific.
- Classification Note: The module provides functions to inspect WAL records and resource-manager data, confirming WAL activity and low-level change records.

## Official Source Content

### General Functions

**`get_raw_page(relname text, fork text, blkno bigint) returns bytea`**
: `get_raw_page` reads the specified block of the named
relation and returns a copy as a `bytea` value.  This allows a
single time-consistent copy of the block to be obtained.
`fork` should be `'main'` for
the main data fork, `'fsm'` for the
[free space map](#storage-fsm),
`'vm'` for the
[visibility map](#storage-vm), or
`'init'` for the initialization fork.

**`get_raw_page(relname text, blkno bigint) returns bytea`**
: A shorthand version of `get_raw_page`, for reading
from the main fork.  Equivalent to
`get_raw_page(relname, 'main', blkno)`

**`page_header(page bytea) returns record`**
: `page_header` shows fields that are common to all
PostgreSQL heap and index pages.

A page image obtained with `get_raw_page` should be
passed as argument.  For example:

```
test=# SELECT * FROM page_header(get_raw_page('pg_class', 0));
lsn    | checksum | flags  | lower | upper | special | pagesize | version | prune_xid
-----------+----------+--------+-------+-------+---------+----------+---------+-----------
0/24A1B50 |        0 |      1 |   232 |   368 |    8192 |     8192 |       4 |         0
```

The returned columns correspond to the fields in the
`PageHeaderData` struct.
See `src/include/storage/bufpage.h` for details.

The `checksum` field is the checksum stored in
the page, which might be incorrect if the page is somehow corrupted.  If
data checksums are not enabled for this instance, then the value stored
is meaningless.

**`page_checksum(page bytea, blkno bigint) returns smallint`**
: `page_checksum` computes the checksum for the page, as if
it was located at the given block.

A page image obtained with `get_raw_page` should be
passed as argument.  For example:

```
test=# SELECT page_checksum(get_raw_page('pg_class', 0), 0);
page_checksum
---------------
13443
```

Note that the checksum depends on the block number, so matching block
numbers should be passed (except when doing esoteric debugging).

The checksum computed with this function can be compared with
the `checksum` result field of the
function `page_header`.  If data checksums are
enabled for this instance, then the two values should be equal.

**`fsm_page_contents(page bytea) returns text`**
: `fsm_page_contents` shows the internal node structure
of an FSM page.  For example:

```
test=# SELECT fsm_page_contents(get_raw_page('pg_class', 'fsm', 0));
```

The output is a multiline string, with one line per node in the binary
tree within the page.  Only those nodes that are not zero are printed.
The so-called "next" pointer, which points to the next slot to be
returned from the page, is also printed.

See `src/backend/storage/freespace/README` for more
information on the structure of an FSM page.

### General Functions

**`pg_get_wal_record_info(in_lsn pg_lsn) returns record`**
: Gets WAL record information about a record that is located at or
after the `in_lsn` argument.  For
example:

```
postgres=# SELECT * FROM pg_get_wal_record_info('0/E419E28');
-[ RECORD 1 ]----+-------------------------------------------------
start_lsn        | 0/E419E28
end_lsn          | 0/E419E68
prev_lsn         | 0/E419D78
xid              | 0
resource_manager | Heap2
record_type      | VACUUM
record_length    | 58
main_data_length | 2
fpi_length       | 0
description      | nunused: 5, unused: [1, 2, 3, 4, 5]
block_ref        | blkref #0: rel 1663/16385/1249 fork main blk 364
```

If `in_lsn` isn't at the start of a WAL
record, information about the next valid WAL record is shown
instead.  If there is no next valid WAL record, the function
raises an error.

**`
pg_get_wal_records_info(start_lsn pg_lsn, end_lsn pg_lsn)
returns setof record
`**
: Gets information of all the valid WAL records between
`start_lsn` and `end_lsn`.
Returns one row per WAL record.  For example:

```
postgres=# SELECT * FROM pg_get_wal_records_info('0/1E913618', '0/1E913740') LIMIT 1;
-[ RECORD 1 ]----+--------------------------------------------------------------
start_lsn        | 0/1E913618
end_lsn          | 0/1E913650
prev_lsn         | 0/1E9135A0
xid              | 0
resource_manager | Standby
record_type      | RUNNING_XACTS
record_length    | 50
main_data_length | 24
fpi_length       | 0
description      | nextXid 33775 latestCompletedXid 33774 oldestRunningXid 33775
block_ref        |
```

The function raises an error if
`start_lsn` is not available.

**`pg_get_wal_block_info(start_lsn pg_lsn, end_lsn pg_lsn, show_data boolean DEFAULT true) returns setof record`**
: Gets information about each block reference from all the valid
WAL records between `start_lsn` and
`end_lsn` with one or more block
references.  Returns one row per block reference per WAL record.
For example:

```
postgres=# SELECT * FROM pg_get_wal_block_info('0/1230278', '0/12302B8');
-[ RECORD 1 ]-----+-----------------------------------
start_lsn         | 0/1230278
end_lsn           | 0/12302B8
prev_lsn          | 0/122FD40
block_id          | 0
reltablespace     | 1663
reldatabase       | 1
relfilenode       | 2658
relforknumber     | 0
relblocknumber    | 11
xid               | 341
resource_manager  | Btree
record_type       | INSERT_LEAF
record_length     | 64
main_data_length  | 2
block_data_length | 16
block_fpi_length  | 0
block_fpi_info    |
description       | off: 46
block_data        | \x00002a00070010402630000070696400
block_fpi_data    |
```

This example involves a WAL record that only contains one block
reference, but many WAL records contain several block
references.  Rows output by
`pg_get_wal_block_info` are guaranteed to
have a unique combination of
`start_lsn` and
`block_id` values.

Much of the information shown here matches the output that
`pg_get_wal_records_info` would show, given
the same arguments.  However,
`pg_get_wal_block_info` unnests the
information from each WAL record into an expanded form by
outputting one row per block reference, so certain details are
tracked at the block reference level rather than at the
whole-record level.  This structure is useful with queries that
track how individual blocks changed over time.  Note that
records with no block references (e.g.,
`COMMIT` WAL records) will have no rows
returned, so `pg_get_wal_block_info` may
actually return *fewer* rows than
`pg_get_wal_records_info`.

The `reltablespace`,
`reldatabase`, and
`relfilenode` parameters reference
[`pg_tablespace`](#catalog-pg-tablespace).`oid`,
[`pg_database`](#catalog-pg-database).`oid`, and
[`pg_class`](#catalog-pg-class).`relfilenode`
respectively.  The `relforknumber`
field is the fork number within the relation for the block
reference; see `common/relpath.h` for
details.

> **Tip:**
> The `pg_filenode_relation` function (see
> [functions-admin-dblocation](#functions-admin-dblocation)) can help you to
> determine which relation was modified during original execution.
>

It is possible for clients to avoid the overhead of
materializing block data.  This may make function execution
significantly faster.  When `show_data`
is set to `false`, `block_data`
and `block_fpi_data` values are omitted
(that is, the `block_data` and
`block_fpi_data` `OUT`
arguments are `NULL` for all rows returned).
Obviously, this optimization is only feasible with queries where
block data isn't truly required.

The function raises an error if
`start_lsn` is not available.

**`
pg_get_wal_stats(start_lsn pg_lsn, end_lsn pg_lsn, per_record boolean DEFAULT false)
returns setof record
`**
: Gets statistics of all the valid WAL records between
`start_lsn` and
`end_lsn`. By default, it returns one row per
`resource_manager` type. When
`per_record` is set to `true`,
it returns one row per `record_type`.
For example:

```
postgres=# SELECT * FROM pg_get_wal_stats('0/1E847D00', '0/1E84F500')
WHERE count > 0 AND
"resource_manager/record_type" = 'Transaction'
LIMIT 1;
-[ RECORD 1 ]----------------+-------------------
resource_manager/record_type | Transaction
count                        | 2
count_percentage             | 8
record_size                  | 875
record_size_percentage       | 41.23468426013195
fpi_size                     | 0
fpi_size_percentage          | 0
combined_size                | 875
combined_size_percentage     | 2.8634072910530795
```

The function raises an error if
`start_lsn` is not available.
