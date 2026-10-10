# TiUP mirror rotate command usage, signing flow, and addr option

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-mirror-rotate.md`
- Source Title: `tiup mirror rotate`
- Source Heading Path: `tiup mirror rotate | tiup mirror rotate > Syntax | tiup mirror rotate > Options | tiup mirror rotate > Options > --addr | tiup mirror rotate > Outputs`
- Source Line Ranges: `5-63`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `shared`
- Topic Tags: `mirror`, `root.json`, `signatures`, `trust-chain`, `certificate-expiration`, `key-rotation`, `syntax`, `temporary-http-server`, `admin-signing`, `addr`, `outputs`, `version-dependency`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0992_4f2f5dca67`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-mirror-rotate.md#tiup-mirror-rotate`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d6a225130cebf3683daa35492530a28e38f7f5abb7a4030f4c68721255534b03`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-rotate#tiup-mirror-rotate
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-mirror-rotate.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how `tiup mirror rotate` updates and re-signs `root.json`, including the signing flow, temporary HTTP server, `--addr` option, and output about signature status.
- Retrieval Keywords: tiup mirror rotate, root.json, snapshot.json, timestamp.json, chain of trust, mirror administrators, re-signed by all administrators, temporary HTTP server, --addr, 0.0.0.0:8080, sign command, expires field, version field from N to N+1, current signature status, TiUP versions earlier than v1.5.0, #983
- Follow-up Guidance: For how mirror administrators sign files, refer to the `sign` command.
- Classification Note: This is reference content because it describes the purpose, cases for updating `root.json`, command syntax, option `--addr`, outputs, and version note for `tiup mirror rotate`.

## Official Source Content

# tiup mirror rotate

`root.json` is an important file in a TiUP mirror. It stores the public keys needed for the entire system and is the basis of the chain of trust in TiUP. It mainly contains the following parts:

- Signatures of mirror administrators. For the official mirror, there are five signatures. For an initialized mirror, there are three signatures by default.
- The public keys used to verify the following files:
    - root.json
    - index.json
    - snapshot.json
    - timestamp.json
- Expiration date of `root.json`. For the official mirror, the expiration date is one year later than the creation date of `root.json`.

For detailed description of TiUP mirror, see [TiUP Mirror Reference](https://docs.pingcap.com/tidb/stable/tiup/tiup-mirror-reference).

You need to update `root.json` in the following cases:

- Replace the key of the mirror.
- Update the expiration date of certificate files.

After the content of `root.json` is updated, the file must be re-signed by all administrators; otherwise, the client rejects the file. The update process is as follows:

1. The user (client) updates the content of `root.json`.
2. All administrators sign the new `root.json` file.
3. tiup-server updates `snapshot.json` to record the version of the new `root.json` file.
4. tiup-server signs the new `snapshot.json` file.
5. tiup-server updates `timestamp.json` to record the hash value of the new `snapshot.json` file.
6. tiup-server signs the new `timestamp.json` file.

TiUP uses the command `tiup mirror rotate` to automate the above process.

> **Note:**
>
> + For TiUP versions earlier than v1.5.0, running this command does not return a correct new `root.json` file. See [#983](https://github.com/pingcap/tiup/issues/983).
> + Before using this command, make sure that all TiUP clients are upgraded to v1.5.0 or a later version.
## Syntax

```shell
tiup mirror rotate [flags]
```

After executing this command, TiUP starts an editor for the user to modify the file content to the target value, such as changing the value of the `expires` field to a later date. Then, TiUP changes the `version` field from `N` to `N+1` and saves the file. After the file is saved, TiUP starts a temporary HTTP server and waits for all mirror administrators to sign the file.

For how mirror administrators sign files, refer to the [`sign` command](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-sign).
## Options
### --addr

- Specifies the listening address of the temporary server. You need to make sure that the address is accessible to other mirror administrators so that they can use the [`sign` command](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror-sign) to sign the file.
- Data type: `STRING`
- If this option is not specified in the command, TiUP listens on `0.0.0.0:8080` by default.
## Outputs

The current signature status of each mirror administrator.

[<< Back to the previous page - TiUP Mirror command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-command-mirror#command-list)
