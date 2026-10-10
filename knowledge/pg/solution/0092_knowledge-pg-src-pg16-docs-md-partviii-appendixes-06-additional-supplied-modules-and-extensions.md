# Repairing Corruption

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > amcheck - tools to verify table and index consistency > Repairing Corruption`
- Source Line Ranges: `548-561`
- Chunk ID: `pg16_solution_0092_7990bd83d0`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f5ef4f2020d5a3a4812842e337a5f0ad7cdd207907c1710828343201082e5671`

## Retrieval Guidance

- Use When: Respond to confirmed PostgreSQL index or table corruption.
- Retrieval Keywords: amcheck repairing corruption, REINDEX, restore from backup, index corruption repair, heap corruption repair
- Follow-up Guidance: Human review is required because corruption repair can involve data loss, restore decisions, or production downtime.
- Classification Note: This section discusses corrective actions after corruption has been confirmed.

## Official Source Content

### Repairing Corruption

No error concerning corruption raised by `amcheck` should
ever be a false positive.  `amcheck` raises
errors in the event of conditions that, by definition, should never
happen, and so careful analysis of `amcheck`
errors is often required.

There is no general method of repairing problems that
`amcheck` detects.  An explanation for the root cause of
an invariant violation should be sought.  [pageinspect](#pageinspect) may play a useful role in diagnosing
corruption that `amcheck` detects.  A `REINDEX`
may not be effective in repairing corruption.
