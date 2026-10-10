# Client-only installation

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Building and Installation with Autoconf and Make > Client-only installation`
- Source Line Ranges: `224-247, 410-424`
- Chunk ID: `pg16_solution_0006_c329eb5f6e`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `af48ede7eb0370939d616408305604faccad1448745476f03bcf2f72fb965e68`

## Retrieval Guidance

- Use When: 只需要 psql/libpq 等客户端组件，不安装完整服务器。
- Retrieval Keywords: client-only installation, src/bin install, src/interfaces install, libpq headers
- Follow-up Guidance: 确认 doc/src/include/src/interfaces 是否都需要安装。
- Classification Note: 给出只安装客户端程序和接口库的 make -C 命令。

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

## Client-only installation:

If you want to install only the client applications and
interface libraries, then you can use these commands:

```
make -C src/bin install
make -C src/include install
make -C src/interfaces install
make -C doc install
```

`src/bin` has a few binaries for server-only use,
but they are small.
