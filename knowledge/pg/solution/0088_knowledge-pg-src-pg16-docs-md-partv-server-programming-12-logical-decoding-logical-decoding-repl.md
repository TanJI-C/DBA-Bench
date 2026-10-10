# slot persistence, catalog_xmin, restart_lsn, dropping unused slots

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/12_logical_decoding.md`
- Source Title: `Logical Decoding`
- Source Heading Path: `Logical Decoding > Replication Slots > slot persistence, catalog_xmin, restart_lsn, dropping unused slots`
- Source Line Ranges: `232-308`
- Chunk ID: `pg16_solution_0088_0f26f25989`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4145e39941929df77bf3522a240b900078740fdb0fe8352a3144dddded8449f5`

## Retrieval Guidance

- Use When: Remediate confirmed WAL or catalog bloat caused by an inactive logical replication slot.
- Retrieval Keywords: replication slot WAL retention, restart_lsn, catalog_xmin, pg_drop_replication_slot, unused logical slot, disk full WAL
- Follow-up Guidance: Check replication consumer state before dropping a slot because data loss for that consumer may result.
- Classification Note: The slot sections describe confirmed consequences of unused slots retaining WAL/catalog state and the corrective action of consuming or dropping slots.

## Official Source Content

### Replication Slots

In the context of logical replication, a slot represents a stream of
changes that can be replayed to a client in the order they were made on
the origin server. Each slot streams a sequence of changes from a single
database.

> **Note:**
PostgreSQL also has streaming replication slots
> (see [streaming-replication](#streaming-replication)), but they are used somewhat
> differently there.
>

A replication slot has an identifier that is unique across all databases
in a PostgreSQL cluster. Slots persist
independently of the connection using them and are crash-safe.

A logical slot will emit each change just once in normal operation.
The current position of each slot is persisted only at checkpoint, so in
the case of a crash the slot may return to an earlier LSN, which will
then cause recent changes to be sent again when the server restarts.
Logical decoding clients are responsible for avoiding ill effects from
handling the same message more than once.  Clients may wish to record
the last LSN they saw when decoding and skip over any repeated data or
(when using the replication protocol) request that decoding start from
that LSN rather than letting the server determine the start point.
The Replication Progress Tracking feature is designed for this purpose,
refer to [replication origins](#replication-origins).

Multiple independent slots may exist for a single database. Each slot has
its own state, allowing different consumers to receive changes from
different points in the database change stream. For most applications, a
separate slot will be required for each consumer.

A logical replication slot knows nothing about the state of the
receiver(s).  It's even possible to have multiple different receivers using
the same slot at different times; they'll just get the changes following
on from when the last receiver stopped consuming them. Only one receiver
may consume changes from a slot at any given time.

A logical replication slot can also be created on a hot standby. To prevent
`VACUUM` from removing required rows from the system
catalogs, `hot_standby_feedback` should be set on the
standby. In spite of that, if any required rows get removed, the slot gets
invalidated. It's highly recommended to use a physical slot between the
primary and the standby. Otherwise, `hot_standby_feedback`
will work but only while the connection is alive (for example a node
restart would break it). Then, the primary may delete system catalog rows
that could be needed by the logical decoding on the standby (as it does
not know about the catalog_xmin on the standby). Existing logical slots
on standby also get invalidated if `wal_level` on the
primary is reduced to less than `logical`.
This is done as soon as the standby detects such a change in the WAL stream.
It means that, for walsenders which are lagging (if any), some WAL records up
to the `wal_level` parameter change on the primary won't be
decoded.

Creation of a logical slot requires information about all the currently
running transactions. On the primary, this information is available
directly, but on a standby, this information has to be obtained from
primary. Thus, slot creation may need to wait for some activity to happen
on the primary. If the primary is idle, creating a logical slot on
standby may take noticeable time. This can be sped up by calling the
`pg_log_standby_snapshot` function on the primary.

> **Caution:**

> Replication slots persist across crashes and know nothing about the state
> of their consumer(s). They will prevent removal of required resources
> even when there is no connection using them. This consumes storage
> because neither required WAL nor required rows from the system catalogs
> can be removed by `VACUUM` as long as they are required by a replication
> slot.  In extreme cases this could cause the database to shut down to prevent
> transaction ID wraparound (see [vacuum-for-wraparound](#vacuum-for-wraparound)).
> So if a slot is no longer required it should be dropped.
>
