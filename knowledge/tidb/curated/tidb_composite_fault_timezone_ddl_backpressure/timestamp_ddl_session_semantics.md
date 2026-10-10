# Timestamp DDL and session time semantics

## Timestamp defaults are session-sensitive

Temporal DDL must be read together with the session and server time-zone
settings that interpret it. A lower-bound `TIMESTAMP` default can be accepted
in one session and rejected by a downstream MySQL-compatible session when the
same displayed literal maps outside the downstream type's valid range. The
database name or the fact that both endpoints report a running status does not
remove this semantic difference.

## Cross-endpoint diagnosis

Compare the upstream DDL text, the upstream session time zone, the downstream
session and global time zones, and the downstream error. `SHOW CREATE TABLE`
and `INFORMATION_SCHEMA.COLUMNS` should be used after repair to check the
column type, nullability, and default. The accepted downstream definition may
render the same UTC instant with a local clock value; compare the instant and
column contract, not only the literal spelling.

## Scoped repair

Use a connection-local time-zone setting for a diagnostic DDL probe when that
is needed. Do not change a global time zone to make one replicated DDL appear
valid. The schema repair must be limited to the affected downstream object and
must be verified before the replication feed is resumed.
