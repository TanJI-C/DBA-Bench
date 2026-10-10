# RESET

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/reset.md`
- Source Title: `reset`
- Source Heading Path: `Part VI Reference > SQL Commands > RESET`
- Source Line Ranges: `1-61`
- Chunk ID: `pg16_configuration_0223_0883dbe8c6`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `4a13c6fd40d3dda09e322ccdd45e061a8bb4276642b0d0bd4a53d963c2ec767d`

## Retrieval Guidance

- Use When: Use when removing session-level runtime parameter overrides.
- Retrieval Keywords: RESET, RESET ALL, configuration_parameter, runtime parameter, SET DEFAULT
- Follow-up Guidance: Verify effective value with SHOW/current_setting and understand transaction rollback behavior.
- Classification Note: Restores run-time configuration parameters to default values and documents reset source/transaction semantics.

## Official Source Content

RESET
7
SQL - Language Statements

RESET
restore the value of a run-time parameter to the default value

```
RESET `configuration_parameter`
RESET ALL
```

## Description

`RESET` restores run-time parameters to their
default values.  `RESET` is an alternative
spelling for

```
SET `configuration_parameter` TO DEFAULT
```

Refer to [sql-set](#sql-set) for
details.

The default value is defined as the value that the parameter would
have had, if no `SET` had ever been issued for it in the
current session.  The actual source of this value might be a
compiled-in default, the configuration file, command-line options,
or per-database or per-user default settings.  This is subtly different
from defining it as "the value that the parameter had at session
start", because if the value came from the configuration file, it
will be reset to whatever is specified by the configuration file now.
See [runtime-config](#runtime-config) for details.

The transactional behavior of `RESET` is the same as
`SET`: its effects will be undone by transaction rollback.

## Parameters

**`configuration_parameter`**
: Name of a settable run-time parameter.  Available parameters are
documented in [runtime-config](#runtime-config) and on the
[sql-set](#sql-set) reference page.

**`ALL`**
: Resets all settable run-time parameters to default values.

## Examples

Set the `timezone` configuration variable to its default value:

```
RESET timezone;
```

## Compatibility

`RESET` is a PostgreSQL extension.

## See Also
