# Parameters; Examples; Operator Class Interface; Limitations

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > bloom - bloom filter index access method > Parameters; Examples; Operator Class Interface; Limitations`
- Source Line Ranges: `574-583, 617-742, 801-821, 838-850, 895-910, 911-1041, 1042-1054, 1055-1066, 1256-1303, 1584-1655, 1709-1736, 1818-1902, 1939-1986, 2030-2056, 2097-2155, 2186-2217, 2227-2242, 2268-2283, 2310-2321, 2337-2353, 2371-2404, 2454-2502, 2523-2539, 2568-2603, 2655-2678, 2721-2745, 2800-2809, 3694-3759, 4143-4184, 4279-4294, 5954-5964, 6072-6089, 6240-6254, 6574-6632, 7305-7320, 7321-7443, 7444-7483, 7484-7491, 7492-7503, 8484-8542, 8543-8596, 8963-8989, 9256-9278, 9299-9387, 10281-10299, 10327-10345, 10915-11035`
- Chunk ID: `pg16_configuration_0169_290382553d`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `374d1d604566d195c4940c8ebeca5536210b55583f7a6ce2651d30763e4fc7d2`

## Retrieval Guidance

- Use When: Tune or define bloom indexes for multi-column equality workloads.
- Retrieval Keywords: bloom index, length parameter, col1 bits, bloom operator class, bloom index false positives
- Follow-up Guidance: Validate false-positive rate and query plans against workload data before adopting bloom indexes.
- Classification Note: The module defines index parameters such as signature length and per-column bit settings that configure bloom index behavior.

## Official Source Content

### Configuration Parameters

**`auth_delay.milliseconds` (`integer`)**
: The number of milliseconds to wait before reporting an authentication
failure.  The default is 0.

These parameters must be set in `postgresql.conf`.
Typical usage might be:

```

### Configuration Parameters

There are several configuration parameters that control the behavior of
`auto_explain`.  Note that the default behavior is
to do nothing, so you must set at least
`auto_explain.log_min_duration` if you want any results.

**`auto_explain.log_min_duration` (`integer`)**
: `auto_explain.log_min_duration` is the minimum statement
execution time, in milliseconds, that will cause the statement's plan to
be logged. Setting this to `0` logs all plans.
`-1` (the default) disables logging of plans. For
example, if you set it to `250ms` then all statements
that run 250ms or longer will be logged. Only superusers can change this
setting.

**`auto_explain.log_parameter_max_length` (`integer`)**
: `auto_explain.log_parameter_max_length` controls the
logging of query parameter values. A value of `-1` (the
default) logs the parameter values in full. `0` disables
logging of parameter values. A value greater than zero truncates each
parameter value to that many bytes. Only superusers can change this
setting.

**`auto_explain.log_analyze` (`boolean`)**
: `auto_explain.log_analyze` causes `EXPLAIN ANALYZE`
output, rather than just `EXPLAIN` output, to be printed
when an execution plan is logged. This parameter is off by default.
Only superusers can change this setting.

> **Note:**
> When this parameter is on, per-plan-node timing occurs for all
> statements executed, whether or not they run long enough to actually
> get logged.  This can have an extremely negative impact on performance.
> Turning off `auto_explain.log_timing` ameliorates the
> performance cost, at the price of obtaining less information.
>

**`auto_explain.log_buffers` (`boolean`)**
: `auto_explain.log_buffers` controls whether buffer
usage statistics are printed when an execution plan is logged; it's
equivalent to the `BUFFERS` option of `EXPLAIN`.
This parameter has no effect
unless `auto_explain.log_analyze` is enabled.
This parameter is off by default.
Only superusers can change this setting.

**`auto_explain.log_wal` (`boolean`)**
: `auto_explain.log_wal` controls whether WAL
usage statistics are printed when an execution plan is logged; it's
equivalent to the `WAL` option of `EXPLAIN`.
This parameter has no effect
unless `auto_explain.log_analyze` is enabled.
This parameter is off by default.
Only superusers can change this setting.

**`auto_explain.log_timing` (`boolean`)**
: `auto_explain.log_timing` controls whether per-node
timing information is printed when an execution plan is logged; it's
equivalent to the `TIMING` option of `EXPLAIN`.
The overhead of repeatedly reading the system clock can slow down
queries significantly on some systems, so it may be useful to set this
parameter to off when only actual row counts, and not exact times, are
needed.
This parameter has no effect
unless `auto_explain.log_analyze` is enabled.
This parameter is on by default.
Only superusers can change this setting.

**`auto_explain.log_triggers` (`boolean`)**
: `auto_explain.log_triggers` causes trigger
execution statistics to be included when an execution plan is logged.
This parameter has no effect
unless `auto_explain.log_analyze` is enabled.
This parameter is off by default.
Only superusers can change this setting.

**`auto_explain.log_verbose` (`boolean`)**
: `auto_explain.log_verbose` controls whether verbose
details are printed when an execution plan is logged; it's
equivalent to the `VERBOSE` option of `EXPLAIN`.
This parameter is off by default.
Only superusers can change this setting.

**`auto_explain.log_settings` (`boolean`)**
: `auto_explain.log_settings` controls whether information
about modified configuration options is printed when an execution plan is logged.
Only options affecting query planning with value different from the built-in
default value are included in the output.  This parameter is off by default.
Only superusers can change this setting.

**`auto_explain.log_format` (`enum`)**
: `auto_explain.log_format` selects the
`EXPLAIN` output format to be used.
The allowed values are `text`, `xml`,
`json`, and `yaml`.  The default is text.
Only superusers can change this setting.

**`auto_explain.log_level` (`enum`)**
: `auto_explain.log_level` selects the log level at which
auto_explain will log the query plan.
Valid values are `DEBUG5`, `DEBUG4`,
`DEBUG3`, `DEBUG2`,
`DEBUG1`, `INFO`,
`NOTICE`, `WARNING`,
and `LOG`. The default is `LOG`.
Only superusers can change this setting.

**`auto_explain.log_nested_statements` (`boolean`)**
: `auto_explain.log_nested_statements` causes nested
statements (statements executed inside a function) to be considered
for logging.  When it is off, only top-level query plans are logged. This
parameter is off by default. Only superusers can change this setting.

