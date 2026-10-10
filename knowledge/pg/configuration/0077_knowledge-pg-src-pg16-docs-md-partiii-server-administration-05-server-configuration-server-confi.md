# bytea/xml/gin/createrole/restrict defaults

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Client Connection Defaults > Statement Behavior > bytea/xml/gin/createrole/restrict defaults`
- Source Line Ranges: `249-359, 3651-4707, 5004-5856`
- Chunk ID: `pg16_configuration_0077_7016ed177d`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f5af7077d89df165c2a2a816342258665c8c8ccac3b66cfc0c48c82b8b81f276`

## Retrieval Guidance

- Use When: 需要设置输出格式、XML 解析默认、GIN pending list、CREATEROLE 自动 grant 或限制非系统关系访问。
- Retrieval Keywords: bytea_output, xmlbinary, xmloption, gin_pending_list_limit, createrole_self_grant, restrict_nonsystem_relation_kind
- Follow-up Guidance: createrole_self_grant 涉及权限模型，变更需安全审查。
- Classification Note: 定义 bytea_output、xmlbinary、xmloption、gin_pending_list_limit、createrole_self_grant、restrict_nonsystem_relation_kind。

## Official Source Content

### Managing Configuration File Contents

PostgreSQL provides several features for breaking
down complex `postgresql.conf` files into sub-files.
These features are especially useful when managing multiple servers
with related, but not identical, configurations.

In addition to individual parameter settings,
the `postgresql.conf` file can contain *include
directives*, which specify another file to read and process as if
it were inserted into the configuration file at this point.  This
feature allows a configuration file to be divided into physically
separate parts.  Include directives simply look like:

```
include 'filename'
```

If the file name is not an absolute path, it is taken as relative to
the directory containing the referencing configuration file.
Inclusions can be nested.

There is also an `include_if_exists` directive, which acts
the same as the `include` directive, except
when the referenced file does not exist or cannot be read.  A regular
`include` will consider this an error condition, but
`include_if_exists` merely logs a message and continues
processing the referencing configuration file.

The `postgresql.conf` file can also contain
`include_dir` directives, which specify an entire
directory of configuration files to include.  These look like

```
include_dir 'directory'
```

Non-absolute directory names are taken as relative to the directory
containing the referencing configuration file.  Within the specified
directory, only non-directory files whose names end with the
suffix `.conf` will be included.  File names that
start with the `.` character are also ignored, to
prevent mistakes since such files are hidden on some platforms.  Multiple
files within an include directory are processed in file name order
(according to C locale rules, i.e., numbers before letters, and
uppercase letters before lowercase ones).

Include files or directories can be used to logically separate portions
of the database configuration, rather than having a single large
`postgresql.conf` file.  Consider a company that has two
database servers, each with a different amount of memory.  There are
likely elements of the configuration both will share, for things such
as logging.  But memory-related parameters on the server will vary
between the two.  And there might be server specific customizations,
too.  One way to manage this situation is to break the custom
configuration changes for your site into three files.  You could add
this to the end of your `postgresql.conf` file to include
them:

```
include 'shared.conf'
include 'memory.conf'
include 'server.conf'
```

All systems would have the same `shared.conf`.  Each
server with a particular amount of memory could share the
same `memory.conf`; you might have one for all servers
with 8GB of RAM, another for those having 16GB.  And
finally `server.conf` could have truly server-specific
configuration information in it.

Another possibility is to create a configuration file directory and
put this information into files there. For example, a `conf.d`
directory could be referenced at the end of `postgresql.conf`:

```
include_dir 'conf.d'
```

Then you could name the files in the `conf.d` directory
like this:

```
00shared.conf
01memory.conf
02server.conf
```

This naming convention establishes a clear order in which these
files will be loaded.  This is important because only the last
setting encountered for a particular parameter while the server is
reading configuration files will be used.  In this example,
something set in `conf.d/02server.conf` would override a
value set in `conf.d/01memory.conf`.

You might instead use this approach to naming the files
descriptively:

```
00shared.conf
01memory-8GB.conf
02server-foo.conf
```

This sort of arrangement gives a unique name for each configuration file
variation.  This can help eliminate ambiguity when several servers have
their configurations all stored in one place, such as in a version
control repository.  (Storing database configuration files under version
control is another good practice to consider.)

## Error Reporting and Logging

### Where to Log

**`log_destination` (`string`)**
: PostgreSQL supports several methods
for logging server messages, including
stderr, csvlog,
jsonlog, and
syslog. On Windows,
eventlog is also supported. Set this
parameter to a list of desired log destinations separated by
commas. The default is to log to stderr
only.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

