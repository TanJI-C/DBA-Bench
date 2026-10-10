# Numeric Types except floating output GUC; Character Types; Boolean Type; Enumerated Types; Geometric Types; Network Address Types; Bit String Types; Text Search Types; UUID Type; XML Type except XML option; JSON Types except indexing; Arrays except array_nulls; Composite Types; Range Types except indexing and constraints; Domain Types; Object Identifier Types; pg_lsn Type; Pseudo-Types

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/05_data_types.md`
- Source Title: `Data Types`
- Source Heading Path: `Data Types > Numeric Types except floating output GUC; Character Types; Boolean Type; Enumerated Types; Geometric Types; Network Address Types; Bit String Types; Text Search Types; UUID Type; XML Type except XML option; JSON Types except indexing; Arrays except array_nulls; Composite Types; Range Types except indexing and constraints; Domain Types; Object Identifier Types; pg_lsn Type; Pseudo-Types`
- Source Line Ranges: `564-683, 684-734, 1435-1465, 1466-1500, 1501-1623, 1624-1810, 1811-1976, 1977-2008, 2009-2032, 2033-2237, 2238-2280, 3861-4339, 4801-4835, 4836-5028, 5029-5050, 5051-5113`
- Chunk ID: `pg16_fact_0148_f4ad0b38fc`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ace9e8c605a63453bb8f107c96be27c83b6341398da4d2c1a18a38ed09df9516`

## Retrieval Guidance

- Use When: Need facts about data type behavior, literal syntax, or type semantics.
- Retrieval Keywords: data type, numeric, character, boolean, enum, geometric, inet, cidr, json, array, range, domain, oid, pg_lsn
- Follow-up Guidance: Use configuration records for type display/input parameters and solution records for index/constraint design.
- Classification Note: Reference material describing PostgreSQL data types, literals, input/output syntax, storage semantics, operators context, and type-specific behavior.

## Official Source Content

## Character Types

| Name | Description |
| --- | --- |
| `character varying(`n`)`, `varchar(`n`)` | variable-length with limit |
| `character(`n`)`, `char(`n`)`, `bpchar(`n`)` | fixed-length, blank-padded |
| `bpchar` | variable unlimited length, blank-trimmed |
| `text` | variable unlimited length |

