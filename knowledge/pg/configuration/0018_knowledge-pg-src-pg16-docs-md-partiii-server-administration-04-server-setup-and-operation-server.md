# Resource Limits

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/04_server_setup_and_operation.md`
- Source Title: `Server Setup and Operation`
- Source Heading Path: `Server Setup and Operation > Managing Kernel Resources > Resource Limits`
- Source Line Ranges: `526-666, 873-953`
- Chunk ID: `pg16_configuration_0018_1aff356c4f`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d3c420bca79d4591c9c314b9f3c5ca832f0e50834f2c3cfb99224fd90f46f108`

## Retrieval Guidance

- Use When: 高连接数、多实例或文件句柄/进程数/监听队列限制相关问题。
- Retrieval Keywords: ulimit, open files, Too many open files, maxproc, openfiles, fs.file-max, somaxconn, max_files_per_process
- Follow-up Guidance: 专用服务器可提高 OS 限制；不改系统全局限制时可限制 max_files_per_process。
- Classification Note: 说明 maxproc/openfiles/datasize、ulimit、fs.file-max、somaxconn 和 max_files_per_process 的语义。

## Official Source Content

## Managing Kernel Resources

PostgreSQL can sometimes exhaust various operating system
resource limits, especially when multiple copies of the server are running
on the same system, or in very large installations.  This section explains
the kernel resources used by PostgreSQL and the steps you
can take to resolve problems related to kernel resource consumption.

### Shared Memory and Semaphores

PostgreSQL requires the operating system to provide
inter-process communication (IPC) features, specifically
shared memory and semaphores.  Unix-derived systems typically provide
"System V" IPC,
"POSIX" IPC, or both.
Windows has its own implementation of
these features and is not discussed here.

