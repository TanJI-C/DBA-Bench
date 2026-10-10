# Delete a TiDB Cloud cluster with terraform destroy

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/terraform-use-cluster-resource.md`
- Source Title: `Use Cluster Resource (Deprecated)`
- Source Heading Path: `Use Cluster Resource (Deprecated) > Delete a cluster`
- Source Line Ranges: `965-985`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`
- Topic Tags: `terraform`, `deletion`, `destroy`, `cluster-management`, `state-management`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0375_6602fc07f6`
- Source ID: `tidb-docs-8.1:tidb-cloud/terraform-use-cluster-resource.md#delete-a-cluster`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b5ac22213feebe6a54a16f62e9244682325e64f41504e5ecc7f5989bd1c97df2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/terraform-use-cluster-resource#delete-a-cluster
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/terraform-use-cluster-resource.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documented command flow to delete a TiDB Cloud cluster resource managed by Terraform.
- Retrieval Keywords: Delete a cluster, terraform destroy, cluster.tf, terraform show, Plan: 0 to add, 0 to change, 1 to destroy, Do you really want to destroy all resources?, There is no undo, Enter a value: yes
- Follow-up Guidance: After `terraform destroy`, the content says that running `terraform show` returns nothing because the resource has been cleared.
- Classification Note: This is an operation chunk because the content gives the command sequence and expected prompt/output for destroying a Terraform-managed cluster resource.

## Official Source Content

## Delete a cluster

To delete a cluster, go to the cluster directory where the corresponding `cluster.tf` file is located, and then run the `terraform destroy` command to destroy the cluster resource:

```
$ terraform destroy

Plan: 0 to add, 0 to change, 1 to destroy.

Do you really want to destroy all resources?
Terraform will destroy all your managed infrastructure, as shown above.
There is no undo. Only 'yes' will be accepted to confirm.

Enter a value: yes
```

Now, if you run the `terraform show` command, you will get nothing because the resource has been cleared:

```
$ terraform show
```
