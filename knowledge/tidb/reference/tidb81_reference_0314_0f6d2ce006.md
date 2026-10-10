# JSONPath syntax and selection examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/functions-and-operators/json-functions.md`
- Source Title: `JSON Functions`
- Source Heading Path: `JSON Functions > JSONPath`
- Source Line Ranges: `72-137`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`
- Topic Tags: `jsonpath`, `json_extract`, `member-selection`, `array-selection`, `wildcard`, `path-wildcard`, `range-selection`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0314_0f6d2ce006`
- Source ID: `tidb-docs-8.1:functions-and-operators/json-functions.md#jsonpath`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `e64dcb081d202d4fafdaa5c7740362d963e6cdcddeb2a955989eade92a90b8c5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions#jsonpath
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/functions-and-operators/json-functions.md

## Retrieval Guidance

- Use When: Use this chunk when you need the JSONPath symbols and example paths used by JSON functions such as JSON_EXTRACT() to select members, arrays, wildcards, path wildcards, or array ranges in a JSON document.
- Retrieval Keywords: JSONPath, JSON_EXTRACT(), $, member selection, ., array selection, [], wildcard, *, path wildcard, **, array range selection, [<n> to <n>], $.database.name, $.database.features[0], $.database.versions[*].release_date, $**.version, $.database.features[0 to 2]
- Follow-up Guidance: It also points to the JSON_EXTRACT() reference and the IETF draft for JSONPath for more information.
- Classification Note: This is reference content because it defines JSONPath syntax elements and gives exact selection examples with their returned values.

## Official Source Content

## JSONPath

Many of JSON functions use [JSONPath](https://www.rfc-editor.org/rfc/rfc9535.html) to select parts of a JSON document.

| Symbol         | Description                  |
| -------------- | ---------------------------- |
| `$`            | Document root                |
| `.`            | Member selection             |
| `[]`           | Array selection              |
| `*`            | Wildcard                     |
| `**`           | Path wildcard                |
| `[<n> to <n>]` | Array range selection        |

The subsequent content takes the following JSON document as an example to demonstrate how to use JSONPath:

```json
{
    "database": {
        "name": "TiDB",
        "features": [
            "distributed",
            "scalable",
            "relational",
            "cloud native"
        ],
        "license": "Apache-2.0 license",
        "versions": [
            {
                "version": "v8.1.2",
                "type": "lts",
                "release_date": "2024-12-26" 
            },
            {
                "version": "v8.0.0",        
                "type": "dmr",
                "release_date": "2024-03-29"
            }
        ]
    },
    "migration_tool": {
        "name": "TiDB Data Migration",
        "features": [
            "MySQL compatible",            
            "Shard merging"
        ],
        "license": "Apache-2.0 license"
    }
}
```

| JSONPath                              | Description                             | Example with [`JSON_EXTRACT()`](https://docs.pingcap.com/tidb/stable/functions-and-operators/json-functions/json-functions-search#json_extract) | 
|-------------------------------------- |-----------------------------------------|-------------------------------|
| `$`                                   | The root of the document                | Returns the full document                              |
| `$.database`                          | The `database` object                  |  Returns the full structure starting with `"database"`. It does not include `"migration_tool"` and the structure below that.                             |
| `$.database.name`                     | The name of the database.               | `"TiDB"`                      |
| `$.database.features`                 | All database features                   | `["distributed", "scalable", "relational", "cloud native"]`                              |
| `$.database.features[0]`              | The first database feature.             | `"distributed"`               |
| `$.database.features[2]`              | The third database feature.             | `"relational"`                |
| `$.database.versions[0].type`         | The type of the first database version. | `"lts"`                       |
| `$.database.versions[*].release_date` | The release date for all versions.      | `["2024-12-26","2024-03-29"]` |
| `$.*.features`                        | Two array's of features                 | `[["distributed", "scalable", "relational", "cloud native"], ["MySQL compatible", "Shard merging"]]`                              |
| `$**.version`                         | All versions, with path wildcard        | `["v8.1.2","v8.0.0"]`         |
| `$.database.features[0 to 2]`         | Range of database features from the first to the third.             | `["scalable","relational"]`   |

For more information, see [the IETF draft for JSONPath](https://www.ietf.org/archive/id/draft-goessner-dispatch-jsonpath-00.html).
