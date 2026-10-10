from src.scenarios.evaluation.diagnosis import ExpectedCondition


def condition(
    condition_id: str,
    *aliases: str,
    critical: bool = False,
    contradictions: tuple[str, ...] = (),
) -> ExpectedCondition:
    return ExpectedCondition(
        condition_id=condition_id,
        aliases=frozenset((condition_id.casefold(), *(alias.casefold() for alias in aliases))),
        critical=critical,
        contradictions=frozenset(item.casefold() for item in contradictions),
    )
