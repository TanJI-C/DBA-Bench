# Parameter Interaction via the Shell

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Setting Parameters > Parameter Interaction via the Shell`
- Source Line Ranges: `8-89, 212-248`
- Chunk ID: `pg16_configuration_0028_223388b985`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `44817b45dbdb50528b241a6abb65e54a0cad95b90392af086866a8de4d53e08f`

## Retrieval Guidance

- Use When: 需要在启动命令或客户端环境中临时覆盖配置。
- Retrieval Keywords: postgres -c, PGOPTIONS, environment variable, geqo=off, statement_timeout
- Follow-up Guidance: postgres -c 覆盖配置文件且通常需重启才能变更。
- Classification Note: 说明 postgres -c 和 PGOPTIONS -c 传递参数的作用域与优先级。

## Official Source Content

## Setting Parameters

### Parameter Names and Values

All parameter names are case-insensitive. Every parameter takes a
value of one of five types: boolean, string, integer, floating point,
or enumerated (enum).  The type determines the syntax for setting the
parameter:

- *Boolean:*
Values can be written as
`on`,
`off`,
`true`,
`false`,
`yes`,
`no`,
`1`,
`0`
(all case-insensitive) or any unambiguous prefix of one of these.
- *String:*
In general, enclose the value in single quotes, doubling any single
quotes within the value.  Quotes can usually be omitted if the value
is a simple number or identifier, however.
(Values that match an SQL keyword require quoting in some contexts.)
- *Numeric (integer and floating point):*
Numeric parameters can be specified in the customary integer and
floating-point formats; fractional values are rounded to the nearest
integer if the parameter is of integer type.  Integer parameters
additionally accept hexadecimal input (beginning
with `0x`) and octal input (beginning
with `0`), but these formats cannot have a fraction.
Do not use thousands separators.
Quotes are not required, except for hexadecimal input.
- *Numeric with Unit:*
Some numeric parameters have an implicit unit, because they describe
quantities of memory or time. The unit might be bytes, kilobytes, blocks
(typically eight kilobytes), milliseconds, seconds, or minutes.
An unadorned numeric value for one of these settings will use the
setting's default unit, which can be learned from
`pg_settings`.`unit`.
For convenience, settings can be given with a unit specified explicitly,
for example `'120 ms'` for a time value, and they will be
converted to whatever the parameter's actual unit is.  Note that the
value must be written as a string (with quotes) to use this feature.
The unit name is case-sensitive, and there can be whitespace between
the numeric value and the unit.

Valid memory units are `B` (bytes),
`kB` (kilobytes),
`MB` (megabytes), `GB`
(gigabytes), and `TB` (terabytes).
The multiplier for memory units is 1024, not 1000.
- Valid time units are
`us` (microseconds),
`ms` (milliseconds),
`s` (seconds), `min` (minutes),
`h` (hours), and `d` (days).

If a fractional value is specified with a unit, it will be rounded
to a multiple of the next smaller unit if there is one.
For example, `30.1 GB` will be converted
to `30822 MB` not `32319628902 B`.
If the parameter is of integer type, a final rounding to integer
occurs after any unit conversion.

*Enumerated:*
Enumerated-type parameters are written in the same way as string
parameters, but are restricted to have one of a limited set of
values.  The values allowable for such a parameter can be found from
`pg_settings`.`enumvals`.
Enum parameter values are case-insensitive.

### Parameter Interaction via the Configuration File

The most fundamental way to set these parameters is to edit the file
`postgresql.conf`,
which is normally kept in the data directory.  A default copy is
installed when the database cluster directory is initialized.
An example of what this file might look like is:

```

### Parameter Interaction via the Shell

In addition to setting global defaults or attaching
overrides at the database or role level, you can pass settings to
PostgreSQL via shell facilities.
Both the server and libpq client library
accept parameter values via the shell.

- During server startup, parameter settings can be
passed to the `postgres` command via the
`-c` command-line parameter.  For example,

```
postgres -c log_connections=yes -c log_destination='syslog'
```

Settings provided in this way override those set via
`postgresql.conf` or `ALTER SYSTEM`,
so they cannot be changed globally without restarting the server.
- When starting a client session via libpq,
parameter settings can be
specified using the `PGOPTIONS` environment variable.
Settings established in this way constitute defaults for the life
of the session, but do not affect other sessions.
For historical reasons, the format of `PGOPTIONS` is
similar to that used when launching the `postgres`
command; specifically, the `-c` flag must be specified.
For example,

```
env PGOPTIONS="-c geqo=off -c statement_timeout=5min" psql
```

Other clients and libraries might provide their own mechanisms,
via the shell or otherwise, that allow the user to alter session
settings without direct use of SQL commands.
