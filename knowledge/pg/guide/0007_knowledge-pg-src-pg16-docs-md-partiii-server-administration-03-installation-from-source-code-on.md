# Running the Regression Tests

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/03_installation_from_source_code_on_windows.md`
- Source Title: `Installation from Source Code on Windows`
- Source Heading Path: `Installation from Source Code on Windows > Running the Regression Tests`
- Source Line Ranges: `321-431`
- Chunk ID: `pg16_guide_0007_fa85ad63cc`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0a273d678c8e97bfcf41b88cd1c11c0c227565f35c092de83fd58236dd080be6`

## Retrieval Guidance

- Use When: Windows 上需要确认 MSVC 构建是否通过测试。
- Retrieval Keywords: vcregress check, vcregress installcheck, vcregress taptest, IPC::Run, PERL5LIB
- Follow-up Guidance: 测试失败时检查所需 DLL 是否在 PATH，TAP 测试是否安装 IPC::Run。
- Classification Note: vcregress 系列命令用于验证构建结果，DLL/PERL5LIB 问题也是测试失败线索。

## Official Source Content

### Running the Regression Tests

To run the regression tests, make sure you have completed the build of all
required parts first. Also, make sure that the DLLs required to load all
parts of the system (such as the Perl and Python DLLs for the procedural
languages) are present in the system path. If they are not, set it through
the `buildenv.pl` file. To run the tests, run one of
the following commands from the `src\tools\msvc`
directory:

```
vcregress check
vcregress installcheck
vcregress plcheck
vcregress contribcheck
vcregress modulescheck
vcregress ecpgcheck
vcregress isolationcheck
vcregress bincheck
vcregress recoverycheck
vcregress taptest
```

To change the schedule used (default is parallel), append it to the
command line like:

```
vcregress check serial
```

`vcregress taptest` can be used to run the TAP tests
of a target directory, like:

```
vcregress taptest src\bin\initdb\
```

For more information about the regression tests, see
[regress](#regress).

Running the regression tests on client programs with
`vcregress bincheck`, on recovery tests with
`vcregress recoverycheck`, or TAP tests specified with
`vcregress taptest` requires an additional Perl module
to be installed:

**IPC::Run**
: As of this writing, `IPC::Run` is not included in the
ActiveState Perl installation, nor in the ActiveState Perl Package
Manager (PPM) library. To install, download the
`IPC-Run-.tar.gz` source archive from
CPAN,
at [](https://metacpan.org/dist/IPC-Run), and
uncompress. Edit the `buildenv.pl` file, and add a PERL5LIB
variable to point to the `lib` subdirectory from the
extracted archive. For example:

```
$ENV{PERL5LIB}=$ENV{PERL5LIB} . ';c:\IPC-Run-0.94\lib';
```

The TAP tests run with `vcregress` support the
environment variables `PROVE_TESTS`, that is expanded
automatically using the name patterns given, and
`PROVE_FLAGS`. These can be set on a Windows terminal,
before running `vcregress`:

```
set PROVE_FLAGS=--timer --jobs 2
set PROVE_TESTS=t/020*.pl t/010*.pl
```

It is also possible to set up those parameters in
`buildenv.pl`:

```
$ENV{PROVE_FLAGS}='--timer --jobs 2'
$ENV{PROVE_TESTS}='t/020*.pl t/010*.pl'
```

Additionally, the behavior of TAP tests can be controlled by a set of
environment variables, see [regress-tap-vars](#regress-tap-vars).

Some of the TAP tests depend on a set of external commands that would
optionally trigger tests related to them. Each one of those variables
can be set or unset in `buildenv.pl`:

**`GZIP_PROGRAM`**
: Path to a gzip command. The default is
`gzip`, which will search for a command by that
name in the configured `PATH`.

**`LZ4`**
: Path to a lz4 command. The default is
`lz4`, which will search for a command by that
name in the configured `PATH`.

**`OPENSSL`**
: Path to an openssl command. The default is
`openssl`, which will search for a command by that
name in the configured `PATH`.

**`TAR`**
: Path to a tar command. The default is
`tar`, which will search for a command by that
name in the configured `PATH`.

**`ZSTD`**
: Path to a zstd command. The default is
`zstd`, which will search for a command by that
name in the configured `PATH`.