**`auto_explain.sample_rate` (`real`)**
: `auto_explain.sample_rate` causes auto_explain to only
explain a fraction of the statements in each session.  The default is 1,
meaning explain all the queries.  In case of nested statements, either all
will be explained or none. Only superusers can change this setting.

In ordinary usage, these parameters are set
in `postgresql.conf`, although superusers can alter them
on-the-fly within their own sessions.
Typical usage might be:

```

### Configuration Parameters

**`basebackup_to_shell.command` (`string`)**
: The command which the server should execute for each archive generated
by the backup process. If `%f` occurs in the command
string, it will be replaced by the name of the archive (e.g.
`base.tar`). If `%d` occurs in the
command string, it will be replaced by the target detail provided by
the user. A target detail is required if `%d` is
used in the command string, and prohibited otherwise. For security
reasons, it may contain only alphanumeric characters. If
`%%` occurs in the command string, it will be replaced
by a single `%`. If `%` occurs in
the command string followed by any other character or at the end of the
string, an error occurs.

**`basebackup_to_shell.required_role` (`string`)**
: The role required in order to make use of the `shell`
backup target. If this is not set, any replication user may make use of
the `shell` backup target.

### Configuration Parameters

**`basic_archive.archive_directory` (`string`)**
: The directory where the server should copy WAL segment files.  This
directory must already exist.  The default is an empty string, which
effectively halts WAL archiving, but if [guc-archive-mode](#guc-archive-mode)
is enabled, the server will accumulate WAL segment files in the
expectation that a value will soon be provided.

These parameters must be set in `postgresql.conf`.
Typical usage might be:

```

### Parameters

A `bloom` index accepts the following parameters in its
`WITH` clause:

**`length`**
: Length of each signature (index entry) in bits. It is rounded up to the
nearest multiple of `16`. The default is
`80` bits and the maximum is `4096`.

**`col1 — col32`**
: Number of bits generated for each index column. Each parameter's name
refers to the number of the index column that it controls.  The default
is `2` bits and the maximum is `4095`.
Parameters for index columns not actually used are ignored.

### Examples

This is an example of creating a bloom index:

```
CREATE INDEX bloomidx ON tbloom USING bloom (i1,i2,i3)
WITH (length=80, col1=2, col2=2, col3=4);
```

The index is created with a signature length of 80 bits, with attributes
i1 and i2 mapped to 2 bits, and attribute i3 mapped to 4 bits.  We could
have omitted the `length`, `col1`,
and `col2` specifications since those have the default values.

Here is a more complete example of bloom index definition and usage, as
well as a comparison with equivalent btree indexes.  The bloom index is
considerably smaller than the btree index, and can perform better.

```
=# CREATE TABLE tbloom AS
SELECT
(random() * 1000000)::int as i1,
(random() * 1000000)::int as i2,
(random() * 1000000)::int as i3,
(random() * 1000000)::int as i4,
(random() * 1000000)::int as i5,
(random() * 1000000)::int as i6
FROM
generate_series(1,10000000);
SELECT 10000000
```

A sequential scan over this large table takes a long time:

```
=# EXPLAIN ANALYZE SELECT * FROM tbloom WHERE i2 = 898732 AND i5 = 123451;
QUERY PLAN
------------------------------------------------------------------------------------------------------
Seq Scan on tbloom  (cost=0.00..213744.00 rows=250 width=24) (actual time=357.059..357.059 rows=0 loops=1)
Filter: ((i2 = 898732) AND (i5 = 123451))
Rows Removed by Filter: 10000000
Planning Time: 0.346 ms
Execution Time: 357.076 ms
(5 rows)
```

Even with the btree index defined the result will still be a
sequential scan:

```
=# CREATE INDEX btreeidx ON tbloom (i1, i2, i3, i4, i5, i6);
CREATE INDEX
=# SELECT pg_size_pretty(pg_relation_size('btreeidx'));
pg_size_pretty
----------------
386 MB
(1 row)
=# EXPLAIN ANALYZE SELECT * FROM tbloom WHERE i2 = 898732 AND i5 = 123451;
QUERY PLAN
------------------------------------------------------------------------------------------------------
Seq Scan on tbloom  (cost=0.00..213744.00 rows=2 width=24) (actual time=351.016..351.017 rows=0 loops=1)
Filter: ((i2 = 898732) AND (i5 = 123451))
Rows Removed by Filter: 10000000
Planning Time: 0.138 ms
Execution Time: 351.035 ms
(5 rows)
```

Having the bloom index defined on the table is better than btree in
handling this type of search:

```
=# CREATE INDEX bloomidx ON tbloom USING bloom (i1, i2, i3, i4, i5, i6);
CREATE INDEX
=# SELECT pg_size_pretty(pg_relation_size('bloomidx'));
pg_size_pretty
----------------
153 MB
(1 row)
=# EXPLAIN ANALYZE SELECT * FROM tbloom WHERE i2 = 898732 AND i5 = 123451;
QUERY PLAN
---------------------------------------------------------------------------------------------------------------------
Bitmap Heap Scan on tbloom  (cost=1792.00..1799.69 rows=2 width=24) (actual time=22.605..22.606 rows=0 loops=1)
Recheck Cond: ((i2 = 898732) AND (i5 = 123451))
Rows Removed by Index Recheck: 2300
Heap Blocks: exact=2256
->  Bitmap Index Scan on bloomidx  (cost=0.00..178436.00 rows=1 width=0) (actual time=20.005..20.005 rows=2300 loops=1)
Index Cond: ((i2 = 898732) AND (i5 = 123451))
Planning Time: 0.099 ms
Execution Time: 22.632 ms
(8 rows)
```

Now, the main problem with the btree search is that btree is inefficient
when the search conditions do not constrain the leading index column(s).
A better strategy for btree is to create a separate index on each column.
Then the planner will choose something like this:

