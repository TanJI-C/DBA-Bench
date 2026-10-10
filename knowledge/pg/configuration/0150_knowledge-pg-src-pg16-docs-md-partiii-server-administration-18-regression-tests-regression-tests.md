# Custom Server Settings

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/18_regression_tests.md`
- Source Title: `Regression Tests`
- Source Heading Path: `Regression Tests > Running the Tests > Custom Server Settings`
- Source Line Ranges: `8-37, 77-104, 105-233, 234-270, 271-292, 293-304`
- Chunk ID: `pg16_configuration_0150_95d236037c`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `19212b852bdd67e35e31c2b273ebd1e7c0dff21c0e24f3722d3c45d0d95165f6`

## Retrieval Guidance

- Use When: 回归测试需要额外日志、资源限制或运行时检查参数。
- Retrieval Keywords: PGOPTIONS, EXTRA_REGRESS_OPTS, --temp-config, test_postgresql.conf, debug_parallel_query, work_mem
- Follow-up Guidance: 只设置允许通过 PGOPTIONS 或 temp-config 生效的参数。
- Classification Note: 说明 PGOPTIONS 和 EXTRA_REGRESS_OPTS --temp-config 注入服务器设置。

## Official Source Content

## Running the Tests

The regression tests can be run against an already installed and
running server, or using a temporary installation within the build
tree.  Furthermore, there is a "parallel" and a
"sequential" mode for running the tests.  The
sequential method runs each test script alone, while the
parallel method starts up multiple server processes to run groups
of tests in parallel.  Parallel testing adds confidence that
interprocess communication and locking are working correctly.
Some tests may run sequentially even in the "parallel"
mode in case this is required by the test.

### Running the Tests Against a Temporary Installation

To run the parallel regression tests after building but before installation,
type:

```
make check
```

in the top-level directory.  (Or you can change to
`src/test/regress` and run the command there.)
Tests which are run in parallel are prefixed with "+", and
tests which run sequentially are prefixed with "-".
At the end you should see something like:

```

### Running the Tests Against an Existing Installation

