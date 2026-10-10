# Indexing

## Knowledge Metadata

- Knowledge Type: `solution`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/05_data_types.md`
- Source Title: `Data Types`
- Source Heading Path: `Data Types > Range Types > Indexing`
- Source Line Ranges: `2778-2987, 4340-4800`
- Chunk ID: `pg16_solution_0100_710b6350f5`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ebd4f0be5dc0c1504606c8eab23ff5c4fb9ea3b9607f59a889a9ceb0d0fdcb9f`

## Retrieval Guidance

- Use When: Root cause is slow range containment or overlap queries.
- Retrieval Keywords: range index, GiST, SP-GiST, multirange, overlap operator, range query
- Follow-up Guidance: Choose index type based on operator support and verify plan usage with EXPLAIN.
- Classification Note: Recommends GiST and SP-GiST indexes for range operators and multirange operations.

## Official Source Content

### `jsonb` Indexing

GIN indexes can be used to efficiently search for
keys or key/value pairs occurring within a large number of
`jsonb` documents (datums).
Two GIN "operator classes" are provided, offering different
performance and flexibility trade-offs.

The default GIN operator class for `jsonb` supports queries with
the key-exists operators `?`, `?|`
and `?&`, the containment operator
`@>`, and the `jsonpath` match
operators `@?` and `@@`.
(For details of the semantics that these operators
implement, see [functions-jsonb-op-table](#functions-jsonb-op-table).)
An example of creating an index with this operator class is:

```
CREATE INDEX idxgin ON api USING GIN (jdoc);
```

The non-default GIN operator class `jsonb_path_ops`
does not support the key-exists operators, but it does support
`@>`, `@?` and `@@`.
An example of creating an index with this operator class is:

```
CREATE INDEX idxginp ON api USING GIN (jdoc jsonb_path_ops);
```

Consider the example of a table that stores JSON documents
retrieved from a third-party web service, with a documented schema
definition.  A typical document is:

```
{
"guid": "9c36adc1-7fb5-4d5b-83b4-90356a46061a",
"name": "Angela Barton",
"is_active": true,
"company": "Magnafone",
"address": "178 Howard Place, Gulf, Washington, 702",
"registered": "2009-11-07T08:53:22 +08:00",
"latitude": 19.793713,
"longitude": 86.513373,
"tags": [
"enim",
"aliquip",
"qui"
]
}
```

We store these documents in a table named `api`,
in a `jsonb` column named `jdoc`.
If a GIN index is created on this column,
queries like the following can make use of the index:

```
-- Find documents in which the key "company" has value "Magnafone"
SELECT jdoc->'guid', jdoc->'name' FROM api WHERE jdoc @> '{"company": "Magnafone"}';
```

However, the index could not be used for queries like the
following, because though the operator `?` is indexable,
it is not applied directly to the indexed column `jdoc`:

```
-- Find documents in which the key "tags" contains key or array element "qui"
SELECT jdoc->'guid', jdoc->'name' FROM api WHERE jdoc -> 'tags' ? 'qui';
```

Still, with appropriate use of expression indexes, the above
query can use an index.  If querying for particular items within
the `"tags"` key is common, defining an index like this
may be worthwhile:

```
CREATE INDEX idxgintags ON api USING GIN ((jdoc -> 'tags'));
```

Now, the `WHERE` clause `jdoc -> 'tags' ? 'qui'`
will be recognized as an application of the indexable
operator `?` to the indexed
expression `jdoc -> 'tags'`.
(More information on expression indexes can be found in [indexes-expressional](#indexes-expressional).)

Another approach to querying is to exploit containment, for example:

```
-- Find documents in which the key "tags" contains array element "qui"
SELECT jdoc->'guid', jdoc->'name' FROM api WHERE jdoc @> '{"tags": ["qui"]}';
```

A simple GIN index on the `jdoc` column can support this
query.  But note that such an index will store copies of every key and
value in the `jdoc` column, whereas the expression index
of the previous example stores only data found under
the `tags` key.  While the simple-index approach is far more
flexible (since it supports queries about any key), targeted expression
indexes are likely to be smaller and faster to search than a simple
index.

GIN indexes also support the `@?`
and `@@` operators, which
perform `jsonpath` matching.  Examples are

```
SELECT jdoc->'guid', jdoc->'name' FROM api WHERE jdoc @? '$.tags[*] ? (@ == "qui")';
```

```
SELECT jdoc->'guid', jdoc->'name' FROM api WHERE jdoc @@ '$.tags[*] == "qui"';
```

For these operators, a GIN index extracts clauses of the form
``accessors_chain`
= `constant`` out of
the `jsonpath` pattern, and does the index search based on
the keys and values mentioned in these clauses.  The accessors chain
may include `.`key``,
`[*]`,
and `[`index`]` accessors.
The `jsonb_ops` operator class also
supports `.*` and `.**` accessors,
but the `jsonb_path_ops` operator class does not.

Although the `jsonb_path_ops` operator class supports
only queries with the `@>`, `@?`
and `@@` operators, it has notable
performance advantages over the default operator
class `jsonb_ops`.  A `jsonb_path_ops`
index is usually much smaller than a `jsonb_ops`
index over the same data, and the specificity of searches is better,
particularly when queries contain keys that appear frequently in the
data.  Therefore search operations typically perform better
than with the default operator class.

The technical difference between a `jsonb_ops`
and a `jsonb_path_ops` GIN index is that the former
creates independent index items for each key and value in the data,
while the latter creates index items only for each value in the
data.
(Note: For this purpose, the term "value" includes array elements,
though JSON terminology sometimes considers array elements distinct
from values within objects.)
Basically, each `jsonb_path_ops` index item is
a hash of the value and the key(s) leading to it; for example to index
`{"foo": {"bar": "baz"}}`, a single index item would
be created incorporating all three of `foo`, `bar`,
and `baz` into the hash value.  Thus a containment query
looking for this structure would result in an extremely specific index
search; but there is no way at all to find out whether `foo`
appears as a key.  On the other hand, a `jsonb_ops`
index would create three index items representing `foo`,
`bar`, and `baz` separately; then to do the
containment query, it would look for rows containing all three of
these items.  While GIN indexes can perform such an AND search fairly
efficiently, it will still be less specific and slower than the
equivalent `jsonb_path_ops` search, especially if
there are a very large number of rows containing any single one of the
three index items.

A disadvantage of the `jsonb_path_ops` approach is
that it produces no index entries for JSON structures not containing
any values, such as `{"a": {}}`.  If a search for
documents containing such a structure is requested, it will require a
full-index scan, which is quite slow.  `jsonb_path_ops` is
therefore ill-suited for applications that often perform such searches.

`jsonb` also supports `btree` and `hash`
indexes.  These are usually useful only if it's important to check
equality of complete JSON documents.
The `btree` ordering for `jsonb` datums is seldom
of great interest, but for completeness it is:

```
`Object` > `Array` > `Boolean` > `Number` > `String` > `null`

`Object with n pairs` > `object with n - 1 pairs`

`Array with n elements` > `array with n - 1 elements`
```

with the exception that (for historical reasons) an empty top level array sorts less than `null`.
Objects with equal numbers of pairs are compared in the order:

```
`key-1`, `value-1`, `key-2` ...
```

Note that object keys are compared in their storage order;
in particular, since shorter keys are stored before longer keys, this
can lead to results that might be unintuitive, such as:

```
{ "aa": 1, "c": 1} > {"b": 1, "d": 1}
```

Similarly, arrays with equal numbers of elements are compared in the
order:

```
`element-1`, `element-2` ...
```

Primitive JSON values are compared using the same
comparison rules as for the underlying
PostgreSQL data type.  Strings are
compared using the default database collation.

## Range Types

Range types are data types representing a range of values of some
element type (called the range's *subtype*).
For instance, ranges
of `timestamp` might be used to represent the ranges of
time that a meeting room is reserved. In this case the data type
is `tsrange` (short for "timestamp range"),
and `timestamp` is the subtype.  The subtype must have
a total order so that it is well-defined whether element values are
within, before, or after a range of values.

Range types are useful because they represent many element values in a
single range value, and because concepts such as overlapping ranges can
be expressed clearly. The use of time and date ranges for scheduling
purposes is the clearest example; but price ranges, measurement
ranges from an instrument, and so forth can also be useful.

Every range type has a corresponding multirange type. A multirange is
an ordered list of non-contiguous, non-empty, non-null ranges. Most
range operators also work on multiranges, and they have a few functions
of their own.

### Built-in Range and Multirange Types

PostgreSQL comes with the following built-in range types:

- `int4range` — Range of `integer`,
`int4multirange` — corresponding Multirange
- `int8range` — Range of `bigint`,
`int8multirange` — corresponding Multirange
- `numrange` — Range of `numeric`,
`nummultirange` — corresponding Multirange
- `tsrange` — Range of `timestamp without time zone`,
`tsmultirange` — corresponding Multirange
- `tstzrange` — Range of `timestamp with time zone`,
`tstzmultirange` — corresponding Multirange
- `daterange` — Range of `date`,
`datemultirange` — corresponding Multirange

In addition, you can define your own range types;
see [sql-createtype](#sql-createtype) for more information.

### Examples

```
CREATE TABLE reservation (room int, during tsrange);
INSERT INTO reservation VALUES
(1108, '[2010-01-01 14:30, 2010-01-01 15:30)');

-- Containment
SELECT int4range(10, 20) @> 3;

-- Overlaps
SELECT numrange(11.1, 22.2) && numrange(20.0, 30.0);

-- Extract the upper bound
SELECT upper(int8range(15, 25));

-- Compute the intersection
SELECT int4range(10, 20) * int4range(15, 25);

-- Is the range empty?
SELECT isempty(numrange(1, 5));
```

See [range-operators-table](#range-operators-table)
and [range-functions-table](#range-functions-table) for complete lists of
operators and functions on range types.

### Inclusive and Exclusive Bounds

Every non-empty range has two bounds, the lower bound and the upper
bound. All points between these values are included in the range. An
inclusive bound means that the boundary point itself is included in
the range as well, while an exclusive bound means that the boundary
point is not included in the range.

In the text form of a range, an inclusive lower bound is represented by
"`[`" while an exclusive lower bound is
represented by "`(`". Likewise, an inclusive upper bound is represented by
"`]`", while an exclusive upper bound is
represented by "`)`".
(See [rangetypes-io](#rangetypes-io) for more details.)

The functions `lower_inc`
and `upper_inc` test the inclusivity of the lower
and upper bounds of a range value, respectively.

### Infinite (Unbounded) Ranges

The lower bound of a range can be omitted, meaning that all
values less than the upper bound are included in the range, e.g.,
`(,3]`. Likewise, if the upper bound of the range
is omitted, then all values greater than the lower bound are included
in the range. If both lower and upper bounds are omitted, all values
of the element type are considered to be in the range.  Specifying a
missing bound as inclusive is automatically converted to exclusive,
e.g., `[,]` is converted to `(,)`.
You can think of these missing values as +/-infinity, but they are
special range type values and are considered to be beyond any range
element type's +/-infinity values.

Element types that have the notion of "infinity" can
use them as explicit bound values.  For example, with timestamp
ranges, `[today,infinity)` excludes the special
`timestamp` value `infinity`,
while `[today,infinity]` include it, as does
`[today,)` and `[today,]`.

The functions `lower_inf`
and `upper_inf` test for infinite lower
and upper bounds of a range, respectively.

### Range Input/Output

The input for a range value must follow one of the following patterns:

```
(`lower-bound`,`upper-bound`)
(`lower-bound`,`upper-bound`]
[`lower-bound`,`upper-bound`)
[`lower-bound`,`upper-bound`]
empty
```

The parentheses or brackets indicate whether the lower and upper bounds
are exclusive or inclusive, as described previously.
Notice that the final pattern is `empty`, which
represents an empty range (a range that contains no points).

The `lower-bound` may be either a string
that is valid input for the subtype, or empty to indicate no
lower bound.  Likewise, `upper-bound` may be
either a string that is valid input for the subtype, or empty to
indicate no upper bound.

Each bound value can be quoted using `"` (double quote)
characters.  This is necessary if the bound value contains parentheses,
brackets, commas, double quotes, or backslashes, since these characters
would otherwise be taken as part of the range syntax.  To put a double
quote or backslash in a quoted bound value, precede it with a
backslash. (Also, a pair of double quotes within a double-quoted bound
value is taken to represent a double quote character, analogously to the
rules for single quotes in SQL literal strings.) Alternatively, you can
avoid quoting and use backslash-escaping to protect all data characters
that would otherwise be taken as range syntax.  Also, to write a bound
value that is an empty string, write `""`, since writing
nothing means an infinite bound.

Whitespace is allowed before and after the range value, but any whitespace
between the parentheses or brackets is taken as part of the lower or upper
bound value.  (Depending on the element type, it might or might not be
significant.)

> **Note:**

> These rules are very similar to those for writing field values in
> composite-type literals.  See [rowtypes-io-syntax](#rowtypes-io-syntax) for
> additional commentary.
>

Examples:

```
-- includes 3, does not include 7, and does include all points in between
SELECT '[3,7)'::int4range;

-- does not include either 3 or 7, but includes all points in between
SELECT '(3,7)'::int4range;

-- includes only the single point 4
SELECT '[4,4]'::int4range;

-- includes no points (and will be normalized to 'empty')
SELECT '[4,4)'::int4range;
```

The input for a multirange is curly brackets (`{` and
`}`) containing zero or more valid ranges,
separated by commas. Whitespace is permitted around the brackets and
commas. This is intended to be reminiscent of array syntax, although
multiranges are much simpler: they have just one dimension and there is
no need to quote their contents. (The bounds of their ranges may be
quoted as above however.)

Examples:

```
SELECT '{}'::int4multirange;
SELECT '{[3,7)}'::int4multirange;
SELECT '{[3,7), [8,9)}'::int4multirange;
```

### Constructing Ranges and Multiranges

Each range type has a constructor function with the same name as the range
type.  Using the constructor function is frequently more convenient than
writing a range literal constant, since it avoids the need for extra
quoting of the bound values.  The constructor function
accepts two or three arguments.  The two-argument form constructs a range
in standard form (lower bound inclusive, upper bound exclusive), while
the three-argument form constructs a range with bounds of the form
specified by the third argument.
The third argument must be one of the strings
"`()`",
"`(]`",
"`[)`", or
"`[]`".
For example:

```
-- The full form is: lower bound, upper bound, and text argument indicating
-- inclusivity/exclusivity of bounds.
SELECT numrange(1.0, 14.0, '(]');

-- If the third argument is omitted, '[)' is assumed.
SELECT numrange(1.0, 14.0);

-- Although '(]' is specified here, on display the value will be converted to
-- canonical form, since int8range is a discrete range type (see below).
SELECT int8range(1, 14, '(]');

-- Using NULL for either bound causes the range to be unbounded on that side.
SELECT numrange(NULL, 2.2);
```

Each range type also has a multirange constructor with the same name as the
multirange type.  The constructor function takes zero or more arguments
which are all ranges of the appropriate type.
For example:

```
SELECT nummultirange();
SELECT nummultirange(numrange(1.0, 14.0));
SELECT nummultirange(numrange(1.0, 14.0), numrange(20.0, 25.0));
```

### Discrete Range Types

A discrete range is one whose element type has a well-defined
"step", such as `integer` or `date`.
In these types two elements can be said to be adjacent, when there are
no valid values between them.  This contrasts with continuous ranges,
where it's always (or almost always) possible to identify other element
values between two given values.  For example, a range over the
`numeric` type is continuous, as is a range over `timestamp`.
(Even though `timestamp` has limited precision, and so could
theoretically be treated as discrete, it's better to consider it continuous
since the step size is normally not of interest.)

Another way to think about a discrete range type is that there is a clear
idea of a "next" or "previous" value for each element value.
Knowing that, it is possible to convert between inclusive and exclusive
representations of a range's bounds, by choosing the next or previous
element value instead of the one originally given.
For example, in an integer range type `[4,8]` and
`(3,9)` denote the same set of values; but this would not be so
for a range over numeric.

A discrete range type should have a *canonicalization*
function that is aware of the desired step size for the element type.
The canonicalization function is charged with converting equivalent values
of the range type to have identical representations, in particular
consistently inclusive or exclusive bounds.
If a canonicalization function is not specified, then ranges with different
formatting will always be treated as unequal, even though they might
represent the same set of values in reality.

The built-in range types `int4range`, `int8range`,
and `daterange` all use a canonical form that includes
the lower bound and excludes the upper bound; that is,
`[)`. User-defined range types can use other conventions,
however.

### Defining New Range Types

Users can define their own range types. The most common reason to do
this is to use ranges over subtypes not provided among the built-in
range types.
For example, to define a new range type of subtype `float8`:

```
CREATE TYPE floatrange AS RANGE (
subtype = float8,
subtype_diff = float8mi
);

SELECT '[1.234, 5.678]'::floatrange;
```

Because `float8` has no meaningful
"step", we do not define a canonicalization
function in this example.

When you define your own range you automatically get a corresponding
multirange type.

Defining your own range type also allows you to specify a different
subtype B-tree operator class or collation to use, so as to change the sort
ordering that determines which values fall into a given range.

If the subtype is considered to have discrete rather than continuous
values, the `CREATE TYPE` command should specify a
`canonical` function.
The canonicalization function takes an input range value, and must return
an equivalent range value that may have different bounds and formatting.
The canonical output for two ranges that represent the same set of values,
for example the integer ranges `[1, 7]` and `[1,
8)`, must be identical.  It doesn't matter which representation
you choose to be the canonical one, so long as two equivalent values with
different formattings are always mapped to the same value with the same
formatting.  In addition to adjusting the inclusive/exclusive bounds
format, a canonicalization function might round off boundary values, in
case the desired step size is larger than what the subtype is capable of
storing.  For instance, a range type over `timestamp` could be
defined to have a step size of an hour, in which case the canonicalization
function would need to round off bounds that weren't a multiple of an hour,
or perhaps throw an error instead.

In addition, any range type that is meant to be used with GiST or SP-GiST
indexes should define a subtype difference, or `subtype_diff`,
function.  (The index will still work without `subtype_diff`,
but it is likely to be considerably less efficient than if a difference
function is provided.)  The subtype difference function takes two input
values of the subtype, and returns their difference
(i.e., `X` minus `Y`) represented as
a `float8` value.  In our example above, the
function `float8mi` that underlies the regular `float8`
minus operator can be used; but for any other subtype, some type
conversion would be necessary.  Some creative thought about how to
represent differences as numbers might be needed, too.  To the greatest
extent possible, the `subtype_diff` function should agree with
the sort ordering implied by the selected operator class and collation;
that is, its result should be positive whenever its first argument is
greater than its second according to the sort ordering.

A less-oversimplified example of a `subtype_diff` function is:

```
CREATE FUNCTION time_subtype_diff(x time, y time) RETURNS float8 AS
'SELECT EXTRACT(EPOCH FROM (x - y))' LANGUAGE sql STRICT IMMUTABLE;

CREATE TYPE timerange AS RANGE (
subtype = time,
subtype_diff = time_subtype_diff
);

SELECT '[11:10, 23:00]'::timerange;
```

See [sql-createtype](#sql-createtype) for more information about creating
range types.

### Indexing

GiST and SP-GiST indexes can be created for table columns of range types.
GiST indexes can be also created for table columns of multirange types.
For instance, to create a GiST index:

```
CREATE INDEX reservation_idx ON reservation USING GIST (during);
```

A GiST or SP-GiST index on ranges can accelerate queries involving these
range operators:
`=`,
`&&`,
`<@`,
`@>`,
`<<`,
`>>`,
`-|-`,
`&<`, and
`&>`.
A GiST index on multiranges can accelerate queries involving the same
set of multirange operators.
A GiST index on ranges and GiST index on multiranges can also accelerate
queries involving these cross-type range to multirange and multirange to
range operators correspondingly:
`&&`,
`<@`,
`@>`,
`<<`,
`>>`,
`-|-`,
`&<`, and
`&>`.
See [range-operators-table](#range-operators-table) for more information.

In addition, B-tree and hash indexes can be created for table columns of
range types.  For these index types, basically the only useful range
operation is equality.  There is a B-tree sort ordering defined for range
values, with corresponding `<` and `>` operators,
but the ordering is rather arbitrary and not usually useful in the real
world.  Range types' B-tree and hash support is primarily meant to
allow sorting and hashing internally in queries, rather than creation of
actual indexes.

### Constraints on Ranges

While `UNIQUE` is a natural constraint for scalar
values, it is usually unsuitable for range types. Instead, an
exclusion constraint is often more appropriate
(see [CREATE TABLE
... CONSTRAINT ... EXCLUDE](#sql-createtable-exclude)). Exclusion constraints allow the
specification of constraints such as "non-overlapping" on a
range type. For example:

```
CREATE TABLE reservation (
during tsrange,
EXCLUDE USING GIST (during WITH &&)
);
```

That constraint will prevent any overlapping values from existing
in the table at the same time:

```
INSERT INTO reservation VALUES
('[2010-01-01 11:30, 2010-01-01 15:00)');
INSERT 0 1

INSERT INTO reservation VALUES
('[2010-01-01 14:45, 2010-01-01 15:45)');
ERROR:  conflicting key value violates exclusion constraint "reservation_during_excl"
DETAIL:  Key (during)=(["2010-01-01 14:45:00","2010-01-01 15:45:00")) conflicts
with existing key (during)=(["2010-01-01 11:30:00","2010-01-01 15:00:00")).
```

You can use the [`btree_gist`](#btree-gist)
extension to define exclusion constraints on plain scalar data types, which
can then be combined with range exclusions for maximum flexibility.  For
example, after `btree_gist` is installed, the following
constraint will reject overlapping ranges only if the meeting room numbers
are equal:

```
CREATE EXTENSION btree_gist;
CREATE TABLE room_reservation (
room text,
during tsrange,
EXCLUDE USING GIST (room WITH =, during WITH &&)
);

INSERT INTO room_reservation VALUES
('123A', '[2010-01-01 14:00, 2010-01-01 15:00)');
INSERT 0 1

INSERT INTO room_reservation VALUES
('123A', '[2010-01-01 14:30, 2010-01-01 15:30)');
ERROR:  conflicting key value violates exclusion constraint "room_reservation_room_during_excl"
DETAIL:  Key (room, during)=(123A, ["2010-01-01 14:30:00","2010-01-01 15:30:00")) conflicts
with existing key (room, during)=(123A, ["2010-01-01 14:00:00","2010-01-01 15:00:00")).

INSERT INTO room_reservation VALUES
('123B', '[2010-01-01 14:30, 2010-01-01 15:30)');
INSERT 0 1
```
