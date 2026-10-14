from dataclasses import dataclass
import json
from typing import Any, Sequence, Tuple


PG_SQL_RESULT_MAX_ROWS = 200


PG_AGENT_SQL_STATEMENT_TIMEOUT = '60s'


PG_AGENT_SQL_LOCK_TIMEOUT = '10s'


PG_SQL_RESULT_MAX_BYTES = 128 * 1024


PG_SQL_VALUE_MAX_CHARS = 2048


SQL_TRUNCATION_HINT = (
    "本次结果超过 128 KiB 已截断：仅返回部分行，超长字段被裁剪到 2048 字符。"
    "请缩小查询窗口后重试：只 SELECT 需要的列（避免对宽系统表使用 SELECT *），"
    "增加 WHERE 过滤或使用更小的 LIMIT，或改用 COUNT/SUM 等聚合；必要时分页逐段查看。"
)


SQL_TRUNCATION_HINT_EN = (
    "This result exceeded 128 KiB and was truncated: only some rows are returned, and overlong fields are cut to 2048 characters. "
    "Narrow the query window and retry: SELECT only the columns you need (avoid SELECT * on wide system tables), "
    "add WHERE filters or use a smaller LIMIT, or switch to aggregates such as COUNT/SUM; page through the result if necessary."
)

def _bound_sql_value(value: Any) -> Any:
    if isinstance(value, str) and len(value) > PG_SQL_VALUE_MAX_CHARS:
        return value[:PG_SQL_VALUE_MAX_CHARS] + "...[truncated]"
    if isinstance(value, bytes):
        return value[:PG_SQL_VALUE_MAX_CHARS].decode("utf-8", errors="replace") + "...[truncated]"
    if isinstance(value, (list, tuple)):
        return [_bound_sql_value(item) for item in value]
    if isinstance(value, dict):
        return {key: _bound_sql_value(item) for key, item in value.items()}
    return value


def _bound_sql_rows(rows: Sequence[Sequence[Any]]) -> tuple[list[list[Any]], bool]:
    bounded: list[list[Any]] = []
    encoded_bytes = 0
    truncated = len(rows) > PG_SQL_RESULT_MAX_ROWS
    for row in rows[:PG_SQL_RESULT_MAX_ROWS]:
        candidate = [_bound_sql_value(value) for value in row]
        row_bytes = len(json.dumps(candidate, default=str, ensure_ascii=False).encode("utf-8"))
        if bounded and encoded_bytes + row_bytes > PG_SQL_RESULT_MAX_BYTES:
            truncated = True
            break
        bounded.append(candidate)
        encoded_bytes += row_bytes
    return bounded, truncated


@dataclass(frozen=True)
class SqlConnectionSurface:
    """A scenario-registered SQL database exposed through execute_sql."""

    name: str
    database: str
    description: str
    query_examples: Tuple[str, ...]
    write_policy: str = "unrestricted"
