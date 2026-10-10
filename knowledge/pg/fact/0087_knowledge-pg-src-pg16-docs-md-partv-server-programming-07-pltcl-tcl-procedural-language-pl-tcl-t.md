# Functions and Arguments; Data Values; Global Data; Database Access; Trigger Functions; Event Trigger Functions; Modules and Unknown Command Handling

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/07_pltcl_-_tcl_procedural_language.md`
- Source Title: `PL/Tcl — Tcl Procedural Language`
- Source Heading Path: `PL/Tcl - Tcl Procedural Language > Functions and Arguments; Data Values; Global Data; Database Access; Trigger Functions; Event Trigger Functions; Modules and Unknown Command Handling`
- Source Line Ranges: `52-58, 185-214`
- Chunk ID: `pg16_fact_0087_dd62d0e6ce`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `128e5569e575aea1b96d45d7fa26783ba8364e1ac1df87c65e218b4130901955`

## Retrieval Guidance

- Use When: Write or understand PL/Tcl functions and database access.
- Retrieval Keywords: PL/Tcl, pltcl, SPI in PL/Tcl, Tcl trigger, return_next, quote_ident, spi_exec
- Follow-up Guidance: Use configuration and error-handling records for startup procedures or trapped failures.
- Classification Note: These sections document PL/Tcl function syntax, type mapping, shared data, SPI access, trigger/event-trigger behavior, and module loading as language reference.

## Official Source Content

## PL/Tcl Functions and Arguments

To create a function in the PL/Tcl language, use
the standard [sql-createfunction](#sql-createfunction) syntax:

```
CREATE FUNCTION `funcname` (`argument-types`) RETURNS `return-type` AS $$

## Event Trigger Functions in PL/Tcl

Event trigger functions can be written in PL/Tcl.
PostgreSQL requires that a function that is
to be called as an event trigger must be declared as a function with no
arguments and a return type of `event_trigger`.

The information from the trigger manager is passed to the function body
in the following variables:

**`$TG_event`**
: The name of the event the trigger is fired for.

**`$TG_tag`**
: The command tag for which the trigger is fired.

The return value of the trigger function is ignored.

Here's a little example event trigger function that simply raises
a `NOTICE` message each time a supported command is
executed:

```
CREATE OR REPLACE FUNCTION tclsnitch() RETURNS event_trigger AS $$
elog NOTICE "tclsnitch: $TG_event $TG_tag"
$$ LANGUAGE pltcl;

CREATE EVENT TRIGGER tcl_a_snitch ON ddl_command_start EXECUTE FUNCTION tclsnitch();
```
