# Cleaning and Installing

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/03_installation_from_source_code_on_windows.md`
- Source Title: `Installation from Source Code on Windows`
- Source Heading Path: `Installation from Source Code on Windows > Cleaning and Installing`
- Source Line Ranges: `293-320`
- Chunk ID: `pg16_solution_0017_265dc98cec`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `787756af236614b3bf104660b049f7d94b51029b620612ae062928662fb8989c`

## Retrieval Guidance

- Use When: Windows 构建后需要清理或安装产物。
- Retrieval Keywords: clean.bat, clean dist, install c:\destination, install client
- Follow-up Guidance: 大改动后先 clean 再构建。
- Classification Note: 说明 clean.bat、dist 清理和 install 目标目录/客户端安装动作。

## Official Source Content

### Cleaning and Installing

Most of the time, the automatic dependency tracking in Visual Studio will
handle changed files. But if there have been large changes, you may need
to clean the installation. To do this, simply run the
`clean.bat` command, which will automatically clean out
all generated files. You can also run it with the

dist parameter, in which case it will behave like
make distclean and remove the flex/bison output files
as well.

By default, all files are written into a subdirectory of the
`debug` or `release` directories. To
install these files using the standard layout, and also generate the files
required to initialize and use the database, run the command:

```
install c:\destination\directory
```

If you want to install only the client applications and
interface libraries, then you can use these commands:

```
install c:\destination\directory client
```
