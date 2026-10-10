# Storage Parameters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_table.md`
- Source Title: `create table`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE TABLE > Storage Parameters`
- Source Line Ranges: `768-943`
- Chunk ID: `pg16_configuration_0220_ddad91ea38`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `876dc6e529ea39c710150d59fb6acea71a844fead3591214fc5bcf955e65b29b`

## Retrieval Guidance

- Use When: Use when choosing per-table storage, TOAST, autovacuum, or planner reloptions.
- Retrieval Keywords: CREATE TABLE WITH, Storage Parameters, fillfactor, autovacuum_enabled, toast_tuple_target, parallel_workers
- Follow-up Guidance: Validate parameter applicability and whether later VACUUM FULL/CLUSTER/rewrite is needed for changes.
- Classification Note: Storage parameters configure table/TOAST/autovacuum/storage behavior at relation creation time.

## Official Source Content

### Storage Parameters

The `WITH` clause can specify *storage parameters*
for tables, and for indexes associated with a `UNIQUE`,
`PRIMARY KEY`, or `EXCLUDE` constraint.
Storage parameters for
indexes are documented in [sql-createindex](#sql-createindex).
The storage parameters currently
available for tables are listed below.  For many of these parameters, as
shown, there is an additional parameter with the same name prefixed with
`toast.`, which controls the behavior of the
table's secondary TOAST table, if any
(see [storage-toast](#storage-toast) for more information about TOAST).
If a table parameter value is set and the
equivalent `toast.` parameter is not, the TOAST table
will use the table's parameter value.
Specifying these parameters for partitioned tables is not supported,
but you may specify them for individual leaf partitions.

**`fillfactor` (`integer`)**
: The fillfactor for a table is a percentage between 10 and 100.
100 (complete packing) is the default.  When a smaller fillfactor
is specified, `INSERT` operations pack table pages only
to the indicated percentage; the remaining space on each page is
reserved for updating rows on that page.  This gives `UPDATE`
a chance to place the updated copy of a row on the same page as the
original, which is more efficient than placing it on a different
page, and makes [heap-only tuple
updates](#storage-hot) more likely.
For a table whose entries are never updated, complete packing is the
best choice, but in heavily updated tables smaller fillfactors are
appropriate.  This parameter cannot be set for TOAST tables.

**`toast_tuple_target` (`integer`)**
: The toast_tuple_target specifies the minimum tuple length required before
we try to compress and/or move long column values into TOAST tables, and
is also the target length we try to reduce the length below once toasting
begins. This affects columns marked as External (for move),
Main (for compression), or Extended (for both) and applies only to new
tuples. There is no effect on existing rows.
By default this parameter is set to allow at least 4 tuples per block,
which with the default block size will be 2040 bytes. Valid values are
between 128 bytes and the (block size - header), by default 8160 bytes.
Changing this value may not be useful for very short or very long rows.
Note that the default setting is often close to optimal, and
it is possible that setting this parameter could have negative
effects in some cases.
This parameter cannot be set for TOAST tables.

**`parallel_workers` (`integer`)**
: This sets the number of workers that should be used to assist a parallel
scan of this table.  If not set, the system will determine a value based
on the relation size.  The actual number of workers chosen by the planner
or by utility statements that use parallel scans may be less, for example
due to the setting of [guc-max-worker-processes](#guc-max-worker-processes).

**`autovacuum_enabled`, `toast.autovacuum_enabled` (`boolean`)**
: Enables or disables the autovacuum daemon for a particular table.
If true, the autovacuum daemon will perform automatic `VACUUM`
and/or `ANALYZE` operations on this table following the rules
discussed in [autovacuum](#autovacuum).
If false, this table will not be autovacuumed, except to prevent
transaction ID wraparound. See [vacuum-for-wraparound](#vacuum-for-wraparound) for
more about wraparound prevention.
Note that the autovacuum daemon does not run at all (except to prevent
transaction ID wraparound) if the [guc-autovacuum](#guc-autovacuum)
parameter is false; setting individual tables' storage parameters does
not override that.  Therefore there is seldom much point in explicitly
setting this storage parameter to `true`, only
to `false`.

**`vacuum_index_cleanup`, `toast.vacuum_index_cleanup` (`enum`)**
: Forces or disables index cleanup when `VACUUM`
is run on this table.  The default value is
`AUTO`.  With `OFF`, index
cleanup is disabled, with `ON` it is enabled,
and with `AUTO` a decision is made dynamically,
each time `VACUUM` runs.  The dynamic behavior
allows `VACUUM` to avoid needlessly scanning
indexes to remove very few dead tuples.  Forcibly disabling all
index cleanup can speed up `VACUUM` very
significantly, but may also lead to severely bloated indexes if
table modifications are frequent.  The
`INDEX_CLEANUP` parameter of [`VACUUM`](#sql-vacuum), if
specified, overrides the value of this option.

**`vacuum_truncate`, `toast.vacuum_truncate` (`boolean`)**
: Enables or disables vacuum to try to truncate off any empty pages
at the end of this table. The default value is `true`.
If `true`, `VACUUM` and
autovacuum do the truncation and the disk space for
the truncated pages is returned to the operating system.
Note that the truncation requires `ACCESS EXCLUSIVE`
lock on the table. The `TRUNCATE` parameter
of [`VACUUM`](#sql-vacuum), if specified, overrides the value
of this option.

**`autovacuum_vacuum_threshold`, `toast.autovacuum_vacuum_threshold` (`integer`)**
: Per-table value for [guc-autovacuum-vacuum-threshold](#guc-autovacuum-vacuum-threshold)
parameter.

**`autovacuum_vacuum_scale_factor`, `toast.autovacuum_vacuum_scale_factor` (`floating point`)**
: Per-table value for [guc-autovacuum-vacuum-scale-factor](#guc-autovacuum-vacuum-scale-factor)
parameter.

**`autovacuum_vacuum_insert_threshold`, `toast.autovacuum_vacuum_insert_threshold` (`integer`)**
: Per-table value for [guc-autovacuum-vacuum-insert-threshold](#guc-autovacuum-vacuum-insert-threshold)
parameter.  The special value of -1 may be used to disable insert vacuums on the table.

**`autovacuum_vacuum_insert_scale_factor`, `toast.autovacuum_vacuum_insert_scale_factor` (`floating point`)**
: Per-table value for [guc-autovacuum-vacuum-insert-scale-factor](#guc-autovacuum-vacuum-insert-scale-factor)
parameter.

**`autovacuum_analyze_threshold` (`integer`)**
: Per-table value for [guc-autovacuum-analyze-threshold](#guc-autovacuum-analyze-threshold)
parameter.

**`autovacuum_analyze_scale_factor` (`floating point`)**
: Per-table value for [guc-autovacuum-analyze-scale-factor](#guc-autovacuum-analyze-scale-factor)
parameter.

**`autovacuum_vacuum_cost_delay`, `toast.autovacuum_vacuum_cost_delay` (`floating point`)**
: Per-table value for [guc-autovacuum-vacuum-cost-delay](#guc-autovacuum-vacuum-cost-delay)
parameter.

**`autovacuum_vacuum_cost_limit`, `toast.autovacuum_vacuum_cost_limit` (`integer`)**
: Per-table value for [guc-autovacuum-vacuum-cost-limit](#guc-autovacuum-vacuum-cost-limit)
parameter.

**`autovacuum_freeze_min_age`, `toast.autovacuum_freeze_min_age` (`integer`)**
: Per-table value for [guc-vacuum-freeze-min-age](#guc-vacuum-freeze-min-age)
parameter.  Note that autovacuum will ignore
per-table `autovacuum_freeze_min_age` parameters that are
larger than half the
system-wide [guc-autovacuum-freeze-max-age](#guc-autovacuum-freeze-max-age) setting.

**`autovacuum_freeze_max_age`, `toast.autovacuum_freeze_max_age` (`integer`)**
: Per-table value for [guc-autovacuum-freeze-max-age](#guc-autovacuum-freeze-max-age)
parameter.  Note that autovacuum will ignore
per-table `autovacuum_freeze_max_age` parameters that are
larger than the system-wide setting (it can only be set smaller).

**`autovacuum_freeze_table_age`, `toast.autovacuum_freeze_table_age` (`integer`)**
: Per-table value for [guc-vacuum-freeze-table-age](#guc-vacuum-freeze-table-age)
parameter.

**`autovacuum_multixact_freeze_min_age`, `toast.autovacuum_multixact_freeze_min_age` (`integer`)**
: Per-table value for [guc-vacuum-multixact-freeze-min-age](#guc-vacuum-multixact-freeze-min-age)
parameter.  Note that autovacuum will ignore
per-table `autovacuum_multixact_freeze_min_age` parameters
that are larger than half the
system-wide [guc-autovacuum-multixact-freeze-max-age](#guc-autovacuum-multixact-freeze-max-age)
setting.

**`autovacuum_multixact_freeze_max_age`, `toast.autovacuum_multixact_freeze_max_age` (`integer`)**
: Per-table value
for [guc-autovacuum-multixact-freeze-max-age](#guc-autovacuum-multixact-freeze-max-age) parameter.
Note that autovacuum will ignore
per-table `autovacuum_multixact_freeze_max_age` parameters
that are larger than the system-wide setting (it can only be set
smaller).

**`autovacuum_multixact_freeze_table_age`, `toast.autovacuum_multixact_freeze_table_age` (`integer`)**
: Per-table value
for [guc-vacuum-multixact-freeze-table-age](#guc-vacuum-multixact-freeze-table-age) parameter.

**`log_autovacuum_min_duration`, `toast.log_autovacuum_min_duration` (`integer`)**
: Per-table value for [guc-log-autovacuum-min-duration](#guc-log-autovacuum-min-duration)
parameter.

**`user_catalog_table` (`boolean`)**
: Declare the table as an additional catalog table for purposes of
logical replication. See
[logicaldecoding-capabilities](#logicaldecoding-capabilities) for details.
This parameter cannot be set for TOAST tables.
