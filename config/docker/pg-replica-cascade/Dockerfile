FROM postgres:16

# The scenario uses the upstream PostgreSQL server and its real replication,
# lock-manager, and pg_stat_statements implementations.  No metric generator
# or fault-specific wait_event shim is included in the image.
RUN mkdir -p /opt/aiopsbench/replica-cascade \
    && chown -R postgres:postgres /opt/aiopsbench/replica-cascade
