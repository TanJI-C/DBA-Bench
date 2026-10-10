# Configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Building and Installation with Meson > Configuration`
- Source Line Ranges: `248-293, 1188-1212, 1213-1233`
- Chunk ID: `pg16_configuration_0009_eb279395e5`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1095118a1fdf7e86abb3421083a105ad63ecb7d299be587f386ab38cd6e22583`

## Retrieval Guidance

- Use When: 需要创建或修改 Meson 构建目录配置。
- Retrieval Keywords: meson setup build, meson configure, --prefix, --buildtype=debug, -Dssl=openssl
- Follow-up Guidance: 构建目录创建后用 meson configure 调整选项。
- Classification Note: 说明 meson setup/meson configure、builddir、prefix、debug、ssl 等配置语义。

## Official Source Content

## Configuration

The first step of the installation procedure is to configure the
source tree for your system and choose the options you would like.
This is done by running the `configure` script. For a
default installation simply enter:

```
./configure
```

This script will run a number of tests to determine values for various
system dependent variables and detect any quirks of your
operating system, and finally will create several files in the
build tree to record what it found.

You can also run `configure` in a directory outside
the source tree, and then build there, if you want to keep the build
directory separate from the original source files.  This procedure is
called a
*VPATH*
build.  Here's how:

```
mkdir build_dir
cd build_dir
/path/to/source/tree/configure [options go here]
make
```

The default configuration will build the server and utilities, as
well as all client applications and interfaces that require only a
C compiler. All files will be installed under
`/usr/local/pgsql` by default.

You can customize the build and installation process by supplying one
or more command line options to `configure`.
Typically you would customize the install location, or the set of
optional features that are built.  `configure`
has a large number of options, which are described in
[configure-options](#configure-options).

Also, `configure` responds to certain environment
variables, as described in [configure-envvars](#configure-envvars).
These provide additional ways to customize the configuration.

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

## Configuration

The first step of the installation procedure is to configure the
build tree for your system and choose the options you would like. To
create and configure the build directory, you can start with the
`meson setup` command.

```
meson setup build
```

The setup command takes a `builddir` and a `srcdir`
argument. If no `srcdir` is given, Meson will deduce the
`srcdir` based on the current directory and the location
of `meson.build`. The `builddir` is mandatory.

Running `meson setup` loads the build configuration file and sets up the build directory.
Additionally, you can also pass several build options to Meson. Some commonly
used options are mentioned in the subsequent sections. For example:

```
