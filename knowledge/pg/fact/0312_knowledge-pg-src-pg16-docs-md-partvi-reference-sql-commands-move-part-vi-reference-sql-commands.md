# MOVE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/move.md`
- Source Title: `move`
- Source Heading Path: `Part VI Reference > SQL Commands > MOVE`
- Source Line Ranges: `1-79`
- Chunk ID: `pg16_fact_0312_1abe3f6541`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `893910fc4664bf97eab94e4ed037a873a17f7609d04724d046452538af17ab04`

## Retrieval Guidance

- Use When: Use for cursor movement syntax.
- Retrieval Keywords: MOVE, cursor move, FORWARD, BACKWARD
- Follow-up Guidance: No section split needed.
- Classification Note: Cursor positioning syntax reference.

## Official Source Content

MOVE
7
SQL - Language Statements

MOVE
position a cursor

```
MOVE [ `direction` ] [ FROM | IN ] `cursor_name`

where `direction` can be one of:

NEXT
PRIOR
FIRST
LAST
ABSOLUTE `count`
RELATIVE `count`
`count`
ALL
FORWARD
FORWARD `count`
FORWARD ALL
BACKWARD
BACKWARD `count`
BACKWARD ALL
```

## Description

`MOVE` repositions a cursor without retrieving any data.
`MOVE` works exactly like the `FETCH`
command, except it only positions the cursor and does not return rows.

The parameters for the `MOVE` command are identical to
those of the `FETCH` command; refer to
[sql-fetch](#sql-fetch)
for details on syntax and usage.

## Outputs

On successful completion, a `MOVE` command returns a command
tag of the form

```
MOVE `count`
```

The `count` is the number
of rows that a `FETCH` command with the same parameters
would have returned (possibly zero).

## Examples

```
BEGIN WORK;
DECLARE liahona CURSOR FOR SELECT * FROM films;

-- Skip the first 5 rows:
MOVE FORWARD 5 IN liahona;
MOVE 5

-- Fetch the 6th row from the cursor liahona:
FETCH 1 FROM liahona;
code  | title  | did | date_prod  |  kind  |  len
-------+--------+-----+------------+--------+-------
P_303 | 48 Hrs | 103 | 1982-10-22 | Action | 01:37
(1 row)

-- Close the cursor liahona and end the transaction:
CLOSE liahona;
COMMIT WORK;
```

## Compatibility

There is no `MOVE` statement in the SQL standard.

## See Also
