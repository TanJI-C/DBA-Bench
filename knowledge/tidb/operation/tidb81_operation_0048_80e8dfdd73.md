# Bookshop schema and sample data import methods

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/develop/dev-guide-bookshop-schema-design.md`
- Source Title: `Bookshop Example Application`
- Source Heading Path: `Bookshop Example Application | Bookshop Example Application > Import table structures and data | Bookshop Example Application > Import table structures and data > Method 1: Via `tiup demo` | Bookshop Example Application > Import table structures and data > Method 1: Via `tiup demo` > Configure connection information | Bookshop Example Application > Import table structures and data > Method 1: Via `tiup demo` > Set the data volume | Bookshop Example Application > Import table structures and data > Method 2: Via TiDB Cloud Import | Bookshop Example Application > Import table structures and data > View data import status`
- Source Line Ranges: `5-156`
- Source Scope: `developer`
- Primary Component: `shared`
- Related Components: `tiup`, `cloud`, `sql`
- Topic Tags: `sample-data`, `import`, `tiup-demo`, `tidb-cloud-import`, `connection-parameters`, `data-volume`, `verification`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0048_80e8dfdd73`
- Source ID: `tidb-docs-8.1:develop/dev-guide-bookshop-schema-design.md#bookshop-example-application`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e1e3950e28febe7525b508e0f6d3864b7766dad5b8f4e061af36ccfef7761290`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/develop/dev-guide-bookshop-schema-design#bookshop-example-application
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/develop/dev-guide-bookshop-schema-design.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the official Bookshop sample data import methods, connection parameters for `tiup demo bookshop prepare`, TiDB Cloud import settings, or the SQL used to verify imported table row counts and sizes.
- Retrieval Keywords: tiup demo bookshop prepare, --password, --host, --port, --db, --user, --users, --authors, --books, --orders, --ratings, --drop-tables, tiup demo bookshop --help, TiDB Cloud Import, Import data from Cloud Storage, Amazon S3, Included Schema Files, Data Format SQL, s3://developer.pingcap.com/bookshop/, arn:aws:iam::494090988690:role/s3-tidb-cloud-developer-access, information_schema.TABLES, table_rows, data_length, index_length, bookshop import status
- Follow-up Guidance: After the import is completed, the source provides a `SELECT` query against `information_schema.TABLES` to view each `bookshop` table's row count, data size, index size, and total size.
- Classification Note: The chunk is classified as an operation because it provides procedures and commands for importing Bookshop table structures and data and for checking import results.

## Official Source Content

# Bookshop Example Application

Bookshop is a virtual online bookstore application through which you can buy books of various categories and rate the books you have read.

To make your reading on the application developer guide more smoothly, we present the example SQL statements based on the [table structures](#description-of-the-tables) and data of the Bookshop application. This document focuses on the methods of importing the table structures and data as well as the definitions of the table structures.
## Import table structures and data

You can import Bookshop table structures and data either [via TiUP](#method-1-via-tiup-demo) or [via the import feature of TiDB Cloud](#method-2-via-tidb-cloud-import).

For TiDB Cloud, you can skip [Method 1: Via `tiup demo`](#method-1-via-tiup-demo) and import Bookshop table structures [via the import feature of TiDB Cloud](#method-2-via-tidb-cloud-import).
### Method 1: Via `tiup demo`

If your TiDB cluster is deployed using [TiUP](https://docs.pingcap.com/tidb/stable/tiup/tiup-reference#tiup-reference) or you can connect to your TiDB server, you can quickly generate and import sample data for the Bookshop application by running the following command:

If your TiDB cluster is deployed using [TiUP](https://docs.pingcap.com/tidb/stable/tiup-reference) or you can connect to your TiDB server, you can quickly generate and import sample data for the Bookshop application by running the following command:

```shell
tiup demo bookshop prepare
```

By default, this command enables your application to connect to port `4000` on address `127.0.0.1`, enables you to log in as the `root` user without a password, and creates a [table structure](#description-of-the-tables) in the database named `bookshop`.
#### Configure connection information

The following table lists the connection parameters. You can change their default settings to match your environment.

| Parameter    | Abbreviation | Default value      | Description           |
| ------------ | ---- | ----------- | -------------- |
| `--password` | `-p` | None        | Database user password |
| `--host`     | `-H` | `127.0.0.1` | Database address     |
| `--port`     | `-P` | `4000`      | Database port     |
| `--db`       | `-D` | `bookshop`  | Database name     |
| `--user`     | `-U` | `root`      | Database user     |

For example, if you want to connect to a database on TiDB Cloud, you can specify the connection information as follows:

```shell
tiup demo bookshop prepare -U <username> -H <endpoint> -P 4000 -p <password>
```
#### Set the data volume

You can specify the volume of data to be generated in each database table by configuring the following parameters:

| Parameter        | Default value   | Description                              |
| ----------- | -------- | --------------------------------- |
| `--users`   | `10000`  | The number of rows of data to be generated in the `users` table   |
| `--authors` | `20000`  | The number of rows to be generated in the `authors` table |
| `--books`   | `20000`  | The number of rows of data to be generated in the `books` table   |
| `--orders`  | `300000` | The number of rows of data to be generated in the `orders` table  |
| `--ratings` | `300000` | The number of rows of data to be generated in the `ratings` table |

For example, the following command is executed to generate:

- 200,000 rows of user information via the `--users` parameter
- 500,000 rows of book information via the `--books` parameter
- 100,000 rows of author information via the `--authors` parameter
- 1,000,000 rows of rating records via the `--ratings` parameter
- 1,000,000 rows of order records via the `--orders` parameter

```shell
tiup demo bookshop prepare --users=200000 --books=500000 --authors=100000 --ratings=1000000 --orders=1000000 --drop-tables
```

You can delete the original table structure through the `--drop-tables` parameter. For more parameter descriptions, run the `tiup demo bookshop --help` command.
### Method 2: Via TiDB Cloud Import

1. Open the **Import** page for your target cluster.

    1. Log in to the [TiDB Cloud console](https://tidbcloud.com/) and navigate to the [**Clusters**](https://tidbcloud.com/project/clusters) page of your project.

        > **Tip:**
        >
        > You can use the combo box in the upper-left corner to switch between organizations, projects, and clusters.

    2. Click the name of your target cluster to go to its overview page, and then click **Import** in the left navigation pane.

2. Select **Import data from Cloud Storage**, and then click **Amazon S3**.

3. On the **Import Data from Amazon S3** page, configure the following source data information:

    - **Import File Count**: for {{{ .starter }}}, select **Multiple files**. This field is not available in TiDB Cloud Dedicated.
    - **Included Schema Files**: select **Yes**.
    - **Data Format**: select **SQL**.
    - **Folder URI**: enter `s3://developer.pingcap.com/bookshop/`.
    - **Bucket Access**: select **AWS Role ARN**.
    - **Role ARN**: enter `arn:aws:iam::494090988690:role/s3-tidb-cloud-developer-access`.

    In this example, the following data is generated in advance:

    - 200,000 rows of user information
    - 500,000 rows of book information
    - 100,000 rows of author information
    - 1,000,000 rows of rating records
    - 1,000,000 rows of order records

