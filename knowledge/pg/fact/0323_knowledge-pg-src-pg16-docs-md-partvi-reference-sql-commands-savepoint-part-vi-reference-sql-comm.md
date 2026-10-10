# SAVEPOINT

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/savepoint.md`
- Source Title: `savepoint`
- Source Heading Path: `Part VI Reference > SQL Commands > SAVEPOINT`
- Source Line Ranges: `1-104`
- Chunk ID: `pg16_fact_0323_5ca4e3b9ea`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `c43f612ee29a306c95349038a8731f1da812fc426ca203cd8f2c7284c6fad6a1`

## Retrieval Guidance

- Use When: Use for savepoint syntax and behavior.
- Retrieval Keywords: SAVEPOINT, subtransaction, transaction savepoint
- Follow-up Guidance: No section split needed.
- Classification Note: Savepoint creation syntax reference.

## Official Source Content

SAVEPOINT
7
SQL - Language Statements

SAVEPOINT
define a new savepoint within the current transaction

```
SAVEPOINT `savepoint_name`
```

## Description

`SAVEPOINT` establishes a new savepoint within
the current transaction.

A savepoint is a special mark inside a transaction that allows all commands
that are executed after it was established to be rolled back, restoring
the transaction state to what it was at the time of the savepoint.

## Parameters

**`savepoint_name`**
: The name to give to the new savepoint.  If savepoints with the
same name already exist, they will be inaccessible until newer
identically-named savepoints are released.

## Notes

Use [`ROLLBACK TO`](#sql-rollback-to) to
rollback to a savepoint.  Use [`RELEASE SAVEPOINT`](#sql-release-savepoint)
to destroy a savepoint, keeping
the effects of commands executed after it was established.

Savepoints can only be established when inside a transaction block.
There can be multiple savepoints defined within a transaction.

## Examples

To establish a savepoint and later undo the effects of all commands executed
after it was established:

```
BEGIN;
INSERT INTO table1 VALUES (1);
SAVEPOINT my_savepoint;
INSERT INTO table1 VALUES (2);
ROLLBACK TO SAVEPOINT my_savepoint;
INSERT INTO table1 VALUES (3);
COMMIT;
```

The above transaction will insert the values 1 and 3, but not 2.

To establish and later destroy a savepoint:

```
BEGIN;
INSERT INTO table1 VALUES (3);
SAVEPOINT my_savepoint;
INSERT INTO table1 VALUES (4);
RELEASE SAVEPOINT my_savepoint;
COMMIT;
```

The above transaction will insert both 3 and 4.

To use a single savepoint name:

```
BEGIN;
INSERT INTO table1 VALUES (1);
SAVEPOINT my_savepoint;
INSERT INTO table1 VALUES (2);
SAVEPOINT my_savepoint;
INSERT INTO table1 VALUES (3);

-- rollback to the second savepoint
ROLLBACK TO SAVEPOINT my_savepoint;
SELECT * FROM table1;               -- shows rows 1 and 2

-- release the second savepoint
RELEASE SAVEPOINT my_savepoint;

-- rollback to the first savepoint
ROLLBACK TO SAVEPOINT my_savepoint;
SELECT * FROM table1;               -- shows only row 1
COMMIT;
```

The above transaction shows row 3 being rolled back first, then row 2.

## Compatibility

SQL requires a savepoint to be destroyed automatically when another
savepoint with the same name is established.  In
PostgreSQL, the old savepoint is kept, though only the more
recent one will be used when rolling back or releasing.  (Releasing the
newer savepoint with `RELEASE SAVEPOINT` will cause the older one
to again become accessible to `ROLLBACK TO SAVEPOINT` and
`RELEASE SAVEPOINT`.) Otherwise, `SAVEPOINT` is
fully SQL conforming.

## See Also
