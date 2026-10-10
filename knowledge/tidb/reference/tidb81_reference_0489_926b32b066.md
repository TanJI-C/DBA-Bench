# New feature documentation template

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/resources/doc-templates/template-new-feature.md`
- Source Title: `(The same as L1 heading) Feature name such as "Clustered Indexes" in 59 characters or less. Include the keywords of this document. Test title here https://moz.com/learn/seo/title-tag`
- Source Heading Path: `New Feature Name (the same as title in the metadata) | New Feature Name (the same as title in the metadata) > Usage scenario(s) | New Feature Name (the same as title in the metadata) > Usage scenario(s) > Usage scenario 1 | New Feature Name (the same as title in the metadata) > Usage scenario(s) > Usage scenario 2 | New Feature Name (the same as title in the metadata) > Prerequisites (optional) | New Feature Name (the same as title in the metadata) > Usage or Procedures | New Feature Name (the same as title in the metadata) > Usage or Procedures > Method 1: AAA (recommended) | New Feature Name (the same as title in the metadata) > Usage or Procedures > Method 2: BBB | New Feature Name (the same as title in the metadata) > Parameter reference | New Feature Name (the same as title in the metadata) > Limitations | New Feature Name (the same as title in the metadata) > Compatibility | New Feature Name (the same as title in the metadata) > FAQ (optional) | New Feature Name (the same as title in the metadata) > FAQ (optional) > Q1: xxx | New Feature Name (the same as title in the metadata) > FAQ (optional) > Q2: xxx | New Feature Name (the same as title in the metadata) > More resources`
- Source Line Ranges: `5-119`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: `tidb`, `tiflash`, `tiup`
- Topic Tags: `template`, `feature-documentation`, `usage-scenarios`, `prerequisites`, `procedures`, `parameters`, `limitations`, `compatibility`, `faq`, `resources`, `warnings`, `notes`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0489_926b32b066`
- Source ID: `tidb-docs-8.1:resources/doc-templates/template-new-feature.md#new-feature-name-the-same-as-title-in-the-metadata`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `8bd09ac7e547fd6d9212f70122c0ba24d8d7e445e6e248b71aba760378f2d1ba`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/resources/doc-templates/template-new-feature#new-feature-name-the-same-as-title-in-the-metadata
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/resources/doc-templates/template-new-feature.md

## Retrieval Guidance

- Use When: Use this chunk when looking for the official template structure and required sections for documenting a new feature in TiDB documentation.
- Retrieval Keywords: new feature documentation template, Usage scenario(s), Prerequisites (optional), Usage or Procedures, Method 1: AAA (recommended), Method 2: BBB, Parameter reference, Limitations, Compatibility, FAQ (optional), More resources, Warning, Note, TOC.md, all indentation on the PingCAP website must be 4 spaces
- Follow-up Guidance: The template also points to example and related documents such as Clustered Indexes, Maintain a TiFlash Cluster, Scale in a TiFlash cluster, Explore HTAP, and TiFlash Architecture.
- Classification Note: This is classified as reference content because it specifies the document template structure, required headings, formatting rules, and example sections for feature documentation.

## Official Source Content

# New Feature Name (the same as title in the metadata)

> About this template:
>
> - This document is a template for new features, including feature concepts and how to use the feature. You can directly copy and use this template and delete unnecessary annotations. An example of this type of document: [Clustered Indexes](https://docs.pingcap.com/tidb/stable/clustered-indexes).
> - For a new document, please add a link to the appropriate location in the `TOC.md` file (consider where users are most likely to look for this document in the table of contents).
> - The headings within the document cannot skip levels, and try to avoid using level 5 headings.

> **Warning** (Optional)
>
> This feature is experimental. It is not recommended that you use it in the production environment. The syntax and implementation might be changed or removed without prior notice. If you find a bug, you can report an [issue](https://github.com/pingcap/tidb/issues) on GitHub.

This document describes the Usage scenarios, usage methods, and limitations of [feature name] and the FAQs when using this feature.

[Feature name] is a XXX that can be used to do XXX. By using this feature, you can achieve or optimize [a summary of the usage scenario]. (The implementation details or principles can be omitted, or you can consider putting them in a separate section or another document).

If you need to add notes or warnings, strictly follow the following format.

> **Note**
>
> For general tips and notes, use a note.

> **Warning**
>
> If the information might bring risks to users, such as system availability, security, data loss, etc., use a warning.

If the notes or warnings are nested in a list, indent them with four spaces.

To prevent incorrect display, **all indentation on the PingCAP website must be 4 spaces.**
## Usage scenario(s)

Usage scenarios are very important. You need to introduce why users need to use this feature, in what cases they can use it, and what problems this feature can solve from the user's perspective.

[New feature] is suitable for the following scenarios:

- unordered list
- unordered list
### Usage scenario 1
### Usage scenario 2
## Prerequisites (optional)

- Prepare xxx. Describes how to prepare xxx. You can provide a link to the reference document.
- Ensure that xxx. Describes how to check whether xxx meets the requirements. If not, describe how to handle it.
## Usage or Procedures

TiDB provides x methods for xxx, which are AAA method and BBB method.

In the case of xxx, to achieve xxx, it is recommended to use the AAA method.
### Method 1: AAA (recommended)

1. first step
2. second step
3. third step
### Method 2: BBB

1. first step
2. second step
3. third step
## Parameter reference

If this feature is mainly a new syntax or command, list the specific configuration item or parameter description, default value, and example.

You can either use a table or an unordered list.

| Parameter | Description | Default value | Required | Example |
| :-- | :-- | :-- | :-- | :-- |
| xxx | xxx | xxx | xxx | xxx |
## Limitations

In this section, list the usage limitations. If there is no order between the limitations, use an unordered list.
## Compatibility

In this section, list the compatibility information of this feature, including:

- The compatibility with previous TiDB versions
- The compatibility with MySQL
- The compatibility under different architectures or platforms.
## FAQ (optional)

In this section, list the FAQs when using this feature.

If there are many FAQs, you can add a separate FAQ document for this feature.
### Q1: xxx

Answer.
### Q2: xxx

Answer.
## More resources

In this section, provide more related documents that users might want to read, such as:

- To view the TiFlash version, important logs, and system tables, see [Maintain a TiFlash Cluster](https://docs.pingcap.com/tidb/stable/tiflash/maintain-tiflash).
- If you need to remove a TiFlash node, see [Scale in a TiFlash cluster](https://docs.pingcap.com/tidb/stable/scale-tidb-using-tiup#scale-in-a-tiflash-cluster).

You can also directly provide the documents that users might be interested in, such as:

- [Explore HTAP](https://docs.pingcap.com/tidb/stable/explore-htap)
- [TiFlash Architecture](https://docs.pingcap.com/tidb/stable/tiflash/tiflash-overview#architecture)
- [Maintain a TiFlash cluster](https://docs.pingcap.com/tidb/stable/tiflash/maintain-tiflash)
