"""TiCDC changefeed lifecycle over the pinned ``cdc`` cli.

The pinned pingcap/ticdc image keeps the binary at ``/cdc`` (it is not on
PATH). v8.1 cli facts verified live against pingcap/ticdc:v8.1.0:

- ``create`` and ``resume`` accept ``--no-confirm`` (create: skip the config
  confirmation; resume: skip the ignore-ineligible-table prompt);
- ``pause`` and ``remove`` have no ``--no-confirm`` flag and never prompt
  (pause flags are only -c/--changefeed-id and -n/--namespace);
- ``query --simple`` prints one JSON object with state / checkpoint_tso /
  checkpoint_time / error; ``query`` without ``--simple`` prints the full
  changefeed config.

Lifecycle actions run their cli command against PD and return the post-action
``query --simple`` observation trimmed to the agent-relevant fields
(state / checkpoint_tso / error). ``remove`` returns the cli confirmation:
the feed no longer exists, so there is no post-state to query.
"""

from __future__ import annotations

from collections.abc import Callable
import json

TICDC_CLI = "/cdc"

CliRunner = Callable[[list[str]], str]


class CdcChangefeedAdmin:
    """Changefeed lifecycle operations through one capture's ``cdc`` cli.

    ``cli_runner`` receives the full argument vector (after ``docker exec``)
    and returns the captured stdout; the environment wires it to the deployment
    (``PersistentTiDBEnvironment.changefeed_cli_runner``) so callers never
    touch the deployment directly. ``pd_address`` is the in-network PD client
    URL (e.g. ``http://pd-0:2379``).
    """

    def __init__(self, *, cli_runner: CliRunner, pd_address: str):
        if not pd_address.startswith("http://"):
            raise ValueError(f"pd_address must be an http URL: pd_address={pd_address!r}")
        self.pd_address = pd_address
        self._cli_runner = cli_runner

    def _run(self, command: list[str]) -> str:
        return self._cli_runner([TICDC_CLI, "cli", *command])

    def _observe(self, changefeed_id: str) -> dict:
        stdout = self._run([
            "changefeed", "query",
            f"--changefeed-id={changefeed_id}", "--simple",
        ])
        payload = json.loads(stdout)
        if not isinstance(payload, dict):
            raise TypeError(f"cdc cli changefeed query returned non-mapping output: payload={payload!r}")
        return {
            "changefeed_id": changefeed_id,
            "state": payload["state"],
            "checkpoint_tso": int(payload["checkpoint_tso"]),
            "error": payload["error"],
        }

    def create(self, changefeed_id: str, sink_uri: str, start_ts: int | None = None) -> dict:
        command = [
            "changefeed", "create",
            f"--pd={self.pd_address}",
            f"--changefeed-id={changefeed_id}",
            f"--sink-uri={sink_uri}",
        ]
        if start_ts is not None:
            command.append(f"--start-ts={int(start_ts)}")
        command.append("--no-confirm")
        self._run(command)
        return self._observe(changefeed_id)

    def pause(self, changefeed_id: str) -> dict:
        self._run([
            "changefeed", "pause",
            f"--pd={self.pd_address}",
            f"--changefeed-id={changefeed_id}",
        ])
        return self._observe(changefeed_id)

    def resume(self, changefeed_id: str) -> dict:
        self._run([
            "changefeed", "resume",
            f"--pd={self.pd_address}",
            f"--changefeed-id={changefeed_id}",
            "--no-confirm",
        ])
        return self._observe(changefeed_id)

    def remove(self, changefeed_id: str) -> dict:
        output = self._run([
            "changefeed", "remove",
            f"--pd={self.pd_address}",
            f"--changefeed-id={changefeed_id}",
        ])
        return {"changefeed_id": changefeed_id, "state": "removed", "detail": output.strip()}

    def query(self, changefeed_id: str) -> dict:
        return self._observe(changefeed_id)