```
=# CREATE INDEX btreeidx1 ON tbloom (i1);
CREATE INDEX
=# CREATE INDEX btreeidx2 ON tbloom (i2);
CREATE INDEX
=# CREATE INDEX btreeidx3 ON tbloom (i3);
CREATE INDEX
=# CREATE INDEX btreeidx4 ON tbloom (i4);
CREATE INDEX
=# CREATE INDEX btreeidx5 ON tbloom (i5);
CREATE INDEX
=# CREATE INDEX btreeidx6 ON tbloom (i6);
CREATE INDEX
=# EXPLAIN ANALYZE SELECT * FROM tbloom WHERE i2 = 898732 AND i5 = 123451;
QUERY PLAN
---------------------------------------------------------------------------------------------------------------------------
Bitmap Heap Scan on tbloom  (cost=9.29..13.30 rows=1 width=24) (actual time=0.032..0.033 rows=0 loops=1)
Recheck Cond: ((i5 = 123451) AND (i2 = 898732))
->  BitmapAnd  (cost=9.29..9.29 rows=1 width=0) (actual time=0.047..0.047 rows=0 loops=1)
->  Bitmap Index Scan on btreeidx5  (cost=0.00..4.52 rows=11 width=0) (actual time=0.026..0.026 rows=7 loops=1)
Index Cond: (i5 = 123451)
->  Bitmap Index Scan on btreeidx2  (cost=0.00..4.52 rows=11 width=0) (actual time=0.007..0.007 rows=8 loops=1)
Index Cond: (i2 = 898732)
Planning Time: 0.264 ms
Execution Time: 0.047 ms
(9 rows)
```

Although this query runs much faster than with either of the single
indexes, we pay a penalty in index size.  Each of the single-column
btree indexes occupies 88.5 MB, so the total space needed is 531 MB,
over three times the space used by the bloom index.

### Operator Class Interface

An operator class for bloom indexes requires only a hash function for the
indexed data type and an equality operator for searching. This example
shows the operator class definition for the `text` data type:

```
CREATE OPERATOR CLASS text_ops
DEFAULT FOR TYPE text USING bloom AS
OPERATOR    1   =(text, text),
FUNCTION    1   hashtext(text);
```

### Limitations

- Only operator classes for `int4` and `text` are
included with the module.
- Only the `=` operator is supported for search.  But
it is possible to add support for arrays with union and intersection
operations in the future.
- `bloom` access method doesn't support
`UNIQUE` indexes.
- `bloom` access method doesn't support searching for
`NULL` values.

### Limitations

- `citext`'s case-folding behavior depends on
the `LC_CTYPE` setting of your database. How it compares
values is therefore determined when the database is created.
It is not truly
case-insensitive in the terms defined by the Unicode standard.
Effectively, what this means is that, as long as you're happy with your
collation, you should be happy with `citext`'s comparisons. But
if you have data in different languages stored in your database, users
of one language may find their query results are not as expected if the
collation is for another language.
- As of PostgreSQL 9.1, you can attach a
`COLLATE` specification to `citext` columns or data
values.  Currently, `citext` operators will honor a non-default
`COLLATE` specification while comparing case-folded strings,
but the initial folding to lower case is always done according to the
database's `LC_CTYPE` setting (that is, as though
`COLLATE "default"` were given).  This may be changed in a
future release so that both steps follow the input `COLLATE`
specification.
- `citext` is not as efficient as `text` because the
operator functions and the B-tree comparison functions must make copies
of the data and convert it to lower case for comparisons.  Also, only
`text` can support B-Tree deduplication.  However,
`citext` is slightly more efficient than using
`lower` to get case-insensitive matching.
- `citext` doesn't help much if you need data to compare
case-sensitively in some contexts and case-insensitively in other
contexts.  The standard answer is to use the `text` type and
manually use the `lower` function when you need to compare
case-insensitively; this works all right if case-insensitive comparison
is needed only infrequently.  If you need case-insensitive behavior most
of the time and case-sensitive infrequently, consider storing the data
as `citext` and explicitly casting the column to `text`
when you want case-sensitive comparison.  In either situation, you will
need two indexes if you want both types of searches to be fast.
- The schema containing the `citext` operators must be
in the current `search_path` (typically `public`);
if it is not, the normal case-sensitive `text` operators
will be invoked instead.
- The approach of lower-casing strings for comparison does not handle some
Unicode special cases correctly, for example when one upper-case letter
has two lower-case letter equivalents.  Unicode distinguishes between
*case mapping* and *case
folding* for this reason.  Use nondeterministic collations
instead of `citext` to handle that correctly.

## Examples

```
SELECT dblink_connect('dbname=postgres options=-csearch_path=');
dblink_connect
----------------
OK
(1 row)

SELECT dblink_connect('myconn', 'dbname=postgres options=-csearch_path=');
dblink_connect
----------------
OK
(1 row)

-- FOREIGN DATA WRAPPER functionality
-- Note: local connection must require password authentication for this to work properly
--       Otherwise, you will receive the following error from dblink_connect():
--       ERROR:  password is required
--       DETAIL:  Non-superuser cannot connect if the server does not request a password.
--       HINT:  Target server's authentication method must be changed.

CREATE SERVER fdtest FOREIGN DATA WRAPPER dblink_fdw OPTIONS (hostaddr '127.0.0.1', dbname 'contrib_regression');

CREATE USER regress_dblink_user WITH PASSWORD 'secret';
CREATE USER MAPPING FOR regress_dblink_user SERVER fdtest OPTIONS (user 'regress_dblink_user', password 'secret');
GRANT USAGE ON FOREIGN SERVER fdtest TO regress_dblink_user;
GRANT SELECT ON TABLE foo TO regress_dblink_user;

\set ORIGINAL_USER :USER
\c - regress_dblink_user
SELECT dblink_connect('myconn', 'fdtest');
dblink_connect
----------------
OK
(1 row)

SELECT * FROM dblink('myconn', 'SELECT * FROM foo') AS t(a int, b text, c text[]);
a  | b |       c
----+---+---------------
0 | a | {a0,b0,c0}
1 | b | {a1,b1,c1}
2 | c | {a2,b2,c2}
3 | d | {a3,b3,c3}
4 | e | {a4,b4,c4}
5 | f | {a5,b5,c5}
6 | g | {a6,b6,c6}
7 | h | {a7,b7,c7}
8 | i | {a8,b8,c8}
9 | j | {a9,b9,c9}
10 | k | {a10,b10,c10}
(11 rows)

\c - :ORIGINAL_USER
REVOKE USAGE ON FOREIGN SERVER fdtest FROM regress_dblink_user;
REVOKE SELECT ON TABLE foo FROM regress_dblink_user;
DROP USER MAPPING FOR regress_dblink_user SERVER fdtest;
DROP USER regress_dblink_user;
DROP SERVER fdtest;
```

