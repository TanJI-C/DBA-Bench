# Short Version

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Building and Installation with Meson > Short Version`
- Source Line Ranges: `226-245, 1188-1212`
- Chunk ID: `pg16_solution_0009_8684e1c919`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8f440d10f9413cc52732db082b759f27b69c93305ed69a3b955b382481f3af74`

## Retrieval Guidance

- Use When: 需要用 Meson/Ninja 从源码构建并启动 PostgreSQL。
- Retrieval Keywords: meson setup, ninja, ninja install, initdb, pg_ctl start
- Follow-up Guidance: 确认使用 Git checkout 时 Meson 支持状态和版本要求。
- Classification Note: 提供 meson setup、ninja、install、initdb、pg_ctl 的端到端构建安装流程。

## Official Source Content

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
