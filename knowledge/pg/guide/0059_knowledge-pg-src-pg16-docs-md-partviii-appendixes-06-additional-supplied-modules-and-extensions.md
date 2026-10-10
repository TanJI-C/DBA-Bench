# General; Heap; B-Tree; BRIN; GIN; GiST; Hash functions

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > pageinspect - low-level inspection of database pages > General; Heap; B-Tree; BRIN; GIN; GiST; Hash functions`
- Source Line Ranges: `407-445, 1078-1145, 4591-4669, 4670-4747, 4748-4924, 4925-4987, 4988-5040, 5041-5093, 5094-5182, 5406-5453, 7632-7804`
- Chunk ID: `pg16_guide_0059_73770c99a0`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3fd19056bba6a10a45549b99d1823b9294a18fbbbab19813d19a0113b0160a48`

## Retrieval Guidance

- Use When: Inspect raw PostgreSQL pages to diagnose storage, tuple, or index-page anomalies.
- Retrieval Keywords: pageinspect, get_raw_page, page_header, heap_page_items, bt_page_items, gin_page_opaque_info, hash_page_items
- Follow-up Guidance: Human review is required because page-level interpretation is version- and access-method-specific.
- Classification Note: The module exposes page-level inspection functions that confirm storage layout, tuple headers, index page state, and low-level corruption evidence.

## Official Source Content

### Optional heapallindexed Verification

When the
heapallindexed argument to B-Tree
verification functions is `true`, an additional
phase of verification is performed against the table associated with
the target index relation.  This consists of a "dummy"
`CREATE INDEX CONCURRENTLY` operation, which checks for the
presence of all hypothetical new index tuples against a temporary,
in-memory summarizing structure (this is built when needed during
the basic first phase of verification).  The summarizing structure
"fingerprints" every tuple found within the target
index.  The high level principle behind

heapallindexed verification is that a new
index that is equivalent to the existing, target index must only
have entries that can be found in the existing structure.

The additional
heapallindexed phase adds
significant overhead: verification will typically take several times
longer.  However, there is no change to the relation-level locks
acquired when
heapallindexed verification is
performed.

The summarizing structure is bound in size by
`maintenance_work_mem`.  In order to ensure that
there is no more than a 2% probability of failure to detect an
inconsistency for each heap tuple that should be represented in the
index, approximately 2 bytes of memory are needed per tuple.  As
less memory is made available per tuple, the probability of missing
an inconsistency slowly increases.  This approach limits the
overhead of verification significantly, while only slightly reducing
the probability of detecting a problem, especially for installations
where verification is treated as a routine maintenance task.  Any
single absent or malformed tuple has a new opportunity to be
detected with each new verification attempt.

## btree_gin — GIN operator classes with B-tree behavior

`btree_gin` provides GIN operator classes that
implement B-tree equivalent behavior for the data types
`int2`, `int4`, `int8`, `float4`,
`float8`, `timestamp with time zone`,
`timestamp without time zone`, `time with time zone`,
`time without time zone`, `date`, `interval`,
`oid`, `money`, `"char"`,
`varchar`, `text`, `bytea`, `bit`,
`varbit`, `macaddr`, `macaddr8`, `inet`,
`cidr`, `uuid`, `name`, `bool`,
`bpchar`, and all `enum` types.

In general, these operator classes will not outperform the equivalent
standard B-tree index methods, and they lack one major feature of the
standard B-tree code: the ability to enforce uniqueness.  However,
they are useful for GIN testing and as a base for developing other
GIN operator classes.  Also, for queries that test both a GIN-indexable
column and a B-tree-indexable column, it might be more efficient to create
a multicolumn GIN index that uses one of these operator classes than to create
two separate indexes that would have to be combined via bitmap ANDing.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Example Usage

```
CREATE TABLE test (a int4);
-- create index
CREATE INDEX testidx ON test USING GIN (a);
-- query
SELECT * FROM test WHERE a  42 AS dist FROM test ORDER BY a  42 LIMIT 10;
```

