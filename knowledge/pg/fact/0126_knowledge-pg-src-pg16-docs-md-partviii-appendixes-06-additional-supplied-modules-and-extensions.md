# adminpack - pgAdmin support toolpack

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > adminpack - pgAdmin support toolpack`
- Source Line Ranges: `1-11155`
- Chunk ID: `pg16_fact_0126_c5edfc57e5`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `f7fb0528dd4895abd16bdb8fda9f1dfee3697085fee8c686616f6bb4d4d226e0`

## Retrieval Guidance

- Use When: Look up adminpack functions and privileges.
- Retrieval Keywords: adminpack, pg_file_write, pg_file_rename, pg_file_unlink, pg_logdir_ls, pgAdmin
- Follow-up Guidance: Review security implications before granting access to file-manipulation functions.
- Classification Note: The module section documents support functions for pgAdmin/server file access as extension reference.

## Official Source Content

## Additional Supplied Modules and Extensions

This appendix and the next one contain information on the
optional components
found in the `contrib` directory of the
PostgreSQL distribution.
These include porting tools, analysis utilities,
and plug-in features that are not part of the core PostgreSQL system.
They are separate mainly
because they address a limited audience or are too experimental
to be part of the main source tree.  This does not preclude their
usefulness.

This appendix covers extensions and other server plug-in module
libraries found in
`contrib`.  [contrib-prog](#contrib-prog) covers utility
programs.

When building from the source distribution, these optional
components are not built
automatically, unless you build the "world" target
(see [build](#build)).
You can build and install all of them by running:

```
make
make install
```

in the `contrib` directory of a configured source tree;
or to build and install
just one selected module, do the same in that module's subdirectory.
Many of the modules have regression tests, which can be executed by
running:

```
make check
```

before installation or

```
make installcheck
```

once you have a PostgreSQL server running.

If you are using a pre-packaged version of PostgreSQL,
these components are typically made available as a separate subpackage,
such as `postgresql-contrib`.

Many components supply new user-defined functions, operators, or types,
packaged as *extensions*.
To make use of one of these extensions, after you have installed the code
you need to register the new SQL objects in the database system.
This is done by executing
a [sql-createextension](#sql-createextension) command.  In a fresh database,
you can simply do

```
CREATE EXTENSION `extension_name`;
```

This command registers the new SQL objects in the current database only,
so you need to run it in every database in which you want
the extension's facilities to be available.  Alternatively, run it in
database `template1` so that the extension will be copied into
subsequently-created databases by default.

For all extensions, the `CREATE EXTENSION` command must be
run by a database superuser, unless the extension is
considered "trusted".  Trusted extensions can be run by any
user who has `CREATE` privilege on the current
database.  Extensions that are trusted are identified as such in the
sections that follow.  Generally, trusted extensions are ones that cannot
provide access to outside-the-database functionality.

The following extensions are trusted in a default installation:

Many extensions allow you to install their objects in a schema of your
choice.  To do that, add `SCHEMA
`schema_name`` to the `CREATE EXTENSION`
command.  By default, the objects will be placed in your current creation
target schema, which in turn defaults to `public`.

Note, however, that some of these components are not "extensions"
in this sense, but are loaded into the server in some other way, for instance
by way of
[guc-shared-preload-libraries](#guc-shared-preload-libraries).  See the documentation of each
component for details.

## adminpack — pgAdmin support toolpack

`adminpack` provides a number of support functions which
pgAdmin and other administration and management tools can
use to provide additional functionality, such as remote management
of server log files.
Use of all these functions is only allowed to database superusers by default, but may be
allowed to other users by using the `GRANT` command.

The functions shown in [functions-adminpack-table](#functions-adminpack-table) provide
write access to files on the machine hosting the server.  (See also the
functions in [functions-admin-genfile-table](#functions-admin-genfile-table), which
provide read-only access.)
Only files within the database cluster directory can be accessed, unless the
user is a superuser or given privileges of one of the
`pg_read_server_files` or
`pg_write_server_files` roles, as appropriate for the
function, but either a relative or absolute path is allowable.

| Function                         Description |
| --- |
| `pg_catalog.pg_file_write` ( filename `text`, data `text`, append `boolean` )         bigint                         Writes, or appends to, a text file. |
| `pg_catalog.pg_file_sync` ( filename `text` )         void                         Flushes a file or directory to disk. |
| `pg_catalog.pg_file_rename` ( oldname `text`, newname `text` , archivename `text`  )         boolean                         Renames a file. |
| `pg_catalog.pg_file_unlink` ( filename `text` )         boolean                         Removes a file. |
| `pg_catalog.pg_logdir_ls` ()         setof record                         Lists the log files in the `log_directory` directory. |

`pg_file_write` writes the specified
data into
the file named by
filename.  If
append is
false, the file must not already exist.  If
append is true,
the file can already exist, and will be appended to if so.
Returns the number of bytes written.

`pg_file_sync` fsyncs the specified file or directory
named by
filename.  An error is thrown
on failure (e.g., the specified file is not present). Note that
[guc-data-sync-retry](#guc-data-sync-retry) has no effect on this function,
and therefore a PANIC-level error will not be raised even on failure to
flush database files.

`pg_file_rename` renames a file.  If
archivename
is omitted or NULL, it simply renames
oldname
to
newname (which must not already exist).
If
archivename is provided, it first
renames
newname to
archivename (which must
not already exist), and then renames
oldname
to
newname.  In event of failure of the second rename step,
it will try to rename
archivename back
to
newname before reporting the error.
Returns true on success, false if the source file(s) are not present or
not writable; other cases throw errors.

`pg_file_unlink` removes the specified file.
Returns true on success, false if the specified file is not present
or the `unlink()` call fails; other cases throw errors.

`pg_logdir_ls` returns the start timestamps and path
names of all the log files in the [guc-log-directory](#guc-log-directory)
directory.  The [guc-log-filename](#guc-log-filename) parameter must have its
default setting (`postgresql-%Y-%m-%d_%H%M%S.log`) to use this
function.

## amcheck — tools to verify table and index consistency

The `amcheck` module provides functions that allow you to
verify the logical consistency of the structure of relations.

The B-Tree checking functions verify various *invariants* in the
structure of the representation of particular relations.  The
correctness of the access method functions behind index scans and
other important operations relies on these invariants always
holding.  For example, certain functions verify, among other things,
that all B-Tree pages have items in "logical" order (e.g.,
for B-Tree indexes on `text`, index tuples should be in
collated lexical order).  If that particular invariant somehow fails
to hold, we can expect binary searches on the affected page to
incorrectly guide index scans, resulting in wrong answers to SQL
queries.  If the structure appears to be valid, no error is raised.

Verification is performed using the same procedures as those used by
index scans themselves, which may be user-defined operator class
code.  For example, B-Tree index verification relies on comparisons
made with one or more B-Tree support function 1 routines.  See [xindex-support](#xindex-support) for details of operator class support
functions.

Unlike the B-Tree checking functions which report corruption by raising
errors, the heap checking function `verify_heapam` checks
a table and attempts to return a set of rows, one row per corruption
detected.  Despite this, if facilities that
`verify_heapam` relies upon are themselves corrupted, the
function may be unable to continue and may instead raise an error.

Permission to execute `amcheck` functions may be granted
to non-superusers, but before granting such permissions careful consideration
should be given to data security and privacy concerns.  Although the
corruption reports generated by these functions do not focus on the contents
of the corrupted data so much as on the structure of that data and the nature
of the corruptions found, an attacker who gains permission to execute these
functions, particularly if the attacker can also induce corruption, might be
able to infer something of the data itself from such messages.

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

### Repairing Corruption

No error concerning corruption raised by `amcheck` should
ever be a false positive.  `amcheck` raises
errors in the event of conditions that, by definition, should never
happen, and so careful analysis of `amcheck`
errors is often required.

There is no general method of repairing problems that
`amcheck` detects.  An explanation for the root cause of
an invariant violation should be sought.  [pageinspect](#pageinspect) may play a useful role in diagnosing
corruption that `amcheck` detects.  A `REINDEX`
may not be effective in repairing corruption.

## auth_delay — pause on authentication failure

`auth_delay` causes the server to pause briefly before
reporting authentication failure, to make brute-force attacks on database
passwords more difficult.  Note that it does nothing to prevent
denial-of-service attacks, and may even exacerbate them, since processes
that are waiting before reporting authentication failure will still consume
connection slots.

In order to function, this module must be loaded via
[guc-shared-preload-libraries](#guc-shared-preload-libraries) in `postgresql.conf`.

### Configuration Parameters

**`auth_delay.milliseconds` (`integer`)**
: The number of milliseconds to wait before reporting an authentication
failure.  The default is 0.

These parameters must be set in `postgresql.conf`.
Typical usage might be:

```
# postgresql.conf
shared_preload_libraries = 'auth_delay'

auth_delay.milliseconds = '500'
```

### Author

KaiGai Kohei kaigai@ak.jp.nec.com

## auto_explain — log execution plans of slow queries

The `auto_explain` module provides a means for
logging execution plans of slow statements automatically, without
having to run [sql-explain](#sql-explain)
by hand.  This is especially helpful for tracking down un-optimized queries
in large applications.

The module provides no SQL-accessible functions.  To use it, simply
load it into the server.  You can load it into an individual session:

```
LOAD 'auto_explain';
```

(You must be superuser to do that.)  More typical usage is to preload
it into some or all sessions by including `auto_explain` in
[guc-session-preload-libraries](#guc-session-preload-libraries) or
[guc-shared-preload-libraries](#guc-shared-preload-libraries) in
`postgresql.conf`.  Then you can track unexpectedly slow queries
no matter when they happen.  Of course there is a price in overhead for
that.

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
# postgresql.conf
session_preload_libraries = 'auto_explain'

auto_explain.log_min_duration = '3s'
```

### Example

```
postgres=# LOAD 'auto_explain';
postgres=# SET auto_explain.log_min_duration = 0;
postgres=# SET auto_explain.log_analyze = true;
postgres=# SELECT count(*)
FROM pg_class, pg_index
WHERE oid = indrelid AND indisunique;
```

This might produce log output such as:

```

LOG:  duration: 3.651 ms  plan:
Query Text: SELECT count(*)
FROM pg_class, pg_index
WHERE oid = indrelid AND indisunique;
Aggregate  (cost=16.79..16.80 rows=1 width=0) (actual time=3.626..3.627 rows=1 loops=1)
->  Hash Join  (cost=4.17..16.55 rows=92 width=0) (actual time=3.349..3.594 rows=92 loops=1)
Hash Cond: (pg_class.oid = pg_index.indrelid)
->  Seq Scan on pg_class  (cost=0.00..9.55 rows=255 width=4) (actual time=0.016..0.140 rows=255 loops=1)
->  Hash  (cost=3.02..3.02 rows=92 width=4) (actual time=3.238..3.238 rows=92 loops=1)
Buckets: 1024  Batches: 1  Memory Usage: 4kB
->  Seq Scan on pg_index  (cost=0.00..3.02 rows=92 width=4) (actual time=0.008..3.187 rows=92 loops=1)
Filter: indisunique

```

### Author

Takahiro Itagaki itagaki.takahiro@oss.ntt.co.jp

## basebackup_to_shell — example "shell" pg_basebackup module

`basebackup_to_shell` adds a custom basebackup target
called `shell`. This makes it possible to run
`pg_basebackup --target=shell` or, depending on how this
module is configured,
`pg_basebackup --target=shell:`DETAIL_STRING``,
and cause a server command chosen by the server administrator to be executed
for each tar archive generated by the backup process. The command will receive
the contents of the archive via standard input.

