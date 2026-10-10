# psql Support; Limitations

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/09_full_text_search.md`
- Source Title: `Full Text Search`
- Source Heading Path: `Full Text Search > psql Support; Limitations`
- Source Line Ranges: `2643-2817, 2818-2844`
- Chunk ID: `pg16_fact_0158_d6a31a5fe1`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d1848e488da48982d4611becee1092497967566465750f33aea6eb4e413307be`

## Retrieval Guidance

- Use When: Need facts about psql helpers or constraints of the full-text search feature.
- Retrieval Keywords: psql, full text search support, limitations, text search display
- Follow-up Guidance: Use operational records only when the issue is performance or unexpected matching behavior.
- Classification Note: Describes psql display support and documented limitations for PostgreSQL full-text search.

## Official Source Content

## psql Support

Information about text search configuration objects can be obtained
in psql using a set of commands:

```
\dF{d,p,t}+ PATTERN
```

An optional `+` produces more details.

The optional parameter `PATTERN` can be the name of
a text search object, optionally schema-qualified.  If
`PATTERN` is omitted then information about all
visible objects will be displayed.  `PATTERN` can be a
regular expression and can provide *separate* patterns
for the schema and object names.  The following examples illustrate this:

```
=> \dF *fulltext*
List of text search configurations
Schema |  Name        | Description
--------+--------------+-------------
public | fulltext_cfg |
```

```
=> \dF *.fulltext*
List of text search configurations
Schema   |  Name        | Description
----------+----------------------------
fulltext | fulltext_cfg |
public   | fulltext_cfg |
```

The available commands are:

**`\dF+ PATTERN`**
: List text search configurations (add `+` for more detail).

```
=> \dF russian
List of text search configurations
Schema   |  Name   |            Description
------------+---------+------------------------------------
pg_catalog | russian | configuration for russian language

=> \dF+ russian
Text search configuration "pg_catalog.russian"
Parser: "pg_catalog.default"
Token      | Dictionaries
-----------------+--------------
asciihword      | english_stem
asciiword       | english_stem
email           | simple
file            | simple
float           | simple
host            | simple
hword           | russian_stem
hword_asciipart | english_stem
hword_numpart   | simple
hword_part      | russian_stem
int             | simple
numhword        | simple
numword         | simple
sfloat          | simple
uint            | simple
url             | simple
url_path        | simple
version         | simple
word            | russian_stem
```

**`\dFd+ PATTERN`**
: List text search dictionaries (add `+` for more detail).

```
=> \dFd
List of text search dictionaries
Schema   |      Name       |                        Description
------------+-----------------+-----------------------------------------------------------
pg_catalog | arabic_stem     | snowball stemmer for arabic language
pg_catalog | armenian_stem   | snowball stemmer for armenian language
pg_catalog | basque_stem     | snowball stemmer for basque language
pg_catalog | catalan_stem    | snowball stemmer for catalan language
pg_catalog | danish_stem     | snowball stemmer for danish language
pg_catalog | dutch_stem      | snowball stemmer for dutch language
pg_catalog | english_stem    | snowball stemmer for english language
pg_catalog | finnish_stem    | snowball stemmer for finnish language
pg_catalog | french_stem     | snowball stemmer for french language
pg_catalog | german_stem     | snowball stemmer for german language
pg_catalog | greek_stem      | snowball stemmer for greek language
pg_catalog | hindi_stem      | snowball stemmer for hindi language
pg_catalog | hungarian_stem  | snowball stemmer for hungarian language
pg_catalog | indonesian_stem | snowball stemmer for indonesian language
pg_catalog | irish_stem      | snowball stemmer for irish language
pg_catalog | italian_stem    | snowball stemmer for italian language
pg_catalog | lithuanian_stem | snowball stemmer for lithuanian language
pg_catalog | nepali_stem     | snowball stemmer for nepali language
pg_catalog | norwegian_stem  | snowball stemmer for norwegian language
pg_catalog | portuguese_stem | snowball stemmer for portuguese language
pg_catalog | romanian_stem   | snowball stemmer for romanian language
pg_catalog | russian_stem    | snowball stemmer for russian language
pg_catalog | serbian_stem    | snowball stemmer for serbian language
pg_catalog | simple          | simple dictionary: just lower case and check for stopword
pg_catalog | spanish_stem    | snowball stemmer for spanish language
pg_catalog | swedish_stem    | snowball stemmer for swedish language
pg_catalog | tamil_stem      | snowball stemmer for tamil language
pg_catalog | turkish_stem    | snowball stemmer for turkish language
pg_catalog | yiddish_stem    | snowball stemmer for yiddish language
```

**`\dFp+ PATTERN`**
: List text search parsers (add `+` for more detail).

```
=> \dFp
List of text search parsers
Schema   |  Name   |     Description
------------+---------+---------------------
pg_catalog | default | default word parser
=> \dFp+
Text search parser "pg_catalog.default"
Method      |    Function    | Description
-----------------+----------------+-------------
Start parse     | prsd_start     |
Get next token  | prsd_nexttoken |
End parse       | prsd_end       |
Get headline    | prsd_headline  |
Get token types | prsd_lextype   |

Token types for parser "pg_catalog.default"
Token name    |               Description
-----------------+------------------------------------------
asciihword      | Hyphenated word, all ASCII
asciiword       | Word, all ASCII
blank           | Space symbols
email           | Email address
entity          | XML entity
file            | File or path name
float           | Decimal notation
host            | Host
hword           | Hyphenated word, all letters
hword_asciipart | Hyphenated word part, all ASCII
hword_numpart   | Hyphenated word part, letters and digits
hword_part      | Hyphenated word part, all letters
int             | Signed integer
numhword        | Hyphenated word, letters and digits
numword         | Word, letters and digits
protocol        | Protocol head
sfloat          | Scientific notation
tag             | XML tag
uint            | Unsigned integer
url             | URL
url_path        | URL path
version         | Version number
word            | Word, all letters
(23 rows)
```

**`\dFt+ PATTERN`**
: List text search templates (add `+` for more detail).

```
=> \dFt
List of text search templates
Schema   |   Name    |                        Description
------------+-----------+-----------------------------------------------------------
pg_catalog | ispell    | ispell dictionary
pg_catalog | simple    | simple dictionary: just lower case and check for stopword
pg_catalog | snowball  | snowball stemmer
pg_catalog | synonym   | synonym dictionary: replace word by its synonym
pg_catalog | thesaurus | thesaurus dictionary: phrase by phrase substitution
```

## Limitations

The current limitations of PostgreSQL's
text search features are:

- The length of each lexeme must be less than 2 kilobytes
- The length of a `tsvector` (lexemes + positions) must be
less than 1 megabyte
- The number of lexemes must be less than
2^64
- Position values in `tsvector` must be greater than 0 and
no more than 16,383
- The match distance in a ``
(FOLLOWED BY) `tsquery` operator cannot be more than
16,384
- No more than 256 positions per lexeme
- The number of nodes (lexemes + operators) in a `tsquery`
must be less than 32,768

For comparison, the PostgreSQL 8.1 documentation
contained 10,441 unique words, a total of 335,420 words, and the most
frequent word "postgresql" was mentioned 6,127 times in 655
documents.

Another example — the PostgreSQL mailing
list archives contained 910,989 unique words with 57,491,343 lexemes in
461,020 messages.
