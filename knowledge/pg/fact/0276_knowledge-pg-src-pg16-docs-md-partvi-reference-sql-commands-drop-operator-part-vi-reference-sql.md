# DROP OPERATOR

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_operator.md`
- Source Title: `drop operator`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP OPERATOR`
- Source Line Ranges: `1-68`
- Chunk ID: `pg16_fact_0276_64e403d28a`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `1ee9095e6035984940723fb4b77cb0460af3499e12dccc04afa9fc31bf4c440f`

## Retrieval Guidance

- Use When: Use for operator drop syntax.
- Retrieval Keywords: DROP OPERATOR, operator signature, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Operator removal syntax reference.

## Official Source Content

DROP OPERATOR
7
SQL - Language Statements

DROP OPERATOR
remove an operator

```
DROP OPERATOR [ IF EXISTS ] `name` ( { `left_type` | NONE } , `right_type` ) [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP OPERATOR` drops an existing operator from
the database system.  To execute this command you must be the owner
of the operator.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the operator does not exist. A notice is issued
in this case.

**`name`**
: The name (optionally schema-qualified) of an existing operator.

**`left_type`**
: The data type of the operator's left operand; write
`NONE` if the operator has no left operand.

**`right_type`**
: The data type of the operator's right operand.

**`CASCADE`**
: Automatically drop objects that depend on the operator (such as views
using it), and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the operator if any objects depend on it.  This
is the default.

## Examples

Remove the power operator `a^b` for type `integer`:

```
DROP OPERATOR ^ (integer, integer);
```

Remove the bitwise-complement prefix operator
`~b` for type `bit`:

```
DROP OPERATOR ~ (none, bit);
```

Remove multiple operators in one command:

```
DROP OPERATOR ~ (none, bit), ^ (integer, integer);
```

## Compatibility

There is no `DROP OPERATOR` statement in the SQL standard.

## See Also
