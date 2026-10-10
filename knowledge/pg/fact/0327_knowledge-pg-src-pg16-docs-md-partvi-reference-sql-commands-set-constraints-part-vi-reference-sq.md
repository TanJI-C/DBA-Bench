# SET CONSTRAINTS

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/set_constraints.md`
- Source Title: `set constraints`
- Source Heading Path: `Part VI Reference > SQL Commands > SET CONSTRAINTS`
- Source Line Ranges: `1-83`
- Chunk ID: `pg16_fact_0327_4093b9fd44`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `6a61cd67e754c963bfef5d4a2590d2868c582b8fd9100c3a107bc3098b27d21e`

## Retrieval Guidance

- Use When: Use for controlling deferrable constraint checking within transactions.
- Retrieval Keywords: SET CONSTRAINTS, deferred constraint, immediate constraint, deferrable
- Follow-up Guidance: No section split needed.
- Classification Note: Constraint-checking timing syntax reference for deferrable constraints; ordinary transaction semantics, not server parameter configuration.

## Official Source Content

SET CONSTRAINTS
7
SQL - Language Statements

SET CONSTRAINTS
set constraint check timing for the current transaction

```
SET CONSTRAINTS { ALL | `name` [, ...] } { DEFERRED | IMMEDIATE }
```

## Description

`SET CONSTRAINTS` sets the behavior of constraint
checking within the current transaction. `IMMEDIATE`
constraints are checked at the end of each
statement. `DEFERRED` constraints are not checked until
transaction commit.  Each constraint has its own
`IMMEDIATE` or `DEFERRED` mode.

Upon creation, a constraint is given one of three
characteristics: `DEFERRABLE INITIALLY DEFERRED`,
`DEFERRABLE INITIALLY IMMEDIATE`, or
`NOT DEFERRABLE`. The third
class is always `IMMEDIATE` and is not affected by the
`SET CONSTRAINTS` command.  The first two classes start
every transaction in the indicated mode, but their behavior can be changed
within a transaction by `SET CONSTRAINTS`.

`SET CONSTRAINTS` with a list of constraint names changes
the mode of just those constraints (which must all be deferrable).  Each
constraint name can be schema-qualified.  The
current schema search path is used to find the first matching name if
no schema name is specified.  `SET CONSTRAINTS ALL`
changes the mode of all deferrable constraints.

When `SET CONSTRAINTS` changes the mode of a constraint
from `DEFERRED`
to `IMMEDIATE`, the new mode takes effect
retroactively: any outstanding data modifications that would have
been checked at the end of the transaction are instead checked during the
execution of the `SET CONSTRAINTS` command.
If any such constraint is violated, the `SET CONSTRAINTS`
fails (and does not change the constraint mode).  Thus, `SET
CONSTRAINTS` can be used to force checking of constraints to
occur at a specific point in a transaction.

Currently, only `UNIQUE`, `PRIMARY KEY`,
`REFERENCES` (foreign key), and `EXCLUDE`
constraints are affected by this setting.
`NOT NULL` and `CHECK` constraints are
always checked immediately when a row is inserted or modified
(*not* at the end of the statement).
Uniqueness and exclusion constraints that have not been declared
`DEFERRABLE` are also checked immediately.

The firing of triggers that are declared as "constraint triggers"
is also controlled by this setting — they fire at the same time
that the associated constraint should be checked.

## Notes

Because PostgreSQL does not require constraint
names to be unique within a schema (but only per-table), it is possible
that there is more than one match for a specified constraint name.
In this case `SET CONSTRAINTS` will act on all matches.
For a non-schema-qualified name, once a match or matches have been found in
some schema in the search path, schemas appearing later in the path are not
searched.

This command only alters the behavior of constraints within the
current transaction.  Issuing this outside of a transaction block
emits a warning and otherwise has no effect.

## Compatibility

This command complies with the behavior defined in the SQL
standard, except for the limitation that, in
PostgreSQL, it does not apply to
`NOT NULL` and `CHECK` constraints.
Also, PostgreSQL checks non-deferrable
uniqueness constraints immediately, not at end of statement as the
standard would suggest.