If csvlog is included in `log_destination`,
log entries are output in "comma separated
value" (CSV) format, which is convenient for
loading logs into programs.
See [runtime-config-logging-csvlog](#runtime-config-logging-csvlog) for details.
[guc-logging-collector](#guc-logging-collector) must be enabled to generate
CSV-format log output.

If jsonlog is included in
`log_destination`, log entries are output in
JSON format, which is convenient for loading logs
into programs.
See [runtime-config-logging-jsonlog](#runtime-config-logging-jsonlog) for details.
[guc-logging-collector](#guc-logging-collector) must be enabled to generate
JSON-format log output.

When either stderr,
csvlog or jsonlog are
included, the file `current_logfiles` is created to
record the location of the log file(s) currently in use by the logging
collector and the associated logging destination. This provides a
convenient way to find the logs currently in use by the instance. Here
is an example of this file's content:

```
stderr log/postgresql.log
csvlog log/postgresql.csv
jsonlog log/postgresql.json
```

`current_logfiles` is recreated when a new log file
is created as an effect of rotation, and
when `log_destination` is reloaded.  It is removed when
none of stderr,
csvlog or jsonlog are
included in `log_destination`, and when the logging
collector is disabled.

> **Note:**
> On most Unix systems, you will need to alter the configuration of
> your system's syslog daemon in order
> to make use of the syslog option for
> `log_destination`.  PostgreSQL
> can log to syslog facilities
> `LOCAL0` through `LOCAL7` (see  linkend="guc-syslog-facility"/>), but the default
> syslog configuration on most platforms
> will discard all such messages.  You will need to add something like:
> ```
> local0.*    /var/log/postgresql
> ```
> to the  syslog daemon's configuration file
> to make it work.
>
>
> On Windows, when you use the `eventlog`
> option for `log_destination`, you should
> register an event source and its library with the operating
> system so that the Windows Event Viewer can display event
> log messages cleanly.
> See [event-log-registration](#event-log-registration) for details.
>

**`logging_collector` (`boolean`)**
: This parameter enables the *logging collector*, which
is a background process that captures log messages
sent to stderr and redirects them into log files.
This approach is often more useful than
logging to syslog, since some types of messages
might not appear in syslog output.  (One common
example is dynamic-linker failure messages; another is error messages
produced by scripts such as `archive_command`.)
This parameter can only be set at server start.

> **Note:**
> It is possible to log to stderr without using the
> logging collector; the log messages will just go to wherever the
> server's stderr is directed.  However, that method is
> only suitable for low log volumes, since it provides no convenient
> way to rotate log files.  Also, on some platforms not using the
> logging collector can result in lost or garbled log output, because
> multiple processes writing concurrently to the same log file can
> overwrite each other's output.
>

> **Note:**
> The logging collector is designed to never lose messages.  This means
> that in case of extremely high load, server processes could be
> blocked while trying to send additional log messages when the
> collector has fallen behind.  In contrast, syslog
> prefers to drop messages if it cannot write them, which means it
> may fail to log some messages in such cases but it will not block
> the rest of the system.
>

**`log_directory` (`string`)**
: When `logging_collector` is enabled,
this parameter determines the directory in which log files will be created.
It can be specified as an absolute path, or relative to the
cluster data directory.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.
The default is `log`.

**`log_filename` (`string`)**
: When `logging_collector` is enabled,
this parameter sets the file names of the created log files.  The value
is treated as a `strftime` pattern,
so `%`-escapes can be used to specify time-varying
file names.  (Note that if there are
any time-zone-dependent `%`-escapes, the computation
is done in the zone specified
by [guc-log-timezone](#guc-log-timezone).)
The supported `%`-escapes are similar to those
listed in the Open Group's [strftime
](https://pubs.opengroup.org/onlinepubs/009695399/functions/strftime.html) specification.
Note that the system's `strftime` is not used
directly, so platform-specific (nonstandard) extensions do not work.
The default is `postgresql-%Y-%m-%d_%H%M%S.log`.

If you specify a file name without escapes, you should plan to
use a log rotation utility to avoid eventually filling the
entire disk.  In releases prior to 8.4, if
no `%` escapes were
present, PostgreSQL would append
the epoch of the new log file's creation time, but this is no
longer the case.

If CSV-format output is enabled in `log_destination`,
`.csv` will be appended to the timestamped
log file name to create the file name for CSV-format output.
(If `log_filename` ends in `.log`, the suffix is
replaced instead.)

If JSON-format output is enabled in `log_destination`,
`.json` will be appended to the timestamped
log file name to create the file name for JSON-format output.
(If `log_filename` ends in `.log`, the suffix is
replaced instead.)

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`log_file_mode` (`integer`)**
: On Unix systems this parameter sets the permissions for log files
when `logging_collector` is enabled. (On Microsoft
Windows this parameter is ignored.)
The parameter value is expected to be a numeric mode
specified in the format accepted by the
`chmod` and `umask`
system calls.  (To use the customary octal format the number
must start with a `0` (zero).)

The default permissions are `0600`, meaning only the
server owner can read or write the log files.  The other commonly
useful setting is `0640`, allowing members of the owner's
group to read the files.  Note however that to make use of such a
setting, you'll need to alter [guc-log-directory](#guc-log-directory) to
store the files somewhere outside the cluster data directory.  In
any case, it's unwise to make the log files world-readable, since
they might contain sensitive data.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`log_rotation_age` (`integer`)**
: When `logging_collector` is enabled,
this parameter determines the maximum amount of time to use an
individual log file, after which a new log file will be created.
If this value is specified without units, it is taken as minutes.
The default is 24 hours.
Set to zero to disable time-based creation of new log files.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`log_rotation_size` (`integer`)**
: When `logging_collector` is enabled,
this parameter determines the maximum size of an individual log file.
After this amount of data has been emitted into a log file,
a new log file will be created.
If this value is specified without units, it is taken as kilobytes.
The default is 10 megabytes.
Set to zero to disable size-based creation of new log files.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`log_truncate_on_rotation` (`boolean`)**
: When `logging_collector` is enabled,
this parameter will cause PostgreSQL to truncate (overwrite),
rather than append to, any existing log file of the same name.
However, truncation will occur only when a new file is being opened
due to time-based rotation, not during server startup or size-based
rotation.  When off, pre-existing files will be appended to in
all cases.  For example, using this setting in combination with
a `log_filename` like `postgresql-%H.log`
would result in generating twenty-four hourly log files and then
cyclically overwriting them.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

Example:  To keep 7 days of logs, one log file per day named
`server_log.Mon`, `server_log.Tue`,
etc., and automatically overwrite last week's log with this week's log,
set `log_filename` to `server_log.%a`,
`log_truncate_on_rotation` to `on`, and
`log_rotation_age` to `1440`.

Example: To keep 24 hours of logs, one log file per hour, but
also rotate sooner if the log file size exceeds 1GB, set
`log_filename` to `server_log.%H%M`,
`log_truncate_on_rotation` to `on`,
`log_rotation_age` to `60`, and
`log_rotation_size` to `1000000`.
Including `%M` in `log_filename` allows
any size-driven rotations that might occur to select a file name
different from the hour's initial file name.

**`syslog_facility` (`enum`)**
: When logging to syslog is enabled, this parameter
determines the syslog
"facility" to be used.  You can choose
from `LOCAL0`, `LOCAL1`,
`LOCAL2`, `LOCAL3`, `LOCAL4`,
`LOCAL5`, `LOCAL6`, `LOCAL7`;
the default is `LOCAL0`. See also the
documentation of your system's
syslog daemon.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`syslog_ident` (`string`)**
: When logging to syslog is enabled, this parameter
determines the program name used to identify
PostgreSQL messages in
syslog logs. The default is
`postgres`.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`syslog_sequence_numbers` (`boolean`)**
: When logging to syslog and this is on (the
default), then each message will be prefixed by an increasing
sequence number (such as `[2]`).  This circumvents
the "--- last message repeated N times ---" suppression
that many syslog implementations perform by default.  In more modern
syslog implementations, repeated message suppression can be configured
(for example, `$RepeatedMsgReduction`
in rsyslog), so this might not be
necessary.  Also, you could turn this off if you actually want to
suppress repeated messages.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`syslog_split_messages` (`boolean`)**
: When logging to syslog is enabled, this parameter
determines how messages are delivered to syslog.  When on (the
default), messages are split by lines, and long lines are split so
that they will fit into 1024 bytes, which is a typical size limit for
traditional syslog implementations.  When off, PostgreSQL server log
messages are delivered to the syslog service as is, and it is up to
the syslog service to cope with the potentially bulky messages.

If syslog is ultimately logging to a text file, then the effect will
be the same either way, and it is best to leave the setting on, since
most syslog implementations either cannot handle large messages or
would need to be specially configured to handle them.  But if syslog
is ultimately writing into some other medium, it might be necessary or
more useful to keep messages logically together.

This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`event_source` (`string`)**
: When logging to event log is enabled, this parameter
determines the program name used to identify
PostgreSQL messages in
the log. The default is `PostgreSQL`.
This parameter can only be set at server start.

### When to Log

**`log_min_messages` (`enum`)**
: Controls which [message
levels](#runtime-config-severity-levels) are written to the server log.
Valid values are `DEBUG5`, `DEBUG4`,
`DEBUG3`, `DEBUG2`, `DEBUG1`,
`INFO`, `NOTICE`, `WARNING`,
`ERROR`, `LOG`, `FATAL`, and
`PANIC`.  Each level includes all the levels that
follow it.  The later the level, the fewer messages are sent
to the log.  The default is `WARNING`.  Note that
`LOG` has a different rank here than in
[guc-client-min-messages](#guc-client-min-messages).
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_min_error_statement` (`enum`)**
: Controls which SQL statements that cause an error
condition are recorded in the server log.  The current
SQL statement is included in the log entry for any message of
the specified
[severity](#runtime-config-severity-levels)
or higher.
Valid values are `DEBUG5`,
`DEBUG4`, `DEBUG3`,
`DEBUG2`, `DEBUG1`,
`INFO`, `NOTICE`,
`WARNING`, `ERROR`,
`LOG`,
`FATAL`, and `PANIC`.
The default is `ERROR`, which means statements
causing errors, log messages, fatal errors, or panics will be logged.
To effectively turn off logging of failing statements,
set this parameter to `PANIC`.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_min_duration_statement` (`integer`)**
: Causes the duration of each completed statement to be logged
if the statement ran for at least the specified amount of time.
For example, if you set it to `250ms`
then all SQL statements that run 250ms or longer will be
logged.  Enabling this parameter can be helpful in tracking down
unoptimized queries in your applications.
If this value is specified without units, it is taken as milliseconds.
Setting this to zero prints all statement durations.
`-1` (the default) disables logging statement
durations.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

This overrides [guc-log-min-duration-sample](#guc-log-min-duration-sample),
meaning that queries with duration exceeding this setting are not
subject to sampling and are always logged.

For clients using extended query protocol, durations of the Parse,
Bind, and Execute steps are logged independently.

> **Note:**
> When using this option together with
> [guc-log-statement](#guc-log-statement),
> the text of statements that are logged because of
> `log_statement` will not be repeated in the
> duration log message.
> If you are not using syslog, it is recommended
> that you log the PID or session ID using
> [guc-log-line-prefix](#guc-log-line-prefix)
> so that you can link the statement message to the later
> duration message using the process ID or session ID.
>

**`log_min_duration_sample` (`integer`)**
: Allows sampling the duration of completed statements that ran for
at least the specified amount of time.  This produces the same
kind of log entries as
[guc-log-min-duration-statement](#guc-log-min-duration-statement), but only for a
subset of the executed statements, with sample rate controlled by
[guc-log-statement-sample-rate](#guc-log-statement-sample-rate).
For example, if you set it to `100ms` then all
SQL statements that run 100ms or longer will be considered for
sampling.  Enabling this parameter can be helpful when the
traffic is too high to log all queries.
If this value is specified without units, it is taken as milliseconds.
Setting this to zero samples all statement durations.
`-1` (the default) disables sampling statement
durations.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

This setting has lower priority
than `log_min_duration_statement`, meaning that
statements with durations
exceeding `log_min_duration_statement` are not
subject to sampling and are always logged.

Other notes for `log_min_duration_statement`
apply also to this setting.

**`log_statement_sample_rate` (`floating point`)**
: Determines the fraction of statements with duration exceeding
[guc-log-min-duration-sample](#guc-log-min-duration-sample) that will be logged.
Sampling is stochastic, for example `0.5` means
there is statistically one chance in two that any given statement
will be logged.
The default is `1.0`, meaning to log all sampled
statements.
Setting this to zero disables sampled statement-duration logging,
the same as setting
`log_min_duration_sample` to
`-1`.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_transaction_sample_rate` (`floating point`)**
: Sets the fraction of transactions whose statements are all logged,
in addition to statements logged for other reasons.  It applies to
each new transaction regardless of its statements' durations.
Sampling is stochastic, for example `0.1` means
there is statistically one chance in ten that any given transaction
will be logged.
`log_transaction_sample_rate` can be helpful to
construct a sample of transactions.
The default is `0`, meaning not to log
statements from any additional transactions.  Setting this
to `1` logs all statements of all transactions.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

> **Note:**
> Like all statement-logging options, this option can add significant
> overhead.
>

**`log_startup_progress_interval` (`integer`)**
: Sets the amount of time after which the startup process will log
a message about a long-running operation that is still in progress,
as well as the interval between further progress messages for that
operation. The default is 10 seconds. A setting of `0`
disables the feature.  If this value is specified without units,
it is taken as milliseconds.  This setting is applied separately to
each operation.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

For example, if syncing the data directory takes 25 seconds and
thereafter resetting unlogged relations takes 8 seconds, and if this
setting has the default value of 10 seconds, then a messages will be
logged for syncing the data directory after it has been in progress
for 10 seconds and again after it has been in progress for 20 seconds,
but nothing will be logged for resetting unlogged relations.

[runtime-config-severity-levels](#runtime-config-severity-levels) explains the message
severity levels used by PostgreSQL.  If logging output
is sent to syslog or Windows'
eventlog, the severity levels are translated
as shown in the table.

| Severity | Usage | syslog | eventlog |
| --- | --- | --- | --- |
| `DEBUG1 .. DEBUG5` | Provides successively-more-detailed information for use by          developers. | `DEBUG` | `INFORMATION` |
| `INFO` | Provides information implicitly requested by the user,          e.g., output from `VACUUM VERBOSE`. | `INFO` | `INFORMATION` |
| `NOTICE` | Provides information that might be helpful to users, e.g.,          notice of truncation of long identifiers. | `NOTICE` | `INFORMATION` |
| `WARNING` | Provides warnings of likely problems, e.g., `COMMIT`          outside a transaction block. | `NOTICE` | `WARNING` |
| `ERROR` | Reports an error that caused the current command to          abort. | `WARNING` | `ERROR` |
| `LOG` | Reports information of interest to administrators, e.g.,          checkpoint activity. | `INFO` | `INFORMATION` |
| `FATAL` | Reports an error that caused the current session to          abort. | `ERR` | `ERROR` |
| `PANIC` | Reports an error that caused all database sessions to abort. | `CRIT` | `ERROR` |

### What to Log

> **Note:**

> What you choose to log can have security implications;  see
> [logfile-maintenance](#logfile-maintenance).
>

**`application_name` (`string`)**
: The `application_name` can be any string of less than
`NAMEDATALEN` characters (64 characters in a standard build).
It is typically set by an application upon connection to the server.
The name will be displayed in the `pg_stat_activity` view
and included in CSV log entries.  It can also be included in regular
log entries via the [guc-log-line-prefix](#guc-log-line-prefix) parameter.
Only printable ASCII characters may be used in the
`application_name` value.
Other characters are replaced with [C-style hexadecimal escapes](#sql-syntax-strings-escape).

**`debug_print_parse` (`boolean`)**
: These parameters enable various debugging output to be emitted.
When set, they print the resulting parse tree, the query rewriter
output, or the execution plan for each executed query.
These messages are emitted at `LOG` message level, so by
default they will appear in the server log but will not be sent to the
client.  You can change that by adjusting
[guc-client-min-messages](#guc-client-min-messages) and/or
[guc-log-min-messages](#guc-log-min-messages).
These parameters are off by default.

**`debug_pretty_print` (`boolean`)**
: When set, `debug_pretty_print` indents the messages
produced by `debug_print_parse`,
`debug_print_rewritten`, or
`debug_print_plan`.  This results in more readable
but much longer output than the "compact" format used when
it is off.  It is on by default.

**`log_autovacuum_min_duration` (`integer`)**
: Causes each action executed by autovacuum to be logged if it ran for at
least the specified amount of time.  Setting this to zero logs
all autovacuum actions. `-1` disables logging autovacuum
actions. If this value is specified without units, it is taken as milliseconds.
For example, if you set this to
`250ms` then all automatic vacuums and analyzes that run
250ms or longer will be logged.  In addition, when this parameter is
set to any value other than `-1`, a message will be
logged if an autovacuum action is skipped due to a conflicting lock or a
concurrently dropped relation. The default is `10min`.
Enabling this parameter can be helpful in tracking autovacuum activity.
This parameter can only be set in the `postgresql.conf`
file or on the server command line; but the setting can be overridden for
individual tables by changing table storage parameters.

**`log_checkpoints` (`boolean`)**
: Causes checkpoints and restartpoints to be logged in the server log.
Some statistics are included in the log messages, including the number
of buffers written and the time spent writing them.
This parameter can only be set in the `postgresql.conf`
file or on the server command line. The default is on.

**`log_connections` (`boolean`)**
: Causes each attempted connection to the server to be logged,
as well as successful completion of both client authentication (if
necessary) and authorization.
Only superusers and users with the appropriate `SET`
privilege can change this parameter at session start,
and it cannot be changed at all within a session.
The default is `off`.

> **Note:**
> Some client programs, like psql, attempt
> to connect twice while determining if a password is required, so
> duplicate "connection received" messages do not
> necessarily indicate a problem.
>

**`log_disconnections` (`boolean`)**
: Causes session terminations to be logged.  The log output
provides information similar to `log_connections`,
plus the duration of the session.
Only superusers and users with the appropriate `SET`
privilege can change this parameter at session start,
and it cannot be changed at all within a session.
The default is `off`.

**`log_duration` (`boolean`)**
: Causes the duration of every completed statement to be logged.
The default is `off`.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

For clients using extended query protocol, durations of the Parse,
Bind, and Execute steps are logged independently.

> **Note:**
> The difference between enabling `log_duration` and setting
> [guc-log-min-duration-statement](#guc-log-min-duration-statement) to zero is that
> exceeding `log_min_duration_statement` forces the text of
> the query to be logged, but this option doesn't.  Thus, if
> `log_duration` is `on` and
> `log_min_duration_statement` has a positive value, all
> durations are logged but the query text is included only for
> statements exceeding the threshold.  This behavior can be useful for
> gathering statistics in high-load installations.
>

**`log_error_verbosity` (`enum`)**
: Controls the amount of detail written in the server log for each
message that is logged.  Valid values are `TERSE`,
`DEFAULT`, and `VERBOSE`, each adding more
fields to displayed messages.  `TERSE` excludes
the logging of `DETAIL`, `HINT`,
`QUERY`, and `CONTEXT` error information.
`VERBOSE` output includes the `SQLSTATE` error
code (see also [errcodes-appendix](#errcodes-appendix)) and the source code file name, function name,
and line number that generated the error.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_hostname` (`boolean`)**
: By default, connection log messages only show the IP address of the
connecting host. Turning this parameter on causes logging of the
host name as well.  Note that depending on your host name resolution
setup this might impose a non-negligible performance penalty.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`log_line_prefix` (`string`)**
: This is a `printf`-style string that is output at the
beginning of each log line.
`%` characters begin "escape sequences"
that are replaced with status information as outlined below.
Unrecognized escapes are ignored. Other
characters are copied straight to the log line. Some escapes are
only recognized by session processes, and will be treated as empty by
background processes such as the main server process. Status
information may be aligned either left or right by specifying a
numeric literal after the % and before the option. A negative
value will cause the status information to be padded on the
right with spaces to give it a minimum width, whereas a positive
value will pad on the left. Padding can be useful to aid human
readability in log files.

This parameter can only be set in the `postgresql.conf`
file or on the server command line. The default is
`'%m [%p] '` which logs a time stamp and the process ID.

Escape
Effect
Session only

`%a`
Application name
yes

`%u`
User name
yes

`%d`
Database name
yes

`%r`
Remote host name or IP address, and remote port
yes

`%h`
Remote host name or IP address
yes

`%b`
Backend type
no

`%p`
Process ID
no

`%P`
Process ID of the parallel group leader, if this process
is a parallel query worker
no

`%t`
Time stamp without milliseconds
no

`%m`
Time stamp with milliseconds
no

`%n`
Time stamp with milliseconds (as a Unix epoch)
no

`%i`
Command tag: type of session's current command
yes

`%e`
SQLSTATE error code
no

`%c`
Session ID: see below
no

`%l`
Number of the log line for each session or process, starting at 1
no

`%s`
Process start time stamp
no

`%v`
Virtual transaction ID (backendID/localXID);  see
[transaction-id](#transaction-id)
no

`%x`
Transaction ID (0 if none is assigned);  see
[transaction-id](#transaction-id)
no

`%q`
Produces no output, but tells non-session
processes to stop at this point in the string; ignored by
session processes
no

`%Q`
Query identifier of the current query.  Query
identifiers are not computed by default, so this field
will be zero unless [guc-compute-query-id](#guc-compute-query-id)
parameter is enabled or a third-party module that computes
query identifiers is configured.
yes

`%%`
Literal `%`
no

The backend type corresponds to the column
`backend_type` in the view
[
`pg_stat_activity`](#monitoring-pg-stat-activity-view),
but additional types can appear
in the log that don't show in that view.

The `%c` escape prints a quasi-unique session identifier,
consisting of two 4-byte hexadecimal numbers (without leading zeros)
separated by a dot.  The numbers are the process start time and the
process ID, so `%c` can also be used as a space saving way
of printing those items.  For example, to generate the session
identifier from `pg_stat_activity`, use this query:

```
SELECT to_hex(trunc(EXTRACT(EPOCH FROM backend_start))::integer) || '.' ||
to_hex(pid)
FROM pg_stat_activity;
```

> **Tip:**
> If you set a nonempty value for `log_line_prefix`,
> you should usually make its last character be a space, to provide
> visual separation from the rest of the log line.  A punctuation
> character can be used too.
>

> **Tip:**
> Syslog produces its own
> time stamp and process ID information, so you probably do not want to
> include those escapes if you are logging to syslog.
>

> **Tip:**
> The `%q` escape is useful when including information that is
> only available in session (backend) context like user or database
> name.  For example:
> ```
> log_line_prefix = '%m [%p] %q%u@%d/%a '
> ```
>

> **Note:**
> The `%Q` escape always reports a zero identifier
> for lines output by [guc-log-statement](#guc-log-statement) because
> `log_statement` generates output before an
> identifier can be calculated, including invalid statements for
> which an identifier cannot be calculated.
>

**`log_lock_waits` (`boolean`)**
: Controls whether a log message is produced when a session waits
longer than [guc-deadlock-timeout](#guc-deadlock-timeout) to acquire a
lock.  This is useful in determining if lock waits are causing
poor performance.  The default is `off`.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_recovery_conflict_waits` (`boolean`)**
: Controls whether a log message is produced when the startup process
waits longer than `deadlock_timeout`
for recovery conflicts.  This is useful in determining if recovery
conflicts prevent the recovery from applying WAL.

The default is `off`.  This parameter can only be set
in the `postgresql.conf` file or on the server
command line.

**`log_parameter_max_length` (`integer`)**
: If greater than zero, each bind parameter value logged with a
non-error statement-logging message is trimmed to this many bytes.
Zero disables logging of bind parameters for non-error statement logs.
`-1` (the default) allows bind parameters to be
logged in full.
If this value is specified without units, it is taken as bytes.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

This setting only affects log messages printed as a result of
[guc-log-statement](#guc-log-statement),
[guc-log-duration](#guc-log-duration), and related settings.  Non-zero
values of this setting add some overhead, particularly if parameters
are sent in binary form, since then conversion to text is required.

**`log_parameter_max_length_on_error` (`integer`)**
: If greater than zero, each bind parameter value reported in error
messages is trimmed to this many bytes.
Zero (the default) disables including bind parameters in error
messages.
`-1` allows bind parameters to be printed in full.
If this value is specified without units, it is taken as bytes.

Non-zero values of this setting add overhead, as
PostgreSQL will need to store textual
representations of parameter values in memory at the start of each
statement, whether or not an error eventually occurs.  The overhead
is greater when bind parameters are sent in binary form than when
they are sent as text, since the former case requires data
conversion while the latter only requires copying the string.

**`log_statement` (`enum`)**
: Controls which SQL statements are logged. Valid values are
`none` (off), `ddl`, `mod`, and
`all` (all statements). `ddl` logs all data definition
statements, such as `CREATE`, `ALTER`, and
`DROP` statements. `mod` logs all
`ddl` statements, plus data-modifying statements
such as `INSERT`,
`UPDATE`, `DELETE`, `TRUNCATE`,
and `COPY FROM`.
`PREPARE`, `EXECUTE`, and
`EXPLAIN ANALYZE` statements are also logged if their
contained command is of an appropriate type.  For clients using
extended query protocol, logging occurs when an Execute message
is received, and values of the Bind parameters are included
(with any embedded single-quote marks doubled).

The default is `none`.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

> **Note:**
> Statements that contain simple syntax errors are not logged
> even by the `log_statement` = `all` setting,
> because the log message is emitted only after basic parsing has
> been done to determine the statement type.  In the case of extended
> query protocol, this setting likewise does not log statements that
> fail before the Execute phase (i.e., during parse analysis or
> planning).  Set `log_min_error_statement` to
> `ERROR` (or lower) to log such statements.
>
>
> Logged statements might reveal sensitive data and even contain
> plaintext passwords.
>

**`log_replication_commands` (`boolean`)**
: Causes each replication command to be logged in the server log.
See [protocol-replication](#protocol-replication) for more information about
replication command. The default value is `off`.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_temp_files` (`integer`)**
: Controls logging of temporary file names and sizes.
Temporary files can be
created for sorts, hashes, and temporary query results.
If enabled by this setting, a log entry is emitted for each
temporary file, with the file size specified in bytes, when it is deleted.
A value of zero logs all temporary file information, while positive
values log only files whose size is greater than or equal to
the specified amount of data.
If this value is specified without units, it is taken as kilobytes.
The default setting is -1, which disables such logging.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`log_timezone` (`string`)**
: Sets the time zone used for timestamps written in the server log.
Unlike [guc-timezone](#guc-timezone), this value is cluster-wide,
so that all sessions will report timestamps consistently.
The built-in default is `GMT`, but that is typically
overridden in `postgresql.conf`; initdb
will install a setting there corresponding to its system environment.
See [datatype-timezones](#datatype-timezones) for more information.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

### Using CSV-Format Log Output

Including `csvlog` in the `log_destination` list
provides a convenient way to import log files into a database table.
This option emits log lines in comma-separated-values
(CSV) format,
with these columns:
time stamp with milliseconds,
user name,
database name,
process ID,
client host:port number,
session ID,
per-session line number,
command tag,
session start time,
virtual transaction ID,
regular transaction ID,
error severity,
SQLSTATE code,
error message,
error message detail,
hint,
internal query that led to the error (if any),
character count of the error position therein,
error context,
user query that led to the error (if any and enabled by
`log_min_error_statement`),
character count of the error position therein,
location of the error in the PostgreSQL source code
(if `log_error_verbosity` is set to `verbose`),
application name, backend type, process ID of parallel group leader,
and query id.
Here is a sample table definition for storing CSV-format log output:

```
CREATE TABLE postgres_log
(
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
query_id bigint,
PRIMARY KEY (session_id, session_line_num)
);
```

To import a log file into this table, use the `COPY FROM`
command:

```
COPY postgres_log FROM '/full/path/to/logfile.csv' WITH csv;
```

It is also possible to access the file as a foreign table, using
the supplied [file-fdw](#file-fdw) module.

There are a few things you need to do to simplify importing CSV log
files:

1. Set `log_filename` and
`log_rotation_age` to provide a consistent,
predictable naming scheme for your log files.  This lets you
predict what the file name will be and know when an individual log
file is complete and therefore ready to be imported.
2. Set `log_rotation_size` to 0 to disable
size-based log rotation, as it makes the log file name difficult
to predict.
3. Set `log_truncate_on_rotation` to `on` so
that old log data isn't mixed with the new in the same file.
4. The table definition above includes a primary key specification.
This is useful to protect against accidentally importing the same
information twice.  The `COPY` command commits all of the
data it imports at one time, so any error will cause the entire
import to fail.  If you import a partial log file and later import
the file again when it is complete, the primary key violation will
cause the import to fail.  Wait until the log is complete and
closed before importing.  This procedure will also protect against
accidentally importing a partial line that hasn't been completely
written, which would also cause `COPY` to fail.

### Using JSON-Format Log Output

Including `jsonlog` in the
`log_destination` list provides a convenient way to
import log files into many different programs. This option emits log
lines in JSON format.

String fields with null values are excluded from output.
Additional fields may be added in the future. User applications that
process `jsonlog` output should ignore unknown fields.

Each log line is serialized as a JSON object with the set of keys and
their associated values shown in [runtime-config-logging-jsonlog-keys-values](#runtime-config-logging-jsonlog-keys-values).

| Key name | Type | Description |
| --- | --- | --- |
| `timestamp` | string | Time stamp with milliseconds |
| `user` | string | User name |
| `dbname` | string | Database name |
| `pid` | number | Process ID |
| `remote_host` | string | Client host |
| `remote_port` | number | Client port |
| `session_id` | string | Session ID |
| `line_num` | number | Per-session line number |
| `ps` | string | Current ps display |
| `session_start` | string | Session start time |
| `vxid` | string | Virtual transaction ID |
| `txid` | string | Regular transaction ID |
| `error_severity` | string | Error severity |
| `state_code` | string | SQLSTATE code |
| `message` | string | Error message |
| `detail` | string | Error message detail |
| `hint` | string | Error message hint |
| `internal_query` | string | Internal query that led to the error |
| `internal_position` | number | Cursor index into internal query |
| `context` | string | Error context |
| `statement` | string | Client-supplied query string |
| `cursor_position` | number | Cursor index into query string |
| `func_name` | string | Error location function name |
| `file_name` | string | File name of error location |
| `file_line_num` | number | File line number of the error location |
| `application_name` | string | Client application name |
| `backend_type` | string | Type of backend |
| `leader_pid` | number | Process ID of leader for active parallel workers |
| `query_id` | number | Query ID |

### Process Title

These settings control how process titles of server processes are
modified.  Process titles are typically viewed using programs like
ps or, on Windows, Process Explorer.
See [monitoring-ps](#monitoring-ps) for details.

**`cluster_name` (`string`)**
: Sets a name that identifies this database cluster (instance) for
various purposes.  The cluster name appears in the process title for
all server processes in this cluster.  Moreover, it is the default
application name for a standby connection (see [guc-synchronous-standby-names](#guc-synchronous-standby-names)).

The name can be any string of less
than `NAMEDATALEN` characters (64 characters in a standard
build). Only printable ASCII characters may be used in the
`cluster_name` value.
Other characters are replaced with [C-style hexadecimal escapes](#sql-syntax-strings-escape).
No name is shown if this parameter is set to the empty string
`''` (which is the default).
This parameter can only be set at server start.

**`update_process_title` (`boolean`)**
: Enables updating of the process title every time a new SQL command
is received by the server.
This setting defaults to `on` on most platforms, but it
defaults to `off` on Windows due to that platform's larger
overhead for updating the process title.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

## Client Connection Defaults

### Statement Behavior

**`client_min_messages` (`enum`)**
: Controls which
[message levels](#runtime-config-severity-levels)
are sent to the client.
Valid values are `DEBUG5`,
`DEBUG4`, `DEBUG3`, `DEBUG2`,
`DEBUG1`, `LOG`, `NOTICE`,
`WARNING`, and `ERROR`.
Each level includes all the levels that follow it.  The later the level,
the fewer messages are sent.  The default is
`NOTICE`.  Note that `LOG` has a different
rank here than in [guc-log-min-messages](#guc-log-min-messages).

`INFO` level messages are always sent to the client.

**`search_path` (`string`)**
: This variable specifies the order in which schemas are searched
when an object (table, data type, function, etc.) is referenced by a
simple name with no schema specified.  When there are objects of
identical names in different schemas, the one found first
in the search path is used.  An object that is not in any of the
schemas in the search path can only be referenced by specifying
its containing schema with a qualified (dotted) name.

The value for `search_path` must be a comma-separated
list of schema names.  Any name that is not an existing schema, or is
a schema for which the user does not have `USAGE`
permission, is silently ignored.

If one of the list items is the special name
`$user`, then the schema having the name returned by
`CURRENT_USER` is substituted, if there is such a schema
and the user has `USAGE` permission for it.
(If not, `$user` is ignored.)

The system catalog schema, `pg_catalog`, is always
searched, whether it is mentioned in the path or not.  If it is
mentioned in the path then it will be searched in the specified
order.  If `pg_catalog` is not in the path then it will
be searched *before* searching any of the path items.

Likewise, the current session's temporary-table schema,
`pg_temp_`nnn``, is always searched if it
exists.  It can be explicitly listed in the path by using the
alias `pg_temp`.  If it is not listed in the path then
it is searched first (even before `pg_catalog`).  However,
the temporary schema is only searched for relation (table, view,
sequence, etc.) and data type names.  It is never searched for
function or operator names.

When objects are created without specifying a particular target
schema, they will be placed in the first valid schema named in
`search_path`.  An error is reported if the search
path is empty.

The default value for this parameter is
`"$user", public`.
This setting supports shared use of a database (where no users
have private schemas, and all share use of `public`),
private per-user schemas, and combinations of these.  Other
effects can be obtained by altering the default search path
setting, either globally or per-user.

For more information on schema handling, see
[ddl-schemas](#ddl-schemas).  In particular, the default
configuration is suitable only when the database has a single user or
a few mutually-trusting users.

The current effective value of the search path can be examined
via the SQL function
`current_schemas`
(see [functions-info](#functions-info)).
This is not quite the same as
examining the value of `search_path`, since
`current_schemas` shows how the items
appearing in `search_path` were resolved.

**`row_security` (`boolean`)**
: This variable controls whether to raise an error in lieu of applying a
row security policy.  When set to `on`, policies apply
normally.  When set to `off`, queries fail which would
otherwise apply at least one policy.  The default is `on`.
Change to `off` where limited row visibility could cause
incorrect results; for example, pg_dump makes that
change by default.  This variable has no effect on roles which bypass
every row security policy, to wit, superusers and roles with
the `BYPASSRLS` attribute.

For more information on row security policies,
see [sql-createpolicy](#sql-createpolicy).

**`default_table_access_method` (`string`)**
: This parameter specifies the default table access method to use when
creating tables or materialized views if the `CREATE`
command does not explicitly specify an access method, or when
`SELECT ... INTO` is used, which does not allow
specifying a table access method. The default is `heap`.

**`default_tablespace` (`string`)**
: This variable specifies the default tablespace in which to create
objects (tables and indexes) when a `CREATE` command does
not explicitly specify a tablespace.

The value is either the name of a tablespace, or an empty string
to specify using the default tablespace of the current database.
If the value does not match the name of any existing tablespace,
PostgreSQL will automatically use the default
tablespace of the current database.  If a nondefault tablespace
is specified, the user must have `CREATE` privilege
for it, or creation attempts will fail.

This variable is not used for temporary tables; for them,
[guc-temp-tablespaces](#guc-temp-tablespaces) is consulted instead.

This variable is also not used when creating databases.
By default, a new database inherits its tablespace setting from
the template database it is copied from.

If this parameter is set to a value other than the empty string
when a partitioned table is created, the partitioned table's
tablespace will be set to that value, which will be used as
the default tablespace for partitions created in the future,
even if `default_tablespace` has changed since then.

For more information on tablespaces,
see [manage-ag-tablespaces](#manage-ag-tablespaces).

**`default_toast_compression` (`enum`)**
: This variable sets the default
[TOAST](#storage-toast)
compression method for values of compressible columns.
(This can be overridden for individual columns by setting
the `COMPRESSION` column option in
`CREATE TABLE` or
`ALTER TABLE`.)
The supported compression methods are `pglz` and
(if PostgreSQL was compiled with
`--with-lz4`) `lz4`.
The default is `pglz`.

**`temp_tablespaces` (`string`)**
: This variable specifies tablespaces in which to create temporary
objects (temp tables and indexes on temp tables) when a
`CREATE` command does not explicitly specify a tablespace.
Temporary files for purposes such as sorting large data sets
are also created in these tablespaces.

The value is a list of names of tablespaces.  When there is more than
one name in the list, PostgreSQL chooses a random
member of the list each time a temporary object is to be created;
except that within a transaction, successively created temporary
objects are placed in successive tablespaces from the list.
If the selected element of the list is an empty string,
PostgreSQL will automatically use the default
tablespace of the current database instead.

When `temp_tablespaces` is set interactively, specifying a
nonexistent tablespace is an error, as is specifying a tablespace for
which the user does not have `CREATE` privilege.  However,
when using a previously set value, nonexistent tablespaces are
ignored, as are tablespaces for which the user lacks
`CREATE` privilege.  In particular, this rule applies when
using a value set in `postgresql.conf`.

The default value is an empty string, which results in all temporary
objects being created in the default tablespace of the current
database.

See also [guc-default-tablespace](#guc-default-tablespace).

**`check_function_bodies` (`boolean`)**
: This parameter is normally on. When set to `off`, it
disables validation of the routine body string during [sql-createfunction](#sql-createfunction) and [sql-createprocedure](#sql-createprocedure).  Disabling validation avoids side
effects of the validation process, in particular preventing false
positives due to problems such as forward references.
Set this parameter
to `off` before loading functions on behalf of other
users; pg_dump does so automatically.

**`default_transaction_isolation` (`enum`)**
: Each SQL transaction has an isolation level, which can be
either "read uncommitted", "read
committed", "repeatable read", or
"serializable".  This parameter controls the
default isolation level of each new transaction. The default
is "read committed".

Consult [mvcc](#mvcc) and [sql-set-transaction](#sql-set-transaction) for more information.

**`default_transaction_read_only` (`boolean`)**
: A read-only SQL transaction cannot alter non-temporary tables.
This parameter controls the default read-only status of each new
transaction. The default is `off` (read/write).

Consult [sql-set-transaction](#sql-set-transaction) for more information.

**`default_transaction_deferrable` (`boolean`)**
: When running at the `serializable` isolation level,
a deferrable read-only SQL transaction may be delayed before
it is allowed to proceed.  However, once it begins executing
it does not incur any of the overhead required to ensure
serializability; so serialization code will have no reason to
force it to abort because of concurrent updates, making this
option suitable for long-running read-only transactions.

This parameter controls the default deferrable status of each
new transaction.  It currently has no effect on read-write
transactions or those operating at isolation levels lower
than `serializable`. The default is `off`.

Consult [sql-set-transaction](#sql-set-transaction) for more information.

**`transaction_isolation` (`enum`)**
: This parameter reflects the current transaction's isolation level.
At the beginning of each transaction, it is set to the current value
of [guc-default-transaction-isolation](#guc-default-transaction-isolation).
Any subsequent attempt to change it is equivalent to a [sql-set-transaction](#sql-set-transaction) command.

**`transaction_read_only` (`boolean`)**
: This parameter reflects the current transaction's read-only status.
At the beginning of each transaction, it is set to the current value
of [guc-default-transaction-read-only](#guc-default-transaction-read-only).
Any subsequent attempt to change it is equivalent to a [sql-set-transaction](#sql-set-transaction) command.

**`transaction_deferrable` (`boolean`)**
: This parameter reflects the current transaction's deferrability status.
At the beginning of each transaction, it is set to the current value
of [guc-default-transaction-deferrable](#guc-default-transaction-deferrable).
Any subsequent attempt to change it is equivalent to a [sql-set-transaction](#sql-set-transaction) command.

**`session_replication_role` (`enum`)**
: Controls firing of replication-related triggers and rules for the
current session.
Possible values are `origin` (the default),
`replica` and `local`.
Setting this parameter results in discarding any previously cached
query plans.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

The intended use of this setting is that logical replication systems
set it to `replica` when they are applying replicated
changes.  The effect of that will be that triggers and rules (that
have not been altered from their default configuration) will not fire
on the replica.  See the [`ALTER TABLE`](#sql-altertable) clauses
`ENABLE TRIGGER` and `ENABLE RULE`
for more information.

PostgreSQL treats the settings `origin` and
`local` the same internally.  Third-party replication
systems may use these two values for their internal purposes, for
example using `local` to designate a session whose
changes should not be replicated.

Since foreign keys are implemented as triggers, setting this parameter
to `replica` also disables all foreign key checks,
which can leave data in an inconsistent state if improperly used.

**`statement_timeout` (`integer`)**
: Abort any statement that takes more than the specified amount of time.
If `log_min_error_statement` is set
to `ERROR` or lower, the statement that timed out
will also be logged.
If this value is specified without units, it is taken as milliseconds.
A value of zero (the default) disables the timeout.

The timeout is measured from the time a command arrives at the
server until it is completed by the server.  If multiple SQL
statements appear in a single simple-Query message, the timeout
is applied to each statement separately.
(PostgreSQL versions before 13 usually
treated the timeout as applying to the whole query string.)
In extended query protocol, the timeout starts running when any
query-related message (Parse, Bind, Execute, Describe) arrives, and
it is canceled by completion of an Execute or Sync message.

Setting `statement_timeout` in
`postgresql.conf` is not recommended because it would
affect all sessions.

**`lock_timeout` (`integer`)**
: Abort any statement that waits longer than the specified amount of
time while attempting to acquire a lock on a table, index,
row, or other database object.  The time limit applies separately to
each lock acquisition attempt.  The limit applies both to explicit
locking requests (such as `LOCK TABLE`, or `SELECT
FOR UPDATE` without `NOWAIT`) and to implicitly-acquired
locks.
If this value is specified without units, it is taken as milliseconds.
A value of zero (the default) disables the timeout.

Unlike `statement_timeout`, this timeout can only occur
while waiting for locks.  Note that if `statement_timeout`
is nonzero, it is rather pointless to set `lock_timeout` to
the same or larger value, since the statement timeout would always
trigger first.  If `log_min_error_statement` is set to
`ERROR` or lower, the statement that timed out will be
logged.

Setting `lock_timeout` in
`postgresql.conf` is not recommended because it would
affect all sessions.

**`idle_in_transaction_session_timeout` (`integer`)**
: Terminate any session that has been idle (that is, waiting for a
client query) within an open transaction for longer than the
specified amount of time.
If this value is specified without units, it is taken as milliseconds.
A value of zero (the default) disables the timeout.

This option can be used to ensure that idle sessions do not hold
locks for an unreasonable amount of time.  Even when no significant
locks are held, an open transaction prevents vacuuming away
recently-dead tuples that may be visible only to this transaction;
so remaining idle for a long time can contribute to table bloat.
See [routine-vacuuming](#routine-vacuuming) for more details.

**`idle_session_timeout` (`integer`)**
: Terminate any session that has been idle (that is, waiting for a
client query), but not within an open transaction, for longer than
the specified amount of time.
If this value is specified without units, it is taken as milliseconds.
A value of zero (the default) disables the timeout.

Unlike the case with an open transaction, an idle session without a
transaction imposes no large costs on the server, so there is less
need to enable this timeout
than `idle_in_transaction_session_timeout`.

Be wary of enforcing this timeout on connections made through
connection-pooling software or other middleware, as such a layer
may not react well to unexpected connection closure.  It may be
helpful to enable this timeout only for interactive sessions,
perhaps by applying it only to particular users.

**`vacuum_freeze_table_age` (`integer`)**
: `VACUUM` performs an aggressive scan if the table's
`pg_class`.`relfrozenxid` field has reached
the age specified by this setting.  An aggressive scan differs from
a regular `VACUUM` in that it visits every page that might
contain unfrozen XIDs or MXIDs, not just those that might contain dead
tuples.  The default is 150 million transactions.  Although users can
set this value anywhere from zero to two billion, `VACUUM`
will silently limit the effective value to 95% of
[guc-autovacuum-freeze-max-age](#guc-autovacuum-freeze-max-age), so that a
periodic manual `VACUUM` has a chance to run before an
anti-wraparound autovacuum is launched for the table. For more
information see
[vacuum-for-wraparound](#vacuum-for-wraparound).

**`vacuum_freeze_min_age` (`integer`)**
: Specifies the cutoff age (in transactions) that
`VACUUM` should use to decide whether to
trigger freezing of pages that have an older XID.
The default is 50 million transactions.  Although
users can set this value anywhere from zero to one billion,
`VACUUM` will silently limit the effective value to half
the value of [guc-autovacuum-freeze-max-age](#guc-autovacuum-freeze-max-age), so
that there is not an unreasonably short time between forced
autovacuums.  For more information see [vacuum-for-wraparound](#vacuum-for-wraparound).

**`vacuum_failsafe_age` (`integer`)**
: Specifies the maximum age (in transactions) that a table's
`pg_class`.`relfrozenxid`
field can attain before `VACUUM` takes
extraordinary measures to avoid system-wide transaction ID
wraparound failure.  This is `VACUUM`'s
strategy of last resort.  The failsafe typically triggers
when an autovacuum to prevent transaction ID wraparound has
already been running for some time, though it's possible for
the failsafe to trigger during any `VACUUM`.

When the failsafe is triggered, any cost-based delay that is
in effect will no longer be applied, further non-essential
maintenance tasks (such as index vacuuming) are bypassed, and any
Buffer Access Strategy
in use will be disabled resulting in `VACUUM` being
free to make use of all of
shared buffers.

The default is 1.6 billion transactions.  Although users can
set this value anywhere from zero to 2.1 billion,
`VACUUM` will silently adjust the effective
value to no less than 105% of [guc-autovacuum-freeze-max-age](#guc-autovacuum-freeze-max-age).

**`vacuum_multixact_freeze_table_age` (`integer`)**
: `VACUUM` performs an aggressive scan if the table's
`pg_class`.`relminmxid` field has reached
the age specified by this setting.  An aggressive scan differs from
a regular `VACUUM` in that it visits every page that might
contain unfrozen XIDs or MXIDs, not just those that might contain dead
tuples.  The default is 150 million multixacts.
Although users can set this value anywhere from zero to two billion,
`VACUUM` will silently limit the effective value to 95% of
[guc-autovacuum-multixact-freeze-max-age](#guc-autovacuum-multixact-freeze-max-age), so that a
periodic manual `VACUUM` has a chance to run before an
anti-wraparound is launched for the table.
For more information see [vacuum-for-multixact-wraparound](#vacuum-for-multixact-wraparound).

**`vacuum_multixact_freeze_min_age` (`integer`)**
: Specifies the cutoff age (in multixacts) that `VACUUM`
should use to decide whether to trigger freezing of pages with
an older multixact ID.  The default is 5 million multixacts.
Although users can set this value anywhere from zero to one billion,
`VACUUM` will silently limit the effective value to half
the value of [guc-autovacuum-multixact-freeze-max-age](#guc-autovacuum-multixact-freeze-max-age),
so that there is not an unreasonably short time between forced
autovacuums.
For more information see [vacuum-for-multixact-wraparound](#vacuum-for-multixact-wraparound).

**`vacuum_multixact_failsafe_age` (`integer`)**
: Specifies the maximum age (in multixacts) that a table's
`pg_class`.`relminmxid`
field can attain before `VACUUM` takes
extraordinary measures to avoid system-wide multixact ID
wraparound failure.  This is `VACUUM`'s
strategy of last resort.  The failsafe typically triggers when
an autovacuum to prevent transaction ID wraparound has already
been running for some time, though it's possible for the
failsafe to trigger during any `VACUUM`.

When the failsafe is triggered, any cost-based delay that is
in effect will no longer be applied, and further non-essential
maintenance tasks (such as index vacuuming) are bypassed.

The default is 1.6 billion multixacts.  Although users can set
this value anywhere from zero to 2.1 billion,
`VACUUM` will silently adjust the effective
value to no less than 105% of [guc-autovacuum-multixact-freeze-max-age](#guc-autovacuum-multixact-freeze-max-age).

**`bytea_output` (`enum`)**
: Sets the output format for values of type `bytea`.
Valid values are `hex` (the default)
and `escape` (the traditional PostgreSQL
format).  See [datatype-binary](#datatype-binary) for more
information.  The `bytea` type always
accepts both formats on input, regardless of this setting.

**`xmlbinary` (`enum`)**
: Sets how binary values are to be encoded in XML.  This applies
for example when `bytea` values are converted to
XML by the functions `xmlelement` or
`xmlforest`.  Possible values are
`base64` and `hex`, which
are both defined in the XML Schema standard.  The default is
`base64`.  For further information about
XML-related functions, see [functions-xml](#functions-xml).

The actual choice here is mostly a matter of taste,
constrained only by possible restrictions in client
applications.  Both methods support all possible values,
although the hex encoding will be somewhat larger than the
base64 encoding.

**`xmloption` (`enum`)**
: Sets whether `DOCUMENT` or
`CONTENT` is implicit when converting between
XML and character string values.  See [datatype-xml](#datatype-xml) for a description of this.  Valid
values are `DOCUMENT` and
`CONTENT`.  The default is
`CONTENT`.

According to the SQL standard, the command to set this option is

```
SET XML OPTION { DOCUMENT | CONTENT };
```

This syntax is also available in PostgreSQL.

**`gin_pending_list_limit` (`integer`)**
: Sets the maximum size of a GIN index's pending list, which is used
when `fastupdate` is enabled. If the list grows
larger than this maximum size, it is cleaned up by moving
the entries in it to the index's main GIN data structure in bulk.
If this value is specified without units, it is taken as kilobytes.
The default is four megabytes (`4MB`). This setting
can be overridden for individual GIN indexes by changing
index storage parameters.
See [gin-fast-update](#gin-fast-update) and [gin-tips](#gin-tips)
for more information.

**`createrole_self_grant` (`string`)**
: If a user who has `CREATEROLE` but not
`SUPERUSER` creates a role, and if this
is set to a non-empty value, the newly-created role will be granted
to the creating user with the options specified. The value must be
`set`, `inherit`, or a
comma-separated list of these. The default value is an empty string,
which disables the feature.

The purpose of this option is to allow a `CREATEROLE`
user who is not a superuser to automatically inherit, or automatically
gain the ability to `SET ROLE` to, any created users.
Since a `CREATEROLE` user is always implicitly granted
`ADMIN OPTION` on created roles, that user could
always execute a `GRANT` statement that would achieve
the same effect as this setting. However, it can be convenient for
usability reasons if the grant happens automatically. A superuser
automatically inherits the privileges of every role and can always
`SET ROLE` to any role, and this setting can be used
to produce a similar behavior for `CREATEROLE` users
for users which they create.

**`restrict_nonsystem_relation_kind` (`string`)**
: Set relation kinds for which access to non-system relations is prohibited.
The value takes the form of a comma-separated list of relation kinds.
Currently, the supported relation kinds are `view` and
`foreign-table`.

### Locale and Formatting

**`DateStyle` (`string`)**
: Sets the display format for date and time values, as well as the
rules for interpreting ambiguous date input values. For
historical reasons, this variable contains two independent
components: the output format specification (`ISO`,
`Postgres`, `SQL`, or `German`)
and the input/output specification for year/month/day ordering
(`DMY`, `MDY`, or `YMD`). These
can be set separately or together. The keywords `Euro`
and `European` are synonyms for `DMY`; the
keywords `US`, `NonEuro`, and
`NonEuropean` are synonyms for `MDY`. See
[datatype-datetime](#datatype-datetime) for more information. The
built-in default is `ISO, MDY`, but
initdb will initialize the
configuration file with a setting that corresponds to the
behavior of the chosen `lc_time` locale.

**`IntervalStyle` (`enum`)**
: Sets the display format for interval values.
The value `sql_standard` will produce
output matching SQL standard interval literals.
The value `postgres` (which is the default) will produce
output matching PostgreSQL releases prior to 8.4
when the [guc-datestyle](#guc-datestyle)
parameter was set to `ISO`.
The value `postgres_verbose` will produce output
matching PostgreSQL releases prior to 8.4
when the `DateStyle`
parameter was set to non-`ISO` output.
The value `iso_8601` will produce output matching the time
interval "format with designators" defined in section
4.4.3.2 of ISO 8601.

The `IntervalStyle` parameter also affects the
interpretation of ambiguous interval input.  See
[datatype-interval-input](#datatype-interval-input) for more information.

**`TimeZone` (`string`)**
: Sets the time zone for displaying and interpreting time stamps.
The built-in default is `GMT`, but that is typically
overridden in `postgresql.conf`; initdb
will install a setting there corresponding to its system environment.
See [datatype-timezones](#datatype-timezones) for more information.

**`timezone_abbreviations` (`string`)**
: Sets the collection of time zone abbreviations that will be accepted
by the server for datetime input.  The default is `'Default'`,
which is a collection that works in most of the world; there are
also `'Australia'` and `'India'`,
and other collections can be defined for a particular installation.
See [datetime-config-files](#datetime-config-files) for more information.

**`extra_float_digits` (`integer`)**
: This parameter adjusts the number of digits used for textual output of
floating-point values, including `float4`, `float8`,
and geometric data types.

If the value is 1 (the default) or above, float values are output in
shortest-precise format; see [datatype-float](#datatype-float). The
actual number of digits generated depends only on the value being
output, not on the value of this parameter. At most 17 digits are
required for `float8` values, and 9 for `float4`
values. This format is both fast and precise, preserving the original
binary float value exactly when correctly read. For historical
compatibility, values up to 3 are permitted.

If the value is zero or negative, then the output is rounded to a
given decimal precision. The precision used is the standard number of
digits for the type (`FLT_DIG`
or `DBL_DIG` as appropriate) reduced according to the
value of this parameter. (For example, specifying -1 will cause
`float4` values to be output rounded to 5 significant
digits, and `float8` values
rounded to 14 digits.) This format is slower and does not preserve all
the bits of the binary float value, but may be more human-readable.

> **Note:**
> The meaning of this parameter, and its default value, changed
> in PostgreSQL 12;
> see [datatype-float](#datatype-float) for further discussion.
>

**`client_encoding` (`string`)**
: Sets the client-side encoding (character set).
The default is to use the database encoding.
The character sets supported by the PostgreSQL
server are described in [multibyte-charset-supported](#multibyte-charset-supported).

**`lc_messages` (`string`)**
: Sets the language in which messages are displayed.  Acceptable
values are system-dependent; see [locale](#locale) for
more information.  If this variable is set to the empty string
(which is the default) then the value is inherited from the
execution environment of the server in a system-dependent way.

On some systems, this locale category does not exist.  Setting
this variable will still work, but there will be no effect.
Also, there is a chance that no translated messages for the
desired language exist.  In that case you will continue to see
the English messages.

Only superusers and users with the appropriate `SET`
privilege can change this setting.

**`lc_monetary` (`string`)**
: Sets the locale to use for formatting monetary amounts, for
example with the `to_char` family of
functions.  Acceptable values are system-dependent; see [locale](#locale) for more information.  If this variable is
set to the empty string (which is the default) then the value
is inherited from the execution environment of the server in a
system-dependent way.

**`lc_numeric` (`string`)**
: Sets the locale to use for formatting numbers, for example
with the `to_char` family of
functions. Acceptable values are system-dependent; see [locale](#locale) for more information.  If this variable is
set to the empty string (which is the default) then the value
is inherited from the execution environment of the server in a
system-dependent way.

**`lc_time` (`string`)**
: Sets the locale to use for formatting dates and times, for example
with the `to_char` family of
functions. Acceptable values are system-dependent; see [locale](#locale) for more information.  If this variable is
set to the empty string (which is the default) then the value
is inherited from the execution environment of the server in a
system-dependent way.

**`icu_validation_level` (`enum`)**
: When ICU locale validation problems are encountered, controls which
[message level](#runtime-config-severity-levels) is
used to report the problem. Valid values are
`DISABLED`, `DEBUG5`,
`DEBUG4`, `DEBUG3`,
`DEBUG2`, `DEBUG1`,
`INFO`, `NOTICE`,
`WARNING`, `ERROR`, and
`LOG`.

If set to `DISABLED`, does not report validation
problems at all. Otherwise reports problems at the given message
level. The default is `WARNING`.

**`default_text_search_config` (`string`)**
: Selects the text search configuration that is used by those variants
of the text search functions that do not have an explicit argument
specifying the configuration.
See [textsearch](#textsearch) for further information.
The built-in default is `pg_catalog.simple`, but
initdb will initialize the
configuration file with a setting that corresponds to the
chosen `lc_ctype` locale, if a configuration
matching that locale can be identified.

### Shared Library Preloading

Several settings are available for preloading shared libraries into the
server, in order to load additional functionality or achieve performance
benefits.  For example, a setting of
`'$libdir/mylib'` would cause
`mylib.so` (or on some platforms,
`mylib.sl`) to be preloaded from the installation's standard
library directory.  The differences between the settings are when they
take effect and what privileges are required to change them.

PostgreSQL procedural language libraries can
be preloaded in this way, typically by using the
syntax `'$libdir/plXXX'` where
`XXX` is `pgsql`, `perl`,
`tcl`, or `python`.

Only shared libraries specifically intended to be used with PostgreSQL
can be loaded this way.  Every PostgreSQL-supported library has
a "magic block" that is checked to guarantee compatibility.  For
this reason, non-PostgreSQL libraries cannot be loaded in this way.  You
might be able to use operating-system facilities such
as `LD_PRELOAD` for that.

In general, refer to the documentation of a specific module for the
recommended way to load that module.

**`local_preload_libraries` (`string`)**
: This variable specifies one or more shared libraries that are to be
preloaded at connection start.
It contains a comma-separated list of library names, where each name
is interpreted as for the [`LOAD`](#sql-load) command.
Whitespace between entries is ignored; surround a library name with
double quotes if you need to include whitespace or commas in the name.
The parameter value only takes effect at the start of the connection.
Subsequent changes have no effect.  If a specified library is not
found, the connection attempt will fail.

This option can be set by any user.  Because of that, the libraries
that can be loaded are restricted to those appearing in the
`plugins` subdirectory of the installation's
standard library directory.  (It is the database administrator's
responsibility to ensure that only "safe" libraries
are installed there.)  Entries in `local_preload_libraries`
can specify this directory explicitly, for example
`$libdir/plugins/mylib`, or just specify
the library name — `mylib` would have
the same effect as `$libdir/plugins/mylib`.

The intent of this feature is to allow unprivileged users to load
debugging or performance-measurement libraries into specific sessions
without requiring an explicit `LOAD` command.  To that end,
it would be typical to set this parameter using
the `PGOPTIONS` environment variable on the client or by
using
`ALTER ROLE SET`.

However, unless a module is specifically designed to be used in this way by
non-superusers, this is usually not the right setting to use.  Look
at [guc-session-preload-libraries](#guc-session-preload-libraries) instead.

**`session_preload_libraries` (`string`)**
: This variable specifies one or more shared libraries that are to be
preloaded at connection start.
It contains a comma-separated list of library names, where each name
is interpreted as for the [`LOAD`](#sql-load) command.
Whitespace between entries is ignored; surround a library name with
double quotes if you need to include whitespace or commas in the name.
The parameter value only takes effect at the start of the connection.
Subsequent changes have no effect.  If a specified library is not
found, the connection attempt will fail.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

The intent of this feature is to allow debugging or
performance-measurement libraries to be loaded into specific sessions
without an explicit
`LOAD` command being given.  For
example, [auto-explain](#auto-explain) could be enabled for all
sessions under a given user name by setting this parameter
with `ALTER ROLE SET`.  Also, this parameter can be changed
without restarting the server (but changes only take effect when a new
session is started), so it is easier to add new modules this way, even
if they should apply to all sessions.

Unlike [guc-shared-preload-libraries](#guc-shared-preload-libraries), there is no large
performance advantage to loading a library at session start rather than
when it is first used.  There is some advantage, however, when
connection pooling is used.

**`shared_preload_libraries` (`string`)**
: This variable specifies one or more shared libraries to be preloaded at
server start.
It contains a comma-separated list of library names, where each name
is interpreted as for the [`LOAD`](#sql-load) command.
Whitespace between entries is ignored; surround a library name with
double quotes if you need to include whitespace or commas in the name.
This parameter can only be set at server start.  If a specified
library is not found, the server will fail to start.

Some libraries need to perform certain operations that can only take
place at postmaster start, such as allocating shared memory, reserving
light-weight locks, or starting background workers.  Those libraries
must be loaded at server start through this parameter.  See the
documentation of each library for details.

Other libraries can also be preloaded.  By preloading a shared library,
the library startup time is avoided when the library is first used.
However, the time to start each new server process might increase
slightly, even if that process never uses the library.  So this
parameter is recommended only for libraries that will be used in most
sessions.  Also, changing this parameter requires a server restart, so
this is not the right setting to use for short-term debugging tasks,
say.  Use [guc-session-preload-libraries](#guc-session-preload-libraries) for that
instead.

> **Note:**
> On Windows hosts, preloading a library at server start will not reduce
> the time required to start each new server process; each server process
> will re-load all preload libraries.  However, `shared_preload_libraries
> ` is still useful on Windows hosts for libraries that need to
> perform operations at postmaster start time.
>

**`jit_provider` (`string`)**
: This variable is the name of the JIT provider library to be used
(see [jit-pluggable](#jit-pluggable)).
The default is `llvmjit`.
This parameter can only be set at server start.

If set to a non-existent library, JIT will not be
available, but no error will be raised. This allows JIT support to be
installed separately from the main
PostgreSQL package.

### Other Defaults

**`dynamic_library_path` (`string`)**
: If a dynamically loadable module needs to be opened and the
file name specified in the `CREATE FUNCTION` or
`LOAD` command
does not have a directory component (i.e., the
name does not contain a slash), the system will search this
path for the required file.

The value for `dynamic_library_path` must be a
list of absolute directory paths separated by colons (or semi-colons
on Windows).  If a list element starts
with the special string `$libdir`, the
compiled-in PostgreSQL package
library directory is substituted for `$libdir`; this
is where the modules provided by the standard
PostgreSQL distribution are installed.
(Use `pg_config --pkglibdir` to find out the name of
this directory.) For example:

```
dynamic_library_path = '/usr/local/lib/postgresql:/home/my_project/lib:$libdir'
```

or, in a Windows environment:

```
dynamic_library_path = 'C:\tools\postgresql;H:\my_project\lib;$libdir'
```

The default value for this parameter is
`'$libdir'`. If the value is set to an empty
string, the automatic path search is turned off.

This parameter can be changed at run time by superusers and users
with the appropriate `SET` privilege, but a
setting done that way will only persist until the end of the
client connection, so this method should be reserved for
development purposes. The recommended way to set this parameter
is in the `postgresql.conf` configuration
file.

**`gin_fuzzy_search_limit` (`integer`)**
: Soft upper limit of the size of the set returned by GIN index scans. For more
information see [gin-tips](#gin-tips).
