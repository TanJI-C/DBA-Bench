# Import data into TiDB Cloud Serverless with MySQL CLI

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-with-mysql-cli-serverless.md`
- Source Title: `Import Data into TiDB Cloud Serverless via MySQL CLI`
- Source Heading Path: `Import Data into TiDB Cloud Serverless via MySQL CLI | Import Data into TiDB Cloud Serverless via MySQL CLI > Prerequisites | Import Data into TiDB Cloud Serverless via MySQL CLI > Step 1. Connect to your TiDB Cloud Serverless cluster | Import Data into TiDB Cloud Serverless via MySQL CLI > Step 2. Define the table and insert sample data | Import Data into TiDB Cloud Serverless via MySQL CLI > Step 3. Import data from a SQL or CSV file`
- Source Line Ranges: `5-111`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `shared`
- Topic Tags: `data-import`, `mysql-cli`, `serverless`, `sql-file`, `csv-file`, `load-data`, `connection`, `prerequisites`, `sample-data`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0090_33d4e35776`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-with-mysql-cli-serverless.md#import-data-into-tidb-cloud-serverless-via-mysql-cli`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c7255f07674c0762a6e63c3a94c890695177f0975d058bc7d233959e9fde4735`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-with-mysql-cli-serverless#import-data-into-tidb-cloud-serverless-via-mysql-cli
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-with-mysql-cli-serverless.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the documented MySQL CLI procedure to import an SQL file or a CSV file into a TiDB Cloud Serverless cluster, including connection prerequisites and example commands.
- Retrieval Keywords: TiDB Cloud Serverless, MySQL Command-Line Client, MySQL CLI, import data, SQL file, CSV file, LOAD DATA LOCAL INFILE, product_data.sql, product_data.csv, CREATE TABLE products, INSERT INTO products, mysql --comments --connect-timeout 150, --ssl-mode=VERIFY_IDENTITY, --ssl-ca, -P 4000, test database, Connection Type Public, Connect With MySQL CLI, Generate Password, Reset Password
- Follow-up Guidance: The source also includes example SQL and CSV content, the `mysql` command for importing an SQL file, and a `LOAD DATA LOCAL INFILE` example for importing CSV data into the `products` table.
- Classification Note: This is classified as a cloud data_pipeline topic because the official content describes importing data into a TiDB Cloud Serverless cluster through MySQL CLI using SQL statements and `LOAD DATA LOCAL INFILE`.

## Official Source Content

# Import Data into TiDB Cloud Serverless via MySQL CLI

This document describes how to import data into TiDB Cloud Serverless via the [MySQL Command-Line Client](https://dev.mysql.com/doc/refman/8.0/en/mysql.html). You can import data from an SQL file or a CSV file. The following sections provide step-by-step instructions for importing data from each type of file.
## Prerequisites

Before you can import data via MySQL CLI to TiDB Cloud Serverless, you need the following prerequisites:

- You have access to your TiDB Cloud Serverless cluster. If you do not have, create one following the instructions in [Build a TiDB Cloud Serverless Cluster](https://docs.pingcap.com/tidb/stable/develop/dev-guide-build-cluster-in-cloud).
- Install MySQL CLI on your local computer.
## Step 1. Connect to your TiDB Cloud Serverless cluster

Connect to your TiDB cluster.

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. Click **Connect** in the upper-right corner. A connection dialog is displayed.

3. Ensure the configurations in the connection dialog match your operating environment.

    - **Connection Type** is set to `Public`.
    - **Connect With** is set to `MySQL CLI`.
    - **Operating System** matches your environment.

4. Click **Generate Password** to create a random password.

    > **Tip:**
    >
    > If you have created a password before, either use the original password or click **Reset Password** to generate a new one.
## Step 2. Define the table and insert sample data

Before importing data, you need to prepare the table structure and insert real sample data into it. The following is an example SQL file (`product_data.sql`) that you can use to create a table and insert sample data:

```sql
-- Create a table in your TiDB database
CREATE TABLE products (
    product_id INT PRIMARY KEY,
    product_name VARCHAR(255),
    price DECIMAL(10, 2)
);

-- Insert sample data into the table
INSERT INTO products (product_id, product_name, price) VALUES
    (1, 'Laptop', 999.99),
    (2, 'Smartphone', 499.99),
    (3, 'Tablet', 299.99);
```
## Step 3. Import data from a SQL or CSV file

You can import data from an SQL file or a CSV file. The following sections provide step-by-step instructions for importing data from each type.

<div label="From an SQL file">

Do the following to import data from an SQL file:

1. Provide a real SQL file (for example, `product_data.sql`) that contains the data you want to import. This SQL file must contain `INSERT` statements with real data.

2. Use the following command to import data from the SQL file:

    ```bash
    mysql --comments --connect-timeout 150 -u '<your_username>' -h <your_cluster_host> -P 4000 -D test --ssl-mode=VERIFY_IDENTITY --ssl-ca=<your_ca_path> -p<your_password> < product_data.sql
    ```

> **Note:**
>
> The default database name used here is `test`, and you can either manually create your own database or use the `CREATE DATABASE` command in an SQL file.

</div>
<div label="From a CSV file">

Do the following to import data from a CSV file:

1. Create a database and schema in TiDB to match your data import needs.

2. Provide a sample CSV file (for example, `product_data.csv`) that contains the data you want to import. The following is an example of a CSV file:

    **product_data.csv:**

    ```csv
    product_id,product_name,price
    4,Laptop,999.99
    5,Smartphone,499.99
    6,Tablet,299.99
    ```

3. Use the following command to import data from the CSV file:

    ```bash
    mysql --comments --connect-timeout 150 -u '<your_username>' -h <your_host> -P 4000 -D test --ssl-mode=VERIFY_IDENTITY --ssl-ca=<your_ca_path> -p<your_password> -e "LOAD DATA LOCAL INFILE '<your_csv_path>' INTO TABLE products
    FIELDS TERMINATED BY ','
    LINES TERMINATED BY '\n'
    IGNORE 1 LINES (product_id, product_name, price);"
    ```

    Make sure to replace the paths, table name (`products` in this example), `<your_username>`, `<your_host>`, `<your_password>`, `<your_csv_path>`, `<your_ca_path>`, and other placeholders with your actual information, and replace the sample CSV data with your real dataset as needed.

> **Note:**
>
> For more syntax details about `LOAD DATA LOCAL INFILE`, see [`LOAD DATA`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-data).

</div>
