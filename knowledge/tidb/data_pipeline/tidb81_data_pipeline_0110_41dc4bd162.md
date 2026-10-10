# Invoke Bedrock models, store embeddings, and run the RAG demo

## Knowledge Metadata

- Knowledge Type: `data_pipeline`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/vector-search-integrate-with-amazon-bedrock.md`
- Source Title: `Integrate TiDB Vector Search with Amazon Bedrock`
- Source Heading Path: `Integrate TiDB Vector Search with Amazon Bedrock > Get started > Step 5. Invoke the Amazon Titan Text Embeddings V2 model using the Bedrock runtime client | Integrate TiDB Vector Search with Amazon Bedrock > Get started > Step 6. Create a vector table | Integrate TiDB Vector Search with Amazon Bedrock > Get started > Step 7. Save the vector data to TiDB Cloud Serverless | Integrate TiDB Vector Search with Amazon Bedrock > Get started > Step 8. Run the application | Integrate TiDB Vector Search with Amazon Bedrock > See also`
- Source Line Ranges: `139-313`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `tidb`, `ecosystem`, `sql`
- Topic Tags: `embeddings`, `model-invocation`, `bedrock-runtime`, `vector-table`, `hnsw`, `data-ingestion`, `application-run`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_data_pipeline_0110_41dc4bd162`
- Source ID: `tidb-docs-8.1:tidb-cloud/vector-search-integrate-with-amazon-bedrock.md#step-5-invoke-the-amazon-titan-text-embeddings-v2-model-using-the-bedrock-runtime-client`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `472f108affebd358beae9cb37b8644d8771885c6239bcbc7ab7dbb2b562c205f`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-integrate-with-amazon-bedrock#step-5-invoke-the-amazon-titan-text-embeddings-v2-model-using-the-bedrock-runtime-client
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/vector-search-integrate-with-amazon-bedrock.md

## Retrieval Guidance

- Use When: Use this chunk when the user needs the example code for Amazon Bedrock invoke_model calls, the vector table definition, saving embeddings into TiDB Cloud Serverless, or the final demo execution flow and expected output.
- Retrieval Keywords: invoke_model, bedrock-runtime, amazon.titan-embed-text-v2:0, us.meta.llama3-2-3b-instruct-v1:0, dimensions 512, normalize True, application/json, accept */*, accept application/json, generate_result, embedding(content), Entity, __tablename__ = "entity", VectorType(dim=dim_of_embedding_model), hnsw(distance=l2), Base.metadata.create_all(engine), save_entities_with_embedding, Session(engine), python3 demo.py, What is TiDB?, Generated answer, Vector Data Types, Vector Search Index
- Follow-up Guidance: The see also section links to Vector Data Types and Vector Search Index for related vector feature details.
- Classification Note: This is data_pipeline content because it covers model invocation, embedding generation, vector table creation, vector data insertion, and running the end-to-end RAG demo shown in the tutorial.

## Official Source Content

### Step 5. Invoke the Amazon Titan Text Embeddings V2 model using the Bedrock runtime client

The Amazon Bedrock runtime client provides you with an `invoke_model` API that accepts the following parameters:

- `modelId`: the model ID of the foundation model available in Amazon Bedrock.
- `accept`: the type of the input request.
- `contentType`: the content type of the input.
- `body`: a JSON string payload consisting of the prompt and the configurations.

In `demo.py`, add the following code to invoke the `invoke_model` API to generate text embeddings using Amazon Titan Text Embeddings and get responses from Meta Llama 3:

```python
# Bedrock Runtime Client Setup
bedrock_runtime = boto3.client('bedrock-runtime')

# ---- Model Invocation ----
embedding_model_name = "amazon.titan-embed-text-v2:0"
dim_of_embedding_model = 512
llm_name = "us.meta.llama3-2-3b-instruct-v1:0"


def embedding(content):
    """Invoke Amazon Bedrock to get text embeddings."""
    payload = {
        "modelId": embedding_model_name,
        "contentType": "application/json",
        "accept": "*/*",
        "body": {
            "inputText": content,
            "dimensions": dim_of_embedding_model,
            "normalize": True,
        }
    }

    body_bytes = json.dumps(payload['body']).encode('utf-8')

    response = bedrock_runtime.invoke_model(
        body=body_bytes,
        contentType=payload['contentType'],
        accept=payload['accept'],
        modelId=payload['modelId']
    )

    result_body = json.loads(response.get("body").read())
    return result_body.get("embedding")


