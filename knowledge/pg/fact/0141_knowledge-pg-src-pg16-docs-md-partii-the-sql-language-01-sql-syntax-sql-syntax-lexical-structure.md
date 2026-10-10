# Lexical Structure; Value Expressions; Calling Functions

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/01_sql_syntax.md`
- Source Title: `SQL Syntax`
- Source Heading Path: `SQL Syntax > Lexical Structure; Value Expressions; Calling Functions`
- Source Line Ranges: `12-775, 776-1560, 1561-1712`
- Chunk ID: `pg16_fact_0141_e36bcb4780`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `9c2c46bc5af311aed63fd83326dd2770658d134046e972db64b626729f2a5635`

## Retrieval Guidance

- Use When: Need syntax facts for parsing or composing SQL expressions and function calls.
- Retrieval Keywords: identifier, keyword, constant, operator, value expression, aggregate expression, function call
- Follow-up Guidance: Use command-specific documentation when the question concerns a concrete SQL command.
- Classification Note: Reference material for tokens, identifiers, constants, operators, comments, value expressions, aggregate expressions, row/array constructors, expression evaluation, and function-call notation.

## Official Source Content

## Lexical Structure

SQL input consists of a sequence of
*commands*.  A command is composed of a
sequence of *tokens*, terminated by a
semicolon (";").  The end of the input stream also
terminates a command.  Which tokens are valid depends on the syntax
of the particular command.

A token can be a *key word*, an
*identifier*, a *quoted
identifier*, a *literal* (or
constant), or a special character symbol.  Tokens are normally
separated by whitespace (space, tab, newline), but need not be if
there is no ambiguity (which is generally only the case if a
special character is adjacent to some other token type).

For example, the following is (syntactically) valid SQL input:

```
SELECT * FROM MY_TABLE;
UPDATE MY_TABLE SET A = 5;
INSERT INTO MY_TABLE VALUES (3, 'hi there');
```

This is a sequence of three commands, one per line (although this
is not required; more than one command can be on a line, and
commands can usefully be split across lines).

Additionally, *comments* can occur in SQL
input.  They are not tokens, they are effectively equivalent to
whitespace.

The SQL syntax is not very consistent regarding what tokens
identify commands and which are operands or parameters.  The first
few tokens are generally the command name, so in the above example
we would usually speak of a "SELECT", an
"UPDATE", and an "INSERT" command.  But
for instance the `UPDATE` command always requires
a `SET` token to appear in a certain position, and
this particular variation of `INSERT` also
requires a `VALUES` in order to be complete.  The
precise syntax rules for each command are described in [reference](#reference).

### Identifiers and Key Words

Tokens such as `SELECT`, `UPDATE`, or
`VALUES` in the example above are examples of
*key words*, that is, words that have a fixed
meaning in the SQL language.  The tokens `MY_TABLE`
and `A` are examples of
*identifiers*.  They identify names of
tables, columns, or other database objects, depending on the
command they are used in.  Therefore they are sometimes simply
called "names".  Key words and identifiers have the
same lexical structure, meaning that one cannot know whether a
token is an identifier or a key word without knowing the language.
A complete list of key words can be found in [sql-keywords-appendix](#sql-keywords-appendix).

SQL identifiers and key words must begin with a letter
(`a`-`z`, but also letters with
diacritical marks and non-Latin letters) or an underscore
(`_`).  Subsequent characters in an identifier or
key word can be letters, underscores, digits
(`0`-`9`), or dollar signs
(`$`).  Note that dollar signs are not allowed in identifiers
according to the letter of the SQL standard, so their use might render
applications less portable.
The SQL standard will not define a key word that contains
digits or starts or ends with an underscore, so identifiers of this
form are safe against possible conflict with future extensions of the
standard.

The system uses no more than `NAMEDATALEN`-1
bytes of an identifier; longer names can be written in
commands, but they will be truncated.  By default,
`NAMEDATALEN` is 64 so the maximum identifier
length is 63 bytes. If this limit is problematic, it can be raised by
changing the `NAMEDATALEN` constant in
`src/include/pg_config_manual.h`.

Key words and unquoted identifiers are case-insensitive.  Therefore:

```
UPDATE MY_TABLE SET A = 5;
```

can equivalently be written as:

```
uPDaTE my_TabLE SeT a = 5;
```

A convention often used is to write key words in upper
case and names in lower case, e.g.:

```
UPDATE my_table SET a = 5;
```

There is a second kind of identifier:  the *delimited
identifier* or *quoted
identifier*.  It is formed by enclosing an arbitrary
sequence of characters in double-quotes
(`"`).  A delimited
identifier is always an identifier, never a key word.  So
`"select"` could be used to refer to a column or
table named "select", whereas an unquoted
`select` would be taken as a key word and
would therefore provoke a parse error when used where a table or
column name is expected.  The example can be written with quoted
identifiers like this:

```
UPDATE "my_table" SET "a" = 5;
```

Quoted identifiers can contain any character, except the character
with code zero.  (To include a double quote, write two double quotes.)
This allows constructing table or column names that would
otherwise not be possible, such as ones containing spaces or
ampersands.  The length limitation still applies.

Quoting an identifier also makes it case-sensitive, whereas
unquoted names are always folded to lower case.  For example, the
identifiers `FOO`, `foo`, and
`"foo"` are considered the same by
PostgreSQL, but
`"Foo"` and `"FOO"` are
different from these three and each other.  (The folding of
unquoted names to lower case in PostgreSQL is
incompatible with the SQL standard, which says that unquoted names
should be folded to upper case.  Thus, `foo`
should be equivalent to `"FOO"` not
`"foo"` according to the standard.  If you want
to write portable applications you are advised to always quote a
particular name or never quote it.)

A variant of quoted
identifiers allows including escaped Unicode characters identified
by their code points.  This variant starts
with `U&` (upper or lower case U followed by
ampersand) immediately before the opening double quote, without
any spaces in between, for example `U&"foo"`.
(Note that this creates an ambiguity with the
operator `&`.  Use spaces around the operator to
avoid this problem.)  Inside the quotes, Unicode characters can be
specified in escaped form by writing a backslash followed by the
four-digit hexadecimal code point number or alternatively a
backslash followed by a plus sign followed by a six-digit
hexadecimal code point number.  For example, the
identifier `"data"` could be written as

```
U&"d\0061t\+000061"
```

The following less trivial example writes the Russian
word "slon" (elephant) in Cyrillic letters:

```
U&"\0441\043B\043E\043D"
```

If a different escape character than backslash is desired, it can
be specified using
the `UESCAPE`
clause after the string, for example:

```
U&"d!0061t!+000061" UESCAPE '!'
```

