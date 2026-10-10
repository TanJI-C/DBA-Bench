# CLOSE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/close.md`
- Source Title: `close`
- Source Heading Path: `Part VI Reference > SQL Commands > CLOSE`
- Source Line Ranges: `1-64`
- Chunk ID: `pg16_fact_0210_7e3ed901e5`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `64bbf86d300823adcd68338aee8d97df5b06fbf476b5c9bdad833d23e4cdbe4d`

## Retrieval Guidance

- Use When: Use for cursor close syntax and behavior.
- Retrieval Keywords: CLOSE, cursor close, portal, cursor lifecycle
- Follow-up Guidance: No section split needed.
- Classification Note: Cursor lifecycle syntax reference for closing a cursor.

## Official Source Content

CLOSE
7
SQL - Language Statements

CLOSE
close a cursor

```
CLOSE { `name` | ALL }
```

## Description

`CLOSE` frees the resources associated with an open cursor.
After the cursor is closed, no subsequent operations
are allowed on it. A cursor should be closed when it is
no longer needed.

Every non-holdable open cursor is implicitly closed when a
transaction is terminated by `COMMIT` or
`ROLLBACK`.  A holdable cursor is implicitly
closed if the transaction that created it aborts via
`ROLLBACK`.  If the creating transaction
successfully commits, the holdable cursor remains open until an
explicit `CLOSE` is executed, or the client
disconnects.

## Parameters

**`name`**
: The name of an open cursor to close.

**`ALL`**
: Close all open cursors.

## Notes

PostgreSQL does not have an explicit
`OPEN` cursor statement; a cursor is considered
open when it is declared.  Use the
[`DECLARE`](#sql-declare)
statement to declare a cursor.

You can see all available cursors by querying the [`pg_cursors`](#view-pg-cursors) system view.

If a cursor is closed after a savepoint which is later rolled back,
the `CLOSE` is not rolled back; that is, the cursor
remains closed.

## Examples

Close the cursor `liahona`:

```
CLOSE liahona;
```

## Compatibility

`CLOSE` is fully conforming with the SQL
standard. `CLOSE ALL` is a PostgreSQL
extension.

## See Also
