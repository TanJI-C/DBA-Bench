# Automatic Vacuuming

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Automatic Vacuuming`
- Source Line Ranges: `4854-5003`
- Chunk ID: `pg16_configuration_0071_cde31abe13`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `71e026c59dd2b6396d080753a0003b06eeacc442545aba27683824cebd0e80b2`

## Retrieval Guidance

- Use When: 需要调优 autovacuum 触发频率、并发、wraparound 防护和 I/O 节流。
- Retrieval Keywords: autovacuum, autovacuum_max_workers, autovacuum_naptime, autovacuum_vacuum_threshold, autovacuum_analyze_threshold, autovacuum_freeze_max_age, autovacuum_vacuum_cost_delay, autovacuum_vacuum_cost_limit
- Follow-up Guidance: 即使 autovacuum=off，防 xid wraparound 的 autovacuum 仍会启动。
- Classification Note: 定义 autovacuum launcher、worker、naptime、threshold/scale factor、freeze age、cost delay/limit。

## Official Source Content

## Automatic Vacuuming

These settings control the behavior of the *autovacuum*
feature.  Refer to [autovacuum](#autovacuum) for more information.
Note that many of these settings can be overridden on a per-table
basis; see [sql-createtable-storage-parameters](#sql-createtable-storage-parameters).

**`autovacuum` (`boolean`)**
: Controls whether the server should run the
autovacuum launcher daemon.  This is on by default; however,
[guc-track-counts](#guc-track-counts) must also be enabled for
autovacuum to work.
This parameter can only be set in the `postgresql.conf`
file or on the server command line; however, autovacuuming can be
disabled for individual tables by changing table storage parameters.

Note that even when this parameter is disabled, the system
will launch autovacuum processes if necessary to
prevent transaction ID wraparound.  See [vacuum-for-wraparound](#vacuum-for-wraparound) for more information.

**`autovacuum_max_workers` (`integer`)**
: Specifies the maximum number of autovacuum processes (other than the
autovacuum launcher) that may be running at any one time.  The default
is three.  This parameter can only be set at server start.

**`autovacuum_naptime` (`integer`)**
: Specifies the minimum delay between autovacuum runs on any given
database.  In each round the daemon examines the
database and issues `VACUUM` and `ANALYZE` commands
as needed for tables in that database.
If this value is specified without units, it is taken as seconds.
The default is one minute (`1min`).
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`autovacuum_vacuum_threshold` (`integer`)**
: Specifies the minimum number of updated or deleted tuples needed
to trigger a `VACUUM` in any one table.
The default is 50 tuples.
This parameter can only be set in the `postgresql.conf`
file or on the server command line;
but the setting can be overridden for individual tables by
changing table storage parameters.

**`autovacuum_vacuum_insert_threshold` (`integer`)**
: Specifies the number of inserted tuples needed to trigger a
`VACUUM` in any one table.
The default is 1000 tuples.  If -1 is specified, autovacuum will not
trigger a `VACUUM` operation on any tables based on
the number of inserts.
This parameter can only be set in the `postgresql.conf`
file or on the server command line;
but the setting can be overridden for individual tables by
changing table storage parameters.

**`autovacuum_analyze_threshold` (`integer`)**
: Specifies the minimum number of inserted, updated or deleted tuples
needed to trigger an `ANALYZE` in any one table.
The default is 50 tuples.
This parameter can only be set in the `postgresql.conf`
file or on the server command line;
but the setting can be overridden for individual tables by
changing table storage parameters.

**`autovacuum_vacuum_scale_factor` (`floating point`)**
: Specifies a fraction of the table size to add to
`autovacuum_vacuum_threshold`
when deciding whether to trigger a `VACUUM`.
The default is 0.2 (20% of table size).
This parameter can only be set in the `postgresql.conf`
file or on the server command line;
but the setting can be overridden for individual tables by
changing table storage parameters.

**`autovacuum_vacuum_insert_scale_factor` (`floating point`)**
: Specifies a fraction of the table size to add to
`autovacuum_vacuum_insert_threshold`
when deciding whether to trigger a `VACUUM`.
The default is 0.2 (20% of table size).
This parameter can only be set in the `postgresql.conf`
file or on the server command line;
but the setting can be overridden for individual tables by
changing table storage parameters.

**`autovacuum_analyze_scale_factor` (`floating point`)**
: Specifies a fraction of the table size to add to
`autovacuum_analyze_threshold`
when deciding whether to trigger an `ANALYZE`.
The default is 0.1 (10% of table size).
This parameter can only be set in the `postgresql.conf`
file or on the server command line;
but the setting can be overridden for individual tables by
changing table storage parameters.

**`autovacuum_freeze_max_age` (`integer`)**
: Specifies the maximum age (in transactions) that a table's
`pg_class`.`relfrozenxid` field can
attain before a `VACUUM` operation is forced
to prevent transaction ID wraparound within the table.
Note that the system will launch autovacuum processes to
prevent wraparound even when autovacuum is otherwise disabled.

Vacuum also allows removal of old files from the
`pg_xact` subdirectory, which is why the default
is a relatively low 200 million transactions.
This parameter can only be set at server start, but the setting
can be reduced for individual tables by
changing table storage parameters.
For more information see [vacuum-for-wraparound](#vacuum-for-wraparound).

**`autovacuum_multixact_freeze_max_age` (`integer`)**
: Specifies the maximum age (in multixacts) that a table's
`pg_class`.`relminmxid` field can
attain before a `VACUUM` operation is forced to
prevent multixact ID wraparound within the table.
Note that the system will launch autovacuum processes to
prevent wraparound even when autovacuum is otherwise disabled.

Vacuuming multixacts also allows removal of old files from the
`pg_multixact/members` and `pg_multixact/offsets`
subdirectories, which is why the default is a relatively low
400 million multixacts.
This parameter can only be set at server start, but the setting can
be reduced for individual tables by changing table storage parameters.
For more information see [vacuum-for-multixact-wraparound](#vacuum-for-multixact-wraparound).

**`autovacuum_vacuum_cost_delay` (`floating point`)**
: Specifies the cost delay value that will be used in automatic
`VACUUM` operations.  If -1 is specified, the regular
[guc-vacuum-cost-delay](#guc-vacuum-cost-delay) value will be used.
If this value is specified without units, it is taken as milliseconds.
The default value is 2 milliseconds.
This parameter can only be set in the `postgresql.conf`
file or on the server command line;
but the setting can be overridden for individual tables by
changing table storage parameters.

**`autovacuum_vacuum_cost_limit` (`integer`)**
: Specifies the cost limit value that will be used in automatic
`VACUUM` operations.  If -1 is specified (which is the
default), the regular
[guc-vacuum-cost-limit](#guc-vacuum-cost-limit) value will be used.  Note that
the value is distributed proportionally among the running autovacuum
workers, if there is more than one, so that the sum of the limits for
each worker does not exceed the value of this variable.
This parameter can only be set in the `postgresql.conf`
file or on the server command line;
but the setting can be overridden for individual tables by
changing table storage parameters.
