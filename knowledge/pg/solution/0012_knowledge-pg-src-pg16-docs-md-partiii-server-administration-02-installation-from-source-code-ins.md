# Uninstallation / Cleaning

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Building and Installation with Meson > Uninstallation / Cleaning`
- Source Line Ranges: `425-429, 430-1187, 1188-1212, 1338-1342, 1343-1891`
- Chunk ID: `pg16_solution_0012_c073b0ef53`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `78c5650e4c06652d860e109da92442dc927ebd7f53469c2491457c24d1617921`

## Retrieval Guidance

- Use When: 需要撤销 Meson 安装或清理构建产物。
- Retrieval Keywords: ninja uninstall, ninja clean, Meson clean
- Follow-up Guidance: 检查安装目录中是否还有手工创建的文件。
- Classification Note: 说明 ninja uninstall 和 ninja clean 的卸载/清理动作。

## Official Source Content

## Uninstallation:

To undo the installation use the command `make
uninstall`. However, this will not remove any created directories.

## Cleaning:

After the installation you can free disk space by removing the built
files from the source tree with the command `make
clean`. This will preserve the files made by the `configure`
program, so that you can rebuild everything with `make`
later on. To reset the source tree to the state in which it was
distributed, use `make distclean`. If you are going to
build for several platforms within the same source tree you must do
this and re-configure for each platform.  (Alternatively, use
a separate build tree for each platform, so that the source tree
remains unmodified.)

If you perform a build and then discover that your `configure`
options were wrong, or if you change anything that `configure`
investigates (for example, software upgrades), then it's a good
idea to do `make distclean` before reconfiguring and
rebuilding.  Without this, your changes in configuration choices
might not propagate everywhere they need to.

### `configure` Options

`configure`'s command line options are explained below.
This list is not exhaustive (use `./configure --help`
to get one that is).  The options not covered here are meant for
advanced use-cases such as cross-compilation, and are documented in
the standard Autoconf documentation.

#### Installation Locations

These options control where `make install` will put
the files.  The `--prefix` option is sufficient for
most cases.  If you have special needs, you can customize the
installation subdirectories with the other options described in this
section.  Beware however that changing the relative locations of the
different subdirectories may render the installation non-relocatable,
meaning you won't be able to move it after installation.
(The `man` and `doc` locations are
not affected by this restriction.)  For relocatable installs, you
might want to use the `--disable-rpath` option
described later.

**`--prefix=`PREFIX``**
: Install all files under the directory `PREFIX`
instead of `/usr/local/pgsql`. The actual
files will be installed into various subdirectories; no files
will ever be installed directly into the
`PREFIX` directory.

**`--exec-prefix=`EXEC-PREFIX``**
: You can install architecture-dependent files under a
different prefix, `EXEC-PREFIX`, than what
`PREFIX` was set to. This can be useful to
share architecture-independent files between hosts. If you
omit this, then `EXEC-PREFIX` is set equal to
`PREFIX` and both architecture-dependent and
independent files will be installed under the same tree,
which is probably what you want.

**`--bindir=`DIRECTORY``**
: Specifies the directory for executable programs. The default
is ``EXEC-PREFIX`/bin`, which
normally means `/usr/local/pgsql/bin`.

**`--sysconfdir=`DIRECTORY``**
: Sets the directory for various configuration files,
``PREFIX`/etc` by default.

**`--libdir=`DIRECTORY``**
: Sets the location to install libraries and dynamically loadable
modules. The default is
``EXEC-PREFIX`/lib`.

**`--includedir=`DIRECTORY``**
: Sets the directory for installing C and C++ header files. The
default is ``PREFIX`/include`.

**`--datarootdir=`DIRECTORY``**
: Sets the root directory for various types of read-only data
files.  This only sets the default for some of the following
options.  The default is
``PREFIX`/share`.

**`--datadir=`DIRECTORY``**
: Sets the directory for read-only data files used by the
installed programs. The default is
``DATAROOTDIR``. Note that this has
nothing to do with where your database files will be placed.

**`--localedir=`DIRECTORY``**
: Sets the directory for installing locale data, in particular
message translation catalog files.  The default is
``DATAROOTDIR`/locale`.

**`--mandir=`DIRECTORY``**
: The man pages that come with PostgreSQL will be installed under
this directory, in their respective
`man`x`` subdirectories.
The default is ``DATAROOTDIR`/man`.

**`--docdir=`DIRECTORY``**
: Sets the root directory for installing documentation files,
except "man" pages.  This only sets the default for
the following options.  The default value for this option is
``DATAROOTDIR`/doc/postgresql`.

**`--htmldir=`DIRECTORY``**
: The HTML-formatted documentation for
PostgreSQL will be installed under
this directory.  The default is
``DATAROOTDIR``.

> **Note:**

> Care has been taken to make it possible to install
> PostgreSQL into shared installation locations
> (such as `/usr/local/include`) without
> interfering with the namespace of the rest of the system. First,
> the string "`/postgresql`" is
> automatically appended to `datadir`,
> `sysconfdir`, and `docdir`,
> unless the fully expanded directory name already contains the
> string "`postgres`" or
> "`pgsql`". For example, if you choose
> `/usr/local` as prefix, the documentation will
> be installed in `/usr/local/doc/postgresql`,
> but if the prefix is `/opt/postgres`, then it
> will be in `/opt/postgres/doc`. The public C
> header files of the client interfaces are installed into
> `includedir` and are namespace-clean. The
> internal header files and the server header files are installed
> into private directories under `includedir`. See
> the documentation of each interface for information about how to
> access its header files. Finally, a private subdirectory will
> also be created, if appropriate, under `libdir`
> for dynamically loadable modules.
>

#### PostgreSQL Features

The options described in this section enable building of
various PostgreSQL features that are not
built by default.  Most of these are non-default only because they
require additional software, as described in
[install-requirements](#install-requirements).

**`--enable-nls=`LANGUAGES``**
: Enables Native Language Support (NLS),
that is, the ability to display a program's messages in a
language other than English.
`LANGUAGES` is an optional space-separated
list of codes of the languages that you want supported, for
example `--enable-nls='de fr'`.  (The intersection
between your list and the set of actually provided
translations will be computed automatically.)  If you do not
specify a list, then all available translations are
installed.

To use this option, you will need an implementation of the
Gettext API.

**`--with-perl`**
: Build the PL/Perl server-side language.

**`--with-python`**
: Build the PL/Python server-side language.

**`--with-tcl`**
: Build the PL/Tcl server-side language.

**`--with-tclconfig=`DIRECTORY``**
: Tcl installs the file `tclConfig.sh`, which
contains configuration information needed to build modules
interfacing to Tcl. This file is normally found automatically
at a well-known location, but if you want to use a different
version of Tcl you can specify the directory in which to look
for `tclConfig.sh`.

**`--with-llvm`**
: Build with support for LLVM based
JIT compilation (see [jit](#jit)).  This
requires the LLVM library to be installed.
The minimum required version of LLVM is
currently 3.9.

`llvm-config`
will be used to find the required compilation options.
`llvm-config`, and then
`llvm-config-$major-$minor` for all supported
versions, will be searched for in your `PATH`.  If
that would not yield the desired program,
use `LLVM_CONFIG` to specify a path to the
correct `llvm-config`. For example

```
./configure ... --with-llvm LLVM_CONFIG='/path/to/llvm/bin/llvm-config'
```

LLVM support requires a compatible
`clang` compiler (specified, if necessary, using the
`CLANG` environment variable), and a working C++
compiler (specified, if necessary, using the `CXX`
environment variable).

**`--with-lz4`**
: Build with LZ4 compression support.

**`--with-zstd`**
: Build with Zstandard compression support.

**`--with-ssl=`LIBRARY``**
: Build with support for SSL (encrypted)
connections. The only `LIBRARY`
supported is `openssl`. This requires the
OpenSSL package to be installed.
`configure` will check for the required
header files and libraries to make sure that your
OpenSSL installation is sufficient
before proceeding.

**`--with-openssl`**
: Obsolete equivalent of `--with-ssl=openssl`.

**`--with-gssapi`**
: Build with support for GSSAPI authentication. MIT Kerberos is required
to be installed for GSSAPI.  On many systems, the GSSAPI system (a part
of the MIT Kerberos installation) is not installed in a location
that is searched by default (e.g., `/usr/include`,
`/usr/lib`), so you must use the options
`--with-includes` and `--with-libraries` in
addition to this option.  `configure` will check
for the required header files and libraries to make sure that
your GSSAPI installation is sufficient before proceeding.

**`--with-ldap`**
: Build with LDAP
support for authentication and connection parameter lookup (see
[libpq-ldap](#libpq-ldap) and
[auth-ldap](#auth-ldap) for more information). On Unix,
this requires the OpenLDAP package to be
installed. On Windows, the default WinLDAP
library is used.  `configure` will check for the required
header files and libraries to make sure that your
OpenLDAP installation is sufficient before
proceeding.

**`--with-pam`**
: Build with PAM
(Pluggable Authentication Modules) support.

**`--with-bsd-auth`**
: Build with BSD Authentication support.
(The BSD Authentication framework is
currently only available on OpenBSD.)

**`--with-systemd`**
: Build with support
for systemd
service notifications.  This improves integration if the server
is started under systemd but has no impact
otherwise; see [server-start](#server-start) for more
information.  libsystemd and the
associated header files need to be installed to use this option.

**`--with-bonjour`**
: Build with support for Bonjour automatic service discovery.
This requires Bonjour support in your operating system.
Recommended on macOS.

**`--with-uuid=`LIBRARY``**
: Build the [uuid-ossp](#uuid-ossp) module
(which provides functions to generate UUIDs), using the specified
UUID library.
`LIBRARY` must be one of:

- `bsd` to use the UUID functions found in FreeBSD
and some other BSD-derived systems
- `e2fs` to use the UUID library created by
the `e2fsprogs` project; this library is present in most
Linux systems and in macOS, and can be obtained for other
platforms as well
- `ossp` to use the [OSSP UUID library](http://www.ossp.org/pkg/lib/uuid/)

**`--with-ossp-uuid`**
: Obsolete equivalent of `--with-uuid=ossp`.

**`--with-libxml`**
: Build with libxml2, enabling SQL/XML support.  Libxml2 version 2.6.23 or
later is required for this feature.

To detect the required compiler and linker options, PostgreSQL will
query `pkg-config`, if that is installed and knows
about libxml2.  Otherwise the program `xml2-config`,
which is installed by libxml2, will be used if it is found.  Use
of `pkg-config` is preferred, because it can deal
with multi-architecture installations better.

To use a libxml2 installation that is in an unusual location, you
can set `pkg-config`-related environment
variables (see its documentation), or set the environment variable
`XML2_CONFIG` to point to
the `xml2-config` program belonging to the libxml2
installation, or set the variables `XML2_CFLAGS`
and `XML2_LIBS`.  (If `pkg-config` is
installed, then to override its idea of where libxml2 is you must
either set `XML2_CONFIG` or set
both `XML2_CFLAGS` and `XML2_LIBS` to
nonempty strings.)

**`--with-libxslt`**
: Build with libxslt, enabling the
[xml2](#xml2)
module to perform XSL transformations of XML.
`--with-libxml` must be specified as well.

#### Anti-Features

The options described in this section allow disabling
certain PostgreSQL features that are built
by default, but which might need to be turned off if the required
software or system features are not available.  Using these options is
not recommended unless really necessary.

**`--without-icu`**
: Build without support for the
ICU
library, disabling the use of ICU collation features (see [collation](#collation)).

**`--without-readline`**
: Prevents use of the Readline library
(and libedit as well).  This option disables
command-line editing and history in
psql.

**`--with-libedit-preferred`**
: Favors the use of the BSD-licensed libedit library
rather than GPL-licensed Readline.  This option
is significant only if you have both libraries installed; the
default in that case is to use Readline.

**`--without-zlib`**
: Prevents use of the Zlib library.
This disables
support for compressed archives in pg_dump
and pg_restore.

**`--disable-spinlocks`**
: Allow the build to succeed even if PostgreSQL
has no CPU spinlock support for the platform.  The lack of
spinlock support will result in very poor performance; therefore,
this option should only be used if the build aborts and
informs you that the platform lacks spinlock support. If this
option is required to build PostgreSQL on
your platform, please report the problem to the
PostgreSQL developers.

**`--disable-atomics`**
: Disable use of CPU atomic operations.  This option does nothing on
platforms that lack such operations.  On platforms that do have
them, this will result in poor performance.  This option is only
useful for debugging or making performance comparisons.

**`--disable-thread-safety`**
: Disable the thread-safety of client libraries.  This prevents
concurrent threads in libpq and
ECPG programs from safely controlling
their private connection handles.  Use this only on platforms
with deficient threading support.

#### Build Process Details

**`--with-includes=`DIRECTORIES``**
: `DIRECTORIES` is a colon-separated list of
directories that will be added to the list the compiler
searches for header files. If you have optional packages
(such as GNU Readline) installed in a non-standard
location,
you have to use this option and probably also the corresponding
`--with-libraries` option.

Example: `--with-includes=/opt/gnu/include:/usr/sup/include`.

**`--with-libraries=`DIRECTORIES``**
: `DIRECTORIES` is a colon-separated list of
directories to search for libraries. You will probably have
to use this option (and the corresponding
`--with-includes` option) if you have packages
installed in non-standard locations.

Example: `--with-libraries=/opt/gnu/lib:/usr/sup/lib`.

**`--with-system-tzdata=`DIRECTORY``**
: PostgreSQL includes its own time zone database,
which it requires for date and time operations.  This time zone
database is in fact compatible with the IANA time zone
database provided by many operating systems such as FreeBSD,
Linux, and Solaris, so it would be redundant to install it again.
When this option is used, the system-supplied time zone database
in `DIRECTORY` is used instead of the one
included in the PostgreSQL source distribution.
`DIRECTORY` must be specified as an
absolute path.  `/usr/share/zoneinfo` is a
likely directory on some operating systems.  Note that the
installation routine will not detect mismatching or erroneous time
zone data.  If you use this option, you are advised to run the
regression tests to verify that the time zone data you have
pointed to works correctly with PostgreSQL.

This option is mainly aimed at binary package distributors
who know their target operating system well.  The main
advantage of using this option is that the PostgreSQL package
won't need to be upgraded whenever any of the many local
daylight-saving time rules change.  Another advantage is that
PostgreSQL can be cross-compiled more straightforwardly if the
time zone database files do not need to be built during the
installation.

**`--with-extra-version=`STRING``**
: Append `STRING` to the PostgreSQL version number.  You
can use this, for example, to mark binaries built from unreleased Git
snapshots or containing custom patches with an extra version string,
such as a `git describe` identifier or a
distribution package release number.

**`--disable-rpath`**
: Do not mark PostgreSQL's executables
to indicate that they should search for shared libraries in the
installation's library directory (see `--libdir`).
On most platforms, this marking uses an absolute path to the
library directory, so that it will be unhelpful if you relocate
the installation later.  However, you will then need to provide
some other way for the executables to find the shared libraries.
Typically this requires configuring the operating system's
dynamic linker to search the library directory; see
[install-post-shlibs](#install-post-shlibs) for more detail.

#### Miscellaneous

It's fairly common, particularly for test builds, to adjust the
default port number with `--with-pgport`.
The other options in this section are recommended only for advanced
users.

**`--with-pgport=`NUMBER``**
: Set `NUMBER` as the default port number for
server and clients. The default is 5432. The port can always
be changed later on, but if you specify it here then both
server and clients will have the same default compiled in,
which can be very convenient.  Usually the only good reason
to select a non-default value is if you intend to run multiple
PostgreSQL servers on the same machine.

**`--with-krb-srvnam=`NAME``**
: The default name of the Kerberos service principal used
by GSSAPI.
`postgres` is the default. There's usually no
reason to change this unless you are building for a Windows
environment, in which case it must be set to upper case
`POSTGRES`.

**`--with-segsize=`SEGSIZE``**
: Set the *segment size*, in gigabytes.  Large tables are
divided into multiple operating-system files, each of size equal
to the segment size.  This avoids problems with file size limits
that exist on many platforms.  The default segment size, 1 gigabyte,
is safe on all supported platforms.  If your operating system has
"largefile" support (which most do, nowadays), you can use
a larger segment size.  This can be helpful to reduce the number of
file descriptors consumed when working with very large tables.
But be careful not to select a value larger than is supported
by your platform and the file systems you intend to use.  Other
tools you might wish to use, such as tar, could
also set limits on the usable file size.
It is recommended, though not absolutely required, that this value
be a power of 2.
Note that changing this value breaks on-disk database compatibility,
meaning you cannot use `pg_upgrade` to upgrade to
a build with a different segment size.

**`--with-blocksize=`BLOCKSIZE``**
: Set the *block size*, in kilobytes.  This is the unit
of storage and I/O within tables.  The default, 8 kilobytes,
is suitable for most situations; but other values may be useful
in special cases.
The value must be a power of 2 between 1 and 32 (kilobytes).
Note that changing this value breaks on-disk database compatibility,
meaning you cannot use `pg_upgrade` to upgrade to
a build with a different block size.

**`--with-wal-blocksize=`BLOCKSIZE``**
: Set the *WAL block size*, in kilobytes.  This is the unit
of storage and I/O within the WAL log.  The default, 8 kilobytes,
is suitable for most situations; but other values may be useful
in special cases.
The value must be a power of 2 between 1 and 64 (kilobytes).
Note that changing this value breaks on-disk database compatibility,
meaning you cannot use `pg_upgrade` to upgrade to
a build with a different WAL block size.

#### Developer Options

Most of the options in this section are only of interest for
developing or debugging PostgreSQL.
They are not recommended for production builds, except
for `--enable-debug`, which can be useful to enable
detailed bug reports in the unlucky event that you encounter a bug.
On platforms supporting DTrace, `--enable-dtrace`
may also be reasonable to use in production.

When building an installation that will be used to develop code inside
the server, it is recommended to use at least the
options `--enable-debug`
and `--enable-cassert`.

**`--enable-debug`**
: Compiles all programs and libraries with debugging symbols.
This means that you can run the programs in a debugger
to analyze problems. This enlarges the size of the installed
executables considerably, and on non-GCC compilers it usually
also disables compiler optimization, causing slowdowns. However,
having the symbols available is extremely helpful for dealing
with any problems that might arise.  Currently, this option is
recommended for production installations only if you use GCC.
But you should always have it on if you are doing development work
or running a beta version.

**`--enable-cassert`**
: Enables *assertion* checks in the server, which test for
many "cannot happen" conditions.  This is invaluable for
code development purposes, but the tests can slow down the
server significantly.
Also, having the tests turned on won't necessarily enhance the
stability of your server!  The assertion checks are not categorized
for severity, and so what might be a relatively harmless bug will
still lead to server restarts if it triggers an assertion
failure.  This option is not recommended for production use, but
you should have it on for development work or when running a beta
version.

**`--enable-tap-tests`**
: Enable tests using the Perl TAP tools.  This requires a Perl
installation and the Perl module `IPC::Run`.
See [regress-tap](#regress-tap) for more information.

**`--enable-depend`**
: Enables automatic dependency tracking.  With this option, the
makefiles are set up so that all affected object files will
be rebuilt when any header file is changed.  This is useful
if you are doing development work, but is just wasted overhead
if you intend only to compile once and install.  At present,
this option only works with GCC.

**`--enable-coverage`**
: If using GCC, all programs and libraries are compiled with
code coverage testing instrumentation.  When run, they
generate files in the build directory with code coverage
metrics.
See [regress-coverage](#regress-coverage)
for more information. This option is for use only with GCC
and when doing development work.

**`--enable-profiling`**
: If using GCC, all programs and libraries are compiled so they
can be profiled.  On backend exit, a subdirectory will be created
that contains the `gmon.out` file containing
profile data.
This option is for use only with GCC and when doing development work.

**`--enable-dtrace`**
: Compiles PostgreSQL with support for the
dynamic tracing tool DTrace.
See [dynamic-trace](#dynamic-trace)
for more information.

To point to the `dtrace` program, the
environment variable `DTRACE` can be set.  This
will often be necessary because `dtrace` is
typically installed under `/usr/sbin`,
which might not be in your `PATH`.

Extra command-line options for the `dtrace` program
can be specified in the environment variable
`DTRACEFLAGS`.  On Solaris,
to include DTrace support in a 64-bit binary, you must specify
`DTRACEFLAGS="-64"`.  For example,
using the GCC compiler:

```
./configure CC='gcc -m64' --enable-dtrace DTRACEFLAGS='-64' ...
```

Using Sun's compiler:

```
./configure CC='/opt/SUNWspro/bin/cc -xtarget=native64' --enable-dtrace DTRACEFLAGS='-64' ...
```

**`--with-segsize-blocks=SEGSIZE_BLOCKS`**
: Specify the relation segment size in blocks. If both
`--with-segsize` and this option are specified, this
option wins.

This option is only for developers, to test segment related code.

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

## Building and Installation with Meson

### Short Version

```
meson setup build --prefix=/usr/local/pgsql
cd build
ninja
su
ninja install
adduser postgres
mkdir -p /usr/local/pgsql/data
chown postgres /usr/local/pgsql/data
su - postgres
/usr/local/pgsql/bin/initdb -D /usr/local/pgsql/data
/usr/local/pgsql/bin/pg_ctl -D /usr/local/pgsql/data -l logfile start
/usr/local/pgsql/bin/createdb test
/usr/local/pgsql/bin/psql test
```

The long version is the rest of this
section.

### Installation Procedure

## Uninstallation:

To undo the installation, you can use the `ninja
uninstall` command.

## Cleaning:

After the installation, you can free disk space by removing the built
files from the source tree with the `ninja clean`
command.

### `meson setup` Options

`meson setup`'s command-line options are explained below.
This list is not exhaustive (use `meson configure --help`
to get one that is).  The options not covered here are meant for advanced
use-cases, and are documented in the standard [Meson
documentation](https://mesonbuild.com/Commands.html#configure).  These arguments can be used with `meson
setup` as well.

#### Installation Locations

These options control where `ninja install` (or `meson install`) will put
the files.  The `--prefix` option (example
[install-short-meson](#install-short-meson)) is sufficient for
most cases.  If you have special needs, you can customize the
installation subdirectories with the other options described in this
section.  Beware however that changing the relative locations of the
different subdirectories may render the installation non-relocatable,
meaning you won't be able to move it after installation.
(The `man` and `doc` locations are
not affected by this restriction.)  For relocatable installs, you
might want to use the `-Drpath=false` option
described later.

**`--prefix=`PREFIX``**
: Install all files under the directory `PREFIX`
instead of `/usr/local/pgsql` (on Unix based systems) or
``current drive letter`:/usr/local/pgsql` (on Windows).
The actual files will be installed into various subdirectories; no files
will ever be installed directly into the
`PREFIX` directory.

**`--bindir=`DIRECTORY``**
: Specifies the directory for executable programs. The default
is ``PREFIX`/bin`.

**`--sysconfdir=`DIRECTORY``**
: Sets the directory for various configuration files,
``PREFIX`/etc` by default.

**`--libdir=`DIRECTORY``**
: Sets the location to install libraries and dynamically loadable
modules. The default is
``PREFIX`/lib`.

**`--includedir=`DIRECTORY``**
: Sets the directory for installing C and C++ header files. The
default is ``PREFIX`/include`.

**`--datadir=`DIRECTORY``**
: Sets the directory for read-only data files used by the
installed programs. The default is
``PREFIX`/share`. Note that this has
nothing to do with where your database files will be placed.

**`--localedir=`DIRECTORY``**
: Sets the directory for installing locale data, in particular
message translation catalog files.  The default is
``DATADIR`/locale`.

**`--mandir=`DIRECTORY``**
: The man pages that come with PostgreSQL will be installed under
this directory, in their respective
`man`x`` subdirectories.
The default is ``DATADIR`/man`.

> **Note:**

> Care has been taken to make it possible to install
> PostgreSQL into shared installation locations
> (such as `/usr/local/include`) without
> interfering with the namespace of the rest of the system. First,
> the string "`/postgresql`" is
> automatically appended to `datadir`,
> `sysconfdir`, and `docdir`,
> unless the fully expanded directory name already contains the
> string "`postgres`" or
> "`pgsql`". For example, if you choose
> `/usr/local` as prefix, the documentation will
> be installed in `/usr/local/doc/postgresql`,
> but if the prefix is `/opt/postgres`, then it
> will be in `/opt/postgres/doc`. The public C
> header files of the client interfaces are installed into
> `includedir` and are namespace-clean. The
> internal header files and the server header files are installed
> into private directories under `includedir`. See
> the documentation of each interface for information about how to
> access its header files. Finally, a private subdirectory will
> also be created, if appropriate, under `libdir`
> for dynamically loadable modules.
>

#### PostgreSQL Features

The options described in this section enable building of
various optional PostgreSQL features.
Most of these require additional software, as described in
[install-requirements](#install-requirements), and will be automatically enabled if the
required software is found. You can change this behavior by manually
setting these features to `enabled` to require them
or `disabled` to not build with them.

To specify PostgreSQL-specific options, the name of the option
must be prefixed by `-D`.

**`-Dnls={ auto | enabled | disabled }`**
: Enables or disables Native Language Support (NLS),
that is, the ability to display a program's messages in a language
other than English.  Defaults to auto and will be enabled
automatically if an implementation of the Gettext
API is found.

**`-Dplperl={ auto | enabled | disabled }`**
: Build the PL/Perl server-side language.
Defaults to auto.

**`-Dplpython={ auto | enabled | disabled }`**
: Build the PL/Python server-side language.
Defaults to auto.

**`-Dpltcl={ auto | enabled | disabled }`**
: Build the PL/Tcl server-side language.
Defaults to auto.

**`-Dtcl_version=`TCL_VERSION``**
: Specifies the Tcl version to use when building PL/Tcl.

**`-Dicu={ auto | enabled | disabled }`**
: Build with support for the
ICU
library, enabling use of ICU collation features (see [collation](#collation)).  Defaults to auto and requires the
ICU4C package to be installed.  The minimum
required version of ICU4C is currently 4.2.

**`-Dllvm={ auto | enabled | disabled }`**
: Build with support for LLVM based
JIT compilation (see [jit](#jit)).
This requires the LLVM library to be
installed.  The minimum required version of
LLVM is currently 3.9.  Disabled by
default.

`llvm-config`
will be used to find the required compilation options.
`llvm-config`, and then
`llvm-config-$version` for all supported versions,
will be searched for in your `PATH`.  If that would not
yield the desired program, use `LLVM_CONFIG` to specify a
path to the correct `llvm-config`.

**`-Dlz4={ auto | enabled | disabled }`**
: Build with LZ4 compression support.
Defaults to auto.

**`-Dzstd={ auto | enabled | disabled }`**
: Build with Zstandard compression support.
Defaults to auto.

**`-Dssl={ auto | `LIBRARY` }`**
: Build with support for SSL (encrypted) connections.
The only `LIBRARY` supported is
`openssl`. This requires the
OpenSSL package to be installed.  Building
with this will check for the required header files and libraries to
make sure that your OpenSSL installation is
sufficient before proceeding.  The default for this option is auto.

**`-Dgssapi={ auto | enabled | disabled }`**
: Build with support for GSSAPI authentication. MIT Kerberos is required
to be installed for GSSAPI.  On many systems, the GSSAPI system (a part
of the MIT Kerberos installation) is not installed in a location
that is searched by default (e.g., `/usr/include`,
`/usr/lib`).  In
those cases, PostgreSQL will query `pkg-config` to
detect the required compiler and linker options.  Defaults to auto.
`meson configure` will check for the required
header files and libraries to make sure that your GSSAPI installation
is sufficient before proceeding.

**`-Dldap={ auto | enabled | disabled }`**
: Build with
LDAP
support for authentication and connection parameter lookup (see
[libpq-ldap](#libpq-ldap) and
[auth-ldap](#auth-ldap) for more information).  On Unix,
this requires the OpenLDAP package to be
installed. On Windows, the default WinLDAP
library is used.  Defaults to auto.  `meson
configure` will check for the required header files and
libraries to make sure that your OpenLDAP
installation is sufficient before proceeding.

**`-Dpam={ auto | enabled | disabled }`**
: Build with
PAM
(Pluggable Authentication Modules) support.  Defaults to auto.

**`-Dbsd_auth={ auto | enabled | disabled }`**
: Build with BSD Authentication support.  (The BSD Authentication
framework is currently only available on OpenBSD.)  Defaults to auto.

**`-Dsystemd={ auto | enabled | disabled }`**
: Build with support for
systemd
service notifications.  This improves integration if the server is
started under systemd but has no impact
otherwise; see [server-start](#server-start) for more information.  Defaults to
auto.  libsystemd and the associated header
files need to be installed to use this option.

**`-Dbonjour={ auto | enabled | disabled }`**
: Build with support for Bonjour automatic service discovery.  Defaults
to auto and requires Bonjour support in your operating system.
Recommended on macOS.

**`-Duuid=`LIBRARY``**
: Build the [uuid-ossp](#uuid-ossp) module
(which provides functions to generate UUIDs), using the specified
UUID library.
`LIBRARY` must be one of:

- `none` to not build the uuid module. This is the default.
- `bsd` to use the UUID functions found in FreeBSD,
and some other BSD-derived systems
- `e2fs` to use the UUID library created by
the `e2fsprogs` project; this library is present in most
Linux systems and in macOS, and can be obtained for other
platforms as well
- `ossp` to use the [OSSP UUID library](http://www.ossp.org/pkg/lib/uuid/)

**`-Dlibxml={ auto | enabled | disabled }`**
: Build with libxml2, enabling SQL/XML support.  Defaults to
auto. Libxml2 version 2.6.23 or later is required for this feature.

To use a libxml2 installation that is in an unusual location, you
can set `pkg-config`-related environment
variables (see its documentation).

**`-Dlibxslt={ auto | enabled | disabled }`**
: Build with libxslt, enabling the
[xml2](#xml2)
module to perform XSL transformations of XML.
`-Dlibxml` must be specified as well.  Defaults to
auto.

#### Anti-Features

**`-Dreadline={ auto | enabled | disabled }`**
: Allows use of the Readline library (and
libedit as well).  This option defaults to
auto and enables command-line editing and history in
psql and is strongly recommended.

**`-Dlibedit_preferred={ true | false }`**
: Setting this to true favors the use of the BSD-licensed
libedit library rather than GPL-licensed
Readline.  This option is significant only
if you have both libraries installed; the default is false, that is to
use Readline.

**`-Dzlib={ auto | enabled | disabled }`**
: Enables use of the Zlib library.
It defaults to auto and enables
support for compressed archives in pg_dump,
pg_restore and pg_basebackup and is recommended.

**`-Dspinlocks={ true | false }`**
: This option is set to true by default; setting it to false will
allow the build to succeed even if PostgreSQL
has no CPU spinlock support for the platform.  The lack of
spinlock support will result in very poor performance; therefore,
this option should only be changed if the build aborts and
informs you that the platform lacks spinlock support. If setting this
option to false is required to build PostgreSQL on
your platform, please report the problem to the
PostgreSQL developers.

**`-Datomics={ true | false }`**
: This option is set to true by default; setting it to false will
disable use of CPU atomic operations.  The option does nothing on
platforms that lack such operations.  On platforms that do have
them, disabling atomics will result in poor performance.  Changing
this option is only useful for debugging or making performance comparisons.

#### Build Process Details

**`--auto-features={ auto | enabled | disabled }`**
: Setting this option allows you to override the value of all
"auto" features (features that are enabled automatically
if the required software is found).  This can be useful when you want
to disable or enable all the "optional" features at once
without having to set each of them manually. The default value for
this parameter is auto.

**`--backend=`BACKEND``**
: The default backend Meson uses is ninja and that should suffice for
most use cases.  However, if you'd like to fully integrate with Visual
Studio, you can set the `BACKEND` to
`vs`.

**`-Dc_args=`OPTIONS``**
: This option can be used to pass extra options to the C compiler.

**`-Dc_link_args=`OPTIONS``**
: This option can be used to pass extra options to the C linker.

**`-Dextra_include_dirs=`DIRECTORIES``**
: `DIRECTORIES` is a comma-separated list of
directories that will be added to the list the compiler searches for
header files. If you have optional packages (such as GNU
Readline) installed in a non-standard
location, you have to use this option and probably also the
corresponding `-Dextra_lib_dirs` option.

Example: `-Dextra_include_dirs=/opt/gnu/include,/usr/sup/include`.

**`-Dextra_lib_dirs=`DIRECTORIES``**
: `DIRECTORIES` is a comma-separated list of
directories to search for libraries. You will probably have to use
this option (and the corresponding
`-Dextra_include_dirs` option) if you have packages
installed in non-standard locations.

Example: `-Dextra_lib_dirs=/opt/gnu/lib,/usr/sup/lib`.

**`-Dsystem_tzdata=`DIRECTORY``**
: PostgreSQL includes its own time zone
database, which it requires for date and time operations.  This time
zone database is in fact compatible with the IANA time zone database
provided by many operating systems such as FreeBSD, Linux, and
Solaris, so it would be redundant to install it again.  When this
option is used, the system-supplied time zone database in
`DIRECTORY` is used instead of the one
included in the PostgreSQL source distribution.
`DIRECTORY` must be specified as an absolute
path.  `/usr/share/zoneinfo` is a likely directory
on some operating systems.  Note that the installation routine will
not detect mismatching or erroneous time zone data.  If you use this
option, you are advised to run the regression tests to verify that the
time zone data you have pointed to works correctly with
PostgreSQL.

This option is mainly aimed at binary package distributors who know
their target operating system well.  The main advantage of using this
option is that the PostgreSQL package won't need to be upgraded
whenever any of the many local daylight-saving time rules change.
Another advantage is that PostgreSQL can be cross-compiled more
straightforwardly if the time zone database files do not need to be
built during the installation.

**`-Dextra_version=`STRING``**
: Append `STRING` to the PostgreSQL version
number.  You can use this, for example, to mark binaries built from
unreleased Git snapshots or containing
custom patches with an extra version string, such as a `git
describe` identifier or a distribution package release
number.

**`-Drpath={ true | false }`**
: This option is set to true by default.  If set to false,
do not mark PostgreSQL's executables
to indicate that they should search for shared libraries in the
installation's library directory (see `--libdir`).
On most platforms, this marking uses an absolute path to the
library directory, so that it will be unhelpful if you relocate
the installation later.  However, you will then need to provide
some other way for the executables to find the shared libraries.
Typically this requires configuring the operating system's
dynamic linker to search the library directory; see
[install-post-shlibs](#install-post-shlibs) for more detail.

**`-D`BINARY_NAME`=`PATH``**
: If a program required to build PostgreSQL (with or without optional
flags) is stored at a non-standard path, you can specify it manually
to `meson configure`.  The complete list of programs
for which this is supported can be found by running `meson
configure`.  Example:

```
meson configure -DBISON=PATH_TO_BISON
```

#### Documentation

See [docguide-toolsets](#docguide-toolsets) for the tools needed for building
the documentation.

**`-Ddocs={ auto | enabled | disabled }`**
: Enables building the documentation in HTML and
man format. It defaults to auto.

**`-Ddocs_pdf={ auto | enabled | disabled }`**
: Enables building the documentation in PDF
format. It defaults to auto.

**`-Ddocs_html_style={ simple | website }`**
: Controls which CSS stylesheet is used.  The default
is `simple`.  If set to `website`,
the HTML documentation will reference the stylesheet for [postgresql.org](https://www.postgresql.org/docs/current/).

#### Miscellaneous

**`-Dpgport=`NUMBER``**
: Set `NUMBER` as the default port number for
server and clients. The default is 5432. The port can always
be changed later on, but if you specify it here then both
server and clients will have the same default compiled in,
which can be very convenient.  Usually the only good reason
to select a non-default value is if you intend to run multiple
PostgreSQL servers on the same machine.

**`-Dkrb_srvnam=`NAME``**
: The default name of the Kerberos service principal used
by GSSAPI.
`postgres` is the default. There's usually no
reason to change this unless you are building for a Windows
environment, in which case it must be set to upper case
`POSTGRES`.

**`-Dsegsize=`SEGSIZE``**
: Set the *segment size*, in gigabytes.  Large tables are
divided into multiple operating-system files, each of size equal
to the segment size.  This avoids problems with file size limits
that exist on many platforms.  The default segment size, 1 gigabyte,
is safe on all supported platforms.  If your operating system has
"largefile" support (which most do, nowadays), you can use
a larger segment size.  This can be helpful to reduce the number of
file descriptors consumed when working with very large tables.
But be careful not to select a value larger than is supported
by your platform and the file systems you intend to use.  Other
tools you might wish to use, such as tar, could
also set limits on the usable file size.
It is recommended, though not absolutely required, that this value
be a power of 2.

**`-Dblocksize=`BLOCKSIZE``**
: Set the *block size*, in kilobytes.  This is the unit
of storage and I/O within tables.  The default, 8 kilobytes,
is suitable for most situations; but other values may be useful
in special cases.
The value must be a power of 2 between 1 and 32 (kilobytes).

**`-Dwal_blocksize=`BLOCKSIZE``**
: Set the *WAL block size*, in kilobytes.  This is the unit
of storage and I/O within the WAL log.  The default, 8 kilobytes,
is suitable for most situations; but other values may be useful
in special cases.
The value must be a power of 2 between 1 and 64 (kilobytes).

#### Developer Options

Most of the options in this section are only of interest for
developing or debugging PostgreSQL.
They are not recommended for production builds, except
for `--debug`, which can be useful to enable
detailed bug reports in the unlucky event that you encounter a bug.
On platforms supporting DTrace, `-Ddtrace`
may also be reasonable to use in production.

When building an installation that will be used to develop code inside
the server, it is recommended to use at least the `--buildtype=debug`
and `-Dcassert` options.

**`--buildtype=`BUILDTYPE``**
: This option can be used to specify the buildtype to use; defaults to
`debugoptimized`.  If you'd like finer control on the debug
symbols and optimization levels than what this option provides, you
can refer to the `--debug` and
`--optimization` flags.

The following build types are generally used: `plain`,
`debug`, `debugoptimized` and
`release`.  More information about them can be found in
the [Meson
documentation](https://mesonbuild.com/Running-Meson.html#configuring-the-build-directory).

**`--debug`**
: Compiles all programs and libraries with debugging symbols.  This
means that you can run the programs in a debugger to analyze
problems. This enlarges the size of the installed executables
considerably, and on non-GCC compilers it usually also disables
compiler optimization, causing slowdowns. However, having the symbols
available is extremely helpful for dealing with any problems that
might arise.  Currently, this option is recommended for production
installations only if you use GCC.  But you should always have it on
if you are doing development work or running a beta version.

**`--optimization`=`LEVEL`**
: Specify the optimization level. `LEVEL` can be set to any of {0,g,1,2,3,s}.

**`--werror`**
: Setting this option asks the compiler to treat warnings as
errors. This can be useful for code development.

**`-Dcassert={ true | false }`**
: Enables *assertion* checks in the server, which
test for many "cannot happen" conditions.  This is
invaluable for code development purposes, but the tests slow down the
server significantly.  Also, having the tests turned on won't
necessarily enhance the stability of your server!  The assertion
checks are not categorized for severity, and so what might be a
relatively harmless bug will still lead to server restarts if it
triggers an assertion failure.  This option is not recommended for
production use, but you should have it on for development work or when
running a beta version.

**`-Dtap_tests={ auto | enabled | disabled }`**
: Enable tests using the Perl TAP tools.  Defaults to auto and requires
a Perl installation and the Perl module `IPC::Run`.
See [regress-tap](#regress-tap) for more information.

**`-DPG_TEST_EXTRA=`TEST_SUITES``**
: Enable test suites which require special software to run.  This option
accepts arguments via a whitespace-separated list.  See [regress-additional](#regress-additional) for details.

**`-Db_coverage={ true | false }`**
: If using GCC, all programs and libraries are compiled with
code coverage testing instrumentation.  When run, they
generate files in the build directory with code coverage
metrics.
See [regress-coverage](#regress-coverage)
for more information. This option is for use only with GCC
and when doing development work.

**`-Ddtrace={ auto | enabled | disabled }`**
: Enabling this compiles PostgreSQL with support for the
dynamic tracing tool DTrace.
See [dynamic-trace](#dynamic-trace)
for more information.

To point to the `dtrace` program, the
`DTRACE` option can be set.  This
will often be necessary because `dtrace` is
typically installed under `/usr/sbin`,
which might not be in your `PATH`.

**`-Dsegsize_blocks=SEGSIZE_BLOCKS`**
: Specify the relation segment size in blocks. If both
`-Dsegsize` and this option are specified, this option
wins.

This option is only for developers, to test segment related code.
