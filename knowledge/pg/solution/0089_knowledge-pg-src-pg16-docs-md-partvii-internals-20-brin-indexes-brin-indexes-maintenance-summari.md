# Maintenance; Summarization; autosummarize; brin_summarize_new_values; brin_desummarize_range

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVII_internals/20_brin_indexes.md`
- Source Title: `BRIN Indexes`
- Source Heading Path: `BRIN Indexes > Maintenance; Summarization; autosummarize; brin_summarize_new_values; brin_desummarize_range`
- Source Line Ranges: `48-97`
- Chunk ID: `pg16_solution_0089_acbb614c65`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `359e846f3a8fec72ed3acf3d0879f34685a4e30ce13d4bd50e17070e536b2679`

## Retrieval Guidance

- Use When: Remediate confirmed BRIN index inefficiency caused by unsummarized or stale ranges.
- Retrieval Keywords: BRIN summarize, autosummarize, brin_summarize_new_values, brin_desummarize_range, stale BRIN summary, VACUUM BRIN
- Follow-up Guidance: Confirm affected ranges and workload impact before forcing summarization.
- Classification Note: These sections describe actions for summarizing, desummarizing, and maintaining BRIN ranges after missing or stale summaries are identified.

## Official Source Content

### Index Maintenance

At the time of creation, all existing heap pages are scanned and a
summary index tuple is created for each range, including the
possibly-incomplete range at the end.
As new pages are filled with data, page ranges that are already
summarized will cause the summary information to be updated with data
from the new tuples.
When a new page is created that does not fall within the last
summarized range, the range that the new page belongs to
does not automatically acquire a summary tuple;
those tuples remain unsummarized until a summarization run is
invoked later, creating the initial summary for that range.

There are several ways to trigger the initial summarization of a page range.
If the table is vacuumed, either manually or by
[autovacuum](#autovacuum), all existing unsummarized
page ranges are summarized.
Also, if the index's
[index-reloption-autosummarize](#index-reloption-autosummarize) parameter is enabled,
which it isn't by default,
whenever autovacuum runs in that database, summarization will occur for all
unsummarized page ranges that have been filled,
regardless of whether the table itself is processed by autovacuum; see below.

Lastly, the following functions can be used:

When autosummarization is enabled, a request is sent to
`autovacuum` to execute a targeted summarization
for a block range when an insertion is detected for the first item
of the first page of the next block range,
to be fulfilled the next time an autovacuum
worker finishes running in the
same database.  If the request queue is full, the request is not recorded
and a message is sent to the server log:

```
LOG:  request for BRIN range summarization for index "brin_wi_idx" page 128 was not recorded
```

When this happens, the range will remain unsummarized until the next
regular vacuum run on the table, or one of the functions mentioned above
are invoked.

Conversely, a range can be de-summarized using the
`brin_desummarize_range(regclass, bigint)` function,
which is useful when the index tuple is no longer a very good
representation because the existing values have changed.
See [functions-admin-index](#functions-admin-index) for details.
