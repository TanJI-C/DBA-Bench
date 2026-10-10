# tiup mirror sign syntax, options, and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-mirror-sign.md`
- Source Title: `tiup mirror sign`
- Source Heading Path: `tiup mirror sign | tiup mirror sign > Syntax | tiup mirror sign > Options | tiup mirror sign > Options > -k, --key | tiup mirror sign > Options > --timeout | tiup mirror sign > Output`
- Source Line Ranges: `5-50`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `mirror`, `signing`, `manifest`, `http`, `private-key`, `timeout`, `command-options`, `command-output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0994_89afc13f27`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-mirror-sign.md#tiup-mirror-sign`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ceada355b15df5d429751c8a1e2b1d342f67ad29a5817c9e73f14baae7b8065e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-sign#tiup-mirror-sign
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-mirror-sign.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the syntax, options, supported manifest-file forms, or output behavior of the `tiup mirror sign` command for signing TiUP mirror metadata files.
- Retrieval Keywords: tiup mirror sign, tiup mirror sign <manifest-file> [flags], mirror sign, manifest-file, metadata files (*.json), HTTP or HTTPS, local file path, -k, --key, ${TIUP_HOME}/keys/private.json, --timeout, signatures field, http get, http post, Error: this manifest file has already been signed by specified key, Error: unmarshal manifest: %s
- Follow-up Guidance: The source also states that network signing requires the address to support `http get` returning the complete signed file content including the `signatures` field and `http post` to submit the updated content.
- Classification Note: This is reference content because it defines command syntax, option semantics, input forms, and exact success and error outputs for the TiUP command.

## Official Source Content

# tiup mirror sign

The `tiup mirror sign` command is used to sign the metadata files (*.json) defined in TiUP [mirror](https://docs.pingcap.com/tidb/stable/tiup/tiup-mirror-reference). These metadata files might be stored on the local file system or remotely stored using the HTTP protocol to provide a signature entry.
## Syntax

```shell
tiup mirror sign <manifest-file> [flags]
```

`<manifest-file>` is the address of the file to be signed, which has two forms:

- Network address, which starts with HTTP or HTTPS, such as `http://172.16.5.5:8080/rotate/root.json`
- Local file path, which is a relative path or an absolute path

If it is a network address, this address must provide the following features:

- Supports the access via `http get` that returns the complete content of the signed file (including the `signatures` field).
- Supports the access via `http post`. The client adds the signature to the `signatures` field of the content that is returned by `http get` and posts to this network address.
## Options
### -k, --key

- Specifies the location of the private key used for signing the `{component}.json` file.
- Data type: `STRING`
- - If this option is not specified in the command, `"${TIUP_HOME}/keys/private.json"` is used by default.
### --timeout

- Specifies the access timeout time for signing through the network. The unit is in seconds.
- Data type: `INT`
- Default: 10

> **Note:**
>
> This option is valid only when `<manifest-file>` is a network address.
## Output

- If the command is executed successfully, there is no output.
- If the file has been signed by the specified key, TiUP reports the error `Error: this manifest file has already been signed by specified key`.
- If the file is not a valid manifest, TiUP reports the error `Error: unmarshal manifest: %s`.

[<< Back to the previous page - TiUP Mirror command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror#command-list)