By default, PostgreSQL allocates
a very small amount of System V shared memory, as well as a much larger
amount of anonymous `mmap` shared memory.
Alternatively, a single large System V shared memory region can be used
(see [guc-shared-memory-type](#guc-shared-memory-type)).

In addition a significant number of semaphores, which can be either
System V or POSIX style, are created at server startup.  Currently,
POSIX semaphores are used on Linux and FreeBSD systems while other
platforms use System V semaphores.

System V IPC features are typically constrained by
system-wide allocation limits.
When PostgreSQL exceeds one of these limits,
the server will refuse to start and
should leave an instructive error message describing the problem
and what to do about it. (See also [server-start-failures](#server-start-failures).) The relevant kernel
parameters are named consistently across different systems; [sysvipc-parameters](#sysvipc-parameters) gives an overview. The methods to set
them, however, vary. Suggestions for some platforms are given below.

| Name | Description | Values needed to run one PostgreSQL instance |
| --- | --- | --- |
| `SHMMAX` | Maximum size of shared memory segment (bytes) | at least 1kB, but the default is usually much higher |
| `SHMMIN` | Minimum size of shared memory segment (bytes) | 1 |
| `SHMALL` | Total amount of shared memory available (bytes or pages) | same as `SHMMAX` if bytes,         or `ceil(SHMMAX/PAGE_SIZE)` if pages,         plus room for other applications |
| `SHMSEG` | Maximum number of shared memory segments per process | only 1 segment is needed, but the default is much higher |
| `SHMMNI` | Maximum number of shared memory segments system-wide | like `SHMSEG` plus room for other applications |
| `SEMMNI` | Maximum number of semaphore identifiers (i.e., sets) | at least `ceil((max_connections + autovacuum_max_workers + max_wal_senders + max_worker_processes + 6) / 16)` plus room for other applications |
| `SEMMNS` | Maximum number of semaphores system-wide | `ceil((max_connections + autovacuum_max_workers + max_wal_senders + max_worker_processes + 6) / 16) * 17` plus room for other applications |
| `SEMMSL` | Maximum number of semaphores per set | at least 17 |
| `SEMMAP` | Number of entries in semaphore map | see text |
| `SEMVMX` | Maximum value of semaphore | at least 1000 (The default is often 32767; do not change unless necessary) |

PostgreSQL requires a few bytes of System V shared memory
(typically 48 bytes, on 64-bit platforms) for each copy of the server.
On most modern operating systems, this amount can easily be allocated.
However, if you are running many copies of the server or you explicitly
configure the server to use large amounts of System V shared memory (see
[guc-shared-memory-type](#guc-shared-memory-type) and [guc-dynamic-shared-memory-type](#guc-dynamic-shared-memory-type)), it may be necessary to
increase `SHMALL`, which is the total amount of System V shared
memory system-wide.  Note that `SHMALL` is measured in pages
rather than bytes on many systems.

Less likely to cause problems is the minimum size for shared
memory segments (`SHMMIN`), which should be at most
approximately 32 bytes for PostgreSQL (it is
usually just 1). The maximum number of segments system-wide
(`SHMMNI`) or per-process (`SHMSEG`) are unlikely
to cause a problem unless your system has them set to zero.

When using System V semaphores,
PostgreSQL uses one semaphore per allowed connection
([guc-max-connections](#guc-max-connections)), allowed autovacuum worker process
([guc-autovacuum-max-workers](#guc-autovacuum-max-workers)), allowed WAL sender process
([guc-max-wal-senders](#guc-max-wal-senders)), and allowed background
process ([guc-max-worker-processes](#guc-max-worker-processes)), in sets of 16.
Each such set will
also contain a 17th semaphore which contains a "magic
number", to detect collision with semaphore sets used by
other applications. The maximum number of semaphores in the system
is set by `SEMMNS`, which consequently must be at least
as high as `max_connections` plus
`autovacuum_max_workers` plus `max_wal_senders`,
plus `max_worker_processes`, plus one extra for each 16
allowed connections plus workers (see the formula in [sysvipc-parameters](#sysvipc-parameters)).  The parameter `SEMMNI`
determines the limit on the number of semaphore sets that can
exist on the system at one time.  Hence this parameter must be at
least `ceil((max_connections + autovacuum_max_workers + max_wal_senders + max_worker_processes + 6) / 16)`.
Lowering the number
of allowed connections is a temporary workaround for failures,
which are usually confusingly worded "No space
left on device", from the function `semget`.

In some cases it might also be necessary to increase
`SEMMAP` to be at least on the order of
`SEMMNS`.  If the system has this parameter
(many do not), it defines the size of the semaphore
resource map, in which each contiguous block of available semaphores
needs an entry. When a semaphore set is freed it is either added to
an existing entry that is adjacent to the freed block or it is
registered under a new map entry. If the map is full, the freed
semaphores get lost (until reboot). Fragmentation of the semaphore
space could over time lead to fewer available semaphores than there
should be.

Various other settings related to "semaphore undo", such as
`SEMMNU` and `SEMUME`, do not affect
PostgreSQL.

When using POSIX semaphores, the number of semaphores needed is the
same as for System V, that is one semaphore per allowed connection
([guc-max-connections](#guc-max-connections)), allowed autovacuum worker process
([guc-autovacuum-max-workers](#guc-autovacuum-max-workers)), allowed WAL sender process
([guc-max-wal-senders](#guc-max-wal-senders)), and allowed background
process ([guc-max-worker-processes](#guc-max-worker-processes)).
On the platforms where this option is preferred, there is no specific
kernel limit on the number of POSIX semaphores.

**AIX**
: It should not be necessary to do
any special configuration for such parameters as
`SHMMAX`, as it appears this is configured to
allow all memory to be used as shared memory.  That is the
sort of configuration commonly used for other databases such
as DB/2.

It might, however, be necessary to modify the global
`ulimit` information in
`/etc/security/limits`, as the default hard
limits for file sizes (`fsize`) and numbers of
files (`nofiles`) might be too low.

**FreeBSD**
: The default shared memory settings are usually good enough, unless
you have set `shared_memory_type` to `sysv`.
System V semaphores are not used on this platform.

The default IPC settings can be changed using
the `sysctl` or
`loader` interfaces.  The following
parameters can be set using `sysctl`:

```

### Resource Limits

Unix-like operating systems enforce various kinds of resource limits
that might interfere with the operation of your
PostgreSQL server. Of particular
importance are limits on the number of processes per user, the
number of open files per process, and the amount of memory available
to each process. Each of these have a "hard" and a
"soft" limit. The soft limit is what actually counts
but it can be changed by the user up to the hard limit. The hard
limit can only be changed by the root user. The system call
`setrlimit` is responsible for setting these
parameters. The shell's built-in command `ulimit`
(Bourne shells) or `limit` (csh) is
used to control the resource limits from the command line. On
BSD-derived systems the file `/etc/login.conf`
controls the various resource limits set during login. See the
operating system documentation for details. The relevant
parameters are `maxproc`,
`openfiles`, and `datasize`. For
example:

```
default:\
...
:datasize-cur=256M:\
:maxproc-cur=256:\
:openfiles-cur=256:\
...
```

(`-cur` is the soft limit.  Append
`-max` to set the hard limit.)

Kernels can also have system-wide limits on some resources.

- On Linux the kernel parameter
`fs.file-max` determines the maximum number of open
files that the kernel will support.  It can be changed with
`sysctl -w fs.file-max=`N``.
To make the setting persist across reboots, add an assignment
in `/etc/sysctl.conf`.
The maximum limit of files per process is fixed at the time the
kernel is compiled; see
`/usr/src/linux/Documentation/proc.txt` for
more information.

The PostgreSQL server uses one process
per connection so you should provide for at least as many processes
as allowed connections, in addition to what you need for the rest
of your system.  This is usually not a problem but if you run
several servers on one machine things might get tight.

The factory default limit on open files is often set to
"socially friendly" values that allow many users to
coexist on a machine without using an inappropriate fraction of
the system resources.  If you run many servers on a machine this
is perhaps what you want, but on dedicated servers you might want to
raise this limit.

On the other side of the coin, some systems allow individual
processes to open large numbers of files; if more than a few
processes do so then the system-wide limit can easily be exceeded.
If you find this happening, and you do not want to alter the
system-wide limit, you can set PostgreSQL's [guc-max-files-per-process](#guc-max-files-per-process) configuration parameter to
limit the consumption of open files.

Another kernel limit that may be of concern when supporting large
numbers of client connections is the maximum socket connection queue
length.  If more than that many connection requests arrive within a very
short period, some may get rejected before the PostgreSQL server can service
the requests, with those clients receiving unhelpful connection failure
errors such as "Resource temporarily unavailable" or
"Connection refused".  The default queue length limit is 128
on many platforms.  To raise it, adjust the appropriate kernel parameter
via sysctl, then restart the PostgreSQL server.
The parameter is variously named `net.core.somaxconn`
on Linux, `kern.ipc.soacceptqueue` on newer FreeBSD,
and `kern.ipc.somaxconn` on macOS and other BSD
variants.
