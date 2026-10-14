"""BrPermissionEnv: Case-specific capabilities and mutable run state.

Generic TiDB execution remains in src.execution.environments.tidb.
"""

from src.execution.environments.tidb import TiDBEnv
from src.execution.tidb_cluster_control import TiDBClusterControl
import hashlib
import re
import shlex
import subprocess
from typing import Any, Dict, Optional


_BR_REFRESH_IDENTITY_REJECTION = (
    "BR binding refresh rejected: the presented authority chain does not verify "
    "against the current control-plane state; no state changed."
)

class _BrRefreshIdentityError(ValueError):
    """Internal: one BR binding refresh identity check failed.

    The message carries internal diagnostic detail (supplied vs expected
    tuples) and must never be surfaced to the agent verbatim; the focused
    runtime replaces it with the uniform rejection text.
    """
class BrPermissionControl(TiDBClusterControl):
    def _job(self, operation, target, parameters):
        env = self.env
        if operation == 'get':
            state = env.inspect_br_backup_state()
            result = {
                "last_result": env._br_job_result(state["last_result"]),
                "objects": state["objects"],
                "desired_binding": state["desired_binding"],
            }
        elif operation == 'observe':
            if env._br_backup_runtime is None:
                raise RuntimeError(f"No managed external job is configured: run_id={env.run_id!r}")
            runtime = env._br_backup_runtime
            events = list(runtime.get("controller_events", ()))
            default_window = 8
            start_text = parameters.get("start_timestamp")
            end_text = parameters.get("end_timestamp")
            if (start_text is None) != (end_text is None):
                raise ValueError(
                    "job observe start_timestamp and end_timestamp must be provided together"
                )
            windowed = events
            if start_text is not None:
                windowed = [
                    event for event in events
                    if str(start_text) <= event["at"] <= str(end_text)
                ]
            else:
                windowed = events[:default_window]
            oldest_at = events[-1]["at"] if events else None
            result = {
                "job_kind": "br_backup",
                "target_scope": runtime["target_scope"],
                "controller_events": windowed,
                "event_count": len(windowed),
                "total_event_count": len(events),
                "oldest_event_at": oldest_at,
                "window_applied": start_text is not None,
            }
        elif operation == 'release_prefix_quarantine':
            if env._br_backup_runtime is None:
                raise RuntimeError(f"No managed external job is configured: run_id={env.run_id!r}")
            runtime = env._br_backup_runtime
            if not runtime.get("storage_prefix_quarantine"):
                raise ValueError(
                    "release_prefix_quarantine requires parameters.target_prefix, "
                    "parameters.quarantine_ref, and parameters.triggering_change_ref"
                )
            required = {"target_prefix", "quarantine_ref", "triggering_change_ref"}
            if not required.issubset(parameters):
                raise ValueError(
                    "release_prefix_quarantine is missing parameters: "
                    f"missing={sorted(required - set(parameters))!r}"
                )
            result = env._release_br_prefix_quarantine(
                str(parameters["target_prefix"]),
                str(parameters["quarantine_ref"]),
                str(parameters["triggering_change_ref"]),
            )
        elif operation == 'refresh_binding':
            required = {
                "target_scope",
                "request_route_token",
                "request_cache_token",
                "attempt_id",
                "observed_authority_grant_id",
                "desired_authority_grant_id",
                "authority_lease_id",
                "authority_epoch",
                "request_assignment_fence",
                "request_context_token",
                "request_stage",
                "assignment_phase",
                "assignment_reason",
                "cache_phase",
            }
            if target is None or not required.issubset(parameters):
                raise ValueError(
                    "BR binding refresh requires target worker, parameters.target_scope, "
                    "parameters.request_route_token, and the observed failed request "
                    "parameters.request_cache_token and parameters.attempt_id, plus parameters.observed_authority_grant_id and "
                    "parameters.desired_authority_grant_id, parameters.authority_lease_id, and "
                    "parameters.authority_epoch"
                    ", parameters.request_assignment_fence, parameters.request_context_token, "
                    "parameters.request_stage, parameters.assignment_phase, parameters.assignment_reason, "
                    "and parameters.cache_phase"
                )
            result = env._refresh_br_binding_cache(
                target,
                str(parameters["target_scope"]),
                str(parameters["request_route_token"]),
                str(parameters["request_cache_token"]),
                str(parameters["attempt_id"]),
                int(parameters["observed_authority_grant_id"]),
                int(parameters["desired_authority_grant_id"]),
                int(parameters["authority_lease_id"]),
                str(parameters["authority_epoch"]),
                str(parameters["request_assignment_fence"]),
                str(parameters["request_context_token"]),
                str(parameters["request_stage"]),
                str(parameters["assignment_phase"]),
                str(parameters["assignment_reason"]),
                str(parameters["cache_phase"]),
                )
        elif operation == 'start':
            required = ("database", "table")
            missing = [name for name in required if name not in parameters]
            if missing:
                raise ValueError(
                    f"job start is missing parameters: missing={missing!r}"
                )
            credential_keys = {"access_key", "secret_key"} & parameters.keys()
            if credential_keys not in (set(), {"access_key", "secret_key"}):
                raise ValueError(
                    "BR job start requires both access_key and secret_key for an explicit override: "
                    f"provided={sorted(credential_keys)!r}"
                )
            result = env._run_br_backup(
                parameters["database"],
                parameters["table"],
                parameters.get("access_key"),
                parameters.get("secret_key"),
            )
            result = env._br_job_result(result)
        else:
            raise ValueError(f"Unsupported job operation: operation={operation!r}")
        return result

