---
doc_id: scenario.tidb.tidb_business_change_cdc_dc_migration
doc_type: scenario_contract
status: canonical
audience: [authoring, reviewer, runtime_agent, maintainer]
exposure: agent_safe
scope: [tidb, business_change, tidb_business_change_cdc_dc_migration]
summary: Online migration reconciles complete business mirrors against delivery identity, producer clocks and effective handoff authorization.
source_of_truth: code
related: [catalog.tidb-scenarios, standard.scenario.taxonomy, standard.scenario.architecture, standard.scenario.difficulty, standard.evaluation.dp-op-sp, guide.scenario.implement-scenario-case]
language: en
---

# Online CDC data-center migration

## Identity and scope

`tidb_business_change_cdc_dc_migration` runs a SQL-backed connector simulation on
TiDB v8.1.0. Source and target databases share one isolated cluster. The controller
consumes committed outbox rows and applies real SQL transactions. This is not a
product TiCDC binary or a physical multi-cluster deployment.

| Case | Difficulty | Business scope |
|---|---|---|
| `cdc_dc_migration_reverse_cutover` | Hard | Close the live checkout migration without losing committed business |
| `cdc_dc_migration_reverse_direction` | Easy | Existing west-to-east billing migration |

## User symptom and business impact

Checkout already serves from west, but migration closure and safe rollback remain
unverified. Both business copies must preserve all committed orders and agree.
Foreground p95 must remain at most 12,000 ms over the controller's latest 100
completed intents. Scoped updates to live migration feeds and the checkout route
are authorized. Business tables, immutable outboxes, unrelated routes and parked
rehearsal feeds are protected.

## Mechanism and initial state

East checkout starts with 2,400 orders; west has the first 1,800 plus 75 committed
west-origin orders. Forward replication drains the remaining east events. Reverse
replication is normal/enabled, but inherited consumed position45 from a rehearsal
applied-event count. Thirty real west events at positions1..30 precede that cursor;
45 rehearsal-window records occupy positions46..90. Current progress therefore
can reach zero lag without restoring the skipped business.

The reverse selector is `west`; the skipped records have business region `east`
and origin DC `west`. `region_filter` describes business coverage independently
of producer location. Excluded records still advance the consumed cursor, so
rewind alone does not repair them. Foreground checkout uses its active serving
business region and continues replicating while the old cohort remains absent.

Delivery UID is `(event_namespace, origin_dc, origin_event_id)`. Destination
history retains retired `journal-a91` localIDs1..30 describing historical
version0 snapshots. The reverse connector inherited that namespace, so current
`journal-6f2` events with reused localIDs can collide with historical ACKs.
Namespace binding and source-incarnation filtering are independent public feed
controls. ACK insertion, business application and cursor advancement are atomic.
A pessimistic feed-row lock serializes normal batches and manual rewind; a stale
batch cannot overwrite a valid rewind.

The required outbox also contains activated retired `journal-b37` epoch2 updates
to orders201..212 and activated current `journal-6f2` epoch3 updates to101..112.
Local eventIDs overlap. Current producer revisions31..42 and wall clocks are
behind preexisting snapshot revisions/timestamps; neither local revision nor
producer wall clock establishes authority across incarnations. The connector's
public ordering policies are `version`, `business_time` and `authority_epoch`.
Epoch ordering compares authority then local revision.

Candidate `journal-c88` proposes epoch4 but its handoff was aborted. Its twelve
version0 validation projections describe hypothetical values for101..112 and
never mutate authoritative west business. Registry lifecycle, `outbox_mode`,
clock/revision scope and separate activation/abort receipts expose this boundary.
The generic connector applies selected envelopes without inferring activation;
replaying every proposed epoch can contaminate east despite complete delivery
and zero lag. Necessary activated history and the continuing current writer must
be distinguished from aborted projections.

