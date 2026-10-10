# systemd RemoveIPC

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/04_server_setup_and_operation.md`
- Source Title: `Server Setup and Operation`
- Source Heading Path: `Server Setup and Operation > Managing Kernel Resources > systemd RemoveIPC`
- Source Line Ranges: `526-666, 811-872, 873-953, 954-1046, 1047-1080`
- Chunk ID: `pg16_guide_0010_c0fc0ca72c`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dcf82f2fc5ae47d0000819a7b74afddbb098430b19e8c6ee326e768dc9ed4e13`

## Retrieval Guidance

- Use When: systemd 环境中并行查询/共享内存对象随机缺失或相关 WARNING 出现。
- Retrieval Keywords: RemoveIPC, logind.conf, could not remove shared memory segment, PostgreSQL unreliable, useradd -r, adduser --system
- Follow-up Guidance: 将 postgres 创建为 system user，或设置 RemoveIPC=no。
- Classification Note: 包含 RemoveIPC 导致共享内存被清除的症状、原因和修复方向。

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

### systemd RemoveIPC

If systemd is in use, some care must be taken
that IPC resources (including shared memory) are not prematurely
removed by the operating system.  This is especially of concern when
installing PostgreSQL from source.  Users of distribution packages of
PostgreSQL are less likely to be affected, as
the `postgres` user is then normally created as a system
user.

The setting `RemoveIPC`
in `logind.conf` controls whether IPC objects are
removed when a user fully logs out.  System users are exempt.  This
setting defaults to on in stock systemd, but
some operating system distributions default it to off.

A typical observed effect when this setting is on is that shared memory
objects used for parallel query execution are removed at apparently random
times, leading to errors and warnings while attempting to open and remove
them, like

```
WARNING:  could not remove shared memory segment "/PostgreSQL.1450751626": No such file or directory
```

Different types of IPC objects (shared memory vs. semaphores, System V
vs. POSIX) are treated slightly differently
by systemd, so one might observe that some IPC
resources are not removed in the same way as others.  But it is not
advisable to rely on these subtle differences.

A "user logging out" might happen as part of a maintenance
job or manually when an administrator logs in as
the `postgres` user or something similar, so it is hard
to prevent in general.

What is a "system user" is determined
at systemd compile time from
the `SYS_UID_MAX` setting
in `/etc/login.defs`.

Packaging and deployment scripts should be careful to create
the `postgres` user as a system user by
using `useradd -r`, `adduser --system`,
or equivalent.

Alternatively, if the user account was created incorrectly or cannot be
changed, it is recommended to set

```
RemoveIPC=no
```

in `/etc/systemd/logind.conf` or another appropriate
configuration file.

> **Caution:**

> At least one of these two things has to be ensured, or the PostgreSQL
> server will be very unreliable.
>

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

### Linux Memory Overcommit

The default virtual memory behavior on Linux is not
optimal for PostgreSQL. Because of the
way that the kernel implements memory overcommit, the kernel might
terminate the PostgreSQL postmaster (the
supervisor server process) if the memory demands of either
PostgreSQL or another process cause the
system to run out of virtual memory.

If this happens, you will see a kernel message that looks like
this (consult your system documentation and configuration on where
to look for such a message):

```
Out of Memory: Killed process 12345 (postgres).
```

This indicates that the `postgres` process
has been terminated due to memory pressure.
Although existing database connections will continue to function
normally, no new connections will be accepted.  To recover,
PostgreSQL will need to be restarted.

One way to avoid this problem is to run
PostgreSQL on a machine where you can
be sure that other processes will not run the machine out of
memory.  If memory is tight, increasing the swap space of the
operating system can help avoid the problem, because the
out-of-memory (OOM) killer is invoked only when physical memory and
swap space are exhausted.

If PostgreSQL itself is the cause of the
system running out of memory, you can avoid the problem by changing
your configuration.  In some cases, it may help to lower memory-related
configuration parameters, particularly
[`shared_buffers`](#guc-shared-buffers),
[`work_mem`](#guc-work-mem), and
[`hash_mem_multiplier`](#guc-hash-mem-multiplier).
In other cases, the problem may be caused by allowing too many
connections to the database server itself.  In many cases, it may
be better to reduce
[`max_connections`](#guc-max-connections)
and instead make use of external connection-pooling software.

It is possible to modify the
kernel's behavior so that it will not "overcommit" memory.
Although this setting will not prevent the [OOM killer](https://lwn.net/Articles/104179/) from being invoked
altogether, it will lower the chances significantly and will therefore
lead to more robust system behavior.  This is done by selecting strict
overcommit mode via `sysctl`:

```
sysctl -w vm.overcommit_memory=2
```

or placing an equivalent entry in `/etc/sysctl.conf`.
You might also wish to modify the related setting
`vm.overcommit_ratio`.  For details see the kernel documentation
file [](https://www.kernel.org/doc/Documentation/vm/overcommit-accounting).

Another approach, which can be used with or without altering
`vm.overcommit_memory`, is to set the process-specific
*OOM score adjustment* value for the postmaster process to
`-1000`, thereby guaranteeing it will not be targeted by the OOM
killer.  The simplest way to do this is to execute

```
echo -1000 > /proc/self/oom_score_adj
```

in the PostgreSQL startup script just before
invoking `postgres`.
Note that this action must be done as root, or it will have no effect;
so a root-owned startup script is the easiest place to do it.  If you
do this, you should also set these environment variables in the startup
script before invoking `postgres`:

```
export PG_OOM_ADJUST_FILE=/proc/self/oom_score_adj
export PG_OOM_ADJUST_VALUE=0
```

These settings will cause postmaster child processes to run with the
normal OOM score adjustment of zero, so that the OOM killer can still
target them at need.  You could use some other value for
`PG_OOM_ADJUST_VALUE` if you want the child processes to run
with some other OOM score adjustment.  (`PG_OOM_ADJUST_VALUE`
can also be omitted, in which case it defaults to zero.)  If you do not
set `PG_OOM_ADJUST_FILE`, the child processes will run with the
same OOM score adjustment as the postmaster, which is unwise since the
whole point is to ensure that the postmaster has a preferential setting.

### Linux Huge Pages

Using huge pages reduces overhead when using large contiguous chunks of
memory, as PostgreSQL does, particularly when
using large values of [guc-shared-buffers](#guc-shared-buffers).  To use this
feature in PostgreSQL you need a kernel
with `CONFIG_HUGETLBFS=y` and
`CONFIG_HUGETLB_PAGE=y`. You will also have to configure
the operating system to provide enough huge pages of the desired size.
The runtime-computed parameter
[guc-shared-memory-size-in-huge-pages](#guc-shared-memory-size-in-huge-pages) reports the number
of huge pages required.  This parameter can be viewed before starting the
server with a `postgres` command like:

```
$ postgres -D $PGDATA -C shared_memory_size_in_huge_pages
3170
$ grep ^Hugepagesize /proc/meminfo
Hugepagesize:       2048 kB
$ ls /sys/kernel/mm/hugepages
hugepages-1048576kB  hugepages-2048kB
```

In this example the default is 2MB, but you can also explicitly request
either 2MB or 1GB with [guc-huge-page-size](#guc-huge-page-size) to adapt
the number of pages calculated by
`shared_memory_size_in_huge_pages`.

While we need at least `3170` huge pages in this example,
a larger setting would be appropriate if other programs on the machine
also need huge pages.
We can set this with:

```
