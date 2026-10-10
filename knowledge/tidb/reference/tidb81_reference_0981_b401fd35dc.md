# tiup env command syntax, options, and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-env.md`
- Source Title: `tiup env`
- Source Heading Path: `tiup env | tiup env > Syntax | tiup env > Option | tiup env > Output`
- Source Line Ranges: `5-29`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `environment-variables`, `command-syntax`, `command-options`, `command-output`, `defaults`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0981_b401fd35dc`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-env.md#tiup-env`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ac037cf1e0548d8cde3ea96a19213ea69d1fd3c91ff589fe326772a059925710`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-env#tiup-env
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-env.md

## Retrieval Guidance

- Use When: Use this when you need the syntax or output behavior of the `tiup env` command for viewing TiUP-supported environment variables and their values.
- Retrieval Keywords: tiup env, tiup env [name1...N], environment variables, "{key}"="{value}", "{value}" list, default value
- Follow-up Guidance: If `[name1...N]` is not specified, all supported environment variables are viewed by default.
- Classification Note: This is a TiUP reference page for the `tiup env` command, including its syntax, no options, and its output format.

## Official Source Content

# tiup env

TiUP provides users with flexible and customized interfaces, some of which are implemented using environment variables. The `tiup env` command is used to query the user-defined environment variables that TiUP supports and their values.
## Syntax

```shell
tiup env [name1...N]
```

`[name1...N]` is used to view the specified environment variables. If it is not specified, all supported environment variables are viewed by default.
## Option

None
## Output

- If `[name1...N]` is not specified, a list of "{key}"="{value}" is output.
- If `[name1...N]` is specified, the "{value}" list is output in order.

In the above output, if `value` is empty, it means that the value of the environment variable is not set. In this case, TiUP uses the default value.

[<< Back to the previous page - TiUP Reference command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-reference#command-list)
