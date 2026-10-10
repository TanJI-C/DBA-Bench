# ALTER SYSTEM

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_system.md`
- Source Title: `alter system`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER SYSTEM`
- Source Line Ranges: `1-88`
- Chunk ID: `pg16_configuration_0212_ac61041b65`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `7635ff4d4750e1b82e9b2d9c18045cc94aba443962b6ae0a23ea79f23a993b74`

## Retrieval Guidance

- Use When: Use when changing cluster-wide PostgreSQL configuration through SQL rather than editing postgresql.conf manually.
- Retrieval Keywords: ALTER SYSTEM, postgresql.auto.conf, configuration_parameter, server reload, RESET ALL
- Follow-up Guidance: Reload or restart as required by parameter context and verify with SHOW/pg_settings.
- Classification Note: Direct server configuration command that writes postgresql.auto.conf and sets/resets cluster-wide runtime parameters.

## Official Source Content

ALTER SYSTEM
7
SQL - Language Statements

ALTER SYSTEM
change a server configuration parameter

```
ALTER SYSTEM SET `configuration_parameter` { TO | = } { `value` [, ...] | DEFAULT }

ALTER SYSTEM RESET `configuration_parameter`
ALTER SYSTEM RESET ALL
```

## Description

`ALTER SYSTEM` is used for changing server configuration
parameters across the entire database cluster.  It can be more convenient
than the traditional method of manually editing
the `postgresql.conf` file.
`ALTER SYSTEM` writes the given parameter setting to
the `postgresql.auto.conf` file, which is read in
addition to `postgresql.conf`.
Setting a parameter to `DEFAULT`, or using the
`RESET` variant, removes that configuration entry from the
`postgresql.auto.conf` file. Use `RESET
ALL` to remove all such configuration entries.

Values set with `ALTER SYSTEM` will be effective after
the next server configuration reload, or after the next server restart
in the case of parameters that can only be changed at server start.
A server configuration reload can be commanded by calling the SQL
function `pg_reload_conf()`, running `pg_ctl reload`,
or sending a SIGHUP signal to the main server process.

Only superusers and users granted `ALTER SYSTEM` privilege
on a parameter can change it using `ALTER SYSTEM`.  Also, since
this command acts directly on the file system and cannot be rolled back,
it is not allowed inside a transaction block or function.

## Parameters

**`configuration_parameter`**
: Name of a settable configuration parameter.  Available parameters are
documented in [runtime-config](#runtime-config).

**`value`**
: New value of the parameter.  Values can be specified as string
constants, identifiers, numbers, or comma-separated lists of
these, as appropriate for the particular parameter.
Values that are neither numbers nor valid identifiers must be quoted.
`DEFAULT` can be written to specify removing the
parameter and its value from `postgresql.auto.conf`.

For some list-accepting parameters, quoted values will produce
double-quoted output to preserve whitespace and commas; for others,
double-quotes must be used inside single-quoted strings to get
this effect.

## Notes

This command can't be used to set [guc-data-directory](#guc-data-directory),
nor parameters that are not allowed in `postgresql.conf`
(e.g., [preset options](#runtime-config-preset)).

See [config-setting](#config-setting) for other ways to set the parameters.

## Examples

Set the `wal_level`:

```
ALTER SYSTEM SET wal_level = replica;
```

Undo that, restoring whatever setting was effective
in `postgresql.conf`:

```
ALTER SYSTEM RESET wal_level;
```

## Compatibility

The `ALTER SYSTEM` statement is a
PostgreSQL extension.

## See Also