4. Click **Connect** > **Start Import** to start the import process and wait for TiDB Cloud to complete the import.

For more information about how to import or migrate data to TiDB Cloud, see [TiDB Cloud Migration Overview](https://docs.pingcap.com/tidbcloud/tidb-cloud-migration-overview).
### View data import status

After the import is completed, you can view the data volume information of each table by executing the following SQL statement:

```sql
SELECT
    CONCAT(table_schema,'.',table_name) AS 'Table Name',
    table_rows AS 'Number of Rows',
    CONCAT(ROUND(data_length/(1024*1024*1024),4),'G') AS 'Data Size',
    CONCAT(ROUND(index_length/(1024*1024*1024),4),'G') AS 'Index Size',
    CONCAT(ROUND((data_length+index_length)/(1024*1024*1024),4),'G') AS 'Total'
FROM
    information_schema.TABLES
WHERE table_schema LIKE 'bookshop';
```

The result is as follows:

```
+-----------------------+----------------+-----------+------------+---------+
| Table Name            | Number of Rows | Data Size | Index Size | Total   |
+-----------------------+----------------+-----------+------------+---------+
| bookshop.orders       |        1000000 | 0.0373G   | 0.0075G    | 0.0447G |
| bookshop.book_authors |        1000000 | 0.0149G   | 0.0149G    | 0.0298G |
| bookshop.ratings      |        4000000 | 0.1192G   | 0.1192G    | 0.2384G |
| bookshop.authors      |         100000 | 0.0043G   | 0.0000G    | 0.0043G |
| bookshop.users        |         195348 | 0.0048G   | 0.0021G    | 0.0069G |
| bookshop.books        |        1000000 | 0.0546G   | 0.0000G    | 0.0546G |
+-----------------------+----------------+-----------+------------+---------+
6 rows in set (0.03 sec)
```