dblink_connect_u
3

dblink_connect_u
opens a persistent connection to a remote database, insecurely

```
dblink_connect_u(text connstr) returns text
dblink_connect_u(text connname, text connstr) returns text
```

## Examples

```
SELECT dblink_disconnect();
dblink_disconnect
-------------------
OK
(1 row)

SELECT dblink_disconnect('myconn');
dblink_disconnect
-------------------
OK
(1 row)
```

dblink
3

dblink
executes a query in a remote database

```
dblink(text connname, text sql [, bool fail_on_error]) returns setof record
dblink(text connstr, text sql [, bool fail_on_error]) returns setof record
dblink(text sql [, bool fail_on_error]) returns setof record
```

## Examples

```
SELECT * FROM dblink('dbname=postgres options=-csearch_path=',
'select proname, prosrc from pg_proc')
AS t1(proname name, prosrc text) WHERE proname LIKE 'bytea%';
proname   |   prosrc
------------+------------
byteacat   | byteacat
byteaeq    | byteaeq
bytealt    | bytealt
byteale    | byteale
byteagt    | byteagt
byteage    | byteage
byteane    | byteane
byteacmp   | byteacmp
bytealike  | bytealike
byteanlike | byteanlike
byteain    | byteain
byteaout   | byteaout
(12 rows)

SELECT dblink_connect('dbname=postgres options=-csearch_path=');
dblink_connect
----------------
OK
(1 row)

SELECT * FROM dblink('select proname, prosrc from pg_proc')
AS t1(proname name, prosrc text) WHERE proname LIKE 'bytea%';
proname   |   prosrc
------------+------------
byteacat   | byteacat
byteaeq    | byteaeq
bytealt    | bytealt
byteale    | byteale
byteagt    | byteagt
byteage    | byteage
byteane    | byteane
byteacmp   | byteacmp
bytealike  | bytealike
byteanlike | byteanlike
byteain    | byteain
byteaout   | byteaout
(12 rows)

SELECT dblink_connect('myconn', 'dbname=regression options=-csearch_path=');
dblink_connect
----------------
OK
(1 row)

SELECT * FROM dblink('myconn', 'select proname, prosrc from pg_proc')
AS t1(proname name, prosrc text) WHERE proname LIKE 'bytea%';
proname   |   prosrc
------------+------------
bytearecv  | bytearecv
byteasend  | byteasend
byteale    | byteale
byteagt    | byteagt
byteage    | byteage
byteane    | byteane
byteacmp   | byteacmp
bytealike  | bytealike
byteanlike | byteanlike
byteacat   | byteacat
byteaeq    | byteaeq
bytealt    | bytealt
byteain    | byteain
byteaout   | byteaout
(14 rows)
```

dblink_exec
3

dblink_exec
executes a command in a remote database

```
dblink_exec(text connname, text sql [, bool fail_on_error]) returns text
dblink_exec(text connstr, text sql [, bool fail_on_error]) returns text
dblink_exec(text sql [, bool fail_on_error]) returns text
```

## Examples

```
SELECT dblink_connect('dbname=dblink_test_standby');
dblink_connect
----------------
OK
(1 row)

SELECT dblink_exec('insert into foo values(21, ''z'', ''{"a0","b0","c0"}'');');
dblink_exec
-----------------
INSERT 943366 1
(1 row)

SELECT dblink_connect('myconn', 'dbname=regression');
dblink_connect
----------------
OK
(1 row)

SELECT dblink_exec('myconn', 'insert into foo values(21, ''z'', ''{"a0","b0","c0"}'');');
dblink_exec
------------------
INSERT 6432584 1
(1 row)

SELECT dblink_exec('myconn', 'insert into pg_class values (''foo'')',false);
NOTICE:  sql error
DETAIL:  ERROR:  null value in column "relnamespace" violates not-null constraint

dblink_exec
-------------
ERROR
(1 row)
```

dblink_open
3

dblink_open
opens a cursor in a remote database

```
dblink_open(text cursorname, text sql [, bool fail_on_error]) returns text
dblink_open(text connname, text cursorname, text sql [, bool fail_on_error]) returns text
```

## Examples

```
SELECT dblink_connect('dbname=postgres options=-csearch_path=');
dblink_connect
----------------
OK
(1 row)

SELECT dblink_open('foo', 'select proname, prosrc from pg_proc');
dblink_open
-------------
OK
(1 row)
```

dblink_fetch
3

dblink_fetch
returns rows from an open cursor in a remote database

```
dblink_fetch(text cursorname, int howmany [, bool fail_on_error]) returns setof record
dblink_fetch(text connname, text cursorname, int howmany [, bool fail_on_error]) returns setof record
```

## Examples

```
SELECT dblink_connect('dbname=postgres options=-csearch_path=');
dblink_connect
----------------
OK
(1 row)

SELECT dblink_open('foo', 'select proname, prosrc from pg_proc where proname like ''bytea%''');
dblink_open
-------------
OK
(1 row)

SELECT * FROM dblink_fetch('foo', 5) AS (funcname name, source text);
funcname |  source
----------+----------
byteacat | byteacat
byteacmp | byteacmp
byteaeq  | byteaeq
byteage  | byteage
byteagt  | byteagt
(5 rows)

SELECT * FROM dblink_fetch('foo', 5) AS (funcname name, source text);
funcname  |  source
-----------+-----------
byteain   | byteain
byteale   | byteale
bytealike | bytealike
bytealt   | bytealt
byteane   | byteane
(5 rows)

SELECT * FROM dblink_fetch('foo', 5) AS (funcname name, source text);
funcname  |   source
------------+------------
byteanlike | byteanlike
byteaout   | byteaout
(2 rows)

SELECT * FROM dblink_fetch('foo', 5) AS (funcname name, source text);
funcname | source
----------+--------
(0 rows)
```