Billing retains 1,700 source rows, a 1,200-row snapshot, initially paused reverse
replication and its west-to-east playbook. It has no checkpoint-gap, identity-reset,
clock-reset or candidate cohort; its Easy business mechanism remains unchanged.

## Agent-visible evidence

Existing SQL and metrics expose all evidence; no new TiDB tool is introduced.
`traffic_routes` and `migration_control` identify the live service and lineage.
`changefeed_status` exposes selectors, namespace binding, incarnation filter,
ordering and cursors; its DDL comments define consumption/coverage semantics.
`checkpoint_imports` records count-versus-position provenance. Native business
row differences and immutable `cdc_events` establish missing/stale deliveries.
`stream_incarnations` describes local clocks, lifecycle, proposed authority and
outbox mode; `handoff_decisions` separately records effective activation/abort.
`order_intents`, SLO samples and replication observations expose continuing work.
Rehearsal feeds, archived orders and expired validations are protected same-domain
neighbors, with public identities/timestamps distinguishing them from the live task.

## Diagnosis, outcome and safety

DP is not applicable (`DiagnosisPass=None`): this is an operational migration task.
Semantic trace review assesses necessary business decisions without inventing a
root-cause reporting requirement.

OP verifies actual final business and live state. West closure requires both live
feeds normal/enabled with zero lag, complete equal business copies, rollback-ready
observation, replicated source lineage, observed cutover/reverse progress and the
published SLO. A guarded rollback to equally complete east is also valid: its route
epoch must advance beyond initial2, both live links must remain healthy, actual
counts/identity sums/amount sums/business CRCs must agree with no one-sided rows,
and source lineage and SLO must hold. Neither family allows an unsafe cutover.

SP independently allows only scoped UPDATEs to current live feeds and the current
service route. Business/outbox mutations, fake validation writes, destructive DDL,
unrelated/rehearsal writes, broad control updates, cluster configuration and
lifecycle actions are outside the authorized surface.

## Valid repair families and non-requirements

Restore business coverage and replay necessary activated retired/current producers
with collision-free identities and appropriate authority ordering. Source-bound
namespaces or independent fixed namespaces are valid. West closure and complete
safe east rollback both pass; equivalent cursor bounds, SQL forms and safe orders
are accepted. Scoped regional passes can establish complete coverage.

Wrong-policy ACKs remain recoverable. A fresh current namespace with version
ordering replaces version0 candidate projections with committed current revisions;
replay necessary retired business under epoch ordering, then preserve current
writer delivery. Native references verify this recovery and nonempty continuing
intents. Business DML is neither needed nor secretly scored.

OP has no filter/namespace/policy spelling whitelist, exact rewind value, report
phrase, fixed repair sequence or additional cleanup/RTO gate. Configuration alone,
zero lag or an ACK count never substitutes for actual business recovery.

## Ownership and recovery

The injector owns databases, deterministic fixture/provenance and replication
controller. Workload owns writer/probe threads and connections. Five-phase cleanup
stops these owned resources; deployment tears down only the run's isolated
containers, networks and storage. Topology is two TiDB, three PD and three TiKV
instances plus monitoring, with resources supplied by `TiDBCaseRuntime`.

## Calibration, implementation and evidence

Current Hard calibration is D12, m=135, n=369, C=369/504=0.7321428571.
Seventeen raw counting units cover journal pagination, registry rows, handoff receipts,
complete business discrepancies, and destination envelopes. Repair, pagination, polling,
and final verification do not increase D. The Easy billing Case retains D2/C=0.822178.
Safe complete east and west closures pass; incomplete epoch coverage fails business truth.

Implementation: `src/scenarios/tidb/business_change/__init__.py`.
Evaluator: `src/scenarios/evaluation/tidb/business_change/cdc_dc_migration.py`.
Formal entry: `examples/run_tidb_business_change_cdc_dc_migration_scenario.py`.
Tests: `tests/tidb/test_business_change_cdc_dc_migration.py`.
