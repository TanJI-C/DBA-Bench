# DM table selector wildcard rules and examples

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/dm/table-selector.md`
- Source Title: `Table Selector of TiDB Data Migration`
- Source Heading Path: `Table Selector of TiDB Data Migration | Table Selector of TiDB Data Migration > Wildcard character | Table Selector of TiDB Data Migration > Match rules | Table Selector of TiDB Data Migration > Usage examples`
- Source Line Ranges: `5-43`
- Source Scope: `self_managed`
- Primary Component: `dm`
- Related Components: none
- Topic Tags: `table-selector`, `schema-pattern`, `table-pattern`, `wildcards`, `match-rules`, `usage-examples`, `pattern-matching`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0234_eb1106270e`
- Source ID: `tidb-docs-8.1:dm/table-selector.md#table-selector-of-tidb-data-migration`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `39a88f765dae6aa55fccf192cbd910e7f03c7707f406170f2d9586ad0bd9c445`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/dm/table-selector#table-selector-of-tidb-data-migration
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/dm/table-selector.md

## Retrieval Guidance

- Use When: Use this when looking for how DM `schema-pattern` and `table-pattern` wildcard matching works, including supported wildcard characters, match rules, and example patterns.
- Retrieval Keywords: Table Selector of TiDB Data Migration, schema-pattern, table-pattern, wildcard character, asterisk, star, question mark, * matches zero or more characters, * can only be placed at the end of the word, ? matches exactly one character, schema-pattern cannot be empty, table-pattern can be empty, only schema is matched, both schema and table are successfully matched, schema_*, table_*
- Follow-up Guidance: The source includes usage examples for matching schemas with the `schema_` prefix and tables with the `table_` prefix using `schema-pattern` and `table-pattern`.
- Classification Note: This is reference content because it defines DM table selector wildcard syntax, matching constraints, and concrete pattern examples for `schema-pattern` and `table-pattern`.

## Official Source Content

# Table Selector of TiDB Data Migration

Table selector provides a match rule based on [wildcard characters](https://en.wikipedia.org/wiki/Wildcard_character) for schema/table. To match a specified table, configure `schema-pattern`/`table-pattern`.
## Wildcard character

Table selector uses the following two wildcard characters in `schema-pattern`/`table-pattern`:

+ The asterisk character (`*`, also called "star")

    - `*` matches zero or more characters. For example, `doc*` matches `doc` and `document` but not `dodo`.
    - `*` can only be placed at the end of the word. For example, `doc*` is supported, while `do*c` is not supported.

+ The question mark (`?`)

    `?` matches exactly one character except the empty character.
## Match rules

- `schema-pattern` cannot be empty.
- `table-pattern` can be empty. When you configure it as empty, only `schema` is matched according to `schema-pattern`.
- When `table-pattern` is not empty, the `schema` is matched according to `schema-pattern` and `table` is matched according to `table-pattern`. Only when both `schema` and `table` are successfully matched, you can get the match result.
## Usage examples

- Matching all schemas and tables that have a `schema_` prefix in the schema name:

    ```yaml
    schema-pattern: "schema_*"
    table-pattern: ""
    ```

- Matching all tables that have a `schema_` prefix in the schema name and a `table_` prefix in the table name:

    ```yaml
    schema-pattern = "schema_*"
    table-pattern = "table_*"
    ```
