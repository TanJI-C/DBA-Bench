# Optimization

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/17_just-in-time_compilation_(jit).md`
- Source Title: `Just-in-Time Compilation (JIT)`
- Source Heading Path: `Just-in-Time Compilation (JIT) > What Is JIT compilation? > Optimization`
- Source Line Ranges: `6-58`
- Chunk ID: `pg16_fact_0072_02f0650ad5`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e1744d5ee936ecbe61bf68105083c60f6a2f4b8cb5ca46f1d83331f1c5be12e9`

## Retrieval Guidance

- Use When: 需要解释为什么 JIT 优化不是所有查询都值得做。
- Retrieval Keywords: JIT optimization, LLVM optimization, generated code, long-running queries
- Follow-up Guidance: none
- Classification Note: 解释 LLVM 优化与长查询收益/编译开销取舍。

## Official Source Content

## What Is JIT compilation?

Just-in-Time (JIT) compilation is the process of turning
some form of interpreted program evaluation into a native program, and
doing so at run time.
For example, instead of using general-purpose code that can evaluate
arbitrary SQL expressions to evaluate a particular SQL predicate
like `WHERE a.col = 3`, it is possible to generate a
function that is specific to that expression and can be natively executed
by the CPU, yielding a speedup.

PostgreSQL has builtin support to perform
JIT compilation using [LLVM](https://llvm.org/) when
PostgreSQL is built with
[`--with-llvm`](#configure-with-llvm).

See `src/backend/jit/README` for further details.

### JIT Accelerated Operations

Currently PostgreSQL's JIT
implementation has support for accelerating expression evaluation and
tuple deforming.  Several other operations could be accelerated in the
future.

Expression evaluation is used to evaluate `WHERE`
clauses, target lists, aggregates and projections. It can be accelerated
by generating code specific to each case.

Tuple deforming is the process of transforming an on-disk tuple (see [storage-tuple-layout](#storage-tuple-layout)) into its in-memory representation.
It can be accelerated by creating a function specific to the table layout
and the number of columns to be extracted.

### Inlining

PostgreSQL is very extensible and allows new
data types, functions, operators and other database objects to be defined;
see [extend](#extend). In fact the built-in objects are implemented
using nearly the same mechanisms.  This extensibility implies some
overhead, for example due to function calls (see [xfunc](#xfunc)).
To reduce that overhead, JIT compilation can inline the
bodies of small functions into the expressions using them. That allows a
significant percentage of the overhead to be optimized away.

### Optimization

LLVM has support for optimizing generated
code. Some of the optimizations are cheap enough to be performed whenever
JIT is used, while others are only beneficial for
longer-running queries.
See [https://llvm.org/docs/Passes.html#transform-passes](https://llvm.org/docs/Passes.html#transform-passes) for
more details about optimizations.
