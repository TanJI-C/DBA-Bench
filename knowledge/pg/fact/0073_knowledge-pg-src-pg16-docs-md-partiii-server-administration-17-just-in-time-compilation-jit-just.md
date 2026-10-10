# JIT Provider Interface

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/17_just-in-time_compilation_(jit).md`
- Source Title: `Just-in-Time Compilation (JIT)`
- Source Heading Path: `Just-in-Time Compilation (JIT) > Extensibility > Pluggable JIT Providers > JIT Provider Interface`
- Source Line Ranges: `154-211`
- Chunk ID: `pg16_fact_0073_362a9d1764`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `64b8f0a172ae489406b15503938b8c2f0766d1f3f3b246288709a199983e693d`

## Retrieval Guidance

- Use When: 开发或审查自定义 JIT provider 接口。
- Retrieval Keywords: JIT Provider Interface, _PG_jit_provider_init, JitProviderCallbacks, compile_expr, release_context
- Follow-up Guidance: 实现 callback 并确保动态库可由 provider search path 加载。
- Classification Note: 列出 JIT provider 动态库初始化函数和 callback 接口。

## Official Source Content

## Extensibility

### Inlining Support for Extensions

PostgreSQL's JIT
implementation can inline the bodies of functions
of types `C` and `internal`, as well as
operators based on such functions.  To do so for functions in extensions,
the definitions of those functions need to be made available.
When using [PGXS](#extend-pgxs) to build an extension
against a server that has been compiled with LLVM JIT support, the
relevant files will be built and installed automatically.

The relevant files have to be installed into
`$pkglibdir/bitcode/$extension/` and a summary of them
into `$pkglibdir/bitcode/$extension.index.bc`, where
`$pkglibdir` is the directory returned by
`pg_config --pkglibdir` and `$extension`
is the base name of the extension's shared library.

> **Note:**

> For functions built into PostgreSQL itself,
> the bitcode is installed into
> `$pkglibdir/bitcode/postgres`.
>

### Pluggable JIT Providers

PostgreSQL provides a JIT
implementation based on LLVM.  The interface to
the JIT provider is pluggable and the provider can be
changed without recompiling (although currently, the build process only
provides inlining support data for LLVM).
The active provider is chosen via the setting
[guc-jit-provider](#guc-jit-provider).

#### JIT Provider Interface

A JIT provider is loaded by dynamically loading the
named shared library. The normal library search path is used to locate
the library. To provide the required JIT provider
callbacks and to indicate that the library is actually a
JIT provider, it needs to provide a C function named
`_PG_jit_provider_init`. This function is passed a
struct that needs to be filled with the callback function pointers for
individual actions:

```
struct JitProviderCallbacks
{
JitProviderResetAfterErrorCB reset_after_error;
JitProviderReleaseContextCB release_context;
JitProviderCompileExprCB compile_expr;
};

extern void _PG_jit_provider_init(JitProviderCallbacks *cb);
```
