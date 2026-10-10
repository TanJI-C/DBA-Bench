# DROP EVENT TRIGGER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_event_trigger.md`
- Source Title: `drop event trigger`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP EVENT TRIGGER`
- Source Line Ranges: `1-49`
- Chunk ID: `pg16_fact_0266_a24cf66f6b`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `fceae6c730de6d809e77a3efcc218dd06acd5a5d129b50dc78ba7fdfef62645d`

## Retrieval Guidance

- Use When: Use for event trigger drop syntax.
- Retrieval Keywords: DROP EVENT TRIGGER, event trigger, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Event trigger object removal syntax reference.

## Official Source Content

DROP EVENT TRIGGER
7
SQL - Language Statements

DROP EVENT TRIGGER
remove an event trigger

```
DROP EVENT TRIGGER [ IF EXISTS ] `name` [ CASCADE | RESTRICT ]
```

## Description

`DROP EVENT TRIGGER` removes an existing event trigger.
To execute this command, the current user must be the owner of the event
trigger.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the event trigger does not exist. A notice
is issued in this case.

**`name`**
: The name of the event trigger to remove.

**`CASCADE`**
: Automatically drop objects that depend on the trigger,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the trigger if any objects depend on it.  This is
the default.

## Examples

Destroy the trigger `snitch`:

```
DROP EVENT TRIGGER snitch;
```

## Compatibility

There is no `DROP EVENT TRIGGER` statement in the
SQL standard.

## See Also
