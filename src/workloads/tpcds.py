"""TPC-DS workloads, query source and schema-map transformations."""
import json
import hashlib
import os
import random
import re
from functools import lru_cache
from typing import List

from .base import BaseWorkload
from src.workloads.specs import WorkloadProfile


LIGHT_IDS = [
    1, 3, 4, 7, 8, 9, 11, 12, 13, 15, 16, 17, 18, 19, 20, 21, 22, 24, 25, 26, 27, 28,
    29, 30, 32, 34, 36, 37, 39, 40, 41, 42, 43, 44, 45, 46, 48, 50, 52, 53, 55, 59,
    61, 62, 63, 65, 66, 67, 68, 70, 73, 74, 79, 81, 82, 84, 85, 86, 88, 89, 90, 91,
    92, 93, 94, 96, 98, 99,
]
MEDIUM_IDS = [2, 6, 10, 31, 35, 38, 47, 51, 57, 64, 69, 71, 76, 87, 95, 97]
HEAVY_IDS = [5, 14, 23, 33, 49, 54, 56, 58, 60, 72, 75, 77, 78, 80, 83]

_QUERY_FILE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "workloads", "tpcds", "queries", "query_0.sql",
)
_PATTERN = re.compile(
    r"-- start query \d+ in stream 0 using template query(\d+)\.tpl\n"
    r"(.*?)"
    r"-- end query \d+ in stream 0 using template query\d+\.tpl",
    re.DOTALL,
)
# 把 `... + <N> days` / `+ <N> minutes` / `+ <N> hours` 转 PG interval 字面。
# TPC-DS 里只出现 days/minutes/hours（没有 weeks/months/years 变体，PG 这些支持关键字）。
_PG_INTERVAL_FIX = re.compile(r"(\+)\s+(\d+)\s+(days?|minutes?|hours?)", re.IGNORECASE)
_cache: dict = None


def _parse_queries() -> dict:
    global _cache
    if _cache is not None:
        return _cache
    if not os.path.exists(_QUERY_FILE):
        raise FileNotFoundError(
            "TPC-DS query text is not distributed with the repository; fetch it"
            f" per docs/getting-started.md and place query_0.sql at {_QUERY_FILE}"
        )
    with open(_QUERY_FILE, encoding="utf-8") as f:
        text = f.read()
    parsed = {}
    for tpl, body in _PATTERN.findall(text):
        sql = body.strip()
        # 一次性转 PG 兼容，后续直接用
        sql = _PG_INTERVAL_FIX.sub(lambda m: f"{m.group(1)} interval '{m.group(2)} {m.group(3)}'", sql)
        parsed[f"q{tpl}"] = sql
    _cache = parsed
    return _cache


def get_tpcds_query(name: str) -> str:
    """Return SQL body for TPC-DS query 'qN' (e.g. 'q75').

    Raises KeyError if name not found in query_0.sql.
    """
    queries = _parse_queries()
    if name not in queries:
        sample = sorted(queries.keys())[:5]
        raise KeyError(f"TPC-DS query {name!r} not found. Sample available: {sample}")
    return queries[name]


def get_tpcdsx_query(name: str) -> str:
    """Return TPC-DS query text rewritten to the tpcdsx schema."""
    return obfuscate_tpcds_sql(get_tpcds_query(name))


def available_queries() -> list:
    """Return sorted list of all available TPC-DS query names (e.g. ['q1', 'q2', ...])."""
    return sorted(_parse_queries().keys(), key=lambda n: int(n[1:]))

_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
_MAP_PATH = os.path.join(_PROJECT_ROOT, "data", "workloads", "tpcdsx", "schema_map.json")


@lru_cache(maxsize=1)
def load_tpcdsx_schema_map() -> dict:
    with open(_MAP_PATH, encoding="utf-8") as f:
        return json.load(f)