Use an [exclusion
constraint](#sql-createtable-exclude) to enforce the rule that a cage at a zoo
can contain only one kind of animal:

```
=> CREATE TABLE zoo (
cage   INTEGER,
animal TEXT,
EXCLUDE USING GIST (cage WITH =, animal WITH <>)
);

=> INSERT INTO zoo VALUES(123, 'zebra');
INSERT 0 1
=> INSERT INTO zoo VALUES(123, 'zebra');
INSERT 0 1
=> INSERT INTO zoo VALUES(123, 'lion');
ERROR:  conflicting key value violates exclusion constraint "zoo_cage_animal_excl"
DETAIL:  Key (cage, animal)=(123, lion) conflicts with existing key (cage, animal)=(123, zebra).
=> INSERT INTO zoo VALUES(124, 'lion');
INSERT 0 1
```

### Authors

Teodor Sigaev (teodor@stack.net),
Oleg Bartunov (oleg@sai.msu.su),
Janko Richter (jankorichter@yahoo.de), and
Paul Jungwirth (pj@illuminatedcomputing.com).  See
[](http://www.sai.msu.su/~megera/postgres/gist/)
for additional information.

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

### Heap Functions

**`heap_page_items(page bytea) returns setof record`**
: `heap_page_items` shows all line pointers on a heap
page.  For those line pointers that are in use, tuple headers as well
as tuple raw data are also shown. All tuples are shown, whether or not
the tuples were visible to an MVCC snapshot at the time the raw page
was copied.

A heap page image obtained with `get_raw_page` should
be passed as argument.  For example:

```
test=# SELECT * FROM heap_page_items(get_raw_page('pg_class', 0));
```

See `src/include/storage/itemid.h` and
`src/include/access/htup_details.h` for explanations of the fields
returned.

The `heap_tuple_infomask_flags` function can be
used to unpack the flag bits of `t_infomask`
and `t_infomask2` for heap tuples.

**`tuple_data_split(rel_oid oid, t_data bytea, t_infomask integer, t_infomask2 integer, t_bits text [, do_detoast bool]) returns bytea[]`**
: `tuple_data_split` splits tuple data into attributes
in the same way as backend internals.

```
test=# SELECT tuple_data_split('pg_class'::regclass, t_data, t_infomask, t_infomask2, t_bits) FROM heap_page_items(get_raw_page('pg_class', 0));
```

This function should be called with the same arguments as the return
attributes of `heap_page_items`.

If do_detoast is `true`,
attributes will be detoasted as needed. Default value is
`false`.

**`heap_page_item_attrs(page bytea, rel_oid regclass [, do_detoast bool]) returns setof record`**
: `heap_page_item_attrs` is equivalent to
`heap_page_items` except that it returns
tuple raw data as an array of attributes that can optionally
be detoasted by do_detoast which is
`false` by default.

A heap page image obtained with `get_raw_page` should
be passed as argument.  For example:

```
test=# SELECT * FROM heap_page_item_attrs(get_raw_page('pg_class', 0), 'pg_class'::regclass);
```

**`heap_tuple_infomask_flags(t_infomask integer, t_infomask2 integer) returns record`**
: `heap_tuple_infomask_flags` decodes the
`t_infomask` and
`t_infomask2` returned by
`heap_page_items` into a human-readable
set of arrays made of flag names, with one column for all
the flags and one column for combined flags. For example:

```
test=# SELECT t_ctid, raw_flags, combined_flags
FROM heap_page_items(get_raw_page('pg_class', 0)),
LATERAL heap_tuple_infomask_flags(t_infomask, t_infomask2)
WHERE t_infomask IS NOT NULL OR t_infomask2 IS NOT NULL;
```

This function should be called with the same arguments as the return
attributes of `heap_page_items`.

Combined flags are displayed for source-level macros that take into
account the value of more than one raw bit, such as
`HEAP_XMIN_FROZEN`.

See `src/include/access/htup_details.h` for
explanations of the flag names returned.

### B-Tree Functions

**`bt_metap(relname text) returns record`**
: `bt_metap` returns information about a B-tree
index's metapage.  For example:

```
test=# SELECT * FROM bt_metap('pg_cast_oid_index');
-[ RECORD 1 ]-------------+-------
magic                     | 340322
version                   | 4
root                      | 1
level                     | 0
fastroot                  | 1
fastlevel                 | 0
last_cleanup_num_delpages | 0
last_cleanup_num_tuples   | 230
allequalimage             | f
```

**`bt_page_stats(relname text, blkno bigint) returns record`**
: `bt_page_stats` returns summary information about
a data page of a B-tree index.  For example:

```
test=# SELECT * FROM bt_page_stats('pg_cast_oid_index', 1);
-[ RECORD 1 ]-+-----
blkno         | 1
type          | l
live_items    | 224
dead_items    | 0
avg_item_size | 16
page_size     | 8192
free_size     | 3668
btpo_prev     | 0
btpo_next     | 0
btpo_level    | 0
btpo_flags    | 3
```

**`bt_multi_page_stats(relname text, blkno bigint, blk_count bigint) returns setof record`**
: `bt_multi_page_stats` returns the same information
as `bt_page_stats`, but does so for each page of the
range of pages beginning at blkno and extending
for blk_count pages.
If blk_count is negative, all pages
from blkno to the end of the index are reported
on.  For example:

```
test=# SELECT * FROM bt_multi_page_stats('pg_proc_oid_index', 5, 2);
-[ RECORD 1 ]-+-----
blkno         | 5
type          | l
live_items    | 367
dead_items    | 0
avg_item_size | 16
page_size     | 8192
free_size     | 808
btpo_prev     | 4
btpo_next     | 6
btpo_level    | 0
btpo_flags    | 1
-[ RECORD 2 ]-+-----
blkno         | 6
type          | l
live_items    | 367
dead_items    | 0
avg_item_size | 16
page_size     | 8192
free_size     | 808
btpo_prev     | 5
btpo_next     | 7
btpo_level    | 0
btpo_flags    | 1
```

**`bt_page_items(relname text, blkno bigint) returns setof record`**
: `bt_page_items` returns detailed information about
all of the items on a B-tree index page.  For example:

```
test=# SELECT itemoffset, ctid, itemlen, nulls, vars, data, dead, htid, tids[0:2] AS some_tids
FROM bt_page_items('tenk2_hundred', 5);
itemoffset |   ctid    | itemlen | nulls | vars |          data           | dead |  htid  |      some_tids
------------+-----------+---------+-------+------+-------------------------+------+--------+---------------------
1 | (16,1)    |      16 | f     | f    | 30 00 00 00 00 00 00 00 |      |        |
2 | (16,8292) |     616 | f     | f    | 24 00 00 00 00 00 00 00 | f    | (1,6)  | {"(1,6)","(10,22)"}
3 | (16,8292) |     616 | f     | f    | 25 00 00 00 00 00 00 00 | f    | (1,18) | {"(1,18)","(4,22)"}
4 | (16,8292) |     616 | f     | f    | 26 00 00 00 00 00 00 00 | f    | (4,18) | {"(4,18)","(6,17)"}
5 | (16,8292) |     616 | f     | f    | 27 00 00 00 00 00 00 00 | f    | (1,2)  | {"(1,2)","(1,19)"}
6 | (16,8292) |     616 | f     | f    | 28 00 00 00 00 00 00 00 | f    | (2,24) | {"(2,24)","(4,11)"}
7 | (16,8292) |     616 | f     | f    | 29 00 00 00 00 00 00 00 | f    | (2,17) | {"(2,17)","(11,2)"}
8 | (16,8292) |     616 | f     | f    | 2a 00 00 00 00 00 00 00 | f    | (0,25) | {"(0,25)","(3,20)"}
9 | (16,8292) |     616 | f     | f    | 2b 00 00 00 00 00 00 00 | f    | (0,10) | {"(0,10)","(0,14)"}
10 | (16,8292) |     616 | f     | f    | 2c 00 00 00 00 00 00 00 | f    | (1,3)  | {"(1,3)","(3,9)"}
11 | (16,8292) |     616 | f     | f    | 2d 00 00 00 00 00 00 00 | f    | (6,28) | {"(6,28)","(11,1)"}
12 | (16,8292) |     616 | f     | f    | 2e 00 00 00 00 00 00 00 | f    | (0,27) | {"(0,27)","(1,13)"}
13 | (16,8292) |     616 | f     | f    | 2f 00 00 00 00 00 00 00 | f    | (4,17) | {"(4,17)","(4,21)"}
(13 rows)
```

This is a B-tree leaf page.  All tuples that point to the table
happen to be posting list tuples (all of which store a total of
100 6 byte TIDs).  There is also a "high key" tuple
at `itemoffset` number 1.
`ctid` is used to store encoded
information about each tuple in this example, though leaf page
tuples often store a heap TID directly in the
`ctid` field instead.
`tids` is the list of TIDs stored as a
posting list.

In an internal page (not shown), the block number part of
`ctid` is a "downlink",
which is a block number of another page in the index itself.
The offset part (the second number) of
`ctid` stores encoded information about
the tuple, such as the number of columns present (suffix
truncation may have removed unneeded suffix columns).  Truncated
columns are treated as having the value "minus
infinity".

`htid` shows a heap TID for the tuple,
regardless of the underlying tuple representation.  This value
may match `ctid`, or may be decoded
from the alternative representations used by posting list tuples
and tuples from internal pages.  Tuples in internal pages
usually have the implementation level heap TID column truncated
away, which is represented as a NULL
`htid` value.

Note that the first item on any non-rightmost page (any page with
a non-zero value in the `btpo_next` field) is the
page's "high key", meaning its `data`
serves as an upper bound on all items appearing on the page, while
its `ctid` field does not point to
another block.  Also, on internal pages, the first real data
item (the first item that is not a high key) reliably has every
column truncated away, leaving no actual value in its
`data` field.  Such an item does have a
valid downlink in its `ctid` field,
however.

For more details about the structure of B-tree indexes, see
[btree-structure](#btree-structure).  For more details about
deduplication and posting lists, see [btree-deduplication](#btree-deduplication).

**`bt_page_items(page bytea) returns setof record`**
: It is also possible to pass a page to `bt_page_items`
as a `bytea` value.  A page image obtained
with `get_raw_page` should be passed as argument.  So
the last example could also be rewritten like this:

```
test=# SELECT itemoffset, ctid, itemlen, nulls, vars, data, dead, htid, tids[0:2] AS some_tids
FROM bt_page_items(get_raw_page('tenk2_hundred', 5));
itemoffset |   ctid    | itemlen | nulls | vars |          data           | dead |  htid  |      some_tids
------------+-----------+---------+-------+------+-------------------------+------+--------+---------------------
1 | (16,1)    |      16 | f     | f    | 30 00 00 00 00 00 00 00 |      |        |
2 | (16,8292) |     616 | f     | f    | 24 00 00 00 00 00 00 00 | f    | (1,6)  | {"(1,6)","(10,22)"}
3 | (16,8292) |     616 | f     | f    | 25 00 00 00 00 00 00 00 | f    | (1,18) | {"(1,18)","(4,22)"}
4 | (16,8292) |     616 | f     | f    | 26 00 00 00 00 00 00 00 | f    | (4,18) | {"(4,18)","(6,17)"}
5 | (16,8292) |     616 | f     | f    | 27 00 00 00 00 00 00 00 | f    | (1,2)  | {"(1,2)","(1,19)"}
6 | (16,8292) |     616 | f     | f    | 28 00 00 00 00 00 00 00 | f    | (2,24) | {"(2,24)","(4,11)"}
7 | (16,8292) |     616 | f     | f    | 29 00 00 00 00 00 00 00 | f    | (2,17) | {"(2,17)","(11,2)"}
8 | (16,8292) |     616 | f     | f    | 2a 00 00 00 00 00 00 00 | f    | (0,25) | {"(0,25)","(3,20)"}
9 | (16,8292) |     616 | f     | f    | 2b 00 00 00 00 00 00 00 | f    | (0,10) | {"(0,10)","(0,14)"}
10 | (16,8292) |     616 | f     | f    | 2c 00 00 00 00 00 00 00 | f    | (1,3)  | {"(1,3)","(3,9)"}
11 | (16,8292) |     616 | f     | f    | 2d 00 00 00 00 00 00 00 | f    | (6,28) | {"(6,28)","(11,1)"}
12 | (16,8292) |     616 | f     | f    | 2e 00 00 00 00 00 00 00 | f    | (0,27) | {"(0,27)","(1,13)"}
13 | (16,8292) |     616 | f     | f    | 2f 00 00 00 00 00 00 00 | f    | (4,17) | {"(4,17)","(4,21)"}
(13 rows)
```

All the other details are the same as explained in the previous item.

### BRIN Functions

**`brin_page_type(page bytea) returns text`**
: `brin_page_type` returns the page type of the given
BRIN index page, or throws an error if the page is
not a valid BRIN page.  For example:

```
test=# SELECT brin_page_type(get_raw_page('brinidx', 0));
brin_page_type
----------------
meta
```

**`brin_metapage_info(page bytea) returns record`**
: `brin_metapage_info` returns assorted information
about a BRIN index metapage.  For example:

```
test=# SELECT * FROM brin_metapage_info(get_raw_page('brinidx', 0));
magic    | version | pagesperrange | lastrevmappage
------------+---------+---------------+----------------
0xA8109CFA |       1 |             4 |              2
```

**`brin_revmap_data(page bytea) returns setof tid`**
: `brin_revmap_data` returns the list of tuple
identifiers in a BRIN index range map page.
For example:

```
test=# SELECT * FROM brin_revmap_data(get_raw_page('brinidx', 2)) LIMIT 5;
pages
---------
(6,137)
(6,138)
(6,139)
(6,140)
(6,141)
```

**`brin_page_items(page bytea, index oid) returns setof record`**
: `brin_page_items` returns the data stored in the
BRIN data page.  For example:

```
test=# SELECT * FROM brin_page_items(get_raw_page('brinidx', 5),
'brinidx')
ORDER BY blknum, attnum LIMIT 6;
itemoffset | blknum | attnum | allnulls | hasnulls | placeholder | empty |    value
------------+--------+--------+----------+----------+-------------+-------+--------------
137 |      0 |      1 | t        | f        | f           | f     |
137 |      0 |      2 | f        | f        | f           | f     | {1 .. 88}
138 |      4 |      1 | t        | f        | f           | f     |
138 |      4 |      2 | f        | f        | f           | f     | {89 .. 176}
139 |      8 |      1 | t        | f        | f           | f     |
139 |      8 |      2 | f        | f        | f           | f     | {177 .. 264}
```

The returned columns correspond to the fields in the
`BrinMemTuple` and `BrinValues` structs.
See `src/include/access/brin_tuple.h` for details.

### GIN Functions

**`gin_metapage_info(page bytea) returns record`**
: `gin_metapage_info` returns information about
a GIN index metapage.  For example:

```
test=# SELECT * FROM gin_metapage_info(get_raw_page('gin_index', 0));
-[ RECORD 1 ]----+-----------
pending_head     | 4294967295
pending_tail     | 4294967295
tail_free_size   | 0
n_pending_pages  | 0
n_pending_tuples | 0
n_total_pages    | 7
n_entry_pages    | 6
n_data_pages     | 0
n_entries        | 693
version          | 2
```

**`gin_page_opaque_info(page bytea) returns record`**
: `gin_page_opaque_info` returns information about
a GIN index opaque area, like the page type.
For example:

```
test=# SELECT * FROM gin_page_opaque_info(get_raw_page('gin_index', 2));
rightlink | maxoff |         flags
-----------+--------+------------------------
5 |      0 | {data,leaf,compressed}
(1 row)
```

**`gin_leafpage_items(page bytea) returns setof record`**
: `gin_leafpage_items` returns information about
the data stored in a GIN leaf page.  For example:

```
test=# SELECT first_tid, nbytes, tids[0:5] AS some_tids
FROM gin_leafpage_items(get_raw_page('gin_test_idx', 2));
first_tid | nbytes |                        some_tids
-----------+--------+----------------------------------------------------------
(8,41)    |    244 | {"(8,41)","(8,43)","(8,44)","(8,45)","(8,46)"}
(10,45)   |    248 | {"(10,45)","(10,46)","(10,47)","(10,48)","(10,49)"}
(12,52)   |    248 | {"(12,52)","(12,53)","(12,54)","(12,55)","(12,56)"}
(14,59)   |    320 | {"(14,59)","(14,60)","(14,61)","(14,62)","(14,63)"}
(167,16)  |    376 | {"(167,16)","(167,17)","(167,18)","(167,19)","(167,20)"}
(170,30)  |    376 | {"(170,30)","(170,31)","(170,32)","(170,33)","(170,34)"}
(173,44)  |    197 | {"(173,44)","(173,45)","(173,46)","(173,47)","(173,48)"}
(7 rows)
```

### GiST Functions

**`gist_page_opaque_info(page bytea) returns record`**
: `gist_page_opaque_info` returns information from
a GiST index page's opaque area, such as the NSN,
rightlink and page type.
For example:

```
test=# SELECT * FROM gist_page_opaque_info(get_raw_page('test_gist_idx', 2));
lsn | nsn | rightlink | flags
-----+-----+-----------+--------
0/1 | 0/0 |         1 | {leaf}
(1 row)
```

**`gist_page_items(page bytea, index_oid regclass) returns setof record`**
: `gist_page_items` returns information about
the data stored in a page of a GiST index.  For example:

```
test=# SELECT * FROM gist_page_items(get_raw_page('test_gist_idx', 0), 'test_gist_idx');
itemoffset |   ctid    | itemlen | dead |             keys
------------+-----------+---------+------+-------------------------------
1 | (1,65535) |      40 | f    | (p)=("(185,185),(1,1)")
2 | (2,65535) |      40 | f    | (p)=("(370,370),(186,186)")
3 | (3,65535) |      40 | f    | (p)=("(555,555),(371,371)")
4 | (4,65535) |      40 | f    | (p)=("(740,740),(556,556)")
5 | (5,65535) |      40 | f    | (p)=("(870,870),(741,741)")
6 | (6,65535) |      40 | f    | (p)=("(1000,1000),(871,871)")
(6 rows)
```

**`gist_page_items_bytea(page bytea) returns setof record`**
: Same as `gist_page_items`, but returns the key data
as a raw `bytea` blob.  Since it does not attempt to decode
the key, it does not need to know which index is involved.  For
example:

```
test=# SELECT * FROM gist_page_items_bytea(get_raw_page('test_gist_idx', 0));
itemoffset |   ctid    | itemlen | dead |                                      key_data
------------+-----------+---------+------+------------------------------------------------------------------------------------
1 | (1,65535) |      40 | f    | \x00000100ffff28000000000000c064400000000000c06440000000000000f03f000000000000f03f
2 | (2,65535) |      40 | f    | \x00000200ffff28000000000000c074400000000000c074400000000000e064400000000000e06440
3 | (3,65535) |      40 | f    | \x00000300ffff28000000000000207f400000000000207f400000000000d074400000000000d07440
4 | (4,65535) |      40 | f    | \x00000400ffff28000000000000c084400000000000c084400000000000307f400000000000307f40
5 | (5,65535) |      40 | f    | \x00000500ffff28000000000000f089400000000000f089400000000000c884400000000000c88440
6 | (6,65535) |      40 | f    | \x00000600ffff28000000000000208f400000000000208f400000000000f889400000000000f88940
7 | (7,65535) |      40 | f    | \x00000700ffff28000000000000408f400000000000408f400000000000288f400000000000288f40
(7 rows)
```

### Hash Functions

**`hash_page_type(page bytea) returns text`**
: `hash_page_type` returns page type of
the given HASH index page.  For example:

```
test=# SELECT hash_page_type(get_raw_page('con_hash_index', 0));
hash_page_type
----------------
metapage
```

**`hash_page_stats(page bytea) returns setof record`**
: `hash_page_stats` returns information about
a bucket or overflow page of a HASH index.
For example:

```
test=# SELECT * FROM hash_page_stats(get_raw_page('con_hash_index', 1));
-[ RECORD 1 ]---+-----------
live_items      | 407
dead_items      | 0
page_size       | 8192
free_size       | 8
hasho_prevblkno | 4096
hasho_nextblkno | 8474
hasho_bucket    | 0
hasho_flag      | 66
hasho_page_id   | 65408
```

**`hash_page_items(page bytea) returns setof record`**
: `hash_page_items` returns information about
the data stored in a bucket or overflow page of a HASH
index page.  For example:

```
test=# SELECT * FROM hash_page_items(get_raw_page('con_hash_index', 1)) LIMIT 5;
itemoffset |   ctid    |    data
------------+-----------+------------
1 | (899,77)  | 1053474816
2 | (897,29)  | 1053474816
3 | (894,207) | 1053474816
4 | (892,159) | 1053474816
5 | (890,111) | 1053474816
```

**`hash_bitmap_info(index oid, blkno bigint) returns record`**
: `hash_bitmap_info` shows the status of a bit
in the bitmap page for a particular overflow page of HASH
index. For example:

```
test=# SELECT * FROM hash_bitmap_info('con_hash_index', 2052);
bitmapblkno | bitmapbit | bitstatus
-------------+-----------+-----------
65 |         3 | t
```

**`hash_metapage_info(page bytea) returns record`**
: `hash_metapage_info` returns information stored
in the meta page of a HASH index.  For example:

```
test=# SELECT magic, version, ntuples, ffactor, bsize, bmsize, bmshift,
test-#     maxbucket, highmask, lowmask, ovflpoint, firstfree, nmaps, procid,
test-#     regexp_replace(spares::text, '(,0)*}', '}') as spares,
test-#     regexp_replace(mapp::text, '(,0)*}', '}') as mapp
test-# FROM hash_metapage_info(get_raw_page('con_hash_index', 0));
-[ RECORD 1 ]-------------------------------------------------------------------------------
magic     | 105121344
version   | 4
ntuples   | 500500
ffactor   | 40
bsize     | 8152
bmsize    | 4096
bmshift   | 15
maxbucket | 12512
highmask  | 16383
lowmask   | 8191
ovflpoint | 28
firstfree | 1204
nmaps     | 1
procid    | 450
spares    | {0,0,0,0,0,0,1,1,1,1,1,1,1,1,3,4,4,4,45,55,58,59,508,567,628,704,1193,1202,1204}
mapp      | {65}
```

### General Hashing Functions

#### `digest()`

```
digest(data text, type text) returns bytea
digest(data bytea, type text) returns bytea
```

Computes a binary hash of the given
data.

type is the algorithm to use.
Standard algorithms are `md5`, `sha1`,
`sha224`, `sha256`,
`sha384` and `sha512`.
Moreover, any digest algorithm OpenSSL supports
is automatically picked up.

If you want the digest as a hexadecimal string, use
`encode()` on the result.  For example:

```
CREATE OR REPLACE FUNCTION sha1(bytea) returns text AS $$
SELECT encode(digest($1, 'sha1'), 'hex')
$$ LANGUAGE SQL STRICT IMMUTABLE;
```

#### `hmac()`

```
hmac(data text, key text, type text) returns bytea
hmac(data bytea, key bytea, type text) returns bytea
```

Calculates hashed MAC for
data with key
key.

type is the same as in `digest()`.

This is similar to `digest()` but the hash can only be
recalculated knowing the key.  This prevents the scenario of someone
altering data and also changing the hash to match.

If the key is larger than the hash block size it will first be hashed and
the result will be used as key.

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
