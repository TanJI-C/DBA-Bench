# GIN Fast Update Technique; GIN Tips and Tricks

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVII_internals/19_gin_indexes.md`
- Source Title: `GIN Indexes`
- Source Heading Path: `GIN Indexes > GIN Fast Update Technique; GIN Tips and Tricks`
- Source Line Ranges: `331-362, 378-439`
- Chunk ID: `pg16_guide_0052_2a2acaffcf`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `606376417bd297b16cc08d9d47dcb86a1b1d662d23ebb3b077c89db1e969acbe`

## Retrieval Guidance

- Use When: Diagnose GIN insert latency, pending-list effects, or GIN query/index maintenance behavior.
- Retrieval Keywords: GIN fastupdate, GIN pending list, gin_pending_list_limit, slow GIN insert, GIN tips, VACUUM GIN
- Follow-up Guidance: Confirm relation options and pending-list size before changing storage parameters or scheduling maintenance.
- Classification Note: These sections describe pending-list behavior, fast update tradeoffs, and usage tips that help confirm GIN-related performance symptoms.

## Official Source Content

### GIN Fast Update Technique

Updating a GIN index tends to be slow because of the
intrinsic nature of inverted indexes: inserting or updating one heap row
can cause many inserts into the index (one for each key extracted
from the indexed item).
GIN is capable of postponing much of this work by inserting
new tuples into a temporary, unsorted list of pending entries.
When the table is vacuumed or autoanalyzed, or when
`gin_clean_pending_list` function is called, or if the
pending list becomes larger than
[guc-gin-pending-list-limit](#guc-gin-pending-list-limit), the entries are moved to the
main GIN data structure using the same bulk insert
techniques used during initial index creation.  This greatly improves
GIN index update speed, even counting the additional
vacuum overhead.  Moreover the overhead work can be done by a background
process instead of in foreground query processing.

The main disadvantage of this approach is that searches must scan the list
of pending entries in addition to searching the regular index, and so
a large list of pending entries will slow searches significantly.
Another disadvantage is that, while most updates are fast, an update
that causes the pending list to become "too large" will incur an
immediate cleanup cycle and thus be much slower than other updates.
Proper use of autovacuum can minimize both of these problems.

If consistent response time is more important than update speed,
use of pending entries can be disabled by turning off the
`fastupdate` storage parameter for a
GIN index.  See [sql-createindex](#sql-createindex)
for details.

## GIN Tips and Tricks

**Create vs. insert**
: Insertion into a GIN index can be slow
due to the likelihood of many keys being inserted for each item.
So, for bulk insertions into a table it is advisable to drop the GIN
index and recreate it after finishing bulk insertion.

When `fastupdate` is enabled for GIN
(see [gin-fast-update](#gin-fast-update) for details), the penalty is
less than when it is not.  But for very large updates it may still be
best to drop and recreate the index.

**[guc-maintenance-work-mem](#guc-maintenance-work-mem)**
: Build time for a GIN index is very sensitive to
the `maintenance_work_mem` setting; it doesn't pay to
skimp on work memory during index creation.

**[guc-gin-pending-list-limit](#guc-gin-pending-list-limit)**
: During a series of insertions into an existing GIN
index that has `fastupdate` enabled, the system will clean up
the pending-entry list whenever the list grows larger than
`gin_pending_list_limit`. To avoid fluctuations in observed
response time, it's desirable to have pending-list cleanup occur in the
background (i.e., via autovacuum).  Foreground cleanup operations
can be avoided by increasing `gin_pending_list_limit`
or making autovacuum more aggressive.
However, enlarging the threshold of the cleanup operation means that
if a foreground cleanup does occur, it will take even longer.

`gin_pending_list_limit` can be overridden for individual
GIN indexes by changing storage parameters, which allows each
GIN index to have its own cleanup threshold.
For example, it's possible to increase the threshold only for the GIN
index which can be updated heavily, and decrease it otherwise.

**[guc-gin-fuzzy-search-limit](#guc-gin-fuzzy-search-limit)**
: The primary goal of developing GIN indexes was
to create support for highly scalable full-text search in
PostgreSQL, and there are often situations when
a full-text search returns a very large set of results.  Moreover, this
often happens when the query contains very frequent words, so that the
large result set is not even useful.  Since reading many
tuples from the disk and sorting them could take a lot of time, this is
unacceptable for production.  (Note that the index search itself is very
fast.)

To facilitate controlled execution of such queries,
GIN has a configurable soft upper limit on the
number of rows returned: the
`gin_fuzzy_search_limit` configuration parameter.
It is set to 0 (meaning no limit) by default.
If a non-zero limit is set, then the returned set is a subset of
the whole result set, chosen at random.

"Soft" means that the actual number of returned results
could differ somewhat from the specified limit, depending on the query
and the quality of the system's random number generator.

From experience, values in the thousands (e.g., 5000 — 20000)
work well.
