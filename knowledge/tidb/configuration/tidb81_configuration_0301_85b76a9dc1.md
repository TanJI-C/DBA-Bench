# Enable CMEK for a project and create a cluster

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-encrypt-cmek.md`
- Source Title: `Encryption at Rest Using Customer-Managed Encryption Keys`
- Source Heading Path: `Encryption at Rest Using Customer-Managed Encryption Keys > Enable CMEK > Step 1. Create a CMEK-enabled project | Encryption at Rest Using Customer-Managed Encryption Keys > Enable CMEK > Step 2. Complete the CMEK configuration of the project | Encryption at Rest Using Customer-Managed Encryption Keys > Enable CMEK > Step 3. Create a cluster`
- Source Line Ranges: `29-151`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `cmek`, `project-setup`, `api`, `console`, `aws-kms-policy`, `cluster-creation`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0301_85b76a9dc1`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-encrypt-cmek.md#step-1-create-a-cmek-enabled-project`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dc3d1a8484a69206ba770971ece139394b6b2b2e977fde8f46ad3a9929e16673`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-encrypt-cmek#step-1-create-a-cmek-enabled-project
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-encrypt-cmek.md

## Retrieval Guidance

- Use When: Use this chunk when the question asks how to enable CMEK for a project through the TiDB Cloud console or API, including AWS KMS policy details and cluster creation requirements.
- Retrieval Keywords: Create a CMEK-enabled project, aws_cmek_enabled, CreateProject, Configure AWS CMEK, CreateAwsCmek, Project Settings > Encryption Access, Create Encryption Key, KMS Key ARN, ROLE-TRUST-POLICY.JSON, key policy, kms:Encrypt, kms:Decrypt, kms:ReEncrypt*, kms:GenerateDataKey*, kms:CreateGrant, kms:DescribeKey, ec2.<region>.amazonaws.com, TiDB Cloud API beta, create a cluster same region
- Follow-up Guidance: The source notes that when CMEK is enabled, the cluster node EBS volumes and the S3 used for cluster backups are encrypted using CMEK.
- Classification Note: This is classified as configuration because the content provides the console and API setup flow, required fields, AWS KMS policy JSON, and region alignment needed to configure CMEK.

## Official Source Content

### Step 1. Create a CMEK-enabled project

If you are in the `Organization Owner` role of your organization, you can create a CMEK-enabled project using either the TiDB Cloud console or API.

<div label="Use Console" value="console">

To create a CMEK-enabled project, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target organization using the combo box in the upper-left corner.
2. In the left navigation pane, click **Projects**.
3. On the **Projects** page, click **Create New Project** in the upper-right corner.
4. Fill in a project name.
5. Choose to enable the CMEK capability of the project.
6. Click **Confirm** to complete the project creation.

</div>
<div label="Use API" value="api">

You can complete this step using TiDB Cloud API through the [Create a CMEK-enabled project](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Project/operation/CreateProject) endpoint. Make sure that the `aws_cmek_enabled` field is set to `true`.

Currently, TiDB Cloud API is still in beta. For more information, see [TiDB Cloud API Documentation](https://docs.pingcap.com/tidbcloud/api/v1beta).

</div>
### Step 2. Complete the CMEK configuration of the project

You can complete the CMEK configuration of the project using either the TiDB Cloud console or API.

> **Note:**
>
> Make sure that the policy of the key meets the requirements and is free from errors such as insufficient permissions or account issues. These errors can cause clusters to be incorrectly created using this key.

<div label="Use Console" value="console">

To complete the CMEK configuration of the project, take the following steps:

1. In the [TiDB Cloud console](https://tidbcloud.com), switch to your target project using the combo box in the upper-left corner.
2. In the left navigation pane, click **Project Settings** > **Encryption Access**.
3. On the **Encryption Access** page, click **Create Encryption Key** to enter the key creation page.
4. The key provider only supports AWS KMS. You can choose the region where the encryption key can be used.
5. Copy and save the JSON file as `ROLE-TRUST-POLICY.JSON`. This file describes the trust relationship.
6. Add this trust relationship to the key policy of AWS KMS. For more information, refer to [Key policies in AWS KMS](https://docs.aws.amazon.com/kms/latest/developerguide/key-policies.html).
7. In the TiDB Cloud console, scroll to the bottom of the key creation page, and then fill in the **KMS Key ARN** obtained from AWS KMS.
8. Click **Create** to create the key.

</div>
<div label="Use API" value="api">

1. Configure the key policy on AWS KMS, and add the following information to the key policy:

    ```json
    {
        "Version": "2012-10-17",
        "Id": "cmek-policy",
        "Statement": [
            // EBS-related policy
            {
                "Sid": "Allow access through EBS for all principals in the account that are authorized to use EBS",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "*"
                },
                "Action": [
                    "kms:Encrypt",
                    "kms:Decrypt",
                    "kms:ReEncrypt*",
                    "kms:GenerateDataKey*",
                    "kms:CreateGrant",
                    "kms:DescribeKey"
                ],
                "Resource": "*",
                "Condition": {
                    "StringEquals": {
                        "kms:CallerAccount": "<pingcap-account>",
                        "kms:ViaService": "ec2.<region>.amazonaws.com"
                    }
                }
            },
            // S3-related policy
            {
                "Sid": "Allow TiDB cloud role to use KMS to store encrypted backup to S3",
                "Effect": "Allow",
                "Principal": {
                    "AWS": "arn:aws:iam::<pingcap-account>:root"
                },
                "Action": [
                    "kms:Decrypt",
                    "kms:GenerateDataKey"
                ],
                "Resource": "*"
            },
            ... // user's own admin access to KMS
        ]
    }
    ```

    - `<pingcap-account>` is the account where your clusters run in. If you do not know the account, contact [TiDB Cloud Support](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-support).
    - `<region>` is the region where you want to create your cluster, for example, `us-west-2`. If you do not want to specify a region, replace `<region>` with a wildcard `*`, and put it in a `StringLike` block.
    - For EBS-related policy in the preceding block, refer to [AWS documentation](https://docs.aws.amazon.com/kms/latest/developerguide/conditions-kms.html#conditions-kms-caller-account).
    - For S3-related policy in the preceding block, refer to [AWS blog](https://repost.aws/knowledge-center/s3-bucket-access-default-encryption).

2. Call the [Configure AWS CMEK](https://docs.pingcap.com/tidbcloud/api/v1beta#tag/Cluster/operation/CreateAwsCmek) endpoint of TiDB Cloud API.

    Currently, TiDB Cloud API is still in beta. For more information, see [TiDB Cloud API Documentation](https://docs.pingcap.com/tidbcloud/api/v1beta).

</div>

> **Note:**
>
> This feature will be further enhanced in the future, and upcoming features might require additional permissions. Therefore, this policy requirement is subject to change.
### Step 3. Create a cluster

Under the project created in [Step 1](#step-1-create-a-cmek-enabled-project), create a TiDB Cloud Dedicated cluster hosted on AWS. For detailed steps, refer to [this document](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster). Ensure that the region where the cluster is located is the same as that in [Step 2](https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-encrypt-cmek#step-2-complete-the-cmek-configuration-of-the-project).

> **Note:**
>
> When CMEK is enabled, the EBS volumes used by the nodes of the cluster and the S3 used for the cluster backups are encrypted using CMEK.
