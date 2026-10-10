# DROP USER MAPPING

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_user_mapping.md`
- Source Title: `drop user mapping`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP USER MAPPING`
- Source Line Ranges: `1-51`
- Chunk ID: `pg16_fact_0300_9ec16c2213`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `ab82af1995f5596a3f039398bb2fd503ed98fc864f0adafcb740ccb2cbda7896`

## Retrieval Guidance

- Use When: Use for user mapping drop syntax.
- Retrieval Keywords: DROP USER MAPPING, foreign server, user mapping drop
- Follow-up Guidance: No section split needed.
- Classification Note: Foreign user mapping removal syntax reference.

## Official Source Content

DROP USER MAPPING
7
SQL - Language Statements

DROP USER MAPPING
remove a user mapping for a foreign server

```
DROP USER MAPPING [ IF EXISTS ] FOR { `user_name` | USER | CURRENT_ROLE | CURRENT_USER | PUBLIC } SERVER `server_name`
```

## Description

`DROP USER MAPPING` removes an existing user
mapping from foreign server.

The owner of a foreign server can drop user mappings for that server
for any user.  Also, a user can drop a user mapping for their own
user name if `USAGE` privilege on the server has been
granted to the user.

## Parameters

**`IF EXISTS`**
: Do not throw an error if the user mapping does not exist.  A
notice is issued in this case.

**`user_name`**
: User name of the mapping.  `CURRENT_ROLE`, `CURRENT_USER`,
and `USER` match the name of the current
user.  `PUBLIC` is used to match all present and
future user names in the system.

**`server_name`**
: Server name of the user mapping.

## Examples

Drop a user mapping `bob`, server `foo` if it exists:

```
DROP USER MAPPING IF EXISTS FOR bob SERVER foo;
```

## Compatibility

`DROP USER MAPPING` conforms to ISO/IEC 9075-9
(SQL/MED).  The `IF EXISTS` clause is
a PostgreSQL extension.

## See Also
