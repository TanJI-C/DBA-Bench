# Creating XML Values

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/05_data_types.md`
- Source Title: `Data Types`
- Source Heading Path: `Data Types > XML Type > Creating XML Values`
- Source Line Ranges: `2281-2319`
- Chunk ID: `pg16_configuration_0187_3ca1d12b6d`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `26d4d70f199e676f2cfad32999bdf3dc884d88fad92d6b54e76ff93382574a41`

## Retrieval Guidance

- Use When: Need to answer why XML input is interpreted as document or content.
- Retrieval Keywords: SET XML OPTION, xmloption, XML DOCUMENT, XML CONTENT, xmlparse
- Follow-up Guidance: Check xmloption before relying on implicit XML parsing behavior.
- Classification Note: Explains SET XML OPTION and xmloption behavior for DOCUMENT versus CONTENT interpretation.

## Official Source Content

## XML Type

The `xml` data type can be used to store XML data.  Its
advantage over storing XML data in a `text` field is that it
checks the input values for well-formedness, and there are support
functions to perform type-safe operations on it; see [functions-xml](#functions-xml).  Use of this data type requires the
installation to have been built with `configure
--with-libxml`.

The `xml` type can store well-formed
"documents", as defined by the XML standard, as well
as "content" fragments, which are defined by reference
to the more permissive
["document node"](https://www.w3.org/TR/2010/REC-xpath-datamodel-20101214/#DocumentNode)
of the XQuery and XPath data model.
Roughly, this means that content fragments can have
more than one top-level element or character node.  The expression
``xmlvalue` IS DOCUMENT`
can be used to evaluate whether a particular `xml`
value is a full document or only a content fragment.

Limits and compatibility notes for the `xml` data type
can be found in [xml-limits-conformance](#xml-limits-conformance).

### Creating XML Values

To produce a value of type `xml` from character data,
use the function
`xmlparse`:

```
XMLPARSE ( { DOCUMENT | CONTENT } `value`)
```

Examples:

```

XMLPARSE (DOCUMENT '
