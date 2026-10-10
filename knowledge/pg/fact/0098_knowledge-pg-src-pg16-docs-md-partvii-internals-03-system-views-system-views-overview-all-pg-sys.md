# Overview; all pg_* system views

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVII_internals/03_system_views.md`
- Source Title: `System Views`
- Source Heading Path: `System Views > Overview; all pg_* system views`
- Source Line Ranges: `1-1127`
- Chunk ID: `pg16_fact_0098_ed582eedfd`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `11159d43123013ef34b0d8f44ec7a7640c6f2e7505487882b3b21448ee1ddb10`

## Retrieval Guidance

- Use When: Look up PostgreSQL system view columns and meanings.
- Retrieval Keywords: system views, pg_locks, pg_settings, pg_file_settings, pg_hba_file_rules, pg_stats, pg_replication_slots, pg_statistic views
- Follow-up Guidance: Pair view-field reference with separate guide records when using values as incident evidence.
- Classification Note: Per instruction, system views are classified as fact even when views such as pg_locks, pg_settings, pg_file_settings, or pg_stats are useful for inspection.

## Official Source Content

# System Views

In addition to the system catalogs, PostgreSQL
provides a number of built-in views.  Some system views provide convenient
access to some commonly used queries on the system catalogs.  Other views
provide access to internal server state.

The information schema ([information-schema](#information-schema)) provides
an alternative set of views which overlap the functionality of the system
views.  Since the information schema is SQL-standard whereas the views
described here are PostgreSQL-specific,
it's usually better to use the information schema if it provides all
the information you need.

[view-table](#view-table) lists the system views described here.
More detailed documentation of each view follows below.
There are some additional views that provide access to accumulated
statistics; they are described in
[monitoring-stats-views-table](#monitoring-stats-views-table).

## Overview

[view-table](#view-table) lists the system views.
More detailed documentation of each catalog follows below.
Except where noted, all the views described here are read-only.

| View Name | Purpose |
| --- | --- |
| [`pg_available_extensions`](#view-pg-available-extensions) | available extensions |
| [`pg_available_extension_versions`](#view-pg-available-extension-versions) | available versions of extensions |
| [`pg_backend_memory_contexts`](#view-pg-backend-memory-contexts) | backend memory contexts |
| [`pg_config`](#view-pg-config) | compile-time configuration parameters |
| [`pg_cursors`](#view-pg-cursors) | open cursors |
| [`pg_file_settings`](#view-pg-file-settings) | summary of configuration file contents |
| [`pg_group`](#view-pg-group) | groups of database users |
| [`pg_hba_file_rules`](#view-pg-hba-file-rules) | summary of client authentication configuration file contents |
| [`pg_ident_file_mappings`](#view-pg-ident-file-mappings) | summary of client user name mapping configuration file contents |
| [`pg_indexes`](#view-pg-indexes) | indexes |
| [`pg_locks`](#view-pg-locks) | locks currently held or awaited |
| [`pg_matviews`](#view-pg-matviews) | materialized views |
| [`pg_policies`](#view-pg-policies) | policies |
| [`pg_prepared_statements`](#view-pg-prepared-statements) | prepared statements |
| [`pg_prepared_xacts`](#view-pg-prepared-xacts) | prepared transactions |
| [`pg_publication_tables`](#view-pg-publication-tables) | publications and information of their associated tables |
| [`pg_replication_origin_status`](#view-pg-replication-origin-status) | information about replication origins, including replication progress |
| [`pg_replication_slots`](#view-pg-replication-slots) | replication slot information |
| [`pg_roles`](#view-pg-roles) | database roles |
| [`pg_rules`](#view-pg-rules) | rules |
| [`pg_seclabels`](#view-pg-seclabels) | security labels |
| [`pg_sequences`](#view-pg-sequences) | sequences |
| [`pg_settings`](#view-pg-settings) | parameter settings |
| [`pg_shadow`](#view-pg-shadow) | database users |
| [`pg_shmem_allocations`](#view-pg-shmem-allocations) | shared memory allocations |
| [`pg_stats`](#view-pg-stats) | planner statistics |
| [`pg_stats_ext`](#view-pg-stats-ext) | extended planner statistics |
| [`pg_stats_ext_exprs`](#view-pg-stats-ext-exprs) | extended planner statistics for expressions |
| [`pg_tables`](#view-pg-tables) | tables |
| [`pg_timezone_abbrevs`](#view-pg-timezone-abbrevs) | time zone abbreviations |
| [`pg_timezone_names`](#view-pg-timezone-names) | time zone names |
| [`pg_user`](#view-pg-user) | database users |
| [`pg_user_mappings`](#view-pg-user-mappings) | user mappings |
| [`pg_views`](#view-pg-views) | views |

## `pg_available_extensions`

The `pg_available_extensions` view lists the
extensions that are available for installation.
See also the
[`pg_extension`](#catalog-pg-extension)
catalog, which shows the extensions currently installed.

| Column Type                      Description |
| --- |
| `name` `name`                      Extension name |
| `default_version` `text`                      Name of default version, or `NULL` if none is        specified |
| `installed_version` `text`                      Currently installed version of the extension,        or `NULL` if not installed |
| `comment` `text`                      Comment string from the extension's control file |

The `pg_available_extensions` view is read-only.

## `pg_available_extension_versions`

The `pg_available_extension_versions` view lists the
specific extension versions that are available for installation.
See also the [`pg_extension`](#catalog-pg-extension)
catalog, which shows the extensions currently installed.

| Column Type                      Description |
| --- |
| `name` `name`                      Extension name |
| `version` `text`                      Version name |
| `installed` `bool`                      True if this version of this extension is currently        installed |
| `superuser` `bool`                      True if only superusers are allowed to install this extension        (but see `trusted`) |
| `trusted` `bool`                      True if the extension can be installed by non-superusers        with appropriate privileges |
| `relocatable` `bool`                      True if extension can be relocated to another schema |
| `schema` `name`                      Name of the schema that the extension must be installed into,        or `NULL` if partially or fully relocatable |
| `requires` `name[]`                      Names of prerequisite extensions,        or `NULL` if none |
| `comment` `text`                      Comment string from the extension's control file |

The `pg_available_extension_versions` view is
read-only.

## `pg_backend_memory_contexts`

The view `pg_backend_memory_contexts` displays all
the memory contexts of the server process attached to the current session.

`pg_backend_memory_contexts` contains one row
for each memory context.

| Column Type                      Description |
| --- |
| `name` `text`                      Name of the memory context |
| `ident` `text`                      Identification information of the memory context. This field is truncated at 1024 bytes |
| `parent` `text`                      Name of the parent of this memory context |
| `level` `int4`                      Distance from TopMemoryContext in context tree |
| `total_bytes` `int8`                      Total bytes allocated for this memory context |
| `total_nblocks` `int8`                      Total number of blocks allocated for this memory context |
| `free_bytes` `int8`                      Free space in bytes |
| `free_chunks` `int8`                      Total number of free chunks |
| `used_bytes` `int8`                      Used space in bytes |

By default, the `pg_backend_memory_contexts` view can be
read only by superusers or roles with the privileges of the
`pg_read_all_stats` role.

## `pg_config`

The view `pg_config` describes the
compile-time configuration parameters of the currently installed
version of PostgreSQL. It is intended, for example, to
be used by software packages that want to interface to
PostgreSQL to facilitate finding the required header
files and libraries. It provides the same basic information as the
[app-pgconfig](#app-pgconfig) PostgreSQL client
application.

By default, the `pg_config` view can be read
only by superusers.

| Column Type                      Description |
| --- |
| `name` `text`                      The parameter name |
| `setting` `text`                      The parameter value |

## `pg_cursors`

The `pg_cursors` view lists the cursors that
are currently available. Cursors can be defined in several ways:

- via the [`DECLARE`](#sql-declare)
statement in SQL
- via the Bind message in the frontend/backend protocol, as
described in [protocol-flow-ext-query](#protocol-flow-ext-query)
- via the Server Programming Interface (SPI), as described in
[spi-interface](#spi-interface)

The `pg_cursors` view displays cursors
created by any of these means. Cursors only exist for the duration
of the transaction that defines them, unless they have been
declared `WITH HOLD`. Therefore non-holdable
cursors are only present in the view until the end of their
creating transaction.

> **Note:**

> Cursors are used internally to implement some of the components
> of PostgreSQL, such as procedural languages.
> Therefore, the `pg_cursors` view might include cursors
> that have not been explicitly created by the user.
>

| Column Type                      Description |
| --- |
| `name` `text`                      The name of the cursor |
| `statement` `text`                      The verbatim query string submitted to declare this cursor |
| `is_holdable` `bool`                      `true` if the cursor is holdable (that is, it        can be accessed after the transaction that declared the cursor        has committed); `false` otherwise |
| `is_binary` `bool`                      `true` if the cursor was declared        `BINARY`; `false`        otherwise |
| `is_scrollable` `bool`                      `true` if the cursor is scrollable (that is, it        allows rows to be retrieved in a nonsequential manner);        `false` otherwise |
| `creation_time` `timestamptz`                      The time at which the cursor was declared |

The `pg_cursors` view is read-only.

## `pg_file_settings`

The view `pg_file_settings` provides a summary of
the contents of the server's configuration file(s).  A row appears in
this view for each "name = value" entry appearing in the files,
with annotations indicating whether the value could be applied
successfully.  Additional row(s) may appear for problems not linked to
a "name = value" entry, such as syntax errors in the files.

This view is helpful for checking whether planned changes in the
configuration files will work, or for diagnosing a previous failure.
Note that this view reports on the *current* contents of the
files, not on what was last applied by the server.  (The
[`pg_settings`](#view-pg-settings)
view is usually sufficient to determine that.)

By default, the `pg_file_settings` view can be read
only by superusers.

| Column Type                      Description |
| --- |
| `sourcefile` `text`                      Full path name of the configuration file |
| `sourceline` `int4`                      Line number within the configuration file where the entry appears |
| `seqno` `int4`                      Order in which the entries are processed (1..`n`) |
| `name` `text`                      Configuration parameter name |
| `setting` `text`                      Value to be assigned to the parameter |
| `applied` `bool`                      True if the value can be applied successfully |
| `error` `text`                      If not null, an error message indicating why this entry could        not be applied |

If the configuration file contains syntax errors or invalid parameter
names, the server will not attempt to apply any settings from it, and
therefore all the `applied` fields will read as false.
In such a case there will be one or more rows with
non-null `error` fields indicating the
problem(s).  Otherwise, individual settings will be applied if possible.
If an individual setting cannot be applied (e.g., invalid value, or the
setting cannot be changed after server start) it will have an appropriate
message in the `error` field.  Another way that
an entry might have `applied` = false is that it is
overridden by a later entry for the same parameter name; this case is not
considered an error so nothing appears in
the `error` field.

See [config-setting](#config-setting) for more information about the various
ways to change run-time parameters.

## `pg_group`

The view `pg_group` exists for backwards
compatibility: it emulates a catalog that existed in
PostgreSQL before version 8.1.
It shows the names and members of all roles that are marked as not
`rolcanlogin`, which is an approximation to the set
of roles that are being used as groups.

| Column Type                      Description |
| --- |
| `groname` `name`        (references [`pg_authid`](#catalog-pg-authid).`rolname`)                      Name of the group |
| `grosysid` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      ID of this group |
| `grolist` `oid[]`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      An array containing the IDs of the roles in this group |

## `pg_hba_file_rules`

The view `pg_hba_file_rules` provides a summary of
the contents of the client authentication configuration file,
[`pg_hba.conf`](#auth-pg-hba-conf).
A row appears in this view for each
non-empty, non-comment line in the file, with annotations indicating
whether the rule could be applied successfully.

This view can be helpful for checking whether planned changes in the
authentication configuration file will work, or for diagnosing a previous
failure.  Note that this view reports on the *current* contents
of the file, not on what was last loaded by the server.

By default, the `pg_hba_file_rules` view can be read
only by superusers.

| Column Type                      Description |
| --- |
| `rule_number` `int4`                      Number of this rule, if valid, otherwise `NULL`.        This indicates the order in which each rule is considered        until a match is found during authentication. |
| `file_name` `text`                      Name of the file containing this rule |
| `line_number` `int4`                      Line number of this rule in `file_name` |
| `type` `text`                      Type of connection |
| `database` `text[]`                      List of database name(s) to which this rule applies |
| `user_name` `text[]`                      List of user and group name(s) to which this rule applies |
| `address` `text`                      Host name or IP address, or one        of `all`, `samehost`,        or `samenet`, or null for local connections |
| `netmask` `text`                      IP address mask, or null if not applicable |
| `auth_method` `text`                      Authentication method |
| `options` `text[]`                      Options specified for authentication method, if any |
| `error` `text`                      If not null, an error message indicating why this        line could not be processed |

Usually, a row reflecting an incorrect entry will have values for only
the `line_number` and `error` fields.

See [client-authentication](#client-authentication) for more information about
client authentication configuration.

## `pg_ident_file_mappings`

The view `pg_ident_file_mappings` provides a summary
of the contents of the client user name mapping configuration file,
[`pg_ident.conf`](#auth-username-maps).
A row appears in this view for each non-empty, non-comment line in the file,
with annotations indicating whether the map could be applied successfully.

This view can be helpful for checking whether planned changes in the
authentication configuration file will work, or for diagnosing a previous
failure.  Note that this view reports on the *current*
contents of the file, not on what was last loaded by the server.

By default, the `pg_ident_file_mappings` view can be
read only by superusers.

| Column Type                      Description |
| --- |
| `map_number` `int4`                      Number of this map, in priority order, if valid, otherwise        `NULL` |
| `file_name` `text`                      Name of the file containing this map |
| `line_number` `int4`                      Line number of this map in `file_name` |
| `map_name` `text`                      Name of the map |
| `sys_name` `text`                      Detected user name of the client |
| `pg_username` `text`                      Requested PostgreSQL user name |
| `error` `text`                      If not `NULL`, an error message indicating why this        line could not be processed |

Usually, a row reflecting an incorrect entry will have values for only
the `line_number` and `error` fields.

See [client-authentication](#client-authentication) for more information about
client authentication configuration.

## `pg_indexes`

The view `pg_indexes` provides access to
useful information about each index in the database.

| Column Type                      Description |
| --- |
| `schemaname` `name`        (references [`pg_namespace`](#catalog-pg-namespace).`nspname`)                      Name of schema containing table and index |
| `tablename` `name`        (references [`pg_class`](#catalog-pg-class).`relname`)                      Name of table the index is for |
| `indexname` `name`        (references [`pg_class`](#catalog-pg-class).`relname`)                      Name of index |
| `tablespace` `name`        (references [`pg_tablespace`](#catalog-pg-tablespace).`spcname`)                      Name of tablespace containing index (null if default for database) |
| `indexdef` `text`                      Index definition (a reconstructed [sql-createindex](#sql-createindex)        command) |

## `pg_locks`

The view `pg_locks` provides access to
information about the locks held by active processes within the
database server.  See [mvcc](#mvcc) for more discussion
of locking.

`pg_locks` contains one row per active lockable
object, requested lock mode, and relevant process.  Thus, the same
lockable object might
appear many times, if multiple processes are holding or waiting
for locks on it.  However, an object that currently has no locks on it
will not appear at all.

There are several distinct types of lockable objects:
whole relations (e.g., tables), individual pages of relations,
individual tuples of relations,
transaction IDs (both virtual and permanent IDs),
and general database objects (identified by class OID and object OID,
in the same way as in [`pg_description`](#catalog-pg-description) or
[`pg_depend`](#catalog-pg-depend)).  Also, the right to extend a
relation is represented as a separate lockable object, as is the right to
update `pg_database`.`datfrozenxid`.
Also, "advisory" locks can be taken on numbers that have
user-defined meanings.

| Column Type                      Description |
| --- |
| `locktype` `text`                      Type of the lockable object:        `relation`,        `extend`,        `frozenid`,        `page`,        `tuple`,        `transactionid`,        `virtualxid`,        `spectoken`,        `object`,        `userlock`,        `advisory`, or        `applytransaction`.        (See also [wait-event-lock-table](#wait-event-lock-table).) |
| `database` `oid`        (references [`pg_database`](#catalog-pg-database).`oid`)                      OID of the database in which the lock target exists, or        zero if the target is a shared object, or        null if the target is a transaction ID |
| `relation` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      OID of the relation targeted by the lock, or null if the target is not        a relation or part of a relation |
| `page` `int4`                      Page number targeted by the lock within the relation,        or null if the target is not a relation page or tuple |
| `tuple` `int2`                      Tuple number targeted by the lock within the page,        or null if the target is not a tuple |
| `virtualxid` `text`                      Virtual ID of the transaction targeted by the lock,        or null if the target is not a virtual transaction ID;  see        [transactions](#transactions) |
| `transactionid` `xid`                      ID of the transaction targeted by the lock, or null if the target        is not a transaction ID;  [transactions](#transactions) |
| `classid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      OID of the system catalog containing the lock target, or null if the        target is not a general database object |
| `objid` `oid`        (references any OID column)                      OID of the lock target within its system catalog, or null if the        target is not a general database object |
| `objsubid` `int2`                      Column number targeted by the lock (the        `classid` and `objid` refer to the        table itself),        or zero if the target is some other general database object,        or null if the target is not a general database object |
| `virtualtransaction` `text`                      Virtual ID of the transaction that is holding or awaiting this lock |
| `pid` `int4`                      Process ID of the server process holding or awaiting this        lock, or null if the lock is held by a prepared transaction |
| `mode` `text`                      Name of the lock mode held or desired by this process (see [locking-tables](#locking-tables) and [xact-serializable](#xact-serializable)) |
| `granted` `bool`                      True if lock is held, false if lock is awaited |
| `fastpath` `bool`                      True if lock was taken via fast path, false if taken via main        lock table |
| `waitstart` `timestamptz`                      Time when the server process started waiting for this lock,        or null if the lock is held.        Note that this can be null for a very short period of time after        the wait started even though `granted`        is `false`. |

`granted` is true in a row representing a lock
held by the indicated process.  False indicates that this process is
currently waiting to acquire this lock, which implies that at least one
other process is holding or waiting for a conflicting lock mode on the same
lockable object.  The waiting process will sleep until the other lock is
released (or a deadlock situation is detected).  A single process can be
waiting to acquire at most one lock at a time.

Throughout running a transaction, a server process holds an exclusive lock
on the transaction's virtual transaction ID.  If a permanent ID is assigned
to the transaction (which normally happens only if the transaction changes
the state of the database), it also holds an exclusive lock on the
transaction's permanent transaction ID until it ends.  When a process finds
it necessary to wait specifically for another transaction to end, it does
so by attempting to acquire share lock on the other transaction's ID
(either virtual or permanent ID depending on the situation). That will
succeed only when the other transaction terminates and releases its locks.

Although tuples are a lockable type of object,
information about row-level locks is stored on disk, not in memory,
and therefore row-level locks normally do not appear in this view.
If a process is waiting for a
row-level lock, it will usually appear in the view as waiting for the
permanent transaction ID of the current holder of that row lock.

A speculative insertion lock consists of a transaction ID and a speculative
insertion token. The speculative insertion token is displayed in the
`objid` column.

Advisory locks can be acquired on keys consisting of either a single
`bigint` value or two integer values.
A `bigint` key is displayed with its
high-order half in the `classid` column, its low-order half
in the `objid` column, and `objsubid` equal
to 1. The original `bigint` value can be reassembled with the
expression `(classid::bigint << 32) |
objid::bigint`. Integer keys are displayed with the
first key in the
`classid` column, the second key in the `objid`
column, and `objsubid` equal to 2.  The actual meaning of
the keys is up to the user.  Advisory locks are local to each database,
so the `database` column is meaningful for an advisory lock.

Apply transaction locks are used in parallel mode to apply the transaction
in logical replication. The remote transaction ID is displayed in the
`transactionid` column. The `objsubid`
displays the lock subtype which is 0 for the lock used to synchronize the
set of changes, and 1 for the lock used to wait for the transaction to
finish to ensure commit order.

`pg_locks` provides a global view of all locks
in the database cluster, not only those relevant to the current database.
Although its `relation` column can be joined
against [`pg_class`](#catalog-pg-class).`oid` to identify locked
relations, this will only work correctly for relations in the current
database (those for which the `database` column
is either the current database's OID or zero).

The `pid` column can be joined to the
`pid` column of the
[
`pg_stat_activity`](#monitoring-pg-stat-activity-view)
view to get more
information on the session holding or awaiting each lock,
for example

```
SELECT * FROM pg_locks pl LEFT JOIN pg_stat_activity psa
ON pl.pid = psa.pid;
```

Also, if you are using prepared transactions, the
`virtualtransaction` column can be joined to the
`transaction` column of the [`pg_prepared_xacts`](#view-pg-prepared-xacts)
view to get more information on prepared transactions that hold locks.
(A prepared transaction can never be waiting for a lock,
but it continues to hold the locks it acquired while running.)
For example:

```
SELECT * FROM pg_locks pl LEFT JOIN pg_prepared_xacts ppx
ON pl.virtualtransaction = '-1/' || ppx.transaction;
```

While it is possible to obtain information about which processes block
which other processes by joining `pg_locks` against
itself, this is very difficult to get right in detail.  Such a query would
have to encode knowledge about which lock modes conflict with which
others.  Worse, the `pg_locks` view does not expose
information about which processes are ahead of which others in lock wait
queues, nor information about which processes are parallel workers running
on behalf of which other client sessions.  It is better to use
the `pg_blocking_pids()` function
(see [functions-info-session-table](#functions-info-session-table)) to identify which
process(es) a waiting process is blocked behind.

The `pg_locks` view displays data from both the
regular lock manager and the predicate lock manager, which are
separate systems; in addition, the regular lock manager subdivides its
locks into regular and *fast-path* locks.
This data is not guaranteed to be entirely consistent.
When the view is queried,
data on fast-path locks (with `fastpath` = `true`)
is gathered from each backend one at a time, without freezing the state of
the entire lock manager, so it is possible for locks to be taken or
released while information is gathered.  Note, however, that these locks are
known not to conflict with any other lock currently in place.  After
all backends have been queried for fast-path locks, the remainder of the
regular lock manager is locked as a unit, and a consistent snapshot of all
remaining locks is collected as an atomic action.  After unlocking the
regular lock manager, the predicate lock manager is similarly locked and all
predicate locks are collected as an atomic action.  Thus, with the exception
of fast-path locks, each lock manager will deliver a consistent set of
results, but as we do not lock both lock managers simultaneously, it is
possible for locks to be taken or released after we interrogate the regular
lock manager and before we interrogate the predicate lock manager.

Locking the regular and/or predicate lock manager could have some
impact on database performance if this view is very frequently accessed.
The locks are held only for the minimum amount of time necessary to
obtain data from the lock managers, but this does not completely eliminate
the possibility of a performance impact.

## `pg_matviews`

The view `pg_matviews` provides access to
useful information about each materialized view in the database.

| Column Type                      Description |
| --- |
| `schemaname` `name`        (references [`pg_namespace`](#catalog-pg-namespace).`nspname`)                      Name of schema containing materialized view |
| `matviewname` `name`        (references [`pg_class`](#catalog-pg-class).`relname`)                      Name of materialized view |
| `matviewowner` `name`        (references [`pg_authid`](#catalog-pg-authid).`rolname`)                      Name of materialized view's owner |
| `tablespace` `name`        (references [`pg_tablespace`](#catalog-pg-tablespace).`spcname`)                      Name of tablespace containing materialized view (null if default for database) |
| `hasindexes` `bool`                      True if materialized view has (or recently had) any indexes |
| `ispopulated` `bool`                      True if materialized view is currently populated |
| `definition` `text`                      Materialized view definition (a reconstructed [sql-select](#sql-select) query) |

## `pg_policies`

The view `pg_policies` provides access to
useful information about each row-level security policy in the database.

| Column Type                      Description |
| --- |
| `schemaname` `name`        (references [`pg_namespace`](#catalog-pg-namespace).`nspname`)                      Name of schema containing table policy is on |
| `tablename` `name`        (references [`pg_class`](#catalog-pg-class).`relname`)                      Name of table policy is on |
| `policyname` `name`        (references [`pg_policy`](#catalog-pg-policy).`polname`)                      Name of policy |
| `permissive` `text`                      Is the policy permissive or restrictive? |
| `roles` `name[]`                      The roles to which this policy applies |
| `cmd` `text`                      The command type to which the policy is applied |
| `qual` `text`                      The expression added to the security barrier qualifications for        queries that this policy applies to |
| `with_check` `text`                      The expression added to the WITH CHECK qualifications for        queries that attempt to add rows to this table |

## `pg_prepared_statements`

The `pg_prepared_statements` view displays
all the prepared statements that are available in the current
session. See [sql-prepare](#sql-prepare) for more information about prepared
statements.

`pg_prepared_statements` contains one row
for each prepared statement. Rows are added to the view when a new
prepared statement is created and removed when a prepared statement
is released (for example, via the [`DEALLOCATE`](#sql-deallocate) command).

| Column Type                      Description |
| --- |
| `name` `text`                      The identifier of the prepared statement |
| `statement` `text`                      The query string submitted by the client to create this        prepared statement. For prepared statements created via SQL,        this is the `PREPARE` statement submitted by        the client. For prepared statements created via the        frontend/backend protocol, this is the text of the prepared        statement itself. |
| `prepare_time` `timestamptz`                      The time at which the prepared statement was created |
| `parameter_types` `regtype[]`                      The expected parameter types for the prepared statement in the        form of an array of `regtype`. The OID corresponding        to an element of this array can be obtained by casting the        `regtype` value to `oid`. |
| `result_types` `regtype[]`                      The types of the columns returned by the prepared statement in the        form of an array of `regtype`. The OID corresponding        to an element of this array can be obtained by casting the        `regtype` value to `oid`.        If the prepared statement does not provide a result (e.g., a DML        statement), then this field will be null. |
| `from_sql` `bool`                      `true` if the prepared statement was created        via the `PREPARE` SQL command;        `false` if the statement was prepared via the        frontend/backend protocol |
| `generic_plans` `int8`                      Number of times generic plan was chosen |
| `custom_plans` `int8`                      Number of times custom plan was chosen |

The `pg_prepared_statements` view is read-only.

## `pg_prepared_xacts`

The view `pg_prepared_xacts` displays
information about transactions that are currently prepared for two-phase
commit (see [sql-prepare-transaction](#sql-prepare-transaction) for details).

`pg_prepared_xacts` contains one row per prepared
transaction.  An entry is removed when the transaction is committed or
rolled back.

| Column Type                      Description |
| --- |
| `transaction` `xid`                      Numeric transaction identifier of the prepared transaction |
| `gid` `text`                      Global transaction identifier that was assigned to the transaction |
| `prepared` `timestamptz`                      Time at which the transaction was prepared for commit |
| `owner` `name`        (references [`pg_authid`](#catalog-pg-authid).`rolname`)                      Name of the user that executed the transaction |
| `database` `name`        (references [`pg_database`](#catalog-pg-database).`datname`)                      Name of the database in which the transaction was executed |

When the `pg_prepared_xacts` view is accessed, the
internal transaction manager data structures are momentarily locked, and
a copy is made for the view to display.  This ensures that the
view produces a consistent set of results, while not blocking
normal operations longer than necessary.  Nonetheless
there could be some impact on database performance if this view is
frequently accessed.

## `pg_publication_tables`

The view `pg_publication_tables` provides
information about the mapping between publications and information of
tables they contain.  Unlike the underlying catalog
[`pg_publication_rel`](#catalog-pg-publication-rel),
this view expands publications defined as
[`FOR ALL TABLES`](#sql-createpublication-for-all-tables)
and [`FOR TABLES IN SCHEMA`](#sql-createpublication-for-tables-in-schema),
so for such publications there will be a row for each eligible table.

| Column Type                      Description |
| --- |
| `pubname` `name`        (references [`pg_publication`](#catalog-pg-publication).`pubname`)                      Name of publication |
| `schemaname` `name`        (references [`pg_namespace`](#catalog-pg-namespace).`nspname`)                      Name of schema containing table |
| `tablename` `name`        (references [`pg_class`](#catalog-pg-class).`relname`)                      Name of table |
| `attnames` `name[]`        (references [`pg_attribute`](#catalog-pg-attribute).`attname`)                      Names of table columns included in the publication. This contains all        the columns of the table when the user didn't specify the column list        for the table. |
| `rowfilter` `text`                      Expression for the table's publication qualifying condition |

## `pg_replication_origin_status`

The `pg_replication_origin_status` view
contains information about how far replay for a certain origin has
progressed.  For more on replication origins
see [replication-origins](#replication-origins).

| Column Type                      Description |
| --- |
| `local_id` `oid`        (references [`pg_replication_origin`](#catalog-pg-replication-origin).`roident`)                      internal node identifier |
| `external_id` `text`        (references [`pg_replication_origin`](#catalog-pg-replication-origin).`roname`)                      external node identifier |
| `remote_lsn` `pg_lsn`                      The origin node's LSN up to which data has been replicated. |
| `local_lsn` `pg_lsn`                      This node's LSN at which `remote_lsn` has        been replicated. Used to flush commit records before persisting        data to disk when using asynchronous commits. |

## `pg_replication_slots`

The `pg_replication_slots` view provides a listing
of all replication slots that currently exist on the database cluster,
along with their current state.

For more on replication slots,
see [streaming-replication-slots](#streaming-replication-slots) and [logicaldecoding](#logicaldecoding).

| Column Type                      Description |
| --- |
| `slot_name` `name`                      A unique, cluster-wide identifier for the replication slot |
| `plugin` `name`                      The base name of the shared object containing the output plugin this logical slot is using, or null for physical slots. |
| `slot_type` `text`                      The slot type: `physical` or `logical` |
| `datoid` `oid`        (references [`pg_database`](#catalog-pg-database).`oid`)                      The OID of the database this slot is associated with, or        null. Only logical slots have an associated database. |
| `database` `name`        (references [`pg_database`](#catalog-pg-database).`datname`)                      The name of the database this slot is associated with, or        null. Only logical slots have an associated database. |
| `temporary` `bool`                      True if this is a temporary replication slot. Temporary slots are        not saved to disk and are automatically dropped on error or when        the session has finished. |
| `active` `bool`                      True if this slot is currently actively being used |
| `active_pid` `int4`                      The process ID of the session using this slot if the slot        is currently actively being used. `NULL` if        inactive. |
| `xmin` `xid`                      The oldest transaction that this slot needs the database to        retain.  `VACUUM` cannot remove tuples deleted        by any later transaction. |
| `catalog_xmin` `xid`                      The oldest transaction affecting the system catalogs that this        slot needs the database to retain.  `VACUUM` cannot        remove catalog tuples deleted by any later transaction. |
| `restart_lsn` `pg_lsn`                      The address (`LSN`) of oldest WAL which still        might be required by the consumer of this slot and thus won't be        automatically removed during checkpoints unless this LSN        gets behind more than [guc-max-slot-wal-keep-size](#guc-max-slot-wal-keep-size)        from the current LSN.  `NULL`        if the `LSN` of this slot has never been reserved. |
| `confirmed_flush_lsn` `pg_lsn`                      The address (`LSN`) up to which the logical        slot's consumer has confirmed receiving data. Data corresponding to the        transactions committed before this `LSN` is not        available anymore. `NULL` for physical slots. |
| `wal_status` `text`                      Availability of WAL files claimed by this slot.        Possible values are:         - `reserved` means that the claimed files           are within `max_wal_size`. - `extended` means           that `max_wal_size` is exceeded but the files are           still retained, either by the replication slot or           by `wal_keep_size`. - `unreserved` means that the slot no longer           retains the required WAL files and some of them are to be removed at           the next checkpoint.  This typically occurs when           [guc-max-slot-wal-keep-size](#guc-max-slot-wal-keep-size) is set to           a non-negative value.  This state can return           to `reserved` or `extended`. - `lost` means that this slot is no longer usable. |
| `safe_wal_size` `int8`                      The number of bytes that can be written to WAL such that this slot        is not in danger of getting in state "lost".  It is NULL for lost        slots, as well as if `max_slot_wal_keep_size`        is `-1`. |
| `two_phase` `bool`                      True if the slot is enabled for decoding prepared transactions.  Always        false for physical slots. |
| `conflicting` `bool`                      True if this logical slot conflicted with recovery (and so is now        invalidated). Always NULL for physical slots. |

## `pg_roles`

The view `pg_roles` provides access to
information about database roles.  This is simply a publicly
readable view of
[`pg_authid`](#catalog-pg-authid)
that blanks out the password field.

| Column Type                      Description |
| --- |
| `rolname` `name`                      Role name |
| `rolsuper` `bool`                      Role has superuser privileges |
| `rolinherit` `bool`                      Role automatically inherits privileges of roles it is a        member of |
| `rolcreaterole` `bool`                      Role can create more roles |
| `rolcreatedb` `bool`                      Role can create databases |
| `rolcanlogin` `bool`                      Role can log in. That is, this role can be given as the initial        session authorization identifier |
| `rolreplication` `bool`                      Role is a replication role. A replication role can initiate replication        connections and create and drop replication slots. |
| `rolconnlimit` `int4`                      For roles that can log in, this sets maximum number of concurrent        connections this role can make.  -1 means no limit. |
| `rolpassword` `text`                      Not the password (always reads as `********`) |
| `rolvaliduntil` `timestamptz`                      Password expiry time (only used for password authentication);        null if no expiration |
| `rolbypassrls` `bool`                      Role bypasses every row-level security policy, see        [ddl-rowsecurity](#ddl-rowsecurity) for more information. |
| `rolconfig` `text[]`                      Role-specific defaults for run-time configuration variables |
| `oid` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      ID of role |

## `pg_rules`

The view `pg_rules` provides access to
useful information about query rewrite rules.

| Column Type                      Description |
| --- |
| `schemaname` `name`        (references [`pg_namespace`](#catalog-pg-namespace).`nspname`)                      Name of schema containing table |
| `tablename` `name`        (references [`pg_class`](#catalog-pg-class).`relname`)                      Name of table the rule is for |
| `rulename` `name`        (references [`pg_rewrite`](#catalog-pg-rewrite).`rulename`)                      Name of rule |
| `definition` `text`                      Rule definition (a reconstructed creation command) |

The `pg_rules` view excludes the `ON SELECT` rules
of views and materialized views; those can be seen in
[`pg_views`](#view-pg-views) and [`pg_matviews`](#view-pg-matviews).

## `pg_seclabels`

The view `pg_seclabels` provides information about
security labels.  It as an easier-to-query version of the
[`pg_seclabel`](#catalog-pg-seclabel) catalog.

| Column Type                      Description |
| --- |
| `objoid` `oid`        (references any OID column)                      The OID of the object this security label pertains to |
| `classoid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the system catalog this object appears in |
| `objsubid` `int4`                      For a security label on a table column, this is the column number (the        `objoid` and `classoid` refer to        the table itself).  For all other object types, this column is        zero. |
| `objtype` `text`                      The type of object to which this label applies, as text. |
| `objnamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      The OID of the namespace for this object, if applicable;        otherwise NULL. |
| `objname` `text`                      The name of the object to which this label applies, as text. |
| `provider` `text`        (references [`pg_seclabel`](#catalog-pg-seclabel).`provider`)                      The label provider associated with this label. |
| `label` `text`        (references [`pg_seclabel`](#catalog-pg-seclabel).`label`)                      The security label applied to this object. |

## `pg_sequences`

The view `pg_sequences` provides access to
useful information about each sequence in the database.

| Column Type                      Description |
| --- |
| `schemaname` `name`        (references [`pg_namespace`](#catalog-pg-namespace).`nspname`)                      Name of schema containing sequence |
| `sequencename` `name`        (references [`pg_class`](#catalog-pg-class).`relname`)                      Name of sequence |
| `sequenceowner` `name`        (references [`pg_authid`](#catalog-pg-authid).`rolname`)                      Name of sequence's owner |
| `data_type` `regtype`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Data type of the sequence |
| `start_value` `int8`                      Start value of the sequence |
| `min_value` `int8`                      Minimum value of the sequence |
| `max_value` `int8`                      Maximum value of the sequence |
| `increment_by` `int8`                      Increment value of the sequence |
| `cycle` `bool`                      Whether the sequence cycles |
| `cache_size` `int8`                      Cache size of the sequence |
| `last_value` `int8`                      The last sequence value written to disk.  If caching is used,        this value can be greater than the last value handed out from the        sequence. |

The `last_value` column will read as null if any of
the following are true:

- The sequence has not been read from yet.
- The current user does not have `USAGE` or
`SELECT` privilege on the sequence.
- The sequence is unlogged and the server is a standby.

## `pg_settings`

The view `pg_settings` provides access to
run-time parameters of the server.  It is essentially an alternative
interface to the [`SHOW`](#sql-show)
and [`SET`](#sql-set) commands.
It also provides access to some facts about each parameter that are
not directly available from [`SHOW`](#sql-show), such as minimum and
maximum values.

| Column Type                      Description |
| --- |
| `name` `text`                      Run-time configuration parameter name |
| `setting` `text`                      Current value of the parameter |
| `unit` `text`                      Implicit unit of the parameter |
| `category` `text`                      Logical group of the parameter |
| `short_desc` `text`                      A brief description of the parameter |
| `extra_desc` `text`                      Additional, more detailed, description of the parameter |
| `context` `text`                      Context required to set the parameter's value (see below) |
| `vartype` `text`                      Parameter type (`bool`, `enum`,        `integer`, `real`, or `string`) |
| `source` `text`                      Source of the current parameter value |
| `min_val` `text`                      Minimum allowed value of the parameter (null for non-numeric        values) |
| `max_val` `text`                      Maximum allowed value of the parameter (null for non-numeric        values) |
| `enumvals` `text[]`                      Allowed values of an enum parameter (null for non-enum        values) |
| `boot_val` `text`                      Parameter value assumed at server startup if the parameter is        not otherwise set |
| `reset_val` `text`                      Value that [`RESET`](#sql-reset) would reset the parameter to        in the current session |
| `sourcefile` `text`                      Configuration file the current value was set in (null for        values set from sources other than configuration files, or when        examined by a user who neither is a superuser nor has privileges of        `pg_read_all_settings`); helpful when using        `include` directives in configuration files |
| `sourceline` `int4`                      Line number within the configuration file the current value was        set at (null for values set from sources other than configuration files,        or when examined by a user who neither is a superuser nor has privileges of        `pg_read_all_settings`). |
| `pending_restart` `bool`                      `true` if the value has been changed in the        configuration file but needs a restart; or `false`        otherwise. |

There are several possible values of `context`.
In order of decreasing difficulty of changing the setting, they are:

**`internal`**
: These settings cannot be changed directly; they reflect internally
determined values.  Some of them may be adjustable by rebuilding the
server with different configuration options, or by changing options
supplied to initdb.

**`postmaster`**
: These settings can only be applied when the server starts, so any change
requires restarting the server.  Values for these settings are typically
stored in the `postgresql.conf` file, or passed on
the command line when starting the server.  Of course, settings with any
of the lower `context` types can also be
set at server start time.

**`sighup`**
: Changes to these settings can be made in
`postgresql.conf` without restarting the server.
Send a SIGHUP signal to the postmaster to
cause it to re-read `postgresql.conf` and apply
the changes.  The postmaster will also forward the
SIGHUP signal to its child processes so that
they all pick up the new value.

**`superuser-backend`**
: Changes to these settings can be made in
`postgresql.conf` without restarting the server.
They can also be set for a particular session in the connection request
packet (for example, via libpq's `PGOPTIONS`
environment variable), but only if the connecting user is a superuser
or has been granted the appropriate `SET` privilege.
However, these settings never change in a session after it is started.
If you change them in `postgresql.conf`, send a
SIGHUP signal to the postmaster to cause it to
re-read `postgresql.conf`.  The new values will only
affect subsequently-launched sessions.

**`backend`**
: Changes to these settings can be made in
`postgresql.conf` without restarting the server.
They can also be set for a particular session in the connection request
packet (for example, via libpq's `PGOPTIONS`
environment variable); any user can make such a change for their session.
However, these settings never change in a session after it is started.
If you change them in `postgresql.conf`, send a
SIGHUP signal to the postmaster to cause it to
re-read `postgresql.conf`.  The new values will only
affect subsequently-launched sessions.

**`superuser`**
: These settings can be set from `postgresql.conf`,
or within a session via the `SET` command; but only superusers
and users with the appropriate `SET` privilege
can change them via `SET`.  Changes in
`postgresql.conf` will affect existing sessions
only if no session-local value has been established with `SET`.

**`user`**
: These settings can be set from `postgresql.conf`,
or within a session via the `SET` command.  Any user is
allowed to change their session-local value.  Changes in
`postgresql.conf` will affect existing sessions
only if no session-local value has been established with `SET`.

See [config-setting](#config-setting) for more information about the various
ways to change these parameters.

This view cannot be inserted into or deleted from, but it can be updated.  An
`UPDATE` applied to a row of `pg_settings`
is equivalent to executing the `SET` command on that named
parameter. The change only affects the value used by the current
session. If an `UPDATE` is issued within a transaction
that is later aborted, the effects of the `UPDATE` command
disappear when the transaction is rolled back. Once the surrounding
transaction is committed, the effects will persist until the end of the
session, unless overridden by another `UPDATE` or
`SET`.

This view does not
display [customized options](#runtime-config-custom)
unless the extension module that defines them has been loaded by the
backend process executing the query (e.g., via a mention in
[guc-shared-preload-libraries](#guc-shared-preload-libraries),
a call to a C function in the extension, or the
[`LOAD`](#sql-load) command).
For example, since [archive modules](#archive-modules)
are normally loaded only by the archiver process not regular sessions,
this view will not display any customized options defined by such modules
unless special action is taken to load them into the backend process
executing the query.

## `pg_shadow`

The view `pg_shadow` exists for backwards
compatibility: it emulates a catalog that existed in
PostgreSQL before version 8.1.
It shows properties of all roles that are marked as
`rolcanlogin` in
[`pg_authid`](#catalog-pg-authid).

The name stems from the fact that this table
should not be readable by the public since it contains passwords.
[`pg_user`](#view-pg-user)
is a publicly readable view on
`pg_shadow` that blanks out the password field.

| Column Type                      Description |
| --- |
| `usename` `name`        (references [`pg_authid`](#catalog-pg-authid).`rolname`)                      User name |
| `usesysid` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      ID of this user |
| `usecreatedb` `bool`                      User can create databases |
| `usesuper` `bool`                      User is a superuser |
| `userepl` `bool`                      User can initiate streaming replication and put the system in and        out of backup mode. |
| `usebypassrls` `bool`                      User bypasses every row-level security policy, see        [ddl-rowsecurity](#ddl-rowsecurity) for more information. |
| `passwd` `text`                      Encrypted password; null if none.  See        [`pg_authid`](#catalog-pg-authid)        for details of how encrypted passwords are stored. |
| `valuntil` `timestamptz`                      Password expiry time (only used for password authentication) |
| `useconfig` `text[]`                      Session defaults for run-time configuration variables |

## `pg_shmem_allocations`

The `pg_shmem_allocations` view shows allocations
made from the server's main shared memory segment.  This includes both
memory allocated by PostgreSQL itself and memory
allocated by extensions using the mechanisms detailed in
[xfunc-shared-addin](#xfunc-shared-addin).

Note that this view does not include memory allocated using the dynamic
shared memory infrastructure.

| Column Type                      Description |
| --- |
| `name` `text`                      The name of the shared memory allocation. NULL for unused memory        and `` for anonymous        allocations. |
| `off` `int8`                      The offset at which the allocation starts. NULL for anonymous        allocations, since details related to them are not known. |
| `size` `int8`                      Size of the allocation in bytes |
| `allocated_size` `int8`                      Size of the allocation in bytes including padding. For anonymous        allocations, no information about padding is available, so the        `size` and `allocated_size` columns        will always be equal. Padding is not meaningful for free memory, so        the columns will be equal in that case also. |

Anonymous allocations are allocations that have been made
with `ShmemAlloc()` directly, rather than via
`ShmemInitStruct()` or
`ShmemInitHash()`.

By default, the `pg_shmem_allocations` view can be
read only by superusers or roles with privileges of the
`pg_read_all_stats` role.

## `pg_stats`

The view `pg_stats` provides access to
the information stored in the [`pg_statistic`](#catalog-pg-statistic)
catalog.  This view allows access only to rows of
[`pg_statistic`](#catalog-pg-statistic) that correspond to tables the
user has permission to read, and therefore it is safe to allow public
read access to this view.

`pg_stats` is also designed to present the
information in a more readable format than the underlying catalog
— at the cost that its schema must be extended whenever new slot types
are defined for [`pg_statistic`](#catalog-pg-statistic).

| Column Type                      Description |
| --- |
| `schemaname` `name`        (references [`pg_namespace`](#catalog-pg-namespace).`nspname`)                      Name of schema containing table |
| `tablename` `name`        (references [`pg_class`](#catalog-pg-class).`relname`)                      Name of table |
| `attname` `name`        (references [`pg_attribute`](#catalog-pg-attribute).`attname`)                      Name of column described by this row |
| `inherited` `bool`                      If true, this row includes values from child tables, not just the        values in the specified table |
| `null_frac` `float4`                      Fraction of column entries that are null |
| `avg_width` `int4`                      Average width in bytes of column's entries |
| `n_distinct` `float4`                      If greater than zero, the estimated number of distinct values in the        column.  If less than zero, the negative of the number of distinct        values divided by the number of rows.  (The negated form is used when        `ANALYZE` believes that the number of distinct values is        likely to increase as the table grows; the positive form is used when        the column seems to have a fixed number of possible values.)  For        example, -1 indicates a unique column in which the number of distinct        values is the same as the number of rows. |
| `most_common_vals` `anyarray`                      A list of the most common values in the column. (Null if        no values seem to be more common than any others.) |
| `most_common_freqs` `float4[]`                      A list of the frequencies of the most common values,        i.e., number of occurrences of each divided by total number of rows.        (Null when `most_common_vals` is.) |
| `histogram_bounds` `anyarray`                      A list of values that divide the column's values into groups of        approximately equal population.  The values in        `most_common_vals`, if present, are omitted from this        histogram calculation.  (This column is null if the column data type        does not have a `<` operator or if the        `most_common_vals` list accounts for the entire        population.) |
| `correlation` `float4`                      Statistical correlation between physical row ordering and        logical ordering of the column values.  This ranges from -1 to +1.        When the value is near -1 or +1, an index scan on the column will        be estimated to be cheaper than when it is near zero, due to reduction        of random access to the disk.  (This column is null if the column data        type does not have a `<` operator.) |
| `most_common_elems` `anyarray`                      A list of non-null element values most often appearing within values of        the column. (Null for scalar types.) |
| `most_common_elem_freqs` `float4[]`                      A list of the frequencies of the most common element values, i.e., the        fraction of rows containing at least one instance of the given value.        Two or three additional values follow the per-element frequencies;        these are the minimum and maximum of the preceding per-element        frequencies, and optionally the frequency of null elements.        (Null when `most_common_elems` is.) |
| `elem_count_histogram` `float4[]`                      A histogram of the counts of distinct non-null element values within the        values of the column, followed by the average number of distinct        non-null elements.  (Null for scalar types.) |

The maximum number of entries in the array fields can be controlled on a
column-by-column basis using the [`ALTER
TABLE SET STATISTICS`](#sql-altertable)
command, or globally by setting the
[guc-default-statistics-target](#guc-default-statistics-target) run-time parameter.

## `pg_stats_ext`

The view `pg_stats_ext` provides access to
information about each extended statistics object in the database,
combining information stored in the [`pg_statistic_ext`](#catalog-pg-statistic-ext)
and [`pg_statistic_ext_data`](#catalog-pg-statistic-ext-data)
catalogs.  This view allows access only to rows of
[`pg_statistic_ext`](#catalog-pg-statistic-ext) and [`pg_statistic_ext_data`](#catalog-pg-statistic-ext-data)
that correspond to tables the user owns, and therefore
it is safe to allow public read access to this view.

`pg_stats_ext` is also designed to present the
information in a more readable format than the underlying catalogs
— at the cost that its schema must be extended whenever new types
of extended statistics are added to [`pg_statistic_ext`](#catalog-pg-statistic-ext).

| Column Type                      Description |
| --- |
| `schemaname` `name`        (references [`pg_namespace`](#catalog-pg-namespace).`nspname`)                      Name of schema containing table |
| `tablename` `name`        (references [`pg_class`](#catalog-pg-class).`relname`)                      Name of table |
| `statistics_schemaname` `name`        (references [`pg_namespace`](#catalog-pg-namespace).`nspname`)                      Name of schema containing extended statistics object |
| `statistics_name` `name`        (references [`pg_statistic_ext`](#catalog-pg-statistic-ext).`stxname`)                      Name of extended statistics object |
| `statistics_owner` `name`        (references [`pg_authid`](#catalog-pg-authid).`rolname`)                      Owner of the extended statistics object |
| `attnames` `name[]`        (references [`pg_attribute`](#catalog-pg-attribute).`attname`)                      Names of the columns included in the extended statistics object |
| `exprs` `text[]`                      Expressions included in the extended statistics object |
| `kinds` `char[]`                      Types of extended statistics object enabled for this record |
| `inherited` `bool`        (references [`pg_statistic_ext_data`](#catalog-pg-statistic-ext-data).`stxdinherit`)                      If true, the stats include values from child tables, not just the        values in the specified relation |
| `n_distinct` `pg_ndistinct`                      N-distinct counts for combinations of column values. If greater        than zero, the estimated number of distinct values in the combination.        If less than zero, the negative of the number of distinct values divided        by the number of rows.        (The negated form is used when `ANALYZE` believes that        the number of distinct values is likely to increase as the table grows;        the positive form is used when the column seems to have a fixed number        of possible values.)  For example, -1 indicates a unique combination of        columns in which the number of distinct combinations is the same as the        number of rows. |
| `dependencies` `pg_dependencies`                      Functional dependency statistics |
| `most_common_vals` `text[]`                      A list of the most common combinations of values in the columns.        (Null if no combinations seem to be more common than any others.) |
| `most_common_val_nulls` `bool[]`                      A list of NULL flags for the most common combinations of values.        (Null when `most_common_vals` is.) |
| `most_common_freqs` `float8[]`                      A list of the frequencies of the most common combinations,        i.e., number of occurrences of each divided by total number of rows.        (Null when `most_common_vals` is.) |
| `most_common_base_freqs` `float8[]`                      A list of the base frequencies of the most common combinations,        i.e., product of per-value frequencies.        (Null when `most_common_vals` is.) |

The maximum number of entries in the array fields can be controlled on a
column-by-column basis using the [`ALTER
TABLE SET STATISTICS`](#sql-altertable) command, or globally by setting the
[guc-default-statistics-target](#guc-default-statistics-target) run-time parameter.

## `pg_stats_ext_exprs`

The view `pg_stats_ext_exprs` provides access to
information about all expressions included in extended statistics objects,
combining information stored in the [`pg_statistic_ext`](#catalog-pg-statistic-ext)
and [`pg_statistic_ext_data`](#catalog-pg-statistic-ext-data)
catalogs.  This view allows access only to rows of
[`pg_statistic_ext`](#catalog-pg-statistic-ext) and [`pg_statistic_ext_data`](#catalog-pg-statistic-ext-data)
that correspond to tables the user owns, and therefore
it is safe to allow public read access to this view.

`pg_stats_ext_exprs` is also designed to present
the information in a more readable format than the underlying catalogs
— at the cost that its schema must be extended whenever the structure
of statistics in `pg_statistic_ext` changes.

| Column Type                      Description |
| --- |
| `schemaname` `name`        (references [`pg_namespace`](#catalog-pg-namespace).`nspname`)                      Name of schema containing table |
| `tablename` `name`        (references [`pg_class`](#catalog-pg-class).`relname`)                      Name of table the statistics object is defined on |
| `statistics_schemaname` `name`        (references [`pg_namespace`](#catalog-pg-namespace).`nspname`)                      Name of schema containing extended statistics object |
| `statistics_name` `name`        (references [`pg_statistic_ext`](#catalog-pg-statistic-ext).`stxname`)                      Name of extended statistics object |
| `statistics_owner` `name`        (references [`pg_authid`](#catalog-pg-authid).`rolname`)                      Owner of the extended statistics object |
| `expr` `text`                      Expression included in the extended statistics object |
| `inherited` `bool`        (references [`pg_statistic_ext_data`](#catalog-pg-statistic-ext-data).`stxdinherit`)                      If true, the stats include values from child tables, not just the        values in the specified relation |
| `null_frac` `float4`                      Fraction of expression entries that are null |
| `avg_width` `int4`                      Average width in bytes of expression's entries |
| `n_distinct` `float4`                      If greater than zero, the estimated number of distinct values in the        expression.  If less than zero, the negative of the number of distinct        values divided by the number of rows.  (The negated form is used when        `ANALYZE` believes that the number of distinct values is        likely to increase as the table grows; the positive form is used when        the expression seems to have a fixed number of possible values.)  For        example, -1 indicates a unique expression in which the number of distinct        values is the same as the number of rows. |
| `most_common_vals` `anyarray`                      A list of the most common values in the expression. (Null if        no values seem to be more common than any others.) |
| `most_common_freqs` `float4[]`                      A list of the frequencies of the most common values,        i.e., number of occurrences of each divided by total number of rows.        (Null when `most_common_vals` is.) |
| `histogram_bounds` `anyarray`                      A list of values that divide the expression's values into groups of        approximately equal population.  The values in        `most_common_vals`, if present, are omitted from this        histogram calculation.  (This expression is null if the expression data type        does not have a `<` operator or if the        `most_common_vals` list accounts for the entire        population.) |
| `correlation` `float4`                      Statistical correlation between physical row ordering and        logical ordering of the expression values.  This ranges from -1 to +1.        When the value is near -1 or +1, an index scan on the expression will        be estimated to be cheaper than when it is near zero, due to reduction        of random access to the disk.  (This expression is null if the expression's        data type does not have a `<` operator.) |
| `most_common_elems` `anyarray`                      A list of non-null element values most often appearing within values of        the expression. (Null for scalar types.) |
| `most_common_elem_freqs` `float4[]`                      A list of the frequencies of the most common element values, i.e., the        fraction of rows containing at least one instance of the given value.        Two or three additional values follow the per-element frequencies;        these are the minimum and maximum of the preceding per-element        frequencies, and optionally the frequency of null elements.        (Null when `most_common_elems` is.) |
| `elem_count_histogram` `float4[]`                      A histogram of the counts of distinct non-null element values within the        values of the expression, followed by the average number of distinct        non-null elements.  (Null for scalar types.) |

The maximum number of entries in the array fields can be controlled on a
column-by-column basis using the [`ALTER
TABLE SET STATISTICS`](#sql-altertable) command, or globally by setting the
[guc-default-statistics-target](#guc-default-statistics-target) run-time parameter.

## `pg_tables`

The view `pg_tables` provides access to
useful information about each table in the database.

| Column Type                      Description |
| --- |
| `schemaname` `name`        (references [`pg_namespace`](#catalog-pg-namespace).`nspname`)                      Name of schema containing table |
| `tablename` `name`        (references [`pg_class`](#catalog-pg-class).`relname`)                      Name of table |
| `tableowner` `name`        (references [`pg_authid`](#catalog-pg-authid).`rolname`)                      Name of table's owner |
| `tablespace` `name`        (references [`pg_tablespace`](#catalog-pg-tablespace).`spcname`)                      Name of tablespace containing table (null if default for database) |
| `hasindexes` `bool`        (references [`pg_class`](#catalog-pg-class).`relhasindex`)                      True if table has (or recently had) any indexes |
| `hasrules` `bool`        (references [`pg_class`](#catalog-pg-class).`relhasrules`)                      True if table has (or once had) rules |
| `hastriggers` `bool`        (references [`pg_class`](#catalog-pg-class).`relhastriggers`)                      True if table has (or once had) triggers |
| `rowsecurity` `bool`        (references [`pg_class`](#catalog-pg-class).`relrowsecurity`)                      True if row security is enabled on the table |

## `pg_timezone_abbrevs`

The view `pg_timezone_abbrevs` provides a list
of time zone abbreviations that are currently recognized by the datetime
input routines.  The contents of this view change when the
[guc-timezone-abbreviations](#guc-timezone-abbreviations) run-time parameter is modified.

| Column Type                      Description |
| --- |
| `abbrev` `text`                      Time zone abbreviation |
| `utc_offset` `interval`                      Offset from UTC (positive means east of Greenwich) |
| `is_dst` `bool`                      True if this is a daylight-savings abbreviation |

While most timezone abbreviations represent fixed offsets from UTC,
there are some that have historically varied in value
(see [datetime-config-files](#datetime-config-files) for more information).
In such cases this view presents their current meaning.

## `pg_timezone_names`

The view `pg_timezone_names` provides a list
of time zone names that are recognized by `SET TIMEZONE`,
along with their associated abbreviations, UTC offsets,
and daylight-savings status.  (Technically,
PostgreSQL does not use UTC because leap
seconds are not handled.)
Unlike the abbreviations shown in [`pg_timezone_abbrevs`](#view-pg-timezone-abbrevs), many of these names imply a set of daylight-savings transition
date rules.  Therefore, the associated information changes across local DST
boundaries.  The displayed information is computed based on the current
value of `CURRENT_TIMESTAMP`.

| Column Type                      Description |
| --- |
| `name` `text`                      Time zone name |
| `abbrev` `text`                      Time zone abbreviation |
| `utc_offset` `interval`                      Offset from UTC (positive means east of Greenwich) |
| `is_dst` `bool`                      True if currently observing daylight savings |

## `pg_user`

The view `pg_user` provides access to
information about database users.  This is simply a publicly
readable view of
[`pg_shadow`](#view-pg-shadow)
that blanks out the password field.

| Column Type                      Description |
| --- |
| `usename` `name`                      User name |
| `usesysid` `oid`                      ID of this user |
| `usecreatedb` `bool`                      User can create databases |
| `usesuper` `bool`                      User is a superuser |
| `userepl` `bool`                      User can initiate streaming replication and put the system in and        out of backup mode. |
| `usebypassrls` `bool`                      User bypasses every row-level security policy, see        [ddl-rowsecurity](#ddl-rowsecurity) for more information. |
| `passwd` `text`                      Not the password (always reads as `********`) |
| `valuntil` `timestamptz`                      Password expiry time (only used for password authentication) |
| `useconfig` `text[]`                      Session defaults for run-time configuration variables |

## `pg_user_mappings`

The view `pg_user_mappings` provides access
to information about user mappings.  This is essentially a publicly
readable view of
[`pg_user_mapping`](#catalog-pg-user-mapping)
that leaves out the options field if the user has no rights to use
it.

| Column Type                      Description |
| --- |
| `umid` `oid`        (references [`pg_user_mapping`](#catalog-pg-user-mapping).`oid`)                      OID of the user mapping |
| `srvid` `oid`        (references [`pg_foreign_server`](#catalog-pg-foreign-server).`oid`)                      The OID of the foreign server that contains this mapping |
| `srvname` `name`        (references [`pg_foreign_server`](#catalog-pg-foreign-server).`srvname`)                      Name of the foreign server |
| `umuser` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      OID of the local role being mapped, or zero if the user mapping is public |
| `usename` `name`                      Name of the local user to be mapped |
| `umoptions` `text[]`                      User mapping specific options, as "keyword=value" strings |

To protect password information stored as a user mapping option,
the `umoptions` column will read as null
unless one of the following applies:

- current user is the user being mapped, and owns the server or
holds `USAGE` privilege on it
- current user is the server owner and mapping is for `PUBLIC`
- current user is a superuser

## `pg_views`

The view `pg_views` provides access to
useful information about each view in the database.

| Column Type                      Description |
| --- |
| `schemaname` `name`        (references [`pg_namespace`](#catalog-pg-namespace).`nspname`)                      Name of schema containing view |
| `viewname` `name`        (references [`pg_class`](#catalog-pg-class).`relname`)                      Name of view |
| `viewowner` `name`        (references [`pg_authid`](#catalog-pg-authid).`rolname`)                      Name of view's owner |
| `definition` `text`                      View definition (a reconstructed [sql-select](#sql-select) query) |
