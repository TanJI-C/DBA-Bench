# Statistics; Indexes

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > hstore > Statistics; Indexes`
- Source Line Ranges: `3510-3854, 6332-6632, 6747-6785`
- Chunk ID: `pg16_guide_0057_a363e02f44`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cc15e129cd58f27f25a46e9fdc53ab0dd214cf5f33d5f5e1ef7eff52d99f5c07`

## Retrieval Guidance

- Use When: Diagnose hstore query planning or index behavior.
- Retrieval Keywords: hstore statistics, hstore indexes, GIN hstore, GiST hstore, hstore selectivity, ANALYZE hstore
- Follow-up Guidance: Compare EXPLAIN estimates with pg_stats and hstore data distribution.
- Classification Note: The hstore statistics and index sections help confirm planner/index behavior for hstore queries and explain statistics collected for key/value data.

## Official Source Content

## hstore — hstore key/value datatype

This module implements the `hstore` data type for storing sets of
key/value pairs within a single PostgreSQL value.
This can be useful in various scenarios, such as rows with many attributes
that are rarely examined, or semi-structured data.  Keys and values are
simply text strings.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### `hstore` External Representation

The text representation of an `hstore`, used for input and output,
includes zero or more `key` `=>`
`value` pairs separated by commas. Some examples:

```
k => v
foo => bar, baz => whatever
"1-a" => "anything at all"
```

The order of the pairs is not significant (and may not be reproduced on
output). Whitespace between pairs or around the `=>` sign is
ignored. Double-quote keys and values that include whitespace, commas,
`=`s or `>`s. To include a double quote or a
backslash in a key or value, escape it with a backslash.

Each key in an `hstore` is unique. If you declare an `hstore`
with duplicate keys, only one will be stored in the `hstore` and
there is no guarantee as to which will be kept:

```
SELECT 'a=>1,a=>2'::hstore;
hstore
----------
"a"=>"1"
```

A value (but not a key) can be an SQL `NULL`. For example:

```
key => NULL
```

The `NULL` keyword is case-insensitive. Double-quote the
`NULL` to treat it as the ordinary string "NULL".

> **Note:**