The escape character can be any single character other than a
hexadecimal digit, the plus sign, a single quote, a double quote,
or a whitespace character.  Note that the escape character is
written in single quotes, not double quotes,
after `UESCAPE`.

To include the escape character in the identifier literally, write
it twice.

Either the 4-digit or the 6-digit escape form can be used to
specify UTF-16 surrogate pairs to compose characters with code
points larger than U+FFFF, although the availability of the
6-digit form technically makes this unnecessary.  (Surrogate
pairs are not stored directly, but are combined into a single
code point.)

If the server encoding is not UTF-8, the Unicode code point identified
by one of these escape sequences is converted to the actual server
encoding; an error is reported if that's not possible.

### Constants

There are three kinds of *implicitly-typed
constants* in PostgreSQL:
strings, bit strings, and numbers.
Constants can also be specified with explicit types, which can
enable more accurate representation and more efficient handling by
the system. These alternatives are discussed in the following
subsections.

#### String Constants

A string constant in SQL is an arbitrary sequence of characters
bounded by single quotes (`'`), for example
`'This is a string'`.  To include
a single-quote character within a string constant,
write two adjacent single quotes, e.g.,
`'Dianne''s horse'`.
Note that this is *not* the same as a double-quote
character (`"`).

Two string constants that are only separated by whitespace
*with at least one newline* are concatenated
and effectively treated as if the string had been written as one
constant.  For example:

```
SELECT 'foo'
'bar';
```

is equivalent to:

```
SELECT 'foobar';
```

but:

```
SELECT 'foo'      'bar';
```

is not valid syntax.  (This slightly bizarre behavior is specified
by SQL; PostgreSQL is
following the standard.)

#### String Constants with C-Style Escapes

