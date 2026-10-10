# Overview; Operators; Operator Type Resolution; Square Root Operator Type Resolution; String Concatenation Operator Type Resolution; Absolute-Value and Negation Operator Type Resolution; Array Inclusion Operator Type Resolution; Value Storage; Value Storage Type Conversion; character Storage Type Conversion; UNION, CASE, and Related Constructs; Type Resolution for UNION, CASE; Type Resolution examples; SELECT Output Columns

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/07_type_conversion.md`
- Source Title: `Type Conversion`
- Source Heading Path: `Type Conversion > Overview; Operators; Operator Type Resolution; Square Root Operator Type Resolution; String Concatenation Operator Type Resolution; Absolute-Value and Negation Operator Type Resolution; Array Inclusion Operator Type Resolution; Value Storage; Value Storage Type Conversion; character Storage Type Conversion; UNION, CASE, and Related Constructs; Type Resolution for UNION, CASE; Type Resolution examples; SELECT Output Columns`
- Source Line Ranges: `123-131, 132-212, 213-235, 236-275, 276-327, 328-364, 365-370, 371-394, 395-423, 424-437, 438-476, 477-490, 491-506, 507-522, 523-549, 550-581`
- Chunk ID: `pg16_fact_0151_f97ad36983`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `d5bd13a1f562d2de6d92043c6c8c6c4faf3ad33e04c8601677fb1a620a813196`

## Retrieval Guidance

- Use When: Need facts about why PostgreSQL chose a type or cast for an expression.
- Retrieval Keywords: type conversion, operator resolution, implicit cast, unknown type, UNION type resolution, CASE type resolution, SELECT output type
- Follow-up Guidance: Use explicit casts when parser resolution is ambiguous or not the intended behavior.
- Classification Note: Reference material explaining PostgreSQL type conversion, parser resolution of operators and constructs, implicit casts during value storage, and output-column type selection.

## Official Source Content

## Operators

The specific operator that is referenced by an operator expression
is determined using the following procedure.
Note that this procedure is indirectly affected
by the precedence of the operators involved, since that will determine
which sub-expressions are taken to be the inputs of which operators.
See [sql-precedence](#sql-precedence) for more information.

## Operator Type Resolution

Select the operators to be considered from the
pg_operator system catalog.  If a non-schema-qualified
operator name was used (the usual case), the operators
considered are those with the matching name and argument count that are
visible in the current search path (see [ddl-schemas-path](#ddl-schemas-path)).
If a qualified operator name was given, only operators in the specified
schema are considered.

If the search path finds multiple operators with identical argument types,
only the one appearing earliest in the path is considered.  Operators with
different argument types are considered on an equal footing regardless of
search path position.

Check for an operator accepting exactly the input argument types.
If one exists (there can be only one exact match in the set of
operators considered), use it.  Lack of an exact match creates a security
hazard when calling, via qualified name
(Note: The hazard does not arise with a non-schema-qualified name, because a
search path containing schemas that permit untrusted users to create
objects is not a secure schema usage
pattern.)
(not typical), any operator found in a schema that permits untrusted users to
create objects.  In such situations, cast arguments to force an exact match.

If one argument of a binary operator invocation is of the `unknown` type,
then assume it is the same type as the other argument for this check.
Invocations involving two `unknown` inputs, or a prefix operator
with an `unknown` input, will never find a match at this step.

If one argument of a binary operator invocation is of the `unknown`
type and the other is of a domain type, next check to see if there is an
operator accepting exactly the domain's base type on both sides; if so, use it.

Look for the best match.

Discard candidate operators for which the input types do not match
and cannot be converted (using an implicit conversion) to match.
`unknown` literals are
assumed to be convertible to anything for this purpose.  If only one
candidate remains, use it; else continue to the next step.

If any input argument is of a domain type, treat it as being of the
domain's base type for all subsequent steps.  This ensures that domains
act like their base types for purposes of ambiguous-operator resolution.

Run through all candidates and keep those with the most exact matches
on input types.  Keep all candidates if none have exact matches.
If only one candidate remains, use it; else continue to the next step.

Run through all candidates and keep those that accept preferred types (of the
input data type's type category) at the most positions where type conversion
will be required.
Keep all candidates if none accept preferred types.
If only one candidate remains, use it; else continue to the next step.

If any input arguments are `unknown`, check the type
categories accepted at those argument positions by the remaining
candidates.  At each position, select the `string` category
if any
candidate accepts that category.  (This bias towards string is appropriate
since an unknown-type literal looks like a string.) Otherwise, if
all the remaining candidates accept the same type category, select that
category; otherwise fail because the correct choice cannot be deduced
without more clues.  Now discard
candidates that do not accept the selected type category.  Furthermore,
if any candidate accepts a preferred type in that category,
discard candidates that accept non-preferred types for that argument.
Keep all candidates if none survive these tests.
If only one candidate remains, use it; else continue to the next step.

If there are both `unknown` and known-type arguments, and all
the known-type arguments have the same type, assume that the
`unknown` arguments are also of that type, and check which
candidates can accept that type at the `unknown`-argument
positions.  If exactly one candidate passes this test, use it.
Otherwise, fail.

Some examples follow.

## Square Root Operator Type Resolution

There is only one square root operator (prefix `|/`)
defined in the standard catalog, and it takes an argument of type
`double precision`.
The scanner assigns an initial type of `integer` to the argument
in this query expression:

```
SELECT |/ 40 AS "square root of 40";
square root of 40
-------------------
6.324555320336759
(1 row)
```

So the parser does a type conversion on the operand and the query
is equivalent to:

```
SELECT |/ CAST(40 AS double precision) AS "square root of 40";
```

## String Concatenation Operator Type Resolution

A string-like syntax is used for working with string types and for
working with complex extension types.
Strings with unspecified type are matched with likely operator candidates.

An example with one unspecified argument:

```
SELECT text 'abc' || 'def' AS "text and unknown";

