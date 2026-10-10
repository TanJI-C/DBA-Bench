# DROP CONVERSION

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_conversion.md`
- Source Title: `drop conversion`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP CONVERSION`
- Source Line Ranges: `1-47`
- Chunk ID: `pg16_fact_0263_bbd8d597b6`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `d5a4e2c0560019d1602032fb3a1c5f317f362fb4318c32054a09278c481c1232`

## Retrieval Guidance

- Use When: Use for conversion drop syntax.
- Retrieval Keywords: DROP CONVERSION, encoding conversion, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Conversion object removal syntax reference.

## Official Source Content

DROP CONVERSION
7
SQL - Language Statements

DROP CONVERSION
remove a conversion

```
DROP CONVERSION [ IF EXISTS ] `name` [ CASCADE | RESTRICT ]
```

## Description

`DROP CONVERSION` removes a previously defined conversion.
To be able to drop a conversion, you must own the conversion.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the conversion does not exist.
A notice is issued in this case.

**`name`**
: The name of the conversion. The conversion name can be
schema-qualified.

**`CASCADE`**
: These key words do not have any effect, since there are no
dependencies on conversions.

## Examples

To drop the conversion named `myname`:

```
DROP CONVERSION myname;
```

## Compatibility

There is no `DROP CONVERSION` statement in the SQL
standard, but a `DROP TRANSLATION` statement that
goes along with the `CREATE TRANSLATION` statement
that is similar to the `CREATE CONVERSION`
statement in PostgreSQL.

## See Also
