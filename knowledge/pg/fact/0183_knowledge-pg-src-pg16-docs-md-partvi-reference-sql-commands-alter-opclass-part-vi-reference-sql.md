# ALTER OPERATOR CLASS

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_opclass.md`
- Source Title: `alter opclass`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER OPERATOR CLASS`
- Source Line Ranges: `1-56`
- Chunk ID: `pg16_fact_0183_b4ca17414c`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `ff077016e9786fea605343d4815b192cbe55ea6be9e2fcba0fc6f209fb015ad6`

## Retrieval Guidance

- Use When: Use for operator class metadata syntax.
- Retrieval Keywords: ALTER OPERATOR CLASS, opclass rename, opclass owner, opclass schema
- Follow-up Guidance: No section split needed.
- Classification Note: Operator class object DDL reference for rename, owner, and schema.

## Official Source Content

ALTER OPERATOR CLASS
7
SQL - Language Statements

ALTER OPERATOR CLASS
change the definition of an operator class

```
ALTER OPERATOR CLASS `name` USING `index_method`
RENAME TO `new_name`

ALTER OPERATOR CLASS `name` USING `index_method`
OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }

ALTER OPERATOR CLASS `name` USING `index_method`
SET SCHEMA `new_schema`
```

## Description

`ALTER OPERATOR CLASS` changes the definition of
an operator class.

You must own the operator class to use `ALTER OPERATOR CLASS`.
To alter the owner, you must be able to `SET ROLE` to the
new owning role, and that role must have `CREATE`
privilege on the operator class's schema.
(These restrictions enforce that altering the
owner doesn't do anything you couldn't do by dropping and recreating the
operator class.  However, a superuser can alter ownership of any operator
class anyway.)

## Parameters

**`name`**
: The name (optionally schema-qualified) of an existing operator
class.

**`index_method`**
: The name of the index method this operator class is for.

**`new_name`**
: The new name of the operator class.

**`new_owner`**
: The new owner of the operator class.

**`new_schema`**
: The new schema for the operator class.

## Compatibility

There is no `ALTER OPERATOR CLASS` statement in
the SQL standard.

## See Also
