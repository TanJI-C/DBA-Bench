# overview; low-risk reference modules including btree_gin, citext, cube, earthdistance, fuzzystrmatch, intagg, intarray, isn, lo, ltree, seg, spi, tablefunc, tcn, tsm_system_rows, tsm_system_time, uuid-ossp, xml2

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/06_additional_supplied_modules_and_extensions.md`
- Source Title: `postgresql.conf`
- Source Heading Path: `Additional Supplied Modules and Extensions > overview; low-risk reference modules including btree_gin, citext, cube, earthdistance, fuzzystrmatch, intagg, intarray, isn, lo, ltree, seg, spi, tablefunc, tcn, tsm_system_rows, tsm_system_time, uuid-ossp, xml2`
- Source Line Ranges: `1146-1309, 1310-1507, 2970-3063, 3228-3509, 3855-3947, 3948-4018, 4019-4213, 4299-4571, 8601-8755, 9299-9387, 9509-10152, 10153-10207, 10256-10299, 10300-10345, 10487-10550, 10551-10762`
- Chunk ID: `pg16_fact_0125_a65a778241`
- Review Status: `needs_human_review`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ee5a3ad3607ff9d0485d261e412c5d4e9588cabd277191ec363d37d8334ec1f4`

## Retrieval Guidance

- Use When: Look up behavior and usage of supplied PostgreSQL extensions that are not primarily operational diagnostics or configuration tools.
- Retrieval Keywords: contrib modules, btree_gin, citext, cube, earthdistance, fuzzystrmatch, intarray, ltree, tablefunc, uuid-ossp, xml2
- Follow-up Guidance: Review individual module semantics if a production incident depends on side effects, index behavior, or deprecated functionality.
- Classification Note: These module sections are mostly reference for extension data types, functions, operator classes, examples, and compatibility notes without primary diagnostic or remediation semantics.

## Official Source Content

## citext — a case-insensitive character string type

The `citext` module provides a case-insensitive
character string type, `citext`. Essentially, it internally calls
`lower` when comparing values. Otherwise, it behaves almost
exactly like `text`.

> **Tip:**

