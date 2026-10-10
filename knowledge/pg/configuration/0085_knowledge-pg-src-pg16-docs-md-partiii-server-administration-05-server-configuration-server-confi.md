# Customized Options

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Customized Options`
- Source Line Ranges: `6257-6277`
- Chunk ID: `pg16_configuration_0085_d865c08b06`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66b235a36021e2310d1a02177422b3e39ab02a81900da30b3a7bcc557902f7ea`

## Retrieval Guidance

- Use When: 扩展模块需要通过标准 GUC 机制暴露参数。
- Retrieval Keywords: customized options, extension GUC, plpgsql.variable_conflict, placeholder, two-part parameter
- Follow-up Guidance: 加载扩展后未识别 placeholder 会发出 warning 并移除。
- Classification Note: 说明扩展自定义 two-part GUC 名称和 placeholder 机制。

## Official Source Content

## Customized Options

This feature was designed to allow parameters not normally known to
PostgreSQL to be added by add-on modules
(such as procedural languages).  This allows extension modules to be
configured in the standard ways.

Custom options have two-part names: an extension name, then a dot, then
the parameter name proper, much like qualified names in SQL.  An example
is `plpgsql.variable_conflict`.

Because custom options may need to be set in processes that have not
loaded the relevant extension module, PostgreSQL
will accept a setting for any two-part parameter name.  Such variables
are treated as placeholders and have no function until the module that
defines them is loaded. When an extension module is loaded, it will add
its variable definitions and convert any placeholder values according to
those definitions.  If there are any unrecognized placeholders
that begin with its extension name, warnings are issued and those
placeholders are removed.
