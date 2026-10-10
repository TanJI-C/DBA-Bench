# ALTER OPERATOR

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_operator.md`
- Source Title: `alter operator`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER OPERATOR`
- Source Line Ranges: `1-77`
- Chunk ID: `pg16_fact_0184_309e57c765`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `bf18c56e3f9d9d385952a11945b19f6826ea4b9fd4e9cc5cfc53f9863361eab4`

## Retrieval Guidance

- Use When: Use for operator metadata syntax.
- Retrieval Keywords: ALTER OPERATOR, operator owner, operator schema, operator dependency
- Follow-up Guidance: No section split needed.
- Classification Note: Operator object DDL reference for owner, schema, and dependency changes.

## Official Source Content

ALTER OPERATOR
7
SQL - Language Statements

ALTER OPERATOR
change the definition of an operator

```
ALTER OPERATOR `name` ( { `left_type` | NONE } , `right_type` )
OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }

ALTER OPERATOR `name` ( { `left_type` | NONE } , `right_type` )
SET SCHEMA `new_schema`

ALTER OPERATOR `name` ( { `left_type` | NONE } , `right_type` )
SET ( {  RESTRICT = { `res_proc` | NONE }
| JOIN = { `join_proc` | NONE }
} [, ... ] )
```

## Description

`ALTER OPERATOR` changes the definition of
an operator.

You must own the operator to use `ALTER OPERATOR`.
To alter the owner, you must be able to `SET ROLE` to the
new owning role, and that role must have `CREATE`
privilege on the operator's schema.
(These restrictions enforce that altering the owner
doesn't do anything you couldn't do by dropping and recreating the operator.
However, a superuser can alter ownership of any operator anyway.)

## Parameters

**`name`**
: The name (optionally schema-qualified) of an existing operator.

**`left_type`**
: The data type of the operator's left operand; write
`NONE` if the operator has no left operand.

**`right_type`**
: The data type of the operator's right operand.

**`new_owner`**
: The new owner of the operator.

**`new_schema`**
: The new schema for the operator.

**`res_proc`**
: The restriction selectivity estimator function for this operator; write NONE to remove existing selectivity estimator.

**`join_proc`**
: The join selectivity estimator function for this operator; write NONE to remove existing selectivity estimator.

## Examples

Change the owner of a custom operator `a @@ b` for type `text`:

```
ALTER OPERATOR @@ (text, text) OWNER TO joe;
```

Change the restriction and join selectivity estimator functions of a custom operator `a && b` for type `int[]`:

```
ALTER OPERATOR && (_int4, _int4) SET (RESTRICT = _int_contsel, JOIN = _int_contjoinsel);
```

## Compatibility

There is no `ALTER OPERATOR` statement in
the SQL standard.

## See Also
