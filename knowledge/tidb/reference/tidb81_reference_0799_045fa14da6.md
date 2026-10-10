# Constraint concepts

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/database-schema-concepts.md`
- Source Title: `Database Schema`
- Source Heading Path: `Database Schema > Constraints | Database Schema > Constraints > NOT NULL constraints | Database Schema > Constraints > CHECK constraints | Database Schema > Constraints > Primary key constraints | Database Schema > Constraints > Unique key constraints`
- Source Line Ranges: `132-153`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `cloud`, `tidb`
- Topic Tags: `constraints`, `not-null`, `check-constraints`, `primary-key-constraints`, `unique-key-constraints`, `data-integrity`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0799_045fa14da6`
- Source ID: `tidb-docs-8.1:tidb-cloud/database-schema-concepts.md#constraints`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3683e8cbdd27eedd6346a9e509e34c47db6c213d72da549747ad72c7041fc953`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/database-schema-concepts#constraints
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/database-schema-concepts.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the meaning or behavior of TiDB constraints such as `NOT NULL`, `CHECK`, primary key constraints, or unique key constraints.
- Retrieval Keywords: Constraints, NOT NULL constraint, CHECK constraint, Primary key constraints, Unique key constraints, NULL values, insert or update error, data integrity
- Follow-up Guidance: It states that TiDB supports almost the same constraints as MySQL and describes when errors are returned for `NOT NULL` and `CHECK` violations.
- Classification Note: This is reference content because it summarizes constraint semantics and enforcement behavior for TiDB tables.

## Official Source Content

## Constraints

TiDB supports almost the same constraints as MySQL.
### NOT NULL constraints

A `NOT NULL` constraint ensures that a column cannot contain `NULL` values.

When a column is defined with the `NOT NULL` constraint, TiDB ensures that any attempt to insert or update a row with a `NULL` value in that column will result in an error. This behavior is consistent with MySQL's implementation of `NOT NULL` constraints.
### CHECK constraints

A `CHECK` constraint restricts the values of a column in a table to meet your specified conditions. When the `CHECK` constraint is added to a table, TiDB checks whether the constraint is satisfied during the insertion or updates of data into the table. If the constraint is not met, an error is returned.
### Primary key constraints

Like MySQL, primary key constraints in TiDB contain unique constraints, that is, creating a primary key constraint is equivalent to having a unique constraint. In addition, other primary key constraints of TiDB are also similar to those of MySQL.
### Unique key constraints

Unique constraints mean that all non-null values in a unique index and a primary key column are unique.
