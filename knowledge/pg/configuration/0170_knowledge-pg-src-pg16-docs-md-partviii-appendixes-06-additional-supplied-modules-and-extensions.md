# Configuration; Usage

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > dict_int; dict_xsyn; unaccent > Configuration; Usage`
- Source Line Ranges: `574-583, 617-742, 801-821, 838-850, 1105-1136, 1353-1429, 2810-2873, 2874-2969, 5318-5340, 6049-6066, 6240-6254, 6574-6632, 8484-8542, 8719-8742, 10346-10486`
- Chunk ID: `pg16_configuration_0170_77bcc3640e`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `811e2a107aa3d33c27cf30a68806894eb020ff72bf6c922634859acebecd2f03`

## Retrieval Guidance

- Use When: Configure full-text-search dictionary behavior for integers, synonyms, or diacritic removal.
- Retrieval Keywords: dict_int, dict_xsyn, unaccent, text search dictionary, dictionary configuration, RULES, synonym dictionary
- Follow-up Guidance: Re-test representative text-search queries after changing dictionary rules.
- Classification Note: These text-search dictionary modules define dictionary configuration files and options that affect lexeme normalization.

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

### Usage

[cube-operators-table](#cube-operators-table) shows the specialized operators
provided for type `cube`.

| Operator                         Description |
| --- |
| `cube` `&&` `cube`         boolean                         Do the cubes overlap? |
| `cube` `@>` `cube`         boolean                         Does the first cube contain the second? |
| `cube` `` `integer`         float8                         Extracts the n-th coordinate of the cube         (counting from 1). |
| `cube` `~>` `integer`         float8                         Extracts the n-th coordinate of the cube,         counting in the following way: n = 2         * k - 1 means lower bound         of k-th dimension, n = 2         * k means upper bound of         k-th dimension.  Negative         n denotes the inverse value of the corresponding         positive coordinate.  This operator is designed for KNN-GiST support. |
| `cube` `` `cube`         float8                         Computes the Euclidean distance between the two cubes. |
| `cube` `` `cube`         float8                         Computes the taxicab (L-1 metric) distance between the two cubes. |
| `cube` `` `cube`         float8                         Computes the Chebyshev (L-inf metric) distance between the two cubes. |

In addition to the above operators, the usual comparison
operators shown in [functions-comparison-op-table](#functions-comparison-op-table) are
available for type `cube`.  These
operators first compare the first coordinates, and if those are equal,
compare the second coordinates, etc.  They exist mainly to support the
b-tree index operator class for `cube`, which can be useful for
example if you would like a UNIQUE constraint on a `cube` column.
Otherwise, this ordering is not of much practical use.

The `cube` module also provides a GiST index operator class for
`cube` values.
A `cube` GiST index can be used to search for values using the
`=`, `&&`, `@>`, and
`<@` operators in `WHERE` clauses.

In addition, a `cube` GiST index can be used to find nearest
neighbors using the metric operators
`<->`, `<#>`, and
`<=>` in `ORDER BY` clauses.
For example, the nearest neighbor of the 3-D point (0.5, 0.5, 0.5)
could be found efficiently with:

```
SELECT c FROM test ORDER BY c  cube(array[0.5,0.5,0.5]) LIMIT 1;
```

The `~>` operator can also be used in this way to
efficiently retrieve the first few values sorted by a selected coordinate.
For example, to get the first few cubes ordered by the first coordinate
(lower left corner) ascending one could use the following query:

```
SELECT c FROM test ORDER BY c ~> 1 LIMIT 5;
```

And to get 2-D cubes ordered by the first coordinate of the upper right
corner descending:

```
SELECT c FROM test ORDER BY c ~> 3 DESC LIMIT 5;
```