text and unknown
------------------
abcdef
(1 row)
```

In this case the parser looks to see if there is an operator taking `text`
for both arguments. Since there is, it assumes that the second argument should
be interpreted as type `text`.

Here is a concatenation of two values of unspecified types:

```
SELECT 'abc' || 'def' AS "unspecified";

unspecified
-------------
abcdef
(1 row)
```

In this case there is no initial hint for which type to use, since no types
are specified in the query. So, the parser looks for all candidate operators
and finds that there are candidates accepting both string-category and
bit-string-category inputs.  Since string category is preferred when available,
that category is selected, and then the
preferred type for strings, `text`, is used as the specific
type to resolve the unknown-type literals as.

## Absolute-Value and Negation Operator Type Resolution

The PostgreSQL operator catalog has several
entries for the prefix operator `@`, all of which implement
absolute-value operations for various numeric data types.  One of these
entries is for type `float8`, which is the preferred type in
the numeric category.  Therefore, PostgreSQL
will use that entry when faced with an `unknown` input:

```
SELECT @ '-4.5' AS "abs";
abs
-----
4.5
(1 row)
```

Here the system has implicitly resolved the unknown-type literal as type
`float8` before applying the chosen operator.  We can verify that
`float8` and not some other type was used:

```
SELECT @ '-4.5e500' AS "abs";

ERROR:  "-4.5e500" is out of range for type double precision
```

On the other hand, the prefix operator `~` (bitwise negation)
is defined only for integer data types, not for `float8`.  So, if we
try a similar case with `~`, we get:

```
SELECT ~ '20' AS "negation";

ERROR:  operator is not unique: ~ "unknown"
HINT:  Could not choose a best candidate operator. You might need to add
explicit type casts.
```

This happens because the system cannot decide which of the several
possible `~` operators should be preferred.  We can help
it out with an explicit cast:

```
SELECT ~ CAST('20' AS int8) AS "negation";

negation
----------
-21
(1 row)
```

## Array Inclusion Operator Type Resolution

Here is another example of resolving an operator with one known and one
unknown input:

```
SELECT array[1,2]  **Note:**

> The parser learns from the `pg_cast` catalog that
> `text` and `varchar`
> are binary-compatible, meaning that one can be passed to a function that
> accepts the other without doing any physical conversion.  Therefore, no
> type conversion call is really inserted in this case.
>

And, if the function is called with an argument of type `integer`,
the parser will try to convert that to `text`:

```
SELECT substr(1234, 3);
ERROR:  function substr(integer, integer) does not exist
HINT:  No function matches the given name and argument types. You might need
to add explicit type casts.
```

This does not work because `integer` does not have an implicit cast
to `text`.  An explicit cast will work, however:

```
SELECT substr(CAST (1234 AS text), 3);

substr
--------
34
(1 row)
```

## Value Storage

Values to be inserted into a table are converted to the destination
column's data type according to the
following steps.

## Value Storage Type Conversion

Check for an exact match with the target.

