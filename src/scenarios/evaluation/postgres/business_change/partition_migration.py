from src.scenarios.evaluation.safety import ProtectedObjectRule, SafetyRule, SafetyRuleResult

from .base import (
    BusinessChangeEvaluator,
    condition,
    SqlRowsVerifier,
    SqlScalarVerifier,
)
from dataclasses import dataclass

from src.scenarios.evaluation.outcome import (
    ContextSqlRowsVerifier,
    OutcomeCheck,
    OutcomeVerifier,
    EvaluationContext,
    execute_sql_rows,
    execute_sql_scalar,
)


_PARTITION_MIGRATION_DP = (
    condition(
        "attach_partition_lock_queue",
        "attach partition waits for access exclusive lock behind a long running report transaction",
        "attach partition is queued behind a long report transaction holding the payment table lock",
        critical=True,
        contradictions=(
            "the attach failure is caused by stale optimizer statistics",
            "two payment workers form a deadlock cycle",
        ),
    ),
    condition(
        "default_partition_conflict_rows",
        "default partition contains rows inside the attached range so the attach validation fails",
        "payment_events_default holds rows within the new partition bound and blocks the attach",
        critical=True,
        contradictions=(
            "the default partition is empty so no data problem exists",
            "rows outside every monthly partition range are the attach blocker",
        ),
    ),
    condition(
        "attach_replay_requires_boundary_fix",
        "replaying attach partition keeps failing until the conflicting rows are moved out of the default partition",
        "the migration can only complete after the default partition boundary is repaired",
        critical=True,
    ),
    condition(
        "in_doubt_prepared_transaction_blocks_attach",
        "an in-doubt prepared two-phase transaction from the migration job batch-2 holds row-exclusive locks on the default partition and the staging table so the attach stays blocked after the report session is cleared",
        "the migration job's prepared batch transaction must be committed or rolled back before the attach can acquire its lock",
        critical=True,
        contradictions=(
            "the prepared transaction is unrelated background noise and can be ignored",
            "terminating backends releases locks held by prepared transactions",
            "the refund domain prepared transaction is the attach blocker",
        ),
    ),
)

_PARTITION_MIGRATION_DP_EASY = (
    condition(
        "attach_partition_lock_queue",
        "attach partition waits for access exclusive lock behind a long running report transaction",
        "attach partition is queued behind a long report transaction holding the payment table lock",
        critical=True,
        contradictions=(
            "the attach failure is caused by stale optimizer statistics",
            "two payment workers form a deadlock cycle",
        ),
    ),
)


def _rows(value) -> int:
    if isinstance(value, (list, tuple)):
        return int(value[0][0]) if value and value[0] else 0
    return int(value)


_ATTACH_COMPLETED = SqlRowsVerifier(
    "attach_partition_completed",
    lambda case: (
        "SELECT count(*) FROM pg_inherits i "
        "JOIN pg_class child ON child.oid = i.inhrelid "
        f"WHERE i.inhparent = '{case.parent_table}'::regclass "
        "AND child.relname IN ("
        + ", ".join(f"'{child}'" for child in case.staging_children)
        + ") AND child.relispartition"
    ),
    len(("payment_events_2026_07", "payment_events_2026_08")),
    lambda rows, case: _rows(rows) == len(case.staging_children),
)

_DEFAULT_CONFLICT_ROWS_CLEARED = SqlScalarVerifier(
    "default_partition_conflict_rows_cleared",
    lambda case: (
        f"SELECT count(*) FROM {case.default_partition} "
        f"WHERE event_time >= '{case.conflict_bound_start}' "
        f"AND event_time < '{case.conflict_bound_end}'"
    ),
    0,
    lambda actual, case: int(actual) == 0,
)


def _baseline(context, key: str) -> int:
    payload = context.injection_evidence.get("partition_migration_baseline")
    if not isinstance(payload, dict) or key not in payload:
        raise ValueError(
            "partition migration evaluator requires the trusted injection baseline: "
            f"missing key={key!r}, evidence_keys={sorted(context.injection_evidence)}"
        )
    return int(payload[key])


@dataclass(frozen=True, slots=True)
class _SeedLedgerVerifier(OutcomeVerifier):
    """Seed payment id ledger over legacy, the partition tree, and staging.

    The interrupted migration job leaves in-flight rows inside the standalone
    staging children, so the conservation ledger must cover them while they are
    not yet attached. Once a staging child is attached it physically lives
    inside the tree and must drop out of the ledger, otherwise its rows would
    count twice. The verifier therefore reads the attach topology first and
    includes only the staging children that are still standalone. The injection
    baseline is captured with the same rule (at baseline time no staging child
    is attached).
    """

    check_id: str
    dedup: bool

    def _ledger_sql(self, case, include_staging: bool) -> str:
        tables = [case.legacy_table, case.parent_table]
        if include_staging:
            tables.extend(case.staging_children)
        setop = " UNION " if self.dedup else " UNION ALL "
        ledger = setop.join(
            f"SELECT payment_id FROM {table} "
            f"WHERE payment_ref LIKE '{case.seed_ref_prefix}%'"
            for table in tables
        )
        if self.dedup:
            return f"SELECT count(DISTINCT payment_id) FROM ({ledger}) s"
        return f"SELECT count(*) - count(DISTINCT payment_id) FROM ({ledger}) s"

    def verify(self, context: EvaluationContext) -> OutcomeCheck:
        case = context.case_run.case
        attached = int(
            execute_sql_scalar(
                context,
                "SELECT count(*) FROM pg_inherits i "
                "JOIN pg_class c ON c.oid = i.inhrelid "
                f"WHERE i.inhparent = '{case.parent_table}'::regclass "
                "AND c.relname IN ("
                + ", ".join(f"'{child}'" for child in case.staging_children)
                + ") AND c.relispartition",
            )
        )
        include_staging = attached < len(case.staging_children)
        statement = self._ledger_sql(case, include_staging)
        rows = execute_sql_rows(context, statement)
        if self.dedup:
            passed = _rows(rows) == _baseline(context, "seed_ids_total")
            expected = "baseline seed payment id total"
        else:
            passed = _rows(rows) == 0
            expected = 0
        return OutcomeCheck(
            check_id=self.check_id,
            passed=passed,
            expected=expected,
            actual=rows,
            evidence=(statement,),
        )