def generate_result(query: str, info_str: str):
    """Generate answer using Meta Llama 3 model."""
    prompt = f"""
    ONLY use the content below to generate an answer:
    {info_str}

    ----
    Please carefully think about the question: {query}
    """

    payload = {
        "modelId": llm_name,
        "contentType": "application/json",
        "accept": "application/json",
        "body": {
            "prompt": prompt,
            "temperature": 0
        }
    }

    body_bytes = json.dumps(payload['body']).encode('utf-8')

    response = bedrock_runtime.invoke_model(
        body=body_bytes,
        contentType=payload['contentType'],
        accept=payload['accept'],
        modelId=payload['modelId']
    )

    result_body = json.loads(response.get("body").read())
    completion = result_body["generation"]
    return completion
```
### Step 6. Create a vector table

In `demo.py`, add the following code to create a vector table to store text and vector embeddings:

```python
# ---- TiDB Setup and Vector Index Creation ----
class Entity(Base):
    """Define the Entity table with a vector index."""
    __tablename__ = "entity"
    id = Column(Integer, primary_key=True)
    content = Column(Text)
    content_vec = Column(VectorType(dim=dim_of_embedding_model), comment="hnsw(distance=l2)")

# Create the table in TiDB
Base.metadata.create_all(engine)
```
### Step 7. Save the vector data to TiDB Cloud Serverless

In `demo.py`, add the following code to save the vector data to your TiDB Cloud Serverless cluster:

```python
# ---- Saving Vectors to TiDB ----
def save_entities_with_embedding(session, contents):
    """Save multiple entities with their embeddings to the TiDB Serverless database."""
    for content in contents:
        entity = Entity(content=content, content_vec=embedding(content))
        session.add(entity)
    session.commit()
```
### Step 8. Run the application

1. In `demo.py`, add the following code to establish a database session, save embeddings to TiDB, ask an example question (such as "What is TiDB?"), and generate results from the model:

    ```python
    if __name__ == "__main__":
        # Establish a database session
        with Session(engine) as session:
            # Example data
            contents = [
                "TiDB is a distributed SQL database compatible with MySQL.",
                "TiDB supports Hybrid Transactional and Analytical Processing (HTAP).",
                "TiDB can scale horizontally and provides high availability.",
                "Amazon Bedrock allows seamless integration with foundation models.",
                "Meta Llama 3 is a powerful model for text generation."
            ]

            # Save embeddings to TiDB
            save_entities_with_embedding(session, contents)

            # Example query
            query = "What is TiDB?"
            info_str = " ".join(contents)

            # Generate result from Meta Llama 3
            result = generate_result(query, info_str)
            print(f"Generated answer: {result}")
    ```

2. Save all changes to `demo.py` and run the script:

    ```shell
    python3 demo.py
    ```

    The expected output is similar to the following:

    ```
    Generated answer:  What is the main purpose of TiDB?
         What are the key features of TiDB?
         What are the key benefits of TiDB?

        ----
        Based on the provided text, here is the answer to the question:
        What is TiDB?
        TiDB is a distributed SQL database compatible with MySQL.

    ## Step 1: Understand the question
    The question asks for the definition of TiDB.

    ## Step 2: Identify the key information
    The key information provided in the text is that TiDB is a distributed SQL database compatible with MySQL.

    ## Step 3: Provide the answer
    Based on the provided text, TiDB is a distributed SQL database compatible with MySQL.

    The final answer is: TiDB is a distributed SQL database compatible with MySQL.
    ```
## See also

- [Vector Data Types](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-data-types)
- [Vector Search Index](https://docs.pingcap.com/tidb/stable/tidb-cloud/vector-search-index)
