# DROP SUBSCRIPTION

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/drop_subscription.md`
- Source Title: `drop subscription`
- Source Heading Path: `Part VI Reference > SQL Commands > DROP SUBSCRIPTION`
- Source Line Ranges: `1-75`
- Chunk ID: `pg16_fact_0289_eac0a83231`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `48f48f434b37e5d27da89ccbd23a8b946493c4a1e9239ea7e8529e4058bc368d`

## Retrieval Guidance

- Use When: Use for subscription drop syntax and slot behavior.
- Retrieval Keywords: DROP SUBSCRIPTION, logical replication subscription, replication slot
- Follow-up Guidance: Verify remote slot implications before operational use.
- Classification Note: Logical replication subscription removal syntax reference.

## Official Source Content

DROP SUBSCRIPTION
7
SQL - Language Statements

DROP SUBSCRIPTION
remove a subscription

```
DROP SUBSCRIPTION [ IF EXISTS ] `name` [ CASCADE | RESTRICT ]
```

## Description

`DROP SUBSCRIPTION` removes a subscription from the
database cluster.

To execute this command the user must be the owner of the subscription.

`DROP SUBSCRIPTION` cannot be executed inside a
transaction block if the subscription is associated with a replication
slot.  (You can use `ALTER SUBSCRIPTION` to unset the
slot.)

## Parameters

**`IF EXISTS`**
: Do not throw an error if the subscription does not exist. A notice is
issued in this case.

**`name`**
: The name of a subscription to be dropped.

**`CASCADE`**
: These key words do not have any effect, since there are no dependencies
on subscriptions.

## Notes

When dropping a subscription that is associated with a replication slot on
the remote host (the normal state), `DROP SUBSCRIPTION`
will connect to the remote host and try to drop the replication slot (and
any remaining table synchronization slots) as
part of its operation.  This is necessary so that the resources allocated
for the subscription on the remote host are released.  If this fails,
either because the remote host is not reachable or because the remote
replication slot cannot be dropped or does not exist or never existed,
the `DROP SUBSCRIPTION` command will fail.  To proceed
in this situation, first disable the subscription by executing
`ALTER SUBSCRIPTION ... DISABLE`, and then disassociate
it from the replication slot by executing
`ALTER SUBSCRIPTION ... SET (slot_name = NONE)`.
After that, `DROP SUBSCRIPTION` will no longer attempt any
actions on a remote host.  Note that if the remote replication slot still
exists, it (and any related table synchronization slots) should then be
dropped manually; otherwise it/they will continue to
reserve WAL and might eventually cause the disk to fill up.  See
also [logical-replication-subscription-slot](#logical-replication-subscription-slot).

If a subscription is associated with a replication slot, then `DROP
SUBSCRIPTION` cannot be executed inside a transaction block.

## Examples

Drop a subscription:

```
DROP SUBSCRIPTION mysub;
```

## Compatibility

`DROP SUBSCRIPTION` is a PostgreSQL
extension.

## See Also
