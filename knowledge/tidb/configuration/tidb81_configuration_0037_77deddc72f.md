# Register a TiDB connector for Amazon AppFlow

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-aws-appflow-integration.md`
- Source Title: `Integrate TiDB with Amazon AppFlow`
- Source Heading Path: `Integrate TiDB with Amazon AppFlow | Integrate TiDB with Amazon AppFlow > Prerequisites | Integrate TiDB with Amazon AppFlow > Step 1. Register a TiDB connector | Integrate TiDB with Amazon AppFlow > Step 1. Register a TiDB connector > Clone the code | Integrate TiDB with Amazon AppFlow > Step 1. Register a TiDB connector > Build and upload a Lambda | Integrate TiDB with Amazon AppFlow > Step 1. Register a TiDB connector > Use Lambda to register a connector`
- Source Line Ranges: `5-93`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`
- Topic Tags: `amazon appflow`, `aws lambda`, `connector registration`, `prerequisites`, `sam deploy`, `salesforce`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0037_77deddc72f`
- Source ID: `tidb-docs-8.1:develop/dev-guide-aws-appflow-integration.md#integrate-tidb-with-amazon-appflow`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `151e25f5ba1cd9654716d764352ab2a6791cd636dc577d93fa9fa288567549a9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-aws-appflow-integration#integrate-tidb-with-amazon-appflow
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-aws-appflow-integration.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the prerequisites and AWS console or CLI steps to register a TiDB connector for Amazon AppFlow with AWS Lambda.
- Retrieval Keywords: Amazon AppFlow, Register a TiDB connector, AWS Lambda, sam deploy --guided, samconfig.toml, tidb-appflow-integration, git clone https://github.com/pingcap-inc/tidb-appflow-integration, AWS Management Console, Amazon AppFlow > Connectors, Register new connector, ConnectorFunctionRole, AWSCertificateManagerFullAccess, AWSCloudFormationFullAccess, AmazonS3FullAccess, AWSLambda_FullAccess, IAMFullAccess, SalesForce account
- Follow-up Guidance: After the Lambda is deployed and the connector is registered, the document continues with creating an Amazon AppFlow flow.
- Classification Note: The chunk is classified as configuration because it lists prerequisites, IAM permissions, build and deployment commands, and connector registration settings for Amazon AppFlow.

## Official Source Content

# Integrate TiDB with Amazon AppFlow

[Amazon AppFlow](https://aws.amazon.com/appflow/) is a fully managed API integration service that you use to connect your software as a service (SaaS) applications to AWS services, and securely transfer data. With Amazon AppFlow, you can import and export data from and to TiDB into many types of data providers, such as Salesforce, Amazon S3, LinkedIn, and GitHub. For more information, see [Supported source and destination applications](https://docs.aws.amazon.com/appflow/latest/userguide/app-specific.html) in AWS documentation.

This document describes how to integrate TiDB with Amazon AppFlow and takes integrating a {{{ .starter }}} cluster as an example.

If you do not have a TiDB cluster, you can [create a {{{ .starter }}} cluster](https://docs.pingcap.com/tidbcloud/create-tidb-cluster-serverless), which is free and can be created in approximately 30 seconds.
## Prerequisites

- [Git](https://git-scm.com/)
- [JDK](https://openjdk.org/install/) 11 or above
- [Maven](https://maven.apache.org/install.html) 3.8 or above
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html) version 2
- [AWS Serverless Application Model Command Line Interface (AWS SAM CLI)](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html) 1.58.0 or above
- An AWS [Identity and Access Management (IAM) user](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_users.html) with the following requirements:

    - The user can access AWS using an [access key](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_credentials_access-keys.html).
    - The user has the following permissions:

        - `AWSCertificateManagerFullAccess`: used for reading and writing the [AWS Secrets Manager](https://aws.amazon.com/secrets-manager/).
        - `AWSCloudFormationFullAccess`: SAM CLI uses [AWS CloudFormation](https://aws.amazon.com/cloudformation/) to proclaim the AWS resources.
        - `AmazonS3FullAccess`: AWS CloudFormation uses [Amazon S3](https://aws.amazon.com/s3/?nc2=h_ql_prod_fs_s3) to publish.
        - `AWSLambda_FullAccess`: currently, [AWS Lambda](https://aws.amazon.com/lambda/?nc2=h_ql_prod_fs_lbd) is the only way to implement a new connector for Amazon AppFlow.
        - `IAMFullAccess`: SAM CLI needs to create a `ConnectorFunctionRole` for the connector.

- A [SalesForce](https://developer.salesforce.com) account.
## Step 1. Register a TiDB connector
### Clone the code

Clone the [integration example code repository](https://github.com/pingcap-inc/tidb-appflow-integration) for TiDB and Amazon AppFlow:

```bash
git clone https://github.com/pingcap-inc/tidb-appflow-integration
```
### Build and upload a Lambda

1. Build the package:

    ```bash
    cd tidb-appflow-integration
    mvn clean package
    ```

2. (Optional) Configure your AWS access key ID and secret access key if you have not.

    ```bash
    aws configure
    ```

3. Upload your JAR package as a Lambda:

    ```bash
    sam deploy --guided
    ```

    > **Note:**
    >
    > - The `--guided` option uses prompts to guide you through the deployment. Your input will be stored in a configuration file, which is `samconfig.toml` by default.
    > - `stack_name` specifies the name of AWS Lambda that you are deploying.
    > - This prompted guide uses AWS as the cloud provider of {{{ .starter }}}. To use Amazon S3 as the source or destination, you need to set the `region` of AWS Lambda as the same as that of Amazon S3.
    > - If you have already run `sam deploy --guided` before, you can just run `sam deploy` instead, and SAM CLI will use the configuration file `samconfig.toml` to simplify the interaction.

    If you see a similar output as follows, this Lambda is successfully deployed.

    ```
    Successfully created/updated stack - <stack_name> in <region>
    ```

4. Go to the [AWS Lambda console](https://console.aws.amazon.com/lambda/home), and you can see the Lambda that you just uploaded. Note that you need to select the correct region in the upper-right corner of the window.

    ![lambda dashboard](/media/develop/aws-appflow-step-lambda-dashboard.png)
### Use Lambda to register a connector

1. In the [AWS Management Console](https://console.aws.amazon.com), navigate to [Amazon AppFlow > Connectors](https://console.aws.amazon.com/appflow/home#/gallery) and click **Register new connector**.

    ![register connector](/media/develop/aws-appflow-step-register-connector.png)

2. In the **Register a new connector** dialog, choose the Lambda function you uploaded and specify the connector label using the connector name.

    ![register connector dialog](/media/develop/aws-appflow-step-register-connector-dialog.png)

3. Click **Register**. Then, a TiDB connector is registered successfully.
