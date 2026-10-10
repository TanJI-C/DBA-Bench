# Create a custom repository and publish custom components

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tiup/tiup-mirror.md`
- Source Title: `Create a Private Mirror`
- Source Heading Path: `Create a Private Mirror > Custom repository | Create a Private Mirror > Custom repository > Create a custom repository | Create a Private Mirror > Custom repository > Work with custom components`
- Source Line Ranges: `128-206`
- Source Scope: `self_managed`
- Primary Component: `tiup`
- Related Components: `tidb`, `tikv`, `pd`
- Topic Tags: `custom-repository`, `component-packaging`, `key-generation`, `ownership-grant`, `component-publish`, `repository-merge`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0521_f3d40c5bc4`
- Source ID: `tidb-docs-8.1:tiup/tiup-mirror.md#custom-repository`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8a3bfc6bab998dde04f74216f848cd7dd9a7fc5aa315dbe113bb1655c1c5392d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tiup/tiup-mirror#custom-repository
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tiup/tiup-mirror.md

## Retrieval Guidance

- Use When: Use this chunk when you need to initialize a custom TiUP repository, generate keys and grant ownership, publish a self-built component, or merge custom components into another repository.
- Retrieval Keywords: Custom repository, tiup package, Component packaging, tiup mirror init /data/mirror, /data/mirror/keys, tiup mirror genkey, ~/.tiup/keys/private.json, tiup mirror set /data/mirror, tiup mirror grant jdoe, Work with custom components, hello.c, gcc hello.c -o hello, tiup package hello --entry hello --name hello --release v0.0.1, package/hello-v0.0.1-linux-amd64.tar.gz, tiup mirror publish hello v0.0.1 package/hello-v0.0.1-linux-amd64.tar.gz hello, tiup hello, The component `hello` version  is not installed; downloading from repository., tiup mirror merge, /data/my_custom_components
- Follow-up Guidance: The chunk also shows that `tiup mirror merge` can merge a repository with custom components into another one, assuming all components in `/data/my_custom_components` are signed by the current `$USER`.
- Classification Note: This is operation content because it provides step-by-step commands for creating a custom repository, generating and granting keys, packaging and publishing a component, and merging repositories.

## Official Source Content

## Custom repository

You can create a custom repository to work with TiDB components like TiDB, TiKV, or PD that you build by yourself. It is also possible to create your own tiup components.

To create your own components, run the `tiup package` command and perform as instructed in [Component packaging](https://github.com/pingcap/tiup/blob/master/doc/user/package.md).
### Create a custom repository

To create an empty repository in `/data/mirror`:

```bash
tiup mirror init /data/mirror
```

As part of creating the repository, keys will be written to `/data/mirror/keys`.

To create a new private key in `~/.tiup/keys/private.json`:

```bash
tiup mirror genkey
```

Grant `jdoe` with private key `~/.tiup/keys/private.json` ownership of `/data/mirror`:

```bash
tiup mirror set /data/mirror
tiup mirror grant jdoe
```
### Work with custom components

1. Create a custom component called hello.

    ```bash
    $ cat > hello.c << END
    > #include <stdio.h>
    int main() {
      printf("hello\n");
      return (0);
    }
    END
    $ gcc hello.c -o hello
    $ tiup package hello --entry hello --name hello --release v0.0.1
    ```

    `package/hello-v0.0.1-linux-amd64.tar.gz` is created.

2. Create a repository and a private key, and grant ownership to the repository.

    ```bash
    $ tiup mirror init /tmp/m
    $ tiup mirror genkey
    $ tiup mirror set /tmp/m
    $ tiup mirror grant $USER
    ```

    ```bash
    tiup mirror publish hello v0.0.1 package/hello-v0.0.1-linux-amd64.tar.gz hello
    ```

3. Run the component. If it is not installed yet, it will be downloaded first.

    ```bash
    $ tiup hello
    ```

    ```
    The component `hello` version  is not installed; downloading from repository.
    Starting component `hello`: /home/dvaneeden/.tiup/components/hello/v0.0.1/hello
    hello
    ```

    With `tiup mirror merge`, you can merge a repository with custom components into another one. This assumes that all components in `/data/my_custom_components` are signed by the current `$USER`.

    ```bash
    $ tiup mirror set /data/my_mirror
    $ tiup mirror grant $USER
    $ tiup mirror merge /data/my_custom_components
    ```
