# tiup mirror modify command syntax, options, and outputs

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-mirror-modify.md`
- Source Title: `tiup mirror modify`
- Source Heading Path: `tiup mirror modify | tiup mirror modify > Syntax | tiup mirror modify > Options | tiup mirror modify > Options > -k, --key | tiup mirror modify > Options > --yank | tiup mirror modify > Options > --hide | tiup mirror modify > Options > --standalone | tiup mirror modify > Outputs`
- Source Line Ranges: `5-65`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `command syntax`, `component publishing`, `signing`, `private key`, `yank`, `hide`, `standalone`, `authorization`, `error output`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0990_1219aeb2fa`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-mirror-modify.md#tiup-mirror-modify`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `896fa0a2536ca788ae313e7f8f1760633cafe05b473a2012c553e21d8447cd71`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-modify#tiup-mirror-modify
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-mirror-modify.md

## Retrieval Guidance

- Use When: Use this when looking up how to run `tiup mirror modify`, what flags like `-k`, `--yank`, `--hide`, and `--standalone` mean, or what authorization-related errors it returns.
- Retrieval Keywords: tiup mirror modify, tiup mirror modify <component>[:version] [flags], -k, --key, ${TIUP_HOME}/keys/private.json, --yank, --hide, --standalone, tiup list, tiup list <component>, tiup list --all, Error: The server refused, make sure you have access to this component, Error: the signature is not correct, component owner, private key, signing component information, {component}.json
- Follow-up Guidance: For the method to publish a component, the content refers to the `publish` command.
- Classification Note: This is reference content because it defines the `tiup mirror modify` command syntax, explains each option, and lists success and error outputs from the official command documentation.

## Official Source Content

# tiup mirror modify

The `tiup mirror modify` command is used to modify published components. Only valid component owners can modify the components that they have published on their own. For the method to publish a component, refer to the [`publish` command](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-publish).
## Syntax

```shell
tiup mirror modify <component>[:version] [flags]
```

Each parameter is explained as follows:

- `<component>`: the component name
- `[version]`: the component version to modify. If it is not specified, the entire component is modified.
## Options
### -k, --key

- Specifies the component owner's private key used for signing the component information (`{component}.json`).
- Data type: `STRING`
- If this option is not specified in the command, `"${TIUP_HOME}/keys/private.json"` is used by default to sign the component information.
### --yank

Marks a specified component or version as unavailable.

- After the component is marked as unavailable, you can neither see it in the result list of `tiup list` nor install the new version of the component.
- After a component version is marked as unavailable, you can neither see it in the result list of `tiup list <component>` nor install this version.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.
### --hide

- Specifies whether to hide the component. If a component is hidden, you cannot see it in the result list of `tiup list`. To see the hidden component, you can use `tiup list --all`.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.

> **Note:**
>
> This option can only be applied to the component, not to the component version.
### --standalone

- Controls whether the component can run standalone. This option is currently **NOT available**.
- Data type: `BOOLEAN`
- This option is disabled by default and its default value is `false`. To enable this option, you can add this option to the command, and pass the `true` value or do not pass any value.

> **Note:**
>
> This option can only be applied to the component, not to the component version.
## Outputs

- If the command is executed successfully, there is no output.
- If the component owner is not authorized to modify the target component:
    - If the mirror is a remote mirror, TiUP reports the error `Error: The server refused, make sure you have access to this component`.
    - If the mirror is a local mirror, TiUP reports the error `Error: the signature is not correct`.

[<< Back to the previous page - TiUP Mirror command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror#command-list)
