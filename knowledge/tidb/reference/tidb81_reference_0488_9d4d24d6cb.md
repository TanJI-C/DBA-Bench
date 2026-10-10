# Concept document template structure

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/resources/doc-templates/template-concept.md`
- Source Title: `(The same as L1 heading) Concept such as "Garbage Collection Overview" in 59 characters or less. Include the keywords of this document. Test title here https://moz.com/learn/seo/title-tag`
- Source Heading Path: `L1 heading (the same as title in the metadata) | L1 heading (the same as title in the metadata) > L2 heading (e.g. Architecture) | L1 heading (the same as title in the metadata) > L2 heading (e.g. Architecture) > L3 heading (optional, e.g. "xxx component") | L1 heading (the same as title in the metadata) > L2 heading (e.g. Architecture) > L3 heading | L1 heading (the same as title in the metadata) > L2 heading (optional, e.g. "Key features/Limitations") | L1 heading (the same as title in the metadata) > What's next`
- Source Line Ranges: `5-71`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: none
- Topic Tags: `concept-template`, `document-structure`, `architecture-section`, `component-description`, `features`, `limitations`, `warnings`, `notes`, `related-documents`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0488_9d4d24d6cb`
- Source ID: `tidb-docs-8.1:resources/doc-templates/template-concept.md#l1-heading-the-same-as-title-in-the-metadata`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `329453bf98a0a09f6641ddfde302f7a6953ecadde7f40d3a89973a6888becf19`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/resources/doc-templates/template-concept#l1-heading-the-same-as-title-in-the-metadata
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/resources/doc-templates/template-concept.md

## Retrieval Guidance

- Use When: Use this chunk when searching for the official concept document template structure, including required summary text, Architecture section layout, optional Key features/Limitations section, warning and note formatting, and the What's next related-documents section.
- Retrieval Keywords: concept document template, template for concept topics, L1 heading, L2 heading, Architecture, L3 heading, Key features, Limitations, Warning, Note, What's next, TOC.md, TiCDC Overview, Deploy and Maintain TiCDC, Changefeed Overview, TiCDC FAQs, TiCDC Glossary, Keep image size <= 300 KB, Use `.png` or `.jpg`; do not use `.gif` or `.svg`, all indentation on the PingCAP website must be 4 spaces
- Follow-up Guidance: The source also points readers to related example documents such as TiCDC Overview, Deploy and Maintain TiCDC, Changefeed Overview, Explore HTAP, TiCDC FAQs, and TiCDC Glossary.
- Classification Note: The chunk is classified as reference content because it defines the required structure, headings, formatting rules, and related-document patterns for a concept document template.

## Official Source Content

# L1 heading (the same as title in the metadata)

> About this template:
>
> - This document is a template for concept topics, focusing on introducing concepts and explanatory information. You can directly copy and use this template and delete unnecessary annotations. An example of this type of document: [TiCDC Overview](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-overview).
> - For a new document, please add a link to the appropriate location in the `TOC.md` file (consider where users are most likely to look for this document in the table of contents).
> - The headings within the document cannot skip levels, and try to avoid using level 5 headings.

**Required** In the first paragraph, summarize the content of this document in a few sentences.

You can clarify the important terms and definitions within one to three sentences in this paragraph.
## L2 heading (e.g. Architecture)

Taking the overall architecture as an example, you can first introduce the core components in one or two sentences, and then provide the corresponding architecture diagram.

<!--  ![Architecture](/path/to/image)  -->
Keep image size <= 300 KB. Use `.png` or `.jpg`; do not use `.gif` or `.svg`.

Write a more detailed description below the image. Use unordered lists (`*`/`+`/`-`) to introduce each component.

- Component 1: xxx
- Component 2: xxx

You can also describe the basic working principles here, or integrate the principles into the component introduction above.
### L3 heading (optional, e.g. "xxx component")

If the component is complicated, you can elaborate it in a separate section like this one.
### L3 heading

xxx
## L2 heading (optional, e.g. "Key features/Limitations")

In the second L2 heading, introduce the basic info that users need to know beforehand, such as key features, usage scenarios, and limitations.

You can leave out this section if there's no need to provide this information.

If you need to add notes or warnings, strictly follow the following format.

> **Warning**
>
> If the information might bring risks to users, such as system availability, security, data loss, etc., use a warning. For example, the current feature is an experimental feature and is not recommended for production environments.

> **Note**
>
> For general tips and notes, use a note. For example, when reading historical data, even if the current table structure is different from the table structure of the historical data, the historical data will be returned in the table structure of the historical data at that time.

If the notes or warnings are nested in a list, indent them with four spaces.

To prevent incorrect display, all indentation on the PingCAP website must be 4 spaces.
## What's next

In this section, provide more related documents that users might want to read, such as:

- To learn how to deploy and maintain TiCDC, see [Deploy and Maintain TiCDC](https://docs.pingcap.com/tidb/stable/ticdc/deploy-ticdc).
- To learn changefeeds, see [Changefeed Overview](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-changefeed-overview).

You can also directly provide the documents that users might be interested in, such as:

- [Explore HTAP](https://docs.pingcap.com/tidb/stable/explore-htap)
- [TiCDC FAQs](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-faq)
- [TiCDC Glossary](https://docs.pingcap.com/tidb/stable/ticdc/ticdc-glossary)