To run the tests after installation (see [installation](#installation)),
initialize a data directory and start the
server as explained in [runtime](#runtime), then type:

```
make installcheck
```

or for a parallel test:

```
make installcheck-parallel
```

The tests will expect to contact the server at the local host and the
default port number, unless directed otherwise by `PGHOST` and
`PGPORT` environment variables.  The tests will be run in a
database named `regression`; any existing database by this name
will be dropped.

The tests will also transiently create some cluster-wide objects, such as
roles, tablespaces, and subscriptions.  These objects will have names
beginning with `regress_`.  Beware of
using `installcheck` mode with an installation that has
any actual global objects named that way.

### Additional Test Suites

The `make check` and `make installcheck` commands
run only the "core" regression tests, which test built-in
functionality of the PostgreSQL server.  The source
distribution contains many additional test suites, most of them having
to do with add-on functionality such as optional procedural languages.

To run all test suites applicable to the modules that have been selected
to be built, including the core tests, type one of these commands at the
top of the build tree:

```
make check-world
make installcheck-world
```

These commands run the tests using temporary servers or an
already-installed server, respectively, just as previously explained
for `make check` and `make installcheck`.  Other
considerations are the same as previously explained for each method.
Note that `make check-world` builds a separate instance
(temporary data directory) for each tested module, so it requires more
time and disk space than `make installcheck-world`.

On a modern machine with multiple CPU cores and no tight operating-system
limits, you can make things go substantially faster with parallelism.
The recipe that most PostgreSQL developers actually use for running all
tests is something like

```
make check-world -j8 >/dev/null
```

with a `-j` limit near to or a bit more than the number
of available cores.  Discarding stdout
eliminates chatter that's not interesting when you just want to verify
success.  (In case of failure, the stderr
messages are usually enough to determine where to look closer.)

Alternatively, you can run individual test suites by typing
`make check` or `make installcheck` in the appropriate
subdirectory of the build tree.  Keep in mind that `make
installcheck` assumes you've installed the relevant module(s), not
only the core server.

The additional tests that can be invoked this way include:

- Regression tests for optional procedural languages.
These are located under `src/pl`.
- Regression tests for `contrib` modules,
located under `contrib`.
Not all `contrib` modules have tests.
- Regression tests for the interface libraries,
located in `src/interfaces/libpq/test` and
`src/interfaces/ecpg/test`.
- Tests for core-supported authentication methods,
located in `src/test/authentication`.
(See below for additional authentication-related tests.)
- Tests stressing behavior of concurrent sessions,
located in `src/test/isolation`.
- Tests for crash recovery and physical replication,
located in `src/test/recovery`.
- Tests for logical replication,
located in `src/test/subscription`.
- Tests of client programs, located under `src/bin`.

When using `installcheck` mode, these tests will create
and destroy test databases whose names
include `regression`, for
example `pl_regression`
or `contrib_regression`.  Beware of
using `installcheck` mode with an installation that has
any non-test databases named that way.

Some of these auxiliary test suites use the TAP infrastructure explained
in [regress-tap](#regress-tap).
The TAP-based tests are run only when PostgreSQL was configured with the
option `--enable-tap-tests`.  This is recommended for
development, but can be omitted if there is no suitable Perl installation.

Some test suites are not run by default, either because they are not secure
to run on a multiuser system, because they require special software or
because they are resource intensive.  You can decide which test suites to
run additionally by setting the `make` or environment
variable `PG_TEST_EXTRA` to a whitespace-separated list,
for example:

```
make check-world PG_TEST_EXTRA='kerberos ldap ssl load_balance'
```

The following values are currently supported:

**`kerberos`**
: Runs the test suite under `src/test/kerberos`.  This
requires an MIT Kerberos installation and opens TCP/IP listen sockets.

**`ldap`**
: Runs the test suite under `src/test/ldap`.  This
requires an OpenLDAP installation and opens
TCP/IP listen sockets.

**`ssl`**
: Runs the test suite under `src/test/ssl`.  This opens TCP/IP listen sockets.

**`load_balance`**
: Runs the test `src/interfaces/libpq/t/004_load_balance_dns.pl`.
This requires editing the system `hosts` file and
opens TCP/IP listen sockets.

**`wal_consistency_checking`**
: Uses `wal_consistency_checking=all` while running
certain tests under `src/test/recovery`.  Not
enabled by default because it is resource intensive.

Tests for features that are not supported by the current build
configuration are not run even if they are mentioned in
`PG_TEST_EXTRA`.

In addition, there are tests in `src/test/modules`
which will be run by `make check-world` but not
by `make installcheck-world`.  This is because they
install non-production extensions or have other side-effects that are
considered undesirable for a production installation.  You can
use `make install` and `make
installcheck` in one of those subdirectories if you wish,
but it's not recommended to do so with a non-test server.

### Locale and Encoding

By default, tests using a temporary installation use the
locale defined in the current environment and the corresponding
database encoding as determined by `initdb`.  It
can be useful to test different locales by setting the appropriate
environment variables, for example:

```
make check LANG=C
make check LC_COLLATE=en_US.utf8 LC_CTYPE=fr_CA.utf8
```

For implementation reasons, setting `LC_ALL` does not
work for this purpose; all the other locale-related environment
variables do work.

When testing against an existing installation, the locale is
determined by the existing database cluster and cannot be set
separately for the test run.

You can also choose the database encoding explicitly by setting
the variable `ENCODING`, for example:

```
make check LANG=C ENCODING=EUC_JP
```

Setting the database encoding this way typically only makes sense
if the locale is C; otherwise the encoding is chosen automatically
from the locale, and specifying an encoding that does not match
the locale will result in an error.

The database encoding can be set for tests against either a temporary or
an existing installation, though in the latter case it must be
compatible with the installation's locale.

### Custom Server Settings

Custom server settings to use when running a regression test suite can be
set in the `PGOPTIONS` environment variable (for settings
that allow this):

```
make check PGOPTIONS="-c debug_parallel_query=regress -c work_mem=50MB"
```

When running against a temporary installation, custom settings can also be
set by supplying a pre-written `postgresql.conf`:

```
echo 'log_checkpoints = on' > test_postgresql.conf
echo 'work_mem = 50MB' >> test_postgresql.conf
make check EXTRA_REGRESS_OPTS="--temp-config=test_postgresql.conf"
```

This can be useful to enable additional logging, adjust resource limits,
or enable extra run-time checks such as [guc-debug-discard-caches](#guc-debug-discard-caches).

### Extra Tests

The core regression test suite contains a few test files that are not
run by default, because they might be platform-dependent or take a
very long time to run.  You can run these or other extra test
files by setting the variable `EXTRA_TESTS`.  For
example, to run the `numeric_big` test:

```
make check EXTRA_TESTS=numeric_big
```