[datatype-character-table](#datatype-character-table) shows the
general-purpose character types available in
PostgreSQL.

SQL defines two primary character types:
`character varying(`n`)` and
`character(`n`)`, where `n`
is a positive integer.  Both of these types can store strings up to
`n` characters (not bytes) in length.  An attempt to store a
longer string into a column of these types will result in an
error, unless the excess characters are all spaces, in which case
the string will be truncated to the maximum length. (This somewhat
bizarre exception is required by the SQL
standard.)
However, if one explicitly casts a value to `character
varying(`n`)` or
`character(`n`)`, then an over-length
value will be truncated to `n` characters without
raising an error. (This too is required by the
SQL standard.)
If the string to be stored is shorter than the declared
length, values of type `character` will be space-padded;
values of type `character varying` will simply store the
shorter
string.

In addition, PostgreSQL provides the
`text` type, which stores strings of any length.
Although the `text` type is not in the
SQL standard, several other SQL database
management systems have it as well.
`text` is PostgreSQL's native
string data type, in that most built-in functions operating on strings
are declared to take or return `text` not `character
varying`.  For many purposes, `character varying`
acts as though it were a [domain](#domains)
over `text`.

The type name `varchar` is an alias for `character
varying`, while `bpchar` (with length specifier) and
`char` are aliases for `character`.  The
`varchar` and `char` aliases are defined in the
SQL standard;  `bpchar` is a
PostgreSQL extension.

If specified, the length `n` must be greater
than zero and cannot exceed 10,485,760.  If `character
varying` (or `varchar`) is used without
length specifier, the type accepts strings of any length. If
`bpchar` lacks a length specifier, it also accepts strings
of any length, but trailing spaces are semantically insignificant.
If `character` (or `char`) lacks a specifier,
it is equivalent to `character(1)`.

Values of type `character` are physically padded
with spaces to the specified width `n`, and are
stored and displayed that way.  However, trailing spaces are treated as
semantically insignificant and disregarded when comparing two values
of type `character`.  In collations where whitespace
is significant, this behavior can produce unexpected results;
for example `SELECT 'a '::CHAR(2) collate "C" <
E'a\n'::CHAR(2)` returns true, even though `C`
locale would consider a space to be greater than a newline.
Trailing spaces are removed when converting a `character` value
to one of the other string types.  Note that trailing spaces
*are* semantically significant in
`character varying` and `text` values, and
when using pattern matching, that is `LIKE` and
regular expressions.

The characters that can be stored in any of these data types are
determined by the database character set, which is selected when
the database is created.  Regardless of the specific character set,
the character with code zero (sometimes called NUL) cannot be stored.
For more information refer to [multibyte](#multibyte).

The storage requirement for a short string (up to 126 bytes) is 1 byte
plus the actual string, which includes the space padding in the case of
`character`.  Longer strings have 4 bytes of overhead instead
of 1.  Long strings are compressed by the system automatically, so
the physical requirement on disk might be less. Very long values are also
stored in background tables so that they do not interfere with rapid
access to shorter column values. In any case, the longest
possible character string that can be stored is about 1 GB. (The
maximum value that will be allowed for `n` in the data
type declaration is less than that. It wouldn't be useful to
change this because with multibyte character encodings the number of
characters and bytes can be quite different. If you desire to
store long strings with no specific upper limit, use
`text` or `character varying` without a length
specifier, rather than making up an arbitrary length limit.)

> **Tip:**

> There is no performance difference among these three types,
> apart from increased storage space when using the blank-padded
> type, and a few extra CPU cycles to check the length when storing into
> a length-constrained column.  While
> `character(`n`)` has performance
> advantages in some other database systems, there is no such advantage in
> PostgreSQL; in fact
> `character(`n`)` is usually the slowest of
> the three because of its additional storage costs.  In most situations
> `text` or `character varying` should be used
> instead.
>

Refer to [sql-syntax-strings](#sql-syntax-strings) for information about
the syntax of string literals, and to [functions](#functions)
for information about available operators and functions.

## Using the Character Types

```
CREATE TABLE test1 (a character(4));
INSERT INTO test1 VALUES ('ok');
SELECT a, char_length(a) FROM test1; --

a   | char_length
------+-------------
ok   |           2

CREATE TABLE test2 (b varchar(5));
INSERT INTO test2 VALUES ('ok');
INSERT INTO test2 VALUES ('good      ');
INSERT INTO test2 VALUES ('too long');
ERROR:  value too long for type character varying(5)
INSERT INTO test2 VALUES ('too long'::varchar(5)); -- explicit truncation
SELECT b, char_length(b) FROM test2;

b   | char_length
-------+-------------
ok    |           2
good  |           5
too l |           5

```

The `char_length` function is discussed in
[functions-string](#functions-string).

There are two other fixed-length character types in
PostgreSQL, shown in [datatype-character-special-table](#datatype-character-special-table).
These are not intended for general-purpose use, only for use
in the internal system catalogs.
The `name` type is used to store identifiers. Its
length is currently defined as 64 bytes (63 usable characters plus
terminator) but should be referenced using the constant
`NAMEDATALEN` in `C` source code.
The length is set at compile time (and
is therefore adjustable for special uses); the default maximum
length might change in a future release. The type `"char"`
(note the quotes) is different from `char(1)` in that it
only uses one byte of storage, and therefore can store only a single
ASCII character. It is used in the system
catalogs as a simplistic enumeration type.

| Name | Storage Size | Description |
| --- | --- | --- |
| `"char"` | 1 byte | single-byte internal type |
| `name` | 64 bytes | internal type for object names |

## Boolean Type

PostgreSQL provides the
standard SQL type `boolean`;
see [datatype-boolean-table](#datatype-boolean-table).
The `boolean` type can have several states:
"true", "false", and a third state,
"unknown", which is represented by the
SQL null value.

| Name | Storage Size | Description |
| --- | --- | --- |
| `boolean` | 1 byte | state of true or false |

Boolean constants can be represented in SQL queries by the SQL
key words `TRUE`, `FALSE`,
and `NULL`.

The datatype input function for type `boolean` accepts these
string representations for the "true" state:

and these representations for the "false" state:

Unique prefixes of these strings are also accepted, for
example `t` or `n`.
Leading or trailing whitespace is ignored, and case does not matter.

The datatype output function for type `boolean` always emits
either `t` or `f`, as shown in
[datatype-boolean-example](#datatype-boolean-example).

## Using the `boolean` Type

```
CREATE TABLE test1 (a boolean, b text);
INSERT INTO test1 VALUES (TRUE, 'sic est');
INSERT INTO test1 VALUES (FALSE, 'non est');
SELECT * FROM test1;
a |    b
---+---------
t | sic est
f | non est

SELECT * FROM test1 WHERE a;
a |    b
---+---------
t | sic est
```

The key words `TRUE` and `FALSE` are
the preferred (SQL-compliant) method for writing
Boolean constants in SQL queries.  But you can also use the string
representations by following the generic string-literal constant syntax
described in [sql-syntax-constants-generic](#sql-syntax-constants-generic), for
example `'yes'::boolean`.

Note that the parser automatically understands
that `TRUE` and `FALSE` are of
type `boolean`, but this is not so
for `NULL` because that can have any type.
So in some contexts you might have to cast `NULL`
to `boolean` explicitly, for
example `NULL::boolean`.  Conversely, the cast can be
omitted from a string-literal Boolean value in contexts where the parser
can deduce that the literal must be of type `boolean`.

## Enumerated Types

Enumerated (enum) types are data types that
comprise a static, ordered set of values.
They are equivalent to the `enum`
types supported in a number of programming languages. An example of an enum
type might be the days of the week, or a set of status values for
a piece of data.

### Declaration of Enumerated Types

Enum types are created using the [sql-createtype](#sql-createtype) command,
for example:

```
CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');
```

Once created, the enum type can be used in table and function
definitions much like any other type:

```
CREATE TYPE mood AS ENUM ('sad', 'ok', 'happy');
CREATE TABLE person (
name text,
current_mood mood
);
INSERT INTO person VALUES ('Moe', 'happy');
SELECT * FROM person WHERE current_mood = 'happy';
name | current_mood
------+--------------
Moe  | happy
(1 row)
```

### Ordering

The ordering of the values in an enum type is the
order in which the values were listed when the type was created.
All standard comparison operators and related
aggregate functions are supported for enums.  For example:

```
INSERT INTO person VALUES ('Larry', 'sad');
INSERT INTO person VALUES ('Curly', 'ok');
SELECT * FROM person WHERE current_mood > 'sad';
name  | current_mood
-------+--------------
Moe   | happy
Curly | ok
(2 rows)

SELECT * FROM person WHERE current_mood > 'sad' ORDER BY current_mood;
name  | current_mood
-------+--------------
Curly | ok
Moe   | happy
(2 rows)

SELECT name
FROM person
WHERE current_mood = (SELECT MIN(current_mood) FROM person);
name
-------
Larry
(1 row)
```

### Type Safety

Each enumerated data type is separate and cannot
be compared with other enumerated types.  See this example:

```
CREATE TYPE happiness AS ENUM ('happy', 'very happy', 'ecstatic');
CREATE TABLE holidays (
num_weeks integer,
happiness happiness
);
INSERT INTO holidays(num_weeks,happiness) VALUES (4, 'happy');
INSERT INTO holidays(num_weeks,happiness) VALUES (6, 'very happy');
INSERT INTO holidays(num_weeks,happiness) VALUES (8, 'ecstatic');
INSERT INTO holidays(num_weeks,happiness) VALUES (2, 'sad');
ERROR:  invalid input value for enum happiness: "sad"
SELECT person.name, holidays.num_weeks FROM person, holidays
WHERE person.current_mood = holidays.happiness;
ERROR:  operator does not exist: mood = happiness
```

If you really need to do something like that, you can either
write a custom operator or add explicit casts to your query:

```
SELECT person.name, holidays.num_weeks FROM person, holidays
WHERE person.current_mood::text = holidays.happiness::text;
name | num_weeks
------+-----------
Moe  |         4
(1 row)
```

### Implementation Details

Enum labels are case sensitive, so
`'happy'` is not the same as `'HAPPY'`.
White space in the labels is significant too.

Although enum types are primarily intended for static sets of values,
there is support for adding new values to an existing enum type, and for
renaming values (see [sql-altertype](#sql-altertype)).  Existing values
cannot be removed from an enum type, nor can the sort ordering of such
values be changed, short of dropping and re-creating the enum type.

An enum value occupies four bytes on disk.  The length of an enum
value's textual label is limited by the `NAMEDATALEN`
setting compiled into PostgreSQL; in standard
builds this means at most 63 bytes.

The translations from internal enum values to textual labels are
kept in the system catalog
[`pg_enum`](#catalog-pg-enum).
Querying this catalog directly can be useful.

## Geometric Types

Geometric data types represent two-dimensional spatial
objects. [datatype-geo-table](#datatype-geo-table) shows the geometric
types available in PostgreSQL.

| Name | Storage Size | Description | Representation |
| --- | --- | --- | --- |
| `point` | 16 bytes | Point on a plane | (x,y) |
| `line` | 24 bytes | Infinite line | {A,B,C} |
| `lseg` | 32 bytes | Finite line segment | ((x1,y1),(x2,y2)) |
| `box` | 32 bytes | Rectangular box | ((x1,y1),(x2,y2)) |
| `path` | 16+16n bytes | Closed path (similar to polygon) | ((x1,y1),...) |
| `path` | 16+16n bytes | Open path | [(x1,y1),...] |
| `polygon` | 40+16n bytes | Polygon (similar to closed path) | ((x1,y1),...) |
| `circle` | 24 bytes | Circle |  (center point and radius) |

In all these types, the individual coordinates are stored as
`double precision` (`float8`) numbers.

A rich set of functions and operators is available to perform various geometric
operations such as scaling, translation, rotation, and determining
intersections.  They are explained in [functions-geometry](#functions-geometry).

### Points

Points are the fundamental two-dimensional building block for geometric
types.  Values of type `point` are specified using either of
the following syntaxes:

```
( `x` , `y` )
`x` , `y`
```

where `x` and `y` are the respective
coordinates, as floating-point numbers.

Points are output using the first syntax.

### Lines

Lines are represented by the linear
equation `A`x + `B`y + `C` = 0,
where `A` and `B` are not both zero.  Values
of type `line` are input and output in the following form:

```
{ `A`, `B`, `C` }
```

Alternatively, any of the following forms can be used for input:

```
[ ( `x1` , `y1` ) , ( `x2` , `y2` ) ]
( ( `x1` , `y1` ) , ( `x2` , `y2` ) )
( `x1` , `y1` ) , ( `x2` , `y2` )
`x1` , `y1`   ,   `x2` , `y2`
```

where
`(`x1`,`y1`)`
and
`(`x2`,`y2`)`
are two different points on the line.

### Line Segments

Line segments are represented by pairs of points that are the endpoints
of the segment.  Values of type `lseg` are specified using any
of the following syntaxes:

```
[ ( `x1` , `y1` ) , ( `x2` , `y2` ) ]
( ( `x1` , `y1` ) , ( `x2` , `y2` ) )
( `x1` , `y1` ) , ( `x2` , `y2` )
`x1` , `y1`   ,   `x2` , `y2`
```

where
`(`x1`,`y1`)`
and
`(`x2`,`y2`)`
are the end points of the line segment.

Line segments are output using the first syntax.

### Boxes

Boxes are represented by pairs of points that are opposite
corners of the box.
Values of type `box` are specified using any of the following
syntaxes:

```
( ( `x1` , `y1` ) , ( `x2` , `y2` ) )
( `x1` , `y1` ) , ( `x2` , `y2` )
`x1` , `y1`   ,   `x2` , `y2`
```

where
`(`x1`,`y1`)`
and
`(`x2`,`y2`)`
are any two opposite corners of the box.

Boxes are output using the second syntax.

Any two opposite corners can be supplied on input, but the values
will be reordered as needed to store the
upper right and lower left corners, in that order.

### Paths

Paths are represented by lists of connected points. Paths can be
*open*, where
the first and last points in the list are considered not connected, or
*closed*,
where the first and last points are considered connected.

Values of type `path` are specified using any of the following
syntaxes:

```
[ ( `x1` , `y1` ) , ... , ( `xn` , `yn` ) ]
( ( `x1` , `y1` ) , ... , ( `xn` , `yn` ) )
( `x1` , `y1` ) , ... , ( `xn` , `yn` )
( `x1` , `y1`   , ... ,   `xn` , `yn` )
`x1` , `y1`   , ... ,   `xn` , `yn`
```

where the points are the end points of the line segments
comprising the path.  Square brackets (`[]`) indicate
an open path, while parentheses (`()`) indicate a
closed path.  When the outermost parentheses are omitted, as
in the third through fifth syntaxes, a closed path is assumed.

Paths are output using the first or second syntax, as appropriate.

### Polygons

Polygons are represented by lists of points (the vertexes of the
polygon). Polygons are very similar to closed paths; the essential
semantic difference is that a polygon is considered to include the
area within it, while a path is not.

An important implementation difference between polygons and
paths is that the stored representation of a polygon includes its
smallest bounding box.  This speeds up certain search operations,
although computing the bounding box adds overhead while constructing
new polygons.

Values of type `polygon` are specified using any of the
following syntaxes:

```
( ( `x1` , `y1` ) , ... , ( `xn` , `yn` ) )
( `x1` , `y1` ) , ... , ( `xn` , `yn` )
( `x1` , `y1`   , ... ,   `xn` , `yn` )
`x1` , `y1`   , ... ,   `xn` , `yn`
```

where the points are the end points of the line segments
comprising the boundary of the polygon.

Polygons are output using the first syntax.

### Circles

Circles are represented by a center point and radius.
Values of type `circle` are specified using any of the
following syntaxes:

```

( ( `x` , `y` ) , `r` )
( `x` , `y` ) , `r`
`x` , `y`   , `r`
```

where
`(`x`,`y`)`
is the center point and `r` is the radius of the
circle.

Circles are output using the first syntax.

## Network Address Types

PostgreSQL offers data types to store IPv4, IPv6, and MAC
addresses, as shown in [datatype-net-types-table](#datatype-net-types-table).  It
is better to use these types instead of plain text types to store
network addresses, because
these types offer input error checking and specialized
operators and functions (see [functions-net](#functions-net)).

| Name | Storage Size | Description |
| --- | --- | --- |
| `cidr` | 7 or 19 bytes | IPv4 and IPv6 networks |
| `inet` | 7 or 19 bytes | IPv4 and IPv6 hosts and networks |
| `macaddr` | 6 bytes | MAC addresses |
| `macaddr8` | 8 bytes | MAC addresses (EUI-64 format) |

When sorting `inet` or `cidr` data types,
IPv4 addresses will always sort before IPv6 addresses, including
IPv4 addresses encapsulated or mapped to IPv6 addresses, such as
::10.2.3.4 or ::ffff:10.4.3.2.

### `inet`

The `inet` type holds an IPv4 or IPv6 host address, and
optionally its subnet, all in one field.
The subnet is represented by the number of network address bits
present in the host address (the
"netmask").  If the netmask is 32 and the address is IPv4,
then the value does not indicate a subnet, only a single host.
In IPv6, the address length is 128 bits, so 128 bits specify a
unique host address.  Note that if you
want to accept only networks, you should use the
`cidr` type rather than `inet`.

The input format for this type is
`address/y`
where
`address`
is an IPv4 or IPv6 address and
`y`
is the number of bits in the netmask.  If the
`/y`
portion is omitted, the
netmask is taken to be 32 for IPv4 or 128 for IPv6,
so the value represents
just a single host.  On display, the
`/y`
portion is suppressed if the netmask specifies a single host.

### `cidr`

The `cidr` type holds an IPv4 or IPv6 network specification.
Input and output formats follow Classless Internet Domain Routing
conventions.
The format for specifying networks is `address/y` where `address` is the network's lowest
address represented as an
IPv4 or IPv6 address, and `y` is the number of bits in the netmask.  If
`y` is omitted, it is calculated
using assumptions from the older classful network numbering system, except
it will be at least large enough to include all of the octets
written in the input.  It is an error to specify a network address
that has bits set to the right of the specified netmask.

[datatype-net-cidr-table](#datatype-net-cidr-table) shows some examples.

| `cidr` Input | `cidr` Output | ``abbrev(`cidr`)`` |
| --- | --- | --- |
| 192.168.100.128/25 | 192.168.100.128/25 | 192.168.100.128/25 |
| 192.168/24 | 192.168.0.0/24 | 192.168.0/24 |
| 192.168/25 | 192.168.0.0/25 | 192.168.0.0/25 |
| 192.168.1 | 192.168.1.0/24 | 192.168.1/24 |
| 192.168 | 192.168.0.0/24 | 192.168.0/24 |
| 128.1 | 128.1.0.0/16 | 128.1/16 |
| 128 | 128.0.0.0/16 | 128.0/16 |
| 128.1.2 | 128.1.2.0/24 | 128.1.2/24 |
| 10.1.2 | 10.1.2.0/24 | 10.1.2/24 |
| 10.1 | 10.1.0.0/16 | 10.1/16 |
| 10 | 10.0.0.0/8 | 10/8 |
| 10.1.2.3/32 | 10.1.2.3/32 | 10.1.2.3/32 |
| 2001:4f8:3:ba::/64 | 2001:4f8:3:ba::/64 | 2001:4f8:3:ba/64 |
| 2001:4f8:3:ba:2e0:81ff:fe22:d1f1/128 | 2001:4f8:3:ba:2e0:81ff:fe22:d1f1/128 | 2001:4f8:3:ba:2e0:81ff:fe22:d1f1/128 |
| ::ffff:1.2.3.0/120 | ::ffff:1.2.3.0/120 | ::ffff:1.2.3/120 |
| ::ffff:1.2.3.0/128 | ::ffff:1.2.3.0/128 | ::ffff:1.2.3.0/128 |

### `inet` vs. `cidr`

The essential difference between `inet` and `cidr`
data types is that `inet` accepts values with nonzero bits to
the right of the netmask, whereas `cidr` does not.  For
example, `192.168.0.1/24` is valid for `inet`
but not for `cidr`.

> **Tip:**

> If you do not like the output format for `inet` or
> `cidr` values, try the functions `host`,
> `text`, and `abbrev`.
>

### `macaddr`

The `macaddr` type stores MAC addresses, known for example
from Ethernet card hardware addresses (although MAC addresses are
used for other purposes as well).  Input is accepted in the
following formats:

These examples all specify the same address.  Upper and
lower case is accepted for the digits
`a` through `f`.  Output is always in the
first of the forms shown.

IEEE Standard 802-2001 specifies the second form shown (with hyphens)
as the canonical form for MAC addresses, and specifies the first
form (with colons) as used with bit-reversed, MSB-first notation, so that
08-00-2b-01-02-03 = 10:00:D4:80:40:C0.  This convention is widely
ignored nowadays, and it is relevant only for obsolete network
protocols (such as Token Ring).  PostgreSQL makes no provisions
for bit reversal; all accepted formats use the canonical LSB
order.

The remaining five input formats are not part of any standard.

### `macaddr8`

The `macaddr8` type stores MAC addresses in EUI-64
format, known for example from Ethernet card hardware addresses
(although MAC addresses are used for other purposes as well).
This type can accept both 6 and 8 byte length MAC addresses
and stores them in 8 byte length format.  MAC addresses given
in 6 byte format will be stored in 8 byte length format with the
4th and 5th bytes set to FF and FE, respectively.

Note that IPv6 uses a modified EUI-64 format where the 7th bit
should be set to one after the conversion from EUI-48.  The
function `macaddr8_set7bit` is provided to make this
change.

Generally speaking, any input which is comprised of pairs of hex
digits (on byte boundaries), optionally separated consistently by
one of `':'`, `'-'` or `'.'`, is
accepted.  The number of hex digits must be either 16 (8 bytes) or
12 (6 bytes).  Leading and trailing whitespace is ignored.

The following are examples of input formats that are accepted:

These examples all specify the same address.  Upper and
lower case is accepted for the digits
`a` through `f`.  Output is always in the
first of the forms shown.

The last six input formats shown above are not part of any standard.

To convert a traditional 48 bit MAC address in EUI-48 format to
modified EUI-64 format to be included as the host portion of an
IPv6 address, use `macaddr8_set7bit` as shown:

```
SELECT macaddr8_set7bit('08:00:2b:01:02:03');

macaddr8_set7bit
-------------------------
0a:00:2b:ff:fe:01:02:03
(1 row)

```

## Bit String Types

Bit strings are strings of 1's and 0's.  They can be used to store
or visualize bit masks.  There are two SQL bit types:
`bit(`n`)` and `bit
varying(`n`)`, where
`n` is a positive integer.

`bit` type data must match the length
`n` exactly; it is an error to attempt to
store shorter or longer bit strings.  `bit varying` data is
of variable length up to the maximum length
`n`; longer strings will be rejected.
Writing `bit` without a length is equivalent to
`bit(1)`, while `bit varying` without a length
specification means unlimited length.

> **Note:**

> If one explicitly casts a bit-string value to
> `bit(`n`)`, it will be truncated or
> zero-padded on the right to be exactly `n` bits,
> without raising an error.  Similarly,
> if one explicitly casts a bit-string value to
> `bit varying(`n`)`, it will be truncated
> on the right if it is more than `n` bits.
>

Refer to [sql-syntax-bit-strings](#sql-syntax-bit-strings) for information about the syntax
of bit string constants.  Bit-logical operators and string
manipulation functions are available; see [functions-bitstring](#functions-bitstring).

## Using the Bit String Types

```
CREATE TABLE test (a BIT(3), b BIT VARYING(5));
INSERT INTO test VALUES (B'101', B'00');
INSERT INTO test VALUES (B'10', B'101');

ERROR:  bit string length 2 does not match type bit(3)

INSERT INTO test VALUES (B'10'::bit(3), B'101');
SELECT * FROM test;

a  |  b
-----+-----
101 | 00
100 | 101

```

A bit string value requires 1 byte for each group of 8 bits, plus
5 or 8 bytes overhead depending on the length of the string
(but long values may be compressed or moved out-of-line, as explained
in [datatype-character](#datatype-character) for character strings).

## Text Search Types

PostgreSQL provides two data types that
are designed to support full text search, which is the activity of
searching through a collection of natural-language *documents*
to locate those that best match a *query*.
The `tsvector` type represents a document in a form optimized
for text search; the `tsquery` type similarly represents
a text query.
[textsearch](#textsearch) provides a detailed explanation of this
facility, and [functions-textsearch](#functions-textsearch) summarizes the
related functions and operators.

### `tsvector`

A `tsvector` value is a sorted list of distinct
*lexemes*, which are words that have been
*normalized* to merge different variants of the same word
(see [textsearch](#textsearch) for details).  Sorting and
duplicate-elimination are done automatically during input, as shown in
this example:

```
SELECT 'a fat cat sat on a mat and ate a fat rat'::tsvector;
tsvector
----------------------------------------------------
'a' 'and' 'ate' 'cat' 'fat' 'mat' 'on' 'rat' 'sat'
```

To represent
lexemes containing whitespace or punctuation, surround them with quotes:

```
SELECT $$the lexeme '    ' contains spaces$$::tsvector;
tsvector
-------------------------------------------
'    ' 'contains' 'lexeme' 'spaces' 'the'
```

(We use dollar-quoted string literals in this example and the next one
to avoid the confusion of having to double quote marks within the
literals.)  Embedded quotes and backslashes must be doubled:

```
SELECT $$the lexeme 'Joe''s' contains a quote$$::tsvector;
tsvector
------------------------------------------------
'Joe''s' 'a' 'contains' 'lexeme' 'quote' 'the'
```

Optionally, integer *positions*
can be attached to lexemes:

```
SELECT 'a:1 fat:2 cat:3 sat:4 on:5 a:6 mat:7 and:8 ate:9 a:10 fat:11 rat:12'::tsvector;
tsvector
-------------------------------------------------------------------------------
'a':1,6,10 'and':8 'ate':9 'cat':3 'fat':2,11 'mat':7 'on':5 'rat':12 'sat':4
```

A position normally indicates the source word's location in the
document.  Positional information can be used for
*proximity ranking*.  Position values can
range from 1 to 16383; larger numbers are silently set to 16383.
Duplicate positions for the same lexeme are discarded.

Lexemes that have positions can further be labeled with a
*weight*, which can be `A`,
`B`, `C`, or `D`.
`D` is the default and hence is not shown on output:

```
SELECT 'a:1A fat:2B,4C cat:5D'::tsvector;
tsvector
----------------------------
'a':1A 'cat':5 'fat':2B,4C
```

Weights are typically used to reflect document structure, for example
by marking title words differently from body words.  Text search
ranking functions can assign different priorities to the different
weight markers.

It is important to understand that the
`tsvector` type itself does not perform any word
normalization; it assumes the words it is given are normalized
appropriately for the application.  For example,

```
SELECT 'The Fat Rats'::tsvector;
tsvector
--------------------
'Fat' 'Rats' 'The'
```

For most English-text-searching applications the above words would
be considered non-normalized, but `tsvector` doesn't care.
Raw document text should usually be passed through
`to_tsvector` to normalize the words appropriately
for searching:

```
SELECT to_tsvector('english', 'The Fat Rats');
to_tsvector
-----------------
'fat':2 'rat':3
```

Again, see [textsearch](#textsearch) for more detail.

### `tsquery`

A `tsquery` value stores lexemes that are to be
searched for, and can combine them using the Boolean operators
`&` (AND), `|` (OR), and
`!` (NOT), as well as the phrase search operator
`<->` (FOLLOWED BY).  There is also a variant
`<`N`>` of the FOLLOWED BY
operator, where `N` is an integer constant that
specifies the distance between the two lexemes being searched
for.  `<->` is equivalent to `<1>`.

Parentheses can be used to enforce grouping of these operators.
In the absence of parentheses, `!` (NOT) binds most tightly,
`<->` (FOLLOWED BY) next most tightly, then
`&` (AND), with `|` (OR) binding
the least tightly.

Here are some examples:

```
SELECT 'fat & rat'::tsquery;
tsquery
---------------
'fat' & 'rat'

SELECT 'fat & (rat | cat)'::tsquery;
tsquery
---------------------------
'fat' & ( 'rat' | 'cat' )

SELECT 'fat & rat & ! cat'::tsquery;
tsquery
------------------------
'fat' & 'rat' & !'cat'
```

Optionally, lexemes in a `tsquery` can be labeled with
one or more weight letters, which restricts them to match only
`tsvector` lexemes with one of those weights:

```
SELECT 'fat:ab & cat'::tsquery;
tsquery
------------------
'fat':AB & 'cat'
```

Also, lexemes in a `tsquery` can be labeled with `*`
to specify prefix matching:

```
SELECT 'super:*'::tsquery;
tsquery
-----------
'super':*
```

This query will match any word in a `tsvector` that begins
with "super".

Quoting rules for lexemes are the same as described previously for
lexemes in `tsvector`; and, as with `tsvector`,
any required normalization of words must be done before converting
to the `tsquery` type.  The `to_tsquery`
function is convenient for performing such normalization:

```
SELECT to_tsquery('Fat:ab & Cats');
to_tsquery
------------------
'fat':AB & 'cat'
```

Note that `to_tsquery` will process prefixes in the same way
as other words, which means this comparison returns true:

```
SELECT to_tsvector( 'postgraduate' ) @@ to_tsquery( 'postgres:*' );
?column?
----------
t
```

because `postgres` gets stemmed to `postgr`:

```
SELECT to_tsvector( 'postgraduate' ), to_tsquery( 'postgres:*' );
to_tsvector  | to_tsquery
---------------+------------
'postgradu':1 | 'postgr':*
```

which will match the stemmed form of `postgraduate`.

## UUID Type

The data type `uuid` stores Universally Unique Identifiers
(UUID) as defined by [RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122),
ISO/IEC 9834-8:2005, and related standards.
(Some systems refer to this data type as a globally unique identifier, or
GUID, instead.)  This
identifier is a 128-bit quantity that is generated by an algorithm chosen
to make it very unlikely that the same identifier will be generated by
anyone else in the known universe using the same algorithm.  Therefore,
for distributed systems, these identifiers provide a better uniqueness
guarantee than sequence generators, which
are only unique within a single database.

A UUID is written as a sequence of lower-case hexadecimal digits,
in several groups separated by hyphens, specifically a group of 8
digits followed by three groups of 4 digits followed by a group of
12 digits, for a total of 32 digits representing the 128 bits.  An
example of a UUID in this standard form is:

```
a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11
```

PostgreSQL also accepts the following
alternative forms for input:
use of upper-case digits, the standard format surrounded by
braces, omitting some or all hyphens, adding a hyphen after any
group of four digits.  Examples are:

```
A0EEBC99-9C0B-4EF8-BB6D-6BB9BD380A11
{a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11}
a0eebc999c0b4ef8bb6d6bb9bd380a11
a0ee-bc99-9c0b-4ef8-bb6d-6bb9-bd38-0a11
{a0eebc99-9c0b4ef8-bb6d6bb9-bd380a11}
```

Output is always in the standard form.

See [functions-uuid](#functions-uuid) for how to generate a UUID in
PostgreSQL.

## Composite Types

A *composite type* represents the structure of a row or record;
it is essentially just a list of field names and their data types.
PostgreSQL allows  composite types to be
used in many of the same ways that simple types can be used.  For example, a
column of a table can be declared to be of a composite type.

### Declaration of Composite Types

Here are two simple examples of defining composite types:

```
CREATE TYPE complex AS (
r       double precision,
i       double precision
);

CREATE TYPE inventory_item AS (
name            text,
supplier_id     integer,
price           numeric
);
```

The syntax is comparable to `CREATE TABLE`, except that only
field names and types can be specified; no constraints (such as `NOT
NULL`) can presently be included.  Note that the `AS` keyword
is essential; without it, the system will think a different kind
of `CREATE TYPE` command is meant, and you will get odd syntax
errors.

Having defined the types, we can use them to create tables:

```
CREATE TABLE on_hand (
item      inventory_item,
count     integer
);

INSERT INTO on_hand VALUES (ROW('fuzzy dice', 42, 1.99), 1000);
```

or functions:

```
CREATE FUNCTION price_extension(inventory_item, integer) RETURNS numeric
AS 'SELECT $1.price * $2' LANGUAGE SQL;

SELECT price_extension(item, 10) FROM on_hand;
```

Whenever you create a table, a composite type is also automatically
created, with the same name as the table, to represent the table's
row type.  For example, had we said:

```
CREATE TABLE inventory_item (
name            text,
supplier_id     integer REFERENCES suppliers,
price           numeric CHECK (price > 0)
);
```

then the same `inventory_item` composite type shown above would
come into being as a
byproduct, and could be used just as above.  Note however an important
restriction of the current implementation: since no constraints are
associated with a composite type, the constraints shown in the table
definition *do not apply* to values of the composite type
outside the table.  (To work around this, create a
domain over the composite
type, and apply the desired constraints as `CHECK`
constraints of the domain.)

### Constructing Composite Values

To write a composite value as a literal constant, enclose the field
values within parentheses and separate them by commas.  You can put double
quotes around any field value, and must do so if it contains commas or
parentheses.  (More details appear [below](#rowtypes-io-syntax).)  Thus, the general format of
a composite constant is the following:

```
'( `val1` , `val2` , ... )'
```

An example is:

```
'("fuzzy dice",42,1.99)'
```

which would be a valid value of the `inventory_item` type
defined above.  To make a field be NULL, write no characters at all
in its position in the list.  For example, this constant specifies
a NULL third field:

```
'("fuzzy dice",42,)'
```

If you want an empty string rather than NULL, write double quotes:

```
'("",42,)'
```

Here the first field is a non-NULL empty string, the third is NULL.

(These constants are actually only a special case of
the generic type constants discussed in [sql-syntax-constants-generic](#sql-syntax-constants-generic).  The constant is initially
treated as a string and passed to the composite-type input conversion
routine.  An explicit type specification might be necessary to tell
which type to convert the constant to.)

The `ROW` expression syntax can also be used to
construct composite values.  In most cases this is considerably
simpler to use than the string-literal syntax since you don't have
to worry about multiple layers of quoting.  We already used this
method above:

```
ROW('fuzzy dice', 42, 1.99)
ROW('', 42, NULL)
```

The ROW keyword is actually optional as long as you have more than one
field in the expression, so these can be simplified to:

```
('fuzzy dice', 42, 1.99)
('', 42, NULL)
```

The `ROW` expression syntax is discussed in more detail in [sql-syntax-row-constructors](#sql-syntax-row-constructors).

### Accessing Composite Types

To access a field of a composite column, one writes a dot and the field
name, much like selecting a field from a table name.  In fact, it's so
much like selecting from a table name that you often have to use parentheses
to keep from confusing the parser.  For example, you might try to select
some subfields from our `on_hand` example table with something
like:

```
SELECT item.name FROM on_hand WHERE item.price > 9.99;
```

This will not work since the name `item` is taken to be a table
name, not a column name of `on_hand`, per SQL syntax rules.
You must write it like this:

```
SELECT (item).name FROM on_hand WHERE (item).price > 9.99;
```

or if you need to use the table name as well (for instance in a multitable
query), like this:

```
SELECT (on_hand.item).name FROM on_hand WHERE (on_hand.item).price > 9.99;
```

Now the parenthesized object is correctly interpreted as a reference to
the `item` column, and then the subfield can be selected from it.

Similar syntactic issues apply whenever you select a field from a composite
value.  For instance, to select just one field from the result of a function
that returns a composite value, you'd need to write something like:

```
SELECT (my_func(...)).field FROM ...
```

Without the extra parentheses, this will generate a syntax error.

The special field name `*` means "all fields", as
further explained in [rowtypes-usage](#rowtypes-usage).

### Modifying Composite Types

Here are some examples of the proper syntax for inserting and updating
composite columns.
First, inserting or updating a whole column:

```
INSERT INTO mytab (complex_col) VALUES((1.1,2.2));

UPDATE mytab SET complex_col = ROW(1.1,2.2) WHERE ...;
```

The first example omits `ROW`, the second uses it; we
could have done it either way.

We can update an individual subfield of a composite column:

```
UPDATE mytab SET complex_col.r = (complex_col).r + 1 WHERE ...;
```

Notice here that we don't need to (and indeed cannot)
put parentheses around the column name appearing just after
`SET`, but we do need parentheses when referencing the same
column in the expression to the right of the equal sign.

And we can specify subfields as targets for `INSERT`, too:

```
INSERT INTO mytab (complex_col.r, complex_col.i) VALUES(1.1, 2.2);
```

Had we not supplied values for all the subfields of the column, the
remaining subfields would have been filled with null values.

### Using Composite Types in Queries

There are various special syntax rules and behaviors associated with
composite types in queries.  These rules provide useful shortcuts,
but can be confusing if you don't know the logic behind them.

In PostgreSQL, a reference to a table name (or alias)
in a query is effectively a reference to the composite value of the
table's current row.  For example, if we had a table
`inventory_item` as shown
[above](#rowtypes-declaring), we could write:

```
SELECT c FROM inventory_item c;
```

This query produces a single composite-valued column, so we might get
output like:

```
c
------------------------
("fuzzy dice",42,1.99)
(1 row)
```

Note however that simple names are matched to column names before table
names, so this example works only because there is no column
named `c` in the query's tables.

The ordinary qualified-column-name
syntax `table_name``.``column_name`
can be understood as applying [field
selection](#field-selection) to the composite value of the table's current row.
(For efficiency reasons, it's not actually implemented that way.)

When we write

```
SELECT c.* FROM inventory_item c;
```

then, according to the SQL standard, we should get the contents of the
table expanded into separate columns:

```
name    | supplier_id | price
------------+-------------+-------
fuzzy dice |          42 |  1.99
(1 row)
```

as if the query were

```
SELECT c.name, c.supplier_id, c.price FROM inventory_item c;
```

PostgreSQL will apply this expansion behavior to
any composite-valued expression, although as shown [above](#rowtypes-accessing), you need to write parentheses
around the value that `.*` is applied to whenever it's not a
simple table name.  For example, if `myfunc()` is a function
returning a composite type with columns `a`,
`b`, and `c`, then these two queries have the
same result:

```
SELECT (myfunc(x)).* FROM some_table;
SELECT (myfunc(x)).a, (myfunc(x)).b, (myfunc(x)).c FROM some_table;
```

> **Tip:**

> PostgreSQL handles column expansion by
> actually transforming the first form into the second.  So, in this
> example, `myfunc()` would get invoked three times per row
> with either syntax.  If it's an expensive function you may wish to
> avoid that, which you can do with a query like:
> ```
> SELECT m.* FROM some_table, LATERAL myfunc(x) AS m;
> ```
> Placing the function in
> a `LATERAL` `FROM` item keeps it from
> being invoked more than once per row.  `m.*` is still
> expanded into `m.a, m.b, m.c`, but now those variables
> are just references to the output of the `FROM` item.
> (The `LATERAL` keyword is optional here, but we show it
> to clarify that the function is getting `x`
> from `some_table`.)
>

The `composite_value``.*` syntax results in
column expansion of this kind when it appears at the top level of
a [`SELECT` output
list](#queries-select-lists), a [`RETURNING`
list](#dml-returning) in `INSERT`/`UPDATE`/`DELETE`,
a [`VALUES` clause](#queries-values), or
a [row constructor](#sql-syntax-row-constructors).
In all other contexts (including when nested inside one of those
constructs), attaching `.*` to a composite value does not
change the value, since it means "all columns" and so the
same composite value is produced again.  For example,
if `somefunc()` accepts a composite-valued argument,
these queries are the same:

```
SELECT somefunc(c.*) FROM inventory_item c;
SELECT somefunc(c) FROM inventory_item c;
```

In both cases, the current row of `inventory_item` is
passed to the function as a single composite-valued argument.
Even though `.*` does nothing in such cases, using it is good
style, since it makes clear that a composite value is intended.  In
particular, the parser will consider `c` in `c.*` to
refer to a table name or alias, not to a column name, so that there is
no ambiguity; whereas without `.*`, it is not clear
whether `c` means a table name or a column name, and in fact
the column-name interpretation will be preferred if there is a column
named `c`.

Another example demonstrating these concepts is that all these queries
mean the same thing:

```
SELECT * FROM inventory_item c ORDER BY c;
SELECT * FROM inventory_item c ORDER BY c.*;
SELECT * FROM inventory_item c ORDER BY ROW(c.*);
```

All of these `ORDER BY` clauses specify the row's composite
value, resulting in sorting the rows according to the rules described
in [composite-type-comparison](#composite-type-comparison).  However,
if `inventory_item` contained a column
named `c`, the first case would be different from the
others, as it would mean to sort by that column only.  Given the column
names previously shown, these queries are also equivalent to those above:

```
SELECT * FROM inventory_item c ORDER BY ROW(c.name, c.supplier_id, c.price);
SELECT * FROM inventory_item c ORDER BY (c.name, c.supplier_id, c.price);
```

(The last case uses a row constructor with the key word `ROW`
omitted.)

Another special syntactical behavior associated with composite values is
that we can use *functional notation* for extracting a field
of a composite value.  The simple way to explain this is that
the notations ``field`(`table`)`
and ``table`.`field``
are interchangeable.  For example, these queries are equivalent:

```
SELECT c.name FROM inventory_item c WHERE c.price > 1000;
SELECT name(c) FROM inventory_item c WHERE price(c) > 1000;
```

Moreover, if we have a function that accepts a single argument of a
composite type, we can call it with either notation.  These queries are
all equivalent:

```
SELECT somefunc(c) FROM inventory_item c;
SELECT somefunc(c.*) FROM inventory_item c;
SELECT c.somefunc FROM inventory_item c;
```

This equivalence between functional notation and field notation
makes it possible to use functions on composite types to implement
"computed fields".

An application using the last query above wouldn't need to be directly
aware that `somefunc` isn't a real column of the table.

> **Tip:**

> Because of this behavior, it's unwise to give a function that takes a
> single composite-type argument the same name as any of the fields of
> that composite type.  If there is ambiguity, the field-name
> interpretation will be chosen if field-name syntax is used, while the
> function will be chosen if function-call syntax is used.  However,
> PostgreSQL versions before 11 always chose the
> field-name interpretation, unless the syntax of the call required it to
> be a function call.  One way to force the function interpretation in
> older versions is to schema-qualify the function name, that is, write
> ``schema`.`func`(`compositevalue`)`.
>

### Composite Type Input and Output Syntax

The external text representation of a composite value consists of items that
are interpreted according to the I/O conversion rules for the individual
field types, plus decoration that indicates the composite structure.
The decoration consists of parentheses (`(` and `)`)
around the whole value, plus commas (`,`) between adjacent
items.  Whitespace outside the parentheses is ignored, but within the
parentheses it is considered part of the field value, and might or might not be
significant depending on the input conversion rules for the field data type.
For example, in:

```
'(  42)'
```

the whitespace will be ignored if the field type is integer, but not if
it is text.

As shown previously, when writing a composite value you can write double
quotes around any individual field value.
You *must* do so if the field value would otherwise
confuse the composite-value parser.  In particular, fields containing
parentheses, commas, double quotes, or backslashes must be double-quoted.
To put a double quote or backslash in a quoted composite field value,
precede it with a backslash.  (Also, a pair of double quotes within a
double-quoted field value is taken to represent a double quote character,
analogously to the rules for single quotes in SQL literal strings.)
Alternatively, you can avoid quoting and use backslash-escaping to
protect all data characters
that would otherwise be taken as composite syntax.

A completely empty field value (no characters at all between the commas
or parentheses) represents a NULL.  To write a value that is an empty
string rather than NULL, write `""`.

The composite output routine will put double quotes around field values
if they are empty strings or contain parentheses, commas,
double quotes, backslashes, or white space.  (Doing so for white space
is not essential, but aids legibility.)  Double quotes and backslashes
embedded in field values will be doubled.

> **Note:**

> Remember that what you write in an SQL command will first be interpreted
> as a string literal, and then as a composite.  This doubles the number of
> backslashes you need (assuming escape string syntax is used).
> For example, to insert a `text` field
> containing a double quote and a backslash in a composite
> value, you'd need to write:
> ```
> INSERT ... VALUES ('("\"\\")');
> ```
> The string-literal processor removes one level of backslashes, so that
> what arrives at the composite-value parser looks like
> `("\"\\")`.  In turn, the string
> fed to the `text` data type's input routine
> becomes `"\`.  (If we were working
> with a data type whose input routine also treated backslashes specially,
> `bytea` for example, we might need as many as eight backslashes
> in the command to get one backslash into the stored composite field.)
> Dollar quoting (see [sql-syntax-dollar-quoting](#sql-syntax-dollar-quoting)) can be
> used to avoid the need to double backslashes.
>

> **Tip:**

> The `ROW` constructor syntax is usually easier to work with
> than the composite-literal syntax when writing composite values in SQL
> commands.
> In `ROW`, individual field values are written the same way
> they would be written when not members of a composite.
>

## Domain Types

A *domain* is a user-defined data type that is
based on another *underlying type*.  Optionally,
it can have constraints that restrict its valid values to a subset of
what the underlying type would allow.  Otherwise it behaves like the
underlying type — for example, any operator or function that
can be applied to the underlying type will work on the domain type.
The underlying type can be any built-in or user-defined base type,
enum type, array type, composite type, range type, or another domain.

For example, we could create a domain over integers that accepts only
positive integers:

```
CREATE DOMAIN posint AS integer CHECK (VALUE > 0);
CREATE TABLE mytable (id posint);
INSERT INTO mytable VALUES(1);   -- works
INSERT INTO mytable VALUES(-1);  -- fails
```

When an operator or function of the underlying type is applied to a
domain value, the domain is automatically down-cast to the underlying
type.  Thus, for example, the result of `mytable.id - 1`
is considered to be of type `integer` not `posint`.
We could write `(mytable.id - 1)::posint` to cast the
result back to `posint`, causing the domain's constraints
to be rechecked.  In this case, that would result in an error if the
expression had been applied to an `id` value of
1.  Assigning a value of the underlying type to a field or variable of
the domain type is allowed without writing an explicit cast, but the
domain's constraints will be checked.

For additional information see [sql-createdomain](#sql-createdomain).

## Object Identifier Types

Object identifiers (OIDs) are used internally by
PostgreSQL as primary keys for various
system tables.
Type `oid` represents an object identifier.  There are also
several alias types for `oid`, each
named `reg`something``.
[datatype-oid-table](#datatype-oid-table) shows an
overview.

The `oid` type is currently implemented as an unsigned
four-byte integer.  Therefore, it is not large enough to provide
database-wide uniqueness in large databases, or even in large
individual tables.

The `oid` type itself has few operations beyond comparison.
It can be cast to integer, however, and then manipulated using the
standard integer operators.  (Beware of possible
signed-versus-unsigned confusion if you do this.)

The OID alias types have no operations of their own except
for specialized input and output routines.  These routines are able
to accept and display symbolic names for system objects, rather than
the raw numeric value that type `oid` would use.  The alias
types allow simplified lookup of OID values for objects.  For example,
to examine the `pg_attribute` rows related to a table
`mytable`, one could write:

```
SELECT * FROM pg_attribute WHERE attrelid = 'mytable'::regclass;
```

rather than:

```
SELECT * FROM pg_attribute
WHERE attrelid = (SELECT oid FROM pg_class WHERE relname = 'mytable');
```

While that doesn't look all that bad by itself, it's still oversimplified.
A far more complicated sub-select would be needed to
select the right OID if there are multiple tables named
`mytable` in different schemas.
The `regclass` input converter handles the table lookup according
to the schema path setting, and so it does the "right thing"
automatically.  Similarly, casting a table's OID to
`regclass` is handy for symbolic display of a numeric OID.

| Name | References | Description | Value Example |
| --- | --- | --- | --- |
| `oid` | any | numeric object identifier | `564182` |
| `regclass` | `pg_class` | relation name | `pg_type` |
| `regcollation` | `pg_collation` | collation name | `"POSIX"` |
| `regconfig` | `pg_ts_config` | text search configuration | `english` |
| `regdictionary` | `pg_ts_dict` | text search dictionary | `simple` |
| `regnamespace` | `pg_namespace` | namespace name | `pg_catalog` |
| `regoper` | `pg_operator` | operator name | `+` |
| `regoperator` | `pg_operator` | operator with argument types | `*(integer,integer)`          or `-(NONE,integer)` |
| `regproc` | `pg_proc` | function name | `sum` |
| `regprocedure` | `pg_proc` | function with argument types | `sum(int4)` |
| `regrole` | `pg_authid` | role name | `smithee` |
| `regtype` | `pg_type` | data type name | `integer` |

All of the OID alias types for objects that are grouped by namespace
accept schema-qualified names, and will
display schema-qualified names on output if the object would not
be found in the current search path without being qualified.
For example, `myschema.mytable` is acceptable input
for `regclass` (if there is such a table).  That value
might be output as `myschema.mytable`, or
just `mytable`, depending on the current search path.
The `regproc` and `regoper` alias types will only
accept input names that are unique (not overloaded), so they are
of limited use; for most uses `regprocedure` or
`regoperator` are more appropriate.  For `regoperator`,
unary operators are identified by writing `NONE` for the unused
operand.

The input functions for these types allow whitespace between tokens,
and will fold upper-case letters to lower case, except within double
quotes; this is done to make the syntax rules similar to the way
object names are written in SQL.  Conversely, the output functions
will use double quotes if needed to make the output be a valid SQL
identifier.  For example, the OID of a function
named `Foo` (with upper case `F`)
taking two integer arguments could be entered as
`' "Foo" ( int, integer ) '::regprocedure`.  The
output would look like `"Foo"(integer,integer)`.
Both the function name and the argument type names could be
schema-qualified, too.

Many built-in PostgreSQL functions accept
the OID of a table, or another kind of database object, and for
convenience are declared as taking `regclass` (or the
appropriate OID alias type).  This means you do not have to look up
the object's OID by hand, but can just enter its name as a string
literal.  For example, the `nextval(regclass)` function
takes a sequence relation's OID, so you could call it like this:

```
nextval('foo')              operates on sequence `foo`
nextval('FOO')              same as above
nextval('"Foo"')            operates on sequence `Foo`
nextval('myschema.foo')     operates on `myschema.foo`
nextval('"myschema".foo')   same as above
nextval('foo')              searches search path for `foo`
```

> **Note:**

> When you write the argument of such a function as an unadorned
> literal string, it becomes a constant of type `regclass`
> (or the appropriate type).
> Since this is really just an OID, it will track the originally
> identified object despite later renaming, schema reassignment,
> etc.  This "early binding" behavior is usually desirable for
> object references in column defaults and views.  But sometimes you might
> want "late binding" where the object reference is resolved
> at run time.  To get late-binding behavior, force the constant to be
> stored as a `text` constant instead of `regclass`:
> ```
> nextval('foo'::text)      `foo` is looked up at runtime
> ```
> The `to_regclass()` function and its siblings
> can also be used to perform run-time lookups.  See
> [functions-info-catalog-table](#functions-info-catalog-table).
>

Another practical example of use of `regclass`
is to look up the OID of a table listed in
the `information_schema` views, which don't supply
such OIDs directly.  One might for example wish to call
the `pg_relation_size()` function, which requires
the table OID.  Taking the above rules into account, the correct way
to do that is

```
SELECT table_schema, table_name,
pg_relation_size((quote_ident(table_schema) || '.' ||
quote_ident(table_name))::regclass)
FROM information_schema.tables
WHERE ...
```

The `quote_ident()` function will take care of
double-quoting the identifiers where needed.  The seemingly easier

```
SELECT pg_relation_size(table_name)
FROM information_schema.tables
WHERE ...
```

is *not recommended*, because it will fail for
tables that are outside your search path or have names that require
quoting.

An additional property of most of the OID alias types is the creation of
dependencies.  If a
constant of one of these types appears in a stored expression
(such as a column default expression or view), it creates a dependency
on the referenced object.  For example, if a column has a default
expression `nextval('my_seq'::regclass)`,
PostgreSQL
understands that the default expression depends on the sequence
`my_seq`, so the system will not let the sequence
be dropped without first removing the default expression.  The
alternative of `nextval('my_seq'::text)` does not
create a dependency.
(`regrole` is an exception to this property. Constants of this
type are not allowed in stored expressions.)

Another identifier type used by the system is `xid`, or transaction
(abbreviated xact) identifier.  This is the data type of the system columns
`xmin` and `xmax`.  Transaction identifiers are 32-bit quantities.
In some contexts, a 64-bit variant `xid8` is used.  Unlike
`xid` values, `xid8` values increase strictly
monotonically and cannot be reused in the lifetime of a database
cluster.  See [transaction-id](#transaction-id) for more details.

A third identifier type used by the system is `cid`, or
command identifier.  This is the data type of the system columns
`cmin` and `cmax`. Command identifiers are also 32-bit quantities.

A final identifier type used by the system is `tid`, or tuple
identifier (row identifier).  This is the data type of the system column
`ctid`.  A tuple ID is a pair
(block number, tuple index within block) that identifies the
physical location of the row within its table.

(The system columns are further explained in [ddl-system-columns](#ddl-system-columns).)

## `pg_lsn` Type

The `pg_lsn` data type can be used to store LSN (Log Sequence
Number) data which is a pointer to a location in the WAL. This type is a
representation of `XLogRecPtr` and an internal system type of
PostgreSQL.

Internally, an LSN is a 64-bit integer, representing a byte position in
the write-ahead log stream.  It is printed as two hexadecimal numbers of
up to 8 digits each, separated by a slash; for example,
`16/B374D848`.  The `pg_lsn` type supports the
standard comparison operators, like `=` and
`>`.  Two LSNs can be subtracted using the
`-` operator; the result is the number of bytes separating
those write-ahead log locations.  Also the number of bytes can be
added into and subtracted from LSN using the
`+(pg_lsn,numeric)` and
`-(pg_lsn,numeric)` operators, respectively. Note that
the calculated LSN should be in the range of `pg_lsn` type,
i.e., between `0/0` and
`FFFFFFFF/FFFFFFFF`.

## Pseudo-Types

The PostgreSQL type system contains a
number of special-purpose entries that are collectively called
*pseudo-types*.  A pseudo-type cannot be used as a
column data type, but it can be used to declare a function's
argument or result type.  Each of the available pseudo-types is
useful in situations where a function's behavior does not
correspond to simply taking or returning a value of a specific
SQL data type.  [datatype-pseudotypes-table](#datatype-pseudotypes-table) lists the existing
pseudo-types.

| Name | Description |
| --- | --- |
| `any` | Indicates that a function accepts any input data type. |
| `anyelement` | Indicates that a function accepts any data type         (see [extend-types-polymorphic](#extend-types-polymorphic)). |
| `anyarray` | Indicates that a function accepts any array data type         (see [extend-types-polymorphic](#extend-types-polymorphic)). |
| `anynonarray` | Indicates that a function accepts any non-array data type         (see [extend-types-polymorphic](#extend-types-polymorphic)). |
| `anyenum` | Indicates that a function accepts any enum data type         (see [extend-types-polymorphic](#extend-types-polymorphic) and         [datatype-enum](#datatype-enum)). |
| `anyrange` | Indicates that a function accepts any range data type         (see [extend-types-polymorphic](#extend-types-polymorphic) and         [rangetypes](#rangetypes)). |
| `anymultirange` | Indicates that a function accepts any multirange data type         (see [extend-types-polymorphic](#extend-types-polymorphic) and         [rangetypes](#rangetypes)). |
| `anycompatible` | Indicates that a function accepts any data type,         with automatic promotion of multiple arguments to a common data type         (see [extend-types-polymorphic](#extend-types-polymorphic)). |
| `anycompatiblearray` | Indicates that a function accepts any array data type,         with automatic promotion of multiple arguments to a common data type         (see [extend-types-polymorphic](#extend-types-polymorphic)). |
| `anycompatiblenonarray` | Indicates that a function accepts any non-array data type,         with automatic promotion of multiple arguments to a common data type         (see [extend-types-polymorphic](#extend-types-polymorphic)). |
| `anycompatiblerange` | Indicates that a function accepts any range data type,         with automatic promotion of multiple arguments to a common data type         (see [extend-types-polymorphic](#extend-types-polymorphic) and         [rangetypes](#rangetypes)). |
| `anycompatiblemultirange` | Indicates that a function accepts any multirange data type,         with automatic promotion of multiple arguments to a common data type         (see [extend-types-polymorphic](#extend-types-polymorphic) and         [rangetypes](#rangetypes)). |
| `cstring` | Indicates that a function accepts or returns a null-terminated C string. |
| `internal` | Indicates that a function accepts or returns a server-internal         data type. |
| `language_handler` | A procedural language call handler is declared to return `language_handler`. |
| `fdw_handler` | A foreign-data wrapper handler is declared to return `fdw_handler`. |
| `table_am_handler` | A table access method handler is declared to return `table_am_handler`. |
| `index_am_handler` | An index access method handler is declared to return `index_am_handler`. |
| `tsm_handler` | A tablesample method handler is declared to return `tsm_handler`. |
| `record` | Identifies a function taking or returning an unspecified row type. |
| `trigger` | A trigger function is declared to return `trigger.` |
| `event_trigger` | An event trigger function is declared to return `event_trigger.` |
| `pg_ddl_command` | Identifies a representation of DDL commands that is available to event triggers. |
| `void` | Indicates that a function returns no value. |
| `unknown` | Identifies a not-yet-resolved type, e.g., of an undecorated          string literal. |

Functions coded in C (whether built-in or dynamically loaded) can be
declared to accept or return any of these pseudo-types.  It is up to
the function author to ensure that the function will behave safely
when a pseudo-type is used as an argument type.

Functions coded in procedural languages can use pseudo-types only as
allowed by their implementation languages.  At present most procedural
languages forbid use of a pseudo-type as an argument type, and allow
only `void` and `record` as a result type (plus
`trigger` or `event_trigger` when the function is used
as a trigger or event trigger).  Some also support polymorphic functions
using the polymorphic pseudo-types, which are shown above and discussed
in detail in [extend-types-polymorphic](#extend-types-polymorphic).

The `internal` pseudo-type is used to declare functions
that are meant only to be called internally by the database
system, and not by direct invocation in an SQL
query.  If a function has at least one `internal`-type
argument then it cannot be called from SQL.  To
preserve the type safety of this restriction it is important to
follow this coding rule: do not create any function that is
declared to return `internal` unless it has at least one
`internal` argument.
