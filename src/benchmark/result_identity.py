"""Stable identities and filenames for selected results and their analyses."""

from src.scenarios.case_tags import citation_tag


def validate_case_tag(record: dict) -> str:
    expected = citation_tag(record["scenario_id"], record["case_id"])
    if record["citation_tag"] != expected or "alias" in record:
        raise ValueError(
            f"Result identity must use its frozen citation tag: "
            f"scenario_id={record['scenario_id']!r}, case_id={record['case_id']!r}, "
            f"citation_tag={record['citation_tag']!r}, expected={expected!r}, "
            f"alias_present={'alias' in record}"
        )
    return expected


def result_run_key(tag: str, agent_id: str, repetition: int) -> str:
    return f"{tag}/{agent_id}/r{repetition:03d}"


def result_run_filename(tag: str, repetition: int) -> str:
    return f"{tag}__r{repetition:03d}.json"


def analysis_run_filename(tag: str, agent_id: str, repetition: int) -> str:
    return f"{tag}__{agent_id}__r{repetition:03d}.json"


def persistent_result_tag(scenario_id: str) -> str:
    from src.benchmark.adapters.persistent_scenario import persistent_scenario_definition_path
    from src.persistent_scenarios.model.loader import load_persistent_scenario

    spec = load_persistent_scenario(persistent_scenario_definition_path(scenario_id))
    if spec.citation_tag is None:
        raise ValueError(f"Development fixture has no formal result citation tag: scenario_id={scenario_id!r}")
    return spec.citation_tag
