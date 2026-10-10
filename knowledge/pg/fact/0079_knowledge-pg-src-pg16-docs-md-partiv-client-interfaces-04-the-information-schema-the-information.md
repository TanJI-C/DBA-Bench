# The Schema; Data Types; all information_schema views

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIV_client_interfaces/04_the_information_schema.md`
- Source Title: `The Information Schema`
- Source Heading Path: `The Information Schema > The Schema; Data Types; all information_schema views`
- Source Line Ranges: `38-53, 54-89`
- Chunk ID: `pg16_fact_0079_242e061728`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `bbfd46f438e1768c56a0ba4a08aa6e1574d5575d65cddebbdd00d19f85df6bbc`

## Retrieval Guidance

- Use When: Retrieve portable metadata about database objects, privileges, routines, tables, columns, domains, and constraints.
- Retrieval Keywords: information_schema, columns, tables, routines, schemata, table_privileges, foreign_tables, views
- Follow-up Guidance: Use PostgreSQL-specific system catalog/view records when non-standard metadata fields are needed.
- Classification Note: The chapter is a SQL-standard metadata reference for information_schema views and their columns; per instruction, schema/view fields remain fact even when useful for inspection.

## Official Source Content

## The Schema

The information schema itself is a schema named
`information_schema`.  This schema automatically
exists in all databases.  The owner of this schema is the initial
database user in the cluster, and that user naturally has all the
privileges on this schema, including the ability to drop it (but
the space savings achieved by that are minuscule).

By default, the information schema is not in the schema search
path, so you need to access all objects in it through qualified
names.  Since the names of some of the objects in the information
schema are generic names that might occur in user applications, you
should be careful if you want to put the information schema in the
path.

## Data Types

The columns of the information schema views use special data types
that are defined in the information schema.  These are defined as
simple domains over ordinary built-in types.  You should not use
these types for work outside the information schema, but your
applications must be prepared for them if they select from the
information schema.

These types are:

**`cardinal_number`**
: A nonnegative integer.

**`character_data`**
: A character string (without specific maximum length).

**`sql_identifier`**
: A character string.  This type is used for SQL identifiers, the
type `character_data` is used for any other kind of
text data.

**`time_stamp`**
: A domain over the type `timestamp with time zone`

**`yes_or_no`**
: A character string domain that contains
either `YES` or `NO`.  This
is used to represent Boolean (true/false) data in the
information schema.  (The information schema was invented
before the type `boolean` was added to the SQL
standard, so this convention is necessary to keep the
information schema backward compatible.)

Every column in the information schema has one of these five types.
