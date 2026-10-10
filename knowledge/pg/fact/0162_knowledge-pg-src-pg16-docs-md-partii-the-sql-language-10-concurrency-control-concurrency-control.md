# Caveats

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/10_concurrency_control.md`
- Source Title: `Concurrency Control`
- Source Heading Path: `Concurrency Control > Caveats`
- Source Line Ranges: `1132-1165`
- Chunk ID: `pg16_fact_0162_99eeef63fc`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `608aa21f2dd51bf7ea01ff3132eb7b8482996b1424a4c3250504de49c38d8cbd`

## Retrieval Guidance

- Use When: Need facts about edge cases in concurrency behavior.
- Retrieval Keywords: concurrency caveat, consistency caveat, transaction behavior, isolation limitation
- Follow-up Guidance: Use isolation and locking solution records if the caveat maps to a concrete application problem.
- Classification Note: Documents limitations and caveats in PostgreSQL consistency behavior without a direct diagnostic or remediation procedure.

## Official Source Content

## Caveats

Some DDL commands, currently only [`TRUNCATE`](#sql-truncate) and the
table-rewriting forms of [`ALTER TABLE`](#sql-altertable), are not
MVCC-safe.  This means that after the truncation or rewrite commits, the
table will appear empty to concurrent transactions, if they are using a
snapshot taken before the DDL command committed.  This will only be an
issue for a transaction that did not access the table in question
before the DDL command started — any transaction that has done so
would hold at least an `ACCESS SHARE` table lock,
which would block the DDL command until that transaction completes.
So these commands will not cause any apparent inconsistency in the
table contents for successive queries on the target table, but they
could cause visible inconsistency between the contents of the target
table and other tables in the database.

Support for the Serializable transaction isolation level has not yet
been added to hot standby replication targets (described in
[hot-standby](#hot-standby)).  The strictest isolation level currently
supported in hot standby mode is Repeatable Read.  While performing all
permanent database writes within Serializable transactions on the
primary will ensure that all standbys will eventually reach a consistent
state, a Repeatable Read transaction run on the standby can sometimes
see a transient state that is inconsistent with any serial execution
of the transactions on the primary.

Internal access to the system catalogs is not done using the isolation
level of the current transaction.  This means that newly created database
objects such as tables are visible to concurrent Repeatable Read and
Serializable transactions, even though the rows they contain are not.  In
contrast, queries that explicitly examine the system catalogs don't see
rows representing concurrently created database objects, in the higher
isolation levels.