PostgreSQL also accepts "escape"
string constants, which are an extension to the SQL standard.
An escape string constant is specified by writing the letter
`E` (upper or lower case) just before the opening single
quote, e.g., `E'foo'`.  (When continuing an escape string
constant across lines, write `E` only before the first opening
quote.)
Within an escape string, a backslash character (`\`) begins a
C-like *backslash escape* sequence, in which the combination
of backslash and following character(s) represent a special byte
value, as shown in [sql-backslash-table](#sql-backslash-table).

| Backslash Escape Sequence | Interpretation |
| --- | --- |
| `\b` | backspace |
| `\f` | form feed |
| `\n` | newline |
| `\r` | carriage return |
| `\t` | tab |
| `\`o``,          `\`oo``,          `\`ooo``          (`o` = 0–7) | octal byte value |
| `\x`h``,          `\x`hh``          (`h` = 0–9, A–F) | hexadecimal byte value |
| `\u`xxxx``,          `\U`xxxxxxxx``          (`x` = 0–9, A–F) | 16 or 32-bit hexadecimal Unicode character value |

Any other
character following a backslash is taken literally. Thus, to
include a backslash character, write two backslashes (`\\`).
Also, a single quote can be included in an escape string by writing
`\'`, in addition to the normal way of `''`.

It is your responsibility that the byte sequences you create,
especially when using the octal or hexadecimal escapes, compose
valid characters in the server character set encoding.
A useful alternative is to use Unicode escapes or the
alternative Unicode escape syntax, explained
in [sql-syntax-strings-uescape](#sql-syntax-strings-uescape); then the server
will check that the character conversion is possible.

> **Caution:**

> If the configuration parameter
> [guc-standard-conforming-strings](#guc-standard-conforming-strings) is `off`,
> then PostgreSQL recognizes backslash escapes
> in both regular and escape string constants.  However, as of
> PostgreSQL 9.1, the default is `on`, meaning
> that backslash escapes are recognized only in escape string constants.
> This behavior is more standards-compliant, but might break applications
> which rely on the historical behavior, where backslash escapes
> were always recognized.  As a workaround, you can set this parameter
> to `off`, but it is better to migrate away from using backslash
> escapes.  If you need to use a backslash escape to represent a special
> character, write the string constant with an `E`.
>

>

> In addition to `standard_conforming_strings`, the configuration
> parameters [guc-escape-string-warning](#guc-escape-string-warning) and
> [guc-backslash-quote](#guc-backslash-quote) govern treatment of backslashes
> in string constants.
>

The character with the code zero cannot be in a string constant.

#### String Constants with Unicode Escapes

PostgreSQL also supports another type
of escape syntax for strings that allows specifying arbitrary
Unicode characters by code point.  A Unicode escape string
constant starts with `U&` (upper or lower case
letter U followed by ampersand) immediately before the opening
quote, without any spaces in between, for
example `U&'foo'`.  (Note that this creates an
ambiguity with the operator `&`.  Use spaces
around the operator to avoid this problem.)  Inside the quotes,
Unicode characters can be specified in escaped form by writing a
backslash followed by the four-digit hexadecimal code point
number or alternatively a backslash followed by a plus sign
followed by a six-digit hexadecimal code point number.  For
example, the string `'data'` could be written as

```
U&'d\0061t\+000061'
```

The following less trivial example writes the Russian
word "slon" (elephant) in Cyrillic letters:

```
U&'\0441\043B\043E\043D'
```

If a different escape character than backslash is desired, it can
be specified using
the `UESCAPE`
clause after the string, for example:

```
U&'d!0061t!+000061' UESCAPE '!'
```

The escape character can be any single character other than a
hexadecimal digit, the plus sign, a single quote, a double quote,
or a whitespace character.

To include the escape character in the string literally, write
it twice.

Either the 4-digit or the 6-digit escape form can be used to
specify UTF-16 surrogate pairs to compose characters with code
points larger than U+FFFF, although the availability of the
6-digit form technically makes this unnecessary.  (Surrogate
pairs are not stored directly, but are combined into a single
code point.)

If the server encoding is not UTF-8, the Unicode code point identified
by one of these escape sequences is converted to the actual server
encoding; an error is reported if that's not possible.

Also, the Unicode escape syntax for string constants only works
when the configuration
parameter [guc-standard-conforming-strings](#guc-standard-conforming-strings) is
turned on.  This is because otherwise this syntax could confuse
clients that parse the SQL statements to the point that it could
lead to SQL injections and similar security issues.  If the
parameter is set to off, this syntax will be rejected with an
error message.

#### Dollar-Quoted String Constants

While the standard syntax for specifying string constants is usually
convenient, it can be difficult to understand when the desired string
contains many single quotes, since each of those must
be doubled. To allow more readable queries in such situations,
PostgreSQL provides another way, called
"dollar quoting", to write string constants.
A dollar-quoted string constant
consists of a dollar sign (`$`), an optional
"tag" of zero or more characters, another dollar
sign, an arbitrary sequence of characters that makes up the
string content, a dollar sign, the same tag that began this
dollar quote, and a dollar sign. For example, here are two
different ways to specify the string "Dianne's horse"
using dollar quoting:

```
$$Dianne's horse$$
$SomeTag$Dianne's horse$SomeTag$
```

Notice that inside the dollar-quoted string, single quotes can be
used without needing to be escaped.  Indeed, no characters inside
a dollar-quoted string are ever escaped: the string content is always
written literally.  Backslashes are not special, and neither are
dollar signs, unless they are part of a sequence matching the opening
tag.

It is possible to nest dollar-quoted string constants by choosing
different tags at each nesting level.  This is most commonly used in
writing function definitions.  For example:

```
$function$
BEGIN
RETURN ($1 ~ $q$[\t\r\n\v\\]$q$);
END;
$function$
```

Here, the sequence `$q$[\t\r\n\v\\]$q$` represents a
dollar-quoted literal string `[\t\r\n\v\\]`, which will
be recognized when the function body is executed by
PostgreSQL.  But since the sequence does not match
the outer dollar quoting delimiter `$function$`, it is
just some more characters within the constant so far as the outer
string is concerned.

The tag, if any, of a dollar-quoted string follows the same rules
as an unquoted identifier, except that it cannot contain a dollar sign.
Tags are case sensitive, so `$tag$String content$tag$`
is correct, but `$TAG$String content$tag$` is not.

A dollar-quoted string that follows a keyword or identifier must
be separated from it by whitespace; otherwise the dollar quoting
delimiter would be taken as part of the preceding identifier.

Dollar quoting is not part of the SQL standard, but it is often a more
convenient way to write complicated string literals than the
standard-compliant single quote syntax.  It is particularly useful when
representing string constants inside other constants, as is often needed
in procedural function definitions.  With single-quote syntax, each
backslash in the above example would have to be written as four
backslashes, which would be reduced to two backslashes in parsing the
original string constant, and then to one when the inner string constant
is re-parsed during function execution.

#### Bit-String Constants

Bit-string constants look like regular string constants with a
`B` (upper or lower case) immediately before the
opening quote (no intervening whitespace), e.g.,
`B'1001'`.  The only characters allowed within
bit-string constants are `0` and
`1`.

Alternatively, bit-string constants can be specified in hexadecimal
notation, using a leading `X` (upper or lower case),
e.g., `X'1FF'`.  This notation is equivalent to
a bit-string constant with four binary digits for each hexadecimal digit.

Both forms of bit-string constant can be continued
across lines in the same way as regular string constants.
Dollar quoting cannot be used in a bit-string constant.

#### Numeric Constants

Numeric constants are accepted in these general forms:

```
`digits`
`digits`.`digits`e+-`digits`
`digits`.`digits`e+-`digits`
`digits`e+-`digits`
```

where `digits` is one or more decimal
digits (0 through 9).  At least one digit must be before or after the
decimal point, if one is used.  At least one digit must follow the
exponent marker (`e`), if one is present.
There cannot be any spaces or other characters embedded in the
constant, except for underscores, which can be used for visual grouping as
described below.  Note that any leading plus or minus sign is not actually
considered part of the constant; it is an operator applied to the
constant.

These are some examples of valid numeric constants:

```
42
3.5
4.
.001
5e2
1.925e-3
```

Additionally, non-decimal integer constants are accepted in these forms:

```
0x`hexdigits`
0o`octdigits`
0b`bindigits`
```

where `hexdigits` is one or more hexadecimal digits
(0-9, A-F), `octdigits` is one or more octal
digits (0-7), and `bindigits` is one or more binary
digits (0 or 1).  Hexadecimal digits and the radix prefixes can be in
upper or lower case.  Note that only integers can have non-decimal forms,
not numbers with fractional parts.

These are some examples of valid non-decimal integer constants:

```
0b100101
0B10011001
0o273
0O755
0x42f
0XFFFF
```

For visual grouping, underscores can be inserted between digits.  These
have no further effect on the value of the constant.  For example:

```
1_500_000_000
0b10001000_00000000
0o_1_755
0xFFFF_FFFF
1.618_034
```

Underscores are not allowed at the start or end of a numeric constant or
a group of digits (that is, immediately before or after the decimal point
or the exponent marker), and more than one underscore in a row is not
allowed.

A numeric constant that contains neither a decimal point nor an
exponent is initially presumed to be type `integer` if its
value fits in type `integer` (32 bits); otherwise it is
presumed to be type `bigint` if its
value fits in type `bigint` (64 bits); otherwise it is
taken to be type `numeric`.  Constants that contain decimal
points and/or exponents are always initially presumed to be type
`numeric`.

The initially assigned data type of a numeric constant is just a
starting point for the type resolution algorithms.  In most cases
the constant will be automatically coerced to the most
appropriate type depending on context.  When necessary, you can
force a numeric value to be interpreted as a specific data type
by casting it.
For example, you can force a numeric value to be treated as type
`real` (`float4`) by writing:

```
REAL '1.23'  -- string style
1.23::REAL   -- PostgreSQL (historical) style
```

These are actually just special cases of the general casting
notations discussed next.

#### Constants of Other Types

A constant of an *arbitrary* type can be
entered using any one of the following notations:

```
`type` '`string`'
'`string`'::`type`
CAST ( '`string`' AS `type` )
```

The string constant's text is passed to the input conversion
routine for the type called `type`. The
result is a constant of the indicated type.  The explicit type
cast can be omitted if there is no ambiguity as to the type the
constant must be (for example, when it is assigned directly to a
table column), in which case it is automatically coerced.

The string constant can be written using either regular SQL
notation or dollar-quoting.

It is also possible to specify a type coercion using a function-like
syntax:

```
`typename` ( '`string`' )
```

but not all type names can be used in this way; see [sql-syntax-type-casts](#sql-syntax-type-casts) for details.

The `::`, `CAST()`, and
function-call syntaxes can also be used to specify run-time type
conversions of arbitrary expressions, as discussed in [sql-syntax-type-casts](#sql-syntax-type-casts).  To avoid syntactic ambiguity, the
``type` '`string`'`
syntax can only be used to specify the type of a simple literal constant.
Another restriction on the
``type` '`string`'`
syntax is that it does not work for array types; use `::`
or `CAST()` to specify the type of an array constant.

The `CAST()` syntax conforms to SQL.  The
``type` '`string`'`
syntax is a generalization of the standard: SQL specifies this syntax only
for a few data types, but PostgreSQL allows it
for all types.  The syntax with
`::` is historical PostgreSQL
usage, as is the function-call syntax.

### Operators

An operator name is a sequence of up to `NAMEDATALEN`-1
(63 by default) characters from the following list:

```
+ - * /  = ~ ! @ # % ^ & | ` ?
```

There are a few restrictions on operator names, however:

- `--` and `/*` cannot appear
anywhere in an operator name, since they will be taken as the
start of a comment.
- A multiple-character operator name cannot end in `+` or `-`,
unless the name also contains at least one of these characters:

```
~ ! @ # % ^ & | ` ?
```

For example, `@-` is an allowed operator name,
but `*-` is not.  This restriction allows
PostgreSQL to parse SQL-compliant
queries without requiring spaces between tokens.

When working with non-SQL-standard operator names, you will usually
need to separate adjacent operators with spaces to avoid ambiguity.
For example, if you have defined a prefix operator named `@`,
you cannot write `X*@Y`; you must write
`X* @Y` to ensure that
PostgreSQL reads it as two operator names
not one.

### Special Characters

Some characters that are not alphanumeric have a special meaning
that is different from being an operator.  Details on the usage can
be found at the location where the respective syntax element is
described.  This section only exists to advise the existence and
summarize the purposes of these characters.

- A dollar sign (`$`) followed by digits is used
to represent a positional parameter in the body of a function
definition or a prepared statement.  In other contexts the
dollar sign can be part of an identifier or a dollar-quoted string
constant.
- Parentheses (`()`) have their usual meaning to
group expressions and enforce precedence.  In some cases
parentheses are required as part of the fixed syntax of a
particular SQL command.
- Brackets (`[]`) are used to select the elements
of an array.  See [arrays](#arrays) for more information
on arrays.
- Commas (`,`) are used in some syntactical
constructs to separate the elements of a list.
- The semicolon (`;`) terminates an SQL command.
It cannot appear anywhere within a command, except within a
string constant or quoted identifier.
- The colon (`:`) is used to select
"slices" from arrays. (See [arrays](#arrays).)  In certain SQL dialects (such as Embedded
SQL), the colon is used to prefix variable names.
- The asterisk (`*`) is used in some contexts to denote
all the fields of a table row or composite value.  It also
has a special meaning when used as the argument of an
aggregate function, namely that the aggregate does not require
any explicit parameter.
- The period (`.`) is used in numeric
constants, and to separate schema, table, and column names.

### Comments

A comment is a sequence of characters beginning with
double dashes and extending to the end of the line, e.g.:

```
-- This is a standard SQL comment
```

Alternatively, C-style block comments can be used:

```
/* multiline comment
* with nesting: /* nested block comment */
*/
```

where the comment begins with `/*` and extends to
the matching occurrence of `*/`. These block
comments nest, as specified in the SQL standard but unlike C, so that one can
comment out larger blocks of code that might contain existing block
comments.

A comment is removed from the input stream before further syntax
analysis and is effectively replaced by whitespace.

### Operator Precedence

[sql-precedence-table](#sql-precedence-table) shows the precedence and
associativity of the operators in PostgreSQL.
Most operators have the same precedence and are left-associative.
The precedence and associativity of the operators is hard-wired
into the parser.
Add parentheses if you want an expression with multiple operators
to be parsed in some other way than what the precedence rules imply.

| Operator/Element | Associativity | Description |
| --- | --- | --- |
| `.` | left | table/column name separator |
| `::` | left | PostgreSQL-style typecast |
| `[` `]` | left | array element selection |
| `+` `-` | right | unary plus, unary minus |
| `COLLATE` | left | collation selection |
| `AT` | left | `AT TIME ZONE` |
| `^` | left | exponentiation |
| `*` `/` `%` | left | multiplication, division, modulo |
| `+` `-` | left | addition, subtraction |
| (any other operator) | left | all other native and user-defined operators |
| `BETWEEN` `IN` `LIKE` `ILIKE` `SIMILAR` |  | range containment, set membership, string matching |
| `` `=` `=` `<>` |  | comparison operators |
| `IS` `ISNULL` `NOTNULL` |  | `IS TRUE`, `IS FALSE`, `IS        NULL`, `IS DISTINCT FROM`, etc. |
| `NOT` | right | logical negation |
| `AND` | left | logical conjunction |
| `OR` | left | logical disjunction |

Note that the operator precedence rules also apply to user-defined
operators that have the same names as the built-in operators
mentioned above.  For example, if you define a
"+" operator for some custom data type it will have
the same precedence as the built-in "+" operator, no
matter what yours does.

When a schema-qualified operator name is used in the
`OPERATOR` syntax, as for example in:

```
SELECT 3 OPERATOR(pg_catalog.+) 4;
```

the `OPERATOR` construct is taken to have the default precedence
shown in [sql-precedence-table](#sql-precedence-table) for
"any other operator".  This is true no matter
which specific operator appears inside `OPERATOR()`.

> **Note:**

> PostgreSQL versions before 9.5 used slightly different
> operator precedence rules.  In particular, `<=`
> `>=` and `<>` used to be treated as
> generic operators; `IS` tests used to have higher priority;
> and `NOT BETWEEN` and related constructs acted inconsistently,
> being taken in some cases as having the precedence of `NOT`
> rather than `BETWEEN`.  These rules were changed for better
> compliance with the SQL standard and to reduce confusion from
> inconsistent treatment of logically equivalent constructs.  In most
> cases, these changes will result in no behavioral change, or perhaps
> in "no such operator" failures which can be resolved by adding
> parentheses.  However there are corner cases in which a query might
> change behavior without any parsing error being reported.
>

## Value Expressions

Value expressions are used in a variety of contexts, such
as in the target list of the `SELECT` command, as
new column values in `INSERT` or
`UPDATE`, or in search conditions in a number of
commands.  The result of a value expression is sometimes called a
*scalar*, to distinguish it from the result of
a table expression (which is a table).  Value expressions are
therefore also called *scalar expressions* (or
even simply *expressions*).  The expression
syntax allows the calculation of values from primitive parts using
arithmetic, logical, set, and other operations.

A value expression is one of the following:

- A constant or literal value
- A column reference
- A positional parameter reference, in the body of a function definition
or prepared statement
- A subscripted expression
- A field selection expression
- An operator invocation
- A function call
- An aggregate expression
- A window function call
- A type cast
- A collation expression
- A scalar subquery
- An array constructor
- A row constructor
- Another value expression in parentheses (used to group
subexpressions and override
precedence)

In addition to this list, there are a number of constructs that can
be classified as an expression but do not follow any general syntax
rules.  These generally have the semantics of a function or
operator and are explained in the appropriate location in [functions](#functions).  An example is the `IS NULL`
clause.

We have already discussed constants in [sql-syntax-constants](#sql-syntax-constants).  The following sections discuss
the remaining options.

### Column References

A column can be referenced in the form:

```
`correlation`.`columnname`
```

`correlation` is the name of a
table (possibly qualified with a schema name), or an alias for a table
defined by means of a `FROM` clause.
The correlation name and separating dot can be omitted if the column name
is unique across all the tables being used in the current query.  (See also [queries](#queries).)

### Positional Parameters

A positional parameter reference is used to indicate a value
that is supplied externally to an SQL statement.  Parameters are
used in SQL function definitions and in prepared queries.  Some
client libraries also support specifying data values separately
from the SQL command string, in which case parameters are used to
refer to the out-of-line data values.
The form of a parameter reference is:

```
$`number`
```

For example, consider the definition of a function,
`dept`, as:

```
CREATE FUNCTION dept(text) RETURNS dept
AS $$ SELECT * FROM dept WHERE name = $1 $$
LANGUAGE SQL;
```

Here the `$1` references the value of the first
function argument whenever the function is invoked.

### Subscripts

If an expression yields a value of an array type, then a specific
element of the array value can be extracted by writing

```
`expression`[`subscript`]
```

or multiple adjacent elements (an "array slice") can be extracted
by writing

```
`expression`[`lower_subscript`:`upper_subscript`]
```

(Here, the brackets `[ ]` are meant to appear literally.)
Each `subscript` is itself an expression,
which will be rounded to the nearest integer value.

In general the array `expression` must be
parenthesized, but the parentheses can be omitted when the expression
to be subscripted is just a column reference or positional parameter.
Also, multiple subscripts can be concatenated when the original array
is multidimensional.
For example:

```
mytable.arraycolumn[4]
mytable.two_d_column[17][34]
$1[10:42]
(arrayfunction(a,b))[42]
```

The parentheses in the last example are required.
See [arrays](#arrays) for more about arrays.

### Field Selection

If an expression yields a value of a composite type (row type), then a
specific field of the row can be extracted by writing

```
`expression`.`fieldname`
```

In general the row `expression` must be
parenthesized, but the parentheses can be omitted when the expression
to be selected from is just a table reference or positional parameter.
For example:

```
mytable.mycolumn
$1.somecolumn
(rowfunction(a,b)).col3
```

(Thus, a qualified column reference is actually just a special case
of the field selection syntax.)  An important special case is
extracting a field from a table column that is of a composite type:

```
(compositecol).somefield
(mytable.compositecol).somefield
```

The parentheses are required here to show that
`compositecol` is a column name not a table name,
or that `mytable` is a table name not a schema name
in the second case.

You can ask for all fields of a composite value by
writing `.*`:

```
(compositecol).*
```

This notation behaves differently depending on context;
see [rowtypes-usage](#rowtypes-usage) for details.

### Operator Invocations

There are two possible syntaxes for an operator invocation:

where the `operator` token follows the syntax
rules of [sql-syntax-operators](#sql-syntax-operators), or is one of the
key words `AND`, `OR`, and
`NOT`, or is a qualified operator name in the form:

```
`OPERATOR(``schema``.``operatorname``)`
```

Which particular operators exist and whether
they are unary or binary depends on what operators have been
defined by the system or the user.  [functions](#functions)
describes the built-in operators.

### Function Calls

The syntax for a function call is the name of a function
(possibly qualified with a schema name), followed by its argument list
enclosed in parentheses:

```
`function_name` (`expression` , `expression` ...  )
```

For example, the following computes the square root of 2:

```
sqrt(2)
```

The list of built-in functions is in [functions](#functions).
Other functions can be added by the user.

When issuing queries in a database where some users mistrust other users,
observe security precautions from [typeconv-func](#typeconv-func) when
writing function calls.

The arguments can optionally have names attached.
See [sql-syntax-calling-funcs](#sql-syntax-calling-funcs) for details.

> **Note:**

> A function that takes a single argument of composite type can
> optionally be called using field-selection syntax, and conversely
> field selection can be written in functional style.  That is, the
> notations `col(table)` and `table.col` are
> interchangeable.  This behavior is not SQL-standard but is provided
> in PostgreSQL because it allows use of functions to
> emulate "computed fields".  For more information see
> [rowtypes-usage](#rowtypes-usage).
>

### Aggregate Expressions

An *aggregate expression* represents the
application of an aggregate function across the rows selected by a
query.  An aggregate function reduces multiple inputs to a single
output value, such as the sum or average of the inputs.  The
syntax of an aggregate expression is one of the following:

```
`aggregate_name` (`expression` [ , ... ] [ `order_by_clause` ] ) [ FILTER ( WHERE `filter_clause` ) ]
`aggregate_name` (ALL `expression` [ , ... ] [ `order_by_clause` ] ) [ FILTER ( WHERE `filter_clause` ) ]
`aggregate_name` (DISTINCT `expression` [ , ... ] [ `order_by_clause` ] ) [ FILTER ( WHERE `filter_clause` ) ]
`aggregate_name` ( * ) [ FILTER ( WHERE `filter_clause` ) ]
`aggregate_name` ( [ `expression` [ , ... ] ] ) WITHIN GROUP ( `order_by_clause` ) [ FILTER ( WHERE `filter_clause` ) ]
```

where `aggregate_name` is a previously
defined aggregate (possibly qualified with a schema name) and
`expression` is
any value expression that does not itself contain an aggregate
expression or a window function call.  The optional
`order_by_clause` and
`filter_clause` are described below.

The first form of aggregate expression invokes the aggregate
once for each input row.
The second form is the same as the first, since
`ALL` is the default.
The third form invokes the aggregate once for each distinct value
of the expression (or distinct set of values, for multiple expressions)
found in the input rows.
The fourth form invokes the aggregate once for each input row; since no
particular input value is specified, it is generally only useful
for the `count(*)` aggregate function.
The last form is used with *ordered-set* aggregate
functions, which are described below.

Most aggregate functions ignore null inputs, so that rows in which
one or more of the expression(s) yield null are discarded.  This
can be assumed to be true, unless otherwise specified, for all
built-in aggregates.

For example, `count(*)` yields the total number
of input rows; `count(f1)` yields the number of
input rows in which `f1` is non-null, since
`count` ignores nulls; and
`count(distinct f1)` yields the number of
distinct non-null values of `f1`.

Ordinarily, the input rows are fed to the aggregate function in an
unspecified order.  In many cases this does not matter; for example,
`min` produces the same result no matter what order it
receives the inputs in.  However, some aggregate functions
(such as `array_agg` and `string_agg`) produce
results that depend on the ordering of the input rows.  When using
such an aggregate, the optional `order_by_clause` can be
used to specify the desired ordering.  The `order_by_clause`
has the same syntax as for a query-level `ORDER BY` clause, as
described in [queries-order](#queries-order), except that its expressions
are always just expressions and cannot be output-column names or numbers.
For example:

```
SELECT array_agg(a ORDER BY b DESC) FROM table;
```

When dealing with multiple-argument aggregate functions, note that the
`ORDER BY` clause goes after all the aggregate arguments.
For example, write this:

```
SELECT string_agg(a, ',' ORDER BY a) FROM table;
```

not this:

```
SELECT string_agg(a ORDER BY a, ',') FROM table;  -- incorrect
```

The latter is syntactically valid, but it represents a call of a
single-argument aggregate function with two `ORDER BY` keys
(the second one being rather useless since it's a constant).

If `DISTINCT` is specified in addition to an
`order_by_clause`, then all the `ORDER BY`
expressions must match regular arguments of the aggregate; that is,
you cannot sort on an expression that is not included in the
`DISTINCT` list.

> **Note:**

> The ability to specify both `DISTINCT` and `ORDER BY`
> in an aggregate function is a PostgreSQL extension.
>

Placing `ORDER BY` within the aggregate's regular argument
list, as described so far, is used when ordering the input rows for
general-purpose and statistical aggregates, for which ordering is
optional.  There is a
subclass of aggregate functions called *ordered-set
aggregates* for which an `order_by_clause`
is *required*, usually because the aggregate's computation is
only sensible in terms of a specific ordering of its input rows.
Typical examples of ordered-set aggregates include rank and percentile
calculations.  For an ordered-set aggregate,
the `order_by_clause` is written
inside `WITHIN GROUP (...)`, as shown in the final syntax
alternative above.  The expressions in
the `order_by_clause` are evaluated once per
input row just like regular aggregate arguments, sorted as per
the `order_by_clause`'s requirements, and fed
to the aggregate function as input arguments.  (This is unlike the case
for a non-`WITHIN GROUP` `order_by_clause`,
which is not treated as argument(s) to the aggregate function.)  The
argument expressions preceding `WITHIN GROUP`, if any, are
called *direct arguments* to distinguish them from
the *aggregated arguments* listed in
the `order_by_clause`.  Unlike regular aggregate
arguments, direct arguments are evaluated only once per aggregate call,
not once per input row.  This means that they can contain variables only
if those variables are grouped by `GROUP BY`; this restriction
is the same as if the direct arguments were not inside an aggregate
expression at all.  Direct arguments are typically used for things like
percentile fractions, which only make sense as a single value per
aggregation calculation.  The direct argument list can be empty; in this
case, write just `()` not `(*)`.
(PostgreSQL will actually accept either spelling, but
only the first way conforms to the SQL standard.)

An example of an ordered-set aggregate call is:

```
SELECT percentile_cont(0.5) WITHIN GROUP (ORDER BY income) FROM households;
percentile_cont
-----------------
50489
```

which obtains the 50th percentile, or median, value of
the `income` column from table `households`.
Here, `0.5` is a direct argument; it would make no sense
for the percentile fraction to be a value varying across rows.

If `FILTER` is specified, then only the input
rows for which the `filter_clause`
evaluates to true are fed to the aggregate function; other rows
are discarded.  For example:

```
SELECT
count(*) AS unfiltered,
count(*) FILTER (WHERE i  **Note:**

> The function-like syntax is in fact just a function call.  When
> one of the two standard cast syntaxes is used to do a run-time
> conversion, it will internally invoke a registered function to
> perform the conversion.  By convention, these conversion functions
> have the same name as their output type, and thus the "function-like
> syntax" is nothing more than a direct invocation of the underlying
> conversion function.  Obviously, this is not something that a portable
> application should rely on.  For further details see
> [sql-createcast](#sql-createcast).
>

### Collation Expressions

The `COLLATE` clause overrides the collation of
an expression.  It is appended to the expression it applies to:

```
`expr` COLLATE `collation`
```

where `collation` is a possibly
schema-qualified identifier.  The `COLLATE`
clause binds tighter than operators; parentheses can be used when
necessary.

If no collation is explicitly specified, the database system
either derives a collation from the columns involved in the
expression, or it defaults to the default collation of the
database if no column is involved in the expression.

The two common uses of the `COLLATE` clause are
overriding the sort order in an `ORDER BY` clause, for
example:

```
SELECT a, b, c FROM tbl WHERE ... ORDER BY a COLLATE "C";
```

and overriding the collation of a function or operator call that
has locale-sensitive results, for example:

```
SELECT * FROM tbl WHERE a > 'foo' COLLATE "C";
```

Note that in the latter case the `COLLATE` clause is
attached to an input argument of the operator we wish to affect.
It doesn't matter which argument of the operator or function call the
`COLLATE` clause is attached to, because the collation that is
applied by the operator or function is derived by considering all
arguments, and an explicit `COLLATE` clause will override the
collations of all other arguments.  (Attaching non-matching
`COLLATE` clauses to more than one argument, however, is an
error.  For more details see [collation](#collation).)
Thus, this gives the same result as the previous example:

```
SELECT * FROM tbl WHERE a COLLATE "C" > 'foo';
```

But this is an error:

```
SELECT * FROM tbl WHERE (a > 'foo') COLLATE "C";
```

because it attempts to apply a collation to the result of the
`>` operator, which is of the non-collatable data type
`boolean`.

### Scalar Subqueries

A scalar subquery is an ordinary
`SELECT` query in parentheses that returns exactly one
row with one column.  (See [queries](#queries) for information about writing queries.)
The `SELECT` query is executed
and the single returned value is used in the surrounding value expression.
It is an error to use a query that
returns more than one row or more than one column as a scalar subquery.
(But if, during a particular execution, the subquery returns no rows,
there is no error; the scalar result is taken to be null.)
The subquery can refer to variables from the surrounding query,
which will act as constants during any one evaluation of the subquery.
See also [functions-subquery](#functions-subquery) for other expressions involving subqueries.

For example, the following finds the largest city population in each
state:

```
SELECT name, (SELECT max(pop) FROM cities WHERE cities.state = states.name)
FROM states;
```

### Array Constructors

An array constructor is an expression that builds an
array value using values for its member elements.  A simple array
constructor
consists of the key word `ARRAY`, a left square bracket
`[`, a list of expressions (separated by commas) for the
array element values, and finally a right square bracket `]`.
For example:

```
SELECT ARRAY[1,2,3+4];
array
---------
{1,2,7}
(1 row)
```

By default,
the array element type is the common type of the member expressions,
determined using the same rules as for `UNION` or
`CASE` constructs (see [typeconv-union-case](#typeconv-union-case)).
You can override this by explicitly casting the array constructor to the
desired type, for example:

```
SELECT ARRAY[1,2,22.7]::integer[];
array
----------
{1,2,23}
(1 row)
```

This has the same effect as casting each expression to the array
element type individually.
For more on casting, see [sql-syntax-type-casts](#sql-syntax-type-casts).

Multidimensional array values can be built by nesting array
constructors.
In the inner constructors, the key word `ARRAY` can
be omitted.  For example, these produce the same result:

```
SELECT ARRAY[ARRAY[1,2], ARRAY[3,4]];
array
---------------
{{1,2},{3,4}}
(1 row)

SELECT ARRAY[[1,2],[3,4]];
array
---------------
{{1,2},{3,4}}
(1 row)
```

Since multidimensional arrays must be rectangular, inner constructors
at the same level must produce sub-arrays of identical dimensions.
Any cast applied to the outer `ARRAY` constructor propagates
automatically to all the inner constructors.

Multidimensional array constructor elements can be anything yielding
an array of the proper kind, not only a sub-`ARRAY` construct.
For example:

```
CREATE TABLE arr(f1 int[], f2 int[]);

INSERT INTO arr VALUES (ARRAY[[1,2],[3,4]], ARRAY[[5,6],[7,8]]);

SELECT ARRAY[f1, f2, '{{9,10},{11,12}}'::int[]] FROM arr;
array
------------------------------------------------
{{{1,2},{3,4}},{{5,6},{7,8}},{{9,10},{11,12}}}
(1 row)
```

You can construct an empty array, but since it's impossible to have an
array with no type, you must explicitly cast your empty array to the
desired type.  For example:

```
SELECT ARRAY[]::integer[];
array
-------
{}
(1 row)
```

It is also possible to construct an array from the results of a
subquery.  In this form, the array constructor is written with the
key word `ARRAY` followed by a parenthesized (not
bracketed) subquery. For example:

```
SELECT ARRAY(SELECT oid FROM pg_proc WHERE proname LIKE 'bytea%');
array
------------------------------------------------------------------
{2011,1954,1948,1952,1951,1244,1950,2005,1949,1953,2006,31,2412}
(1 row)

SELECT ARRAY(SELECT ARRAY[i, i*2] FROM generate_series(1,5) AS a(i));
array
----------------------------------
{{1,2},{2,4},{3,6},{4,8},{5,10}}
(1 row)
```

The subquery must return a single column.
If the subquery's output column is of a non-array type, the resulting
one-dimensional array will have an element for each row in the
subquery result, with an element type matching that of the
subquery's output column.
If the subquery's output column is of an array type, the result will be
an array of the same type but one higher dimension; in this case all
the subquery rows must yield arrays of identical dimensionality, else
the result would not be rectangular.

The subscripts of an array value built with `ARRAY`
always begin with one.  For more information about arrays, see
[arrays](#arrays).

### Row Constructors

A row constructor is an expression that builds a row value (also
called a composite value) using values
for its member fields.  A row constructor consists of the key word
`ROW`, a left parenthesis, zero or more
expressions (separated by commas) for the row field values, and finally
a right parenthesis.  For example:

```
SELECT ROW(1,2.5,'this is a test');
```

The key word `ROW` is optional when there is more than one
expression in the list.

A row constructor can include the syntax
`rowvalue``.*`,
which will be expanded to a list of the elements of the row value,
just as occurs when the `.*` syntax is used at the top level
of a `SELECT` list (see [rowtypes-usage](#rowtypes-usage)).
For example, if table `t` has
columns `f1` and `f2`, these are the same:

```
SELECT ROW(t.*, 42) FROM t;
SELECT ROW(t.f1, t.f2, 42) FROM t;
```

> **Note:**

> Before PostgreSQL 8.2, the
> `.*` syntax was not expanded in row constructors, so
> that writing `ROW(t.*, 42)` created a two-field row whose first
> field was another row value.  The new behavior is usually more useful.
> If you need the old behavior of nested row values, write the inner
> row value without `.*`, for instance
> `ROW(t, 42)`.
>

By default, the value created by a `ROW` expression is of
an anonymous record type.  If necessary, it can be cast to a named
composite type — either the row type of a table, or a composite type
created with `CREATE TYPE AS`.  An explicit cast might be needed
to avoid ambiguity.  For example:

```
CREATE TABLE mytable(f1 int, f2 float, f3 text);

CREATE FUNCTION getf1(mytable) RETURNS int AS 'SELECT $1.f1' LANGUAGE SQL;

-- No cast needed since only one getf1() exists
SELECT getf1(ROW(1,2.5,'this is a test'));
getf1
-------
1
(1 row)

CREATE TYPE myrowtype AS (f1 int, f2 text, f3 numeric);

CREATE FUNCTION getf1(myrowtype) RETURNS int AS 'SELECT $1.f1' LANGUAGE SQL;

-- Now we need a cast to indicate which function to call:
SELECT getf1(ROW(1,2.5,'this is a test'));
ERROR:  function getf1(record) is not unique

SELECT getf1(ROW(1,2.5,'this is a test')::mytable);
getf1
-------
1
(1 row)

SELECT getf1(CAST(ROW(11,'this is a test',2.5) AS myrowtype));
getf1
-------
11
(1 row)
```

Row constructors can be used to build composite values to be stored
in a composite-type table column, or to be passed to a function that
accepts a composite parameter.  Also,
it is possible to compare two row values or test a row with
`IS NULL` or `IS NOT NULL`, for example:

```
SELECT ROW(1,2.5,'this is a test') = ROW(1, 3, 'not the same');

SELECT ROW(table.*) IS NULL FROM table;  -- detect all-null rows
```

For more detail see [functions-comparisons](#functions-comparisons).
Row constructors can also be used in connection with subqueries,
as discussed in [functions-subquery](#functions-subquery).

### Expression Evaluation Rules

The order of evaluation of subexpressions is not defined.  In
particular, the inputs of an operator or function are not necessarily
evaluated left-to-right or in any other fixed order.

Furthermore, if the result of an expression can be determined by
evaluating only some parts of it, then other subexpressions
might not be evaluated at all.  For instance, if one wrote:

```
SELECT true OR somefunc();
```

then `somefunc()` would (probably) not be called
at all. The same would be the case if one wrote:

```
SELECT somefunc() OR true;
```

Note that this is not the same as the left-to-right
"short-circuiting" of Boolean operators that is found
in some programming languages.

As a consequence, it is unwise to use functions with side effects
as part of complex expressions.  It is particularly dangerous to
rely on side effects or evaluation order in `WHERE` and `HAVING` clauses,
since those clauses are extensively reprocessed as part of
developing an execution plan.  Boolean
expressions (`AND`/`OR`/`NOT` combinations) in those clauses can be reorganized
in any manner allowed by the laws of Boolean algebra.

When it is essential to force evaluation order, a `CASE`
construct (see [functions-conditional](#functions-conditional)) can be
used.  For example, this is an untrustworthy way of trying to
avoid division by zero in a `WHERE` clause:

```
SELECT ... WHERE x > 0 AND y/x > 1.5;
```

But this is safe:

```
SELECT ... WHERE CASE WHEN x > 0 THEN y/x > 1.5 ELSE false END;
```

A `CASE` construct used in this fashion will defeat optimization
attempts, so it should only be done when necessary.  (In this particular
example, it would be better to sidestep the problem by writing
`y > 1.5*x` instead.)

`CASE` is not a cure-all for such issues, however.
One limitation of the technique illustrated above is that it does not
prevent early evaluation of constant subexpressions.
As described in [xfunc-volatility](#xfunc-volatility), functions and
operators marked `IMMUTABLE` can be evaluated when
the query is planned rather than when it is executed.  Thus for example

```
SELECT CASE WHEN x > 0 THEN x ELSE 1/0 END FROM tab;
```

is likely to result in a division-by-zero failure due to the planner
trying to simplify the constant subexpression,
even if every row in the table has `x > 0` so that the
`ELSE` arm would never be entered at run time.

While that particular example might seem silly, related cases that don't
obviously involve constants can occur in queries executed within
functions, since the values of function arguments and local variables
can be inserted into queries as constants for planning purposes.
Within PL/pgSQL functions, for example, using an
`IF`-`THEN`-`ELSE` statement to protect
a risky computation is much safer than just nesting it in a
`CASE` expression.

Another limitation of the same kind is that a `CASE` cannot
prevent evaluation of an aggregate expression contained within it,
because aggregate expressions are computed before other
expressions in a `SELECT` list or `HAVING` clause
are considered.  For example, the following query can cause a
division-by-zero error despite seemingly having protected against it:

```
SELECT CASE WHEN min(employees) > 0
THEN avg(expenses / employees)
END
FROM departments;
```

The `min()` and `avg()` aggregates are computed
concurrently over all the input rows, so if any row
has `employees` equal to zero, the division-by-zero error
will occur before there is any opportunity to test the result of
`min()`.  Instead, use a `WHERE`
or `FILTER` clause to prevent problematic input rows from
reaching an aggregate function in the first place.

## Calling Functions

PostgreSQL allows functions that have named
parameters to be called using either *positional* or
*named* notation.  Named notation is especially
useful for functions that have a large number of parameters, since it
makes the associations between parameters and actual arguments more
explicit and reliable.
In positional notation, a function call is written with
its argument values in the same order as they are defined in the function
declaration.  In named notation, the arguments are matched to the
function parameters by name and can be written in any order.
For each notation, also consider the effect of function argument types,
documented in [typeconv-func](#typeconv-func).

In either notation, parameters that have default values given in the
function declaration need not be written in the call at all.  But this
is particularly useful in named notation, since any combination of
parameters can be omitted; while in positional notation parameters can
only be omitted from right to left.

PostgreSQL also supports
*mixed* notation, which combines positional and
named notation.  In this case, positional parameters are written first
and named parameters appear after them.

The following examples will illustrate the usage of all three
notations, using the following function definition:

```
CREATE FUNCTION concat_lower_or_upper(a text, b text, uppercase boolean DEFAULT false)
RETURNS text
AS
$$
SELECT CASE
WHEN $3 THEN UPPER($1 || ' ' || $2)
ELSE LOWER($1 || ' ' || $2)
END;
$$
LANGUAGE SQL IMMUTABLE STRICT;
```

Function `concat_lower_or_upper` has two mandatory
parameters, `a` and `b`.  Additionally
there is one optional parameter `uppercase` which defaults
to `false`.  The `a` and
`b` inputs will be concatenated, and forced to either
upper or lower case depending on the `uppercase`
parameter.  The remaining details of this function
definition are not important here (see [extend](#extend) for
more information).

### Using Positional Notation

Positional notation is the traditional mechanism for passing arguments
to functions in PostgreSQL.  An example is:

```
SELECT concat_lower_or_upper('Hello', 'World', true);
concat_lower_or_upper
-----------------------
HELLO WORLD
(1 row)
```

All arguments are specified in order.  The result is upper case since
`uppercase` is specified as `true`.
Another example is:

```
SELECT concat_lower_or_upper('Hello', 'World');
concat_lower_or_upper
-----------------------
hello world
(1 row)
```

Here, the `uppercase` parameter is omitted, so it
receives its default value of `false`, resulting in
lower case output.  In positional notation, arguments can be omitted
from right to left so long as they have defaults.

### Using Named Notation

In named notation, each argument's name is specified using
`=>` to separate it from the argument expression.
For example:

```
SELECT concat_lower_or_upper(a => 'Hello', b => 'World');
concat_lower_or_upper
-----------------------
hello world
(1 row)
```

Again, the argument `uppercase` was omitted
so it is set to `false` implicitly.  One advantage of
using named notation is that the arguments may be specified in any
order, for example:

```
SELECT concat_lower_or_upper(a => 'Hello', b => 'World', uppercase => true);
concat_lower_or_upper
-----------------------
HELLO WORLD
(1 row)

SELECT concat_lower_or_upper(a => 'Hello', uppercase => true, b => 'World');
concat_lower_or_upper
-----------------------
HELLO WORLD
(1 row)
```

An older syntax based on ":=" is supported for backward compatibility:

```
SELECT concat_lower_or_upper(a := 'Hello', uppercase := true, b := 'World');
concat_lower_or_upper
-----------------------
HELLO WORLD
(1 row)
```

### Using Mixed Notation

The mixed notation combines positional and named notation. However, as
already mentioned, named arguments cannot precede positional arguments.
For example:

```
SELECT concat_lower_or_upper('Hello', 'World', uppercase => true);
concat_lower_or_upper
-----------------------
HELLO WORLD
(1 row)
```

In the above query, the arguments `a` and
`b` are specified positionally, while
`uppercase` is specified by name.  In this example,
that adds little except documentation.  With a more complex function
having numerous parameters that have default values, named or mixed
notation can save a great deal of writing and reduce chances for error.

> **Note:**

> Named and mixed call notations currently cannot be used when calling an
> aggregate function (but they do work when an aggregate function is used
> as a window function).
>
