---
doc_id: standard.knowledge.postgresql-document-classification
doc_type: standard
status: canonical
audience: [authoring, reviewer, maintainer]
exposure: agent_safe
scope: [postgres, knowledge]
summary: Defines the section-level classification rules and materialization boundary for the PostgreSQL hierarchical knowledge base.
source_of_truth: code
related: []
---

# PostgreSQL Hierarchical Classification Rules

This document defines the section-level rules used to classify PostgreSQL 16
official documentation into `configuration`, `guide`, `solution`, and `fact`.

## Source Boundary

Only this directory can be used as source:

```text
`knowledge/pg_src/pg16-docs-md` (a local mirror of the upstream PostgreSQL 16 documentation; not distributed with the repo)
```

Do not reuse existing `knowledge/pg` content as source text.

## Classification Unit

The default unit is a Markdown section. A section can be split further when it
contains multiple operational roles. A whole file can be used as a unit only
when the file is already a narrow reference entry, such as a single SQL command
or client utility.

## Priority

When a section could fit multiple categories, prefer:

1. `solution`
2. `guide`
3. `configuration`
4. `fact`

This keeps concrete remediation and diagnostic evidence more discoverable.

## `configuration`

Use for parameter and configuration semantics.

Include content about:

- parameter meaning, unit, default, allowed value, scope, or restart/reload
  behavior
- `postgresql.conf`, `postgresql.auto.conf`, `pg_hba.conf`
- `SET`, `SHOW`, `RESET`, `ALTER SYSTEM`
- `ALTER DATABASE`, `ALTER ROLE`, or related default-setting behavior
- `pg_settings`, `current_setting`, `set_config`
- WAL, planner, logging, memory, connection, authentication, autovacuum, JIT,
  replication, SSL, and OS resource settings

## `guide`

Use for diagnosis and root-cause confirmation.

Include content that tells an agent what to inspect when symptoms appear:

- lock waits, blockers, deadlocks, long transactions
- `pg_locks`, `pg_stat_activity`, wait events
- table bloat, dead tuples, vacuum/autovacuum evidence
- slow queries, `EXPLAIN`, planner statistics, index usage
- disk usage, WAL growth, checkpoint pressure, temporary files
- replication lag/conflicts, progress reporting, readiness checks

## `solution`

Use for remediation after a cause has been confirmed.

Include content about:

- `VACUUM`, `ANALYZE`, `REINDEX`, `CLUSTER`, `CHECKPOINT`
- `CREATE INDEX`, `CREATE STATISTICS`, and documented tuning actions after
  query diagnosis
- backup, restore, PITR, failover, upgrade, checksum, repair, and recovery
  procedures
- `pg_dump`, `pg_restore`, `pg_basebackup`, `pg_amcheck`, `pg_resetwal`,
  `vacuumdb`, `reindexdb`, `clusterdb`, and related utilities

## `fact`

Use for foundational facts and reference material not covered above:

- tutorials
- SQL syntax and object semantics
- data types, functions, operators
- catalog, view, and information-schema field reference
- internals, storage, WAL mechanism, index internals
- appendixes, glossary, error codes, keywords, limits

## Split Rules

Split mixed sections:

- view field definitions go to `fact`; instructions for using the view to
  confirm a problem go to `guide`
- command semantics for a repair action go to `solution`; general syntax-only
  object reference can stay `fact`
- parameter semantics go to `configuration`; diagnosis that uses a parameter as
  evidence goes to `guide`

## Mapping Fields

Every target snippet must have:

- `chunk_id`
- `category`
- `target_file`
- `source_file`
- `source_title`
- `source_heading_path`
- `source_line_start`
- `source_line_end`
- `classification_reason`
- `retrieval_keywords`
- `use_when`
- `follow_up`
- `review_status`

Use `review_status = "needs_human_review"` for broad or ambiguous sections.
