from types import SimpleNamespace

from src.scenarios.postgres.system_failure.lock_contention import PgSystemFailureLockContentionInjector


def test_lock_injector_install_only_prepares_persistent_state():
    calls = []

    class Environment:
        def metrics_hidden(self):
            class Context:
                def __enter__(self):
                    return self

                def __exit__(self, *args):
                    return False

            return Context()

        def execute_sql(self, statement):
            calls.append(statement)
            return {"status": "success"}

    injector = PgSystemFailureLockContentionInjector()
    injector._configure = lambda config, env: setattr(injector, "env", env)
    injector._install_persistent_state = lambda: calls.append("install")
    injector._start_runtime = lambda: calls.append("runtime")
    injector.install(SimpleNamespace(config={}, env=Environment()))

    assert calls == ["install"]
