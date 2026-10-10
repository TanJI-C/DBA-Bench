import socket

from src.benchmark.runner import rebase_command_ports


def test_rebase_keeps_command_when_ports_free():
    command = ["python", "scenario.py", "--port", "59991"]

    rebased, chosen = rebase_command_ports(command)

    assert chosen is None
    assert rebased == command


def test_rebase_shifts_occupied_port_to_next_free():
    with socket.socket() as held:
        held.bind(("0.0.0.0", 59992))
        held.listen(1)
        command = ["python", "scenario.py", "--port", "59992"]

        rebased, chosen = rebase_command_ports(command)

    assert chosen == 59993
    assert rebased[rebased.index("--port") + 1] == "59993"


def test_rebase_shifts_port_pair_preserving_offsets():
    with socket.socket() as held:
        held.bind(("0.0.0.0", 59994))
        held.listen(1)
        command = [
            "python", "scenario.py",
            "--primary-port", "59994",
            "--restore-port", "59995",
        ]

        rebased, chosen = rebase_command_ports(command)

    assert chosen == 59995
    assert rebased[rebased.index("--primary-port") + 1] == "59995"
    assert rebased[rebased.index("--restore-port") + 1] == "59996"
