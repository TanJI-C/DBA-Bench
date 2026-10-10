# DROP OPERATOR CLASS

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_opclass.md`
- Source Title: `drop opclass`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP OPERATOR CLASS`
- Source Line Ranges: `1-70`
- Chunk ID: `pg16_fact_0275_af0f08e3e9`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `42f482175da9bee3b49b037520a9aa8d94acf5605c2c9cd0ac2ab8a0f4f3a75f`

## Retrieval Guidance

- Use When: Use for operator class drop syntax.
- Retrieval Keywords: DROP OPERATOR CLASS, opclass drop, access method, CASCADE
- Follow-up Guidance: No section split needed.
- Classification Note: Operator class removal syntax reference.

## Official Source Content

DROP OPERATOR CLASS
7
SQL - Language Statements

DROP OPERATOR CLASS
remove an operator class

```
DROP OPERATOR CLASS [ IF EXISTS ] `name` USING `index_method` [ CASCADE | RESTRICT ]
```

## Description

`DROP OPERATOR CLASS` drops an existing operator class.
To execute this command you must be the owner of the operator class.

`DROP OPERATOR CLASS` does not drop any of the operators
or functions referenced by the class.  If there are any indexes depending
on the operator class, you will need to specify
`CASCADE` for the drop to complete.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the operator class does not exist. A notice is issued
in this case.

**`name`**
: The name (optionally schema-qualified) of an existing operator class.

**`index_method`**
: The name of the index access method the operator class is for.

**`CASCADE`**
: Automatically drop objects that depend on the operator class (such as
indexes), and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the operator class if any objects depend on it.
This is the default.

## Notes

`DROP OPERATOR CLASS` will not drop the operator family
containing the class, even if there is nothing else left in the
family (in particular, in the case where the family was implicitly
created by `CREATE OPERATOR CLASS`).  An empty operator
family is harmless, but for the sake of tidiness you might wish to
remove the family with `DROP OPERATOR FAMILY`; or perhaps
better, use `DROP OPERATOR FAMILY` in the first place.

## Examples

Remove the B-tree operator class `widget_ops`:

```
DROP OPERATOR CLASS widget_ops USING btree;
```

This command will not succeed if there are any existing indexes
that use the operator class.  Add `CASCADE` to drop
such indexes along with the operator class.

## Compatibility

There is no `DROP OPERATOR CLASS` statement in the
SQL standard.

## See Also
