# Regression Tests

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Building and Installation with Meson > Regression Tests`
- Source Line Ranges: `335-351, 1188-1212, 1285-1305`
- Chunk ID: `pg16_guide_0002_7c5ca1233c`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c926371a139beaf8e25e76f4d8c232b949d2269d2fb598a97dca75210cab8568`

## Retrieval Guidance

- Use When: 需要验证 Meson 构建产物是否正常。
- Retrieval Keywords: meson test, pg_regress, pg_isolation_regress, --setup running
- Follow-up Guidance: 失败时结合 tests/regression 文档判断差异。
- Classification Note: meson test 用于确认构建是否能通过回归验证。

## Official Source Content

## Regression Tests

If you want to test the newly built server before you install it,
you can run the regression tests at this point. The regression
tests are a test suite to verify that PostgreSQL
runs on your machine in the way the developers expected it
to. Type:

```
make check
```

(This won't work as root; do it as an unprivileged user.)
See [regress](#regress) for
detailed information about interpreting the test results. You can
repeat this test at any later time by issuing the same command.

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

## Regression Tests

If you want to test the newly built server before you install it,
you can run the regression tests at this point. The regression
tests are a test suite to verify that PostgreSQL
runs on your machine in the way the developers expected it
to. Type:

```
meson test
```

(This won't work as root; do it as an unprivileged user.)
See [regress](#regress) for
detailed information about interpreting the test results. You can
repeat this test at any later time by issuing the same command.

To run pg_regress and pg_isolation_regress tests against a running
postgres instance, specify --setup running as an
argument to meson test.
