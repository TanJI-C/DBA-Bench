# TiDB Cloud audit logging overview and AWS setup

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/tidb-cloud-auditing.md`
- Source Title: `TiDB Cloud Dedicated Database Audit Logging`
- Source Heading Path: `TiDB Cloud Dedicated Database Audit Logging | TiDB Cloud Dedicated Database Audit Logging > Prerequisites | TiDB Cloud Dedicated Database Audit Logging > Enable audit logging | TiDB Cloud Dedicated Database Audit Logging > Enable audit logging > Enable audit logging for AWS | TiDB Cloud Dedicated Database Audit Logging > Enable audit logging > Enable audit logging for AWS > Step 1. Create an Amazon S3 bucket | TiDB Cloud Dedicated Database Audit Logging > Enable audit logging > Enable audit logging for AWS > Step 2. Configure Amazon S3 access | TiDB Cloud Dedicated Database Audit Logging > Enable audit logging > Enable audit logging for AWS > Step 3. Enable audit logging`
- Source Line Ranges: `5-112`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: none
- Topic Tags: `audit-logging`, `prerequisites`, `aws`, `s3`, `iam`, `bucket-access`, `connection-testing`, `security`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0296_082bb4a473`
- Source ID: `tidb-docs-8.1:tidb-cloud/tidb-cloud-auditing.md#tidb-cloud-dedicated-database-audit-logging`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `dc1e08e98a9d9450c925de94f6a350e964f848c699f9b9774efa1b52e35245ef`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/tidb-cloud-auditing#tidb-cloud-dedicated-database-audit-logging
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/tidb-cloud-auditing.md

## Retrieval Guidance

- Use When: Use this chunk when you need the prerequisites and AWS S3 or IAM details for enabling TiDB Cloud Dedicated database audit logging and testing the bucket connection.
- Retrieval Keywords: TiDB Cloud Dedicated Database Audit Logging, DB Audit Logging, audit logging is disabled by default, TiDB Cloud Dedicated cluster, Serverless clusters not available, Organization Owner, Project Owner, AWS IAM Policy Settings, TiDB Cloud Account ID, TiDB Cloud External ID, Amazon S3 bucket, object lock, s3:PutObject, Bucket URI, Bucket Region, Role ARN, Test Connection, The connection is successfully, Apply for database audit logging, Apply to store audit log files in TiDB Cloud
- Follow-up Guidance: The chunk also states that after changing the bucket URI, location, or ARN, you must click Test Connection again and then click Enable to apply the changes.
- Classification Note: This chunk is classified as configuration because it provides prerequisites and step-by-step AWS bucket, IAM policy, role, and console field setup for enabling audit logging.

## Official Source Content

# TiDB Cloud Dedicated Database Audit Logging

TiDB Cloud provides you with a database audit logging feature to record a history of user access details (such as any SQL statements executed) in logs.