dblink_close
3

dblink_close
closes a cursor in a remote database

```
dblink_close(text cursorname [, bool fail_on_error]) returns text
dblink_close(text connname, text cursorname [, bool fail_on_error]) returns text
```

## Examples

```
SELECT dblink_connect('dbname=postgres options=-csearch_path=');
dblink_connect
----------------
OK
(1 row)

SELECT dblink_open('foo', 'select proname, prosrc from pg_proc');
dblink_open
-------------
OK
(1 row)

SELECT dblink_close('foo');
dblink_close
--------------
OK
(1 row)
```

dblink_get_connections
3

dblink_get_connections
returns the names of all open named dblink connections

```
dblink_get_connections() returns text[]
```

## Examples

```
SELECT dblink_get_connections();
```

dblink_error_message
3

dblink_error_message
gets last error message on the named connection

```
dblink_error_message(text connname) returns text
```

## Examples

```
SELECT dblink_error_message('dtest1');
```

dblink_send_query
3

dblink_send_query
sends an async query to a remote database

```
dblink_send_query(text connname, text sql) returns int
```

## Examples

```
SELECT dblink_send_query('dtest1', 'SELECT * FROM foo WHERE f1 3

dblink_is_busy
checks if connection is busy with an async query

```
dblink_is_busy(text connname) returns int
```

## Examples

```
SELECT dblink_is_busy('dtest1');
```

dblink_get_notify
3

dblink_get_notify
retrieve async notifications on a connection

```
dblink_get_notify() returns setof (notify_name text, be_pid int, extra text)
dblink_get_notify(text connname) returns setof (notify_name text, be_pid int, extra text)
```

## Examples

```
SELECT dblink_exec('LISTEN virtual');
dblink_exec
-------------
LISTEN
(1 row)

SELECT * FROM dblink_get_notify();
notify_name | be_pid | extra
-------------+--------+-------
(0 rows)

NOTIFY virtual;
NOTIFY

SELECT * FROM dblink_get_notify();
notify_name | be_pid | extra
-------------+--------+-------
virtual     |   1229 |
(1 row)
```

dblink_get_result
3

dblink_get_result
gets an async query result

```
dblink_get_result(text connname [, bool fail_on_error]) returns setof record
```

## Examples

```
contrib_regression=# SELECT dblink_connect('dtest1', 'dbname=contrib_regression');
dblink_connect
----------------
OK
(1 row)

contrib_regression=# SELECT * FROM
contrib_regression-# dblink_send_query('dtest1', 'select * from foo where f1  6') AS t1;
t1
----
1
(1 row)

contrib_regression=# SELECT * FROM dblink_get_result('dtest1') AS t1(f1 int, f2 text, f3 text[]);
f1 | f2 |     f3
----+----+------------
0 | a  | {a0,b0,c0}
1 | b  | {a1,b1,c1}
2 | c  | {a2,b2,c2}
(3 rows)

contrib_regression=# SELECT * FROM dblink_get_result('dtest1') AS t1(f1 int, f2 text, f3 text[]);
f1 | f2 |      f3
----+----+---------------
7 | h  | {a7,b7,c7}
8 | i  | {a8,b8,c8}
9 | j  | {a9,b9,c9}
10 | k  | {a10,b10,c10}
(4 rows)

contrib_regression=# SELECT * FROM dblink_get_result('dtest1') AS t1(f1 int, f2 text, f3 text[]);
f1 | f2 | f3
----+----+----
(0 rows)
```

dblink_cancel_query
3

dblink_cancel_query
cancels any active query on the named connection

```
dblink_cancel_query(text connname) returns text
```

## Examples

```
SELECT dblink_cancel_query('dtest1');
```

dblink_get_pkey
3

dblink_get_pkey
returns the positions and field names of a relation's
primary key fields

```
dblink_get_pkey(text relname) returns setof dblink_pkey_results
```

## Examples

```
CREATE TABLE foobar (
f1 int,
f2 int,
f3 int,
PRIMARY KEY (f1, f2, f3)
);
CREATE TABLE

SELECT * FROM dblink_get_pkey('foobar');
position | colname
----------+---------
1 | f1
2 | f2
3 | f3
(3 rows)
```

dblink_build_sql_insert
3

dblink_build_sql_insert

builds an INSERT statement using a local tuple, replacing the
primary key field values with alternative supplied values

```
dblink_build_sql_insert(text relname,
int2vector primary_key_attnums,
integer num_primary_key_atts,
text[] src_pk_att_vals_array,
text[] tgt_pk_att_vals_array) returns text
```

## Examples

```
SELECT dblink_build_sql_insert('foo', '1 2', 2, '{"1", "a"}', '{"1", "b''a"}');
dblink_build_sql_insert
--------------------------------------------------
INSERT INTO foo(f1,f2,f3) VALUES('1','b''a','1')
(1 row)
```

dblink_build_sql_delete
3

dblink_build_sql_delete
builds a DELETE statement using supplied values for primary
key field values

```
dblink_build_sql_delete(text relname,
int2vector primary_key_attnums,
integer num_primary_key_atts,
text[] tgt_pk_att_vals_array) returns text
```

## Examples

```
SELECT dblink_build_sql_delete('"MyFoo"', '1 2', 2, '{"1", "b"}');
dblink_build_sql_delete
---------------------------------------------
DELETE FROM "MyFoo" WHERE f1='1' AND f2='b'
(1 row)
```

dblink_build_sql_update
3

dblink_build_sql_update
builds an UPDATE statement using a local tuple, replacing
the primary key field values with alternative supplied values

```
dblink_build_sql_update(text relname,
int2vector primary_key_attnums,
integer num_primary_key_atts,
text[] src_pk_att_vals_array,
text[] tgt_pk_att_vals_array) returns text
```

## Examples

```
SELECT dblink_build_sql_update('foo', '1 2', 2, '{"1", "a"}', '{"1", "b"}');
dblink_build_sql_update
-------------------------------------------------------------
UPDATE foo SET f1='1',f2='b',f3='1' WHERE f1='1' AND f2='b'
(1 row)
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