Otherwise, try to convert the expression to the target type.  This is possible
if an *assignment cast* between the two types is registered in the
`pg_cast` catalog (see [sql-createcast](#sql-createcast)).
Alternatively, if the expression is an unknown-type literal, the contents of
the literal string will be fed to the input conversion routine for the target
type.

Check to see if there is a sizing cast for the target type.  A sizing
cast is a cast from that type to itself.  If one is found in the
`pg_cast` catalog, apply it to the expression before storing
into the destination column.  The implementation function for such a cast
always takes an extra parameter of type `integer`, which receives
the destination column's `atttypmod` value (typically its
declared length, although the interpretation of `atttypmod`
varies for different data types), and it may take a third `boolean`
parameter that says whether the cast is explicit or implicit.  The cast
function
is responsible for applying any length-dependent semantics such as size
checking or truncation.

## `character` Storage Type Conversion

For a target column declared as `character(20)` the following
statement shows that the stored value is sized correctly:

```
CREATE TABLE vv (v character(20));
INSERT INTO vv SELECT 'abc' || 'def';
SELECT v, octet_length(v) FROM vv;

v           | octet_length
----------------------+--------------
abcdef               |           20
(1 row)
```

What has really happened here is that the two unknown literals are resolved
to `text` by default, allowing the `||` operator
to be resolved as `text` concatenation.  Then the `text`
result of the operator is converted to `bpchar` ("blank-padded
char", the internal name of the `character` data type) to match the target
column type.  (Since the conversion from `text` to
`bpchar` is binary-coercible, this conversion does
not insert any real function call.)  Finally, the sizing function
`bpchar(bpchar, integer, boolean)` is found in the system catalog
and applied to the operator's result and the stored column length.  This
type-specific function performs the required length check and addition of
padding spaces.

## `UNION`, `CASE`, and Related Constructs

SQL `UNION` constructs must match up possibly dissimilar
types to become a single result set.  The resolution algorithm is
applied separately to each output column of a union query.  The
`INTERSECT` and `EXCEPT` constructs resolve
dissimilar types in the same way as `UNION`.
Some other constructs, including
`CASE`, `ARRAY`, `VALUES`,
and the `GREATEST` and `LEAST`
functions, use the identical
algorithm to match up their component expressions and select a result
data type.

## Type Resolution for `UNION`, `CASE`,
and Related Constructs

If all inputs are of the same type, and it is not `unknown`,
resolve as that type.

If any input is of a domain type, treat it as being of the
domain's base type for all subsequent steps.
(Note: Somewhat like the treatment of domain inputs for operators and
functions, this behavior allows a domain type to be preserved through
a `UNION` or similar construct, so long as the user is
careful to ensure that all inputs are implicitly or explicitly of that
exact type.  Otherwise the domain's base type will be used.)

If all inputs are of type `unknown`, resolve as type
`text` (the preferred type of the string category).
Otherwise, `unknown` inputs are ignored for the purposes
of the remaining rules.

If the non-unknown inputs are not all of the same type category, fail.

Select the first non-unknown input type as the candidate type,
then consider each other non-unknown input type, left to right.
(Note: For historical reasons, `CASE` treats
its `ELSE` clause (if any) as the "first"
input, with the `THEN` clauses(s) considered after
that.  In all other cases, "left to right" means the order
in which the expressions appear in the query text.)
If the candidate type can be implicitly converted to the other type,
but not vice-versa, select the other type as the new candidate type.
Then continue considering the remaining inputs.  If, at any stage of this
process, a preferred type is selected, stop considering additional
inputs.

Convert all inputs to the final candidate type.  Fail if there is not an
implicit conversion from a given input type to the candidate type.

Some examples follow.

## Type Resolution with Underspecified Types in a Union

```
SELECT text 'a' AS "text" UNION SELECT 'b';

text
------
a
b
(2 rows)
```

Here, the unknown-type literal `'b'` will be resolved to type `text`.

## Type Resolution in a Simple Union

```
SELECT 1.2 AS "numeric" UNION SELECT 1;

numeric
---------
1
1.2
(2 rows)
```

The literal `1.2` is of type `numeric`,
and the `integer` value `1` can be cast implicitly to
`numeric`, so that type is used.

## Type Resolution in a Transposed Union

```
SELECT 1 AS "real" UNION SELECT CAST('2.2' AS REAL);

real
------
1
2.2
(2 rows)
```

Here, since type `real` cannot be implicitly cast to `integer`,
but `integer` can be implicitly cast to `real`, the union
result type is resolved as `real`.

## Type Resolution in a Nested Union

```
SELECT NULL UNION SELECT NULL UNION SELECT 1;

ERROR:  UNION types text and integer cannot be matched
```

This failure occurs because PostgreSQL treats
multiple `UNION`s as a nest of pairwise operations;
that is, this input is the same as

```
(SELECT NULL UNION SELECT NULL) UNION SELECT 1;
```

The inner `UNION` is resolved as emitting
type `text`, according to the rules given above.  Then the
outer `UNION` has inputs of types `text`
and `integer`, leading to the observed error.  The problem
can be fixed by ensuring that the leftmost `UNION`
has at least one input of the desired result type.

`INTERSECT` and `EXCEPT` operations are
likewise resolved pairwise.  However, the other constructs described in this
section consider all of their inputs in one resolution step.

## `SELECT` Output Columns

The rules given in the preceding sections will result in assignment
of non-`unknown` data types to all expressions in an SQL query,
except for unspecified-type literals that appear as simple output
columns of a `SELECT` command.  For example, in

```
SELECT 'Hello World';
```

there is nothing to identify what type the string literal should be
taken as.  In this situation PostgreSQL will fall back
to resolving the literal's type as `text`.

When the `SELECT` is one arm of a `UNION`
(or `INTERSECT` or `EXCEPT`) construct, or when it
appears within `INSERT ... SELECT`, this rule is not applied
since rules given in preceding sections take precedence.  The type of an
unspecified-type literal can be taken from the other `UNION` arm
in the first case, or from the destination column in the second case.

`RETURNING` lists are treated the same as `SELECT`
output lists for this purpose.

> **Note:**

> Prior to PostgreSQL 10, this rule did not exist, and
> unspecified-type literals in a `SELECT` output list were
> left as type `unknown`.  That had assorted bad consequences,
> so it's been changed.
>
