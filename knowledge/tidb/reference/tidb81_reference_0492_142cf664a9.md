# Troubleshooting document template structure

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/resources/doc-templates/template-troubleshooting.md`
- Source Title: `(The same as L1 heading) Such as "Troubleshoot Increased Read and Write Latency" in 59 characters or less. Include the keywords of this document. Test title here https://moz.com/learn/seo/title-tag`
- Source Heading Path: `L1 heading (the same as title in the metadata) | L1 heading (the same as title in the metadata) > Common causes | L1 heading (the same as title in the metadata) > Common causes > Common cause 1 | L1 heading (the same as title in the metadata) > Common causes > Common cause 2 | L1 heading (the same as title in the metadata) > Other causes | L1 heading (the same as title in the metadata) > Other causes > Cause 1 | L1 heading (the same as title in the metadata) > Other causes > Cause 2`
- Source Line Ranges: `5-62`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: none
- Topic Tags: `troubleshooting`, `template`, `diagnosis`, `symptoms`, `solutions`, `common-causes`, `other-causes`, `document-structure`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0492_142cf664a9`
- Source ID: `tidb-docs-8.1:resources/doc-templates/template-troubleshooting.md#l1-heading-the-same-as-title-in-the-metadata`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `434e2271a2dc1fcbc59b6966a7cbdb8cde819ec1af630dcde97f4a9b7b813dd9`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/resources/doc-templates/template-troubleshooting#l1-heading-the-same-as-title-in-the-metadata
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/resources/doc-templates/template-troubleshooting.md

## Retrieval Guidance

- Use When: Use this chunk when someone needs the official structure and required sections for writing a troubleshooting document that covers diagnosis, symptoms, causes, and solutions.
- Retrieval Keywords: template for troubleshooting topics, how to diagnose and solve problems, Common causes, Other causes, Symptom, Solution, TOC.md, headings cannot skip levels, avoid using level 5 headings, ordered list, unordered lists, Troubleshoot Increased Read and Write Latency
- Follow-up Guidance: After the solution is provided, ask users to check whether the previous problem is resolved after following the solution, and if the problem persists, describe how to proceed.
- Classification Note: This is a reference template because the content defines the document structure, section headings, and writing guidance for troubleshooting topics rather than troubleshooting a specific product issue.

## Official Source Content

# L1 heading (the same as title in the metadata)

> About this template:
>
> - This document is a template for troubleshooting topics, including how to diagnose and solve problems. You can directly copy and use this template and delete unnecessary annotations. An example of this type of document: [Troubleshoot Increased Read and Write Latency](https://docs.pingcap.com/tidb/stable/troubleshoot-cpu-issues).
> - For a new document, please add a link to the appropriate location in the `TOC.md` file (consider where users are most likely to look for this document in the table of contents).
> - The headings within the document cannot skip levels, and try to avoid using level 5 headings.

This document describes how to diagnose [xxx problems] and their possible causes and solutions.
## Common causes

Put the most common causes of the problem in this section to help users prioritize these probable causes.
### Common cause 1

Briefly describe the background information of common cause 1 and the impact on the system.

**Symptom:**

Give the information that helps users determine whether the current problem is caused by common cause 1.

**Solution:**

List the solutions to the problem caused by common cause 1. Use unordered lists or steps to present the information according to whether the solution has a specific order.

If the solution is a series of steps, use an ordered list. For example:

1. The first step
2. The second step
3. The third step

After the solution is provided, ask users to check whether the previous problem is resolved after following the solution. If the problem persists, describe how to proceed.
### Common cause 2

Briefly describe the background information of common cause 2 and the impact on the system.

**Symptom:**

(The same as cause 1)

**Solution:**

(The same as cause 1)
## Other causes

List the less common causes of the problem in this section.
### Cause 1

(The same as the previous section)
### Cause 2

(The same as the previous section)
