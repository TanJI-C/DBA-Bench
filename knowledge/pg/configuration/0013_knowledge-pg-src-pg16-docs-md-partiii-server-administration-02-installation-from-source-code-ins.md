# Environment Variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Post-Installation Setup > Environment Variables`
- Source Line Ranges: `1034-1187, 1892-2009`
- Chunk ID: `pg16_configuration_0013_16bb775cea`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b1c32c468fe6423bb668c095abe0ac397d333eb06d632b37d285b12765b174a1`

## Retrieval Guidance

- Use When: 需要让 shell 找到 PostgreSQL 程序、man page 或设置客户端默认连接位置。
- Retrieval Keywords: PATH, MANPATH, PGHOST, PGPORT, postgresql bin
- Follow-up Guidance: 全局配置写 /etc/profile，单用户配置写用户 shell 启动文件。
- Classification Note: 说明 PATH、MANPATH、PGHOST、PGPORT 等安装后环境变量语义。

## Official Source Content

### `configure` Environment Variables

In addition to the ordinary command-line options described above,
`configure` responds to a number of environment
variables.
You can specify environment variables on the
`configure` command line, for example:

```
./configure CC=/opt/bin/gcc CFLAGS='-O2 -pipe'
```

In this usage an environment variable is little different from a
command-line option.
You can also set such variables beforehand:

```
export CC=/opt/bin/gcc
export CFLAGS='-O2 -pipe'
./configure
```

This usage can be convenient because many programs' configuration
scripts respond to these variables in similar ways.

The most commonly used of these environment variables are
`CC` and `CFLAGS`.
If you prefer a C compiler different from the one
`configure` picks, you can set the
variable `CC` to the program of your choice.
By default, `configure` will pick
`gcc` if available, else the platform's
default (usually `cc`).  Similarly, you can override the
default compiler flags if needed with the `CFLAGS` variable.

Here is a list of the significant variables that can be set in
this manner:

**`BISON`**
: Bison program

**`CC`**
: C compiler

**`CFLAGS`**
: options to pass to the C compiler

**`CLANG`**
: path to `clang` program used to process source code
for inlining when compiling with `--with-llvm`

**`CPP`**
: C preprocessor

**`CPPFLAGS`**
: options to pass to the C preprocessor

**`CXX`**
: C++ compiler

**`CXXFLAGS`**
: options to pass to the C++ compiler

**`DTRACE`**
: location of the `dtrace` program

**`DTRACEFLAGS`**
: options to pass to the `dtrace` program

**`FLEX`**
: Flex program

**`LDFLAGS`**
: options to use when linking either executables or shared libraries

**`LDFLAGS_EX`**
: additional options for linking executables only

**`LDFLAGS_SL`**
: additional options for linking shared libraries only

**`LLVM_CONFIG`**
: `llvm-config` program used to locate the
LLVM installation

**`MSGFMT`**
: `msgfmt` program for native language support

**`PERL`**
: Perl interpreter program.  This will be used to determine the
dependencies for building PL/Perl.  The default is
`perl`.

**`PYTHON`**
: Python interpreter program.  This will be used to determine the
dependencies for building PL/Python.  If this is not set, the
following are probed in this order:
`python3 python`.

**`TCLSH`**
: Tcl interpreter program.  This will be used to
determine the dependencies for building PL/Tcl.
If this is not set, the following are probed in this
order: `tclsh tcl tclsh8.6 tclsh86 tclsh8.5 tclsh85
tclsh8.4 tclsh84`.

**`XML2_CONFIG`**
: `xml2-config` program used to locate the
libxml2 installation

Sometimes it is useful to add compiler flags after-the-fact to the set
that were chosen by `configure`.  An important example is
that gcc's `-Werror` option cannot be included
in the `CFLAGS` passed to `configure`, because
it will break many of `configure`'s built-in tests.  To add
such flags, include them in the `COPT` environment variable
while running `make`.  The contents of `COPT`
are added to both the `CFLAGS` and `LDFLAGS`
options set up by `configure`.  For example, you could do

```
make COPT='-Werror'
```

or

```
export COPT='-Werror'
make
```

> **Note:**

> If using GCC, it is best to build with an optimization level of
> at least `-O1`, because using no optimization
> (`-O0`) disables some important compiler warnings (such
> as the use of uninitialized variables).  However, non-zero
> optimization levels can complicate debugging because stepping
> through compiled code will usually not match up one-to-one with
> source code lines.  If you get confused while trying to debug
> optimized code, recompile the specific files of interest with
> `-O0`.  An easy way to do this is by passing an option
> to make: `make PROFILE=-O0 file.o`.
>

>

> The `COPT` and `PROFILE` environment variables are
> actually handled identically by the PostgreSQL
> makefiles.  Which to use is a matter of preference, but a common habit
> among developers is to use `PROFILE` for one-time flag
> adjustments, while `COPT` might be kept set all the time.
>

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
