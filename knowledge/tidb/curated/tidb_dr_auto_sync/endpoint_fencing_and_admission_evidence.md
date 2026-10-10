# Endpoint fencing and business admission evidence

A failover operation must prevent an old SQL writer from becoming a second
writer. For an orderly exchange, use the distributing router policy, drain the
old backend, and observe zero active connections before submitting the product
role exchange. For an outage, a stopped SQL endpoint is not by itself an
application fence; apply and verify the route fence before promoting the
surviving side.

A product request that is accepted, a changed PD Leader, a healthy SQL
connection, or a short-lived liveness result is only an intermediate
observation. The operation must expose a terminal product state, and the
surviving endpoint still needs a bounded write/read-back probe.

When an application admits writes after an outage, an explicit handoff record
can bind the pre-outage acknowledged business boundary to the surviving
endpoint. The record should use the public business invariants, such as
acknowledged marker count, amount total, and checksum, together with the
observed route-fence generation and failover mode. It is an application
admission artifact, not a replacement for product terminal state, Region
validation, data/index checks, or the bounded canary.

A TSO comparison is not an RPO proof. The acknowledged boundary, the observed
fence, the terminal replication state, the business truth, and the canary must
be checked as separate facts. Use the current schema and router state to bind
the general rule to the current endpoint and business object; do not copy an
identifier or boundary from another run.

