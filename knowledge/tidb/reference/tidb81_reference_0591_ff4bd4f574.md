# EXPLAIN tidb_json example output

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/sql-statements/sql-statement-explain.md`
- Source Title: `EXPLAIN | TiDB SQL Statement Reference`
- Source Heading Path: ``EXPLAIN` > Examples`
- Source Line Ranges: `300-339`
- Source Scope: `developer`
- Primary Component: `sql`
- Related Components: `tidb`, `tikv`
- Topic Tags: `explain`, `execution-plan`, `tidb_json`, `output-format`, `operators`, `examples`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0591_ff4bd4f574`
- Source ID: `tidb-docs-8.1:sql-statements/sql-statement-explain.md#examples`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `18afbe42e01fe190b3ef25d464606b4a056efe60aff1c592f3ec5c6d9f14d7be`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/sql-statements/sql-statement-explain#examples
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/sql-statements/sql-statement-explain.md

## Retrieval Guidance

- Use When: Use this when the user needs the meaning of fields in `EXPLAIN FORMAT=tidb_json` output or wants to understand the nested operator structure in a `TiDB_JSON` example.
- Retrieval Keywords: EXPLAIN FORMAT=tidb_json, TiDB_JSON, id, estRows, taskType, accessObject, operatorInfo, subOperators, Projection_4, IndexReader_6, IndexRangeScan_5, cop[tikv], table:t, index:a(a), range:[1,1], keep order:false, stats:pseudo
- Follow-up Guidance: The source states that `id`, `estRows`, `taskType`, `accessObject`, and `operatorInfo` have the same meaning as the columns in the default format, and that missing fields mean the field is empty.
- Classification Note: This is reference content because it defines the fields and structure of `EXPLAIN` `tidb_json` example output, including parent and sub-node meanings.

## Official Source Content

```
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| TiDB_JSON                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| [
    {
        "id": "Projection_4",
        "estRows": "10.00",
        "taskType": "root",
        "operatorInfo": "test.t.id",
        "subOperators": [
            {
                "id": "IndexReader_6",
                "estRows": "10.00",
                "taskType": "root",
                "operatorInfo": "index:IndexRangeScan_5",
                "subOperators": [
                    {
                        "id": "IndexRangeScan_5",
                        "estRows": "10.00",
                        "taskType": "cop[tikv]",
                        "accessObject": "table:t, index:a(a)",
                        "operatorInfo": "range:[1,1], keep order:false, stats:pseudo"
                    }
                ]
            }
        ]
    }
]
 |
+------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
1 row in set (0.01 sec)
```
In the output, `id`, `estRows`, `taskType`, `accessObject`, and `operatorInfo` have the same meaning as the columns in the default format. `subOperators` is an array that stores the sub-nodes. The fields and meanings of the sub-nodes are the same as the parent node. If a field is missing, it means that the field is empty.

</div>
