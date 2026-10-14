from collections.abc import Mapping
from copy import deepcopy
import hashlib


TIKV_STORAGE_MAINTENANCE_PROCEDURE = "recover-mvcc"


def lightning_network_alias(run_id: str) -> str:
    """Short in-network DNS name for the Case-owned Lightning container.

    The container name is ``{run_id}-lightning`` which easily exceeds the 63-byte
    DNS label limit, so Prometheus can never resolve it. Containers get this
    deterministic alias instead, and the Prometheus scrape target uses it.
    """
    return f"rg05-lg-{hashlib.sha1(run_id.encode('utf-8')).hexdigest()[:12]}"


def lightning_job_id(run_id: str) -> str:
    """Opaque run-scoped Lightning job id, uniform in shape with seeded decoy ids.

    Registry triage must not leak which job is the incident through naming:
    every job id — active or decoy — is ``lightning-job/`` plus a 12-hex token,
    so length, prefix clusters, and list order carry no signal. The frozen
    history series keys reuse this id so agents can bind a job to its history.
    """
    return f"lightning-job/{hashlib.sha256(run_id.encode('utf-8')).hexdigest()[:12]}"


def lightning_decoy_job_id(run_id: str, index: int) -> str:
    """Frozen-history job id for seeded batch decoy ``index`` (1-based).

    The controller's registry seeding and the history assembler must derive
    the same ids so every decoy job owns its frozen lightning series.
    """
    return lightning_job_id(f"{run_id}-batch{index:02d}")


class _TiDBReadinessFatalError(RuntimeError):
    pass


class PersistentBaselineIdentityMismatch(RuntimeError):
    """A persistent baseline was produced under a different cluster identity.

    The baseline is a cache of a Case's initial cluster state; a mismatching
    copy is a cache miss that the deployment rebuilds, not a hard failure.
    """


def canonical_pd_config(config: Mapping[str, object]) -> dict[str, object]:
    normalized = deepcopy(dict(config))
    for key in (
        "client-urls",
        "peer-urls",
        "advertise-client-urls",
        "advertise-peer-urls",
        "name",
    ):
        normalized.pop(key, None)
    metric = normalized.get("metric")
    if metric is not None:
        if not isinstance(metric, dict):
            raise TypeError(f"PD config metric must be an object: metric={metric!r}")
        metric.pop("job", None)
    return normalized


def _render_toml_value(value: object) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (int, float)):
        return repr(value)
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    raise TypeError(f"Unsupported TiKV config override value: value={value!r}")


def _render_toml_sections(sections: Mapping[str, Mapping[str, object]]) -> str:
    blocks = []
    for section, keys in sections.items():
        lines = [f"[{section}]"]
        lines.extend(f"{key} = {_render_toml_value(value)}" for key, value in keys.items())
        blocks.append("\n".join(lines))
    return "\n\n".join(blocks) + "\n"
