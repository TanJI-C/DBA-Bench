# CREATE CONVERSION

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_conversion.md`
- Source Title: `create conversion`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE CONVERSION`
- Source Line Ranges: `1-98`
- Chunk ID: `pg16_fact_0219_27bb48106f`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `d7fd4670b2b087fb26da8f9b5a6d8224afd308092c8b0fefd0e084e133e4613b`

## Retrieval Guidance

- Use When: Use for conversion creation syntax.
- Retrieval Keywords: CREATE CONVERSION, encoding conversion, source encoding, destination encoding
- Follow-up Guidance: No section split needed.
- Classification Note: Encoding conversion object creation reference.

## Official Source Content

CREATE CONVERSION
7
SQL - Language Statements

CREATE CONVERSION
define a new encoding conversion

```
CREATE [ DEFAULT ] CONVERSION `name`
FOR `source_encoding` TO `dest_encoding` FROM `function_name`
```

## Description

`CREATE CONVERSION` defines a new conversion between
two character set encodings.

Conversions that are marked `DEFAULT` can be used for
automatic encoding conversion between client and server.  To support that
usage, two conversions, from encoding A to B *and*
from encoding B to A, must be defined.

To be able to create a conversion, you must have `EXECUTE` privilege
on the function and `CREATE` privilege on the destination schema.

## Parameters

**`DEFAULT`**
: The `DEFAULT` clause indicates that this conversion
is the default for this particular source to destination
encoding. There should be only one default encoding in a schema
for the encoding pair.

**`name`**
: The name of the conversion. The conversion name can be
schema-qualified. If it is not, the conversion is defined in the
current schema. The conversion name must be unique within a
schema.

**`source_encoding`**
: The source encoding name.

**`dest_encoding`**
: The destination encoding name.

**`function_name`**
: The function used to perform the conversion.  The function name can
be schema-qualified.  If it is not, the function will be looked
up in the path.

The function must have the following signature:

```
conv_proc(
integer,  -- source encoding ID
integer,  -- destination encoding ID
cstring,  -- source string (null terminated C string)
internal, -- destination (fill with a null terminated C string)
integer,  -- source string length
boolean   -- if true, don't throw an error if conversion fails
) RETURNS integer;
```

The return value is the number of source bytes that were successfully
converted. If the last argument is false, the function must throw an
error on invalid input, and the return value is always equal to the
source string length.

## Notes

Neither the source nor the destination encoding can
be `SQL_ASCII`, as the server's behavior for cases
involving the `SQL_ASCII` "encoding" is
hard-wired.

Use `DROP CONVERSION` to remove user-defined conversions.

The privileges required to create a conversion might be changed in a future
release.

## Examples

To create a conversion from encoding `UTF8` to
`LATIN1` using `myfunc`:

```
CREATE CONVERSION myconv FOR 'UTF8' TO 'LATIN1' FROM myfunc;
```

## Compatibility

`CREATE CONVERSION`
is a PostgreSQL extension.
There is no `CREATE CONVERSION`
statement in the SQL standard, but a `CREATE TRANSLATION`
statement that is very similar in purpose and syntax.

## See Also