This module is primarily intended as an example of how to create a new
backup targets via an extension module, but in some scenarios it may be
useful for its own sake.
In order to function, this module must be loaded via
[guc-shared-preload-libraries](#guc-shared-preload-libraries) or
[guc-local-preload-libraries](#guc-local-preload-libraries).

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

### Author

Robert Haas rhaas@postgresql.org

## basic_archive — an example WAL archive module

`basic_archive` is an example of an archive module.  This
module copies completed WAL segment files to the specified directory.  This
may not be especially useful, but it can serve as a starting point for
developing your own archive module.  For more information about archive
modules, see [archive-modules](#archive-modules).

In order to function, this module must be loaded via
[guc-archive-library](#guc-archive-library), and [guc-archive-mode](#guc-archive-mode)
must be enabled.

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
# postgresql.conf
archive_mode = 'on'
archive_library = 'basic_archive'
basic_archive.archive_directory = '/path/to/archive/directory'
```

### Notes

Server crashes may leave temporary files with the prefix
`archtemp` in the archive directory.  It is recommended to
delete such files before restarting the server after a crash.  It is safe to
remove such files while the server is running as long as they are unrelated
to any archiving still in progress, but users should use extra caution when
doing so.

### Author

Nathan Bossart

## bloom — bloom filter index access method

`bloom` provides an index access method based on
[Bloom filters](https://en.wikipedia.org/wiki/Bloom_filter).

A Bloom filter is a space-efficient data structure that is used to test
whether an element is a member of a set.  In the case of an index access
method, it allows fast exclusion of non-matching tuples via signatures
whose size is determined at index creation.

A signature is a lossy representation of the indexed attribute(s), and as
such is prone to reporting false positives; that is, it may be reported
that an element is in the set, when it is not.  So index search results
must always be rechecked using the actual attribute values from the heap
entry.  Larger signatures reduce the odds of a false positive and thus
reduce the number of useless heap visits, but of course also make the index
larger and hence slower to scan.

This type of index is most useful when a table has many attributes and
queries test arbitrary combinations of them.  A traditional btree index is
faster than a bloom index, but it can require many btree indexes to support
all possible queries where one needs only a single bloom index.  Note
however that bloom indexes only support equality queries, whereas btree
indexes can also perform inequality and range searches.

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

### Authors

Teodor Sigaev teodor@postgrespro.ru,
Postgres Professional, Moscow, Russia

Alexander Korotkov a.korotkov@postgrespro.ru,
Postgres Professional, Moscow, Russia

Oleg Bartunov obartunov@postgrespro.ru,
Postgres Professional, Moscow, Russia

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

## citext — a case-insensitive character string type

The `citext` module provides a case-insensitive
character string type, `citext`. Essentially, it internally calls
`lower` when comparing values. Otherwise, it behaves almost
exactly like `text`.

> **Tip:**

> Consider using *nondeterministic collations* (see
> [collation-nondeterministic](#collation-nondeterministic)) instead of this module.  They
> can be used for case-insensitive comparisons, accent-insensitive
> comparisons, and other combinations, and they handle more Unicode special
> cases correctly.
>

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Rationale

The standard approach to doing case-insensitive matches
in PostgreSQL has been to use the `lower`
function when comparing values, for example

```
SELECT * FROM tab WHERE lower(col) = LOWER(?);
```

This works reasonably well, but has a number of drawbacks:

- It makes your SQL statements verbose, and you always have to remember to
use `lower` on both the column and the query value.
- It won't use an index, unless you create a functional index using
`lower`.
- If you declare a column as `UNIQUE` or `PRIMARY
KEY`, the implicitly generated index is case-sensitive.  So it's
useless for case-insensitive searches, and it won't enforce
uniqueness case-insensitively.

The `citext` data type allows you to eliminate calls
to `lower` in SQL queries, and allows a primary key to
be case-insensitive. `citext` is locale-aware, just
like `text`, which means that the matching of upper case and
lower case characters is dependent on the rules of
the database's `LC_CTYPE` setting. Again, this behavior is
identical to the use of `lower` in queries. But because it's
done transparently by the data type, you don't have to remember to do
anything special in your queries.

### How to Use It

Here's a simple example of usage:

```
CREATE TABLE users (
nick CITEXT PRIMARY KEY,
pass TEXT   NOT NULL
);

INSERT INTO users VALUES ( 'larry',  sha256(random()::text::bytea) );
INSERT INTO users VALUES ( 'Tom',    sha256(random()::text::bytea) );
INSERT INTO users VALUES ( 'Damian', sha256(random()::text::bytea) );
INSERT INTO users VALUES ( 'NEAL',   sha256(random()::text::bytea) );
INSERT INTO users VALUES ( 'Bjrn',  sha256(random()::text::bytea) );

SELECT * FROM users WHERE nick = 'Larry';
```

The `SELECT` statement will return one tuple, even though
the `nick` column was set to `larry` and the query
was for `Larry`.

### String Comparison Behavior

`citext` performs comparisons by converting each string to lower
case (as though `lower` were called) and then comparing the
results normally.  Thus, for example, two strings are considered equal
if `lower` would produce identical results for them.

In order to emulate a case-insensitive collation as closely as possible,
there are `citext`-specific versions of a number of string-processing
operators and functions.  So, for example, the regular expression
operators `~` and `~*` exhibit the same behavior when
applied to `citext`: they both match case-insensitively.
The same is true
for `!~` and `!~*`, as well as for the
`LIKE` operators `~~` and `~~*`, and
`!~~` and `!~~*`. If you'd like to match
case-sensitively, you can cast the operator's arguments to `text`.

Similarly, all of the following functions perform matching
case-insensitively if their arguments are `citext`:

- `regexp_match()`
- `regexp_matches()`
- `regexp_replace()`
- `regexp_split_to_array()`
- `regexp_split_to_table()`
- `replace()`
- `split_part()`
- `strpos()`
- `translate()`

For the regexp functions, if you want to match case-sensitively, you can
specify the "c" flag to force a case-sensitive match.  Otherwise,
you must cast to `text` before using one of these functions if
you want case-sensitive behavior.

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

### Author

David E. Wheeler david@kineticode.com

Inspired by the original `citext` module by Donald Fraser.

## cube — a multi-dimensional cube data type

This module implements a data type `cube` for
representing multidimensional cubes.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Syntax

[cube-repr-table](#cube-repr-table) shows the valid external
representations for the `cube`
type.  `x`, `y`, etc. denote
floating-point numbers.

| External Syntax | Meaning |
| --- | --- |
| ``x`` | A one-dimensional point        (or, zero-length one-dimensional interval) |
| `(`x`)` | Same as above |
| ``x1`,`x2`,...,`xn`` | A point in n-dimensional space, represented internally as a       zero-volume cube |
| `(`x1`,`x2`,...,`xn`)` | Same as above |
| `(`x`),(`y`)` | A one-dimensional interval starting at `x` and ending at `y` or vice versa; the        order does not matter |
| `[(`x`),(`y`)]` | Same as above |
| `(`x1`,...,`xn`),(`y1`,...,`yn`)` | An n-dimensional cube represented by a pair of its diagonally        opposite corners |
| `[(`x1`,...,`xn`),(`y1`,...,`yn`)]` | Same as above |

It does not matter which order the opposite corners of a cube are
entered in.  The `cube` functions
automatically swap values if needed to create a uniform
"lower left — upper right" internal representation.
When the corners coincide, `cube` stores only one corner
along with an "is point" flag to avoid wasting space.

White space is ignored on input, so
`[(`x`),(`y`)]` is the same as
`[ ( `x` ), ( `y` ) ]`.

### Precision

Values are stored internally as 64-bit floating point numbers. This means
that numbers with more than about 16 significant digits will be truncated.

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

### Defaults

This union:

```
select cube_union('(0,5,2),(2,3,1)', '0');
cube_union
-------------------
(0, 0, 0),(2, 5, 2)
(1 row)
```

does not contradict common sense, neither does the intersection:

```
select cube_inter('(0,-1),(1,1)', '(-2),(2)');
cube_inter
-------------
(0, 0),(1, 0)
(1 row)
```

In all binary operations on differently-dimensioned cubes,
the lower-dimensional one is assumed to be a Cartesian projection, i. e., having zeroes
in place of coordinates omitted in the string representation. The above
examples are equivalent to:

```
cube_union('(0,5,2),(2,3,1)','(0,0,0),(0,0,0)');
cube_inter('(0,-1),(1,1)','(-2,0),(2,0)');
```

The following containment predicate uses the point syntax,
while in fact the second argument is internally represented by a box.
This syntax makes it unnecessary to define a separate point type
and functions for (box,point) predicates.

```
select cube_contains('(0,0),(1,1)', '0.5,0.5');
cube_contains
--------------
t
(1 row)
```

### Notes

For examples of usage, see the regression test `sql/cube.sql`.

To make it harder for people to break things, there
is a limit of 100 on the number of dimensions of cubes. This is set
in `cubedata.h` if you need something bigger.

### Credits

Original author: Gene Selkov, Jr. selkovjr@mcs.anl.gov,
Mathematics and Computer Science Division, Argonne National Laboratory.

My thanks are primarily to Prof. Joe Hellerstein
([](https://dsf.berkeley.edu/jmh/)) for elucidating the
gist of the GiST ([](http://gist.cs.berkeley.edu/)), and
to his former student Andy Dong for his example written for Illustra.
I am also grateful to all Postgres developers, present and past, for
enabling myself to create my own world and live undisturbed in it. And I
would like to acknowledge my gratitude to Argonne Lab and to the
U.S. Department of Energy for the years of faithful support of my database
research.

Minor updates to this package were made by Bruno Wolff III
bruno@wolff.to in August/September of 2002. These include
changing the precision from single precision to double precision and adding
some new functions.

Additional updates were made by Joshua Reich josh@root.net in
July 2006. These include `cube(float8[], float8[])` and
cleaning up the code to use the V1 call protocol instead of the deprecated
V0 protocol.

## dblink — connect to other PostgreSQL databases

`dblink` is a module that supports connections to
other PostgreSQL databases from within a database
session.

See also [postgres-fdw](#postgres-fdw), which provides roughly the same
functionality using a more modern and standards-compliant infrastructure.

dblink_connect
3

dblink_connect
opens a persistent connection to a remote database

```
dblink_connect(text connstr) returns text
dblink_connect(text connname, text connstr) returns text
```

## Description

`dblink_connect()` establishes a connection to a remote
PostgreSQL database.  The server and database to
be contacted are identified through a standard libpq
connection string.  Optionally, a name can be assigned to the
connection.  Multiple named connections can be open at once, but
only one unnamed connection is permitted at a time.  The connection
will persist until closed or until the database session is ended.

The connection string may also be the name of an existing foreign
server.  It is recommended to use the foreign-data wrapper
`dblink_fdw` when defining the foreign
server.  See the example below, as well as
[sql-createserver](#sql-createserver) and
[sql-createusermapping](#sql-createusermapping).

## Arguments

**connname**
: The name to use for this connection; if omitted, an unnamed
connection is opened, replacing any existing unnamed connection.

**connstr**
: libpq-style connection info string, for example
`hostaddr=127.0.0.1 port=5432 dbname=mydb user=postgres
password=mypasswd options=-csearch_path=`.
For details see [libpq-connstring](#libpq-connstring).
Alternatively, the name of a foreign server.

## Return Value

Returns status, which is always `OK` (since any error
causes the function to throw an error instead of returning).

## Notes

If untrusted users have access to a database that has not adopted a
[secure schema usage pattern](#ddl-schemas-patterns),
begin each session by removing publicly-writable schemas from
`search_path`.  One could, for example,
add `options=-csearch_path=` to

connstr.  This consideration is not specific
to `dblink`; it applies to every interface for
executing arbitrary SQL commands.

Only superusers may use `dblink_connect` to create
non-password-authenticated and non-GSSAPI-authenticated connections.
If non-superusers need this capability, use
`dblink_connect_u` instead.

It is unwise to choose connection names that contain equal signs,
as this opens a risk of confusion with connection info strings
in other `dblink` functions.

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

## Description

`dblink_connect_u()` is identical to
`dblink_connect()`, except that it will allow non-superusers
to connect using any authentication method.

If the remote server selects an authentication method that does not
involve a password, then impersonation and subsequent escalation of
privileges can occur, because the session will appear to have
originated from the user as which the local PostgreSQL
server runs.  Also, even if the remote server does demand a password,
it is possible for the password to be supplied from the server
environment, such as a `~/.pgpass` file belonging to the
server's user.  This opens not only a risk of impersonation, but the
possibility of exposing a password to an untrustworthy remote server.
Therefore, `dblink_connect_u()` is initially
installed with all privileges revoked from `PUBLIC`,
making it un-callable except by superusers.  In some situations
it may be appropriate to grant `EXECUTE` permission for
`dblink_connect_u()` to specific users who are considered
trustworthy, but this should be done with care.  It is also recommended
that any `~/.pgpass` file belonging to the server's user
*not* contain any records specifying a wildcard host name.

For further details see `dblink_connect()`.

dblink_disconnect
3

dblink_disconnect
closes a persistent connection to a remote database

```
dblink_disconnect() returns text
dblink_disconnect(text connname) returns text
```

## Description

`dblink_disconnect()` closes a connection previously opened
by `dblink_connect()`.  The form with no arguments closes
an unnamed connection.

## Arguments

**connname**
: The name of a named connection to be closed.

## Return Value

Returns status, which is always `OK` (since any error
causes the function to throw an error instead of returning).

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

## Description

`dblink` executes a query (usually a `SELECT`,
but it can be any SQL statement that returns rows) in a remote database.

When two `text` arguments are given, the first one is first
looked up as a persistent connection's name; if found, the command
is executed on that connection.  If not found, the first argument
is treated as a connection info string as for `dblink_connect`,
and the indicated connection is made just for the duration of this command.

## Arguments

**connname**
: Name of the connection to use; omit this parameter to use the
unnamed connection.

**connstr**
: A connection info string, as previously described for
`dblink_connect`.

**sql**
: The SQL query that you wish to execute in the remote database,
for example `select * from foo`.

**fail_on_error**
: If true (the default when omitted) then an error thrown on the
remote side of the connection causes an error to also be thrown
locally. If false, the remote error is locally reported as a NOTICE,
and the function returns no rows.

## Return Value

The function returns the row(s) produced by the query.  Since
`dblink` can be used with any query, it is declared
to return `record`, rather than specifying any particular
set of columns.  This means that you must specify the expected
set of columns in the calling query — otherwise
PostgreSQL would not know what to expect.
Here is an example:

```
SELECT *
FROM dblink('dbname=mydb options=-csearch_path=',
'select proname, prosrc from pg_proc')
AS t1(proname name, prosrc text)
WHERE proname LIKE 'bytea%';
```

The "alias" part of the `FROM` clause must
specify the column names and types that the function will return.
(Specifying column names in an alias is actually standard SQL
syntax, but specifying column types is a PostgreSQL
extension.)  This allows the system to understand what
`*` should expand to, and what `proname`
in the `WHERE` clause refers to, in advance of trying
to execute the function.  At run time, an error will be thrown
if the actual query result from the remote database does not
have the same number of columns shown in the `FROM` clause.
The column names need not match, however, and `dblink`
does not insist on exact type matches either.  It will succeed
so long as the returned data strings are valid input for the
column type declared in the `FROM` clause.

## Notes

A convenient way to use `dblink` with predetermined
queries is to create a view.
This allows the column type information to be buried in the view,
instead of having to spell it out in every query.  For example,

```
CREATE VIEW myremote_pg_proc AS
SELECT *
FROM dblink('dbname=postgres options=-csearch_path=',
'select proname, prosrc from pg_proc')
AS t1(proname name, prosrc text);

SELECT * FROM myremote_pg_proc WHERE proname LIKE 'bytea%';
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

## Description

`dblink_exec` executes a command (that is, any SQL statement
that doesn't return rows) in a remote database.

When two `text` arguments are given, the first one is first
looked up as a persistent connection's name; if found, the command
is executed on that connection.  If not found, the first argument
is treated as a connection info string as for `dblink_connect`,
and the indicated connection is made just for the duration of this command.

## Arguments

**connname**
: Name of the connection to use; omit this parameter to use the
unnamed connection.

**connstr**
: A connection info string, as previously described for
`dblink_connect`.

**sql**
: The SQL command that you wish to execute in the remote database,
for example
`insert into foo values(0, 'a', '{"a0","b0","c0"}')`.

**fail_on_error**
: If true (the default when omitted) then an error thrown on the
remote side of the connection causes an error to also be thrown
locally. If false, the remote error is locally reported as a NOTICE,
and the function's return value is set to `ERROR`.

## Return Value

Returns status, either the command's status string or `ERROR`.

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

## Description

`dblink_open()` opens a cursor in a remote database.
The cursor can subsequently be manipulated with
`dblink_fetch()` and `dblink_close()`.

## Arguments

**connname**
: Name of the connection to use; omit this parameter to use the
unnamed connection.

**cursorname**
: The name to assign to this cursor.

**sql**
: The `SELECT` statement that you wish to execute in the remote
database, for example `select * from pg_class`.

**fail_on_error**
: If true (the default when omitted) then an error thrown on the
remote side of the connection causes an error to also be thrown
locally. If false, the remote error is locally reported as a NOTICE,
and the function's return value is set to `ERROR`.

## Return Value

Returns status, either `OK` or `ERROR`.

## Notes

Since a cursor can only persist within a transaction,
`dblink_open` starts an explicit transaction block
(`BEGIN`) on the remote side, if the remote side was
not already within a transaction.  This transaction will be
closed again when the matching `dblink_close` is
executed.  Note that if
you use `dblink_exec` to change data between
`dblink_open` and `dblink_close`,
and then an error occurs or you use `dblink_disconnect` before
`dblink_close`, your change *will be
lost* because the transaction will be aborted.

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

## Description

`dblink_fetch` fetches rows from a cursor previously
established by `dblink_open`.

## Arguments

**connname**
: Name of the connection to use; omit this parameter to use the
unnamed connection.

**cursorname**
: The name of the cursor to fetch from.

**howmany**
: The maximum number of rows to retrieve. The next howmany
rows are fetched, starting at the current cursor position, moving
forward. Once the cursor has reached its end, no more rows are produced.

**fail_on_error**
: If true (the default when omitted) then an error thrown on the
remote side of the connection causes an error to also be thrown
locally. If false, the remote error is locally reported as a NOTICE,
and the function returns no rows.

## Return Value

The function returns the row(s) fetched from the cursor.  To use this
function, you will need to specify the expected set of columns,
as previously discussed for `dblink`.

## Notes

On a mismatch between the number of return columns specified in the
`FROM` clause, and the actual number of columns returned by the
remote cursor, an error will be thrown. In this event, the remote cursor
is still advanced by as many rows as it would have been if the error had
not occurred.  The same is true for any other error occurring in the local
query after the remote `FETCH` has been done.

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

## Description

`dblink_close` closes a cursor previously opened with
`dblink_open`.

## Arguments

**connname**
: Name of the connection to use; omit this parameter to use the
unnamed connection.

**cursorname**
: The name of the cursor to close.

**fail_on_error**
: If true (the default when omitted) then an error thrown on the
remote side of the connection causes an error to also be thrown
locally. If false, the remote error is locally reported as a NOTICE,
and the function's return value is set to `ERROR`.

## Return Value

Returns status, either `OK` or `ERROR`.

## Notes

If `dblink_open` started an explicit transaction block,
and this is the last remaining open cursor in this connection,
`dblink_close` will issue the matching `COMMIT`.

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

## Description

`dblink_get_connections` returns an array of the names
of all open named `dblink` connections.

## Return Value

Returns a text array of connection names, or NULL if none.

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

## Description

`dblink_error_message` fetches the most recent remote
error message for a given connection.

## Arguments

**connname**
: Name of the connection to use.

## Return Value

Returns last error message, or `OK` if there has been
no error in this connection.

## Notes

When asynchronous queries are initiated by
`dblink_send_query`, the error message associated with
the connection might not get updated until the server's response message
is consumed. This typically means that `dblink_is_busy`
or `dblink_get_result` should be called prior to
`dblink_error_message`, so that any error generated by
the asynchronous query will be visible.

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

## Description

`dblink_send_query` sends a query to be executed
asynchronously, that is, without immediately waiting for the result.
There must not be an async query already in progress on the
connection.

After successfully dispatching an async query, completion status
can be checked with `dblink_is_busy`, and the results
are ultimately collected with `dblink_get_result`.
It is also possible to attempt to cancel an active async query
using `dblink_cancel_query`.

## Arguments

**connname**
: Name of the connection to use.

**sql**
: The SQL statement that you wish to execute in the remote database,
for example `select * from pg_class`.

## Return Value

Returns 1 if the query was successfully dispatched, 0 otherwise.

## Examples

```
SELECT dblink_send_query('dtest1', 'SELECT * FROM foo WHERE f1 3

dblink_is_busy
checks if connection is busy with an async query

```
dblink_is_busy(text connname) returns int
```

## Description

`dblink_is_busy` tests whether an async query is in progress.

## Arguments

**connname**
: Name of the connection to check.

## Return Value

Returns 1 if connection is busy, 0 if it is not busy.
If this function returns 0, it is guaranteed that
`dblink_get_result` will not block.

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

## Description

`dblink_get_notify` retrieves notifications on either
the unnamed connection, or on a named connection if specified.
To receive notifications via dblink, `LISTEN` must
first be issued, using `dblink_exec`.
For details see [sql-listen](#sql-listen) and [sql-notify](#sql-notify).

## Arguments

**connname**
: The name of a named connection to get notifications on.

## Return Value

Returns `setof (notify_name text, be_pid int, extra text)`, or an empty set if none.

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

## Description

`dblink_get_result` collects the results of an
asynchronous query previously sent with `dblink_send_query`.
If the query is not already completed, `dblink_get_result`
will wait until it is.

## Arguments

**connname**
: Name of the connection to use.

**fail_on_error**
: If true (the default when omitted) then an error thrown on the
remote side of the connection causes an error to also be thrown
locally. If false, the remote error is locally reported as a NOTICE,
and the function returns no rows.

## Return Value

For an async query (that is, an SQL statement returning rows),
the function returns the row(s) produced by the query.  To use this
function, you will need to specify the expected set of columns,
as previously discussed for `dblink`.

For an async command (that is, an SQL statement not returning rows),
the function returns a single row with a single text column containing
the command's status string.  It is still necessary to specify that
the result will have a single text column in the calling `FROM`
clause.

## Notes

This function *must* be called if
`dblink_send_query` returned 1.
It must be called once for each query
sent, and one additional time to obtain an empty set result,
before the connection can be used again.

When using `dblink_send_query` and
`dblink_get_result`, dblink fetches the entire
remote query result before returning any of it to the local query
processor.  If the query returns a large number of rows, this can result
in transient memory bloat in the local session.  It may be better to open
such a query as a cursor with `dblink_open` and then fetch a
manageable number of rows at a time.  Alternatively, use plain
`dblink()`, which avoids memory bloat by spooling large result
sets to disk.

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

## Description

`dblink_cancel_query` attempts to cancel any query that
is in progress on the named connection.  Note that this is not
certain to succeed (since, for example, the remote query might
already have finished).  A cancel request simply improves the
odds that the query will fail soon.  You must still complete the
normal query protocol, for example by calling
`dblink_get_result`.

## Arguments

**connname**
: Name of the connection to use.

## Return Value

Returns `OK` if the cancel request has been sent, or
the text of an error message on failure.

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

## Description

`dblink_get_pkey` provides information about the primary
key of a relation in the local database.  This is sometimes useful
in generating queries to be sent to remote databases.

## Arguments

**relname**
: Name of a local relation, for example `foo` or
`myschema.mytab`.  Include double quotes if the
name is mixed-case or contains special characters, for
example `"FooBar"`; without quotes, the string
will be folded to lower case.

## Return Value

Returns one row for each primary key field, or no rows if the relation
has no primary key.  The result row type is defined as

```
CREATE TYPE dblink_pkey_results AS (position int, colname text);
```

The `position` column simply runs from 1 to `N`;
it is the number of the field within the primary key, not the number
within the table's columns.

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

## Description

`dblink_build_sql_insert` can be useful in doing selective
replication of a local table to a remote database.  It selects a row
from the local table based on primary key, and then builds an SQL
`INSERT` command that will duplicate that row, but with
the primary key values replaced by the values in the last argument.
(To make an exact copy of the row, just specify the same values for
the last two arguments.)

## Arguments

**relname**
: Name of a local relation, for example `foo` or
`myschema.mytab`.  Include double quotes if the
name is mixed-case or contains special characters, for
example `"FooBar"`; without quotes, the string
will be folded to lower case.

**primary_key_attnums**
: Attribute numbers (1-based) of the primary key fields,
for example `1 2`.

**num_primary_key_atts**
: The number of primary key fields.

**src_pk_att_vals_array**
: Values of the primary key fields to be used to look up the
local tuple.  Each field is represented in text form.
An error is thrown if there is no local row with these
primary key values.

**tgt_pk_att_vals_array**
: Values of the primary key fields to be placed in the resulting
`INSERT` command.  Each field is represented in text form.

## Return Value

Returns the requested SQL statement as text.

## Notes

As of PostgreSQL 9.0, the attribute numbers in

primary_key_attnums are interpreted as logical
column numbers, corresponding to the column's position in
`SELECT * FROM relname`.  Previous versions interpreted the
numbers as physical column positions.  There is a difference if any
column(s) to the left of the indicated column have been dropped during
the lifetime of the table.

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

## Description

`dblink_build_sql_delete` can be useful in doing selective
replication of a local table to a remote database.  It builds an SQL
`DELETE` command that will delete the row with the given
primary key values.

## Arguments

**relname**
: Name of a local relation, for example `foo` or
`myschema.mytab`.  Include double quotes if the
name is mixed-case or contains special characters, for
example `"FooBar"`; without quotes, the string
will be folded to lower case.

**primary_key_attnums**
: Attribute numbers (1-based) of the primary key fields,
for example `1 2`.

**num_primary_key_atts**
: The number of primary key fields.

**tgt_pk_att_vals_array**
: Values of the primary key fields to be used in the resulting
`DELETE` command.  Each field is represented in text form.

## Return Value

Returns the requested SQL statement as text.

## Notes

As of PostgreSQL 9.0, the attribute numbers in

primary_key_attnums are interpreted as logical
column numbers, corresponding to the column's position in
`SELECT * FROM relname`.  Previous versions interpreted the
numbers as physical column positions.  There is a difference if any
column(s) to the left of the indicated column have been dropped during
the lifetime of the table.

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

## Description

`dblink_build_sql_update` can be useful in doing selective
replication of a local table to a remote database.  It selects a row
from the local table based on primary key, and then builds an SQL
`UPDATE` command that will duplicate that row, but with
the primary key values replaced by the values in the last argument.
(To make an exact copy of the row, just specify the same values for
the last two arguments.)  The `UPDATE` command always assigns
all fields of the row — the main difference between this and
`dblink_build_sql_insert` is that it's assumed that
the target row already exists in the remote table.

## Arguments

**relname**
: Name of a local relation, for example `foo` or
`myschema.mytab`.  Include double quotes if the
name is mixed-case or contains special characters, for
example `"FooBar"`; without quotes, the string
will be folded to lower case.

**primary_key_attnums**
: Attribute numbers (1-based) of the primary key fields,
for example `1 2`.

**num_primary_key_atts**
: The number of primary key fields.

**src_pk_att_vals_array**
: Values of the primary key fields to be used to look up the
local tuple.  Each field is represented in text form.
An error is thrown if there is no local row with these
primary key values.

**tgt_pk_att_vals_array**
: Values of the primary key fields to be placed in the resulting
`UPDATE` command.  Each field is represented in text form.

## Return Value

Returns the requested SQL statement as text.

## Notes

As of PostgreSQL 9.0, the attribute numbers in

primary_key_attnums are interpreted as logical
column numbers, corresponding to the column's position in
`SELECT * FROM relname`.  Previous versions interpreted the
numbers as physical column positions.  There is a difference if any
column(s) to the left of the indicated column have been dropped during
the lifetime of the table.

## Examples

```
SELECT dblink_build_sql_update('foo', '1 2', 2, '{"1", "a"}', '{"1", "b"}');
dblink_build_sql_update
-------------------------------------------------------------
UPDATE foo SET f1='1',f2='b',f3='1' WHERE f1='1' AND f2='b'
(1 row)
```

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

## earthdistance — calculate great-circle distances

The `earthdistance` module provides two different approaches to
calculating great circle distances on the surface of the Earth. The one
described first depends on the `cube` module.
The second one is based on the built-in `point` data type,
using longitude and latitude for the coordinates.

In this module, the Earth is assumed to be perfectly spherical.
(If that's too inaccurate for you, you might want to look at the
[PostGIS](https://postgis.net/)
project.)

The `cube` module must be installed
before `earthdistance` can be installed
(although you can use the `CASCADE` option
of `CREATE EXTENSION` to install both in one command).

> **Caution:**

> It is strongly recommended that `earthdistance`
> and `cube` be installed in the same schema, and that
> that schema be one for which CREATE privilege has not been and will not
> be granted to any untrusted users.
> Otherwise there are installation-time security hazards
> if `earthdistance`'s schema contains objects defined
> by a hostile user.
> Furthermore, when using `earthdistance`'s functions
> after installation, the entire search path should contain only trusted
> schemas.
>

### Cube-Based Earth Distances

Data is stored in cubes that are points (both corners are the same) using 3
coordinates representing the x, y, and z distance from the center of the
Earth.  A domain
`earth` over type `cube` is provided, which
includes constraint checks that the value meets these restrictions and
is reasonably close to the actual surface of the Earth.

The radius of the Earth is obtained from the `earth()`
function. It is given in meters. But by changing this one function you can
change the module to use some other units, or to use a different value of
the radius that you feel is more appropriate.

This package has applications to astronomical databases as well.
Astronomers will probably want to change `earth()` to return a
radius of `180/pi()` so that distances are in degrees.

Functions are provided to support input in latitude and longitude (in
degrees), to support output of latitude and longitude, to calculate
the great circle distance between two points and to easily specify a
bounding box usable for index searches.

The provided functions are shown
in [earthdistance-cube-functions](#earthdistance-cube-functions).

| Function                         Description |
| --- |
| `earth` ()         float8                         Returns the assumed radius of the Earth. |
| `sec_to_gc` ( `float8` )         float8                         Converts the normal straight line         (secant) distance between two points on the surface of the Earth         to the great circle distance between them. |
| `gc_to_sec` ( `float8` )         float8                         Converts the great circle distance between two points on the         surface of the Earth to the normal straight line (secant) distance         between them. |
| `ll_to_earth` ( `float8`, `float8` )         earth                         Returns the location of a point on the surface of the Earth given         its latitude (argument 1) and longitude (argument 2) in degrees. |
| `latitude` ( `earth` )         float8                         Returns the latitude in degrees of a point on the surface of the         Earth. |
| `longitude` ( `earth` )         float8                         Returns the longitude in degrees of a point on the surface of the         Earth. |
| `earth_distance` ( `earth`, `earth` )         float8                         Returns the great circle distance between two points on the         surface of the Earth. |
| `earth_box` ( `earth`, `float8` )         cube                         Returns a box suitable for an indexed search using the `cube`         `@>`         operator for points within a given great circle distance of a location.         Some points in this box are further than the specified great circle         distance from the location, so a second check using         `earth_distance` should be included in the query. |

### Point-Based Earth Distances

The second part of the module relies on representing Earth locations as
values of type `point`, in which the first component is taken to
represent longitude in degrees, and the second component is taken to
represent latitude in degrees.  Points are taken as (longitude, latitude)
and not vice versa because longitude is closer to the intuitive idea of
x-axis and latitude to y-axis.

A single operator is provided, shown
in [earthdistance-point-operators](#earthdistance-point-operators).

| Operator                         Description |
| --- |
| `point` `` `point`         float8                         Computes the distance in statute miles between         two points on the Earth's surface. |

Note that unlike the `cube`-based part of the module, units
are hardwired here: changing the `earth()` function will
not affect the results of this operator.

One disadvantage of the longitude/latitude representation is that
you need to be careful about the edge conditions near the poles
and near +/- 180 degrees of longitude.  The `cube`-based
representation avoids these discontinuities.

## file_fdw — access data files in the server's file system

The `file_fdw` module provides the foreign-data wrapper
`file_fdw`, which can be used to access data
files in the server's file system, or to execute programs on the server
and read their output.  The data file or program output must be in a format
that can be read by `COPY FROM`;
see [sql-copy](#sql-copy) for details.
Access to data files is currently read-only.

A foreign table created using this wrapper can have the following options:

**`filename`**
: Specifies the file to be read.  Relative paths are relative to the
data directory.
Either `filename` or `program` must be
specified, but not both.

**`program`**
: Specifies the command to be executed.  The standard output of this
command will be read as though `COPY FROM PROGRAM` were used.
Either `program` or `filename` must be
specified, but not both.

**`format`**
: Specifies the data format,
the same as `COPY`'s `FORMAT` option.

**`header`**
: Specifies whether the data has a header line,
the same as `COPY`'s `HEADER` option.

**`delimiter`**
: Specifies the data delimiter character,
the same as `COPY`'s `DELIMITER` option.

**`quote`**
: Specifies the data quote character,
the same as `COPY`'s `QUOTE` option.

**`escape`**
: Specifies the data escape character,
the same as `COPY`'s `ESCAPE` option.

**`null`**
: Specifies the data null string,
the same as `COPY`'s `NULL` option.

**`default`**
: Specifies the string that represents a default value,
the same as `COPY`'s `DEFAULT` option.

**`encoding`**
: Specifies the data encoding,
the same as `COPY`'s `ENCODING` option.

Note that while `COPY` allows options such as `HEADER`
to be specified without a corresponding value, the foreign table option
syntax requires a value to be present in all cases.  To activate
`COPY` options typically written without a value, you can pass
the value TRUE, since all such options are Booleans.

A column of a foreign table created using this wrapper can have the
following options:

**`force_not_null`**
: This is a Boolean option.  If true, it specifies that values of the
column should not be matched against the null string (that is, the
table-level `null` option).  This has the same effect
as listing the column in `COPY`'s
`FORCE_NOT_NULL` option.

**`force_null`**
: This is a Boolean option.  If true, it specifies that values of the
column which match the null string are returned as `NULL`
even if the value is quoted. Without this option, only unquoted
values matching the null string are returned as `NULL`.
This has the same effect  as listing the column in
`COPY`'s `FORCE_NULL` option.

`COPY`'s `FORCE_QUOTE` option is
currently not supported by `file_fdw`.

These options can only be specified for a foreign table or its columns, not
in the options of the `file_fdw` foreign-data wrapper, nor in the
options of a server or user mapping using the wrapper.

Changing table-level options requires being a superuser or having the privileges
of the role `pg_read_server_files` (to use a filename) or
the role `pg_execute_server_program` (to use a program),
for security reasons: only certain users should be able to control which file is
read or which program is run.  In principle regular users could be allowed to
change the other options, but that's not supported at present.

When specifying the `program` option, keep in mind that the option
string is executed by the shell.  If you need to pass any arguments to the
command that come from an untrusted source, you must be careful to strip or
escape any characters that might have special meaning to the shell.
For security reasons, it is best to use a fixed command string, or at least
avoid passing any user input in it.

For a foreign table using `file_fdw`, `EXPLAIN` shows
the name of the file to be read or program to be run.
For a file, unless `COSTS OFF` is
specified, the file size (in bytes) is shown as well.

## Create a Foreign Table for PostgreSQL CSV Logs

One of the obvious uses for `file_fdw` is to make
the PostgreSQL activity log available as a table for querying.  To
do this, first you must be [logging to a CSV file,](#runtime-config-logging-csvlog)
which here we
will call `pglog.csv`.  First, install `file_fdw`
as an extension:

```
CREATE EXTENSION file_fdw;
```

Then create a foreign server:

```
CREATE SERVER pglog FOREIGN DATA WRAPPER file_fdw;
```

Now you are ready to create the foreign data table.  Using the
`CREATE FOREIGN TABLE` command, you will need to define
the columns for the table, the CSV file name, and its format:

```
CREATE FOREIGN TABLE pglog (
log_time timestamp(3) with time zone,
user_name text,
database_name text,
process_id integer,
connection_from text,
session_id text,
session_line_num bigint,
command_tag text,
session_start_time timestamp with time zone,
virtual_transaction_id text,
transaction_id bigint,
error_severity text,
sql_state_code text,
message text,
detail text,
hint text,
internal_query text,
internal_query_pos integer,
context text,
query text,
query_pos integer,
location text,
application_name text,
backend_type text,
leader_pid integer,
query_id bigint
) SERVER pglog
OPTIONS ( filename 'log/pglog.csv', format 'csv' );
```

That's it — now you can query your log directly. In production, of
course, you would need to define some way to deal with log rotation.

## fuzzystrmatch — determine string similarities and distance

The `fuzzystrmatch` module provides several
functions to determine similarities and distance between strings.

> **Caution:**

> At present, the `soundex`, `metaphone`,
> `dmetaphone`, and `dmetaphone_alt` functions do
> not work well with multibyte encodings (such as UTF-8).
> Use `daitch_mokotoff`
> or `levenshtein` with such data.
>

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Soundex

The Soundex system is a method of matching similar-sounding names
by converting them to the same code.  It was initially used by the
United States Census in 1880, 1900, and 1910.  Note that Soundex
is not very useful for non-English names.

The `fuzzystrmatch` module provides two functions
for working with Soundex codes:

```
soundex(text) returns text
difference(text, text) returns int
```

The `soundex` function converts a string to its Soundex code.
The `difference` function converts two strings to their Soundex
codes and then reports the number of matching code positions.  Since
Soundex codes have four characters, the result ranges from zero to four,
with zero being no match and four being an exact match.  (Thus, the
function is misnamed — `similarity` would have been
a better name.)

Here are some usage examples:

```
SELECT soundex('hello world!');

SELECT soundex('Anne'), soundex('Ann'), difference('Anne', 'Ann');
SELECT soundex('Anne'), soundex('Andrew'), difference('Anne', 'Andrew');
SELECT soundex('Anne'), soundex('Margaret'), difference('Anne', 'Margaret');

CREATE TABLE s (nm text);

INSERT INTO s VALUES ('john');
INSERT INTO s VALUES ('joan');
INSERT INTO s VALUES ('wobbly');
INSERT INTO s VALUES ('jack');

SELECT * FROM s WHERE soundex(nm) = soundex('john');

SELECT * FROM s WHERE difference(s.nm, 'john') > 2;
```

### Daitch-Mokotoff Soundex

Like the original Soundex system, Daitch-Mokotoff Soundex matches
similar-sounding names by converting them to the same code.
However, Daitch-Mokotoff Soundex is significantly more useful for
non-English names than the original system.
Major improvements over the original system include:

- The code is based on the first six meaningful letters rather than four.
- A letter or combination of letters maps into ten possible codes rather
than seven.
- Where two consecutive letters have a single sound, they are coded as a
single number.
- When a letter or combination of letters may have different sounds,
multiple codes are emitted to cover all possibilities.

This function generates the Daitch-Mokotoff soundex codes for its input:

```
daitch_mokotoff(
source text) returns text[]
```

The result may contain one or more codes depending on how many plausible
pronunciations there are, so it is represented as an array.

Since a Daitch-Mokotoff soundex code consists of only 6 digits,

source should be preferably a single word or name.

Here are some examples:

```
SELECT daitch_mokotoff('George');
daitch_mokotoff
-----------------
{595000}

SELECT daitch_mokotoff('John');
daitch_mokotoff
-----------------
{160000,460000}

SELECT daitch_mokotoff('Bierschbach');
daitch_mokotoff
-----------------------------------------------------------
{794575,794574,794750,794740,745750,745740,747500,747400}

SELECT daitch_mokotoff('Schwartzenegger');
daitch_mokotoff
-----------------
{479465}
```

For matching of single names, returned text arrays can be matched
directly using the `&&` operator: any overlap
can be considered a match.  A GIN index may
be used for efficiency, see [gin](#gin) and this example:

```
CREATE TABLE s (nm text);
CREATE INDEX ix_s_dm ON s USING gin (daitch_mokotoff(nm)) WITH (fastupdate = off);

INSERT INTO s (nm) VALUES
('Schwartzenegger'),
('John'),
('James'),
('Steinman'),
('Steinmetz');

SELECT * FROM s WHERE daitch_mokotoff(nm) && daitch_mokotoff('Swartzenegger');
SELECT * FROM s WHERE daitch_mokotoff(nm) && daitch_mokotoff('Jane');
SELECT * FROM s WHERE daitch_mokotoff(nm) && daitch_mokotoff('Jens');
```

For indexing and matching of any number of names in any order, Full Text
Search features can be used. See [textsearch](#textsearch) and this
example:

```
CREATE FUNCTION soundex_tsvector(v_name text) RETURNS tsvector
BEGIN ATOMIC
SELECT to_tsvector('simple',
string_agg(array_to_string(daitch_mokotoff(n), ' '), ' '))
FROM regexp_split_to_table(v_name, '\s+') AS n;
END;

CREATE FUNCTION soundex_tsquery(v_name text) RETURNS tsquery
BEGIN ATOMIC
SELECT string_agg('(' || array_to_string(daitch_mokotoff(n), '|') || ')', '&')::tsquery
FROM regexp_split_to_table(v_name, '\s+') AS n;
END;

CREATE TABLE s (nm text);
CREATE INDEX ix_s_txt ON s USING gin (soundex_tsvector(nm)) WITH (fastupdate = off);

INSERT INTO s (nm) VALUES
('John Doe'),
('Jane Roe'),
('Public John Q.'),
('George Best'),
('John Yamson');

SELECT * FROM s WHERE soundex_tsvector(nm) @@ soundex_tsquery('john');
SELECT * FROM s WHERE soundex_tsvector(nm) @@ soundex_tsquery('jane doe');
SELECT * FROM s WHERE soundex_tsvector(nm) @@ soundex_tsquery('john public');
SELECT * FROM s WHERE soundex_tsvector(nm) @@ soundex_tsquery('besst, giorgio');
SELECT * FROM s WHERE soundex_tsvector(nm) @@ soundex_tsquery('Jameson John');
```

If it is desired to avoid recalculation of soundex codes during index
rechecks, an index on a separate column can be used instead of an index on
an expression.  A stored generated column can be used for this; see
[ddl-generated-columns](#ddl-generated-columns).

### Levenshtein

This function calculates the Levenshtein distance between two strings:

```
levenshtein(source text, target text, ins_cost int, del_cost int, sub_cost int) returns int
levenshtein(source text, target text) returns int
levenshtein_less_equal(source text, target text, ins_cost int, del_cost int, sub_cost int, max_d int) returns int
levenshtein_less_equal(source text, target text, max_d int) returns int
```

Both `source` and `target` can be any
non-null string, with a maximum of 255 characters.  The cost parameters
specify how much to charge for a character insertion, deletion, or
substitution, respectively.  You can omit the cost parameters, as in
the second version of the function; in that case they all default to 1.

`levenshtein_less_equal` is an accelerated version of the
Levenshtein function for use when only small distances are of interest.
If the actual distance is less than or equal to `max_d`,
then `levenshtein_less_equal` returns the correct
distance; otherwise it returns some value greater than `max_d`.
If `max_d` is negative then the behavior is the same as
`levenshtein`.

Examples:

```
test=# SELECT levenshtein('GUMBO', 'GAMBOL');
levenshtein
-------------
2
(1 row)

test=# SELECT levenshtein('GUMBO', 'GAMBOL', 2, 1, 1);
levenshtein
-------------
3
(1 row)

test=# SELECT levenshtein_less_equal('extensive', 'exhaustive', 2);
levenshtein_less_equal
------------------------
3
(1 row)

test=# SELECT levenshtein_less_equal('extensive', 'exhaustive', 4);
levenshtein_less_equal
------------------------
4
(1 row)
```

### Metaphone

Metaphone, like Soundex, is based on the idea of constructing a
representative code for an input string.  Two strings are then
deemed similar if they have the same codes.

This function calculates the metaphone code of an input string:

```
metaphone(source text, max_output_length int) returns text
```

`source` has to be a non-null string with a maximum of
255 characters.  `max_output_length` sets the maximum
length of the output metaphone code; if longer, the output is truncated
to this length.

Example:

```
test=# SELECT metaphone('GUMBO', 4);
metaphone
-----------
KM
(1 row)
```

### Double Metaphone

The Double Metaphone system computes two "sounds like" strings
for a given input string — a "primary" and an
"alternate".  In most cases they are the same, but for non-English
names especially they can be a bit different, depending on pronunciation.
These functions compute the primary and alternate codes:

```
dmetaphone(source text) returns text
dmetaphone_alt(source text) returns text
```

There is no length limit on the input strings.

Example:

```
test=# SELECT dmetaphone('gumbo');
dmetaphone
------------
KMP
(1 row)
```

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

## intagg — integer aggregator and enumerator

The `intagg` module provides an integer aggregator and an
enumerator.  `intagg` is now obsolete, because there
are built-in functions that provide a superset of its capabilities.
However, the module is still provided as a compatibility wrapper around
the built-in functions.

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

### Sample Uses

Many database systems have the notion of a one to many table. Such a table
usually sits between two indexed tables, for example:

```
CREATE TABLE left (id INT PRIMARY KEY, ...);
CREATE TABLE right (id INT PRIMARY KEY, ...);
CREATE TABLE one_to_many(left INT REFERENCES left, right INT REFERENCES right);
```

It is typically used like this:

```
SELECT right.* from right JOIN one_to_many ON (right.id = one_to_many.right)
WHERE one_to_many.left = `item`;
```

This will return all the items in the right hand table for an entry
in the left hand table. This is a very common construct in SQL.

Now, this methodology can be cumbersome with a very large number of
entries in the `one_to_many` table.  Often,
a join like this would result in an index scan
and a fetch for each right hand entry in the table for a particular
left hand entry. If you have a very dynamic system, there is not much you
can do. However, if you have some data which is fairly static, you can
create a summary table with the aggregator.

```
CREATE TABLE summary AS
SELECT left, int_array_aggregate(right) AS right
FROM one_to_many
GROUP BY left;
```

This will create a table with one row per left item, and an array
of right items. Now this is pretty useless without some way of using
the array; that's why there is an array enumerator.  You can do

```
SELECT left, int_array_enum(right) FROM summary WHERE left = `item`;
```

The above query using `int_array_enum` produces the same results
as

```
SELECT left, right FROM one_to_many WHERE left = `item`;
```

The difference is that the query against the summary table has to get
only one row from the table, whereas the direct query against
`one_to_many` must index scan and fetch a row for each entry.

On one system, an `EXPLAIN` showed a query with a cost of 8488 was
reduced to a cost of 329.  The original query was a join involving the
`one_to_many` table, which was replaced by:

```
SELECT right, count(right) FROM
( SELECT left, int_array_enum(right) AS right
FROM summary JOIN (SELECT left FROM left_table WHERE left = `item`) AS lefts
ON (summary.left = lefts.left)
) AS list
GROUP BY right
ORDER BY count DESC;
```

## intarray — manipulate arrays of integers

The `intarray` module provides a number of useful functions
and operators for manipulating null-free arrays of integers.
There is also support for indexed searches using some of the operators.

All of these operations will throw an error if a supplied array contains any
NULL elements.

Many of these operations are only sensible for one-dimensional arrays.
Although they will accept input arrays of more dimensions, the data is
treated as though it were a linear array in storage order.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

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

### Benchmark

The source directory `contrib/intarray/bench` contains a
benchmark test suite, which can be run against an installed
PostgreSQL server.  (It also requires `DBD::Pg`
to be installed.)  To run:

```
cd .../contrib/intarray/bench
createdb TEST
psql -c "CREATE EXTENSION intarray" TEST
./create_test.pl | psql TEST
./bench.pl
```

The `bench.pl` script has numerous options, which
are displayed when it is run without any arguments.

### Authors

All work was done by Teodor Sigaev (teodor@sigaev.ru) and
Oleg Bartunov (oleg@sai.msu.su). See
[](http://www.sai.msu.su/~megera/postgres/gist/) for
additional information. Andrey Oktyabrski did a great work on adding new
functions and operations.

## isn — data types for international standard numbers (ISBN, EAN, UPC, etc.)

The `isn` module provides data types for the following
international product numbering standards: EAN13, UPC, ISBN (books), ISMN
(music), and ISSN (serials).  Numbers are validated on input according to a
hard-coded list of prefixes; this list of prefixes is also used to hyphenate
numbers on output.  Since new prefixes are assigned from time to time, the
list of prefixes may be out of date.  It is hoped that a future version of
this module will obtain the prefix list from one or more tables that
can be easily updated by users as needed; however, at present, the
list can only be updated by modifying the source code and recompiling.
Alternatively, prefix validation and hyphenation support may be
dropped from a future version of this module.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Data Types

[isn-datatypes](#isn-datatypes) shows the data types provided by
the `isn` module.

| Data Type | Description |
| --- | --- |
| `EAN13` | European Article Numbers, always displayed in the EAN13 display format |
| `ISBN13` | International Standard Book Numbers to be displayed in        the new EAN13 display format |
| `ISMN13` | International Standard Music Numbers to be displayed in        the new EAN13 display format |
| `ISSN13` | International Standard Serial Numbers to be displayed in the new        EAN13 display format |
| `ISBN` | International Standard Book Numbers to be displayed in the old        short display format |
| `ISMN` | International Standard Music Numbers to be displayed in the        old short display format |
| `ISSN` | International Standard Serial Numbers to be displayed in the        old short display format |
| `UPC` | Universal Product Codes |

Some notes:

1. ISBN13, ISMN13, ISSN13 numbers are all EAN13 numbers.
2. EAN13 numbers aren't always ISBN13, ISMN13 or ISSN13 (some
are).
3. Some ISBN13 numbers can be displayed as ISBN.
4. Some ISMN13 numbers can be displayed as ISMN.
5. Some ISSN13 numbers can be displayed as ISSN.
6. UPC numbers are a subset of the EAN13 numbers (they are basically
EAN13 without the first `0` digit).
7. All UPC, ISBN, ISMN and ISSN numbers can be represented as EAN13
numbers.

Internally, all these types use the same representation (a 64-bit
integer), and all are interchangeable.  Multiple types are provided
to control display formatting and to permit tighter validity checking
of input that is supposed to denote one particular type of number.

The `ISBN`, `ISMN`, and `ISSN` types will display the
short version of the number (ISxN 10) whenever it's possible, and will show
ISxN 13 format for numbers that do not fit in the short version.
The `EAN13`, `ISBN13`, `ISMN13` and
`ISSN13` types will always display the long version of the ISxN
(EAN13).

### Casts

The `isn` module provides the following pairs of type casts:

- ISBN13  EAN13
- ISMN13  EAN13
- ISSN13  EAN13
- ISBN  EAN13
- ISMN  EAN13
- ISSN  EAN13
- UPC   EAN13
- ISBN  ISBN13
- ISMN  ISMN13
- ISSN  ISSN13

When casting from `EAN13` to another type, there is a run-time
check that the value is within the domain of the other type, and an error
is thrown if not.  The other casts are simply relabelings that will
always succeed.

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

### Bibliography

The information to implement this module was collected from
several sites, including:

- [](https://www.isbn-international.org/)
- [](https://www.issn.org/)
- [](https://www.ismn-international.org/)
- [](https://www.wikipedia.org/)

The prefixes used for hyphenation were also compiled from:

- [](https://www.gs1.org/standards/id-keys)
- [](https://en.wikipedia.org/wiki/List_of_ISBN_identifier_groups)
- [](https://www.isbn-international.org/content/isbn-users-manual/29)
- [](https://en.wikipedia.org/wiki/International_Standard_Music_Number)
- [](https://www.ismn-international.org/ranges/tools)

Care was taken during the creation of the algorithms and they
were meticulously verified against the suggested algorithms
in the official ISBN, ISMN, ISSN User Manuals.

### Author

Germn Mndez Bravo (Kronuz), 2004–2006

This module was inspired by Garrett A. Wollman's
`isbn_issn` code.

## lo — manage large objects

The `lo` module provides support for managing Large Objects
(also called LOs or BLOBs).  This includes a data type `lo`
and a trigger `lo_manage`.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Rationale

One of the problems with the JDBC driver (and this affects the ODBC driver
also), is that the specification assumes that references to BLOBs (Binary
Large OBjects) are stored within a table, and if that entry is changed, the
associated BLOB is deleted from the database.

As PostgreSQL stands, this doesn't occur.  Large objects
are treated as objects in their own right; a table entry can reference a
large object by OID, but there can be multiple table entries referencing
the same large object OID, so the system doesn't delete the large object
just because you change or remove one such entry.

Now this is fine for PostgreSQL-specific applications, but
standard code using JDBC or ODBC won't delete the objects, resulting in
orphan objects — objects that are not referenced by anything, and
simply occupy disk space.

The `lo` module allows fixing this by attaching a trigger
to tables that contain LO reference columns.  The trigger essentially just
does a `lo_unlink` whenever you delete or modify a value
referencing a large object.  When you use this trigger, you are assuming
that there is only one database reference to any large object that is
referenced in a trigger-controlled column!

The module also provides a data type `lo`, which is really just
a domain over
the `oid` type.  This is useful for differentiating
database columns that hold large object references from those that are
OIDs of other things.  You don't have to use the `lo` type to
use the trigger, but it may be convenient to use it to keep track of which
columns in your database represent large objects that you are managing with
the trigger.  It is also rumored that the ODBC driver gets confused if you
don't use `lo` for BLOB columns.

### How to Use It

Here's a simple example of usage:

```
CREATE TABLE image (title text, raster lo);

CREATE TRIGGER t_raster BEFORE UPDATE OR DELETE ON image
FOR EACH ROW EXECUTE FUNCTION lo_manage(raster);
```

For each column that will contain unique references to large objects,
create a `BEFORE UPDATE OR DELETE` trigger, and give the column
name as the sole trigger argument.  You can also restrict the trigger
to only execute on updates to the column by using `BEFORE UPDATE
OF` `column_name`.
If you need multiple `lo`
columns in the same table, create a separate trigger for each one,
remembering to give a different name to each trigger on the same table.

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

### Author

Peter Mount peter@retep.org.uk

## ltree — hierarchical tree-like data type

This module implements a data type `ltree` for representing
labels of data stored in a hierarchical tree-like structure.
Extensive facilities for searching through label trees are provided.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Definitions

A *label* is a sequence of alphanumeric characters,
underscores, and hyphens. Valid alphanumeric character ranges are
dependent on the database locale. For example, in C locale, the characters
`A-Za-z0-9_-` are allowed.
Labels must be no more than 1000 characters long.

Examples: `42`, `Personal_Services`

A *label path* is a sequence of zero or more
labels separated by dots, for example `L1.L2.L3`, representing
a path from the root of a hierarchical tree to a particular node.  The
length of a label path cannot exceed 65535 labels.

Example: `Top.Countries.Europe.Russia`

The `ltree` module provides several data types:

- `ltree` stores a label path.
- `lquery` represents a regular-expression-like pattern
for matching `ltree` values.  A simple word matches that
label within a path.  A star symbol (`*`) matches zero
or more labels.  These can be joined with dots to form a pattern that
must match the whole label path.  For example:

```
foo         Match the exact label path `foo`
*.foo.*     Match any label path containing the label `foo`
*.foo       Match any label path whose last label is `foo`
```

Both star symbols and simple words can be quantified to restrict how many
labels they can match:

```
*{`n`}        Match exactly `n` labels
*{`n`,}       Match at least `n` labels
*{`n`,`m`}      Match at least `n` but not more than `m` labels
*{,`m`}       Match at most `m` labels — same as *{0,`m`}
foo{`n`,`m`}    Match at least `n` but not more than `m` occurrences of `foo`
foo{,}      Match any number of occurrences of `foo`, including zero
```

In the absence of any explicit quantifier, the default for a star symbol
is to match any number of labels (that is, `{,}`) while
the default for a non-star item is to match exactly once (that
is, `{1}`).

There are several modifiers that can be put at the end of a non-star
`lquery` item to make it match more than just the exact match:

```
@           Match case-insensitively, for example `a@` matches `A`
*           Match any label with this prefix, for example `foo*` matches `foobar`
%           Match initial underscore-separated words
```

The behavior of `%` is a bit complicated.  It tries to match
words rather than the entire label.  For example
`foo_bar%` matches `foo_bar_baz` but not
`foo_barbaz`.  If combined with `*`, prefix
matching applies to each word separately, for example
`foo_bar%*` matches `foo1_bar2_baz` but
not `foo1_br2_baz`.

Also, you can write several possibly-modified non-star items separated with
`|` (OR) to match any of those items, and you can put
`!` (NOT) at the start of a non-star group to match any
label that doesn't match any of the alternatives.  A quantifier, if any,
goes at the end of the group; it means some number of matches for the
group as a whole (that is, some number of labels matching or not matching
any of the alternatives).

Here's an annotated example of `lquery`:

```
Top.*{0,2}.sport*@.!football|tennis{1,}.Russ*|Spain
a.  b.     c.      d.                   e.
```

This query will match any label path that:

begins with the label `Top`
- and next has zero to two labels before
- a label beginning with the case-insensitive prefix `sport`
- then has one or more labels, none of which
match `football` nor `tennis`
- and then ends with a label beginning with `Russ` or
exactly matching `Spain`.
- `ltxtquery` represents a full-text-search-like
pattern for matching `ltree` values.  An
`ltxtquery` value contains words, possibly with the
modifiers `@`, `*`, `%` at the end;
the modifiers have the same meanings as in `lquery`.
Words can be combined with `&` (AND),
`|` (OR), `!` (NOT), and parentheses.
The key difference from
`lquery` is that `ltxtquery` matches words without
regard to their position in the label path.

Here's an example `ltxtquery`:

```
Europe & Russia*@ & !Transportation
```

This will match paths that contain the label `Europe` and
any label beginning with `Russia` (case-insensitive),
but not paths containing the label `Transportation`.
The location of these words within the path is not important.
Also, when `%` is used, the word can be matched to any
underscore-separated word within a label, regardless of position.

Note: `ltxtquery` allows whitespace between symbols, but
`ltree` and `lquery` do not.

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

### Example

This example uses the following data (also available in file
`contrib/ltree/ltreetest.sql` in the source distribution):

```
CREATE TABLE test (path ltree);
INSERT INTO test VALUES ('Top');
INSERT INTO test VALUES ('Top.Science');
INSERT INTO test VALUES ('Top.Science.Astronomy');
INSERT INTO test VALUES ('Top.Science.Astronomy.Astrophysics');
INSERT INTO test VALUES ('Top.Science.Astronomy.Cosmology');
INSERT INTO test VALUES ('Top.Hobbies');
INSERT INTO test VALUES ('Top.Hobbies.Amateurs_Astronomy');
INSERT INTO test VALUES ('Top.Collections');
INSERT INTO test VALUES ('Top.Collections.Pictures');
INSERT INTO test VALUES ('Top.Collections.Pictures.Astronomy');
INSERT INTO test VALUES ('Top.Collections.Pictures.Astronomy.Stars');
INSERT INTO test VALUES ('Top.Collections.Pictures.Astronomy.Galaxies');
INSERT INTO test VALUES ('Top.Collections.Pictures.Astronomy.Astronauts');
CREATE INDEX path_gist_idx ON test USING GIST (path);
CREATE INDEX path_idx ON test USING BTREE (path);
```

Now, we have a table `test` populated with data describing
the hierarchy shown below:

```
Top
/   |  \
Science Hobbies Collections
/       |              \
Astronomy   Amateurs_Astronomy Pictures
/  \                            |
Astrophysics  Cosmology                Astronomy
/  |    \
Galaxies Stars Astronauts
```

We can do inheritance:

```
ltreetest=> SELECT path FROM test WHERE path  SELECT path FROM test WHERE path ~ '*.Astronomy.*';
path
-----------------------------------------------
Top.Science.Astronomy
Top.Science.Astronomy.Astrophysics
Top.Science.Astronomy.Cosmology
Top.Collections.Pictures.Astronomy
Top.Collections.Pictures.Astronomy.Stars
Top.Collections.Pictures.Astronomy.Galaxies
Top.Collections.Pictures.Astronomy.Astronauts
(7 rows)

ltreetest=> SELECT path FROM test WHERE path ~ '*.!pictures@.Astronomy.*';
path
------------------------------------
Top.Science.Astronomy
Top.Science.Astronomy.Astrophysics
Top.Science.Astronomy.Cosmology
(3 rows)
```

Here are some examples of full text search:

```
ltreetest=> SELECT path FROM test WHERE path @ 'Astro*% & !pictures@';
path
------------------------------------
Top.Science.Astronomy
Top.Science.Astronomy.Astrophysics
Top.Science.Astronomy.Cosmology
Top.Hobbies.Amateurs_Astronomy
(4 rows)

ltreetest=> SELECT path FROM test WHERE path @ 'Astro* & !pictures@';
path
------------------------------------
Top.Science.Astronomy
Top.Science.Astronomy.Astrophysics
Top.Science.Astronomy.Cosmology
(3 rows)
```

Path construction using functions:

```
ltreetest=> SELECT subpath(path,0,2)||'Space'||subpath(path,2) FROM test WHERE path  SELECT ins_label(path,2,'Space') FROM test WHERE path  **Caution:**

> It is strongly recommended that the transform extension be installed in
> the same schema as `ltree`.  Otherwise there are
> installation-time security hazards if a transform extension's schema
> contains objects defined by a hostile user.
>

### Authors

All work was done by Teodor Sigaev (teodor@stack.net) and
Oleg Bartunov (oleg@sai.msu.su). See
[](http://www.sai.msu.su/~megera/postgres/gist/) for
additional information. Authors would like to thank Eugeny Rodichev for
helpful discussions. Comments and bug reports are welcome.

## old_snapshot — inspect `old_snapshot_threshold` state

The `old_snapshot` module allows inspection
of the server state that is used to implement
[guc-old-snapshot-threshold](#guc-old-snapshot-threshold).

### Functions

**`pg_old_snapshot_time_mapping(array_offset OUT int4, end_timestamp OUT timestamptz, newest_xmin OUT xid) returns setof record`**
: Returns all of the entries in the server's timestamp to XID mapping.
Each entry represents the newest xmin of any snapshot taken in the
corresponding minute.

## pageinspect — low-level inspection of database pages

The `pageinspect` module provides functions that allow you to
inspect the contents of database pages at a low level, which is useful for
debugging purposes.  All of these functions may be used only by superusers.

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

## passwordcheck — verify password strength

The `passwordcheck` module checks users' passwords
whenever they are set with
[sql-createrole](#sql-createrole) or
[sql-alterrole](#sql-alterrole).
If a password is considered too weak, it will be rejected and
the command will terminate with an error.

To enable this module, add `'$libdir/passwordcheck'`
to [guc-shared-preload-libraries](#guc-shared-preload-libraries) in
`postgresql.conf`, then restart the server.

You can adapt this module to your needs by changing the source code.
For example, you can use
[CrackLib](https://github.com/cracklib/cracklib)
to check passwords — this only requires uncommenting
two lines in the `Makefile` and rebuilding the
module.  (We cannot include CrackLib
by default for license reasons.)
Without CrackLib, the module enforces a few
simple rules for password strength, which you can modify or extend
as you see fit.

> **Caution:**

> To prevent unencrypted passwords from being sent across the network,
> written to the server log or otherwise stolen by a database administrator,
> PostgreSQL allows the user to supply
> pre-encrypted passwords. Many client programs make use of this
> functionality and encrypt the password before sending it to the server.
>

>

> This limits the usefulness of the `passwordcheck`
> module, because in that case it can only try to guess the password.
> For this reason, `passwordcheck` is not
> recommended if your security requirements are high.
> It is more secure to use an external authentication method such as GSSAPI
> (see [client-authentication](#client-authentication)) than to rely on
> passwords within the database.
>

>

> Alternatively, you could modify `passwordcheck`
> to reject pre-encrypted passwords, but forcing users to set their
> passwords in clear text carries its own security risks.
>

## pg_buffercache — inspect PostgreSQL
buffer cache state

The `pg_buffercache` module provides a means for
examining what's happening in the shared buffer cache in real time.

This module provides the `pg_buffercache_pages()`
function (wrapped in the `pg_buffercache` view),
the `pg_buffercache_summary()` function, and the
`pg_buffercache_usage_counts()` function.

The `pg_buffercache_pages()` function returns a set of
records, each row describing the state of one shared buffer entry. The
`pg_buffercache` view wraps the function for
convenient use.

The `pg_buffercache_summary()` function returns a single
row summarizing the state of the shared buffer cache.

The `pg_buffercache_usage_counts()` function returns a set
of records, each row describing the number of buffers with a given usage
count.

By default, use is restricted to superusers and roles with privileges of the
`pg_monitor` role. Access may be granted to others
using `GRANT`.

### The `pg_buffercache` View

The definitions of the columns exposed by the view are shown in [pgbuffercache-columns](#pgbuffercache-columns).

| Column Type                      Description |
| --- |
| `bufferid` `integer`                      ID, in the range 1..`shared_buffers` |
| `relfilenode` `oid`        (references [`pg_class`](#catalog-pg-class).`relfilenode`)                      Filenode number of the relation |
| `reltablespace` `oid`        (references [`pg_tablespace`](#catalog-pg-tablespace).`oid`)                      Tablespace OID of the relation |
| `reldatabase` `oid`        (references [`pg_database`](#catalog-pg-database).`oid`)                      Database OID of the relation |
| `relforknumber` `smallint`                      Fork number within the relation;  see        `common/relpath.h` |
| `relblocknumber` `bigint`                      Page number within the relation |
| `isdirty` `boolean`                      Is the page dirty? |
| `usagecount` `smallint`                      Clock-sweep access count |
| `pinning_backends` `integer`                      Number of backends pinning this buffer |

There is one row for each buffer in the shared cache. Unused buffers are
shown with all fields null except `bufferid`.  Shared system
catalogs are shown as belonging to database zero.

Because the cache is shared by all the databases, there will normally be
pages from relations not belonging to the current database.  This means
that there may not be matching join rows in `pg_class` for
some rows, or that there could even be incorrect joins.  If you are
trying to join against `pg_class`, it's a good idea to
restrict the join to rows having `reldatabase` equal to
the current database's OID or zero.

Since buffer manager locks are not taken to copy the buffer state data that
the view will display, accessing `pg_buffercache` view
has less impact on normal buffer activity but it doesn't provide a consistent
set of results across all buffers.  However, we ensure that the information of
each buffer is self-consistent.

### The `pg_buffercache_summary()` Function

The definitions of the columns exposed by the function are shown in [pgbuffercache-summary-columns](#pgbuffercache-summary-columns).

| Column Type                      Description |
| --- |
| `buffers_used` `int4`                      Number of used shared buffers |
| `buffers_unused` `int4`                      Number of unused shared buffers |
| `buffers_dirty` `int4`                      Number of dirty shared buffers |
| `buffers_pinned` `int4`                      Number of pinned shared buffers |
| `usagecount_avg` `float8`                      Average usage count of used shared buffers |

The `pg_buffercache_summary()` function returns a
single row summarizing the state of all shared buffers. Similar and more
detailed information is provided by the
`pg_buffercache` view, but
`pg_buffercache_summary()` is significantly cheaper.

Like the `pg_buffercache` view,
`pg_buffercache_summary()` does not acquire buffer
manager locks. Therefore concurrent activity can lead to minor inaccuracies
in the result.

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

### Sample Output

```
regression=# SELECT n.nspname, c.relname, count(*) AS buffers
FROM pg_buffercache b JOIN pg_class c
ON b.relfilenode = pg_relation_filenode(c.oid) AND
b.reldatabase IN (0, (SELECT oid FROM pg_database
WHERE datname = current_database()))
JOIN pg_namespace n ON n.oid = c.relnamespace
GROUP BY n.nspname, c.relname
ORDER BY 3 DESC
LIMIT 10;

nspname   |        relname         | buffers
------------+------------------------+---------
public     | delete_test_table      |     593
public     | delete_test_table_pkey |     494
pg_catalog | pg_attribute           |     472
public     | quad_poly_tbl          |     353
public     | tenk2                  |     349
public     | tenk1                  |     349
public     | gin_test_idx           |     306
pg_catalog | pg_largeobject         |     206
public     | gin_test_tbl           |     188
public     | spgist_text_tbl        |     182
(10 rows)

regression=# SELECT * FROM pg_buffercache_summary();
buffers_used | buffers_unused | buffers_dirty | buffers_pinned | usagecount_avg
--------------+----------------+---------------+----------------+----------------
248 |        2096904 |            39 |              0 |       3.141129
(1 row)

regression=# SELECT * FROM pg_buffercache_usage_counts();
usage_count | buffers | dirty | pinned
-------------+---------+-------+--------
0 |   14650 |     0 |      0
1 |    1436 |   671 |      0
2 |     102 |    88 |      0
3 |      23 |    21 |      0
4 |       9 |     7 |      0
5 |     164 |   106 |      0
(6 rows)
```

### Authors

Mark Kirkwood markir@paradise.net.nz

Design suggestions: Neil Conway neilc@samurai.com

Debugging advice: Tom Lane tgl@sss.pgh.pa.us

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

## pg_freespacemap — examine the free space map

The `pg_freespacemap` module provides a means for examining the
[free space map](#storage-fsm) (FSM).
It provides a function called `pg_freespace`, or two
overloaded functions, to be precise. The functions show the value recorded in
the free space map for a given page, or for all pages in the relation.

By default use is restricted to superusers and roles with privileges of the
`pg_stat_scan_tables` role. Access may be granted to others
using `GRANT`.

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

### Sample Output

```
postgres=# SELECT * FROM pg_freespace('foo');
blkno | avail
-------+-------
0 |     0
1 |     0
2 |     0
3 |    32
4 |   704
5 |   704
6 |   704
7 |  1216
8 |   704
9 |   704
10 |   704
11 |   704
12 |   704
13 |   704
14 |   704
15 |   704
16 |   704
17 |   704
18 |   704
19 |  3648
(20 rows)

postgres=# SELECT * FROM pg_freespace('foo', 7);
pg_freespace
--------------
1216
(1 row)
```

### Author

Original version by Mark Kirkwood markir@paradise.net.nz.
Rewritten in version 8.4 to suit new FSM implementation
by Heikki Linnakangas heikki@enterprisedb.com

## pg_prewarm — preload relation data into buffer caches

The `pg_prewarm` module provides a convenient way
to load relation data into either the operating system buffer cache
or the PostgreSQL buffer cache.  Prewarming
can be performed manually using the `pg_prewarm` function,
or can be performed automatically by including `pg_prewarm` in
[guc-shared-preload-libraries](#guc-shared-preload-libraries).  In the latter case, the
system will run a background worker which periodically records the contents
of shared buffers in a file called `autoprewarm.blocks` and
will, using 2 background workers, reload those same blocks after a restart.

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
# postgresql.conf
shared_preload_libraries = 'pg_prewarm'

pg_prewarm.autoprewarm = true
pg_prewarm.autoprewarm_interval = 300s
```

### Author

Robert Haas rhaas@postgresql.org

## pgrowlocks — show a table's row locking information

The `pgrowlocks` module provides a function to show row
locking information for a specified table.

By default use is restricted to superusers, roles with privileges of the
`pg_stat_scan_tables` role, and users with
`SELECT` permissions on the table.

### Overview

```
pgrowlocks(text) returns setof record
```

The parameter is the name of a table.  The result is a set of records,
with one row for each locked row within the table.  The output columns
are shown in [pgrowlocks-columns](#pgrowlocks-columns).

| Name | Type | Description |
| --- | --- | --- |
| `locked_row` | `tid` | Tuple ID (TID) of locked row |
| `locker` | `xid` | Transaction ID of locker, or multixact ID if       multitransaction;  see [transaction-id](#transaction-id) |
| `multi` | `boolean` | True if locker is a multitransaction |
| `xids` | `xid[]` | Transaction IDs of lockers (more than one if multitransaction) |
| `modes` | `text[]` | Lock mode of lockers (more than one if multitransaction),        an array of `Key Share`, `Share`,        `For No Key Update`, `No Key Update`,        `For Update`, `Update`. |
| `pids` | `integer[]` | Process IDs of locking backends (more than one if multitransaction) |

`pgrowlocks` takes `AccessShareLock` for the
target table and reads each row one by one to collect the row locking
information.  This is not very speedy for a large table.  Note that:

1. If an `ACCESS EXCLUSIVE` lock is taken on the table,
`pgrowlocks` will be blocked.
2. `pgrowlocks` is not guaranteed to produce a
self-consistent snapshot.  It is possible that a new row lock is taken,
or an old lock is freed, during its execution.

`pgrowlocks` does not show the contents of locked
rows. If you want to take a look at the row contents at the same time, you
could do something like this:

```
SELECT * FROM accounts AS a, pgrowlocks('accounts') AS p
WHERE p.locked_row = a.ctid;
```

Be aware however that such a query will be very inefficient.

### Sample Output

```
=# SELECT * FROM pgrowlocks('t1');
locked_row | locker | multi | xids  |     modes      |  pids
------------+--------+-------+-------+----------------+--------
(0,1)      |    609 | f     | {609} | {"For Share"}  | {3161}
(0,2)      |    609 | f     | {609} | {"For Share"}  | {3161}
(0,3)      |    607 | f     | {607} | {"For Update"} | {3107}
(0,4)      |    607 | f     | {607} | {"For Update"} | {3107}
(4 rows)
```

### Author

Tatsuo Ishii

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
# postgresql.conf
shared_preload_libraries = 'pg_stat_statements'

compute_query_id = on
pg_stat_statements.max = 10000
pg_stat_statements.track = all
```

### Sample Output

```
bench=# SELECT pg_stat_statements_reset();

$ pgbench -i bench
$ pgbench -c10 -t300 bench

bench=# \x
bench=# SELECT query, calls, total_exec_time, rows, 100.0 * shared_blks_hit /
nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 5;
-[ RECORD 1 ]---+--------------------------------------------------------------------
query           | UPDATE pgbench_branches SET bbalance = bbalance + $1 WHERE bid = $2
calls           | 3000
total_exec_time | 25565.855387
rows            | 3000
hit_percent     | 100.0000000000000000
-[ RECORD 2 ]---+--------------------------------------------------------------------
query           | UPDATE pgbench_tellers SET tbalance = tbalance + $1 WHERE tid = $2
calls           | 3000
total_exec_time | 20756.669379
rows            | 3000
hit_percent     | 100.0000000000000000
-[ RECORD 3 ]---+--------------------------------------------------------------------
query           | copy pgbench_accounts from stdin
calls           | 1
total_exec_time | 291.865911
rows            | 100000
hit_percent     | 100.0000000000000000
-[ RECORD 4 ]---+--------------------------------------------------------------------
query           | UPDATE pgbench_accounts SET abalance = abalance + $1 WHERE aid = $2
calls           | 3000
total_exec_time | 271.232977
rows            | 3000
hit_percent     | 98.8454011741682975
-[ RECORD 5 ]---+--------------------------------------------------------------------
query           | alter table pgbench_accounts add primary key (aid)
calls           | 1
total_exec_time | 160.588563
rows            | 0
hit_percent     | 100.0000000000000000

bench=# SELECT pg_stat_statements_reset(0,0,s.queryid) FROM pg_stat_statements AS s
WHERE s.query = 'UPDATE pgbench_branches SET bbalance = bbalance + $1 WHERE bid = $2';

bench=# SELECT query, calls, total_exec_time, rows, 100.0 * shared_blks_hit /
nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 5;
-[ RECORD 1 ]---+--------------------------------------------------------------------
query           | UPDATE pgbench_tellers SET tbalance = tbalance + $1 WHERE tid = $2
calls           | 3000
total_exec_time | 20756.669379
rows            | 3000
hit_percent     | 100.0000000000000000
-[ RECORD 2 ]---+--------------------------------------------------------------------
query           | copy pgbench_accounts from stdin
calls           | 1
total_exec_time | 291.865911
rows            | 100000
hit_percent     | 100.0000000000000000
-[ RECORD 3 ]---+--------------------------------------------------------------------
query           | UPDATE pgbench_accounts SET abalance = abalance + $1 WHERE aid = $2
calls           | 3000
total_exec_time | 271.232977
rows            | 3000
hit_percent     | 98.8454011741682975
-[ RECORD 4 ]---+--------------------------------------------------------------------
query           | alter table pgbench_accounts add primary key (aid)
calls           | 1
total_exec_time | 160.588563
rows            | 0
hit_percent     | 100.0000000000000000
-[ RECORD 5 ]---+--------------------------------------------------------------------
query           | vacuum analyze pgbench_accounts
calls           | 1
total_exec_time | 136.448116
rows            | 0
hit_percent     | 99.9201915403032721

bench=# SELECT pg_stat_statements_reset(0,0,0);

bench=# SELECT query, calls, total_exec_time, rows, 100.0 * shared_blks_hit /
nullif(shared_blks_hit + shared_blks_read, 0) AS hit_percent
FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT 5;
-[ RECORD 1 ]---+-----------------------------------------------------------------------------
query           | SELECT pg_stat_statements_reset(0,0,0)
calls           | 1
total_exec_time | 0.189497
rows            | 1
hit_percent     |
-[ RECORD 2 ]---+-----------------------------------------------------------------------------
query           | SELECT query, calls, total_exec_time, rows, $1 * shared_blks_hit /          +
|                nullif(shared_blks_hit + shared_blks_read, $2) AS hit_percent+
|           FROM pg_stat_statements ORDER BY total_exec_time DESC LIMIT $3
calls           | 0
total_exec_time | 0
rows            | 0
hit_percent     |
```

### Authors

Takahiro Itagaki itagaki.takahiro@oss.ntt.co.jp.
Query normalization added by Peter Geoghegan peter@2ndquadrant.com.

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

## `pgstattuple` Output Columns

Column
Type
Description

`table_len`
`bigint`
Physical relation length in bytes

`tuple_count`
`bigint`
Number of live tuples

`tuple_len`
`bigint`
Total length of live tuples in bytes

`tuple_percent`
`float8`
Percentage of live tuples

`dead_tuple_count`
`bigint`
Number of dead tuples

`dead_tuple_len`
`bigint`
Total length of dead tuples in bytes

`dead_tuple_percent`
`float8`
Percentage of dead tuples

`free_space`
`bigint`
Total free space in bytes

`free_percent`
`float8`
Percentage of free space

> **Note:**
> The `table_len` will always be greater than the sum
> of the `tuple_len`, `dead_tuple_len`
> and `free_space`. The difference is accounted for by
> fixed page overhead, the per-page table of pointers to tuples, and
> padding to ensure that tuples are correctly aligned.
>

`pgstattuple` acquires only a read lock on the
relation. So the results do not reflect an instantaneous snapshot;
concurrent updates will affect them.

`pgstattuple` judges a tuple is "dead" if
`HeapTupleSatisfiesDirty` returns false.

**`pgstattuple(text) returns record`**
: This is the same as `pgstattuple(regclass)`, except
that the target relation is specified as TEXT. This function is kept
because of backward-compatibility so far, and will be deprecated in
some future release.

**`pgstatindex(regclass) returns record`**
: `pgstatindex` returns a record showing information
about a B-tree index.  For example:

```
test=> SELECT * FROM pgstatindex('pg_cast_oid_index');
-[ RECORD 1 ]------+------
version            | 2
tree_level         | 0
index_size         | 16384
root_block_no      | 1
internal_pages     | 0
leaf_pages         | 1
empty_pages        | 0
deleted_pages      | 0
avg_leaf_density   | 54.27
leaf_fragmentation | 0
```

The output columns are:

Column
Type
Description

`version`
`integer`
B-tree version number

`tree_level`
`integer`
Tree level of the root page

`index_size`
`bigint`
Total index size in bytes

`root_block_no`
`bigint`
Location of root page (zero if none)

`internal_pages`
`bigint`
Number of "internal" (upper-level) pages

`leaf_pages`
`bigint`
Number of leaf pages

`empty_pages`
`bigint`
Number of empty pages

`deleted_pages`
`bigint`
Number of deleted pages

`avg_leaf_density`
`float8`
Average density of leaf pages

`leaf_fragmentation`
`float8`
Leaf page fragmentation

The reported `index_size` will normally correspond to one more
page than is accounted for by `internal_pages + leaf_pages +
empty_pages + deleted_pages`, because it also includes the
index's metapage.

As with `pgstattuple`, the results are accumulated
page-by-page, and should not be expected to represent an
instantaneous snapshot of the whole index.

**`pgstatindex(text) returns record`**
: This is the same as `pgstatindex(regclass)`, except
that the target index is specified as TEXT. This function is kept
because of backward-compatibility so far, and will be deprecated in
some future release.

**`pgstatginindex(regclass) returns record`**
: `pgstatginindex` returns a record showing information
about a GIN index.  For example:

```
test=> SELECT * FROM pgstatginindex('test_gin_index');
-[ RECORD 1 ]--+--
version        | 1
pending_pages  | 0
pending_tuples | 0
```

The output columns are:

Column
Type
Description

`version`
`integer`
GIN version number

`pending_pages`
`integer`
Number of pages in the pending list

`pending_tuples`
`bigint`
Number of tuples in the pending list

**`pgstathashindex(regclass) returns record`**
: `pgstathashindex` returns a record showing information
about a HASH index.  For example:

```
test=> select * from pgstathashindex('con_hash_index');
-[ RECORD 1 ]--+-----------------
version        | 4
bucket_pages   | 33081
overflow_pages | 0
bitmap_pages   | 1
unused_pages   | 32455
live_items     | 10204006
dead_items     | 0
free_percent   | 61.8005949100872
```

The output columns are:

Column
Type
Description

`version`
`integer`
HASH version number

`bucket_pages`
`bigint`
Number of bucket pages

`overflow_pages`
`bigint`
Number of overflow pages

`bitmap_pages`
`bigint`
Number of bitmap pages

`unused_pages`
`bigint`
Number of unused pages

`live_items`
`bigint`
Number of live tuples

`dead_tuples`
`bigint`
Number of dead tuples

`free_percent`
`float`
Percentage of free space

**`pg_relpages(regclass) returns bigint`**
: `pg_relpages` returns the number of pages in the
relation.

**`pg_relpages(text) returns bigint`**
: This is the same as `pg_relpages(regclass)`, except
that the target relation is specified as TEXT. This function is kept
because of backward-compatibility so far, and will be deprecated in
some future release.

**`pgstattuple_approx(regclass) returns record`**
: `pgstattuple_approx` is a faster alternative to
`pgstattuple` that returns approximate results.
The argument is the target relation's name or OID.
For example:

```
test=> SELECT * FROM pgstattuple_approx('pg_catalog.pg_proc'::regclass);
-[ RECORD 1 ]--------+-------
table_len            | 573440
scanned_percent      | 2
approx_tuple_count   | 2740
approx_tuple_len     | 561210
approx_tuple_percent | 97.87
dead_tuple_count     | 0
dead_tuple_len       | 0
dead_tuple_percent   | 0
approx_free_space    | 11996
approx_free_percent  | 2.09
```

The output columns are described in [pgstatapprox-columns](#pgstatapprox-columns).

Whereas `pgstattuple` always performs a
full-table scan and returns an exact count of live and dead tuples
(and their sizes) and free space, `pgstattuple_approx`
tries to avoid the full-table scan and returns exact dead tuple
statistics along with an approximation of the number and
size of live tuples and free space.

It does this by skipping pages that have only visible tuples
according to the visibility map (if a page has the corresponding VM
bit set, then it is assumed to contain no dead tuples). For such
pages, it derives the free space value from the free space map, and
assumes that the rest of the space on the page is taken up by live
tuples.

For pages that cannot be skipped, it scans each tuple, recording its
presence and size in the appropriate counters, and adding up the
free space on the page. At the end, it estimates the total number of
live tuples based on the number of pages and tuples scanned (in the
same way that VACUUM estimates pg_class.reltuples).

## `pgstattuple_approx` Output Columns

Column
Type
Description

`table_len`
`bigint`
Physical relation length in bytes (exact)

`scanned_percent`
`float8`
Percentage of table scanned

`approx_tuple_count`
`bigint`
Number of live tuples (estimated)

`approx_tuple_len`
`bigint`
Total length of live tuples in bytes (estimated)

`approx_tuple_percent`
`float8`
Percentage of live tuples

`dead_tuple_count`
`bigint`
Number of dead tuples (exact)

`dead_tuple_len`
`bigint`
Total length of dead tuples in bytes (exact)

`dead_tuple_percent`
`float8`
Percentage of dead tuples

`approx_free_space`
`bigint`
Total free space in bytes (estimated)

`approx_free_percent`
`float8`
Percentage of free space

In the above output, the free space figures may not match the
`pgstattuple` output exactly, because the free
space map gives us an exact figure, but is not guaranteed to be
accurate to the byte.

### Authors

Tatsuo Ishii, Satoshi Nagayasu and Abhijit Menon-Sen

## pg_surgery — perform low-level surgery on relation data

The `pg_surgery` module provides various functions to
perform surgery on a damaged relation. These functions are unsafe by design
and using them may corrupt (or further corrupt) your database. For example,
these functions can easily be used to make a table inconsistent with its
own indexes, to cause `UNIQUE` or
`FOREIGN KEY` constraint violations, or even to make
tuples visible which, when read, will cause a database server crash.
They should be used with great caution and only as a last resort.

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

### Authors

Ashutosh Sharma ashu.coek88@gmail.com

## pg_trgm —
support for similarity of text using trigram matching

The `pg_trgm` module provides functions and operators
for determining the similarity of
alphanumeric text based on trigram matching, as
well as index operator classes that support fast searching for similar
strings.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Trigram (or Trigraph) Concepts

A trigram is a group of three consecutive characters taken
from a string.  We can measure the similarity of two strings by
counting the number of trigrams they share.  This simple idea
turns out to be very effective for measuring the similarity of
words in many natural languages.

> **Note:**

> `pg_trgm` ignores non-word characters
> (non-alphanumerics) when extracting trigrams from a string.
> Each word is considered to have two spaces
> prefixed and one space suffixed when determining the set
> of trigrams contained in the string.
> For example, the set of trigrams in the string
> "`cat`" is
> "`  c`",
> "` ca`",
> "`cat`", and
> "`at `".
> The set of trigrams in the string
> "`foo|bar`" is
> "`  f`",
> "` fo`",
> "`foo`",
> "`oo `",
> "`  b`",
> "` ba`",
> "`bar`", and
> "`ar `".
>

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
# SELECT word_similarity('word', 'two words');
word_similarity
-----------------
0.8
(1 row)
```

In the first string, the set of trigrams is
`{"  w"," wo","wor","ord","rd "}`.
In the second string, the ordered set of trigrams is
`{"  t"," tw","two","wo ","  w"," wo","wor","ord","rds","ds "}`.
The most similar extent of an ordered set of trigrams in the second string
is `{"  w"," wo","wor","ord"}`, and the similarity is
`0.8`.

This function returns a value that can be approximately understood as the
greatest similarity between the first string and any substring of the second
string.  However, this function does not add padding to the boundaries of
the extent.  Thus, the number of additional characters present in the
second string is not considered, except for the mismatched word boundaries.

At the same time, `strict_word_similarity`
selects an extent of words in the second string.  In the example above,
`strict_word_similarity` would select the
extent of a single word `'words'`, whose set of trigrams is
`{"  w"," wo","wor","ord","rds","ds "}`.

```
# SELECT strict_word_similarity('word', 'two words'), similarity('word', 'words');
strict_word_similarity | similarity
------------------------+------------
0.571429 |   0.571429
(1 row)
```

Thus, the `strict_word_similarity` function
is useful for finding the similarity to whole words, while
`word_similarity` is more suitable for
finding the similarity for parts of words.

| Operator                         Description |
| --- |
| `text` `%` `text`         boolean                         Returns `true` if its arguments have a similarity         that is greater than the current similarity threshold set by         `pg_trgm.similarity_threshold`. |
| `text` `` `text`         boolean                         Commutator of the `>` `text`         boolean                         Commutator of the `` `text`         real                         Returns the "distance" between the arguments, that is         one minus the `similarity()` value. |
| `text` `` `text`         real                         Returns the "distance" between the arguments, that is         one minus the `word_similarity()` value. |
| `text` `>` `text`         real                         Commutator of the `` operator. |
| `text` `` `text`         real                         Returns the "distance" between the arguments, that is         one minus the `strict_word_similarity()` value. |
| `text` `>>` `text`         real                         Commutator of the `` operator. |

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

## pg_visibility — visibility map information and utilities

The `pg_visibility` module provides a means for examining the
visibility map (VM) and page-level visibility information of a table.
It also provides functions to check the integrity of a visibility map and to
force it to be rebuilt.

Three different bits are used to store information about page-level
visibility.  The all-visible bit in the visibility map indicates that every
tuple in the corresponding page of the relation is visible to every current
and future transaction.  The all-frozen bit in the visibility map indicates
that every tuple in the page is frozen; that is, no future vacuum will need
to modify the page until such time as a tuple is inserted, updated, deleted,
or locked on that page.
The page header's `PD_ALL_VISIBLE` bit has the
same meaning as the all-visible bit in the visibility map, but is stored
within the data page itself rather than in a separate data structure.
These two bits will normally agree, but the page's all-visible bit can
sometimes be set while the visibility map bit is clear after a crash
recovery.  The reported values can also disagree because of a change that
occurs after `pg_visibility` examines the visibility map and
before it examines the data page.  Any event that causes data corruption
can also cause these bits to disagree.

Functions that display information about `PD_ALL_VISIBLE` bits
are much more costly than those that only consult the visibility map,
because they must read the relation's data blocks rather than only the
(much smaller) visibility map.  Functions that check the relation's
data blocks are similarly expensive.

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

### Author

Robert Haas rhaas@postgresql.org

## pg_walinspect — low-level WAL inspection

The `pg_walinspect` module provides SQL functions that
allow you to inspect the contents of write-ahead log of
a running PostgreSQL database cluster at a low
level, which is useful for debugging, analytical, reporting or
educational purposes. It is similar to [pgwaldump](#pgwaldump), but
accessible through SQL rather than a separate utility.

All the functions of this module will provide the WAL information using the
server's current timeline ID.

> **Note:**

> The `pg_walinspect` functions are often called
> using an LSN argument that specifies the location at which a known
> WAL record of interest *begins*.  However, some
> functions, such as
> `[pg_logical_emit_message](#pg-logical-emit-message)`,
> return the LSN *after* the record that was just
> inserted.
>

> **Tip:**

> All of the `pg_walinspect` functions that show
> information about records that fall within a certain LSN range are
> permissive about accepting `end_lsn`
> arguments that are after the server's current LSN.  Using an
> `end_lsn` "from the future"
> will not raise an error.
>

>

> It may be convenient to provide the value
> `FFFFFFFF/FFFFFFFF` (the maximum valid
> `pg_lsn` value) as an `end_lsn`
> argument.  This is equivalent to providing an
> `end_lsn` argument matching the server's
> current LSN.
>

By default, use of these functions is restricted to superusers and members of
the `pg_read_server_files` role. Access may be granted by
superusers to others using `GRANT`.

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

### Author

Bharath Rupireddy bharath.rupireddyforpostgres@gmail.com

## postgres_fdw —
access data stored in external PostgreSQL
servers

The `postgres_fdw` module provides the foreign-data wrapper
`postgres_fdw`, which can be used to access data
stored in external PostgreSQL servers.

The functionality provided by this module overlaps substantially
with the functionality of the older [dblink](#dblink) module.
But `postgres_fdw` provides more transparent and
standards-compliant syntax for accessing remote tables, and can give
better performance in many cases.

To prepare for remote access using `postgres_fdw`:

1. Install the  `postgres_fdw` extension using [sql-createextension](#sql-createextension).
2. Create a foreign server object, using [sql-createserver](#sql-createserver),
to represent each remote database you want to connect to.
Specify connection information, except `user` and
`password`, as options of the server object.
3. Create a user mapping, using [sql-createusermapping](#sql-createusermapping), for
each database user you want to allow to access each foreign server.
Specify the remote user name and password to use as
`user` and `password` options of the
user mapping.
4. Create a foreign table, using [sql-createforeigntable](#sql-createforeigntable)
or [sql-importforeignschema](#sql-importforeignschema),
for each remote table you want to access.  The columns of the foreign
table must match the referenced remote table.  You can, however, use
table and/or column names different from the remote table's, if you
specify the correct remote names as options of the foreign table object.

Now you need only `SELECT` from a foreign table to access
the data stored in its underlying remote table.  You can also modify
the remote table using `INSERT`, `UPDATE`,
`DELETE`, `COPY`, or
`TRUNCATE`.
(Of course, the remote user you have specified in your user mapping must
have privileges to do these things.)

Note that the `ONLY` option specified in
`SELECT`, `UPDATE`,
`DELETE` or `TRUNCATE`
has no effect when accessing or modifying the remote table.

Note that `postgres_fdw` currently lacks support for
`INSERT` statements with an `ON CONFLICT DO
UPDATE` clause.  However, the `ON CONFLICT DO NOTHING`
clause is supported, provided a unique index inference specification
is omitted.
Note also that `postgres_fdw` supports row movement
invoked by `UPDATE` statements executed on partitioned
tables, but it currently does not handle the case where a remote partition
chosen to insert a moved row into is also an `UPDATE`
target partition that will be updated elsewhere in the same command.

It is generally recommended that the columns of a foreign table be declared
with exactly the same data types, and collations if applicable, as the
referenced columns of the remote table.  Although `postgres_fdw`
is currently rather forgiving about performing data type conversions at
need, surprising semantic anomalies may arise when types or collations do
not match, due to the remote server interpreting query conditions
differently from the local server.

Note that a foreign table can be declared with fewer columns, or with a
different column order, than its underlying remote table has.  Matching
of columns to the remote table is by name, not position.

### FDW Options of postgres_fdw

#### Connection Options

A foreign server using the `postgres_fdw` foreign data wrapper
can have the same options that libpq accepts in
connection strings, as described in [libpq-paramkeywords](#libpq-paramkeywords),
except that these options are not allowed or have special handling:

- `user`, `password` and `sslpassword` (specify these
in a user mapping, instead, or use a service file)
- `client_encoding` (this is automatically set from the local
server encoding)
- `application_name` - this may appear in
*either or both* a connection and
[guc-pgfdw-application-name](#guc-pgfdw-application-name).
If both are present, `postgres_fdw.application_name`
overrides the connection setting.
Unlike libpq,
`postgres_fdw` allows
`application_name` to include
"escape sequences".
See [guc-pgfdw-application-name](#guc-pgfdw-application-name) for details.
- `fallback_application_name` (always set to
`postgres_fdw`)
- `sslkey` and `sslcert` - these may
appear in *either or both* a connection and a user
mapping. If both are present, the user mapping setting overrides the
connection setting.

Only superusers may create or modify user mappings with the
`sslcert` or `sslkey` settings.

Non-superusers may connect to foreign servers using password
authentication or with GSSAPI delegated credentials, so specify the
`password` option for user mappings belonging to
non-superusers where password authentication is required.

A superuser may override this check on a per-user-mapping basis by setting
the user mapping option `password_required 'false'`, e.g.,

```
ALTER USER MAPPING FOR some_non_superuser SERVER loopback_nopw
OPTIONS (ADD password_required 'false');
```

To prevent unprivileged users from exploiting the authentication rights
of the unix user the postgres server is running as to escalate to superuser
rights, only the superuser may set this option on a user mapping.

Care is required to ensure that this does not allow the mapped
user the ability to connect as superuser to the mapped database per
CVE-2007-3278 and CVE-2007-6601. Don't set
`password_required=false`
on the `public` role. Keep in mind that the mapped
user can potentially use any client certificates,
`.pgpass`,
`.pg_service.conf` etc. in the unix home directory of the
system user the postgres server runs as. They can also use any trust
relationship granted by authentication modes like `peer`
or `ident` authentication.

#### Object Name Options

These options can be used to control the names used in SQL statements
sent to the remote PostgreSQL server.  These
options are needed when a foreign table is created with names different
from the underlying remote table's names.

**`schema_name` (`string`)**
: This option, which can be specified for a foreign table, gives the
schema name to use for the foreign table on the remote server.  If this
option is omitted, the name of the foreign table's schema is used.

**`table_name` (`string`)**
: This option, which can be specified for a foreign table, gives the
table name to use for the foreign table on the remote server.  If this
option is omitted, the foreign table's name is used.

**`column_name` (`string`)**
: This option, which can be specified for a column of a foreign table,
gives the column name to use for the column on the remote server.
If this option is omitted, the column's name is used.

#### Cost Estimation Options

`postgres_fdw` retrieves remote data by executing queries
against remote servers, so ideally the estimated cost of scanning a
foreign table should be whatever it costs to be done on the remote
server, plus some overhead for communication.  The most reliable way to
get such an estimate is to ask the remote server and then add something
for overhead — but for simple queries, it may not be worth the cost
of an additional remote query to get a cost estimate.
So `postgres_fdw` provides the following options to control
how cost estimation is done:

**`use_remote_estimate` (`boolean`)**
: This option, which can be specified for a foreign table or a foreign
server, controls whether `postgres_fdw` issues remote
`EXPLAIN` commands to obtain cost estimates.
A setting for a foreign table overrides any setting for its server,
but only for that table.
The default is `false`.

**`fdw_startup_cost` (`floating point`)**
: This option, which can be specified for a foreign server, is a floating
point value that is added to the estimated startup cost of any
foreign-table scan on that server.  This represents the additional
overhead of establishing a connection, parsing and planning the query on
the remote side, etc.
The default value is `100`.

**`fdw_tuple_cost` (`floating point`)**
: This option, which can be specified for a foreign server, is a floating
point value that is used as extra cost per-tuple for foreign-table
scans on that server.  This represents the additional overhead of
data transfer between servers.  You might increase or decrease this
number to reflect higher or lower network delay to the remote server.
The default value is `0.01`.

When `use_remote_estimate` is true,
`postgres_fdw` obtains row count and cost estimates from the
remote server and then adds `fdw_startup_cost` and
`fdw_tuple_cost` to the cost estimates.  When
`use_remote_estimate` is false,
`postgres_fdw` performs local row count and cost estimation
and then adds `fdw_startup_cost` and
`fdw_tuple_cost` to the cost estimates.  This local
estimation is unlikely to be very accurate unless local copies of the
remote table's statistics are available.  Running
[sql-analyze](#sql-analyze) on the foreign table is the way to update
the local statistics; this will perform a scan of the remote table and
then calculate and store statistics just as though the table were local.
Keeping local statistics can be a useful way to reduce per-query planning
overhead for a remote table — but if the remote table is
frequently updated, the local statistics will soon be obsolete.

The following option controls how such an `ANALYZE`
operation behaves:

**`analyze_sampling` (`string`)**
: This option, which can be specified for a foreign table or a foreign
server, determines if `ANALYZE` on a foreign table
samples the data on the remote side, or reads and transfers all data
and performs the sampling locally. The supported values
are `off`, `random`,
`system`, `bernoulli`
and `auto`. `off` disables remote
sampling, so all data are transferred and sampled locally.
`random` performs remote sampling using the
`random()` function to choose returned rows,
while `system` and `bernoulli` rely
on the built-in `TABLESAMPLE` methods of those
names. `random` works on all remote server versions,
while `TABLESAMPLE` is supported only since 9.5.
`auto` (the default) picks the recommended sampling
method automatically; currently it means
either `bernoulli` or `random`
depending on the remote server version.

#### Remote Execution Options

By default, only `WHERE` clauses using built-in operators and
functions will be considered for execution on the remote server.  Clauses
involving non-built-in functions are checked locally after rows are
fetched.  If such functions are available on the remote server and can be
relied on to produce the same results as they do locally, performance can
be improved by sending such `WHERE` clauses for remote
execution.  This behavior can be controlled using the following option:

**`extensions` (`string`)**
: This option is a comma-separated list of names
of PostgreSQL extensions that are installed, in
compatible versions, on both the local and remote servers.  Functions
and operators that are immutable and belong to a listed extension will
be considered shippable to the remote server.
This option can only be specified for foreign servers, not per-table.

When using the `extensions` option, *it is the
user's responsibility* that the listed extensions exist and behave
identically on both the local and remote servers.  Otherwise, remote
queries may fail or behave unexpectedly.

**`fetch_size` (`integer`)**
: This option specifies the number of rows `postgres_fdw`
should get in each fetch operation. It can be specified for a foreign
table or a foreign server. The option specified on a table overrides
an option specified for the server.
The default is `100`.

**`batch_size` (`integer`)**
: This option specifies the number of rows `postgres_fdw`
should insert in each insert operation. It can be specified for a
foreign table or a foreign server. The option specified on a table
overrides an option specified for the server.
The default is `1`.

Note the actual number of rows `postgres_fdw` inserts at
once depends on the number of columns and the provided
`batch_size` value. The batch is executed as a single
query, and the libpq protocol (which `postgres_fdw`
uses to connect to a remote server) limits the number of parameters in a
single query to 65535. When the number of columns * `batch_size`
exceeds the limit, the `batch_size` will be adjusted to
avoid an error.

This option also applies when copying into foreign tables.  In that case
the actual number of rows `postgres_fdw` copies at
once is determined in a similar way to the insert case, but it is
limited to at most 1000 due to implementation restrictions of the
`COPY` command.

#### Asynchronous Execution Options

`postgres_fdw` supports asynchronous execution, which
runs multiple parts of an `Append` node
concurrently rather than serially to improve performance.
This execution can be controlled using the following option:

**`async_capable` (`boolean`)**
: This option controls whether `postgres_fdw` allows
foreign tables to be scanned concurrently for asynchronous execution.
It can be specified for a foreign table or a foreign server.
A table-level option overrides a server-level option.
The default is `false`.

In order to ensure that the data being returned from a foreign server
is consistent, `postgres_fdw` will only open one
connection for a given foreign server and will run all queries against
that server sequentially even if there are multiple foreign tables
involved, unless those tables are subject to different user mappings.
In such a case, it may be more performant to disable this option to
eliminate the overhead associated with running queries asynchronously.

Asynchronous execution is applied even when an
`Append` node contains subplan(s) executed
synchronously as well as subplan(s) executed asynchronously.
In such a case, if the asynchronous subplans are ones processed using
`postgres_fdw`, tuples from the asynchronous
subplans are not returned until after at least one synchronous subplan
returns all tuples, as that subplan is executed while the asynchronous
subplans are waiting for the results of asynchronous queries sent to
foreign servers.
This behavior might change in a future release.

#### Transaction Management Options

As described in the Transaction Management section, in
`postgres_fdw` transactions are managed by creating
corresponding remote transactions, and subtransactions are managed by
creating corresponding remote subtransactions. When multiple remote
transactions are involved in the current local transaction, by default
`postgres_fdw` commits or aborts those remote
transactions serially when the local transaction is committed or aborted.
When multiple remote subtransactions are involved in the current local
subtransaction, by default `postgres_fdw` commits or
aborts those remote subtransactions serially when the local subtransaction
is committed or aborted.
Performance can be improved with the following options:

**`parallel_commit` (`boolean`)**
: This option controls whether `postgres_fdw` commits,
in parallel, remote transactions opened on a foreign server in a local
transaction when the local transaction is committed. This setting also
applies to remote and local subtransactions. This option can only be
specified for foreign servers, not per-table. The default is
`false`.

**`parallel_abort` (`boolean`)**
: This option controls whether `postgres_fdw` aborts,
in parallel, remote transactions opened on a foreign server in a local
transaction when the local transaction is aborted. This setting also
applies to remote and local subtransactions. This option can only be
specified for foreign servers, not per-table. The default is
`false`.

If multiple foreign servers with these options enabled are involved in a
local transaction, multiple remote transactions on those foreign servers
are committed or aborted in parallel across those foreign servers when
the local transaction is committed or aborted.

When these options are enabled, a foreign server with many remote
transactions may see a negative performance impact when the local
transaction is committed or aborted.

#### Updatability Options

By default all foreign tables using `postgres_fdw` are assumed
to be updatable.  This may be overridden using the following option:

**`updatable` (`boolean`)**
: This option controls whether `postgres_fdw` allows foreign
tables to be modified using `INSERT`, `UPDATE` and
`DELETE` commands.  It can be specified for a foreign table
or a foreign server.  A table-level option overrides a server-level
option.
The default is `true`.

Of course, if the remote table is not in fact updatable, an error
would occur anyway.  Use of this option primarily allows the error to
be thrown locally without querying the remote server.  Note however
that the `information_schema` views will report a
`postgres_fdw` foreign table to be updatable (or not)
according to the setting of this option, without any check of the
remote server.

#### Truncatability Options

By default all foreign tables using `postgres_fdw` are assumed
to be truncatable.  This may be overridden using the following option:

**`truncatable` (`boolean`)**
: This option controls whether `postgres_fdw` allows
foreign tables to be truncated using the `TRUNCATE`
command. It can be specified for a foreign table or a foreign server.
A table-level option overrides a server-level option.
The default is `true`.

Of course, if the remote table is not in fact truncatable, an error
would occur anyway.  Use of this option primarily allows the error to
be thrown locally without querying the remote server.

#### Importing Options

`postgres_fdw` is able to import foreign table definitions
using [sql-importforeignschema](#sql-importforeignschema).  This command creates
foreign table definitions on the local server that match tables or
views present on the remote server.  If the remote tables to be imported
have columns of user-defined data types, the local server must have
compatible types of the same names.

Importing behavior can be customized with the following options
(given in the `IMPORT FOREIGN SCHEMA` command):

**`import_collate` (`boolean`)**
: This option controls whether column `COLLATE` options
are included in the definitions of foreign tables imported
from a foreign server. The default is `true`.  You might
need to turn this off if the remote server has a different set of
collation names than the local server does, which is likely to be the
case if it's running on a different operating system.
If you do so, however, there is a very severe risk that the imported
table columns' collations will not match the underlying data, resulting
in anomalous query behavior.

Even when this parameter is set to `true`, importing
columns whose collation is the remote server's default can be risky.
They will be imported with `COLLATE "default"`, which
will select the local server's default collation, which could be
different.

**`import_default` (`boolean`)**
: This option controls whether column `DEFAULT` expressions
are included in the definitions of foreign tables imported
from a foreign server. The default is `false`.  If you
enable this option, be wary of defaults that might get computed
differently on the local server than they would be on the remote
server; `nextval()` is a common source of problems.
The `IMPORT` will fail altogether if an imported default
expression uses a function or operator that does not exist locally.

**`import_generated` (`boolean`)**
: This option controls whether column `GENERATED` expressions
are included in the definitions of foreign tables imported
from a foreign server. The default is `true`.
The `IMPORT` will fail altogether if an imported generated
expression uses a function or operator that does not exist locally.

**`import_not_null` (`boolean`)**
: This option controls whether column `NOT NULL`
constraints are included in the definitions of foreign tables imported
from a foreign server. The default is `true`.

Note that constraints other than `NOT NULL` will never be
imported from the remote tables.  Although PostgreSQL
does support check constraints on foreign tables, there is no
provision for importing them automatically, because of the risk that a
constraint expression could evaluate differently on the local and remote
servers.  Any such inconsistency in the behavior of a check
constraint could lead to hard-to-detect errors in query optimization.
So if you wish to import check constraints, you must do so
manually, and you should verify the semantics of each one carefully.
For more detail about the treatment of check constraints on
foreign tables, see [sql-createforeigntable](#sql-createforeigntable).

Tables or foreign tables which are partitions of some other table are
imported only when they are explicitly specified in
`LIMIT TO` clause.  Otherwise they are automatically
excluded from [sql-importforeignschema](#sql-importforeignschema).
Since all data can be accessed through the partitioned table
which is the root of the partitioning hierarchy, importing only
partitioned tables should allow access to all the data without
creating extra objects.

#### Connection Management Options

By default, all connections that `postgres_fdw`
establishes to foreign servers are kept open in the local session
for re-use.

**`keep_connections` (`boolean`)**
: This option controls whether `postgres_fdw` keeps
the connections to the foreign server open so that subsequent
queries can re-use them. It can only be specified for a foreign server.
The default is `on`. If set to `off`,
all connections to this foreign server will be discarded at the end of
each transaction.

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

### Connection Management

`postgres_fdw` establishes a connection to a
foreign server during the first query that uses a foreign table
associated with the foreign server.  By default this connection
is kept and re-used for subsequent queries in the same session.
This behavior can be controlled using
`keep_connections` option for a foreign server. If
multiple user identities (user mappings) are used to access the foreign
server, a connection is established for each user mapping.

When changing the definition of or removing a foreign server or
a user mapping, the associated connections are closed.
But note that if any connections are in use in the current local transaction,
they are kept until the end of the transaction.
Closed connections will be re-established when they are necessary
by future queries using a foreign table.

Once a connection to a foreign server has been established,
it's by default kept until the local or corresponding remote
session exits.  To disconnect a connection explicitly,
`keep_connections` option for a foreign server
may be disabled, or
`postgres_fdw_disconnect` and
`postgres_fdw_disconnect_all` functions
may be used.  For example, these are useful to close
connections that are no longer necessary, thereby releasing
connections on the foreign server.

### Transaction Management

During a query that references any remote tables on a foreign server,
`postgres_fdw` opens a transaction on the
remote server if one is not already open corresponding to the current
local transaction.  The remote transaction is committed or aborted when
the local transaction commits or aborts.  Savepoints are similarly
managed by creating corresponding remote savepoints.

The remote transaction uses `SERIALIZABLE`
isolation level when the local transaction has `SERIALIZABLE`
isolation level; otherwise it uses `REPEATABLE READ`
isolation level.  This choice ensures that if a query performs multiple
table scans on the remote server, it will get snapshot-consistent results
for all the scans.  A consequence is that successive queries within a
single transaction will see the same data from the remote server, even if
concurrent updates are occurring on the remote server due to other
activities.  That behavior would be expected anyway if the local
transaction uses `SERIALIZABLE` or `REPEATABLE READ`
isolation level, but it might be surprising for a `READ
COMMITTED` local transaction.  A future
PostgreSQL release might modify these rules.

Note that it is currently not supported by
`postgres_fdw` to prepare the remote transaction for
two-phase commit.

### Remote Query Optimization

`postgres_fdw` attempts to optimize remote queries to reduce
the amount of data transferred from foreign servers.  This is done by
sending query `WHERE` clauses to the remote server for
execution, and by not retrieving table columns that are not needed for
the current query.  To reduce the risk of misexecution of queries,
`WHERE` clauses are not sent to the remote server unless they use
only data types, operators, and functions that are built-in or belong to an
extension that's listed in the foreign server's `extensions`
option.  Operators and functions in such clauses must
be `IMMUTABLE` as well.
For an `UPDATE` or `DELETE` query,
`postgres_fdw` attempts to optimize the query execution by
sending the whole query to the remote server if there are no query
`WHERE` clauses that cannot be sent to the remote server,
no local joins for the query, no row-level local `BEFORE` or
`AFTER` triggers or stored generated columns on the target
table, and no `CHECK OPTION` constraints from parent
views.  In `UPDATE`,
expressions to assign to target columns must use only built-in data types,
`IMMUTABLE` operators, or `IMMUTABLE` functions,
to reduce the risk of misexecution of the query.

When `postgres_fdw` encounters a join between foreign tables on
the same foreign server, it sends the entire join to the foreign server,
unless for some reason it believes that it will be more efficient to fetch
rows from each table individually, or unless the table references involved
are subject to different user mappings.  While sending the `JOIN`
clauses, it takes the same precautions as mentioned above for the
`WHERE` clauses.

The query that is actually sent to the remote server for execution can
be examined using `EXPLAIN VERBOSE`.

### Remote Query Execution Environment

In the remote sessions opened by `postgres_fdw`,
the [guc-search-path](#guc-search-path) parameter is set to
just `pg_catalog`, so that only built-in objects are visible
without schema qualification.  This is not an issue for queries
generated by `postgres_fdw` itself, because it always
supplies such qualification.  However, this can pose a hazard for
functions that are executed on the remote server via triggers or rules
on remote tables.  For example, if a remote table is actually a view,
any functions used in that view will be executed with the restricted
search path.  It is recommended to schema-qualify all names in such
functions, or else attach `SET search_path` options
(see [sql-createfunction](#sql-createfunction)) to such functions
to establish their expected search path environment.

`postgres_fdw` likewise establishes remote session settings
for various parameters:

- [guc-timezone](#guc-timezone) is set to `UTC`
- [guc-datestyle](#guc-datestyle) is set to `ISO`
- [guc-intervalstyle](#guc-intervalstyle) is set to `postgres`
- [guc-extra-float-digits](#guc-extra-float-digits) is set to `3` for remote
servers 9.0 and newer and is set to `2` for older versions

These are less likely to be problematic than `search_path`, but
can be handled with function `SET` options if the need arises.

It is *not* recommended that you override this behavior by
changing the session-level settings of these parameters; that is likely
to cause `postgres_fdw` to malfunction.

### Cross-Version Compatibility

`postgres_fdw` can be used with remote servers dating back
to PostgreSQL 8.3.  Read-only capability is available
back to 8.1.  A limitation however is that `postgres_fdw`
generally assumes that immutable built-in functions and operators are
safe to send to the remote server for execution, if they appear in a
`WHERE` clause for a foreign table.  Thus, a built-in
function that was added since the remote server's release might be sent
to it for execution, resulting in "function does not exist" or
a similar error.  This type of failure can be worked around by
rewriting the query, for example by embedding the foreign table
reference in a sub-`SELECT` with `OFFSET 0` as an
optimization fence, and placing the problematic function or operator
outside the sub-`SELECT`.

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

### Author

Shigeru Hanada shigeru.hanada@gmail.com

## seg — a datatype for line segments or floating point intervals

This module implements a data type `seg` for
representing line segments, or floating point intervals.
`seg` can represent uncertainty in the interval endpoints,
making it especially useful for representing laboratory measurements.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Rationale

The geometry of measurements is usually more complex than that of a
point in a numeric continuum. A measurement is usually a segment of
that continuum with somewhat fuzzy limits. The measurements come out
as intervals because of uncertainty and randomness, as well as because
the value being measured may naturally be an interval indicating some
condition, such as the temperature range of stability of a protein.

Using just common sense, it appears more convenient to store such data
as intervals, rather than pairs of numbers. In practice, it even turns
out more efficient in most applications.

Further along the line of common sense, the fuzziness of the limits
suggests that the use of traditional numeric data types leads to a
certain loss of information. Consider this: your instrument reads
6.50, and you input this reading into the database. What do you get
when you fetch it? Watch:

```
test=> select 6.50 :: float8 as "pH";
pH
---
6.5
(1 row)
```

In the world of measurements, 6.50 is not the same as 6.5. It may
sometimes be critically different. The experimenters usually write
down (and publish) the digits they trust. 6.50 is actually a fuzzy
interval contained within a bigger and even fuzzier interval, 6.5,
with their center points being (probably) the only common feature they
share. We definitely do not want such different data items to appear the
same.

Conclusion? It is nice to have a special data type that can record the
limits of an interval with arbitrarily variable precision. Variable in
the sense that each data element records its own precision.

Check this out:

```
test=> select '6.25 .. 6.50'::seg as "pH";
pH
------------
6.25 .. 6.50
(1 row)
```

### Syntax

The external representation of an interval is formed using one or two
floating-point numbers joined by the range operator (`..`
or `...`).  Alternatively, it can be specified as a
center point plus or minus a deviation.
Optional certainty indicators (`<`,
`>` or `~`) can be stored as well.
(Certainty indicators are ignored by all the built-in operators, however.)
[seg-repr-table](#seg-repr-table) gives an overview of allowed
representations; [seg-input-examples](#seg-input-examples) shows some
examples.

In [seg-repr-table](#seg-repr-table), `x`, `y`, and
`delta` denote
floating-point numbers.  `x` and `y`, but
not `delta`, can be preceded by a certainty indicator.

| ``x`` | Single value (zero-length interval) |
| --- | --- |
| ``x` .. `y`` | Interval from `x` to `y` |
| ``x` (+-) `delta`` | Interval from `x` - `delta` to       `x` + `delta` |
| ``x` ..` | Open interval with lower bound `x` |
| `.. `x`` | Open interval with upper bound `x` |

| `5.0` | Creates a zero-length segment (a point, if you will) |
| --- | --- |
| `~5.0` | Creates a zero-length segment and records        `~` in the data.  `~` is ignored        by `seg` operations, but        is preserved as a comment. |
| `5.0` | Creates a point at 5.0.  `>` is ignored but        is preserved as a comment. |
| `5(+-)0.3` | Creates an interval `4.7 .. 5.3`.         Note that the `(+-)` notation isn't preserved. |
| `50 .. ` | Everything that is greater than or equal to 50 |
| `.. 0` | Everything that is less than or equal to 0 |
| `1.5e-2 .. 2E-2 ` | Creates an interval `0.015 .. 0.02` |
| `1 ... 2` | The same as `1...2`, or `1 .. 2`,        or `1..2`        (spaces around the range operator are ignored) |

Because the `...` operator is widely used in data sources, it is allowed
as an alternative spelling of the `..` operator.  Unfortunately, this
creates a parsing ambiguity: it is not clear whether the upper bound
in `0...23` is meant to be `23` or `0.23`.
This is resolved by requiring at least one digit before the decimal
point in all numbers in `seg` input.

As a sanity check, `seg` rejects intervals with the lower bound
greater than the upper, for example `5 .. 2`.

### Precision

`seg` values are stored internally as pairs of 32-bit floating point
numbers. This means that numbers with more than 7 significant digits
will be truncated.

Numbers with 7 or fewer significant digits retain their
original precision. That is, if your query returns 0.00, you will be
sure that the trailing zeroes are not the artifacts of formatting: they
reflect the precision of the original data. The number of leading
zeroes does not affect precision: the value 0.0067 is considered to
have just 2 significant digits.

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

### Credits

Original author: Gene Selkov, Jr. selkovjr@mcs.anl.gov,
Mathematics and Computer Science Division, Argonne National Laboratory.

My thanks are primarily to Prof. Joe Hellerstein
([](https://dsf.berkeley.edu/jmh/)) for elucidating the
gist of the GiST ([](http://gist.cs.berkeley.edu/)). I am
also grateful to all Postgres developers, present and past, for enabling
myself to create my own world and live undisturbed in it. And I would like
to acknowledge my gratitude to Argonne Lab and to the U.S. Department of
Energy for the years of faithful support of my database research.

## sepgsql —
SELinux-, label-based mandatory access control (MAC) security module

`sepgsql` is a loadable module that supports label-based
mandatory access control (MAC) based on SELinux security
policy.

> **Warning:**

> The current implementation has significant limitations, and does not
> enforce mandatory access control for all actions.  See
> [sepgsql-limitations](#sepgsql-limitations).
>

### Overview

This module integrates with SELinux to provide an
additional layer of security checking above and beyond what is normally
provided by PostgreSQL.  From the perspective of
SELinux, this module allows
PostgreSQL to function as a user-space object
manager.  Each table or function access initiated by a DML query will be
checked against the system security policy.  This check is in addition to
the usual SQL permissions checking performed by
PostgreSQL.

SELinux access control decisions are made using
security labels, which are represented by strings such as
`system_u:object_r:sepgsql_table_t:s0`.  Each access control
decision involves two labels: the label of the subject attempting to
perform the action, and the label of the object on which the operation is
to be performed.  Since these labels can be applied to any sort of object,
access control decisions for objects stored within the database can be
(and, with this module, are) subjected to the same general criteria used
for objects of any other type, such as files.  This design is intended to
allow a centralized security policy to protect information assets
independent of the particulars of how those assets are stored.

The [`SECURITY LABEL`](#sql-security-label) statement allows assignment of
a security label to a database object.

### Installation

`sepgsql` can only be used on Linux
2.6.28 or higher with SELinux enabled.
It is not available on any other platform.  You will also need
libselinux 2.1.10 or higher and
selinux-policy 3.9.13 or higher (although some
distributions may backport the necessary rules into older policy
versions).

The `sestatus` command allows you to check the status of
SELinux.  A typical display is:

```
$ sestatus
SELinux status:                 enabled
SELinuxfs mount:                /selinux
Current mode:                   enforcing
Mode from config file:          enforcing
Policy version:                 24
Policy from config file:        targeted
```

If SELinux is disabled or not installed, you must set
that product up first before installing this module.

To build this module, include the option `--with-selinux` in
your PostgreSQL `configure` command.  Be sure that the
`libselinux-devel` RPM is installed at build time.

To use this module, you must include `sepgsql`
in the [guc-shared-preload-libraries](#guc-shared-preload-libraries) parameter in
`postgresql.conf`.  The module will not function correctly
if loaded in any other manner.  Once the module is loaded, you
should execute `sepgsql.sql` in each database.
This will install functions needed for security label management, and
assign initial security labels.

Here is an example showing how to initialize a fresh database cluster
with `sepgsql` functions and security labels installed.
Adjust the paths shown as appropriate for your installation:

```
$ export PGDATA=/path/to/data/directory
$ initdb
$ vi $PGDATA/postgresql.conf
change
#shared_preload_libraries = ''                # (change requires restart)
to
shared_preload_libraries = 'sepgsql'          # (change requires restart)
$ for DBNAME in template0 template1 postgres; do
postgres --single -F -c exit_on_error=true $DBNAME \
/dev/null
done
```

Please note that you may see some or all of the following notifications
depending on the particular versions you have of
libselinux and selinux-policy:

```
/etc/selinux/targeted/contexts/sepgsql_contexts:  line 33 has invalid object type db_blobs
/etc/selinux/targeted/contexts/sepgsql_contexts:  line 36 has invalid object type db_language
/etc/selinux/targeted/contexts/sepgsql_contexts:  line 37 has invalid object type db_language
/etc/selinux/targeted/contexts/sepgsql_contexts:  line 38 has invalid object type db_language
/etc/selinux/targeted/contexts/sepgsql_contexts:  line 39 has invalid object type db_language
/etc/selinux/targeted/contexts/sepgsql_contexts:  line 40 has invalid object type db_language
```

These messages are harmless and should be ignored.

If the installation process completes without error, you can now start the
server normally.

### Regression Tests

Due to the nature of SELinux, running the
regression tests for `sepgsql` requires several extra
configuration steps, some of which must be done as root.
The regression tests will not be run by an ordinary
`make check` or `make installcheck` command; you must
set up the configuration and then invoke the test script manually.
The tests must be run in the `contrib/sepgsql` directory
of a configured PostgreSQL build tree.  Although they require a build tree,
the tests are designed to be executed against an installed server,
that is they are comparable to `make installcheck` not
`make check`.

First, set up `sepgsql` in a working database
according to the instructions in [sepgsql-installation](#sepgsql-installation).
Note that the current operating system user must be able to connect to the
database as superuser without password authentication.

Second, build and install the policy package for the regression test.
The `sepgsql-regtest` policy is a special purpose policy package
which provides a set of rules to be allowed during the regression tests.
It should be built from the policy source file
`sepgsql-regtest.te`, which is done using
`make` with a Makefile supplied by SELinux.
You will need to locate the appropriate
Makefile on your system; the path shown below is only an example.
(This Makefile is usually supplied by the
`selinux-policy-devel` or
`selinux-policy` RPM.)
Once built, install this policy package using the
`semodule` command, which loads supplied policy packages
into the kernel.  If the package is correctly installed,
``semodule` -l` should list `sepgsql-regtest` as an
available policy package:

```
$ cd .../contrib/sepgsql
$ make -f /usr/share/selinux/devel/Makefile
$ sudo semodule -u sepgsql-regtest.pp
$ sudo semodule -l | grep sepgsql
sepgsql-regtest 1.07
```

Third, turn on `sepgsql_regression_test_mode`.
For security reasons, the rules in `sepgsql-regtest`
are not enabled by default;
the `sepgsql_regression_test_mode` parameter enables
the rules needed to launch the regression tests.
It can be turned on using the `setsebool` command:

```
$ sudo setsebool sepgsql_regression_test_mode on
$ getsebool sepgsql_regression_test_mode
sepgsql_regression_test_mode --> on
```

Fourth, verify your shell is operating in the `unconfined_t`
domain:

```
$ id -Z
unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
```

See [sepgsql-resources](#sepgsql-resources) for details on adjusting your
working domain, if necessary.

Finally, run the regression test script:

```
$ ./test_sepgsql
```

This script will attempt to verify that you have done all the configuration
steps correctly, and then it will run the regression tests for the
`sepgsql` module.

After completing the tests, it's recommended you disable
the `sepgsql_regression_test_mode` parameter:

```
$ sudo setsebool sepgsql_regression_test_mode off
```

You might prefer to remove the `sepgsql-regtest` policy
entirely:

```
$ sudo semodule -r sepgsql-regtest
```

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

### Features

#### Controlled Object Classes

The security model of SELinux describes all the access
control rules as relationships between a subject entity (typically,
a client of the database) and an object entity (such as a database
object), each of which is
identified by a security label.  If access to an unlabeled object is
attempted, the object is treated as if it were assigned the label
`unlabeled_t`.

Currently, `sepgsql` allows security labels to be
assigned to schemas, tables, columns, sequences, views, and functions.
When `sepgsql` is in use, security labels are
automatically assigned to supported database objects at creation time.
This label is called a default security label, and is decided according
to the system security policy, which takes as input the creator's label,
the label assigned to the new object's parent object and optionally name
of the constructed object.

A new database object basically inherits the security label of the parent
object, except when the security policy has special rules known as
type-transition rules, in which case a different label may be applied.
For schemas, the parent object is the current database; for tables,
sequences, views, and functions, it is the containing schema; for columns,
it is the containing table.

#### DML Permissions

For tables, `db_table:select`, `db_table:insert`,
`db_table:update` or `db_table:delete` are
checked for all the referenced target tables depending on the kind of
statement; in addition, `db_table:select` is also checked for
all the tables that contain columns referenced in the
`WHERE` or `RETURNING` clause, as a data source
for `UPDATE`, and so on.

Column-level permissions will also be checked for each referenced column.
`db_column:select` is checked on not only the columns being
read using `SELECT`, but those being referenced in other DML
statements; `db_column:update` or `db_column:insert`
will also be checked for columns being modified by `UPDATE` or
`INSERT`.

For example, consider:

```
UPDATE t1 SET x = 2, y = func1(y) WHERE z = 100;
```

Here, `db_column:update` will be checked for
`t1.x`, since it is being updated,
`db_column:{select update}` will be checked for
`t1.y`, since it is both updated and referenced, and
`db_column:select` will be checked for `t1.z`, since
it is only referenced.
`db_table:{select update}` will also be checked
at the table level.

For sequences, `db_sequence:get_value` is checked when we
reference a sequence object using `SELECT`; however, note that we
do not currently check permissions on execution of corresponding functions
such as `lastval()`.

For views, `db_view:expand` will be checked, then any other
required permissions will be checked on the objects being
expanded from the view, individually.

For functions, `db_procedure:{execute}` will be checked when
user tries to execute a function as a part of query, or using fast-path
invocation. If this function is a trusted procedure, it also checks
`db_procedure:{entrypoint}` permission to check whether it
can perform as entry point of trusted procedure.

In order to access any schema object, `db_schema:search`
permission is required on the containing schema.  When an object is
referenced without schema qualification, schemas on which this
permission is not present will not be searched (just as if the user did
not have `USAGE` privilege on the schema).  If an explicit schema
qualification is present, an error will occur if the user does not have
the requisite permission on the named schema.

The client must be allowed to access all referenced tables and
columns, even if they originated from views which were then expanded,
so that we apply consistent access control rules independent of the manner
in which the table contents are referenced.

The default database privilege system allows database superusers to
modify system catalogs using DML commands, and reference or modify
toast tables.  These operations are prohibited when
`sepgsql` is enabled.

#### DDL Permissions

SELinux defines several permissions to control common
operations for each object type; such as creation, alter, drop and
relabel of security label. In addition, several object types have
special permissions to control their characteristic operations; such as
addition or deletion of name entries within a particular schema.

Creating a new database object requires `create` permission.
SELinux will grant or deny this permission based on the
client's security label and the proposed security label for the new
object.  In some cases, additional privileges are required:

- [`CREATE DATABASE`](#sql-createdatabase) additionally requires
`getattr` permission for the source or template database.
- Creating a schema object additionally requires `add_name`
permission on the parent schema.
- Creating a table additionally requires permission to create each
individual table column, just as if each table column were a
separate top-level object.
- Creating a function marked as `LEAKPROOF` additionally
requires `install` permission.  (This permission is also
checked when `LEAKPROOF` is set for an existing function.)

When `DROP` command is executed, `drop` will be
checked on the object being removed.  Permissions will be also checked for
objects dropped indirectly via `CASCADE`.  Deletion of objects
contained within a particular schema (tables, views, sequences and
procedures) additionally requires `remove_name` on the schema.

When `ALTER` command is executed, `setattr` will be
checked on the object being modified for each object types, except for
subsidiary objects such as the indexes or triggers of a table, where
permissions are instead checked on the parent object.  In some cases,
additional permissions are required:

- Moving an object to a new schema additionally requires
`remove_name` permission on the old schema and
`add_name` permission on the new one.
- Setting the `LEAKPROOF` attribute on a function requires
`install` permission.
- Using [`SECURITY LABEL`](#sql-security-label) on an object additionally
requires `relabelfrom` permission for the object in
conjunction with its old security label and `relabelto`
permission for the object in conjunction with its new security label.
(In cases where multiple label providers are installed and the user
tries to set a security label, but it is not managed by
SELinux, only `setattr` should be checked here.
This is currently not done due to implementation restrictions.)

#### Trusted Procedures

Trusted procedures are similar to security definer functions or setuid
commands. SELinux provides a feature to allow trusted
code to run using a security label different from that of the client,
generally for the purpose of providing highly controlled access to
sensitive data (e.g., rows might be omitted, or the precision of stored
values might be reduced).  Whether or not a function acts as a trusted
procedure is controlled by its security label and the operating system
security policy.  For example:

```
postgres=# CREATE TABLE customer (
cid     int primary key,
cname   text,
credit  text
);
CREATE TABLE
postgres=# SECURITY LABEL ON COLUMN customer.credit
IS 'system_u:object_r:sepgsql_secret_table_t:s0';
SECURITY LABEL
postgres=# CREATE FUNCTION show_credit(int) RETURNS text
AS 'SELECT regexp_replace(credit, ''-[0-9]+$'', ''-xxxx'', ''g'')
FROM customer WHERE cid = $1'
LANGUAGE sql;
CREATE FUNCTION
postgres=# SECURITY LABEL ON FUNCTION show_credit(int)
IS 'system_u:object_r:sepgsql_trusted_proc_exec_t:s0';
SECURITY LABEL
```

The above operations should be performed by an administrative user.

```
postgres=# SELECT * FROM customer;
ERROR:  SELinux: security policy violation
postgres=# SELECT cid, cname, show_credit(cid) FROM customer;
cid | cname  |     show_credit
-----+--------+---------------------
1 | taro   | 1111-2222-3333-xxxx
2 | hanako | 5555-6666-7777-xxxx
(2 rows)
```

In this case, a regular user cannot reference `customer.credit`
directly, but a trusted procedure `show_credit` allows the user
to print the credit card numbers of customers with some of the digits
masked out.

#### Dynamic Domain Transitions

It is possible to use SELinux's dynamic domain transition feature
to switch the security label of the client process, the client domain,
to a new context, if that is allowed by the security policy.
The client domain needs the `setcurrent` permission and also
`dyntransition` from the old to the new domain.

Dynamic domain transitions should be considered carefully, because they
allow users to switch their label, and therefore their privileges,
at their option, rather than (as in the case of a trusted procedure)
as mandated by the system.
Thus, the `dyntransition` permission is only considered
safe when used to switch to a domain with a smaller set of privileges than
the original one. For example:

```
regression=# select sepgsql_getcon();
sepgsql_getcon
-------------------------------------------------------
unconfined_u:unconfined_r:unconfined_t:s0-s0:c0.c1023
(1 row)

regression=# SELECT sepgsql_setcon('unconfined_u:unconfined_r:unconfined_t:s0-s0:c1.c4');
sepgsql_setcon
----------------
t
(1 row)

regression=# SELECT sepgsql_setcon('unconfined_u:unconfined_r:unconfined_t:s0-s0:c1.c1023');
ERROR:  SELinux: security policy violation
```

In this example above we were allowed to switch from the larger MCS
range `c1.c1023` to the smaller range `c1.c4`, but
switching back was denied.

A combination of dynamic domain transition and trusted procedure
enables an interesting use case that fits the typical process life-cycle
of connection pooling software.
Even if your connection pooling software is not allowed to run most
of SQL commands, you can allow it to switch the security label
of the client using the `sepgsql_setcon()` function
from within a trusted procedure; that should take some
credential to authorize the request to switch the client label.
After that, this session will have the privileges of the target user,
rather than the connection pooler.
The connection pooler can later revert the security label change by
again using `sepgsql_setcon()` with
`NULL` argument, again invoked from within a trusted
procedure with appropriate permissions checks.
The point here is that only the trusted procedure actually has permission
to change the effective security label, and only does so when given proper
credentials.  Of course, for secure operation, the credential store
(table, procedure definition, or whatever) must be protected from
unauthorized access.

#### Miscellaneous

We reject the [`LOAD`](#sql-load) command across the board, because
any module loaded could easily circumvent security policy enforcement.

### Sepgsql Functions

[sepgsql-functions-table](#sepgsql-functions-table) shows the available functions.

| Function                         Description |
| --- |
| `sepgsql_getcon` ()         text                         Returns the client domain, the current security label of the client. |
| `sepgsql_setcon` ( `text` )         boolean                         Switches the client domain of the current session to the new domain,         if allowed by the security policy.         It also accepts `NULL` input as a request to transition         to the client's original domain. |
| `sepgsql_mcstrans_in` ( `text` )         text                         Translates the given qualified MLS/MCS range into raw format if         the mcstrans daemon is running. |
| `sepgsql_mcstrans_out` ( `text` )         text                         Translates the given raw MLS/MCS range into qualified format if         the mcstrans daemon is running. |
| `sepgsql_restorecon` ( `text` )         boolean                         Sets up initial security labels for all objects within the         current database. The argument may be `NULL`, or the         name of a specfile to be used as alternative of the system default. |

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

### External Resources

**[SE-PostgreSQL Introduction](https://wiki.postgresql.org/wiki/SEPostgreSQL)**
: This wiki page provides a brief overview, security design, architecture,
administration and upcoming features.

**[SELinux User's and Administrator's Guide](https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html/selinux_users_and_administrators_guide/index)**
: This document provides a wide spectrum of knowledge to administer
SELinux on your systems.
It focuses primarily on Red Hat operating systems, but is not limited to them.

**[Fedora SELinux FAQ](https://fedoraproject.org/wiki/SELinux_FAQ)**
: This document answers frequently asked questions about
SELinux.
It focuses primarily on Fedora, but is not limited to Fedora.

### Author

KaiGai Kohei kaigai@ak.jp.nec.com

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

## sslinfo — obtain client SSL information

The `sslinfo` module provides information about the SSL
certificate that the current client provided when connecting to
PostgreSQL.  The module is useless (most functions
will return NULL) if the current connection does not use SSL.

Some of the information available through this module can also be obtained
using the built-in system view [
`pg_stat_ssl`](#monitoring-pg-stat-ssl-view).

This extension won't build at all unless the installation was
configured with `--with-ssl=openssl`.

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

### Author

Victor Wagner vitus@cryptocom.ru, Cryptocom LTD

Dmitry Voronin carriingfate92@yandex.ru

E-Mail of Cryptocom OpenSSL development group:
openssl@cryptocom.ru

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

## tcn — a trigger function to notify listeners of changes to table content

The `tcn` module provides a trigger function that notifies
listeners of changes to any table on which it is attached.  It must be
used as an `AFTER` trigger `FOR EACH ROW`.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

Only one parameter may be supplied to the function in a
`CREATE TRIGGER` statement, and that is optional.  If supplied
it will be used for the channel name for the notifications.  If omitted
`tcn` will be used for the channel name.

The payload of the notifications consists of the table name, a letter to
indicate which type of operation was performed, and column name/value pairs
for primary key columns.  Each part is separated from the next by a comma.
For ease of parsing using regular expressions, table and column names are
always wrapped in double quotes, and data values are always wrapped in
single quotes.  Embedded quotes are doubled.

A brief example of using the extension follows.

```
test=# create table tcndata
test-#   (
test(#     a int not null,
test(#     b date not null,
test(#     c text,
test(#     primary key (a, b)
test(#   );
CREATE TABLE
test=# create trigger tcndata_tcn_trigger
test-#   after insert or update or delete on tcndata
test-#   for each row execute function triggered_change_notification();
CREATE TRIGGER
test=# listen tcn;
LISTEN
test=# insert into tcndata values (1, date '2012-12-22', 'one'),
test-#                            (1, date '2012-12-23', 'another'),
test-#                            (2, date '2012-12-23', 'two');
INSERT 0 3
Asynchronous notification "tcn" with payload ""tcndata",I,"a"='1',"b"='2012-12-22'" received from server process with PID 22770.
Asynchronous notification "tcn" with payload ""tcndata",I,"a"='1',"b"='2012-12-23'" received from server process with PID 22770.
Asynchronous notification "tcn" with payload ""tcndata",I,"a"='2',"b"='2012-12-23'" received from server process with PID 22770.
test=# update tcndata set c = 'uno' where a = 1;
UPDATE 2
Asynchronous notification "tcn" with payload ""tcndata",U,"a"='1',"b"='2012-12-22'" received from server process with PID 22770.
Asynchronous notification "tcn" with payload ""tcndata",U,"a"='1',"b"='2012-12-23'" received from server process with PID 22770.
test=# delete from tcndata where a = 1 and b = date '2012-12-22';
DELETE 1
Asynchronous notification "tcn" with payload ""tcndata",D,"a"='1',"b"='2012-12-22'" received from server process with PID 22770.
```

## test_decoding — SQL-based test/example module for WAL logical decoding

`test_decoding` is an example of a logical decoding
output plugin. It doesn't do anything especially useful, but can serve as
a starting point for developing your own output plugin.

`test_decoding` receives WAL through the logical decoding
mechanism and decodes it into text representations of the operations
performed.

Typical output from this plugin, used over the SQL logical decoding
interface, might be:

```
postgres=# SELECT * FROM pg_logical_slot_get_changes('test_slot', NULL, NULL, 'include-xids', '0');
lsn     | xid |                       data
-----------+-----+--------------------------------------------------
0/16D30F8 | 691 | BEGIN
0/16D32A0 | 691 | table public.data: INSERT: id[int4]:2 data[text]:'arg'
0/16D32A0 | 691 | table public.data: INSERT: id[int4]:3 data[text]:'demo'
0/16D32A0 | 691 | COMMIT
0/16D32D8 | 692 | BEGIN
0/16D3398 | 692 | table public.data: DELETE: id[int4]:2
0/16D3398 | 692 | table public.data: DELETE: id[int4]:3
0/16D3398 | 692 | COMMIT
(8 rows)
```

We can also get the changes of the in-progress transaction, and the typical
output might be:

```
postgres[33712]=#* SELECT * FROM pg_logical_slot_get_changes('test_slot', NULL, NULL, 'stream-changes', '1');
lsn    | xid |                       data
-----------+-----+--------------------------------------------------
0/16B21F8 | 503 | opening a streamed block for transaction TXN 503
0/16B21F8 | 503 | streaming change for TXN 503
0/16B2300 | 503 | streaming change for TXN 503
0/16B2408 | 503 | streaming change for TXN 503
0/16BEBA0 | 503 | closing a streamed block for transaction TXN 503
0/16B21F8 | 503 | opening a streamed block for transaction TXN 503
0/16BECA8 | 503 | streaming change for TXN 503
0/16BEDB0 | 503 | streaming change for TXN 503
0/16BEEB8 | 503 | streaming change for TXN 503
0/16BEBA0 | 503 | closing a streamed block for transaction TXN 503
(10 rows)
```

## tsm_system_rows —
the `SYSTEM_ROWS` sampling method for `TABLESAMPLE`

The `tsm_system_rows` module provides the table sampling method
`SYSTEM_ROWS`, which can be used in
the `TABLESAMPLE` clause of a [`SELECT`](#sql-select)
command.

This table sampling method accepts a single integer argument that is the
maximum number of rows to read.  The resulting sample will always contain
exactly that many rows, unless the table does not contain enough rows, in
which case the whole table is selected.

Like the built-in `SYSTEM` sampling
method, `SYSTEM_ROWS` performs block-level sampling, so
that the sample is not completely random but may be subject to clustering
effects, especially if only a small number of rows are requested.

`SYSTEM_ROWS` does not support
the `REPEATABLE` clause.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

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

## tsm_system_time —
the `SYSTEM_TIME` sampling method for `TABLESAMPLE`

The `tsm_system_time` module provides the table sampling method
`SYSTEM_TIME`, which can be used in
the `TABLESAMPLE` clause of a [`SELECT`](#sql-select)
command.

This table sampling method accepts a single floating-point argument that
is the maximum number of milliseconds to spend reading the table.  This
gives you direct control over how long the query takes, at the price that
the size of the sample becomes hard to predict.  The resulting sample will
contain as many rows as could be read in the specified time, unless the
whole table has been read first.

Like the built-in `SYSTEM` sampling
method, `SYSTEM_TIME` performs block-level sampling, so
that the sample is not completely random but may be subject to clustering
effects, especially if only a small number of rows are selected.

`SYSTEM_TIME` does not support
the `REPEATABLE` clause.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

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

## uuid-ossp — a UUID generator

The `uuid-ossp` module provides functions to generate universally
unique identifiers (UUIDs) using one of several standard algorithms.  There
are also functions to produce certain special UUID constants.
This module is only necessary for special requirements beyond what is
available in core PostgreSQL.  See [functions-uuid](#functions-uuid) for built-in ways to generate UUIDs.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

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

### Building `uuid-ossp`

Historically this module depended on the OSSP UUID library, which accounts
for the module's name.  While the OSSP UUID library can still be found
at [](http://www.ossp.org/pkg/lib/uuid/), it is not well
maintained, and is becoming increasingly difficult to port to newer
platforms.  `uuid-ossp` can now be built without the OSSP
library on some platforms.  On FreeBSD and some other BSD-derived
platforms, suitable UUID creation functions are included in the
core `libc` library.  On Linux, macOS, and some other
platforms, suitable functions are provided in the `libuuid`
library, which originally came from the `e2fsprogs` project
(though on modern Linux it is considered part
of `util-linux-ng`).  When invoking `configure`,
specify --with-uuid=bsd` to use the BSD functions,
or `--with-uuid=e2fs` to
use `e2fsprogs`' `libuuid`, or
`--with-uuid=ossp` to use the OSSP UUID library.
More than one of these libraries might be available on a particular
machine, so `configure` does not automatically choose one.

### Author

Peter Eisentraut peter_e@gmx.net

## xml2 — XPath querying and XSLT functionality

The `xml2` module provides XPath querying and
XSLT functionality.

### Deprecation Notice

From PostgreSQL 8.3 on, there is XML-related
functionality based on the SQL/XML standard in the core server.
That functionality covers XML syntax checking and XPath queries,
which is what this module does, and more, but the API is
not at all compatible.  It is planned that this module will be
removed in a future version of PostgreSQL in favor of the newer standard API, so
you are encouraged to try converting your applications.  If you
find that some of the functionality of this module is not
available in an adequate form with the newer API, please explain
your issue to pgsql-hackers@lists.postgresql.org so that the deficiency
can be addressed.

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

### `xpath_table`

```
xpath_table(text key, text document, text relation, text xpaths, text criteria) returns setof record
```

`xpath_table` is a table function that evaluates a set of XPath
queries on each of a set of documents and returns the results as a
table. The primary key field from the original document table is returned
as the first column of the result so that the result set
can readily be used in joins.  The parameters are described in
[xml2-xpath-table-parameters](#xml2-xpath-table-parameters).

| Parameter | Description |
| --- | --- |
| key | the name of the "key" field — this is just a field to be used as         the first column of the output table, i.e., it identifies the record from         which each output row came (see note below about multiple values) |
| document | the name of the field containing the XML document |
| relation | the name of the table or view containing the documents |
| xpaths | one or more XPath expressions, separated by `|` |
| criteria | the contents of the WHERE clause. This cannot be omitted, so use         `true` or `1=1` if you want to         process all the rows in the relation |

These parameters (except the XPath strings) are just substituted
into a plain SQL SELECT statement, so you have some flexibility — the
statement is

`
SELECT <key>, <document> FROM <relation> WHERE <criteria>
`

so those parameters can be *anything* valid in those particular
locations. The result from this SELECT needs to return exactly two
columns (which it will unless you try to list multiple fields for key
or document). Beware that this simplistic approach requires that you
validate any user-supplied values to avoid SQL injection attacks.

The function has to be used in a `FROM` expression, with an
`AS` clause to specify the output columns; for example

```
SELECT * FROM
xpath_table('article_id',
'article_xml',
'articles',
'/article/author|/article/pages|/article/title',
'date_entered > ''2003-01-01'' ')
AS t(article_id integer, author text, page_count integer, title text);
```

The `AS` clause defines the names and types of the columns in the
output table.  The first is the "key" field and the rest correspond
to the XPath queries.
If there are more XPath queries than result columns,
the extra queries will be ignored. If there are more result columns
than XPath queries, the extra columns will be NULL.

Notice that this example defines the `page_count` result
column as an integer.  The function deals internally with string
representations, so when you say you want an integer in the output, it will
take the string representation of the XPath result and use PostgreSQL input
functions to transform it into an integer (or whatever type the `AS`
clause requests). An error will result if it can't do this — for
example if the result is empty — so you may wish to just stick to
`text` as the column type if you think your data has any problems.

The calling `SELECT` statement doesn't necessarily have to be
just `SELECT *` — it can reference the output
columns by name or join them to other tables. The function produces a
virtual table with which you can perform any operation you wish (e.g.,
aggregation, joining, sorting etc.). So we could also have:

```
SELECT t.title, p.fullname, p.email
FROM xpath_table('article_id', 'article_xml', 'articles',
'/article/title|/article/author/@id',
'xpath_string(article_xml,''/article/@date'') > ''2003-03-20'' ')
AS t(article_id integer, title text, author_id integer),
tblPeopleInfo AS p
WHERE t.author_id = p.person_id;
```

as a more complicated example. Of course, you could wrap all
of this in a view for convenience.

#### Multivalued Results

The `xpath_table` function assumes that the results of each XPath query
might be multivalued, so the number of rows returned by the function
may not be the same as the number of input documents. The first row
returned contains the first result from each query, the second row the
second result from each query. If one of the queries has fewer values
than the others, null values will be returned instead.

In some cases, a user will know that a given XPath query will return
only a single result (perhaps a unique document identifier) — if used
alongside an XPath query returning multiple results, the single-valued
result will appear only on the first row of the result. The solution
to this is to use the key field as part of a join against a simpler
XPath query. As an example:

```
CREATE TABLE test (
id int PRIMARY KEY,
xml text
);

INSERT INTO test VALUES (1, '
123
112233
');

INSERT INTO test VALUES (2, '
111222333
111222333
');

SELECT * FROM
xpath_table('id','xml','test',
'/doc/@num|/doc/line/@num|/doc/line/a|/doc/line/b|/doc/line/c',
'true')
AS t(id int, doc_num varchar(10), line_num varchar(10), val1 int, val2 int, val3 int)
WHERE id = 1 ORDER BY doc_num, line_num

id | doc_num | line_num | val1 | val2 | val3
----+---------+----------+------+------+------
1 | C1      | L1       |    1 |    2 |    3
1 |         | L2       |   11 |   22 |   33
```

To get `doc_num` on every line, the solution is to use two invocations
of `xpath_table` and join the results:

```
SELECT t.*,i.doc_num FROM
xpath_table('id', 'xml', 'test',
'/doc/line/@num|/doc/line/a|/doc/line/b|/doc/line/c',
'true')
AS t(id int, line_num varchar(10), val1 int, val2 int, val3 int),
xpath_table('id', 'xml', 'test', '/doc/@num', 'true')
AS i(id int, doc_num varchar(10))
WHERE i.id=t.id AND i.id=1
ORDER BY doc_num, line_num;

id | line_num | val1 | val2 | val3 | doc_num
----+----------+------+------+------+---------
1 | L1       |    1 |    2 |    3 | C1
1 | L2       |   11 |   22 |   33 | C1
(2 rows)
```

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

### Author

John Gray jgray@azuli.co.uk

Development of this module was sponsored by Torchbox Ltd. (www.torchbox.com).
It has the same BSD license as PostgreSQL.

## Additional Supplied Programs

This appendix and the previous one contain information regarding the modules that
can be found in the `contrib` directory of the
PostgreSQL distribution.  See [contrib](#contrib) for
more information about the `contrib` section in general and
server extensions and plug-ins found in `contrib`
specifically.

This appendix covers utility programs found in `contrib`.
Once installed, either from source or a packaging system, they are found in
the `bin` directory of the
PostgreSQL installation and can be used like any
other program.

## Client Applications

This section covers PostgreSQL client
applications in `contrib`.  They can be run from anywhere,
independent of where the database server resides.  See
also [reference-client](#reference-client) for information about client
applications that are part of the core PostgreSQL
distribution.

oid2name
1
Application

oid2name
resolve OIDs and file nodes in a PostgreSQL data directory

`oid2name`
`option`

## Description

oid2name is a utility program that helps administrators to
examine the file structure used by PostgreSQL.  To make use of it, you need
to be familiar with the database file structure, which is described in
[storage](#storage).

> **Note:**

> The name "oid2name" is historical, and is actually rather
> misleading, since most of the time when you use it, you will really
> be concerned with tables' filenode numbers (which are the file names
> visible in the database directories).  Be sure you understand the
> difference between table OIDs and table filenodes!
>

oid2name connects to a target database and
extracts OID, filenode, and/or table name information.  You can also have
it show database OIDs or tablespace OIDs.

## Options

oid2name accepts the following command-line arguments:

**`-f `filenode``**
: show info for table with filenode `filenode`.

**`-i`**
: include indexes and sequences in the listing.

**`-o `oid``**
: show info for table with OID `oid`.

**`-q`**
: omit headers (useful for scripting).

**`-s`**
: show tablespace OIDs.

**`-S`**
: include system objects (those in
`information_schema`, `pg_toast`
and `pg_catalog` schemas).

**`-t `tablename_pattern``**
: show info for table(s) matching `tablename_pattern`.

**`-V`**
: Print the oid2name version and exit.

**`-x`**
: display more information about each object shown: tablespace name,
schema name, and OID.

**`-?`**
: Show help about oid2name command line
arguments, and exit.

oid2name also accepts the following command-line
arguments for connection parameters:

**`-d `database``**
: database to connect to.

**`-h `host``**
: database server's host.

**`-H `host``**
: database server's host.  Use of this parameter is
*deprecated* as of
PostgreSQL 12.

**`-p `port``**
: database server's port.

**`-U `username``**
: user name to connect as.

To display specific tables, select which tables to show by
using `-o`, `-f` and/or `-t`.
`-o` takes an OID,
`-f` takes a filenode,
and `-t` takes a table name (actually, it's a `LIKE`
pattern, so you can use things like `foo%`).
You can use as many
of these options as you like, and the listing will include all objects
matched by any of the options.  But note that these options can only
show objects in the database given by `-d`.

If you don't give any of `-o`, `-f` or `-t`,
but do give `-d`, it will list all tables in the database
named by `-d`.  In this mode, the `-S` and
`-i` options control what gets listed.

If you don't give `-d` either, it will show a listing of database
OIDs.  Alternatively you can give `-s` to get a tablespace
listing.

## Environment

**`PGHOST`**
: Default connection parameters.

This utility, like most other PostgreSQL
utilities, also uses the environment variables supported by
libpq (see [libpq-envars](#libpq-envars)).

The environment variable `PG_COLOR` specifies whether to use
color in diagnostic messages. Possible values are
`always`, `auto` and
`never`.

## Notes

oid2name requires a running database server with
non-corrupt system catalogs.  It is therefore of only limited use
for recovering from catastrophic database corruption situations.

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

## Author

B. Palmer bpalmer@crimelabs.net

vacuumlo
1
Application

vacuumlo
remove orphaned large objects from a PostgreSQL database

`vacuumlo`
`option`
`dbname`

## Description

vacuumlo is a simple utility program that will remove any
"orphaned" large objects from a
PostgreSQL database.  An orphaned large object (LO) is
considered to be any LO whose OID does not appear in any `oid` or
`lo` data column of the database.

If you use this, you may also be interested in the `lo_manage`
trigger in the [lo](#lo) module.
`lo_manage` is useful to try
to avoid creating orphaned LOs in the first place.

All databases named on the command line are processed.

## Options

vacuumlo accepts the following command-line arguments:

**`-l `limit``**
: Remove no more than `limit` large objects per
transaction (default 1000).  Since the server acquires a lock per LO
removed, removing too many LOs in one transaction risks exceeding
[guc-max-locks-per-transaction](#guc-max-locks-per-transaction).  Set the limit to
zero if you want all removals done in a single transaction.

**`-n`**
: Don't remove anything, just show what would be done.

**`-v`**
: Write a lot of progress messages.

**`-V`**
: Print the vacuumlo version and exit.

**`-?`**
: Show help about vacuumlo command line
arguments, and exit.

vacuumlo also accepts the following command-line
arguments for connection parameters:

**`-h `host``**
: Database server's host.

**`-p `port``**
: Database server's port.

**`-U `username``**
: User name to connect as.

**`-w`**
: Never issue a password prompt.  If the server requires password
authentication and a password is not available by other means
such as a `.pgpass` file, the connection
attempt will fail.  This option can be useful in batch jobs and
scripts where no user is present to enter a password.

**`-W`**
: Force vacuumlo to prompt for a
password before connecting to a database.

This option is never essential, since
vacuumlo will automatically prompt
for a password if the server demands password authentication.
However, vacuumlo will waste a
connection attempt finding out that the server wants a password.
In some cases it is worth typing `-W` to avoid the extra
connection attempt.

## Environment

**`PGHOST`**
: Default connection parameters.

This utility, like most other PostgreSQL utilities,
also uses the environment variables supported by libpq
(see [libpq-envars](#libpq-envars)).

The environment variable `PG_COLOR` specifies whether to use
color in diagnostic messages. Possible values are
`always`, `auto` and
`never`.

## Notes

vacuumlo works by the following method:
First, vacuumlo builds a temporary table which contains all
of the OIDs of the large objects in the selected database.  It then scans
through all columns in the database that are of type
`oid` or `lo`, and removes matching entries from the temporary
table.  (Note: Only types with these names are considered; in particular,
domains over them are not considered.)  The remaining entries in the
temporary table identify orphaned LOs.  These are removed.

## Author

Peter Mount peter@retep.org.uk

## Server Applications

Some applications run on the PostgreSQL server
itself.  Currently, no such applications are included in the
`contrib` directory.  See also [reference-server](#reference-server) for information about server applications that
are part of the core PostgreSQL distribution.
