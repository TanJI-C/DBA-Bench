# Shared Libraries

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Post-Installation Setup > Shared Libraries`
- Source Line Ranges: `1892-2009`
- Chunk ID: `pg16_solution_0013_d4003e36b9`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `29d2372be09d831d0f1871f76a466c908b9b4778dbac365537ded4e51185b38b`

## Retrieval Guidance

- Use When: 安装后客户端或程序报 shared library cannot open / not found。
- Retrieval Keywords: LD_LIBRARY_PATH, LD_RUN_PATH, ldconfig, shared libraries, libpq.so cannot open
- Follow-up Guidance: 优先使用系统动态链接器配置，临时场景可用环境变量。
- Classification Note: 说明安装后通过 LD_LIBRARY_PATH、PATH、ldconfig 等解决共享库查找问题。

## Official Source Content

## Post-Installation Setup

### Shared Libraries

On some systems with shared libraries
you need to tell the system how to find the newly installed
shared libraries.  The systems on which this is
*not* necessary include
FreeBSD,
Linux,
NetBSD, OpenBSD, and
Solaris.

The method to set the shared library search path varies between
platforms, but the most widely-used method is to set the
environment variable `LD_LIBRARY_PATH` like so: In Bourne
shells (`sh`, `ksh`, `bash`, `zsh`):

```
LD_LIBRARY_PATH=/usr/local/pgsql/lib
export LD_LIBRARY_PATH
```

or in `csh` or `tcsh`:

```
setenv LD_LIBRARY_PATH /usr/local/pgsql/lib
```

Replace `/usr/local/pgsql/lib` with whatever you set
``--libdir`` to in [configure](#configure).
You should put these commands into a shell start-up file such as
`/etc/profile` or `~/.bash_profile`.  Some
good information about the caveats associated with this method can
be found at [](http://xahlee.info/UnixResource_dir/_/ldpath.html).

On some systems it might be preferable to set the environment
variable `LD_RUN_PATH` *before*
building.

On Cygwin, put the library
directory in the `PATH` or move the
`.dll` files into the `bin`
directory.

If in doubt, refer to the manual pages of your system (perhaps
`ld.so` or `rld`). If you later
get a message like:

```
psql: error in loading shared libraries
libpq.so.2.1: cannot open shared object file: No such file or directory
```

then this step was necessary.  Simply take care of it then.

If you are on Linux and you have root
access, you can run:

```
/sbin/ldconfig /usr/local/pgsql/lib
```

(or equivalent directory) after installation to enable the
run-time linker to find the shared libraries faster.  Refer to the
manual page of `ldconfig` for more information.  On
FreeBSD, NetBSD, and OpenBSD the command is:

```
/sbin/ldconfig -m /usr/local/pgsql/lib
```

instead.  Other systems are not known to have an equivalent
command.

### Environment Variables

If you installed into `/usr/local/pgsql` or some other
location that is not searched for programs by default, you should
add `/usr/local/pgsql/bin` (or whatever you set
``--bindir`` to in [configure](#configure))
into your `PATH`.  Strictly speaking, this is not
necessary, but it will make the use of PostgreSQL
much more convenient.

To do this, add the following to your shell start-up file, such as
`~/.bash_profile` (or `/etc/profile`, if you
want it to affect all users):

```
PATH=/usr/local/pgsql/bin:$PATH
export PATH
```

If you are using `csh` or `tcsh`, then use this command:

```
set path = ( /usr/local/pgsql/bin $path )
```

To enable your system to find the man
documentation, you need to add lines like the following to a
shell start-up file unless you installed into a location that is
searched by default:

```
MANPATH=/usr/local/pgsql/share/man:$MANPATH
export MANPATH
```

The environment variables `PGHOST` and `PGPORT`
specify to client applications the host and port of the database
server, overriding the compiled-in defaults. If you are going to
run client applications remotely then it is convenient if every
user that plans to use the database sets `PGHOST`.  This
is not required, however; the settings can be communicated via command
line options to most client programs.
