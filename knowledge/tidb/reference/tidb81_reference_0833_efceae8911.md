# Private endpoint status reference and connectivity troubleshooting

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/set-up-private-endpoint-connections.md`
- Source Title: `Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink`
- Source Heading Path: `Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink > Set up a private endpoint connection and connect to your cluster > Private endpoint status reference | Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink > Troubleshooting | Connect to a TiDB Cloud Dedicated Cluster via AWS PrivateLink > Troubleshooting > I cannot connect to a TiDB cluster via a private endpoint after enabling private DNS. Why?`
- Source Line Ranges: `185-212`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `aws-privatelink`, `private-endpoint`, `status-reference`, `network-access`, `troubleshooting`, `private-dns`, `security-groups`, `vpc-endpoint`, `connectivity`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0833_efceae8911`
- Source ID: `tidb-docs-8.1:tidb-cloud/set-up-private-endpoint-connections.md#private-endpoint-status-reference`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `735a87cb56947d322497de61bbb937d6a9c393573593f6bc30c90901ddd7afb0`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/set-up-private-endpoint-connections#private-endpoint-status-reference
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/set-up-private-endpoint-connections.md

## Retrieval Guidance

- Use When: Use this chunk when looking for TiDB Cloud AWS PrivateLink private endpoint or private endpoint service status meanings, where those statuses are shown, or connectivity troubleshooting after enabling private DNS.
- Retrieval Keywords: AWS PrivateLink, private endpoint status reference, private endpoint service status, Not Configured, Pending, Active, Deleting, Failed, Creating, Cluster-level Networking page, Project-level Network Access page, Settings > Networking, Project Settings > Network Access, private DNS, I cannot connect to a TiDB cluster via a private endpoint after enabling private DNS, VPC > Endpoints, Manage security groups, Port 4000, customer-defined port
- Follow-up Guidance: For the private DNS connectivity issue, the content points to checking the VPC endpoint security group in the AWS Management Console under VPC > Endpoints and Manage security groups, allowing inbound access from EC2 instances on Port 4000 or a customer-defined port.
- Classification Note: This is reference content because it defines the displayed statuses for private endpoints and private endpoint services and includes a scoped troubleshooting note for private DNS connectivity.

## Official Source Content

### Private endpoint status reference

When you use private endpoint connections, the statuses of private endpoints or private endpoint services are displayed on the following pages:

- Cluster-level **Networking** page: switch to your target cluster using the combo box in the upper-left corner, and then click **Settings** > **Networking** in the left navigation pane.
- Project-level **Network Access** page: switch to your target project using the combo box in the upper-left corner, and then click **Project Settings** > **Network Access** in the left navigation pane.

The possible statuses of a private endpoint are explained as follows:

- **Not Configured**: The endpoint service is created but the private endpoint is not created yet.
- **Pending**: Waiting for processing.
- **Active**: Your private endpoint is ready to use. You cannot edit the private endpoint of this status.
- **Deleting**: The private endpoint is being deleted.
- **Failed**: The private endpoint creation fails. You can click **Edit** of that row to retry the creation.

The possible statuses of a private endpoint service are explained as follows:

- **Creating**: The endpoint service is being created, which takes 3 to 5 minutes.
- **Active**: The endpoint service is created, no matter whether the private endpoint is created or not.
- **Deleting**: The endpoint service or the cluster is being deleted, which takes 3 to 5 minutes.
## Troubleshooting
### I cannot connect to a TiDB cluster via a private endpoint after enabling private DNS. Why?

You might need to properly set the security group for your VPC endpoint in the AWS Management Console. Go to **VPC** > **Endpoints**. Right-click your VPC endpoint and select the proper **Manage security groups**. A proper security group within your VPC that allows inbound access from your EC2 instances on Port 4000 or a customer-defined port.

![Manage security groups](/media/tidb-cloud/private-endpoint/manage-security-groups.png)