> Keep in mind that the `hstore` text format, when used for input,
> applies *before* any required quoting or escaping. If you are
> passing an `hstore` literal via a parameter, then no additional
> processing is needed. But if you're passing it as a quoted literal
> constant, then any single-quote characters and (depending on the setting of
> the `standard_conforming_strings` configuration parameter)
> backslash characters need to be escaped correctly. See
> [sql-syntax-strings](#sql-syntax-strings) for more on the handling of string
> constants.
>

On output, double quotes always surround keys and values, even when it's
not strictly necessary.

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

### Indexes

`hstore` has GiST and GIN index support for the `@>`,
`?`, `?&` and `?|` operators. For example:

```
CREATE INDEX hidx ON testhstore USING GIST (h);

CREATE INDEX hidx ON testhstore USING GIN (h);
```

`gist_hstore_ops` GiST opclass approximates a set of
key/value pairs as a bitmap signature.  Its optional integer parameter
`siglen` determines the
signature length in bytes.  The default length is 16 bytes.
Valid values of signature length are between 1 and 2024 bytes.  Longer
signatures lead to a more precise search (scanning a smaller fraction of the index and
fewer heap pages), at the cost of a larger index.

Example of creating such an index with a signature length of 32 bytes:

```
CREATE INDEX hidx ON testhstore USING GIST (h gist_hstore_ops(siglen=32));
```

`hstore` also supports `btree` or `hash` indexes for
the `=` operator. This allows `hstore` columns to be
declared `UNIQUE`, or to be used in `GROUP BY`,
`ORDER BY` or `DISTINCT` expressions. The sort ordering
for `hstore` values is not particularly useful, but these indexes
may be useful for equivalence lookups. Create indexes for `=`
comparisons as follows:

```
CREATE INDEX hidx ON testhstore USING BTREE (h);

CREATE INDEX hidx ON testhstore USING HASH (h);
```

### Examples

Add a key, or update an existing key with a new value:

```
UPDATE tab SET h['c'] = '3';
```

Another way to do the same thing is:

```
UPDATE tab SET h = h || hstore('c', '3');
```

If multiple keys are to be added or changed in one operation,
the concatenation approach is more efficient than subscripting:

```
UPDATE tab SET h = h || hstore(array['q', 'w'], array['11', '12']);
```

Delete a key:

```
UPDATE tab SET h = delete(h, 'k1');
```

Convert a `record` to an `hstore`:

```
CREATE TABLE test (col1 integer, col2 text, col3 text);
INSERT INTO test VALUES (123, 'foo', 'bar');

SELECT hstore(t) FROM test AS t;
hstore
---------------------------------------------
"col1"=>"123", "col2"=>"foo", "col3"=>"bar"
(1 row)
```

Convert an `hstore` to a predefined `record` type:

```
CREATE TABLE test (col1 integer, col2 text, col3 text);

SELECT * FROM populate_record(null::test,
'"col1"=>"456", "col2"=>"zzz"');
col1 | col2 | col3
------+------+------
456 | zzz  |
(1 row)
```

Modify an existing record using the values from an `hstore`:

```
CREATE TABLE test (col1 integer, col2 text, col3 text);
INSERT INTO test VALUES (123, 'foo', 'bar');

SELECT (r).* FROM (SELECT t #= '"col3"=>"baz"' AS r FROM test t) s;
col1 | col2 | col3
------+------+------
123 | foo  | baz
(1 row)
```

### Statistics

The `hstore` type, because of its intrinsic liberality, could
contain a lot of different keys. Checking for valid keys is the task of the
application. The following examples demonstrate several techniques for
checking keys and obtaining statistics.

Simple example:

```
SELECT * FROM each('aaa=>bq, b=>NULL, ""=>1');
```

Using a table:

```
CREATE TABLE stat AS SELECT (each(h)).key, (each(h)).value FROM testhstore;
```

Online statistics:

```
SELECT key, count(*) FROM
(SELECT (each(h)).key FROM testhstore) AS stat
GROUP BY key
ORDER BY count DESC, key;
key    | count
-----------+-------
line      |   883
query     |   207
pos       |   203
node      |   202
space     |   197
status    |   195
public    |   194
title     |   190
org       |   189
...................
```

### Compatibility

As of PostgreSQL 9.0, `hstore` uses a different internal
representation than previous versions. This presents no obstacle for
dump/restore upgrades since the text representation (used in the dump) is
unchanged.

In the event of a binary upgrade, upward compatibility is maintained by
having the new code recognize old-format data. This will entail a slight
performance penalty when processing data that has not yet been modified by
the new code. It is possible to force an upgrade of all values in a table
column by doing an `UPDATE` statement as follows:

```
UPDATE tablename SET hstorecol = hstorecol || '';
```

Another way to do it is:

```
ALTER TABLE tablename ALTER hstorecol TYPE hstore USING hstorecol || '';
```

The `ALTER TABLE` method requires an
`ACCESS EXCLUSIVE` lock on the table,
but does not result in bloating the table with old row versions.

### Transforms

Additional extensions are available that implement transforms for
the `hstore` type for the languages PL/Perl and PL/Python.  The
extensions for PL/Perl are called `hstore_plperl`
and `hstore_plperlu`, for trusted and untrusted PL/Perl.
If you install these transforms and specify them when creating a
function, `hstore` values are mapped to Perl hashes.  The
extension for PL/Python is called `hstore_plpython3u`.
If you use it, `hstore` values are mapped to Python dictionaries.

> **Caution:**

> It is strongly recommended that the transform extensions be installed in
> the same schema as `hstore`.  Otherwise there are
> installation-time security hazards if a transform extension's schema
> contains objects defined by a hostile user.
>

### Authors

Oleg Bartunov oleg@sai.msu.su, Moscow, Moscow University, Russia

Teodor Sigaev teodor@sigaev.ru, Moscow, Delta-Soft Ltd., Russia

Additional enhancements by Andrew Gierth andrew@tao11.riddles.org.uk,
United Kingdom

## pg_stat_statements — track statistics of SQL planning and execution

The `pg_stat_statements` module provides a means for
tracking planning and execution statistics of all SQL statements executed by
a server.

The module must be loaded by adding `pg_stat_statements` to
[guc-shared-preload-libraries](#guc-shared-preload-libraries) in
`postgresql.conf`, because it requires additional shared memory.
This means that a server restart is needed to add or remove the module.
In addition, query identifier calculation must be enabled in order for the
module to be active, which is done automatically if [guc-compute-query-id](#guc-compute-query-id)
is set to `auto` or `on`, or any third-party
module that calculates query identifiers is loaded.

When `pg_stat_statements` is active, it tracks
statistics across all databases of the server.  To access and manipulate
these statistics, the module provides views
`pg_stat_statements` and
`pg_stat_statements_info`,
and the utility functions `pg_stat_statements_reset` and
`pg_stat_statements`.  These are not available globally but
can be enabled for a specific database with
`CREATE EXTENSION pg_stat_statements`.

### The `pg_stat_statements` View

The statistics gathered by the module are made available via a
view named `pg_stat_statements`.  This view
contains one row for each distinct combination of database ID, user
ID, query ID and whether it's a top-level statement or not (up to
the maximum number of distinct statements that the module can track).
The columns of the view are shown in
[pgstatstatements-columns](#pgstatstatements-columns).

| Column Type                      Description |
| --- |
| `userid` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      OID of user who executed the statement |
| `dbid` `oid`        (references [`pg_database`](#catalog-pg-database).`oid`)                      OID of database in which the statement was executed |
| `toplevel` `bool`                      True if the query was executed as a top-level statement        (always true if `pg_stat_statements.track` is set to        `top`) |
| `queryid` `bigint`                      Hash code to identify identical normalized queries. |
| `query` `text`                      Text of a representative statement |
| `plans` `bigint`                      Number of times the statement was planned        (if `pg_stat_statements.track_planning` is enabled,        otherwise zero) |
| `total_plan_time` `double precision`                      Total time spent planning the statement, in milliseconds        (if `pg_stat_statements.track_planning` is enabled,        otherwise zero) |
| `min_plan_time` `double precision`                      Minimum time spent planning the statement, in milliseconds        (if `pg_stat_statements.track_planning` is enabled,        otherwise zero) |
| `max_plan_time` `double precision`                      Maximum time spent planning the statement, in milliseconds        (if `pg_stat_statements.track_planning` is enabled,        otherwise zero) |
| `mean_plan_time` `double precision`                      Mean time spent planning the statement, in milliseconds        (if `pg_stat_statements.track_planning` is enabled,        otherwise zero) |
| `stddev_plan_time` `double precision`                      Population standard deviation of time spent planning the statement,        in milliseconds        (if `pg_stat_statements.track_planning` is enabled,        otherwise zero) |
| `calls` `bigint`                      Number of times the statement was executed |
| `total_exec_time` `double precision`                      Total time spent executing the statement, in milliseconds |
| `min_exec_time` `double precision`                      Minimum time spent executing the statement, in milliseconds |
| `max_exec_time` `double precision`                      Maximum time spent executing the statement, in milliseconds |
| `mean_exec_time` `double precision`                      Mean time spent executing the statement, in milliseconds |
| `stddev_exec_time` `double precision`                      Population standard deviation of time spent executing the statement, in milliseconds |
| `rows` `bigint`                      Total number of rows retrieved or affected by the statement |
| `shared_blks_hit` `bigint`                      Total number of shared block cache hits by the statement |
| `shared_blks_read` `bigint`                      Total number of shared blocks read by the statement |
| `shared_blks_dirtied` `bigint`                      Total number of shared blocks dirtied by the statement |
| `shared_blks_written` `bigint`                      Total number of shared blocks written by the statement |
| `local_blks_hit` `bigint`                      Total number of local block cache hits by the statement |
| `local_blks_read` `bigint`                      Total number of local blocks read by the statement |
| `local_blks_dirtied` `bigint`                      Total number of local blocks dirtied by the statement |
| `local_blks_written` `bigint`                      Total number of local blocks written by the statement |
| `temp_blks_read` `bigint`                      Total number of temp blocks read by the statement |
| `temp_blks_written` `bigint`                      Total number of temp blocks written by the statement |
| `blk_read_time` `double precision`                      Total time the statement spent reading data file blocks, in milliseconds        (if [guc-track-io-timing](#guc-track-io-timing) is enabled, otherwise zero) |
| `blk_write_time` `double precision`                      Total time the statement spent writing data file blocks, in milliseconds        (if [guc-track-io-timing](#guc-track-io-timing) is enabled, otherwise zero) |
| `temp_blk_read_time` `double precision`                      Total time the statement spent reading temporary file blocks, in        milliseconds (if [guc-track-io-timing](#guc-track-io-timing) is enabled,        otherwise zero) |
| `temp_blk_write_time` `double precision`                      Total time the statement spent writing temporary file blocks, in        milliseconds (if [guc-track-io-timing](#guc-track-io-timing) is enabled,        otherwise zero) |
| `wal_records` `bigint`                      Total number of WAL records generated by the statement |
| `wal_fpi` `bigint`                      Total number of WAL full page images generated by the statement |
| `wal_bytes` `numeric`                      Total amount of WAL generated by the statement in bytes |
| `jit_functions` `bigint`                      Total number of functions JIT-compiled by the statement |
| `jit_generation_time` `double precision`                      Total time spent by the statement on generating JIT code, in milliseconds |
| `jit_inlining_count` `bigint`                      Number of times functions have been inlined |
| `jit_inlining_time` `double precision`                      Total time spent by the statement on inlining functions, in milliseconds |
| `jit_optimization_count` `bigint`                      Number of times the statement has been optimized |
| `jit_optimization_time` `double precision`                      Total time spent by the statement on optimizing, in milliseconds |
| `jit_emission_count` `bigint`                      Number of times code has been emitted |
| `jit_emission_time` `double precision`                      Total time spent by the statement on emitting code, in milliseconds |

For security reasons, only superusers and roles with privileges of the
`pg_read_all_stats` role are allowed to see the SQL text and
`queryid` of queries executed by other users.
Other users can see the statistics, however, if the view has been installed
in their database.

Plannable queries (that is, `SELECT`, `INSERT`,
`UPDATE`, `DELETE`, and `MERGE`)
and utility commands are combined into a single
`pg_stat_statements` entry whenever they have identical query
structures according to an internal hash calculation.  Typically, two
queries will be considered the same for this purpose if they are
semantically equivalent except for the values of literal constants
appearing in the query.

> **Note:**

> The following details about constant replacement and
> `queryid` only apply when  linkend="guc-compute-query-id"/> is enabled.  If you use an external
> module instead to compute `queryid`, you
> should refer to its documentation for details.
>

When a constant's value has been ignored for purposes of matching the query
to other queries, the constant is replaced by a parameter symbol, such
as `$1`, in the `pg_stat_statements`
display.
The rest of the query text is that of the first query that had the
particular `queryid` hash value associated with the
`pg_stat_statements` entry.

Queries on which normalization can be applied may be observed with constant
values in `pg_stat_statements`, especially when there
is a high rate of entry deallocations. To reduce the likelihood of this
happening, consider increasing `pg_stat_statements.max`.
The `pg_stat_statements_info` view, discussed below
in [pgstatstatements-pg-stat-statements-info](#pgstatstatements-pg-stat-statements-info),
provides statistics about entry deallocations.

In some cases, queries with visibly different texts might get merged into a
single `pg_stat_statements` entry.  Normally this will happen
only for semantically equivalent queries, but there is a small chance of
hash collisions causing unrelated queries to be merged into one entry.
(This cannot happen for queries belonging to different users or databases,
however.)

Since the `queryid` hash value is computed on the
post-parse-analysis representation of the queries, the opposite is
also possible: queries with identical texts might appear as
separate entries, if they have different meanings as a result of
factors such as different `search_path` settings.

Consumers of `pg_stat_statements` may wish to use
`queryid` (perhaps in combination with
`dbid` and `userid`) as a more stable
and reliable identifier for each entry than its query text.
However, it is important to understand that there are only limited
guarantees around the stability of the `queryid` hash
value.  Since the identifier is derived from the
post-parse-analysis tree, its value is a function of, among other
things, the internal object identifiers appearing in this representation.
This has some counterintuitive implications.  For example,
`pg_stat_statements` will consider two apparently-identical
queries to be distinct, if they reference a table that was dropped
and recreated between the executions of the two queries.
The hashing process is also sensitive to differences in
machine architecture and other facets of the platform.
Furthermore, it is not safe to assume that `queryid`
will be stable across major versions of PostgreSQL.

Two servers participating in replication based on physical WAL replay can
be expected to have identical `queryid` values for
the same query.  However, logical replication schemes do not promise to
keep replicas identical in all relevant details, so
`queryid` will not be a useful identifier for
accumulating costs across a set of logical replicas.
If in doubt, direct testing is recommended.

Generally, it can be assumed that `queryid` values
are stable between minor version releases of PostgreSQL,
providing that instances are running on the same machine architecture and
the catalog metadata details match.  Compatibility will only be broken
between minor versions as a last resort.

The parameter symbols used to replace constants in
representative query texts start from the next number after the
highest `$``n` parameter in the original query
text, or `$1` if there was none.  It's worth noting that in
some cases there may be hidden parameter symbols that affect this
numbering.  For example, PL/pgSQL uses hidden parameter
symbols to insert values of function local variables into queries, so that
a PL/pgSQL statement like `SELECT i + 1 INTO j`
would have representative text like `SELECT i + $2`.

The representative query texts are kept in an external disk file, and do
not consume shared memory.  Therefore, even very lengthy query texts can
be stored successfully.  However, if many long query texts are
accumulated, the external file might grow unmanageably large.  As a
recovery method if that happens, `pg_stat_statements` may
choose to discard the query texts, whereupon all existing entries in
the `pg_stat_statements` view will show
null `query` fields, though the statistics associated with
each `queryid` are preserved.  If this happens, consider
reducing `pg_stat_statements.max` to prevent
recurrences.

`plans` and `calls` aren't
always expected to match because planning and execution statistics are
updated at their respective end phase, and only for successful operations.
For example, if a statement is successfully planned but fails during
the execution phase, only its planning statistics will be updated.
If planning is skipped because a cached plan is used, only its execution
statistics will be updated.

### The `pg_stat_statements_info` View

The statistics of the `pg_stat_statements` module
itself are tracked and made available via a view named
`pg_stat_statements_info`.  This view contains
only a single row.  The columns of the view are shown in
[pgstatstatementsinfo-columns](#pgstatstatementsinfo-columns).

| Column Type                      Description |
| --- |
| `dealloc` `bigint`                      Total number of times `pg_stat_statements`        entries about the least-executed statements were deallocated        because more distinct statements than        `pg_stat_statements.max` were observed |
| `stats_reset` `timestamp with time zone`                      Time at which all statistics in the        `pg_stat_statements` view were last reset. |

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

### Configuration Parameters

**`pg_stat_statements.max` (`integer`)**
: `pg_stat_statements.max` is the maximum number of
statements tracked by the module (i.e., the maximum number of rows
in the `pg_stat_statements` view).  If more distinct
statements than that are observed, information about the least-executed
statements is discarded.  The number of times such information was
discarded can be seen in the
`pg_stat_statements_info` view.
The default value is 5000.
This parameter can only be set at server start.

**`pg_stat_statements.track` (`enum`)**
: `pg_stat_statements.track` controls which statements
are counted by the module.
Specify `top` to track top-level statements (those issued
directly by clients), `all` to also track nested statements
(such as statements invoked within functions), or `none` to
disable statement statistics collection.
The default value is `top`.
Only superusers can change this setting.

**`pg_stat_statements.track_utility` (`boolean`)**
: `pg_stat_statements.track_utility` controls whether
utility commands are tracked by the module.  Utility commands are
all those other than `SELECT`, `INSERT`,
`UPDATE`, `DELETE`, and `MERGE`.
The default value is `on`.
Only superusers can change this setting.

**`pg_stat_statements.track_planning` (`boolean`)**
: `pg_stat_statements.track_planning` controls whether
planning operations and duration are tracked by the module.
Enabling this parameter may incur a noticeable performance penalty,
especially when statements with identical query structure are executed
by many concurrent connections which compete to update a small number of
`pg_stat_statements` entries.
The default value is `off`.
Only superusers can change this setting.

**`pg_stat_statements.save` (`boolean`)**
: `pg_stat_statements.save` specifies whether to
save statement statistics across server shutdowns.
If it is `off` then statistics are not saved at
shutdown nor reloaded at server start.
The default value is `on`.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

The module requires additional shared memory proportional to
`pg_stat_statements.max`.  Note that this
memory is consumed whenever the module is loaded, even if
`pg_stat_statements.track` is set to `none`.

These parameters must be set in `postgresql.conf`.
Typical usage might be:

```

## pgstattuple — obtain tuple-level statistics

The `pgstattuple` module provides various functions to
obtain tuple-level statistics.

Because these functions return detailed page-level information, access is
restricted by default.  By default, only the
role `pg_stat_scan_tables` has `EXECUTE`
privilege.  Superusers of course bypass this restriction.  After the
extension has been installed, users may issue `GRANT`
commands to change the privileges on the functions to allow others to
execute them.  However, it might be preferable to add those users to
the `pg_stat_scan_tables` role instead.

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
