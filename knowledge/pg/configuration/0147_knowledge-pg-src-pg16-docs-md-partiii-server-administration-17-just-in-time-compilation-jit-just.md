# Inlining Support for Extensions

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/17_just-in-time_compilation_(jit).md`
- Source Title: `Just-in-Time Compilation (JIT)`
- Source Heading Path: `Just-in-Time Compilation (JIT) > Extensibility > Inlining Support for Extensions`
- Source Line Ranges: `154-211`
- Chunk ID: `pg16_configuration_0147_67550e635a`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `64b8f0a172ae489406b15503938b8c2f0766d1f3f3b246288709a199983e693d`

## Retrieval Guidance

- Use When: 扩展函数无法被 JIT inline 或需要构建支持 LLVM 的扩展。
- Retrieval Keywords: JIT extension inlining, PGXS, bitcode, pkglibdir, extension.index.bc
- Follow-up Guidance: 确认服务器和扩展均以 LLVM JIT 支持方式构建。
- Classification Note: 说明扩展函数 inlining 所需 bitcode 安装路径和 PGXS 行为。

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
