# Travel agent cleanup and related vector search references

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-langchain.md`
- Source Title: `Integrate Vector Search with LangChain`
- Source Heading Path: `Integrate Vector Search with LangChain > Advanced usage example: travel agent > Clean up data | Integrate Vector Search with LangChain > See also`
- Source Line Ranges: `569-586`
- Source Scope: `cloud`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `tidb`
- Topic Tags: `cleanup`, `drop-table`, `resource-removal`, `references`, `vector-search`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0444_3f785a4ef1`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-langchain.md#clean-up-data`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `94fb6513e9284dad36124addf9280c87fb5370f7b5e4122c9d9901eea35982c4`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-langchain#clean-up-data
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-langchain.md

## Retrieval Guidance

- Use When: Use this chunk when the query asks how to remove the example travel agent table after the LangChain vector search walkthrough or asks for related vector search reference links.
- Retrieval Keywords: DROP TABLE airplan_routes, clean up data, vector_store.tidb_vector_client.execute, {'success': True, 'result': 0, 'error': None}, Vector Data Types, Vector Search Index
- Follow-up Guidance: The source also points to the related references Vector Data Types and Vector Search Index.
- Classification Note: This is classified as operation because the official content covers cleanup of created resources by dropping the airplan_routes table and includes related reference links.

## Official Source Content

### Clean up data

Finally, clean up the resources by dropping the created table:

```python
vector_store.tidb_vector_client.execute("DROP TABLE airplan_routes")
```

The expected output is as follows:

```plain
{'success': True, 'result': 0, 'error': None}
```
## See also

- [Vector Data Types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types)
- [Vector Search Index](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index)
