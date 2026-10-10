# Architecture

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/16_logical_replication.md`
- Source Title: `Logical Replication`
- Source Heading Path: `Logical Replication > Architecture`
- Source Line Ranges: `1333-1394`
- Chunk ID: `pg16_fact_0067_02f279cfd6`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `eda5501885de439352360605228494fdd4e92196e716a126fc76b11739a719c8`

## Retrieval Guidance

- Use When: 需要理解 logical replication 的进程、协议和变更应用路径。
- Retrieval Keywords: logical replication architecture, walsender, apply worker, logical decoding, pgoutput, session_replication_role
- Follow-up Guidance: 触发器/规则行为异常时检查 ENABLE TRIGGER/RULE 和 session_replication_role。
- Classification Note: 解释 walsender、logical decoding、pgoutput、apply worker 和 trigger 行为。

## Official Source Content

## Architecture

Logical replication starts by copying a snapshot of the data on the
publisher database.  Once that is done, changes on the publisher are sent
to the subscriber as they occur in real time.  The subscriber applies data
in the order in which commits were made on the publisher so that
transactional consistency is guaranteed for the publications within any
single subscription.

Logical replication is built with an architecture similar to physical
streaming replication (see [streaming-replication](#streaming-replication)).  It is
implemented by `walsender` and `apply`
processes.  The walsender process starts logical decoding (described
in [logicaldecoding](#logicaldecoding)) of the WAL and loads the standard
logical decoding output plugin (`pgoutput`).  The plugin
transforms the changes read
from WAL to the logical replication protocol
(see [protocol-logical-replication](#protocol-logical-replication)) and filters the data
according to the publication specification.  The data is then continuously
transferred using the streaming replication protocol to the apply worker,
which maps the data to local tables and applies the individual changes as
they are received, in correct transactional order.

The apply process on the subscriber database always runs with
[`session_replication_role`](#guc-session-replication-role)
set to `replica`. This means that, by default,
triggers and rules will not fire on a subscriber. Users can optionally choose to
enable triggers and rules on a table using the
[`ALTER TABLE`](#sql-altertable) command
and the `ENABLE TRIGGER` and `ENABLE RULE`
clauses.

The logical replication apply process currently only fires row triggers,
not statement triggers.  The initial table synchronization, however, is
implemented like a `COPY` command and thus fires both row
and statement triggers for `INSERT`.

### Initial Snapshot

The initial data in existing subscribed tables is snapshotted and
copied in a parallel instance of a special kind of apply process.
This process will create its own replication slot and copy the existing
data.  As soon as the copy is finished the table contents will become
visible to other backends.  Once existing data is copied, the worker
enters synchronization mode, which ensures that the table is brought
up to a synchronized state with the main apply process by streaming
any changes that happened during the initial data copy using standard
logical replication.  During this synchronization phase, the changes
are applied and committed in the same order as they happened on the
publisher.  Once synchronization is done, control of the
replication of the table is given back to the main apply process where
replication continues as normal.

> **Note:**

> The publication
> [`publish`](#sql-createpublication-with-publish)
> parameter only affects what DML operations will be replicated. The
> initial data synchronization does not take this parameter into account
> when copying the existing table data.
>