> Consider using *nondeterministic collations* (see
> [collation-nondeterministic](#collation-nondeterministic)) instead of this module.  They
> can be used for case-insensitive comparisons, accent-insensitive
> comparisons, and other combinations, and they handle more Unicode special
> cases correctly.
>

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Rationale

The standard approach to doing case-insensitive matches
in PostgreSQL has been to use the `lower`
function when comparing values, for example

```
SELECT * FROM tab WHERE lower(col) = LOWER(?);
```

This works reasonably well, but has a number of drawbacks:

- It makes your SQL statements verbose, and you always have to remember to
use `lower` on both the column and the query value.
- It won't use an index, unless you create a functional index using
`lower`.
- If you declare a column as `UNIQUE` or `PRIMARY
KEY`, the implicitly generated index is case-sensitive.  So it's
useless for case-insensitive searches, and it won't enforce
uniqueness case-insensitively.

The `citext` data type allows you to eliminate calls
to `lower` in SQL queries, and allows a primary key to
be case-insensitive. `citext` is locale-aware, just
like `text`, which means that the matching of upper case and
lower case characters is dependent on the rules of
the database's `LC_CTYPE` setting. Again, this behavior is
identical to the use of `lower` in queries. But because it's
done transparently by the data type, you don't have to remember to do
anything special in your queries.

### How to Use It

Here's a simple example of usage:

```
CREATE TABLE users (
nick CITEXT PRIMARY KEY,
pass TEXT   NOT NULL
);

INSERT INTO users VALUES ( 'larry',  sha256(random()::text::bytea) );
INSERT INTO users VALUES ( 'Tom',    sha256(random()::text::bytea) );
INSERT INTO users VALUES ( 'Damian', sha256(random()::text::bytea) );
INSERT INTO users VALUES ( 'NEAL',   sha256(random()::text::bytea) );
INSERT INTO users VALUES ( 'Bjrn',  sha256(random()::text::bytea) );

SELECT * FROM users WHERE nick = 'Larry';
```

The `SELECT` statement will return one tuple, even though
the `nick` column was set to `larry` and the query
was for `Larry`.

### String Comparison Behavior

`citext` performs comparisons by converting each string to lower
case (as though `lower` were called) and then comparing the
results normally.  Thus, for example, two strings are considered equal
if `lower` would produce identical results for them.

In order to emulate a case-insensitive collation as closely as possible,
there are `citext`-specific versions of a number of string-processing
operators and functions.  So, for example, the regular expression
operators `~` and `~*` exhibit the same behavior when
applied to `citext`: they both match case-insensitively.
The same is true
for `!~` and `!~*`, as well as for the
`LIKE` operators `~~` and `~~*`, and
`!~~` and `!~~*`. If you'd like to match
case-sensitively, you can cast the operator's arguments to `text`.

Similarly, all of the following functions perform matching
case-insensitively if their arguments are `citext`:

- `regexp_match()`
- `regexp_matches()`
- `regexp_replace()`
- `regexp_split_to_array()`
- `regexp_split_to_table()`
- `replace()`
- `split_part()`
- `strpos()`
- `translate()`

For the regexp functions, if you want to match case-sensitively, you can
specify the "c" flag to force a case-sensitive match.  Otherwise,
you must cast to `text` before using one of these functions if
you want case-sensitive behavior.

### Limitations

- `citext`'s case-folding behavior depends on
the `LC_CTYPE` setting of your database. How it compares
values is therefore determined when the database is created.
It is not truly
case-insensitive in the terms defined by the Unicode standard.
Effectively, what this means is that, as long as you're happy with your
collation, you should be happy with `citext`'s comparisons. But
if you have data in different languages stored in your database, users
of one language may find their query results are not as expected if the
collation is for another language.
- As of PostgreSQL 9.1, you can attach a
`COLLATE` specification to `citext` columns or data
values.  Currently, `citext` operators will honor a non-default
`COLLATE` specification while comparing case-folded strings,
but the initial folding to lower case is always done according to the
database's `LC_CTYPE` setting (that is, as though
`COLLATE "default"` were given).  This may be changed in a
future release so that both steps follow the input `COLLATE`
specification.
- `citext` is not as efficient as `text` because the
operator functions and the B-tree comparison functions must make copies
of the data and convert it to lower case for comparisons.  Also, only
`text` can support B-Tree deduplication.  However,
`citext` is slightly more efficient than using
`lower` to get case-insensitive matching.
- `citext` doesn't help much if you need data to compare
case-sensitively in some contexts and case-insensitively in other
contexts.  The standard answer is to use the `text` type and
manually use the `lower` function when you need to compare
case-insensitively; this works all right if case-insensitive comparison
is needed only infrequently.  If you need case-insensitive behavior most
of the time and case-sensitive infrequently, consider storing the data
as `citext` and explicitly casting the column to `text`
when you want case-sensitive comparison.  In either situation, you will
need two indexes if you want both types of searches to be fast.
- The schema containing the `citext` operators must be
in the current `search_path` (typically `public`);
if it is not, the normal case-sensitive `text` operators
will be invoked instead.
- The approach of lower-casing strings for comparison does not handle some
Unicode special cases correctly, for example when one upper-case letter
has two lower-case letter equivalents.  Unicode distinguishes between
*case mapping* and *case
folding* for this reason.  Use nondeterministic collations
instead of `citext` to handle that correctly.

### Author

David E. Wheeler david@kineticode.com

Inspired by the original `citext` module by Donald Fraser.

## cube — a multi-dimensional cube data type

This module implements a data type `cube` for
representing multidimensional cubes.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Syntax

[cube-repr-table](#cube-repr-table) shows the valid external
representations for the `cube`
type.  `x`, `y`, etc. denote
floating-point numbers.

| External Syntax | Meaning |
| --- | --- |
| ``x`` | A one-dimensional point        (or, zero-length one-dimensional interval) |
| `(`x`)` | Same as above |
| ``x1`,`x2`,...,`xn`` | A point in n-dimensional space, represented internally as a       zero-volume cube |
| `(`x1`,`x2`,...,`xn`)` | Same as above |
| `(`x`),(`y`)` | A one-dimensional interval starting at `x` and ending at `y` or vice versa; the        order does not matter |
| `[(`x`),(`y`)]` | Same as above |
| `(`x1`,...,`xn`),(`y1`,...,`yn`)` | An n-dimensional cube represented by a pair of its diagonally        opposite corners |
| `[(`x1`,...,`xn`),(`y1`,...,`yn`)]` | Same as above |

It does not matter which order the opposite corners of a cube are
entered in.  The `cube` functions
automatically swap values if needed to create a uniform
"lower left — upper right" internal representation.
When the corners coincide, `cube` stores only one corner
along with an "is point" flag to avoid wasting space.

White space is ignored on input, so
`[(`x`),(`y`)]` is the same as
`[ ( `x` ), ( `y` ) ]`.

### Precision

Values are stored internally as 64-bit floating point numbers. This means
that numbers with more than about 16 significant digits will be truncated.

### Usage

[cube-operators-table](#cube-operators-table) shows the specialized operators
provided for type `cube`.

| Operator                         Description |
| --- |
| `cube` `&&` `cube`         boolean                         Do the cubes overlap? |
| `cube` `@>` `cube`         boolean                         Does the first cube contain the second? |
| `cube` `` `integer`         float8                         Extracts the n-th coordinate of the cube         (counting from 1). |
| `cube` `~>` `integer`         float8                         Extracts the n-th coordinate of the cube,         counting in the following way: n = 2         * k - 1 means lower bound         of k-th dimension, n = 2         * k means upper bound of         k-th dimension.  Negative         n denotes the inverse value of the corresponding         positive coordinate.  This operator is designed for KNN-GiST support. |
| `cube` `` `cube`         float8                         Computes the Euclidean distance between the two cubes. |
| `cube` `` `cube`         float8                         Computes the taxicab (L-1 metric) distance between the two cubes. |
| `cube` `` `cube`         float8                         Computes the Chebyshev (L-inf metric) distance between the two cubes. |

In addition to the above operators, the usual comparison
operators shown in [functions-comparison-op-table](#functions-comparison-op-table) are
available for type `cube`.  These
operators first compare the first coordinates, and if those are equal,
compare the second coordinates, etc.  They exist mainly to support the
b-tree index operator class for `cube`, which can be useful for
example if you would like a UNIQUE constraint on a `cube` column.
Otherwise, this ordering is not of much practical use.

The `cube` module also provides a GiST index operator class for
`cube` values.
A `cube` GiST index can be used to search for values using the
`=`, `&&`, `@>`, and
`<@` operators in `WHERE` clauses.

In addition, a `cube` GiST index can be used to find nearest
neighbors using the metric operators
`<->`, `<#>`, and
`<=>` in `ORDER BY` clauses.
For example, the nearest neighbor of the 3-D point (0.5, 0.5, 0.5)
could be found efficiently with:

```
SELECT c FROM test ORDER BY c  cube(array[0.5,0.5,0.5]) LIMIT 1;
```

The `~>` operator can also be used in this way to
efficiently retrieve the first few values sorted by a selected coordinate.
For example, to get the first few cubes ordered by the first coordinate
(lower left corner) ascending one could use the following query:

```
SELECT c FROM test ORDER BY c ~> 1 LIMIT 5;
```

And to get 2-D cubes ordered by the first coordinate of the upper right
corner descending:

```
SELECT c FROM test ORDER BY c ~> 3 DESC LIMIT 5;
```

[cube-functions-table](#cube-functions-table) shows the available functions.

| Function                         Description                         Example(s) |
| --- |
| `cube` ( `float8` )         cube                         Makes a one dimensional cube with both coordinates the same.                         `cube(1)`         (1) |
| `cube` ( `float8`, `float8` )         cube                         Makes a one dimensional cube.                         `cube(1, 2)`         (1),(2) |
| `cube` ( `float8[]` )         cube                         Makes a zero-volume cube using the coordinates defined by the array.                         `cube(ARRAY[1,2,3])`         (1, 2, 3) |
| `cube` ( `float8[]`, `float8[]` )         cube                         Makes a cube with upper right and lower left coordinates as defined by         the two arrays, which must be of the same length.                         `cube(ARRAY[1,2], ARRAY[3,4])`         (1, 2),(3, 4) |
| `cube` ( `cube`, `float8` )         cube                         Makes a new cube by adding a dimension on to an existing cube,         with the same values for both endpoints of the new coordinate.  This         is useful for building cubes piece by piece from calculated values.                         `cube('(1,2),(3,4)'::cube, 5)`         (1, 2, 5),(3, 4, 5) |
| `cube` ( `cube`, `float8`, `float8` )         cube                         Makes a new cube by adding a dimension on to an existing cube. This is         useful for building cubes piece by piece from calculated values.                         `cube('(1,2),(3,4)'::cube, 5, 6)`         (1, 2, 5),(3, 4, 6) |
| `cube_dim` ( `cube` )         integer                         Returns the number of dimensions of the cube.                         `cube_dim('(1,2),(3,4)')`         2 |
| `cube_ll_coord` ( `cube`, `integer` )         float8                         Returns the n-th coordinate value for the lower         left corner of the cube.                         `cube_ll_coord('(1,2),(3,4)', 2)`         2 |
| `cube_ur_coord` ( `cube`, `integer` )         float8                         Returns the n-th coordinate value for the         upper right corner of the cube.                         `cube_ur_coord('(1,2),(3,4)', 2)`         4 |
| `cube_is_point` ( `cube` )         boolean                         Returns true if the cube is a point, that is,         the two defining corners are the same.                         `cube_is_point(cube(1,1))`         t |
| `cube_distance` ( `cube`, `cube` )         float8                         Returns the distance between two cubes. If both         cubes are points, this is the normal distance function.                         `cube_distance('(1,2)', '(3,4)')`         2.8284271247461903 |
| `cube_subset` ( `cube`, `integer[]` )         cube                         Makes a new cube from an existing cube, using a list of         dimension indexes from an array. Can be used to extract the endpoints         of a single dimension, or to drop dimensions, or to reorder them as         desired.                         `cube_subset(cube('(1,3,5),(6,7,8)'), ARRAY[2])`         (3),(7)                         `cube_subset(cube('(1,3,5),(6,7,8)'), ARRAY[3,2,1,1])`         (5, 3, 1, 1),(8, 7, 6, 6) |
| `cube_union` ( `cube`, `cube` )         cube                         Produces the union of two cubes.                         `cube_union('(1,2)', '(3,4)')`         (1, 2),(3, 4) |
| `cube_inter` ( `cube`, `cube` )         cube                         Produces the intersection of two cubes.                         `cube_inter('(1,2)', '(3,4)')`         (3, 4),(1, 2) |
| `cube_enlarge` ( c `cube`, r `double`, n `integer` )         cube                         Increases the size of the cube by the specified         radius r in at least n         dimensions.  If the radius is negative the cube is shrunk instead.         All defined dimensions are changed by the         radius r.  Lower-left coordinates are decreased         by r and upper-right coordinates are increased         by r.  If a lower-left coordinate is increased         to more than the corresponding upper-right coordinate (this can only         happen when r  0), then extra dimensions are added to         make n altogether; 0 is used as the initial         value for the extra coordinates.  This function is useful for creating         bounding boxes around a point for searching for nearby points.                         `cube_enlarge('(1,2),(3,4)', 0.5, 3)`         (0.5, 1.5, -0.5),(3.5, 4.5, 0.5) |

### Defaults

This union:

```
select cube_union('(0,5,2),(2,3,1)', '0');
cube_union
-------------------
(0, 0, 0),(2, 5, 2)
(1 row)
```

does not contradict common sense, neither does the intersection:

```
select cube_inter('(0,-1),(1,1)', '(-2),(2)');
cube_inter
-------------
(0, 0),(1, 0)
(1 row)
```

In all binary operations on differently-dimensioned cubes,
the lower-dimensional one is assumed to be a Cartesian projection, i. e., having zeroes
in place of coordinates omitted in the string representation. The above
examples are equivalent to:

```
cube_union('(0,5,2),(2,3,1)','(0,0,0),(0,0,0)');
cube_inter('(0,-1),(1,1)','(-2,0),(2,0)');
```

The following containment predicate uses the point syntax,
while in fact the second argument is internally represented by a box.
This syntax makes it unnecessary to define a separate point type
and functions for (box,point) predicates.

```
select cube_contains('(0,0),(1,1)', '0.5,0.5');
cube_contains
--------------
t
(1 row)
```

### Notes

For examples of usage, see the regression test `sql/cube.sql`.

To make it harder for people to break things, there
is a limit of 100 on the number of dimensions of cubes. This is set
in `cubedata.h` if you need something bigger.

### Credits

Original author: Gene Selkov, Jr. selkovjr@mcs.anl.gov,
Mathematics and Computer Science Division, Argonne National Laboratory.

My thanks are primarily to Prof. Joe Hellerstein
([](https://dsf.berkeley.edu/jmh/)) for elucidating the
gist of the GiST ([](http://gist.cs.berkeley.edu/)), and
to his former student Andy Dong for his example written for Illustra.
I am also grateful to all Postgres developers, present and past, for
enabling myself to create my own world and live undisturbed in it. And I
would like to acknowledge my gratitude to Argonne Lab and to the
U.S. Department of Energy for the years of faithful support of my database
research.

Minor updates to this package were made by Bruno Wolff III
bruno@wolff.to in August/September of 2002. These include
changing the precision from single precision to double precision and adding
some new functions.

Additional updates were made by Joshua Reich josh@root.net in
July 2006. These include `cube(float8[], float8[])` and
cleaning up the code to use the V1 call protocol instead of the deprecated
V0 protocol.

## earthdistance — calculate great-circle distances

The `earthdistance` module provides two different approaches to
calculating great circle distances on the surface of the Earth. The one
described first depends on the `cube` module.
The second one is based on the built-in `point` data type,
using longitude and latitude for the coordinates.

In this module, the Earth is assumed to be perfectly spherical.
(If that's too inaccurate for you, you might want to look at the
[PostGIS](https://postgis.net/)
project.)

The `cube` module must be installed
before `earthdistance` can be installed
(although you can use the `CASCADE` option
of `CREATE EXTENSION` to install both in one command).

> **Caution:**

> It is strongly recommended that `earthdistance`
> and `cube` be installed in the same schema, and that
> that schema be one for which CREATE privilege has not been and will not
> be granted to any untrusted users.
> Otherwise there are installation-time security hazards
> if `earthdistance`'s schema contains objects defined
> by a hostile user.
> Furthermore, when using `earthdistance`'s functions
> after installation, the entire search path should contain only trusted
> schemas.
>

### Cube-Based Earth Distances

Data is stored in cubes that are points (both corners are the same) using 3
coordinates representing the x, y, and z distance from the center of the
Earth.  A domain
`earth` over type `cube` is provided, which
includes constraint checks that the value meets these restrictions and
is reasonably close to the actual surface of the Earth.

The radius of the Earth is obtained from the `earth()`
function. It is given in meters. But by changing this one function you can
change the module to use some other units, or to use a different value of
the radius that you feel is more appropriate.

This package has applications to astronomical databases as well.
Astronomers will probably want to change `earth()` to return a
radius of `180/pi()` so that distances are in degrees.

Functions are provided to support input in latitude and longitude (in
degrees), to support output of latitude and longitude, to calculate
the great circle distance between two points and to easily specify a
bounding box usable for index searches.

The provided functions are shown
in [earthdistance-cube-functions](#earthdistance-cube-functions).

| Function                         Description |
| --- |
| `earth` ()         float8                         Returns the assumed radius of the Earth. |
| `sec_to_gc` ( `float8` )         float8                         Converts the normal straight line         (secant) distance between two points on the surface of the Earth         to the great circle distance between them. |
| `gc_to_sec` ( `float8` )         float8                         Converts the great circle distance between two points on the         surface of the Earth to the normal straight line (secant) distance         between them. |
| `ll_to_earth` ( `float8`, `float8` )         earth                         Returns the location of a point on the surface of the Earth given         its latitude (argument 1) and longitude (argument 2) in degrees. |
| `latitude` ( `earth` )         float8                         Returns the latitude in degrees of a point on the surface of the         Earth. |
| `longitude` ( `earth` )         float8                         Returns the longitude in degrees of a point on the surface of the         Earth. |
| `earth_distance` ( `earth`, `earth` )         float8                         Returns the great circle distance between two points on the         surface of the Earth. |
| `earth_box` ( `earth`, `float8` )         cube                         Returns a box suitable for an indexed search using the `cube`         `@>`         operator for points within a given great circle distance of a location.         Some points in this box are further than the specified great circle         distance from the location, so a second check using         `earth_distance` should be included in the query. |

### Point-Based Earth Distances

The second part of the module relies on representing Earth locations as
values of type `point`, in which the first component is taken to
represent longitude in degrees, and the second component is taken to
represent latitude in degrees.  Points are taken as (longitude, latitude)
and not vice versa because longitude is closer to the intuitive idea of
x-axis and latitude to y-axis.

A single operator is provided, shown
in [earthdistance-point-operators](#earthdistance-point-operators).

| Operator                         Description |
| --- |
| `point` `` `point`         float8                         Computes the distance in statute miles between         two points on the Earth's surface. |

Note that unlike the `cube`-based part of the module, units
are hardwired here: changing the `earth()` function will
not affect the results of this operator.

One disadvantage of the longitude/latitude representation is that
you need to be careful about the edge conditions near the poles
and near +/- 180 degrees of longitude.  The `cube`-based
representation avoids these discontinuities.

## fuzzystrmatch — determine string similarities and distance

The `fuzzystrmatch` module provides several
functions to determine similarities and distance between strings.

> **Caution:**

> At present, the `soundex`, `metaphone`,
> `dmetaphone`, and `dmetaphone_alt` functions do
> not work well with multibyte encodings (such as UTF-8).
> Use `daitch_mokotoff`
> or `levenshtein` with such data.
>

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Soundex

The Soundex system is a method of matching similar-sounding names
by converting them to the same code.  It was initially used by the
United States Census in 1880, 1900, and 1910.  Note that Soundex
is not very useful for non-English names.

The `fuzzystrmatch` module provides two functions
for working with Soundex codes:

```
soundex(text) returns text
difference(text, text) returns int
```

The `soundex` function converts a string to its Soundex code.
The `difference` function converts two strings to their Soundex
codes and then reports the number of matching code positions.  Since
Soundex codes have four characters, the result ranges from zero to four,
with zero being no match and four being an exact match.  (Thus, the
function is misnamed — `similarity` would have been
a better name.)

Here are some usage examples:

```
SELECT soundex('hello world!');

SELECT soundex('Anne'), soundex('Ann'), difference('Anne', 'Ann');
SELECT soundex('Anne'), soundex('Andrew'), difference('Anne', 'Andrew');
SELECT soundex('Anne'), soundex('Margaret'), difference('Anne', 'Margaret');

CREATE TABLE s (nm text);

INSERT INTO s VALUES ('john');
INSERT INTO s VALUES ('joan');
INSERT INTO s VALUES ('wobbly');
INSERT INTO s VALUES ('jack');

SELECT * FROM s WHERE soundex(nm) = soundex('john');

SELECT * FROM s WHERE difference(s.nm, 'john') > 2;
```

### Daitch-Mokotoff Soundex

Like the original Soundex system, Daitch-Mokotoff Soundex matches
similar-sounding names by converting them to the same code.
However, Daitch-Mokotoff Soundex is significantly more useful for
non-English names than the original system.
Major improvements over the original system include:

- The code is based on the first six meaningful letters rather than four.
- A letter or combination of letters maps into ten possible codes rather
than seven.
- Where two consecutive letters have a single sound, they are coded as a
single number.
- When a letter or combination of letters may have different sounds,
multiple codes are emitted to cover all possibilities.

This function generates the Daitch-Mokotoff soundex codes for its input:

```
daitch_mokotoff(
source text) returns text[]
```

The result may contain one or more codes depending on how many plausible
pronunciations there are, so it is represented as an array.

Since a Daitch-Mokotoff soundex code consists of only 6 digits,

source should be preferably a single word or name.

Here are some examples:

```
SELECT daitch_mokotoff('George');
daitch_mokotoff
-----------------
{595000}

SELECT daitch_mokotoff('John');
daitch_mokotoff
-----------------
{160000,460000}

SELECT daitch_mokotoff('Bierschbach');
daitch_mokotoff
-----------------------------------------------------------
{794575,794574,794750,794740,745750,745740,747500,747400}

SELECT daitch_mokotoff('Schwartzenegger');
daitch_mokotoff
-----------------
{479465}
```

For matching of single names, returned text arrays can be matched
directly using the `&&` operator: any overlap
can be considered a match.  A GIN index may
be used for efficiency, see [gin](#gin) and this example:

```
CREATE TABLE s (nm text);
CREATE INDEX ix_s_dm ON s USING gin (daitch_mokotoff(nm)) WITH (fastupdate = off);

INSERT INTO s (nm) VALUES
('Schwartzenegger'),
('John'),
('James'),
('Steinman'),
('Steinmetz');

SELECT * FROM s WHERE daitch_mokotoff(nm) && daitch_mokotoff('Swartzenegger');
SELECT * FROM s WHERE daitch_mokotoff(nm) && daitch_mokotoff('Jane');
SELECT * FROM s WHERE daitch_mokotoff(nm) && daitch_mokotoff('Jens');
```

For indexing and matching of any number of names in any order, Full Text
Search features can be used. See [textsearch](#textsearch) and this
example:

```
CREATE FUNCTION soundex_tsvector(v_name text) RETURNS tsvector
BEGIN ATOMIC
SELECT to_tsvector('simple',
string_agg(array_to_string(daitch_mokotoff(n), ' '), ' '))
FROM regexp_split_to_table(v_name, '\s+') AS n;
END;

CREATE FUNCTION soundex_tsquery(v_name text) RETURNS tsquery
BEGIN ATOMIC
SELECT string_agg('(' || array_to_string(daitch_mokotoff(n), '|') || ')', '&')::tsquery
FROM regexp_split_to_table(v_name, '\s+') AS n;
END;

CREATE TABLE s (nm text);
CREATE INDEX ix_s_txt ON s USING gin (soundex_tsvector(nm)) WITH (fastupdate = off);

INSERT INTO s (nm) VALUES
('John Doe'),
('Jane Roe'),
('Public John Q.'),
('George Best'),
('John Yamson');

SELECT * FROM s WHERE soundex_tsvector(nm) @@ soundex_tsquery('john');
SELECT * FROM s WHERE soundex_tsvector(nm) @@ soundex_tsquery('jane doe');
SELECT * FROM s WHERE soundex_tsvector(nm) @@ soundex_tsquery('john public');
SELECT * FROM s WHERE soundex_tsvector(nm) @@ soundex_tsquery('besst, giorgio');
SELECT * FROM s WHERE soundex_tsvector(nm) @@ soundex_tsquery('Jameson John');
```

If it is desired to avoid recalculation of soundex codes during index
rechecks, an index on a separate column can be used instead of an index on
an expression.  A stored generated column can be used for this; see
[ddl-generated-columns](#ddl-generated-columns).

### Levenshtein

This function calculates the Levenshtein distance between two strings:

```
levenshtein(source text, target text, ins_cost int, del_cost int, sub_cost int) returns int
levenshtein(source text, target text) returns int
levenshtein_less_equal(source text, target text, ins_cost int, del_cost int, sub_cost int, max_d int) returns int
levenshtein_less_equal(source text, target text, max_d int) returns int
```

Both `source` and `target` can be any
non-null string, with a maximum of 255 characters.  The cost parameters
specify how much to charge for a character insertion, deletion, or
substitution, respectively.  You can omit the cost parameters, as in
the second version of the function; in that case they all default to 1.

`levenshtein_less_equal` is an accelerated version of the
Levenshtein function for use when only small distances are of interest.
If the actual distance is less than or equal to `max_d`,
then `levenshtein_less_equal` returns the correct
distance; otherwise it returns some value greater than `max_d`.
If `max_d` is negative then the behavior is the same as
`levenshtein`.

Examples:

```
test=# SELECT levenshtein('GUMBO', 'GAMBOL');
levenshtein
-------------
2
(1 row)

test=# SELECT levenshtein('GUMBO', 'GAMBOL', 2, 1, 1);
levenshtein
-------------
3
(1 row)

test=# SELECT levenshtein_less_equal('extensive', 'exhaustive', 2);
levenshtein_less_equal
------------------------
3
(1 row)

test=# SELECT levenshtein_less_equal('extensive', 'exhaustive', 4);
levenshtein_less_equal
------------------------
4
(1 row)
```

### Metaphone

Metaphone, like Soundex, is based on the idea of constructing a
representative code for an input string.  Two strings are then
deemed similar if they have the same codes.

This function calculates the metaphone code of an input string:

```
metaphone(source text, max_output_length int) returns text
```

`source` has to be a non-null string with a maximum of
255 characters.  `max_output_length` sets the maximum
length of the output metaphone code; if longer, the output is truncated
to this length.

Example:

```
test=# SELECT metaphone('GUMBO', 4);
metaphone
-----------
KM
(1 row)
```

### Double Metaphone

The Double Metaphone system computes two "sounds like" strings
for a given input string — a "primary" and an
"alternate".  In most cases they are the same, but for non-English
names especially they can be a bit different, depending on pronunciation.
These functions compute the primary and alternate codes:

```
dmetaphone(source text) returns text
dmetaphone_alt(source text) returns text
```

There is no length limit on the input strings.

Example:

```
test=# SELECT dmetaphone('gumbo');
dmetaphone
------------
KMP
(1 row)
```

## intagg — integer aggregator and enumerator

The `intagg` module provides an integer aggregator and an
enumerator.  `intagg` is now obsolete, because there
are built-in functions that provide a superset of its capabilities.
However, the module is still provided as a compatibility wrapper around
the built-in functions.

### Functions

The aggregator is an aggregate function
`int_array_aggregate(integer)`
that produces an integer array
containing exactly the integers it is fed.
This is a wrapper around `array_agg`,
which does the same thing for any array type.

The enumerator is a function
`int_array_enum(integer[])`
that returns `setof integer`.  It is essentially the reverse
operation of the aggregator: given an array of integers, expand it
into a set of rows.  This is a wrapper around `unnest`,
which does the same thing for any array type.

### Sample Uses

Many database systems have the notion of a one to many table. Such a table
usually sits between two indexed tables, for example:

```
CREATE TABLE left (id INT PRIMARY KEY, ...);
CREATE TABLE right (id INT PRIMARY KEY, ...);
CREATE TABLE one_to_many(left INT REFERENCES left, right INT REFERENCES right);
```

It is typically used like this:

```
SELECT right.* from right JOIN one_to_many ON (right.id = one_to_many.right)
WHERE one_to_many.left = `item`;
```

This will return all the items in the right hand table for an entry
in the left hand table. This is a very common construct in SQL.

Now, this methodology can be cumbersome with a very large number of
entries in the `one_to_many` table.  Often,
a join like this would result in an index scan
and a fetch for each right hand entry in the table for a particular
left hand entry. If you have a very dynamic system, there is not much you
can do. However, if you have some data which is fairly static, you can
create a summary table with the aggregator.

```
CREATE TABLE summary AS
SELECT left, int_array_aggregate(right) AS right
FROM one_to_many
GROUP BY left;
```

This will create a table with one row per left item, and an array
of right items. Now this is pretty useless without some way of using
the array; that's why there is an array enumerator.  You can do

```
SELECT left, int_array_enum(right) FROM summary WHERE left = `item`;
```

The above query using `int_array_enum` produces the same results
as

```
SELECT left, right FROM one_to_many WHERE left = `item`;
```

The difference is that the query against the summary table has to get
only one row from the table, whereas the direct query against
`one_to_many` must index scan and fetch a row for each entry.

On one system, an `EXPLAIN` showed a query with a cost of 8488 was
reduced to a cost of 329.  The original query was a join involving the
`one_to_many` table, which was replaced by:

```
SELECT right, count(right) FROM
( SELECT left, int_array_enum(right) AS right
FROM summary JOIN (SELECT left FROM left_table WHERE left = `item`) AS lefts
ON (summary.left = lefts.left)
) AS list
GROUP BY right
ORDER BY count DESC;
```

## intarray — manipulate arrays of integers

The `intarray` module provides a number of useful functions
and operators for manipulating null-free arrays of integers.
There is also support for indexed searches using some of the operators.

All of these operations will throw an error if a supplied array contains any
NULL elements.

Many of these operations are only sensible for one-dimensional arrays.
Although they will accept input arrays of more dimensions, the data is
treated as though it were a linear array in storage order.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

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

### Benchmark

The source directory `contrib/intarray/bench` contains a
benchmark test suite, which can be run against an installed
PostgreSQL server.  (It also requires `DBD::Pg`
to be installed.)  To run:

```
cd .../contrib/intarray/bench
createdb TEST
psql -c "CREATE EXTENSION intarray" TEST
./create_test.pl | psql TEST
./bench.pl
```

The `bench.pl` script has numerous options, which
are displayed when it is run without any arguments.

### Authors

All work was done by Teodor Sigaev (teodor@sigaev.ru) and
Oleg Bartunov (oleg@sai.msu.su). See
[](http://www.sai.msu.su/~megera/postgres/gist/) for
additional information. Andrey Oktyabrski did a great work on adding new
functions and operations.

## isn — data types for international standard numbers (ISBN, EAN, UPC, etc.)

The `isn` module provides data types for the following
international product numbering standards: EAN13, UPC, ISBN (books), ISMN
(music), and ISSN (serials).  Numbers are validated on input according to a
hard-coded list of prefixes; this list of prefixes is also used to hyphenate
numbers on output.  Since new prefixes are assigned from time to time, the
list of prefixes may be out of date.  It is hoped that a future version of
this module will obtain the prefix list from one or more tables that
can be easily updated by users as needed; however, at present, the
list can only be updated by modifying the source code and recompiling.
Alternatively, prefix validation and hyphenation support may be
dropped from a future version of this module.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Data Types

[isn-datatypes](#isn-datatypes) shows the data types provided by
the `isn` module.

| Data Type | Description |
| --- | --- |
| `EAN13` | European Article Numbers, always displayed in the EAN13 display format |
| `ISBN13` | International Standard Book Numbers to be displayed in        the new EAN13 display format |
| `ISMN13` | International Standard Music Numbers to be displayed in        the new EAN13 display format |
| `ISSN13` | International Standard Serial Numbers to be displayed in the new        EAN13 display format |
| `ISBN` | International Standard Book Numbers to be displayed in the old        short display format |
| `ISMN` | International Standard Music Numbers to be displayed in the        old short display format |
| `ISSN` | International Standard Serial Numbers to be displayed in the        old short display format |
| `UPC` | Universal Product Codes |

Some notes:

1. ISBN13, ISMN13, ISSN13 numbers are all EAN13 numbers.
2. EAN13 numbers aren't always ISBN13, ISMN13 or ISSN13 (some
are).
3. Some ISBN13 numbers can be displayed as ISBN.
4. Some ISMN13 numbers can be displayed as ISMN.
5. Some ISSN13 numbers can be displayed as ISSN.
6. UPC numbers are a subset of the EAN13 numbers (they are basically
EAN13 without the first `0` digit).
7. All UPC, ISBN, ISMN and ISSN numbers can be represented as EAN13
numbers.

Internally, all these types use the same representation (a 64-bit
integer), and all are interchangeable.  Multiple types are provided
to control display formatting and to permit tighter validity checking
of input that is supposed to denote one particular type of number.

The `ISBN`, `ISMN`, and `ISSN` types will display the
short version of the number (ISxN 10) whenever it's possible, and will show
ISxN 13 format for numbers that do not fit in the short version.
The `EAN13`, `ISBN13`, `ISMN13` and
`ISSN13` types will always display the long version of the ISxN
(EAN13).

### Casts

The `isn` module provides the following pairs of type casts:

- ISBN13  EAN13
- ISMN13  EAN13
- ISSN13  EAN13
- ISBN  EAN13
- ISMN  EAN13
- ISSN  EAN13
- UPC   EAN13
- ISBN  ISBN13
- ISMN  ISMN13
- ISSN  ISSN13

When casting from `EAN13` to another type, there is a run-time
check that the value is within the domain of the other type, and an error
is thrown if not.  The other casts are simply relabelings that will
always succeed.

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

### Examples

```
--Using the types directly:
SELECT isbn('978-0-393-04002-9');
SELECT isbn13('0901690546');
SELECT issn('1436-4522');

--Casting types:
-- note that you can only cast from ean13 to another type when the
-- number would be valid in the realm of the target type;
-- thus, the following will NOT work: select isbn(ean13('0220356483481'));
-- but these will:
SELECT upc(ean13('0220356483481'));
SELECT ean13(upc('220356483481'));

--Create a table with a single column to hold ISBN numbers:
CREATE TABLE test (id isbn);
INSERT INTO test VALUES('9780393040029');

--Automatically calculate check digits (observe the '?'):
INSERT INTO test VALUES('220500896?');
INSERT INTO test VALUES('978055215372?');

SELECT issn('3251231?');
SELECT ismn('979047213542?');

--Using the weak mode:
SELECT isn_weak(true);
INSERT INTO test VALUES('978-0-11-000533-4');
INSERT INTO test VALUES('9780141219307');
INSERT INTO test VALUES('2-205-00876-X');
SELECT isn_weak(false);

SELECT id FROM test WHERE NOT is_valid(id);
UPDATE test SET id = make_valid(id) WHERE id = '2-205-00876-X!';

SELECT * FROM test;

SELECT isbn13(id) FROM test;
```

### Bibliography

The information to implement this module was collected from
several sites, including:

- [](https://www.isbn-international.org/)
- [](https://www.issn.org/)
- [](https://www.ismn-international.org/)
- [](https://www.wikipedia.org/)

The prefixes used for hyphenation were also compiled from:

- [](https://www.gs1.org/standards/id-keys)
- [](https://en.wikipedia.org/wiki/List_of_ISBN_identifier_groups)
- [](https://www.isbn-international.org/content/isbn-users-manual/29)
- [](https://en.wikipedia.org/wiki/International_Standard_Music_Number)
- [](https://www.ismn-international.org/ranges/tools)

Care was taken during the creation of the algorithms and they
were meticulously verified against the suggested algorithms
in the official ISBN, ISMN, ISSN User Manuals.

### Author

Germn Mndez Bravo (Kronuz), 2004–2006

This module was inspired by Garrett A. Wollman's
`isbn_issn` code.

## ltree — hierarchical tree-like data type

This module implements a data type `ltree` for representing
labels of data stored in a hierarchical tree-like structure.
Extensive facilities for searching through label trees are provided.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Definitions

A *label* is a sequence of alphanumeric characters,
underscores, and hyphens. Valid alphanumeric character ranges are
dependent on the database locale. For example, in C locale, the characters
`A-Za-z0-9_-` are allowed.
Labels must be no more than 1000 characters long.

Examples: `42`, `Personal_Services`

A *label path* is a sequence of zero or more
labels separated by dots, for example `L1.L2.L3`, representing
a path from the root of a hierarchical tree to a particular node.  The
length of a label path cannot exceed 65535 labels.

Example: `Top.Countries.Europe.Russia`

The `ltree` module provides several data types:

- `ltree` stores a label path.
- `lquery` represents a regular-expression-like pattern
for matching `ltree` values.  A simple word matches that
label within a path.  A star symbol (`*`) matches zero
or more labels.  These can be joined with dots to form a pattern that
must match the whole label path.  For example:

```
foo         Match the exact label path `foo`
*.foo.*     Match any label path containing the label `foo`
*.foo       Match any label path whose last label is `foo`
```

Both star symbols and simple words can be quantified to restrict how many
labels they can match:

```
*{`n`}        Match exactly `n` labels
*{`n`,}       Match at least `n` labels
*{`n`,`m`}      Match at least `n` but not more than `m` labels
*{,`m`}       Match at most `m` labels — same as *{0,`m`}
foo{`n`,`m`}    Match at least `n` but not more than `m` occurrences of `foo`
foo{,}      Match any number of occurrences of `foo`, including zero
```

In the absence of any explicit quantifier, the default for a star symbol
is to match any number of labels (that is, `{,}`) while
the default for a non-star item is to match exactly once (that
is, `{1}`).

There are several modifiers that can be put at the end of a non-star
`lquery` item to make it match more than just the exact match:

```
@           Match case-insensitively, for example `a@` matches `A`
*           Match any label with this prefix, for example `foo*` matches `foobar`
%           Match initial underscore-separated words
```

The behavior of `%` is a bit complicated.  It tries to match
words rather than the entire label.  For example
`foo_bar%` matches `foo_bar_baz` but not
`foo_barbaz`.  If combined with `*`, prefix
matching applies to each word separately, for example
`foo_bar%*` matches `foo1_bar2_baz` but
not `foo1_br2_baz`.

Also, you can write several possibly-modified non-star items separated with
`|` (OR) to match any of those items, and you can put
`!` (NOT) at the start of a non-star group to match any
label that doesn't match any of the alternatives.  A quantifier, if any,
goes at the end of the group; it means some number of matches for the
group as a whole (that is, some number of labels matching or not matching
any of the alternatives).

Here's an annotated example of `lquery`:

```
Top.*{0,2}.sport*@.!football|tennis{1,}.Russ*|Spain
a.  b.     c.      d.                   e.
```

This query will match any label path that:

begins with the label `Top`
- and next has zero to two labels before
- a label beginning with the case-insensitive prefix `sport`
- then has one or more labels, none of which
match `football` nor `tennis`
- and then ends with a label beginning with `Russ` or
exactly matching `Spain`.
- `ltxtquery` represents a full-text-search-like
pattern for matching `ltree` values.  An
`ltxtquery` value contains words, possibly with the
modifiers `@`, `*`, `%` at the end;
the modifiers have the same meanings as in `lquery`.
Words can be combined with `&` (AND),
`|` (OR), `!` (NOT), and parentheses.
The key difference from
`lquery` is that `ltxtquery` matches words without
regard to their position in the label path.

Here's an example `ltxtquery`:

```
Europe & Russia*@ & !Transportation
```

This will match paths that contain the label `Europe` and
any label beginning with `Russia` (case-insensitive),
but not paths containing the label `Transportation`.
The location of these words within the path is not important.
Also, when `%` is used, the word can be matched to any
underscore-separated word within a label, regardless of position.

Note: `ltxtquery` allows whitespace between symbols, but
`ltree` and `lquery` do not.

### Operators and Functions

Type `ltree` has the usual comparison operators
`=`, `<>`,
`<`, `>`, `<=`, `>=`.
Comparison sorts in the order of a tree traversal, with the children
of a node sorted by label text.  In addition, the specialized
operators shown in [ltree-op-table](#ltree-op-table) are available.

| Operator                         Description |
| --- |
| `ltree` `@>` `ltree`         boolean                         Is left argument an ancestor of right (or equal)? |
| `ltree` `` `ltree`         boolean                         `ltree` `` `ltree[]`         boolean                         Does array contain a descendant of `ltree`? |
| `ltree[]` `~` `lquery`         boolean                         `lquery` `~` `ltree[]`         boolean                         Does array contain any path matching `lquery`? |
| `ltree[]` `?` `lquery[]`         boolean                         `lquery[]` `?` `ltree[]`         boolean                         Does `ltree` array contain any path matching         any `lquery`? |
| `ltree[]` `@` `ltxtquery`         boolean                         `ltxtquery` `@` `ltree[]`         boolean                         Does array contain any path matching `ltxtquery`? |
| `ltree[]` `?@>` `ltree`         ltree                         Returns first array entry that is an ancestor of `ltree`,         or `NULL` if none. |
| `ltree[]` `?=`, `>`
- GiST index over `ltree` (`gist_ltree_ops`
opclass):
`=`, `>`,
`@>`, ` ltree[]`,
`@`, `~`, `?`

`gist__ltree_ops` GiST opclass works similarly to
`gist_ltree_ops` and also takes signature length as
a parameter.  The default value of `siglen` in
`gist__ltree_ops` is 28 bytes.

Example of creating such an index with the default signature length of 28 bytes:

```
CREATE INDEX path_gist_idx ON test USING GIST (array_path);
```

Example of creating such an index with a signature length of 100 bytes:

```
CREATE INDEX path_gist_idx ON test USING GIST (array_path gist__ltree_ops(siglen=100));
```

Note: This index type is lossy.

### Example

This example uses the following data (also available in file
`contrib/ltree/ltreetest.sql` in the source distribution):

```
CREATE TABLE test (path ltree);
INSERT INTO test VALUES ('Top');
INSERT INTO test VALUES ('Top.Science');
INSERT INTO test VALUES ('Top.Science.Astronomy');
INSERT INTO test VALUES ('Top.Science.Astronomy.Astrophysics');
INSERT INTO test VALUES ('Top.Science.Astronomy.Cosmology');
INSERT INTO test VALUES ('Top.Hobbies');
INSERT INTO test VALUES ('Top.Hobbies.Amateurs_Astronomy');
INSERT INTO test VALUES ('Top.Collections');
INSERT INTO test VALUES ('Top.Collections.Pictures');
INSERT INTO test VALUES ('Top.Collections.Pictures.Astronomy');
INSERT INTO test VALUES ('Top.Collections.Pictures.Astronomy.Stars');
INSERT INTO test VALUES ('Top.Collections.Pictures.Astronomy.Galaxies');
INSERT INTO test VALUES ('Top.Collections.Pictures.Astronomy.Astronauts');
CREATE INDEX path_gist_idx ON test USING GIST (path);
CREATE INDEX path_idx ON test USING BTREE (path);
```

Now, we have a table `test` populated with data describing
the hierarchy shown below:

```
Top
/   |  \
Science Hobbies Collections
/       |              \
Astronomy   Amateurs_Astronomy Pictures
/  \                            |
Astrophysics  Cosmology                Astronomy
/  |    \
Galaxies Stars Astronauts
```

We can do inheritance:

```
ltreetest=> SELECT path FROM test WHERE path  SELECT path FROM test WHERE path ~ '*.Astronomy.*';
path
-----------------------------------------------
Top.Science.Astronomy
Top.Science.Astronomy.Astrophysics
Top.Science.Astronomy.Cosmology
Top.Collections.Pictures.Astronomy
Top.Collections.Pictures.Astronomy.Stars
Top.Collections.Pictures.Astronomy.Galaxies
Top.Collections.Pictures.Astronomy.Astronauts
(7 rows)

ltreetest=> SELECT path FROM test WHERE path ~ '*.!pictures@.Astronomy.*';
path
------------------------------------
Top.Science.Astronomy
Top.Science.Astronomy.Astrophysics
Top.Science.Astronomy.Cosmology
(3 rows)
```

Here are some examples of full text search:

```
ltreetest=> SELECT path FROM test WHERE path @ 'Astro*% & !pictures@';
path
------------------------------------
Top.Science.Astronomy
Top.Science.Astronomy.Astrophysics
Top.Science.Astronomy.Cosmology
Top.Hobbies.Amateurs_Astronomy
(4 rows)

ltreetest=> SELECT path FROM test WHERE path @ 'Astro* & !pictures@';
path
------------------------------------
Top.Science.Astronomy
Top.Science.Astronomy.Astrophysics
Top.Science.Astronomy.Cosmology
(3 rows)
```

Path construction using functions:

```
ltreetest=> SELECT subpath(path,0,2)||'Space'||subpath(path,2) FROM test WHERE path  SELECT ins_label(path,2,'Space') FROM test WHERE path  **Caution:**

> It is strongly recommended that the transform extension be installed in
> the same schema as `ltree`.  Otherwise there are
> installation-time security hazards if a transform extension's schema
> contains objects defined by a hostile user.
>

### Authors

All work was done by Teodor Sigaev (teodor@stack.net) and
Oleg Bartunov (oleg@sai.msu.su). See
[](http://www.sai.msu.su/~megera/postgres/gist/) for
additional information. Authors would like to thank Eugeny Rodichev for
helpful discussions. Comments and bug reports are welcome.

## seg — a datatype for line segments or floating point intervals

This module implements a data type `seg` for
representing line segments, or floating point intervals.
`seg` can represent uncertainty in the interval endpoints,
making it especially useful for representing laboratory measurements.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Rationale

The geometry of measurements is usually more complex than that of a
point in a numeric continuum. A measurement is usually a segment of
that continuum with somewhat fuzzy limits. The measurements come out
as intervals because of uncertainty and randomness, as well as because
the value being measured may naturally be an interval indicating some
condition, such as the temperature range of stability of a protein.

Using just common sense, it appears more convenient to store such data
as intervals, rather than pairs of numbers. In practice, it even turns
out more efficient in most applications.

Further along the line of common sense, the fuzziness of the limits
suggests that the use of traditional numeric data types leads to a
certain loss of information. Consider this: your instrument reads
6.50, and you input this reading into the database. What do you get
when you fetch it? Watch:

```
test=> select 6.50 :: float8 as "pH";
pH
---
6.5
(1 row)
```

In the world of measurements, 6.50 is not the same as 6.5. It may
sometimes be critically different. The experimenters usually write
down (and publish) the digits they trust. 6.50 is actually a fuzzy
interval contained within a bigger and even fuzzier interval, 6.5,
with their center points being (probably) the only common feature they
share. We definitely do not want such different data items to appear the
same.

Conclusion? It is nice to have a special data type that can record the
limits of an interval with arbitrarily variable precision. Variable in
the sense that each data element records its own precision.

Check this out:

```
test=> select '6.25 .. 6.50'::seg as "pH";
pH
------------
6.25 .. 6.50
(1 row)
```

### Syntax

The external representation of an interval is formed using one or two
floating-point numbers joined by the range operator (`..`
or `...`).  Alternatively, it can be specified as a
center point plus or minus a deviation.
Optional certainty indicators (`<`,
`>` or `~`) can be stored as well.
(Certainty indicators are ignored by all the built-in operators, however.)
[seg-repr-table](#seg-repr-table) gives an overview of allowed
representations; [seg-input-examples](#seg-input-examples) shows some
examples.

In [seg-repr-table](#seg-repr-table), `x`, `y`, and
`delta` denote
floating-point numbers.  `x` and `y`, but
not `delta`, can be preceded by a certainty indicator.

| ``x`` | Single value (zero-length interval) |
| --- | --- |
| ``x` .. `y`` | Interval from `x` to `y` |
| ``x` (+-) `delta`` | Interval from `x` - `delta` to       `x` + `delta` |
| ``x` ..` | Open interval with lower bound `x` |
| `.. `x`` | Open interval with upper bound `x` |

| `5.0` | Creates a zero-length segment (a point, if you will) |
| --- | --- |
| `~5.0` | Creates a zero-length segment and records        `~` in the data.  `~` is ignored        by `seg` operations, but        is preserved as a comment. |
| `5.0` | Creates a point at 5.0.  `>` is ignored but        is preserved as a comment. |
| `5(+-)0.3` | Creates an interval `4.7 .. 5.3`.         Note that the `(+-)` notation isn't preserved. |
| `50 .. ` | Everything that is greater than or equal to 50 |
| `.. 0` | Everything that is less than or equal to 0 |
| `1.5e-2 .. 2E-2 ` | Creates an interval `0.015 .. 0.02` |
| `1 ... 2` | The same as `1...2`, or `1 .. 2`,        or `1..2`        (spaces around the range operator are ignored) |

Because the `...` operator is widely used in data sources, it is allowed
as an alternative spelling of the `..` operator.  Unfortunately, this
creates a parsing ambiguity: it is not clear whether the upper bound
in `0...23` is meant to be `23` or `0.23`.
This is resolved by requiring at least one digit before the decimal
point in all numbers in `seg` input.

As a sanity check, `seg` rejects intervals with the lower bound
greater than the upper, for example `5 .. 2`.

### Precision

`seg` values are stored internally as pairs of 32-bit floating point
numbers. This means that numbers with more than 7 significant digits
will be truncated.

Numbers with 7 or fewer significant digits retain their
original precision. That is, if your query returns 0.00, you will be
sure that the trailing zeroes are not the artifacts of formatting: they
reflect the precision of the original data. The number of leading
zeroes does not affect precision: the value 0.0067 is considered to
have just 2 significant digits.

### Usage

The `seg` module includes a GiST index operator class for
`seg` values.
The operators supported by the GiST operator class are shown in [seg-gist-operators](#seg-gist-operators).

| Operator                         Description |
| --- |
| `seg` `>` `seg`         boolean                         Is the first `seg` entirely to the right of the second?         [a, b] >> [c, d] is true if a > d. |
| `seg` `&` `seg`         boolean                         Does the first `seg` not extend to the left of the         second?         [a, b] &> [c, d] is true if a >= c. |
| `seg` `=` `seg`         boolean                         Are the two `seg`s equal? |
| `seg` `&&` `seg`         boolean                         Do the two `seg`s overlap? |
| `seg` `@>` `seg`         boolean                         Does the first `seg` contain the second? |
| `seg` ` select '10(+-)1'::seg as seg;
seg
---------
9.0 .. 11             -- should be: 9 .. 11
```

The performance of an R-tree index can largely depend on the initial
order of input values. It may be very helpful to sort the input table
on the `seg` column; see the script `sort-segments.pl`
for an example.

### Credits

Original author: Gene Selkov, Jr. selkovjr@mcs.anl.gov,
Mathematics and Computer Science Division, Argonne National Laboratory.

My thanks are primarily to Prof. Joe Hellerstein
([](https://dsf.berkeley.edu/jmh/)) for elucidating the
gist of the GiST ([](http://gist.cs.berkeley.edu/)). I am
also grateful to all Postgres developers, present and past, for enabling
myself to create my own world and live undisturbed in it. And I would like
to acknowledge my gratitude to Argonne Lab and to the U.S. Department of
Energy for the years of faithful support of my database research.

## spi — Server Programming Interface features/examples

The spi module provides several workable examples
of using the [Server Programming Interface](#spi)
(SPI) and triggers.  While these functions are of
some value in
their own right, they are even more useful as examples to modify for
your own purposes.  The functions are general enough to be used
with any table, but you have to specify table and field names (as described
below) while creating a trigger.

Each of the groups of functions described below is provided as a
separately-installable extension.

### refint — Functions for Implementing Referential Integrity

`check_primary_key()` and
`check_foreign_key()` are used to check foreign key constraints.
(This functionality is long since superseded by the built-in foreign
key mechanism, of course, but the module is still useful as an example.)

`check_primary_key()` checks the referencing table.
To use, create a `BEFORE INSERT OR UPDATE` trigger using this
function on a table referencing another table. Specify as the trigger
arguments: the referencing table's column name(s) which form the foreign
key, the referenced table name, and the column names in the referenced table
which form the primary/unique key.  To handle multiple foreign
keys, create a trigger for each reference.

`check_foreign_key()` checks the referenced table.
To use, create a `BEFORE DELETE OR UPDATE` trigger using this
function on a table referenced by other table(s).  Specify as the trigger
arguments: the number of referencing tables for which the function has to
perform checking, the action if a referencing key is found
(`cascade` — to delete the referencing row,
`restrict` — to abort transaction if referencing keys
exist, `setnull` — to set referencing key fields to null),
the triggered table's column names which form the primary/unique key, then
the referencing table name and column names (repeated for as many
referencing tables as were specified by first argument).  Note that the
primary/unique key columns should be marked NOT NULL and should have a
unique index.

There are examples in `refint.example`.

### autoinc — Functions for Autoincrementing Fields

`autoinc()` is a trigger that stores the next value of
a sequence into an integer field.  This has some overlap with the
built-in "serial column" feature, but it is not the same:
`autoinc()` will override attempts to substitute a
different field value during inserts, and optionally it can be
used to increment the field during updates, too.

To use, create a `BEFORE INSERT` (or optionally `BEFORE
INSERT OR UPDATE`) trigger using this function.  Specify two
trigger arguments: the name of the integer column to be modified,
and the name of the sequence object that will supply values.
(Actually, you can specify any number of pairs of such names, if
you'd like to update more than one autoincrementing column.)

There is an example in `autoinc.example`.

### insert_username — Functions for Tracking Who Changed a Table

`insert_username()` is a trigger that stores the current
user's name into a text field.  This can be useful for tracking
who last modified a particular row within a table.

To use, create a `BEFORE INSERT` and/or `UPDATE`
trigger using this function.  Specify a single trigger
argument: the name of the text column to be modified.

There is an example in `insert_username.example`.

### moddatetime — Functions for Tracking Last Modification Time

`moddatetime()` is a trigger that stores the current
time into a `timestamp` field.  This can be useful for tracking
the last modification time of a particular row within a table.

To use, create a `BEFORE UPDATE`
trigger using this function.  Specify a single trigger
argument: the name of the column to be modified.
The column must be of type `timestamp` or `timestamp with
time zone`.

There is an example in `moddatetime.example`.

## tablefunc — functions that return tables (`crosstab` and others)

The `tablefunc` module includes various functions that return
tables (that is, multiple rows).  These functions are useful both in their
own right and as examples of how to write C functions that return
multiple rows.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Functions Provided

[tablefunc-functions](#tablefunc-functions) summarizes the functions provided
by the `tablefunc` module.

| Function                         Description |
| --- |
| `normal_rand` ( numvals `integer`, mean `float8`, stddev `float8` )         setof float8                         Produces a set of normally distributed random values. |
| `crosstab` ( sql `text` )         setof record                         Produces a "pivot table" containing         row names plus `N` value columns, where         `N` is determined by the row type specified         in the calling query. |
| `crosstab`N`` ( sql `text` )         setof table_crosstab_`N`                         Produces a "pivot table" containing         row names plus `N` value columns.         `crosstab2`, `crosstab3`, and         `crosstab4` are predefined, but you can create additional         `crosstab`N`` functions as described below. |
| `crosstab` ( source_sql `text`, category_sql `text` )         setof record                         Produces a "pivot table"         with the value columns specified by a second query. |
| `crosstab` ( sql `text`, N `integer` )         setof record                         Obsolete version of `crosstab(text)`.         The parameter N is now ignored, since the         number of value columns is always determined by the calling query. |
| `connectby` ( relname `text`, keyid_fld `text`, parent_keyid_fld `text`         , orderby_fld `text` , start_with `text`, max_depth `integer`         , branch_delim `text`  )         setof record                         Produces a representation of a hierarchical tree structure. |

#### `normal_rand`

```
normal_rand(int numvals, float8 mean, float8 stddev) returns setof float8
```

`normal_rand` produces a set of normally distributed random
values (Gaussian distribution).

numvals is the number of values to be returned
from the function.
mean is the mean of the normal
distribution of values and
stddev is the standard
deviation of the normal distribution of values.

For example, this call requests 1000 values with a mean of 5 and a
standard deviation of 3:

```
test=# SELECT * FROM normal_rand(1000, 5, 3);
normal_rand
----------------------
1.56556322244898
9.10040991424657
5.36957140345079
-0.369151492880995
0.283600703686639
.
.
.
4.82992125404908
9.71308014517282
2.49639286969028
(1000 rows)
```

#### `crosstab(text)`

```
crosstab(text sql)
crosstab(text sql, int N)
```

The `crosstab` function is used to produce "pivot"
displays, wherein data is listed across the page rather than down.
For example, we might have data like

```
row1    val11
row1    val12
row1    val13
...
row2    val21
row2    val22
row2    val23
...
```

which we wish to display like

```
row1    val11   val12   val13   ...
row2    val21   val22   val23   ...
...
```

The `crosstab` function takes a text parameter that is an SQL
query producing raw data formatted in the first way, and produces a table
formatted in the second way.

The
sql parameter is an SQL statement that produces
the source set of data. This statement must return one
`row_name` column, one
`category` column, and one
`value` column.
N is an
obsolete parameter, ignored if supplied (formerly this had to match the
number of output value columns, but now that is determined by the
calling query).

For example, the provided query might produce a set something like:

```
row_name    cat    value
----------+-------+-------
row1      cat1    val1
row1      cat2    val2
row1      cat3    val3
row1      cat4    val4
row2      cat1    val5
row2      cat2    val6
row2      cat3    val7
row2      cat4    val8
```

The `crosstab` function is declared to return `setof
record`, so the actual names and types of the output columns must be
defined in the `FROM` clause of the calling `SELECT`
statement, for example:

```
SELECT * FROM crosstab('...') AS ct(row_name text, category_1 text, category_2 text);
```

This example produces a set something like:

```

row_name   category_1   category_2
----------+------------+------------
row1        val1         val2
row2        val5         val6
```

The `FROM` clause must define the output as one
`row_name` column (of the same data type as the first result
column of the SQL query) followed by N `value` columns
(all of the same data type as the third result column of the SQL query).
You can set up as many output value columns as you wish.  The names of the
output columns are up to you.

The `crosstab` function produces one output row for each
consecutive group of input rows with the same
`row_name` value.  It fills the output
`value` columns, left to right, with the
`value` fields from these rows.  If there
are fewer rows in a group than there are output `value`
columns, the extra output columns are filled with nulls; if there are
more rows, the extra input rows are skipped.

In practice the SQL query should always specify `ORDER BY 1,2`
to ensure that the input rows are properly ordered, that is, values with
the same `row_name` are brought together and
correctly ordered within the row.  Notice that `crosstab`
itself does not pay any attention to the second column of the query
result; it's just there to be ordered by, to control the order in which
the third-column values appear across the page.

Here is a complete example:

```
CREATE TABLE ct(id SERIAL, rowid TEXT, attribute TEXT, value TEXT);
INSERT INTO ct(rowid, attribute, value) VALUES('test1','att1','val1');
INSERT INTO ct(rowid, attribute, value) VALUES('test1','att2','val2');
INSERT INTO ct(rowid, attribute, value) VALUES('test1','att3','val3');
INSERT INTO ct(rowid, attribute, value) VALUES('test1','att4','val4');
INSERT INTO ct(rowid, attribute, value) VALUES('test2','att1','val5');
INSERT INTO ct(rowid, attribute, value) VALUES('test2','att2','val6');
INSERT INTO ct(rowid, attribute, value) VALUES('test2','att3','val7');
INSERT INTO ct(rowid, attribute, value) VALUES('test2','att4','val8');

SELECT *
FROM crosstab(
'select rowid, attribute, value
from ct
where attribute = ''att2'' or attribute = ''att3''
order by 1,2')
AS ct(row_name text, category_1 text, category_2 text, category_3 text);

row_name | category_1 | category_2 | category_3
----------+------------+------------+------------
test1    | val2       | val3       |
test2    | val6       | val7       |
(2 rows)
```

You can avoid always having to write out a `FROM` clause to
define the output columns, by setting up a custom crosstab function that
has the desired output row type wired into its definition.  This is
described in the next section.  Another possibility is to embed the
required `FROM` clause in a view definition.

> **Note:**

> See also the `[\crosstabview](#app-psql-meta-commands-crosstabview)`
> command in psql, which provides functionality similar
> to `crosstab()`.
>

#### `crosstab`N`(text)`

```
crosstab`N`(text sql)
```

The `crosstab`N`` functions are examples of how
to set up custom wrappers for the general `crosstab` function,
so that you need not write out column names and types in the calling
`SELECT` query.  The `tablefunc` module includes
`crosstab2`, `crosstab3`, and
`crosstab4`, whose output row types are defined as

```
CREATE TYPE tablefunc_crosstab_N AS (
row_name TEXT,
category_1 TEXT,
category_2 TEXT,
.
.
.
category_N TEXT
);
```

Thus, these functions can be used directly when the input query produces
`row_name` and `value` columns of type
`text`, and you want 2, 3, or 4 output values columns.
In all other ways they behave exactly as described above for the
general `crosstab` function.

For instance, the example given in the previous section would also
work as

```
SELECT *
FROM crosstab3(
'select rowid, attribute, value
from ct
where attribute = ''att2'' or attribute = ''att3''
order by 1,2');
```

These functions are provided mostly for illustration purposes. You
can create your own return types and functions based on the
underlying `crosstab()` function.  There are two ways
to do it:

- Create a composite type describing the desired output columns,
similar to the examples in
`contrib/tablefunc/tablefunc--1.0.sql`.
Then define a
unique function name accepting one `text` parameter and returning
`setof your_type_name`, but linking to the same underlying
`crosstab` C function.  For example, if your source data
produces row names that are `text`, and values that are
`float8`, and you want 5 value columns:

```
CREATE TYPE my_crosstab_float8_5_cols AS (
my_row_name text,
my_category_1 float8,
my_category_2 float8,
my_category_3 float8,
my_category_4 float8,
my_category_5 float8
);

CREATE OR REPLACE FUNCTION crosstab_float8_5_cols(text)
RETURNS setof my_crosstab_float8_5_cols
AS '$libdir/tablefunc','crosstab' LANGUAGE C STABLE STRICT;
```
- Use `OUT` parameters to define the return type implicitly.
The same example could also be done this way:

```
CREATE OR REPLACE FUNCTION crosstab_float8_5_cols(
IN text,
OUT my_row_name text,
OUT my_category_1 float8,
OUT my_category_2 float8,
OUT my_category_3 float8,
OUT my_category_4 float8,
OUT my_category_5 float8)
RETURNS setof record
AS '$libdir/tablefunc','crosstab' LANGUAGE C STABLE STRICT;
```

#### `crosstab(text, text)`

```
crosstab(text source_sql, text category_sql)
```

The main limitation of the single-parameter form of `crosstab`
is that it treats all values in a group alike, inserting each value into
the first available column.  If you want the value
columns to correspond to specific categories of data, and some groups
might not have data for some of the categories, that doesn't work well.
The two-parameter form of `crosstab` handles this case by
providing an explicit list of the categories corresponding to the
output columns.

source_sql is an SQL statement that produces the
source set of data.  This statement must return one
`row_name` column, one
`category` column, and one
`value` column. It may also have one or more
"extra" columns.
The `row_name` column must be first. The
`category` and `value`
columns must be the last two columns, in that order.  Any columns between
`row_name` and
`category` are treated as "extra".
The "extra" columns are expected to be the same for all rows
with the same `row_name` value.

For example,
source_sql might produce a set
something like:

```
SELECT row_name, extra_col, cat, value FROM foo ORDER BY 1;

row_name    extra_col   cat    value
----------+------------+-----+---------
row1         extra1    cat1    val1
row1         extra1    cat2    val2
row1         extra1    cat4    val4
row2         extra2    cat1    val5
row2         extra2    cat2    val6
row2         extra2    cat3    val7
row2         extra2    cat4    val8
```

category_sql is an SQL statement that produces
the set of categories. This statement must return only one column.
It must produce at least one row, or an error will be generated.
Also, it must not produce duplicate values, or an error will be
generated.
category_sql might be something like:

```
SELECT DISTINCT cat FROM foo ORDER BY 1;
cat
-------
cat1
cat2
cat3
cat4
```

The `crosstab` function is declared to return `setof
record`, so the actual names and types of the output columns must be
defined in the `FROM` clause of the calling `SELECT`
statement, for example:

```
SELECT * FROM crosstab('...', '...')
AS ct(row_name text, extra text, cat1 text, cat2 text, cat3 text, cat4 text);
```

This will produce a result something like:

```

row_name   extra   cat1   cat2   cat3   cat4
---------+-------+------+------+------+------
row1     extra1  val1   val2          val4
row2     extra2  val5   val6   val7   val8
```

The `FROM` clause must define the proper number of output
columns of the proper data types.  If there are `N`
columns in the
source_sql query's result, the first
`N`-2 of them must match up with the first
`N`-2 output columns.  The remaining output columns
must have the type of the last column of the
source_sql
query's result, and there must be exactly as many of them as there
are rows in the
category_sql query's result.

The `crosstab` function produces one output row for each
consecutive group of input rows with the same
`row_name` value.  The output
`row_name` column, plus any "extra"
columns, are copied from the first row of the group.  The output
`value` columns are filled with the
`value` fields from rows having matching
`category` values.  If a row's `category`
does not match any output of the
category_sql
query, its `value` is ignored.  Output
columns whose matching category is not present in any input row
of the group are filled with nulls.

In practice the
source_sql query should always
specify `ORDER BY 1` to ensure that values with the same
`row_name` are brought together.  However,
ordering of the categories within a group is not important.
Also, it is essential to be sure that the order of the

category_sql query's output matches the specified
output column order.

Here are two complete examples:

```
create table sales(year int, month int, qty int);
insert into sales values(2007, 1, 1000);
insert into sales values(2007, 2, 1500);
insert into sales values(2007, 7, 500);
insert into sales values(2007, 11, 1500);
insert into sales values(2007, 12, 2000);
insert into sales values(2008, 1, 1000);

select * from crosstab(
'select year, month, qty from sales order by 1',
'select m from generate_series(1,12) m'
) as (
year int,
"Jan" int,
"Feb" int,
"Mar" int,
"Apr" int,
"May" int,
"Jun" int,
"Jul" int,
"Aug" int,
"Sep" int,
"Oct" int,
"Nov" int,
"Dec" int
);
year | Jan  | Feb  | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov  | Dec
------+------+------+-----+-----+-----+-----+-----+-----+-----+-----+------+------
2007 | 1000 | 1500 |     |     |     |     | 500 |     |     |     | 1500 | 2000
2008 | 1000 |      |     |     |     |     |     |     |     |     |      |
(2 rows)
```

```
CREATE TABLE cth(rowid text, rowdt timestamp, attribute text, val text);
INSERT INTO cth VALUES('test1','01 March 2003','temperature','42');
INSERT INTO cth VALUES('test1','01 March 2003','test_result','PASS');
INSERT INTO cth VALUES('test1','01 March 2003','volts','2.6987');
INSERT INTO cth VALUES('test2','02 March 2003','temperature','53');
INSERT INTO cth VALUES('test2','02 March 2003','test_result','FAIL');
INSERT INTO cth VALUES('test2','02 March 2003','test_startdate','01 March 2003');
INSERT INTO cth VALUES('test2','02 March 2003','volts','3.1234');

SELECT * FROM crosstab
(
'SELECT rowid, rowdt, attribute, val FROM cth ORDER BY 1',
'SELECT DISTINCT attribute FROM cth ORDER BY 1'
)
AS
(
rowid text,
rowdt timestamp,
temperature int4,
test_result text,
test_startdate timestamp,
volts float8
);
rowid |          rowdt           | temperature | test_result |      test_startdate      | volts
-------+--------------------------+-------------+-------------+--------------------------+--------
test1 | Sat Mar 01 00:00:00 2003 |          42 | PASS        |                          | 2.6987
test2 | Sun Mar 02 00:00:00 2003 |          53 | FAIL        | Sat Mar 01 00:00:00 2003 | 3.1234
(2 rows)
```

You can create predefined functions to avoid having to write out
the result column names and types in each query.  See the examples
in the previous section.  The underlying C function for this form
of `crosstab` is named `crosstab_hash`.

#### `connectby`

```
connectby(text relname, text keyid_fld, text parent_keyid_fld
[, text orderby_fld ], text start_with, int max_depth
[, text branch_delim ])
```

The `connectby` function produces a display of hierarchical
data that is stored in a table.  The table must have a key field that
uniquely identifies rows, and a parent-key field that references the
parent (if any) of each row.  `connectby` can display the
sub-tree descending from any row.

[tablefunc-connectby-parameters](#tablefunc-connectby-parameters) explains the
parameters.

| Parameter | Description |
| --- | --- |
| relname | Name of the source relation |
| keyid_fld | Name of the key field |
| parent_keyid_fld | Name of the parent-key field |
| orderby_fld | Name of the field to order siblings by (optional) |
| start_with | Key value of the row to start at |
| max_depth | Maximum depth to descend to, or zero for unlimited depth |
| branch_delim | String to separate keys with in branch output (optional) |

The key and parent-key fields can be any data type, but they must be
the same type.  Note that the
start_with value must be
entered as a text string, regardless of the type of the key field.

The `connectby` function is declared to return `setof
record`, so the actual names and types of the output columns must be
defined in the `FROM` clause of the calling `SELECT`
statement, for example:

```
SELECT * FROM connectby('connectby_tree', 'keyid', 'parent_keyid', 'pos', 'row2', 0, '~')
AS t(keyid text, parent_keyid text, level int, branch text, pos int);
```

The first two output columns are used for the current row's key and
its parent row's key; they must match the type of the table's key field.
The third output column is the depth in the tree and must be of type
`integer`.  If a
branch_delim parameter was
given, the next output column is the branch display and must be of type
`text`.  Finally, if an
orderby_fld
parameter was given, the last output column is a serial number, and must
be of type `integer`.

The "branch" output column shows the path of keys taken to
reach the current row.  The keys are separated by the specified

branch_delim string.  If no branch display is
wanted, omit both the
branch_delim parameter
and the branch column in the output column list.

If the ordering of siblings of the same parent is important,
include the
orderby_fld parameter to
specify which field to order siblings by.  This field can be of any
sortable data type.  The output column list must include a final
integer serial-number column, if and only if

orderby_fld is specified.

The parameters representing table and field names are copied as-is
into the SQL queries that `connectby` generates internally.
Therefore, include double quotes if the names are mixed-case or contain
special characters.  You may also need to schema-qualify the table name.

In large tables, performance will be poor unless there is an index on
the parent-key field.

It is important that the
branch_delim string
not appear in any key values, else `connectby` may incorrectly
report an infinite-recursion error.  Note that if

branch_delim is not provided, a default value
of `~` is used for recursion detection purposes.

Here is an example:

```
CREATE TABLE connectby_tree(keyid text, parent_keyid text, pos int);

INSERT INTO connectby_tree VALUES('row1',NULL, 0);
INSERT INTO connectby_tree VALUES('row2','row1', 0);
INSERT INTO connectby_tree VALUES('row3','row1', 0);
INSERT INTO connectby_tree VALUES('row4','row2', 1);
INSERT INTO connectby_tree VALUES('row5','row2', 0);
INSERT INTO connectby_tree VALUES('row6','row4', 0);
INSERT INTO connectby_tree VALUES('row7','row3', 0);
INSERT INTO connectby_tree VALUES('row8','row6', 0);
INSERT INTO connectby_tree VALUES('row9','row5', 0);

-- with branch, without orderby_fld (order of results is not guaranteed)
SELECT * FROM connectby('connectby_tree', 'keyid', 'parent_keyid', 'row2', 0, '~')
AS t(keyid text, parent_keyid text, level int, branch text);
keyid | parent_keyid | level |       branch
-------+--------------+-------+---------------------
row2  |              |     0 | row2
row4  | row2         |     1 | row2~row4
row6  | row4         |     2 | row2~row4~row6
row8  | row6         |     3 | row2~row4~row6~row8
row5  | row2         |     1 | row2~row5
row9  | row5         |     2 | row2~row5~row9
(6 rows)

-- without branch, without orderby_fld (order of results is not guaranteed)
SELECT * FROM connectby('connectby_tree', 'keyid', 'parent_keyid', 'row2', 0)
AS t(keyid text, parent_keyid text, level int);
keyid | parent_keyid | level
-------+--------------+-------
row2  |              |     0
row4  | row2         |     1
row6  | row4         |     2
row8  | row6         |     3
row5  | row2         |     1
row9  | row5         |     2
(6 rows)

-- with branch, with orderby_fld (notice that row5 comes before row4)
SELECT * FROM connectby('connectby_tree', 'keyid', 'parent_keyid', 'pos', 'row2', 0, '~')
AS t(keyid text, parent_keyid text, level int, branch text, pos int);
keyid | parent_keyid | level |       branch        | pos
-------+--------------+-------+---------------------+-----
row2  |              |     0 | row2                |   1
row5  | row2         |     1 | row2~row5           |   2
row9  | row5         |     2 | row2~row5~row9      |   3
row4  | row2         |     1 | row2~row4           |   4
row6  | row4         |     2 | row2~row4~row6      |   5
row8  | row6         |     3 | row2~row4~row6~row8 |   6
(6 rows)

-- without branch, with orderby_fld (notice that row5 comes before row4)
SELECT * FROM connectby('connectby_tree', 'keyid', 'parent_keyid', 'pos', 'row2', 0)
AS t(keyid text, parent_keyid text, level int, pos int);
keyid | parent_keyid | level | pos
-------+--------------+-------+-----
row2  |              |     0 |   1
row5  | row2         |     1 |   2
row9  | row5         |     2 |   3
row4  | row2         |     1 |   4
row6  | row4         |     2 |   5
row8  | row6         |     3 |   6
(6 rows)
```

### Author

Joe Conway

## tcn — a trigger function to notify listeners of changes to table content

The `tcn` module provides a trigger function that notifies
listeners of changes to any table on which it is attached.  It must be
used as an `AFTER` trigger `FOR EACH ROW`.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

Only one parameter may be supplied to the function in a
`CREATE TRIGGER` statement, and that is optional.  If supplied
it will be used for the channel name for the notifications.  If omitted
`tcn` will be used for the channel name.

The payload of the notifications consists of the table name, a letter to
indicate which type of operation was performed, and column name/value pairs
for primary key columns.  Each part is separated from the next by a comma.
For ease of parsing using regular expressions, table and column names are
always wrapped in double quotes, and data values are always wrapped in
single quotes.  Embedded quotes are doubled.

A brief example of using the extension follows.

```
test=# create table tcndata
test-#   (
test(#     a int not null,
test(#     b date not null,
test(#     c text,
test(#     primary key (a, b)
test(#   );
CREATE TABLE
test=# create trigger tcndata_tcn_trigger
test-#   after insert or update or delete on tcndata
test-#   for each row execute function triggered_change_notification();
CREATE TRIGGER
test=# listen tcn;
LISTEN
test=# insert into tcndata values (1, date '2012-12-22', 'one'),
test-#                            (1, date '2012-12-23', 'another'),
test-#                            (2, date '2012-12-23', 'two');
INSERT 0 3
Asynchronous notification "tcn" with payload ""tcndata",I,"a"='1',"b"='2012-12-22'" received from server process with PID 22770.
Asynchronous notification "tcn" with payload ""tcndata",I,"a"='1',"b"='2012-12-23'" received from server process with PID 22770.
Asynchronous notification "tcn" with payload ""tcndata",I,"a"='2',"b"='2012-12-23'" received from server process with PID 22770.
test=# update tcndata set c = 'uno' where a = 1;
UPDATE 2
Asynchronous notification "tcn" with payload ""tcndata",U,"a"='1',"b"='2012-12-22'" received from server process with PID 22770.
Asynchronous notification "tcn" with payload ""tcndata",U,"a"='1',"b"='2012-12-23'" received from server process with PID 22770.
test=# delete from tcndata where a = 1 and b = date '2012-12-22';
DELETE 1
Asynchronous notification "tcn" with payload ""tcndata",D,"a"='1',"b"='2012-12-22'" received from server process with PID 22770.
```

## tsm_system_rows —
the `SYSTEM_ROWS` sampling method for `TABLESAMPLE`

The `tsm_system_rows` module provides the table sampling method
`SYSTEM_ROWS`, which can be used in
the `TABLESAMPLE` clause of a [`SELECT`](#sql-select)
command.

This table sampling method accepts a single integer argument that is the
maximum number of rows to read.  The resulting sample will always contain
exactly that many rows, unless the table does not contain enough rows, in
which case the whole table is selected.

Like the built-in `SYSTEM` sampling
method, `SYSTEM_ROWS` performs block-level sampling, so
that the sample is not completely random but may be subject to clustering
effects, especially if only a small number of rows are requested.

`SYSTEM_ROWS` does not support
the `REPEATABLE` clause.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Examples

Here is an example of selecting a sample of a table with
`SYSTEM_ROWS`.  First install the extension:

```
CREATE EXTENSION tsm_system_rows;
```

Then you can use it in a `SELECT` command, for instance:

```
SELECT * FROM my_table TABLESAMPLE SYSTEM_ROWS(100);
```

This command will return a sample of 100 rows from the
table `my_table` (unless the table does not have 100
visible rows, in which case all its rows are returned).

## tsm_system_time —
the `SYSTEM_TIME` sampling method for `TABLESAMPLE`

The `tsm_system_time` module provides the table sampling method
`SYSTEM_TIME`, which can be used in
the `TABLESAMPLE` clause of a [`SELECT`](#sql-select)
command.

This table sampling method accepts a single floating-point argument that
is the maximum number of milliseconds to spend reading the table.  This
gives you direct control over how long the query takes, at the price that
the size of the sample becomes hard to predict.  The resulting sample will
contain as many rows as could be read in the specified time, unless the
whole table has been read first.

Like the built-in `SYSTEM` sampling
method, `SYSTEM_TIME` performs block-level sampling, so
that the sample is not completely random but may be subject to clustering
effects, especially if only a small number of rows are selected.

`SYSTEM_TIME` does not support
the `REPEATABLE` clause.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### Examples

Here is an example of selecting a sample of a table with
`SYSTEM_TIME`.  First install the extension:

```
CREATE EXTENSION tsm_system_time;
```

Then you can use it in a `SELECT` command, for instance:

```
SELECT * FROM my_table TABLESAMPLE SYSTEM_TIME(1000);
```

This command will return as large a sample of `my_table` as
it can read in 1 second (1000 milliseconds).  Of course, if the whole
table can be read in under 1 second, all its rows will be returned.

## uuid-ossp — a UUID generator

The `uuid-ossp` module provides functions to generate universally
unique identifiers (UUIDs) using one of several standard algorithms.  There
are also functions to produce certain special UUID constants.
This module is only necessary for special requirements beyond what is
available in core PostgreSQL.  See [functions-uuid](#functions-uuid) for built-in ways to generate UUIDs.

This module is considered "trusted", that is, it can be
installed by non-superusers who have `CREATE` privilege
on the current database.

### `uuid-ossp` Functions

[uuid-ossp-functions](#uuid-ossp-functions) shows the functions available to
generate UUIDs.
The relevant standards ITU-T Rec. X.667, ISO/IEC 9834-8:2005, and
[RFC 4122](https://datatracker.ietf.org/doc/html/rfc4122)
specify four algorithms for generating UUIDs, identified by the
version numbers 1, 3, 4, and 5.  (There is no version 2 algorithm.)
Each of these algorithms could be suitable for a different set of
applications.

| Function                         Description |
| --- |
| `uuid_generate_v1` ()         uuid                         Generates a version 1 UUID.  This involves the MAC         address of the computer and a time stamp.  Note that UUIDs of this         kind reveal the identity of the computer that created the identifier         and the time at which it did so, which might make it unsuitable for         certain security-sensitive applications. |
| `uuid_generate_v1mc` ()         uuid                         Generates a version 1 UUID, but uses a random multicast         MAC address instead of the real MAC address of the computer. |
| `uuid_generate_v3` ( namespace `uuid`, name `text` )         uuid                         Generates a version 3 UUID in the given namespace using         the specified input name.  The namespace should be one of the special         constants produced by the `uuid_ns_*()` functions         shown in [uuid-ossp-constants](#uuid-ossp-constants).  (It could be any UUID         in theory.)  The name is an identifier in the selected namespace.                         For example:   ``` SELECT uuid_generate_v3(uuid_ns_url(), 'http://www.postgresql.org'); ```           The name parameter will be MD5-hashed, so the cleartext cannot be         derived from the generated UUID.         The generation of UUIDs by this method has no random or         environment-dependent element and is therefore reproducible. |
| `uuid_generate_v4` ()         uuid                         Generates a version 4 UUID, which is derived entirely         from random numbers. |
| `uuid_generate_v5` ( namespace `uuid`, name `text` )         uuid                         Generates a version 5 UUID, which works like a version 3         UUID except that SHA-1 is used as a hashing method.  Version 5 should         be preferred over version 3 because SHA-1 is thought to be more secure         than MD5. |

| Function                         Description |
| --- |
| `uuid_nil` ()         uuid                         Returns a "nil" UUID constant, which does not occur as a         real UUID. |
| `uuid_ns_dns` ()         uuid                         Returns a constant designating the DNS namespace for UUIDs. |
| `uuid_ns_url` ()         uuid                         Returns a constant designating the URL namespace for UUIDs. |
| `uuid_ns_oid` ()         uuid                         Returns a constant designating the ISO object identifier (OID) namespace for         UUIDs.  (This pertains to ASN.1 OIDs, which are unrelated to the OIDs         used in PostgreSQL.) |
| `uuid_ns_x500` ()         uuid                         Returns a constant designating the X.500 distinguished name (DN)         namespace for UUIDs. |

### Building `uuid-ossp`

Historically this module depended on the OSSP UUID library, which accounts
for the module's name.  While the OSSP UUID library can still be found
at [](http://www.ossp.org/pkg/lib/uuid/), it is not well
maintained, and is becoming increasingly difficult to port to newer
platforms.  `uuid-ossp` can now be built without the OSSP
library on some platforms.  On FreeBSD and some other BSD-derived
platforms, suitable UUID creation functions are included in the
core `libc` library.  On Linux, macOS, and some other
platforms, suitable functions are provided in the `libuuid`
library, which originally came from the `e2fsprogs` project
(though on modern Linux it is considered part
of `util-linux-ng`).  When invoking `configure`,
specify --with-uuid=bsd` to use the BSD functions,
or `--with-uuid=e2fs` to
use `e2fsprogs`' `libuuid`, or
`--with-uuid=ossp` to use the OSSP UUID library.
More than one of these libraries might be available on a particular
machine, so `configure` does not automatically choose one.

### Author

Peter Eisentraut peter_e@gmx.net

## xml2 — XPath querying and XSLT functionality

The `xml2` module provides XPath querying and
XSLT functionality.

### Deprecation Notice

From PostgreSQL 8.3 on, there is XML-related
functionality based on the SQL/XML standard in the core server.
That functionality covers XML syntax checking and XPath queries,
which is what this module does, and more, but the API is
not at all compatible.  It is planned that this module will be
removed in a future version of PostgreSQL in favor of the newer standard API, so
you are encouraged to try converting your applications.  If you
find that some of the functionality of this module is not
available in an adequate form with the newer API, please explain
your issue to pgsql-hackers@lists.postgresql.org so that the deficiency
can be addressed.

### Description of Functions

[xml2-functions-table](#xml2-functions-table) shows the functions provided by this module.
These functions provide straightforward XML parsing and XPath queries.

| Function                         Description |
| --- |
| `xml_valid` ( document `text` )         boolean                         Parses the given document and returns true if the         document is well-formed XML.  (Note: this is an alias for the standard         PostgreSQL function `xml_is_well_formed()`.  The         name `xml_valid()` is technically incorrect since validity         and well-formedness have different meanings in XML.) |
| `xpath_string` ( document `text`, query `text` )         text                         Evaluates the XPath query on the supplied document, and         casts the result to `text`. |
| `xpath_number` ( document `text`, query `text` )         real                         Evaluates the XPath query on the supplied document, and         casts the result to `real`. |
| `xpath_bool` ( document `text`, query `text` )         boolean                         Evaluates the XPath query on the supplied document, and         casts the result to `boolean`. |
| `xpath_nodeset` ( document `text`, query `text`, toptag `text`, itemtag `text` )         text                         Evaluates the query on the document and wraps the result in XML         tags. If the result is multivalued, the output will look like:  ```  Value 1 which could be an XML fragment Value 2....  ```          If either toptag         or itemtag is an empty string, the relevant tag         is omitted. |
| `xpath_nodeset` ( document `text`, query `text`, itemtag `text` )         text                         Like `xpath_nodeset(document, query, toptag, itemtag)` but result omits toptag. |
| `xpath_nodeset` ( document `text`, query `text` )         text                         Like `xpath_nodeset(document, query, toptag, itemtag)` but result omits both tags. |
| `xpath_list` ( document `text`, query `text`, separator `text` )         text                         Evaluates the query on the document and returns multiple values         separated by the specified separator, for example `Value         1,Value 2,Value 3` if separator         is `,`. |
| `xpath_list` ( document `text`, query `text` )         text                         This is a wrapper for the above function that uses `,`         as the separator. |

### `xpath_table`

```
xpath_table(text key, text document, text relation, text xpaths, text criteria) returns setof record
```

`xpath_table` is a table function that evaluates a set of XPath
queries on each of a set of documents and returns the results as a
table. The primary key field from the original document table is returned
as the first column of the result so that the result set
can readily be used in joins.  The parameters are described in
[xml2-xpath-table-parameters](#xml2-xpath-table-parameters).

| Parameter | Description |
| --- | --- |
| key | the name of the "key" field — this is just a field to be used as         the first column of the output table, i.e., it identifies the record from         which each output row came (see note below about multiple values) |
| document | the name of the field containing the XML document |
| relation | the name of the table or view containing the documents |
| xpaths | one or more XPath expressions, separated by `|` |
| criteria | the contents of the WHERE clause. This cannot be omitted, so use         `true` or `1=1` if you want to         process all the rows in the relation |

These parameters (except the XPath strings) are just substituted
into a plain SQL SELECT statement, so you have some flexibility — the
statement is

`
SELECT <key>, <document> FROM <relation> WHERE <criteria>
`

so those parameters can be *anything* valid in those particular
locations. The result from this SELECT needs to return exactly two
columns (which it will unless you try to list multiple fields for key
or document). Beware that this simplistic approach requires that you
validate any user-supplied values to avoid SQL injection attacks.

The function has to be used in a `FROM` expression, with an
`AS` clause to specify the output columns; for example

```
SELECT * FROM
xpath_table('article_id',
'article_xml',
'articles',
'/article/author|/article/pages|/article/title',
'date_entered > ''2003-01-01'' ')
AS t(article_id integer, author text, page_count integer, title text);
```

The `AS` clause defines the names and types of the columns in the
output table.  The first is the "key" field and the rest correspond
to the XPath queries.
If there are more XPath queries than result columns,
the extra queries will be ignored. If there are more result columns
than XPath queries, the extra columns will be NULL.

Notice that this example defines the `page_count` result
column as an integer.  The function deals internally with string
representations, so when you say you want an integer in the output, it will
take the string representation of the XPath result and use PostgreSQL input
functions to transform it into an integer (or whatever type the `AS`
clause requests). An error will result if it can't do this — for
example if the result is empty — so you may wish to just stick to
`text` as the column type if you think your data has any problems.

The calling `SELECT` statement doesn't necessarily have to be
just `SELECT *` — it can reference the output
columns by name or join them to other tables. The function produces a
virtual table with which you can perform any operation you wish (e.g.,
aggregation, joining, sorting etc.). So we could also have:

```
SELECT t.title, p.fullname, p.email
FROM xpath_table('article_id', 'article_xml', 'articles',
'/article/title|/article/author/@id',
'xpath_string(article_xml,''/article/@date'') > ''2003-03-20'' ')
AS t(article_id integer, title text, author_id integer),
tblPeopleInfo AS p
WHERE t.author_id = p.person_id;
```

as a more complicated example. Of course, you could wrap all
of this in a view for convenience.

#### Multivalued Results

The `xpath_table` function assumes that the results of each XPath query
might be multivalued, so the number of rows returned by the function
may not be the same as the number of input documents. The first row
returned contains the first result from each query, the second row the
second result from each query. If one of the queries has fewer values
than the others, null values will be returned instead.

In some cases, a user will know that a given XPath query will return
only a single result (perhaps a unique document identifier) — if used
alongside an XPath query returning multiple results, the single-valued
result will appear only on the first row of the result. The solution
to this is to use the key field as part of a join against a simpler
XPath query. As an example:

```
CREATE TABLE test (
id int PRIMARY KEY,
xml text
);

INSERT INTO test VALUES (1, '
123
112233
');

INSERT INTO test VALUES (2, '
111222333
111222333
');

SELECT * FROM
xpath_table('id','xml','test',
'/doc/@num|/doc/line/@num|/doc/line/a|/doc/line/b|/doc/line/c',
'true')
AS t(id int, doc_num varchar(10), line_num varchar(10), val1 int, val2 int, val3 int)
WHERE id = 1 ORDER BY doc_num, line_num

id | doc_num | line_num | val1 | val2 | val3
----+---------+----------+------+------+------
1 | C1      | L1       |    1 |    2 |    3
1 |         | L2       |   11 |   22 |   33
```

To get `doc_num` on every line, the solution is to use two invocations
of `xpath_table` and join the results:

```
SELECT t.*,i.doc_num FROM
xpath_table('id', 'xml', 'test',
'/doc/line/@num|/doc/line/a|/doc/line/b|/doc/line/c',
'true')
AS t(id int, line_num varchar(10), val1 int, val2 int, val3 int),
xpath_table('id', 'xml', 'test', '/doc/@num', 'true')
AS i(id int, doc_num varchar(10))
WHERE i.id=t.id AND i.id=1
ORDER BY doc_num, line_num;

id | line_num | val1 | val2 | val3 | doc_num
----+----------+------+------+------+---------
1 | L1       |    1 |    2 |    3 | C1
1 | L2       |   11 |   22 |   33 | C1
(2 rows)
```

### XSLT Functions

The following functions are available if libxslt is installed:

#### `xslt_process`

```
xslt_process(text document, text stylesheet, text paramlist) returns text
```

This function applies the XSL stylesheet to the document and returns
the transformed result. The `paramlist` is a list of parameter
assignments to be used in the transformation, specified in the form
`a=1,b=2`. Note that the
parameter parsing is very simple-minded: parameter values cannot
contain commas!

There is also a two-parameter version of `xslt_process` which
does not pass any parameters to the transformation.

### Author

John Gray jgray@azuli.co.uk

Development of this module was sponsored by Torchbox Ltd. (www.torchbox.com).
It has the same BSD license as PostgreSQL.
