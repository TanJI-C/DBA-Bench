# Coverage with Autoconf and Make

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/18_regression_tests.md`
- Source Title: `Regression Tests`
- Source Heading Path: `Regression Tests > Test Coverage Examination > Coverage with Autoconf and Make`
- Source Line Ranges: `642-708`
- Chunk ID: `pg16_solution_0082_9f1e930843`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3c825ebc90036a9fbaca7c3f7a2c5a32ffdb9cf5aea9f2130bdf895dcab9b68c`

## Retrieval Guidance

- Use When: 使用 Autoconf/Make 构建时生成 PostgreSQL 覆盖率报告。
- Retrieval Keywords: --enable-coverage, make coverage-html, make coverage, make coverage-clean, coverage/index.html
- Follow-up Guidance: 多轮测试覆盖率会累积；需要隔离时先 coverage-clean。
- Classification Note: 给出 --enable-coverage、make coverage-html/coverage 和 coverage-clean 流程。

## Official Source Content

## Test Coverage Examination

The PostgreSQL source code can be compiled with coverage testing
instrumentation, so that it becomes possible to examine which
parts of the code are covered by the regression tests or any other
test suite that is run with the code.  This is currently supported
when compiling with GCC, and it requires the `gcov`
and `lcov` packages.

### Coverage with Autoconf and Make

A typical workflow looks like this:

```
./configure --enable-coverage ... OTHER OPTIONS ...
make
make check # or other test suite
make coverage-html
```

Then point your HTML browser
to `coverage/index.html`.

If you don't have `lcov` or prefer text output over an
HTML report, you can run

```
make coverage
```

instead of `make coverage-html`, which will
produce `.gcov` output files for each source file
relevant to the test.  (`make coverage` and `make
coverage-html` will overwrite each other's files, so mixing them
might be confusing.)

You can run several different tests before making the coverage report;
the execution counts will accumulate.  If you want
to reset the execution counts between test runs, run:

```
make coverage-clean
```

You can run the `make coverage-html` or `make
coverage` command in a subdirectory if you want a coverage
report for only a portion of the code tree.

Use `make distclean` to clean up when done.

### Coverage with Meson

A typical workflow looks like this:

```
meson setup -Db_coverage=true ... OTHER OPTIONS ... builddir/
meson compile -C builddir/
meson test -C builddir/
cd builddir/
ninja coverage-html
```

Then point your HTML browser
to `./meson-logs/coveragereport/index.html`.

You can run several different tests before making the coverage report;
the execution counts will accumulate.
