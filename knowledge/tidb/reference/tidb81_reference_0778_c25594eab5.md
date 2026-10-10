# Customized development data format for Kafka binlog output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-binlog/binlog-consumer-client.md`
- Source Title: `Binlog Consumer Client User Guide`
- Source Heading Path: `Binlog Consumer Client User Guide > Customized development | Binlog Consumer Client User Guide > Customized development > Data format`
- Source Line Ranges: `25-121`
- Source Scope: `developer`
- Primary Component: `tidb`
- Related Components: `shared`
- Topic Tags: `binlog`, `kafka`, `protobuf`, `schema`, `dml`, `ddl`, `commit-ts`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0778_c25594eab5`
- Source ID: `tidb-docs-8.1:tidb-binlog/binlog-consumer-client.md#customized-development`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `66bea6d76a6b8220fb3d3b52f127ab52638a907f7a59177aa29783340bff1098`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-binlog/binlog-consumer-client#customized-development
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-binlog/binlog-consumer-client.md

## Retrieval Guidance

- Use When: Use this chunk when you need the exact protobuf schema of the binlog data that Drainer outputs to Kafka for customized development.
- Retrieval Keywords: Customized development, Data format, secondary_binlog.proto, protobuf schema, message Binlog, message DMLData, message DDLData, message TableMutation, message Column, message ColumnInfo, message Row, enum MutationType, enum BinlogType, commit_ts, ddl_query, schema_name, table_name, column_info, mysql_type, is_primary_key
- Follow-up Guidance: For the definition of the data format, the content points to `secondary_binlog.proto` in the TiDB release-8.1 source tree.
- Classification Note: This is classified as reference because it defines the exact data structures and field names used in Kafka binlog output.

## Official Source Content

## Customized development
### Data format

Firstly, you need to obtain the format information of the data which is output to Kafka by Drainer:

```
// `Column` stores the column data in the corresponding variable based on the data type.
message Column {
  // Indicates whether the data is null
  optional bool is_null = 1 [ default = false ];
  // Stores `int` data
  optional int64 int64_value = 2;
  // Stores `uint`, `enum`, and `set` data
  optional uint64 uint64_value = 3;
  // Stores `float` and `double` data
  optional double double_value = 4;
  // Stores `bit`, `blob`, `binary` and `json` data
  optional bytes bytes_value = 5;
  // Stores `date`, `time`, `decimal`, `text`, `char` data
  optional string string_value = 6;
}

// `ColumnInfo` stores the column information, including the column name, type, and whether it is the primary key.
message ColumnInfo {
  optional string name = 1 [ (gogoproto.nullable) = false ];
  // the lower case column field type in MySQL
  // https://dev.mysql.com/doc/refman/8.0/en/data-types.html
  // for the `numeric` type: int bigint smallint tinyint float double decimal bit
  // for the `string` type: text longtext mediumtext char tinytext varchar
  // blob longblob mediumblob binary tinyblob varbinary
  // enum set
  // for the `json` type: json
  optional string mysql_type = 2 [ (gogoproto.nullable) = false ];
  optional bool is_primary_key = 3 [ (gogoproto.nullable) = false ];
}

// `Row` stores the actual data of a row.
message Row { repeated Column columns = 1; }

// `MutationType` indicates the DML type.
enum MutationType {
  Insert = 0;
  Update = 1;
  Delete = 2;
}

// `Table` contains mutations in a table.
message Table {
  optional string schema_name = 1;
  optional string table_name = 2;
  repeated ColumnInfo column_info = 3;
  repeated TableMutation mutations = 4;
}

// `TableMutation` stores mutations of a row.
message TableMutation {
  required MutationType type = 1;
  // data after modification
  required Row row = 2;
  // data before modification. It only takes effect for `Update MutationType`.
  optional Row change_row = 3;
}

// `DMLData` stores all the mutations caused by DML in a transaction.
message DMLData {
  // `tables` contains all the table changes in the transaction.
  repeated Table tables = 1;
}

// `DDLData` stores the DDL information.
message DDLData {
  // the database used currently
  optional string schema_name = 1;
  // the relates table
  optional string table_name = 2;
  // `ddl_query` is the original DDL statement query.
  optional bytes ddl_query = 3;
}

// `BinlogType` indicates the binlog type, including DML and DDL.
enum BinlogType {
  DML = 0; //  Has `dml_data`
  DDL = 1; //  Has `ddl_query`
}

// `Binlog` stores all the changes in a transaction. Kafka stores the serialized result of the structure data.
message Binlog {
  optional BinlogType type = 1 [ (gogoproto.nullable) = false ];
  optional int64 commit_ts = 2 [ (gogoproto.nullable) = false ];
  optional DMLData dml_data = 3;
  optional DDLData ddl_data = 4;
}
```

For the definition of the data format, see [`secondary_binlog.proto`](https://github.com/pingcap/tidb/blob/release-8.1/pkg/tidb-binlog/proto/proto/secondary_binlog.proto)
