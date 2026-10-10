# DROP AGGREGATE

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_aggregate.md`
- Source Title: `drop aggregate`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP AGGREGATE`
- Source Line Ranges: `1-94`
- Chunk ID: `pg16_fact_0260_6c5e86d1cf`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `656440f4abba4d3c84a17066159b7f06e4e31ea9d281aefbf0e992ab4efeee2f`

## Retrieval Guidance

- Use When: Use for aggregate drop syntax.
- Retrieval Keywords: DROP AGGREGATE, aggregate signature, CASCADE, RESTRICT
- Follow-up Guidance: No section split needed.
- Classification Note: Aggregate object removal syntax reference.

## Official Source Content

DROP AGGREGATE
7
SQL - Language Statements

DROP AGGREGATE
remove an aggregate function

```
DROP AGGREGATE [ IF EXISTS ] `name` ( `aggregate_signature` ) [, ...] [ CASCADE | RESTRICT ]

where `aggregate_signature` is:

* |
[ `argmode` ] [ `argname` ] `argtype` [ , ... ] |
[ [ `argmode` ] [ `argname` ] `argtype` [ , ... ] ] ORDER BY [ `argmode` ] [ `argname` ] `argtype` [ , ... ]
```

## Description

`DROP AGGREGATE` removes an existing
aggregate function. To execute this command the current
user must be the owner of the aggregate function.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the aggregate does not exist. A notice is issued
in this case.

**`name`**
: The name (optionally schema-qualified) of an existing aggregate function.

**`argmode`**
: The mode of an argument: `IN` or `VARIADIC`.
If omitted, the default is `IN`.

**`argname`**
: The name of an argument.
Note that `DROP AGGREGATE` does not actually pay
any attention to argument names, since only the argument data
types are needed to determine the aggregate function's identity.

**`argtype`**
: An input data type on which the aggregate function operates.
To reference a zero-argument aggregate function, write `*`
in place of the list of argument specifications.
To reference an ordered-set aggregate function, write
`ORDER BY` between the direct and aggregated argument
specifications.

**`CASCADE`**
: Automatically drop objects that depend on the aggregate function
(such as views using it),
and in turn all objects that depend on those objects
(see [ddl-depend](#ddl-depend)).

**`RESTRICT`**
: Refuse to drop the aggregate function if any objects depend on
it.  This is the default.

## Notes

Alternative syntaxes for referencing ordered-set aggregates
are described under [sql-alteraggregate](#sql-alteraggregate).

## Examples

To remove the aggregate function `myavg` for type
`integer`:

```
DROP AGGREGATE myavg(integer);
```

To remove the hypothetical-set aggregate function `myrank`,
which takes an arbitrary list of ordering columns and a matching list
of direct arguments:

```
DROP AGGREGATE myrank(VARIADIC "any" ORDER BY VARIADIC "any");
```

To remove multiple aggregate functions in one command:

```
DROP AGGREGATE myavg(integer), myavg(bigint);
```

## Compatibility

There is no `DROP AGGREGATE` statement in the SQL
standard.

## See Also
