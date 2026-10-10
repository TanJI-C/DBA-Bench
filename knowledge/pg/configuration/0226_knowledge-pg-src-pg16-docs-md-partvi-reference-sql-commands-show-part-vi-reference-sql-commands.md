# SHOW

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/show.md`
- Source Title: `show`
- Source Heading Path: `Part VI Reference > SQL Commands > SHOW`
- Source Line Ranges: `1-98`
- Chunk ID: `pg16_configuration_0226_2a0342f575`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `800a4d7bde7e192d5dfd2565e960857890b3b39b529df192689fd0ee6bd147d8`

## Retrieval Guidance

- Use When: Use when retrieving or verifying effective configuration parameter values.
- Retrieval Keywords: SHOW, SHOW ALL, runtime parameter, pg_settings, current_setting
- Follow-up Guidance: For source and context, query pg_settings or compare ALTER SYSTEM/postgresql.conf/session defaults.
- Classification Note: Displays current run-time configuration values and SHOW ALL output; it is configuration inspection rather than general SQL fact.

## Official Source Content

SHOW
7
SQL - Language Statements

SHOW
show the value of a run-time parameter

```
SHOW `name`
SHOW ALL
```

## Description

`SHOW` will display the current setting of
run-time parameters. These variables can be set using the
`SET` statement, by editing the
`postgresql.conf` configuration file, through
the `PGOPTIONS` environmental variable (when using
libpq or a libpq-based
application), or through command-line flags when starting the
`postgres` server.  See [runtime-config](#runtime-config) for details.

## Parameters

**`name`**
: The name of a run-time parameter.  Available parameters are
documented in [runtime-config](#runtime-config) and on the [sql-set](#sql-set) reference page.  In
addition, there are a few parameters that can be shown but not
set:

`SERVER_VERSION`

Shows the server's version number.

**`SERVER_ENCODING`**
: Shows the server-side character set encoding.  At present,
this parameter can be shown but not set, because the
encoding is determined at database creation time.

**`IS_SUPERUSER`**
: True if the current role has superuser privileges.

`ALL`

Show the values of all configuration parameters, with descriptions.

## Notes

The function `current_setting` produces
equivalent output; see [functions-admin-set](#functions-admin-set).
Also, the
[`pg_settings`](#view-pg-settings)
system view produces the same information.

## Examples

Show the current setting of the parameter `DateStyle`:

```
SHOW DateStyle;
DateStyle
-----------
ISO, MDY
(1 row)
```

Show the current setting of the parameter `geqo`:

```
SHOW geqo;
geqo
------
on
(1 row)
```

Show all settings:

```
SHOW ALL;
name         | setting |                description
-------------------------+---------+-------------------------------------------------
allow_system_table_mods | off     | Allows modifications of the structure of ...
.
.
.
xmloption               | content | Sets whether XML data in implicit parsing ...
zero_damaged_pages      | off     | Continues processing past damaged page headers.
(196 rows)
```

## Compatibility

The `SHOW` command is a
PostgreSQL extension.

## See Also
