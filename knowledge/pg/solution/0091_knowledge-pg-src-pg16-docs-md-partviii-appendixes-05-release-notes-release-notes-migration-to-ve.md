# Migration to Version 16; migration/incompatibility notes for major versions

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/05_release_notes.md`
- Source Title: `05 release notes`
- Source Heading Path: `Release Notes > Migration to Version 16; migration/incompatibility notes for major versions`
- Source Line Ranges: `38-44, 513-519, 585-591, 981-987, 1439-1450, 1961-1975, 2322-2328, 2366-2372, 2810-2816, 2897-2909, 3448-3454, 3898-3911, 4370-4380, 4900-4910`
- Chunk ID: `pg16_solution_0091_007c552b2f`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4ff094c786941510180691fc59488ae552acde0d15d884452b5b75ea30f7226d`

## Retrieval Guidance

- Use When: Plan or execute remediation for a confirmed version-upgrade compatibility issue.
- Retrieval Keywords: Migration to Version 16, upgrade incompatibility, PostgreSQL upgrade, release migration, dump restore, pg_upgrade
- Follow-up Guidance: Human review is needed because release-note actions are version-specific and can affect production upgrade safety.
- Classification Note: Migration sections contain action-oriented upgrade checks and incompatibility handling after deciding to move between PostgreSQL versions.

## Official Source Content

### Migration to Version 16.14

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.10,
see [release-16-10](#release-16-10).

### Migration to Version 16.13

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.10,
see [release-16-10](#release-16-10).

### Migration to Version 16.12

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.10,
see [release-16-10](#release-16-10).

### Migration to Version 16.11

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.10,
see [release-16-10](#release-16-10).

### Migration to Version 16.10

A dump/restore is not required for those running 16.X.

However, if you have any
BRIN `numeric_minmax_multi_ops` indexes, it is
advisable to reindex them after updating.  See the fourth changelog
entry below.

Also, if you are upgrading from a version earlier than 16.9,
see [release-16-9](#release-16-9).

### Migration to Version 16.9

A dump/restore is not required for those running 16.X.

However, if you have any self-referential foreign key constraints on
partitioned tables, it may be necessary to recreate those constraints
to ensure that they are being enforced correctly.  See the second
changelog entry below.

Also, if you have any BRIN bloom indexes, it may be advisable to
reindex them after updating.  See the third changelog entry below.

Also, if you are upgrading from a version earlier than 16.5,
see [release-16-5](#release-16-5).

### Migration to Version 16.8

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.5,
see [release-16-5](#release-16-5).

### Migration to Version 16.7

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.5,
see [release-16-5](#release-16-5).

### Migration to Version 16.6

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.5,
see [release-16-5](#release-16-5).

### Migration to Version 16.5

A dump/restore is not required for those running 16.X.

However, if you have ever detached a partition from a partitioned
table that has a foreign-key reference to another partitioned table,
and not dropped the former partition, then you may have catalog and/or
data corruption to repair, as detailed in the fifth changelog entry
below.

Also, if you are upgrading from a version earlier than 16.3,
see [release-16-3](#release-16-3).

### Migration to Version 16.4

A dump/restore is not required for those running 16.X.

However, if you are upgrading from a version earlier than 16.3,
see [release-16-3](#release-16-3).

### Migration to Version 16.3

A dump/restore is not required for those running 16.X.

However, a security vulnerability was found in the system
views `pg_stats_ext`
and `pg_stats_ext_exprs`, potentially allowing
authenticated database users to see data they shouldn't.  If this is
of concern in your installation, follow the steps in the first
changelog entry below to rectify it.

Also, if you are upgrading from a version earlier than 16.2,
see [release-16-2](#release-16-2).

### Migration to Version 16.2

A dump/restore is not required for those running 16.X.

However, one bug was fixed that could have resulted in corruption of
GIN indexes during concurrent updates.  If you suspect such
corruption, reindex affected indexes after installing this update.

Also, if you are upgrading from a version earlier than 16.1,
see [release-16-1](#release-16-1).

### Migration to Version 16.1

A dump/restore is not required for those running 16.X.

However, several mistakes have been discovered that could lead to
certain types of indexes yielding wrong search results or being
unnecessarily inefficient.  It is advisable
to `REINDEX` potentially-affected indexes after
installing this update.  See the fourth through seventh changelog
entries below.
