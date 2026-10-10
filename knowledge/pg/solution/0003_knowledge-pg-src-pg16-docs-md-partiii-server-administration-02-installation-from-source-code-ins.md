# Short Version

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Building and Installation with Autoconf and Make > Short Version`
- Source Line Ranges: `224-247, 1190-1210`
- Chunk ID: `pg16_solution_0003_dbae6b1759`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8f44810d0c0229de4140fe6ba74ffb46af306a529e653aae542510cf14580018`

## Retrieval Guidance

- Use When: 需要快速执行 Unix Autoconf/Make 源码安装流程。
- Retrieval Keywords: ./configure, make, make install, initdb, pg_ctl start, createdb, psql
- Follow-up Guidance: 生产环境需结合后续配置、权限和升级说明。
- Classification Note: 提供从 configure、make、install 到 initdb/start/psql 的端到端命令序列。

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
