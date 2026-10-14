import ast
import importlib.util
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _imported_modules(path: Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if node.level:
                package = ".".join(path.relative_to(PROJECT_ROOT).with_suffix("").parts[:-1])
                module = importlib.util.resolve_name("." * node.level + module, package)
            modules.append(module)
    return tuple(modules)


def test_control_plane_packages_do_not_import_orchestration():
    violations = []
    for package in (
        PROJECT_ROOT / "src/agents",
        PROJECT_ROOT / "src/scenarios/evaluation",
        PROJECT_ROOT / "src/database",
        PROJECT_ROOT / "src/workloads",
        PROJECT_ROOT / "src/execution",
    ):
        for path in package.rglob("*.py"):
            for module in _imported_modules(path):
                if module == "src.scenarios.runtime" or module.startswith("src.scenarios.runtime."):
                    violations.append(f"{path}: {module}")
    assert violations == []


def test_shared_infrastructure_does_not_import_task_domains_or_benchmark():
    forbidden = ("src.scenarios", "src.persistent_scenarios", "src.benchmark")
    violations = []
    for name in ("database", "execution", "protocols", "workloads"):
        for path in (PROJECT_ROOT / "src" / name).rglob("*.py"):
            for module in _imported_modules(path):
                if any(module == prefix or module.startswith(prefix + ".") for prefix in forbidden):
                    violations.append(f"{path}: {module}")
    assert violations == []


def test_benchmark_execution_core_uses_target_adapters():
    shared_infrastructure = {"src.execution.host_ports"}
    forbidden = ("src.scenarios", "src.persistent_scenarios.backend", "src.execution")
    violations = []
    for name in ("planner.py", "runner.py", "isolation.py", "store.py", "aggregate.py"):
        path = PROJECT_ROOT / "src/benchmark" / name
        for module in _imported_modules(path):
            if module not in shared_infrastructure and any(module == prefix or module.startswith(prefix + ".") for prefix in forbidden):
                violations.append(f"{path}: {module}")
    assert violations == []
