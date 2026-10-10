# Installing the Files

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Building and Installation with Autoconf and Make > Installing the Files`
- Source Line Ranges: `224-247, 352-409, 1306-1337`
- Chunk ID: `pg16_solution_0005_9112dc7351`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `54a2d7ffa23183d4b803eefc066136a61cedc846d20c18c415690a168149f674`

## Retrieval Guidance

- Use When: 源码构建完成后需要安装文件到目标目录。
- Retrieval Keywords: make install, make install-docs, make install-world, install-strip, headers
- Follow-up Guidance: 升级现有系统前先查 Upgrading a PostgreSQL Cluster。
- Classification Note: 说明 make install、install-docs、install-world 和权限要求，是安装动作。

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

## Installing the Files

> **Note:**

> If you are upgrading an existing system be sure to read
> [upgrading](#upgrading),
> which has instructions about upgrading a
> cluster.
>

To install PostgreSQL enter:

```
make install
```

This will install files into the directories that were specified
in [configure](#configure). Make sure that you have appropriate
permissions to write into that area. Normally you need to do this
step as root. Alternatively, you can create the target
directories in advance and arrange for appropriate permissions to
be granted.

To install the documentation (HTML and man pages), enter:

```
make install-docs
```

If you built the world above, type instead:

```
make install-world
```

This also installs the documentation.

If you built the world without the documentation above, type instead:

```
make install-world-bin
```

You can use `make install-strip` instead of
`make install` to strip the executable files and
libraries as they are installed.  This will save some space.  If
you built with debugging support, stripping will effectively
remove the debugging support, so it should only be done if
debugging is no longer needed.  `install-strip`
tries to do a reasonable job saving space, but it does not have
perfect knowledge of how to strip every unneeded byte from an
executable file, so if you want to save all the disk space you
possibly can, you will have to do manual work.

The standard installation provides all the header files needed for client
application development as well as for server-side program
development, such as custom functions or data types written in C.

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
