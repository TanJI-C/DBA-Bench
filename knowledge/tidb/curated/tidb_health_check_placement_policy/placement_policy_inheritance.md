# TiDB v8.1 placement policy inheritance

This source is a version-bound operational summary for self-managed TiDB v8.1. A placement
policy is a reusable definition; attaching it to an object is a separate binding. The
database/default, table, and partition scopes must be inspected independently.

## Scope precedence

An object can inherit a database or global default when it has no object-level policy. A table
binding overrides that inherited value for the table and for partitions that do not have their
own binding. A partition binding is more specific than the table binding. `ALTER TABLE t
PLACEMENT POLICY=DEFAULT` removes the table-level override; it does not remove an explicit
partition binding. `ALTER TABLE t PARTITION p PLACEMENT POLICY=DEFAULT` removes only that
partition override. The SQL keyword `DEFAULT` means inheritance and is not the same thing as a
custom policy whose name happens to contain the word default.

## Observation

Use `information_schema.tables.TIDB_PLACEMENT_POLICY_NAME` for table bindings and
`information_schema.partitions.TIDB_PLACEMENT_POLICY_NAME` for partition bindings. Use
`SHOW CREATE TABLE` when the table DDL is ambiguous, and use `SHOW PLACEMENT` or `SHOW
PLACEMENT FOR TABLE` for the asynchronous placement state. A table row with a policy name is
not proof that all partitions use that name: the partition catalog is the authoritative check
for explicit partition overrides.
