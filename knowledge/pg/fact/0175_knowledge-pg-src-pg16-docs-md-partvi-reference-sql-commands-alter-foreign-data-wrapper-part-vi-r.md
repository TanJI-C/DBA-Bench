# ALTER FOREIGN DATA WRAPPER

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/alter_foreign_data_wrapper.md`
- Source Title: `alter foreign data wrapper`
- Source Heading Path: `Part VI Reference > SQL Commands > ALTER FOREIGN DATA WRAPPER`
- Source Line Ranges: `1-95`
- Chunk ID: `pg16_fact_0175_56df93f94e`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `4045c6a6299b8c8c49f76c0d5c3adfeab07e72e8b81b771c0b6569e79fb9d53e`

## Retrieval Guidance

- Use When: Use for FDW object syntax and option reference.
- Retrieval Keywords: ALTER FOREIGN DATA WRAPPER, FDW options, FDW handler, FDW validator
- Follow-up Guidance: No section split needed.
- Classification Note: Foreign data wrapper object DDL reference for handler, validator, options, owner, and rename.

## Official Source Content

ALTER FOREIGN DATA WRAPPER
7
SQL - Language Statements

ALTER FOREIGN DATA WRAPPER
change the definition of a foreign-data wrapper

```
ALTER FOREIGN DATA WRAPPER `name`
[ HANDLER `handler_function` | NO HANDLER ]
[ VALIDATOR `validator_function` | NO VALIDATOR ]
[ OPTIONS ( [ ADD | SET | DROP ] `option` ['`value`'] [, ... ]) ]
ALTER FOREIGN DATA WRAPPER `name` OWNER TO { `new_owner` | CURRENT_ROLE | CURRENT_USER | SESSION_USER }
ALTER FOREIGN DATA WRAPPER `name` RENAME TO `new_name`
```

## Description

`ALTER FOREIGN DATA WRAPPER` changes the
definition of a foreign-data wrapper.  The first form of the
command changes the support functions or the generic options of the
foreign-data wrapper (at least one clause is required).  The second
form changes the owner of the foreign-data wrapper.

Only superusers can alter foreign-data wrappers.  Additionally,
only superusers can own foreign-data wrappers.

## Parameters

**`name`**
: The name of an existing foreign-data wrapper.

**`HANDLER `handler_function``**
: Specifies a new handler function for the foreign-data wrapper.

**`NO HANDLER`**
: This is used to specify that the foreign-data wrapper should no
longer have a handler function.

Note that foreign tables that use a foreign-data wrapper with no
handler cannot be accessed.

**`VALIDATOR `validator_function``**
: Specifies a new validator function for the foreign-data wrapper.

Note that it is possible that pre-existing options of the foreign-data
wrapper, or of dependent servers, user mappings, or foreign tables, are
invalid according to the new validator.  PostgreSQL does
not check for this.  It is up to the user to make sure that these
options are correct before using the modified foreign-data wrapper.
However, any options specified in this `ALTER FOREIGN DATA
WRAPPER` command will be checked using the new validator.

**`NO VALIDATOR`**
: This is used to specify that the foreign-data wrapper should no
longer have a validator function.

**`OPTIONS ( [ ADD | SET | DROP ] `option` ['`value`'] [, ... ] )`**
: Change options for the foreign-data
wrapper.  `ADD`, `SET`, and `DROP`
specify the action to be performed.  `ADD` is assumed
if no operation is explicitly specified.  Option names must be
unique; names and values are also validated using the foreign
data wrapper's validator function, if any.

**`new_owner`**
: The user name of the new owner of the foreign-data wrapper.

**`new_name`**
: The new name for the foreign-data wrapper.

## Examples

Change a foreign-data wrapper `dbi`, add
option `foo`, drop `bar`:

```
ALTER FOREIGN DATA WRAPPER dbi OPTIONS (ADD foo '1', DROP bar);
```

Change the foreign-data wrapper `dbi` validator
to `bob.myvalidator`:

```
ALTER FOREIGN DATA WRAPPER dbi VALIDATOR bob.myvalidator;
```

## Compatibility

`ALTER FOREIGN DATA WRAPPER` conforms to ISO/IEC
9075-9 (SQL/MED), except that the `HANDLER`,
`VALIDATOR`, `OWNER TO`, and `RENAME`
clauses are extensions.

## See Also
