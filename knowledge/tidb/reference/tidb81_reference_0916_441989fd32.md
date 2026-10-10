# Choose Chat2Query knowledge base types and structures

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/tidb-cloud/use-chat2query-knowledge.md`
- Source Title: `Use Knowledge Bases`
- Source Heading Path: `Use Knowledge Bases > Step 2. Choose a knowledge type | Use Knowledge Bases > Step 2. Choose a knowledge type > Few-shot example | Use Knowledge Bases > Step 2. Choose a knowledge type > Few-shot example > Knowledge structure | Use Knowledge Bases > Step 2. Choose a knowledge type > Few-shot example > Use cases | Use Knowledge Bases > Step 2. Choose a knowledge type > Term-sheet explanation | Use Knowledge Bases > Step 2. Choose a knowledge type > Term-sheet explanation > Knowledge structure | Use Knowledge Bases > Step 2. Choose a knowledge type > Term-sheet explanation > Use cases | Use Knowledge Bases > Step 2. Choose a knowledge type > Instruction | Use Knowledge Bases > Step 2. Choose a knowledge type > Instruction > Knowledge structure | Use Knowledge Bases > Step 2. Choose a knowledge type > Instruction > Use cases`
- Source Line Ranges: `64-159`
- Source Scope: `cloud`
- Primary Component: `cloud`
- Related Components: `shared`, `sql`
- Topic Tags: `chat2query`, `knowledge-base`, `knowledge-types`, `few-shot`, `term-sheet`, `instruction`, `schema`, `use-cases`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0916_441989fd32`
- Source ID: `tidb-docs-8.1:tidb-cloud/use-chat2query-knowledge.md#step-2-choose-a-knowledge-type`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2778e93fb0eec82ea65330998301ec598f4979fd1433bf76e08cdb0803fac3fb`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/tidb-cloud/use-chat2query-knowledge#step-2-choose-a-knowledge-type
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/tidb-cloud/use-chat2query-knowledge.md

## Retrieval Guidance

- Use When: Use this chunk when you need to decide between the Chat2Query knowledge types and understand their supported structures and example use cases.
- Retrieval Keywords: Step 2. Choose a knowledge type, Few-shot example, Term-sheet explanation, Instruction, knowledge structure, use cases, question, answer, term, description, instruction, 512 characters, LAG function, OVER clause
- Follow-up Guidance: The source states that before adding knowledge to your knowledge base, you need to choose a knowledge type that best suits your use case.
- Classification Note: This is classified as a reference because it describes the supported knowledge types, their data structures, notes, and scenarios rather than a procedural endpoint workflow.

## Official Source Content

## Step 2. Choose a knowledge type

The knowledge base of each database can contain multiple types of knowledge. Before adding knowledge to your knowledge base, you need to choose a knowledge type that best suits your use case.

Currently, Chat2Query knowledge bases support the following knowledge types. Each type is specifically designed for different scenarios and has a unique knowledge structure.

- [Few-shot example](#few-shot-example)
- [Term-sheet explanation](#term-sheet-explanation)
- [Instruction](#instruction)
### Few-shot example

Few-shot example refers to the Q&A learning samples provided to Chat2Query, which include sample questions and their corresponding answers. These examples help Chat2Query handle new tasks more effectively.

> **Note:**
>
> Make sure the accuracy of newly added examples, because the quality of examples affects how well Chat2Query learns. Poor examples, such as mismatched questions and answers, can degrade the performance of Chat2Query on new tasks.
#### Knowledge structure

Each example consists of a sample question and its corresponding answer.

For example:

```json
{
    "question": "How many records are in the 'test' table?",
    "answer": "SELECT COUNT(*) FROM `test`;"
}
```
#### Use cases

Few-Shot examples can significantly improve the performance of Chat2Query in various scenarios, including but not limited to the following:

1. **When dealing with rare or complex questions**: if Chat2Query encounters infrequent or complex questions, adding few-shot examples can enhance its understanding and improve the accuracy of the results.

2. **When struggling with a certain type of question**: if Chat2Query frequently makes mistakes or has difficulty with specific questions, adding few-shot examples can help improve its performance on these questions.
### Term-sheet explanation

Term-sheet explanation refers to a comprehensive explanation of a specific term or a group of similar terms, helping Chat2Query understand the meaning and usage of these terms.

> **Note:**
>
> Make sure the accuracy of newly added term explanations, because the quality of explanations affects how well Chat2Query learns. Incorrect interpretations do not improve Chat2Query results but also potentially lead to adverse effects.
#### Knowledge structure

Each explanation includes either a single term or a list of similar terms and their detailed descriptions.

For example:

```json
{
    "term": ["OSS"],
    "description": "OSS Insight is a powerful tool that provides online data analysis for users based on nearly 6 billion rows of GitHub event data."
}
```
#### Use cases

Term-sheet explanation is primarily used to improve Chat2Query's comprehension of user queries, especially in these situations:

- **Dealing with industry-specific terminology or acronyms**: when your query contains industry-specific terminology or acronyms that might not be universally recognized, using a term-sheet explanation can help Chat2Query understand the meaning and usage of these terms.
- **Dealing with ambiguities in user queries**: when your query contains ambiguous concepts that is confusing, using a term-sheet explanation can help Chat2Query clarify these ambiguities.
- **Dealing with terms with various meanings**: when your query contains terms that carry different meanings in various contexts, using a term-sheet explanation can assist Chat2Query in discerning the correct interpretation.
### Instruction

Instruction is a piece of textual command. It is used to guide or control the behavior of Chat2Query, specifically instructing it on how to generate SQL according to specific requirements or conditions.

> **Note:**
>
> - The instruction has a length limit of 512 characters.
> - Make sure to provide as clear and specific instructions as possible to ensure that Chat2Query can understand and execute the instructions effectively.
#### Knowledge structure

Instruction only includes a piece of textual command.

For example:

```json
{
    "instruction": "If the task requires calculating the sequential growth rate, use the LAG function with the OVER clause in SQL"
}
```
#### Use cases

Instruction can be used in many scenarios to guide Chat2Query to output according to your requirements, including but not limited to the following:

- **Limiting query scope**: if you want the SQL to consider only certain tables or columns, use an instruction to specify this.
- **Guiding SQL structure**: if you have specific requirements for the SQL structure, use an instruction to guide Chat2Query.
