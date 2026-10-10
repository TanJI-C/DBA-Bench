# DROP RULE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_rule.md`
- Source Title: `drop rule`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP RULE`
- Source Line Ranges: `1-52`
- Chunk ID: `pg16_fact_0284_830dba0b1e`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `407d657264e3412cba43242b636c420490c845b1e029317d1a43e8c0c596bec0`

## Retrieval Guidance

- Use When: Use for rule drop syntax.
- Retrieval Keywords: DROP RULE, rewrite rule drop, ON table
- Follow-up Guidance: No section split needed.
- Classification Note: Rewrite rule removal syntax reference.

## Official Source Content

DROP RULE
7
SQL - Language Statements

DROP RULE
remove a rewrite rule

```
DROP RULE [ IF EXISTS ] `name` ON `table_name` [ CASCADE | RESTRICT ]
```

## Description

`DROP RULE` drops a rewrite rule.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the rule does not exist. A notice is issued
in this case.

**`name`**
: The name of the rule to drop.

**`table_name`**
: The name (optionally schema-qualified) of the table or view that
the rule applies to.

**`CASCADE`**
: Automatically drop objects that depend on the rule,
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the rule if any objects depend on it.  This is
the default.

## Examples

To drop the rewrite rule `newrule`:

```
DROP RULE newrule ON mytable;
```

## Compatibility

`DROP RULE` is a
PostgreSQL language extension, as is the
entire query rewrite system.

## See Also
