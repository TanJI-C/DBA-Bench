# Compatibility and format differences from official Canal

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/ticdc/ticdc-canal-json.md`
- Source Title: `TiCDC Canal-JSON Protocol`
- Source Heading Path: `TiCDC Canal-JSON Protocol > Comparison of TiCDC Canal-JSON and the official Canal | TiCDC Canal-JSON Protocol > Comparison of TiCDC Canal-JSON and the official Canal > Compatibility with the official Canal | TiCDC Canal-JSON Protocol > Comparison of TiCDC Canal-JSON and the official Canal > Event of `Update` Type | TiCDC Canal-JSON Protocol > Comparison of TiCDC Canal-JSON and the official Canal > `mysqlType` field | TiCDC Canal-JSON Protocol > Changes in TiCDC Canal-JSON`
- Source Line Ranges: `300-502`
- Source Scope: `self_managed`
- Primary Component: `ticdc`
- Related Components: `shared`
- Topic Tags: `canal-json`, `compatibility`, `official-canal`, `update-events`, `old-field`, `mysqltype`, `content-compatible`, `version-dependent`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0759_44a0ade2b7`
- Source ID: `tidb-docs-8.1:ticdc/ticdc-canal-json.md#comparison-of-ticdc-canal-json-and-the-official-canal`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5db3d3c059f792735716dc94be2d7106d55592192e4bf37506da0b823d5ebb6e`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/ticdc/ticdc-canal-json#comparison-of-ticdc-canal-json-and-the-official-canal
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/ticdc/ticdc-canal-json.md

## Retrieval Guidance

- Use When: Use this chunk when comparing TiCDC Canal-JSON with the official Canal format, especially the `old` field in `UPDATE` events, the `mysqlType` field, and `content-compatible=true` behavior.
- Retrieval Keywords: Comparison of TiCDC Canal-JSON and the official Canal, Compatibility with the official Canal, content-compatible=true, sink-uri, only_output_updated_columns, Event of UPDATE Type, old field contains all the column data, old field contains only the modified column data, mysqlType field, full information of the type parameter, official Canal, TiCDC Canal-JSON, decimal(10, 4), char(16), varchar(16), binary(16), varbinary(16), enum('a','b','c'), set('a','b','c'), bit(64)
- Follow-up Guidance: The chunk includes side-by-side JSON examples showing `UPDATE` event `old` contents and `mysqlType` output differences between TiCDC and the official Canal.
- Classification Note: This is reference content because it documents format differences and compatibility behavior for TiCDC Canal-JSON versus the official Canal using exact fields, options, and examples.

## Official Source Content

## Comparison of TiCDC Canal-JSON and the official Canal

The way that TiCDC implements the Canal-JSON data format, including the `Update` Event and the `mysqlType` field, differs from the official Canal. The following table shows the main differences.

| Item            | TiCDC Canal-JSON                                                                                                                             | Canal                                |
|:----------------|:---------------------------------------------------------------------------------------------------------------------------------------------|:-------------------------------------|
| Event of `Update` Type  | By default, the `old` field contains all the column data. When `only_output_updated_columns` is `true`, the `old` field contains only the modified column data.  | The `old` field contains only the modified column data    |
| `mysqlType` field  | For types with parameters, it does not contain the information of the type parameter                                                         | For types with parameters, it contains the full information of the type parameter    |
### Compatibility with the official Canal

Starting from v6.5.6, v7.1.3, and v7.6.0, TiCDC Canal-JSON supports compatibility with the data format of the official Canal. When creating a changefeed, you can set `content-compatible=true` in `sink-uri` to enable this feature. In this mode, TiCDC outputs Canal-JSON format data that is compatible with the official Canal. The specific changes are as follows:

* The `mysqlType` field contains the full information of the type parameter for each type.
* An Event of `Update` Type only outputs the modified column data.
### Event of `Update` Type

For an Event of `Update` Type:

- In TiCDC, the `old` field contains all the column data
- In the official Canal, the `old` field contains only the modified column data

Assume that the following SQL statements are executed sequentially in the upstream TiDB:

```sql
create table tp_int
(
    id          int auto_increment,
    c_tinyint   tinyint   null,
    c_smallint  smallint  null,
    c_mediumint mediumint null,
    c_int       int       null,
    c_bigint    bigint    null,
    constraint pk
        primary key (id)
);

