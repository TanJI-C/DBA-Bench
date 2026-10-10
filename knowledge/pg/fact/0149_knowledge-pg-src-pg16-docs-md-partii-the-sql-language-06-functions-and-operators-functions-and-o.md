# Logical Operators; Mathematical Functions and Operators; String Functions and Operators; Binary String Functions and Operators; Bit String Functions and Operators; Pattern Matching; Enum Support Functions; Geometric Functions and Operators; Network Address Functions and Operators; UUID Functions; XML Functions; JSON Functions and Operators; Sequence Manipulation Functions; Conditional Expressions; Array Functions and Operators; Aggregate Functions; Window Functions; Subquery Expressions; Row and Array Comparisons; Set Returning Functions; Trigger Functions; Event Trigger Functions

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/06_functions_and_operators.md`
- Source Title: `Functions and Operators`
- Source Heading Path: `Functions and Operators > Logical Operators; Mathematical Functions and Operators; String Functions and Operators; Binary String Functions and Operators; Bit String Functions and Operators; Pattern Matching; Enum Support Functions; Geometric Functions and Operators; Network Address Functions and Operators; UUID Functions; XML Functions; JSON Functions and Operators; Sequence Manipulation Functions; Conditional Expressions; Array Functions and Operators; Aggregate Functions; Window Functions; Subquery Expressions; Row and Array Comparisons; Set Returning Functions; Trigger Functions; Event Trigger Functions`
- Source Line Ranges: `37-71, 247-361, 362-640, 641-765, 766-818, 819-2231, 3495-3520, 3521-3630, 3631-3700, 3770-3787, 3788-4011, 4012-4301, 4302-4363, 4364-4579, 4580-4675, 4676-4920, 4921-4999, 5000-5245, 5246-5482, 5483-5681, 6597-6653, 6654-6772`
- Chunk ID: `pg16_fact_0149_50241a52c9`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `addec5baedd18f0b91bb48824e037e61b218a97f1eeb1d0dfbc52b12625a5491`

## Retrieval Guidance

- Use When: Need function or operator semantics and examples.
- Retrieval Keywords: operator, function, aggregate, window function, JSON function, XML function, array function, trigger function
- Follow-up Guidance: Use system administration function records when the function is used for operations or diagnostics.
- Classification Note: Reference material listing SQL operators, predicates, scalar functions, aggregate/window functions, JSON/XML/text/array helpers, trigger/event-trigger helpers, and expression semantics.

## Official Source Content

## Logical Operators

The usual logical operators are available:

```
`boolean` `AND` `boolean` boolean
`boolean` `OR` `boolean` boolean
`NOT` `boolean` boolean
```

SQL uses a three-valued logic system with true,
false, and `null`, which represents "unknown".
Observe the following truth tables:

| `a` | `b` | `a` AND `b` | `a` OR `b` |
| --- | --- | --- | --- |
| TRUE | TRUE | TRUE | TRUE |
| TRUE | FALSE | FALSE | TRUE |
| TRUE | NULL | NULL | TRUE |
| FALSE | FALSE | FALSE | FALSE |
| FALSE | NULL | FALSE | NULL |
| NULL | NULL | NULL | NULL |

| `a` | NOT `a` |
| --- | --- |
| TRUE | FALSE |
| FALSE | TRUE |
| NULL | NULL |

The operators `AND` and `OR` are
commutative, that is, you can switch the left and right operands
without affecting the result.  (However, it is not guaranteed that
the left operand is evaluated before the right operand.  See [syntax-express-eval](#syntax-express-eval) for more information about the
order of evaluation of subexpressions.)

## Mathematical Functions and Operators

Mathematical operators are provided for many
PostgreSQL types. For types without
standard mathematical conventions
(e.g., date/time types) we
describe the actual behavior in subsequent sections.

[functions-math-op-table](#functions-math-op-table) shows the mathematical
operators that are available for the standard numeric types.
Unless otherwise noted, operators shown as
accepting `numeric_type` are available for all
the types `smallint`, `integer`,
`bigint`, `numeric`, `real`,
and `double precision`.
Operators shown as accepting `integral_type`
are available for the types `smallint`, `integer`,
and `bigint`.
Except where noted, each form of an operator returns the same data type
as its argument(s).  Calls involving multiple argument data types, such
as `integer` `+` `numeric`,
are resolved by using the type appearing later in these lists.

| Operator                         Description                         Example(s) |
| --- |
| `numeric_type` `+` `numeric_type`         `numeric_type`                         Addition                         `2 + 3`         5 |
| `+` `numeric_type`         `numeric_type`                         Unary plus (no operation)                         `+ 3.5`         3.5 |
| `numeric_type` `-` `numeric_type`         `numeric_type`                         Subtraction                         `2 - 3`         -1 |
| `-` `numeric_type`         `numeric_type`                         Negation                         `- (-4)`         4 |
| `numeric_type` `*` `numeric_type`         `numeric_type`                         Multiplication                         `2 * 3`         6 |
| `numeric_type` `/` `numeric_type`         `numeric_type`                         Division (for integral types, division truncates the result towards         zero)                         `5.0 / 2`         2.5000000000000000                         `5 / 2`         2                         `(-5) / 2`         -2 |
| `numeric_type` `%` `numeric_type`         `numeric_type`                         Modulo (remainder); available for `smallint`,         `integer`, `bigint`, and `numeric`                         `5 % 4`         1 |
| `numeric` `^` `numeric`         numeric                         `double precision` `^` `double precision`         double precision                         Exponentiation                         `2 ^ 3`         8                         Unlike typical mathematical practice, multiple uses of         `^` will associate left to right by default:                         `2 ^ 3 ^ 3`         512                         `2 ^ (3 ^ 3)`         134217728 |
| `|/` `double precision`         double precision                         Square root                         `|/ 25.0`         5 |
| `||/` `double precision`         double precision                         Cube root                         `||/ 64.0`         4 |
| `@` `numeric_type`         `numeric_type`                         Absolute value                         `@ -5.0`         5.0 |
| `integral_type` `&` `integral_type`         `integral_type`                         Bitwise AND                         `91 & 15`         11 |
| `integral_type` `|` `integral_type`         `integral_type`                         Bitwise OR                         `32 | 3`         35 |
| `integral_type` `#` `integral_type`         `integral_type`                         Bitwise exclusive OR                         `17 # 5`         20 |
| `~` `integral_type`         `integral_type`                         Bitwise NOT                         `~1`         -2 |
| `integral_type` `>` `integer`         `integral_type`                         Bitwise shift right                         `8 >> 2`         2 |

