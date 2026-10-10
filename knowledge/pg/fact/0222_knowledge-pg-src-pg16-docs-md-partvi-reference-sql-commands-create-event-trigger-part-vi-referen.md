# CREATE EVENT TRIGGER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_event_trigger.md`
- Source Title: `create event trigger`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE EVENT TRIGGER`
- Source Line Ranges: `1-89`
- Chunk ID: `pg16_fact_0222_9d8df390cf`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `311e7e457f16cb416853c46e6552a4c890b86553bb16a508c235946ddd4918ca`

## Retrieval Guidance

- Use When: Use for event trigger creation syntax.
- Retrieval Keywords: CREATE EVENT TRIGGER, DDL event, event trigger function, ddl_command_start
- Follow-up Guidance: No section split needed.
- Classification Note: Event trigger object creation reference.

## Official Source Content

CREATE EVENT TRIGGER
7
SQL - Language Statements

CREATE EVENT TRIGGER
define a new event trigger

```
CREATE EVENT TRIGGER `name`
ON `event`
[ WHEN `filter_variable` IN (`filter_value` [, ... ]) [ AND ... ] ]
EXECUTE { FUNCTION | PROCEDURE } `function_name`()
```

## Description

`CREATE EVENT TRIGGER` creates a new event trigger.
Whenever the designated event occurs and the `WHEN` condition
associated with the trigger, if any, is satisfied, the trigger function
will be executed.  For a general introduction to event triggers, see
[event-triggers](#event-triggers).  The user who creates an event trigger
becomes its owner.

## Parameters

**`name`**
: The name to give the new trigger.  This name must be unique within
the database.

**`event`**
: The name of the event that triggers a call to the given function.
See [event-trigger-definition](#event-trigger-definition) for more information
on event names.

**`filter_variable`**
: The name of a variable used to filter events.  This makes it possible
to restrict the firing of the trigger to a subset of the cases in which
it is supported.  Currently the only supported
`filter_variable`
is `TAG`.

**`filter_value`**
: A list of values for the
associated `filter_variable`
for which the trigger should fire.  For `TAG`, this means a
list of command tags (e.g., `'DROP FUNCTION'`).

**`function_name`**
: A user-supplied function that is declared as taking no argument and
returning type `event_trigger`.

In the syntax of `CREATE EVENT TRIGGER`, the keywords
`FUNCTION` and `PROCEDURE` are
equivalent, but the referenced function must in any case be a function,
not a procedure.  The use of the keyword `PROCEDURE`
here is historical and deprecated.

## Notes

Only superusers can create event triggers.

Event triggers are disabled in single-user mode (see [app-postgres](#app-postgres)).  If an erroneous event trigger disables the
database so much that you can't even drop the trigger, restart in
single-user mode and you'll be able to do that.

## Examples

Forbid the execution of any [DDL](#ddl) command:

```
CREATE OR REPLACE FUNCTION abort_any_command()
RETURNS event_trigger
LANGUAGE plpgsql
AS $$
BEGIN
RAISE EXCEPTION 'command % is disabled', tg_tag;
END;
$$;

CREATE EVENT TRIGGER abort_ddl ON ddl_command_start
EXECUTE FUNCTION abort_any_command();
```

## Compatibility

There is no `CREATE EVENT TRIGGER` statement in the
SQL standard.

## See Also