class BrPermissionEnv(TiDBEnv):
    cluster_control_type = BrPermissionControl

    def __init__(self, *args, **kwargs):
        self._br_backup_runtime = None
        self._br_backup_attempt_no = 0
        self._last_br_backup_result = None
        super().__init__(*args, **kwargs)

    def configure_br_backup_runtime(self, runtime: Dict[str, Any]) -> None:
        if self._br_backup_runtime is not None:
            raise RuntimeError(f"TiDB BR backup runtime is already configured: run_id={self.run_id!r}")
        self._br_backup_runtime = dict(runtime)

    def clear_br_backup_runtime(self) -> None:
        if self._br_backup_runtime is None:
            raise RuntimeError(f"TiDB BR backup runtime is not configured: run_id={self.run_id!r}")
        self._br_backup_runtime = None
        self._br_backup_attempt_no = 0
        self._last_br_backup_result = None

    def _require_br_backup_runtime(self) -> Dict[str, Any]:
        if self._br_backup_runtime is None:
            raise RuntimeError(f"TiDB BR backup runtime is not configured: run_id={self.run_id!r}")
        return self._br_backup_runtime

    def capture_br_source_truth(self, case) -> Dict[str, int]:
        runtime = self._require_br_backup_runtime()
        if (case.database, case.table) != (runtime["database"], runtime["table"]):
            raise ValueError(
                "TiDB BR source truth target mismatch: "
                f"case={case.database}.{case.table}, runtime={runtime['database']}.{runtime['table']}"
            )
        sql = (
            f"SELECT COUNT(*), COALESCE(SUM(event_id), 0), "
            f"BIT_XOR(CRC32(CONCAT_WS('#', event_id, tenant_id, event_type, amount, payload))) "
            f"FROM {runtime['database']}.{runtime['table']}"
        )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(sql)
            row = cursor.fetchone()
        if row is None or len(row) != 3:
            raise RuntimeError(
                "TiDB BR source truth query returned an invalid row: "
                f"run_id={self.run_id!r}, sql={sql!r}, row={row!r}"
            )
        return {
            "row_count": int(row[0]),
            "event_id_sum": int(row[1]),
            "crc": int(row[2]),
        }

    def _record_br_backup_attempt(
        self,
        runtime: Dict[str, Any],
        result: Dict[str, object],
    ) -> str:
        self._br_backup_attempt_no += 1
        attempt_id = f"{runtime['run_prefix']}-{self._br_backup_attempt_no:03d}"
        dispatch_id = f"{attempt_id}-dispatch"
        route_token = (
            runtime["request_route_token"]
            if self._br_backup_attempt_no == 1
            else "rt-1a6d4c8e2f90"
            if self._br_backup_attempt_no == 2
            else f"rt-{hashlib.sha256(attempt_id.encode('utf-8')).hexdigest()[:12]}"
        )
        lease_token = (
            runtime["target_lease_token"]
            if result["http_status"] == 403
            else runtime["post_handoff_lease_token"]
        )
        material_handle = str(result["material_handle"])
        request_assignment_fence = str(
            result["request_assignment_fence"]
        )
        request_context_token = str(result["request_context_token"])
        request_started_at = (
            "2026-08-01 23:58:40"
            if result["http_status"] == 403
            else "2026-08-01 23:59:40"
        )
        event_time = (
            "2026-08-01 23:58:47"
            if result["http_status"] == 403
            else "2026-08-01 23:59:46"
        )
        metrics = result["metrics"]
        status = str(result["status"])
        error_text = str(result.get("error", ""))[-2048:]
        result["dispatch_id"] = dispatch_id
        result["audit_dispatch_id"] = dispatch_id
        result["lease_token"] = lease_token
        result["material_handle"] = material_handle
        result["request_assignment_fence"] = request_assignment_fence
        result["request_context_token"] = request_context_token
        request_stage = "backup_upload"
        assignment_phase = (
            runtime.get("target_execution_phase", "dispatch_window")
            if result["http_status"] == 403
            else "retry_data_plane"
        )
        assignment_reason = (
            runtime.get("target_execution_reason", "storage-write")
            if result["http_status"] == 403
            else "post-refresh-retry"
        )
        result["request_stage"] = request_stage
        result["assignment_phase"] = assignment_phase
        result["assignment_reason"] = assignment_reason
        result["cache_phase"] = assignment_phase
        is_failed_write = result["http_status"] == 403 and self._br_backup_attempt_no == 1
        if is_failed_write:
            runtime["failed_dispatch_id"] = dispatch_id
            runtime["failed_request_started_at"] = request_started_at
            runtime["failed_request_event_time"] = event_time
            runtime["failed_request_attempt_id"] = f"{attempt_id}-write"
            runtime["failed_request_route_token"] = route_token
            runtime["failed_request_assignment_fence"] = request_assignment_fence
            runtime["failed_request_context_token"] = request_context_token
            runtime["failed_request_stage"] = request_stage
            runtime["failed_request_assignment_phase"] = assignment_phase
            runtime["failed_request_assignment_reason"] = assignment_reason
            runtime["failed_request_cache_phase"] = assignment_phase
        sql = (
            f"INSERT INTO {runtime['history_table']} "
            "(job_id, storage_uri, database_name, table_name, status, error_text, "
            "ranges_total, ranges_succeed, ranges_failed, checksum_percent, actor) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
        )
        values = (
            attempt_id,
            runtime["storage"],
            runtime["database"],
            runtime["table"],
            status,
            error_text,
            metrics["total_ranges"],
            metrics["ranges_succeed"],
            metrics["ranges_failed"],
            metrics["checksum_percent"],
            "br-agent",
        )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(sql, values)
            cursor.execute(
                f"INSERT INTO {runtime['dispatch_routes_table']} "
                "(route_token, dispatch_id, target_scope, executor_handle, lease_token, route_generation, valid_from, "
                "valid_to, route_state, assignment_phase, route_reason, request_assignment_fence, request_context_token) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    route_token,
                    dispatch_id,
                    result["target_scope"],
                    result["executor_handle"],
                    lease_token,
                    3000 + self._br_backup_attempt_no,
                    request_started_at,
                    "2026-08-01 23:59:00" if result["http_status"] == 403 else None,
                    "released" if result["http_status"] == 403 else "active",
                    assignment_phase,
                    assignment_reason,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            cursor.execute(
                f"INSERT INTO {runtime['job_dispatches_table']} "
                "(dispatch_id, job_id, target_scope, storage_uri, dispatch_generation, "
                "dispatched_at, released_at, dispatch_state, assignment_phase, assignment_reason, request_assignment_fence, request_context_token) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    dispatch_id,
                    attempt_id,
                    result["target_scope"],
                    runtime["storage"],
                    3000 + self._br_backup_attempt_no,
                    request_started_at,
                    "2026-08-01 23:59:00" if result["http_status"] == 403 else None,
                    "released" if result["http_status"] == 403 else "active",
                    assignment_phase,
                    assignment_reason,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            cursor.execute(
                f"INSERT INTO {runtime['storage_audit_table']} "
                "(job_id, target_scope, storage_uri, dispatch_id, http_status, access_key_fingerprint, "
                "policy_decision, request_stage, request_started_at, event_time, request_assignment_fence, request_context_token) VALUES "
                "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                (
                    attempt_id,
                    result["target_scope"],
                    runtime["storage"],
                    dispatch_id,
                    result["http_status"],
                    result["access_key_fingerprint"],
                    result.get("policy_decision", "allow"),
                    request_stage,
                    request_started_at,
                    event_time,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            if is_failed_write:
                cursor.execute(
                    f"INSERT INTO {runtime['request_attempts_table']} "
                    "(attempt_id, dispatch_id, target_scope, request_context_token, request_assignment_fence, "
                    "request_started_at, event_time, request_stage, execution_phase, execution_reason, attempt_sequence, "
                    "operation_name, attempt_state, access_key_fingerprint, http_status) VALUES "
                    "(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)",
                    (
                        runtime["failed_request_attempt_id"],
                        dispatch_id,
                        result["target_scope"],
                        request_context_token,
                        request_assignment_fence,
                        request_started_at,
                        event_time,
                        request_stage,
                        assignment_phase,
                        assignment_reason,
                        int(runtime["failed_request_attempt_sequence"]),
                        "put_backup_chunk",
                        "failed",
                        result["access_key_fingerprint"],
                        403,
                    ),
                )
        return attempt_id

    def _release_br_prefix_quarantine(
        self,
        target_prefix: str,
        quarantine_ref: str,
        triggering_change_ref: str,
    ) -> Dict[str, object]:
        runtime = self._require_br_backup_runtime()
        mismatch = not (
            target_prefix == runtime["object_prefix"]
            and quarantine_ref == runtime["prefix_quarantine_ref"]
            and triggering_change_ref == runtime["target_change_ref"]
        )
        if mismatch or not runtime.get("prefix_quarantine_active"):
            raise _BrRefreshIdentityError(
                "BR storage prefix quarantine release rejected: the presented quarantine "
                "identity does not verify against the storage guard state; no state changed."
            )
        runtime["prefix_quarantine_active"] = False
        return {
            "released": True,
            "prefix": runtime["object_prefix"],
            "bucket": runtime["bucket"],
            "quarantine_ref": runtime["prefix_quarantine_ref"],
            "guard": "bucket-denial-rate-guard",
        }

    def _record_br_quarantine_denial(
        self,
        runtime: Dict[str, Any],
        result: Dict[str, object],
    ) -> None:
        # r11: every denied write is announced on the controller stream, but
        # the release ticket itself is issued only by the storage guard into
        # its ticket table on the first denial, so the release identity
        # cannot be observed before the denied attempt happened.
        denial_count = int(runtime.get("quarantine_denial_count", 0)) + 1
        runtime["quarantine_denial_count"] = denial_count
        denial_seconds = 2 * 60 + 3 + 20 * (denial_count - 1)
        at = f"2026-08-02 00:{denial_seconds // 60:02d}:{denial_seconds % 60:02d}"
        event = {
            "event": "storage_write_denied",
            "prefix": runtime["object_prefix"],
            "bucket": runtime["bucket"],
            "guard": "bucket-denial-rate-guard",
            "dispatch_id": result["dispatch_id"],
            "access_key_fingerprint": result["access_key_fingerprint"],
            "at": at,
        }
        runtime["controller_events"] = [event] + list(
            runtime.get("controller_events", ())
        )
        if runtime.get("quarantine_ticket_issued"):
            return
        runtime["quarantine_ticket_issued"] = True
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"INSERT INTO {runtime['quarantine_tickets_table']} "
                "(ticket_ref, prefix, bucket, guard, triggering_change_ref, "
                "issued_at, ticket_state) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                (
                    runtime["prefix_quarantine_ref"],
                    runtime["object_prefix"],
                    runtime["bucket"],
                    "bucket-denial-rate-guard",
                    runtime["target_change_ref"],
                    at,
                    "active",
                ),
            )

    def _run_br_backup(
        self,
        database: str,
        table: str,
        access_key: Optional[str] = None,
        secret_key: Optional[str] = None,
    ) -> Dict[str, object]:
        runtime = self._require_br_backup_runtime()
        expected_target = (runtime["database"], runtime["table"])
        if (database, table) != expected_target:
            raise ValueError(
                "BR backup target is outside the active case contract: "
                f"requested={database}.{table}, expected={expected_target[0]}.{expected_target[1]}"
            )
        if (access_key is None) != (secret_key is None):
            raise ValueError(
                "BR backup credentials must be supplied together: "
                f"database={database!r}, table={table!r}, access_key_supplied={access_key is not None}, "
                f"secret_key_supplied={secret_key is not None}"
            )
        credential_source = "explicit_override" if access_key is not None else "worker_observed_binding"
        access_key = runtime["observed_access_key"] if access_key is None else access_key
        secret_key = runtime["observed_secret_key"] if secret_key is None else secret_key
        # r9: the storage denial-rate guard quarantines the backup prefix after
        # repeated denied writes. Wrong credentials still fail authentication
        # (real 403 below); correct credentials hit the guard and are denied
        # by policy until the quarantine is released through the bounded op.
        if (
            runtime.get("storage_prefix_quarantine")
            and runtime.get("prefix_quarantine_active")
            and access_key == runtime["correct_access_key"]
        ):
            result = {
                "status": "error",
                "operation": "br_backup_table",
                "database": database,
                "table": table,
                "exit_code": 1,
                "metrics": self._parse_br_metrics(""),
                "output": "",
                "credential_source": credential_source,
                "access_key_fingerprint": self._br_access_key_fingerprint(access_key),
                "target_scope": runtime["target_scope"],
                "executor_handle": runtime["target_executor_handle"],
                "material_handle": (
                    runtime["observed_material_handle"]
                    if credential_source == "worker_observed_binding"
                    else "mh-explicit-override"
                ),
                "request_assignment_fence": (
                    runtime["target_assignment_fence"]
                    if self._br_backup_attempt_no == 0
                    else runtime["retry_assignment_fence"]
                ),
                "request_context_token": (
                    runtime["target_request_context"]
                    if self._br_backup_attempt_no == 0
                    else runtime["retry_request_context"]
                ),
                "http_status": 403,
                "policy_decision": "deny",
                "error": (
                    "BR failed: failed to get region of bucket admission: Forbidden: "
                    "quarantine policy denies writes to prefix "
                    f"{runtime['object_prefix']}"
                ),
            }
            attempt_id = self._record_br_backup_attempt(runtime, result)
            self._record_br_quarantine_denial(runtime, result)
            result["attempt_id"] = attempt_id
            self._last_br_backup_result = result
            return result
        container_name = (
            f"aiopsbench-br-{hashlib.sha256(self.run_id.encode()).hexdigest()[:12]}-"
            f"{self._br_backup_attempt_no + 1:03d}"
        )
        command = [
            "docker", "run", "--rm", "--name", container_name,
            "--network", runtime["network_name"],
            "-e", f"AWS_ACCESS_KEY_ID={access_key}",
            "-e", f"AWS_SECRET_ACCESS_KEY={secret_key}",
            "--entrypoint", "/br", runtime["br_image"],
            "backup", "table",
            "--pd", runtime["pd_endpoint"],
            "--db", database,
            "--table", table,
            "--storage", runtime["storage"],
            "--send-credentials-to-tikv=true",
            "--checksum=true",
            "--log-file", "-",
        ]
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        try:
            stdout, stderr = process.communicate(timeout=int(runtime["timeout_seconds"]))
            output = "\n".join(part for part in (stdout, stderr) if part)
            status = "success" if process.returncode == 0 else "error"
            error = output if status == "error" else ""
            exit_code = process.returncode
        except subprocess.TimeoutExpired as exc:
            process.kill()
            stdout, stderr = process.communicate()
            cleanup = subprocess.run(
                ["docker", "rm", "--force", container_name],
                capture_output=True,
                text=True,
                timeout=30,
            )
            if cleanup.returncode != 0:
                raise RuntimeError(
                    "Timed-out BR backup container cleanup failed: "
                    f"run_id={self.run_id!r}, container={container_name!r}, "
                    f"returncode={cleanup.returncode}, stdout={cleanup.stdout.strip()!r}, "
                    f"stderr={cleanup.stderr.strip()!r}"
                ) from exc
            output = "\n".join(part for part in (stdout, stderr) if part)
            status = "error"
            error = (
                f"BR backup timed out: timeout_seconds={runtime['timeout_seconds']}, "
                f"output={output}"
            )
            exit_code = 124
        redacted_output = output
        redacted_error = error
        for value in {access_key}:
            redacted_output = redacted_output.replace(value, "<redacted-access-key>")
            redacted_error = redacted_error.replace(value, "<redacted-access-key>")
        for value in {secret_key}:
            redacted_output = redacted_output.replace(value, "<redacted-secret-key>")
            redacted_error = redacted_error.replace(value, "<redacted-secret-key>")
        result = {
            "status": status,
            "operation": "br_backup_table",
            "database": database,
            "table": table,
            "exit_code": exit_code,
            "metrics": self._parse_br_metrics(output),
            "output": redacted_output,
            "credential_source": credential_source,
            "access_key_fingerprint": self._br_access_key_fingerprint(access_key),
            "target_scope": runtime["target_scope"],
            "executor_handle": runtime["target_executor_handle"],
            "material_handle": (
                runtime["observed_material_handle"]
                if credential_source == "worker_observed_binding"
                else "mh-explicit-override"
            ),
            "request_assignment_fence": (
                runtime["target_assignment_fence"]
                if self._br_backup_attempt_no == 0
                else runtime["retry_assignment_fence"]
            ),
            "request_context_token": (
                runtime["target_request_context"]
                if self._br_backup_attempt_no == 0
                else runtime["retry_request_context"]
            ),
            "http_status": 200 if status == "success" else 403,
        }
        if redacted_error:
            result["error"] = redacted_error
        attempt_id = self._record_br_backup_attempt(runtime, result)
        result["attempt_id"] = attempt_id
        self._last_br_backup_result = result
        return result

    def _list_br_objects(self, runtime: Dict[str, str]) -> tuple[str, ...]:
        backupmeta_path = (
            f"admission/{runtime['bucket']}/"
            f"{runtime['object_prefix'].rstrip('/')}/backupmeta"
        )
        script = (
            "mc alias set admission http://"
            f"{runtime['minio_container']}:9000 {runtime['correct_access_key']} "
            f"{runtime['correct_secret_key']} >/dev/null && "
            f"mc stat {shlex.quote(backupmeta_path)}"
        )
        completed = subprocess.run(
            [
                "docker", "run", "--rm", "--network", runtime["network_name"],
                "--entrypoint", "/bin/sh", runtime["mc_image"], "-c", script,
            ],
            capture_output=True,
            text=True,
            timeout=120,
        )
        if completed.returncode != 0:
            not_found = completed.stderr.casefold()
            if "object does not exist" in not_found or "nosuchkey" in not_found or "not found" in not_found:
                return ()
            raise RuntimeError(
                "BR object listing failed: "
                f"run_id={self.run_id!r}, returncode={completed.returncode}, "
                f"stdout={completed.stdout.strip()!r}, stderr={completed.stderr.strip()!r}"
            )
        evidence = tuple(line for line in completed.stdout.splitlines() if line.strip())
        return (backupmeta_path, *evidence)

    @staticmethod
    def _br_access_key_fingerprint(access_key: str) -> str:
        return hashlib.sha256(access_key.encode("utf-8")).hexdigest()[:16]

    def _br_binding_propagation(self, runtime: Dict[str, Any]) -> list[dict[str, object]]:
        desired_binding_id = int(runtime["desired_binding_id"])
        desired_revision = int(runtime["desired_revision"])
        observed_binding_id = int(runtime["observed_binding_id"])
        observed_revision = int(runtime["observed_revision"])
        desired_credential_id = int(runtime["desired_credential_id"])
        return [
            {
                "worker_id": runtime["target_worker"],
                "target_scope": runtime["target_scope"],
                "desired_binding_id": desired_binding_id,
                "desired_revision": desired_revision,
                "desired_credential_id": desired_credential_id,
                "observed_binding_id": observed_binding_id,
                "observed_revision": observed_revision,
                "observed_material_handle": runtime["observed_material_handle"],
                "lease_state": "converged" if observed_revision == desired_revision else "stale",
                "last_heartbeat": "2026-08-01 23:59:58" if observed_revision == desired_revision else "2026-08-01 23:58:41",
                "change_ref": runtime["target_change_ref"],
            },
            {
                "worker_id": runtime["healthy_worker"],
                "target_scope": runtime["target_scope"],
                "desired_binding_id": desired_binding_id,
                "desired_revision": desired_revision,
                "desired_credential_id": desired_credential_id,
                "observed_binding_id": desired_binding_id,
                "observed_revision": desired_revision,
                "observed_material_handle": runtime["correct_material_handle"],
                "lease_state": "converged",
                "last_heartbeat": "2026-08-01 23:59:59",
                "change_ref": runtime["target_change_ref"],
            },
        ]

    def _br_storage_observations(self, runtime: Dict[str, Any]) -> dict[str, object]:
        return {
            "target_scope": runtime["target_scope"],
            "target_storage_uri": runtime["storage"],
            "object_store_state": "healthy",
            "target_prefix_policy": "allow",
            "canary_scope": f"{runtime['target_scope']}/rehearsal",
            "canary_worker": runtime["healthy_worker"],
            "canary_write_state": "success",
            "last_forbidden_worker": runtime["target_worker"],
            "last_forbidden_material_handle": runtime["target_material_handle"],
            "last_forbidden_at": "2026-08-01 23:58:47",
        }

    def _br_request_cache_state(self, runtime: Dict[str, Any]) -> list[dict[str, object]]:
        sql = (
            f"SELECT cache_token, route_token, target_scope, worker_handle, material_handle, cache_phase, "
            f"valid_from, valid_to, cache_state, change_ref, request_assignment_fence, request_context_token "
            f"FROM {runtime['request_cache_table']} "
            "WHERE target_scope=%s ORDER BY valid_from DESC, cache_token DESC"
        )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(sql, (runtime["target_scope"],))
            rows = cursor.fetchall()
        return [
            {
                "cache_token": str(row[0]),
                "route_token": str(row[1]),
                "target_scope": str(row[2]),
                "worker_handle": str(row[3]),
                "material_handle": str(row[4]),
                "cache_phase": str(row[5]),
                "valid_from": str(row[6]),
                "valid_to": None if row[7] is None else str(row[7]),
                "cache_state": str(row[8]),
                "change_ref": str(row[9]),
                "request_assignment_fence": str(row[10]),
                "request_context_token": str(row[11]),
            }
            for row in rows
        ]

    def _refresh_br_binding_cache(
        self,
        target: str,
        target_scope: str,
        request_route_token: str,
        request_cache_token: str,
        attempt_id: str,
        observed_authority_grant_id: int,
        desired_authority_grant_id: int,
        authority_lease_id: int,
        authority_epoch: str,
        request_assignment_fence: str,
        request_context_token: str,
        request_stage: str,
        assignment_phase: str,
        assignment_reason: str,
        cache_phase: str,
    ) -> dict[str, object]:
        runtime = self._require_br_backup_runtime()
        try:
            return self._refresh_br_binding_cache_checked(
                runtime,
                target,
                target_scope,
                request_route_token,
                request_cache_token,
                attempt_id,
                observed_authority_grant_id,
                desired_authority_grant_id,
                authority_lease_id,
                authority_epoch,
                request_assignment_fence,
                request_context_token,
                request_stage,
                assignment_phase,
                assignment_reason,
                cache_phase,
            )
        except _BrRefreshIdentityError:
            if not runtime.get("uniform_refresh_rejection", False):
                raise
            raise ValueError(_BR_REFRESH_IDENTITY_REJECTION) from None

    def _refresh_br_binding_cache_checked(
        self,
        runtime: Dict[str, Any],
        target: str,
        target_scope: str,
        request_route_token: str,
        request_cache_token: str,
        attempt_id: str,
        observed_authority_grant_id: int,
        desired_authority_grant_id: int,
        authority_lease_id: int,
        authority_epoch: str,
        request_assignment_fence: str,
        request_context_token: str,
        request_stage: str,
        assignment_phase: str,
        assignment_reason: str,
        cache_phase: str,
    ) -> dict[str, object]:
        # r4 focused authority model: lease rows carry the desired sentinel 0
        # and the validator derives the unique request-time-valid production
        # grant from the control-plane credential and the grants window.
        derive_desired_from_grants = bool(runtime.get("derive_desired_from_grants", False))
        if target != runtime["target_worker"]:
            raise _BrRefreshIdentityError(
                "BR binding refresh target does not match the failed request assignment; no state changed: "
                f"attempted_target={target!r}, target_scope={target_scope!r}, "
                f"request_route_token={request_route_token!r}, request_cache_token={request_cache_token!r}, "
                f"run_id={self.run_id!r}"
            )
        if target_scope != runtime["target_scope"]:
            raise _BrRefreshIdentityError(
                "BR binding refresh scope is outside the approved table scope: "
                f"target_scope={target_scope!r}, expected={runtime['target_scope']!r}, run_id={self.run_id!r}"
            )
        request_started_at = runtime["failed_request_started_at"]
        failed_dispatch_id = runtime["failed_dispatch_id"]
        failed_request_assignment_fence = runtime["failed_request_assignment_fence"]
        failed_request_context_token = runtime["failed_request_context_token"]
        failed_request_stage = runtime["failed_request_stage"]
        failed_request_assignment_phase = runtime["failed_request_assignment_phase"]
        failed_request_assignment_reason = runtime["failed_request_assignment_reason"]
        failed_request_cache_phase = runtime["failed_request_cache_phase"]
        failed_request_event_time = runtime["failed_request_event_time"]
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT attempt_id, dispatch_id, target_scope, request_context_token, request_assignment_fence, "
                f"request_started_at, event_time, request_stage, execution_phase, execution_reason, attempt_sequence, "
                f"operation_name, attempt_state, access_key_fingerprint, http_status "
                f"FROM {runtime['request_attempts_table']} WHERE attempt_id=%s",
                (attempt_id,),
            )
            attempt_rows = cursor.fetchall()
        if len(attempt_rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires one failed-write execution attempt from the request ledger; no state changed: "
                f"attempt_id={attempt_id!r}, failed_dispatch_id={failed_dispatch_id!r}, "
                f"target_scope={target_scope!r}, rows={attempt_rows!r}"
            )
        attempt_row = attempt_rows[0]
        if not (
            str(attempt_row[0]) == attempt_id
            and str(attempt_row[1]) == failed_dispatch_id
            and str(attempt_row[2]) == target_scope
            and str(attempt_row[3]) == failed_request_context_token
            and str(attempt_row[4]) == failed_request_assignment_fence
            and str(attempt_row[5]) == request_started_at
            and str(attempt_row[6]) == failed_request_event_time
            and str(attempt_row[7]) == failed_request_stage
            and str(attempt_row[8]) == failed_request_assignment_phase
            and str(attempt_row[9]) == failed_request_assignment_reason
            and str(attempt_row[11]) == "put_backup_chunk"
            and str(attempt_row[12]) == "failed"
            and int(attempt_row[14]) == 403
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh candidate does not satisfy the complete failed-request identity contract; no state changed: "
                f"attempt_id={attempt_id!r}, target_scope={target_scope!r}, "
                f"operation={attempt_row[11]!r}, attempt_state={attempt_row[12]!r}"
            )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT job_id, target_scope, storage_uri, dispatch_id, http_status, access_key_fingerprint, "
                f"policy_decision, request_stage, request_started_at, event_time, request_assignment_fence, "
                f"request_context_token FROM {runtime['storage_audit_table']} "
                "WHERE dispatch_id=%s AND target_scope=%s AND http_status=403 "
                "AND request_stage=%s AND request_started_at=%s AND event_time=%s "
                "AND request_assignment_fence=%s AND request_context_token=%s",
                (
                    failed_dispatch_id,
                    target_scope,
                    failed_request_stage,
                    request_started_at,
                    failed_request_event_time,
                    failed_request_assignment_fence,
                    failed_request_context_token,
                ),
            )
            audit_rows = cursor.fetchall()
        if (
            len(audit_rows) != 1
            or str(audit_rows[0][3]) != str(attempt_row[1])
            or str(audit_rows[0][5]) != str(attempt_row[13])
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh request ledger does not map to one failed storage audit event; no state changed: "
                f"attempt_id={attempt_id!r}, failed_dispatch_id={failed_dispatch_id!r}, "
                f"request_started_at={request_started_at!r}, event_time={failed_request_event_time!r}, "
                f"audit_rows={audit_rows!r}"
            )
        if request_context_token != failed_request_context_token:
            raise _BrRefreshIdentityError(
                "BR binding refresh request context does not identify the failed request; no state changed: "
                f"supplied_context={request_context_token!r}, failed_context={failed_request_context_token!r}, "
                f"target_scope={target_scope!r}, request_route_token={request_route_token!r}, "
                f"request_cache_token={request_cache_token!r}"
            )
        supplied_phases = {
            "request_stage": request_stage,
            "assignment_phase": assignment_phase,
            "assignment_reason": assignment_reason,
            "cache_phase": cache_phase,
        }
        failed_phases = {
            "request_stage": failed_request_stage,
            "assignment_phase": failed_request_assignment_phase,
            "assignment_reason": failed_request_assignment_reason,
            "cache_phase": failed_request_cache_phase,
        }
        if supplied_phases != failed_phases:
            raise _BrRefreshIdentityError(
                "BR binding refresh execution phase does not identify the failed request; no state changed: "
                f"supplied={supplied_phases!r}, failed={failed_phases!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT route_token, dispatch_id, target_scope, executor_handle, lease_token, route_generation, "
                f"valid_from, valid_to, route_state, assignment_phase, route_reason, request_assignment_fence, request_context_token "
                f"FROM {runtime['dispatch_routes_table']} "
                "WHERE route_token=%s AND dispatch_id=%s AND target_scope=%s "
                "AND valid_from <= %s AND (valid_to IS NULL OR valid_to > %s) "
                "AND request_assignment_fence=%s AND request_context_token=%s",
                (
                    request_route_token,
                    failed_dispatch_id,
                    target_scope,
                    request_started_at,
                    request_started_at,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            route_rows = cursor.fetchall()
        if len(route_rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires the request-time route for the failed dispatch: "
                f"request_route_token={request_route_token!r}, failed_dispatch_id={failed_dispatch_id!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}, rows={route_rows!r}"
            )
        route_row = route_rows[0]
        if (
            str(route_row[11]) != request_assignment_fence
            or str(route_row[12]) != request_context_token
            or request_assignment_fence != failed_request_assignment_fence
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh route assignment fence/context is not the failed request identity; no state changed: "
                f"request_route_token={request_route_token!r}, supplied_fence={request_assignment_fence!r}, "
                f"supplied_context={request_context_token!r}, failed_fence={failed_request_assignment_fence!r}, "
                f"failed_context={failed_request_context_token!r}, route_fence={route_row[11]!r}, "
                f"route_context={route_row[12]!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        if (
            str(route_row[3]) != runtime["target_executor_handle"]
            or str(route_row[4]) != runtime["target_lease_token"]
            or int(route_row[5]) != 3001
            or str(route_row[8]) != "released"
            or str(route_row[9]) != assignment_phase
            or str(route_row[10]) != assignment_reason
            ):
            raise _BrRefreshIdentityError(
                "BR binding refresh route is not the failed request data-plane executor: "
                f"request_route_token={request_route_token!r}, failed_dispatch_id={failed_dispatch_id!r}, "
                f"target_scope={target_scope!r}, route={route_row!r}"
            )
        route_generation = int(route_row[5])
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT assignment_id, executor_handle, lease_token, assignment_generation, worker_handle, "
                f"target_scope, valid_from, valid_to, assignment_state "
                f"FROM {runtime['worker_registry_table']} "
                "WHERE executor_handle=%s AND lease_token=%s AND assignment_generation=%s "
                "AND target_scope=%s AND valid_from <= %s AND (valid_to IS NULL OR valid_to > %s)",
                (
                    runtime["target_executor_handle"],
                    runtime["target_lease_token"],
                    route_generation,
                    target_scope,
                    request_started_at,
                    request_started_at,
                ),
            )
            registry_rows = cursor.fetchall()
        if len(registry_rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires one request-time worker registry assignment: "
                f"request_route_token={request_route_token!r}, lease_token={runtime['target_lease_token']!r}, "
                f"assignment_generation={route_generation}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, rows={registry_rows!r}"
            )
        registry_row = registry_rows[0]
        if (
            str(registry_row[1]) != runtime["target_executor_handle"]
            or str(registry_row[2]) != runtime["target_lease_token"]
            or int(registry_row[3]) != route_generation
            or str(registry_row[4]) != runtime["target_worker_handle"]
            or str(registry_row[5]) != target_scope
            or str(registry_row[8]) != "active"
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh registry assignment is not the failed request identity: "
                f"request_route_token={request_route_token!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, registry={registry_row!r}"
            )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT lease_id, lease_token, assignment_generation, authority_epoch, worker_id, target_scope, change_ref, request_assignment_fence, request_context_token, execution_phase, execution_reason "
                f"FROM {runtime['worker_leases_table']} "
                "WHERE lease_token=%s AND assignment_generation=%s AND target_scope=%s "
                "AND valid_from <= %s AND (valid_to IS NULL OR valid_to > %s) "
                "AND request_assignment_fence=%s AND request_context_token=%s",
                (
                    runtime["target_lease_token"],
                    route_generation,
                    target_scope,
                    request_started_at,
                    request_started_at,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            worker_lease_rows = cursor.fetchall()
        if len(worker_lease_rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires one request-time worker lease identity: "
                f"request_route_token={request_route_token!r}, lease_token={runtime['target_lease_token']!r}, "
                f"assignment_generation={route_generation}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, rows={worker_lease_rows!r}"
            )
        worker_lease_row = worker_lease_rows[0]
        if (
            str(worker_lease_row[7]) != request_assignment_fence
            or str(worker_lease_row[8]) != request_context_token
            or str(worker_lease_row[9]) != assignment_phase
            or str(worker_lease_row[10]) != assignment_reason
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh worker lease fence/context does not identify the failed request; no state changed: "
                f"request_route_token={request_route_token!r}, supplied_fence={request_assignment_fence!r}, "
                f"supplied_context={request_context_token!r}, worker_lease_fence={worker_lease_row[7]!r}, "
                f"worker_lease_context={worker_lease_row[8]!r}, worker_lease_phase={worker_lease_row[9]!r}, "
                f"worker_lease_reason={worker_lease_row[10]!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}"
            )
        # r9: under epoch_from_observation the lease-table epoch columns lag the
        # controller's live promoted epoch, so the supplied epoch is verified
        # against the runtime live epoch instead of the stale table column.
        if runtime.get("epoch_from_observation"):
            if authority_epoch != runtime["live_authority_epoch"]:
                raise _BrRefreshIdentityError(
                    "BR binding refresh authority epoch does not identify the failed worker lease; no state changed: "
                    f"supplied_authority_epoch={authority_epoch!r}, request_route_token={request_route_token!r}, "
                    f"target={target!r}, target_scope={target_scope!r}, request_started_at={request_started_at!r}"
                )
        elif str(worker_lease_row[3]) != authority_epoch:
            raise _BrRefreshIdentityError(
                "BR binding refresh authority epoch does not identify the failed worker lease; no state changed: "
                f"supplied_authority_epoch={authority_epoch!r}, request_route_token={request_route_token!r}, "
                f"target={target!r}, target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        if (
            str(worker_lease_row[1]) != runtime["target_lease_token"]
            or int(worker_lease_row[2]) != route_generation
            or str(worker_lease_row[4]) != target
            or str(worker_lease_row[5]) != target_scope
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh worker lease is not the failed request identity: "
                f"request_route_token={request_route_token!r}, target={target!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}, "
                f"worker_lease={worker_lease_row!r}"
            )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT cache_token, route_token, target_scope, worker_handle, material_handle, cache_phase, "
                f"valid_from, valid_to, cache_state, change_ref, request_assignment_fence, request_context_token FROM {runtime['request_cache_table']} "
                "WHERE cache_token=%s AND target_scope=%s "
                "AND valid_from <= %s AND (valid_to IS NULL OR valid_to > %s) "
                "AND request_assignment_fence=%s AND request_context_token=%s",
                (
                    request_cache_token,
                    target_scope,
                    request_started_at,
                    request_started_at,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            rows = cursor.fetchall()
        if len(rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires one request cache snapshot joined to the failed route: "
                f"request_route_token={request_route_token!r}, request_cache_token={request_cache_token!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}, rows={rows!r}"
            )
        cache_row = rows[0]
        if str(cache_row[10]) != request_assignment_fence or str(cache_row[11]) != request_context_token:
            raise _BrRefreshIdentityError(
                "BR binding refresh request cache fence/context does not identify the failed request; no state changed: "
                f"request_route_token={request_route_token!r}, request_cache_token={request_cache_token!r}, "
                f"supplied_fence={request_assignment_fence!r}, cache_fence={cache_row[10]!r}, "
                f"supplied_context={request_context_token!r}, cache_context={cache_row[11]!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        if (
            str(cache_row[3]) != runtime["target_worker_handle"]
            or str(cache_row[4]) != runtime["target_material_handle"]
            or str(cache_row[5]) != cache_phase
            or str(cache_row[8]) != "serving"
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh request cache token is not the failed request assignment snapshot: "
                f"request_route_token={request_route_token!r}, request_cache_token={request_cache_token!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}, "
                f"worker_handle={cache_row[3]!r}, material_handle={cache_row[4]!r}, "
                f"cache_phase={cache_row[5]!r}, expected_cache_phase={cache_phase!r}, cache_state={cache_row[8]!r}"
            )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT material_handle, credential_id, target_scope, storage_uri, material_status, valid_from, valid_to "
                f"FROM {runtime['worker_materials_table']} WHERE material_handle=%s",
                (str(cache_row[4]),),
            )
            material_rows = cursor.fetchall()
        if len(material_rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires one material row for the failed request cache: "
                f"material_handle={cache_row[4]!r}, target_scope={target_scope!r}, rows={material_rows!r}"
            )
        material_row = material_rows[0]
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT grant_id, credential_id, grant_scope, grant_uri, grant_state, valid_from, valid_to "
                f"FROM {runtime['credential_grants_table']} WHERE grant_id IN (%s, %s)",
                (observed_authority_grant_id, desired_authority_grant_id),
            )
            grant_rows = cursor.fetchall()
        if len(grant_rows) != 2:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires distinct observed and desired authority grant rows: "
                f"observed_authority_grant_id={observed_authority_grant_id!r}, "
                f"desired_authority_grant_id={desired_authority_grant_id!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, rows={grant_rows!r}"
            )
        grants_by_id = {int(row[0]): row for row in grant_rows}
        observed_grant = grants_by_id[observed_authority_grant_id]
        desired_grant = grants_by_id[desired_authority_grant_id]

        def valid_at(grant: tuple) -> bool:
            grant_valid_from = str(grant[5])
            grant_valid_to = None if grant[6] is None else str(grant[6])
            return (
                str(grant[4]) == "active"
                and grant_valid_from <= request_started_at
                and (grant_valid_to is None or grant_valid_to > request_started_at)
            )

        if not (
            observed_authority_grant_id != desired_authority_grant_id
            and int(observed_grant[0]) == observed_authority_grant_id
            and int(observed_grant[1]) == int(material_row[1])
            and str(material_row[2]) == target_scope
            and valid_at(observed_grant)
            and not (str(observed_grant[2]) == target_scope and str(observed_grant[3]) == runtime["storage"])
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh observed authority grant does not identify the failed material's non-production authority; no state changed: "
                f"observed_authority_grant_id={observed_authority_grant_id!r}, material={material_row!r}, "
                f"grant={observed_grant!r}, target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        if not (
            int(desired_grant[0]) == desired_authority_grant_id
            and int(desired_grant[1]) == int(runtime["desired_credential_id"])
            and str(desired_grant[2]) == target_scope
            and str(desired_grant[3]) == runtime["storage"]
            and valid_at(desired_grant)
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh desired authority grant does not cover the failed production request; no state changed: "
                f"desired_authority_grant_id={desired_authority_grant_id!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, grant={desired_grant!r}"
            )
        if derive_desired_from_grants:
            with self._ensure_connection().cursor() as cursor:
                cursor.execute(
                    f"SELECT grant_id FROM {runtime['credential_grants_table']} "
                    "WHERE credential_id=%s AND grant_scope=%s AND grant_uri=%s AND grant_state='active' "
                    "AND valid_from<=%s AND (valid_to IS NULL OR valid_to>%s)",
                    (
                        int(runtime["desired_credential_id"]),
                        target_scope,
                        runtime["storage"],
                        request_started_at,
                        request_started_at,
                    ),
                )
                derived_grant_ids = [int(row[0]) for row in cursor.fetchall()]
            if derived_grant_ids != [desired_authority_grant_id]:
                raise _BrRefreshIdentityError(
                    "BR binding refresh desired authority grant is not the unique request-time-valid "
                    "production grant derived from the control-plane credential and the grants window; no state changed: "
                    f"desired_authority_grant_id={desired_authority_grant_id!r}, derived_grant_ids={derived_grant_ids!r}, "
                    f"desired_credential_id={int(runtime['desired_credential_id'])}, target_scope={target_scope!r}, "
                    f"request_started_at={request_started_at!r}"
                )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"SELECT lease_id, lease_token, assignment_generation, authority_epoch, target_scope, observed_grant_id, desired_grant_id, "
                f"observed_revision, desired_revision, lease_state, valid_from, valid_to, change_ref, request_assignment_fence, request_context_token, execution_phase, execution_reason "
                f"FROM {runtime['authority_leases_table']} WHERE lease_id=%s",
                (authority_lease_id,),
            )
            authority_lease_rows = cursor.fetchall()
        if len(authority_lease_rows) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh requires one authority grant lease row: "
                f"authority_lease_id={authority_lease_id!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, rows={authority_lease_rows!r}"
            )
        authority_lease = authority_lease_rows[0]
        if (
            str(authority_lease[13]) != request_assignment_fence
            or str(authority_lease[14]) != request_context_token
            or str(authority_lease[15]) != assignment_phase
            or str(authority_lease[16]) != assignment_reason
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh authority lease fence/context does not identify the failed request; no state changed: "
                f"authority_lease_id={authority_lease_id!r}, supplied_fence={request_assignment_fence!r}, "
                f"authority_fence={authority_lease[13]!r}, supplied_context={request_context_token!r}, "
                f"authority_context={authority_lease[14]!r}, authority_phase={authority_lease[15]!r}, "
                f"authority_reason={authority_lease[16]!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}"
            )
        change_refs = {
                "cache": str(cache_row[9]),
                "worker_lease": str(worker_lease_row[6]),
                "authority_lease": str(authority_lease[12]),
                "target": str(runtime["target_change_ref"]),
            }
        if len(set(change_refs.values())) != 1:
            raise _BrRefreshIdentityError(
                "BR binding refresh change_ref does not identify one rotation watch across the failed request cache, worker lease, and authority lease; no state changed: "
                f"request_route_token={request_route_token!r}, request_cache_token={request_cache_token!r}, "
                f"authority_lease_id={authority_lease_id!r}, change_refs={change_refs!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        if runtime.get("epoch_from_observation"):
            if authority_epoch != runtime["live_authority_epoch"]:
                raise _BrRefreshIdentityError(
                    "BR binding refresh authority epoch does not identify the failed authority lease; no state changed: "
                    f"supplied_authority_epoch={authority_epoch!r}, authority_lease_id={authority_lease_id!r}, "
                    f"target_scope={target_scope!r}, request_started_at={request_started_at!r}"
                )
        elif str(authority_lease[3]) != authority_epoch:
            raise _BrRefreshIdentityError(
                "BR binding refresh authority epoch does not identify the failed authority lease; no state changed: "
                f"supplied_authority_epoch={authority_epoch!r}, authority_lease_id={authority_lease_id!r}, "
                f"target_scope={target_scope!r}, request_started_at={request_started_at!r}"
            )
        lease_valid_from = str(authority_lease[10])
        lease_valid_to = None if authority_lease[11] is None else str(authority_lease[11])
        if not (
            int(authority_lease[0]) == authority_lease_id
            and str(authority_lease[1]) == runtime["target_lease_token"]
            and int(authority_lease[2]) == route_generation
            and str(authority_lease[4]) == target_scope
            and int(authority_lease[5]) == observed_authority_grant_id
            and int(authority_lease[6]) == (0 if derive_desired_from_grants else desired_authority_grant_id)
            and int(authority_lease[7]) < int(authority_lease[8])
            and str(authority_lease[9]) == "stale"
            and lease_valid_from <= request_started_at
            and (lease_valid_to is None or lease_valid_to > request_started_at)
        ):
            raise _BrRefreshIdentityError(
                "BR binding refresh authority grant lease is not the stale failed-request lease; no state changed: "
                f"authority_lease_id={authority_lease_id!r}, target_scope={target_scope!r}, "
                f"request_started_at={request_started_at!r}, lease={authority_lease!r}"
            )
        with self._ensure_connection().cursor() as cursor:
            # r9: under epoch_from_observation the row still carries the
            # pre-promotion epoch column, so the update matches on the stored
            # row epoch and converges the row onto the live promoted epoch.
            row_epoch = str(authority_lease[3])
            cursor.execute(
                f"UPDATE {runtime['authority_leases_table']} SET observed_grant_id=%s, observed_revision=%s, "
                "lease_state='converged', authority_epoch=%s WHERE lease_id=%s AND lease_token=%s AND assignment_generation=%s "
                "AND authority_epoch=%s AND target_scope=%s AND request_assignment_fence=%s AND request_context_token=%s",
                (
                    desired_authority_grant_id,
                    int(authority_lease[8]),
                    authority_epoch,
                    authority_lease_id,
                    runtime["target_lease_token"],
                    route_generation,
                    row_epoch,
                    target_scope,
                    request_assignment_fence,
                    request_context_token,
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    "SF06 authority grant lease refresh updated an unexpected row count: "
                    f"run_id={self.run_id!r}, authority_lease_id={authority_lease_id!r}, "
                    f"target_scope={target_scope!r}, rowcount={cursor.rowcount}"
                )
        previous = self._br_binding_propagation(runtime)[0]
        runtime["observed_binding_id"] = runtime["desired_binding_id"]
        runtime["observed_revision"] = runtime["desired_revision"]
        runtime["observed_material_handle"] = runtime["correct_material_handle"]
        runtime["request_cache_material_handle"] = runtime["correct_material_handle"]
        runtime["observed_access_key"] = runtime["correct_access_key"]
        runtime["observed_secret_key"] = runtime["correct_secret_key"]
        self._update_br_worker_lease(runtime)
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"UPDATE {runtime['request_cache_table']} "
                "SET cache_state='serving', change_ref=%s, request_assignment_fence=%s "
                "WHERE target_scope=%s AND cache_phase='retry_data_plane' "
                "AND cache_state='standby'",
                (
                    "br-rotation-watch-20260801-2359-refresh",
                    runtime["retry_assignment_fence"],
                    runtime["target_scope"],
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    "SF06 request material cache refresh updated an unexpected row count: "
                    f"run_id={self.run_id!r}, target_scope={runtime['target_scope']!r}, "
                    f"rowcount={cursor.rowcount}"
                )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                f"UPDATE {runtime['bindings_relation']} SET credential_id=%s "
                "WHERE binding_id=%s AND target_scope=%s AND role='primary' "
                "AND binding_state='effective'",
                (
                    int(runtime["desired_credential_id"]),
                    int(runtime["desired_binding_id"]),
                    runtime["target_scope"],
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    "SF06 effective binding refresh updated an unexpected row count: "
                    f"run_id={self.run_id!r}, binding_id={runtime['desired_binding_id']!r}, "
                    f"target_scope={runtime['target_scope']!r}, rowcount={cursor.rowcount}"
                )
        current = self._br_binding_propagation(runtime)[0]
        return {
            "acknowledged": True,
            "worker_id": target,
            "target_scope": target_scope,
            "authority_epoch": authority_epoch,
            "observed_authority_grant_id": observed_authority_grant_id,
            "desired_authority_grant_id": desired_authority_grant_id,
            "authority_lease_id": authority_lease_id,
            "request_assignment_fence": request_assignment_fence,
            "request_context_token": request_context_token,
            "previous": previous,
            "current": current,
        }

    def _update_br_worker_lease(self, runtime: Dict[str, Any]) -> None:
        row_epoch = runtime["target_authority_epoch"]
        # r9: under epoch_from_observation the converged worker lease also
        # advances onto the live promoted epoch.
        target_epoch = (
            runtime.get("live_authority_epoch")
            if runtime.get("epoch_from_observation")
            else row_epoch
        )
        sql = (
            f"UPDATE {runtime['worker_leases_table']} "
            "SET observed_binding_id=%s, observed_revision=%s, "
            "observed_material_handle=%s, lease_state='converged', "
            "authority_epoch=%s, last_heartbeat='2026-08-01 23:59:58' "
            "WHERE lease_id=%s AND lease_token=%s AND assignment_generation=%s "
                "AND authority_epoch=%s AND target_scope=%s AND request_assignment_fence=%s AND request_context_token=%s"
        )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(
                sql,
                (
                    int(runtime["desired_binding_id"]),
                    int(runtime["desired_revision"]),
                    runtime["correct_material_handle"],
                    target_epoch,
                    int(runtime["target_lease_id"]),
                    runtime["target_lease_token"],
                    int(runtime["target_assignment_generation"]),
                    row_epoch,
                    runtime["target_scope"],
                    runtime["target_assignment_fence"],
                    runtime["target_request_context"],
                ),
            )
            if cursor.rowcount != 1:
                raise RuntimeError(
                    "SF06 worker lease refresh updated an unexpected row count: "
                    f"run_id={self.run_id!r}, worker={runtime['target_worker']!r}, "
                    f"target_scope={runtime['target_scope']!r}, rowcount={cursor.rowcount}"
                )

    def _read_br_effective_binding(self, runtime: Dict[str, Any]) -> Dict[str, object]:
        sql = (
            f"SELECT b.binding_id, b.credential_id, b.role, b.binding_state, "
            f"b.effective_from, b.effective_to, b.change_ticket, "
            f"c.profile_name, c.status "
            f"FROM {runtime['bindings_relation']} b "
            f"JOIN {runtime['credentials_relation']} c ON c.credential_id = b.credential_id "
            "WHERE b.target_scope = %s AND b.binding_state = 'effective' "
            "ORDER BY b.effective_from DESC, b.binding_id DESC"
        )
        with self._ensure_connection().cursor() as cursor:
            cursor.execute(sql, (runtime["target_scope"],))
            rows = cursor.fetchall()
        if len(rows) != 1:
            raise RuntimeError(
                "SF06 effective BR runtime binding is not unique: "
                f"run_id={self.run_id!r}, target_scope={runtime['target_scope']!r}, rows={rows!r}"
            )
        row = rows[0]
        return {
            "binding_id": int(row[0]),
            "credential_id": int(row[1]),
            "role": str(row[2]),
            "binding_state": str(row[3]),
            "effective_from": str(row[4]),
            "effective_to": None if row[5] is None else str(row[5]),
            "change_ticket": str(row[6]),
            "profile_name": str(row[7]),
            "credential_status": str(row[8]),
        }

    def inspect_br_backup_state(self) -> Dict[str, object]:
        runtime = self._require_br_backup_runtime()
        objects = self._list_br_objects(runtime)
        return {
            "last_result": self._last_br_backup_result,
            "objects": list(objects),
            "object_count": len(objects),
            "has_backupmeta": any("backupmeta" in item.casefold() for item in objects),
            "desired_binding": self._read_br_effective_binding(runtime),
            "effective_binding": self._read_br_effective_binding(runtime),
            "propagation": self._br_binding_propagation(runtime),
            "storage_observations": self._br_storage_observations(runtime),
            "request_cache": self._br_request_cache_state(runtime),
        }

    @staticmethod
    def _br_job_result(result: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        if result is None:
            return None
        keys = (
            "status", "operation", "database", "table", "exit_code", "metrics",
            "attempt_id", "output", "error", "credential_source",
        )
        return {key: result[key] for key in keys if key in result}

    @staticmethod
    def _parse_br_metrics(output: str) -> Dict[str, object]:
        def integer(name: str, pattern: str) -> Optional[int]:
            match = re.search(pattern, output, re.IGNORECASE)
            return int(match.group(1)) if match else None

        checksum_values = re.findall(r"Checksum[^\n]*?([0-9]+(?:\.[0-9]+)?)%", output, re.IGNORECASE)
        return {
            "total_ranges": integer("total_ranges", r"total-ranges=(\d+)"),
            "ranges_succeed": integer("ranges_succeed", r"ranges-succeed=(\d+)"),
            "ranges_failed": integer("ranges_failed", r"ranges-failed=(\d+)"),
            "checksum_percent": float(checksum_values[-1]) if checksum_values else None,
        }

    def br_prefix_quarantine_state(self) -> Optional[Dict[str, object]]:
        """Current storage-guard quarantine state for the BR backup prefix."""
        runtime = self._require_br_backup_runtime()
        if not runtime.get("storage_prefix_quarantine"):
            return None
        return {
            "prefix": runtime["object_prefix"],
            "bucket": runtime["bucket"],
            "quarantine_ref": runtime["prefix_quarantine_ref"],
            "active": bool(runtime.get("prefix_quarantine_active")),
        }
