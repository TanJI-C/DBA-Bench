# tiup mirror set syntax, root certificate option, and output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-mirror-set.md`
- Source Title: `tiup mirror set`
- Source Heading Path: `tiup mirror set | tiup mirror set > Syntax | tiup mirror set > Option | tiup mirror set > Option > -r, --root | tiup mirror set > Output`
- Source Line Ranges: `5-50`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `mirror`, `syntax`, `network-address`, `local-file-path`, `root-certificate`, `security`, `man-in-the-middle`, `command-options`, `output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0993_1e6b831ea0`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-mirror-set.md#tiup-mirror-set`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `637b1ae4bc67d6245faad36887384d3ee754315a73bd89296950805192f73b56`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-set#tiup-mirror-set
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-mirror-set.md

## Retrieval Guidance

- Use When: Use this chunk when looking up how to switch the current TiUP mirror to a network address or local file system path and how the root certificate option works.
- Retrieval Keywords: tiup mirror set, tiup mirror set <mirror-addr> [flags], mirror-addr, network address, local file path, https://tiup-mirrors.pingcap.com, -r, --root, root certificate, root.json, man-in-the-middle attacks, wget <mirror-addr>/root.json -O /path/to/local/root.json, tiup mirror set <mirror-addr> -r /path/to/local/root.json, {mirror-dir}/root.json, Output None
- Follow-up Guidance: The source also states that the official mirror address is https://tiup-mirrors.pingcap.com and that the default root certificate path is {mirror-dir}/root.json.
- Classification Note: This is reference content because it defines the tiup mirror set command syntax, accepted mirror address forms, the -r/--root option, and the command output.

## Official Source Content

# tiup mirror set

The `tiup mirror set` command is used to switch the current mirror and supports two forms of mirrors: local file system and remote network address.

The address of the official mirror is `https://tiup-mirrors.pingcap.com`.
## Syntax

```shell
tiup mirror set <mirror-addr> [flags]
```

`<mirror-addr>` is the mirror address, which has two forms:

- Network address: starts with `http` or `https`. For example, `http://172.16.5.5:8080`, `https://tiup-mirrors.pingcap.com`.
- Local file path: the absolute path of the mirror directory. For example, `/path/to/local-tiup-mirror`.
## Option
### -r, --root

This option specifies the root certificate.

As the most critical part of mirror security, the root certificate of each mirror is different from one another. When you use the network mirror, it might suffer from man-in-the-middle attacks. To avoid such attacks, it is recommended to manually download the root certificate of the root network mirror to the local:

```
wget <mirror-addr>/root.json -O /path/to/local/root.json
```

Perform a manual check to ensure that the root certificate is correct, and then switch the mirror by manually specifying the root certificate:

```
tiup mirror set <mirror-addr> -r /path/to/local/root.json
```

In the steps above, if the mirror is attacked before the `wget` command, you can find that the root certificate is incorrect. If the mirror is attacked after the `wget` command, TiUP will find that the mirror does not match the root certificate.

- Data type: `String`
- Default: `{mirror-dir}/root.json`
## Output

None

[<< Back to the previous page - TiUP Mirror command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror#command-list)
