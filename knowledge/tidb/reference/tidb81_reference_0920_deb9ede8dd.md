# Full-text search joins and support links

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-full-text-search-sql.md`
- Source Title: `Full-Text Search with SQL`
- Source Heading Path: `Full-Text Search with SQL > Advanced example: Join search results with other tables | Full-Text Search with SQL > See also | Full-Text Search with SQL > Feedback & help`
- Source Line Ranges: `155-220`
- Source Scope: `cloud`
- Primary Component: `sql`
- Related Components: `cloud`, `tidb`
- Topic Tags: `joins`, `subqueries`, `full-text search`, `author lookup`, `related links`, `support channels`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0920_deb9ede8dd`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-full-text-search-sql.md#advanced-example-join-search-results-with-other-tables`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `cdccdbe971a882858904c6e0318c1a1726467c6a892d6e1613eb198840e0c33d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-full-text-search-sql#advanced-example-join-search-results-with-other-tables
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-full-text-search-sql.md

## Retrieval Guidance

- Use When: Use this chunk when the user wants an example of combining full-text search with joins or subqueries, or needs the official feedback and help links for full-text search.
- Retrieval Keywords: Advanced example: Join search results with other tables, joins and subqueries, users table, tickets table, FULLTEXT INDEX (name) WITH PARSER STANDARD, SELECT t.title AS TICKET_TITLE, u.id AS AUTHOR_ID, u.name AS AUTHOR_NAME, LEFT JOIN users u ON t.author_id = u.id, WHERE t.author_id IN, SELECT id FROM users WHERE fts_match_word("Alice", name), Hybrid Search, Feedback & help, Join our Discord, Support Portal
- Follow-up Guidance: The page also points to Hybrid Search and provides Discord and Support Portal links for feedback or help.
- Classification Note: This is classified as a reference chunk because it gives an illustrative SQL join and subquery example plus related links and support channels rather than a primary setup procedure.

## Official Source Content

## Advanced example: Join search results with other tables

You can combine full-text search with other SQL features such as joins and subqueries.

Assume you have a `users` table and a `tickets` table, and want to find tickets created by authors based on a full-text search of their names:

```sql
CREATE TABLE users(
    id INT,
    name TEXT,
    FULLTEXT INDEX (name) WITH PARSER STANDARD
);

INSERT INTO users VALUES (1, "Alice Smith");
INSERT INTO users VALUES (2, "Bob Johnson");

CREATE TABLE tickets(
    id INT,
    title TEXT,
    author_id INT
);

INSERT INTO tickets VALUES (1, "Ticket 1", 1);
INSERT INTO tickets VALUES (2, "Ticket 2", 1);
INSERT INTO tickets VALUES (3, "Ticket 3", 2);
```

You can use a subquery to find matching user IDs based on the author's name, and then use these IDs in the outer query to retrieve and join related ticket information:

```sql
SELECT t.title AS TICKET_TITLE, u.id AS AUTHOR_ID, u.name AS AUTHOR_NAME FROM tickets t
LEFT JOIN users u ON t.author_id = u.id
WHERE t.author_id IN
(
    SELECT id FROM users
    WHERE fts_match_word("Alice", name)
);

+--------------+-----------+-------------+
| TICKET_TITLE | AUTHOR_ID | AUTHOR_NAME |
+--------------+-----------+-------------+
| Ticket 1     |         1 | Alice Smith |
| Ticket 2     |         1 | Alice Smith |
+--------------+-----------+-------------+
```
## See also

- [Hybrid Search](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-hybrid-search)
## Feedback & help

Full-text search is still in the early stages with limited accessibility. If you would like to try full-text search in a region that is not yet available, or if you have feedback or need help, feel free to reach out to us:

- [Join our Discord](https://discord.gg/zcqexutz2R)

- [Join our Discord](https://discord.gg/zcqexutz2R)
- [Visit our Support Portal](https://tidb.support.pingcap.com/)
