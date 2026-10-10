# Full shard migration to TiDB Cloud via S3 and Dumpling

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/migrate-sql-shards.md`
- Source Title: `Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud`
- Source Heading Path: `Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Perform full data migration from MySQL to TiDB Cloud | Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Perform full data migration from MySQL to TiDB Cloud > Step 1. Create directories in the Amazon S3 bucket | Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Perform full data migration from MySQL to TiDB Cloud > Step 2. Use Dumpling to export data to Amazon S3 | Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Perform full data migration from MySQL to TiDB Cloud > Step 3. Create schemas in TiDB Cloud cluster | Migrate and Merge MySQL Shards of Large Datasets to TiDB Cloud > Perform full data migration from MySQL to TiDB Cloud > Step 4. Configure Amazon S3 access`
- Source Line Ranges: `51-173`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `dumpling`, `tidb`, `shared`
- Topic Tags: `full-migration`, `s3-layout`, `csv-export`, `schema-creation`, `auto-increment-conflict`, `s3-access`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0102_03390b36d3`
- Source ID: `tidb-docs-8.1:tidb-cloud/migrate-sql-shards.md#perform-full-data-migration-from-mysql-to-tidb-cloud`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `462d5dcd17d5bf738dcc4a17cf960759999cbc53fef5398c65f3729d6bd3ea7f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/migrate-sql-shards#perform-full-data-migration-from-mysql-to-tidb-cloud
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/migrate-sql-shards.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the documented full migration procedure for exporting sharded MySQL tables to Amazon S3 with Dumpling and preparing a TiDB Cloud target schema for merge import.
- Retrieval Keywords: Perform full data migration from MySQL to TiDB Cloud, Dumpling, Amazon S3, CSV, --filetype csv, --no-schemas, -t option, Option list of Dumpling, s3://dumpling-s3/store/sales/instance01/, s3://dumpling-s3/store/sales/instance02/, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, --s3.region, CREATE DATABASE store, CREATE TABLE sales, INDEX (`id`), UNIQUE KEY `ind_uid` (`uid`), auto-increment primary keys, Mapping Settings, Configure Amazon S3 access, role ARN, s3:GetObject, s3:ListBucket
- Follow-up Guidance: If you cannot update the CSV filenames according to the naming rules, you can keep the filenames unchanged and use the Mapping Settings in Step 5 to import your source data to a single target table.
- Classification Note: This is classified as a data pipeline topic because the content gives step-by-step export, file layout, schema creation, and S3 access details for full shard migration into TiDB Cloud.

## Official Source Content

## Perform full data migration from MySQL to TiDB Cloud

The following is the procedure to migrate and merge full data of MySQL shards to TiDB Cloud.

In the following example, you only need to export the data in tables to **CSV** format.
### Step 1. Create directories in the Amazon S3 bucket

Create a first-level directory `store` (corresponding to the level of databases) and a second-level directory `sales` (corresponding to the level of tables) in the Amazon S3 bucket. In `sales`, create a third-level directory for each MySQL instance (corresponding to the level of MySQL instances). For example:

- Migrate the data in MySQL instance1 to `s3://dumpling-s3/store/sales/instance01/`
- Migrate the data in MySQL instance2 to `s3://dumpling-s3/store/sales/instance02/`

If there are shards across multiple instances, you can create one first-level directory for each database and create one second-level directory for each sharded table. Then create a third-level directory for each MySQL instance for easy management. For example, if you want to migrate and merge tables `stock_N.product_N` from MySQL instance1 and MySQL instance2 into the table `stock.products` in TiDB Cloud, you can create the following directories:

- `s3://dumpling-s3/stock/products/instance01/`
- `s3://dumpling-s3/stock/products/instance02/`
### Step 2. Use Dumpling to export data to Amazon S3