insert into tp_int(c_tinyint, c_smallint, c_mediumint, c_int, c_bigint)
values (127, 32767, 8388607, 2147483647, 9223372036854775807);

update tp_int set c_int = 0, c_tinyint = 0 where c_smallint = 32767;
```

For the `update` statement, TiCDC outputs an Event message with `type` as `UPDATE`, as shown below. The `update` statement only modifies the `c_int` and `c_tinyint` columns. The `old` field in the output event message contains all the column data.

```json
{
    "id": 0,
    ...
    "type": "UPDATE",
    ...
    "sqlType": {
        ...
    },
    "mysqlType": {
        ...
    },
    "data": [
        {
            "c_bigint": "9223372036854775807",
            "c_int": "0",
            "c_mediumint": "8388607",
            "c_smallint": "32767",
            "c_tinyint": "0",
            "id": "2"
        }
    ],
    "old": [                              // In TiCDC, this field contains all the column data.
        {
            "c_bigint": "9223372036854775807",
            "c_int": "2147483647",        // Modified column
            "c_mediumint": "8388607",
            "c_smallint": "32767",
            "c_tinyint": "127",           // Modified column
            "id": "2"
        }
    ]
}
```

For the official Canal, the `old` field in the output event message contains only the modified column data, as shown below.

```json
{
    "id": 0,
    ...
    "type": "UPDATE",
    ...
    "sqlType": {
        ...
    },
    "mysqlType": {
        ...
    },
    "data": [
        {
            "c_bigint": "9223372036854775807",
            "c_int": "0",
            "c_mediumint": "8388607",
            "c_smallint": "32767",
            "c_tinyint": "0",
            "id": "2"
        }
    ],
    "old": [                              // In Canal, this field contains only the modified column data.
        {
            "c_int": "2147483647",        // Modified column
            "c_tinyint": "127",           // Modified column
        }
    ]
}
```
### `mysqlType` field

For the `mysqlType` field, if a type contains parameters, the official Canal contains the full information of the type parameter. TiCDC does not contain such information.

In the following example, the table-defining SQL statement contains a parameter for each column, such as the ones for `decimal`, `char`, `varchar` and `enum`. By comparing the Canal-JSON formats generated by TiCDC and the official Canal, you can see that TiCDC only contains the basic MySQL information in the `mysqlType` field. If you need the full information of the type parameter, you need to implement it by other means.

Assume that the following SQL statements are executed sequentially in the upstream TiDB:

```sql
create table t (
    id     int auto_increment,
    c_decimal    decimal(10, 4) null,
    c_char       char(16)      null,
    c_varchar    varchar(16)   null,
    c_binary     binary(16)    null,
    c_varbinary  varbinary(16) null,
    c_enum enum('a','b','c') null,
    c_set  set('a','b','c')  null,
    c_bit  bit(64)            null,
    constraint pk
        primary key (id)
);

insert into t (c_decimal, c_char, c_varchar, c_binary, c_varbinary, c_enum, c_set, c_bit)
values (123.456, "abc", "abc", "abc", "abc", 'a', 'a,b', b'1000001');
```

The output of TiCDC is as follows:

```json
{
    "id": 0,
    ...
    "isDdl": false,
    "sqlType": {
        ...
    },
    "mysqlType": {
        "c_binary": "binary",
        "c_bit": "bit",
        "c_char": "char",
        "c_decimal": "decimal",
        "c_enum": "enum",
        "c_set": "set",
        "c_varbinary": "varbinary",
        "c_varchar": "varchar",
        "id": "int"
    },
    "data": [
        {
            ...
        }
    ],
    "old": null,
}
```

The output of the official Canal is as follows:

```json
{
    "id": 0,
    ...
    "isDdl": false,
    "sqlType": {
        ...
    },
    "mysqlType": {
        "c_binary": "binary(16)",
        "c_bit": "bit(64)",
        "c_char": "char(16)",
        "c_decimal": "decimal(10, 4)",
        "c_enum": "enum('a','b','c')",
        "c_set": "set('a','b','c')",
        "c_varbinary": "varbinary(16)",
        "c_varchar": "varchar(16)",
        "id": "int"
    },
    "data": [
        {
            ...
        }
    ],
    "old": null,
}
```
## Changes in TiCDC Canal-JSON
