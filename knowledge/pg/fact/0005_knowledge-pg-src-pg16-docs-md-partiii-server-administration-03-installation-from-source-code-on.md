# Requirements

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/03_installation_from_source_code_on_windows.md`
- Source Title: `Installation from Source Code on Windows`
- Source Heading Path: `Installation from Source Code on Windows > Requirements`
- Source Line Ranges: `120-236`
- Chunk ID: `pg16_fact_0005_5d805f1e12`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ba69114ded8ad2d84a9cf342e608161f4ca7714e1925a8e4cd2e352776f3eaff`

## Retrieval Guidance

- Use When: 准备 Windows 源码构建依赖。
- Retrieval Keywords: Windows SDK, Strawberry Perl, Bison, Flex, Diff, Gettext, MIT Kerberos, OpenSSL, Python, zlib, LZ4, Zstandard
- Follow-up Guidance: 第三方库路径通过 config.pl 指定。
- Classification Note: 列出 Windows MSVC 构建所需和可选第三方组件。

## Official Source Content

### Requirements

The following additional products are required to build
PostgreSQL. Use the
`config.pl` file to specify which directories the libraries
are available in.

**Microsoft Windows SDK**
: If your build environment doesn't ship with a supported version of the
Microsoft Windows SDK it
is recommended that you upgrade to the latest version (currently
version 10), available for download from
[](https://www.microsoft.com/download).

You must always include the
Windows Headers and Libraries part of the SDK.
If you install a Windows SDK
including the Visual C++ Compilers,
you don't need Visual Studio to build.
Note that as of Version 8.0a the Windows SDK no longer ships with a
complete command-line build environment.

**Strawberry Perl**
: Strawberry Perl is required to run the build generation scripts. MinGW
or Cygwin Perl will not work. It must also be present in the PATH.
Binaries can be downloaded from
[](https://strawberryperl.com).

The following additional products are not required to get started,
but are required to build the complete package. Use the
`config.pl` file to specify which directories the libraries
are available in.

**Magicsplat Tcl**
: Required for building PL/Tcl.
Binaries can be downloaded from
[](https://www.magicsplat.com/tcl-installer/index.html).

**Bison and
Flex**
: Bison and Flex are
required to build from Git, but not required when building from a release
file. Only Bison versions 2.3 and later
will work. Flex must be version 2.5.35 or later.

Both Bison and Flex
are included in the msys tool suite, available
from [](http://www.mingw.org/wiki/MSYS) as part of the
MinGW compiler suite.

You will need to add the directory containing
`flex.exe` and `bison.exe` to the
PATH environment variable in `buildenv.pl` unless
they are already in PATH. In the case of MinGW, the directory is the
`\msys\1.0\bin` subdirectory of your MinGW
installation directory.

> **Note:**
> The Bison distribution from GnuWin32 appears to have a bug that
> causes Bison to malfunction when installed in a directory with
> spaces in the name, such as the default location on English
> installations `C:\Program Files\GnuWin32`.
> Consider installing into `C:\GnuWin32` or use the
> NTFS short name path to GnuWin32 in your PATH environment setting
> (e.g., `C:\PROGRA~1\GnuWin32`).
>

**Diff**
: Diff is required to run the regression tests, and can be downloaded
from [](http://gnuwin32.sourceforge.net).

**Gettext**
: Gettext is required to build with NLS support, and can be downloaded
from [](http://gnuwin32.sourceforge.net). Note that binaries,
dependencies and developer files are all needed.

**MIT Kerberos**
: Required for GSSAPI authentication support. MIT Kerberos can be
downloaded from
[](https://web.mit.edu/Kerberos/dist/index.html).

**libxml2 and
libxslt**
: Required for XML support. Binaries can be downloaded from
[](https://zlatkovic.com/pub/libxml) or source from
[](http://xmlsoft.org). Note that libxml2 requires iconv,
which is available from the same download location.

**LZ4**
: Required for supporting LZ4 compression.
Binaries and source can be downloaded from
[](https://github.com/lz4/lz4/releases).

**Zstandard**
: Required for supporting Zstandard compression.
Binaries and source can be downloaded from
[](https://github.com/facebook/zstd/releases).

**OpenSSL**
: Required for SSL support. Binaries can be downloaded from
[](https://slproweb.com/products/Win32OpenSSL.html)
or source from [](https://www.openssl.org).

**ossp-uuid**
: Required for UUID-OSSP support (contrib only). Source can be
downloaded from
[](http://www.ossp.org/pkg/lib/uuid/).

**Python**
: Required for building PL/Python. Binaries can
be downloaded from [](https://www.python.org).

**zlib**
: Required for compression support in pg_dump
and pg_restore. Binaries can be downloaded
from [](https://www.zlib.net).
