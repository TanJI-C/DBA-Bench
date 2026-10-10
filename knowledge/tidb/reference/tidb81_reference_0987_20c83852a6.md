# tiup mirror grant syntax options and outputs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-mirror-grant.md`
- Source Title: `tiup mirror grant`
- Source Heading Path: `tiup mirror grant | tiup mirror grant > Syntax | tiup mirror grant > Options | tiup mirror grant > Options > -k, --key | tiup mirror grant > Options > -n, --name | tiup mirror grant > Options > Outputs`
- Source Line Ranges: `5-45`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `mirror`, `component-owner`, `public-key`, `local-mirror`, `command-syntax`, `options`, `outputs`, `error-messages`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0987_20c83852a6`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-mirror-grant.md#tiup-mirror-grant`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8f8cb680e172cbe7882c74bf7f5396cd7c90f2b5314536573da381358b2eb1ed`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-grant#tiup-mirror-grant
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-mirror-grant.md

## Retrieval Guidance

- Use When: Use this chunk when looking up the syntax, options, local-mirror limitation, or output and error messages for the `tiup mirror grant` command that introduces a component owner to a mirror.
- Retrieval Keywords: tiup mirror grant, tiup mirror grant <id> [flags], introduce a component owner, local mirror, current mirror is a local mirror, -k, --key, -n, --name, public key, private key, Owner field, Error: owner %s exists, Error: key %s exists, component owner's ID
- Follow-up Guidance: It also states that component owners can use their keys to publish new components or modify components they previously published, and that the owner to be added needs to send a public key to the mirror administrator before being added.
- Classification Note: This is reference content because it defines the command purpose, exact syntax, option semantics, defaults, and command outputs for `tiup mirror grant`.

## Official Source Content

# tiup mirror grant

The `tiup mirror grant` command is used to introduce a component owner to the current mirror.

Component owners can use their keys to publish new components or to modify components they previously published. Before adding a new component owner, the component owner to be added needs to send his or her own public key to the mirror administrator.

> **Note:**
>
> This command is only supported when the current mirror is a local mirror.
## Syntax

```shell
tiup mirror grant <id> [flags]
```

`<id>` stands for the component owner's ID, which must be unique in the whole mirror. It is recommended to use an ID that matches the regular expression `^[a-z\d](?:[a-z\d]|-(?=[a-z\d])){0,38}$`.
## Options
### -k, --key

- Specifies the key of the introduced component owner. This key can either be public or private. If it is a private key, TiUP converts it to the corresponding public key before storing it in the mirror.
- A key can be used by only one component owner.
- Data type: `STRING`
- Default: "${TIUP_HOME}/keys/private.json"
### -n, --name

- Specifies the name of the component owner. The name is displayed on the `Owner` field of the component list. If `-n/--name` is not specified, `<id>` is used as the component owner's name.
- Data type: `STRING`
- Default: `<id>`
### Outputs

- If the command is executed successfully, there is no output.
- If the component owner's ID is duplicated, TiUP reports the error `Error: owner %s exists`.
- If the key is used by another component owner, TiUP reports the error `Error: key %s exists`.

[<< Back to the previous page - TiUP Mirror command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror#command-list)
