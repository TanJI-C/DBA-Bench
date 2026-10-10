# test_decoding - SQL-based test/example module for WAL logical decoding

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > test_decoding - SQL-based test/example module for WAL logical decoding`
- Source Line Ranges: `10208-10255`
- Chunk ID: `pg16_fact_0128_ec01174565`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e7730ffad1165cc2ac4bf12b1a4e387b5ff91431423b08c87b0e2a21fb5c7a12`

## Retrieval Guidance

- Use When: Understand or test logical decoding output using the supplied example plugin.
- Retrieval Keywords: test_decoding, logical decoding output, pg_logical_slot_get_changes, output plugin example
- Follow-up Guidance: Use logical-decoding slot records for WAL retention or replication-slot remediation.
- Classification Note: The module is a test/example logical decoding output plugin and is primarily reference for decoding output behavior.

## Official Source Content

## test_decoding — SQL-based test/example module for WAL logical decoding

`test_decoding` is an example of a logical decoding
output plugin. It doesn't do anything especially useful, but can serve as
a starting point for developing your own output plugin.

`test_decoding` receives WAL through the logical decoding
mechanism and decodes it into text representations of the operations
performed.

Typical output from this plugin, used over the SQL logical decoding
interface, might be:

```
postgres=# SELECT * FROM pg_logical_slot_get_changes('test_slot', NULL, NULL, 'include-xids', '0');
lsn     | xid |                       data
-----------+-----+--------------------------------------------------
0/16D30F8 | 691 | BEGIN
0/16D32A0 | 691 | table public.data: INSERT: id[int4]:2 data[text]:'arg'
0/16D32A0 | 691 | table public.data: INSERT: id[int4]:3 data[text]:'demo'
0/16D32A0 | 691 | COMMIT
0/16D32D8 | 692 | BEGIN
0/16D3398 | 692 | table public.data: DELETE: id[int4]:2
0/16D3398 | 692 | table public.data: DELETE: id[int4]:3
0/16D3398 | 692 | COMMIT
(8 rows)
```

We can also get the changes of the in-progress transaction, and the typical
output might be:

```
postgres[33712]=#* SELECT * FROM pg_logical_slot_get_changes('test_slot', NULL, NULL, 'stream-changes', '1');
lsn    | xid |                       data
-----------+-----+--------------------------------------------------
0/16B21F8 | 503 | opening a streamed block for transaction TXN 503
0/16B21F8 | 503 | streaming change for TXN 503
0/16B2300 | 503 | streaming change for TXN 503
0/16B2408 | 503 | streaming change for TXN 503
0/16BEBA0 | 503 | closing a streamed block for transaction TXN 503
0/16B21F8 | 503 | opening a streamed block for transaction TXN 503
0/16BECA8 | 503 | streaming change for TXN 503
0/16BEDB0 | 503 | streaming change for TXN 503
0/16BEEB8 | 503 | streaming change for TXN 503
0/16BEBA0 | 503 | closing a streamed block for transaction TXN 503
(10 rows)
```