### Examples

```
--Using the types directly:
SELECT isbn('978-0-393-04002-9');
SELECT isbn13('0901690546');
SELECT issn('1436-4522');

--Casting types:
-- note that you can only cast from ean13 to another type when the
-- number would be valid in the realm of the target type;
-- thus, the following will NOT work: select isbn(ean13('0220356483481'));
-- but these will:
SELECT upc(ean13('0220356483481'));
SELECT ean13(upc('220356483481'));

--Create a table with a single column to hold ISBN numbers:
CREATE TABLE test (id isbn);
INSERT INTO test VALUES('9780393040029');

--Automatically calculate check digits (observe the '?'):
INSERT INTO test VALUES('220500896?');
INSERT INTO test VALUES('978055215372?');

SELECT issn('3251231?');
SELECT ismn('979047213542?');

--Using the weak mode:
SELECT isn_weak(true);
INSERT INTO test VALUES('978-0-11-000533-4');
INSERT INTO test VALUES('9780141219307');
INSERT INTO test VALUES('2-205-00876-X');
SELECT isn_weak(false);

SELECT id FROM test WHERE NOT is_valid(id);
UPDATE test SET id = make_valid(id) WHERE id = '2-205-00876-X!';

SELECT * FROM test;

SELECT isbn13(id) FROM test;
```

### Limitations

- Dropping a table will still orphan any objects it contains, as the trigger
is not executed.  You can avoid this by preceding the `DROP
TABLE` with `DELETE FROM `table``.

`TRUNCATE` has the same hazard.

