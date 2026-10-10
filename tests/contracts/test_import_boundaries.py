import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]


def _imported_modules(path: Path) -> tuple[str, ...]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    modules = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
            modules.append(node.module)
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
