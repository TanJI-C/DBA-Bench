# Functions; Optional heapallindexed Verification; Using amcheck Effectively

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > amcheck - tools to verify table and index consistency > Functions; Optional heapallindexed Verification; Using amcheck Effectively`
- Source Line Ranges: `208-406, 407-445, 446-547, 3576-3654, 3863-3878, 3965-3992, 4098-4142, 4426-4468, 4578-4584, 4591-4669, 4670-4747, 4748-4924, 4925-4987, 4988-5040, 5041-5093, 5094-5182, 5394-6101, 6114-6133, 6187-6239, 6540-6573, 6761-6785, 7133-7187, 7238-7255, 7534-7580, 7632-7804, 8286-8344, 9244-9255, 9313-9343, 9344-9361, 9362-9373, 9374-9387, 9402-9499, 9509-10152, 10464-10486, 10499-10525, 10570-10586, 10736-10755`
- Chunk ID: `pg16_guide_0055_57f2c9a107`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7e01f9afba969c4139475a51873178762629138657744aa58325ec0a1cd15406`

## Retrieval Guidance

- Use When: Verify suspected index or heap corruption and collect confirmation signals before repair.
- Retrieval Keywords: amcheck, bt_index_check, bt_index_parent_check, verify_heapam, heapallindexed, index corruption, table corruption
- Follow-up Guidance: Route repair decisions to the separate corruption repair record.
- Classification Note: These sections describe verification functions and usage patterns that confirm B-tree, heap, or index consistency problems.

## Official Source Content

### Functions

**`bt_index_check(index regclass, heapallindexed boolean) returns void`**
: `bt_index_check` tests that its target, a
B-Tree index, respects a variety of invariants.  Example usage:

```
test=# SELECT bt_index_check(index => c.oid, heapallindexed => i.indisunique),
c.relname,
c.relpages
FROM pg_index i
JOIN pg_opclass op ON i.indclass[0] = op.oid
JOIN pg_am am ON op.opcmethod = am.oid
JOIN pg_class c ON i.indexrelid = c.oid
JOIN pg_namespace n ON c.relnamespace = n.oid
WHERE am.amname = 'btree' AND n.nspname = 'pg_catalog'
-- Don't check temp tables, which may be from another session:
AND c.relpersistence != 't'
-- Function may throw an error when this is omitted:
AND c.relkind = 'i' AND i.indisready AND i.indisvalid
ORDER BY c.relpages DESC LIMIT 10;
bt_index_check |             relname             | relpages
----------------+---------------------------------+----------
| pg_depend_reference_index       |       43
| pg_depend_depender_index        |       40
| pg_proc_proname_args_nsp_index  |       31
| pg_description_o_c_o_index      |       21
| pg_attribute_relid_attnam_index |       14
| pg_proc_oid_index               |       10
| pg_attribute_relid_attnum_index |        9
| pg_amproc_fam_proc_index        |        5
| pg_amop_opr_fam_index           |        5
| pg_amop_fam_strat_index         |        5
(10 rows)
```

This example shows a session that performs verification of the
10 largest catalog indexes in the database "test".
Verification of the presence of heap tuples as index tuples is
requested for the subset that are unique indexes.  Since no
error is raised, all indexes tested appear to be logically
consistent.  Naturally, this query could easily be changed to
call `bt_index_check` for every index in the
database where verification is supported.

`bt_index_check` acquires an `AccessShareLock`
on the target index and the heap relation it belongs to. This lock mode
is the same lock mode acquired on relations by simple
`SELECT` statements.
`bt_index_check` does not verify invariants
that span child/parent relationships, but will verify the
presence of all heap tuples as index tuples within the index
when heapallindexed is
`true`.  When a routine, lightweight test for
corruption is required in a live production environment, using
`bt_index_check` often provides the best
trade-off between thoroughness of verification and limiting the
impact on application performance and availability.

**`bt_index_parent_check(index regclass, heapallindexed boolean, rootdescend boolean) returns void`**
: `bt_index_parent_check` tests that its
target, a B-Tree index, respects a variety of invariants.
Optionally, when the heapallindexed
argument is `true`, the function verifies the
presence of all heap tuples that should be found within the
index.  When the optional rootdescend
argument is `true`, verification re-finds
tuples on the leaf level by performing a new search from the
root page for each tuple.  The checks that can be performed by
`bt_index_parent_check` are a superset of the
checks that can be performed by `bt_index_check`.
`bt_index_parent_check` can be thought of as
a more thorough variant of `bt_index_check`:
unlike `bt_index_check`,
`bt_index_parent_check` also checks
invariants that span parent/child relationships, including checking
that there are no missing downlinks in the index structure.
`bt_index_parent_check` follows the general
convention of raising an error if it finds a logical
inconsistency or other problem.

A `ShareLock` is required on the target index by
`bt_index_parent_check` (a
`ShareLock` is also acquired on the heap relation).
These locks prevent concurrent data modification from
`INSERT`, `UPDATE`, and `DELETE`
commands.  The locks also prevent the underlying relation from
being concurrently processed by `VACUUM`, as well as
all other utility commands.  Note that the function holds locks
only while running, not for the entire transaction.

`bt_index_parent_check`'s additional
verification is more likely to detect various pathological
cases.  These cases may involve an incorrectly implemented
B-Tree operator class used by the index that is checked, or,
hypothetically, undiscovered bugs in the underlying B-Tree index
access method code.  Note that
`bt_index_parent_check` cannot be used when
hot standby mode is enabled (i.e., on read-only physical
replicas), unlike `bt_index_check`.

> **Tip:**

> `bt_index_check` and
> `bt_index_parent_check` both output log
> messages about the verification process at
> `DEBUG1` and `DEBUG2` severity
> levels.  These messages provide detailed information about the
> verification process that may be of interest to
> PostgreSQL developers.  Advanced users
> may also find this information helpful, since it provides
> additional context should verification actually detect an
> inconsistency.  Running:
> ```
> SET client_min_messages = DEBUG1;
> ```
> in an interactive psql session before
> running a verification query will display messages about the
> progress of verification with a manageable level of detail.
>

**`
verify_heapam(relation regclass,
on_error_stop boolean,
check_toast boolean,
skip text,
startblock bigint,
endblock bigint,
blkno OUT bigint,
offnum OUT integer,
attnum OUT integer,
msg OUT text)
returns setof record
`**
: Checks a table, sequence, or materialized view for structural corruption,
where pages in the relation contain data that is invalidly formatted, and
for logical corruption, where pages are structurally valid but
inconsistent with the rest of the database cluster.

The following optional arguments are recognized:

`on_error_stop`

If true, corruption checking stops at the end of the first block in
which any corruptions are found.

Defaults to false.

**`check_toast`**
: If true, toasted values are checked against the target relation's
TOAST table.

This option is known to be slow.  Also, if the toast table or its
index is corrupt, checking it against toast values could conceivably
crash the server, although in many cases this would just produce an
error.

Defaults to false.

**`skip`**
: If not `none`, corruption checking skips blocks that
are marked as all-visible or all-frozen, as specified.
Valid options are `all-visible`,
`all-frozen` and `none`.

Defaults to `none`.

**`startblock`**
: If specified, corruption checking begins at the specified block,
skipping all previous blocks.  It is an error to specify a
startblock outside the range of blocks in the
target table.

By default, checking begins at the first block.

**`endblock`**
: If specified, corruption checking ends at the specified block,
skipping all remaining blocks.  It is an error to specify an
endblock outside the range of blocks in the target
table.

By default, all blocks are checked.

For each corruption detected, `verify_heapam` returns
a row with the following columns:

**`blkno`**
: The number of the block containing the corrupt page.

**`offnum`**
: The OffsetNumber of the corrupt tuple.

**`attnum`**
: The attribute number of the corrupt column in the tuple, if the
corruption is specific to a column and not the tuple as a whole.

**`msg`**
: A message describing the problem detected.

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

### Using `amcheck` Effectively

