# DROP DOMAIN

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_domain.md`
- Source Title: `drop domain`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP DOMAIN`
- Source Line Ranges: `1-50`
- Chunk ID: `pg16_fact_0265_6603c429e3`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `72ac34b26090730f2bcebaf14b3efd0932b38e82a96bfd4d41b2e22e17595483`

## Retrieval Guidance

- Use When: Use for domain drop syntax.
- Retrieval Keywords: DROP DOMAIN, domain object, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Domain object removal syntax reference.

## Official Source Content

DROP DOMAIN
7
SQL - Language Statements

DROP DOMAIN
remove a domain

```
DROP DOMAIN [ IF EXISTS ] `name` [, ...] [ CASCADE | RESTRICT ]
```

## Description

`DROP DOMAIN` removes a domain.  Only the owner of
a domain can remove it.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the domain does not exist. A notice is issued
in this case.

**`name`**
: The name (optionally schema-qualified) of an existing domain.

**`CASCADE`**
: Automatically drop objects that depend on the domain (such as
table columns),
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the domain if any objects depend on it.  This is
the default.

## Examples

To remove the domain `box`:

```
DROP DOMAIN box;
```

## Compatibility

This command conforms to the SQL standard, except for the
`IF EXISTS` option, which is a PostgreSQL
extension.

## See Also
