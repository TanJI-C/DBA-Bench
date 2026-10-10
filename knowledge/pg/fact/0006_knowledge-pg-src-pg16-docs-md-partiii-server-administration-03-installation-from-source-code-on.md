# Special Considerations for 64-Bit Windows

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/03_installation_from_source_code_on_windows.md`
- Source Title: `Installation from Source Code on Windows`
- Source Heading Path: `Installation from Source Code on Windows > Special Considerations for 64-Bit Windows`
- Source Line Ranges: `237-252`
- Chunk ID: `pg16_fact_0006_8e7de02016`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d9faa2e063124d77637b5b36b89e3ae4dc5c2fdd6f018090a22c1a4105aa8394`

## Retrieval Guidance

- Use When: Windows 64 位构建或加载第三方库失败时确认架构约束。
- Retrieval Keywords: 64-bit Windows, x64 architecture, 32-bit library, 64-bit OpenSSL, 64-bit Python
- Follow-up Guidance: 用正确架构的 Visual Studio 命令提示符和第三方库。
- Classification Note: 说明 x64 构建限制、32/64-bit 混用限制和第三方库位数要求。

## Official Source Content

### Special Considerations for 64-Bit Windows

PostgreSQL will only build for the x64 architecture on 64-bit Windows.

Mixing 32- and 64-bit versions in the same build tree is not supported.
The build system will automatically detect if it's running in a 32- or
64-bit environment, and build PostgreSQL accordingly. For this reason, it
is important to start the correct command prompt before building.

To use a server-side third party library such as Python or
OpenSSL, this library *must* also be
64-bit. There is no support for loading a 32-bit library in a 64-bit
server. Several of the third party libraries that PostgreSQL supports may
only be available in 32-bit versions, in which case they cannot be used with
64-bit PostgreSQL.