@lru_cache(maxsize=1)
def _identifier_map() -> dict:
    schema_map = load_tpcdsx_schema_map()
    pairs = {}
    pairs.update(schema_map["tables"])
    pairs.update(schema_map.get("indexes", {}))
    for old, new in schema_map["columns"].items():
        old_col = old.rsplit(".", 1)[1]
        new_col = new.rsplit(".", 1)[1]
        pairs[old_col] = new_col
    return pairs


@lru_cache(maxsize=1)
def _identifier_pattern():
    names = sorted(_identifier_map(), key=len, reverse=True)
    return re.compile(r"(?<![A-Za-z0-9_])(" + "|".join(map(re.escape, names)) + r")(?![A-Za-z0-9_])")


def obfuscate_tpcds_sql(sql: str) -> str:
    pairs = _identifier_map()
    return _identifier_pattern().sub(lambda match: pairs[match.group(1)], sql)

def _build_default_mix() -> List[WorkloadProfile]:
    """默认 mix 从 query_0.sql 自动抽样。

    配额 5 LIGHT（68 选 5）+ 3 MEDIUM（16 选 3）+ 1 HEAVY（15 选 1）。
    HEAVY 进默认 mix 是关键：topsql 按 total_ms 排序，runner 跑慢 SQL 才能进 top 10；
    topsql 应以记录慢查询为主，所以让 runner 主动制造慢 SQL 而不改算法。
    LIGHT 减到 5 是为了让 MEDIUM/HEAVY 占更多 round-robin 份额（6 worker × MEDIUM/HEAVY qps 0.3-0.5 → 180s 跑 30+ exec）。
    """
    rng = random.Random(0xA10B)  # 固定种子，保证默认 mix 可复现
    light_sample = rng.sample(LIGHT_IDS, 5)
    medium_sample = rng.sample(MEDIUM_IDS, 3)
    heavy_sample = rng.sample(HEAVY_IDS, 1)
    profiles = []
    for qid in light_sample:
        profiles.append(WorkloadProfile(
            name=f"tpcds_q{qid}",
            sql=get_tpcds_query(f"q{qid}"),
            qps=round(rng.uniform(0.3, 0.6), 3),
            tier="LIGHT",
        ))
    for qid in medium_sample:
        profiles.append(WorkloadProfile(
            name=f"tpcds_q{qid}",
            sql=get_tpcds_query(f"q{qid}"),
            # MEDIUM 0.1-0.2 qps × 6 worker → 每条 MEDIUM 180s 跑 12+ exec，
            # 单次 3-8s × 12 ≈ 40-100s total_ms → 进 topsql top 10。
            # qps 上限受内存约束：6 worker × 3 MEDIUM 同时跑，更高 qps 会把 512MB 的 PG 打到 OOM。
            qps=round(rng.uniform(0.1, 0.2), 3),
            tier="MEDIUM",
        ))
    for qid in heavy_sample:
        profiles.append(WorkloadProfile(
            name=f"tpcds_q{qid}",
            sql=get_tpcds_query(f"q{qid}"),
            # HEAVY 0.1 qps × 6 worker → 180s 跑 6+ exec，
            # 单次 5-12s × 6 ≈ 30-70s total_ms → 进 topsql top 5。
            # qps=0.1 即每 10s 一条 HEAVY，6 worker 同时 6 个 HEAVY 跑也是 6×5-12s 占满 1CPU/512MB。
            qps=0.1,
            tier="HEAVY",
        ))
    return profiles


def default_mix() -> tuple[WorkloadProfile, ...]:
    """构建默认 TPC-DS mix，首次调用时才解析 query_0.sql。

    查询原文不随仓库分发（见 docs/getting-started.md），模块导入不得依赖它；
    没有查询文本时，只有真正构建 TPC-DS 负载的路径会在此处报错。
    """
    return tuple(_build_default_mix())


