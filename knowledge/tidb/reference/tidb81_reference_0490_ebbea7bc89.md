# Reference document template structure

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/resources/doc-templates/template-reference.md`
- Source Title: `(The same as L1 heading) Such as "Garbage Collection Configuration" in 59 characters or less. Include the keywords of this document. Test title here https://moz.com/learn/seo/title-tag`
- Source Heading Path: `L1 heading (the same as title in the metadata) | L1 heading (the same as title in the metadata) > L2 heading (A category or a parameter/configuration item) | L1 heading (the same as title in the metadata) > L2 heading (A category or a parameter/configuration item) > L3 Heading (optional, a parameter or a configuration item) | L1 heading (the same as title in the metadata) > L2 heading (A category or a parameter/configuration item) > L3 Heading 2 | L1 heading (the same as title in the metadata) > L2 Heading 2 | L1 heading (the same as title in the metadata) > L2 heading 3`
- Source Line Ranges: `5-62`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: none
- Topic Tags: `template`, `reference-topics`, `headings`, `parameters`, `warnings`, `notes`, `tables`, `formatting`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0490_ebbea7bc89`
- Source ID: `tidb-docs-8.1:resources/doc-templates/template-reference.md#l1-heading-the-same-as-title-in-the-metadata`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ece14f5eda04c60a4bad61c6859f8459749cc039c6b4231896d5de6a66c976c9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/resources/doc-templates/template-reference#l1-heading-the-same-as-title-in-the-metadata
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/resources/doc-templates/template-reference.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the required structure and formatting rules for a reference document template covering commands, parameters, or configuration options.
- Retrieval Keywords: reference document template, commands, parameters, configuration options, TOC.md, headings cannot skip levels, avoid using level 5 headings, Warning, Note, indentation must be 4 spaces, table must have headers, Parameter Description Default value Required Example, TiDB Cluster Alert Rules
- Follow-up Guidance: The source also points to adding a link in `TOC.md` and gives `TiDB Cluster Alert Rules` as an example of this document type.
- Classification Note: The content is classified as reference because it defines the template structure, heading hierarchy, warning and note format, and table format for reference topics.

## Official Source Content

# L1 heading (the same as title in the metadata)

> About this template:
>
> - This document is a template for reference topics, including commands, parameters, configuration options. You can directly copy and use this template and delete unnecessary annotations. An example of this type of document: [TiDB Cluster Alert Rules](https://docs.pingcap.com/tidb/stable/alert-rules)
> - For a new document, please add a link to the appropriate location in the `TOC.md` file (consider where users are most likely to look for this document in the table of contents).
> - The headings within the document cannot skip levels, and try to avoid using level 5 headings.

**Required** In the first paragraph, summarize the content of this document in a few sentences.

You can use the following sentence:

"This document describes..."
## L2 heading (A category or a parameter/configuration item)

Introduce the category/parameter/configuration item described in this section, using the following sentence:

"This section describes..."
### L3 Heading (optional, a parameter or a configuration item)

If you need to list multiple parameters, use unordered lists (`*`/`+`/`-`).

- xxx: xxx
- xxx: xxx
- xxx: xxx
### L3 Heading 2

xxx
## L2 Heading 2

If you need to add notes or warnings, strictly follow the following format.

> **Warning**
>
> If the information might bring risks to users, such as system availability, security, data loss, etc., use a warning. For example, the current feature is an experimental feature and is not recommended for production environments.

> **Note**
>
> For general tips and notes, use a note. For example, when reading historical data, even if the current table structure is different from the table structure of the historical data, the historical data will be returned in the table structure of the historical data at that time.

If the notes or warnings are nested in a list, indent them with four spaces.

To prevent incorrect display, all indentation on the PingCAP website must be 4 spaces.
## L2 heading 3

If you need to use a table, note that the table must have headers (namely, the first row).

The following table lists the description, default value, and example of the specific configuration item/parameter.

| Parameter | Description | Default value | Required | Example |
| :-- | :-- | :-- | :-- | :-- |
| xxx | xxx | xxx | xxx | xxx |
