# Configuration Parameters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > basebackup_to_shell - example shell pg_basebackup module > Configuration Parameters`
- Source Line Ranges: `574-583, 617-742, 801-821, 838-850, 6240-6254, 6574-6632, 8484-8542`
- Chunk ID: `pg16_configuration_0167_ae086e7c12`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `491ea2b0e26573552e6c36cf12279422e249db0d79657b602970baca3848b14f`

## Retrieval Guidance

- Use When: Configure the example basebackup_to_shell target module.
- Retrieval Keywords: basebackup_to_shell, basebackup_to_shell.command, pg_basebackup target, backup module configuration
- Follow-up Guidance: Review command execution security before enabling shell-backed backup targets.
- Classification Note: The section defines module parameters for invoking shell commands from the base backup target implementation.

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
