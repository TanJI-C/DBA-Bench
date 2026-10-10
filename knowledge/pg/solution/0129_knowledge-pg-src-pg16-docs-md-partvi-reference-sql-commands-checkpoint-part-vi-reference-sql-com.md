# CHECKPOINT

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/checkpoint.md`
- Source Title: `checkpoint`
- Source Heading Path: `Part VI Reference > SQL Commands > CHECKPOINT`
- Source Line Ranges: `1-38`
- Chunk ID: `pg16_solution_0129_0a49de6c6f`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `0c78b0f2afe90dbac2033473a18d12dbda7f8f49f5f7909aa9428e02df3c3523`

## Retrieval Guidance

- Use When: Use only after confirming a need to force checkpoint behavior, such as controlled maintenance or recovery validation.
- Retrieval Keywords: CHECKPOINT, force checkpoint, WAL checkpoint, restartpoint
- Follow-up Guidance: Check checkpoint cost/IO impact and required privileges before use.
- Classification Note: Forces an immediate checkpoint/restartpoint; it is an operational action, not normal syntax-only reference.

## Official Source Content

CHECKPOINT
7
SQL - Language Statements

CHECKPOINT
force a write-ahead log checkpoint

```
CHECKPOINT
```

## Description

A checkpoint is a point in the write-ahead log sequence at which
all data files have been updated to reflect the information in the
log.  All data files will be flushed to disk.  Refer to
[wal-configuration](#wal-configuration) for more details about what happens
during a checkpoint.

The `CHECKPOINT` command forces an immediate
checkpoint when the command is issued, without waiting for a
regular checkpoint scheduled by the system (controlled by the settings in
[runtime-config-wal-checkpoints](#runtime-config-wal-checkpoints)).
`CHECKPOINT` is not intended for use during normal
operation.

If executed during recovery, the `CHECKPOINT` command
will force a restartpoint (see [wal-configuration](#wal-configuration))
rather than writing a new checkpoint.

Only superusers or users with the privileges of
the [`pg_checkpoint`](#predefined-roles-table)
role can call `CHECKPOINT`.

## Compatibility

The `CHECKPOINT` command is a
PostgreSQL language extension.
