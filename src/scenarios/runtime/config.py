import os


def required_run_timeout_seconds() -> int:
    variable = "AIOPS_RUN_TIMEOUT_SECONDS"
    if variable not in os.environ:
        raise RuntimeError(
            f"Scenario runtime requires environment variable {variable}; "
            "the experiment runner sets it from runtime.timeout_seconds"
        )
    raw = os.environ[variable]
    try:
        seconds = int(raw)
    except ValueError as exc:
        raise ValueError(
            f"Scenario runtime timeout must be an integer: {variable}={raw!r}"
        ) from exc
    if seconds <= 0:
        raise ValueError(
            f"Scenario runtime timeout must be positive: {variable}={raw!r}"
        )
    return seconds
