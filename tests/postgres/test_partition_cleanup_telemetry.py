from types import SimpleNamespace

from src.scenarios.postgres.resource_governance.partition_cleanup import _find_admission_chain


def _case(**overrides):
    values = {
        "admission_sample_count": 2,
        "admission_filesystem_io_mb_per_sec": 1.0,
        "admission_bufferio_waiters": 1,
        "admission_host_pressure": 1.0,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def _sample(filesystem_io, bufferio_waiters, cpu_pressure):
    return {
        "filesystem_io_mb_per_sec": filesystem_io,
        "bufferio_waiters": bufferio_waiters,
        "cpu_pressure_some_avg10": cpu_pressure,
    }


def test_admission_chain_uses_baselines_and_later_cpu_sample():
    samples = [
        _sample(0.0, 0, 0.4),
        _sample(2.0, 0, 0.5),
        _sample(0.2, 1, 0.6),
        _sample(0.1, 1, 1.6),
    ]

    assert _find_admission_chain(
        samples,
        _case(),
        baseline_cpu_pressure=0.4,
        baseline_bufferio_waiters=0,
    ) == {"filesystem_index": 1, "bufferio_index": 2, "cpu_index": 3}


def test_admission_chain_rejects_background_cpu_without_new_pressure():
    samples = [
        _sample(0.0, 0, 0.4),
        _sample(2.0, 0, 0.5),
        _sample(0.2, 1, 0.6),
        _sample(0.1, 1, 0.9),
    ]

    assert _find_admission_chain(
        samples,
        _case(),
        baseline_cpu_pressure=0.4,
        baseline_bufferio_waiters=0,
    ) is None


def test_admission_chain_requires_waiter_after_filesystem_io():
    samples = [
        _sample(2.0, 0, 0.5),
        _sample(0.1, 0, 1.6),
    ]

    assert _find_admission_chain(
        samples,
        _case(),
        baseline_cpu_pressure=0.4,
        baseline_bufferio_waiters=0,
    ) is None
