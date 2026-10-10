# Import and upgrade a DM 1.0 cluster from DM-Ansible

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/maintain-dm-using-tiup.md`
- Source Title: `Maintain a DM Cluster Using TiUP`
- Source Heading Path: `Maintain a DM Cluster Using TiUP > Import and upgrade a DM 1.0 cluster deployed using DM-Ansible`
- Source Line Ranges: `271-302`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: `tiup`
- Topic Tags: `import`, `upgrade`, `dm-ansible`, `topology`, `migration`, `version-compatibility`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0119_a4b31903fb`
- Source ID: `tidb-docs-8.1:dm/maintain-dm-using-tiup.md#import-and-upgrade-a-dm-1-0-cluster-deployed-using-dm-ansible`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `caafd3c53741ac91451b7a23c0e17471ca9d6da427ccdeac488612a0306770d9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/maintain-dm-using-tiup#import-and-upgrade-a-dm-1-0-cluster-deployed-using-dm-ansible
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/maintain-dm-using-tiup.md

## Retrieval Guidance

- Use When: Use this chunk when you need the TiUP DM import procedure, limitations, and version notes for taking over a DM 1.0 cluster deployed using DM-Ansible.
- Retrieval Keywords: tiup dm import, DM 1.0 cluster deployed using DM-Ansible, DM Portal component, You need to stop the original cluster before importing, Don't run stop-task, TiUP only supports importing to a DM cluster of v2.0.0-rc.2 or a later version, tiup update --self && tiup update dm, tiup dm import --dir=/path/to/dm-ansible --cluster-version ${version}, tiup list dm-master, topology.yml, Only one DM-master node exists in the cluster after importing, tiup dm start
- Follow-up Guidance: The source states that TiUP generates `topology.yml` from the previous DM-Ansible deployment, then after deployment you can run `tiup dm start` to begin upgrading the DM kernel.
- Classification Note: This is classified as an operation because the content explains the import and upgrade workflow for a DM 1.0 cluster into a TiUP-managed DM 2.0 or later deployment.

## Official Source Content

## Import and upgrade a DM 1.0 cluster deployed using DM-Ansible

> **Note:**
>
> - TiUP does not support importing the DM Portal component in a DM 1.0 cluster.
> - You need to stop the original cluster before importing.
> - Don't run `stop-task` for tasks that need to be upgraded to 2.0.
> - TiUP only supports importing to a DM cluster of v2.0.0-rc.2 or a later version.
> - The `import` command is used to import data from a DM 1.0 cluster to a new DM 2.0 cluster. If you need to import DM migration tasks to an existing DM 2.0 cluster, refer to [Manually Upgrade TiDB Data Migration from v1.0.x to v2.0+](https://docs.pingcap.com/tidb/stable/dm/manually-upgrade-dm-1.0-to-2.0).
> - The deployment directories of some components are different from those of the original cluster. You can execute the `display` command to view the details.
> - Run `tiup update --self && tiup update dm` before importing to make sure that the TiUP DM component is the latest version.
> - Only one DM-master node exists in the cluster after importing. Refer to [Scale out a cluster](#scale-out-a-cluster) to scale out the DM-master.

Before TiUP is released, DM-Ansible is often used to deploy DM clusters. To enable TiUP to take over the DM 1.0 cluster deployed by DM-Ansible, use the `import` command.

For example, to import a cluster deployed using DM Ansible:

```bash
tiup dm import --dir=/path/to/dm-ansible --cluster-version ${version}
```

Execute `tiup list dm-master` to view the latest cluster version supported by TiUP.

The process of using the `import` command is as follows:

1. TiUP generates a topology file [`topology.yml`](https://github.com/pingcap/tiup/blob/master/embed/examples/dm/topology.example.yaml) based on the DM cluster previously deployed using DM-Ansible.
2. After confirming that the topology file has been generated, you can use it to deploy the DM cluster of v2.0 or later versions.

After the deployment is completed, you can execute the `tiup dm start` command to start the cluster and begin the process of upgrading the DM kernel.
