# Introduction

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/10_concurrency_control.md`
- Source Title: `Concurrency Control`
- Source Heading Path: `Concurrency Control > Introduction`
- Source Line Ranges: `11-47`
- Chunk ID: `pg16_fact_0159_6c7c6acb3a`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1167a90475d8ffe5032ce7d96be354d806a5225e0cff8295fe6183e81de2f546`

## Retrieval Guidance

- Use When: Need basic facts about PostgreSQL concurrency model.
- Retrieval Keywords: MVCC, concurrency control, transaction isolation, read consistency
- Follow-up Guidance: Use locking or isolation records for concrete behavior.
- Classification Note: Introduces MVCC and concurrency-control goals at a conceptual level.

## Official Source Content

## Introduction

PostgreSQL provides a rich set of tools
for developers to manage concurrent access to data.  Internally,
data consistency is maintained by using a multiversion
model (Multiversion Concurrency Control, MVCC).
This means that each SQL statement sees
a snapshot of data (a *database version*)
as it was some
time ago, regardless of the current state of the underlying data.
This prevents statements from viewing inconsistent data produced
by concurrent transactions performing updates on the same
data rows, providing *transaction isolation*
for each database session.  MVCC, by eschewing
the locking methodologies of traditional database systems,
minimizes lock contention in order to allow for reasonable
performance in multiuser environments.

The main advantage of using the MVCC model of
concurrency control rather than locking is that in
MVCC locks acquired for querying (reading) data
do not conflict with locks acquired for writing data, and so
reading never blocks writing and writing never blocks reading.
PostgreSQL maintains this guarantee
even when providing the strictest level of transaction
isolation through the use of an innovative *Serializable
Snapshot Isolation* (SSI) level.

Table- and row-level locking facilities are also available in
PostgreSQL for applications which don't
generally need full transaction isolation and prefer to explicitly
manage particular points of conflict.  However, proper
use of MVCC will generally provide better
performance than locks.  In addition, application-defined advisory
locks provide a mechanism for acquiring locks that are not tied
to a single transaction.
