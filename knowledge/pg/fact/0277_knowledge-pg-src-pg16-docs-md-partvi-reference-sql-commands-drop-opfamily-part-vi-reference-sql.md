# DROP OPERATOR FAMILY

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_opfamily.md`
- Source Title: `drop opfamily`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP OPERATOR FAMILY`
- Source Line Ranges: `1-61`
- Chunk ID: `pg16_fact_0277_684bb1eb3e`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `eb5dd78e9a80dde214513cfc09ecb830547e3a5b53eebef1b51a91c869d4e1fc`

## Retrieval Guidance

- Use When: Use for operator family drop syntax.
- Retrieval Keywords: DROP OPERATOR FAMILY, opfamily drop, access method, CASCADE
- Follow-up Guidance: No section split needed.
- Classification Note: Operator family removal syntax reference.

## Official Source Content

DROP OPERATOR FAMILY
7
SQL - Language Statements

DROP OPERATOR FAMILY
remove an operator family

```
DROP OPERATOR FAMILY [ IF EXISTS ] `name` USING `index_method` [ CASCADE | RESTRICT ]
```

## Description

`DROP OPERATOR FAMILY` drops an existing operator family.
To execute this command you must be the owner of the operator family.

`DROP OPERATOR FAMILY` includes dropping any operator
classes contained in the family, but it does not drop any of the operators
or functions referenced by the family.  If there are any indexes depending
on operator classes within the family, you will need to specify
`CASCADE` for the drop to complete.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the operator family does not exist.
A notice is issued in this case.

**`name`**
: The name (optionally schema-qualified) of an existing operator family.

**`index_method`**
: The name of the index access method the operator family is for.

**`CASCADE`**
: Automatically drop objects that depend on the operator family,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the operator family if any objects depend on it.
This is the default.

## Examples

Remove the B-tree operator family `float_ops`:

```
DROP OPERATOR FAMILY float_ops USING btree;
```

This command will not succeed if there are any existing indexes
that use operator classes within the family.  Add `CASCADE` to
drop such indexes along with the operator family.

## Compatibility

There is no `DROP OPERATOR FAMILY` statement in the
SQL standard.

## See Also
