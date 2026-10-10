# TiUP command completion

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-command-completion.md`
- Source Title: `tiup completion`
- Source Heading Path: `tiup completion | tiup completion > Syntax | tiup completion > Usage | tiup completion > Usage > bash | tiup completion > Usage > zsh`
- Source Line Ranges: `5-46`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: none
- Topic Tags: `command completion`, `bash`, `zsh`, `shell configuration`, `bash-completion`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0495_c3b70ed41b`
- Source ID: `tidb-docs-8.1:tiup/tiup-command-completion.md#tiup-completion`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8f351252108831abd7904a4759dda8869371f2a3a14bc2366b8c4571e7b9f6ef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-command-completion#tiup-completion
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-command-completion.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how to generate TiUP shell auto-completion for bash or zsh and how to configure the generated completion file.
- Retrieval Keywords: tiup completion, tiup completion <shell>, bash, zsh, bash-completion, tiup completion bash, tiup completion zsh, .bash_profile, source '$HOME/.tiup.completion.bash', ${fpath[1]}/_tiup
- Follow-up Guidance: The content includes example commands for writing `tiup completion bash` output to `~/.tiup.completion.bash`, sourcing it from `.bash_profile`, and writing `tiup completion zsh` output to `${fpath[1]}/_tiup`.
- Classification Note: This is classified as a self-managed TiUP operation topic because the content explains the `tiup completion` command syntax and shell configuration steps for command-line completion.

## Official Source Content

# tiup completion

To reduce user costs, TiUP provides the `tiup completion` command to generate a configuration file for automatic command-line completion. Currently, TiUP supports completing `bash` and `zsh` commands.

If you want to complete `bash` commands, you need to install `bash-completion` first. See the following instructions:

- On macOS: If your bash version is earlier than 4.1, run `brew install bash-completion`; otherwise, run `brew install bash-completion@2`.
- On Linux: Use a package manager to install `bash-completion`. For example, run `yum install bash-completion` or `apt install bash-completion`.
## Syntax

```shell
tiup completion <shell>
```

`<shell>` is used to set the type of shell you use. Currently, `bash` and `zsh` are supported.
## Usage
### bash

Write the `tiup completion bash` command into a file and source the file in `.bash_profile`. See the following example:

```shell
tiup completion bash > ~/.tiup.completion.bash

printf "
# tiup shell completion
source '$HOME/.tiup.completion.bash'
" >> $HOME/.bash_profile

source $HOME/.bash_profile
```
### zsh

```shell
tiup completion zsh > "${fpath[1]}/_tiup"
```

[<< Back to the previous page - TiUP Reference command list](https://docs.pingcap.com/tidb/stable/tiup/tiup-reference#command-list)
