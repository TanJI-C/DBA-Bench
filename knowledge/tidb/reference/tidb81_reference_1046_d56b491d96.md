# Private mirror purpose and tiup mirror command overview

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-mirror.md`
- Source Title: `Create a Private Mirror`
- Source Heading Path: `Create a Private Mirror | Create a Private Mirror > TiUP `mirror` overview`
- Source Line Ranges: `5-49`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `private-mirror`, `offline-deployment`, `repository-management`, `command-reference`, `component-repository`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_1046_d56b491d96`
- Source ID: `tidb-docs-8.1:tiup/tiup-mirror.md#create-a-private-mirror`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9f1a41effa6cba605b2cc89acb8ecf29acbdd982806271cc87a30cbcba05c10e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-mirror#create-a-private-mirror
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-mirror.md

## Retrieval Guidance

- Use When: Use this chunk when you need the purpose of a TiUP private mirror in an isolated network environment or a command overview of `tiup mirror` for repository management.
- Retrieval Keywords: Create a Private Mirror, TiUP `mirror` overview, tiup mirror --help, private mirror, offline deployment, component repository, repository can be used either online or offline, init, sign, genkey, clone, merge, publish, show, set, modify, renew, grant, rotate root.json
- Follow-up Guidance: For command-specific details, use `tiup mirror [command] --help` as stated in the overview.
- Classification Note: This is reference content because it explains the purpose of a private mirror and lists the available `tiup mirror` subcommands and flags from the official help output.

## Official Source Content

# Create a Private Mirror

When creating a private cloud, usually, you need to use an isolated network environment, where the official mirror of TiUP is not accessible. Therefore, you can create a private mirror, which is mainly implemented by the `mirror` command. You can also use the `mirror` command for offline deployment. A private mirror also allows you to use components that you build and package by yourself.
## TiUP `mirror` overview

Execute the following command to get the help information of the `mirror` command:

```bash
tiup mirror --help
```

```bash
The `mirror` command is used to manage a component repository for TiUP, you can use
it to create a private repository, or to add new component to an existing repository.
The repository can be used either online or offline.
It also provides some useful utilities to help manage keys, users, and versions
of components or the repository itself.

Usage:
  tiup mirror <command> [flags]

Available Commands:
  init        Initialize an empty repository
  sign        Add signatures to a manifest file
  genkey      Generate a new key pair
  clone       Clone a local mirror from a remote mirror and download all selected components
  merge       Merge two or more offline mirrors
  publish     Publish a component
  show        Show the mirror address
  set         Set mirror address
  modify      Modify published component
  renew       Renew the manifest of a published component.
  grant       grant a new owner
  rotate      Rotate root.json

Global Flags:
      --help                 Help for this command

Use "tiup mirror [command] --help" for more information about a command.
```
