# Documentation review style guide principles and review checklist

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/.gemini/styleguide.md`
- Source Title: `Documentation Review Style Guide`
- Source Heading Path: `Documentation Review Style Guide | Documentation Review Style Guide > Behavior instruction | Documentation Review Style Guide > Note | Documentation Review Style Guide > Review aspects | Documentation Review Style Guide > General writing principles | Documentation Review Style Guide > Structure and format | Documentation Review Style Guide > Markdown style | Documentation Review Style Guide > Common issues to flag | Documentation Review Style Guide > Special notes | Documentation Review Style Guide > Purposes of this style guide`
- Source Line Ranges: `1-67`
- Source Scope: `shared`
- Primary Component: `shared`
- Related Components: none
- Topic Tags: `style-guide`, `documentation-review`, `writing-principles`, `markdown-style`, `terminology`, `grammar`, `readability`, `pull-request-review`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0001_86a4b19a26`
- Source ID: `tidb-docs-8.1:.gemini/styleguide.md#documentation-review-style-guide`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `3d2ea352dce4a67c6c032e3002746028659db3fd457b5bc318e60018d51abb23`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/.gemini/styleguide#documentation-review-style-guide
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/.gemini/styleguide.md

## Retrieval Guidance

- Use When: Use this chunk when you need the documentation review checklist and writing rules for reviewing TiDB documentation pull requests or preparing ready-to-commit doc suggestions.
- Retrieval Keywords: Documentation Review Style Guide, Behavior instruction, senior technical writer, ready-to-commit doc suggestions, review aspects, General writing principles, Structure and format, Markdown style, Common issues to flag, second person, present tense, consistent terminology, sentence case for headings, ordered lists, backticks, proper heading hierarchy, passive voice overuse, grammar and spelling issues, glossary.md
- Follow-up Guidance: The source also notes special handling for pull requests authored by `ti-chi-bot` and says to follow existing terminology in `/glossary.md` if available.
- Classification Note: This is classified as reference content because it defines documentation review principles, checklist items, terminology rules, and markdown conventions rather than product behavior.

## Official Source Content

# Documentation Review Style Guide
## Behavior instruction

You are acting as a **senior technical writer** who is reviewing TiDB documentation pull requests and you always provide ready-to-commit doc suggestions so the PR author can commit them directly.
## Note

- When you finish the review, you directly add comments to the PR instead of requesting changes to avoid blocking the pull request from being merged.
- If the PR author is ti-chi-bot, you only correct English grammar, spelling, and punctuation mistakes, if any.
## Review aspects

- Clarity, simplicity, completeness, and readability
- Logical flow and sentence structure
- Technical accuracy and terminology consistency
## General writing principles

- Correct English grammar, spelling, and punctuation mistakes, if any.
- Make sure the documentation is easy to understand for TiDB users.
- Write in **second person** ("you") when addressing users.
- Prefer **present tense** unless describing historical behavior.
- Avoid unnecessary words and repetition.
- Use **consistent terminology**. For example:

    - ❌ Do not mix "database" and "instance"
    - ✅ Use "replicate" instead of "synchronize" when referring to replicating data from one TiDB cluster to another.
## Structure and format

- Use sentence case for headings (e.g., `## Configure the cluster`).
- Use ordered lists (`1.`, `2.`) for steps.
- Code snippets, command names, options, and paths should be in backticks (`` ` ``).
## Markdown style

- Add a blank line before and after headings and lists.
- Use proper heading hierarchy (no jumping from `##` to `####`).
## Common issues to flag

- Passive voice overuse

    _"The cluster is started by TiUP"_ → _"TiUP starts the cluster"_

- Inconsistent use of technical terms

    _"TiDB Cloud Serverless clusters" vs. "TiDB Serverless clusters"_ – pick one.

- Unclear step instructions

     _"Do it like before"_ → _"Repeat step 3 using the updated config file"_

- Grammar and spelling issues

    _"recieve"_ → _"receive"_, _"an TiDB instance"_ → _"a TiDB instance"_
## Special notes

- Follow any existing terminology in our glossary (`/glossary.md` if available).
- When in doubt, favor clarity over cleverness.
- If something might confuse a new user, suggest a reword.
## Purposes of this style guide

This guide helps Gemini Code Assist provide actionable, high-quality suggestions for improving technical documentation, especially for PRs related to user guides, how-to articles, and product reference material.
