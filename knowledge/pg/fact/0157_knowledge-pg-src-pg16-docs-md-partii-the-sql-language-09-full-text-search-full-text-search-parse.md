# Parsers; Dictionaries; Stop Words; Simple Dictionary; Synonym Dictionary; Thesaurus Dictionary; Ispell Dictionary; Snowball Dictionary

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/09_full_text_search.md`
- Source Title: `Full Text Search`
- Source Heading Path: `Full Text Search > Parsers; Dictionaries; Stop Words; Simple Dictionary; Synonym Dictionary; Thesaurus Dictionary; Ispell Dictionary; Snowball Dictionary`
- Source Line Ranges: `1420-1521, 1522-1852, 2010-2167, 2168-2198`
- Chunk ID: `pg16_fact_0157_16e85fca5e`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `40d17bae816abc22b62bea144308b52a1dc441de952940d029b59d24c9d039d3`

## Retrieval Guidance

- Use When: Need facts about full-text parser and dictionary mechanics.
- Retrieval Keywords: text search parser, dictionary, stop words, synonym, thesaurus, Ispell, Snowball
- Follow-up Guidance: Use Testing and Debugging Text Search to confirm actual token and lexeme output.
- Classification Note: Explains full-text parser and dictionary object behavior, dictionary templates, stop words, synonyms, thesaurus rules, Ispell, and Snowball stemming.

## Official Source Content

## Parsers

Text search parsers are responsible for splitting raw document text
into *tokens* and identifying each token's type, where
the set of possible types is defined by the parser itself.
Note that a parser does not modify the text at all — it simply
identifies plausible word boundaries.  Because of this limited scope,
there is less need for application-specific custom parsers than there is
for custom dictionaries.  At present PostgreSQL
provides just one built-in parser, which has been found to be useful for a
wide range of applications.

The built-in parser is named `pg_catalog.default`.
It recognizes 23 token types, shown in [textsearch-default-parser](#textsearch-default-parser).

| Alias | Description | Example |
| --- | --- | --- |
| `asciiword` | Word, all ASCII letters | `elephant` |
| `word` | Word, all letters | `maana` |
| `numword` | Word, letters and digits | `beta1` |
| `asciihword` | Hyphenated word, all ASCII | `up-to-date` |
| `hword` | Hyphenated word, all letters | `lgico-matemtica` |
| `numhword` | Hyphenated word, letters and digits | `postgresql-beta1` |
| `hword_asciipart` | Hyphenated word part, all ASCII | `postgresql` in the context `postgresql-beta1` |
| `hword_part` | Hyphenated word part, all letters | `lgico` or `matemtica`        in the context `lgico-matemtica` |
| `hword_numpart` | Hyphenated word part, letters and digits | `beta1` in the context        `postgresql-beta1` |
| `email` | Email address | `foo@example.com` |
| `protocol` | Protocol head | `http://` |
| `url` | URL | `example.com/stuff/index.html` |
| `host` | Host | `example.com` |
| `url_path` | URL path | `/stuff/index.html`, in the context of a URL |
| `file` | File or path name | `/usr/local/foo.txt`, if not within a URL |
| `sfloat` | Scientific notation | `-1.234e56` |
| `float` | Decimal notation | `-1.234` |
| `int` | Signed integer | `-1234` |
| `uint` | Unsigned integer | `1234` |
| `version` | Version number | `8.3.0` |
| `tag` | XML tag | `` |
| `entity` | XML entity | `` |
| `blank` | Space symbols | (any whitespace or punctuation not otherwise recognized) |

> **Note:**

> The parser's notion of a "letter" is determined by the database's
> locale setting, specifically `lc_ctype`.  Words containing
> only the basic ASCII letters are reported as a separate token type,
> since it is sometimes useful to distinguish them.  In most European
> languages, token types `word` and `asciiword`
> should be treated alike.
>

>

