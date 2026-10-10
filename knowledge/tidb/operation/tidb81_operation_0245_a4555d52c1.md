# TiCDC upgrade, configuration, lifecycle, TLS, and status commands

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/deploy-ticdc.md`
- Source Title: `Deploy and Maintain TiCDC`
- Source Heading Path: `Deploy and Maintain TiCDC > Upgrade TiCDC using TiUP | Deploy and Maintain TiCDC > Upgrade TiCDC using TiUP > Upgrade cautions | Deploy and Maintain TiCDC > Modify TiCDC cluster configurations using TiUP | Deploy and Maintain TiCDC > Stop and start TiCDC using TiUP | Deploy and Maintain TiCDC > Enable TLS for TiCDC | Deploy and Maintain TiCDC > View TiCDC status using the command-line tool`
- Source Line Ranges: `86-181`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `tiup`, `tidb`, `pd`, `tikv`, `tiflash`, `shared`
- Topic Tags: `upgrade`, `rolling-upgrade`, `compatibility`, `configuration`, `gc-ttl`, `reload`, `start-stop`, `restart`, `tls`, `status`, `cli`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0245_a4555d52c1`
- Source ID: `tidb-docs-8.1:ticdc/deploy-ticdc.md#upgrade-ticdc-using-tiup`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e92ca68f9ab09cad7f487890472d2fd98bc035cf95f00794be0454eb1b303771`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/deploy-ticdc#upgrade-ticdc-using-tiup
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/deploy-ticdc.md

## Retrieval Guidance

- Use When: Use this chunk when you need TiUP commands and cautions for upgrading, reconfiguring, starting or stopping, enabling TLS for, or checking the status of TiCDC.
- Retrieval Keywords: Upgrade TiCDC using TiUP, tiup cluster upgrade <cluster-name> <version> --transfer-timeout 600, tiup update --self, tiup update --all, Upgrade cautions, TiCDC v4.0.2 reconfigured changefeed, Configuration file compatibility notes, Since v6.3.0 TiCDC supports rolling upgrade, TiUP v1.11.3 or later, at least two TiCDC instances, Modify TiCDC cluster configurations using TiUP, tiup cluster edit-config <cluster-name>, server_configs, cdc, gc-ttl, 172800, tiup cluster reload -R cdc, Stop and start TiCDC using TiUP, tiup cluster stop -R cdc, tiup cluster start -R cdc, tiup cluster restart -R cdc, Enable TLS for TiCDC, View TiCDC status using the command-line tool, tiup cdc:v<CLUSTER_VERSION> cli capture list --server=http://10.0.10.25:8300, is-owner, cluster-id, default
- Follow-up Guidance: The source also references configuration file compatibility notes, upgrade FAQs, and the document for enabling TLS between TiDB components.
- Classification Note: This is classified as operation for the `ticdc` component because the content describes operational lifecycle tasks including upgrade, configuration reload, process control, TLS enablement reference, and CLI status inspection.

## Official Source Content

## Upgrade TiCDC using TiUP

You can upgrade TiDB clusters using TiUP, during which TiCDC is upgraded as well. After you execute the upgrade command, TiUP automatically upgrades the TiCDC component. The following is an example:

```shell
tiup update --self && \
tiup update --all && \
tiup cluster upgrade <cluster-name> <version> --transfer-timeout 600
```

> **Note:**
>
> In the preceding command, you need to replace `<cluster-name>` and `<version>` with the actual cluster name and cluster version. For example, the version can be v8.1.2.
### Upgrade cautions

When you upgrade a TiCDC cluster, you need to pay attention to the following:

- TiCDC v4.0.2 reconfigured `changefeed`. For details, see [Configuration file compatibility notes](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-compatibility#cli-and-configuration-file-compatibility).
- If you encounter any problem during the upgrade, you can refer to [upgrade FAQs](https://docs.pingcap.com/tidb/stable/upgrade-tidb-using-tiup#faq) for solutions.
- Since v6.3.0, TiCDC supports rolling upgrade. During the upgrade, the replication latency is stable and does not fluctuate significantly. Rolling upgrade takes effect automatically if the following conditions are met:

- TiCDC is v6.3.0 or later.
    - TiUP is v1.11.3 or later.
    - At least two TiCDC instances are running in the cluster.
## Modify TiCDC cluster configurations using TiUP

This section describes how to use the [`tiup cluster edit-config`](https://docs.pingcap.com/tidb/stable/tiup/tiup-component-cluster-edit-config) command to modify the configurations of TiCDC. In the following example, it is assumed that you need to change the default value of `gc-ttl` from `86400` to `172800` (48 hours).

1. Run the `tiup cluster edit-config` command. Replace `<cluster-name>` with the actual cluster name:

    ```shell
    tiup cluster edit-config <cluster-name>
    ```

2. In the vi editor, modify the `cdc` [`server-configs`](https://docs.pingcap.com/tidb/stable/tiup/tiup-cluster-topology-reference#server_configs):

    ```shell
    server_configs:
      tidb: {}
      tikv: {}
      pd: {}
      tiflash: {}
      tiflash-learner: {}
      pump: {}
      drainer: {}
      cdc:
        gc-ttl: 172800
    ```

    In the preceding command, `gc-ttl` is set to 48 hours.

3. Run the `tiup cluster reload -R cdc` command to reload the configuration.
## Stop and start TiCDC using TiUP

You can use TiUP to easily stop and start TiCDC nodes. The commands are as follows:

- Stop TiCDC: `tiup cluster stop -R cdc`
- Start TiCDC: `tiup cluster start -R cdc`
- Restart TiCDC: `tiup cluster restart -R cdc`
## Enable TLS for TiCDC

See [Enable TLS Between TiDB Components](https://docs.pingcap.com/tidb/stable/enable-tls-between-components).
## View TiCDC status using the command-line tool

Run the following command to view the TiCDC cluster status. Note that you need to replace `v<CLUSTER_VERSION>` with the TiCDC cluster version, such as `v8.1.2`:

```shell
tiup cdc:v<CLUSTER_VERSION> cli capture list --server=http://10.0.10.25:8300
```

```shell
[
  {
    "id": "806e3a1b-0e31-477f-9dd6-f3f2c570abdd",
    "is-owner": true,
    "address": "127.0.0.1:8300",
    "cluster-id": "default"
  },
  {
    "id": "ea2a4203-56fe-43a6-b442-7b295f458ebc",
    "is-owner": false,
    "address": "127.0.0.1:8301",
    "cluster-id": "default"
  }
]
```

- `id`: Indicates the ID of the service process.
- `is-owner`: Indicates whether the service process is the owner node.
- `address`: Indicates the address via which the service process provides interface to the outside.
- `cluster-id`: Indicates the ID of the TiCDC cluster. The default value is `default`.
