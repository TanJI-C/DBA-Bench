# Vector search relevance scoring, retriever usage, and cleanup

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-langchain.md`
- Source Title: `Integrate Vector Search with LangChain`
- Source Heading Path: `Integrate Vector Search with LangChain > Get started > Step 6. Perform a vector search > Option 2: Use `similarity_search_with_relevance_scores()` | Integrate Vector Search with LangChain > Get started > Use as a retriever | Integrate Vector Search with LangChain > Get started > Remove the vector store`
- Source Line Ranges: `205-287`
- Source Scope: `developer`
- Primary Component: `ecosystem`
- Related Components: `cloud`, `sql`, `tidb`
- Topic Tags: `vector-search`, `langchain`, `relevance-scores`, `retriever`, `similarity-search`, `cleanup`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0113_7002cb6ab2`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-langchain.md#option-2-use-similarity-search-with-relevance-scores`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `42d346ccf1828a7e68b8bc4c0e5e1a58276f3102911ec2e8d84f347b5f455f00`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-langchain#option-2-use-similarity-search-with-relevance-scores
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-langchain.md

## Retrieval Guidance

- Use When: Use this chunk when looking for how TiDB vector search in LangChain returns relevance scores, exposes a retriever interface, or removes an existing vector store.
- Retrieval Keywords: similarity_search_with_relevance_scores(), top k documents, relevance scores, higher score indicates a higher degree of similarity, vector_store.as_retriever, search_type="similarity_score_threshold", search_kwargs, score_threshold, retriever.invoke(query), Use as a retriever, drop_vectorstore(), Remove the vector store
- Follow-up Guidance: It also shows `vector_store.as_retriever(search_type="similarity_score_threshold", search_kwargs={"k": 3, "score_threshold": 0.8})` and the cleanup call `vector_store.drop_vectorstore()`.
- Classification Note: This is classified as data_pipeline because the content demonstrates runtime search usage, retriever invocation, and vector store cleanup in a LangChain workflow.

## Official Source Content

#### Option 2: Use `similarity_search_with_relevance_scores()`

The `similarity_search_with_relevance_scores()` method returns the top `k` documents with the highest relevance scores. A higher score indicates a higher degree of similarity between a document and your query.

```python
docs_with_relevance_score = vector_store.similarity_search_with_relevance_scores(query, k=2)
for doc, score in docs_with_relevance_score:
    print("-" * 80)
    print("Score: ", score)
    print(doc.page_content)
    print("-" * 80)
```

<details>
   <summary><b>Expected output</b></summary>

```plain
--------------------------------------------------------------------------------
Score:  0.8152758634748147
Tonight. I call on the Senate to: Pass the Freedom to Vote Act. Pass the John Lewis Voting Rights Act. And while you’re at it, pass the Disclose Act so Americans can know who is funding our elections.

Tonight, I’d like to honor someone who has dedicated his life to serve this country: Justice Stephen Breyer—an Army veteran, Constitutional scholar, and retiring Justice of the United States Supreme Court. Justice Breyer, thank you for your service.

One of the most serious constitutional responsibilities a President has is nominating someone to serve on the United States Supreme Court.

And I did that 4 days ago, when I nominated Circuit Court of Appeals Judge Ketanji Brown Jackson. One of our nation’s top legal minds, who will continue Justice Breyer’s legacy of excellence.
--------------------------------------------------------------------------------
--------------------------------------------------------------------------------
Score:  0.7824248697721444
A former top litigator in private practice. A former federal public defender. And from a family of public school educators and police officers. A consensus builder. Since she’s been nominated, she’s received a broad range of support—from the Fraternal Order of Police to former judges appointed by Democrats and Republicans.

And if we are to advance liberty and justice, we need to secure the Border and fix the immigration system.

We can do both. At our border, we’ve installed new technology like cutting-edge scanners to better detect drug smuggling.

We’ve set up joint patrols with Mexico and Guatemala to catch more human traffickers.

We’re putting in place dedicated immigration judges so families fleeing persecution and violence can have their cases heard faster.

We’re securing commitments and supporting partners in South and Central America to host more refugees and secure their own borders.
--------------------------------------------------------------------------------
```

</details>
### Use as a retriever

In Langchain, a [retriever](https://python.langchain.com/v0.2/docs/concepts/#retrievers) is an interface that retrieves documents in response to an unstructured query, providing more functionality than a vector store. The following code demonstrates how to use TiDB vector store as a retriever.

```python
retriever = vector_store.as_retriever(
   search_type="similarity_score_threshold",
   search_kwargs={"k": 3, "score_threshold": 0.8},
)
docs_retrieved = retriever.invoke(query)
for doc in docs_retrieved:
   print("-" * 80)
   print(doc.page_content)
   print("-" * 80)
```

The expected output is as follows:

```
--------------------------------------------------------------------------------
Tonight. I call on the Senate to: Pass the Freedom to Vote Act. Pass the John Lewis Voting Rights Act. And while you’re at it, pass the Disclose Act so Americans can know who is funding our elections.

Tonight, I’d like to honor someone who has dedicated his life to serve this country: Justice Stephen Breyer—an Army veteran, Constitutional scholar, and retiring Justice of the United States Supreme Court. Justice Breyer, thank you for your service.

One of the most serious constitutional responsibilities a President has is nominating someone to serve on the United States Supreme Court.

And I did that 4 days ago, when I nominated Circuit Court of Appeals Judge Ketanji Brown Jackson. One of our nation’s top legal minds, who will continue Justice Breyer’s legacy of excellence.
--------------------------------------------------------------------------------
```
### Remove the vector store

To remove an existing TiDB vector store, use the `drop_vectorstore()` method:

```python
vector_store.drop_vectorstore()
```
