# When Color is Used; Configuring the Colors

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/13_color_support.md`
- Source Title: `13 color support`
- Source Heading Path: `Color Support > When Color is Used; Configuring the Colors`
- Source Line Ranges: `6-16, 17-55`
- Chunk ID: `pg16_configuration_0177_594f56d2c8`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2fb7f0e07fcd4117bade9752a715db5611cb3a5abe3d8c223ca5525abf6f2462`

## Retrieval Guidance

- Use When: Configure PostgreSQL command-line color output behavior.
- Retrieval Keywords: color support, PG_COLOR, PG_COLORS, terminal color, psql color, environment variables
- Follow-up Guidance: Treat as client/tool presentation configuration, not server behavior.
- Classification Note: The appendix defines environment variables and syntax for configuring colorized output in PostgreSQL tools.

## Official Source Content

## When Color is Used

To use colorized output, set the environment variable
`PG_COLOR`
as follows:

1. If the value is `always`, then color is used.
2. If the value is `auto` and the standard error stream
is associated with a terminal device, then color is used.
3. Otherwise, color is not used.

## Configuring the Colors

The actual colors to be used are configured using the environment variable
`PG_COLORS`
(note plural).  The value is a colon-separated list of
``key`=`value``
pairs.  The keys specify what the color is to be used for.  The values are
SGR (Select Graphic Rendition) specifications, which are interpreted by the
terminal.

The following keys are currently in use:

**`error`**
: used to highlight the text "error" in error messages

**`warning`**
: used to highlight the text "warning" in warning
messages

**`note`**
: used to highlight the text "detail" and
"hint" in such messages

**`locus`**
: used to highlight location information (e.g., program name and
file name) in messages

The default value is
`error=01;31:warning=01;35:note=01;36:locus=01`
(`01;31` = bold red, `01;35` = bold
magenta, `01;36` = bold cyan, `01` = bold
default color).

> **Tip:**

> This color specification format is also used by other software packages
> such as GCC, GNU
> coreutils, and GNU grep.
>
