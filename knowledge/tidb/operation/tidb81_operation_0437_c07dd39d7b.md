# Add knowledge entries to a Chat2Query knowledge base

## Knowledge Metadata

- Knowledge Type: `operation`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/use-chat2query-knowledge.md`
- Source Title: `Use Knowledge Bases`
- Source Heading Path: `Use Knowledge Bases > Step 3. Add knowledge to the newly created knowledge base | Use Knowledge Bases > Step 3. Add knowledge to the newly created knowledge base > Add a few-shot example type of knowledge | Use Knowledge Bases > Step 3. Add knowledge to the newly created knowledge base > Add a term-sheet explanation type of knowledge | Use Knowledge Bases > Step 3. Add knowledge to the newly created knowledge base > Add an instruction type of knowledge`
- Source Line Ranges: `160-218`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`, `sql`
- Topic Tags: `chat2query`, `knowledge-base`, `data-endpoint`, `few-shot`, `term-sheet`, `instruction`, `api`, `curl`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_operation_0437_c07dd39d7b`
- Source ID: `tidb-docs-8.1:tidb-cloud/use-chat2query-knowledge.md#step-3-add-knowledge-to-the-newly-created-knowledge-base`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `94dc1f0f14db560a25f6e964574269b8a8451b4b6238d315a58da0c359ceced5`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-knowledge#step-3-add-knowledge-to-the-newly-created-knowledge-base
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/use-chat2query-knowledge.md

## Retrieval Guidance

- Use When: Use this chunk when you need the API endpoint and example payloads for adding few-shot, term-sheet, or instruction knowledge to an existing Chat2Query knowledge base.
- Retrieval Keywords: add knowledge, /v3/knowledgeBases/{knowledge_base_id}/data, knowledge_base_id, type few-shot, type term-sheet, type instruction, raw_data, meta_data, How many records are in the 'test' table?, SELECT COUNT(*) FROM `test`;, OSS, LAG function, OVER clause
- Follow-up Guidance: The examples show that you add knowledge by posting to `/v3/knowledgeBases/{knowledge_base_id}/data` with a `type`, `meta_data`, and `raw_data` payload.
- Classification Note: This is classified as an operation because it provides concrete POST examples for adding each supported knowledge type to a newly created knowledge base.

## Official Source Content

## Step 3. Add knowledge to the newly created knowledge base

To add new knowledge, you can call the `/v3/knowledgeBases/{knowledge_base_id}/data` endpoint.
### Add a few-shot example type of knowledge

For example, if you want Chat2Query to generate SQL statements of the count of rows in a table in a specific structure, you can add a few-shot example type of knowledge by calling `/v3/knowledgeBases/{knowledge_base_id}/data` as follows:

```bash
curl --digest --user ${PUBLIC_KEY}:${PRIVATE_KEY} --request POST 'https://<region>.data.tidbcloud.com/api/v1beta/app/chat2query-<ID>/endpoint/v3/knowledgeBases/<knowledge_base_id>/data'\
 --header 'content-type: application/json'\
 --data-raw '{
    "type": "few-shot",
    "meta_data": {},
    "raw_data": {
         "question": "How many records are in the 'test' table?",
         "answer": "SELECT COUNT(*) FROM `test`;"
    }
}'
```

In the preceding example code, `"type": "few-shot"` represents the few-shot example knowledge type.
### Add a term-sheet explanation type of knowledge

For example, if you want Chat2Query to comprehend the meaning of the term `OSS` using your provided explanation, you can add a term-sheet explanation type of knowledge by calling `/v3/knowledgeBases/{knowledge_base_id}/data` as follows:

```bash
curl --digest --user ${PUBLIC_KEY}:${PRIVATE_KEY} --request POST 'https://<region>.data.tidbcloud.com/api/v1beta/app/chat2query-<ID>/endpoint/v3/knowledgeBases/<knowledge_base_id>/data'\
 --header 'content-type: application/json'\
 --data-raw '{
    "type": "term-sheet",
    "meta_data": {},
    "raw_data": {
        "term": ["OSS"],
        "description": "OSS Insight is a powerful tool that provides online data analysis for users based on nearly 6 billion rows of GitHub event data."
    }
}'
```

In the preceding example code, `"type": "term-sheet"` represents the term-sheet explanation knowledge type.
### Add an instruction type of knowledge

For example, if you want Chat2Query to consistently use the `LAG` function with the `OVER` clause in SQL queries when dealing with questions about sequential growth rate calculation, you can add an instruction type of knowledge by calling `/v3/knowledgeBases/{knowledge_base_id}/data` as follows:

```bash
curl --digest --user ${PUBLIC_KEY}:${PRIVATE_KEY} --request POST 'https://<region>.data.tidbcloud.com/api/v1beta/app/chat2query-<ID>/endpoint/v3/knowledgeBases/<knowledge_base_id>/data'\
 --header 'content-type: application/json'\
 --data-raw '{
    "type": "instruction",
    "meta_data": {},
    "raw_data": {
        "instruction": "If the task requires calculating the sequential growth rate, use the LAG function with the OVER clause in SQL"
    }
}'
```

In the preceding example code, `"type": "instruction"` represents the instruction knowledge type.