[functions-math-func-table](#functions-math-func-table) shows the available
mathematical functions.
Many of these functions are provided in multiple forms with different
argument types.
Except where noted, any given form of a function returns the same
data type as its argument(s); cross-type cases are resolved in the
same way as explained above for operators.
The functions working with `double precision` data are mostly
implemented on top of the host system's C library; accuracy and behavior in
boundary cases can therefore vary depending on the host system.

| Function                         Description                         Example(s) |
| --- |
| `abs` ( `numeric_type` )         `numeric_type`                         Absolute value                         `abs(-17.4)`         17.4 |
| `cbrt` ( `double precision` )         double precision                         Cube root                         `cbrt(64.0)`         4 |
| `ceil` ( `numeric` )         numeric                         `ceil` ( `double precision` )         double precision                         Nearest integer greater than or equal to argument                         `ceil(42.2)`         43                         `ceil(-42.8)`         -42 |
| `ceiling` ( `numeric` )         numeric                         `ceiling` ( `double precision` )         double precision                         Nearest integer greater than or equal to argument (same         as `ceil`)                         `ceiling(95.3)`         96 |
| `degrees` ( `double precision` )         double precision                         Converts radians to degrees                         `degrees(0.5)`         28.64788975654116 |
| `div` ( y `numeric`,         x `numeric` )         numeric                         Integer quotient of y/x         (truncates towards zero)                         `div(9, 4)`         2 |
| `erf` ( `double precision` )         double precision                         Error function                         `erf(1.0)`         0.8427007929497149 |
| `erfc` ( `double precision` )         double precision                         Complementary error function (`1 - erf(x)`, without         loss of precision for large inputs)                         `erfc(1.0)`         0.15729920705028513 |
| `exp` ( `numeric` )         numeric                         `exp` ( `double precision` )         double precision                         Exponential (`e` raised to the given power)                         `exp(1.0)`         2.7182818284590452 |
| `factorial` ( `bigint` )         numeric                         Factorial                         `factorial(5)`         120 |
| `floor` ( `numeric` )         numeric                         `floor` ( `double precision` )         double precision                         Nearest integer less than or equal to argument                         `floor(42.8)`         42                         `floor(-42.8)`         -43 |
| `gcd` ( `numeric_type`, `numeric_type` )         `numeric_type`                         Greatest common divisor (the largest positive number that divides both         inputs with no remainder); returns `0` if both inputs         are zero; available for `integer`, `bigint`,         and `numeric`                         `gcd(1071, 462)`         21 |
| `lcm` ( `numeric_type`, `numeric_type` )         `numeric_type`                         Least common multiple (the smallest strictly positive number that is         an integral multiple of both inputs); returns `0` if         either input is zero; available for `integer`,         `bigint`, and `numeric`                         `lcm(1071, 462)`         23562 |
| `ln` ( `numeric` )         numeric                         `ln` ( `double precision` )         double precision                         Natural logarithm                         `ln(2.0)`         0.6931471805599453 |
| `log` ( `numeric` )         numeric                         `log` ( `double precision` )         double precision                         Base 10 logarithm                         `log(100)`         2 |
| `log10` ( `numeric` )         numeric                         `log10` ( `double precision` )         double precision                         Base 10 logarithm (same as `log`)                         `log10(1000)`         3 |
| `log` ( b `numeric`,         x `numeric` )         numeric                         Logarithm of x to base b                        `log(2.0, 64.0)`        6.0000000000000000 |
| `min_scale` ( `numeric` )         integer                         Minimum scale (number of fractional decimal digits) needed         to represent the supplied value precisely                         `min_scale(8.4100)`         2 |
| `mod` ( y `numeric_type`,         x `numeric_type` )         `numeric_type`                         Remainder of y/x;         available for `smallint`, `integer`,         `bigint`, and `numeric`                         `mod(9, 4)`         1 |
| `pi` (  )         double precision                         Approximate value of                          `pi()`         3.141592653589793 |
| `power` ( a `numeric`,         b `numeric` )         numeric                         `power` ( a `double precision`,         b `double precision` )         double precision                         a raised to the power of b                         `power(9, 3)`         729 |
| `radians` ( `double precision` )         double precision                         Converts degrees to radians                         `radians(45.0)`         0.7853981633974483 |
| `round` ( `numeric` )         numeric                         `round` ( `double precision` )         double precision                         Rounds to nearest integer.  For `numeric`, ties are         broken by rounding away from zero.  For `double precision`,         the tie-breaking behavior is platform dependent, but         "round to nearest even" is the most common rule.                         `round(42.4)`         42 |
| `round` ( v `numeric`, s `integer` )         numeric                         Rounds v to s decimal         places.  Ties are broken by rounding away from zero.                         `round(42.4382, 2)`         42.44                         `round(1234.56, -1)`         1230 |
| `scale` ( `numeric` )         integer                         Scale of the argument (the number of decimal digits in the fractional part)                         `scale(8.4100)`         4 |
| `sign` ( `numeric` )         numeric                         `sign` ( `double precision` )         double precision                         Sign of the argument (-1, 0, or +1)                         `sign(-8.4)`         -1 |
| `sqrt` ( `numeric` )          numeric                          `sqrt` ( `double precision` )          double precision                         Square root                         `sqrt(2)`         1.4142135623730951 |
| `trim_scale` ( `numeric` )         numeric                         Reduces the value's scale (number of fractional decimal digits) by         removing trailing zeroes                         `trim_scale(8.4100)`         8.41 |
| `trunc` ( `numeric` )         numeric                         `trunc` ( `double precision` )         double precision                         Truncates to integer (towards zero)                         `trunc(42.8)`         42                         `trunc(-42.8)`         -42 |
| `trunc` ( v `numeric`, s `integer` )        numeric                         Truncates v to s         decimal places                         `trunc(42.4382, 2)`         42.43 |
| `width_bucket` ( operand `numeric`, low `numeric`, high `numeric`, count `integer` )         integer                         `width_bucket` ( operand `double precision`, low `double precision`, high `double precision`, count `integer` )         integer                         Returns the number of the bucket in         which operand falls in a histogram         having count equal-width buckets spanning the         range low to high.         The buckets have inclusive lower bounds and exclusive upper bounds.         Returns `0` for an input less         than low,         or `count+1` for an input         greater than or equal to high.         If low > high,         the behavior is mirror-reversed, with bucket `1`         now being the one just below low, and the         inclusive bounds now being on the upper side.                         `width_bucket(5.35, 0.024, 10.06, 5)`         3                         `width_bucket(9, 10, 0, 10)`         2 |
| `width_bucket` ( operand `anycompatible`, thresholds `anycompatiblearray` )        integer                         Returns the number of the bucket in         which operand falls given an array listing the         inclusive lower bounds of the buckets.         Returns `0` for an input less than the first lower         bound.  operand and the array elements can be         of any type having standard comparison operators.         The thresholds array *must be         sorted*, smallest first, or unexpected results will be         obtained.                         `width_bucket(now(), array['yesterday', 'today', 'tomorrow']::timestamptz[])`         2 |

[functions-math-random-table](#functions-math-random-table) shows functions for
generating random numbers.

| Function                         Description                         Example(s) |
| --- |
| `random` ( )         double precision                         Returns a random value in the range 0.0  **Note:**

> Another way to work with angles measured in degrees is to use the unit
> transformation functions ``radians()``
> and ``degrees()`` shown earlier.
> However, using the degree-based trigonometric functions is preferred,
> as that way avoids round-off error for special cases such
> as `sind(30)`.
>

[functions-math-hyp-table](#functions-math-hyp-table) shows the
available hyperbolic functions.

| Function                         Description                         Example(s) |
| --- |
| `sinh` ( `double precision` )         double precision                         Hyperbolic sine                         `sinh(1)`         1.1752011936438014 |
| `cosh` ( `double precision` )         double precision                         Hyperbolic cosine                         `cosh(0)`         1 |
| `tanh` ( `double precision` )         double precision                         Hyperbolic tangent                         `tanh(1)`         0.7615941559557649 |
| `asinh` ( `double precision` )         double precision                         Inverse hyperbolic sine                         `asinh(1)`         0.881373587019543 |
| `acosh` ( `double precision` )         double precision                         Inverse hyperbolic cosine                         `acosh(1)`         0 |
| `atanh` ( `double precision` )         double precision                         Inverse hyperbolic tangent                         `atanh(0.5)`         0.5493061443340548 |

## String Functions and Operators

This section describes functions and operators for examining and
manipulating string values.  Strings in this context include values
of the types `character`, `character varying`,
and `text`.  Except where noted, these functions and operators
are declared to accept and return type `text`.  They will
interchangeably accept `character varying` arguments.
Values of type `character` will be converted
to `text` before the function or operator is applied, resulting
in stripping any trailing spaces in the `character` value.

SQL defines some string functions that use
key words, rather than commas, to separate
arguments.  Details are in
[functions-string-sql](#functions-string-sql).
PostgreSQL also provides versions of these functions
that use the regular function invocation syntax
(see [functions-string-other](#functions-string-other)).

> **Note:**

> The string concatenation operator (`||`) will accept
> non-string input, so long as at least one input is of string type, as shown
> in [functions-string-sql](#functions-string-sql).  For other cases, inserting an
> explicit coercion to `text` can be used to have non-string input
> accepted.
>

| Function/Operator                         Description                         Example(s) |
| --- |
| `text` `||` `text`         text                         Concatenates the two strings.                         `'Post' || 'greSQL'`         PostgreSQL |
| `text` `||` `anynonarray`         text                         `anynonarray` `||` `text`         text                         Converts the non-string input to text, then concatenates the two         strings.  (The non-string input cannot be of an array type, because         that would create ambiguity with the array `||`         operators.  If you want to concatenate an array's text equivalent,         cast it to `text` explicitly.)                         `'Value: ' || 42`         Value: 42 |
| `btrim` ( string `text`         , characters `text`  )         text                         Removes the longest string containing only characters         in characters (a space by default)         from the start and end of string.                         `btrim('xyxtrimyyx', 'xyz')`         trim |
| `text` `IS` `NOT` form `NORMALIZED`         boolean                         Checks whether the string is in the specified Unicode normalization         form.  The optional form key word specifies the         form: `NFC` (the default), `NFD`,         `NFKC`, or `NFKD`.  This expression can         only be used when the server encoding is `UTF8`.  Note         that checking for normalization using this expression is often faster         than normalizing possibly already normalized strings.                         `U&'\0061\0308bc' IS NFD NORMALIZED`         t |
| `bit_length` ( `text` )         integer                         Returns number of bits in the string (8         times the `octet_length`).                         `bit_length('jose')`         32 |
| `char_length` ( `text` )         integer                                  `character_length` ( `text` )         integer                         Returns number of characters in the string.                         `char_length('jos')`         4 |
| `lower` ( `text` )         text                         Converts the string to all lower case, according to the rules of the         database's locale.                         `lower('TOM')`         tom |
| `lpad` ( string `text`,         length `integer`         , fill `text`  )         text                         Extends the string to length         length by prepending the characters         fill (a space by default).  If the         string is already longer than         length then it is truncated (on the right).                         `lpad('hi', 5, 'xy')`         xyxhi |
| `ltrim` ( string `text`         , characters `text`  )         text                         Removes the longest string containing only characters in         characters (a space by default) from the start of         string.                         `ltrim('zzzytest', 'xyz')`         test |
| `normalize` ( `text`         , form  )         text                         Converts the string to the specified Unicode         normalization form.  The optional form key word         specifies the form: `NFC` (the default),         `NFD`, `NFKC`, or         `NFKD`.  This function can only be used when the         server encoding is `UTF8`.                         `normalize(U&'\0061\0308bc', NFC)`         U&'\00E4bc' |
| `octet_length` ( `text` )         integer                         Returns number of bytes in the string.                         `octet_length('jos')`         5 (if server encoding is UTF8) |
| `octet_length` ( `character` )         integer                         Returns number of bytes in the string.  Since this version of the         function accepts type `character` directly, it will not         strip trailing spaces.                         `octet_length('abc '::character(4))`         4 |
| `overlay` ( string `text` `PLACING` newsubstring `text` `FROM` start `integer`  `FOR` count `integer`  )         text                         Replaces the substring of string that starts at         the start'th character and extends         for count characters         with newsubstring.         If count is omitted, it defaults to the length         of newsubstring.                         `overlay('Txxxxas' placing 'hom' from 2 for 4)`         Thomas |
| `position` ( substring `text` `IN` string `text` )         integer                         Returns first starting index of the specified         substring within         string, or zero if it's not present.                         `position('om' in 'Thomas')`         3 |
| `rpad` ( string `text`,         length `integer`         , fill `text`  )         text                         Extends the string to length         length by appending the characters         fill (a space by default).  If the         string is already longer than         length then it is truncated.                         `rpad('hi', 5, 'xy')`         hixyx |
| `rtrim` ( string `text`          , characters `text`  )         text                         Removes the longest string containing only characters in         characters (a space by default) from the end of         string.                         `rtrim('testxxzx', 'xyz')`         test |
| `substring` ( string `text`  `FROM` start `integer`   `FOR` count `integer`  )         text                         Extracts the substring of string starting at         the start'th character if that is specified,         and stopping after count characters if that is         specified.  Provide at least one of start         and count.                         `substring('Thomas' from 2 for 3)`         hom                         `substring('Thomas' from 3)`         omas                         `substring('Thomas' for 2)`         Th |
| `substring` ( string `text` `FROM` pattern `text` )         text                         Extracts the first substring matching POSIX regular expression; see         [functions-posix-regexp](#functions-posix-regexp).                         `substring('Thomas' from '...$')`         mas |
| `substring` ( string `text` `SIMILAR` pattern `text` `ESCAPE` escape `text` )         text                         `substring` ( string `text` `FROM` pattern `text` `FOR` escape `text` )         text                         Extracts the first substring matching SQL regular expression;         see [functions-similarto-regexp](#functions-similarto-regexp).  The first form has         been specified since SQL:2003; the second form was only in SQL:1999         and should be considered obsolete.                         `substring('Thomas' similar '%#"o_a#"_' escape '#')`         oma |
| `trim` (  `LEADING` | `TRAILING` | `BOTH`           characters `text`  `FROM`         string `text` )         text                         Removes the longest string containing only characters in         characters (a space by default) from the         start, end, or both ends (`BOTH` is the default)         of string.                         `trim(both 'xyz' from 'yxTomxx')`         Tom |
| `trim` (  `LEADING` | `TRAILING` | `BOTH`   `FROM`          string `text` ,         characters `text`  )         text                         This is a non-standard syntax for `trim()`.                         `trim(both from 'yxTomxx', 'xyz')`         Tom |
| `upper` ( `text` )         text                         Converts the string to all upper case, according to the rules of the         database's locale.                         `upper('tom')`         TOM |

Additional string manipulation functions and operators are available
and are listed in [functions-string-other](#functions-string-other).  (Some of
these are used internally to implement
the SQL-standard string functions listed in
[functions-string-sql](#functions-string-sql).)
There are also pattern-matching operators, which are described in
[functions-matching](#functions-matching), and operators for full-text
search, which are described in [textsearch](#textsearch).

| Function/Operator                         Description                         Example(s) |
| --- |
| `text` `^@` `text`         boolean                         Returns true if the first string starts with the second string         (equivalent to the `starts_with()` function).                         `'alphabet' ^@ 'alph'`         t |
| `ascii` ( `text` )         integer                         Returns the numeric code of the first character of the argument.         In UTF8 encoding, returns the Unicode code point         of the character.  In other multibyte encodings, the argument must         be an ASCII character.                         `ascii('x')`         120 |
| `chr` ( `integer` )         text                         Returns the character with the given code. In UTF8         encoding the argument is treated as a Unicode code point. In other         multibyte encodings the argument must designate         an ASCII character.  `chr(0)` is         disallowed because text data types cannot store that character.                       `chr(65)`         A |
| `concat` ( val1 `"any"`          [, val2 `"any"` [, ...] ] )         text                         Concatenates the text representations of all the arguments.         NULL arguments are ignored.                         `concat('abcde', 2, NULL, 22)`         abcde222 |
| `concat_ws` ( sep `text`,         val1 `"any"`         [, val2 `"any"` [, ...] ] )         text                         Concatenates all but the first argument, with separators. The first         argument is used as the separator string, and should not be NULL.         Other NULL arguments are ignored.                         `concat_ws(',', 'abcde', 2, NULL, 22)`         abcde,2,22 |
| `format` ( formatstr `text`         [, formatarg `"any"` [, ...] ] )         text                          Formats arguments according to a format string;          see [functions-string-format](#functions-string-format).          This function is similar to the C function `sprintf`.                         `format('Hello %s, %1$s', 'World')`         Hello World, World |
| `initcap` ( `text` )         text                         Converts the first letter of each word to upper case and the         rest to lower case. Words are sequences of alphanumeric         characters separated by non-alphanumeric characters.                         `initcap('hi THOMAS')`         Hi Thomas |
| `left` ( string `text`,         n `integer` )         text                         Returns first n characters in the         string, or when n is negative, returns         all but last |n| characters.                         `left('abcde', 2)`         ab |
| `length` ( `text` )         integer                         Returns the number of characters in the string.                         `length('jose')`         4 |
| `md5` ( `text` )         text                         Computes the MD5 [hash](#functions-hash-note) of         the argument, with the result written in hexadecimal.                         `md5('abc')`         900150983cd24fb0d6963f7d28e17f72 |
| `parse_ident` ( qualified_identifier `text`         [, strict_mode `boolean` `DEFAULT` `true` ] )         text[]                         Splits qualified_identifier into an array of         identifiers, removing any quoting of individual identifiers.  By         default, extra characters after the last identifier are considered an         error; but if the second parameter is `false`, then such         extra characters are ignored. (This behavior is useful for parsing         names for objects like functions.) Note that this function does not         truncate over-length identifiers. If you want truncation you can cast         the result to `name[]`.                         `parse_ident('"SomeSchema".someTable')`         {SomeSchema,sometable} |
| `pg_client_encoding` ( )         name                         Returns current client encoding name.                         `pg_client_encoding()`         UTF8 |
| `quote_ident` ( `text` )         text                         Returns the given string suitably quoted to be used as an identifier         in an SQL statement string.         Quotes are added only if necessary (i.e., if the string contains         non-identifier characters or would be case-folded).         Embedded quotes are properly doubled.         See also [plpgsql-quote-literal-example](#plpgsql-quote-literal-example).                         `quote_ident('Foo bar')`         "Foo bar" |
| `quote_literal` ( `text` )         text                         Returns the given string suitably quoted to be used as a string literal         in an SQL statement string.         Embedded single-quotes and backslashes are properly doubled.         Note that `quote_literal` returns null on null         input; if the argument might be null,         `quote_nullable` is often more suitable.         See also [plpgsql-quote-literal-example](#plpgsql-quote-literal-example).                         `quote_literal(E'O\'Reilly')`         'O''Reilly' |
| `quote_literal` ( `anyelement` )         text                         Converts the given value to text and then quotes it as a literal.         Embedded single-quotes and backslashes are properly doubled.                         `quote_literal(42.5)`         '42.5' |
| `quote_nullable` ( `text` )         text                         Returns the given string suitably quoted to be used as a string literal         in an SQL statement string; or, if the argument         is null, returns `NULL`.         Embedded single-quotes and backslashes are properly doubled.         See also [plpgsql-quote-literal-example](#plpgsql-quote-literal-example).                         `quote_nullable(NULL)`         NULL |
| `quote_nullable` ( `anyelement` )         text                         Converts the given value to text and then quotes it as a literal;         or, if the argument is null, returns `NULL`.         Embedded single-quotes and backslashes are properly doubled.                         `quote_nullable(42.5)`         '42.5' |
| `regexp_count` ( string `text`, pattern `text`          [, start `integer`          [, flags `text` ] ] )         integer                         Returns the number of times the POSIX regular         expression pattern matches in         the string; see         [functions-posix-regexp](#functions-posix-regexp).                         `regexp_count('123456789012', '\d\d\d', 2)`         3 |
| `regexp_instr` ( string `text`, pattern `text`          [, start `integer`          [, N `integer`          [, endoption `integer`          [, flags `text`          [, subexpr `integer` ] ] ] ] ] )         integer                         Returns the position within string where         the N'th match of the POSIX regular         expression pattern occurs, or zero if there is         no such match; see [functions-posix-regexp](#functions-posix-regexp).                         `regexp_instr('ABCDEF', 'c(.)(..)', 1, 1, 0, 'i')`         3                         `regexp_instr('ABCDEF', 'c(.)(..)', 1, 1, 0, 'i', 2)`         5 |
| `regexp_like` ( string `text`, pattern `text`          [, flags `text` ] )         boolean                         Checks whether a match of the POSIX regular         expression pattern occurs         within string; see         [functions-posix-regexp](#functions-posix-regexp).                         `regexp_like('Hello World', 'world$', 'i')`         t |
| `regexp_match` ( string `text`, pattern `text` [, flags `text` ] )         text[]                         Returns substrings within the first match of the POSIX regular         expression pattern to         the string; see         [functions-posix-regexp](#functions-posix-regexp).                         `regexp_match('foobarbequebaz', '(bar)(beque)')`         {bar,beque} |
| `regexp_matches` ( string `text`, pattern `text` [, flags `text` ] )         setof text[]                         Returns substrings within the first match of the POSIX regular         expression pattern to         the string, or substrings within all         such matches if the `g` flag is used;         see [functions-posix-regexp](#functions-posix-regexp).                         `regexp_matches('foobarbequebaz', 'ba.', 'g')`           ``` {bar}  {baz} ``` |
| `regexp_replace` ( string `text`, pattern `text`, replacement `text`          [, start `integer` ]          [, flags `text` ] )         text                         Replaces the substring that is the first match to the POSIX         regular expression pattern, or all such         matches if the `g` flag is used; see         [functions-posix-regexp](#functions-posix-regexp).                         `regexp_replace('Thomas', '.[mN]a.', 'M')`         ThM |
| `regexp_replace` ( string `text`, pattern `text`, replacement `text`,          start `integer`,          N `integer`          [, flags `text` ] )         text                         Replaces the substring that is the N'th         match to the POSIX regular expression pattern,         or all such matches if N is zero; see         [functions-posix-regexp](#functions-posix-regexp).                         `regexp_replace('Thomas', '.', 'X', 3, 2)`         ThoXas |
| `regexp_split_to_array` ( string `text`, pattern `text` [, flags `text` ] )         text[]                         Splits string using a POSIX regular         expression as the delimiter, producing an array of results; see         [functions-posix-regexp](#functions-posix-regexp).                         `regexp_split_to_array('hello world', '\s+')`         {hello,world} |
| `regexp_split_to_table` ( string `text`, pattern `text` [, flags `text` ] )         setof text                         Splits string using a POSIX regular         expression as the delimiter, producing a set of results; see         [functions-posix-regexp](#functions-posix-regexp).                         `regexp_split_to_table('hello world', '\s+')`           ``` hello  world ``` |
| `regexp_substr` ( string `text`, pattern `text`          [, start `integer`          [, N `integer`          [, flags `text`          [, subexpr `integer` ] ] ] ] )         text                         Returns the substring within string that         matches the N'th occurrence of the POSIX         regular expression pattern,         or `NULL` if there is no such match; see         [functions-posix-regexp](#functions-posix-regexp).                         `regexp_substr('ABCDEF', 'c(.)(..)', 1, 1, 'i')`         CDEF                         `regexp_substr('ABCDEF', 'c(.)(..)', 1, 1, 'i', 2)`         EF |
| `repeat` ( string `text`, number `integer` )         text                         Repeats string the specified         number of times.                         `repeat('Pg', 4)`         PgPgPgPg |
| `replace` ( string `text`,         from `text`,         to `text` )         text                         Replaces all occurrences in string of         substring from with         substring to.                         `replace('abcdefabcdef', 'cd', 'XX')`         abXXefabXXef |
| `reverse` ( `text` )         text                         Reverses the order of the characters in the string.                         `reverse('abcde')`         edcba |
| `right` ( string `text`,          n `integer` )         text                         Returns last n characters in the string,         or when n is negative, returns all but         first |n| characters.                         `right('abcde', 2)`         de |
| `split_part` ( string `text`,         delimiter `text`,         n `integer` )         text                         Splits string at occurrences         of delimiter and returns         the n'th field (counting from one),         or when n is negative, returns         the |n|'th-from-last field.                         `split_part('abc~@~def~@~ghi', '~@~', 2)`         def                         `split_part('abc,def,ghi,jkl', ',', -2)`         ghi |
| `starts_with` ( string `text`, prefix `text` )         boolean                         Returns true if string starts         with prefix.                         `starts_with('alphabet', 'alph')`         t |
| `string_to_array` ( string `text`, delimiter `text` , null_string `text`  )         text[]                         Splits the string at occurrences         of delimiter and forms the resulting fields         into a `text` array.         If delimiter is `NULL`,         each character in the string will become a         separate element in the array.         If delimiter is an empty string, then         the string is treated as a single field.         If null_string is supplied and is         not `NULL`, fields matching that string are         replaced by `NULL`.         See also [`array_to_string`](#function-array-to-string).                         `string_to_array('xx~~yy~~zz', '~~', 'yy')`         {xx,NULL,zz} |
| `string_to_table` ( string `text`, delimiter `text` , null_string `text`  )         setof text                         Splits the string at occurrences         of delimiter and returns the resulting fields         as a set of `text` rows.         If delimiter is `NULL`,         each character in the string will become a         separate row of the result.         If delimiter is an empty string, then         the string is treated as a single field.         If null_string is supplied and is         not `NULL`, fields matching that string are         replaced by `NULL`.                         `string_to_table('xx~^~yy~^~zz', '~^~', 'yy')`           ``` xx  NULL  zz ``` |
| `strpos` ( string `text`, substring `text` )         integer                         Returns first starting index of the specified substring         within string, or zero if it's not present.         (Same as `position(substring in         string)`, but note the reversed         argument order.)                         `strpos('high', 'ig')`         2 |
| `substr` ( string `text`, start `integer` , count `integer`  )         text                         Extracts the substring of string starting at         the start'th character,         and extending for count characters if that is         specified.  (Same         as `substring(string         from start         for count)`.)                         `substr('alphabet', 3)`         phabet                         `substr('alphabet', 3, 2)`         ph |
| `to_ascii` ( string `text` )         text                         `to_ascii` ( string `text`,         encoding `name` )         text                         `to_ascii` ( string `text`,         encoding `integer` )         text                         Converts string to ASCII         from another encoding, which may be identified by name or number.         If encoding is omitted the database encoding         is assumed (which in practice is the only useful case).         The conversion consists primarily of dropping accents.         Conversion is only supported         from `LATIN1`, `LATIN2`,         `LATIN9`, and `WIN1250` encodings.         (See the [unaccent](#unaccent) module for another, more flexible         solution.)                         `to_ascii('Karl')`         Karel |
| `to_hex` ( `integer` )         text                         `to_hex` ( `bigint` )         text                         Converts the number to its equivalent hexadecimal representation.                         `to_hex(2147483647)`         7fffffff |
| `translate` ( string `text`,         from `text`,         to `text` )         text                         Replaces each character in string that         matches a character in the from set with the         corresponding character in the to         set. If from is longer than         to, occurrences of the extra characters in         from are deleted.                         `translate('12345', '143', 'ax')`         a2x5 |
| `unistr` ( `text` )         text                         Evaluate escaped Unicode characters in the argument.  Unicode characters         can be specified as         `\`XXXX`` (4 hexadecimal         digits), `\+`XXXXXX`` (6         hexadecimal digits),         `\u`XXXX`` (4 hexadecimal         digits), or `\U`XXXXXXXX``         (8 hexadecimal digits).  To specify a backslash, write two         backslashes.  All other characters are taken literally.                          If the server encoding is not UTF-8, the Unicode code point identified         by one of these escape sequences is converted to the actual server         encoding; an error is reported if that's not possible.                          This function provides a (non-standard) alternative to string         constants with Unicode escapes (see [sql-syntax-strings-uescape](#sql-syntax-strings-uescape)).                          `unistr('d\0061t\+000061')`         data                         `unistr('d\u0061t\U00000061')`         data |

The `concat`, `concat_ws` and
`format` functions are variadic, so it is possible to
pass the values to be concatenated or formatted as an array marked with
the `VARIADIC` keyword (see [xfunc-sql-variadic-functions](#xfunc-sql-variadic-functions)).  The array's elements are
treated as if they were separate ordinary arguments to the function.
If the variadic array argument is NULL, `concat`
and `concat_ws` return NULL, but
`format` treats a NULL as a zero-element array.

See also the aggregate function `string_agg` in
[functions-aggregate](#functions-aggregate), and the functions for
converting between strings and the `bytea` type in
[functions-binarystring-conversions](#functions-binarystring-conversions).

### `format`

The function `format` produces output formatted according to
a format string, in a style similar to the C function
`sprintf`.

```
`format`(
formatstr `text` [,
formatarg `"any"` [, ...] ])
```

formatstr is a format string that specifies how the
result should be formatted.  Text in the format string is copied
directly to the result, except where *format specifiers* are
used.  Format specifiers act as placeholders in the string, defining how
subsequent function arguments should be formatted and inserted into the
result.  Each
formatarg argument is converted to text
according to the usual output rules for its data type, and then formatted
and inserted into the result string according to the format specifier(s).

Format specifiers are introduced by a `%` character and have
the form

```
%[
position][
flags][
width]
type
```

where the component fields are:

**position (optional)**
: A string of the form `n$` where
n is the index of the argument to print.
Index 1 means the first argument after
formatstr.  If the position is
omitted, the default is to use the next argument in sequence.

**flags (optional)**
: Additional options controlling how the format specifier's output is
formatted.  Currently the only supported flag is a minus sign
(`-`) which will cause the format specifier's output to be
left-justified.  This has no effect unless the width
field is also specified.

**width (optional)**
: Specifies the *minimum* number of characters to use to
display the format specifier's output.  The output is padded on the
left or right (depending on the `-` flag) with spaces as
needed to fill the width.  A too-small width does not cause
truncation of the output, but is simply ignored.  The width may be
specified using any of the following: a positive integer; an
asterisk (`*`) to use the next function argument as the
width; or a string of the form `*n$` to
use the nth function argument as the width.

If the width comes from a function argument, that argument is
consumed before the argument that is used for the format specifier's
value.  If the width argument is negative, the result is left
aligned (as if the `-` flag had been specified) within a
field of length `abs`(width).

**type (required)**
: The type of format conversion to use to produce the format
specifier's output.  The following types are supported:

- `s` formats the argument value as a simple
string.  A null value is treated as an empty string.
- `I` treats the argument value as an SQL
identifier, double-quoting it if necessary.
It is an error for the value to be null (equivalent to
`quote_ident`).
- `L` quotes the argument value as an SQL literal.
A null value is displayed as the string `NULL`, without
quotes (equivalent to `quote_nullable`).

In addition to the format specifiers described above, the special sequence
`%%` may be used to output a literal `%` character.

Here are some examples of the basic format conversions:

```
SELECT format('Hello %s', 'World');
Result: Hello World

SELECT format('Testing %s, %s, %s, %%', 'one', 'two', 'three');
Result: Testing one, two, three, %

SELECT format('INSERT INTO %I VALUES(%L)', 'Foo bar', E'O\'Reilly');
Result: INSERT INTO "Foo bar" VALUES('O''Reilly')

SELECT format('INSERT INTO %I VALUES(%L)', 'locations', 'C:\Program Files');
Result: INSERT INTO locations VALUES('C:\Program Files')
```

Here are examples using
width fields
and the `-` flag:

```
SELECT format('|%10s|', 'foo');
Result: |       foo|

SELECT format('|%-10s|', 'foo');
Result: |foo       |

SELECT format('|%*s|', 10, 'foo');
Result: |       foo|

SELECT format('|%*s|', -10, 'foo');
Result: |foo       |

SELECT format('|%-*s|', 10, 'foo');
Result: |foo       |

SELECT format('|%-*s|', -10, 'foo');
Result: |foo       |
```

These examples show use of
position fields:

```
SELECT format('Testing %3$s, %2$s, %1$s', 'one', 'two', 'three');
Result: Testing three, two, one

SELECT format('|%*2$s|', 'foo', 10, 'bar');
Result: |       bar|

SELECT format('|%1$*2$s|', 'foo', 10, 'bar');
Result: |       foo|
```

Unlike the standard C function `sprintf`,
PostgreSQL's `format` function allows format
specifiers with and without
position fields to be mixed
in the same format string.  A format specifier without a

position field always uses the next argument after the
last argument consumed.
In addition, the `format` function does not require all
function arguments to be used in the format string.
For example:

```
SELECT format('Testing %3$s, %2$s, %s', 'one', 'two', 'three');
Result: Testing three, two, three
```

The `%I` and `%L` format specifiers are particularly
useful for safely constructing dynamic SQL statements.  See
[plpgsql-quote-literal-example](#plpgsql-quote-literal-example).

## Binary String Functions and Operators

This section describes functions and operators for examining and
manipulating binary strings, that is values of type `bytea`.
Many of these are equivalent, in purpose and syntax, to the
text-string functions described in the previous section.

SQL defines some string functions that use
key words, rather than commas, to separate
arguments.  Details are in
[functions-binarystring-sql](#functions-binarystring-sql).
PostgreSQL also provides versions of these functions
that use the regular function invocation syntax
(see [functions-binarystring-other](#functions-binarystring-other)).

| Function/Operator                         Description                         Example(s) |
| --- |
| `bytea` `||` `bytea`         bytea                         Concatenates the two binary strings.                         `'\x123456'::bytea || '\x789a00bcde'::bytea`         \x123456789a00bcde |
| `bit_length` ( `bytea` )         integer                         Returns number of bits in the binary string (8         times the `octet_length`).                         `bit_length('\x123456'::bytea)`         24 |
| `btrim` ( bytes `bytea`,         bytesremoved `bytea` )         bytea                         Removes the longest string containing only bytes appearing in         bytesremoved from the start and end of         bytes.                         `btrim('\x1234567890'::bytea, '\x9012'::bytea)`         \x345678 |
| `ltrim` ( bytes `bytea`,          bytesremoved `bytea` )          bytea                            Removes the longest string containing only bytes appearing in          bytesremoved from the start of          bytes.                            `ltrim('\x1234567890'::bytea, '\x9012'::bytea)`          \x34567890 |
| `octet_length` ( `bytea` )         integer                         Returns number of bytes in the binary string.                         `octet_length('\x123456'::bytea)`         3 |
| `overlay` ( bytes `bytea` `PLACING` newsubstring `bytea` `FROM` start `integer`  `FOR` count `integer`  )         bytea                         Replaces the substring of bytes that starts at         the start'th byte and extends         for count bytes         with newsubstring.         If count is omitted, it defaults to the length         of newsubstring.                         `overlay('\x1234567890'::bytea placing '\002\003'::bytea from 2 for 3)`         \x12020390 |
| `position` ( substring `bytea` `IN` bytes `bytea` )         integer                         Returns first starting index of the specified         substring within         bytes, or zero if it's not present.                         `position('\x5678'::bytea in '\x1234567890'::bytea)`         3 |
| `rtrim` ( bytes `bytea`,          bytesremoved `bytea` )          bytea                            Removes the longest string containing only bytes appearing in          bytesremoved from the end of          bytes.                            `rtrim('\x1234567890'::bytea, '\x9012'::bytea)`          \x12345678 |
| `substring` ( bytes `bytea`  `FROM` start `integer`   `FOR` count `integer`  )         bytea                         Extracts the substring of bytes starting at         the start'th byte if that is specified,         and stopping after count bytes if that is         specified.  Provide at least one of start         and count.                         `substring('\x1234567890'::bytea from 3 for 2)`         \x5678 |
| `trim` (  `LEADING` | `TRAILING` | `BOTH`          bytesremoved `bytea` `FROM`         bytes `bytea` )         bytea                         Removes the longest string containing only bytes appearing in         bytesremoved from the start,         end, or both ends (`BOTH` is the default)         of bytes.                         `trim('\x9012'::bytea from '\x1234567890'::bytea)`         \x345678 |
| `trim` (  `LEADING` | `TRAILING` | `BOTH`   `FROM`          bytes `bytea`,         bytesremoved `bytea` )         bytea                         This is a non-standard syntax for `trim()`.                         `trim(both from '\x1234567890'::bytea, '\x9012'::bytea)`         \x345678 |

Additional binary string manipulation functions are available and
are listed in [functions-binarystring-other](#functions-binarystring-other).  Some
of them are used internally to implement the
SQL-standard string functions listed in [functions-binarystring-sql](#functions-binarystring-sql).

| Function                         Description                         Example(s) |
| --- |
| `bit_count` ( bytes `bytea` )         bigint                         Returns the number of bits set in the binary string (also known as         "popcount").                         `bit_count('\x1234567890'::bytea)`         15 |
| `get_bit` ( bytes `bytea`,         n `bigint` )         integer                         Extracts [n'th](#functions-zerobased-note) bit         from binary string.                         `get_bit('\x1234567890'::bytea, 30)`         1 |
| `get_byte` ( bytes `bytea`,         n `integer` )         integer                         Extracts [n'th](#functions-zerobased-note) byte         from binary string.                         `get_byte('\x1234567890'::bytea, 4)`         144 |
| `length` ( `bytea` )         integer                         Returns the number of bytes in the binary string.                         `length('\x1234567890'::bytea)`         5 |
| `length` ( bytes `bytea`,         encoding `name` )         integer                         Returns the number of characters in the binary string, assuming         that it is text in the given encoding.                         `length('jose'::bytea, 'UTF8')`         4 |
| `md5` ( `bytea` )         text                         Computes the MD5 [hash](#functions-hash-note) of         the binary string, with the result written in hexadecimal.                         `md5('Th\000omas'::bytea)`         8ab2d3c9689aaf18b4958c334c82d8b1 |
| `set_bit` ( bytes `bytea`,         n `bigint`,         newvalue `integer` )         bytea                         Sets [n'th](#functions-zerobased-note) bit in         binary string to newvalue.                         `set_bit('\x1234567890'::bytea, 30, 0)`         \x1234563890 |
| `set_byte` ( bytes `bytea`,         n `integer`,         newvalue `integer` )         bytea                         Sets [n'th](#functions-zerobased-note) byte in         binary string to newvalue.                         `set_byte('\x1234567890'::bytea, 4, 64)`         \x1234567840 |
| `sha224` ( `bytea` )         bytea                         Computes the SHA-224 [hash](#functions-hash-note)         of the binary string.                         `sha224('abc'::bytea)`         \x23097d223405d8228642a477bda255b32aadbce4bda0b3f7e36c9da7 |
| `sha256` ( `bytea` )         bytea                         Computes the SHA-256 [hash](#functions-hash-note)         of the binary string.                         `sha256('abc'::bytea)`         \xba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad |
| `sha384` ( `bytea` )         bytea                         Computes the SHA-384 [hash](#functions-hash-note)         of the binary string.                         `sha384('abc'::bytea)`         \xcb00753f45a35e8bb5a03d699ac65007272c32ab0eded1631a8b605a43ff5bed8086072ba1e7cc2358baeca134c825a7 |
| `sha512` ( `bytea` )         bytea                         Computes the SHA-512 [hash](#functions-hash-note)         of the binary string.                         `sha512('abc'::bytea)`         \xddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f |
| `substr` ( bytes `bytea`, start `integer` , count `integer`  )         bytea                         Extracts the substring of bytes starting at         the start'th byte,         and extending for count bytes if that is         specified.  (Same         as `substring(bytes         from start         for count)`.)                         `substr('\x1234567890'::bytea, 3, 2)`         \x5678 |

Functions `get_byte` and `set_byte`
number the first byte of a binary string as byte 0.
Functions `get_bit` and `set_bit`
number bits from the right within each byte; for example bit 0 is the least
significant bit of the first byte, and bit 15 is the most significant bit
of the second byte.

For historical reasons, the function `md5`
returns a hex-encoded value of type `text` whereas the SHA-2
functions return type `bytea`.  Use the functions
[`encode`](#function-encode)
and [`decode`](#function-decode) to
convert between the two.  For example write `encode(sha256('abc'),
'hex')` to get a hex-encoded text representation,
or `decode(md5('abc'), 'hex')` to get
a `bytea` value.

Functions for converting strings between different character sets
(encodings), and for representing arbitrary binary data in textual
form, are shown in
[functions-binarystring-conversions](#functions-binarystring-conversions).  For these
functions, an argument or result of type `text` is expressed
in the database's default encoding, while arguments or results of
type `bytea` are in an encoding named by another argument.

| Function                      Description                      Example(s) |
| --- |
| `convert` ( bytes `bytea`,        src_encoding `name`,        dest_encoding `name` )        bytea                      Converts a binary string representing text in        encoding src_encoding        to a binary string in encoding dest_encoding        (see [multibyte-conversions-supported](#multibyte-conversions-supported) for        available conversions).                      `convert('text_in_utf8', 'UTF8', 'LATIN1')`        \x746578745f696e5f75746638 |
| `convert_from` ( bytes `bytea`,        src_encoding `name` )        text                      Converts a binary string representing text in        encoding src_encoding        to `text` in the database encoding        (see [multibyte-conversions-supported](#multibyte-conversions-supported) for        available conversions).                      `convert_from('text_in_utf8', 'UTF8')`        text_in_utf8 |
| `convert_to` ( string `text`,        dest_encoding `name` )        bytea                      Converts a `text` string (in the database encoding) to a        binary string encoded in encoding dest_encoding        (see [multibyte-conversions-supported](#multibyte-conversions-supported) for        available conversions).                      `convert_to('some_text', 'UTF8')`        \x736f6d655f74657874 |
| `encode` ( bytes `bytea`,        format `text` )        text                      Encodes binary data into a textual representation; supported        format values are:        [`base64`](#encode-format-base64),        [`escape`](#encode-format-escape),        [`hex`](#encode-format-hex).                      `encode('123\000\001', 'base64')`        MTIzAAE= |
| `decode` ( string `text`,        format `text` )        bytea                      Decodes binary data from a textual representation; supported        format values are the same as        for `encode`.                      `decode('MTIzAAE=', 'base64')`        \x3132330001 |

The `encode` and `decode`
functions support the following textual formats:

**base64**
: The `base64` format is that
of [RFC
2045 Section 6.8](https://datatracker.ietf.org/doc/html/rfc2045#section-6.8).  As per the RFC, encoded lines are
broken at 76 characters.  However instead of the MIME CRLF
end-of-line marker, only a newline is used for end-of-line.
The `decode` function ignores carriage-return,
newline, space, and tab characters.  Otherwise, an error is
raised when `decode` is supplied invalid
base64 data — including when trailing padding is incorrect.

**escape**
: The `escape` format converts zero bytes and
bytes with the high bit set into octal escape sequences
(`\``nnn`), and it doubles
backslashes.  Other byte values are represented literally.
The `decode` function will raise an error if a
backslash is not followed by either a second backslash or three
octal digits; it accepts other byte values unchanged.

**hex**
: The `hex` format represents each 4 bits of
data as one hexadecimal digit, `0`
through `f`, writing the higher-order digit of
each byte first.  The `encode` function outputs
the `a`-`f` hex digits in lower
case.  Because the smallest unit of data is 8 bits, there are
always an even number of characters returned
by `encode`.
The `decode` function
accepts the `a`-`f` characters in
either upper or lower case.  An error is raised
when `decode` is given invalid hex data
— including when given an odd number of characters.

See also the aggregate function `string_agg` in
[functions-aggregate](#functions-aggregate) and the large object functions
in [lo-funcs](#lo-funcs).

## Bit String Functions and Operators

This section describes functions and operators for examining and
manipulating bit strings, that is values of the types
`bit` and `bit varying`.  (While only
type `bit` is mentioned in these tables, values of
type `bit varying` can be used interchangeably.)
Bit strings support the usual comparison operators shown in
[functions-comparison-op-table](#functions-comparison-op-table), as well as the
operators shown in [functions-bit-string-op-table](#functions-bit-string-op-table).

| Operator                         Description                         Example(s) |
| --- |
| `bit` `||` `bit`         bit                         Concatenation                         `B'10001' || B'011'`         10001011 |
| `bit` `&` `bit`         bit                         Bitwise AND (inputs must be of equal length)                         `B'10001' & B'01101'`         00001 |
| `bit` `|` `bit`         bit                         Bitwise OR (inputs must be of equal length)                         `B'10001' | B'01101'`         11101 |
| `bit` `#` `bit`         bit                         Bitwise exclusive OR (inputs must be of equal length)                         `B'10001' # B'01101'`         11100 |
| `~` `bit`         bit                         Bitwise NOT                         `~ B'10001'`         01110 |
| `bit` `>` `integer`         bit                         Bitwise shift right         (string length is preserved)                         `B'10001' >> 2`         00100 |

Some of the functions available for binary strings are also available
for bit strings, as shown in [functions-bit-string-table](#functions-bit-string-table).

| Function                         Description                         Example(s) |
| --- |
| `bit_count` ( `bit` )         bigint                         Returns the number of bits set in the bit string (also known as         "popcount").                         `bit_count(B'10111')`         4 |
| `bit_length` ( `bit` )         integer                         Returns number of bits in the bit string.                         `bit_length(B'10111')`         5 |
| `length` ( `bit` )         integer                         Returns number of bits in the bit string.                         `length(B'10111')`         5 |
| `octet_length` ( `bit` )         integer                         Returns number of bytes in the bit string.                         `octet_length(B'1011111011')`         2 |
| `overlay` ( bits `bit` `PLACING` newsubstring `bit` `FROM` start `integer`  `FOR` count `integer`  )         bit                         Replaces the substring of bits that starts at         the start'th bit and extends         for count bits         with newsubstring.         If count is omitted, it defaults to the length         of newsubstring.                         `overlay(B'01010101010101010' placing B'11111' from 2 for 3)`         0111110101010101010 |
| `position` ( substring `bit` `IN` bits `bit` )         integer                         Returns first starting index of the specified substring         within bits, or zero if it's not present.                         `position(B'010' in B'000001101011')`         8 |
| `substring` ( bits `bit`  `FROM` start `integer`   `FOR` count `integer`  )         bit                         Extracts the substring of bits starting at         the start'th bit if that is specified,         and stopping after count bits if that is         specified.  Provide at least one of start         and count.                         `substring(B'110010111111' from 3 for 2)`         00 |
| `get_bit` ( bits `bit`,         n `integer` )         integer                         Extracts n'th bit         from bit string; the first (leftmost) bit is bit 0.                         `get_bit(B'101010101010101010', 6)`         1 |
| `set_bit` ( bits `bit`,         n `integer`,         newvalue `integer` )         bit                         Sets n'th bit in         bit string to newvalue;         the first (leftmost) bit is bit 0.                         `set_bit(B'101010101010101010', 6, 0)`         101010001010101010 |

In addition, it is possible to cast integral values to and from type
`bit`.
Casting an integer to `bit(n)` copies the rightmost
`n` bits.  Casting an integer to a bit string width wider
than the integer itself will sign-extend on the left.
Some examples:

```
44::bit(10)                    0000101100
44::bit(3)                     100
cast(-44 as bit(12))           111111010100
'1110'::bit(4)::integer        14
```

Note that casting to just "bit" means casting to
`bit(1)`, and so will deliver only the least significant
bit of the integer.

## Pattern Matching

There are three separate approaches to pattern matching provided
by PostgreSQL: the traditional
SQL `LIKE` operator, the
more recent `SIMILAR TO` operator (added in
SQL:1999), and POSIX-style regular
expressions.  Aside from the basic "does this string match
this pattern?" operators, functions are available to extract
or replace matching substrings and to split a string at matching
locations.

> **Tip:**

> If you have pattern matching needs that go beyond this,
> consider writing a user-defined function in Perl or Tcl.
>

> **Caution:**

> While most regular-expression searches can be executed very quickly,
> regular expressions can be contrived that take arbitrary amounts of
> time and memory to process.  Be wary of accepting regular-expression
> search patterns from hostile sources.  If you must do so, it is
> advisable to impose a statement timeout.
>

>

> Searches using `SIMILAR TO` patterns have the same
> security hazards, since `SIMILAR TO` provides many
> of the same capabilities as POSIX-style regular
> expressions.
>

>

> `LIKE` searches, being much simpler than the other
> two options, are safer to use with possibly-hostile pattern sources.
>

The pattern matching operators of all three kinds do not support
nondeterministic collations.  If required, apply a different collation to
the expression to work around this limitation.

### `LIKE`

```
`string` LIKE `pattern` ESCAPE `escape-character`
`string` NOT LIKE `pattern` ESCAPE `escape-character`
```

The `LIKE` expression returns true if the
`string` matches the supplied
`pattern`.  (As
expected, the `NOT LIKE` expression returns
false if `LIKE` returns true, and vice versa.
An equivalent expression is
`NOT (`string` LIKE
`pattern`)`.)

If `pattern` does not contain percent
signs or underscores, then the pattern only represents the string
itself; in that case `LIKE` acts like the
equals operator.  An underscore (`_`) in
`pattern` stands for (matches) any single
character; a percent sign (`%`) matches any sequence
of zero or more characters.

Some examples:

```
'abc' LIKE 'abc'    true
'abc' LIKE 'a%'     true
'abc' LIKE '_b_'    true
'abc' LIKE 'c'      false
```

`LIKE` pattern matching always covers the entire
string.  Therefore, if it's desired to match a sequence anywhere within
a string, the pattern must start and end with a percent sign.

To match a literal underscore or percent sign without matching
other characters, the respective character in
`pattern` must be
preceded by the escape character.  The default escape
character is the backslash but a different one can be selected by
using the `ESCAPE` clause.  To match the escape
character itself, write two escape characters.

> **Note:**

> If you have [guc-standard-conforming-strings](#guc-standard-conforming-strings) turned off,
> any backslashes you write in literal string constants will need to be
> doubled.  See [sql-syntax-strings](#sql-syntax-strings) for more information.
>

It's also possible to select no escape character by writing
`ESCAPE ''`.  This effectively disables the
escape mechanism, which makes it impossible to turn off the
special meaning of underscore and percent signs in the pattern.

According to the SQL standard, omitting `ESCAPE`
means there is no escape character (rather than defaulting to a
backslash), and a zero-length `ESCAPE` value is
disallowed.  PostgreSQL's behavior in
this regard is therefore slightly nonstandard.

The key word `ILIKE` can be used instead of
`LIKE` to make the match case-insensitive according
to the active locale.  This is not in the SQL standard but is a
PostgreSQL extension.

The operator `~~` is equivalent to
`LIKE`, and `~~*` corresponds to
`ILIKE`.  There are also
`!~~` and `!~~*` operators that
represent `NOT LIKE` and `NOT
ILIKE`, respectively.  All of these operators are
PostgreSQL-specific.  You may see these
operator names in `EXPLAIN` output and similar
places, since the parser actually translates `LIKE`
et al. to these operators.

The phrases `LIKE`, `ILIKE`,
`NOT LIKE`, and `NOT ILIKE` are
generally treated as operators
in PostgreSQL syntax; for example they can
be used in `expression`
`operator` ANY
(`subquery`) constructs, although
an `ESCAPE` clause cannot be included there.  In some
obscure cases it may be necessary to use the underlying operator names
instead.

Also see the starts-with operator `^@` and the
corresponding `starts_with()` function, which are
useful in cases where simply matching the beginning of a string is
needed.

### `SIMILAR TO` Regular Expressions

```
`string` SIMILAR TO `pattern` ESCAPE `escape-character`
`string` NOT SIMILAR TO `pattern` ESCAPE `escape-character`
```

The `SIMILAR TO` operator returns true or
false depending on whether its pattern matches the given string.
It is similar to `LIKE`, except that it
interprets the pattern using the SQL standard's definition of a
regular expression.  SQL regular expressions are a curious cross
between `LIKE` notation and common (POSIX) regular
expression notation.

Like `LIKE`, the `SIMILAR TO`
operator succeeds only if its pattern matches the entire string;
this is unlike common regular expression behavior where the pattern
can match any part of the string.
Also like
`LIKE`, `SIMILAR TO` uses
`_` and `%` as wildcard characters denoting
any single character and any string, respectively (these are
comparable to `.` and `.*` in POSIX regular
expressions).

In addition to these facilities borrowed from `LIKE`,
`SIMILAR TO` supports these pattern-matching
metacharacters borrowed from POSIX regular expressions:

- `|` denotes alternation (either of two alternatives).
- `*` denotes repetition of the previous item zero
or more times.
- `+` denotes repetition of the previous item one
or more times.
- `?` denotes repetition of the previous item zero
or one time.
- `{``m``}` denotes repetition
of the previous item exactly `m` times.
- `{``m``,}` denotes repetition
of the previous item `m` or more times.
- `{``m``,``n``}`
denotes repetition of the previous item at least `m` and
not more than `n` times.
- Parentheses `()` can be used to group items into
a single logical item.
- A bracket expression `[...]` specifies a character
class, just as in POSIX regular expressions.

Notice that the period (`.`) is not a metacharacter
for `SIMILAR TO`.

As with `LIKE`, a backslash disables the special
meaning of any of these metacharacters.  A different escape character
can be specified with `ESCAPE`, or the escape
capability can be disabled by writing `ESCAPE ''`.

According to the SQL standard, omitting `ESCAPE`
means there is no escape character (rather than defaulting to a
backslash), and a zero-length `ESCAPE` value is
disallowed.  PostgreSQL's behavior in
this regard is therefore slightly nonstandard.

Another nonstandard extension is that following the escape character
with a letter or digit provides access to the escape sequences
defined for POSIX regular expressions; see
[posix-character-entry-escapes-table](#posix-character-entry-escapes-table),
[posix-class-shorthand-escapes-table](#posix-class-shorthand-escapes-table), and
[posix-constraint-escapes-table](#posix-constraint-escapes-table) below.

Some examples:

```
'abc' SIMILAR TO 'abc'          true
'abc' SIMILAR TO 'a'            false
'abc' SIMILAR TO '%(b|d)%'      true
'abc' SIMILAR TO '(b|c)%'       false
'-abc-' SIMILAR TO '%\mabc\M%'  true
'xabcy' SIMILAR TO '%\mabc\M%'  false
```

The `substring` function with three parameters
provides extraction of a substring that matches an SQL
regular expression pattern.  The function can be written according
to standard SQL syntax:

```
substring(`string` similar `pattern` escape `escape-character`)
```

or using the now obsolete SQL:1999 syntax:

```
substring(`string` from `pattern` for `escape-character`)
```

or as a plain three-argument function:

```
substring(`string`, `pattern`, `escape-character`)
```

As with `SIMILAR TO`, the
specified pattern must match the entire data string, or else the
function fails and returns null.  To indicate the part of the
pattern for which the matching data sub-string is of interest,
the pattern should contain
two occurrences of the escape character followed by a double quote
(`"`).
The text matching the portion of the pattern
between these separators is returned when the match is successful.

The escape-double-quote separators actually
divide `substring`'s pattern into three independent
regular expressions; for example, a vertical bar (`|`)
in any of the three sections affects only that section.  Also, the first
and third of these regular expressions are defined to match the smallest
possible amount of text, not the largest, when there is any ambiguity
about how much of the data string matches which pattern.  (In POSIX
parlance, the first and third regular expressions are forced to be
non-greedy.)

As an extension to the SQL standard, PostgreSQL
allows there to be just one escape-double-quote separator, in which case
the third regular expression is taken as empty; or no separators, in which
case the first and third regular expressions are taken as empty.

Some examples, with `#"` delimiting the return string:

```
substring('foobar' similar '%#"o_b#"%' escape '#')   oob
substring('foobar' similar '#"o_b#"%' escape '#')    NULL
```

### POSIX Regular Expressions

[functions-posix-table](#functions-posix-table) lists the available
operators for pattern matching using POSIX regular expressions.

| Operator                         Description                         Example(s) |
| --- |
| `text` `~` `text`         boolean                         String matches regular expression, case sensitively                         `'thomas' ~ 't.*ma'`         t |
| `text` `~*` `text`         boolean                         String matches regular expression, case-insensitively                         `'thomas' ~* 'T.*ma'`         t |
| `text` `!~` `text`         boolean                         String does not match regular expression, case sensitively                         `'thomas' !~ 't.*max'`         t |
| `text` `!~*` `text`         boolean                         String does not match regular expression, case-insensitively                         `'thomas' !~* 'T.*ma'`         f |

POSIX regular expressions provide a more
powerful means for pattern matching than the `LIKE` and
`SIMILAR TO` operators.
Many Unix tools such as `egrep`,
`sed`, or `awk` use a pattern
matching language that is similar to the one described here.

A regular expression is a character sequence that is an
abbreviated definition of a set of strings (a *regular
set*).  A string is said to match a regular expression
if it is a member of the regular set described by the regular
expression.  As with `LIKE`, pattern characters
match string characters exactly unless they are special characters
in the regular expression language — but regular expressions use
different special characters than `LIKE` does.
Unlike `LIKE` patterns, a
regular expression is allowed to match anywhere within a string, unless
the regular expression is explicitly anchored to the beginning or
end of the string.

Some examples:

```
'abcd' ~ 'bc'     true
'abcd' ~ 'a.c'    true — dot matches any character
'abcd' ~ 'a.*d'   true — `*` repeats the preceding pattern item
'abcd' ~ '(b|x)'  true — `|` means OR, parentheses group
'abcd' ~ '^a'     true — `^` anchors to start of string
'abcd' ~ '^(b|c)' false — would match except for anchoring
```

The POSIX pattern language is described in much
greater detail below.

The `substring` function with two parameters,
`substring(`string` from
`pattern`)`, provides extraction of a
substring
that matches a POSIX regular expression pattern.  It returns null if
there is no match, otherwise the first portion of the text that matched the
pattern.  But if the pattern contains any parentheses, the portion
of the text that matched the first parenthesized subexpression (the
one whose left parenthesis comes first) is
returned.  You can put parentheses around the whole expression
if you want to use parentheses within it without triggering this
exception.  If you need parentheses in the pattern before the
subexpression you want to extract, see the non-capturing parentheses
described below.

Some examples:

```
substring('foobar' from 'o.b')     oob
substring('foobar' from 'o(.)b')   o
```

The `regexp_count` function counts the number of
places where a POSIX regular expression pattern matches a string.
It has the syntax
`regexp_count`(`string`,
`pattern`
, `start`
, `flags`
).
`pattern` is searched for
in `string`, normally from the beginning of
the string, but if the `start` parameter is
provided then beginning from that character index.
The `flags` parameter is an optional text
string containing zero or more single-letter flags that change the
function's behavior.  For example, including `i` in
`flags` specifies case-insensitive matching.
Supported flags are described in
[posix-embedded-options-table](#posix-embedded-options-table).

Some examples:

```
regexp_count('ABCABCAXYaxy', 'A.')          3
regexp_count('ABCABCAXYaxy', 'A.', 1, 'i')  4
```

The `regexp_instr` function returns the starting or
ending position of the `N`'th match of a
POSIX regular expression pattern to a string, or zero if there is no
such match.  It has the syntax
`regexp_instr`(`string`,
`pattern`
, `start`
, `N`
, `endoption`
, `flags`
, `subexpr`
).
`pattern` is searched for
in `string`, normally from the beginning of
the string, but if the `start` parameter is
provided then beginning from that character index.
If `N` is specified
then the `N`'th match of the pattern
is located, otherwise the first match is located.
If the `endoption` parameter is omitted or
specified as zero, the function returns the position of the first
character of the match.  Otherwise, `endoption`
must be one, and the function returns the position of the character
following the match.
The `flags` parameter is an optional text
string containing zero or more single-letter flags that change the
function's behavior.  Supported flags are described
in [posix-embedded-options-table](#posix-embedded-options-table).
For a pattern containing parenthesized
subexpressions, `subexpr` is an integer
indicating which subexpression is of interest: the result identifies
the position of the substring matching that subexpression.
Subexpressions are numbered in the order of their leading parentheses.
When `subexpr` is omitted or zero, the result
identifies the position of the whole match regardless of
parenthesized subexpressions.

Some examples:

```
regexp_instr('number of your street, town zip, FR', '[^,]+', 1, 2)
23
regexp_instr('ABCDEFGHI', '(c..)(...)', 1, 1, 0, 'i', 2)
6
```

The `regexp_like` function checks whether a match
of a POSIX regular expression pattern occurs within a string,
returning boolean true or false.  It has the syntax
`regexp_like`(`string`,
`pattern`
, `flags` ).
The `flags` parameter is an optional text
string containing zero or more single-letter flags that change the
function's behavior.  Supported flags are described
in [posix-embedded-options-table](#posix-embedded-options-table).
This function has the same results as the `~`
operator if no flags are specified.  If only the `i`
flag is specified, it has the same results as
the `~*` operator.

Some examples:

```
regexp_like('Hello World', 'world')       false
regexp_like('Hello World', 'world', 'i')  true
```

The `regexp_match` function returns a text array of
matching substring(s) within the first match of a POSIX
regular expression pattern to a string.  It has the syntax
`regexp_match`(`string`,
`pattern` , `flags` ).
If there is no match, the result is `NULL`.
If a match is found, and the `pattern` contains no
parenthesized subexpressions, then the result is a single-element text
array containing the substring matching the whole pattern.
If a match is found, and the `pattern` contains
parenthesized subexpressions, then the result is a text array
whose `n`'th element is the substring matching
the `n`'th parenthesized subexpression of
the `pattern` (not counting "non-capturing"
parentheses; see below for details).
The `flags` parameter is an optional text string
containing zero or more single-letter flags that change the function's
behavior.  Supported flags are described
in [posix-embedded-options-table](#posix-embedded-options-table).

Some examples:

```
SELECT regexp_match('foobarbequebaz', 'bar.*que');
regexp_match
--------------
{barbeque}
(1 row)

SELECT regexp_match('foobarbequebaz', '(bar)(beque)');
regexp_match
--------------
{bar,beque}
(1 row)
```

> **Tip:**

> In the common case where you just want the whole matching substring
> or `NULL` for no match, the best solution is to
> use `regexp_substr()`.
> However, `regexp_substr()` only exists
> in PostgreSQL version 15 and up.  When
> working in older versions, you can extract the first element
> of `regexp_match()`'s result, for example:
> ```
> SELECT (regexp_match('foobarbequebaz', 'bar.*que'))[1];
> regexp_match
> --------------
> barbeque
> (1 row)
> ```
>

The `regexp_matches` function returns a set of text arrays
of matching substring(s) within matches of a POSIX regular
expression pattern to a string.  It has the same syntax as
`regexp_match`.
This function returns no rows if there is no match, one row if there is
a match and the `g` flag is not given, or `N`
rows if there are `N` matches and the `g` flag
is given.  Each returned row is a text array containing the whole
matched substring or the substrings matching parenthesized
subexpressions of the `pattern`, just as described above
for `regexp_match`.
`regexp_matches` accepts all the flags shown
in [posix-embedded-options-table](#posix-embedded-options-table), plus
the `g` flag which commands it to return all matches, not
just the first one.

Some examples:

```
SELECT regexp_matches('foo', 'not there');
regexp_matches
----------------
(0 rows)

SELECT regexp_matches('foobarbequebazilbarfbonk', '(b[^b]+)(b[^b]+)', 'g');
regexp_matches
----------------
{bar,beque}
{bazil,barf}
(2 rows)
```

> **Tip:**

> In most cases `regexp_matches()` should be used with
> the `g` flag, since if you only want the first match, it's
> easier and more efficient to use `regexp_match()`.
> However, `regexp_match()` only exists
> in PostgreSQL version 10 and up.  When working in older
> versions, a common trick is to place a `regexp_matches()`
> call in a sub-select, for example:
> ```
> SELECT col1, (SELECT regexp_matches(col2, '(bar)(beque)')) FROM tab;
> ```
> This produces a text array if there's a match, or `NULL` if
> not, the same as `regexp_match()` would do.  Without the
> sub-select, this query would produce no output at all for table rows
> without a match, which is typically not the desired behavior.
>

The `regexp_replace` function provides substitution of
new text for substrings that match POSIX regular expression patterns.
It has the syntax
`regexp_replace`(`source`,
`pattern`, `replacement`
, `start`
, `N`

, `flags` ).
(Notice that `N` cannot be specified
unless `start` is,
but `flags` can be given in any case.)
The `source` string is returned unchanged if
there is no match to the `pattern`.  If there is a
match, the `source` string is returned with the
`replacement` string substituted for the matching
substring.  The `replacement` string can contain
`\``n`, where `n` is 1
through 9, to indicate that the source substring matching the
`n`'th parenthesized subexpression of the pattern should be
inserted, and it can contain `\&` to indicate that the
substring matching the entire pattern should be inserted.  Write
`\\` if you need to put a literal backslash in the replacement
text.
`pattern` is searched for
in `string`, normally from the beginning of
the string, but if the `start` parameter is
provided then beginning from that character index.
By default, only the first match of the pattern is replaced.
If `N` is specified and is greater than zero,
then the `N`'th match of the pattern
is replaced.
If the `g` flag is given, or
if `N` is specified and is zero, then all
matches at or after the `start` position are
replaced.  (The `g` flag is ignored
when `N` is specified.)
The `flags` parameter is an optional text
string containing zero or more single-letter flags that change the
function's behavior.  Supported flags (though
not `g`) are
described in [posix-embedded-options-table](#posix-embedded-options-table).

Some examples:

```
regexp_replace('foobarbaz', 'b..', 'X')
fooXbaz
regexp_replace('foobarbaz', 'b..', 'X', 'g')
fooXX
regexp_replace('foobarbaz', 'b(..)', 'X\1Y', 'g')
fooXarYXazY
regexp_replace('A PostgreSQL function', 'a|e|i|o|u', 'X', 1, 0, 'i')
X PXstgrXSQL fXnctXXn
regexp_replace('A PostgreSQL function', 'a|e|i|o|u', 'X', 1, 3, 'i')
A PostgrXSQL function
```

The `regexp_split_to_table` function splits a string using a POSIX
regular expression pattern as a delimiter.  It has the syntax
`regexp_split_to_table`(`string`, `pattern`
, `flags` ).
If there is no match to the `pattern`, the function returns the
`string`.  If there is at least one match, for each match it returns
the text from the end of the last match (or the beginning of the string)
to the beginning of the match.  When there are no more matches, it
returns the text from the end of the last match to the end of the string.
The `flags` parameter is an optional text string containing
zero or more single-letter flags that change the function's behavior.
`regexp_split_to_table` supports the flags described in
[posix-embedded-options-table](#posix-embedded-options-table).

The `regexp_split_to_array` function behaves the same as
`regexp_split_to_table`, except that `regexp_split_to_array`
returns its result as an array of `text`.  It has the syntax
`regexp_split_to_array`(`string`, `pattern`
, `flags` ).
The parameters are the same as for `regexp_split_to_table`.

Some examples:

```
SELECT foo FROM regexp_split_to_table('the quick brown fox jumps over the lazy dog', '\s+') AS foo;
foo
-------
the
quick
brown
fox
jumps
over
the
lazy
dog
(9 rows)

SELECT regexp_split_to_array('the quick brown fox jumps over the lazy dog', '\s+');
regexp_split_to_array
-----------------------------------------------
{the,quick,brown,fox,jumps,over,the,lazy,dog}
(1 row)

SELECT foo FROM regexp_split_to_table('the quick brown fox', '\s*') AS foo;
foo
-----
t
h
e
q
u
i
c
k
b
r
o
w
n
f
o
x
(16 rows)
```

As the last example demonstrates, the regexp split functions ignore
zero-length matches that occur at the start or end of the string
or immediately after a previous match.  This is contrary to the strict
definition of regexp matching that is implemented by
the other regexp functions, but is usually the most convenient behavior
in practice.  Other software systems such as Perl use similar definitions.

The `regexp_substr` function returns the substring
that matches a POSIX regular expression pattern,
or `NULL` if there is no match.  It has the syntax
`regexp_substr`(`string`,
`pattern`
, `start`
, `N`
, `flags`
, `subexpr`
).
`pattern` is searched for
in `string`, normally from the beginning of
the string, but if the `start` parameter is
provided then beginning from that character index.
If `N` is specified
then the `N`'th match of the pattern
is returned, otherwise the first match is returned.
The `flags` parameter is an optional text
string containing zero or more single-letter flags that change the
function's behavior.  Supported flags are described
in [posix-embedded-options-table](#posix-embedded-options-table).
For a pattern containing parenthesized
subexpressions, `subexpr` is an integer
indicating which subexpression is of interest: the result is the
substring matching that subexpression.
Subexpressions are numbered in the order of their leading parentheses.
When `subexpr` is omitted or zero, the result
is the whole match regardless of parenthesized subexpressions.

Some examples:

```
regexp_substr('number of your street, town zip, FR', '[^,]+', 1, 2)
town zip
regexp_substr('ABCDEFGHI', '(c..)(...)', 1, 1, 'i', 2)
FGH
```

#### Regular Expression Details

PostgreSQL's regular expressions are implemented
using a software package written by Henry Spencer.  Much of
the description of regular expressions below is copied verbatim from his
manual.

Regular expressions (REs), as defined in
POSIX 1003.2, come in two forms:
*extended* REs or EREs
(roughly those of `egrep`), and
*basic* REs or BREs
(roughly those of `ed`).
PostgreSQL supports both forms, and
also implements some extensions
that are not in the POSIX standard, but have become widely used
due to their availability in programming languages such as Perl and Tcl.
REs using these non-POSIX extensions are called
*advanced* REs or AREs
in this documentation.  AREs are almost an exact superset of EREs,
but BREs have several notational incompatibilities (as well as being
much more limited).
We first describe the ARE and ERE forms, noting features that apply
only to AREs, and then describe how BREs differ.

> **Note:**

> PostgreSQL always initially presumes that a regular
> expression follows the ARE rules.  However, the more limited ERE or
> BRE rules can be chosen by prepending an *embedded option*
> to the RE pattern, as described in [posix-metasyntax](#posix-metasyntax).
> This can be useful for compatibility with applications that expect
> exactly the POSIX 1003.2 rules.
>

A regular expression is defined as one or more
*branches*, separated by
`|`.  It matches anything that matches one of the
branches.

A branch is zero or more *quantified atoms* or
*constraints*, concatenated.
It matches a match for the first, followed by a match for the second, etc.;
an empty branch matches the empty string.

A quantified atom is an *atom* possibly followed
by a single *quantifier*.
Without a quantifier, it matches a match for the atom.
With a quantifier, it can match some number of matches of the atom.
An *atom* can be any of the possibilities
shown in [posix-atoms-table](#posix-atoms-table).
The possible quantifiers and their meanings are shown in
[posix-quantifiers-table](#posix-quantifiers-table).

A *constraint* matches an empty string, but matches only when
specific conditions are met.  A constraint can be used where an atom
could be used, except it cannot be followed by a quantifier.
The simple constraints are shown in
[posix-constraints-table](#posix-constraints-table);
some more constraints are described later.

| Atom | Description |
| --- | --- |
| `(``re``)` | (where `re` is any regular expression)        matches a match for        `re`, with the match noted for possible reporting |
| `(?:``re``)` | as above, but the match is not noted for reporting        (a "non-capturing" set of parentheses)        (AREs only) |
| `.` | matches any single character |
| `[``chars``]` | a *bracket expression*,        matching any one of the `chars` (see        [posix-bracket-expressions](#posix-bracket-expressions) for more detail) |
| `\``k` | (where `k` is a non-alphanumeric character)        matches that character taken as an ordinary character,        e.g., `\\` matches a backslash character |
| `\``c` | where `c` is alphanumeric        (possibly followed by other characters)        is an *escape*, see [posix-escape-sequences](#posix-escape-sequences)        (AREs only; in EREs and BREs, this matches `c`) |
| `{` | when followed by a character other than a digit,        matches the left-brace character `{`;        when followed by a digit, it is the beginning of a        `bound` (see below) |
| `x` | where `x` is a single character with no other        significance, matches that character |

An RE cannot end with a backslash (`\`).

> **Note:**

> If you have [guc-standard-conforming-strings](#guc-standard-conforming-strings) turned off,
> any backslashes you write in literal string constants will need to be
> doubled.  See [sql-syntax-strings](#sql-syntax-strings) for more information.
>

| Quantifier | Matches |
| --- | --- |
| `*` | a sequence of 0 or more matches of the atom |
| `+` | a sequence of 1 or more matches of the atom |
| `?` | a sequence of 0 or 1 matches of the atom |
| `{``m``}` | a sequence of exactly `m` matches of the atom |
| `{``m``,}` | a sequence of `m` or more matches of the atom |
| `{``m``,``n``}` | a sequence of `m` through `n`        (inclusive) matches of the atom; `m` cannot exceed        `n` |
| `*?` | non-greedy version of `*` |
| `+?` | non-greedy version of `+` |
| `??` | non-greedy version of `?` |
| `{``m``}?` | non-greedy version of `{``m``}` |
| `{``m``,}?` | non-greedy version of `{``m``,}` |
| `{``m``,``n``}?` | non-greedy version of `{``m``,``n``}` |

The forms using `{``...``}`
are known as *bounds*.
The numbers `m` and `n` within a bound are
unsigned decimal integers with permissible values from 0 to 255 inclusive.

*Non-greedy* quantifiers (available in AREs only) match the
same possibilities as their corresponding normal (*greedy*)
counterparts, but prefer the smallest number rather than the largest
number of matches.
See [posix-matching-rules](#posix-matching-rules) for more detail.

> **Note:**

> A quantifier cannot immediately follow another quantifier, e.g.,
> `**` is invalid.
> A quantifier cannot
> begin an expression or subexpression or follow
> `^` or `|`.
>

| Constraint | Description |
| --- | --- |
| `^` | matches at the beginning of the string |
| `$` | matches at the end of the string |
| `(?=``re``)` | *positive lookahead* matches at any point        where a substring matching `re` begins        (AREs only) |
| `(?!``re``)` | *negative lookahead* matches at any point        where no substring matching `re` begins        (AREs only) |
| `(? **Note:**

> PostgreSQL currently does not support multi-character collating
> elements. This information describes possible future behavior.
>

Within a bracket expression, a collating element enclosed in
`[=` and `=]` is an *equivalence
class*, standing for the sequences of characters of all collating
elements equivalent to that one, including itself.  (If there are
no other equivalent collating elements, the treatment is as if the
enclosing delimiters were `[.` and
`.]`.)  For example, if `o` and
`^` are the members of an equivalence class, then
`[[=o=]]`, `[[=^=]]`, and
`[o^]` are all synonymous.  An equivalence class
cannot be an endpoint of a range.

Within a bracket expression, the name of a character class
enclosed in `[:` and `:]` stands
for the list of all characters belonging to that class.  A character
class cannot be used as an endpoint of a range.
The POSIX standard defines these character class
names:
`alnum` (letters and numeric digits),
`alpha` (letters),
`blank` (space and tab),
`cntrl` (control characters),
`digit` (numeric digits),
`graph` (printable characters except space),
`lower` (lower-case letters),
`print` (printable characters including space),
`punct` (punctuation),
`space` (any white space),
`upper` (upper-case letters),
and `xdigit` (hexadecimal digits).
The behavior of these standard character classes is generally
consistent across platforms for characters in the 7-bit ASCII set.
Whether a given non-ASCII character is considered to belong to one
of these classes depends on the *collation*
that is used for the regular-expression function or operator
(see [collation](#collation)), or by default on the
database's `LC_CTYPE` locale setting (see
[locale](#locale)).  The classification of non-ASCII
characters can vary across platforms even in similarly-named
locales.  (But the `C` locale never considers any
non-ASCII characters to belong to any of these classes.)
In addition to these standard character
classes, PostgreSQL defines
the `word` character class, which is the same as
`alnum` plus the underscore (`_`)
character, and
the `ascii` character class, which contains exactly
the 7-bit ASCII set.

There are two special cases of bracket expressions:  the bracket
expressions `[[:<:]]` and
`[[:>:]]` are constraints,
matching empty strings at the beginning
and end of a word respectively.  A word is defined as a sequence
of word characters that is neither preceded nor followed by word
characters.  A word character is any character belonging to the
`word` character class, that is, any letter, digit,
or underscore.  This is an extension, compatible with but not
specified by POSIX 1003.2, and should be used with
caution in software intended to be portable to other systems.
The constraint escapes described below are usually preferable; they
are no more standard, but are easier to type.

#### Regular Expression Escapes

*Escapes* are special sequences beginning with `\`
followed by an alphanumeric character. Escapes come in several varieties:
character entry, class shorthands, constraint escapes, and back references.
A `\` followed by an alphanumeric character but not constituting
a valid escape is illegal in AREs.
In EREs, there are no escapes: outside a bracket expression,
a `\` followed by an alphanumeric character merely stands for
that character as an ordinary character, and inside a bracket expression,
`\` is an ordinary character.
(The latter is the one actual incompatibility between EREs and AREs.)

*Character-entry escapes* exist to make it easier to specify
non-printing and other inconvenient characters in REs.  They are
shown in [posix-character-entry-escapes-table](#posix-character-entry-escapes-table).

*Class-shorthand escapes* provide shorthands for certain
commonly-used character classes.  They are
shown in [posix-class-shorthand-escapes-table](#posix-class-shorthand-escapes-table).

A *constraint escape* is a constraint,
matching the empty string if specific conditions are met,
written as an escape.  They are
shown in [posix-constraint-escapes-table](#posix-constraint-escapes-table).

A *back reference* (`\``n`) matches the
same string matched by the previous parenthesized subexpression specified
by the number `n`
(see [posix-constraint-backref-table](#posix-constraint-backref-table)).  For example,
`([bc])\1` matches `bb` or `cc`
but not `bc` or `cb`.
The subexpression must entirely precede the back reference in the RE.
Subexpressions are numbered in the order of their leading parentheses.
Non-capturing parentheses do not define subexpressions.
The back reference considers only the string characters matched by the
referenced subexpression, not any constraints contained in it.  For
example, `(^\d)\1` will match `22`.

| Escape | Description |
| --- | --- |
| `\a` | alert (bell) character, as in C |
| `\b` | backspace, as in C |
| `\B` | synonym for backslash (`\`) to help reduce the need for backslash        doubling |
| `\c``X` | (where `X` is any character) the character whose        low-order 5 bits are the same as those of        `X`, and whose other bits are all zero |
| `\e` | the character whose collating-sequence name        is `ESC`,        or failing that, the character with octal value `033` |
| `\f` | form feed, as in C |
| `\n` | newline, as in C |
| `\r` | carriage return, as in C |
| `\t` | horizontal tab, as in C |
| `\u``wxyz` | (where `wxyz` is exactly four hexadecimal digits)        the character whose hexadecimal value is        `0x``wxyz` |
| `\U``stuvwxyz` | (where `stuvwxyz` is exactly eight hexadecimal        digits)        the character whose hexadecimal value is        `0x``stuvwxyz` |
| `\v` | vertical tab, as in C |
| `\x``hhh` | (where `hhh` is any sequence of hexadecimal        digits)        the character whose hexadecimal value is        `0x``hhh`        (a single character no matter how many hexadecimal digits are used) |
| `\0` | the character whose value is `0` (the null byte) |
| `\``xy` | (where `xy` is exactly two octal digits,        and is not a *back reference*)        the character whose octal value is        `0``xy` |
| `\``xyz` | (where `xyz` is exactly three octal digits,        and is not a *back reference*)        the character whose octal value is        `0``xyz` |

Hexadecimal digits are `0`-`9`,
`a`-`f`, and `A`-`F`.
Octal digits are `0`-`7`.

Numeric character-entry escapes specifying values outside the ASCII range
(0–127) have meanings dependent on the database encoding.  When the
encoding is UTF-8, escape values are equivalent to Unicode code points,
for example `\u1234` means the character `U+1234`.
For other multibyte encodings, character-entry escapes usually just
specify the concatenation of the byte values for the character.  If the
escape value does not correspond to any legal character in the database
encoding, no error will be raised, but it will never match any data.

The character-entry escapes are always taken as ordinary characters.
For example, `\135` is `]` in ASCII, but
`\135` does not terminate a bracket expression.

| Escape | Description |
| --- | --- |
| `\d` | matches any digit, like         `[[:digit:]]` |
| `\s` | matches any whitespace character, like         `[[:space:]]` |
| `\w` | matches any word character, like         `[[:word:]]` |
| `\D` | matches any non-digit, like         `[^[:digit:]]` |
| `\S` | matches any non-whitespace character, like         `[^[:space:]]` |
| `\W` | matches any non-word character, like         `[^[:word:]]` |

The class-shorthand escapes also work within bracket expressions,
although the definitions shown above are not quite syntactically
valid in that context.
For example, `[a-c\d]` is equivalent to
`[a-c[:digit:]]`.

| Escape | Description |
| --- | --- |
| `\A` | matches only at the beginning of the string        (see [posix-matching-rules](#posix-matching-rules) for how this differs from        `^`) |
| `\m` | matches only at the beginning of a word |
| `\M` | matches only at the end of a word |
| `\y` | matches only at the beginning or end of a word |
| `\Y` | matches only at a point that is not the beginning or end of a        word |
| `\Z` | matches only at the end of the string        (see [posix-matching-rules](#posix-matching-rules) for how this differs from        `$`) |

A word is defined as in the specification of
`[[:<:]]` and `[[:>:]]` above.
Constraint escapes are illegal within bracket expressions.

| Escape | Description |
| --- | --- |
| `\``m` | (where `m` is a nonzero digit)        a back reference to the `m`'th subexpression |
| `\``mnn` | (where `m` is a nonzero digit, and        `nn` is some more digits, and the decimal value        `mnn` is not greater than the number of closing capturing        parentheses seen so far)        a back reference to the `mnn`'th subexpression |

> **Note:**

> There is an inherent ambiguity between octal character-entry
> escapes and back references, which is resolved by the following heuristics,
> as hinted at above.
> A leading zero always indicates an octal escape.
> A single non-zero digit, not followed by another digit,
> is always taken as a back reference.
> A multi-digit sequence not starting with a zero is taken as a back
> reference if it comes after a suitable subexpression
> (i.e., the number is in the legal range for a back reference),
> and otherwise is taken as octal.
>

#### Regular Expression Metasyntax

In addition to the main syntax described above, there are some special
forms and miscellaneous syntactic facilities available.

An RE can begin with one of two special *director* prefixes.
If an RE begins with `***:`,
the rest of the RE is taken as an ARE.  (This normally has no effect in
PostgreSQL, since REs are assumed to be AREs;
but it does have an effect if ERE or BRE mode had been specified by
the `flags` parameter to a regex function.)
If an RE begins with `***=`,
the rest of the RE is taken to be a literal string,
with all characters considered ordinary characters.

An ARE can begin with *embedded options*:
a sequence `(?``xyz``)`
(where `xyz` is one or more alphabetic characters)
specifies options affecting the rest of the RE.
These options override any previously determined options —
in particular, they can override the case-sensitivity behavior implied by
a regex operator, or the `flags` parameter to a regex
function.
The available option letters are
shown in [posix-embedded-options-table](#posix-embedded-options-table).
Note that these same option letters are used in the `flags`
parameters of regex functions.

| Option | Description |
| --- | --- |
| `b` | rest of RE is a BRE |
| `c` | case-sensitive matching (overrides operator type) |
| `e` | rest of RE is an ERE |
| `i` | case-insensitive matching (see        [posix-matching-rules](#posix-matching-rules)) (overrides operator type) |
| `m` | historical synonym for `n` |
| `n` | newline-sensitive matching (see        [posix-matching-rules](#posix-matching-rules)) |
| `p` | partial newline-sensitive matching (see        [posix-matching-rules](#posix-matching-rules)) |
| `q` | rest of RE is a literal ("quoted") string, all ordinary        characters |
| `s` | non-newline-sensitive matching (default) |
| `t` | tight syntax (default; see below) |
| `w` | inverse partial newline-sensitive ("weird") matching        (see [posix-matching-rules](#posix-matching-rules)) |
| `x` | expanded syntax (see below) |

Embedded options take effect at the `)` terminating the sequence.
They can appear only at the start of an ARE (after the
`***:` director if any).

In addition to the usual (*tight*) RE syntax, in which all
characters are significant, there is an *expanded* syntax,
available by specifying the embedded `x` option.
In the expanded syntax,
white-space characters in the RE are ignored, as are
all characters between a `#`
and the following newline (or the end of the RE).  This
permits paragraphing and commenting a complex RE.
There are three exceptions to that basic rule:

- a white-space character or `#` preceded by `\` is
retained
- white space or `#` within a bracket expression is retained
- white space and comments cannot appear within multi-character symbols,
such as `(?:`

For this purpose, white-space characters are blank, tab, newline, and
any character that belongs to the `space` character class.

Finally, in an ARE, outside bracket expressions, the sequence
`(?#``ttt``)`
(where `ttt` is any text not containing a `)`)
is a comment, completely ignored.
Again, this is not allowed between the characters of
multi-character symbols, like `(?:`.
Such comments are more a historical artifact than a useful facility,
and their use is deprecated; use the expanded syntax instead.

*None* of these metasyntax extensions is available if
an initial `***=` director
has specified that the user's input be treated as a literal string
rather than as an RE.

#### Regular Expression Matching Rules

In the event that an RE could match more than one substring of a given
string, the RE matches the one starting earliest in the string.
If the RE could match more than one substring starting at that point,
either the longest possible match or the shortest possible match will
be taken, depending on whether the RE is *greedy* or
*non-greedy*.

Whether an RE is greedy or not is determined by the following rules:

- Most atoms, and all constraints, have no greediness attribute (because
they cannot match variable amounts of text anyway).
- Adding parentheses around an RE does not change its greediness.
- A quantified atom with a fixed-repetition quantifier
(`{``m``}`
or
`{``m``}?`)
has the same greediness (possibly none) as the atom itself.
- A quantified atom with other normal quantifiers (including
`{``m``,``n``}`
with `m` equal to `n`)
is greedy (prefers longest match).
- A quantified atom with a non-greedy quantifier (including
`{``m``,``n``}?`
with `m` equal to `n`)
is non-greedy (prefers shortest match).
- A branch — that is, an RE that has no top-level
`|` operator — has the same greediness as the first
quantified atom in it that has a greediness attribute.
- An RE consisting of two or more branches connected by the
`|` operator is always greedy.

The above rules associate greediness attributes not only with individual
quantified atoms, but with branches and entire REs that contain quantified
atoms.  What that means is that the matching is done in such a way that
the branch, or whole RE, matches the longest or shortest possible
substring *as a whole*.  Once the length of the entire match
is determined, the part of it that matches any particular subexpression
is determined on the basis of the greediness attribute of that
subexpression, with subexpressions starting earlier in the RE taking
priority over ones starting later.

An example of what this means:

```
SELECT SUBSTRING('XY1234Z', 'Y*([0-9]{1,3})');
Result: 123
SELECT SUBSTRING('XY1234Z', 'Y*?([0-9]{1,3})');
Result: 1
```

In the first case, the RE as a whole is greedy because `Y*`
is greedy.  It can match beginning at the `Y`, and it matches
the longest possible string starting there, i.e., `Y123`.
The output is the parenthesized part of that, or `123`.
In the second case, the RE as a whole is non-greedy because `Y*?`
is non-greedy.  It can match beginning at the `Y`, and it matches
the shortest possible string starting there, i.e., `Y1`.
The subexpression `[0-9]{1,3}` is greedy but it cannot change
the decision as to the overall match length; so it is forced to match
just `1`.

In short, when an RE contains both greedy and non-greedy subexpressions,
the total match length is either as long as possible or as short as
possible, according to the attribute assigned to the whole RE.  The
attributes assigned to the subexpressions only affect how much of that
match they are allowed to "eat" relative to each other.

The quantifiers `{1,1}` and `{1,1}?`
can be used to force greediness or non-greediness, respectively,
on a subexpression or a whole RE.
This is useful when you need the whole RE to have a greediness attribute
different from what's deduced from its elements.  As an example,
suppose that we are trying to separate a string containing some digits
into the digits and the parts before and after them.  We might try to
do that like this:

```
SELECT regexp_match('abc01234xyz', '(.*)(\d+)(.*)');
Result: {abc0123,4,xyz}
```

That didn't work: the first `.*` is greedy so
it "eats" as much as it can, leaving the `\d+` to
match at the last possible place, the last digit.  We might try to fix
that by making it non-greedy:

```
SELECT regexp_match('abc01234xyz', '(.*?)(\d+)(.*)');
Result: {abc,0,""}
```

That didn't work either, because now the RE as a whole is non-greedy
and so it ends the overall match as soon as possible.  We can get what
we want by forcing the RE as a whole to be greedy:

```
SELECT regexp_match('abc01234xyz', '(?:(.*?)(\d+)(.*)){1,1}');
Result: {abc,01234,xyz}
```

Controlling the RE's overall greediness separately from its components'
greediness allows great flexibility in handling variable-length patterns.

When deciding what is a longer or shorter match,
match lengths are measured in characters, not collating elements.
An empty string is considered longer than no match at all.
For example:
`bb*`
matches the three middle characters of `abbbc`;
`(week|wee)(night|knights)`
matches all ten characters of `weeknights`;
when `(.*).*`
is matched against `abc` the parenthesized subexpression
matches all three characters; and when
`(a*)*` is matched against `bc`
both the whole RE and the parenthesized
subexpression match an empty string.

If case-independent matching is specified,
the effect is much as if all case distinctions had vanished from the
alphabet.
When an alphabetic that exists in multiple cases appears as an
ordinary character outside a bracket expression, it is effectively
transformed into a bracket expression containing both cases,
e.g., `x` becomes `[xX]`.
When it appears inside a bracket expression, all case counterparts
of it are added to the bracket expression, e.g.,
`[x]` becomes `[xX]`
and `[^x]` becomes `[^xX]`.

If newline-sensitive matching is specified, `.`
and bracket expressions using `^`
will never match the newline character
(so that matches will not cross lines unless the RE
explicitly includes a newline)
and `^` and `$`
will match the empty string after and before a newline
respectively, in addition to matching at beginning and end of string
respectively.
But the ARE escapes `\A` and `\Z`
continue to match beginning or end of string *only*.
Also, the character class shorthands `\D`
and `\W` will match a newline regardless of this mode.
(Before PostgreSQL 14, they did not match
newlines when in newline-sensitive mode.
Write `[^[:digit:]]`
or `[^[:word:]]` to get the old behavior.)

If partial newline-sensitive matching is specified,
this affects `.` and bracket expressions
as with newline-sensitive matching, but not `^`
and `$`.

If inverse partial newline-sensitive matching is specified,
this affects `^` and `$`
as with newline-sensitive matching, but not `.`
and bracket expressions.
This isn't very useful but is provided for symmetry.

#### Limits and Compatibility

No particular limit is imposed on the length of REs in this
implementation.  However,
programs intended to be highly portable should not employ REs longer
than 256 bytes,
as a POSIX-compliant implementation can refuse to accept such REs.

The only feature of AREs that is actually incompatible with
POSIX EREs is that `\` does not lose its special
significance inside bracket expressions.
All other ARE features use syntax which is illegal or has
undefined or unspecified effects in POSIX EREs;
the `***` syntax of directors likewise is outside the POSIX
syntax for both BREs and EREs.

Many of the ARE extensions are borrowed from Perl, but some have
been changed to clean them up, and a few Perl extensions are not present.
Incompatibilities of note include `\b`, `\B`,
the lack of special treatment for a trailing newline,
the addition of complemented bracket expressions to the things
affected by newline-sensitive matching,
the restrictions on parentheses and back references in lookahead/lookbehind
constraints, and the longest/shortest-match (rather than first-match)
matching semantics.

#### Basic Regular Expressions

BREs differ from EREs in several respects.
In BREs, `|`, `+`, and `?`
are ordinary characters and there is no equivalent
for their functionality.
The delimiters for bounds are
`\{` and `\}`,
with `{` and `}`
by themselves ordinary characters.
The parentheses for nested subexpressions are
`\(` and `\)`,
with `(` and `)` by themselves ordinary characters.
`^` is an ordinary character except at the beginning of the
RE or the beginning of a parenthesized subexpression,
`$` is an ordinary character except at the end of the
RE or the end of a parenthesized subexpression,
and `*` is an ordinary character if it appears at the beginning
of the RE or the beginning of a parenthesized subexpression
(after a possible leading `^`).
Finally, single-digit back references are available, and
`\<` and `\>`
are synonyms for
`[[:<:]]` and `[[:>:]]`
respectively; no other escapes are available in BREs.

#### Differences from SQL Standard and XQuery

Since SQL:2008, the SQL standard includes regular expression operators
and functions that performs pattern
matching according to the XQuery regular expression
standard:

- `LIKE_REGEX`
- `OCCURRENCES_REGEX`
- `POSITION_REGEX`
- `SUBSTRING_REGEX`
- `TRANSLATE_REGEX`

PostgreSQL does not currently implement these
operators and functions.  You can get approximately equivalent
functionality in each case as shown in [functions-regexp-sql-table](#functions-regexp-sql-table).  (Various optional clauses on
both sides have been omitted in this table.)

| SQL standard | PostgreSQL |
| --- | --- |
| ``string` LIKE_REGEX `pattern`` | `regexp_like(`string`, `pattern`)` or ``string` ~ `pattern`` |
| `OCCURRENCES_REGEX(`pattern` IN `string`)` | `regexp_count(`string`, `pattern`)` |
| `POSITION_REGEX(`pattern` IN `string`)` | `regexp_instr(`string`, `pattern`)` |
| `SUBSTRING_REGEX(`pattern` IN `string`)` | `regexp_substr(`string`, `pattern`)` |
| `TRANSLATE_REGEX(`pattern` IN `string` WITH `replacement`)` | `regexp_replace(`string`, `pattern`, `replacement`)` |

Regular expression functions similar to those provided by PostgreSQL are
also available in a number of other SQL implementations, whereas the
SQL-standard functions are not as widely implemented.  Some of the
details of the regular expression syntax will likely differ in each
implementation.

The SQL-standard operators and functions use XQuery regular expressions,
which are quite close to the ARE syntax described above.
Notable differences between the existing POSIX-based
regular-expression feature and XQuery regular expressions include:

- XQuery character class subtraction is not supported.  An example of
this feature is using the following to match only English
consonants: `[a-z-[aeiou]]`.
- XQuery character class shorthands `\c`,
`\C`, `\i`,
and `\I` are not supported.
- XQuery character class elements
using `\p{UnicodeProperty}` or the
inverse `\P{UnicodeProperty}` are not supported.
- POSIX interprets character classes such as `\w`
(see [posix-class-shorthand-escapes-table](#posix-class-shorthand-escapes-table))
according to the prevailing locale (which you can control by
attaching a `COLLATE` clause to the operator or
function).  XQuery specifies these classes by reference to Unicode
character properties, so equivalent behavior is obtained only with
a locale that follows the Unicode rules.
- The SQL standard (not XQuery itself) attempts to cater for more
variants of "newline" than POSIX does.  The
newline-sensitive matching options described above consider only
ASCII NL (`\n`) to be a newline, but SQL would have
us treat CR (`\r`), CRLF (`\r\n`)
(a Windows-style newline), and some Unicode-only characters like
LINE SEPARATOR (U+2028) as newlines as well.
Notably, `.` and `\s` should
count `\r\n` as one character not two according to
SQL.
- Of the character-entry escapes described in
[posix-character-entry-escapes-table](#posix-character-entry-escapes-table),
XQuery supports only `\n`, `\r`,
and `\t`.
- XQuery does not support
the `[:`name`:]` syntax
for character classes within bracket expressions.
- XQuery does not have lookahead or lookbehind constraints,
nor any of the constraint escapes described in
[posix-constraint-escapes-table](#posix-constraint-escapes-table).
- The metasyntax forms described in [posix-metasyntax](#posix-metasyntax)
do not exist in XQuery.
- The regular expression flag letters defined by XQuery are
related to but not the same as the option letters for POSIX
([posix-embedded-options-table](#posix-embedded-options-table)).  While the
`i` and `q` options behave the
same, others do not:

XQuery's `s` (allow dot to match newline)
and `m` (allow `^`
and `$` to match at newlines) flags provide
access to the same behaviors as
POSIX's `n`, `p`
and `w` flags, but they
do *not* match the behavior of
POSIX's `s` and `m` flags.
Note in particular that dot-matches-newline is the default
behavior in POSIX but not XQuery.
- XQuery's `x` (ignore whitespace in pattern) flag
is noticeably different from POSIX's expanded-mode flag.
POSIX's `x` flag also
allows `#` to begin a comment in the pattern,
and POSIX will not ignore a whitespace character after a
backslash.

## Enum Support Functions

For enum types (described in [datatype-enum](#datatype-enum)),
there are several functions that allow cleaner programming without
hard-coding particular values of an enum type.
These are listed in [functions-enum-table](#functions-enum-table). The examples
assume an enum type created as:

```
CREATE TYPE rainbow AS ENUM ('red', 'orange', 'yellow', 'green', 'blue', 'purple');
```

| Function                         Description                         Example(s) |
| --- |
| `enum_first` ( `anyenum` )         anyenum                         Returns the first value of the input enum type.                         `enum_first(null::rainbow)`         red |
| `enum_last` ( `anyenum` )         anyenum                         Returns the last value of the input enum type.                         `enum_last(null::rainbow)`         purple |
| `enum_range` ( `anyenum` )         anyarray                         Returns all values of the input enum type in an ordered array.                         `enum_range(null::rainbow)`         {red,orange,yellow,green,blue,purple} |
| `enum_range` ( `anyenum`, `anyenum` )         anyarray                         Returns the range between the two given enum values, as an ordered         array. The values must be from the same enum type. If the first         parameter is null, the result will start with the first value of         the enum type.         If the second parameter is null, the result will end with the last         value of the enum type.                         `enum_range('orange'::rainbow, 'green'::rainbow)`         {orange,yellow,green}                         `enum_range(NULL, 'green'::rainbow)`         {red,orange,yellow,green}                         `enum_range('orange'::rainbow, NULL)`         {orange,yellow,green,blue,purple} |

Notice that except for the two-argument form of `enum_range`,
these functions disregard the specific value passed to them; they care
only about its declared data type.  Either null or a specific value of
the type can be passed, with the same result.  It is more common to
apply these functions to a table column or function argument than to
a hardwired type name as used in the examples.

## Geometric Functions and Operators

The geometric types `point`, `box`,
`lseg`, `line`, `path`,
`polygon`, and `circle` have a large set of
native support functions and operators, shown in [functions-geometry-op-table](#functions-geometry-op-table), [functions-geometry-func-table](#functions-geometry-func-table), and [functions-geometry-conv-table](#functions-geometry-conv-table).

| Operator                         Description                         Example(s) |
| --- |
| `geometric_type` `+` `point`         `geometric_type`                         Adds the coordinates of the second `point` to those of each         point of the first argument, thus performing translation.         Available for `point`, `box`, `path`,         `circle`.                         `box '(1,1),(0,0)' + point '(2,0)'`         (3,1),(2,0) |
| `path` `+` `path`         path                         Concatenates two open paths (returns NULL if either path is closed).                         `path '[(0,0),(1,1)]' + path '[(2,2),(3,3),(4,4)]'`         [(0,0),(1,1),(2,2),(3,3),(4,4)] |
| `geometric_type` `-` `point`         `geometric_type`                         Subtracts the coordinates of the second `point` from those         of each point of the first argument, thus performing translation.         Available for `point`, `box`, `path`,         `circle`.                         `box '(1,1),(0,0)' - point '(2,0)'`         (-1,1),(-2,0) |
| `geometric_type` `*` `point`         `geometric_type`                         Multiplies each point of the first argument by the second         `point` (treating a point as being a complex number         represented by real and imaginary parts, and performing standard         complex multiplication).  If one interprets         the second `point` as a vector, this is equivalent to         scaling the object's size and distance from the origin by the length         of the vector, and rotating it counterclockwise around the origin by         the vector's angle from the `x` axis.         Available for `point`, `box`, (Note: "Rotating" a         box with these operators only moves its corner points: the box is         still considered to have sides parallel to the axes.  Hence the box's         size is not preserved, as a true rotation would do.)         `path`, `circle`.                         `path '((0,0),(1,0),(1,1))' * point '(3.0,0)'`         ((0,0),(3,0),(3,3))                         `path '((0,0),(1,0),(1,1))' * point(cosd(45), sind(45))`         ((0,0),(0.7071067811865475,0.7071067811865475),(0,1.414213562373095)) |
| `geometric_type` `/` `point`         `geometric_type`                         Divides each point of the first argument by the second         `point` (treating a point as being a complex number         represented by real and imaginary parts, and performing standard         complex division).  If one interprets         the second `point` as a vector, this is equivalent to         scaling the object's size and distance from the origin down by the         length of the vector, and rotating it clockwise around the origin by         the vector's angle from the `x` axis.         Available for `point`, `box`, `path`,         `circle`.                         `path '((0,0),(1,0),(1,1))' / point '(2.0,0)'`         ((0,0),(0.5,0),(0.5,0.5))                         `path '((0,0),(1,0),(1,1))' / point(cosd(45), sind(45))`         ((0,0),(0.7071067811865476,-0.7071067811865476),(1.4142135623730951,0)) |
| `@-@` `geometric_type`         double precision                         Computes the total length.         Available for `lseg`, `path`.                         `@-@ path '[(0,0),(1,0),(1,1)]'`         2 |
| `@@` `geometric_type`         point                         Computes the center point.         Available for `box`, `lseg`,         `polygon`, `circle`.                         `@@ box '(2,2),(0,0)'`         (1,1) |
| `#` `geometric_type`         integer                         Returns the number of points.         Available for `path`, `polygon`.                         `# path '((1,0),(0,1),(-1,0))'`         3 |
| `geometric_type` `#` `geometric_type`         point                         Computes the point of intersection, or NULL if there is none.         Available for `lseg`, `line`.                         `lseg '[(0,0),(1,1)]' # lseg '[(1,0),(0,1)]'`         (0.5,0.5) |
| `box` `#` `box`         box                         Computes the intersection of two boxes, or NULL if there is none.                         `box '(2,2),(-1,-1)' # box '(1,1),(-2,-2)'`         (1,1),(-1,-1) |
| `geometric_type` `##` `geometric_type`         point                         Computes the closest point to the first object on the second object.         Available for these pairs of types:         (`point`, `box`),         (`point`, `lseg`),         (`point`, `line`),         (`lseg`, `box`),         (`lseg`, `lseg`),         (`line`, `lseg`).                         `point '(0,0)' ## lseg '[(2,0),(0,2)]'`         (1,1) |
| `geometric_type` `` `geometric_type`         double precision                         Computes the distance between the objects.         Available for all seven geometric types, for all combinations         of `point` with another geometric type, and for         these additional pairs of types:         (`box`, `lseg`),         (`lseg`, `line`),         (`polygon`, `circle`)         (and the commutator cases).                         `circle ''  circle ''`         3 |
| `geometric_type` `@>` `geometric_type`         boolean                         Does first object contain second?         Available for these pairs of types:         (`box`, `point`),         (`box`, `box`),         (`path`, `point`),         (`polygon`, `point`),         (`polygon`, `polygon`),         (`circle`, `point`),         (`circle`, `circle`).                         `circle '' @> point '(1,1)'`         t |
| `geometric_type` `'`         t |
| `geometric_type` `&&` `geometric_type`         boolean                         Do these objects overlap?  (One point in common makes this true.)         Available for `box`, `polygon`,         `circle`.                         `box '(1,1),(0,0)' && box '(2,2),(0,0)'`         t |
| `geometric_type` `' '`         t |
| `geometric_type` `>>` `geometric_type`         boolean                         Is first object strictly right of second?         Available for `point`, `box`,         `polygon`, `circle`.                         `circle '' >> circle ''`         t |
| `geometric_type` `&` `geometric_type`         boolean                         Does first object not extend to the left of second?         Available for `box`, `polygon`,         `circle`.                         `box '(3,3),(0,0)' &> box '(2,2),(0,0)'`         t |
| `geometric_type` `>` `geometric_type`         boolean                         Is first object strictly above second?         Available for `point`, `box`, `polygon`,         `circle`.                         `box '(5,5),(3,4)' |>> box '(3,3),(0,0)'`         t |
| `geometric_type` `&` `geometric_type`         boolean                         Does first object not extend below second?         Available for `box`, `polygon`,         `circle`.                         `box '(3,3),(0,0)' |&> box '(2,2),(0,0)'`         t |
| `box` `^` `box`         boolean                         Is first object above second (allows edges to touch)?                         `box '((2,2),(1,1))' >^ box '((1,1),(0,0))'`         t |
| `geometric_type` `?#` `geometric_type`         boolean                         Do these objects intersect?         Available for these pairs of types:         (`box`, `box`),         (`lseg`, `box`),         (`lseg`, `lseg`),         (`lseg`, `line`),         (`line`, `box`),         (`line`, `line`),         (`path`, `path`).                         `lseg '[(-1,0),(1,0)]' ?# box '(2,2),(-2,-2)'`         t |
| `?-` `line`         boolean                         `?-` `lseg`         boolean                         Is line horizontal?                         `?- lseg '[(-1,0),(1,0)]'`         t |
| `point` `?-` `point`         boolean                         Are points horizontally aligned (that is, have same y coordinate)?                         `point '(1,0)' ?- point '(0,0)'`         t |
| `?|` `line`         boolean                         `?|` `lseg`         boolean                         Is line vertical?                         `?| lseg '[(-1,0),(1,0)]'`         f |
| `point` `?|` `point`         boolean                         Are points vertically aligned (that is, have same x coordinate)?                         `point '(0,1)' ?| point '(0,0)'`         t |
| `line` `?-|` `line`         boolean                         `lseg` `?-|` `lseg`         boolean                         Are lines perpendicular?                         `lseg '[(0,0),(0,1)]' ?-| lseg '[(0,0),(1,0)]'`         t |
| `line` `?||` `line`         boolean                         `lseg` `?||` `lseg`         boolean                         Are lines parallel?                         `lseg '[(-1,0),(1,0)]' ?|| lseg '[(-1,2),(1,2)]'`         t |
| `geometric_type` `~=` `geometric_type`         boolean                         Are these objects the same?         Available for `point`, `box`,         `polygon`, `circle`.                         `polygon '((0,0),(1,1))' ~= polygon '((1,1),(0,0))'`         t |

> **Caution:**

> Note that the "same as" operator, `~=`,
> represents the usual notion of equality for the `point`,
> `box`, `polygon`, and `circle` types.
> Some of the geometric types also have an `=` operator, but
> `=` compares for equal *areas* only.
> The other scalar comparison operators (`<=` and so
> on), where available for these types, likewise compare areas.
>

> **Note:**

> Before PostgreSQL 14, the point
> is strictly below/above comparison operators `point`
> `<<|` `point` and `point`
> `|>>` `point` were respectively
> called `<^` and `>^`.  These
> names are still available, but are deprecated and will eventually be
> removed.
>

| Function                         Description                         Example(s) |
| --- |
| `area` ( `geometric_type` )         double precision                         Computes area.         Available for `box`, `path`, `circle`.         A `path` input must be closed, else NULL is returned.         Also, if the `path` is self-intersecting, the result may be         meaningless.                         `area(box '(2,2),(0,0)')`         4 |
| `center` ( `geometric_type` )         point                         Computes center point.         Available for `box`, `circle`.                         `center(box '(1,2),(0,0)')`         (0.5,1) |
| `diagonal` ( `box` )         lseg                         Extracts box's diagonal as a line segment         (same as `lseg(box)`).                         `diagonal(box '(1,2),(0,0)')`         [(1,2),(0,0)] |
| `diameter` ( `circle` )         double precision                         Computes diameter of circle.                         `diameter(circle '')`         4 |
| `height` ( `box` )         double precision                         Computes vertical size of box.                         `height(box '(1,2),(0,0)')`         2 |
| `isclosed` ( `path` )         boolean                         Is path closed?                         `isclosed(path '((0,0),(1,1),(2,0))')`         t |
| `isopen` ( `path` )         boolean                         Is path open?                         `isopen(path '[(0,0),(1,1),(2,0)]')`         t |
| `length` ( `geometric_type` )         double precision                         Computes the total length.         Available for `lseg`, `path`.                         `length(path '((-1,0),(1,0))')`         4 |
| `npoints` ( `geometric_type` )         integer                         Returns the number of points.         Available for `path`, `polygon`.                         `npoints(path '[(0,0),(1,1),(2,0)]')`         3 |
| `pclose` ( `path` )         path                         Converts path to closed form.                         `pclose(path '[(0,0),(1,1),(2,0)]')`         ((0,0),(1,1),(2,0)) |
| `popen` ( `path` )         path                         Converts path to open form.                         `popen(path '((0,0),(1,1),(2,0))')`         [(0,0),(1,1),(2,0)] |
| `radius` ( `circle` )         double precision                         Computes radius of circle.                         `radius(circle '')`         2 |
| `slope` ( `point`, `point` )         double precision                         Computes slope of a line drawn through the two points.                         `slope(point '(0,0)', point '(2,1)')`         0.5 |
| `width` ( `box` )         double precision                         Computes horizontal size of box.                         `width(box '(1,2),(0,0)')`         1 |

| Function                         Description                         Example(s) |
| --- |
| `box` ( `circle` )         box                         Computes box inscribed within the circle.                         `box(circle '')`         (1.414213562373095,1.414213562373095),(-1.414213562373095,-1.414213562373095) |
| `box` ( `point` )         box                         Converts point to empty box.                         `box(point '(1,0)')`         (1,0),(1,0) |
| `box` ( `point`, `point` )         box                         Converts any two corner points to box.                         `box(point '(0,1)', point '(1,0)')`         (1,1),(0,0) |
| `box` ( `polygon` )         box                         Computes bounding box of polygon.                         `box(polygon '((0,0),(1,1),(2,0))')`         (2,1),(0,0) |
| `bound_box` ( `box`, `box` )         box                         Computes bounding box of two boxes.                         `bound_box(box '(1,1),(0,0)', box '(4,4),(3,3)')`         (4,4),(0,0) |
| `circle` ( `box` )         circle                         Computes smallest circle enclosing box.                         `circle(box '(1,1),(0,0)')`          |
| `circle` ( `point`, `double precision` )         circle                         Constructs circle from center and radius.                         `circle(point '(0,0)', 2.0)`          |
| `circle` ( `polygon` )         circle                         Converts polygon to circle.  The circle's center is the mean of the         positions of the polygon's points, and the radius is the average         distance of the polygon's points from that center.                         `circle(polygon '((0,0),(1,3),(2,0))')`          |
| `line` ( `point`, `point` )         line                         Converts two points to the line through them.                         `line(point '(-1,0)', point '(1,0)')`         {0,-1,0} |
| `lseg` ( `box` )         lseg                         Extracts box's diagonal as a line segment.                         `lseg(box '(1,0),(-1,0)')`         [(1,0),(-1,0)] |
| `lseg` ( `point`, `point` )         lseg                         Constructs line segment from two endpoints.                         `lseg(point '(-1,0)', point '(1,0)')`         [(-1,0),(1,0)] |
| `path` ( `polygon` )         path                         Converts polygon to a closed path with the same list of points.                         `path(polygon '((0,0),(1,1),(2,0))')`         ((0,0),(1,1),(2,0)) |
| `point` ( `double precision`, `double precision` )         point                         Constructs point from its coordinates.                         `point(23.4, -44.5)`         (23.4,-44.5) |
| `point` ( `box` )         point                         Computes center of box.                         `point(box '(1,0),(-1,0)')`         (0,0) |
| `point` ( `circle` )         point                         Computes center of circle.                         `point(circle '')`         (0,0) |
| `point` ( `lseg` )         point                         Computes center of line segment.                         `point(lseg '[(-1,0),(1,0)]')`         (0,0) |
| `point` ( `polygon` )         point                         Computes center of polygon (the mean of the         positions of the polygon's points).                         `point(polygon '((0,0),(1,1),(2,0))')`         (1,0.3333333333333333) |
| `polygon` ( `box` )         polygon                         Converts box to a 4-point polygon.                         `polygon(box '(1,1),(0,0)')`         ((0,0),(0,1),(1,1),(1,0)) |
| `polygon` ( `circle` )         polygon                         Converts circle to a 12-point polygon.                         `polygon(circle '')`         ((-2,0),(-1.7320508075688774,0.9999999999999999),(-1.0000000000000002,1.7320508075688772),(-1.2246063538223773e-16,2),(0.9999999999999996,1.7320508075688774),(1.732050807568877,1.0000000000000007),(2,2.4492127076447545e-16),(1.7320508075688776,-0.9999999999999994),(1.0000000000000009,-1.7320508075688767),(3.673819061467132e-16,-2),(-0.9999999999999987,-1.732050807568878),(-1.7320508075688767,-1.0000000000000009)) |
| `polygon` ( `integer`, `circle` )         polygon                         Converts circle to an `n`-point polygon.                         `polygon(4, circle '')`         ((2,0),(3,1),(4,1.2246063538223773e-16),(3,-1)) |
| `polygon` ( `path` )         polygon                         Converts closed path to a polygon with the same list of points.                         `polygon(path '((0,0),(1,1),(2,0))')`         ((0,0),(1,1),(2,0)) |

It is possible to access the two component numbers of a `point`
as though the point were an array with indexes 0 and 1.  For example, if
`t.p` is a `point` column then
`SELECT p[0] FROM t` retrieves the X coordinate and
`UPDATE t SET p[1] = ...` changes the Y coordinate.
In the same way, a value of type `box` or `lseg` can be treated
as an array of two `point` values.

## Network Address Functions and Operators

The IP network address types, `cidr` and `inet`,
support the usual comparison operators shown in
[functions-comparison-op-table](#functions-comparison-op-table)
as well as the specialized operators and functions shown in
[cidr-inet-operators-table](#cidr-inet-operators-table) and
[cidr-inet-functions-table](#cidr-inet-functions-table).

Any `cidr` value can be cast to `inet` implicitly;
therefore, the operators and functions shown below as operating on
`inet` also work on `cidr` values.  (Where there are
separate functions for `inet` and `cidr`, it is
because the behavior should be different for the two cases.)
Also, it is permitted to cast an `inet` value
to `cidr`.  When this is done, any bits to the right of the
netmask are silently zeroed to create a valid `cidr` value.

| Operator                         Description                         Example(s) |
| --- |
| `inet` `>` `inet`         boolean                         Does subnet strictly contain subnet?                         `inet '192.168.1/24' >> inet '192.168.1.5'`         t |
| `inet` `>>=` `inet`         boolean                         Does subnet contain or equal subnet?                         `inet '192.168.1/24' >>= inet '192.168.1/24'`         t |
| `inet` `&&` `inet`         boolean                         Does either subnet contain or equal the other?                         `inet '192.168.1/24' && inet '192.168.1.80/28'`         t                         `inet '192.168.1/24' && inet '192.168.2.0/28'`         f |
| `~` `inet`         inet                         Computes bitwise NOT.                         `~ inet '192.168.1.6'`         63.87.254.249 |
| `inet` `&` `inet`         inet                         Computes bitwise AND.                         `inet '192.168.1.6' & inet '0.0.0.255'`         0.0.0.6 |
| `inet` `|` `inet`         inet                         Computes bitwise OR.                         `inet '192.168.1.6' | inet '0.0.0.255'`         192.168.1.255 |
| `inet` `+` `bigint`         inet                         Adds an offset to an address.                         `inet '192.168.1.6' + 25`         192.168.1.31 |
| `bigint` `+` `inet`         inet                         Adds an offset to an address.                         `200 + inet '::ffff:fff0:1'`         ::ffff:255.240.0.201 |
| `inet` `-` `bigint`         inet                         Subtracts an offset from an address.                         `inet '192.168.1.43' - 36`         192.168.1.7 |
| `inet` `-` `inet`         bigint                         Computes the difference of two addresses.                         `inet '192.168.1.43' - inet '192.168.1.19'`         24                         `inet '::1' - inet '::ffff:1'`         -4294901760 |

| Function                         Description                         Example(s) |
| --- |
| `abbrev` ( `inet` )         text                         Creates an abbreviated display format as text.         (The result is the same as the `inet` output function         produces; it is "abbreviated" only in comparison to the         result of an explicit cast to `text`, which for historical         reasons will never suppress the netmask part.)                         `abbrev(inet '10.1.0.0/32')`         10.1.0.0 |
| `abbrev` ( `cidr` )         text                         Creates an abbreviated display format as text.         (The abbreviation consists of dropping all-zero octets to the right         of the netmask; more examples are in         [datatype-net-cidr-table](#datatype-net-cidr-table).)                         `abbrev(cidr '10.1.0.0/16')`         10.1/16 |
| `broadcast` ( `inet` )         inet                         Computes the broadcast address for the address's network.                         `broadcast(inet '192.168.1.5/24')`         192.168.1.255/24 |
| `family` ( `inet` )         integer                         Returns the address's family: `4` for IPv4,         `6` for IPv6.                         `family(inet '::1')`         6 |
| `host` ( `inet` )         text                         Returns the IP address as text, ignoring the netmask.                         `host(inet '192.168.1.0/24')`         192.168.1.0 |
| `hostmask` ( `inet` )         inet                         Computes the host mask for the address's network.                         `hostmask(inet '192.168.23.20/30')`         0.0.0.3 |
| `inet_merge` ( `inet`, `inet` )         cidr                         Computes the smallest network that includes both of the given networks.                         `inet_merge(inet '192.168.1.5/24', inet '192.168.2.5/24')`         192.168.0.0/22 |
| `inet_same_family` ( `inet`, `inet` )         boolean                         Tests whether the addresses belong to the same IP family.                         `inet_same_family(inet '192.168.1.5/24', inet '::1')`         f |
| `masklen` ( `inet` )         integer                         Returns the netmask length in bits.                         `masklen(inet '192.168.1.5/24')`         24 |
| `netmask` ( `inet` )         inet                         Computes the network mask for the address's network.                         `netmask(inet '192.168.1.5/24')`         255.255.255.0 |
| `network` ( `inet` )         cidr                         Returns the network part of the address, zeroing out         whatever is to the right of the netmask.         (This is equivalent to casting the value to `cidr`.)                         `network(inet '192.168.1.5/24')`         192.168.1.0/24 |
| `set_masklen` ( `inet`, `integer` )         inet                         Sets the netmask length for an `inet` value.         The address part does not change.                         `set_masklen(inet '192.168.1.5/24', 16)`         192.168.1.5/16 |
| `set_masklen` ( `cidr`, `integer` )         cidr                         Sets the netmask length for a `cidr` value.         Address bits to the right of the new netmask are set to zero.                         `set_masklen(cidr '192.168.1.0/24', 16)`         192.168.0.0/16 |
| `text` ( `inet` )         text                         Returns the unabbreviated IP address and netmask length as text.         (This has the same result as an explicit cast to `text`.)                         `text(inet '192.168.1.5')`         192.168.1.5/32 |

> **Tip:**

> The `abbrev`, `host`,
> and `text` functions are primarily intended to offer
> alternative display formats for IP addresses.
>

The MAC address types, `macaddr` and `macaddr8`,
support the usual comparison operators shown in
[functions-comparison-op-table](#functions-comparison-op-table)
as well as the specialized functions shown in
[macaddr-functions-table](#macaddr-functions-table).
In addition, they support the bitwise logical operators
`~`, `&` and `|`
(NOT, AND and OR), just as shown above for IP addresses.

| Function                         Description                         Example(s) |
| --- |
| `trunc` ( `macaddr` )         macaddr                         Sets the last 3 bytes of the address to zero.  The remaining prefix         can be associated with a particular manufacturer (using data not         included in PostgreSQL).                         `trunc(macaddr '12:34:56:78:90:ab')`         12:34:56:00:00:00 |
| `trunc` ( `macaddr8` )         macaddr8                         Sets the last 5 bytes of the address to zero.  The remaining prefix         can be associated with a particular manufacturer (using data not         included in PostgreSQL).                         `trunc(macaddr8 '12:34:56:78:90:ab:cd:ef')`         12:34:56:00:00:00:00:00 |
| `macaddr8_set7bit` ( `macaddr8` )         macaddr8                         Sets the 7th bit of the address to one, creating what is known as         modified EUI-64, for inclusion in an IPv6 address.                         `macaddr8_set7bit(macaddr8 '00:34:56:ab:cd:ef')`         02:34:56:ff:fe:ab:cd:ef |

## UUID Functions

PostgreSQL includes one function to generate a UUID:

```
`gen_random_uuid` () uuid
```

This function returns a version 4 (random) UUID.  This is the most commonly
used type of UUID and is appropriate for most applications.

The [uuid-ossp](#uuid-ossp) module provides additional functions that
implement other standard algorithms for generating UUIDs.

PostgreSQL also provides the usual comparison
operators shown in [functions-comparison-op-table](#functions-comparison-op-table) for
UUIDs.

## XML Functions

The functions and function-like expressions described in this
section operate on values of type `xml`.  See [datatype-xml](#datatype-xml) for information about the `xml`
type.  The function-like expressions `xmlparse`
and `xmlserialize` for converting to and from
type `xml` are documented there, not in this section.

Use of most of these functions
requires PostgreSQL to have been built
with `configure --with-libxml`.

### Producing XML Content

A set of functions and function-like expressions is available for
producing XML content from SQL data.  As such, they are
particularly suitable for formatting query results into XML
documents for processing in client applications.

#### `xmlcomment`

```
`xmlcomment` ( `text` ) xml
```

The function `xmlcomment` creates an XML value
containing an XML comment with the specified text as content.
The text cannot contain "`--`" or end with a
"`-`", otherwise the resulting construct
would not be a valid XML comment.
If the argument is null, the result is null.

Example:

```

SELECT xmlcomment('hello');

xmlcomment
--------------

```

#### `xmlconcat`

```
`xmlconcat` ( `xml` , ... ) xml
```

The function `xmlconcat` concatenates a list
of individual XML values to create a single value containing an
XML content fragment.  Null values are omitted; the result is
only null if there are no nonnull arguments.

Example:

```

SELECT xmlconcat('', 'foo');

xmlconcat
----------------------
foo

```

XML declarations, if present, are combined as follows.  If all
argument values have the same XML version declaration, that
version is used in the result, else no version is used.  If all
argument values have the standalone declaration value
"yes", then that value is used in the result.  If
all argument values have a standalone declaration value and at
least one is "no", then that is used in the result.
Else the result will have no standalone declaration.  If the
result is determined to require a standalone declaration but no
version declaration, a version declaration with version 1.0 will
be used because XML requires an XML declaration to contain a
version declaration.  Encoding declarations are ignored and
removed in all cases.

Example:

```

SELECT xmlconcat('', '');

xmlconcat
-----------------------------------

```

#### `xmlelement`

```
`xmlelement` ( `NAME` `name` , `XMLATTRIBUTES` ( `attvalue`  `AS` `attname`  , ... )  , `content` , ... ) xml
```

The `xmlelement` expression produces an XML
element with the given name, attributes, and content.
The `name`
and `attname` items shown in the syntax are
simple identifiers, not values.  The `attvalue`
and `content` items are expressions, which can
yield any PostgreSQL data type.  The
argument(s) within `XMLATTRIBUTES` generate attributes
of the XML element; the `content` value(s) are
concatenated to form its content.

Examples:

```

SELECT xmlelement(name foo);

xmlelement
------------

SELECT xmlelement(name foo, xmlattributes('xyz' as bar));

xmlelement
------------------

SELECT xmlelement(name foo, xmlattributes(current_date as bar), 'cont', 'ent');

xmlelement
-------------------------------------
content

```

Element and attribute names that are not valid XML names are
escaped by replacing the offending characters by the sequence
`_x`HHHH`_`, where
`HHHH` is the character's Unicode
codepoint in hexadecimal notation.  For example:

```

SELECT xmlelement(name "foo$bar", xmlattributes('xyz' as "a&b"));

xmlelement
----------------------------------

```

An explicit attribute name need not be specified if the attribute
value is a column reference, in which case the column's name will
be used as the attribute name by default.  In other cases, the
attribute must be given an explicit name.  So this example is
valid:

```
CREATE TABLE test (a xml, b xml);
SELECT xmlelement(name test, xmlattributes(a, b)) FROM test;
```

But these are not:

```
SELECT xmlelement(name test, xmlattributes('constant'), a, b) FROM test;
SELECT xmlelement(name test, xmlattributes(func(a, b))) FROM test;
```

Element content, if specified, will be formatted according to
its data type.  If the content is itself of type `xml`,
complex XML documents can be constructed.  For example:

```

SELECT xmlelement(name foo, xmlattributes('xyz' as bar),
xmlelement(name abc),
xmlcomment('test'),
xmlelement(name xyz));

xmlelement
----------------------------------------------

```

Content of other types will be formatted into valid XML character
data.  This means in particular that the characters <, >,
and & will be converted to entities.  Binary data (data type
`bytea`) will be represented in base64 or hex
encoding, depending on the setting of the configuration parameter
[guc-xmlbinary](#guc-xmlbinary).  The particular behavior for
individual data types is expected to evolve in order to align the
PostgreSQL mappings with those specified in SQL:2006 and later,
as discussed in [functions-xml-limits-casts](#functions-xml-limits-casts).

#### `xmlforest`

```
`xmlforest` ( `content`  `AS` `name`  , ... ) xml
```

The `xmlforest` expression produces an XML
forest (sequence) of elements using the given names and content.
As for `xmlelement`,
each `name` must be a simple identifier, while
the `content` expressions can have any data
type.

Examples:

```
SELECT xmlforest('abc' AS foo, 123 AS bar);

xmlforest
------------------------------
abc123

SELECT xmlforest(table_name, column_name)
FROM information_schema.columns
WHERE table_schema = 'pg_catalog';

xmlforest
-----------------------------------------------------------------------
|  |
|  |
|  |

]]>
```

## JSON Functions and Operators

This section describes:

- functions and operators for processing and creating JSON data
- the SQL/JSON path language

To provide native support for JSON data types within the SQL environment,
PostgreSQL implements the
*SQL/JSON data model*.
This model comprises sequences of items. Each item can hold SQL scalar
values, with an additional SQL/JSON null value, and composite data structures
that use JSON arrays and objects. The model is a formalization of the implied
data model in the JSON specification
[RFC 7159](https://datatracker.ietf.org/doc/html/rfc7159).

SQL/JSON allows you to handle JSON data alongside regular SQL data,
with transaction support, including:

- Uploading JSON data into the database and storing it in
regular SQL columns as character or binary strings.
- Generating JSON objects and arrays from relational data.
- Querying JSON data using SQL/JSON query functions and
SQL/JSON path language expressions.

To learn more about the SQL/JSON standard, see
[sqltr-19075-6](#sqltr-19075-6). For details on JSON types
supported in PostgreSQL,
see [datatype-json](#datatype-json).

### Processing and Creating JSON Data

[functions-json-op-table](#functions-json-op-table) shows the operators that
are available for use with JSON data types (see [datatype-json](#datatype-json)).
In addition, the usual comparison operators shown in [functions-comparison-op-table](#functions-comparison-op-table) are available for
`jsonb`, though not for `json`.  The comparison
operators follow the ordering rules for B-tree operations outlined in
[json-indexing](#json-indexing).
See also [functions-aggregate](#functions-aggregate) for the aggregate
function `json_agg` which aggregates record
values as JSON, the aggregate function
`json_object_agg` which aggregates pairs of values
into a JSON object, and their `jsonb` equivalents,
`jsonb_agg` and `jsonb_object_agg`.

| Operator                         Description                         Example(s) |
| --- |
| `json` `->` `integer`         json                         `jsonb` `->` `integer`         jsonb                         Extracts n'th element of JSON array         (array elements are indexed from zero, but negative integers count         from the end).                         `'[{"a":"foo"},{"b":"bar"},{"c":"baz"}]'::json -> 2`         {"c":"baz"}                         `'[{"a":"foo"},{"b":"bar"},{"c":"baz"}]'::json -> -3`         {"a":"foo"} |
| `json` `->` `text`         json                         `jsonb` `->` `text`         jsonb                         Extracts JSON object field with the given key.                         `'{"a": {"b":"foo"}}'::json -> 'a'`         {"b":"foo"} |
| `json` `->>` `integer`         text                         `jsonb` `->>` `integer`         text                         Extracts n'th element of JSON array,         as `text`.                         `'[1,2,3]'::json ->> 2`         3 |
| `json` `->>` `text`         text                         `jsonb` `->>` `text`         text                         Extracts JSON object field with the given key, as `text`.                         `'{"a":1,"b":2}'::json ->> 'b'`         2 |
| `json` `#>` `text[]`         json                         `jsonb` `#>` `text[]`         jsonb                         Extracts JSON sub-object at the specified path, where path elements         can be either field keys or array indexes.                         `'{"a": {"b": ["foo","bar"]}}'::json #> '{a,b,1}'`         "bar" |
| `json` `#>>` `text[]`         text                         `jsonb` `#>>` `text[]`         text                         Extracts JSON sub-object at the specified path as `text`.                         `'{"a": {"b": ["foo","bar"]}}'::json #>> '{a,b,1}'`         bar |

> **Note:**

> The field/element/path extraction operators return NULL, rather than
> failing, if the JSON input does not have the right structure to match
> the request; for example if no such key or array element exists.
>

Some further operators exist only for `jsonb`, as shown
in [functions-jsonb-op-table](#functions-jsonb-op-table).
[json-indexing](#json-indexing)
describes how these operators can be used to effectively search indexed
`jsonb` data.

| Operator                         Description                         Example(s) |
| --- |
| `jsonb` `@>` `jsonb`         boolean                         Does the first JSON value contain the second?         (See [json-containment](#json-containment) for details about containment.)                         `'{"a":1, "b":2}'::jsonb &#64;> '{"b":2}'::jsonb`         t |
| `jsonb` ` 2)'`         t |
| `jsonb` `@@` `jsonpath`         boolean                         Returns the result of a JSON path predicate check for the         specified JSON value.  Only the first item of the result is taken into         account.  If the result is not Boolean, then `NULL`         is returned.                         `'{"a":[1,2,3,4,5]}'::jsonb @@ '$.a[*] > 2'`         t |

> **Note:**

> The `jsonpath` operators `@?`
> and `@@` suppress the following errors: missing object
> field or array element, unexpected JSON item type, datetime and numeric
> errors.  The `jsonpath`-related functions described below can
> also be told to suppress these types of errors.  This behavior might be
> helpful when searching JSON document collections of varying structure.
>

[functions-json-creation-table](#functions-json-creation-table) shows the functions that are
available for constructing `json` and `jsonb` values.
Some functions in this table have a `RETURNING` clause,
which specifies the data type returned.  It must be one of `json`,
`jsonb`, `bytea`, a character string type (`text`,
`char`, or `varchar`), or a type
that can be cast to `json`.
By default, the `json` type is returned.

| Function                         Description                         Example(s) |
| --- |
| `to_json` ( `anyelement` )         json                                  `to_jsonb` ( `anyelement` )         jsonb                         Converts any SQL value to `json` or `jsonb`.         Arrays and composites are converted recursively to arrays and         objects (multidimensional arrays become arrays of arrays in JSON).         Otherwise, if there is a cast from the SQL data type         to `json`, the cast function will be used to perform the         conversion; (Note: For example, the  extension has a cast           from `hstore` to `json`, so that           `hstore` values converted via the JSON creation functions           will be represented as JSON objects, not as primitive string values.)         otherwise, a scalar JSON value is produced.  For any scalar other than         a number, a Boolean, or a null value, the text representation will be         used, with escaping as necessary to make it a valid JSON string value.                         `to_json('Fred said "Hi."'::text)`         "Fred said \"Hi.\""                         `to_jsonb(row(42, 'Fred said "Hi."'::text))`         {"f1": 42, "f2": "Fred said \"Hi.\""} |
| `array_to_json` ( `anyarray` , `boolean`  )         json                         Converts an SQL array to a JSON array.  The behavior is the same         as `to_json` except that line feeds will be added         between top-level array elements if the optional boolean parameter is         true.                         `array_to_json('{{1,5},{99,100}}'::int[])`         [[1,5],[99,100]] |
| `json_array` (           { `value_expression`  `FORMAT JSON`  } , ...            { `NULL` | `ABSENT` } `ON NULL`            `RETURNING` `data_type`  `FORMAT JSON`  `ENCODING UTF8`   )                            `json_array` (           `query_expression`            `RETURNING` `data_type`  `FORMAT JSON`  `ENCODING UTF8`   )                            Constructs a JSON array from either a series of          `value_expression` parameters or from the results          of `query_expression`,          which must be a SELECT query returning a single column. If          `ABSENT ON NULL` is specified, NULL values are ignored.          This is always the case if a          `query_expression` is used.                            `json_array(1,true,json '{"a":null}')`          [1, true, {"a":null}]                            `json_array(SELECT * FROM (VALUES(1),(2)) t)`          [1, 2] |
| `row_to_json` ( `record` , `boolean`  )         json                         Converts an SQL composite value to a JSON object.  The behavior is the         same as `to_json` except that line feeds will be         added between top-level elements if the optional boolean parameter is         true.                         `row_to_json(row(1,'foo'))`         {"f1":1,"f2":"foo"} |
| `json_build_array` ( `VARIADIC` `"any"` )         json                                  `jsonb_build_array` ( `VARIADIC` `"any"` )         jsonb                         Builds a possibly-heterogeneously-typed JSON array out of a variadic         argument list.  Each argument is converted as         per `to_json` or `to_jsonb`.                         `json_build_array(1, 2, 'foo', 4, 5)`         [1, 2, "foo", 4, 5] |
| `json_build_object` ( `VARIADIC` `"any"` )         json                                  `jsonb_build_object` ( `VARIADIC` `"any"` )         jsonb                         Builds a JSON object out of a variadic argument list.  By convention,         the argument list consists of alternating keys and values.  Key         arguments are coerced to text; value arguments are converted as         per `to_json` or `to_jsonb`.                         `json_build_object('foo', 1, 2, row(3,'bar'))`         {"foo" : 1, "2" : {"f1":3,"f2":"bar"}} |
| `json_object` (           { `key_expression` { `VALUE` | ':' }           `value_expression`  `FORMAT JSON`  `ENCODING UTF8`   }, ...            { `NULL` | `ABSENT` } `ON NULL`            { `WITH` | `WITHOUT` } `UNIQUE`  `KEYS`             `RETURNING` `data_type`  `FORMAT JSON`  `ENCODING UTF8`   )                            Constructs a JSON object of all the key/value pairs given,          or an empty object if none are given.          `key_expression` is a scalar expression          defining the JSON key, which is          converted to the `text` type.          It cannot be `NULL` nor can it          belong to a type that has a cast to the `json` type.          If `WITH UNIQUE KEYS` is specified, there must not          be any duplicate `key_expression`.          Any pair for which the `value_expression`          evaluates to `NULL` is omitted from the output          if `ABSENT ON NULL` is specified;          if `NULL ON NULL` is specified or the clause          omitted, the key is included with value `NULL`.                            `json_object('code' VALUE 'P123', 'title': 'Jaws')`          {"code" : "P123", "title" : "Jaws"} |
| `json_object` ( `text[]` )         json                                  `jsonb_object` ( `text[]` )         jsonb                         Builds a JSON object out of a text array.  The array must have either         exactly one dimension with an even number of members, in which case         they are taken as alternating key/value pairs, or two dimensions         such that each inner array has exactly two elements, which         are taken as a key/value pair.  All values are converted to JSON         strings.                         `json_object('{a, 1, b, "def", c, 3.5}')`         {"a" : "1", "b" : "def", "c" : "3.5"}                 `json_object('{{a, 1}, {b, "def"}, {c, 3.5}}')`         {"a" : "1", "b" : "def", "c" : "3.5"} |
| `json_object` ( keys `text[]`, values `text[]` )         json                         `jsonb_object` ( keys `text[]`, values `text[]` )         jsonb                         This form of `json_object` takes keys and values         pairwise from separate text arrays.  Otherwise it is identical to         the one-argument form.                         `json_object('{a,b}', '{1,2}')`         {"a": "1", "b": "2"} |

[functions-sqljson-misc](#functions-sqljson-misc) details SQL/JSON
facilities for testing JSON.

| Function signature                         Description                         Example(s) |
| --- |
| `expression` `IS`  `NOT`  `JSON`          { `VALUE` | `SCALAR` | `ARRAY` | `OBJECT` }           { `WITH` | `WITHOUT` } `UNIQUE`  `KEYS`                           This predicate tests whether `expression` can be         parsed as JSON, possibly of a specified type.         If `SCALAR` or `ARRAY` or         `OBJECT` is specified, the         test is whether or not the JSON is of that particular type. If         `WITH UNIQUE KEYS` is specified, then any object in the         `expression` is also tested to see if it         has duplicate keys.                  ``` SELECT js,   js IS JSON "json?",   js IS JSON SCALAR "scalar?",   js IS JSON OBJECT "object?",   js IS JSON ARRAY "array?" FROM (VALUES       ('123'), ('"abc"'), ('{"a": "b"}'), ('[1,2]'),('abc')) foo(js);      js     | json? | scalar? | object? | array? ------------+-------+---------+---------+--------  123        | t     | t       | f       | f  "abc"      | t     | t       | f       | f  {"a": "b"} | t     | f       | t       | f  [1,2]      | t     | f       | f       | t  abc        | f     | f       | f       | f ```                   ``` SELECT js,   js IS JSON OBJECT "object?",   js IS JSON ARRAY "array?",   js IS JSON ARRAY WITH UNIQUE KEYS "array w. UK?",   js IS JSON ARRAY WITHOUT UNIQUE KEYS "array w/o UK?" FROM (VALUES ('[{"a":"1"},  {"b":"2","b":"3"}]')) foo(js); -[ RECORD 1 ]-+-------------------- js            | [{"a":"1"},        +               |  {"b":"2","b":"3"}] object?       | f array?        | t array w. UK?  | f array w/o UK? | t ``` |

[functions-json-processing-table](#functions-json-processing-table) shows the functions that
are available for processing `json` and `jsonb` values.

| Function                         Description                         Example(s) |
| --- |
| `json_array_elements` ( `json` )         setof json                                  `jsonb_array_elements` ( `jsonb` )         setof jsonb                         Expands the top-level JSON array into a set of JSON values.                         `select * from json_array_elements('[1,true, [2,false]]')`           ``` value -----------  1  true  [2,false] ``` |
| `json_array_elements_text` ( `json` )         setof text                                  `jsonb_array_elements_text` ( `jsonb` )         setof text                         Expands the top-level JSON array into a set of `text` values.                         `select * from json_array_elements_text('["foo", "bar"]')`           ``` value -----------  foo  bar ``` |
| `json_array_length` ( `json` )         integer                                  `jsonb_array_length` ( `jsonb` )         integer                         Returns the number of elements in the top-level JSON array.                         `json_array_length('[1,2,3,{"f1":1,"f2":[5,6]},4]')`         5                         `jsonb_array_length('[]')`         0 |
| `json_each` ( `json` )         setof record         ( key `text`,         value `json` )                                  `jsonb_each` ( `jsonb` )         setof record         ( key `text`,         value `jsonb` )                         Expands the top-level JSON object into a set of key/value pairs.                         `select * from json_each('{"a":"foo", "b":"bar"}')`           ``` key | value -----+-------  a   | "foo"  b   | "bar" ``` |
| `json_each_text` ( `json` )         setof record         ( key `text`,         value `text` )                                  `jsonb_each_text` ( `jsonb` )         setof record         ( key `text`,         value `text` )                         Expands the top-level JSON object into a set of key/value pairs.         The returned values will be of         type `text`.                         `select * from json_each_text('{"a":"foo", "b":"bar"}')`           ``` key | value -----+-------  a   | foo  b   | bar ``` |
| `json_extract_path` ( from_json `json`, `VARIADIC` path_elems `text[]` )         json                                  `jsonb_extract_path` ( from_json `jsonb`, `VARIADIC` path_elems `text[]` )         jsonb                         Extracts JSON sub-object at the specified path.         (This is functionally equivalent to the `#>`         operator, but writing the path out as a variadic list can be more         convenient in some cases.)                         `json_extract_path('{"f2":{"f3":1},"f4":{"f5":99,"f6":"foo"}}', 'f4', 'f6')`         "foo" |
| `json_extract_path_text` ( from_json `json`, `VARIADIC` path_elems `text[]` )         text                                  `jsonb_extract_path_text` ( from_json `jsonb`, `VARIADIC` path_elems `text[]` )         text                         Extracts JSON sub-object at the specified path as `text`.         (This is functionally equivalent to the `#>>`         operator.)                         `json_extract_path_text('{"f2":{"f3":1},"f4":{"f5":99,"f6":"foo"}}', 'f4', 'f6')`         foo |
| `json_object_keys` ( `json` )         setof text                                  `jsonb_object_keys` ( `jsonb` )         setof text                         Returns the set of keys in the top-level JSON object.                         `select * from json_object_keys('{"f1":"abc","f2":{"f3":"a", "f4":"b"}}')`           ``` json_object_keys ------------------  f1  f2 ``` |
| `json_populate_record` ( base `anyelement`, from_json `json` )         anyelement                                  `jsonb_populate_record` ( base `anyelement`, from_json `jsonb` )         anyelement                         Expands the top-level JSON object to a row having the composite type         of the base argument.  The JSON object         is scanned for fields whose names match column names of the output row         type, and their values are inserted into those columns of the output.         (Fields that do not correspond to any output column name are ignored.)         In typical use, the value of base is just         `NULL`, which means that any output columns that do         not match any object field will be filled with nulls.  However,         if base isn't `NULL` then         the values it contains will be used for unmatched columns.                         To convert a JSON value to the SQL type of an output column, the         following rules are applied in sequence:          - A JSON null value is converted to an SQL null in all cases. - If the output column is of type `json`            or `jsonb`, the JSON value is just reproduced exactly. - If the output column is a composite (row) type, and the JSON value            is a JSON object, the fields of the object are converted to columns            of the output row type by recursive application of these rules. - Likewise, if the output column is an array type and the JSON value            is a JSON array, the elements of the JSON array are converted to            elements of the output array by recursive application of these            rules. - Otherwise, if the JSON value is a string, the contents of the            string are fed to the input conversion function for the column's            data type. - Otherwise, the ordinary text representation of the JSON value is            fed to the input conversion function for the column's data type.                          While the example below uses a constant JSON value, typical use would         be to reference a `json` or `jsonb` column         laterally from another table in the query's `FROM`         clause.  Writing `json_populate_record` in         the `FROM` clause is good practice, since all of the         extracted columns are available for use without duplicate function         calls.                         `create type subrowtype as (d int, e text);`         `create type myrowtype as (a int, b text[], c subrowtype);`                         `select * from json_populate_record(null::myrowtype,          '{"a": 1, "b": ["2", "a b"], "c": {"d": 4, "e": "a  b c"}, "x": "foo"}')`           ``` a |   b       |      c ---+-----------+-------------  1 | {2,"a b"} | (4,"a b c") ``` |
| `json_populate_recordset` ( base `anyelement`, from_json `json` )         setof anyelement                                  `jsonb_populate_recordset` ( base `anyelement`, from_json `jsonb` )         setof anyelement                         Expands the top-level JSON array of objects to a set of rows having         the composite type of the base argument.         Each element of the JSON array is processed as described above         for `json[b]_populate_record`.                         `create type twoints as (a int, b int);`                         `select * from json_populate_recordset(null::twoints, '[{"a":1,"b":2}, {"a":3,"b":4}]')`           ``` a | b ---+---  1 | 2  3 | 4 ``` |
| `json_to_record` ( `json` )         record                                  `jsonb_to_record` ( `jsonb` )         record                         Expands the top-level JSON object to a row having the composite type         defined by an `AS` clause.  (As with all functions         returning `record`, the calling query must explicitly         define the structure of the record with an `AS`         clause.)  The output record is filled from fields of the JSON object,         in the same way as described above         for `json[b]_populate_record`.  Since there is no         input record value, unmatched columns are always filled with nulls.                         `create type myrowtype as (a int, b text);`                         `select * from json_to_record('{"a":1,"b":[1,2,3],"c":[1,2,3],"e":"bar","r": {"a": 123, "b": "a b c"}}') as x(a int, b text, c int[], d text, r myrowtype)`           ``` a |    b    |    c    | d |       r ---+---------+---------+---+---------------  1 | [1,2,3] | {1,2,3} |   | (123,"a b c") ``` |
| `json_to_recordset` ( `json` )         setof record                                  `jsonb_to_recordset` ( `jsonb` )         setof record                         Expands the top-level JSON array of objects to a set of rows having         the composite type defined by an `AS` clause.  (As         with all functions returning `record`, the calling query         must explicitly define the structure of the record with         an `AS` clause.)  Each element of the JSON array is         processed as described above         for `json[b]_populate_record`.                         `select * from json_to_recordset('[{"a":1,"b":"foo"}, {"a":"2","c":"bar"}]') as x(a int, b text)`           ``` a |  b ---+-----  1 | foo  2 | ``` |
| `jsonb_set` ( target `jsonb`, path `text[]`, new_value `jsonb` , create_if_missing `boolean`  )         jsonb                         Returns target         with the item designated by path         replaced by new_value, or with         new_value added if         create_if_missing is true (which is the         default) and the item designated by path         does not exist.         All earlier steps in the path must exist, or         the target is returned unchanged.         As with the path oriented operators, negative integers that         appear in the path count from the end         of JSON arrays.         If the last path step is an array index that is out of range,         and create_if_missing is true, the new         value is added at the beginning of the array if the index is negative,         or at the end of the array if it is positive.                         `jsonb_set('[{"f1":1,"f2":null},2,null,3]', '{0,f1}', '[2,3,4]', false)`         [{"f1": [2, 3, 4], "f2": null}, 2, null, 3]                         `jsonb_set('[{"f1":1,"f2":null},2]', '{0,f3}', '[2,3,4]')`         [{"f1": 1, "f2": null, "f3": [2, 3, 4]}, 2] |
| `jsonb_set_lax` ( target `jsonb`, path `text[]`, new_value `jsonb` , create_if_missing `boolean` , null_value_treatment `text`  )         jsonb                         If new_value is not `NULL`,         behaves identically to `jsonb_set`. Otherwise behaves         according to the value         of null_value_treatment which must be one         of `'raise_exception'`,         `'use_json_null'`, `'delete_key'`, or         `'return_target'`. The default is         `'use_json_null'`.                         `jsonb_set_lax('[{"f1":1,"f2":null},2,null,3]', '{0,f1}', null)`         [{"f1": null, "f2": null}, 2, null, 3]                         `jsonb_set_lax('[{"f1":99,"f2":null},2]', '{0,f3}', null, true, 'return_target')`         [{"f1": 99, "f2": null}, 2] |
| `jsonb_insert` ( target `jsonb`, path `text[]`, new_value `jsonb` , insert_after `boolean`  )         jsonb                         Returns target         with new_value inserted.  If the item         designated by the path is an array         element, new_value will be inserted before         that item if insert_after is false (which         is the default), or after it         if insert_after is true.  If the item         designated by the path is an object         field, new_value will be inserted only if         the object does not already contain that key.         All earlier steps in the path must exist, or         the target is returned unchanged.         As with the path oriented operators, negative integers that         appear in the path count from the end         of JSON arrays.         If the last path step is an array index that is out of range, the new         value is added at the beginning of the array if the index is negative,         or at the end of the array if it is positive.                         `jsonb_insert('{"a": [0,1,2]}', '{a, 1}', '"new_value"')`         {"a": [0, "new_value", 1, 2]}                         `jsonb_insert('{"a": [0,1,2]}', '{a, 1}', '"new_value"', true)`         {"a": [0, 1, "new_value", 2]} |
| `json_strip_nulls` ( `json` )         json                                  `jsonb_strip_nulls` ( `jsonb` )         jsonb                         Deletes all object fields that have null values from the given JSON         value, recursively.  Null values that are not object fields are         untouched.                         `json_strip_nulls('[{"f1":1, "f2":null}, 2, null, 3]')`         [{"f1":1},2,null,3] |
| `jsonb_path_exists` ( target `jsonb`, path `jsonpath` , vars `jsonb` , silent `boolean`  )         boolean                         Checks whether the JSON path returns any item for the specified JSON         value.         If the vars argument is specified, it must         be a JSON object, and its fields provide named values to be         substituted into the `jsonpath` expression.         If the silent argument is specified and         is `true`, the function suppresses the same errors         as the `@?` and `@@` operators do.                         `jsonb_path_exists('{"a":[1,2,3,4,5]}', '$.a[*] ? (@ >= $min && @ = $min && @ = $min && @ = $min && @ = $min && @  130)
```

To get the start times of segments with such values, you have to
filter out irrelevant segments before returning the start times, so the
filter expression is applied to the previous step, and the path used
in the condition is different:

```
$.track.segments[*] ? (@.HR > 130)."start time"
```

You can use several filter expressions in sequence, if required. For
example, the following expression selects start times of all segments that
contain locations with relevant coordinates and high heart rate values:

```
$.track.segments[*] ? (@.location[1]  130)."start time"
```

Using filter expressions at different nesting levels is also allowed.
The following example first filters all segments by location, and then
returns high heart rate values for these segments, if available:

```
$.track.segments[*] ? (@.location[1]  130)
```

You can also nest filter expressions within each other:

```
$.track ? (exists(@.segments[*] ? (@.HR > 130))).segments.size()
```

This expression returns the size of the track if it contains any
segments with high heart rate values, or an empty sequence otherwise.

PostgreSQL's implementation of the SQL/JSON path
language has the following deviations from the SQL/JSON standard:

- A path expression can be a Boolean predicate, although the SQL/JSON
standard allows predicates only in filters.  This is necessary for
implementation of the `@@` operator. For example,
the following `jsonpath` expression is valid in
PostgreSQL:

```
$.track.segments[*].HR  **Note:**

> The result type of the `datetime()` and
> `datetime(`template`)`
> methods can be `date`, `timetz`, `time`,
> `timestamptz`, or `timestamp`.
> Both methods determine their result type dynamically.
>

>

> The `datetime()` method sequentially tries to
> match its input string to the ISO formats
> for `date`, `timetz`, `time`,
> `timestamptz`, and `timestamp`. It stops on
> the first matching format and emits the corresponding data type.
>

>

> The `datetime(`template`)`
> method determines the result type according to the fields used in the
> provided template string.
>

>

> The `datetime()` and
> `datetime(`template`)` methods
> use the same parsing rules as the `to_timestamp` SQL
> function does (see [functions-formatting](#functions-formatting)), with three
> exceptions.  First, these methods don't allow unmatched template
> patterns.  Second, only the following separators are allowed in the
> template string: minus sign, period, solidus (slash), comma, apostrophe,
> semicolon, colon and space.  Third, separators in the template string
> must exactly match the input string.
>

>

> If different date/time types need to be compared, an implicit cast is
> applied. A `date` value can be cast to `timestamp`
> or `timestamptz`, `timestamp` can be cast to
> `timestamptz`, and `time` to `timetz`.
> However, all but the first of these conversions depend on the current
> [guc-timezone](#guc-timezone) setting, and thus can only be performed
> within timezone-aware `jsonpath` functions.
>

[functions-sqljson-filter-ex-table](#functions-sqljson-filter-ex-table) shows the available
filter expression elements.

| Predicate/Value                         Description                         Example(s) |
| --- |
| `value` `==` `value`         boolean                         Equality comparison (this, and the other comparison operators, work on         all JSON scalar values)                         `jsonb_path_query_array('[1, "a", 1, 3]', '$[*] ? (@ == 1)')`         [1, 1]                         `jsonb_path_query_array('[1, "a", 1, 3]', '$[*] ? (@ == "a")')`         ["a"] |
| `value` `!=` `value`         boolean                         `value` `<>` `value`         boolean                         Non-equality comparison                         `jsonb_path_query_array('[1, 2, 1, 3]', '$[*] ? (@ != 1)')`         [2, 3]                         `jsonb_path_query_array('["a", "b", "c"]', '$[*] ? (@ <> "b")')`         ["a", "c"] |
| `value` `` `value`         boolean                         Greater-than comparison                         `jsonb_path_query_array('[1, 2, 3]', '$[*] ? (@ > 2)')`         [3] |
| `value` `>=` `value`         boolean                         Greater-than-or-equal-to comparison                         `jsonb_path_query_array('[1, 2, 3]', '$[*] ? (@ >= 2)')`         [2, 3] |
| `true`         boolean                         JSON constant `true`                         `jsonb_path_query('[{"name": "John", "parent": false}, {"name": "Chris", "parent": true}]', '$[*] ? (@.parent == true)')`         {"name": "Chris", "parent": true} |
| `false`         boolean                         JSON constant `false`                         `jsonb_path_query('[{"name": "John", "parent": false}, {"name": "Chris", "parent": true}]', '$[*] ? (@.parent == false)')`         {"name": "John", "parent": false} |
| `null`         `value`                         JSON constant `null` (note that, unlike in SQL,         comparison to `null` works normally)                         `jsonb_path_query('[{"name": "Mary", "job": null}, {"name": "Michael", "job": "driver"}]', '$[*] ? (@.job == null) .name')`         "Mary" |
| `boolean` `&&` `boolean`         boolean                         Boolean AND                         `jsonb_path_query('[1, 3, 7]', '$[*] ? (@ > 1 && @  5)')`         7 |
| `!` `boolean`         boolean                         Boolean NOT                         `jsonb_path_query('[1, 3, 7]', '$[*] ? (!(@  0) is unknown)')`         "foo" |
| `string` `like_regex` `string`  `flag` `string`          boolean                         Tests whether the first operand matches the regular expression         given by the second operand, optionally with modifications         described by a string of `flag` characters (see         [jsonpath-regular-expressions](#jsonpath-regular-expressions)).                         `jsonb_path_query_array('["abc", "abd", "aBdC", "abdacb", "babc"]', '$[*] ? (@ like_regex "^ab.*c")')`         ["abc", "abdacb"]                         `jsonb_path_query_array('["abc", "abd", "aBdC", "abdacb", "babc"]', '$[*] ? (@ like_regex "^ab.*c" flag "i")')`         ["abc", "aBdC", "abdacb"] |
| `string` `starts with` `string`         boolean                         Tests whether the second operand is an initial substring of the first         operand.                         `jsonb_path_query('["John Smith", "Mary Stone", "Bob Johnson"]', '$[*] ? (@ starts with "John")')`         "John Smith" |
| `exists` `(` `path_expression` `)`         boolean                         Tests whether a path expression matches at least one SQL/JSON item.         Returns `unknown` if the path expression would result         in an error; the second example uses this to avoid a no-such-key error         in strict mode.                         `jsonb_path_query('{"x": [1, 2], "y": [2, 4]}', 'strict $.* ? (exists (@ ? (@[*] > 2)))')`         [2, 4]                         `jsonb_path_query_array('{"value": 41}', 'strict $ ? (exists (@.name)) .name')`         [] |

#### SQL/JSON Regular Expressions

SQL/JSON path expressions allow matching text to a regular expression
with the `like_regex` filter.  For example, the
following SQL/JSON path query would case-insensitively match all
strings in an array that start with an English vowel:

```
$[*] ? (@ like_regex "^[aeiou]" flag "i")
```

The optional `flag` string may include one or more of
the characters
`i` for case-insensitive match,
`m` to allow `^`
and `$` to match at newlines,
`s` to allow `.` to match a newline,
and `q` to quote the whole pattern (reducing the
behavior to a simple substring match).

The SQL/JSON standard borrows its definition for regular expressions
from the `LIKE_REGEX` operator, which in turn uses the
XQuery standard.  PostgreSQL does not currently support the
`LIKE_REGEX` operator.  Therefore,
the `like_regex` filter is implemented using the
POSIX regular expression engine described in
[functions-posix-regexp](#functions-posix-regexp).  This leads to various minor
discrepancies from standard SQL/JSON behavior, which are cataloged in
[posix-vs-xquery](#posix-vs-xquery).
Note, however, that the flag-letter incompatibilities described there
do not apply to SQL/JSON, as it translates the XQuery flag letters to
match what the POSIX engine expects.

Keep in mind that the pattern argument of `like_regex`
is a JSON path string literal, written according to the rules given in
[datatype-jsonpath](#datatype-jsonpath).  This means in particular that any
backslashes you want to use in the regular expression must be doubled.
For example, to match string values of the root document that contain
only digits:

```
$.* ? (@ like_regex "^\\d+$")
```

## Sequence Manipulation Functions

This section describes functions for operating on *sequence
objects*, also called sequence generators or just sequences.
Sequence objects are special single-row tables created with [sql-createsequence](#sql-createsequence).
Sequence objects are commonly used to generate unique identifiers
for rows of a table.  The sequence functions, listed in [functions-sequence-table](#functions-sequence-table), provide simple, multiuser-safe
methods for obtaining successive sequence values from sequence
objects.

| Function                         Description |
| --- |
| `nextval` ( `regclass` )         bigint                         Advances the sequence object to its next value and returns that value.         This is done atomically: even if multiple sessions         execute `nextval` concurrently, each will safely         receive a distinct sequence value.         If the sequence object has been created with default parameters,         successive `nextval` calls will return successive         values beginning with 1.  Other behaviors can be obtained by using         appropriate parameters in the [sql-createsequence](#sql-createsequence)         command.                        This function requires `USAGE`         or `UPDATE` privilege on the sequence. |
| `setval` ( `regclass`, `bigint` , `boolean`  )         bigint                         Sets the sequence object's current value, and optionally         its `is_called` flag.  The two-parameter         form sets the sequence's `last_value` field to the         specified value and sets its `is_called` field to         `true`, meaning that the next         `nextval` will advance the sequence before         returning a value.  The value that will be reported         by `currval` is also set to the specified value.         In the three-parameter form, `is_called` can be set         to either `true`         or `false`.  `true` has the same         effect as the two-parameter form. If it is set         to `false`, the next `nextval`         will return exactly the specified value, and sequence advancement         commences with the following `nextval`.         Furthermore, the value reported by `currval` is not         changed in this case.  For example,  ``` SELECT setval('myseq', 42);           Next `nextval` will return 43 SELECT setval('myseq', 42, true);     Same as above SELECT setval('myseq', 42, false);    Next `nextval` will return 42 ```          The result returned by `setval` is just the value of its         second argument.                         This function requires `UPDATE` privilege on the         sequence. |
| `currval` ( `regclass` )         bigint                         Returns the value most recently obtained         by `nextval` for this sequence in the current         session.  (An error is reported if `nextval` has         never been called for this sequence in this session.)  Because this is         returning a session-local value, it gives a predictable answer whether         or not other sessions have executed `nextval` since         the current session did.                         This function requires `USAGE`         or `SELECT` privilege on the sequence. |
| `lastval` ()         bigint                         Returns the value most recently returned by         `nextval` in the current session. This function is         identical to `currval`, except that instead         of taking the sequence name as an argument it refers to whichever         sequence `nextval` was most recently applied to         in the current session. It is an error to call         `lastval` if `nextval`         has not yet been called in the current session.                         This function requires `USAGE`         or `SELECT` privilege on the last used sequence. |

> **Caution:**

> To avoid blocking concurrent transactions that obtain numbers from
> the same sequence, the value obtained by `nextval`
> is not reclaimed for re-use if the calling transaction later aborts.
> This means that transaction aborts or database crashes can result in
> gaps in the sequence of assigned values.  That can happen without a
> transaction abort, too.  For example an `INSERT` with
> an `ON CONFLICT` clause will compute the to-be-inserted
> tuple, including doing any required `nextval`
> calls, before detecting any conflict that would cause it to follow
> the `ON CONFLICT` rule instead.
> Thus, PostgreSQL sequence
> objects *cannot be used to obtain "gapless"
> sequences*.
>

>

> Likewise, sequence state changes made by `setval`
> are immediately visible to other transactions, and are not undone if
> the calling transaction rolls back.
>

>

> If the database cluster crashes before committing a transaction
> containing a `nextval`
> or `setval` call, the sequence state change might
> not have made its way to persistent storage, so that it is uncertain
> whether the sequence will have its original or updated state after the
> cluster restarts.  This is harmless for usage of the sequence within
> the database, since other effects of uncommitted transactions will not
> be visible either.  However, if you wish to use a sequence value for
> persistent outside-the-database purposes, make sure that the
> `nextval` call has been committed before doing so.
>

The sequence to be operated on by a sequence function is specified by
a `regclass` argument, which is simply the OID of the sequence in the
`pg_class` system catalog.  You do not have to look up the
OID by hand, however, since the `regclass` data type's input
converter will do the work for you.  See [datatype-oid](#datatype-oid)
for details.

## Conditional Expressions

This section describes the SQL-compliant conditional expressions
available in PostgreSQL.

> **Tip:**

> If your needs go beyond the capabilities of these conditional
> expressions, you might want to consider writing a server-side function
> in a more expressive programming language.
>

> **Note:**

> Although `COALESCE`, `GREATEST`, and
> `LEAST` are syntactically similar to functions, they are
> not ordinary functions, and thus cannot be used with explicit
> `VARIADIC` array arguments.
>

### `CASE`

The SQL `CASE` expression is a
generic conditional expression, similar to if/else statements in
other programming languages:

```
CASE WHEN `condition` THEN `result`
WHEN ...
ELSE `result`
END
```

`CASE` clauses can be used wherever
an expression is valid.  Each `condition` is an
expression that returns a `boolean` result.  If the condition's
result is true, the value of the `CASE` expression is the
`result` that follows the condition, and the
remainder of the `CASE` expression is not processed.  If the
condition's result is not true, any subsequent `WHEN` clauses
are examined in the same manner.  If no `WHEN`
`condition` yields true, the value of the
`CASE` expression is the `result` of the
`ELSE` clause.  If the `ELSE` clause is
omitted and no condition is true, the result is null.

An example:

```
SELECT * FROM test;

a
---
1
2
3

SELECT a,
CASE WHEN a=1 THEN 'one'
WHEN a=2 THEN 'two'
ELSE 'other'
END
FROM test;

a | case
---+-------
1 | one
2 | two
3 | other
```

The data types of all the `result`
expressions must be convertible to a single output type.
See [typeconv-union-case](#typeconv-union-case) for more details.

There is a "simple" form of `CASE` expression
that is a variant of the general form above:

```
CASE `expression`
WHEN `value` THEN `result`
WHEN ...
ELSE `result`
END
```

The first
`expression` is computed, then compared to
each of the `value` expressions in the
`WHEN` clauses until one is found that is equal to it.  If
no match is found, the `result` of the
`ELSE` clause (or a null value) is returned.  This is similar
to the `switch` statement in C.

The example above can be written using the simple
`CASE` syntax:

```
SELECT a,
CASE a WHEN 1 THEN 'one'
WHEN 2 THEN 'two'
ELSE 'other'
END
FROM test;

a | case
---+-------
1 | one
2 | two
3 | other
```

A `CASE` expression does not evaluate any subexpressions
that are not needed to determine the result.  For example, this is a
possible way of avoiding a division-by-zero failure:

```
SELECT ... WHERE CASE WHEN x <> 0 THEN y/x > 1.5 ELSE false END;
```

> **Note:**

> As described in [syntax-express-eval](#syntax-express-eval), there are various
> situations in which subexpressions of an expression are evaluated at
> different times, so that the principle that "`CASE`
> evaluates only necessary subexpressions" is not ironclad.  For
> example a constant `1/0` subexpression will usually result in
> a division-by-zero failure at planning time, even if it's within
> a `CASE` arm that would never be entered at run time.
>

### `COALESCE`

```
`COALESCE`(`value` , ...)
```

The `COALESCE` function returns the first of its
arguments that is not null.  Null is returned only if all arguments
are null.  It is often used to substitute a default value for
null values when data is retrieved for display, for example:

```
SELECT COALESCE(description, short_description, '(none)') ...
```

This returns `description` if it is not null, otherwise
`short_description` if it is not null, otherwise `(none)`.

The arguments must all be convertible to a common data type, which
will be the type of the result (see
[typeconv-union-case](#typeconv-union-case) for details).

Like a `CASE` expression, `COALESCE` only
evaluates the arguments that are needed to determine the result;
that is, arguments to the right of the first non-null argument are
not evaluated.  This SQL-standard function provides capabilities similar
to `NVL` and `IFNULL`, which are used in some other
database systems.

### `NULLIF`

```
`NULLIF`(`value1`, `value2`)
```

The `NULLIF` function returns a null value if
`value1` equals `value2`;
otherwise it returns `value1`.
This can be used to perform the inverse operation of the
`COALESCE` example given above:

```
SELECT NULLIF(value, '(none)') ...
```

In this example, if `value` is `(none)`,
null is returned, otherwise the value of `value`
is returned.

The two arguments must be of comparable types.
To be specific, they are compared exactly as if you had
written ``value1`
= `value2``, so there must be a
suitable `=` operator available.

The result has the same type as the first argument — but there is
a subtlety.  What is actually returned is the first argument of the
implied `=` operator, and in some cases that will have
been promoted to match the second argument's type.  For
example, `NULLIF(1, 2.2)` yields `numeric`,
because there is no `integer` `=`
`numeric` operator,
only `numeric` `=` `numeric`.

### `GREATEST` and `LEAST`

```
`GREATEST`(`value` , ...)
```

```
`LEAST`(`value` , ...)
```

The `GREATEST` and `LEAST` functions select the
largest or smallest value from a list of any number of expressions.
The expressions must all be convertible to a common data type, which
will be the type of the result
(see [typeconv-union-case](#typeconv-union-case) for details).

NULL values in the argument list are ignored.  The result will be NULL
only if all the expressions evaluate to NULL.  (This is a deviation from
the SQL standard.  According to the standard, the return value is NULL if
any argument is NULL.  Some other databases behave this way.)

## Array Functions and Operators

[array-operators-table](#array-operators-table) shows the specialized operators
available for array types.
In addition to those, the usual comparison operators shown in [functions-comparison-op-table](#functions-comparison-op-table) are available for
arrays.  The comparison operators compare the array contents
element-by-element, using the default B-tree comparison function for
the element data type, and sort based on the first difference.
In multidimensional arrays the elements are visited in row-major order
(last subscript varies most rapidly).
If the contents of two arrays are equal but the dimensionality is
different, the first difference in the dimensionality information
determines the sort order.

| Operator                         Description                         Example(s) |
| --- |
| `anyarray` `@>` `anyarray`         boolean                         Does the first array contain the second, that is, does each element         appearing in the second array equal some element of the first array?         (Duplicates are not treated specially,         thus `ARRAY[1]` and `ARRAY[1,1]` are         each considered to contain the other.)                         `ARRAY[1,4,3] @> ARRAY[3,1,3]`         t |
| `anyarray` `` `anyrange`         boolean                         Does the first range contain the second?                         `int4range(2,4) @> int4range(2,3)`         t |
| `anyrange` `@>` `anyelement`         boolean                         Does the range contain the element?                         `'[2011-01-01,2011-03-01)'::tsrange @> '2011-01-10'::timestamp`         t |
| `anyrange` `>` `anyrange`         boolean                         Is the first range strictly right of the second?                         `int8range(50,60) >> int8range(20,30)`         t |
| `anyrange` `&` `anyrange`         boolean                         Does the first range not extend to the left of the second?                         `int8range(7,20) &> int8range(5,10)`         t |
| `anyrange` `-|-` `anyrange`         boolean                         Are the ranges adjacent?                         `numrange(1.1,2.2) -|- numrange(2.2,3.3)`         t |
| `anyrange` `+` `anyrange`         anyrange                         Computes the union of the ranges.  The ranges must overlap or be         adjacent, so that the union is a single range (but         see `range_merge()`).                         `numrange(5,15) + numrange(10,20)`         [5,20) |
| `anyrange` `*` `anyrange`         anyrange                         Computes the intersection of the ranges.                         `int8range(5,15) * int8range(10,20)`         [10,15) |
| `anyrange` `-` `anyrange`         anyrange                         Computes the difference of the ranges.  The second range must not be         contained in the first in such a way that the difference would not be         a single range.                         `int8range(5,15) - int8range(10,20)`         [5,10) |

| Operator                         Description                         Example(s) |
| --- |
| `anymultirange` `@>` `anymultirange`         boolean                         Does the first multirange contain the second?                         `'{[2,4)}'::int4multirange @> '{[2,3)}'::int4multirange`         t |
| `anymultirange` `@>` `anyrange`         boolean                         Does the multirange contain the range?                         `'{[2,4)}'::int4multirange @> int4range(2,3)`         t |
| `anymultirange` `@>` `anyelement`         boolean                         Does the multirange contain the element?                         `'{[2011-01-01,2011-03-01)}'::tsmultirange @> '2011-01-10'::timestamp`         t |
| `anyrange` `@>` `anymultirange`         boolean                         Does the range contain the multirange?                         `'[2,4)'::int4range @> '{[2,3)}'::int4multirange`         t |
| `anymultirange` `>` `anymultirange`         boolean                         Is the first multirange strictly right of the second?                         `'{[50,60)}'::int8multirange >> '{[20,30)}'::int8multirange`         t |
| `anymultirange` `>>` `anyrange`         boolean                         Is the multirange strictly right of the range?                         `'{[50,60)}'::int8multirange >> int8range(20,30)`         t |
| `anyrange` `>>` `anymultirange`         boolean                         Is the range strictly right of the multirange?                         `int8range(50,60) >> '{[20,30)}'::int8multirange`         t |
| `anymultirange` `&` `anymultirange`         boolean                         Does the first multirange not extend to the left of the second?                         `'{[7,20)}'::int8multirange &> '{[5,10)}'::int8multirange`         t |
| `anymultirange` `&>` `anyrange`         boolean                         Does the multirange not extend to the left of the range?                         `'{[7,20)}'::int8multirange &> int8range(5,10)`         t |
| `anyrange` `&>` `anymultirange`         boolean                         Does the range not extend to the left of the multirange?                         `int8range(7,20) &> '{[5,10)}'::int8multirange`         t |
| `anymultirange` `-|-` `anymultirange`         boolean                         Are the multiranges adjacent?                         `'{[1.1,2.2)}'::nummultirange -|- '{[2.2,3.3)}'::nummultirange`         t |
| `anymultirange` `-|-` `anyrange`         boolean                         Is the multirange adjacent to the range?                         `'{[1.1,2.2)}'::nummultirange -|- numrange(2.2,3.3)`         t |
| `anyrange` `-|-` `anymultirange`         boolean                         Is the range adjacent to the multirange?                         `numrange(1.1,2.2) -|- '{[2.2,3.3)}'::nummultirange`         t |
| `anymultirange` `+` `anymultirange`         anymultirange                         Computes the union of the multiranges.  The multiranges need not overlap         or be adjacent.                         `'{[5,10)}'::nummultirange + '{[15,20)}'::nummultirange`         {[5,10), [15,20)} |
| `anymultirange` `*` `anymultirange`         anymultirange                         Computes the intersection of the multiranges.                         `'{[5,15)}'::int8multirange * '{[10,20)}'::int8multirange`         {[10,15)} |
| `anymultirange` `-` `anymultirange`         anymultirange                         Computes the difference of the multiranges.                         `'{[5,20)}'::int8multirange - '{[10,15)}'::int8multirange`         {[5,10), [15,20)} |

The left-of/right-of/adjacent operators always return false when an empty
range or multirange is involved; that is, an empty range is not considered to
be either before or after any other range.

Elsewhere empty ranges and multiranges are treated as the additive identity:
anything unioned with an empty value is itself. Anything minus an empty
value is itself. An empty multirange has exactly the same points as an empty
range. Every range contains the empty range. Every multirange contains as many
empty ranges as you like.

The range union and difference operators will fail if the resulting range would
need to contain two disjoint sub-ranges, as such a range cannot be
represented. There are separate operators for union and difference that take
multirange parameters and return a multirange, and they do not fail even if
their arguments are disjoint. So if you need a union or difference operation
for ranges that may be disjoint, you can avoid errors by first casting your
ranges to multiranges.

[range-functions-table](#range-functions-table) shows the functions
available for use with range types.
[multirange-functions-table](#multirange-functions-table) shows the functions
available for use with multirange types.

| Function                         Description                         Example(s) |
| --- |
| `lower` ( `anyrange` )         anyelement                         Extracts the lower bound of the range (`NULL` if the         range is empty or has no lower bound).                         `lower(numrange(1.1,2.2))`         1.1 |
| `upper` ( `anyrange` )         anyelement                         Extracts the upper bound of the range (`NULL` if the         range is empty or has no upper bound).                         `upper(numrange(1.1,2.2))`         2.2 |
| `isempty` ( `anyrange` )         boolean                         Is the range empty?                         `isempty(numrange(1.1,2.2))`         f |
| `lower_inc` ( `anyrange` )         boolean                         Is the range's lower bound inclusive?                         `lower_inc(numrange(1.1,2.2))`         t |
| `upper_inc` ( `anyrange` )         boolean                         Is the range's upper bound inclusive?                         `upper_inc(numrange(1.1,2.2))`         f |
| `lower_inf` ( `anyrange` )         boolean                         Does the range have no lower bound?  (A lower bound of         `-Infinity` returns false.)                         `lower_inf('(,)'::daterange)`         t |
| `upper_inf` ( `anyrange` )         boolean                         Does the range have no upper bound?  (An upper bound of         `Infinity` returns false.)                         `upper_inf('(,)'::daterange)`         t |
| `range_merge` ( `anyrange`, `anyrange` )         anyrange                         Computes the smallest range that includes both of the given ranges.                         `range_merge('[1,2)'::int4range, '[3,4)'::int4range)`         [1,4) |

| Function                         Description                         Example(s) |
| --- |
| `lower` ( `anymultirange` )         anyelement                         Extracts the lower bound of the multirange (`NULL` if the         multirange is empty has no lower bound).                         `lower('{[1.1,2.2)}'::nummultirange)`         1.1 |
| `upper` ( `anymultirange` )         anyelement                         Extracts the upper bound of the multirange (`NULL` if the         multirange is empty or has no upper bound).                         `upper('{[1.1,2.2)}'::nummultirange)`         2.2 |
| `isempty` ( `anymultirange` )         boolean                         Is the multirange empty?                         `isempty('{[1.1,2.2)}'::nummultirange)`         f |
| `lower_inc` ( `anymultirange` )         boolean                         Is the multirange's lower bound inclusive?                         `lower_inc('{[1.1,2.2)}'::nummultirange)`         t |
| `upper_inc` ( `anymultirange` )         boolean                         Is the multirange's upper bound inclusive?                         `upper_inc('{[1.1,2.2)}'::nummultirange)`         f |
| `lower_inf` ( `anymultirange` )         boolean                         Does the multirange have no lower bound?  (A lower bound of         `-Infinity` returns false.)                         `lower_inf('{(,)}'::datemultirange)`         t |
| `upper_inf` ( `anymultirange` )         boolean                         Does the multirange have no upper bound?  (An upper bound of         `Infinity` returns false.)                         `upper_inf('{(,)}'::datemultirange)`         t |
| `range_merge` ( `anymultirange` )         anyrange                         Computes the smallest range that includes the entire multirange.                         `range_merge('{[1,2), [3,4)}'::int4multirange)`         [1,4) |
| `multirange` ( `anyrange` )         anymultirange                         Returns a multirange containing just the given range.                         `multirange('[1,2)'::int4range)`         {[1,2)} |
| `unnest` ( `anymultirange` )         setof anyrange                         Expands a multirange into a set of ranges.         The ranges are read out in storage order (ascending).                         `unnest('{[1,2), [3,4)}'::int4multirange)`           ``` [1,2)  [3,4) ``` |

The `lower_inc`, `upper_inc`,
`lower_inf`, and `upper_inf`
functions all return false for an empty range or multirange.

## Aggregate Functions

*Aggregate functions* compute a single result
from a set of input values.  The built-in general-purpose aggregate
functions are listed in [functions-aggregate-table](#functions-aggregate-table)
while statistical aggregates are in [functions-aggregate-statistics-table](#functions-aggregate-statistics-table).
The built-in within-group ordered-set aggregate functions
are listed in [functions-orderedset-table](#functions-orderedset-table)
while the built-in within-group hypothetical-set ones are in [functions-hypothetical-table](#functions-hypothetical-table).  Grouping operations,
which are closely related to aggregate functions, are listed in
[functions-grouping-table](#functions-grouping-table).
The special syntax considerations for aggregate
functions are explained in [syntax-aggregates](#syntax-aggregates).
Consult [tutorial-agg](#tutorial-agg) for additional introductory
information.

Aggregate functions that support *Partial Mode*
are eligible to participate in various optimizations, such as parallel
aggregation.

| Function                         Description | Partial Mode |
| --- | --- |
| `any_value` ( `anyelement` )         `same as input type`                         Returns an arbitrary value from the non-null input values. | Yes |
| `array_agg` ( `anynonarray` )         anyarray                         Collects all the input values, including nulls, into an array. | Yes |
| `array_agg` ( `anyarray` )         anyarray                         Concatenates all the input arrays into an array of one higher         dimension.  (The inputs must all have the same dimensionality, and         cannot be empty or null.) | Yes |
| `avg` ( `smallint` )         numeric                         `avg` ( `integer` )         numeric                         `avg` ( `bigint` )         numeric                         `avg` ( `numeric` )         numeric                         `avg` ( `real` )         double precision                         `avg` ( `double precision` )         double precision                         `avg` ( `interval` )         interval                         Computes the average (arithmetic mean) of all the non-null input         values. | Yes |
| `bit_and` ( `smallint` )         smallint                         `bit_and` ( `integer` )         integer                         `bit_and` ( `bigint` )         bigint                         `bit_and` ( `bit` )         bit                         Computes the bitwise AND of all non-null input values. | Yes |
| `bit_or` ( `smallint` )         smallint                         `bit_or` ( `integer` )         integer                         `bit_or` ( `bigint` )         bigint                         `bit_or` ( `bit` )         bit                         Computes the bitwise OR of all non-null input values. | Yes |
| `bit_xor` ( `smallint` )         smallint                         `bit_xor` ( `integer` )         integer                         `bit_xor` ( `bigint` )         bigint                         `bit_xor` ( `bit` )         bit                         Computes the bitwise exclusive OR of all non-null input values.         Can be useful as a checksum for an unordered set of values. | Yes |
| `bool_and` ( `boolean` )         boolean                         Returns true if all non-null input values are true, otherwise false. | Yes |
| `bool_or` ( `boolean` )         boolean                         Returns true if any non-null input value is true, otherwise false. | Yes |
| `count` ( `*` )         bigint                         Computes the number of input rows. | Yes |
| `count` ( `"any"` )         bigint                         Computes the number of input rows in which the input value is not         null. | Yes |
| `every` ( `boolean` )         boolean                         This is the SQL standard's equivalent to `bool_and`. | Yes |
| `json_agg` ( `anyelement` )         json                                  `jsonb_agg` ( `anyelement` )         jsonb                         Collects all the input values, including nulls, into a JSON array.         Values are converted to JSON as per `to_json`         or `to_jsonb`. | No |
| `json_agg_strict` ( `anyelement` )         json                                  `jsonb_agg_strict` ( `anyelement` )         jsonb                         Collects all the input values, skipping nulls, into a JSON array.         Values are converted to JSON as per `to_json`         or `to_jsonb`. | No |
| `json_arrayagg` (          `value_expression`           `ORDER BY` `sort_expression`           { `NULL` | `ABSENT` } `ON NULL`           `RETURNING` `data_type`  `FORMAT JSON`  `ENCODING UTF8`   )                         Behaves in the same way as `json_array`         but as an aggregate function so it only takes one         `value_expression` parameter.         If `ABSENT ON NULL` is specified, any NULL         values are omitted.         If `ORDER BY` is specified, the elements will         appear in the array in that order rather than in the input order.                         `SELECT json_arrayagg(v) FROM (VALUES(2),(1)) t(v)`         [2, 1] | No |
| `json_objectagg` (           { `key_expression` { `VALUE` | ':' } `value_expression` }            { `NULL` | `ABSENT` } `ON NULL`           { `WITH` | `WITHOUT` } `UNIQUE`  `KEYS`            `RETURNING` `data_type`  `FORMAT JSON`  `ENCODING UTF8`   )                            Behaves like `json_object`, but as an          aggregate function, so it only takes one          `key_expression` and one          `value_expression` parameter.                            `SELECT json_objectagg(k:v) FROM (VALUES ('a'::text,current_date),('b',current_date + 1)) AS t(k,v)`          { "a" : "2022-05-10", "b" : "2022-05-11" } | No |
| `json_object_agg` ( key          `"any"`, value          `"any"` )         json                                  `jsonb_object_agg` ( key          `"any"`, value          `"any"` )         jsonb                         Collects all the key/value pairs into a JSON object.  Key arguments         are coerced to text; value arguments are converted as per         `to_json` or `to_jsonb`.         Values can be null, but keys cannot. | No |
| `json_object_agg_strict` (          key `"any"`,          value `"any"` )         json                                  `jsonb_object_agg_strict` (          key `"any"`,          value `"any"` )         jsonb                         Collects all the key/value pairs into a JSON object.  Key arguments         are coerced to text; value arguments are converted as per         `to_json` or `to_jsonb`.         The key can not be null. If the         value is null then the entry is skipped, | No |
| `json_object_agg_unique` (          key `"any"`,          value `"any"` )         json                                  `jsonb_object_agg_unique` (          key `"any"`,          value `"any"` )         jsonb                         Collects all the key/value pairs into a JSON object.  Key arguments         are coerced to text; value arguments are converted as per         `to_json` or `to_jsonb`.         Values can be null, but keys cannot.         If there is a duplicate key an error is thrown. | No |
| `json_object_agg_unique_strict` (          key `"any"`,          value `"any"` )         json                                  `jsonb_object_agg_unique_strict` (          key `"any"`,          value `"any"` )         jsonb                         Collects all the key/value pairs into a JSON object.  Key arguments         are coerced to text; value arguments are converted as per         `to_json` or `to_jsonb`.         The key can not be null. If the         value is null then the entry is skipped.         If there is a duplicate key an error is thrown. | No |
| `max` ( `see text` )         `same as input type`                         Computes the maximum of the non-null input         values.  Available for any numeric, string, date/time, or enum type,         as well as `inet`, `interval`,         `money`, `oid`, `pg_lsn`,         `tid`, `xid8`,         and arrays of any of these types. | Yes |
| `min` ( `see text` )         `same as input type`                         Computes the minimum of the non-null input         values.  Available for any numeric, string, date/time, or enum type,         as well as `inet`, `interval`,         `money`, `oid`, `pg_lsn`,         `tid`, `xid8`,         and arrays of any of these types. | Yes |
| `range_agg` ( value          `anyrange` )         anymultirange                         `range_agg` ( value          `anymultirange` )         anymultirange                         Computes the union of the non-null input values. | No |
| `range_intersect_agg` ( value          `anyrange` )         anyrange                         `range_intersect_agg` ( value          `anymultirange` )         anymultirange                         Computes the intersection of the non-null input values. | No |
| `string_agg` ( value          `text`, delimiter `text` )         text                         `string_agg` ( value          `bytea`, delimiter `bytea` )         bytea                         Concatenates the non-null input values into a string.  Each value         after the first is preceded by the         corresponding delimiter (if it's not null). | Yes |
| `sum` ( `smallint` )         bigint                         `sum` ( `integer` )         bigint                         `sum` ( `bigint` )         numeric                         `sum` ( `numeric` )         numeric                         `sum` ( `real` )         real                         `sum` ( `double precision` )         double precision                         `sum` ( `interval` )         interval                         `sum` ( `money` )         money                         Computes the sum of the non-null input values. | Yes |
| `xmlagg` ( `xml` )         xml                         Concatenates the non-null XML input values (see         [functions-xml-xmlagg](#functions-xml-xmlagg)). | No |

It should be noted that except for `count`,
these functions return a null value when no rows are selected.  In
particular, `sum` of no rows returns null, not
zero as one might expect, and `array_agg`
returns null rather than an empty array when there are no input
rows.  The `coalesce` function can be used to
substitute zero or an empty array for null when necessary.

The aggregate functions `array_agg`,
`json_agg`, `jsonb_agg`,
`json_agg_strict`, `jsonb_agg_strict`,
`json_object_agg`, `jsonb_object_agg`,
`json_object_agg_strict`, `jsonb_object_agg_strict`,
`json_object_agg_unique`, `jsonb_object_agg_unique`,
`json_object_agg_unique_strict`,
`jsonb_object_agg_unique_strict`,
`string_agg`,
and `xmlagg`, as well as similar user-defined
aggregate functions, produce meaningfully different result values
depending on the order of the input values.  This ordering is
unspecified by default, but can be controlled by writing an
`ORDER BY` clause within the aggregate call, as shown in
[syntax-aggregates](#syntax-aggregates).
Alternatively, supplying the input values from a sorted subquery
will usually work.  For example:

```

SELECT xmlagg(x) FROM (SELECT x FROM test ORDER BY y DESC) AS tab;

```

Beware that this approach can fail if the outer query level contains
additional processing, such as a join, because that might cause the
subquery's output to be reordered before the aggregate is computed.

> **Note:**

> The boolean aggregates `bool_and` and
> `bool_or` correspond to the standard SQL aggregates
> `every` and `any` or
> `some`.
> PostgreSQL
> supports `every`, but not `any`
> or `some`, because there is an ambiguity built into
> the standard syntax:
> ```
> SELECT b1 = ANY((SELECT b2 FROM t2 ...)) FROM t1 ...;
> ```
> Here `ANY` can be considered either as introducing
> a subquery, or as being an aggregate function, if the subquery
> returns one row with a Boolean value.
> Thus the standard name cannot be given to these aggregates.
>

> **Note:**

> Users accustomed to working with other SQL database management
> systems might be disappointed by the performance of the
> `count` aggregate when it is applied to the
> entire table. A query like:
> ```
> SELECT count(*) FROM sometable;
> ```
> will require effort proportional to the size of the table:
> PostgreSQL will need to scan either the
> entire table or the entirety of an index that includes all rows in
> the table.
>

[functions-aggregate-statistics-table](#functions-aggregate-statistics-table) shows
aggregate functions typically used in statistical analysis.
(These are separated out merely to avoid cluttering the listing
of more-commonly-used aggregates.)  Functions shown as
accepting `numeric_type` are available for all
the types `smallint`, `integer`,
`bigint`, `numeric`, `real`,
and `double precision`.
Where the description mentions

N, it means the
number of input rows for which all the input expressions are non-null.
In all cases, null is returned if the computation is meaningless,
for example when
N is zero.

| Function                         Description | Partial Mode |
| --- | --- |
| `corr` ( Y `double precision`, X `double precision` )         double precision                         Computes the correlation coefficient. | Yes |
| `covar_pop` ( Y `double precision`, X `double precision` )         double precision                         Computes the population covariance. | Yes |
| `covar_samp` ( Y `double precision`, X `double precision` )         double precision                         Computes the sample covariance. | Yes |
| `regr_avgx` ( Y `double precision`, X `double precision` )         double precision                         Computes the average of the independent variable,         `sum(X)/N`. | Yes |
| `regr_avgy` ( Y `double precision`, X `double precision` )         double precision                         Computes the average of the dependent variable,         `sum(Y)/N`. | Yes |
| `regr_count` ( Y `double precision`, X `double precision` )         bigint                         Computes the number of rows in which both inputs are non-null. | Yes |
| `regr_intercept` ( Y `double precision`, X `double precision` )         double precision                         Computes the y-intercept of the least-squares-fit linear equation         determined by the         (X, Y) pairs. | Yes |
| `regr_r2` ( Y `double precision`, X `double precision` )         double precision                         Computes the square of the correlation coefficient. | Yes |
| `regr_slope` ( Y `double precision`, X `double precision` )         double precision                         Computes the slope of the least-squares-fit linear equation determined         by the (X, Y)         pairs. | Yes |
| `regr_sxx` ( Y `double precision`, X `double precision` )         double precision                         Computes the "sum of squares" of the independent         variable,         `sum(X^2) - sum(X)^2/N`. | Yes |
| `regr_sxy` ( Y `double precision`, X `double precision` )         double precision                         Computes the "sum of products" of independent times         dependent variables,         `sum(X*Y) - sum(X) * sum(Y)/N`. | Yes |
| `regr_syy` ( Y `double precision`, X `double precision` )         double precision                         Computes the "sum of squares" of the dependent         variable,         `sum(Y^2) - sum(Y)^2/N`. | Yes |
| `stddev` ( `numeric_type` )          `double precision`         for `real` or `double precision`,         otherwise `numeric`                         This is a historical alias for `stddev_samp`. | Yes |
| `stddev_pop` ( `numeric_type` )          `double precision`         for `real` or `double precision`,         otherwise `numeric`                         Computes the population standard deviation of the input values. | Yes |
| `stddev_samp` ( `numeric_type` )          `double precision`         for `real` or `double precision`,         otherwise `numeric`                         Computes the sample standard deviation of the input values. | Yes |
| `variance` ( `numeric_type` )          `double precision`         for `real` or `double precision`,         otherwise `numeric`                         This is a historical alias for `var_samp`. | Yes |
| `var_pop` ( `numeric_type` )          `double precision`         for `real` or `double precision`,         otherwise `numeric`                         Computes the population variance of the input values (square of the         population standard deviation). | Yes |
| `var_samp` ( `numeric_type` )          `double precision`         for `real` or `double precision`,         otherwise `numeric`                         Computes the sample variance of the input values (square of the sample         standard deviation). | Yes |

[functions-orderedset-table](#functions-orderedset-table) shows some
aggregate functions that use the *ordered-set aggregate*
syntax.  These functions are sometimes referred to as "inverse
distribution" functions.  Their aggregated input is introduced by
`ORDER BY`, and they may also take a *direct
argument* that is not aggregated, but is computed only once.
All these functions ignore null values in their aggregated input.
For those that take a
fraction parameter, the
fraction value must be between 0 and 1; an error is thrown if not.
However, a null
fraction value simply produces a
null result.

| Function                         Description | Partial Mode |
| --- | --- |
| `mode` () `WITHIN GROUP` ( `ORDER BY` `anyelement` )         anyelement                         Computes the *mode*, the most frequent         value of the aggregated argument (arbitrarily choosing the first one         if there are multiple equally-frequent values).  The aggregated         argument must be of a sortable type. | No |
| `percentile_cont` ( fraction `double precision` ) `WITHIN GROUP` ( `ORDER BY` `double precision` )         double precision                         `percentile_cont` ( fraction `double precision` ) `WITHIN GROUP` ( `ORDER BY` `interval` )         interval                         Computes the *continuous percentile*, a value         corresponding to the specified fraction         within the ordered set of aggregated argument values.  This will         interpolate between adjacent input items if needed. | No |
| `percentile_cont` ( fractions `double precision[]` ) `WITHIN GROUP` ( `ORDER BY` `double precision` )         double precision[]                         `percentile_cont` ( fractions `double precision[]` ) `WITHIN GROUP` ( `ORDER BY` `interval` )         interval[]                         Computes multiple continuous percentiles.  The result is an array of         the same dimensions as the fractions         parameter, with each non-null element replaced by the (possibly         interpolated) value corresponding to that percentile. | No |
| `percentile_disc` ( fraction `double precision` ) `WITHIN GROUP` ( `ORDER BY` `anyelement` )         anyelement                         Computes the *discrete percentile*, the first         value within the ordered set of aggregated argument values whose         position in the ordering equals or exceeds the         specified fraction.  The aggregated         argument must be of a sortable type. | No |
| `percentile_disc` ( fractions `double precision[]` ) `WITHIN GROUP` ( `ORDER BY` `anyelement` )         anyarray                         Computes multiple discrete percentiles.  The result is an array of the         same dimensions as the fractions parameter,         with each non-null element replaced by the input value corresponding         to that percentile.         The aggregated argument must be of a sortable type. | No |

Each of the "hypothetical-set" aggregates listed in
[functions-hypothetical-table](#functions-hypothetical-table) is associated with a
window function of the same name defined in
[functions-window](#functions-window).  In each case, the aggregate's result
is the value that the associated window function would have
returned for the "hypothetical" row constructed from
`args`, if such a row had been added to the sorted
group of rows represented by the `sorted_args`.
For each of these functions, the list of direct arguments
given in `args` must match the number and types of
the aggregated arguments given in `sorted_args`.
Unlike most built-in aggregates, these aggregates are not strict, that is
they do not drop input rows containing nulls.  Null values sort according
to the rule specified in the `ORDER BY` clause.

| Function                         Description | Partial Mode |
| --- | --- |
| `rank` ( `args` ) `WITHIN GROUP` ( `ORDER BY` `sorted_args` )         bigint                         Computes the rank of the hypothetical row, with gaps; that is, the row         number of the first row in its peer group. | No |
| `dense_rank` ( `args` ) `WITHIN GROUP` ( `ORDER BY` `sorted_args` )         bigint                         Computes the rank of the hypothetical row, without gaps; this function         effectively counts peer groups. | No |
| `percent_rank` ( `args` ) `WITHIN GROUP` ( `ORDER BY` `sorted_args` )         double precision                         Computes the relative rank of the hypothetical row, that is         (`rank` - 1) / (total rows - 1).         The value thus ranges from 0 to 1 inclusive. | No |
| `cume_dist` ( `args` ) `WITHIN GROUP` ( `ORDER BY` `sorted_args` )         double precision                         Computes the cumulative distribution, that is (number of rows         preceding or peers with hypothetical row) / (total rows).  The value         thus ranges from 1/N to 1. | No |

| Function                         Description |
| --- |
| `GROUPING` ( `group_by_expression(s)` )         integer                         Returns a bit mask indicating which `GROUP BY`         expressions are not included in the current grouping set.         Bits are assigned with the rightmost argument corresponding to the         least-significant bit; each bit is 0 if the corresponding expression         is included in the grouping criteria of the grouping set generating         the current result row, and 1 if it is not included. |

The grouping operations shown in
[functions-grouping-table](#functions-grouping-table) are used in conjunction with
grouping sets (see [queries-grouping-sets](#queries-grouping-sets)) to distinguish
result rows.  The arguments to the `GROUPING` function
are not actually evaluated, but they must exactly match expressions given
in the `GROUP BY` clause of the associated query level.
For example:

```
=> SELECT * FROM items_sold;
make  | model | sales
-------+-------+-------
Foo   | GT    |  10
Foo   | Tour  |  20
Bar   | City  |  15
Bar   | Sport |  5
(4 rows)

=> SELECT make, model, GROUPING(make,model), sum(sales) FROM items_sold GROUP BY ROLLUP(make,model);
make  | model | grouping | sum
-------+-------+----------+-----
Foo   | GT    |        0 | 10
Foo   | Tour  |        0 | 20
Bar   | City  |        0 | 15
Bar   | Sport |        0 | 5
Foo   |       |        1 | 30
Bar   |       |        1 | 20
|       |        3 | 50
(7 rows)
```

Here, the `grouping` value `0` in the
first four rows shows that those have been grouped normally, over both the
grouping columns.  The value `1` indicates
that `model` was not grouped by in the next-to-last two
rows, and the value `3` indicates that
neither `make` nor `model` was grouped
by in the last row (which therefore is an aggregate over all the input
rows).

## Window Functions

*Window functions* provide the ability to perform
calculations across sets of rows that are related to the current query
row.  See [tutorial-window](#tutorial-window) for an introduction to this
feature, and [syntax-window-functions](#syntax-window-functions) for syntax
details.

The built-in window functions are listed in
[functions-window-table](#functions-window-table).  Note that these functions
*must* be invoked using window function syntax, i.e., an
`OVER` clause is required.

In addition to these functions, any built-in or user-defined
ordinary aggregate (i.e., not ordered-set or hypothetical-set aggregates)
can be used as a window function; see
[functions-aggregate](#functions-aggregate) for a list of the built-in aggregates.
Aggregate functions act as window functions only when an `OVER`
clause follows the call; otherwise they act as plain aggregates
and return a single row for the entire set.

| Function                         Description |
| --- |
| `row_number` ()         bigint                         Returns the number of the current row within its partition, counting         from 1. |
| `rank` ()         bigint                         Returns the rank of the current row, with gaps; that is,         the `row_number` of the first row in its peer         group. |
| `dense_rank` ()         bigint                         Returns the rank of the current row, without gaps; this function         effectively counts peer groups. |
| `percent_rank` ()         double precision                         Returns the relative rank of the current row, that is         (`rank` - 1) / (total partition rows - 1).         The value thus ranges from 0 to 1 inclusive. |
| `cume_dist` ()         double precision                         Returns the cumulative distribution, that is (number of partition rows         preceding or peers with current row) / (total partition rows).         The value thus ranges from 1/N to 1. |
| `ntile` ( num_buckets `integer` )         integer                         Returns an integer ranging from 1 to the argument value, dividing the         partition as equally as possible. |
| `lag` ( value `anycompatible`           , offset `integer`           , default `anycompatible`  )         anycompatible                         Returns value evaluated at         the row that is offset         rows before the current row within the partition; if there is no such         row, instead returns default         (which must be of a type compatible with         value).         Both offset and         default are evaluated         with respect to the current row.  If omitted,         offset defaults to 1 and         default to `NULL`. |
| `lead` ( value `anycompatible`           , offset `integer`           , default `anycompatible`  )         anycompatible                         Returns value evaluated at         the row that is offset         rows after the current row within the partition; if there is no such         row, instead returns default         (which must be of a type compatible with         value).         Both offset and         default are evaluated         with respect to the current row.  If omitted,         offset defaults to 1 and         default to `NULL`. |
| `first_value` ( value `anyelement` )         anyelement                         Returns value evaluated         at the row that is the first row of the window frame. |
| `last_value` ( value `anyelement` )         anyelement                         Returns value evaluated         at the row that is the last row of the window frame. |
| `nth_value` ( value `anyelement`, n `integer` )         anyelement                         Returns value evaluated         at the row that is the n'th         row of the window frame (counting from 1);         returns `NULL` if there is no such row. |

All of the functions listed in
[functions-window-table](#functions-window-table) depend on the sort ordering
specified by the `ORDER BY` clause of the associated window
definition.  Rows that are not distinct when considering only the
`ORDER BY` columns are said to be *peers*.
The four ranking functions (including `cume_dist`) are
defined so that they give the same answer for all rows of a peer group.

Note that `first_value`, `last_value`, and
`nth_value` consider only the rows within the "window
frame", which by default contains the rows from the start of the
partition through the last peer of the current row.  This is
likely to give unhelpful results for `last_value` and
sometimes also `nth_value`.  You can redefine the frame by
adding a suitable frame specification (`RANGE`,
`ROWS` or `GROUPS`) to
the `OVER` clause.
See [syntax-window-functions](#syntax-window-functions) for more information
about frame specifications.

When an aggregate function is used as a window function, it aggregates
over the rows within the current row's window frame.
An aggregate used with `ORDER BY` and the default window frame
definition produces a "running sum" type of behavior, which may or
may not be what's wanted.  To obtain
aggregation over the whole partition, omit `ORDER BY` or use
`ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING`.
Other frame specifications can be used to obtain other effects.

> **Note:**

> The SQL standard defines a `RESPECT NULLS` or
> `IGNORE NULLS` option for `lead`, `lag`,
> `first_value`, `last_value`, and
> `nth_value`.  This is not implemented in
> PostgreSQL: the behavior is always the
> same as the standard's default, namely `RESPECT NULLS`.
> Likewise, the standard's `FROM FIRST` or `FROM LAST`
> option for `nth_value` is not implemented: only the
> default `FROM FIRST` behavior is supported.  (You can achieve
> the result of `FROM LAST` by reversing the `ORDER BY`
> ordering.)
>

## Subquery Expressions

This section describes the SQL-compliant subquery
expressions available in PostgreSQL.
All of the expression forms documented in this section return
Boolean (true/false) results.

### `EXISTS`

```
EXISTS (`subquery`)
```

The argument of `EXISTS` is an arbitrary `SELECT` statement,
or *subquery*.  The
subquery is evaluated to determine whether it returns any rows.
If it returns at least one row, the result of `EXISTS` is
"true"; if the subquery returns no rows, the result of `EXISTS`
is "false".

The subquery can refer to variables from the surrounding query,
which will act as constants during any one evaluation of the subquery.

The subquery will generally only be executed long enough to determine
whether at least one row is returned, not all the way to completion.
It is unwise to write a subquery that has side effects (such as
calling sequence functions); whether the side effects occur
might be unpredictable.

Since the result depends only on whether any rows are returned,
and not on the contents of those rows, the output list of the
subquery is normally unimportant.  A common coding convention is
to write all `EXISTS` tests in the form
`EXISTS(SELECT 1 WHERE ...)`.  There are exceptions to
this rule however, such as subqueries that use `INTERSECT`.

This simple example is like an inner join on `col2`, but
it produces at most one output row for each `tab1` row,
even if there are several matching `tab2` rows:

```
SELECT col1
FROM tab1
WHERE EXISTS (SELECT 1 FROM tab2 WHERE col2 = tab1.col2);
```

### `IN`

```
`expression` IN (`subquery`)
```

The right-hand side is a parenthesized
subquery, which must return exactly one column.  The left-hand expression
is evaluated and compared to each row of the subquery result.
The result of `IN` is "true" if any equal subquery row is found.
The result is "false" if no equal row is found (including the
case where the subquery returns no rows).

Note that if the left-hand expression yields null, or if there are
no equal right-hand values and at least one right-hand row yields
null, the result of the `IN` construct will be null, not false.
This is in accordance with SQL's normal rules for Boolean combinations
of null values.

As with `EXISTS`, it's unwise to assume that the subquery will
be evaluated completely.

```
`row_constructor` IN (`subquery`)
```

The left-hand side of this form of `IN` is a row constructor,
as described in [sql-syntax-row-constructors](#sql-syntax-row-constructors).
The right-hand side is a parenthesized
subquery, which must return exactly as many columns as there are
expressions in the left-hand row.  The left-hand expressions are
evaluated and compared row-wise to each row of the subquery result.
The result of `IN` is "true" if any equal subquery row is found.
The result is "false" if no equal row is found (including the
case where the subquery returns no rows).

As usual, null values in the rows are combined per
the normal rules of SQL Boolean expressions.  Two rows are considered
equal if all their corresponding members are non-null and equal; the rows
are unequal if any corresponding members are non-null and unequal;
otherwise the result of that row comparison is unknown (null).
If all the per-row results are either unequal or null, with at least one
null, then the result of `IN` is null.

### `NOT IN`

```
`expression` NOT IN (`subquery`)
```

The right-hand side is a parenthesized
subquery, which must return exactly one column.  The left-hand expression
is evaluated and compared to each row of the subquery result.
The result of `NOT IN` is "true" if only unequal subquery rows
are found (including the case where the subquery returns no rows).
The result is "false" if any equal row is found.

Note that if the left-hand expression yields null, or if there are
no equal right-hand values and at least one right-hand row yields
null, the result of the `NOT IN` construct will be null, not true.
This is in accordance with SQL's normal rules for Boolean combinations
of null values.

As with `EXISTS`, it's unwise to assume that the subquery will
be evaluated completely.

```
`row_constructor` NOT IN (`subquery`)
```

The left-hand side of this form of `NOT IN` is a row constructor,
as described in [sql-syntax-row-constructors](#sql-syntax-row-constructors).
The right-hand side is a parenthesized
subquery, which must return exactly as many columns as there are
expressions in the left-hand row.  The left-hand expressions are
evaluated and compared row-wise to each row of the subquery result.
The result of `NOT IN` is "true" if only unequal subquery rows
are found (including the case where the subquery returns no rows).
The result is "false" if any equal row is found.

As usual, null values in the rows are combined per
the normal rules of SQL Boolean expressions.  Two rows are considered
equal if all their corresponding members are non-null and equal; the rows
are unequal if any corresponding members are non-null and unequal;
otherwise the result of that row comparison is unknown (null).
If all the per-row results are either unequal or null, with at least one
null, then the result of `NOT IN` is null.

### `ANY`/`SOME`

```
`expression` `operator` ANY (`subquery`)
`expression` `operator` SOME (`subquery`)
```

The right-hand side is a parenthesized
subquery, which must return exactly one column.  The left-hand expression
is evaluated and compared to each row of the subquery result using the
given `operator`, which must yield a Boolean
result.
The result of `ANY` is "true" if any true result is obtained.
The result is "false" if no true result is found (including the
case where the subquery returns no rows).

`SOME` is a synonym for `ANY`.
`IN` is equivalent to `= ANY`.

Note that if there are no successes and at least one right-hand row yields
null for the operator's result, the result of the `ANY` construct
will be null, not false.
This is in accordance with SQL's normal rules for Boolean combinations
of null values.

As with `EXISTS`, it's unwise to assume that the subquery will
be evaluated completely.

```
`row_constructor` `operator` ANY (`subquery`)
`row_constructor` `operator` SOME (`subquery`)
```

The left-hand side of this form of `ANY` is a row constructor,
as described in [sql-syntax-row-constructors](#sql-syntax-row-constructors).
The right-hand side is a parenthesized
subquery, which must return exactly as many columns as there are
expressions in the left-hand row.  The left-hand expressions are
evaluated and compared row-wise to each row of the subquery result,
using the given `operator`.
The result of `ANY` is "true" if the comparison
returns true for any subquery row.
The result is "false" if the comparison returns false for every
subquery row (including the case where the subquery returns no
rows).
The result is NULL if no comparison with a subquery row returns true,
and at least one comparison returns NULL.

See [row-wise-comparison](#row-wise-comparison) for details about the meaning
of a row constructor comparison.

### `ALL`

```
`expression` `operator` ALL (`subquery`)
```

The right-hand side is a parenthesized
subquery, which must return exactly one column.  The left-hand expression
is evaluated and compared to each row of the subquery result using the
given `operator`, which must yield a Boolean
result.
The result of `ALL` is "true" if all rows yield true
(including the case where the subquery returns no rows).
The result is "false" if any false result is found.
The result is NULL if no comparison with a subquery row returns false,
and at least one comparison returns NULL.

`NOT IN` is equivalent to `<> ALL`.

As with `EXISTS`, it's unwise to assume that the subquery will
be evaluated completely.

```
`row_constructor` `operator` ALL (`subquery`)
```

The left-hand side of this form of `ALL` is a row constructor,
as described in [sql-syntax-row-constructors](#sql-syntax-row-constructors).
The right-hand side is a parenthesized
subquery, which must return exactly as many columns as there are
expressions in the left-hand row.  The left-hand expressions are
evaluated and compared row-wise to each row of the subquery result,
using the given `operator`.
The result of `ALL` is "true" if the comparison
returns true for all subquery rows (including the
case where the subquery returns no rows).
The result is "false" if the comparison returns false for any
subquery row.
The result is NULL if no comparison with a subquery row returns false,
and at least one comparison returns NULL.

See [row-wise-comparison](#row-wise-comparison) for details about the meaning
of a row constructor comparison.

### Single-Row Comparison

```
`row_constructor` `operator` (`subquery`)
```

The left-hand side is a row constructor,
as described in [sql-syntax-row-constructors](#sql-syntax-row-constructors).
The right-hand side is a parenthesized subquery, which must return exactly
as many columns as there are expressions in the left-hand row. Furthermore,
the subquery cannot return more than one row.  (If it returns zero rows,
the result is taken to be null.)  The left-hand side is evaluated and
compared row-wise to the single subquery result row.

See [row-wise-comparison](#row-wise-comparison) for details about the meaning
of a row constructor comparison.

## Row and Array Comparisons

This section describes several specialized constructs for making
multiple comparisons between groups of values.  These forms are
syntactically related to the subquery forms of the previous section,
but do not involve subqueries.
The forms involving array subexpressions are
PostgreSQL extensions; the rest are
SQL-compliant.
All of the expression forms documented in this section return
Boolean (true/false) results.

### `IN`

```
`expression` IN (`value` , ...)
```

The right-hand side is a parenthesized list
of expressions.  The result is "true" if the left-hand expression's
result is equal to any of the right-hand expressions.  This is a shorthand
notation for

```
`expression` = `value1`
OR
`expression` = `value2`
OR
...
```

Note that if the left-hand expression yields null, or if there are
no equal right-hand values and at least one right-hand expression yields
null, the result of the `IN` construct will be null, not false.
This is in accordance with SQL's normal rules for Boolean combinations
of null values.

### `NOT IN`

```
`expression` NOT IN (`value` , ...)
```

The right-hand side is a parenthesized list
of expressions.  The result is "true" if the left-hand expression's
result is unequal to all of the right-hand expressions.  This is a shorthand
notation for

```
`expression` <> `value1`
AND
`expression` <> `value2`
AND
...
```

Note that if the left-hand expression yields null, or if there are
no equal right-hand values and at least one right-hand expression yields
null, the result of the `NOT IN` construct will be null, not true
as one might naively expect.
This is in accordance with SQL's normal rules for Boolean combinations
of null values.

> **Tip:**

> `x NOT IN y` is equivalent to `NOT (x IN y)` in all
> cases.  However, null values are much more likely to trip up the novice when
> working with `NOT IN` than when working with `IN`.
> It is best to express your condition positively if possible.
>

### `ANY`/`SOME` (array)

```
`expression` `operator` ANY (`array expression`)
`expression` `operator` SOME (`array expression`)
```

The right-hand side is a parenthesized expression, which must yield an
array value.
The left-hand expression
is evaluated and compared to each element of the array using the
given `operator`, which must yield a Boolean
result.
The result of `ANY` is "true" if any true result is obtained.
The result is "false" if no true result is found (including the
case where the array has zero elements).

If the array expression yields a null array, the result of
`ANY` will be null.  If the left-hand expression yields null,
the result of `ANY` is ordinarily null (though a non-strict
comparison operator could possibly yield a different result).
Also, if the right-hand array contains any null elements and no true
comparison result is obtained, the result of `ANY`
will be null, not false (again, assuming a strict comparison operator).
This is in accordance with SQL's normal rules for Boolean combinations
of null values.

`SOME` is a synonym for `ANY`.

### `ALL` (array)

```
`expression` `operator` ALL (`array expression`)
```

The right-hand side is a parenthesized expression, which must yield an
array value.
The left-hand expression
is evaluated and compared to each element of the array using the
given `operator`, which must yield a Boolean
result.
The result of `ALL` is "true" if all comparisons yield true
(including the case where the array has zero elements).
The result is "false" if any false result is found.

If the array expression yields a null array, the result of
`ALL` will be null.  If the left-hand expression yields null,
the result of `ALL` is ordinarily null (though a non-strict
comparison operator could possibly yield a different result).
Also, if the right-hand array contains any null elements and no false
comparison result is obtained, the result of `ALL`
will be null, not true (again, assuming a strict comparison operator).
This is in accordance with SQL's normal rules for Boolean combinations
of null values.

### Row Constructor Comparison

```
`row_constructor` `operator` `row_constructor`
```

Each side is a row constructor,
as described in [sql-syntax-row-constructors](#sql-syntax-row-constructors).
The two row constructors must have the same number of fields.
The given `operator` is applied to each pair
of corresponding fields.  (Since the fields could be of different
types, this means that a different specific operator could be selected
for each pair.)
All the selected operators must be members of some B-tree operator
class, or be the negator of an `=` member of a B-tree
operator class, meaning that row constructor comparison is only
possible when the `operator` is
`=`,
`<>`,
`<`,
`<=`,
`>`, or
`>=`,
or has semantics similar to one of these.

The `=` and `<>` cases work slightly differently
from the others.  Two rows are considered
equal if all their corresponding members are non-null and equal; the rows
are unequal if any corresponding members are non-null and unequal;
otherwise the result of the row comparison is unknown (null).

For the `<`, `<=`, `>` and
`>=` cases, the row elements are compared left-to-right,
stopping as soon as an unequal or null pair of elements is found.
If either of this pair of elements is null, the result of the
row comparison is unknown (null); otherwise comparison of this pair
of elements determines the result.  For example,
`ROW(1,2,NULL) < ROW(1,3,0)`
yields true, not null, because the third pair of elements are not
considered.

```
`row_constructor` IS DISTINCT FROM `row_constructor`
```

This construct is similar to a `<>` row comparison,
but it does not yield null for null inputs.  Instead, any null value is
considered unequal to (distinct from) any non-null value, and any two
nulls are considered equal (not distinct).  Thus the result will
either be true or false, never null.

```
`row_constructor` IS NOT DISTINCT FROM `row_constructor`
```

This construct is similar to a `=` row comparison,
but it does not yield null for null inputs.  Instead, any null value is
considered unequal to (distinct from) any non-null value, and any two
nulls are considered equal (not distinct).  Thus the result will always
be either true or false, never null.

### Composite Type Comparison

```
`record` `operator` `record`
```

The SQL specification requires row-wise comparison to return NULL if the
result depends on comparing two NULL values or a NULL and a non-NULL.
PostgreSQL does this only when comparing the
results of two row constructors (as in
[row-wise-comparison](#row-wise-comparison)) or comparing a row constructor
to the output of a subquery (as in [functions-subquery](#functions-subquery)).
In other contexts where two composite-type values are compared, two
NULL field values are considered equal, and a NULL is considered larger
than a non-NULL.  This is necessary in order to have consistent sorting
and indexing behavior for composite types.

Each side is evaluated and they are compared row-wise.  Composite type
comparisons are allowed when the `operator` is
`=`,
`<>`,
`<`,
`<=`,
`>` or
`>=`,
or has semantics similar to one of these.  (To be specific, an operator
can be a row comparison operator if it is a member of a B-tree operator
class, or is the negator of the `=` member of a B-tree operator
class.)  The default behavior of the above operators is the same as for
`IS [ NOT ] DISTINCT FROM` for row constructors (see
[row-wise-comparison](#row-wise-comparison)).

To support matching of rows which include elements without a default
B-tree operator class, the following operators are defined for composite
type comparison:
`*=`,
`*<>`,
`*<`,
`*<=`,
`*>`, and
`*>=`.
These operators compare the internal binary representation of the two
rows.  Two rows might have a different binary representation even
though comparisons of the two rows with the equality operator is true.
The ordering of rows under these comparison operators is deterministic
but not otherwise meaningful.  These operators are used internally
for materialized views and might be useful for other specialized
purposes such as replication and B-Tree deduplication (see [btree-deduplication](#btree-deduplication)).  They are not intended to be
generally useful for writing queries, though.

## Set Returning Functions

This section describes functions that possibly return more than one row.
The most widely used functions in this class are series generating
functions, as detailed in [functions-srf-series](#functions-srf-series) and
[functions-srf-subscripts](#functions-srf-subscripts).  Other, more specialized
set-returning functions are described elsewhere in this manual.
See [queries-tablefunctions](#queries-tablefunctions) for ways to combine multiple
set-returning functions.

| Function                         Description |
| --- |
| `generate_series` ( start `integer`, stop `integer` , step `integer`  )         setof integer                         `generate_series` ( start `bigint`, stop `bigint` , step `bigint`  )         setof bigint                         `generate_series` ( start `numeric`, stop `numeric` , step `numeric`  )         setof numeric                         Generates a series of values from start         to stop, with a step size         of step.  step         defaults to 1. |
| `generate_series` ( start `timestamp`, stop `timestamp`, step `interval` )         setof timestamp                         `generate_series` ( start `timestamp with time zone`, stop `timestamp with time zone`, step `interval` , timezone `text`  )         setof timestamp with time zone                         Generates a series of values from start         to stop, with a step size         of step.         In the timezone-aware form, times of day and daylight-savings         adjustments are computed according to the time zone named by         the timezone argument, or the current         [guc-timezone](#guc-timezone) setting if that is omitted. |

When
step is positive, zero rows are returned if

start is greater than
stop.
Conversely, when
step is negative, zero rows are
returned if
start is less than
stop.
Zero rows are also returned if any input is `NULL`.
It is an error
for
step to be zero. Some examples follow:

```
SELECT * FROM generate_series(2,4);
generate_series
-----------------
2
3
4
(3 rows)

SELECT * FROM generate_series(5,1,-2);
generate_series
-----------------
5
3
1
(3 rows)

SELECT * FROM generate_series(4,3);
generate_series
-----------------
(0 rows)

SELECT generate_series(1.1, 4, 1.3);
generate_series
-----------------
1.1
2.4
3.7
(3 rows)

-- this example relies on the date-plus-integer operator:
SELECT current_date + s.a AS dates FROM generate_series(0,14,7) AS s(a);
dates
------------
2004-02-05
2004-02-12
2004-02-19
(3 rows)

SELECT * FROM generate_series('2008-03-01 00:00'::timestamp,
'2008-03-04 12:00', '10 hours');
generate_series
---------------------
2008-03-01 00:00:00
2008-03-01 10:00:00
2008-03-01 20:00:00
2008-03-02 06:00:00
2008-03-02 16:00:00
2008-03-03 02:00:00
2008-03-03 12:00:00
2008-03-03 22:00:00
2008-03-04 08:00:00
(9 rows)

-- this example assumes that TimeZone is set to UTC; note the DST transition:
SELECT * FROM generate_series('2001-10-22 00:00 -04:00'::timestamptz,
'2001-11-01 00:00 -05:00'::timestamptz,
'1 day'::interval, 'America/New_York');
generate_series
------------------------
2001-10-22 04:00:00+00
2001-10-23 04:00:00+00
2001-10-24 04:00:00+00
2001-10-25 04:00:00+00
2001-10-26 04:00:00+00
2001-10-27 04:00:00+00
2001-10-28 04:00:00+00
2001-10-29 05:00:00+00
2001-10-30 05:00:00+00
2001-10-31 05:00:00+00
2001-11-01 05:00:00+00
(11 rows)
```

| Function                         Description |
| --- |
| `generate_subscripts` ( array `anyarray`, dim `integer` )         setof integer                         Generates a series comprising the valid subscripts of         the dim'th dimension of the given array. |
| `generate_subscripts` ( array `anyarray`, dim `integer`,  reverse `boolean` )         setof integer                         Generates a series comprising the valid subscripts of         the dim'th dimension of the given array.         When reverse is true, returns the series in         reverse order. |

`generate_subscripts` is a convenience function that generates
the set of valid subscripts for the specified dimension of the given
array.
Zero rows are returned for arrays that do not have the requested dimension,
or if any input is `NULL`.
Some examples follow:

```
-- basic usage:
SELECT generate_subscripts('{NULL,1,NULL,2}'::int[], 1) AS s;
s
---
1
2
3
4
(4 rows)

-- presenting an array, the subscript and the subscripted
-- value requires a subquery:
SELECT * FROM arrays;
a
--------------------
{-1,-2}
{100,200,300}
(2 rows)

SELECT a AS array, s AS subscript, a[s] AS value
FROM (SELECT generate_subscripts(a, 1) AS s, a FROM arrays) foo;
array     | subscript | value
---------------+-----------+-------
{-1,-2}       |         1 |    -1
{-1,-2}       |         2 |    -2
{100,200,300} |         1 |   100
{100,200,300} |         2 |   200
{100,200,300} |         3 |   300
(5 rows)

-- unnest a 2D array:
CREATE OR REPLACE FUNCTION unnest2(anyarray)
RETURNS SETOF anyelement AS $$
select $1[i][j]
from generate_subscripts($1,1) g1(i),
generate_subscripts($1,2) g2(j);
$$ LANGUAGE sql IMMUTABLE;
CREATE FUNCTION
SELECT * FROM unnest2(ARRAY[[1,2],[3,4]]);
unnest2
---------
1
2
3
4
(4 rows)
```

When a function in the `FROM` clause is suffixed
by `WITH ORDINALITY`, a `bigint` column is
appended to the function's output column(s), which starts from 1 and
increments by 1 for each row of the function's output.
This is most useful in the case of set returning
functions such as `unnest()`.

```
-- set returning function WITH ORDINALITY:
SELECT * FROM pg_ls_dir('.') WITH ORDINALITY AS t(ls,n);
ls        | n
-----------------+----
pg_serial       |  1
pg_twophase     |  2
postmaster.opts |  3
pg_notify       |  4
postgresql.conf |  5
pg_tblspc       |  6
logfile         |  7
base            |  8
postmaster.pid  |  9
pg_ident.conf   | 10
global          | 11
pg_xact         | 12
pg_snapshots    | 13
pg_multixact    | 14
PG_VERSION      | 15
pg_wal          | 16
pg_hba.conf     | 17
pg_stat_tmp     | 18
pg_subtrans     | 19
(19 rows)
```

## Trigger Functions

While many uses of triggers involve user-written trigger functions,
PostgreSQL provides a few built-in trigger
functions that can be used directly in user-defined triggers.  These
are summarized in [builtin-triggers-table](#builtin-triggers-table).
(Additional built-in trigger functions exist, which implement foreign
key constraints and deferred index constraints.  Those are not documented
here since users need not use them directly.)

For more information about creating triggers, see
[sql-createtrigger](#sql-createtrigger).

| Function                         Description                         Example Usage |
| --- |
| `suppress_redundant_updates_trigger` ( )         trigger                         Suppresses do-nothing update operations.  See below for details.                         `CREATE TRIGGER ... suppress_redundant_updates_trigger()` |
| `tsvector_update_trigger` ( )         trigger                         Automatically updates a `tsvector` column from associated         plain-text document column(s).  The text search configuration to use         is specified by name as a trigger argument.  See         [textsearch-update-triggers](#textsearch-update-triggers) for details.                         `CREATE TRIGGER ... tsvector_update_trigger(tsvcol, 'pg_catalog.swedish', title, body)` |
| `tsvector_update_trigger_column` ( )         trigger                         Automatically updates a `tsvector` column from associated         plain-text document column(s).  The text search configuration to use         is taken from a `regconfig` column of the table.  See         [textsearch-update-triggers](#textsearch-update-triggers) for details.                         `CREATE TRIGGER ... tsvector_update_trigger_column(tsvcol, tsconfigcol, title, body)` |

The `suppress_redundant_updates_trigger` function,
when applied as a row-level `BEFORE UPDATE` trigger,
will prevent any update that does not actually change the data in the
row from taking place.  This overrides the normal behavior which always
performs a physical row update
regardless of whether or not the data has changed. (This normal behavior
makes updates run faster, since no checking is required, and is also
useful in certain cases.)

Ideally, you should avoid running updates that don't actually
change the data in the record. Redundant updates can cost considerable
unnecessary time, especially if there are lots of indexes to alter,
and space in dead rows that will eventually have to be vacuumed.
However, detecting such situations in client code is not
always easy, or even possible, and writing expressions to detect
them can be error-prone. An alternative is to use
`suppress_redundant_updates_trigger`, which will skip
updates that don't change the data. You should use this with care,
however. The trigger takes a small but non-trivial time for each record,
so if most of the records affected by updates do actually change,
use of this trigger will make updates run slower on average.

The `suppress_redundant_updates_trigger` function can be
added to a table like this:

```
CREATE TRIGGER z_min_update
BEFORE UPDATE ON tablename
FOR EACH ROW EXECUTE FUNCTION suppress_redundant_updates_trigger();
```

In most cases, you need to fire this trigger last for each row, so that
it does not override other triggers that might wish to alter the row.
Bearing in mind that triggers fire in name order, you would therefore
choose a trigger name that comes after the name of any other trigger
you might have on the table.  (Hence the "z" prefix in the
example.)

## Event Trigger Functions

PostgreSQL provides these helper functions
to retrieve information from event triggers.

For more information about event triggers,
see [event-triggers](#event-triggers).

### Capturing Changes at Command End

```
`pg_event_trigger_ddl_commands` () setof record
```

`pg_event_trigger_ddl_commands` returns a list of
DDL commands executed by each user action,
when invoked in a function attached to a
`ddl_command_end` event trigger.  If called in any other
context, an error is raised.
`pg_event_trigger_ddl_commands` returns one row for each
base command executed; some commands that are a single SQL sentence
may return more than one row.  This function returns the following
columns:

| Name | Type | Description |
| --- | --- | --- |
| `classid` | `oid` | OID of catalog the object belongs in |
| `objid` | `oid` | OID of the object itself |
| `objsubid` | `integer` | Sub-object ID (e.g., attribute number for a column) |
| `command_tag` | `text` | Command tag |
| `object_type` | `text` | Type of the object |
| `schema_name` | `text` | Name of the schema the object belongs in, if any; otherwise `NULL`.          No quoting is applied. |
| `object_identity` | `text` | Text rendering of the object identity, schema-qualified. Each          identifier included in the identity is quoted if necessary. |
| `in_extension` | `boolean` | True if the command is part of an extension script |
| `command` | `pg_ddl_command` | A complete representation of the command, in internal format.          This cannot be output directly, but it can be passed to other          functions to obtain different pieces of information about the          command. |

### Processing Objects Dropped by a DDL Command

```
`pg_event_trigger_dropped_objects` () setof record
```

`pg_event_trigger_dropped_objects` returns a list of all objects
dropped by the command in whose `sql_drop` event it is called.
If called in any other context, an error is raised.
This function returns the following columns:

| Name | Type | Description |
| --- | --- | --- |
| `classid` | `oid` | OID of catalog the object belonged in |
| `objid` | `oid` | OID of the object itself |
| `objsubid` | `integer` | Sub-object ID (e.g., attribute number for a column) |
| `original` | `boolean` | True if this was one of the root object(s) of the deletion |
| `normal` | `boolean` | True if there was a normal dependency relationship          in the dependency graph leading to this object |
| `is_temporary` | `boolean` | True if this was a temporary object |
| `object_type` | `text` | Type of the object |
| `schema_name` | `text` | Name of the schema the object belonged in, if any; otherwise `NULL`.          No quoting is applied. |
| `object_name` | `text` | Name of the object, if the combination of schema and name can be          used as a unique identifier for the object; otherwise `NULL`.          No quoting is applied, and name is never schema-qualified. |
| `object_identity` | `text` | Text rendering of the object identity, schema-qualified. Each          identifier included in the identity is quoted if necessary. |
| `address_names` | `text[]` | An array that, together with `object_type` and          `address_args`, can be used by          the `pg_get_object_address` function to          recreate the object address in a remote server containing an          identically named object of the same kind. |
| `address_args` | `text[]` | Complement for `address_names` |

The `pg_event_trigger_dropped_objects` function can be used
in an event trigger like this:

```
CREATE FUNCTION test_event_trigger_for_drops()
RETURNS event_trigger LANGUAGE plpgsql AS $$
DECLARE
obj record;
BEGIN
FOR obj IN SELECT * FROM pg_event_trigger_dropped_objects()
LOOP
RAISE NOTICE '% dropped object: % %.% %',
tg_tag,
obj.object_type,
obj.schema_name,
obj.object_name,
obj.object_identity;
END LOOP;
END;
$$;
CREATE EVENT TRIGGER test_event_trigger_for_drops
ON sql_drop
EXECUTE FUNCTION test_event_trigger_for_drops();
```

### Handling a Table Rewrite Event

The functions shown in
[functions-event-trigger-table-rewrite](#functions-event-trigger-table-rewrite)
provide information about a table for which a
`table_rewrite` event has just been called.
If called in any other context, an error is raised.

| Function                         Description |
| --- |
| `pg_event_trigger_table_rewrite_oid` ()         oid                         Returns the OID of the table about to be rewritten. |
| `pg_event_trigger_table_rewrite_reason` ()         integer                         Returns a code explaining the reason(s) for rewriting. The value is         a bitmap built from the following values: `1`         (the table has changed its persistence), `2`         (default value of a column has changed), `4`         (a column has a new data type) and `8`         (the table access method has changed). |

These functions can be used in an event trigger like this:

```
CREATE FUNCTION test_event_trigger_table_rewrite_oid()
RETURNS event_trigger
LANGUAGE plpgsql AS
$$
BEGIN
RAISE NOTICE 'rewriting table % for reason %',
pg_event_trigger_table_rewrite_oid()::regclass,
pg_event_trigger_table_rewrite_reason();
END;
$$;

CREATE EVENT TRIGGER test_table_rewrite_oid
ON table_rewrite
EXECUTE FUNCTION test_event_trigger_table_rewrite_oid();
```