`amcheck` can be effective at detecting various types of
failure modes that [data
checksums](#app-initdb-data-checksums) will fail to catch.  These include:

- Structural inconsistencies caused by incorrect operator class
implementations.

This includes issues caused by the comparison rules of operating
system collations changing. Comparisons of datums of a collatable
type like `text` must be immutable (just as all
comparisons used for B-Tree index scans must be immutable), which
implies that operating system collation rules must never change.
Though rare, updates to operating system collation rules can
cause these issues. More commonly, an inconsistency in the
collation order between a primary server and a standby server is
implicated, possibly because the *major* operating
system version in use is inconsistent.  Such inconsistencies will
generally only arise on standby servers, and so can generally
only be detected on standby servers.

If a problem like this arises, it may not affect each individual
index that is ordered using an affected collation, simply because
*indexed* values might happen to have the same
absolute ordering regardless of the behavioral inconsistency. See
[locale](#locale) and [collation](#collation) for
further details about how PostgreSQL uses
operating system locales and collations.
- Structural inconsistencies between indexes and the heap relations
that are indexed (when heapallindexed
verification is performed).

There is no cross-checking of indexes against their heap relation
during normal operation.  Symptoms of heap corruption can be subtle.
- Corruption caused by hypothetical undiscovered bugs in the
underlying PostgreSQL access method
code, sort code, or transaction management code.

Automatic verification of the structural integrity of indexes
plays a role in the general testing of new or proposed
PostgreSQL features that could plausibly allow a
logical inconsistency to be introduced.  Verification of table
structure and associated visibility and transaction status
information plays a similar role.  One obvious testing strategy
is to call `amcheck` functions continuously
when running the standard regression tests.  See [regress-run](#regress-run) for details on running the tests.
- File system or storage subsystem faults where checksums happen to
simply not be enabled.

Note that `amcheck` examines a page as represented in some
shared memory buffer at the time of verification if there is only a
shared buffer hit when accessing the block. Consequently,
`amcheck` does not necessarily examine data read from the
file system at the time of verification. Note that when checksums are
enabled, `amcheck` may raise an error due to a checksum
failure when a corrupt block is read into a buffer.
- Corruption caused by faulty RAM, or the broader memory subsystem.

PostgreSQL does not protect against correctable
memory errors and it is assumed you will operate using RAM that
uses industry standard Error Correcting Codes (ECC) or better
protection.  However, ECC memory is typically only immune to
single-bit errors, and should not be assumed to provide
*absolute* protection against failures that
result in memory corruption.

When heapallindexed verification is
performed, there is generally a greatly increased chance of
detecting single-bit errors, since strict binary equality is
tested, and the indexed attributes within the heap are tested.

Structural corruption can happen due to faulty storage hardware, or
relation files being overwritten or modified by unrelated software.
This kind of corruption can also be detected with
[data page
checksums](#checksums).

Relation pages which are correctly formatted, internally consistent, and
correct relative to their own internal checksums may still contain
logical corruption.  As such, this kind of corruption cannot be detected
with checksums.  Examples include toasted
values in the main table which lack a corresponding entry in the toast
table, and tuples in the main table with a Transaction ID that is older
than the oldest valid Transaction ID in the database or cluster.

Multiple causes of logical corruption have been observed in production
systems, including bugs in the PostgreSQL
server software, faulty and ill-conceived backup and restore tools, and
user error.

Corrupt relations are most concerning in live production environments,
precisely the same environments where high risk activities are least
welcome.  For this reason, `verify_heapam` has been
designed to diagnose corruption without undue risk.  It cannot guard
against all causes of backend crashes, as even executing the calling
query could be unsafe on a badly corrupted system.   Access to [catalog tables](#catalogs-overview) is performed and could
be problematic if the catalogs themselves are corrupted.

In general, `amcheck` can only prove the presence of
corruption; it cannot prove its absence.

### `hstore` Operators and Functions

The operators provided by the `hstore` module are
shown in [hstore-op-table](#hstore-op-table), the functions
in [hstore-func-table](#hstore-func-table).

| Operator                         Description                         Example(s) |
| --- |
| `hstore` `->` `text`         text                         Returns value associated with given key, or `NULL` if         not present.                         `'a=>x, b=>y'::hstore -> 'a'`         x |
| `hstore` `->` `text[]`         text[]                         Returns values associated with given keys, or `NULL`         if not present.                         `'a=>x, b=>y, c=>z'::hstore -> ARRAY['c','a']`         {"z","x"} |
| `hstore` `||` `hstore`         hstore                         Concatenates two `hstore`s.                         `'a=>b, c=>d'::hstore || 'c=>x, d=>q'::hstore`         "a"=>"b", "c"=>"x", "d"=>"q" |
| `hstore` `?` `text`         boolean                         Does `hstore` contain key?                         `'a=>1'::hstore ? 'a'`         t |
| `hstore` `?&` `text[]`         boolean                         Does `hstore` contain all the specified keys?                         `'a=>1,b=>2'::hstore ?& ARRAY['a','b']`         t |
| `hstore` `?|` `text[]`         boolean                         Does `hstore` contain any of the specified keys?                         `'a=>1,b=>2'::hstore ?| ARRAY['b','c']`         t |
| `hstore` `@>` `hstore`         boolean                         Does left operand contain right?                         `'a=>b, b=>1, c=>NULL'::hstore @> 'b=>1'`         t |
| `hstore` `c'::hstore b, b=>1, c=>NULL'`         f |
| `hstore` `-` `text`         hstore                         Deletes key from left operand.                         `'a=>1, b=>2, c=>3'::hstore - 'b'::text`         "a"=>"1", "c"=>"3" |
| `hstore` `-` `text[]`         hstore                         Deletes keys from left operand.                         `'a=>1, b=>2, c=>3'::hstore - ARRAY['a','b']`         "c"=>"3" |
| `hstore` `-` `hstore`         hstore                         Deletes pairs from left operand that match pairs in the right operand.                         `'a=>1, b=>2, c=>3'::hstore - 'a=>4, b=>2'::hstore`         "a"=>"1", "c"=>"3" |
| `anyelement` `#=` `hstore`         anyelement                         Replaces fields in the left operand (which must be a composite type)         with matching values from `hstore`.                         `ROW(1,3) #= 'f1=>11'::hstore`         (11,3) |
| `%%` `hstore`         text[]                         Converts `hstore` to an array of alternating keys and         values.                         `%% 'a=>foo, b=>bar'::hstore`         {a,foo,b,bar} |
| `%#` `hstore`         text[]                         Converts `hstore` to a two-dimensional key/value array.                         `%# 'a=>foo, b=>bar'::hstore`         {{a,foo},{b,bar}} |

| Function                         Description                         Example(s) |
| --- |
| `hstore` ( `record` )         hstore                         Constructs an `hstore` from a record or row.                         `hstore(ROW(1,2))`         "f1"=>"1", "f2"=>"2" |
| `hstore` ( `text[]` )         hstore                         Constructs an `hstore` from an array, which may be either         a key/value array, or a two-dimensional array.                         `hstore(ARRAY['a','1','b','2'])`         "a"=>"1", "b"=>"2"                         `hstore(ARRAY[['c','3'],['d','4']])`         "c"=>"3", "d"=>"4" |
| `hstore` ( `text[]`, `text[]` )         hstore                         Constructs an `hstore` from separate key and value arrays.                         `hstore(ARRAY['a','b'], ARRAY['1','2'])`         "a"=>"1", "b"=>"2" |
| `hstore` ( `text`, `text` )         hstore                         Makes a single-item `hstore`.                         `hstore('a', 'b')`         "a"=>"b" |
| `akeys` ( `hstore` )         text[]                         Extracts an `hstore`'s keys as an array.                         `akeys('a=>1,b=>2')`         {a,b} |
| `skeys` ( `hstore` )         setof text                         Extracts an `hstore`'s keys as a set.                         `skeys('a=>1,b=>2')`           ``` a b ``` |
| `avals` ( `hstore` )         text[]                         Extracts an `hstore`'s values as an array.                         `avals('a=>1,b=>2')`         {1,2} |
| `svals` ( `hstore` )         setof text                         Extracts an `hstore`'s values as a set.                         `svals('a=>1,b=>2')`           ``` 1 2 ``` |
| `hstore_to_array` ( `hstore` )         text[]                         Extracts an `hstore`'s keys and values as an array of         alternating keys and values.                         `hstore_to_array('a=>1,b=>2')`         {a,1,b,2} |
| `hstore_to_matrix` ( `hstore` )         text[]                         Extracts an `hstore`'s keys and values as a two-dimensional         array.                         `hstore_to_matrix('a=>1,b=>2')`         {{a,1},{b,2}} |
| `hstore_to_json` ( `hstore` )         json                         Converts an `hstore` to a `json` value,         converting all non-null values to JSON strings.                         This function is used implicitly when an `hstore` value is         cast to `json`.                         `hstore_to_json('"a key"=>1, b=>t, c=>null, d=>12345, e=>012345, f=>1.234, g=>2.345e+4')`         {"a key": "1", "b": "t", "c": null, "d": "12345", "e": "012345", "f": "1.234", "g": "2.345e+4"} |
| `hstore_to_jsonb` ( `hstore` )         jsonb                         Converts an `hstore` to a `jsonb` value,         converting all non-null values to JSON strings.                         This function is used implicitly when an `hstore` value is         cast to `jsonb`.                         `hstore_to_jsonb('"a key"=>1, b=>t, c=>null, d=>12345, e=>012345, f=>1.234, g=>2.345e+4')`         {"a key": "1", "b": "t", "c": null, "d": "12345", "e": "012345", "f": "1.234", "g": "2.345e+4"} |
| `hstore_to_json_loose` ( `hstore` )         json                         Converts an `hstore` to a `json` value, but         attempts to distinguish numerical and Boolean values so they are         unquoted in the JSON.                         `hstore_to_json_loose('"a key"=>1, b=>t, c=>null, d=>12345, e=>012345, f=>1.234, g=>2.345e+4')`         {"a key": 1, "b": true, "c": null, "d": 12345, "e": "012345", "f": 1.234, "g": 2.345e+4} |
| `hstore_to_jsonb_loose` ( `hstore` )         jsonb                         Converts an `hstore` to a `jsonb` value, but         attempts to distinguish numerical and Boolean values so they are         unquoted in the JSON.                         `hstore_to_jsonb_loose('"a key"=>1, b=>t, c=>null, d=>12345, e=>012345, f=>1.234, g=>2.345e+4')`         {"a key": 1, "b": true, "c": null, "d": 12345, "e": "012345", "f": 1.234, "g": 2.345e+4} |
| `slice` ( `hstore`, `text[]` )         hstore                         Extracts a subset of an `hstore` containing only the         specified keys.                         `slice('a=>1,b=>2,c=>3'::hstore, ARRAY['b','c','x'])`         "b"=>"2", "c"=>"3" |
| `each` ( `hstore` )         setof record         ( key `text`,         value `text` )                         Extracts an `hstore`'s keys and values as a set of records.                         `select * from each('a=>1,b=>2')`           ``` key | value -----+-------  a   | 1  b   | 2 ``` |
| `exist` ( `hstore`, `text` )         boolean                         Does `hstore` contain key?                         `exist('a=>1', 'a')`         t |
| `defined` ( `hstore`, `text` )         boolean                         Does `hstore` contain a non-`NULL` value         for key?                         `defined('a=>NULL', 'a')`         f |
| `delete` ( `hstore`, `text` )         hstore                         Deletes pair with matching key.                         `delete('a=>1,b=>2', 'b')`         "a"=>"1" |
| `delete` ( `hstore`, `text[]` )         hstore                         Deletes pairs with matching keys.                         `delete('a=>1,b=>2,c=>3', ARRAY['a','b'])`         "c"=>"3" |
| `delete` ( `hstore`, `hstore` )         hstore                         Deletes pairs matching those in the second argument.                         `delete('a=>1,b=>2', 'a=>4,b=>2'::hstore)`         "a"=>"1" |
| `populate_record` ( `anyelement`, `hstore` )         anyelement                         Replaces fields in the left operand (which must be a composite type)         with matching values from `hstore`.                         `populate_record(ROW(1,2), 'f1=>42'::hstore)`         (42,2) |

In addition to these operators and functions, values of
the `hstore` type can be subscripted, allowing them to act
like associative arrays.  Only a single subscript of type `text`
can be specified; it is interpreted as a key and the corresponding
value is fetched or stored.  For example,

```
CREATE TABLE mytable (h hstore);
INSERT INTO mytable VALUES ('a=>b, c=>d');
SELECT h['a'] FROM mytable;
h
---
b
(1 row)

UPDATE mytable SET h['c'] = 'new';
SELECT h FROM mytable;
h
----------------------
"a"=>"b", "c"=>"new"
(1 row)
```

A subscripted fetch returns `NULL` if the subscript
is `NULL` or that key does not exist in
the `hstore`.  (Thus, a subscripted fetch is not greatly
different from the `->` operator.)
A subscripted update fails if the subscript is `NULL`;
otherwise, it replaces the value for that key, adding an entry to
the `hstore` if the key does not already exist.

### Functions

The aggregator is an aggregate function
`int_array_aggregate(integer)`
that produces an integer array
containing exactly the integers it is fed.
This is a wrapper around `array_agg`,
which does the same thing for any array type.

The enumerator is a function
`int_array_enum(integer[])`
that returns `setof integer`.  It is essentially the reverse
operation of the aggregator: given an array of integers, expand it
into a set of rows.  This is a wrapper around `unnest`,
which does the same thing for any array type.

### `intarray` Functions and Operators

The functions provided by the `intarray` module
are shown in [intarray-func-table](#intarray-func-table), the operators
in [intarray-op-table](#intarray-op-table).

| Function                         Description                         Example(s) |
| --- |
| `icount` ( `integer[]` )         integer                         Returns the number of elements in the array.                         `icount('{1,2,3}'::integer[])`         3 |
| `sort` ( `integer[]`, dir `text` )         integer[]                         Sorts the array in either ascending or descending order.         dir must be `asc`         or `desc`.                         `sort('{1,3,2}'::integer[], 'desc')`         {3,2,1} |
| `sort` ( `integer[]` )         integer[]                                  `sort_asc` ( `integer[]` )         integer[]                         Sorts in ascending order.                         `sort(array[11,77,44])`         {11,44,77} |
| `sort_desc` ( `integer[]` )         integer[]                         Sorts in descending order.                         `sort_desc(array[11,77,44])`         {77,44,11} |
| `uniq` ( `integer[]` )         integer[]                         Removes adjacent duplicates.         Often used with `sort` to remove all duplicates.                         `uniq('{1,2,2,3,1,1}'::integer[])`         {1,2,3,1}                         `uniq(sort('{1,2,3,2,1}'::integer[]))`         {1,2,3} |
| `idx` ( `integer[]`, item `integer` )         integer                         Returns index of the first array element         matching item, or 0 if no match.                         `idx(array[11,22,33,22,11], 22)`         2 |
| `subarray` ( `integer[]`, start `integer`, len `integer` )         integer[]                         Extracts the portion of the array starting at         position start, with len         elements.                         `subarray('{1,2,3,2,1}'::integer[], 2, 3)`         {2,3,2} |
| `subarray` ( `integer[]`, start `integer` )         integer[]                         Extracts the portion of the array starting at         position start.                         `subarray('{1,2,3,2,1}'::integer[], 2)`         {2,3,2,1} |
| `intset` ( `integer` )         integer[]                         Makes a single-element array.                         `intset(42)`         {42} |

| Operator                         Description |
| --- |
| `integer[]` `&&` `integer[]`         boolean                         Do arrays overlap (have at least one element in common)? |
| `integer[]` `@>` `integer[]`         boolean                         Does left array contain right array? |
| `integer[]` ` '{1,2}';

-- the same, using QUERY operator
SELECT message.mid FROM message WHERE message.sections @@ '1&2'::query_int;
```

### Functions and Operators

The `isn` module provides the standard comparison operators,
plus B-tree and hash indexing support for all these data types.  In
addition there are several specialized functions; shown in [isn-functions](#isn-functions).
In this table,
`isn` means any one of the module's data types.

| Function                         Description |
| --- |
| `isn_weak` ( `boolean` )         boolean                         Sets the weak input mode, and returns new setting. |
| `isn_weak` ()         boolean                         Returns the current status of the weak mode. |
| `make_valid` ( `isn` )         isn                         Validates an invalid number (clears the invalid flag). |
| `is_valid` ( `isn` )         boolean                         Checks for the presence of the invalid flag. |

*Weak* mode is used to be able to insert invalid data
into a table. Invalid means the check digit is wrong, not that there are
missing numbers.

Why would you want to use the weak mode? Well, it could be that
you have a huge collection of ISBN numbers, and that there are so many of
them that for weird reasons some have the wrong check digit (perhaps the
numbers were scanned from a printed list and the OCR got the numbers wrong,
perhaps the numbers were manually captured... who knows). Anyway, the point
is you might want to clean the mess up, but you still want to be able to
have all the numbers in your database and maybe use an external tool to
locate the invalid numbers in the database so you can verify the
information and validate it more easily; so for example you'd want to
select all the invalid numbers in the table.

When you insert invalid numbers in a table using the weak mode, the number
will be inserted with the corrected check digit, but it will be displayed
with an exclamation mark (`!`) at the end, for example
`0-11-000322-5!`.  This invalid marker can be checked with
the `is_valid` function and cleared with the
`make_valid` function.

You can also force the insertion of invalid numbers even when not in the
weak mode, by appending the `!` character at the end of the
number.

Another special feature is that during input, you can write
`?` in place of the check digit, and the correct check digit
will be inserted automatically.

### Operators and Functions

Type `ltree` has the usual comparison operators
`=`, `<>`,
`<`, `>`, `<=`, `>=`.
Comparison sorts in the order of a tree traversal, with the children
of a node sorted by label text.  In addition, the specialized
operators shown in [ltree-op-table](#ltree-op-table) are available.

| Operator                         Description |
| --- |
| `ltree` `@>` `ltree`         boolean                         Is left argument an ancestor of right (or equal)? |
| `ltree` `` `ltree`         boolean                         `ltree` `` `ltree[]`         boolean                         Does array contain a descendant of `ltree`? |
| `ltree[]` `~` `lquery`         boolean                         `lquery` `~` `ltree[]`         boolean                         Does array contain any path matching `lquery`? |
| `ltree[]` `?` `lquery[]`         boolean                         `lquery[]` `?` `ltree[]`         boolean                         Does `ltree` array contain any path matching         any `lquery`? |
| `ltree[]` `@` `ltxtquery`         boolean                         `ltxtquery` `@` `ltree[]`         boolean                         Does array contain any path matching `ltxtquery`? |
| `ltree[]` `?@>` `ltree`         ltree                         Returns first array entry that is an ancestor of `ltree`,         or `NULL` if none. |
| `ltree[]` `?=`, `>`
- GiST index over `ltree` (`gist_ltree_ops`
opclass):
`=`, `>`,
`@>`, ` ltree[]`,
`@`, `~`, `?`

`gist__ltree_ops` GiST opclass works similarly to
`gist_ltree_ops` and also takes signature length as
a parameter.  The default value of `siglen` in
`gist__ltree_ops` is 28 bytes.

Example of creating such an index with the default signature length of 28 bytes:

```
CREATE INDEX path_gist_idx ON test USING GIST (array_path);
```

Example of creating such an index with a signature length of 100 bytes:

```
CREATE INDEX path_gist_idx ON test USING GIST (array_path gist__ltree_ops(siglen=100));
```

Note: This index type is lossy.

### Functions

**`pg_old_snapshot_time_mapping(array_offset OUT int4, end_timestamp OUT timestamptz, newest_xmin OUT xid) returns setof record`**
: Returns all of the entries in the server's timestamp to XID mapping.
Each entry represents the newest xmin of any snapshot taken in the
corresponding minute.

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

## pgcrypto — cryptographic functions

The `pgcrypto` module provides cryptographic functions for
PostgreSQL.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

`pgcrypto` requires OpenSSL and won't be installed if
OpenSSL support was not selected when PostgreSQL was built.

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

### Password Hashing Functions

The functions `crypt()` and `gen_salt()`
are specifically designed for hashing passwords.
`crypt()` does the hashing and `gen_salt()`
prepares algorithm parameters for it.

The algorithms in `crypt()` differ from the usual
MD5 or SHA1 hashing algorithms in the following respects:

1. They are slow.  As the amount of data is so small, this is the only
way to make brute-forcing passwords hard.
2. They use a random value, called the *salt*, so that users
having the same password will have different encrypted passwords.
This is also an additional defense against reversing the algorithm.
3. They include the algorithm type in the result, so passwords hashed with
different algorithms can co-exist.
4. Some of them are adaptive — that means when computers get
faster, you can tune the algorithm to be slower, without
introducing incompatibility with existing passwords.

[pgcrypto-crypt-algorithms](#pgcrypto-crypt-algorithms) lists the algorithms
supported by the `crypt()` function.

| Algorithm | Max Password Length | Adaptive? | Salt Bits | Output Length | Description |
| --- | --- | --- | --- | --- | --- |
| `bf` | 72 | yes | 128 | 60 | Blowfish-based, variant 2a |
| `md5` | unlimited | no | 48 | 34 | MD5-based crypt |
| `xdes` | 8 | yes | 24 | 20 | Extended DES |
| `des` | 8 | no | 12 | 13 | Original UNIX crypt |

#### `crypt()`

```
crypt(password text, salt text) returns text
```

Calculates a crypt(3)-style hash of
password.
When storing a new password, you need to use
`gen_salt()` to generate a new
salt value.
To check a password, pass the stored hash value as
salt,
and test whether the result matches the stored value.

Example of setting a new password:

```
UPDATE ... SET pswhash = crypt('new password', gen_salt('md5'));
```

Example of authentication:

```
SELECT (pswhash = crypt('entered password', pswhash)) AS pswmatch FROM ... ;
```

This returns `true` if the entered password is correct.

#### `gen_salt()`

```
gen_salt(type text [, iter_count integer ]) returns text
```

Generates a new random salt string for use in `crypt()`.
The salt string also tells `crypt()` which algorithm to use.

The
type parameter specifies the hashing algorithm.
The accepted types are: `des`, `xdes`,
`md5` and `bf`.

The
iter_count parameter lets the user specify the iteration
count, for algorithms that have one.
The higher the count, the more time it takes to hash
the password and therefore the more time to break it.  Although with
too high a count the time to calculate a hash may be several years
— which is somewhat impractical.  If the
iter_count
parameter is omitted, the default iteration count is used.
Allowed values for
iter_count depend on the algorithm and
are shown in [pgcrypto-icfc-table](#pgcrypto-icfc-table).

| Algorithm | Default | Min | Max |
| --- | --- | --- | --- |
| `xdes` | 725 | 1 | 16777215 |
| `bf` | 6 | 4 | 31 |

For `xdes` there is an additional limitation that the
iteration count must be an odd number.

To pick an appropriate iteration count, consider that
the original DES crypt was designed to have the speed of 4 hashes per
second on the hardware of that time.
Slower than 4 hashes per second would probably dampen usability.
Faster than 100 hashes per second is probably too fast.

[pgcrypto-hash-speed-table](#pgcrypto-hash-speed-table) gives an overview of the relative slowness
of different hashing algorithms.
The table shows how much time it would take to try all
combinations of characters in an 8-character password, assuming
that the password contains either only lower case letters, or
upper- and lower-case letters and numbers.
In the `crypt-bf` entries, the number after a slash is
the
iter_count parameter of
`gen_salt`.

| Algorithm | Hashes/sec | For `[a-z]` | For `[A-Za-z0-9]` | Duration relative to `md5 hash` |
| --- | --- | --- | --- | --- |
| `crypt-bf/8` | 1792 | 4 years | 3927 years | 100k |
| `crypt-bf/7` | 3648 | 2 years | 1929 years | 50k |
| `crypt-bf/6` | 7168 | 1 year | 982 years | 25k |
| `crypt-bf/5` | 13504 | 188 days | 521 years | 12.5k |
| `crypt-md5` | 171584 | 15 days | 41 years | 1k |
| `crypt-des` | 23221568 | 157.5 minutes | 108 days | 7 |
| `sha1` | 37774272 | 90 minutes | 68 days | 4 |
| `md5` (hash) | 150085504 | 22.5 minutes | 17 days | 1 |

Notes:

- The machine used is an Intel Mobile Core i3.
- `crypt-des` and `crypt-md5` algorithm numbers are
taken from John the Ripper v1.6.38 `-test` output.
- `md5 hash` numbers are from mdcrack 1.2.
- `sha1` numbers are from lcrack-20031130-beta.
- `crypt-bf` numbers are taken using a simple program that
loops over 1000 8-character passwords.  That way the speed
with different numbers of iterations can be shown.  For reference: `john
-test` shows 13506 loops/sec for `crypt-bf/5`.
(The very small
difference in results is in accordance with the fact that the
`crypt-bf` implementation in `pgcrypto`
is the same one used in John the Ripper.)

Note that "try all combinations" is not a realistic exercise.
Usually password cracking is done with the help of dictionaries, which
contain both regular words and various mutations of them.  So, even
somewhat word-like passwords could be cracked much faster than the above
numbers suggest, while a 6-character non-word-like password may escape
cracking.  Or not.

### PGP Encryption Functions

The functions here implement the encryption part of the OpenPGP
([RFC 4880](https://datatracker.ietf.org/doc/html/rfc4880))
standard.  Supported are both symmetric-key and public-key encryption.

An encrypted PGP message consists of 2 parts, or *packets*:

- Packet containing a session key — either symmetric-key or public-key
encrypted.
- Packet containing data encrypted with the session key.

When encrypting with a symmetric key (i.e., a password):

1. The given password is hashed using a String2Key (S2K) algorithm.  This is
rather similar to `crypt()` algorithms — purposefully
slow and with random salt — but it produces a full-length binary
key.
2. If a separate session key is requested, a new random key will be
generated.  Otherwise the S2K key will be used directly as the session
key.
3. If the S2K key is to be used directly, then only S2K settings will be put
into the session key packet.  Otherwise the session key will be encrypted
with the S2K key and put into the session key packet.

When encrypting with a public key:

1. A new random session key is generated.
2. It is encrypted using the public key and put into the session key packet.

In either case the data to be encrypted is processed as follows:

1. Optional data-manipulation: compression, conversion to UTF-8,
and/or conversion of line-endings.
2. The data is prefixed with a block of random bytes.  This is equivalent
to using a random IV.
3. A SHA1 hash of the random prefix and data is appended.
4. All this is encrypted with the session key and placed in the data packet.

#### `pgp_sym_encrypt()`

```
pgp_sym_encrypt(data text, psw text [, options text ]) returns bytea
pgp_sym_encrypt_bytea(data bytea, psw text [, options text ]) returns bytea
```

Encrypt
data with a symmetric PGP key
psw.
The
options parameter can contain option settings,
as described below.

#### `pgp_sym_decrypt()`

```
pgp_sym_decrypt(msg bytea, psw text [, options text ]) returns text
pgp_sym_decrypt_bytea(msg bytea, psw text [, options text ]) returns bytea
```

Decrypt a symmetric-key-encrypted PGP message.

Decrypting `bytea` data with `pgp_sym_decrypt` is disallowed.
This is to avoid outputting invalid character data.  Decrypting
originally textual data with `pgp_sym_decrypt_bytea` is fine.

The
options parameter can contain option settings,
as described below.

#### `pgp_pub_encrypt()`

```
pgp_pub_encrypt(data text, key bytea [, options text ]) returns bytea
pgp_pub_encrypt_bytea(data bytea, key bytea [, options text ]) returns bytea
```

Encrypt
data with a public PGP key
key.
Giving this function a secret key will produce an error.

The
options parameter can contain option settings,
as described below.

#### `pgp_pub_decrypt()`

```
pgp_pub_decrypt(msg bytea, key bytea [, psw text [, options text ]]) returns text
pgp_pub_decrypt_bytea(msg bytea, key bytea [, psw text [, options text ]]) returns bytea
```

Decrypt a public-key-encrypted message.
key must be the
secret key corresponding to the public key that was used to encrypt.
If the secret key is password-protected, you must give the password in

psw.  If there is no password, but you want to specify
options, you need to give an empty password.

Decrypting `bytea` data with `pgp_pub_decrypt` is disallowed.
This is to avoid outputting invalid character data.  Decrypting
originally textual data with `pgp_pub_decrypt_bytea` is fine.

The
options parameter can contain option settings,
as described below.

#### `pgp_key_id()`

```
pgp_key_id(bytea) returns text
```

`pgp_key_id` extracts the key ID of a PGP public or secret key.
Or it gives the key ID that was used for encrypting the data, if given
an encrypted message.

It can return 2 special key IDs:

- `SYMKEY`

The message is encrypted with a symmetric key.
- `ANYKEY`

The message is public-key encrypted, but the key ID has been removed.
That means you will need to try all your secret keys on it to see
which one decrypts it.  `pgcrypto` itself does not produce
such messages.

Note that different keys may have the same ID.   This is rare but a normal
event. The client application should then try to decrypt with each one,
to see which fits — like handling `ANYKEY`.

#### `armor()`, `dearmor()`

```
armor(data bytea [ , keys text[], values text[] ]) returns text
dearmor(data text) returns bytea
```

These functions wrap/unwrap binary data into PGP ASCII-armor format,
which is basically Base64 with CRC and additional formatting.

If the
keys and
values arrays are specified,
an *armor header* is added to the armored format for each
key/value pair. Both arrays must be single-dimensional, and they must
be of the same length.  The keys and values cannot contain any non-ASCII
characters.

#### `pgp_armor_headers`

```
pgp_armor_headers(data text, key out text, value out text) returns setof record
```

`pgp_armor_headers()` extracts the armor headers from

data.  The return value is a set of rows with two columns,
key and value.  If the keys or values contain any non-ASCII characters,
they are treated as UTF-8.

#### Options for PGP Functions

Options are named to be similar to GnuPG.  An option's value should be
given after an equal sign; separate options from each other with commas.
For example:

```
pgp_sym_encrypt(data, psw, 'compress-algo=1, cipher-algo=aes256')
```

All of the options except `convert-crlf` apply only to
encrypt functions.  Decrypt functions get the parameters from the PGP
data.

The most interesting options are probably
`compress-algo` and `unicode-mode`.
The rest should have reasonable defaults.

##### cipher-algo

Which cipher algorithm to use.

```
Values: bf, aes128, aes192, aes256, 3des, cast5
Default: aes128
Applies to: pgp_sym_encrypt, pgp_pub_encrypt
```

##### compress-algo

Which compression algorithm to use.  Only available if
PostgreSQL was built with zlib.

```
Values:
0 - no compression
1 - ZIP compression
2 - ZLIB compression (= ZIP plus meta-data and block CRCs)
Default: 0
Applies to: pgp_sym_encrypt, pgp_pub_encrypt
```

##### compress-level

How much to compress.  Higher levels compress smaller but are slower.
0 disables compression.

```
Values: 0, 1-9
Default: 6
Applies to: pgp_sym_encrypt, pgp_pub_encrypt
```

##### convert-crlf

Whether to convert `\n` into `\r\n` when
encrypting and `\r\n` to `\n` when
decrypting.  RFC 4880 specifies that text data should be stored using
`\r\n` line-feeds.  Use this to get fully RFC-compliant
behavior.

```
Values: 0, 1
Default: 0
Applies to: pgp_sym_encrypt, pgp_pub_encrypt, pgp_sym_decrypt, pgp_pub_decrypt
```

##### disable-mdc

Do not protect data with SHA-1.  The only good reason to use this
option is to achieve compatibility with ancient PGP products, predating
the addition of SHA-1 protected packets to RFC 4880.
Recent gnupg.org and pgp.com software supports it fine.

```
Values: 0, 1
Default: 0
Applies to: pgp_sym_encrypt, pgp_pub_encrypt
```

##### sess-key

Use separate session key.  Public-key encryption always uses a separate
session key; this option is for symmetric-key encryption, which by default
uses the S2K key directly.

```
Values: 0, 1
Default: 0
Applies to: pgp_sym_encrypt
```

##### s2k-mode

Which S2K algorithm to use.

```
Values:
0 - Without salt.  Dangerous!
1 - With salt but with fixed iteration count.
3 - Variable iteration count.
Default: 3
Applies to: pgp_sym_encrypt
```

##### s2k-count

The number of iterations of the S2K algorithm to use.  It must
be a value between 1024 and 65011712, inclusive.

```
Default: A random value between 65536 and 253952
Applies to: pgp_sym_encrypt, only with s2k-mode=3
```

##### s2k-digest-algo

Which digest algorithm to use in S2K calculation.

```
Values: md5, sha1
Default: sha1
Applies to: pgp_sym_encrypt
```

##### s2k-cipher-algo

Which cipher to use for encrypting separate session key.

```
Values: bf, aes, aes128, aes192, aes256
Default: use cipher-algo
Applies to: pgp_sym_encrypt
```

##### unicode-mode

Whether to convert textual data from database internal encoding to
UTF-8 and back.  If your database already is UTF-8, no conversion will
be done, but the message will be tagged as UTF-8.  Without this option
it will not be.

```
Values: 0, 1
Default: 0
Applies to: pgp_sym_encrypt, pgp_pub_encrypt
```

#### Generating PGP Keys with GnuPG

To generate a new key:

```
gpg --gen-key
```

The preferred key type is "DSA and Elgamal".

For RSA encryption you must create either DSA or RSA sign-only key
as master and then add an RSA encryption subkey with
`gpg --edit-key`.

To list keys:

```
gpg --list-secret-keys
```

To export a public key in ASCII-armor format:

```
gpg -a --export KEYID > public.key
```

To export a secret key in ASCII-armor format:

```
gpg -a --export-secret-keys KEYID > secret.key
```

You need to use `dearmor()` on these keys before giving them to
the PGP functions.  Or if you can handle binary data, you can drop
`-a` from the command.

For more details see `man gpg`,
[The GNU
Privacy Handbook](https://www.gnupg.org/gph/en/manual.html) and other documentation on
[](https://www.gnupg.org/).

#### Limitations of PGP Code

- No support for signing.  That also means that it is not checked
whether the encryption subkey belongs to the master key.
- No support for encryption key as master key.  As such practice
is generally discouraged, this should not be a problem.
- No support for several subkeys.  This may seem like a problem, as this
is common practice.  On the other hand, you should not use your regular
GPG/PGP keys with `pgcrypto`, but create new ones,
as the usage scenario is rather different.

### Raw Encryption Functions

These functions only run a cipher over data; they don't have any advanced
features of PGP encryption.  Therefore they have some major problems:

1. They use user key directly as cipher key.
2. They don't provide any integrity checking, to see
if the encrypted data was modified.
3. They expect that users manage all encryption parameters
themselves, even IV.
4. They don't handle text.

So, with the introduction of PGP encryption, usage of raw
encryption functions is discouraged.

```
encrypt(data bytea, key bytea, type text) returns bytea
decrypt(data bytea, key bytea, type text) returns bytea

encrypt_iv(data bytea, key bytea, iv bytea, type text) returns bytea
decrypt_iv(data bytea, key bytea, iv bytea, type text) returns bytea
```

Encrypt/decrypt data using the cipher method specified by

type.  The syntax of the

type string is:

```
`algorithm` ` `-` `mode`   `/pad:` `padding`
```

where `algorithm` is one of:

- `bf` — Blowfish
- `aes` — AES (Rijndael-128, -192 or -256)

and `mode` is one of:

- `cbc` — next block depends on previous (default)
- `ecb` — each block is encrypted separately (for
testing only)

and `padding` is one of:

- `pkcs` — data may be any length (default)
- `none` — data must be multiple of cipher block size

So, for example, these are equivalent:

```
encrypt(data, 'fooz', 'bf')
encrypt(data, 'fooz', 'bf-cbc/pad:pkcs')
```

In `encrypt_iv` and `decrypt_iv`, the

iv parameter is the initial value for the CBC mode;
it is ignored for ECB.
It is clipped or padded with zeroes if not exactly block size.
It defaults to all zeroes in the functions without this parameter.

### Random-Data Functions

```
gen_random_bytes(count integer) returns bytea
```

Returns
count cryptographically strong random bytes.
At most 1024 bytes can be extracted at a time.  This is to avoid
draining the randomness generator pool.

```
gen_random_uuid() returns uuid
```

Returns a version 4 (random) UUID. (Obsolete, this function
internally calls the [core
function](#functions-uuid) of the same name.)

### Notes

#### Configuration

`pgcrypto` configures itself according to the findings of the
main PostgreSQL `configure` script.  The options that
affect it are `--with-zlib` and
`--with-ssl=openssl`.

When compiled with zlib, PGP encryption functions are able to
compress data before encrypting.

`pgcrypto` requires OpenSSL.
Otherwise, it will not be built or installed.

When compiled against OpenSSL 3.0.0 and later
versions, the legacy provider must be activated in the
`openssl.cnf` configuration file in order to use older
ciphers like DES or Blowfish.

#### NULL Handling

As is standard in SQL, all functions return NULL, if any of the arguments
are NULL.  This may create security risks on careless usage.

#### Security Limitations

All `pgcrypto` functions run inside the database server.
That means that all
the data and passwords move between `pgcrypto` and client
applications in clear text.  Thus you must:

1. Connect locally or use SSL connections.
2. Trust both system and database administrator.

If you cannot, then better do crypto inside client application.

The implementation does not resist
[side-channel
attacks](https://en.wikipedia.org/wiki/Side-channel_attack).  For example, the time required for
a `pgcrypto` decryption function to complete varies among
ciphertexts of a given size.

### Author

Marko Kreen markokr@gmail.com

`pgcrypto` uses code from the following sources:

| Algorithm | Author | Source origin |
| --- | --- | --- |
| DES crypt | David Burren and others | FreeBSD libcrypt |
| MD5 crypt | Poul-Henning Kamp | FreeBSD libcrypt |
| Blowfish crypt | Solar Designer | www.openwall.com |

### Functions

**`pg_freespace(rel regclass IN, blkno bigint IN) returns int2`**
: Returns the amount of free space on the page of the relation, specified
by `blkno`, according to the FSM.

**`pg_freespace(rel regclass IN, blkno OUT bigint, avail OUT int2)`**
: Displays the amount of free space on each page of the relation,
according to the FSM. A set of
`(blkno bigint, avail int2)`
tuples is returned, one tuple for each page in the relation.

The values stored in the free space map are not exact. They're rounded
to precision of 1/256th of `BLCKSZ` (32 bytes with default `BLCKSZ`), and
they're not kept fully up-to-date as tuples are inserted and updated.

For indexes, what is tracked is entirely-unused pages, rather than free
space within pages.  Therefore, the values are not meaningful, just
whether a page is in-use or empty.

### Functions

```
pg_prewarm(regclass, mode text default 'buffer', fork text default 'main',
first_block int8 default null,
last_block int8 default null) RETURNS int8
```

The first argument is the relation to be prewarmed.  The second argument
is the prewarming method to be used, as further discussed below; the third
is the relation fork to be prewarmed, usually `main`.
The fourth argument is the first block number to prewarm
(`NULL` is accepted as a synonym for zero).  The fifth
argument is the last block number to prewarm (`NULL`
means prewarm through the last block in the relation).  The return value
is the number of blocks prewarmed.

There are three available prewarming methods.  `prefetch`
issues asynchronous prefetch requests to the operating system, if this is
supported, or throws an error otherwise.  `read` reads
the requested range of blocks; unlike `prefetch`, this is
synchronous and supported on all platforms and builds, but may be slower.
`buffer` reads the requested range of blocks into the
database buffer cache.

Note that with any of these methods, attempting to prewarm more blocks than
can be cached — by the OS when using `prefetch` or
`read`, or by PostgreSQL when
using `buffer` — will likely result in lower-numbered
blocks being evicted as higher numbered blocks are read in.  Prewarmed data
also enjoys no special protection from cache evictions, so it is possible
that other system activity may evict the newly prewarmed blocks shortly
after they are read; conversely, prewarming may also evict other data from
cache. For these reasons, prewarming is typically most useful at startup,
when caches are largely empty.

```
autoprewarm_start_worker() RETURNS void
```

Launch the main autoprewarm worker.  This will normally happen
automatically, but is useful if automatic prewarm was not configured at
server startup time and you wish to start up the worker at a later time.

```
autoprewarm_dump_now() RETURNS int8
```

Update `autoprewarm.blocks` immediately.  This may be useful
if the autoprewarm worker is not running but you anticipate running it
after the next restart.  The return value is the number of records written
to `autoprewarm.blocks`.

### Functions

**`pg_stat_statements_reset(userid Oid, dbid Oid, queryid bigint) returns void`**
: `pg_stat_statements_reset` discards statistics
gathered so far by `pg_stat_statements` corresponding
to the specified `userid`, `dbid`
and `queryid`.  If any of the parameters are not
specified, the default value `0`(invalid) is used for
each of them and the statistics that match with other parameters will be
reset.  If no parameter is specified or all the specified parameters are
`0`(invalid), it will discard all statistics.
If all statistics in the `pg_stat_statements`
view are discarded, it will also reset the statistics in the
`pg_stat_statements_info` view.
By default, this function can only be executed by superusers.
Access may be granted to others using `GRANT`.

**`pg_stat_statements(showtext boolean) returns setof record`**
: The `pg_stat_statements` view is defined in
terms of a function also named `pg_stat_statements`.
It is possible for clients to call
the `pg_stat_statements` function directly, and by
specifying `showtext := false` have query text be
omitted (that is, the `OUT` argument that corresponds
to the view's `query` column will return nulls).  This
feature is intended to support external tools that might wish to avoid
the overhead of repeatedly retrieving query texts of indeterminate
length.  Such tools can instead cache the first query text observed
for each entry themselves, since that is
all `pg_stat_statements` itself does, and then retrieve
query texts only as needed.  Since the server stores query texts in a
file, this approach may reduce physical I/O for repeated examination
of the `pg_stat_statements` data.

### Functions

**`pgstattuple(regclass) returns record`**
: `pgstattuple` returns a relation's physical length,
percentage of "dead" tuples, and other info. This may help users
to determine whether vacuum is necessary or not.  The argument is the
target relation's name (optionally schema-qualified) or OID.
For example:

```
test=> SELECT * FROM pgstattuple('pg_catalog.pg_proc');
-[ RECORD 1 ]------+-------
table_len          | 458752
tuple_count        | 1470
tuple_len          | 438896
tuple_percent      | 95.67
dead_tuple_count   | 11
dead_tuple_len     | 3157
dead_tuple_percent | 0.69
free_space         | 8932
free_percent       | 1.95
```

The output columns are described in [pgstattuple-columns](#pgstattuple-columns).

### Functions

**`heap_force_kill(regclass, tid[]) returns void`**
: `heap_force_kill` marks "used" line
pointers as "dead" without examining the tuples. The
intended use of this function is to forcibly remove tuples that are not
otherwise accessible. For example:

```
test=> select * from t1 where ctid = '(0, 1)';
ERROR:  could not access status of transaction 4007513275
DETAIL:  Could not open file "pg_xact/0EED": No such file or directory.

test=# select heap_force_kill('t1'::regclass, ARRAY['(0, 1)']::tid[]);
heap_force_kill
-----------------

(1 row)

test=# select * from t1 where ctid = '(0, 1)';
(0 rows)
```

**`heap_force_freeze(regclass, tid[]) returns void`**
: `heap_force_freeze` marks tuples as frozen without
examining the tuple data. The intended use of this function is to
make accessible tuples which are inaccessible due to corrupted
visibility information, or which prevent the table from being
successfully vacuumed due to corrupted visibility information.
For example:

```
test=> vacuum t1;
ERROR:  found xmin 507 from before relfrozenxid 515
CONTEXT:  while scanning block 0 of relation "public.t1"

test=# select ctid from t1 where xmin = 507;
ctid
-------
(0,3)
(1 row)

test=# select heap_force_freeze('t1'::regclass, ARRAY['(0, 3)']::tid[]);
heap_force_freeze
-------------------

(1 row)

test=# select ctid from t1 where xmin = 2;
ctid
-------
(0,3)
(1 row)
```

### Functions and Operators

The functions provided by the `pg_trgm` module
are shown in [pgtrgm-func-table](#pgtrgm-func-table), the operators
in [pgtrgm-op-table](#pgtrgm-op-table).

| Function                         Description |
| --- |
| `similarity` ( `text`, `text` )         real                         Returns a number that indicates how similar the two arguments are.         The range of the result is zero (indicating that the two strings are         completely dissimilar) to one (indicating that the two strings are         identical). |
| `show_trgm` ( `text` )         text[]                         Returns an array of all the trigrams in the given string.         (In practice this is seldom useful except for debugging.) |
| `word_similarity` ( `text`, `text` )         real                         Returns a number that indicates the greatest similarity between         the set of trigrams in the first string and any continuous extent         of an ordered set of trigrams in the second string.  For details, see         the explanation below. |
| `strict_word_similarity` ( `text`, `text` )         real                         Same as `word_similarity`, but forces         extent boundaries to match word boundaries.  Since we don't have         cross-word trigrams, this function actually returns greatest similarity         between first string and any continuous extent of words of the second         string. |
| `show_limit` ()         real                         Returns the current similarity threshold used by the `%`         operator.  This sets the minimum similarity between         two words for them to be considered similar enough to         be misspellings of each other, for example.         (*Deprecated*; instead use `SHOW`         `pg_trgm.similarity_threshold`.) |
| `set_limit` ( `real` )         real                         Sets the current similarity threshold that is used by the `%`         operator.  The threshold must be between 0 and 1 (default is 0.3).         Returns the same value passed in.         (*Deprecated*; instead use `SET`         `pg_trgm.similarity_threshold`.) |

Consider the following example:

```

### Functions

**`pg_visibility_map(relation regclass, blkno bigint, all_visible OUT boolean, all_frozen OUT boolean) returns record`**
: Returns the all-visible and all-frozen bits in the visibility map for
the given block of the given relation.

**`pg_visibility(relation regclass, blkno bigint, all_visible OUT boolean, all_frozen OUT boolean, pd_all_visible OUT boolean) returns record`**
: Returns the all-visible and all-frozen bits in the visibility map for
the given block of the given relation, plus the
`PD_ALL_VISIBLE` bit of that block.

**`pg_visibility_map(relation regclass, blkno OUT bigint, all_visible OUT boolean, all_frozen OUT boolean) returns setof record`**
: Returns the all-visible and all-frozen bits in the visibility map for
each block of the given relation.

**`pg_visibility(relation regclass, blkno OUT bigint, all_visible OUT boolean, all_frozen OUT boolean, pd_all_visible OUT boolean) returns setof record`**
: Returns the all-visible and all-frozen bits in the visibility map for
each block of the given relation, plus the `PD_ALL_VISIBLE`
bit of each block.

**`pg_visibility_map_summary(relation regclass, all_visible OUT bigint, all_frozen OUT bigint) returns record`**
: Returns the number of all-visible pages and the number of all-frozen
pages in the relation according to the visibility map.

**`pg_check_frozen(relation regclass, t_ctid OUT tid) returns setof tid`**
: Returns the TIDs of non-frozen tuples stored in pages marked all-frozen
in the visibility map.  If this function returns a non-empty set of
TIDs, the visibility map is corrupt.

**`pg_check_visible(relation regclass, t_ctid OUT tid) returns setof tid`**
: Returns the TIDs of non-all-visible tuples stored in pages marked
all-visible in the visibility map.  If this function returns a non-empty
set of TIDs, the visibility map is corrupt.

**`pg_truncate_visibility_map(relation regclass) returns void`**
: Truncates the visibility map for the given relation.  This function is
useful if you believe that the visibility map for the relation is
corrupt and wish to force rebuilding it.  The first `VACUUM`
executed on the given relation after this function is executed will scan
every page in the relation and rebuild the visibility map.  (Until that
is done, queries will treat the visibility map as containing all zeroes.)

By default, these functions are executable only by superusers and roles with privileges
of the `pg_stat_scan_tables` role, with the exception of
`pg_truncate_visibility_map(relation regclass)` which can only
be executed by superusers.

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

### Functions

**`postgres_fdw_get_connections(OUT server_name text, OUT valid boolean) returns setof record`**
: This function returns the foreign server names of all the open
connections that `postgres_fdw` established from
the local session to the foreign servers. It also returns whether
each connection is valid or not. `false` is returned
if the foreign server connection is used in the current local
transaction but its foreign server or user mapping is changed or
dropped (Note that server name of an invalid connection will be
`NULL` if the server is dropped),
and then such invalid connection will be closed at
the end of that transaction. `true` is returned
otherwise. If there are no open connections, no record is returned.
Example usage of the function:

```
postgres=# SELECT * FROM postgres_fdw_get_connections() ORDER BY 1;
server_name | valid
-------------+-------
loopback1   | t
loopback2   | f
```

**`postgres_fdw_disconnect(server_name text) returns boolean`**
: This function discards the open connections that are established by
`postgres_fdw` from the local session to
the foreign server with the given name.  Note that there can be
multiple connections to the given server using different user mappings.
If the connections are used in the current local transaction,
they are not disconnected and warning messages are reported.
This function returns `true` if it disconnects
at least one connection, otherwise `false`.
If no foreign server with the given name is found, an error is reported.
Example usage of the function:

```
postgres=# SELECT postgres_fdw_disconnect('loopback1');
postgres_fdw_disconnect
-------------------------
t
```

**`postgres_fdw_disconnect_all() returns boolean`**
: This function discards all the open connections that are established by
`postgres_fdw` from the local session to
foreign servers.  If the connections are used in the current local
transaction, they are not disconnected and warning messages are reported.
This function returns `true` if it disconnects
at least one connection, otherwise `false`.
Example usage of the function:

```
postgres=# SELECT postgres_fdw_disconnect_all();
postgres_fdw_disconnect_all
-----------------------------
t
```

### Sepgsql Functions

[sepgsql-functions-table](#sepgsql-functions-table) shows the available functions.

| Function                         Description |
| --- |
| `sepgsql_getcon` ()         text                         Returns the client domain, the current security label of the client. |
| `sepgsql_setcon` ( `text` )         boolean                         Switches the client domain of the current session to the new domain,         if allowed by the security policy.         It also accepts `NULL` input as a request to transition         to the client's original domain. |
| `sepgsql_mcstrans_in` ( `text` )         text                         Translates the given qualified MLS/MCS range into raw format if         the mcstrans daemon is running. |
| `sepgsql_mcstrans_out` ( `text` )         text                         Translates the given raw MLS/MCS range into qualified format if         the mcstrans daemon is running. |
| `sepgsql_restorecon` ( `text` )         boolean                         Sets up initial security labels for all objects within the         current database. The argument may be `NULL`, or the         name of a specfile to be used as alternative of the system default. |

### refint — Functions for Implementing Referential Integrity

`check_primary_key()` and
`check_foreign_key()` are used to check foreign key constraints.
(This functionality is long since superseded by the built-in foreign
key mechanism, of course, but the module is still useful as an example.)

`check_primary_key()` checks the referencing table.
To use, create a `BEFORE INSERT OR UPDATE` trigger using this
function on a table referencing another table. Specify as the trigger
arguments: the referencing table's column name(s) which form the foreign
key, the referenced table name, and the column names in the referenced table
which form the primary/unique key.  To handle multiple foreign
keys, create a trigger for each reference.

`check_foreign_key()` checks the referenced table.
To use, create a `BEFORE DELETE OR UPDATE` trigger using this
function on a table referenced by other table(s).  Specify as the trigger
arguments: the number of referencing tables for which the function has to
perform checking, the action if a referencing key is found
(`cascade` — to delete the referencing row,
`restrict` — to abort transaction if referencing keys
exist, `setnull` — to set referencing key fields to null),
the triggered table's column names which form the primary/unique key, then
the referencing table name and column names (repeated for as many
referencing tables as were specified by first argument).  Note that the
primary/unique key columns should be marked NOT NULL and should have a
unique index.

There are examples in `refint.example`.

### autoinc — Functions for Autoincrementing Fields

`autoinc()` is a trigger that stores the next value of
a sequence into an integer field.  This has some overlap with the
built-in "serial column" feature, but it is not the same:
`autoinc()` will override attempts to substitute a
different field value during inserts, and optionally it can be
used to increment the field during updates, too.

To use, create a `BEFORE INSERT` (or optionally `BEFORE
INSERT OR UPDATE`) trigger using this function.  Specify two
trigger arguments: the name of the integer column to be modified,
and the name of the sequence object that will supply values.
(Actually, you can specify any number of pairs of such names, if
you'd like to update more than one autoincrementing column.)

There is an example in `autoinc.example`.

### insert_username — Functions for Tracking Who Changed a Table

`insert_username()` is a trigger that stores the current
user's name into a text field.  This can be useful for tracking
who last modified a particular row within a table.

To use, create a `BEFORE INSERT` and/or `UPDATE`
trigger using this function.  Specify a single trigger
argument: the name of the text column to be modified.

There is an example in `insert_username.example`.

### moddatetime — Functions for Tracking Last Modification Time

`moddatetime()` is a trigger that stores the current
time into a `timestamp` field.  This can be useful for tracking
the last modification time of a particular row within a table.

To use, create a `BEFORE UPDATE`
trigger using this function.  Specify a single trigger
argument: the name of the column to be modified.
The column must be of type `timestamp` or `timestamp with
time zone`.

There is an example in `moddatetime.example`.

### Functions Provided

**`ssl_is_used() returns boolean`**
: Returns true if current connection to server uses SSL, and false
otherwise.

**`ssl_version() returns text`**
: Returns the name of the protocol used for the SSL connection (e.g., TLSv1.0,
TLSv1.1, TLSv1.2 or TLSv1.3).

**`ssl_cipher() returns text`**
: Returns the name of the cipher used for the SSL connection
(e.g., DHE-RSA-AES256-SHA).

**`ssl_client_cert_present() returns boolean`**
: Returns true if current client has presented a valid SSL client
certificate to the server, and false otherwise.  (The server
might or might not be configured to require a client certificate.)

**`ssl_client_serial() returns numeric`**
: Returns serial number of current client certificate.  The combination of
certificate serial number and certificate issuer is guaranteed to
uniquely identify a certificate (but not its owner — the owner
ought to regularly change their keys, and get new certificates from the
issuer).

So, if you run your own CA and allow only certificates from this CA to
be accepted by the server, the serial number is the most reliable (albeit
not very mnemonic) means to identify a user.

**`ssl_client_dn() returns text`**
: Returns the full subject of the current client certificate, converting
character data into the current database encoding.  It is assumed that
if you use non-ASCII characters in the certificate names, your
database is able to represent these characters, too.  If your database
uses the SQL_ASCII encoding, non-ASCII characters in the name will be
represented as UTF-8 sequences.

The result looks like `/CN=Somebody /C=Some country/O=Some organization`.

**`ssl_issuer_dn() returns text`**
: Returns the full issuer name of the current client certificate, converting
character data into the current database encoding.  Encoding conversions
are handled the same as for `ssl_client_dn`.

The combination of the return value of this function with the
certificate serial number uniquely identifies the certificate.

This function is really useful only if you have more than one trusted CA
certificate in your server's certificate authority file, or if this CA
has issued some intermediate certificate authority certificates.

**`ssl_client_dn_field(fieldname text) returns text`**
: This function returns the value of the specified field in the
certificate subject, or NULL if the field is not present.
Field names are string constants that are converted into ASN1 object
identifiers using the OpenSSL object
database.  The following values are acceptable:

```
commonName (alias CN)
surname (alias SN)
name
givenName (alias GN)
countryName (alias C)
localityName (alias L)
stateOrProvinceName (alias ST)
organizationName (alias O)
organizationalUnitName (alias OU)
title
description
initials
postalCode
streetAddress
generationQualifier
description
dnQualifier
x500UniqueIdentifier
pseudonym
role
emailAddress
```

All of these fields are optional, except `commonName`.
It depends
entirely on your CA's policy which of them would be included and which
wouldn't.  The meaning of these fields, however, is strictly defined by
the X.500 and X.509 standards, so you cannot just assign arbitrary
meaning to them.

**`ssl_issuer_field(fieldname text) returns text`**
: Same as `ssl_client_dn_field`, but for the certificate issuer
rather than the certificate subject.

**`ssl_extension_info() returns setof record`**
: Provide information about extensions of client certificate: extension name,
extension value, and if it is a critical extension.

## tablefunc — functions that return tables (`crosstab` and others)

The `tablefunc` module includes various functions that return
tables (that is, multiple rows).  These functions are useful both in their
own right and as examples of how to write C functions that return
multiple rows.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Functions Provided

[tablefunc-functions](#tablefunc-functions) summarizes the functions provided
by the `tablefunc` module.

| Function                         Description |
| --- |
| `normal_rand` ( numvals `integer`, mean `float8`, stddev `float8` )         setof float8                         Produces a set of normally distributed random values. |
| `crosstab` ( sql `text` )         setof record                         Produces a "pivot table" containing         row names plus `N` value columns, where         `N` is determined by the row type specified         in the calling query. |
| `crosstab`N`` ( sql `text` )         setof table_crosstab_`N`                         Produces a "pivot table" containing         row names plus `N` value columns.         `crosstab2`, `crosstab3`, and         `crosstab4` are predefined, but you can create additional         `crosstab`N`` functions as described below. |
| `crosstab` ( source_sql `text`, category_sql `text` )         setof record                         Produces a "pivot table"         with the value columns specified by a second query. |
| `crosstab` ( sql `text`, N `integer` )         setof record                         Obsolete version of `crosstab(text)`.         The parameter N is now ignored, since the         number of value columns is always determined by the calling query. |
| `connectby` ( relname `text`, keyid_fld `text`, parent_keyid_fld `text`         , orderby_fld `text` , start_with `text`, max_depth `integer`         , branch_delim `text`  )         setof record                         Produces a representation of a hierarchical tree structure. |

#### `normal_rand`

```
normal_rand(int numvals, float8 mean, float8 stddev) returns setof float8
```

`normal_rand` produces a set of normally distributed random
values (Gaussian distribution).

numvals is the number of values to be returned
from the function.
mean is the mean of the normal
distribution of values and
stddev is the standard
deviation of the normal distribution of values.

For example, this call requests 1000 values with a mean of 5 and a
standard deviation of 3:

```
test=# SELECT * FROM normal_rand(1000, 5, 3);
normal_rand
----------------------
1.56556322244898
9.10040991424657
5.36957140345079
-0.369151492880995
0.283600703686639
.
.
.
4.82992125404908
9.71308014517282
2.49639286969028
(1000 rows)
```

#### `crosstab(text)`

```
crosstab(text sql)
crosstab(text sql, int N)
```

The `crosstab` function is used to produce "pivot"
displays, wherein data is listed across the page rather than down.
For example, we might have data like

```
row1    val11
row1    val12
row1    val13
...
row2    val21
row2    val22
row2    val23
...
```

which we wish to display like

```
row1    val11   val12   val13   ...
row2    val21   val22   val23   ...
...
```

The `crosstab` function takes a text parameter that is an SQL
query producing raw data formatted in the first way, and produces a table
formatted in the second way.

The
sql parameter is an SQL statement that produces
the source set of data. This statement must return one
`row_name` column, one
`category` column, and one
`value` column.
N is an
obsolete parameter, ignored if supplied (formerly this had to match the
number of output value columns, but now that is determined by the
calling query).

For example, the provided query might produce a set something like:

```
row_name    cat    value
----------+-------+-------
row1      cat1    val1
row1      cat2    val2
row1      cat3    val3
row1      cat4    val4
row2      cat1    val5
row2      cat2    val6
row2      cat3    val7
row2      cat4    val8
```

The `crosstab` function is declared to return `setof
record`, so the actual names and types of the output columns must be
defined in the `FROM` clause of the calling `SELECT`
statement, for example:

```
SELECT * FROM crosstab('...') AS ct(row_name text, category_1 text, category_2 text);
```

This example produces a set something like:

```

row_name   category_1   category_2
----------+------------+------------
row1        val1         val2
row2        val5         val6
```

The `FROM` clause must define the output as one
`row_name` column (of the same data type as the first result
column of the SQL query) followed by N `value` columns
(all of the same data type as the third result column of the SQL query).
You can set up as many output value columns as you wish.  The names of the
output columns are up to you.

The `crosstab` function produces one output row for each
consecutive group of input rows with the same
`row_name` value.  It fills the output
`value` columns, left to right, with the
`value` fields from these rows.  If there
are fewer rows in a group than there are output `value`
columns, the extra output columns are filled with nulls; if there are
more rows, the extra input rows are skipped.

In practice the SQL query should always specify `ORDER BY 1,2`
to ensure that the input rows are properly ordered, that is, values with
the same `row_name` are brought together and
correctly ordered within the row.  Notice that `crosstab`
itself does not pay any attention to the second column of the query
result; it's just there to be ordered by, to control the order in which
the third-column values appear across the page.

Here is a complete example:

```
CREATE TABLE ct(id SERIAL, rowid TEXT, attribute TEXT, value TEXT);
INSERT INTO ct(rowid, attribute, value) VALUES('test1','att1','val1');
INSERT INTO ct(rowid, attribute, value) VALUES('test1','att2','val2');
INSERT INTO ct(rowid, attribute, value) VALUES('test1','att3','val3');
INSERT INTO ct(rowid, attribute, value) VALUES('test1','att4','val4');
INSERT INTO ct(rowid, attribute, value) VALUES('test2','att1','val5');
INSERT INTO ct(rowid, attribute, value) VALUES('test2','att2','val6');
INSERT INTO ct(rowid, attribute, value) VALUES('test2','att3','val7');
INSERT INTO ct(rowid, attribute, value) VALUES('test2','att4','val8');

SELECT *
FROM crosstab(
'select rowid, attribute, value
from ct
where attribute = ''att2'' or attribute = ''att3''
order by 1,2')
AS ct(row_name text, category_1 text, category_2 text, category_3 text);

row_name | category_1 | category_2 | category_3
----------+------------+------------+------------
test1    | val2       | val3       |
test2    | val6       | val7       |
(2 rows)
```

You can avoid always having to write out a `FROM` clause to
define the output columns, by setting up a custom crosstab function that
has the desired output row type wired into its definition.  This is
described in the next section.  Another possibility is to embed the
required `FROM` clause in a view definition.

> **Note:**

> See also the `[\crosstabview](#app-psql-meta-commands-crosstabview)`
> command in psql, which provides functionality similar
> to `crosstab()`.
>

#### `crosstab`N`(text)`

```
crosstab`N`(text sql)
```

The `crosstab`N`` functions are examples of how
to set up custom wrappers for the general `crosstab` function,
so that you need not write out column names and types in the calling
`SELECT` query.  The `tablefunc` module includes
`crosstab2`, `crosstab3`, and
`crosstab4`, whose output row types are defined as

```
CREATE TYPE tablefunc_crosstab_N AS (
row_name TEXT,
category_1 TEXT,
category_2 TEXT,
.
.
.
category_N TEXT
);
```

Thus, these functions can be used directly when the input query produces
`row_name` and `value` columns of type
`text`, and you want 2, 3, or 4 output values columns.
In all other ways they behave exactly as described above for the
general `crosstab` function.

For instance, the example given in the previous section would also
work as

```
SELECT *
FROM crosstab3(
'select rowid, attribute, value
from ct
where attribute = ''att2'' or attribute = ''att3''
order by 1,2');
```

These functions are provided mostly for illustration purposes. You
can create your own return types and functions based on the
underlying `crosstab()` function.  There are two ways
to do it:

- Create a composite type describing the desired output columns,
similar to the examples in
`contrib/tablefunc/tablefunc--1.0.sql`.
Then define a
unique function name accepting one `text` parameter and returning
`setof your_type_name`, but linking to the same underlying
`crosstab` C function.  For example, if your source data
produces row names that are `text`, and values that are
`float8`, and you want 5 value columns:

```
CREATE TYPE my_crosstab_float8_5_cols AS (
my_row_name text,
my_category_1 float8,
my_category_2 float8,
my_category_3 float8,
my_category_4 float8,
my_category_5 float8
);

CREATE OR REPLACE FUNCTION crosstab_float8_5_cols(text)
RETURNS setof my_crosstab_float8_5_cols
AS '$libdir/tablefunc','crosstab' LANGUAGE C STABLE STRICT;
```
- Use `OUT` parameters to define the return type implicitly.
The same example could also be done this way:

```
CREATE OR REPLACE FUNCTION crosstab_float8_5_cols(
IN text,
OUT my_row_name text,
OUT my_category_1 float8,
OUT my_category_2 float8,
OUT my_category_3 float8,
OUT my_category_4 float8,
OUT my_category_5 float8)
RETURNS setof record
AS '$libdir/tablefunc','crosstab' LANGUAGE C STABLE STRICT;
```

#### `crosstab(text, text)`

```
crosstab(text source_sql, text category_sql)
```

The main limitation of the single-parameter form of `crosstab`
is that it treats all values in a group alike, inserting each value into
the first available column.  If you want the value
columns to correspond to specific categories of data, and some groups
might not have data for some of the categories, that doesn't work well.
The two-parameter form of `crosstab` handles this case by
providing an explicit list of the categories corresponding to the
output columns.

source_sql is an SQL statement that produces the
source set of data.  This statement must return one
`row_name` column, one
`category` column, and one
`value` column. It may also have one or more
"extra" columns.
The `row_name` column must be first. The
`category` and `value`
columns must be the last two columns, in that order.  Any columns between
`row_name` and
`category` are treated as "extra".
The "extra" columns are expected to be the same for all rows
with the same `row_name` value.

For example,
source_sql might produce a set
something like:

```
SELECT row_name, extra_col, cat, value FROM foo ORDER BY 1;

row_name    extra_col   cat    value
----------+------------+-----+---------
row1         extra1    cat1    val1
row1         extra1    cat2    val2
row1         extra1    cat4    val4
row2         extra2    cat1    val5
row2         extra2    cat2    val6
row2         extra2    cat3    val7
row2         extra2    cat4    val8
```

category_sql is an SQL statement that produces
the set of categories. This statement must return only one column.
It must produce at least one row, or an error will be generated.
Also, it must not produce duplicate values, or an error will be
generated.
category_sql might be something like:

```
SELECT DISTINCT cat FROM foo ORDER BY 1;
cat
-------
cat1
cat2
cat3
cat4
```

The `crosstab` function is declared to return `setof
record`, so the actual names and types of the output columns must be
defined in the `FROM` clause of the calling `SELECT`
statement, for example:

```
SELECT * FROM crosstab('...', '...')
AS ct(row_name text, extra text, cat1 text, cat2 text, cat3 text, cat4 text);
```

This will produce a result something like:

```

row_name   extra   cat1   cat2   cat3   cat4
---------+-------+------+------+------+------
row1     extra1  val1   val2          val4
row2     extra2  val5   val6   val7   val8
```

The `FROM` clause must define the proper number of output
columns of the proper data types.  If there are `N`
columns in the
source_sql query's result, the first
`N`-2 of them must match up with the first
`N`-2 output columns.  The remaining output columns
must have the type of the last column of the
source_sql
query's result, and there must be exactly as many of them as there
are rows in the
category_sql query's result.

The `crosstab` function produces one output row for each
consecutive group of input rows with the same
`row_name` value.  The output
`row_name` column, plus any "extra"
columns, are copied from the first row of the group.  The output
`value` columns are filled with the
`value` fields from rows having matching
`category` values.  If a row's `category`
does not match any output of the
category_sql
query, its `value` is ignored.  Output
columns whose matching category is not present in any input row
of the group are filled with nulls.

In practice the
source_sql query should always
specify `ORDER BY 1` to ensure that values with the same
`row_name` are brought together.  However,
ordering of the categories within a group is not important.
Also, it is essential to be sure that the order of the

category_sql query's output matches the specified
output column order.

Here are two complete examples:

```
create table sales(year int, month int, qty int);
insert into sales values(2007, 1, 1000);
insert into sales values(2007, 2, 1500);
insert into sales values(2007, 7, 500);
insert into sales values(2007, 11, 1500);
insert into sales values(2007, 12, 2000);
insert into sales values(2008, 1, 1000);

select * from crosstab(
'select year, month, qty from sales order by 1',
'select m from generate_series(1,12) m'
) as (
year int,
"Jan" int,
"Feb" int,
"Mar" int,
"Apr" int,
"May" int,
"Jun" int,
"Jul" int,
"Aug" int,
"Sep" int,
"Oct" int,
"Nov" int,
"Dec" int
);
year | Jan  | Feb  | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov  | Dec
------+------+------+-----+-----+-----+-----+-----+-----+-----+-----+------+------
2007 | 1000 | 1500 |     |     |     |     | 500 |     |     |     | 1500 | 2000
2008 | 1000 |      |     |     |     |     |     |     |     |     |      |
(2 rows)
```

```
CREATE TABLE cth(rowid text, rowdt timestamp, attribute text, val text);
INSERT INTO cth VALUES('test1','01 March 2003','temperature','42');
INSERT INTO cth VALUES('test1','01 March 2003','test_result','PASS');
INSERT INTO cth VALUES('test1','01 March 2003','volts','2.6987');
INSERT INTO cth VALUES('test2','02 March 2003','temperature','53');
INSERT INTO cth VALUES('test2','02 March 2003','test_result','FAIL');
INSERT INTO cth VALUES('test2','02 March 2003','test_startdate','01 March 2003');
INSERT INTO cth VALUES('test2','02 March 2003','volts','3.1234');

SELECT * FROM crosstab
(
'SELECT rowid, rowdt, attribute, val FROM cth ORDER BY 1',
'SELECT DISTINCT attribute FROM cth ORDER BY 1'
)
AS
(
rowid text,
rowdt timestamp,
temperature int4,
test_result text,
test_startdate timestamp,
volts float8
);
rowid |          rowdt           | temperature | test_result |      test_startdate      | volts
-------+--------------------------+-------------+-------------+--------------------------+--------
test1 | Sat Mar 01 00:00:00 2003 |          42 | PASS        |                          | 2.6987
test2 | Sun Mar 02 00:00:00 2003 |          53 | FAIL        | Sat Mar 01 00:00:00 2003 | 3.1234
(2 rows)
```

You can create predefined functions to avoid having to write out
the result column names and types in each query.  See the examples
in the previous section.  The underlying C function for this form
of `crosstab` is named `crosstab_hash`.

#### `connectby`

```
connectby(text relname, text keyid_fld, text parent_keyid_fld
[, text orderby_fld ], text start_with, int max_depth
[, text branch_delim ])
```

The `connectby` function produces a display of hierarchical
data that is stored in a table.  The table must have a key field that
uniquely identifies rows, and a parent-key field that references the
parent (if any) of each row.  `connectby` can display the
sub-tree descending from any row.

[tablefunc-connectby-parameters](#tablefunc-connectby-parameters) explains the
parameters.

| Parameter | Description |
| --- | --- |
| relname | Name of the source relation |
| keyid_fld | Name of the key field |
| parent_keyid_fld | Name of the parent-key field |
| orderby_fld | Name of the field to order siblings by (optional) |
| start_with | Key value of the row to start at |
| max_depth | Maximum depth to descend to, or zero for unlimited depth |
| branch_delim | String to separate keys with in branch output (optional) |

The key and parent-key fields can be any data type, but they must be
the same type.  Note that the
start_with value must be
entered as a text string, regardless of the type of the key field.

The `connectby` function is declared to return `setof
record`, so the actual names and types of the output columns must be
defined in the `FROM` clause of the calling `SELECT`
statement, for example:

```
SELECT * FROM connectby('connectby_tree', 'keyid', 'parent_keyid', 'pos', 'row2', 0, '~')
AS t(keyid text, parent_keyid text, level int, branch text, pos int);
```

The first two output columns are used for the current row's key and
its parent row's key; they must match the type of the table's key field.
The third output column is the depth in the tree and must be of type
`integer`.  If a
branch_delim parameter was
given, the next output column is the branch display and must be of type
`text`.  Finally, if an
orderby_fld
parameter was given, the last output column is a serial number, and must
be of type `integer`.

The "branch" output column shows the path of keys taken to
reach the current row.  The keys are separated by the specified

branch_delim string.  If no branch display is
wanted, omit both the
branch_delim parameter
and the branch column in the output column list.

If the ordering of siblings of the same parent is important,
include the
orderby_fld parameter to
specify which field to order siblings by.  This field can be of any
sortable data type.  The output column list must include a final
integer serial-number column, if and only if

orderby_fld is specified.

The parameters representing table and field names are copied as-is
into the SQL queries that `connectby` generates internally.
Therefore, include double quotes if the names are mixed-case or contain
special characters.  You may also need to schema-qualify the table name.

In large tables, performance will be poor unless there is an index on
the parent-key field.

It is important that the
branch_delim string
not appear in any key values, else `connectby` may incorrectly
report an infinite-recursion error.  Note that if

branch_delim is not provided, a default value
of `~` is used for recursion detection purposes.

Here is an example:

```
CREATE TABLE connectby_tree(keyid text, parent_keyid text, pos int);

INSERT INTO connectby_tree VALUES('row1',NULL, 0);
INSERT INTO connectby_tree VALUES('row2','row1', 0);
INSERT INTO connectby_tree VALUES('row3','row1', 0);
INSERT INTO connectby_tree VALUES('row4','row2', 1);
INSERT INTO connectby_tree VALUES('row5','row2', 0);
INSERT INTO connectby_tree VALUES('row6','row4', 0);
INSERT INTO connectby_tree VALUES('row7','row3', 0);
INSERT INTO connectby_tree VALUES('row8','row6', 0);
INSERT INTO connectby_tree VALUES('row9','row5', 0);

-- with branch, without orderby_fld (order of results is not guaranteed)
SELECT * FROM connectby('connectby_tree', 'keyid', 'parent_keyid', 'row2', 0, '~')
AS t(keyid text, parent_keyid text, level int, branch text);
keyid | parent_keyid | level |       branch
-------+--------------+-------+---------------------
row2  |              |     0 | row2
row4  | row2         |     1 | row2~row4
row6  | row4         |     2 | row2~row4~row6
row8  | row6         |     3 | row2~row4~row6~row8
row5  | row2         |     1 | row2~row5
row9  | row5         |     2 | row2~row5~row9
(6 rows)

-- without branch, without orderby_fld (order of results is not guaranteed)
SELECT * FROM connectby('connectby_tree', 'keyid', 'parent_keyid', 'row2', 0)
AS t(keyid text, parent_keyid text, level int);
keyid | parent_keyid | level
-------+--------------+-------
row2  |              |     0
row4  | row2         |     1
row6  | row4         |     2
row8  | row6         |     3
row5  | row2         |     1
row9  | row5         |     2
(6 rows)

-- with branch, with orderby_fld (notice that row5 comes before row4)
SELECT * FROM connectby('connectby_tree', 'keyid', 'parent_keyid', 'pos', 'row2', 0, '~')
AS t(keyid text, parent_keyid text, level int, branch text, pos int);
keyid | parent_keyid | level |       branch        | pos
-------+--------------+-------+---------------------+-----
row2  |              |     0 | row2                |   1
row5  | row2         |     1 | row2~row5           |   2
row9  | row5         |     2 | row2~row5~row9      |   3
row4  | row2         |     1 | row2~row4           |   4
row6  | row4         |     2 | row2~row4~row6      |   5
row8  | row6         |     3 | row2~row4~row6~row8 |   6
(6 rows)

-- without branch, with orderby_fld (notice that row5 comes before row4)
SELECT * FROM connectby('connectby_tree', 'keyid', 'parent_keyid', 'pos', 'row2', 0)
AS t(keyid text, parent_keyid text, level int, pos int);
keyid | parent_keyid | level | pos
-------+--------------+-------+-----
row2  |              |     0 |   1
row5  | row2         |     1 |   2
row9  | row5         |     2 |   3
row4  | row2         |     1 |   4
row6  | row4         |     2 |   5
row8  | row6         |     3 |   6
(6 rows)
```

### Author

Joe Conway

### Functions

The `unaccent()` function removes accents (diacritic signs) from
a given string.  Basically, it's a wrapper around
`unaccent`-type dictionaries, but it can be used outside normal
text search contexts.

```
unaccent(`dictionary` `regdictionary`,  `string` `text`) returns `text`
```

If the `dictionary` argument is
omitted, the text search dictionary named `unaccent` and
appearing in the same schema as the `unaccent()`
function itself is used.

For example:

```
SELECT unaccent('unaccent', 'Htel');
SELECT unaccent('Htel');
```

### `uuid-ossp` Functions

[uuid-ossp-functions](#uuid-ossp-functions) shows the functions available to
generate UUIDs.
The relevant standards ITU-T Rec. X.667, ISO/IEC 9834-8:2005, and
[RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122)
specify four algorithms for generating UUIDs, identified by the
version numbers 1, 3, 4, and 5.  (There is no version 2 algorithm.)
Each of these algorithms could be suitable for a different set of
applications.

| Function                         Description |
| --- |
| `uuid_generate_v1` ()         uuid                         Generates a version 1 UUID.  This involves the MAC         address of the computer and a time stamp.  Note that UUIDs of this         kind reveal the identity of the computer that created the identifier         and the time at which it did so, which might make it unsuitable for         certain security-sensitive applications. |
| `uuid_generate_v1mc` ()         uuid                         Generates a version 1 UUID, but uses a random multicast         MAC address instead of the real MAC address of the computer. |
| `uuid_generate_v3` ( namespace `uuid`, name `text` )         uuid                         Generates a version 3 UUID in the given namespace using         the specified input name.  The namespace should be one of the special         constants produced by the `uuid_ns_*()` functions         shown in [uuid-ossp-constants](#uuid-ossp-constants).  (It could be any UUID         in theory.)  The name is an identifier in the selected namespace.                         For example:   ``` SELECT uuid_generate_v3(uuid_ns_url(), 'http://www.postgresql.org'); ```           The name parameter will be MD5-hashed, so the cleartext cannot be         derived from the generated UUID.         The generation of UUIDs by this method has no random or         environment-dependent element and is therefore reproducible. |
| `uuid_generate_v4` ()         uuid                         Generates a version 4 UUID, which is derived entirely         from random numbers. |
| `uuid_generate_v5` ( namespace `uuid`, name `text` )         uuid                         Generates a version 5 UUID, which works like a version 3         UUID except that SHA-1 is used as a hashing method.  Version 5 should         be preferred over version 3 because SHA-1 is thought to be more secure         than MD5. |

| Function                         Description |
| --- |
| `uuid_nil` ()         uuid                         Returns a "nil" UUID constant, which does not occur as a         real UUID. |
| `uuid_ns_dns` ()         uuid                         Returns a constant designating the DNS namespace for UUIDs. |
| `uuid_ns_url` ()         uuid                         Returns a constant designating the URL namespace for UUIDs. |
| `uuid_ns_oid` ()         uuid                         Returns a constant designating the ISO object identifier (OID) namespace for         UUIDs.  (This pertains to ASN.1 OIDs, which are unrelated to the OIDs         used in PostgreSQL.) |
| `uuid_ns_x500` ()         uuid                         Returns a constant designating the X.500 distinguished name (DN)         namespace for UUIDs. |

### Description of Functions

[xml2-functions-table](#xml2-functions-table) shows the functions provided by this module.
These functions provide straightforward XML parsing and XPath queries.

| Function                         Description |
| --- |
| `xml_valid` ( document `text` )         boolean                         Parses the given document and returns true if the         document is well-formed XML.  (Note: this is an alias for the standard         PostgreSQL function `xml_is_well_formed()`.  The         name `xml_valid()` is technically incorrect since validity         and well-formedness have different meanings in XML.) |
| `xpath_string` ( document `text`, query `text` )         text                         Evaluates the XPath query on the supplied document, and         casts the result to `text`. |
| `xpath_number` ( document `text`, query `text` )         real                         Evaluates the XPath query on the supplied document, and         casts the result to `real`. |
| `xpath_bool` ( document `text`, query `text` )         boolean                         Evaluates the XPath query on the supplied document, and         casts the result to `boolean`. |
| `xpath_nodeset` ( document `text`, query `text`, toptag `text`, itemtag `text` )         text                         Evaluates the query on the document and wraps the result in XML         tags. If the result is multivalued, the output will look like:  ```  Value 1 which could be an XML fragment Value 2....  ```          If either toptag         or itemtag is an empty string, the relevant tag         is omitted. |
| `xpath_nodeset` ( document `text`, query `text`, itemtag `text` )         text                         Like `xpath_nodeset(document, query, toptag, itemtag)` but result omits toptag. |
| `xpath_nodeset` ( document `text`, query `text` )         text                         Like `xpath_nodeset(document, query, toptag, itemtag)` but result omits both tags. |
| `xpath_list` ( document `text`, query `text`, separator `text` )         text                         Evaluates the query on the document and returns multiple values         separated by the specified separator, for example `Value         1,Value 2,Value 3` if separator         is `,`. |
| `xpath_list` ( document `text`, query `text` )         text                         This is a wrapper for the above function that uses `,`         as the separator. |

### XSLT Functions

The following functions are available if libxslt is installed:

#### `xslt_process`

```
xslt_process(text document, text stylesheet, text paramlist) returns text
```

This function applies the XSL stylesheet to the document and returns
the transformed result. The `paramlist` is a list of parameter
assignments to be used in the transformation, specified in the form
`a=1,b=2`. Note that the
parameter parsing is very simple-minded: parameter values cannot
contain commas!

There is also a two-parameter version of `xslt_process` which
does not pass any parameters to the transformation.
