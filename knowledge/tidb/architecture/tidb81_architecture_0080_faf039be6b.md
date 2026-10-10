# AWS Lambda and CloudFormation integration overview and prerequisites

## Knowledge Metadata

- Knowledge Type: `architecture`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-aws-lambda.md`
- Source Title: `Integrate TiDB Cloud Serverless with Amazon Lambda Using AWS CloudFormation`
- Source Heading Path: `Integrate TiDB Cloud Serverless with Amazon Lambda Using AWS CloudFormation | Integrate TiDB Cloud Serverless with Amazon Lambda Using AWS CloudFormation > Solution overview | Integrate TiDB Cloud Serverless with Amazon Lambda Using AWS CloudFormation > Prerequisites`
- Source Line Ranges: `5-104`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `aws`, `lambda`, `cloudformation`, `api-gateway`, `secrets-manager`, `prerequisites`, `region`, `s3`, `iam`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_architecture_0080_faf039be6b`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-aws-lambda.md#integrate-tidb-cloud-serverless-with-amazon-lambda-using-aws-cloudformation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9346420a0241530bdea7b580480ed4e0f04e16fd699219f83556d423eb3c995e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-aws-lambda#integrate-tidb-cloud-serverless-with-amazon-lambda-using-aws-cloudformation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-aws-lambda.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the architecture overview, prerequisites, or region-specific setup details for integrating TiDB Cloud Serverless with AWS Lambda by using AWS CloudFormation.
- Retrieval Keywords: TiDB Cloud Serverless, AWS Lambda, AWS CloudFormation, AWS API Gateway, AWS Secrets Manager SDK, Sequelize ORM, Fastify API framework, AWS account prerequisites, S3, IAM Roles, Postman, cURL, cloudformation_template.yml, cloudformation_template.json, us-east-1, aws-lambda-cloudformation/src/secretManager.ts, region variable, yarn build, aws-lambda-cloudformation/dist/index.zip, Gitpod
- Follow-up Guidance: If a different AWS region other than `us-east-1` is used, the content includes the steps to modify `aws-lambda-cloudformation/src/secretManager.ts`, rebuild `index.zip`, and upload it to an S3 bucket.
- Classification Note: This chunk is classified as architecture because it describes the solution components, their roles, prerequisites, and the setup context for the integration.

## Official Source Content

# Integrate TiDB Cloud Serverless with Amazon Lambda Using AWS CloudFormation

This document provides a step-by-step guide on how to use [AWS CloudFormation](https://aws.amazon.com/cloudformation/) to integrate [TiDB Cloud Serverless](https://www.pingcap.com/tidb-cloud/), a cloud-native distributed SQL database, with [AWS Lambda](https://aws.amazon.com/lambda/), a serverless and event-driven compute service. By integrating TiDB Cloud Serverless with Amazon Lambda, you can leverage the scalability and cost-efficiency of microservices through TiDB Cloud Serverless and AWS Lambda. AWS CloudFormation automates the creation and management of AWS resources, including Lambda functions, API Gateway, and Secrets Manager.
## Solution overview

In this guide, you will create a fully functional online bookshop with the following components:

- AWS Lambda Function: handles requests and queries data from a TiDB Cloud Serverless cluster using Sequelize ORM and Fastify API framework.
- AWS Secrets Manager SDK: retrieves and manages connection configurations for the TiDB Cloud Serverless cluster.
- AWS API Gateway: handles HTTP request routes.
- TiDB Cloud Serverless: a cloud-native distributed SQL database.

AWS CloudFormation is used to create the necessary resources for the project, including the Secrets Manager, API Gateway, and Lambda Functions.

The structure of the bookshop project is as follows:

![AWS Lambda structure overview](/media/develop/aws-lambda-structure-overview.png)
## Prerequisites

Before getting started, ensure that you have the following:

- An AWS account with access to the following AWS services:
    - [AWS CloudFormation](https://aws.amazon.com/cloudformation/)
    - [Secrets Manager](https://aws.amazon.com/secrets-manager/)
    - [API Gateway](https://aws.amazon.com/api-gateway/)
    - [Lambda services](https://aws.amazon.com/lambda/)
    - [S3](https://aws.amazon.com/s3/)
    - [IAM Roles](https://docs.aws.amazon.com/IAM/latest/UserGuide/id_roles.html)
- A [TiDB Cloud](https://tidbcloud.com) account and a TiDB Cloud Serverless cluster. Get the connection information for your TiDB Cloud Serverless cluster:

    ![TiDB Cloud connection information](/media/develop/aws-lambda-tidbcloud-connection-info.png)

- API test tools such as [Postman](https://www.postman.com/) and [cURL](https://curl.se/). Most examples in this document use cURL. For Windows users, Postman is recommended.
- Download the [latest release assets](https://github.com/pingcap/TiDB-Lambda-integration/releases/latest) of the project to your local machine, which includes `cloudformation_template.yml` and `cloudformation_template.json` files.

> **Note:**
>
> - When you create the AWS resources, it is recommended to use `us-east-1` as your cluster region. This is because the Lambda function code in this demo hardcodes the region as `us-east-1`, and the code bundle is stored in the `us-east-1` region. 
> - If you use a different region, you need to follow the following instructions to modify the Lambda function code, rebuild it, and upload the code bundle to your own S3 bucket.

<details>
<summary>Modify and rebuild the Lambda function code if you use a region other than <code>us-east-1</code></summary>

If you use `us-east-1` as your cluster region, skip this section and go to [Step 1: Set up the project using AWS CloudFormation](#step-1-set-up-the-bookshop-project-using-aws-cloudformation).

If you use a different AWS region other than `us-east-1` to create the AWS resources, you need to modify the Lambda function code, rebuild it, and upload the code bundle to your own S3 bucket.

To avoid local development environment issues, it is recommended that you use a cloud-native development environment, such as [Gitpod](https://www.gitpod.io/).

To rebuild and upload the code bundle to your own S3 bucket, do the following:

1. Initialize the development environment.

    - Open the [Gitpod](https://gitpod.io/#/https://github.com/pingcap/TiDB-Lambda-integration) workspace and log in with your GitHub account.

2. Modify the Lambda function code.

    1. Open the `aws-lambda-cloudformation/src/secretManager.ts` file in the left sidebar.
    2. Locate the line 22 and then modify the `region` variable to match your own region.

3. Rebuild the code bundle.

    1. Install the dependencies.

        1. Open a terminal in Gitpod.
        2. Enter the working directory:

            ```shell
            cd aws-lambda-cloudformation
            ```

        3. Install the dependencies:

            ```shell
            yarn
            ```

    2. Rebuild the code bundle.

        1. Build the code bundle.

            ```shell
            yarn build
            ```

        2. Check the `aws-lambda-cloudformation/dist/index.zip` file.
        3. Right-click the `index.zip` file and select **Download**.

4. Upload the rebuilt code bundle to your own S3 bucket.

    1. Visit the [S3 service](https://console.aws.amazon.com/s3) in the AWS Management Console.
    2. Create a new bucket in your selected region.
    3. Upload the `index.zip` file to the bucket.
    4. Note down the S3 bucket name and region for later use.

</details>