class TPCDSWorkload(BaseWorkload):
    """
    TPC-DS 工作负载。
    负责自动下载 tpcds-kit，编译并生成 TPC-DS 数据（SCALE=1）。
    生成 init.sql 以在 PostgreSQL 中建表并导入数据。
    """
    def __init__(self, workload_root: str = None, scale: int = 1):
        super().__init__("tpcds", workload_root)
        self.manifest_path = os.path.join(self.workload_dir, "runtime", "manifest.json")
        self.scale = scale
        # 16GB: the continuous-ops episodes coexist a 64MB max_wal_size fault
        # with a WAL-retention slot; pg_wal cannot recycle past the slot and
        # legitimately grows past the previous ceilings; zero-agent gates accumulate the most.
        self.disk_quota_mb = 32768
        self.tpcds_kit_dir = os.path.join(self.workload_dir, "tpcds-kit")
        self.tools_dir = os.path.join(self.tpcds_kit_dir, "tools")

    REQUIRED_TABLES = (
        "dbgen_version", "customer_address", "customer_demographics", "date_dim",
        "warehouse", "ship_mode", "time_dim", "reason", "income_band", "item",
        "store", "call_center", "customer", "web_site", "store_returns",
        "household_demographics", "web_page", "promotion", "catalog_page",
        "inventory", "catalog_returns", "web_returns", "web_sales", "catalog_sales", "store_sales",
    )

    def prepare(self):
        print(f"[Workload:TPCDSWorkload] Preparing TPC-DS workload at {self.workload_dir} (SCALE={self.scale})")
        self.ensure_dir(self.workload_dir)
        self.ensure_dir(self.data_dir)

        required_data_paths = {
            table: os.path.join(self.data_dir, f"{table}.dat")
            for table in self.REQUIRED_TABLES
        }
        dataset_ready = all(
            os.path.isfile(path) and os.path.getsize(path) > 0
            for path in required_data_paths.values()
        )

        # A checked-in or pre-generated dataset is a complete local artifact;
        # only incomplete data requires the generator toolchain.
        dsdgen_path = os.path.join(self.tools_dir, "dsdgen")
        if not dataset_ready and not os.path.exists(dsdgen_path):
            print("[Workload:TPCDSWorkload] dsdgen not found, compiling tpcds-kit...")
            if not os.path.exists(self.tpcds_kit_dir):
                import subprocess
                print("[Workload:TPCDSWorkload] Cloning tpcds-kit repository...")
                subprocess.run(
                    ["git", "clone", "https://github.com/gregrahn/tpcds-kit.git"],
                    cwd=self.workload_dir, check=True
                )
            print("[Workload:TPCDSWorkload] Building tpcds-kit...")
            import subprocess
            subprocess.run(["make", "clean"], cwd=self.tools_dir, check=False)
            subprocess.run(
                ["make", "OS=LINUX", "CFLAGS=-O3 -fcommon -D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE -DYYDEBUG -DLINUX -g -Wall", "-j4"],
                cwd=self.tools_dir, check=True
            )

        # 2. Check if data exists, if not generate
        store_sales_dat = required_data_paths["store_sales"]
        if not dataset_ready:
            print(f"[Workload:TPCDSWorkload] Generating TPC-DS data (SCALE={self.scale}) into {self.data_dir}...")
            import subprocess
            rel_data_dir = os.path.relpath(self.data_dir, self.tools_dir)
            subprocess.run(
                ["./dsdgen", "-SCALE", str(self.scale), "-DIR", rel_data_dir, "-DISTRIBUTIONS", "tpcds.idx", "-TERMINATE", "N", "-FORCE"],
                cwd=self.tools_dir, check=True
            )
            if not os.path.exists(store_sales_dat):
                raise RuntimeError(f"TPC-DS data generation did not create {store_sales_dat}")
        for name in os.listdir(self.data_dir):
            if name.endswith(".dat"):
                os.chmod(os.path.join(self.data_dir, name), 0o644)

        # 3. Generate init.sql when the source kit is available; otherwise an
        # existing generated schema is the required local artifact.
        init_sql_path = self.get_init_sql_path()
        schema_path = os.path.join(self.tools_dir, "tpcds.sql")
        if os.path.isfile(schema_path):
            self._generate_init_sql()
        elif not os.path.isfile(init_sql_path):
            raise FileNotFoundError(
                "TPC-DS schema source is unavailable: "
                f"schema_path={schema_path}, init_sql_path={init_sql_path}"
            )

        data_files = {}
        for table in self.REQUIRED_TABLES:
            path = os.path.join(self.data_dir, f"{table}.dat")
            if not os.path.isfile(path) or os.path.getsize(path) == 0:
                raise RuntimeError(
                    "TPC-DS dataset file is missing or empty: "
                    f"scale={self.scale}, table={table!r}, path={path}"
                )
            data_files[f"{table}.dat"] = {
                "size_bytes": os.path.getsize(path),
                "sha256": self._sha256(path),
            }
        schema_source = "tpcds.sql" if os.path.isfile(schema_path) else "init.sql"
        schema_digest = self._sha256(schema_path if schema_source == "tpcds.sql" else init_sql_path)
        manifest = {
            "workload_name": self.workload_name,
            "scale": self.scale,
            "required_tables": list(self.REQUIRED_TABLES),
            "data_files": data_files,
            "init_sql": os.path.relpath(init_sql_path, os.path.dirname(self.manifest_path)),
            "init_sql_sha256": self._sha256(init_sql_path),
            "schema_sha256": schema_digest,
            "schema_source": schema_source,
        }
        manifest["dataset_fingerprint"] = hashlib.sha256(
            json.dumps(manifest, ensure_ascii=True, sort_keys=True).encode("utf-8")
        ).hexdigest()
        self.save_manifest(manifest)
        print(f"[Workload:TPCDSWorkload] Ready.")

    @staticmethod
    def _sha256(path: str) -> str:
        digest = hashlib.sha256()
        with open(path, "rb") as stream:
            for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def validate_database(self, env) -> None:
        payload = env.execute_sql(
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = 'public' AND table_name = ANY(ARRAY["
            + ",".join("'" + table + "'" for table in self.REQUIRED_TABLES)
            + "]) ORDER BY table_name;"
        )
        if isinstance(payload, str):
            payload = json.loads(payload)
        if not isinstance(payload, dict) or payload.get("status") != "success":
            raise RuntimeError(
                "TPC-DS database schema readiness probe failed: "
                f"scale={self.scale}, result={payload!r}"
            )
        rows = payload.get("result")
        if not isinstance(rows, list):
            raise TypeError(f"TPC-DS schema readiness result must be a list: result={payload!r}")
        actual_tables = {row[0] for row in rows if isinstance(row, list) and len(row) == 1}
        expected_tables = set(self.REQUIRED_TABLES)
        if actual_tables != expected_tables:
            raise RuntimeError(
                "TPC-DS database schema readiness mismatch: "
                f"scale={self.scale}, missing={sorted(expected_tables - actual_tables)}, "
                f"unexpected={sorted(actual_tables - expected_tables)}"
            )
        count_payload = env.execute_sql("SELECT count(*) FROM customer;")
        if isinstance(count_payload, str):
            count_payload = json.loads(count_payload)
        if not isinstance(count_payload, dict) or count_payload.get("status") != "success":
            raise RuntimeError(
                "TPC-DS customer row readiness probe failed: "
                f"scale={self.scale}, result={count_payload!r}"
            )
        count_rows = count_payload.get("result")
        if not isinstance(count_rows, list) or len(count_rows) != 1 or not isinstance(count_rows[0], list) or len(count_rows[0]) != 1:
            raise ValueError(f"TPC-DS customer readiness result has an invalid shape: result={count_payload!r}")
        if int(count_rows[0][0]) <= 0:
            raise RuntimeError(
                "TPC-DS customer table is empty after deployment: "
                f"scale={self.scale}, count={count_rows[0][0]}"
            )

    def _generate_init_sql(self):
        tpcds_sql_path = os.path.join(self.tools_dir, "tpcds.sql")
        if not os.path.exists(tpcds_sql_path):
            raise FileNotFoundError(f"Schema file not found: {tpcds_sql_path}")
            
        with open(tpcds_sql_path, "r") as f:
            schema_sql = f.read()

        tables = self.REQUIRED_TABLES

        init_sql = "-- TPC-DS Initialization\n\n"
        init_sql += schema_sql
        init_sql += "\n\n-- Data Loading\n"

        for table in tables:
            dat_file = f"/workload_data/{table}.dat"
            init_sql += f"COPY {table} FROM '{dat_file}' WITH (FORMAT csv, DELIMITER '|', NULL '');\n"

        # Also generate primary keys / foreign keys ?
        # For simplicity, we just add the COPY commands. TPC-DS constraints are usually added after loading for performance.
        # tpcds.sql already defines tables but NO primary keys to speed up loading. We can add tpcds_ri.sql later if needed.

        init_sql_path = self.get_init_sql_path()
        with open(init_sql_path, "w") as f:
            f.write(init_sql)
        os.chmod(init_sql_path, 0o644)
        print(f"[Workload:TPCDSWorkload] Generated init.sql: {init_sql_path}")


class TPCDSXWorkload(TPCDSWorkload):
    """TPC-DS data with obfuscated retail-neutral schema names."""

    def __init__(self, workload_root: str = None, scale: int = 1):
        BaseWorkload.__init__(self, "tpcdsx", workload_root)
        self.manifest_path = os.path.join(self.workload_dir, "runtime", "manifest.json")
        self.scale = scale
        self.disk_quota_mb = 8192
        self.source_workload = TPCDSWorkload(workload_root, scale)
        self.source_workload_dir = self.source_workload.workload_dir
        self.data_dir = self.source_workload.data_dir
        self.tpcds_kit_dir = self.source_workload.tpcds_kit_dir
        self.tools_dir = self.source_workload.tools_dir

    def prepare(self):
        self.source_workload.prepare()
        self.ensure_dir(self.workload_dir)
        self._generate_init_sql()
        source_manifest = self.source_workload.load_manifest()
        if source_manifest is None:
            raise RuntimeError(
                "TPC-DSX source workload did not produce a manifest: "
                f"path={self.source_workload.manifest_path}"
            )
        manifest = {
            **source_manifest,
            "workload_name": self.workload_name,
            "init_sql": os.path.relpath(self.get_init_sql_path(), os.path.dirname(self.manifest_path)),
            "init_sql_sha256": self._sha256(self.get_init_sql_path()),
            "source_workload": self.source_workload.workload_name,
        }
        manifest.pop("dataset_fingerprint", None)
        manifest["dataset_fingerprint"] = hashlib.sha256(
            json.dumps(manifest, ensure_ascii=True, sort_keys=True).encode("utf-8")
        ).hexdigest()
        self.save_manifest(manifest)
        print("[Workload:TPCDSXWorkload] Ready.")

    def _generate_init_sql(self):
        tpcds_sql_path = os.path.join(self.tools_dir, "tpcds.sql")
        if not os.path.exists(tpcds_sql_path):
            raise FileNotFoundError(f"Schema file not found: {tpcds_sql_path}")

        with open(tpcds_sql_path, "r") as f:
            schema_sql = obfuscate_tpcds_sql(f.read())

        schema_map = load_tpcdsx_schema_map()
        init_sql = "-- TPC-DSX Initialization\n\n"
        init_sql += schema_sql
        init_sql += "\n\n-- Data Loading\n"

        for old_table, new_table in schema_map["tables"].items():
            dat_file = f"/workload_data/{old_table}.dat"
            init_sql += f"COPY {new_table} FROM '{dat_file}' WITH (FORMAT csv, DELIMITER '|', NULL '');\n"

        init_sql_path = self.get_init_sql_path()
        with open(init_sql_path, "w") as f:
            f.write(init_sql)
        os.chmod(init_sql_path, 0o644)
        print(f"[Workload:TPCDSXWorkload] Generated init.sql: {init_sql_path}")
