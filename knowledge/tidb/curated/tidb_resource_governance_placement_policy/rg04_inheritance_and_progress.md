# TiDB v8.1 placement inheritance and asynchronous progress

## Scope precedence

Database or global defaults are inherited only when an object has no more-specific binding. A table
binding overrides the inherited value, and an explicit partition binding overrides the table. A
table-level `PLACEMENT POLICY=DEFAULT` removes the table override; it does not remove an explicit
partition override. Inspect `INFORMATION_SCHEMA.TABLES`,
`INFORMATION_SCHEMA.PARTITIONS`, and `SHOW CREATE TABLE` when attachment scope is ambiguous.

## Admission is not convergence

Placement changes are scheduled asynchronously by PD. A successful `CREATE PLACEMENT POLICY` or
`ALTER TABLE ... PLACEMENT POLICY` is only an admission event. `SHOW PLACEMENT` reports object
states such as `PENDING`, `INPROGRESS`, and `SCHEDULED`; a policy-definition row can have no object
state. Re-read the target object after waiting and use Region peers and operator state to establish
physical completion.

An accepted rule can remain unsatisfied when the requested followers, label domains, or fault-domain
survival objective exceed healthy TiKV Store capacity. A pending or in-progress neighbor is not proof
that the target is the same object or that the target repair is complete.

