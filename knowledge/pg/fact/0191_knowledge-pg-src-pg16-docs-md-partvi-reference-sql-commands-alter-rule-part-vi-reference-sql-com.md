# ALTER RULE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_rule.md`
- Source Title: `alter rule`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER RULE`
- Source Line Ranges: `1-46`
- Chunk ID: `pg16_fact_0191_53e6eee768`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `71c5cb05537ec3806c33b535ed6e7b77006ad4716471d4621d8f0bdfac38f386`

## Retrieval Guidance

- Use When: Use for rule rename syntax.
- Retrieval Keywords: ALTER RULE, rule rename, rewrite rule
- Follow-up Guidance: No section split needed.
- Classification Note: Rule object DDL reference for rename only.

## Official Source Content

ALTER RULE
7
SQL - Language Statements

ALTER RULE
change the definition of a rule

```
ALTER RULE `name` ON `table_name` RENAME TO `new_name`
```

## Description

`ALTER RULE` changes properties of an existing
rule.  Currently, the only available action is to change the rule's name.

To use `ALTER RULE`, you must own the table or view that
the rule applies to.

## Parameters

**`name`**
: The name of an existing rule to alter.

**`table_name`**
: The name (optionally schema-qualified) of the table or view that the
rule applies to.

**`new_name`**
: The new name for the rule.

## Examples

To rename an existing rule:

```
ALTER RULE notify_all ON emp RENAME TO notify_me;
```

## Compatibility

`ALTER RULE` is a
PostgreSQL language extension, as is the
entire query rewrite system.

## See Also
