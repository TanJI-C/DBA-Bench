# Build

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Building and Installation with Autoconf and Make > Build`
- Source Line Ranges: `224-247, 294-334, 799-865, 1188-1212, 1254-1284, 1285-1305, 1306-1337, 1338-1342, 1343-1891, 1892-2009, 2010-2054, 2055-2400`
- Chunk ID: `pg16_solution_0004_0e9eb02b3b`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6d821f52ed7a08950d6942166068732b7f5912381e11eb92f001ca79ccdd37e2`

## Retrieval Guidance

- Use When: 源码已配置完成，需要实际编译 PostgreSQL。
- Retrieval Keywords: make all, make world, make world-bin, MAKELEVEL
- Follow-up Guidance: 构建失败时检查 GNU make 和依赖版本。
- Classification Note: 给出 make、make world、make world-bin 等构建动作。

## Official Source Content

## Building and Installation with Autoconf and Make

### Short Version

```
./configure
make
su
make install
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

## Build

To start the build, type either of:

```
make
make all
```

(Remember to use GNU make.)
The build will take a few minutes depending on your
hardware.

If you want to build everything that can be built, including the
documentation (HTML and man pages), and the additional modules
(`contrib`), type instead:

```
make world
```

If you want to build everything that can be built, including the
additional modules (`contrib`), but without
the documentation, type instead:

```
make world-bin
```

If you want to invoke the build from another makefile rather than
manually, you must unset `MAKELEVEL` or set it to zero,
for instance like this:

```
build-postgresql:
$(MAKE) -C postgresql MAKELEVEL=0 all
```

Failure to do that can lead to strange error messages, typically about
missing header files.

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

## Build

By default, Meson uses the [Ninja](https://ninja-build.org/) build tool.  To build
PostgreSQL from source using Meson, you can
simply use the `ninja` command in the build directory.

```
ninja
```

Ninja will automatically detect the number of CPUs in your computer and
parallelize itself accordingly. You can override the number of parallel
processes used with the command line argument `-j`.

It should be noted that after the initial configure step,
`ninja` is the only command you ever need to type to
compile. No matter how you alter your source tree (short of moving it to a
completely new location), Meson will detect the changes and regenerate
itself accordingly. This is especially handy if you have multiple build
directories. Often one of them is used for development (the "debug" build)
and others only every now and then (such as a "static analysis" build).
Any configuration can be built just by cd'ing to the corresponding
directory and running Ninja.

If you'd like to build with a backend other than ninja, you can use
configure with the `--backend` option to select the one you
want to use and then build using `meson compile`. To
learn more about these backends and other arguments you can provide to
ninja, you can refer to the [
Meson documentation](https://mesonbuild.com/Running-Meson.html#building-from-the-source).

## Regression Tests

If you want to test the newly built server before you install it,
you can run the regression tests at this point. The regression
tests are a test suite to verify that PostgreSQL
runs on your machine in the way the developers expected it
to. Type:

```
meson test
```

(This won't work as root; do it as an unprivileged user.)
See [regress](#regress) for
detailed information about interpreting the test results. You can
repeat this test at any later time by issuing the same command.

To run pg_regress and pg_isolation_regress tests against a running
postgres instance, specify --setup running as an
argument to meson test.

## Installing the Files

> **Note:**

> If you are upgrading an existing system be sure to read
> [upgrading](#upgrading),
> which has instructions about upgrading a
> cluster.
>

Once PostgreSQL is built, you can install it by simply running the
`ninja install` command.

```
ninja install
```

This will install files into the directories that were specified
in [meson-configure](#meson-configure). Make sure that you have appropriate
permissions to write into that area. You might need to do this
step as root. Alternatively, you can create the target directories
in advance and arrange for appropriate permissions to be granted.
The standard installation provides all the header files needed for client
application development as well as for server-side program
development, such as custom functions or data types written in C.

`ninja install` should work for most cases, but if you'd
like to use more options (such as `--quiet` to suppress
extra output), you could also use `meson install`
instead. You can learn more about [meson install](https://mesonbuild.com/Commands.html#install)
and its options in the Meson documentation.

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

## Platform-Specific Notes

This section documents additional platform-specific issues
regarding the installation and setup of PostgreSQL.  Be sure to
read the installation instructions, and in
particular [install-requirements](#install-requirements) as well.  Also,
check [regress](#regress) regarding the
interpretation of regression test results.

Platforms that are not covered here have no known platform-specific
installation issues.

### AIX

You can use GCC or the native IBM compiler `xlc`
to build PostgreSQL
on AIX.

AIX versions before 7.1 are no longer
tested nor supported by the PostgreSQL
community.

#### Memory Management

AIX can be somewhat peculiar with regards to the way it does
memory management.  You can have a server with many multiples of
gigabytes of RAM free, but still get out of memory or address
space errors when running applications.  One example
is loading of extensions failing with unusual errors.
For example, running as the owner of the PostgreSQL installation:

```
=# CREATE EXTENSION plperl;
ERROR:  could not load library "/opt/dbs/pgsql/lib/plperl.so": A memory address is not in the address space for the process.
```

Running as a non-owner in the group possessing the PostgreSQL
installation:

```
=# CREATE EXTENSION plperl;
ERROR:  could not load library "/opt/dbs/pgsql/lib/plperl.so": Bad address
```

Another example is out of memory errors in the PostgreSQL server
logs, with every memory allocation near or greater than 256 MB
failing.

The overall cause of all these problems is the default bittedness
and memory model used by the server process.  By default, all
binaries built on AIX are 32-bit.  This does not depend upon
hardware type or kernel in use.  These 32-bit processes are
limited to 4 GB of memory laid out in 256 MB segments using one
of a few models.  The default allows for less than 256 MB in the
heap as it shares a single segment with the stack.

In the case of the `plperl` example, above,
check your umask and the permissions of the binaries in your
PostgreSQL installation.  The binaries involved in that example
were 32-bit and installed as mode 750 instead of 755.  Due to the
permissions being set in this fashion, only the owner or a member
of the possessing group can load the library.  Since it isn't
world-readable, the loader places the object into the process'
heap instead of the shared library segments where it would
otherwise be placed.

The "ideal" solution for this is to use a 64-bit
build of PostgreSQL, but that is not always practical, because
systems with 32-bit processors can build, but not run, 64-bit
binaries.

If a 32-bit binary is desired, set `LDR_CNTRL` to
`MAXDATA=0x`n`0000000`,
where 1 <= n <= 8, before starting the PostgreSQL server,
and try different values and `postgresql.conf`
settings to find a configuration that works satisfactorily.  This
use of `LDR_CNTRL` tells AIX that you want the
server to have `MAXDATA` bytes set aside for the
heap, allocated in 256 MB segments.  When you find a workable
configuration,
`ldedit` can be used to modify the binaries so
that they default to using the desired heap size.  PostgreSQL can
also be rebuilt, passing `configure
LDFLAGS="-Wl,-bmaxdata:0x`n`0000000"`
to achieve the same effect.

For a 64-bit build, set `OBJECT_MODE` to 64 and
pass `CC="gcc -maix64"`
and `LDFLAGS="-Wl,-bbigtoc"`
to `configure`.  (Options for
`xlc` might differ.)  If you omit the export of
`OBJECT_MODE`, your build may fail with linker errors.  When
`OBJECT_MODE` is set, it tells AIX's build utilities
such as `ar`, `as`, and `ld` what
type of objects to default to handling.

By default, overcommit of paging space can happen.  While we have
not seen this occur, AIX will kill processes when it runs out of
memory and the overcommit is accessed.  The closest to this that
we have seen is fork failing because the system decided that
there was not enough memory for another process.  Like many other
parts of AIX, the paging space allocation method and
out-of-memory kill is configurable on a system- or process-wide
basis if this becomes a problem.

### Cygwin

PostgreSQL can be built using Cygwin, a Linux-like environment for
Windows, but that method is inferior to the native Windows build
(see [install-windows](#install-windows)) and
running a server under Cygwin is no longer recommended.

When building from source, proceed according to the Unix-style
installation procedure (i.e., `./configure;
make`; etc.), noting the following Cygwin-specific
differences:

- Set your path to use the Cygwin bin directory before the
Windows utilities.  This will help prevent problems with
compilation.
- The `adduser` command is not supported; use
the appropriate user management application on Windows.
Otherwise, skip this step.
- The `su` command is not supported; use ssh to
simulate su on Windows. Otherwise, skip this step.
- OpenSSL is not supported.
- Start `cygserver` for shared memory support.
To do this, enter the command `/usr/sbin/cygserver
&`.  This program needs to be running anytime you
start the PostgreSQL server or initialize a database cluster
(`initdb`).  The
default `cygserver` configuration may need to
be changed (e.g., increase `SEMMNS`) to prevent
PostgreSQL from failing due to a lack of system resources.
- Building might fail on some systems where a locale other than
C is in use. To fix this, set the locale to C by doing
`export LANG=C.utf8` before building, and then
setting it back to the previous setting after you have installed
PostgreSQL.
- The parallel regression tests (`make check`)
can generate spurious regression test failures due to
overflowing the `listen()` backlog queue
which causes connection refused errors or hangs.  You can limit
the number of connections using the make
variable `MAX_CONNECTIONS` thus:

```
make MAX_CONNECTIONS=5 check
```

(On some systems you can have up to about 10 simultaneous
connections.)

It is possible to install `cygserver` and the
PostgreSQL server as Windows NT services.  For information on how
to do this, please refer to the `README`
document included with the PostgreSQL binary package on Cygwin.
It is installed in the
directory `/usr/share/doc/Cygwin`.

### macOS

To build PostgreSQL from source
on macOS, you will need to install Apple's
command line developer tools, which can be done by issuing

```
xcode-select --install
```

(note that this will pop up a GUI dialog window for confirmation).
You may or may not wish to also install Xcode.

On recent macOS releases, it's necessary to
embed the "sysroot" path in the include switches used to
find some system header files.  This results in the outputs of
the configure script varying depending on
which SDK version was used during configure.
That shouldn't pose any problem in simple scenarios, but if you are
trying to do something like building an extension on a different machine
than the server code was built on, you may need to force use of a
different sysroot path.  To do that, set `PG_SYSROOT`,
for example

```
make PG_SYSROOT=`/desired/path` all
```

To find out the appropriate path on your machine, run

```
xcrun --show-sdk-path
```

Note that building an extension using a different sysroot version than
was used to build the core server is not really recommended; in the
worst case it could result in hard-to-debug ABI inconsistencies.

You can also select a non-default sysroot path when configuring, by
specifying `PG_SYSROOT`
to configure:

```
./configure ... PG_SYSROOT=`/desired/path`
```

This would primarily be useful to cross-compile for some other
macOS version.  There is no guarantee that the resulting executables
will run on the current host.

To suppress the `-isysroot` options altogether, use

```
./configure ... PG_SYSROOT=none
```

(any nonexistent pathname will work).  This might be useful if you wish
to build with a non-Apple compiler, but beware that that case is not
tested or supported by the PostgreSQL developers.

macOS's "System Integrity
Protection" (SIP) feature breaks `make check`,
because it prevents passing the needed setting
of `DYLD_LIBRARY_PATH` down to the executables being
tested.  You can work around that by doing `make
install` before `make check`.
Most PostgreSQL developers just turn off SIP, though.

### MinGW/Native Windows

PostgreSQL for Windows can be built using MinGW, a Unix-like build
environment for Microsoft operating systems, or using
Microsoft's Visual C++ compiler suite.
The MinGW build procedure uses the normal build system described in
this chapter; the Visual C++ build works completely differently
and is described in [install-windows](#install-windows).

The native Windows port requires a 32 or 64-bit version of Windows
2000 or later. Earlier operating systems do
not have sufficient infrastructure (but Cygwin may be used on
those).  MinGW, the Unix-like build tools, and MSYS, a collection
of Unix tools required to run shell scripts
like `configure`, can be downloaded
from [](http://www.mingw.org/).  Neither is
required to run the resulting binaries; they are needed only for
creating the binaries.

To build 64 bit binaries using MinGW, install the 64 bit tool set
from [](https://mingw-w64.org/), put its bin
directory in the `PATH`, and run
`configure` with the
`--host=x86_64-w64-mingw32` option.

After you have everything installed, it is suggested that you
run psql
under `CMD.EXE`, as the MSYS console has
buffering issues.

#### Collecting Crash Dumps on Windows

If PostgreSQL on Windows crashes, it has the ability to generate
minidumps that can be used to track down the cause
for the crash, similar to core dumps on Unix. These dumps can be
read using the Windows Debugger Tools or using
Visual Studio. To enable the generation of dumps
on Windows, create a subdirectory named `crashdumps`
inside the cluster data directory. The dumps will then be written
into this directory with a unique name based on the identifier of
the crashing process and the current time of the crash.

### Solaris

PostgreSQL is well-supported on Solaris.  The more up to date your
operating system, the fewer issues you will experience.

#### Required Tools

You can build with either GCC or Sun's compiler suite.  For
better code optimization, Sun's compiler is strongly recommended
on the SPARC architecture.  If
you are using Sun's compiler, be careful not to select
`/usr/ucb/cc`;
use `/opt/SUNWspro/bin/cc`.

You can download Sun Studio
from [](https://www.oracle.com/technetwork/server-storage/solarisstudio/downloads/).
Many GNU tools are integrated into Solaris 10, or they are
present on the Solaris companion CD.  If you need packages for
older versions of Solaris, you can find these tools
at [](http://www.sunfreeware.com).
If you prefer
sources, look
at [](https://www.gnu.org/prep/ftp).

#### configure Complains About a Failed Test Program

If `configure` complains about a failed test
program, this is probably a case of the run-time linker being
unable to find some library, probably libz, libreadline or some
other non-standard library such as libssl.  To point it to the
right location, set the `LDFLAGS` environment
variable on the `configure` command line, e.g.,

```
configure ... LDFLAGS="-R /usr/sfw/lib:/opt/sfw/lib:/usr/local/lib"
```

See
the ld1
man page for more information.

#### Compiling for Optimal Performance

On the SPARC architecture, Sun Studio is strongly recommended for
compilation.  Try using the `-xO5` optimization
flag to generate significantly faster binaries.  Do not use any
flags that modify behavior of floating-point operations
and `errno` processing (e.g.,
`-fast`).

If you do not have a reason to use 64-bit binaries on SPARC,
prefer the 32-bit version.  The 64-bit operations are slower and
64-bit binaries are slower than the 32-bit variants.  On the
other hand, 32-bit code on the AMD64 CPU family is not native,
so 32-bit code is significantly slower on that CPU family.

#### Using DTrace for Tracing PostgreSQL

Yes, using DTrace is possible.  See [dynamic-trace](#dynamic-trace) for
further information.

If you see the linking of the `postgres` executable abort with an
error message like:

```
Undefined                       first referenced
symbol                             in file
AbortTransaction                    utils/probes.o
CommitTransaction                   utils/probes.o
ld: fatal: Symbol referencing errors. No output written to postgres
collect2: ld returned 1 exit status
make: *** [postgres] Error 1
```

your DTrace installation is too old to handle probes in static
functions.  You need Solaris 10u4 or newer to use DTrace.
