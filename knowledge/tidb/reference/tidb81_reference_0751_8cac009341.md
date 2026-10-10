# Table filter syntax rules and pattern forms

## Knowledge Metadata

- Knowledge Type: `reference`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/table-filter.md`
- Source Title: `Table Filter`
- Source Heading Path: `Table Filter > Syntax | Table Filter > Syntax > Plain table names | Table Filter > Syntax > Wildcards | Table Filter > Syntax > File import | Table Filter > Syntax > Comments and blank lines | Table Filter > Syntax > Exclusion | Table Filter > Syntax > Escape character | Table Filter > Syntax > Quoted identifier | Table Filter > Syntax > Regular expression`
- Source Line Ranges: `84-220`
- Source Scope: `self_managed`
- Primary Component: `shared`
- Related Components: none
- Topic Tags: `syntax`, `wildcards`, `file-import`, `comments`, `exclusion`, `escaping`, `quoted-identifiers`, `regular-expressions`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_reference_0751_8cac009341`
- Source ID: `tidb-docs-8.1:table-filter.md#syntax`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `1b893754fa29695f271d9052e8661821fc2c16272687e2771e020987b0961c5d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/table-filter#syntax
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/table-filter.md

## Retrieval Guidance

- Use When: Use this when looking for the exact table filter rule syntax, including wildcards, exclusions, escaping, quoted identifiers, file import, comments, and regular expressions.
- Retrieval Keywords: schema pattern, table pattern, plain table names, wildcards, fnmatch(3), *, ?, [a-z], [!a-z], @config/filter.txt, file import, comments and blank lines, leading #, syntax error, exclusion, !*.Password, escape character, db\.with\.dots.*, quoted identifier, "db.with.dots"."tbl\1", `db.with.dots`.`tbl\2`, regular expression, /^db\d{2,}$/./^tbl\d{2,}$/, Go dialect, \/
- Follow-up Guidance: It also states restrictions such as no nested file import, prohibited backslash sequences, no partial quoted identifiers, and every slash in regular expressions must be escaped.
- Classification Note: This is reference content because it defines the formal syntax and matching forms for table filter rules.

## Official Source Content

## Syntax
### Plain table names

Each table filter rule consists of a "schema pattern" and a "table pattern", separated by a dot (`.`). Tables whose fully-qualified name matches the rules are accepted.

```
db1.tbl1
db2.tbl2
db3.tbl3
```

A plain name must only consist of valid [identifier characters](https://docs.pingcap.com/tidb/stable/schema-object-names), such as:

* digits (`0` to `9`)
* letters (`a` to `z`, `A` to `Z`)
* `$`
* `_`
* non ASCII characters (U+0080 to U+10FFFF)

All other ASCII characters are reserved. Some punctuations have special meanings, as described in the next section.
### Wildcards

Each part of the name can be a wildcard symbol described in [fnmatch(3)](https://pubs.opengroup.org/onlinepubs/9699919799/utilities/V3_chap02.html#tag_18_13):

* `*` — matches zero or more characters
* `?` — matches one character
* `[a-z]` — matches one character between "a" and "z" inclusively
* `[!a-z]` — matches one character except "a" to "z".

```
db[0-9].tbl[0-9a-f][0-9a-f]
data.*
*.backup_*
```

"Character" here means a Unicode code point, such as:

* U+00E9 (é) is 1 character.
* U+0065 U+0301 (é) are 2 characters.
* U+1F926 U+1F3FF U+200D U+2640 U+FE0F (🤦🏿‍♀️) are 5 characters.
### File import

To import a file as the filter rule, include an `@` at the beginning of the rule to specify the file name. The table filter parser treats each line of the imported file as additional filter rules.

For example, if a file `config/filter.txt` has the following content:

```
employees.*
*.WorkOrder
```

the following two invocations are equivalent:

```bash
tiup dumpling -f '@config/filter.txt'
tiup dumpling -f 'employees.*' -f '*.WorkOrder'
```

A filter file cannot further import another file.
### Comments and blank lines

Inside a filter file, leading and trailing white-spaces of every line are trimmed. Furthermore, blank lines (empty strings) are ignored.

A leading `#` marks a comment and is ignored. `#` not at start of line is considered syntax error.

```
# this line is a comment
db.table   # but this part is not comment and may cause error
```
### Exclusion

An `!` at the beginning of the rule means the pattern after it is used to exclude tables from being processed. This effectively turns the filter into a block list.

```
*.*
#^ note: must add the *.* to include all tables first
!*.Password
!employees.salaries
```
### Escape character

To turn a special character into an identifier character, precede it with a backslash `\`.

```
db\.with\.dots.*
```

For simplicity and future compatibility, the following sequences are prohibited:

* `\` at the end of the line after trimming whitespaces (use `[ ]` to match a literal whitespace at the end).
* `\` followed by any ASCII alphanumeric character (`[0-9a-zA-Z]`). In particular, C-like escape sequences like `\0`, `\r`, `\n` and `\t` currently are meaningless.
### Quoted identifier

Besides `\`, special characters can also be suppressed by quoting using `"` or `` ` ``.

```
"db.with.dots"."tbl\1"
`db.with.dots`.`tbl\2`
```

The quotation mark can be included within an identifier by doubling itself.

```
"foo""bar".`foo``bar`
# equivalent to:
foo\"bar.foo\`bar
```

Quoted identifiers cannot span multiple lines.

It is invalid to partially quote an identifier:

```
"this is "invalid*.*
```
### Regular expression

In case very complex rules are needed, each pattern can be written as a regular expression delimited with `/`:

```
/^db\d{2,}$/./^tbl\d{2,}$/
```

These regular expressions use the [Go dialect](https://pkg.go.dev/regexp/syntax?tab=doc). The pattern is matched if the identifier contains a substring matching the regular expression. For instance, `/b/` matches `db01`.

> **Note:**
>
> Every `/` in the regular expression must be escaped as `\/`, including inside `[…]`. You cannot place an unescaped `/` between `\Q…\E`.
