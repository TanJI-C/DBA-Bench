from src.scenarios.evaluation.outcome import REPORT_OUTCOME_FIELDS, ReportTermsVerifier, build_outcome_result
from src.scenarios.evaluation.tidb.base import TidbEvaluator


def contains_all(value: object, terms: tuple[str, ...]) -> bool:
    text = str(value).casefold()
    return all(term.casefold() in text for term in terms)


def contains_any(value: object, alternatives: tuple[tuple[str, ...], ...]) -> bool:
    return any(contains_all(value, terms) for terms in alternatives)


class TidbHealthCheckEvaluator(TidbEvaluator):
    diagnosis_applicable = False
    diagnosis_conditions = ()

    def OutcomePassFunc(self, context):
        checks = tuple(verifier.verify(context) for verifier in self.outcome_verifiers)
        report_ids = {
            verifier.check_id
            for verifier in self.outcome_verifiers
            if isinstance(verifier, ReportTermsVerifier)
        }
        return build_outcome_result(
            checks,
            report_fields_used=REPORT_OUTCOME_FIELDS if report_ids else (),
            trusted_artifacts_used=tuple(
                check.check_id for check in checks if check.check_id not in report_ids
            ),
        )
