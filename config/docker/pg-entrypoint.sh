#!/bin/bash
# 容器 entrypoint：初始化环境后以 postgres 用户启动 PG，然后保持容器存活
# PG 崩溃不影响容器运行，agent 可继续在容器内操作

PGDATA=${PGDATA:-/var/lib/postgresql/data_fat}
POSTGRES_RUNTIME_OPTIONS=${POSTGRES_RUNTIME_OPTIONS:-"-c shared_buffers=64MB -c work_mem=8MB -c shared_preload_libraries=pg_stat_statements -c logging_collector=on -c log_destination=stderr -c log_directory=/var/log/postgresql -c log_filename=postgresql-%Y-%m-%d_%H%M%S.log -c log_rotation_age=1d -c log_rotation_size=100MB"}
PG_NOFILE_LIMIT=${PG_NOFILE_LIMIT:-}
if [ -z "$PG_NOFILE_LIMIT" ] && [ -f /etc/aiopsbench_pg_nofile_limit ]; then
    PG_NOFILE_LIMIT=$(cat /etc/aiopsbench_pg_nofile_limit)
fi
# 自动探测 PG 主版本路径，兼容 15/16 等不同胖镜像
PG_BIN=$(ls -d /usr/lib/postgresql/*/bin 2>/dev/null | sort -V | tail -1)
if [ -z "$PG_BIN" ] || [ ! -x "$PG_BIN/pg_ctl" ]; then
    echo "[entrypoint] ERROR: pg_ctl not found under /usr/lib/postgresql/*/bin" >&2
    exit 1
fi
echo "[entrypoint] Using PG_BIN=$PG_BIN"

# 确保日志目录存在
mkdir -p /var/log/postgresql
chown postgres:postgres /var/log/postgresql
touch /var/log/postgresql/postgresql.log
chown postgres:postgres /var/log/postgresql/postgresql.log

# 以 postgres 用户启动 PG 服务
if [ -n "$PG_NOFILE_LIMIT" ]; then
    echo "[entrypoint] Applying PostgreSQL nofile soft limit: $PG_NOFILE_LIMIT"
    su - postgres -c "ulimit -n $PG_NOFILE_LIMIT && $PG_BIN/pg_ctl start -D $PGDATA -l /var/log/postgresql/postgresql.log -o \"$POSTGRES_RUNTIME_OPTIONS\""
else
    su - postgres -c "$PG_BIN/pg_ctl start -D $PGDATA -l /var/log/postgresql/postgresql.log -o \"$POSTGRES_RUNTIME_OPTIONS\""
fi

# 保持容器存活（PG 崩溃不影响容器）
exec tail -f /var/log/postgresql/postgresql.log
