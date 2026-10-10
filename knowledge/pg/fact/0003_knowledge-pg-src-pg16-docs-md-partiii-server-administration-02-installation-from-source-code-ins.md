# Supported Platforms

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Supported Platforms`
- Source Line Ranges: `2010-2054`
- Chunk ID: `pg16_fact_0003_2be9499789`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `98db3d10334f1a062506bfd2fc4642f825f4f2bc28d02570ee9b824c02d1e5ef`

## Retrieval Guidance

- Use When: 确认平台是否属于 PostgreSQL 社区支持范围。
- Retrieval Keywords: supported platforms, Build Farm, CPU architecture, Linux, Windows, FreeBSD, macOS, AIX, Solaris
- Follow-up Guidance: 不在 build farm 的平台应准备额外验证。
- Classification Note: 列出支持平台、CPU/OS 兼容范围和 build farm 背景。

## Official Source Content

## Supported Platforms

A platform (that is, a CPU architecture and operating system combination)
is considered supported by the PostgreSQL development
community if the code contains provisions to work on that platform and
it has recently been verified to build and pass its regression tests
on that platform.  Currently, most testing of platform compatibility
is done automatically by test machines in the
[PostgreSQL Build Farm](https://buildfarm.postgresql.org/).
If you are interested in using PostgreSQL on a platform
that is not represented in the build farm, but on which the code works
or can be made to work, you are strongly encouraged to set up a build
farm member machine so that continued compatibility can be assured.

In general, PostgreSQL can be expected to work on
these CPU architectures: x86, PowerPC, S/390, SPARC, ARM, MIPS, RISC-V,
and PA-RISC, including
big-endian, little-endian, 32-bit, and 64-bit variants where applicable.
It is often
possible to build on an unsupported CPU type by configuring with
`--disable-spinlocks`, but performance will be poor.

PostgreSQL can be expected to work on current
versions of these operating systems: Linux, Windows,
FreeBSD, OpenBSD, NetBSD, DragonFlyBSD, macOS, AIX, Solaris, and illumos.
Other Unix-like systems may also work but are not currently
being tested.  In most cases, all CPU architectures supported by
a given operating system will work.  Look in
[installation-platform-notes](#installation-platform-notes) below to see if
there is information
specific to your operating system, particularly if using an older system.

If you have installation problems on a platform that is known
to be supported according to recent build farm results, please report
it to pgsql-bugs@lists.postgresql.org.  If you are interested
in porting PostgreSQL to a new platform,
pgsql-hackers@lists.postgresql.org is the appropriate place
to discuss that.

Historical versions of PostgreSQL or POSTGRES
also ran on CPU architectures including Alpha, Itanium, M32R, M68K,
M88K, NS32K, SuperH, and VAX, and operating systems including 4.3BSD, BEOS,
BSD/OS, DG/UX, Dynix, HP-UX, IRIX, NeXTSTEP, QNX, SCO, SINIX, Sprite, SunOS,
Tru64 UNIX, and ULTRIX.
