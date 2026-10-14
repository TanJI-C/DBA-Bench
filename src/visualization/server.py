"""Lightweight visualization server for AiOpsBench run traces.

Usage:
    python -m src.visualization.server [--port PORT] [--traces-dir DIR]
"""

import argparse
import json
import os
import re
import sys
from functools import partial
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
from socketserver import ThreadingMixIn
from urllib.parse import parse_qs, unquote, urlparse

from src.visualization.trace_index import TraceIndex
from src.visualization.experiment_index import ExperimentIndex
from src.visualization.dataset_index import DatasetIndex
from src.visualization.result_set_index import ResultSetIndex

STATIC_DIR = Path(__file__).parent / "static"

TASK_META_RE = re.compile(
    r'(<script[^>]*data-task-meta[^>]*>)(.*?)(</script>)',
    re.DOTALL,
)


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    allow_reuse_address = True
    daemon_threads = True


class VisualizationHandler(SimpleHTTPRequestHandler):
    """Serves static files and trace JSON API."""

    def __init__(
        self,
        *args,
        traces_dir: str = "traces",
        reports_dir: str = "docs/reports",
        artifacts_dir: str = "artifacts/experiments",
        datasets_dir: str = "datasets",
        results_dir: str = "results",
        human_console=None,
        human_runs=None,
        **kwargs,
    ):
        self.traces_dir = traces_dir
        self.reports_dir = reports_dir
        self.artifacts_dir = artifacts_dir
        self.datasets_dir = datasets_dir
        self.results_dir = results_dir
        self.human_console = human_console
        self.human_runs = human_runs
        self.project_root = Path(artifacts_dir).resolve().parents[1]
        super().__init__(*args, directory=str(STATIC_DIR), **kwargs)

    def address_string(self):
        """Skip reverse DNS lookup to avoid latency."""
        return self.client_address[0]

    def end_headers(self):
        self.send_header("Cache-Control", "no-cache")
        super().end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        if parsed.path.startswith("/api/human/"):
            self._human_api(parsed.path, post=False)
        elif parsed.path in ("/human", "/human/"):
            self._send_file(STATIC_DIR / "human.html")
        elif parsed.path == "/api/health":
            self._json_response({"status": "ok"})
        elif parsed.path == "/api/traces":
            self._list_traces(parse_qs(parsed.query))
        elif parsed.path.startswith("/api/traces/"):
            self._serve_trace(parsed.path)
        elif parsed.path == "/api/experiments":
            self._json_response(ExperimentIndex(self.artifacts_dir).list_experiments())
        elif parsed.path.startswith("/api/experiments/") and parsed.path.endswith("/runs"):
            self._list_experiment_runs(parsed.path, parse_qs(parsed.query))
        elif parsed.path == "/api/result-sets":
            self._result_set_api(())
        elif parsed.path.startswith("/api/result-sets/"):
            relative = unquote(parsed.path.removeprefix("/api/result-sets/")).strip("/")
            self._result_set_api(tuple(relative.split("/")))
        elif parsed.path == "/api/datasets":
            self._list_datasets()
        elif parsed.path.startswith("/api/datasets/"):
            self._dataset_api(parsed.path, parse_qs(parsed.query))
        elif self.path == "/api/reports":
            self._list_reports()
        elif self.path == "/api/tasks":
            self._list_tasks()
        elif self.path in ("/dashboard", "/dashboard/", "/reports", "/reports/"):
            self._serve_dashboard()
        elif self.path.startswith("/reports/"):
            self._serve_report()
        elif parsed.path.startswith("/artifacts/"):
            self._serve_artifact(parsed.path)
        elif parsed.path in ("/raw-traces", "/raw-traces/"):
            self._send_file(STATIC_DIR / "raw-traces.html")
        elif parsed.path in ("/experiments", "/experiments/"):
            self._send_file(STATIC_DIR / "experiments.html")
        elif parsed.path in ("/results", "/results/"):
            self._send_file(STATIC_DIR / "results.html")
        elif parsed.path in ("/datasets", "/datasets/"):
            self._send_file(STATIC_DIR / "datasets.html")
        else:
            super().do_GET()

    def do_POST(self):
        if self.path.startswith("/api/human/"):
            self._human_api(urlparse(self.path).path, post=True)
        elif self.path == "/api/tasks/toggle":
            self._toggle_task_hidden()
        elif self.path == "/api/tasks/update":
            self._update_task_meta()
        else:
            self.send_error(404, "Not found")

    def _human_api(self, path, *, post):
        from src.visualization.human_console import SessionConflict

        if self.human_console is None:
            self.send_error(503, "Human console is not enabled")
            return
        try:
            if post:
                origin = self.headers.get("Origin")
                if origin and urlparse(origin).netloc != self.headers.get("Host"):
                    self.send_error(403, "Cross-origin human actions are forbidden")
                    return
                body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            parts = path.removeprefix("/api/human/").strip("/").split("/")
            if parts == ["catalog"] and not post:
                result = self.human_runs.catalog()
            elif parts == ["runs"]:
                result = self.human_runs.launch(body) if post else self.human_runs.list_jobs()
            elif len(parts) == 3 and parts[0] == "runs" and parts[2] == "cancel" and post:
                result = self.human_runs.cancel(parts[1])
            elif parts == ["sessions"]:
                result = self.human_console.register(body) if post else self.human_console.list_sessions()
            elif len(parts) == 2 and parts[0] == "sessions" and not post:
                result = self.human_console.get(parts[1])
            elif len(parts) == 3 and parts[0] == "sessions":
                session_id, operation = parts[1:]
                if operation == "next" and not post:
                    result = {"action": self.human_console.next_action(session_id)}
                elif operation == "actions" and post:
                    result = self.human_console.enqueue(session_id, body)
                elif operation == "result" and post:
                    result = self.human_console.result(session_id, body)
                elif operation == "finish" and post:
                    result = self.human_console.finish(session_id, body)
                else:
                    self.send_error(404)
                    return
            else:
                self.send_error(404)
                return
        except SessionConflict as exc:
            self._json_response({"error": str(exc)}, status=409)
            return
        except (ValueError, TypeError, KeyError, StopIteration, RuntimeError) as exc:
            self._json_response({"error": f"请求失败：{exc}"}, status=400)
            return
        self._json_response(result)

    def do_OPTIONS(self):
        # CORS preflight for dashboard client-side fetch.
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def _list_traces(self, params):
        """List available trace files."""
        try:
            result = TraceIndex.for_directory(self.traces_dir).query(params)
        except ValueError as exc:
            self.send_error(400, str(exc))
            return
        self._json_response(result)

    def _serve_trace(self, request_path):
        """Serve a specific trace file."""
        relative = unquote(request_path.split("/api/traces/", 1)[1])
        raw = relative.endswith("/raw")
        filename = relative[:-4] if raw else relative
        filepath = Path(self.traces_dir) / filename
        if not filepath.exists() or not filepath.is_file():
            self.send_error(404, "Trace not found")
            return
        try:
            filepath.resolve().relative_to(Path(self.traces_dir).resolve())
        except ValueError:
            self.send_error(403, "Forbidden")
            return
        if raw:
            self._send_file(filepath)
            return
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as exc:
            self.send_error(422, f"Invalid trace JSON at line {exc.lineno}, column {exc.colno}: {filename}")
            return
        self._json_response(data)

    def _list_experiment_runs(self, request_path, params):
        experiment_id = unquote(request_path.removeprefix("/api/experiments/").removesuffix("/runs"))
        try:
            result = ExperimentIndex(self.artifacts_dir).query_runs(experiment_id, params)
        except FileNotFoundError as exc:
            self.send_error(404, str(exc))
            return
        except ValueError as exc:
            self.send_error(400, str(exc))
            return
        self._json_response(result)

    def _result_set_api(self, parts: tuple[str, ...]) -> None:
        index = ResultSetIndex(self.results_dir)
        try:
            if not parts:
                result = index.list_result_sets()
            elif len(parts) == 1:
                result = index.result_set(parts[0])
            elif len(parts) == 2 and parts[1] == "analysis":
                result = index.analysis(parts[0])
            elif len(parts) == 3 and parts[1] == "categories":
                result = index.category(parts[0], parts[2])
            else:
                self.send_error(404, "ResultSet endpoint not found")
                return
        except FileNotFoundError as exc:
            self.send_error(404, str(exc))
            return
        except (ValueError, KeyError, json.JSONDecodeError) as exc:
            self.send_error(422, str(exc))
            return
        self._json_response(result)

    def _dataset_index(self):
        return DatasetIndex(
            self.datasets_dir,
            self.artifacts_dir,
            self.project_root,
        )

    def _list_datasets(self):
        try:
            result = self._dataset_index().list_datasets()
        except (FileNotFoundError, ValueError) as exc:
            self.send_error(400, str(exc))
            return
        self._json_response(result)

    def _dataset_api(self, request_path, params):
        relative = unquote(request_path.removeprefix("/api/datasets/")).strip("/")
        try:
            if "/runs/" in relative:
                dataset_id, run_id = relative.split("/runs/", 1)
                attempt_text = params.get("attempt", [""])[0]
                if not attempt_text.isdigit() or int(attempt_text) < 1:
                    raise ValueError(
                        f"Dataset run detail requires a positive integer attempt; "
                        f"got {attempt_text!r}"
                    )
                result = self._dataset_index().run_detail(
                    dataset_id,
                    run_id,
                    int(attempt_text),
                )
            else:
                result = self._dataset_index().dataset(relative)
        except FileNotFoundError as exc:
            self.send_error(404, str(exc))
            return
        except (ValueError, json.JSONDecodeError) as exc:
            self.send_error(400, str(exc))
            return
        self._json_response(result)

    def _serve_artifact(self, request_path):
        prefix = "/artifacts/experiments/"
        if not request_path.startswith(prefix):
            self.send_error(404, "Artifact not found")
            return
        relative = unquote(request_path.removeprefix(prefix))
        filepath = (Path(self.artifacts_dir) / relative).resolve()
        try:
            filepath.relative_to(Path(self.artifacts_dir).resolve())
        except ValueError:
            self.send_error(403, "Forbidden")
            return
        if not filepath.is_file():
            self.send_error(404, "Artifact not found")
            return
        self._send_file(filepath)

    def _report_files(self):
        reports_path = Path(self.reports_dir)
        if not reports_path.exists():
            return []
        return sorted(reports_path.rglob("*.html"), key=lambda p: p.stat().st_mtime, reverse=True)

    def _list_reports(self):
        """List generated work-canvas reports."""
        files = [
            {
                "filename": f.relative_to(Path(self.reports_dir)).as_posix(),
                "url": f"/reports/{f.relative_to(Path(self.reports_dir)).as_posix()}",
                "mtime": f.stat().st_mtime,
            }
            for f in self._report_files()
        ]
        self._json_response(files)

    # ---- task overview API --------------------------------------------

    def _scan_task_metas(self) -> list[dict]:
        """Return [{path, title, status, updated, blocker, next, type, hidden, pinned}] for every report with a data-task-meta block."""
        reports_root = Path(self.reports_dir).resolve()
        candidates = list(reports_root.rglob("*.html"))
        seen: set[str] = set()
        out: list[dict] = []
        for f in candidates:
            if f.name == "project_dashboard.html":
                continue
            try:
                text = f.read_text(encoding="utf-8")
            except OSError:
                continue
            m = TASK_META_RE.search(text)
            if not m:
                continue
            try:
                data = json.loads(m.group(2).strip())
            except json.JSONDecodeError:
                continue
            rel = "/reports/" + str(f.relative_to(reports_root).as_posix())
            if rel in seen:
                continue
            seen.add(rel)
            out.append({
                "path": str(data.get("path", rel)),
                "title": str(data.get("title", f.stem)),
                "status": str(data.get("status", "running")),
                "updated": str(data.get("updated", "")),
                "blocker": str(data.get("blocker", "无")),
                "next": str(data.get("next", "")),
                "type": str(data.get("type", "")),
                "hidden": bool(data.get("hidden", False)),
                "pinned": bool(data.get("pinned", False)),
            })
        # Pinned tasks always float to the top, then by updated desc.
        out.sort(key=lambda r: (r["pinned"], r["updated"], r["title"]), reverse=True)
        return out

    def _list_tasks(self):
        self._json_response(self._scan_task_metas())

    def _toggle_task_hidden(self):
        def mutate(data, body):
            data["hidden"] = bool(body.get("hidden", not data.get("hidden", False)))
        self._mutate_task_meta(mutate)

    def _update_task_meta(self):
        # Body: {path, status?, notes?, needs_input?, pinned?, review_state?}
        # needs_input is the full list (client owns the array).
        def mutate(data, body):
            if "status" in body:
                data["status"] = str(body["status"])
            if "notes" in body:
                data["notes"] = str(body["notes"])
            if "needs_input" in body:
                ni = body["needs_input"]
                if isinstance(ni, list):
                    data["needs_input"] = [
                        {"text": str(item.get("text", "")), "done": bool(item.get("done", False))}
                        if isinstance(item, dict) else {"text": str(item), "done": False}
                        for item in ni
                    ]
            if "pinned" in body:
                data["pinned"] = bool(body["pinned"])
            if "review_state" in body:
                data["review_state"] = self._normalize_review_state(
                    body["review_state"]
                )
            data["updated"] = __import__("datetime").date.today().isoformat()
        self._mutate_task_meta(mutate)

    @staticmethod
    def _normalize_review_state(raw):
        if not isinstance(raw, dict):
            raise ValueError("review_state must be an object")
        if len(raw) > 200:
            raise ValueError("review_state contains too many entries")
        allowed_statuses = {"未确认", "通过", "需修缮", "暂缓"}
        normalized = {}
        for raw_key, raw_review in raw.items():
            key = str(raw_key)
            if not key or len(key) > 300 or not isinstance(raw_review, dict):
                raise ValueError("review_state contains an invalid case entry")
            status = str(raw_review.get("status", "未确认"))
            if status not in allowed_statuses:
                raise ValueError(f"invalid review status: {status}")
            note = str(raw_review.get("note", ""))
            if len(note) > 20_000:
                raise ValueError(f"review note is too long: {key}")
            normalized[key] = {
                "status": status,
                "definition": bool(raw_review.get("definition", False)),
                "dp": bool(raw_review.get("dp", False)),
                "outcome": bool(raw_review.get("outcome", False)),
                "sp": bool(raw_review.get("sp", False)),
                "note": note,
            }
        return normalized

    def _mutate_task_meta(self, mutate):
        # Dashboard / task editor both call this; mutate(data, body)
        # edits the parsed JSON in place. Server rewrites the data-task-meta
        # block and returns the freshly scanned list.
        length = int(self.headers.get("Content-Length", 0) or 0)
        try:
            body = json.loads(self.rfile.read(length) or b"{}")
        except json.JSONDecodeError:
            self.send_error(400, "Body must be JSON")
            return
        rel = str(body.get("path", "")).lstrip("/")
        if rel.startswith("reports/"):
            rel = rel[len("reports/"):]
        if not rel:
            self.send_error(400, "path is required")
            return
        filepath = (Path(self.reports_dir) / rel).resolve()
        try:
            filepath.relative_to(Path(self.reports_dir).resolve())
        except ValueError:
            self.send_error(403, "Forbidden")
            return
        if not filepath.is_file():
            self.send_error(404, "Report not found")
            return
        try:
            text = filepath.read_text(encoding="utf-8")
        except OSError as exc:
            self.send_error(500, f"Read failed: {exc}")
            return
        m = TASK_META_RE.search(text)
        if not m:
            self.send_error(404, "Task meta block not found in target report")
            return
        try:
            data = json.loads(m.group(2).strip())
        except json.JSONDecodeError:
            self.send_error(500, "Task meta JSON is malformed")
            return
        try:
            mutate(data, body)
        except ValueError as exc:
            self.send_error(400, str(exc))
            return
        new_block = json.dumps(data, ensure_ascii=False, indent=2)
        new_text = text[:m.start(2)] + "\n" + new_block + "\n        " + text[m.end(2):]
        try:
            filepath.write_text(new_text, encoding="utf-8")
        except OSError as exc:
            self.send_error(500, f"Write failed: {exc}")
            return
        self._json_response(self._scan_task_metas())

    def _serve_dashboard(self):
        dashboard = Path(self.reports_dir) / "project_dashboard.html"
        if dashboard.is_file():
            self._send_file(dashboard)
            return
        legacy = Path(self.reports_dir) / "project_work_canvas.html"
        if legacy.is_file():
            self._send_file(legacy)
            return
        self.send_error(404, "No project dashboard found")

    def _serve_report(self):
        filename = unquote(self.path.split("/reports/", 1)[1].split("?", 1)[0])
        filepath = Path(self.reports_dir) / filename
        if not filepath.exists() or not filepath.is_file():
            self.send_error(404, "Report not found")
            return
        try:
            filepath.resolve().relative_to(Path(self.reports_dir).resolve())
        except ValueError:
            self.send_error(403, "Forbidden")
            return
        self._send_file(filepath)

    def _send_file(self, filepath):
        import mimetypes

        body = filepath.read_bytes()
        mime, _ = mimetypes.guess_type(str(filepath))
        content_type = mime or "application/octet-stream"
        if content_type.startswith("text/") and "charset" not in content_type:
            content_type = f"{content_type}; charset=utf-8"
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _json_response(self, data, status=200):
        """Send a JSON response."""
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description="AiOpsBench Visualization Server")
    parser.add_argument("--port", type=int, default=9235)
    parser.add_argument("--traces-dir", default="logs/traces")
    parser.add_argument("--reports-dir", default="docs/reports")
    parser.add_argument("--artifacts-dir", default="artifacts/experiments")
    parser.add_argument("--datasets-dir", default="datasets")
    parser.add_argument("--results-dir", default="results")
    args = parser.parse_args()

    from src.visualization.human_console import HumanConsole
    from src.visualization.human_runs import HumanRuns
    root = Path(__file__).resolve().parents[2]

    handler = partial(
        VisualizationHandler,
        traces_dir=args.traces_dir,
        reports_dir=args.reports_dir,
        artifacts_dir=args.artifacts_dir,
        datasets_dir=args.datasets_dir,
        results_dir=args.results_dir,
        human_console=HumanConsole(root / "artifacts/human-console/sessions"),
        human_runs=HumanRuns(root, f"http://127.0.0.1:{args.port}"),
    )
    server = ThreadedHTTPServer(("0.0.0.0", args.port), handler)
    print(f"Visualization server running at http://localhost:{args.port}")
    print(f"Serving traces from: {os.path.abspath(args.traces_dir)}")
    print(f"Serving reports from: {os.path.abspath(args.reports_dir)}")
    print(f"Serving experiments from: {os.path.abspath(args.artifacts_dir)}")
    print(f"Serving datasets from: {os.path.abspath(args.datasets_dir)}")
    print(f"Serving result sets from: {os.path.abspath(args.results_dir)}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
        server.shutdown()


if __name__ == "__main__":
    main()
