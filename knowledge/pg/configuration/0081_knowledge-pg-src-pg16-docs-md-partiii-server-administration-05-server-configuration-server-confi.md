# Lock Management

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Lock Management`
- Source Line Ranges: `5857-5935`
- Chunk ID: `pg16_configuration_0081_be822786d2`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `a9235b26d3fc9cf2a7aa91226ef1d45adbea638eaa17f7e198ac81c587a22bfa`

## Retrieval Guidance

- Use When: 需要调优死锁检测、锁等待日志或多表/serializable 事务锁表容量。
- Retrieval Keywords: deadlock_timeout, max_locks_per_transaction, max_pred_locks_per_transaction, max_pred_locks_per_relation, max_pred_locks_per_page, log_lock_waits
- Follow-up Guidance: standby 的 max_locks_per_transaction 应不低于 primary。
- Classification Note: 定义 deadlock_timeout、max_locks_per_transaction、predicate lock 上限和提升规则。

## Official Source Content

## Lock Management

**`deadlock_timeout` (`integer`)**
: This is the amount of time to wait on a lock
before checking to see if there is a deadlock condition. The
check for deadlock is relatively expensive, so the server doesn't run
it every time it waits for a lock. We optimistically assume
that deadlocks are not common in production applications and
just wait on the lock for a while before checking for a
deadlock. Increasing this value reduces the amount of time
wasted in needless deadlock checks, but slows down reporting of
real deadlock errors.
If this value is specified without units, it is taken as milliseconds.
The default is one second (`1s`),
which is probably about the smallest value you would want in
practice. On a heavily loaded server you might want to raise it.
Ideally the setting should exceed your typical transaction time,
so as to improve the odds that a lock will be released before
the waiter decides to check for deadlock.
Only superusers and users with the appropriate `SET`
privilege can change this setting.

When [guc-log-lock-waits](#guc-log-lock-waits) is set,
this parameter also determines the amount of time to wait before
a log message is issued about the lock wait.  If you are trying
to investigate locking delays you might want to set a shorter than
normal `deadlock_timeout`.

**`max_locks_per_transaction` (`integer`)**
: The shared lock table has space for
`max_locks_per_transaction` objects
(e.g., tables) per server process or prepared transaction;
hence, no more than this many distinct objects can be locked at
any one time.  This parameter limits the average number of object
locks used by each transaction; individual transactions
can lock more objects as long as the locks of all transactions
fit in the lock table.  This is *not* the number of
rows that can be locked; that value is unlimited.  The default,
64, has historically proven sufficient, but you might need to
raise this value if you have queries that touch many different
tables in a single transaction, e.g., query of a parent table with
many children.  This parameter can only be set at server start.

When running a standby server, you must set this parameter to have the
same or higher value as on the primary server. Otherwise, queries
will not be allowed in the standby server.

**`max_pred_locks_per_transaction` (`integer`)**
: The shared predicate lock table has space for
`max_pred_locks_per_transaction` objects
(e.g., tables) per server process or prepared transaction;
hence, no more than this many distinct objects can be locked at
any one time.  This parameter limits the average number of object
locks used by each transaction; individual transactions
can lock more objects as long as the locks of all transactions
fit in the lock table.  This is *not* the number of
rows that can be locked; that value is unlimited.  The default,
64, has historically proven sufficient, but you might need to
raise this value if you have clients that touch many different
tables in a single serializable transaction. This parameter can
only be set at server start.

**`max_pred_locks_per_relation` (`integer`)**
: This controls how many pages or tuples of a single relation can be
predicate-locked before the lock is promoted to covering the whole
relation.  Values greater than or equal to zero mean an absolute
limit, while negative values
mean [guc-max-pred-locks-per-transaction](#guc-max-pred-locks-per-transaction) divided by
the absolute value of this setting.  The default is -2, which keeps
the behavior from previous versions of PostgreSQL.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

**`max_pred_locks_per_page` (`integer`)**
: This controls how many rows on a single page can be predicate-locked
before the lock is promoted to covering the whole page.  The default
is 2.  This parameter can only be set in
the `postgresql.conf` file or on the server command line.
