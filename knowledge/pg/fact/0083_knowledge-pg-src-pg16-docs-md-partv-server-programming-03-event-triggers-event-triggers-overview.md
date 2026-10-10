# Overview; Event Trigger Firing Matrix; Writing Event Trigger Functions in C; Event Trigger Interface; Examples

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/03_event_triggers.md`
- Source Title: `Event Triggers`
- Source Heading Path: `Event Triggers > Overview; Event Trigger Firing Matrix; Writing Event Trigger Functions in C; Event Trigger Interface; Examples`
- Source Line Ranges: `96-214, 215-289`
- Chunk ID: `pg16_fact_0083_31da396673`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ccfeafe8def9acd011e6b6035ed553c4a9494fcb67943655fa111006f6558331`

## Retrieval Guidance

- Use When: Implement or understand event triggers for DDL-related behavior.
- Retrieval Keywords: event trigger, ddl_command_start, ddl_command_end, sql_drop, EventTriggerData, pg_event_trigger
- Follow-up Guidance: Check system catalog and event trigger function records for object metadata.
- Classification Note: The chapter is reference material for event trigger events, APIs, firing points, and examples.

## Official Source Content

## Event Trigger Firing Matrix

[event-trigger-by-command-tag](#event-trigger-by-command-tag) lists all commands
for which event triggers are supported.

| Command Tag | `ddl_command_start` | `ddl_command_end` | `sql_drop` | `table_rewrite` | Notes |
| --- | --- | --- | --- | --- | --- |
| `ALTER AGGREGATE` | `X` | `X` | `-` | `-` |  |
| `ALTER COLLATION` | `X` | `X` | `-` | `-` |  |
| `ALTER CONVERSION` | `X` | `X` | `-` | `-` |  |
| `ALTER DOMAIN` | `X` | `X` | `-` | `-` |  |
| `ALTER DEFAULT PRIVILEGES` | `X` | `X` | `-` | `-` |  |
| `ALTER EXTENSION` | `X` | `X` | `-` | `-` |  |
| `ALTER FOREIGN DATA WRAPPER` | `X` | `X` | `-` | `-` |  |
| `ALTER FOREIGN TABLE` | `X` | `X` | `X` | `-` |  |
| `ALTER FUNCTION` | `X` | `X` | `-` | `-` |  |
| `ALTER LANGUAGE` | `X` | `X` | `-` | `-` |  |
| `ALTER LARGE OBJECT` | `X` | `X` | `-` | `-` |  |
| `ALTER MATERIALIZED VIEW` | `X` | `X` | `-` | `X` |  |
| `ALTER OPERATOR` | `X` | `X` | `-` | `-` |  |
| `ALTER OPERATOR CLASS` | `X` | `X` | `-` | `-` |  |
| `ALTER OPERATOR FAMILY` | `X` | `X` | `-` | `-` |  |
| `ALTER POLICY` | `X` | `X` | `-` | `-` |  |
| `ALTER PROCEDURE` | `X` | `X` | `-` | `-` |  |
| `ALTER PUBLICATION` | `X` | `X` | `-` | `-` |  |
| `ALTER ROUTINE` | `X` | `X` | `-` | `-` |  |
| `ALTER SCHEMA` | `X` | `X` | `-` | `-` |  |
| `ALTER SEQUENCE` | `X` | `X` | `-` | `-` |  |
| `ALTER SERVER` | `X` | `X` | `-` | `-` |  |
| `ALTER STATISTICS` | `X` | `X` | `-` | `-` |  |
| `ALTER SUBSCRIPTION` | `X` | `X` | `-` | `-` |  |
| `ALTER TABLE` | `X` | `X` | `X` | `X` |  |
| `ALTER TEXT SEARCH CONFIGURATION` | `X` | `X` | `-` | `-` |  |
| `ALTER TEXT SEARCH DICTIONARY` | `X` | `X` | `-` | `-` |  |
| `ALTER TEXT SEARCH PARSER` | `X` | `X` | `-` | `-` |  |
| `ALTER TEXT SEARCH TEMPLATE` | `X` | `X` | `-` | `-` |  |
| `ALTER TRIGGER` | `X` | `X` | `-` | `-` |  |
| `ALTER TYPE` | `X` | `X` | `-` | `X` |  |
| `ALTER USER MAPPING` | `X` | `X` | `-` | `-` |  |
| `ALTER VIEW` | `X` | `X` | `-` | `-` |  |
| `COMMENT` | `X` | `X` | `-` | `-` | Only for local objects |
| `CREATE ACCESS METHOD` | `X` | `X` | `-` | `-` |  |
| `CREATE AGGREGATE` | `X` | `X` | `-` | `-` |  |
| `CREATE CAST` | `X` | `X` | `-` | `-` |  |
| `CREATE COLLATION` | `X` | `X` | `-` | `-` |  |
| `CREATE CONVERSION` | `X` | `X` | `-` | `-` |  |
| `CREATE DOMAIN` | `X` | `X` | `-` | `-` |  |
| `CREATE EXTENSION` | `X` | `X` | `-` | `-` |  |
| `CREATE FOREIGN DATA WRAPPER` | `X` | `X` | `-` | `-` |  |
| `CREATE FOREIGN TABLE` | `X` | `X` | `-` | `-` |  |
| `CREATE FUNCTION` | `X` | `X` | `-` | `-` |  |
| `CREATE INDEX` | `X` | `X` | `-` | `-` |  |
| `CREATE LANGUAGE` | `X` | `X` | `-` | `-` |  |
| `CREATE MATERIALIZED VIEW` | `X` | `X` | `-` | `-` |  |
| `CREATE OPERATOR` | `X` | `X` | `-` | `-` |  |
| `CREATE OPERATOR CLASS` | `X` | `X` | `-` | `-` |  |
| `CREATE OPERATOR FAMILY` | `X` | `X` | `-` | `-` |  |
| `CREATE POLICY` | `X` | `X` | `-` | `-` |  |
| `CREATE PROCEDURE` | `X` | `X` | `-` | `-` |  |
| `CREATE PUBLICATION` | `X` | `X` | `-` | `-` |  |
| `CREATE RULE` | `X` | `X` | `-` | `-` |  |
| `CREATE SCHEMA` | `X` | `X` | `-` | `-` |  |
| `CREATE SEQUENCE` | `X` | `X` | `-` | `-` |  |
| `CREATE SERVER` | `X` | `X` | `-` | `-` |  |
| `CREATE STATISTICS` | `X` | `X` | `-` | `-` |  |
| `CREATE SUBSCRIPTION` | `X` | `X` | `-` | `-` |  |
| `CREATE TABLE` | `X` | `X` | `-` | `-` |  |
| `CREATE TABLE AS` | `X` | `X` | `-` | `-` |  |
| `CREATE TEXT SEARCH CONFIGURATION` | `X` | `X` | `-` | `-` |  |
| `CREATE TEXT SEARCH DICTIONARY` | `X` | `X` | `-` | `-` |  |
| `CREATE TEXT SEARCH PARSER` | `X` | `X` | `-` | `-` |  |
| `CREATE TEXT SEARCH TEMPLATE` | `X` | `X` | `-` | `-` |  |
| `CREATE TRIGGER` | `X` | `X` | `-` | `-` |  |
| `CREATE TYPE` | `X` | `X` | `-` | `-` |  |
| `CREATE USER MAPPING` | `X` | `X` | `-` | `-` |  |
| `CREATE VIEW` | `X` | `X` | `-` | `-` |  |
| `DROP ACCESS METHOD` | `X` | `X` | `X` | `-` |  |
| `DROP AGGREGATE` | `X` | `X` | `X` | `-` |  |
| `DROP CAST` | `X` | `X` | `X` | `-` |  |
| `DROP COLLATION` | `X` | `X` | `X` | `-` |  |
| `DROP CONVERSION` | `X` | `X` | `X` | `-` |  |
| `DROP DOMAIN` | `X` | `X` | `X` | `-` |  |
| `DROP EXTENSION` | `X` | `X` | `X` | `-` |  |
| `DROP FOREIGN DATA WRAPPER` | `X` | `X` | `X` | `-` |  |
| `DROP FOREIGN TABLE` | `X` | `X` | `X` | `-` |  |
| `DROP FUNCTION` | `X` | `X` | `X` | `-` |  |
| `DROP INDEX` | `X` | `X` | `X` | `-` |  |
| `DROP LANGUAGE` | `X` | `X` | `X` | `-` |  |
| `DROP MATERIALIZED VIEW` | `X` | `X` | `X` | `-` |  |
| `DROP OPERATOR` | `X` | `X` | `X` | `-` |  |
| `DROP OPERATOR CLASS` | `X` | `X` | `X` | `-` |  |
| `DROP OPERATOR FAMILY` | `X` | `X` | `X` | `-` |  |
| `DROP OWNED` | `X` | `X` | `X` | `-` |  |
| `DROP POLICY` | `X` | `X` | `X` | `-` |  |
| `DROP PROCEDURE` | `X` | `X` | `X` | `-` |  |
| `DROP PUBLICATION` | `X` | `X` | `X` | `-` |  |
| `DROP ROUTINE` | `X` | `X` | `X` | `-` |  |
| `DROP RULE` | `X` | `X` | `X` | `-` |  |
| `DROP SCHEMA` | `X` | `X` | `X` | `-` |  |
| `DROP SEQUENCE` | `X` | `X` | `X` | `-` |  |
| `DROP SERVER` | `X` | `X` | `X` | `-` |  |
| `DROP STATISTICS` | `X` | `X` | `X` | `-` |  |
| `DROP SUBSCRIPTION` | `X` | `X` | `X` | `-` |  |
| `DROP TABLE` | `X` | `X` | `X` | `-` |  |
| `DROP TEXT SEARCH CONFIGURATION` | `X` | `X` | `X` | `-` |  |
| `DROP TEXT SEARCH DICTIONARY` | `X` | `X` | `X` | `-` |  |
| `DROP TEXT SEARCH PARSER` | `X` | `X` | `X` | `-` |  |
| `DROP TEXT SEARCH TEMPLATE` | `X` | `X` | `X` | `-` |  |
| `DROP TRIGGER` | `X` | `X` | `X` | `-` |  |
| `DROP TYPE` | `X` | `X` | `X` | `-` |  |
| `DROP USER MAPPING` | `X` | `X` | `X` | `-` |  |
| `DROP VIEW` | `X` | `X` | `X` | `-` |  |
| `GRANT` | `X` | `X` | `-` | `-` | Only for local objects |
| `IMPORT FOREIGN SCHEMA` | `X` | `X` | `-` | `-` |  |
| `REFRESH MATERIALIZED VIEW` | `X` | `X` | `-` | `-` |  |
| `REVOKE` | `X` | `X` | `-` | `-` | Only for local objects |
| `SECURITY LABEL` | `X` | `X` | `-` | `-` | Only for local objects |
| `SELECT INTO` | `X` | `X` | `-` | `-` |  |

## Writing Event Trigger Functions in C

This section describes the low-level details of the interface to an
event trigger function. This information is only needed when writing
event trigger functions in C. If you are using a higher-level language
then these details are handled for you. In most cases you should
consider using a procedural language before writing your event triggers
in C. The documentation of each procedural language explains how to
write an event trigger in that language.

Event trigger functions must use the "version 1" function
manager interface.

When a function is called by the event trigger manager, it is not passed
any normal arguments, but it is passed a "context" pointer
pointing to a `EventTriggerData` structure. C functions can
check whether they were called from the event trigger manager or not by
executing the macro:

```
CALLED_AS_EVENT_TRIGGER(fcinfo)
```

which expands to:

```
((fcinfo)->context != NULL && IsA((fcinfo)->context, EventTriggerData))
```

If this returns true, then it is safe to cast
`fcinfo->context` to type `EventTriggerData
*` and make use of the pointed-to
`EventTriggerData` structure.  The function must
*not* alter the `EventTriggerData`
structure or any of the data it points to.

`struct EventTriggerData` is defined in
`commands/event_trigger.h`:

```
typedef struct EventTriggerData
{
NodeTag     type;
const char *event;      /* event name */
Node       *parsetree;  /* parse tree */
CommandTag  tag;        /* command tag */
} EventTriggerData;
```

where the members are defined as follows:

**`type`**
: Always `T_EventTriggerData`.

**`event`**
: Describes the event for which the function is called, one of
`"ddl_command_start"`, `"ddl_command_end"`,
`"sql_drop"`, `"table_rewrite"`.
See [event-trigger-definition](#event-trigger-definition) for the meaning of these
events.

**`parsetree`**
: A pointer to the parse tree of the command.  Check the PostgreSQL
source code for details.  The parse tree structure is subject to change
without notice.

**`tag`**
: The command tag associated with the event for which the event trigger
is run, for example `"CREATE FUNCTION"`.

An event trigger function must return a `NULL` pointer
(*not* an SQL null value, that is, do not
set
isNull true).
