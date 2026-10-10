# Run the AWS Lambda sample app and connect to TiDB

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-sample-application-aws-lambda.md`
- Source Title: `Connect to TiDB with mysql2 in AWS Lambda Function`
- Source Heading Path: `Connect to TiDB with mysql2 in AWS Lambda Function > Run the sample app to connect to TiDB | Connect to TiDB with mysql2 in AWS Lambda Function > Run the sample app to connect to TiDB > Step 1: Clone the sample app repository | Connect to TiDB with mysql2 in AWS Lambda Function > Run the sample app to connect to TiDB > Step 2: Install dependencies | Connect to TiDB with mysql2 in AWS Lambda Function > Run the sample app to connect to TiDB > Step 3: Configure connection information | Connect to TiDB with mysql2 in AWS Lambda Function > Run the sample app to connect to TiDB > Step 4: Run the code and check the result`
- Source Line Ranges: `51-166`
- Source Scope: `developer`
- Primary Component: `shared`
- Related Components: `cloud`, `tidb`
- Topic Tags: `sample-app`, `clone`, `npm-install`, `connection-string`, `env-json`, `tls`, `sam-local`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0063_e4fd7a8537`
- Source ID: `tidb-docs-8.1:develop/dev-guide-sample-application-aws-lambda.md#run-the-sample-app-to-connect-to-tidb`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c4575674ab090f7015c9eee2a609b0b14c76b05c1f644f4bb30c71e7dbc6cf45`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-sample-application-aws-lambda#run-the-sample-app-to-connect-to-tidb
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-sample-application-aws-lambda.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact steps to clone the tidb-aws-lambda-quickstart sample, configure env.json, and verify a TiDB connection locally with sam local invoke.
- Retrieval Keywords: Run the sample app to connect to TiDB, tidb-samples/tidb-aws-lambda-quickstart, git clone git@github.com:tidb-samples/tidb-aws-lambda-quickstart.git, npm install, env.json, TIDB_HOST, TIDB_PORT, TIDB_USER, TIDB_PASSWORD, Connection Type Public, Branch main, Connect With General, Node.js uses the built-in Mozilla CA certificate, sam local invoke --env-vars env.json -e events/event.json "tidbHelloWorldFunction", {"statusCode":200, Hello World
- Follow-up Guidance: After confirming the successful output, the next section covers how to deploy the AWS Lambda Function.
- Classification Note: This is operational content because it provides the step-by-step procedure to run the sample application and confirm the TiDB connection result.

## Official Source Content

## Run the sample app to connect to TiDB

This section demonstrates how to run the sample application code and connect to TiDB.

> **Note**
>
> For complete code snippets and running instructions, refer to the [tidb-samples/tidb-aws-lambda-quickstart](https://github.com/tidb-samples/tidb-aws-lambda-quickstart) GitHub repository.
### Step 1: Clone the sample app repository

Run the following commands in your terminal window to clone the sample code repository:

```bash
git clone git@github.com:tidb-samples/tidb-aws-lambda-quickstart.git
cd tidb-aws-lambda-quickstart
```
### Step 2: Install dependencies

Run the following command to install the required packages (including `mysql2`) for the sample app:

```bash
npm install
```
### Step 3: Configure connection information

Connect to your TiDB cluster depending on the TiDB deployment option you've selected.

<div label="{{{ .starter }}} or Essential">

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

    - **Connection Type** is set to `Public`
    - **Branch** is set to `main`
    - **Connect With** is set to `General`
    - **Operating System** matches your environment.

    > **Note**
    >
    > In Node.js applications, you don't have to provide an SSL CA certificate, because Node.js uses the built-in [Mozilla CA certificate](https://wiki.mozilla.org/CA/Included_Certificates) by default when establishing the TLS (SSL) connection.

4. Click **Generate Password** to create a random password.

    > **Tip**
    >
    > If you have generated a password before, you can either use the original password or click **Reset Password** to generate a new one.

5. Copy and paste the corresponding connection string into `env.json`. The following is an example:

    ```json
    {
      "Parameters": {
        "TIDB_HOST": "{gateway-region}.aws.tidbcloud.com",
        "TIDB_PORT": "4000",
        "TIDB_USER": "{prefix}.root",
        "TIDB_PASSWORD": "{password}"
      }
    }
    ```

    Replace the placeholders in `{}` with the values obtained in the connection dialog.

</div>

<div label="TiDB Self-Managed">

Copy and paste the corresponding connection string into `env.json`. The following is an example:

```json
{
  "Parameters": {
    "TIDB_HOST": "{tidb_server_host}",
    "TIDB_PORT": "4000",
    "TIDB_USER": "root",
    "TIDB_PASSWORD": "{password}"
  }
}
```

Replace the placeholders in `{}` with the values obtained in the **Connect** window.

</div>
### Step 4: Run the code and check the result

1. (Prerequisite) Install the [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html).

2. Build the bundle:

    ```bash
    npm run build
    ```

3. Invoke the sample Lambda function:

    ```bash
    sam local invoke --env-vars env.json -e events/event.json "tidbHelloWorldFunction"
    ```

4. Check the output in the terminal. If the output is similar to the following, the connection is successful:

    ```bash
    {"statusCode":200,"body":"{\"results\":[{\"Hello World\":\"Hello World\"}]}"}
    ```

After you confirm that the connection is successful, you can follow the [next section](#deploy-the-aws-lambda-function) to deploy the AWS Lambda Function.
