# configure Environment Variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > configure Environment Variables`
- Source Line Ranges: `1034-1187`
- Chunk ID: `pg16_configuration_0008_c6429ebf7c`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4a20230bb06189d5fb66248c43c2a025bc1f5e954786e01d63b75e334cffc411`

## Retrieval Guidance

- Use When: 需要覆盖编译器、链接器、工具路径或临时编译 flags。
- Retrieval Keywords: CC, CFLAGS, CPPFLAGS, LDFLAGS, LLVM_CONFIG, PERL, PYTHON, TCLSH, XML2_CONFIG, COPT, PROFILE
- Follow-up Guidance: 避免在 configure 阶段直接使用会破坏探测的 flags，例如 -Werror。
- Classification Note: 定义 CC、CFLAGS、LLVM_CONFIG、PERL、PYTHON、COPT 等构建环境变量语义。

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
