# GUC Parameters; Index Support; Functions and Operators

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > pg_trgm > GUC Parameters; Index Support; Functions and Operators`
- Source Line Ranges: `3965-3992, 4098-4142, 7192-7255, 7305-7320, 7321-7443, 7444-7483, 7484-7491, 7492-7503, 8963-8989`
- Chunk ID: `pg16_configuration_0174_e51230b27d`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9f511eaf52c1443c32946024ee7c649ad331a2f94c92ea86581bce44309d83e0`

## Retrieval Guidance

- Use When: Configure trigram matching thresholds or index support for similarity search.
- Retrieval Keywords: pg_trgm, pg_trgm.similarity_threshold, pg_trgm.word_similarity_threshold, trigram index, GIN trigram, GiST trigram
- Follow-up Guidance: Validate threshold changes against false positives, query plans, and user-facing search behavior.
- Classification Note: The module defines GUCs and index/operator behavior controlling trigram similarity thresholds and search support.

## Official Source Content

### `intarray` Functions and Operators

The functions provided by the `intarray` module
are shown in [intarray-func-table](#intarray-func-table), the operators
in [intarray-op-table](#intarray-op-table).

| Function                         Description                         Example(s) |
| --- |
| `icount` ( `integer[]` )         integer                         Returns the number of elements in the array.                         `icount('{1,2,3}'::integer[])`         3 |
| `sort` ( `integer[]`, dir `text` )         integer[]                         Sorts the array in either ascending or descending order.         dir must be `asc`         or `desc`.                         `sort('{1,3,2}'::integer[], 'desc')`         {3,2,1} |
| `sort` ( `integer[]` )         integer[]                                  `sort_asc` ( `integer[]` )         integer[]                         Sorts in ascending order.                         `sort(array[11,77,44])`         {11,44,77} |
| `sort_desc` ( `integer[]` )         integer[]                         Sorts in descending order.                         `sort_desc(array[11,77,44])`         {77,44,11} |
| `uniq` ( `integer[]` )         integer[]                         Removes adjacent duplicates.         Often used with `sort` to remove all duplicates.                         `uniq('{1,2,2,3,1,1}'::integer[])`         {1,2,3,1}                         `uniq(sort('{1,2,3,2,1}'::integer[]))`         {1,2,3} |
| `idx` ( `integer[]`, item `integer` )         integer                         Returns index of the first array element         matching item, or 0 if no match.                         `idx(array[11,22,33,22,11], 22)`         2 |
| `subarray` ( `integer[]`, start `integer`, len `integer` )         integer[]                         Extracts the portion of the array starting at         position start, with len         elements.                         `subarray('{1,2,3,2,1}'::integer[], 2, 3)`         {2,3,2} |
| `subarray` ( `integer[]`, start `integer` )         integer[]                         Extracts the portion of the array starting at         position start.                         `subarray('{1,2,3,2,1}'::integer[], 2)`         {2,3,2,1} |
| `intset` ( `integer` )         integer[]                         Makes a single-element array.                         `intset(42)`         {42} |

| Operator                         Description |
| --- |
| `integer[]` `&&` `integer[]`         boolean                         Do arrays overlap (have at least one element in common)? |
| `integer[]` `@>` `integer[]`         boolean                         Does left array contain right array? |
| `integer[]` ` '{1,2}';

-- the same, using QUERY operator
SELECT message.mid FROM message WHERE message.sections @@ '1&2'::query_int;
```

### Functions and Operators

The `isn` module provides the standard comparison operators,
plus B-tree and hash indexing support for all these data types.  In
addition there are several specialized functions; shown in [isn-functions](#isn-functions).
In this table,
`isn` means any one of the module's data types.

| Function                         Description |
| --- |
| `isn_weak` ( `boolean` )         boolean                         Sets the weak input mode, and returns new setting. |
| `isn_weak` ()         boolean                         Returns the current status of the weak mode. |
| `make_valid` ( `isn` )         isn                         Validates an invalid number (clears the invalid flag). |
| `is_valid` ( `isn` )         boolean                         Checks for the presence of the invalid flag. |

*Weak* mode is used to be able to insert invalid data
into a table. Invalid means the check digit is wrong, not that there are
missing numbers.

Why would you want to use the weak mode? Well, it could be that
you have a huge collection of ISBN numbers, and that there are so many of
them that for weird reasons some have the wrong check digit (perhaps the
numbers were scanned from a printed list and the OCR got the numbers wrong,
perhaps the numbers were manually captured... who knows). Anyway, the point
is you might want to clean the mess up, but you still want to be able to
have all the numbers in your database and maybe use an external tool to
locate the invalid numbers in the database so you can verify the
information and validate it more easily; so for example you'd want to
select all the invalid numbers in the table.

When you insert invalid numbers in a table using the weak mode, the number
will be inserted with the corrected check digit, but it will be displayed
with an exclamation mark (`!`) at the end, for example
`0-11-000322-5!`.  This invalid marker can be checked with
the `is_valid` function and cleared with the
`make_valid` function.

You can also force the insertion of invalid numbers even when not in the
weak mode, by appending the `!` character at the end of the
number.

Another special feature is that during input, you can write
`?` in place of the check digit, and the correct check digit
will be inserted automatically.

## pg_trgm —
support for similarity of text using trigram matching

The `pg_trgm` module provides functions and operators
for determining the similarity of
alphanumeric text based on trigram matching, as
well as index operator classes that support fast searching for similar
strings.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Trigram (or Trigraph) Concepts

A trigram is a group of three consecutive characters taken
from a string.  We can measure the similarity of two strings by
counting the number of trigrams they share.  This simple idea
turns out to be very effective for measuring the similarity of
words in many natural languages.

> **Note:**

> `pg_trgm` ignores non-word characters
> (non-alphanumerics) when extracting trigrams from a string.
> Each word is considered to have two spaces
> prefixed and one space suffixed when determining the set
> of trigrams contained in the string.
> For example, the set of trigrams in the string
> "`cat`" is
> "`  c`",
> "` ca`",
> "`cat`", and
> "`at `".
> The set of trigrams in the string
> "`foo|bar`" is
> "`  f`",
> "` fo`",
> "`foo`",
> "`oo `",
> "`  b`",
> "` ba`",
> "`bar`", and
> "`ar `".
>

### Functions and Operators

The functions provided by the `pg_trgm` module
are shown in [pgtrgm-func-table](#pgtrgm-func-table), the operators
in [pgtrgm-op-table](#pgtrgm-op-table).

| Function                         Description |
| --- |
| `similarity` ( `text`, `text` )         real                         Returns a number that indicates how similar the two arguments are.         The range of the result is zero (indicating that the two strings are         completely dissimilar) to one (indicating that the two strings are         identical). |
| `show_trgm` ( `text` )         text[]                         Returns an array of all the trigrams in the given string.         (In practice this is seldom useful except for debugging.) |
| `word_similarity` ( `text`, `text` )         real                         Returns a number that indicates the greatest similarity between         the set of trigrams in the first string and any continuous extent         of an ordered set of trigrams in the second string.  For details, see         the explanation below. |
| `strict_word_similarity` ( `text`, `text` )         real                         Same as `word_similarity`, but forces         extent boundaries to match word boundaries.  Since we don't have         cross-word trigrams, this function actually returns greatest similarity         between first string and any continuous extent of words of the second         string. |
| `show_limit` ()         real                         Returns the current similarity threshold used by the `%`         operator.  This sets the minimum similarity between         two words for them to be considered similar enough to         be misspellings of each other, for example.         (*Deprecated*; instead use `SHOW`         `pg_trgm.similarity_threshold`.) |
| `set_limit` ( `real` )         real                         Sets the current similarity threshold that is used by the `%`         operator.  The threshold must be between 0 and 1 (default is 0.3).         Returns the same value passed in.         (*Deprecated*; instead use `SET`         `pg_trgm.similarity_threshold`.) |

Consider the following example:

```

### GUC Parameters

**`pg_trgm.similarity_threshold` (`real`)**
: Sets the current similarity threshold that is used by the `%`
operator.  The threshold must be between 0 and 1 (default is 0.3).

**`pg_trgm.word_similarity_threshold` (`real`)**
: Sets the current word similarity threshold that is used by the
`` operators.  The threshold
must be between 0 and 1 (default is 0.6).

**`pg_trgm.strict_word_similarity_threshold` (`real`)**
: Sets the current strict word similarity threshold that is used by the
`>` operators.  The threshold
must be between 0 and 1 (default is 0.5).

### Index Support

The `pg_trgm` module provides GiST and GIN index
operator classes that allow you to create an index over a text column for
the purpose of very fast similarity searches.  These index types support
the above-described similarity operators, and additionally support
trigram-based index searches for `LIKE`, `ILIKE`,
`~`, `~*` and `=` queries.
The similarity comparisons are case-insensitive in a default build of
`pg_trgm`.
Inequality operators are not supported.
Note that those indexes may not be as efficient as regular B-tree indexes
for equality operator.

Example:

```
CREATE TABLE test_trgm (t text);
CREATE INDEX trgm_idx ON test_trgm USING GIST (t gist_trgm_ops);
```

or

```
CREATE INDEX trgm_idx ON test_trgm USING GIN (t gin_trgm_ops);
```

`gist_trgm_ops` GiST opclass approximates a set of
trigrams as a bitmap signature.  Its optional integer parameter
`siglen` determines the
signature length in bytes.  The default length is 12 bytes.
Valid values of signature length are between 1 and 2024 bytes.  Longer
signatures lead to a more precise search (scanning a smaller fraction of the index and
fewer heap pages), at the cost of a larger index.

Example of creating such an index with a signature length of 32 bytes:

```
CREATE INDEX trgm_idx ON test_trgm USING GIST (t gist_trgm_ops(siglen=32));
```

At this point, you will have an index on the `t` column that
you can use for similarity searching.  A typical query is

```
SELECT t, similarity(t, '`word`') AS sml
FROM test_trgm
WHERE t % '`word`'
ORDER BY sml DESC, t;
```

This will return all values in the text column that are sufficiently
similar to `word`, sorted from best match to worst.  The
index will be used to make this a fast operation even over very large data
sets.

A variant of the above query is

```
SELECT t, t  '`word`' AS dist
FROM test_trgm
ORDER BY dist LIMIT 10;
```

This can be implemented quite efficiently by GiST indexes, but not
by GIN indexes.  It will usually beat the first formulation when only
a small number of the closest matches is wanted.

Also you can use an index on the `t` column for word
similarity or strict word similarity.  Typical queries are:

```
SELECT t, word_similarity('`word`', t) AS sml
FROM test_trgm
WHERE '`word`'  t AS dist
FROM test_trgm
ORDER BY dist LIMIT 10;
```

and

```
SELECT t, '`word`'  t AS dist
FROM test_trgm
ORDER BY dist LIMIT 10;
```

This can be implemented quite efficiently by GiST indexes, but not
by GIN indexes.

Beginning in PostgreSQL 9.1, these index types also support
index searches for `LIKE` and `ILIKE`, for example

```
SELECT * FROM test_trgm WHERE t LIKE '%foo%bar';
```

The index search works by extracting trigrams from the search string
and then looking these up in the index.  The more trigrams in the search
string, the more effective the index search is.  Unlike B-tree based
searches, the search string need not be left-anchored.

Beginning in PostgreSQL 9.3, these index types also support
index searches for regular-expression matches
(`~` and `~*` operators), for example

```
SELECT * FROM test_trgm WHERE t ~ '(foo|bar)';
```

The index search works by extracting trigrams from the regular expression
and then looking these up in the index.  The more trigrams that can be
extracted from the regular expression, the more effective the index search
is.  Unlike B-tree based searches, the search string need not be
left-anchored.

For both `LIKE` and regular-expression searches, keep in mind
that a pattern with no extractable trigrams will degenerate to a full-index
scan.

The choice between GiST and GIN indexing depends on the relative
performance characteristics of GiST and GIN, which are discussed elsewhere.

### Text Search Integration

Trigram matching is a very useful tool when used in conjunction
with a full text index.  In particular it can help to recognize
misspelled input words that will not be matched directly by the
full text search mechanism.

The first step is to generate an auxiliary table containing all
the unique words in the documents:

```
CREATE TABLE words AS SELECT word FROM
ts_stat('SELECT to_tsvector(''simple'', bodytext) FROM documents');
```

where `documents` is a table that has a text field
`bodytext` that we wish to search.  The reason for using
the `simple` configuration with the `to_tsvector`
function, instead of using a language-specific configuration,
is that we want a list of the original (unstemmed) words.

Next, create a trigram index on the word column:

```
CREATE INDEX words_idx ON words USING GIN (word gin_trgm_ops);
```

Now, a `SELECT` query similar to the previous example can
be used to suggest spellings for misspelled words in user search terms.
A useful extra test is to require that the selected words are also of
similar length to the misspelled word.

> **Note:**

> Since the `words` table has been generated as a separate,
> static table, it will need to be periodically regenerated so that
> it remains reasonably up-to-date with the document collection.
> Keeping it exactly current is usually unnecessary.
>

### References

GiST Development Site
[](http://www.sai.msu.su/~megera/postgres/gist/)

Tsearch2 Development Site
[](http://www.sai.msu.su/~megera/postgres/gist/tsearch/V2/)

### Authors

Oleg Bartunov oleg@sai.msu.su, Moscow, Moscow University, Russia

Teodor Sigaev teodor@sigaev.ru, Moscow, Delta-Soft Ltd.,Russia

Alexander Korotkov a.korotkov@postgrespro.ru, Moscow, Postgres Professional, Russia

Documentation: Christopher Kings-Lynne

This module is sponsored by Delta-Soft Ltd., Moscow, Russia.

### GUC Parameters

**`sepgsql.permissive` (`boolean`)**
: This parameter enables `sepgsql` to function
in permissive mode, regardless of the system setting.
The default is off.
This parameter can only be set in the `postgresql.conf`
file or on the server command line.

When this parameter is on, `sepgsql` functions
in permissive mode, even if SELinux in general is working in enforcing
mode.  This parameter is primarily useful for testing purposes.

**`sepgsql.debug_audit` (`boolean`)**
: This parameter enables the printing of audit messages regardless of
the system policy settings.
The default is off, which means that messages will be printed according
to the system settings.

The security policy of SELinux also has rules to
control whether or not particular accesses are logged.
By default, access violations are logged, but allowed
accesses are not.

This parameter forces all possible logging to be turned on, regardless
of the system policy.
