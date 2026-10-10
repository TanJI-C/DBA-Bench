# Regression Tests

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/02_installation_from_source_code.md`
- Source Title: `Installation from Source Code`
- Source Heading Path: `Installation from Source Code > Building and Installation with Autoconf and Make > Regression Tests`
- Source Line Ranges: `224-247, 335-351, 1285-1305`
- Chunk ID: `pg16_guide_0001_fb6ff93d98`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `73f125dac8dd863cfc71cc67da3becee2a1a5ba0de43e3b66710494efe58727b`

## Retrieval Guidance

- Use When: 需要验证源码构建是否可用或解释测试结果。
- Retrieval Keywords: make check, regression tests, test results, unprivileged user
- Follow-up Guidance: 失败时查 Regression Tests 章节和平台特定测试说明。
- Classification Note: 用于确认新构建的服务器是否按预期运行，属于验证/确诊信号。

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
