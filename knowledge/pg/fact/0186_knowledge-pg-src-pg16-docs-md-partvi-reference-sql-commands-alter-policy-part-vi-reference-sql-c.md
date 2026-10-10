# ALTER POLICY

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_policy.md`
- Source Title: `alter policy`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER POLICY`
- Source Line Ranges: `1-65`
- Chunk ID: `pg16_fact_0186_0a58f15304`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `9fd3d70f9c8e392ce18fc43d044e3a9f9d187a1e206d79051770bd5d5e4f2736`

## Retrieval Guidance

- Use When: Use for RLS policy syntax and behavior reference.
- Retrieval Keywords: ALTER POLICY, row level security, RLS policy, USING, WITH CHECK
- Follow-up Guidance: No section split needed.
- Classification Note: Row-level security policy DDL reference for changing policy roles and expressions.

## Official Source Content

ALTER POLICY
7
SQL - Language Statements

ALTER POLICY
change the definition of a row-level security policy

```
ALTER POLICY `name` ON `table_name` RENAME TO `new_name`

ALTER POLICY `name` ON `table_name`
[ TO { `role_name` | PUBLIC | CURRENT_ROLE | CURRENT_USER | SESSION_USER } [, ...] ]
[ USING ( `using_expression` ) ]
[ WITH CHECK ( `check_expression` ) ]
```

## Description

`ALTER POLICY` changes the definition of an existing
row-level security policy.  Note that `ALTER POLICY`
only allows the set of roles to which the policy applies and the
`USING` and `WITH CHECK` expressions to
be modified.  To change other properties of a policy, such as the command
to which it applies or whether it is permissive or restrictive, the policy
must be dropped and recreated.

To use `ALTER POLICY`, you must own the table that
the policy applies to.

In the second form of `ALTER POLICY`, the role list,
`using_expression`, and
`check_expression` are replaced
independently if specified.  When one of those clauses is omitted, the
corresponding part of the policy is unchanged.

## Parameters

**`name`**
: The name of an existing policy to alter.

**`table_name`**
: The name (optionally schema-qualified) of the table that the
policy is on.

**`new_name`**
: The new name for the policy.

**`role_name`**
: The role(s) to which the policy applies.  Multiple roles can be
specified at one time.  To apply the policy to all roles,
use `PUBLIC`.

**`using_expression`**
: The `USING` expression for the policy.
See [sql-createpolicy](#sql-createpolicy) for details.

**`check_expression`**
: The `WITH CHECK` expression for the policy.
See [sql-createpolicy](#sql-createpolicy) for details.

## Compatibility

`ALTER POLICY` is a PostgreSQL extension.

## See Also
