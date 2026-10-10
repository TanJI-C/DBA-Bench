# Deploy, test, and clean up the bookshop project

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/integrate-tidbcloud-with-aws-lambda.md`
- Source Title: `Integrate TiDB Cloud Serverless with Amazon Lambda Using AWS CloudFormation`
- Source Heading Path: `Integrate TiDB Cloud Serverless with Amazon Lambda Using AWS CloudFormation > Step 1. Set up the bookshop project using AWS CloudFormation | Integrate TiDB Cloud Serverless with Amazon Lambda Using AWS CloudFormation > Step 2. Use the bookshop project | Integrate TiDB Cloud Serverless with Amazon Lambda Using AWS CloudFormation > Step 3. Clean up resources`
- Source Line Ranges: `105-202`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `ecosystem`
- Topic Tags: `deployment`, `cloudformation`, `stack`, `api-testing`, `curl`, `bookshop`, `cleanup`, `api-gateway`, `s3`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0332_ac76b8de3c`
- Source ID: `tidb-docs-8.1:tidb-cloud/integrate-tidbcloud-with-aws-lambda.md#step-1-set-up-the-bookshop-project-using-aws-cloudformation`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9253fa7640266f71ddacdf8335791209e1d4908f7101bb35ad32d2a92e01b21d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/integrate-tidbcloud-with-aws-lambda#step-1-set-up-the-bookshop-project-using-aws-cloudformation
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/integrate-tidbcloud-with-aws-lambda.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the documented deployment steps, API testing examples, or cleanup procedure for the AWS CloudFormation bookshop project.
- Retrieval Keywords: Create Stack, With new resources (standard), Choose an existing template, Upload a template file, S3Bucket, S3Key, TiDBDatabase, TiDBHost, localhost, TiDBPassword, TiDBPort, TiDBUser, TiDBCloudApiGatewayV2, Invoke URL, curl -X POST, /book/init, /book, /book/<book-id>, curl -X PUT, curl -X DELETE, delete the AWS CloudFormation stack
- Follow-up Guidance: After the stack is created, the content says to get the `Invoke URL` from `TiDBCloudApiGatewayV2` in API Gateway and use Postman or cURL to test the book APIs.
- Classification Note: This chunk is classified as operation because it provides the procedural steps to create the stack, use the deployed API, and clean up the created resources.

## Official Source Content

## Step 1. Set up the bookshop project using AWS CloudFormation

To set up the bookshop project using AWS CloudFormation, do the following:

1. Navigate to the AWS Management Console and access the [AWS CloudFormation service](https://console.aws.amazon.com/cloudformation).
2. Click **Create Stack** > **With new resources (standard)**.
3. On the **Create Stack** page, complete the stack creation process.

    1. In the **Prerequisite** area, select **Choose an existing template**.
    2. In the **Specify template** area, select **Upload a template file**, click **Choose file** to upload the template file (either YAML or JSON), and click **Next**.

        If you do not have the file yet, download it from [GitHub](https://github.com/pingcap/TiDB-Lambda-integration/releases/latest). The file contains the AWS CloudFormation template that creates the necessary resources for the project.

        ![Create a stack](/media/develop/aws-lambda-cf-create-stack.png)

    3. Specify stack details.

        - If you use `us-east-1` as your cluster region, fill in the fields as in the following screenshot:

            ![Specify AWS Lambda stack details](/media/develop/aws-lambda-cf-stack-config.png)

            - **Stack name**: enter the stack name.
            - **S3Bucket**: enter the S3 bucket where you store the zip file.
            - **S3Key**: enter the S3 key.
            - **TiDBDatabase**: enter the TiDB Cloud cluster name.
            - **TiDBHost**: enter the host URL for TiDB Cloud database access. Enter `localhost`.
            - **TiDBPassword**: enter the password for TiDB Cloud database access.
            - **TiDBPort**: enter the port for TiDB Cloud database access.
            - **TiDBUser**: enter the user name for TiDB Cloud database access.

        - If you use a different AWS region other than `us-east-1`, follow these steps:

            1. Refer to [Modify and rebuild the Lambda function code if you use a region other than `us-east-1`](#prerequisites) to modify the Lambda function code, rebuild it, and upload the code bundle to your own S3 bucket.
            2. In the stack details fields, specify the S3 bucket name and region in the `S3Bucket` and `S3Key` parameters according to your own configuration.
            3. Fill in other fields as in the preceding screenshot.

    4. Configure stack options. You can use the default configurations.

        ![Configure stack options](/media/develop/aws-lambda-cf-stack-config-option.png)

    5. Review and create the stack.

        ![Review and create the stack](/media/develop/aws-lambda-cf-stack-config-review.png)
## Step 2. Use the bookshop project

After the stack has been created, you can use the project as follows:

1. Visit the [API Gateway service](https://console.aws.amazon.com/apigateway) in the AWS Management Console, click the `TiDBCloudApiGatewayV2` API, and then click **API: TiDBCloudApiGatewayV2** in the left pane.

2. Copy the `Invoke URL` from the **Overview** page. This URL serves as the API endpoint.

    ![API Gateway Invoke URL](/media/develop/aws-lambda-get-apigateway-invoke-url.png)

3. Use API test tools such as Postman and cURL to test the API:

    - Init mock books:

        ```shell
        curl -X POST -H "Content-Type: application/json" -d '{"count":100}' https://<your-api-endpoint>/book/init
        ```

    - Get all books:

        ```shell
        curl https://<your-api-endpoint>/book
        ```

    - Get a book by the book ID:

        ```shell
        curl https://<your-api-endpoint>/book/<book-id>
        ```

    - Create a book:

        ```shell
        curl -X POST -H "Content-Type: application/json" -d '{ "title": "Book Title", "type": "Test", "publishAt": "2022-12-15T21:01:49.000Z", "stock": 123, "price": 12.34, "authors": "Test Test" }' https://  <your-api-endpoint>/book
        ```

    - Update a book:

        ```shell
        curl -X PUT -H "Content-Type: application/json" -d '{ "title": "Book Title(updated)" }' https://<your-api-endpoint>/book/<book-id>
        ```

    - Delete a book:

        ```shell
        curl -X DELETE https://<your-api-endpoint>/book/<book-id>
        ```
## Step 3. Clean up resources

To avoid unnecessary charges, clean up all resources that have been created.

1. Access the [AWS Management Console](https://console.aws.amazon.com/cloudformation). 
2. Delete the AWS CloudFormation stack that you created.