[cube-functions-table](#cube-functions-table) shows the available functions.

| Function                         Description                         Example(s) |
| --- |
| `cube` ( `float8` )         cube                         Makes a one dimensional cube with both coordinates the same.                         `cube(1)`         (1) |
| `cube` ( `float8`, `float8` )         cube                         Makes a one dimensional cube.                         `cube(1, 2)`         (1),(2) |
| `cube` ( `float8[]` )         cube                         Makes a zero-volume cube using the coordinates defined by the array.                         `cube(ARRAY[1,2,3])`         (1, 2, 3) |
| `cube` ( `float8[]`, `float8[]` )         cube                         Makes a cube with upper right and lower left coordinates as defined by         the two arrays, which must be of the same length.                         `cube(ARRAY[1,2], ARRAY[3,4])`         (1, 2),(3, 4) |
| `cube` ( `cube`, `float8` )         cube                         Makes a new cube by adding a dimension on to an existing cube,         with the same values for both endpoints of the new coordinate.  This         is useful for building cubes piece by piece from calculated values.                         `cube('(1,2),(3,4)'::cube, 5)`         (1, 2, 5),(3, 4, 5) |
| `cube` ( `cube`, `float8`, `float8` )         cube                         Makes a new cube by adding a dimension on to an existing cube. This is         useful for building cubes piece by piece from calculated values.                         `cube('(1,2),(3,4)'::cube, 5, 6)`         (1, 2, 5),(3, 4, 6) |
| `cube_dim` ( `cube` )         integer                         Returns the number of dimensions of the cube.                         `cube_dim('(1,2),(3,4)')`         2 |
| `cube_ll_coord` ( `cube`, `integer` )         float8                         Returns the n-th coordinate value for the lower         left corner of the cube.                         `cube_ll_coord('(1,2),(3,4)', 2)`         2 |
| `cube_ur_coord` ( `cube`, `integer` )         float8                         Returns the n-th coordinate value for the         upper right corner of the cube.                         `cube_ur_coord('(1,2),(3,4)', 2)`         4 |
| `cube_is_point` ( `cube` )         boolean                         Returns true if the cube is a point, that is,         the two defining corners are the same.                         `cube_is_point(cube(1,1))`         t |
| `cube_distance` ( `cube`, `cube` )         float8                         Returns the distance between two cubes. If both         cubes are points, this is the normal distance function.                         `cube_distance('(1,2)', '(3,4)')`         2.8284271247461903 |
| `cube_subset` ( `cube`, `integer[]` )         cube                         Makes a new cube from an existing cube, using a list of         dimension indexes from an array. Can be used to extract the endpoints         of a single dimension, or to drop dimensions, or to reorder them as         desired.                         `cube_subset(cube('(1,3,5),(6,7,8)'), ARRAY[2])`         (3),(7)                         `cube_subset(cube('(1,3,5),(6,7,8)'), ARRAY[3,2,1,1])`         (5, 3, 1, 1),(8, 7, 6, 6) |
| `cube_union` ( `cube`, `cube` )         cube                         Produces the union of two cubes.                         `cube_union('(1,2)', '(3,4)')`         (1, 2),(3, 4) |
| `cube_inter` ( `cube`, `cube` )         cube                         Produces the intersection of two cubes.                         `cube_inter('(1,2)', '(3,4)')`         (3, 4),(1, 2) |
| `cube_enlarge` ( c `cube`, r `double`, n `integer` )         cube                         Increases the size of the cube by the specified         radius r in at least n         dimensions.  If the radius is negative the cube is shrunk instead.         All defined dimensions are changed by the         radius r.  Lower-left coordinates are decreased         by r and upper-right coordinates are increased         by r.  If a lower-left coordinate is increased         to more than the corresponding upper-right coordinate (this can only         happen when r  0), then extra dimensions are added to         make n altogether; 0 is used as the initial         value for the extra coordinates.  This function is useful for creating         bounding boxes around a point for searching for nearby points.                         `cube_enlarge('(1,2),(3,4)', 0.5, 3)`         (0.5, 1.5, -0.5),(3.5, 4.5, 0.5) |

## dict_int —
example full-text search dictionary for integers

`dict_int` is an example of an add-on dictionary template
for full-text search.  The motivation for this example dictionary is to
control the indexing of integers (signed and unsigned), allowing such
numbers to be indexed while preventing excessive growth in the number of
unique words, which greatly affects the performance of searching.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Configuration

The dictionary accepts three options:

- The `maxlen` parameter specifies the maximum number of
digits allowed in an integer word.  The default value is 6.
- The `rejectlong` parameter specifies whether an overlength
integer should be truncated or ignored.  If `rejectlong` is
`false` (the default), the dictionary returns the first
`maxlen` digits of the integer. If `rejectlong` is
`true`, the dictionary treats an overlength integer as a stop
word, so that it will not be indexed.  Note that this also means that
such an integer cannot be searched for.
- The `absval` parameter specifies whether leading
"`+`" or "`-`"
signs should be removed from integer words.  The default
is `false`.  When `true`, the sign is
removed before `maxlen` is applied.

### Usage

Installing the `dict_int` extension creates a text search
template `intdict_template` and a dictionary `intdict`
based on it, with the default parameters.  You can alter the
parameters, for example

```
mydb# ALTER TEXT SEARCH DICTIONARY intdict (MAXLEN = 4, REJECTLONG = true);
ALTER TEXT SEARCH DICTIONARY
```

or create new dictionaries based on the template.

To test the dictionary, you can try

```
mydb# select ts_lexize('intdict', '12345678');
ts_lexize
-----------
{123456}
```

but real-world usage will involve including it in a text search
configuration as described in [textsearch](#textsearch).
That might look like this:

```
ALTER TEXT SEARCH CONFIGURATION english
ALTER MAPPING FOR int, uint WITH intdict;
```

## dict_xsyn — example synonym full-text search dictionary

`dict_xsyn` (Extended Synonym Dictionary) is an example of an
add-on dictionary template for full-text search.  This dictionary type
replaces words with groups of their synonyms, and so makes it possible to
search for a word using any of its synonyms.

### Configuration

A `dict_xsyn` dictionary accepts the following options:

- `matchorig` controls whether the original word is accepted by
the dictionary. Default is `true`.
- `matchsynonyms` controls whether the synonyms are
accepted by the dictionary. Default is `false`.
- `keeporig` controls whether the original word is included in
the dictionary's output. Default is `true`.
- `keepsynonyms` controls whether the synonyms are included in
the dictionary's output. Default is `true`.
- `rules` is the base name of the file containing the list of
synonyms.  This file must be stored in
`$SHAREDIR/tsearch_data/` (where `$SHAREDIR` means
the PostgreSQL installation's shared-data directory).
Its name must end in `.rules` (which is not to be included in
the `rules` parameter).

The rules file has the following format:

- Each line represents a group of synonyms for a single word, which is
given first on the line. Synonyms are separated by whitespace, thus:

```
word syn1 syn2 syn3
```
- The sharp (`#`) sign is a comment delimiter. It may appear at
any position in a line.  The rest of the line will be skipped.

Look at `xsyn_sample.rules`, which is installed in
`$SHAREDIR/tsearch_data/`, for an example.

### Usage

Installing the `dict_xsyn` extension creates a text search
template `xsyn_template` and a dictionary `xsyn`
based on it, with default parameters.  You can alter the
parameters, for example

```
mydb# ALTER TEXT SEARCH DICTIONARY xsyn (RULES='my_rules', KEEPORIG=false);
ALTER TEXT SEARCH DICTIONARY
```

or create new dictionaries based on the template.

To test the dictionary, you can try

```
mydb=# SELECT ts_lexize('xsyn', 'word');
ts_lexize
-----------------------
{syn1,syn2,syn3}

mydb# ALTER TEXT SEARCH DICTIONARY xsyn (RULES='my_rules', KEEPORIG=true);
ALTER TEXT SEARCH DICTIONARY

mydb=# SELECT ts_lexize('xsyn', 'word');
ts_lexize
-----------------------
{word,syn1,syn2,syn3}

mydb# ALTER TEXT SEARCH DICTIONARY xsyn (RULES='my_rules', KEEPORIG=false, MATCHSYNONYMS=true);
ALTER TEXT SEARCH DICTIONARY

mydb=# SELECT ts_lexize('xsyn', 'syn1');
ts_lexize
-----------------------
{syn1,syn2,syn3}

mydb# ALTER TEXT SEARCH DICTIONARY xsyn (RULES='my_rules', KEEPORIG=true, MATCHORIG=false, KEEPSYNONYMS=false);
ALTER TEXT SEARCH DICTIONARY

mydb=# SELECT ts_lexize('xsyn', 'syn1');
ts_lexize
-----------------------
{word}
```

Real-world usage will involve including it in a text search
configuration as described in [textsearch](#textsearch).
That might look like this:

```
ALTER TEXT SEARCH CONFIGURATION english
ALTER MAPPING FOR word, asciiword WITH xsyn, english_stem;
```

### The `pg_buffercache_usage_counts()` Function

The definitions of the columns exposed by the function are shown in
[pgbuffercache_usage_counts-columns](#pgbuffercache_usage_counts-columns).

| Column Type                      Description |
| --- |
| `usage_count` `int4`                      A possible buffer usage count |
| `buffers` `int4`                      Number of buffers with the usage count |
| `dirty` `int4`                      Number of dirty buffers with the usage count |
| `pinned` `int4`                      Number of pinned buffers with the usage count |

The `pg_buffercache_usage_counts()` function returns a
set of rows summarizing the states of all shared buffers, aggregated over
the possible usage count values.  Similar and more detailed information is
provided by the `pg_buffercache` view, but
`pg_buffercache_usage_counts()` is significantly cheaper.

Like the `pg_buffercache` view,
`pg_buffercache_usage_counts()` does not acquire buffer
manager locks. Therefore concurrent activity can lead to minor inaccuracies
in the result.

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

### Usage

The `seg` module includes a GiST index operator class for
`seg` values.
The operators supported by the GiST operator class are shown in [seg-gist-operators](#seg-gist-operators).

| Operator                         Description |
| --- |
| `seg` `>` `seg`         boolean                         Is the first `seg` entirely to the right of the second?         [a, b] >> [c, d] is true if a > d. |
| `seg` `&` `seg`         boolean                         Does the first `seg` not extend to the left of the         second?         [a, b] &> [c, d] is true if a >= c. |
| `seg` `=` `seg`         boolean                         Are the two `seg`s equal? |
| `seg` `&&` `seg`         boolean                         Do the two `seg`s overlap? |
| `seg` `@>` `seg`         boolean                         Does the first `seg` contain the second? |
| `seg` ` select '10(+-)1'::seg as seg;
seg
---------
9.0 .. 11             -- should be: 9 .. 11
```

The performance of an R-tree index can largely depend on the initial
order of input values. It may be very helpful to sort the input table
on the `seg` column; see the script `sort-segments.pl`
for an example.

## unaccent — a text search dictionary which removes diacritics

`unaccent` is a text search dictionary that removes accents
(diacritic signs) from lexemes.
It's a filtering dictionary, which means its output is
always passed to the next dictionary (if any), unlike the normal
behavior of dictionaries.  This allows accent-insensitive processing
for full text search.

The current implementation of `unaccent` cannot be used as a
normalizing dictionary for the `thesaurus` dictionary.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Configuration

An `unaccent` dictionary accepts the following options:

- `RULES` is the base name of the file containing the list of
translation rules.  This file must be stored in
`$SHAREDIR/tsearch_data/` (where `$SHAREDIR` means
the PostgreSQL installation's shared-data directory).
Its name must end in `.rules` (which is not to be included in
the `RULES` parameter).

The rules file has the following format:

- Each line represents one translation rule, consisting of a character with
accent followed by a character without accent.  The first is translated
into the second.  For example,

```
A
A
A
A
A
A
AE
```

The two characters must be separated by whitespace, and any leading or
trailing whitespace on a line is ignored.
- Alternatively, if only one character is given on a line, instances of
that character are deleted; this is useful in languages where accents
are represented by separate characters.
- Actually, each "character" can be any string not containing
whitespace, so `unaccent` dictionaries could be used for
other sorts of substring substitutions besides diacritic removal.
- As with other PostgreSQL text search configuration files,
the rules file must be stored in UTF-8 encoding.  The data is
automatically translated into the current database's encoding when
loaded.  Any lines containing untranslatable characters are silently
ignored, so that rules files can contain rules that are not applicable in
the current encoding.

A more complete example, which is directly useful for most European
languages, can be found in `unaccent.rules`, which is installed
in `$SHAREDIR/tsearch_data/` when the `unaccent`
module is installed.  This rules file translates characters with accents
to the same characters without accents, and it also expands ligatures
into the equivalent series of simple characters (for example,  to
AE).

### Usage

Installing the `unaccent` extension creates a text
search template `unaccent` and a dictionary `unaccent`
based on it.  The `unaccent` dictionary has the default
parameter setting `RULES='unaccent'`, which makes it immediately
usable with the standard `unaccent.rules` file.
If you wish, you can alter the parameter, for example

```
mydb=# ALTER TEXT SEARCH DICTIONARY unaccent (RULES='my_rules');
```

or create new dictionaries based on the template.

To test the dictionary, you can try:

```
mydb=# select ts_lexize('unaccent','Htel');
ts_lexize
-----------
{Hotel}
(1 row)
```

Here is an example showing how to insert the
`unaccent` dictionary into a text search configuration:

```
mydb=# CREATE TEXT SEARCH CONFIGURATION fr ( COPY = french );
mydb=# ALTER TEXT SEARCH CONFIGURATION fr
ALTER MAPPING FOR hword, hword_part, word
WITH unaccent, french_stem;
mydb=# select to_tsvector('fr','Htels de la Mer');
to_tsvector
-------------------
'hotel':1 'mer':4
(1 row)

mydb=# select to_tsvector('fr','Htel de la Mer') @@ to_tsquery('fr','Hotels');
?column?
----------
t
(1 row)

mydb=# select ts_headline('fr','Htel de la Mer',to_tsquery('fr','Hotels'));
ts_headline
------------------------
Htel de la Mer
(1 row)
```

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
