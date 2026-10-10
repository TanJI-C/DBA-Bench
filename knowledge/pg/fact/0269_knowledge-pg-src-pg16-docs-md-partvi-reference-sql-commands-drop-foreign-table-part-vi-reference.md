# DROP FOREIGN TABLE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_foreign_table.md`
- Source Title: `drop foreign table`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP FOREIGN TABLE`
- Source Line Ranges: `1-51`
- Chunk ID: `pg16_fact_0269_965ce6cbb1`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `d431a166af1223295dfc449ea5d50e408ef1ad87483658ce68b8d88dad5e4665`

## Retrieval Guidance

- Use When: Use for foreign table drop syntax.
- Retrieval Keywords: DROP FOREIGN TABLE, foreign table drop, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Foreign table removal syntax reference.

## Official Source Content

DROP FOREIGN TABLE
7
SQL - Language Statements

DROP FOREIGN TABLE
remove a foreign table

```
DROP FOREIGN TABLE [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP FOREIGN TABLE` removes a foreign table.
Only the owner of a foreign table can remove it.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the foreign table does not exist.
A notice is issued in this case.

**`name`**
: The name (optionally schema-qualified) of the foreign table to drop.

**`CASCADE`**
: Automatically drop objects that depend on the foreign table (such as
views), and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the foreign table if any objects depend on it.  This is
the default.

## Examples

To destroy two foreign tables, `films` and
`distributors`:

```
DROP FOREIGN TABLE films, distributors;
```

## Compatibility

This command conforms to ISO/IEC 9075-9 (SQL/MED), except that the
standard only allows one foreign table to be dropped per command, and apart
from the `IF EXISTS` option, which is a PostgreSQL
extension.

## See Also
