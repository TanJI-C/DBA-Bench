# Overview; Implementation; WAL; Limitations

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVII_internals/21_hash_indexes.md`
- Source Title: `Hash Indexes`
- Source Heading Path: `Hash Indexes > Overview; Implementation; WAL; Limitations`
- Source Line Ranges: `80-113`
- Chunk ID: `pg16_fact_0115_ced5bbb173`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `61c94861d86c04fb89eb500c2b6648b84c9e41164cd33ab5b7352c0bc4db98dc`

## Retrieval Guidance

- Use When: Understand PostgreSQL hash index internals.
- Retrieval Keywords: hash index, bucket, overflow page, hash metapage, hash index WAL
- Follow-up Guidance: Use access-method records for generic index callback details.
- Classification Note: The chapter documents PostgreSQL hash index behavior and implementation details.

## Official Source Content

## Implementation

There are four kinds of pages in a hash index: the meta page (page zero),
which contains statically allocated control information; primary bucket
pages; overflow pages; and bitmap pages, which keep track of overflow
pages that have been freed and are available for re-use. For addressing
purposes, bitmap pages are regarded as a subset of the overflow pages.

Both scanning the index and inserting tuples require locating the bucket
where a given tuple ought to be located. To do this, we need the bucket
count, highmask, and lowmask from the metapage; however, it's undesirable
for performance reasons to have to lock and pin the metapage for every such
operation. Instead, we retain a cached copy of the metapage in each
backend's relcache entry. This will produce the correct bucket mapping as
long as the target bucket hasn't been split since the last cache refresh.

Primary bucket pages and overflow pages are allocated independently since
any given index might need more or fewer overflow pages relative to its
number of buckets. The hash code uses an interesting set of addressing
rules to support a variable number of overflow pages while not having to
move primary bucket pages around after they are created.

Each row in the table indexed is represented by a single index tuple in
the hash index. Hash index tuples are stored in bucket pages, and if
they exist, overflow pages. We speed up searches by keeping the index entries
in any one index page sorted by hash code, thus allowing binary search to be
used within an index page. Note however that there is *no* assumption about
the relative ordering of hash codes across different index pages of a bucket.

The bucket splitting algorithms to expand the hash index are too complex to
be worthy of mention here, though are described in more detail in
`src/backend/access/hash/README`.
The split algorithm is crash safe and can be restarted if not completed
successfully.