> `email` does not support all valid email characters as
> defined by [RFC 5322](https://datatracker.ietf.org/doc/html/rfc5322).
> Specifically, the only non-alphanumeric characters supported for
> email user names are period, dash, and underscore.
>

>

> `tag` does not support all valid tag names as defined by
> [W3C Recommendation, XML](https://www.w3.org/TR/xml/).
> Specifically, the only tag names supported are those starting with an
> ASCII letter, underscore, or colon, and containing only letters, digits,
> hyphens, underscores, periods, and colons. `tag` also
> includes XML comments starting with `<!--` and ending
> with `-->`, and XML declarations (but note that this
> includes anything starting with `<?x` and ending with
> `>`).
>

It is possible for the parser to produce overlapping tokens from the same
piece of text.  As an example, a hyphenated word will be reported both
as the entire word and as each component:

```
SELECT alias, description, token FROM ts_debug('foo-bar-beta1');
alias      |               description                |     token
-----------------+------------------------------------------+---------------
numhword        | Hyphenated word, letters and digits      | foo-bar-beta1
hword_asciipart | Hyphenated word part, all ASCII          | foo
blank           | Space symbols                            | -
hword_asciipart | Hyphenated word part, all ASCII          | bar
blank           | Space symbols                            | -
hword_numpart   | Hyphenated word part, letters and digits | beta1
```

This behavior is desirable since it allows searches to work for both
the whole compound word and for components.  Here is another
instructive example:

```
SELECT alias, description, token FROM ts_debug('http://example.com/stuff/index.html');
alias   |  description  |            token
----------+---------------+------------------------------
protocol | Protocol head | http://
url      | URL           | example.com/stuff/index.html
host     | Host          | example.com
url_path | URL path      | /stuff/index.html
```

## Dictionaries

Dictionaries are used to eliminate words that should not be considered in a
search (*stop words*), and to *normalize* words so
that different derived forms of the same word will match.  A successfully
normalized word is called a *lexeme*.  Aside from
improving search quality, normalization and removal of stop words reduce the
size of the `tsvector` representation of a document, thereby
improving performance.  Normalization does not always have linguistic meaning
and usually depends on application semantics.

Some examples of normalization:

- Linguistic — Ispell dictionaries try to reduce input words to a
normalized form; stemmer dictionaries remove word endings
- URL locations can be canonicalized to make
equivalent URLs match:

http://www.pgsql.ru/db/mw/index.html
- http://www.pgsql.ru/db/mw/
- http://www.pgsql.ru/db/../db/mw/index.html

Color names can be replaced by their hexadecimal values, e.g.,
`red, green, blue, magenta -> FF0000, 00FF00, 0000FF, FF00FF`

If indexing numbers, we can
remove some fractional digits to reduce the range of possible
numbers, so for example *3.14*159265359,
*3.14*15926, *3.14* will be the same
after normalization if only two digits are kept after the decimal point.

A dictionary is a program that accepts a token as
input and returns:

- an array of lexemes if the input token is known to the dictionary
(notice that one token can produce more than one lexeme)
- a single lexeme with the `TSL_FILTER` flag set, to replace
the original token with a new token to be passed to subsequent
dictionaries (a dictionary that does this is called a
*filtering dictionary*)
- an empty array if the dictionary knows the token, but it is a stop word
- `NULL` if the dictionary does not recognize the input token

PostgreSQL provides predefined dictionaries for
many languages.  There are also several predefined templates that can be
used to create new dictionaries with custom parameters.  Each predefined
dictionary template is described below.  If no existing
template is suitable, it is possible to create new ones; see the
`contrib/` area of the PostgreSQL distribution
for examples.

A text search configuration binds a parser together with a set of
dictionaries to process the parser's output tokens.  For each token
type that the parser can return, a separate list of dictionaries is
specified by the configuration.  When a token of that type is found
by the parser, each dictionary in the list is consulted in turn,
until some dictionary recognizes it as a known word.  If it is identified
as a stop word, or if no dictionary recognizes the token, it will be
discarded and not indexed or searched for.
Normally, the first dictionary that returns a non-`NULL`
output determines the result, and any remaining dictionaries are not
consulted; but a filtering dictionary can replace the given word
with a modified word, which is then passed to subsequent dictionaries.

The general rule for configuring a list of dictionaries
is to place first the most narrow, most specific dictionary, then the more
general dictionaries, finishing with a very general dictionary, like
a Snowball stemmer or `simple`, which
recognizes everything.  For example, for an astronomy-specific search
(`astro_en` configuration) one could bind token type
`asciiword` (ASCII word) to a synonym dictionary of astronomical
terms, a general English dictionary and a Snowball English
stemmer:

```
ALTER TEXT SEARCH CONFIGURATION astro_en
ADD MAPPING FOR asciiword WITH astrosyn, english_ispell, english_stem;
```

A filtering dictionary can be placed anywhere in the list, except at the
end where it'd be useless.  Filtering dictionaries are useful to partially
normalize words to simplify the task of later dictionaries.  For example,
a filtering dictionary could be used to remove accents from accented
letters, as is done by the [unaccent](#unaccent) module.

### Stop Words

Stop words are words that are very common, appear in almost every
document, and have no discrimination value. Therefore, they can be ignored
in the context of full text searching. For example, every English text
contains words like `a` and `the`, so it is
useless to store them in an index.  However, stop words do affect the
positions in `tsvector`, which in turn affect ranking:

```
SELECT to_tsvector('english', 'in the list of stop words');
to_tsvector
----------------------------
'list':3 'stop':5 'word':6
```

The missing positions 1,2,4 are because of stop words.  Ranks
calculated for documents with and without stop words are quite different:

```
SELECT ts_rank_cd (to_tsvector('english', 'in the list of stop words'), to_tsquery('list & stop'));
ts_rank_cd
------------
0.05

SELECT ts_rank_cd (to_tsvector('english', 'list stop words'), to_tsquery('list & stop'));
ts_rank_cd
------------
0.1
```

It is up to the specific dictionary how it treats stop words. For example,
`ispell` dictionaries first normalize words and then
look at the list of stop words, while `Snowball` stemmers
first check the list of stop words. The reason for the different
behavior is an attempt to decrease noise.

### Simple Dictionary

The `simple` dictionary template operates by converting the
input token to lower case and checking it against a file of stop words.
If it is found in the file then an empty array is returned, causing
the token to be discarded.  If not, the lower-cased form of the word
is returned as the normalized lexeme.  Alternatively, the dictionary
can be configured to report non-stop-words as unrecognized, allowing
them to be passed on to the next dictionary in the list.

Here is an example of a dictionary definition using the `simple`
template:

```
CREATE TEXT SEARCH DICTIONARY public.simple_dict (
TEMPLATE = pg_catalog.simple,
STOPWORDS = english
);
```

Here, `english` is the base name of a file of stop words.
The file's full name will be
`$SHAREDIR/tsearch_data/english.stop`,
where `$SHAREDIR` means the
PostgreSQL installation's shared-data directory,
often `/usr/local/share/postgresql` (use `pg_config
--sharedir` to determine it if you're not sure).
The file format is simply a list
of words, one per line.  Blank lines and trailing spaces are ignored,
and upper case is folded to lower case, but no other processing is done
on the file contents.

Now we can test our dictionary:

```
SELECT ts_lexize('public.simple_dict', 'YeS');
ts_lexize
-----------
{yes}

SELECT ts_lexize('public.simple_dict', 'The');
ts_lexize
-----------
{}
```

We can also choose to return `NULL`, instead of the lower-cased
word, if it is not found in the stop words file.  This behavior is
selected by setting the dictionary's `Accept` parameter to
`false`.  Continuing the example:

```
ALTER TEXT SEARCH DICTIONARY public.simple_dict ( Accept = false );

SELECT ts_lexize('public.simple_dict', 'YeS');
ts_lexize
-----------

SELECT ts_lexize('public.simple_dict', 'The');
ts_lexize
-----------
{}
```

With the default setting of `Accept` = `true`,
it is only useful to place a `simple` dictionary at the end
of a list of dictionaries, since it will never pass on any token to
a following dictionary.  Conversely, `Accept` = `false`
is only useful when there is at least one following dictionary.

> **Caution:**

> Most types of dictionaries rely on configuration files, such as files of
> stop words.  These files *must* be stored in UTF-8 encoding.
> They will be translated to the actual database encoding, if that is
> different, when they are read into the server.
>

> **Caution:**

> Normally, a database session will read a dictionary configuration file
> only once, when it is first used within the session.  If you modify a
> configuration file and want to force existing sessions to pick up the
> new contents, issue an `ALTER TEXT SEARCH DICTIONARY` command
> on the dictionary.  This can be a "dummy" update that doesn't
> actually change any parameter values.
>

### Synonym Dictionary

This dictionary template is used to create dictionaries that replace a
word with a synonym. Phrases are not supported (use the thesaurus
template ([textsearch-thesaurus](#textsearch-thesaurus)) for that).  A synonym
dictionary can be used to overcome linguistic problems, for example, to
prevent an English stemmer dictionary from reducing the word "Paris" to
"pari".  It is enough to have a `Paris paris` line in the
synonym dictionary and put it before the `english_stem`
dictionary.  For example:

```
SELECT * FROM ts_debug('english', 'Paris');
alias   |   description   | token |  dictionaries  |  dictionary  | lexemes
-----------+-----------------+-------+----------------+--------------+---------
asciiword | Word, all ASCII | Paris | {english_stem} | english_stem | {pari}

CREATE TEXT SEARCH DICTIONARY my_synonym (
TEMPLATE = synonym,
SYNONYMS = my_synonyms
);

ALTER TEXT SEARCH CONFIGURATION english
ALTER MAPPING FOR asciiword
WITH my_synonym, english_stem;

SELECT * FROM ts_debug('english', 'Paris');
alias   |   description   | token |       dictionaries        | dictionary | lexemes
-----------+-----------------+-------+---------------------------+------------+---------
asciiword | Word, all ASCII | Paris | {my_synonym,english_stem} | my_synonym | {paris}
```

The only parameter required by the `synonym` template is
`SYNONYMS`, which is the base name of its configuration file
— `my_synonyms` in the above example.
The file's full name will be
`$SHAREDIR/tsearch_data/my_synonyms.syn`
(where `$SHAREDIR` means the
PostgreSQL installation's shared-data directory).
The file format is just one line
per word to be substituted, with the word followed by its synonym,
separated by white space.  Blank lines and trailing spaces are ignored.

The `synonym` template also has an optional parameter
`CaseSensitive`, which defaults to `false`.  When
`CaseSensitive` is `false`, words in the synonym file
are folded to lower case, as are input tokens.  When it is
`true`, words and tokens are not folded to lower case,
but are compared as-is.

An asterisk (`*`) can be placed at the end of a synonym
in the configuration file.  This indicates that the synonym is a prefix.
The asterisk is ignored when the entry is used in
`to_tsvector()`, but when it is used in
`to_tsquery()`, the result will be a query item with
the prefix match marker (see
[textsearch-parsing-queries](#textsearch-parsing-queries)).
For example, suppose we have these entries in
`$SHAREDIR/tsearch_data/synonym_sample.syn`:

```
postgres        pgsql
postgresql      pgsql
postgre pgsql
gogle   googl
indices index*
```

Then we will get these results:

```
mydb=# CREATE TEXT SEARCH DICTIONARY syn (template=synonym, synonyms='synonym_sample');
mydb=# SELECT ts_lexize('syn', 'indices');
ts_lexize
-----------
{index}
(1 row)

mydb=# CREATE TEXT SEARCH CONFIGURATION tst (copy=simple);
mydb=# ALTER TEXT SEARCH CONFIGURATION tst ALTER MAPPING FOR asciiword WITH syn;
mydb=# SELECT to_tsvector('tst', 'indices');
to_tsvector
-------------
'index':1
(1 row)

mydb=# SELECT to_tsquery('tst', 'indices');
to_tsquery
------------
'index':*
(1 row)

mydb=# SELECT 'indexes are very useful'::tsvector;
tsvector
---------------------------------
'are' 'indexes' 'useful' 'very'
(1 row)

mydb=# SELECT 'indexes are very useful'::tsvector @@ to_tsquery('tst', 'indices');
?column?
----------
t
(1 row)
```

### Thesaurus Dictionary

A thesaurus dictionary (sometimes abbreviated as TZ) is
a collection of words that includes information about the relationships
of words and phrases, i.e., broader terms (BT), narrower
terms (NT), preferred terms, non-preferred terms, related
terms, etc.

Basically a thesaurus dictionary replaces all non-preferred terms by one
preferred term and, optionally, preserves the original terms for indexing
as well.  PostgreSQL's current implementation of the
thesaurus dictionary is an extension of the synonym dictionary with added
*phrase* support.  A thesaurus dictionary requires
a configuration file of the following format:

```

### Ispell Dictionary

The Ispell dictionary template supports
*morphological dictionaries*, which can normalize many
different linguistic forms of a word into the same lexeme.  For example,
an English Ispell dictionary can match all declensions and
conjugations of the search term `bank`, e.g.,
`banking`, `banked`, `banks`,
`banks'`, and `bank's`.

The standard PostgreSQL distribution does
not include any Ispell configuration files.
Dictionaries for a large number of languages are available from [Ispell](https://www.cs.hmc.edu/~geoff/ispell.html).
Also, some more modern dictionary file formats are supported — [MySpell](https://en.wikipedia.org/wiki/MySpell) (OO < 2.0.1)
and [Hunspell](https://hunspell.github.io/)
(OO >= 2.0.2).  A large list of dictionaries is available on the [OpenOffice
Wiki](https://wiki.openoffice.org/wiki/Dictionaries).

To create an Ispell dictionary perform these steps:

- download dictionary configuration files. OpenOffice
extension files have the `.oxt` extension. It is necessary
to extract `.aff` and `.dic` files, change
extensions to `.affix` and `.dict`. For some
dictionary files it is also needed to convert characters to the UTF-8
encoding with commands (for example, for a Norwegian language dictionary):

```
iconv -f ISO_8859-1 -t UTF-8 -o nn_no.affix nn_NO.aff
iconv -f ISO_8859-1 -t UTF-8 -o nn_no.dict nn_NO.dic
```
- copy files to the `$SHAREDIR/tsearch_data` directory
- load files into PostgreSQL with the following command:

```
CREATE TEXT SEARCH DICTIONARY english_hunspell (
TEMPLATE = ispell,
DictFile = en_us,
AffFile = en_us,
Stopwords = english);
```

Here, `DictFile`, `AffFile`, and `StopWords`
specify the base names of the dictionary, affixes, and stop-words files.
The stop-words file has the same format explained above for the
`simple` dictionary type.  The format of the other files is
not specified here but is available from the above-mentioned web sites.

Ispell dictionaries usually recognize a limited set of words, so they
should be followed by another broader dictionary; for
example, a Snowball dictionary, which recognizes everything.

The `.affix` file of Ispell has the following
structure:

```
prefixes
flag *A:
.           >   RE      # As in enter > reenter
suffixes
flag T:
E           >   ST      # As in late > latest
[^AEIOU]Y   >   -Y,IEST # As in dirty > dirtiest
[AEIOU]Y    >   EST     # As in gray > grayest
[^EY]       >   EST     # As in small > smallest
```

And the `.dict` file has the following structure:

```
lapse/ADGRS
lard/DGRS
large/PRTY
lark/MRS
```

Format of the `.dict` file is:

```
basic_form/affix_class_name
```

In the `.affix` file every affix flag is described in the
following format:

```
condition > [-stripping_letters,] adding_affix
```

Here, condition has a format similar to the format of regular expressions.
It can use groupings `[...]` and `[^...]`.
For example, `[AEIOU]Y` means that the last letter of the word
is `"y"` and the penultimate letter is `"a"`,
`"e"`, `"i"`, `"o"` or `"u"`.
`[^EY]` means that the last letter is neither `"e"`
nor `"y"`.

Ispell dictionaries support splitting compound words;
a useful feature.
Notice that the affix file should specify a special flag using the
`compoundwords controlled` statement that marks dictionary
words that can participate in compound formation:

```
compoundwords  controlled z
```

Here are some examples for the Norwegian language:

```
SELECT ts_lexize('norwegian_ispell', 'overbuljongterningpakkmesterassistent');
{over,buljong,terning,pakk,mester,assistent}
SELECT ts_lexize('norwegian_ispell', 'sjokoladefabrikk');
{sjokoladefabrikk,sjokolade,fabrikk}
```

MySpell format is a subset of Hunspell.
The `.affix` file of Hunspell has the following
structure:

```
PFX A Y 1
PFX A   0     re         .
SFX T N 4
SFX T   0     st         e
SFX T   y     iest       [^aeiou]y
SFX T   0     est        [aeiou]y
SFX T   0     est        [^ey]
```

The first line of an affix class is the header. Fields of an affix rules are
listed after the header:

- parameter name (PFX or SFX)
- flag (name of the affix class)
- stripping characters from beginning (at prefix) or end (at suffix) of the
word
- adding affix
- condition that has a format similar to the format of regular expressions.

The `.dict` file looks like the `.dict` file of
Ispell:

```
larder/M
lardy/RT
large/RSPMYT
largehearted
```

> **Note:**

> MySpell does not support compound words.
> Hunspell has sophisticated support for compound words. At
> present, PostgreSQL implements only the basic
> compound word operations of Hunspell.
>

### Snowball Dictionary

The Snowball dictionary template is based on a project
by Martin Porter, inventor of the popular Porter's stemming algorithm
for the English language.  Snowball now provides stemming algorithms for
many languages (see the [Snowball
site](https://snowballstem.org/) for more information).  Each algorithm understands how to
reduce common variant forms of words to a base, or stem, spelling within
its language.  A Snowball dictionary requires a `language`
parameter to identify which stemmer to use, and optionally can specify a
`stopword` file name that gives a list of words to eliminate.
(PostgreSQL's standard stopword lists are also
provided by the Snowball project.)
For example, there is a built-in definition equivalent to

```
CREATE TEXT SEARCH DICTIONARY english_stem (
TEMPLATE = snowball,
Language = english,
StopWords = english
);
```

The stopword file format is the same as already explained.

A Snowball dictionary recognizes everything, whether
or not it is able to simplify the word, so it should be placed
at the end of the dictionary list. It is useless to have it
before any other dictionary because a token will never pass through it to
the next dictionary.
