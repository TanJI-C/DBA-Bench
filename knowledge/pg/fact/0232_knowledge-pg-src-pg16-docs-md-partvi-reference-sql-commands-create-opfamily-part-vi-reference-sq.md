# CREATE OPERATOR FAMILY

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_opfamily.md`
- Source Title: `create opfamily`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE OPERATOR FAMILY`
- Source Line Ranges: `1-59`
- Chunk ID: `pg16_fact_0232_93035bc9bd`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `f36c8cb40436794d9a5575134651e8a0c0510c5b94eac7acf0e8bd31366a7e89`

## Retrieval Guidance

- Use When: Use for operator family creation syntax.
- Retrieval Keywords: CREATE OPERATOR FAMILY, opfamily, index access method
- Follow-up Guidance: No section split needed.
- Classification Note: Operator family object creation reference.

## Official Source Content

CREATE OPERATOR FAMILY
7
SQL - Language Statements

CREATE OPERATOR FAMILY
define a new operator family

```
CREATE OPERATOR FAMILY `name` USING `index_method`
```

## Description

`CREATE OPERATOR FAMILY` creates a new operator family.
An operator family defines a collection of related operator classes,
and perhaps some additional operators and support functions that are
compatible with these operator classes but not essential for the
functioning of any individual index.  (Operators and functions that
are essential to indexes should be grouped within the relevant operator
class, rather than being "loose" in the operator family.
Typically, single-data-type operators are bound to operator classes,
while cross-data-type operators can be loose in an operator family
containing operator classes for both data types.)

The new operator family is initially empty.  It should be populated
by issuing subsequent `CREATE OPERATOR CLASS` commands
to add contained operator classes, and optionally
`ALTER OPERATOR FAMILY` commands to add "loose"
operators and their corresponding support functions.

If a schema name is given then the operator family is created in the
specified schema.  Otherwise it is created in the current schema.
Two operator families in the same schema can have the same name only if they
are for different index methods.

The user who defines an operator family becomes its owner.  Presently,
the creating user must be a superuser.  (This restriction is made because
an erroneous operator family definition could confuse or even crash the
server.)

Refer to [xindex](#xindex) for further information.

## Parameters

**`name`**
: The name of the operator family to be created.  The name can be
schema-qualified.

**`index_method`**
: The name of the index method this operator family is for.

## Compatibility

`CREATE OPERATOR FAMILY` is a
PostgreSQL extension.  There is no
`CREATE OPERATOR FAMILY` statement in the SQL
standard.

## See Also
