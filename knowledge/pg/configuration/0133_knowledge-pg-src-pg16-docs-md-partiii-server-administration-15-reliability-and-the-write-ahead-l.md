# WAL Configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/15_reliability_and_the_write-ahead_log.md`
- Source Title: `Reliability and the Write-Ahead Log`
- Source Heading Path: `Reliability and the Write-Ahead Log > WAL Configuration`
- Source Line Ranges: `340-634`
- Chunk ID: `pg16_configuration_0133_48fa7d2469`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6f48461ab9095757ded31446ecbf17c7214bd86a1a14aab3777370cb9adf84ef`

## Retrieval Guidance

- Use When: 需要调优 checkpoint/WAL I/O、恢复时间、WAL 占用或 commit flush 行为。
- Retrieval Keywords: WAL configuration, checkpoint_timeout, max_wal_size, checkpoint_completion_target, wal_buffers, wal_sync_method, recovery_prefetch
- Follow-up Guidance: 结合 pg_stat_wal、pg_stat_bgwriter、checkpoint_warning 和磁盘空间监控验证。
- Classification Note: 集中解释 checkpoint、max/min_wal_size、wal_buffers、commit_delay、sync_method 和 recovery prefetch。

## Official Source Content

## WAL Configuration

There are several WAL-related configuration parameters that
affect database performance. This section explains their use.
Consult [runtime-config](#runtime-config) for general information about
setting server configuration parameters.

*Checkpoints*
are points in the sequence of transactions at which it is guaranteed
that the heap and index data files have been updated with all
information written before that checkpoint.  At checkpoint time, all
dirty data pages are flushed to disk and a special checkpoint record is
written to the WAL file.  (The change records were previously flushed
to the WAL files.)
In the event of a crash, the crash recovery procedure looks at the latest
checkpoint record to determine the point in the WAL (known as the redo
record) from which it should start the REDO operation.  Any changes made to
data files before that point are guaranteed to be already on disk.
Hence, after a checkpoint, WAL segments preceding the one containing
the redo record are no longer needed and can be recycled or removed. (When
WAL archiving is being done, the WAL segments must be
archived before being recycled or removed.)

The checkpoint requirement of flushing all dirty data pages to disk
can cause a significant I/O load.  For this reason, checkpoint
activity is throttled so that I/O begins at checkpoint start and completes
before the next checkpoint is due to start; this minimizes performance
degradation during checkpoints.

The server's checkpointer process automatically performs
a checkpoint every so often.  A checkpoint is begun every [guc-checkpoint-timeout](#guc-checkpoint-timeout) seconds, or if
[guc-max-wal-size](#guc-max-wal-size) is about to be exceeded,
whichever comes first.
The default settings are 5 minutes and 1 GB, respectively.
If no WAL has been written since the previous checkpoint, new checkpoints
will be skipped even if `checkpoint_timeout` has passed.
(If WAL archiving is being used and you want to put a lower limit on how
often files are archived in order to bound potential data loss, you should
adjust the [guc-archive-timeout](#guc-archive-timeout) parameter rather than the
checkpoint parameters.)
It is also possible to force a checkpoint by using the SQL
command `CHECKPOINT`.

Reducing `checkpoint_timeout` and/or
`max_wal_size` causes checkpoints to occur
more often. This allows faster after-crash recovery, since less work
will need to be redone. However, one must balance this against the
increased cost of flushing dirty data pages more often. If
[guc-full-page-writes](#guc-full-page-writes) is set (as is the default), there is
another factor to consider. To ensure data page consistency,
the first modification of a data page after each checkpoint results in
logging the entire page content. In that case,
a smaller checkpoint interval increases the volume of output to the WAL,
partially negating the goal of using a smaller interval,
and in any case causing more disk I/O.

Checkpoints are fairly expensive, first because they require writing
out all currently dirty buffers, and second because they result in
extra subsequent WAL traffic as discussed above.  It is therefore
wise to set the checkpointing parameters high enough so that checkpoints
don't happen too often.  As a simple sanity check on your checkpointing
parameters, you can set the [guc-checkpoint-warning](#guc-checkpoint-warning)
parameter.  If checkpoints happen closer together than
`checkpoint_warning` seconds,
a message will be output to the server log recommending increasing
`max_wal_size`.  Occasional appearance of such
a message is not cause for alarm, but if it appears often then the
checkpoint control parameters should be increased. Bulk operations such
as large `COPY` transfers might cause a number of such warnings
to appear if you have not set `max_wal_size` high
enough.

To avoid flooding the I/O system with a burst of page writes,
writing dirty buffers during a checkpoint is spread over a period of time.
That period is controlled by
[guc-checkpoint-completion-target](#guc-checkpoint-completion-target), which is
given as a fraction of the checkpoint interval (configured by using
`checkpoint_timeout`).
The I/O rate is adjusted so that the checkpoint finishes when the
given fraction of
`checkpoint_timeout` seconds have elapsed, or before
`max_wal_size` is exceeded, whichever is sooner.
With the default value of 0.9,
PostgreSQL can be expected to complete each checkpoint
a bit before the next scheduled checkpoint (at around 90% of the last checkpoint's
duration).  This spreads out the I/O as much as possible so that the checkpoint
I/O load is consistent throughout the checkpoint interval.  The disadvantage of
this is that prolonging checkpoints affects recovery time, because more WAL
segments will need to be kept around for possible use in recovery.  A user
concerned about the amount of time required to recover might wish to reduce
`checkpoint_timeout` so that checkpoints occur more frequently
but still spread the I/O across the checkpoint interval.  Alternatively,
`checkpoint_completion_target` could be reduced, but this would
result in times of more intense I/O (during the checkpoint) and times of less I/O
(after the checkpoint completed but before the next scheduled checkpoint) and
therefore is not recommended.
Although `checkpoint_completion_target` could be set as high as
1.0, it is typically recommended to set it to no higher than 0.9 (the default)
since checkpoints include some other activities besides writing dirty buffers.
A setting of 1.0 is quite likely to result in checkpoints not being
completed on time, which would result in performance loss due to
unexpected variation in the number of WAL segments needed.

On Linux and POSIX platforms [guc-checkpoint-flush-after](#guc-checkpoint-flush-after)
allows to force the OS that pages written by the checkpoint should be
flushed to disk after a configurable number of bytes.  Otherwise, these
pages may be kept in the OS's page cache, inducing a stall when
`fsync` is issued at the end of a checkpoint.  This setting will
often help to reduce transaction latency, but it also can have an adverse
effect on performance; particularly for workloads that are bigger than
[guc-shared-buffers](#guc-shared-buffers), but smaller than the OS's page cache.

The number of WAL segment files in `pg_wal` directory depends on
`min_wal_size`, `max_wal_size` and
the amount of WAL generated in previous checkpoint cycles. When old WAL
segment files are no longer needed, they are removed or recycled (that is,
renamed to become future segments in the numbered sequence). If, due to a
short-term peak of WAL output rate, `max_wal_size` is
exceeded, the unneeded segment files will be removed until the system
gets back under this limit. Below that limit, the system recycles enough
WAL files to cover the estimated need until the next checkpoint, and
removes the rest. The estimate is based on a moving average of the number
of WAL files used in previous checkpoint cycles. The moving average
is increased immediately if the actual usage exceeds the estimate, so it
accommodates peak usage rather than average usage to some extent.
`min_wal_size` puts a minimum on the amount of WAL files
recycled for future usage; that much WAL is always recycled for future use,
even if the system is idle and the WAL usage estimate suggests that little
WAL is needed.

Independently of `max_wal_size`,
the most recent [guc-wal-keep-size](#guc-wal-keep-size) megabytes of
WAL files plus one additional WAL file are
kept at all times. Also, if WAL archiving is used, old segments cannot be
removed or recycled until they are archived. If WAL archiving cannot keep up
with the pace that WAL is generated, or if `archive_command`
or `archive_library`
fails repeatedly, old WAL files will accumulate in `pg_wal`
until the situation is resolved. A slow or failed standby server that
uses a replication slot will have the same effect (see
[streaming-replication-slots](#streaming-replication-slots)).

In archive recovery or standby mode, the server periodically performs
*restartpoints*,
which are similar to checkpoints in normal operation: the server forces
all its state to disk, updates the `pg_control` file to
indicate that the already-processed WAL data need not be scanned again,
and then recycles any old WAL segment files in the `pg_wal`
directory.
Restartpoints can't be performed more frequently than checkpoints on the
primary because restartpoints can only be performed at checkpoint records.
A restartpoint is triggered when a checkpoint record is reached if at
least `checkpoint_timeout` seconds have passed since the last
restartpoint, or if WAL size is about to exceed
`max_wal_size`. However, because of limitations on when a
restartpoint can be performed, `max_wal_size` is often exceeded
during recovery, by up to one checkpoint cycle's worth of WAL.
(`max_wal_size` is never a hard limit anyway, so you should
always leave plenty of headroom to avoid running out of disk space.)

There are two commonly used internal WAL functions:
`XLogInsertRecord` and `XLogFlush`.
`XLogInsertRecord` is used to place a new record into
the WAL buffers in shared memory. If there is no
space for the new record, `XLogInsertRecord` will have
to write (move to kernel cache) a few filled WAL
buffers. This is undesirable because `XLogInsertRecord`
is used on every database low level modification (for example, row
insertion) at a time when an exclusive lock is held on affected
data pages, so the operation needs to be as fast as possible.  What
is worse, writing WAL buffers might also force the
creation of a new WAL segment, which takes even more
time. Normally, WAL buffers should be written
and flushed by an `XLogFlush` request, which is
made, for the most part, at transaction commit time to ensure that
transaction records are flushed to permanent storage. On systems
with high WAL output, `XLogFlush` requests might
not occur often enough to prevent `XLogInsertRecord`
from having to do writes.  On such systems
one should increase the number of WAL buffers by
modifying the [guc-wal-buffers](#guc-wal-buffers) parameter.  When
[guc-full-page-writes](#guc-full-page-writes) is set and the system is very busy,
setting `wal_buffers` higher will help smooth response times
during the period immediately following each checkpoint.

The [guc-commit-delay](#guc-commit-delay) parameter defines for how many
microseconds a group commit leader process will sleep after acquiring a
lock within `XLogFlush`, while group commit
followers queue up behind the leader.  This delay allows other server
processes to add their commit records to the WAL buffers so that all of
them will be flushed by the leader's eventual sync operation.  No sleep
will occur if [guc-fsync](#guc-fsync) is not enabled, or if fewer
than [guc-commit-siblings](#guc-commit-siblings) other sessions are currently
in active transactions; this avoids sleeping when it's unlikely that
any other session will commit soon.  Note that on some platforms, the
resolution of a sleep request is ten milliseconds, so that any nonzero
`commit_delay` setting between 1 and 10000
microseconds would have the same effect.  Note also that on some
platforms, sleep operations may take slightly longer than requested by
the parameter.

Since the purpose of `commit_delay` is to allow the
cost of each flush operation to be amortized across concurrently
committing transactions (potentially at the expense of transaction
latency), it is necessary to quantify that cost before the setting can
be chosen intelligently.  The higher that cost is, the more effective
`commit_delay` is expected to be in increasing
transaction throughput, up to a point.  The [pgtestfsync](#pgtestfsync) program can be used to measure the average time
in microseconds that a single WAL flush operation takes.  A value of
half of the average time the program reports it takes to flush after a
single 8kB write operation is often the most effective setting for
`commit_delay`, so this value is recommended as the
starting point to use when optimizing for a particular workload.  While
tuning `commit_delay` is particularly useful when the
WAL is stored on high-latency rotating disks, benefits can be
significant even on storage media with very fast sync times, such as
solid-state drives or RAID arrays with a battery-backed write cache;
but this should definitely be tested against a representative workload.
Higher values of `commit_siblings` should be used in
such cases, whereas smaller `commit_siblings` values
are often helpful on higher latency media.  Note that it is quite
possible that a setting of `commit_delay` that is too
high can increase transaction latency by so much that total transaction
throughput suffers.

When `commit_delay` is set to zero (the default), it
is still possible for a form of group commit to occur, but each group
will consist only of sessions that reach the point where they need to
flush their commit records during the window in which the previous
flush operation (if any) is occurring.  At higher client counts a
"gangway effect" tends to occur, so that the effects of group
commit become significant even when `commit_delay` is
zero, and thus explicitly setting `commit_delay` tends
to help less.  Setting `commit_delay` can only help
when (1) there are some concurrently committing transactions, and (2)
throughput is limited to some degree by commit rate; but with high
rotational latency this setting can be effective in increasing
transaction throughput with as few as two clients (that is, a single
committing client with one sibling transaction).

The [guc-wal-sync-method](#guc-wal-sync-method) parameter determines how
PostgreSQL will ask the kernel to force
WAL updates out to disk.
All the options should be the same in terms of reliability, with
the exception of `fsync_writethrough`, which can sometimes
force a flush of the disk cache even when other options do not do so.
However, it's quite platform-specific which one will be the fastest.
You can test the speeds of different options using the [pgtestfsync](#pgtestfsync) program.
Note that this parameter is irrelevant if `fsync`
has been turned off.

Enabling the [guc-wal-debug](#guc-wal-debug) configuration parameter
(provided that PostgreSQL has been
compiled with support for it) will result in each
`XLogInsertRecord` and `XLogFlush`
WAL call being logged to the server log. This
option might be replaced by a more general mechanism in the future.

There are two internal functions to write WAL data to disk:
`XLogWrite` and `issue_xlog_fsync`.
When [guc-track-wal-io-timing](#guc-track-wal-io-timing) is enabled, the total
amounts of time `XLogWrite` writes and
`issue_xlog_fsync` syncs WAL data to disk are counted as
`wal_write_time` and `wal_sync_time` in
[pg-stat-wal-view](#pg-stat-wal-view), respectively.
`XLogWrite` is normally called by
`XLogInsertRecord` (when there is no space for the new
record in WAL buffers), `XLogFlush` and the WAL writer,
to write WAL buffers to disk and call `issue_xlog_fsync`.
`issue_xlog_fsync` is normally called by
`XLogWrite` to sync WAL files to disk.
If `wal_sync_method` is either
`open_datasync` or `open_sync`,
a write operation in `XLogWrite` guarantees to sync written
WAL data to disk and `issue_xlog_fsync` does nothing.
If `wal_sync_method` is either `fdatasync`,
`fsync`, or `fsync_writethrough`,
the write operation moves WAL buffers to kernel cache and
`issue_xlog_fsync` syncs them to disk. Regardless
of the setting of `track_wal_io_timing`, the number
of times `XLogWrite` writes and
`issue_xlog_fsync` syncs WAL data to disk are also
counted as `wal_write` and `wal_sync`
in `pg_stat_wal`, respectively.

The [guc-recovery-prefetch](#guc-recovery-prefetch) parameter can be used to reduce
I/O wait times during recovery by instructing the kernel to initiate reads
of disk blocks that will soon be needed but are not currently in
PostgreSQL's buffer pool.
The [guc-maintenance-io-concurrency](#guc-maintenance-io-concurrency) and
[guc-wal-decode-buffer-size](#guc-wal-decode-buffer-size) settings limit prefetching
concurrency and distance, respectively.  By default, it is set to
`try`, which enables the feature on systems where
`posix_fadvise` is available.
