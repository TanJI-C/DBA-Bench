# Index Storage Parameters

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/create_index.md`
- Source Title: `create index`
- Source Heading Path: `Part VI Reference > SQL Commands > CREATE INDEX > Index Storage Parameters`
- Source Line Ranges: `211-315`
- Chunk ID: `pg16_configuration_0216_964747331f`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `37b5ad5ba762ffe56ad21276970488b23ab7314c21607933a453a1565a7eba3f`

## Retrieval Guidance

- Use When: Use when tuning physical index storage while creating an index.
- Retrieval Keywords: CREATE INDEX WITH, Index Storage Parameters, fillfactor, deduplicate_items, index reloptions
- Follow-up Guidance: Verify parameter support for chosen index method and consider maintenance cost.
- Classification Note: Index storage parameters configure physical/index-method behavior such as fillfactor or deduplication.

## Official Source Content

### Index Storage Parameters

The optional `WITH` clause specifies *storage
parameters* for the index.  Each index method has its own set of allowed
storage parameters.  The B-tree, hash, GiST and SP-GiST index methods all
accept this parameter:

**`fillfactor` (`integer`)**
: The fillfactor for an index is a percentage that determines how full
the index method will try to pack index pages.  For B-trees, leaf pages
are filled to this percentage during initial index builds, and also
when extending the index at the right (adding new largest key values).
If pages
subsequently become completely full, they will be split, leading to
fragmentation of the on-disk index structure.  B-trees use a default
fillfactor of 90, but any integer value from 10 to 100 can be selected.

B-tree indexes on tables where many inserts and/or updates are
anticipated can benefit from lower fillfactor settings at
`CREATE INDEX` time (following bulk loading into the
table).  Values in the range of 50 - 90 can usefully "smooth
out" the *rate* of page splits during the
early life of the B-tree index (lowering fillfactor like this may even
lower the absolute number of page splits, though this effect is highly
workload dependent).  The B-tree bottom-up index deletion technique
described in [btree-deletion](#btree-deletion) is dependent on having
some "extra" space on pages to store "extra"
tuple versions, and so can be affected by fillfactor (though the effect
is usually not significant).

In other specific cases it might be useful to increase fillfactor to
100 at `CREATE INDEX` time as a way of maximizing
space utilization.  You should only consider this when you are
completely sure that the table is static (i.e. that it will never be
affected by either inserts or updates).  A fillfactor setting of 100
otherwise risks *harming* performance: even a few
updates or inserts will cause a sudden flood of page splits.

The other index methods use fillfactor in different but roughly
analogous ways; the default fillfactor varies between methods.

B-tree indexes additionally accept this parameter:

**`deduplicate_items` (`boolean`)**
: Controls usage of the B-tree deduplication technique described
in [btree-deduplication](#btree-deduplication).  Set to
`ON` or `OFF` to enable or
disable the optimization.  (Alternative spellings of
`ON` and `OFF` are allowed as
described in [config-setting](#config-setting).) The default is
`ON`.

> **Note:**
> Turning `deduplicate_items` off via
> `ALTER INDEX` prevents future insertions from
> triggering deduplication, but does not in itself make existing
> posting list tuples use the standard tuple representation.
>

GiST indexes additionally accept this parameter:

**`buffering` (`enum`)**
: Determines whether the buffered build technique described in
[gist-buffering-build](#gist-buffering-build) is used to build the index. With
`OFF` buffering is disabled, with `ON`
it is enabled, and with `AUTO` it is initially disabled,
but is turned on on-the-fly once the index size reaches
[guc-effective-cache-size](#guc-effective-cache-size).  The default
is `AUTO`.
Note that if sorted build is possible, it will be used instead of
buffered build unless `buffering=ON` is specified.

GIN indexes accept different parameters:

**`fastupdate` (`boolean`)**
: This setting controls usage of the fast update technique described in
[gin-fast-update](#gin-fast-update).  It is a Boolean parameter:
`ON` enables fast update, `OFF` disables it.
The default is `ON`.

> **Note:**
> Turning `fastupdate` off via `ALTER INDEX` prevents
> future insertions from going into the list of pending index entries,
> but does not in itself flush previous entries.  You might want to
> `VACUUM` the table or call `gin_clean_pending_list`
> function afterward to ensure the pending list is emptied.
>

**`gin_pending_list_limit` (`integer`)**
: Custom [guc-gin-pending-list-limit](#guc-gin-pending-list-limit) parameter.
This value is specified in kilobytes.

BRIN indexes accept different parameters:

**`pages_per_range` (`integer`)**
: Defines the number of table blocks that make up one block range for
each entry of a BRIN index (see [brin-intro](#brin-intro)
for more details).  The default is `128`.

**`autosummarize` (`boolean`)**
: Defines whether a summarization run is queued for the previous page
range whenever an insertion is detected on the next one.
See [brin-operation](#brin-operation) for more details.
The default is `off`.
