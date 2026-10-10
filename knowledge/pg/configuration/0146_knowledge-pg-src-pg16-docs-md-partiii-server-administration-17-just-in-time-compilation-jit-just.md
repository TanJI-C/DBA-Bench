# Configuration

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/17_just-in-time_compilation_(jit).md`
- Source Title: `Just-in-Time Compilation (JIT)`
- Source Heading Path: `Just-in-Time Compilation (JIT) > Configuration`
- Source Line Ranges: `137-153`
- Chunk ID: `pg16_configuration_0146_2b37d603c4`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6be0ec9d211774277c389148cd4cb232f2d4fd4dcdbfe6bbea874c7f678609ff`

## Retrieval Guidance

- Use When: 需要配置 JIT 开关、阈值、优化级别或 provider。
- Retrieval Keywords: jit, jit_above_cost, jit_inline_above_cost, jit_optimize_above_cost, jit_provider
- Follow-up Guidance: 对分析型查询做基准测试后再调整阈值。
- Classification Note: 集中解释 jit、jit_above_cost、jit_inline_above_cost、jit_optimize_above_cost、jit_provider。

## Official Source Content

## Configuration

The configuration variable
[guc-jit](#guc-jit) determines whether JIT
compilation is enabled or disabled.
If it is enabled, the configuration variables
[guc-jit-above-cost](#guc-jit-above-cost), [guc-jit-inline-above-cost](#guc-jit-inline-above-cost), and [guc-jit-optimize-above-cost](#guc-jit-optimize-above-cost) determine
whether JIT compilation is performed for a query,
and how much effort is spent doing so.

[guc-jit-provider](#guc-jit-provider) determines which JIT
implementation is used. It is rarely required to be changed. See [jit-pluggable](#jit-pluggable).

For development and debugging purposes a few additional configuration
parameters exist, as described in
[runtime-config-developer](#runtime-config-developer).
