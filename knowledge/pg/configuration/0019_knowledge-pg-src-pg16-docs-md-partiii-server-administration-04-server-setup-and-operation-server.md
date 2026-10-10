# Linux Huge Pages

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/04_server_setup_and_operation.md`
- Source Title: `Server Setup and Operation`
- Source Heading Path: `Server Setup and Operation > Managing Kernel Resources > Linux Huge Pages`
- Source Line Ranges: `526-666, 1047-1080`
- Chunk ID: `pg16_configuration_0019_53bdd1b903`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6cb243e27a4da2cbe56aa224eabf5ddd59d20a0709776b081d5f1cf030e91776`

## Retrieval Guidance

- Use When: 需要为大 shared_buffers 实例启用或排查 Linux huge pages。
- Retrieval Keywords: huge pages, huge_pages, huge_page_size, shared_memory_size_in_huge_pages, vm.nr_hugepages, hugetlb, transparent huge pages
- Follow-up Guidance: 先用 postgres -C shared_memory_size_in_huge_pages 估算页数，再配置系统页数和权限。
- Classification Note: 说明 huge_pages、huge_page_size、shared_memory_size_in_huge_pages、vm.nr_hugepages、vm.hugetlb_shm_group 等配置语义。

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
