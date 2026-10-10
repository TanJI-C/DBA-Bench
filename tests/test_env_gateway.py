import pytest

from src.scenarios.runtime.env_gateway import EnvGateway


def test_terminal_environment_tools_are_rejected_by_gateway_dispatch():
    gateway = EnvGateway(object(), [])

    assert gateway.TERMINAL_TOOLS == ("submit", "exit")
    for api in gateway.TERMINAL_TOOLS:
        with pytest.raises(ValueError, match="终止工具"):
            gateway.execute(api, {})
