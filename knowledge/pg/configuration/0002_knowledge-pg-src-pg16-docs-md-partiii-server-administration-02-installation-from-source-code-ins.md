# Installation Locations

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > configure Options > Installation Locations`
- Source Line Ranges: `450-1033, 1358-1440`
- Chunk ID: `pg16_configuration_0002_72908b658b`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b5506755be5df6de660d687ecb058a8e0882e723d48a854e2134aa11e2ab5016`

## Retrieval Guidance

- Use When: 需要定制源码安装目录布局。
- Retrieval Keywords: --prefix, --exec-prefix, --bindir, --sysconfdir, --libdir, --includedir, --datadir, --docdir
- Follow-up Guidance: 检查是否需要 relocatable install 和 --disable-rpath。
- Classification Note: 定义 --prefix、--bindir、--libdir 等安装位置选项语义。

## Official Source Content

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