> **Note:**
>
> Currently, the database audit logging feature is only available upon request. To request this feature, click **?** in the lower-right corner of the [TiDB Cloud console](https://tidbcloud.com) and click **Request Support**. Then, fill in "Apply for database audit logging" in the **Description** field and click **Submit**.

To assess the effectiveness of user access policies and other information security measures of your organization, it is a security best practice to conduct a periodic analysis of the database audit logs.

The audit logging feature is disabled by default. To audit a cluster, you need to enable the audit logging first, and then specify the auditing filter rules.

> **Note:**
>
> Because audit logging consumes cluster resources, be prudent about whether to audit a cluster.
## Prerequisites

- You are using a TiDB Cloud Dedicated cluster. Audit logging is not available for TiDB Cloud Serverless clusters.
- You are in the `Organization Owner` or `Project Owner` role of your organization. Otherwise, you cannot see the database audit-related options in the TiDB Cloud console. For more information, see [User roles](https://docs.pingcap.com/tidb/stable/tidb-cloud/manage-user-access#user-roles).
## Enable audit logging

TiDB Cloud supports recording the audit logs of a TiDB Cloud Dedicated cluster to your cloud storage service. Before enabling database audit logging, configure your cloud storage service on the cloud provider where the cluster is located.

> **Note:**
>
> For TiDB clusters deployed on AWS, you can choose to store audit log files in TiDB Cloud when enabling database audit logging. Currently, this feature is only available upon request. To request this feature, click **?** in the lower-right corner of the [TiDB Cloud console](https://tidbcloud.com) and click **Request Support**. Then, fill in "Apply to store audit log files in TiDB Cloud" in the **Description** field and click **Submit**.
### Enable audit logging for AWS

To enable audit logging for AWS, take the following steps:
#### Step 1. Create an Amazon S3 bucket

Specify an Amazon S3 bucket in your corporate-owned AWS account as a destination to which TiDB Cloud writes the audit logs.

> Note:
>
> Do not enable object lock on the AWS S3 bucket. Enabling object lock will prevent TiDB Cloud from pushing audit log files to S3.

For more information, see [Creating a bucket](https://docs.aws.amazon.com/AmazonS3/latest/userguide/create-bucket-overview.html) in the AWS User Guide.
#### Step 2. Configure Amazon S3 access

1. Get the TiDB Cloud Account ID and the External ID of the TiDB cluster that you want to enable audit logging.

    1. In the TiDB Cloud console, navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Settings** > **DB Audit Logging** in the left navigation pane.
    3. On the **DB Audit Logging** page, click **Enable** in the upper-right corner.
    4. In the **Enable Database Audit Logging** dialog, locate the **AWS IAM Policy Settings** section, and record **TiDB Cloud Account ID** and **TiDB Cloud External ID** for later use.

2. In the AWS Management Console, go to **IAM** > **Access Management** > **Policies**, and then check whether there is a storage bucket policy with the `s3:PutObject` write-only permission.

    - If yes, record the matched storage bucket policy for later use.
    - If not, go to **IAM** > **Access Management** > **Policies** > **Create Policy**, and define a bucket policy according to the following policy template.

        ```json
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Action": "s3:PutObject",
                    "Resource": "<Your S3 bucket ARN>/*"
                }
            ]
        }
        ```

        In the template, `<Your S3 bucket ARN>` is the Amazon Resource Name (ARN) of your S3 bucket where the audit log files are to be written. You can go to the **Properties** tab in your S3 bucket and get the ARN value in the **Bucket Overview** area. In the `"Resource"` field, you need to add `/*` after the ARN. For example, if the ARN is `arn:aws:s3:::tidb-cloud-test`, you need to configure the value of the `"Resource"` field as `"arn:aws:s3:::tidb-cloud-test/*"`.

3. Go to **IAM** > **Access Management** > **Roles**, and then check whether a role whose trust entity corresponds to the TiDB Cloud Account ID and the External ID that you recorded earlier already exists.

    - If yes, record the matched role for later use.
    - If not, click **Create role**, select **Another AWS account** as the trust entity type, and then enter the TiDB Cloud Account ID value into the **Account ID** field. Then, choose the **Require External ID** option and enter the TiDB Cloud External ID value into the **External ID** field.

4. In **IAM** > **Access Management** > **Roles**, click the role name from the previous step to go to the **Summary** page, and then take the following steps:

    1. Under the **Permissions** tab, check whether the recorded policy with the `s3:PutObject` write-only permission is attached to the role. If not, choose **Attach Policies**, search for the needed policy, and then click **Attach Policy**.
    2. Return to the **Summary** page and copy the **Role ARN** value to your clipboard.
#### Step 3. Enable audit logging

In the TiDB Cloud console, go back to the **Enable Database Audit Logging** dialog box where you got the TiDB Cloud account ID and the External ID values, and then take the following steps:

1. In the **Bucket URI** field, enter the URI of your S3 bucket where the audit log files are to be written.
2. In the **Bucket Region** drop-down list, select the AWS region where the bucket locates.
3. In the **Role ARN** field, fill in the Role ARN value that you copied in [Step 2. Configure Amazon S3 access](#step-2-configure-amazon-s3-access).
4. Click **Test Connection** to verify whether TiDB Cloud can access and write to the bucket.

    If it is successful, **The connection is successfully** is displayed. Otherwise, check your access configuration.

5. Click **Enable** to enable audit logging for the cluster.

    TiDB Cloud is ready to write audit logs for the specified cluster to your Amazon S3 bucket.

> **Note:**
>
> - After enabling audit logging, if you make any new changes to the bucket URI, location, or ARN, you must click **Test Connection** again to verify that TiDB Cloud can connect to the bucket. Then, click **Enable** to apply the changes.
> - To remove TiDB Cloud's access to your Amazon S3, simply delete the trust policy granted to this cluster in the AWS Management Console.
