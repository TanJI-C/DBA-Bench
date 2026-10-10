# Import Bikeshare example data into TiDB

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/import-example-data.md`
- Source Title: `Import Example Database`
- Source Heading Path: `Import Example Database | Import Example Database > Download all data files | Import Example Database > Load data into TiDB | Import Example Database > Load data into TiDB > Import all files`
- Source Line Ranges: `5-67`
- Source Scope: `self_managed`
- Primary Component: `sql`
- Related Components: `tidb`, `shared`
- Topic Tags: `example-data`, `download`, `schema`, `load-data`, `mysql-client`, `local-infile`, `csv`, `bash`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0026_50744fb03a`
- Source ID: `tidb-docs-8.1:import-example-data.md#import-example-database`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ecab36a0be35635063cdad36bc8d3f1e231b946f9e43ea82ab252848df3e5cf2`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/import-example-data#import-example-database
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/import-example-data.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the official example for downloading Capital Bikeshare system data and importing the bikeshare CSV files into TiDB with SQL or a bash loop.
- Retrieval Keywords: Import Bikeshare example data into TiDB, Import Example Database, Capital Bikeshare system data, 2010-2017-capitalbikeshare-tripdata.zip, CREATE DATABASE bikeshare, CREATE TABLE trips, LOAD DATA LOCAL INFILE, mysql --local-infile=1, for FILE in *.csv, 2017Q1-capitalbikeshare-tripdata.csv
- Follow-up Guidance: The source also includes the exact bash commands to download and unzip the yearly tripdata files and the full `LOAD DATA LOCAL INFILE` statement for importing each CSV into the `trips` table.
- Classification Note: This is classified as data_pipeline for the sql component because the content defines the `bikeshare` schema and `trips` table, then shows `LOAD DATA LOCAL INFILE` and MySQL client commands to load example CSV data into TiDB.

## Official Source Content

# Import Example Database

Examples used in the TiDB manual use [System Data](https://www.capitalbikeshare.com/system-data) from Capital Bikeshare, released under the [Capital Bikeshare Data License Agreement](https://www.capitalbikeshare.com/data-license-agreement).
## Download all data files

The system data is available [for download in .zip files](https://s3.amazonaws.com/capitalbikeshare-data/index.html) organized per year. Downloading and extracting all files requires approximately 3GB of disk space. To download all files for years 2010-2017 using a bash script:

```bash
mkdir -p bikeshare-data && cd bikeshare-data

curl -L --remote-name-all https://s3.amazonaws.com/capitalbikeshare-data/{2010..2017}-capitalbikeshare-tripdata.zip
unzip \*-tripdata.zip
```
## Load data into TiDB

The system data can be imported into TiDB using the following schema:

```sql
CREATE DATABASE bikeshare;
USE bikeshare;

CREATE TABLE trips (
 trip_id bigint NOT NULL PRIMARY KEY AUTO_INCREMENT,
 duration integer not null,
 start_date datetime,
 end_date datetime,
 start_station_number integer,
 start_station varchar(255),
 end_station_number integer,
 end_station varchar(255),
 bike_number varchar(255),
 member_type varchar(255)
);
```

You can import files individually using the example `LOAD DATA` command here, or import all files using the bash loop below:

```sql
LOAD DATA LOCAL INFILE '2017Q1-capitalbikeshare-tripdata.csv' INTO TABLE trips
  FIELDS TERMINATED BY ',' ENCLOSED BY '"'
  LINES TERMINATED BY '\r\n'
  IGNORE 1 LINES
(duration, start_date, end_date, start_station_number, start_station,
end_station_number, end_station, bike_number, member_type);
```
### Import all files

> **Note:**
>
> When you start the MySQL client, use the `--local-infile=1` option.

To import all `*.csv` files into TiDB in a bash loop:

```bash
for FILE in *.csv; do
 echo "== $FILE =="
 mysql bikeshare --local-infile=1 -e "LOAD DATA LOCAL INFILE '${FILE}' INTO TABLE trips FIELDS TERMINATED BY ',' ENCLOSED BY '\"' LINES TERMINATED BY '\r\n' IGNORE 1 LINES (duration, start_date, end_date, start_station_number, start_station, end_station_number, end_station, bike_number, member_type);"
done;
```
