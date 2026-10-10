# ALTER EVENT TRIGGER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_event_trigger.md`
- Source Title: `alter event trigger`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER EVENT TRIGGER`
- Source Line Ranges: `1-43`
- Chunk ID: `pg16_fact_0173_d2f6d50cf7`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `0a46c7f82edd55ecaa93ef2c39a2957c33541d009d3d006f91e007bd4305aef9`

## Retrieval Guidance

- Use When: Use for event trigger DDL syntax.
- Retrieval Keywords: ALTER EVENT TRIGGER, event trigger enable, event trigger disable, event trigger owner
- Follow-up Guidance: No section split needed.
- Classification Note: Object-reference DDL for event trigger state, owner, and name.

## Official Source Content

ALTER EVENT TRIGGER
7
SQL - Language Statements

ALTER EVENT TRIGGER
change the definition of an event trigger

```
ALTER EVENT TRIGGER `name` DISABLE
ALTER EVENT TRIGGER `name` ENABLE [ REPLICA | ALWAYS ]
ALTER EVENT TRIGGER `name` OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
ALTER EVENT TRIGGER `name` RENAME TO `new_name`
```

## Description

`ALTER EVENT TRIGGER` changes properties of an
existing event trigger.

You must be superuser to alter an event trigger.

## Parameters

**`name`**
: The name of an existing trigger to alter.

**`new_owner`**
: The user name of the new owner of the event trigger.

**`new_name`**
: The new name of the event trigger.

**`DISABLE`/`ENABLE [ REPLICA | ALWAYS ]`**
: These forms configure the firing of event triggers.  A disabled trigger
is still known to the system, but is not executed when its triggering
event occurs.  See also [guc-session-replication-role](#guc-session-replication-role).

## Compatibility

There is no `ALTER EVENT TRIGGER` statement in the
SQL standard.

## See Also
