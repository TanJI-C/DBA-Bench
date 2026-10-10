# Uninstallation

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Building and Installation with Autoconf and Make > Uninstallation`
- Source Line Ranges: `224-247, 425-429, 1338-1342`
- Chunk ID: `pg16_solution_0007_35835e63c8`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `f58d2cb5bc9629446941abcc8b344ce9b3a0cef00cf9ce15483e70484bc8357e`

## Retrieval Guidance

- Use When: 需要撤销源码安装的 PostgreSQL 文件。
- Retrieval Keywords: make uninstall, remove installation, created directories
- Follow-up Guidance: 手工清理由安装创建但 uninstall 不删除的目录。
- Classification Note: 说明 make uninstall 的卸载动作及目录保留行为。

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

## Uninstallation:

To undo the installation use the command `make
uninstall`. However, this will not remove any created directories.

## Uninstallation:

To undo the installation, you can use the `ninja
uninstall` command.