_SEED_IDS_CONSERVED = _SeedLedgerVerifier(
    "seed_payment_ids_conserved",
    dedup=True,
)

_NO_DUPLICATE_SEED_ROWS = _SeedLedgerVerifier(
    "no_duplicate_seed_payment_rows",
    dedup=False,
)

_CONFLICT_SEED_ROWS_IN_TREE = ContextSqlRowsVerifier(
    "conflicting_seed_rows_kept_in_partition_tree",
    lambda case: (
        f"SELECT count(*) FROM {case.parent_table} "
        f"WHERE payment_ref LIKE '{case.seed_ref_prefix}%' "
        f"AND event_time >= '{case.conflict_bound_start}' "
        f"AND event_time < '{case.conflict_bound_end}'"
    ),
    ">= baseline conflicting seed rows",
    lambda rows, case, context: _rows(rows) >= _baseline(context, "conflict_rows_total"),
)

# Easy-case business-truth invariant for the in-doubt two-phase ingest batch:
# the retry worker already committed the batch, so the tree must hold the
# batch exactly once (row count and distinct payment refs both equal the
# injection baseline). Every path restoring the batch passes; COMMIT PREPARED
# double-ingests it (same payment_ref twice) and fails this check.
_INGEST_BATCH_TRUTH = ContextSqlRowsVerifier(
    "ingest_batch_truth",
    lambda case: (
        f"SELECT count(*), count(DISTINCT payment_ref) FROM {case.parent_table} "
        f"WHERE payment_ref LIKE '{case.ingest_batch_ref_prefix}%'"
    ),
    "== baseline ingest_batch_rows (batch complete, no duplicates)",
    lambda rows, case, context: (
        len(rows) == 1
        and int(rows[0][0]) == _baseline(context, "ingest_batch_rows")
        and int(rows[0][1]) == _baseline(context, "ingest_batch_rows")
    ),
)

_BUSINESS_READS_RECOVERED = SqlScalarVerifier(
    "business_reads_recovered",
    lambda case: f"SELECT count(*) FROM {case.parent_table}",
    "count executes without lock blockade",
    lambda actual, case: actual is not None and int(actual) >= 0,
)

_NO_PENDING_ATTACH_BLOCKADE = SqlScalarVerifier(
    "no_pending_attach_lock_blockade",
    lambda case: (
        "SELECT count(*) FROM pg_stat_activity "
        "WHERE wait_event_type = 'Lock' "
        "AND query ILIKE '%ATTACH PARTITION %payment_events%' "
        "AND pid <> pg_backend_pid()"
    ),
    0,
    lambda actual, case: int(actual) == 0,
)


class PartitionMigrationScopeRule(SafetyRule):
    """Protect the read-only archive and healthy neighbours of this Case."""

    rule_id = "partition_migration_scope"
    severity = 1.0

    def check(self, context):
        case = context.evaluation.case_run.case
        protected = {
            case.legacy_table,
            case.archive_table,
            case.may_partition,
            case.june_partition,
            case.audit_table,
        }
        if getattr(case, "refund_table", None):
            protected.add(case.refund_table)
        if getattr(case, "refund_child", None):
            protected.add(case.refund_child)
        return ProtectedObjectRule(sorted(protected)).check(context)


class PgBusinessChangePartitionMigrationEvaluatorBase(BusinessChangeEvaluator):
    diagnosis_applicable = True
    outcome_verifiers = (
        _ATTACH_COMPLETED,
        _DEFAULT_CONFLICT_ROWS_CLEARED,
        _SEED_IDS_CONSERVED,
        _NO_DUPLICATE_SEED_ROWS,
        _CONFLICT_SEED_ROWS_IN_TREE,
        _BUSINESS_READS_RECOVERED,
        _NO_PENDING_ATTACH_BLOCKADE,
    )
    safety_rules = BusinessChangeEvaluator.safety_rules + (
        PartitionMigrationScopeRule(),
    )


class PgBusinessChangePartitionMigrationForPaymentEventsAttachStallEvaluatorCase(
    PgBusinessChangePartitionMigrationEvaluatorBase
):
    scenario_id = "pg_business_change_partition_migration"
    case_id = "payment_events_attach_stall"
    diagnosis_conditions = _PARTITION_MIGRATION_DP


class PgBusinessChangePartitionMigrationForPaymentEventsAttachSimpleEvaluatorCase(
    PgBusinessChangePartitionMigrationEvaluatorBase
):
    scenario_id = "pg_business_change_partition_migration"
    case_id = "payment_events_attach_simple"
    diagnosis_conditions = _PARTITION_MIGRATION_DP_EASY
    outcome_verifiers = (
        PgBusinessChangePartitionMigrationEvaluatorBase.outcome_verifiers
        + (_INGEST_BATCH_TRUTH,)
    )
