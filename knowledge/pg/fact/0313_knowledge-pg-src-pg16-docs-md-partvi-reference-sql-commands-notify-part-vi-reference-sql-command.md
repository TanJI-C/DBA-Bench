# NOTIFY

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/notify.md`
- Source Title: `notify`
- Source Heading Path: `Part VI Reference > SQL Commands > NOTIFY`
- Source Line Ranges: `124-132`
- Chunk ID: `pg16_fact_0313_f3fc161993`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a53369be81899f7c09fa7733a5ca3b27b959164c5d2be220dc77dbbd5a24f9f9`

## Retrieval Guidance

- Use When: Use for notification syntax and transaction delivery behavior.
- Retrieval Keywords: NOTIFY, LISTEN, payload, asynchronous notification
- Follow-up Guidance: No section split needed.
- Classification Note: Asynchronous notification send syntax reference.

## Official Source Content

### pg_notify

To send a notification you can also use the function
``pg_notify`(`text`,
`text`)`. The function takes the channel name as the
first argument and the payload as the second. The function is much easier
to use than the `NOTIFY` command if you need to work with
non-constant channel names and payloads.