For information about how to install Dumpling, see [Dumpling Introduction](https://docs.pingcap.com/tidb/stable/dumpling-overview).

When you use Dumpling to export data to Amazon S3, note the following:

- Enable binlog for upstream clusters.
- Choose the correct Amazon S3 directory and region.
- Choose the appropriate concurrency by configuring the `-t` option to minimize the impact on the upstream cluster, or export directly from the backup database. For more information about how to use this parameter, see [Option list of Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#option-list-of-dumpling).
- Set appropriate values for `--filetype csv` and `--no-schemas`. For more information about how to use these parameters, see [Option list of Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#option-list-of-dumpling).

Name the CSV files as follows:

- If the data of one table is separated into multiple CSV files, append a numeric suffix to these CSV files. For example, `${db_name}.${table_name}.000001.csv` and `${db_name}.${table_name}.000002.csv`. The numeric suffixes can be inconsecutive but must be in ascending order. You also need to add extra zeros before the number to ensure all the suffixes are in the same length.

> **Note:**
>
> If you cannot update the CSV filenames according to the preceding rules in some cases (for example, the CSV file links are also used by your other programs), you can keep the filenames unchanged and use the **Mapping Settings** in [Step 5](#step-5-perform-the-data-import-task) to import your source data to a single target table.

To export data to Amazon S3, do the following:

1. Get the `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` of the Amazon S3 bucket.

    ```shell
    [root@localhost ~]# export AWS_ACCESS_KEY_ID={your_aws_access_key_id}
    [root@localhost ~]# export AWS_SECRET_ACCESS_KEY= {your_aws_secret_access_key}
    ```

2. Export data from MySQL instance1 to the `s3://dumpling-s3/store/sales/instance01/` directory in the Amazon S3 bucket.

    ```shell
    [root@localhost ~]# tiup dumpling -u {username} -p {password} -P {port} -h {mysql01-ip} -B store_01,store_02 -r 20000 --filetype csv --no-schemas -o "s3://dumpling-s3/store/sales/instance01/" --s3.region "ap-northeast-1"
    ```

    For more information about the parameters, see [Option list of Dumpling](https://docs.pingcap.com/tidb/stable/dumpling-overview#option-list-of-dumpling).

3. Export data from MySQL instance2 to the `s3://dumpling-s3/store/sales/instance02/` directory in the Amazon S3 bucket.

    ```shell
    [root@localhost ~]# tiup dumpling -u {username} -p {password} -P {port} -h {mysql02-ip} -B store_01,store_02 -r 20000 --filetype csv --no-schemas -o "s3://dumpling-s3/store/sales/instance02/" --s3.region "ap-northeast-1"
    ```

For detailed steps, see [Export data to Amazon S3 cloud storage](https://docs.pingcap.com/tidb/stable/dumpling-overview#export-data-to-amazon-s3-cloud-storage).
### Step 3. Create schemas in TiDB Cloud cluster

Create schemas in the TiDB Cloud cluster as follows:

```sql
mysql> CREATE DATABASE store;
Query OK, 0 rows affected (0.16 sec)
mysql> use store;
Database changed
```

In this example, the column IDs of the upstream tables `sale_01` and `sale_02` are auto-increment primary keys. Conflicts might occur when you merge sharded tables in the downstream database. Execute the following SQL statement to set the ID column as a normal index instead of a primary key:

```sql
mysql> CREATE TABLE `sales` (
         `id` bigint(20) NOT NULL ,
         `uid` varchar(40) NOT NULL,
         `sale_num` bigint DEFAULT NULL,
         INDEX (`id`),
         UNIQUE KEY `ind_uid` (`uid`)
        );
Query OK, 0 rows affected (0.17 sec)
```

For more information about the solutions to solve such conflicts, see [Remove the PRIMARY KEY attribute from the column](https://docs.pingcap.com/tidb/stable/shard-merge-best-practices#remove-the-primary-key-attribute-from-the-column).
### Step 4. Configure Amazon S3 access

Follow the instructions in [Configure Amazon S3 access](https://docs.pingcap.com/tidb/stable/tidb-cloud/dedicated-external-storage#configure-amazon-s3-access) to get the role ARN to access the source data.

The following example only lists key policy configurations. Replace the Amazon S3 path with your own values.

```yaml
{
   "Version": "2012-10-17",
   "Statement": [
       {
           "Sid": "VisualEditor0",
           "Effect": "Allow",
           "Action": [
               "s3:GetObject",
               "s3:GetObjectVersion"
           ],
           "Resource": [
               "arn:aws:s3:::dumpling-s3/*"
           ]
       },
       {
           "Sid": "VisualEditor1",
           "Effect": "Allow",
           "Action": [
               "s3:ListBucket",
               "s3:GetBucketLocation"
           ],

           "Resource": "arn:aws:s3:::dumpling-s3"
       }
   ]
}
```
