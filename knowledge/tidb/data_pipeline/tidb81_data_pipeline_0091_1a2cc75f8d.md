# Import data into TiDB Cloud Dedicated with MySQL CLI

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/import-with-mysql-cli.md`
- Source Title: `Import Data into TiDB Cloud Dedicated via MySQL CLI`
- Source Heading Path: `Import Data into TiDB Cloud Dedicated via MySQL CLI | Import Data into TiDB Cloud Dedicated via MySQL CLI > Prerequisites | Import Data into TiDB Cloud Dedicated via MySQL CLI > Step 1. Connect to your TiDB Cloud Dedicated cluster | Import Data into TiDB Cloud Dedicated via MySQL CLI > Step 2. Define the table and insert sample data | Import Data into TiDB Cloud Dedicated via MySQL CLI > Step 3. Import data from a SQL or CSV file`
- Source Line Ranges: `5-107`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `sql`, `tidb`
- Topic Tags: `mysql-cli`, `data-import`, `sql-file`, `csv-file`, `connection`, `networking`, `ip-access-list`, `load-data`, `sample-data`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0091_1a2cc75f8d`
- Source ID: `tidb-docs-8.1:tidb-cloud/import-with-mysql-cli.md#import-data-into-tidb-cloud-dedicated-via-mysql-cli`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2db8bdf06e23382f96c46fc12d7aa065d52eee312a6393a1353ce829dfb7add5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/import-with-mysql-cli#import-data-into-tidb-cloud-dedicated-via-mysql-cli
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/import-with-mysql-cli.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the documented steps and example commands to import SQL or CSV data into a TiDB Cloud Dedicated cluster with MySQL CLI, including connection setup and `LOAD DATA LOCAL INFILE` usage.
- Retrieval Keywords: TiDB Cloud Dedicated, MySQL Command-Line Client, mysql CLI, import data, SQL file, CSV file, IP Access List, Allow access from anywhere, Connect, Settings > Networking, product_data.sql, product_data.csv, CREATE TABLE products, INSERT INTO products, mysql --comments --connect-timeout 150, --ssl-mode=VERIFY_IDENTITY, --ssl-ca, LOAD DATA LOCAL INFILE, FIELDS TERMINATED BY ',', LINES TERMINATED BY '\n', IGNORE 1 LINES, database name test
- Follow-up Guidance: The source also points to `Connect to TiDB Cloud Dedicated via Public Connection` for obtaining the connection string and to `LOAD DATA` for more syntax details about `LOAD DATA LOCAL INFILE`.
- Classification Note: This chunk is classified as `data_pipeline` for the `cloud` component because it documents importing data into TiDB Cloud Dedicated via MySQL CLI from SQL and CSV files.

## Official Source Content

# Import Data into TiDB Cloud Dedicated via MySQL CLI

This document describes how to import data into TiDB Cloud Dedicated via the [MySQL Command-Line Client](https://dev.mysql.com/doc/refman/8.0/en/mysql.html). You can import data from an SQL file or a CSV file. The following sections provide step-by-step instructions for importing data from each type of file.
## Prerequisites

Before you can import data via MySQL CLI to TiDB Cloud Dedicated, you need the following prerequisites:

- You have access to your TiDB Cloud Dedicated cluster. If you do not have, create one following the instructions in [Create a TiDB Cloud Dedicated cluster](https://docs.pingcap.com/tidb/stable/tidb-cloud/create-tidb-cluster).
- Install MySQL CLI on your local computer.
## Step 1. Connect to your TiDB Cloud Dedicated cluster

Connect to your TiDB cluster.

1. Navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page, and then click the name of your target cluster to go to its overview page.

2. In the left navigation pane, click **Settings** > **Networking**.

3. On the **Networking** page, click **Add IP Address** in the **IP Access List** area.

4. In the dialog, choose **Allow access from anywhere**, and then click **Confirm**.

5. In the upper-right corner, click **Connect** to open the dialog for connection information.

    For more details about how to obtain the connection string, see [Connect to TiDB Cloud Dedicated via Public Connection](https://docs.pingcap.com/tidb/stable/tidb-cloud/connect-via-standard-connection).
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

4. Make sure to replace the paths, table name (`products` in this example), `<your_username>`, `<your_host>`, `<your_password>`, `<your_csv_path>`, `<your_ca_path>`, and other placeholders with your actual information, and replace the sample CSV data with your real dataset as needed.

> **Note:**
>
> For more syntax details about `LOAD DATA LOCAL INFILE`, see [`LOAD DATA`](https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-load-data).

</div>