If you already have, or suspect you have, orphaned large objects, see the
[vacuumlo](#vacuumlo) module to help
you clean them up.  It's a good idea to run vacuumlo
occasionally as a back-stop to the `lo_manage` trigger.
- Some frontends may create their own tables, and will not create the
associated trigger(s).  Also, users may not remember (or know) to create
the triggers.

#### Limitations of PGP Code

- No support for signing.  That also means that it is not checked
whether the encryption subkey belongs to the master key.
- No support for encryption key as master key.  As such practice
is generally discouraged, this should not be a problem.
- No support for several subkeys.  This may seem like a problem, as this
is common practice.  On the other hand, you should not use your regular
GPG/PGP keys with `pgcrypto`, but create new ones,
as the usage scenario is rather different.

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

### Configuration Parameters

**`pg_prewarm.autoprewarm` (`boolean`)**
: Controls whether the server should run the autoprewarm worker. This is
on by default. This parameter can only be set at server start.

**`pg_prewarm.autoprewarm_interval` (`integer`)**
: This is the interval between updates to `autoprewarm.blocks`.
The default is 300 seconds. If set to 0, the file will not be
dumped at regular intervals, but only when the server is shut down.

These parameters must be set in `postgresql.conf`.
Typical usage might be:

```

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

### GUC Parameters

**`pg_trgm.similarity_threshold` (`real`)**
: Sets the current similarity threshold that is used by the `%`
operator.  The threshold must be between 0 and 1 (default is 0.3).

**`pg_trgm.word_similarity_threshold` (`real`)**
: Sets the current word similarity threshold that is used by the
`` operators.  The threshold
must be between 0 and 1 (default is 0.6).

**`pg_trgm.strict_word_similarity_threshold` (`real`)**
: Sets the current strict word similarity threshold that is used by the
`>` operators.  The threshold
must be between 0 and 1 (default is 0.5).

### Index Support

The `pg_trgm` module provides GiST and GIN index
operator classes that allow you to create an index over a text column for
the purpose of very fast similarity searches.  These index types support
the above-described similarity operators, and additionally support
trigram-based index searches for `LIKE`, `ILIKE`,
`~`, `~*` and `=` queries.
The similarity comparisons are case-insensitive in a default build of
`pg_trgm`.
Inequality operators are not supported.
Note that those indexes may not be as efficient as regular B-tree indexes
for equality operator.

Example:

```
CREATE TABLE test_trgm (t text);
CREATE INDEX trgm_idx ON test_trgm USING GIST (t gist_trgm_ops);
```

or

```
CREATE INDEX trgm_idx ON test_trgm USING GIN (t gin_trgm_ops);
```

`gist_trgm_ops` GiST opclass approximates a set of
trigrams as a bitmap signature.  Its optional integer parameter
`siglen` determines the
signature length in bytes.  The default length is 12 bytes.
Valid values of signature length are between 1 and 2024 bytes.  Longer
signatures lead to a more precise search (scanning a smaller fraction of the index and
fewer heap pages), at the cost of a larger index.

Example of creating such an index with a signature length of 32 bytes:

```
CREATE INDEX trgm_idx ON test_trgm USING GIST (t gist_trgm_ops(siglen=32));
```

At this point, you will have an index on the `t` column that
you can use for similarity searching.  A typical query is

```
SELECT t, similarity(t, '`word`') AS sml
FROM test_trgm
WHERE t % '`word`'
ORDER BY sml DESC, t;
```

This will return all values in the text column that are sufficiently
similar to `word`, sorted from best match to worst.  The
index will be used to make this a fast operation even over very large data
sets.

A variant of the above query is

```
SELECT t, t  '`word`' AS dist
FROM test_trgm
ORDER BY dist LIMIT 10;
```

This can be implemented quite efficiently by GiST indexes, but not
by GIN indexes.  It will usually beat the first formulation when only
a small number of the closest matches is wanted.

Also you can use an index on the `t` column for word
similarity or strict word similarity.  Typical queries are:

```
SELECT t, word_similarity('`word`', t) AS sml
FROM test_trgm
WHERE '`word`'  t AS dist
FROM test_trgm
ORDER BY dist LIMIT 10;
```

and

```
SELECT t, '`word`'  t AS dist
FROM test_trgm
ORDER BY dist LIMIT 10;
```

This can be implemented quite efficiently by GiST indexes, but not
by GIN indexes.

Beginning in PostgreSQL 9.1, these index types also support
index searches for `LIKE` and `ILIKE`, for example

```
SELECT * FROM test_trgm WHERE t LIKE '%foo%bar';
```

The index search works by extracting trigrams from the search string
and then looking these up in the index.  The more trigrams in the search
string, the more effective the index search is.  Unlike B-tree based
searches, the search string need not be left-anchored.

Beginning in PostgreSQL 9.3, these index types also support
index searches for regular-expression matches
(`~` and `~*` operators), for example

```
SELECT * FROM test_trgm WHERE t ~ '(foo|bar)';
```

The index search works by extracting trigrams from the regular expression
and then looking these up in the index.  The more trigrams that can be
extracted from the regular expression, the more effective the index search
is.  Unlike B-tree based searches, the search string need not be
left-anchored.

For both `LIKE` and regular-expression searches, keep in mind
that a pattern with no extractable trigrams will degenerate to a full-index
scan.

The choice between GiST and GIN indexing depends on the relative
performance characteristics of GiST and GIN, which are discussed elsewhere.

### Text Search Integration

Trigram matching is a very useful tool when used in conjunction
with a full text index.  In particular it can help to recognize
misspelled input words that will not be matched directly by the
full text search mechanism.

The first step is to generate an auxiliary table containing all
the unique words in the documents:

```
CREATE TABLE words AS SELECT word FROM
ts_stat('SELECT to_tsvector(''simple'', bodytext) FROM documents');
```

where `documents` is a table that has a text field
`bodytext` that we wish to search.  The reason for using
the `simple` configuration with the `to_tsvector`
function, instead of using a language-specific configuration,
is that we want a list of the original (unstemmed) words.

Next, create a trigram index on the word column:

```
CREATE INDEX words_idx ON words USING GIN (word gin_trgm_ops);
```

Now, a `SELECT` query similar to the previous example can
be used to suggest spellings for misspelled words in user search terms.
A useful extra test is to require that the selected words are also of
similar length to the misspelled word.

> **Note:**

> Since the `words` table has been generated as a separate,
> static table, it will need to be periodically regenerated so that
> it remains reasonably up-to-date with the document collection.
> Keeping it exactly current is usually unnecessary.
>

### References

GiST Development Site
[](http://www.sai.msu.su/~megera/postgres/gist/)

Tsearch2 Development Site
[](http://www.sai.msu.su/~megera/postgres/gist/tsearch/V2/)

### Authors

Oleg Bartunov oleg@sai.msu.su, Moscow, Moscow University, Russia

Teodor Sigaev teodor@sigaev.ru, Moscow, Delta-Soft Ltd.,Russia

Alexander Korotkov a.korotkov@postgrespro.ru, Moscow, Postgres Professional, Russia

Documentation: Christopher Kings-Lynne

This module is sponsored by Delta-Soft Ltd., Moscow, Russia.

### Configuration Parameters

**`postgres_fdw.application_name` (`string`)**
: Specifies a value for [guc-application-name](#guc-application-name)
configuration parameter used when `postgres_fdw`
establishes a connection to a foreign server.  This overrides
`application_name` option of the server object.
Note that change of this parameter doesn't affect any existing
connections until they are re-established.

`postgres_fdw.application_name` can be any string
of any length and contain even non-ASCII characters.  However when
it's passed to and used as `application_name`
in a foreign server, note that it will be truncated to less than
`NAMEDATALEN` characters.
Anything other than printable ASCII characters are replaced with [C-style hexadecimal escapes](#sql-syntax-strings-escape).
See [guc-application-name](#guc-application-name) for details.

`%` characters begin "escape sequences"
that are replaced with status information as outlined below.
Unrecognized escapes are ignored. Other characters are copied straight
to the application name. Note that it's not allowed to specify a
plus/minus sign or a numeric literal after the `%`
and before the option, for alignment and padding.

Escape
Effect

`%a`
Application name on local server

`%c`

Session ID on local server
(see [guc-log-line-prefix](#guc-log-line-prefix) for details)

`%C`

Cluster name on local server
(see [guc-cluster-name](#guc-cluster-name) for details)

`%u`
User name on local server

`%d`
Database name on local server

`%p`
Process ID of backend on local server

`%%`
Literal %

For example, suppose user `local_user` establishes
a connection from database `local_db` to
`foreign_db` as user `foreign_user`,
the setting `'db=%d, user=%u'` is replaced with
`'db=local_db, user=local_user'`.

### Examples

Here is an example of creating a foreign table with
`postgres_fdw`. First install the extension:

```
CREATE EXTENSION postgres_fdw;
```

Then create a foreign server using [sql-createserver](#sql-createserver).
In this example we wish to connect to a PostgreSQL server
on host `192.83.123.89` listening on
port `5432`.  The database to which the connection is made
is named `foreign_db` on the remote server:

```
CREATE SERVER foreign_server
FOREIGN DATA WRAPPER postgres_fdw
OPTIONS (host '192.83.123.89', port '5432', dbname 'foreign_db');
```

A user mapping, defined with [sql-createusermapping](#sql-createusermapping), is
needed as well to identify the role that will be used on the remote
server:

```
CREATE USER MAPPING FOR local_user
SERVER foreign_server
OPTIONS (user 'foreign_user', password 'password');
```

Now it is possible to create a foreign table with
[sql-createforeigntable](#sql-createforeigntable).  In this example we
wish to access the table named `some_schema.some_table`
on the remote server.  The local name for it will
be `foreign_table`:

```
CREATE FOREIGN TABLE foreign_table (
id integer NOT NULL,
data text
)
SERVER foreign_server
OPTIONS (schema_name 'some_schema', table_name 'some_table');
```

It's essential that the data types and other properties of the columns
declared in `CREATE FOREIGN TABLE` match the actual remote table.
Column names must match as well, unless you attach `column_name`
options to the individual columns to show how they are named in the remote
table.
In many cases, use of [`IMPORT FOREIGN SCHEMA`](#sql-importforeignschema) is
preferable to constructing foreign table definitions manually.

### GUC Parameters

**`sepgsql.permissive` (`boolean`)**
: This parameter enables `sepgsql` to function
in permissive mode, regardless of the system setting.
The default is off.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

When this parameter is on, `sepgsql` functions
in permissive mode, even if SELinux in general is working in enforcing
mode.  This parameter is primarily useful for testing purposes.

**`sepgsql.debug_audit` (`boolean`)**
: This parameter enables the printing of audit messages regardless of
the system policy settings.
The default is off, which means that messages will be printed according
to the system settings.

The security policy of SELinux also has rules to
control whether or not particular accesses are logged.
By default, access violations are logged, but allowed
accesses are not.

This parameter forces all possible logging to be turned on, regardless
of the system policy.

### Limitations

**Data Definition Language (DDL) Permissions**
: Due to implementation restrictions, some DDL operations do not
check permissions.

**Data Control Language (DCL) Permissions**
: Due to implementation restrictions, DCL operations do not check
permissions.

**Row-level access control**
: PostgreSQL supports row-level access, but
`sepgsql` does not.

**Covert channels**
: `sepgsql` does not try to hide the existence of
a certain object, even if the user is not allowed to reference it.
For example, we can infer the existence of an invisible object as
a result of primary key conflicts, foreign key violations, and so on,
even if we cannot obtain the contents of the object.  The existence
of a top secret table cannot be hidden; we only hope to conceal its
contents.

## spi — Server Programming Interface features/examples

The spi module provides several workable examples
of using the [Server Programming Interface](#spi)
(SPI) and triggers.  While these functions are of
some value in
their own right, they are even more useful as examples to modify for
your own purposes.  The functions are general enough to be used
with any table, but you have to specify table and field names (as described
below) while creating a trigger.

Each of the groups of functions described below is provided as a
separately-installable extension.

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

### Examples

Here is an example of selecting a sample of a table with
`SYSTEM_ROWS`.  First install the extension:

```
CREATE EXTENSION tsm_system_rows;
```

Then you can use it in a `SELECT` command, for instance:

```
SELECT * FROM my_table TABLESAMPLE SYSTEM_ROWS(100);
```

This command will return a sample of 100 rows from the
table `my_table` (unless the table does not have 100
visible rows, in which case all its rows are returned).

### Examples

Here is an example of selecting a sample of a table with
`SYSTEM_TIME`.  First install the extension:

```
CREATE EXTENSION tsm_system_time;
```

Then you can use it in a `SELECT` command, for instance:

```
SELECT * FROM my_table TABLESAMPLE SYSTEM_TIME(1000);
```

This command will return as large a sample of `my_table` as
it can read in 1 second (1000 milliseconds).  Of course, if the whole
table can be read in under 1 second, all its rows will be returned.

## Examples

```
$ # what's in this database server, anyway?
$ oid2name
All databases:
Oid  Database Name  Tablespace
----------------------------------
17228       alvherre  pg_default
17255     regression  pg_default
17227      template0  pg_default
1      template1  pg_default

$ oid2name -s
All tablespaces:
Oid  Tablespace Name
-------------------------
1663       pg_default
1664        pg_global
155151         fastdisk
155152          bigdisk

$ # OK, let's look into database alvherre
$ cd $PGDATA/base/17228

$ # get top 10 db objects in the default tablespace, ordered by size
$ ls -lS * | head -10
-rw-------  1 alvherre alvherre 136536064 sep 14 09:51 155173
-rw-------  1 alvherre alvherre  17965056 sep 14 09:51 1155291
-rw-------  1 alvherre alvherre   1204224 sep 14 09:51 16717
-rw-------  1 alvherre alvherre    581632 sep  6 17:51 1255
-rw-------  1 alvherre alvherre    237568 sep 14 09:50 16674
-rw-------  1 alvherre alvherre    212992 sep 14 09:51 1249
-rw-------  1 alvherre alvherre    204800 sep 14 09:51 16684
-rw-------  1 alvherre alvherre    196608 sep 14 09:50 16700
-rw-------  1 alvherre alvherre    163840 sep 14 09:50 16699
-rw-------  1 alvherre alvherre    122880 sep  6 17:51 16751

$ # I wonder what file 155173 is ...
$ oid2name -d alvherre -f 155173
From database "alvherre":
Filenode  Table Name
----------------------
155173    accounts

$ # you can ask for more than one object
$ oid2name -d alvherre -f 155173 -f 1155291
From database "alvherre":
Filenode     Table Name
-------------------------
155173       accounts
1155291  accounts_pkey

$ # you can mix the options, and get more details with -x
$ oid2name -d alvherre -t accounts -f 1155291 -x
From database "alvherre":
Filenode     Table Name      Oid  Schema  Tablespace
------------------------------------------------------
155173       accounts   155173  public  pg_default
1155291  accounts_pkey  1155291  public  pg_default

$ # show disk space for every db object
$ du [0-9]* |
> while read SIZE FILENODE
> do
>   echo "$SIZE       `oid2name -q -d alvherre -i -f $FILENODE`"
> done
16            1155287  branches_pkey
16            1155289  tellers_pkey
17561            1155291  accounts_pkey
...

$ # same, but sort by size
$ du [0-9]* | sort -rn | while read SIZE FN
> do
>   echo "$SIZE   `oid2name -q -d alvherre -f $FN`"
> done
133466             155173    accounts
17561            1155291  accounts_pkey
1177              16717  pg_proc_proname_args_nsp_index
...

$ # If you want to see what's in tablespaces, use the pg_tblspc directory
$ cd $PGDATA/pg_tblspc
$ oid2name -s
All tablespaces:
Oid  Tablespace Name
-------------------------
1663       pg_default
1664        pg_global
155151         fastdisk
155152          bigdisk

$ # what databases have objects in tablespace "fastdisk"?
$ ls -d 155151/*
155151/17228/  155151/PG_VERSION

$ # Oh, what was database 17228 again?
$ oid2name
All databases:
Oid  Database Name  Tablespace
----------------------------------
17228       alvherre  pg_default
17255     regression  pg_default
17227      template0  pg_default
1      template1  pg_default

$ # Let's see what objects does this database have in the tablespace.
$ cd 155151/17228
$ ls -l
total 0
-rw-------  1 postgres postgres 0 sep 13 23:20 155156

$ # OK, this is a pretty small table ... but which one is it?
$ oid2name -d alvherre -f 155156
From database "alvherre":
Filenode  Table Name
----------------------
155156         foo
```
