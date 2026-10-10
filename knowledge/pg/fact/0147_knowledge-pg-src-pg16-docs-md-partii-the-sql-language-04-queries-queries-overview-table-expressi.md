# Overview; Table Expressions; Select Lists; Combining Queries; Sorting Rows; LIMIT and OFFSET; VALUES Lists; WITH Queries except materialization

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/04_queries.md`
- Source Title: `Queries`
- Source Heading Path: `Queries > Overview; Table Expressions; Select Lists; Combining Queries; Sorting Rows; LIMIT and OFFSET; VALUES Lists; WITH Queries except materialization`
- Source Line Ranges: `69-1152, 1153-1298, 1299-1389, 1390-1471, 1472-1520, 1521-1587, 1588-2160`
- Chunk ID: `pg16_fact_0147_541f80f64a`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `5b9a348b1e175568e6af7f298d34c431c2fb6746aff4b6ddc9079da0ca27457a`

## Retrieval Guidance

- Use When: Need SQL query semantics or syntax facts.
- Retrieval Keywords: SELECT, FROM, JOIN, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT, WITH, recursive query
- Follow-up Guidance: Use performance and index records when the question is about slow execution.
- Classification Note: Reference material for SELECT query structure, FROM, joins, WHERE, GROUP BY, HAVING, window processing, set operations, ORDER BY, LIMIT/OFFSET, VALUES, and recursive/data-modifying CTE semantics.

## Official Source Content

## Table Expressions

A *table expression* computes a table.  The
table expression contains a `FROM` clause that is
optionally followed by `WHERE`, `GROUP BY`, and
`HAVING` clauses.  Trivial table expressions simply refer
to a table on disk, a so-called base table, but more complex
expressions can be used to modify or combine base tables in various
ways.

The optional `WHERE`, `GROUP BY`, and
`HAVING` clauses in the table expression specify a
pipeline of successive transformations performed on the table
derived in the `FROM` clause.  All these transformations
produce a virtual table that provides the rows that are passed to
the select list to compute the output rows of the query.

### The `FROM` Clause

The [`FROM`](#sql-from) clause derives a
table from one or more other tables given in a comma-separated
table reference list.

```
FROM `table_reference` , `table_reference` , ...
```

A table reference can be a table name (possibly schema-qualified),
or a derived table such as a subquery, a `JOIN` construct, or
complex combinations of these.  If more than one table reference is
listed in the `FROM` clause, the tables are cross-joined
(that is, the Cartesian product of their rows is formed; see below).
The result of the `FROM` list is an intermediate virtual
table that can then be subject to
transformations by the `WHERE`, `GROUP BY`,
and `HAVING` clauses and is finally the result of the
overall table expression.

When a table reference names a table that is the parent of a
table inheritance hierarchy, the table reference produces rows of
not only that table but all of its descendant tables, unless the
key word `ONLY` precedes the table name.  However, the
reference produces only the columns that appear in the named table
— any columns added in subtables are ignored.

Instead of writing `ONLY` before the table name, you can write
`*` after the table name to explicitly specify that descendant
tables are included.  There is no real reason to use this syntax any more,
because searching descendant tables is now always the default behavior.
However, it is supported for compatibility with older releases.

#### Joined Tables

A joined table is a table derived from two other (real or
derived) tables according to the rules of the particular join
type.  Inner, outer, and cross-joins are available.
The general syntax of a joined table is

```
`T1` `join_type` `T2`  `join_condition`
```

Joins of all types can be chained together, or nested: either or
both `T1` and
`T2` can be joined tables.  Parentheses
can be used around `JOIN` clauses to control the join
order.  In the absence of parentheses, `JOIN` clauses
nest left-to-right.

**Cross join**
: ```
`T1` CROSS JOIN `T2`
```

For every possible combination of rows from
`T1` and
`T2` (i.e., a Cartesian product),
the joined table will contain a
row consisting of all columns in `T1`
followed by all columns in `T2`.  If
the tables have N and M rows respectively, the joined
table will have N * M rows.

`FROM `T1` CROSS JOIN
`T2`` is equivalent to
`FROM `T1` INNER JOIN
`T2` ON TRUE` (see below).
It is also equivalent to
`FROM `T1`,
`T2``.

> **Note:**
> This latter equivalence does not hold exactly when more than two
> tables appear, because `JOIN` binds more tightly than
> comma.  For example
> `FROM `T1` CROSS JOIN
> `T2` INNER JOIN `T3`
> ON `condition``
> is not the same as
> `FROM `T1`,
> `T2` INNER JOIN `T3`
> ON `condition``
> because the `condition` can
> reference `T1` in the first case but not
> the second.
>

**Qualified joins**
: ```
`T1` { INNER | { LEFT | RIGHT | FULL } OUTER } JOIN `T2` ON `boolean_expression`
`T1` { INNER | { LEFT | RIGHT | FULL } OUTER } JOIN `T2` USING ( `join column list` )
`T1` NATURAL { INNER | { LEFT | RIGHT | FULL } OUTER } JOIN `T2`
```

The words `INNER` and
`OUTER` are optional in all forms.
`INNER` is the default;
`LEFT`, `RIGHT`, and
`FULL` imply an outer join.

The *join condition* is specified in the
`ON` or `USING` clause, or implicitly by
the word `NATURAL`.  The join condition determines
which rows from the two source tables are considered to
"match", as explained in detail below.

The possible types of qualified join are:

`INNER JOIN`

For each row R1 of T1, the joined table has a row for each
row in T2 that satisfies the join condition with R1.

**`LEFT OUTER JOIN`**
: First, an inner join is performed.  Then, for each row in
T1 that does not satisfy the join condition with any row in
T2, a joined row is added with null values in columns of
T2.  Thus, the joined table always has at least
one row for each row in T1.

**`RIGHT OUTER JOIN`**
: First, an inner join is performed.  Then, for each row in
T2 that does not satisfy the join condition with any row in
T1, a joined row is added with null values in columns of
T1.  This is the converse of a left join: the result table
will always have a row for each row in T2.

**`FULL OUTER JOIN`**
: First, an inner join is performed.  Then, for each row in
T1 that does not satisfy the join condition with any row in
T2, a joined row is added with null values in columns of
T2.  Also, for each row of T2 that does not satisfy the
join condition with any row in T1, a joined row with null
values in the columns of T1 is added.

The `ON` clause is the most general kind of join
condition: it takes a Boolean value expression of the same
kind as is used in a `WHERE` clause.  A pair of rows
from `T1` and `T2` match if the
`ON` expression evaluates to true.

The `USING` clause is a shorthand that allows you to take
advantage of the specific situation where both sides of the join use
the same name for the joining column(s).  It takes a
comma-separated list of the shared column names
and forms a join condition that includes an equality comparison
for each one.  For example, joining `T1`
and `T2` with `USING (a, b)` produces
the join condition `ON `T1`.a
= `T2`.a AND `T1`.b
= `T2`.b`.

Furthermore, the output of `JOIN USING` suppresses
redundant columns: there is no need to print both of the matched
columns, since they must have equal values.  While `JOIN
ON` produces all columns from `T1` followed by all
columns from `T2`, `JOIN USING` produces one
output column for each of the listed column pairs (in the listed
order), followed by any remaining columns from `T1`,
followed by any remaining columns from `T2`.

Finally, `NATURAL` is a shorthand form of
`USING`: it forms a `USING` list
consisting of all column names that appear in both
input tables.  As with `USING`, these columns appear
only once in the output table.  If there are no common
column names, `NATURAL JOIN` behaves like
`JOIN ... ON TRUE`, producing a cross-product join.

> **Note:**

> `USING` is reasonably safe from column changes
> in the joined relations since only the listed columns
> are combined.  `NATURAL` is considerably more risky since
> any schema changes to either relation that cause a new matching
> column name to be present will cause the join to combine that new
> column as well.
>

To put this together, assume we have tables `t1`:

```
num | name
-----+------
1 | a
2 | b
3 | c
```

and `t2`:

```
num | value
-----+-------
1 | xxx
3 | yyy
5 | zzz
```

then we get the following results for the various joins:

```
=> SELECT * FROM t1 CROSS JOIN t2;
num | name | num | value
-----+------+-----+-------
1 | a    |   1 | xxx
1 | a    |   3 | yyy
1 | a    |   5 | zzz
2 | b    |   1 | xxx
2 | b    |   3 | yyy
2 | b    |   5 | zzz
3 | c    |   1 | xxx
3 | c    |   3 | yyy
3 | c    |   5 | zzz
(9 rows)

=> SELECT * FROM t1 INNER JOIN t2 ON t1.num = t2.num;
num | name | num | value
-----+------+-----+-------
1 | a    |   1 | xxx
3 | c    |   3 | yyy
(2 rows)

=> SELECT * FROM t1 INNER JOIN t2 USING (num);
num | name | value
-----+------+-------
1 | a    | xxx
3 | c    | yyy
(2 rows)

=> SELECT * FROM t1 NATURAL INNER JOIN t2;
num | name | value
-----+------+-------
1 | a    | xxx
3 | c    | yyy
(2 rows)

=> SELECT * FROM t1 LEFT JOIN t2 ON t1.num = t2.num;
num | name | num | value
-----+------+-----+-------
1 | a    |   1 | xxx
2 | b    |     |
3 | c    |   3 | yyy
(3 rows)

=> SELECT * FROM t1 LEFT JOIN t2 USING (num);
num | name | value
-----+------+-------
1 | a    | xxx
2 | b    |
3 | c    | yyy
(3 rows)

=> SELECT * FROM t1 RIGHT JOIN t2 ON t1.num = t2.num;
num | name | num | value
-----+------+-----+-------
1 | a    |   1 | xxx
3 | c    |   3 | yyy
|      |   5 | zzz
(3 rows)

=> SELECT * FROM t1 FULL JOIN t2 ON t1.num = t2.num;
num | name | num | value
-----+------+-----+-------
1 | a    |   1 | xxx
2 | b    |     |
3 | c    |   3 | yyy
|      |   5 | zzz
(4 rows)
```

The join condition specified with `ON` can also contain
conditions that do not relate directly to the join.  This can
prove useful for some queries but needs to be thought out
carefully.  For example:

```
=> SELECT * FROM t1 LEFT JOIN t2 ON t1.num = t2.num AND t2.value = 'xxx';
num | name | num | value
-----+------+-----+-------
1 | a    |   1 | xxx
2 | b    |     |
3 | c    |     |
(3 rows)
```

Notice that placing the restriction in the `WHERE` clause
produces a different result:

```
=> SELECT * FROM t1 LEFT JOIN t2 ON t1.num = t2.num WHERE t2.value = 'xxx';
num | name | num | value
-----+------+-----+-------
1 | a    |   1 | xxx
(1 row)
```

This is because a restriction placed in the `ON`
clause is processed *before* the join, while
a restriction placed in the `WHERE` clause is processed
*after* the join.
That does not matter with inner joins, but it matters a lot with outer
joins.

#### Table and Column Aliases

A temporary name can be given to tables and complex table
references to be used for references to the derived table in
the rest of the query.  This is called a *table
alias*.

To create a table alias, write

```
FROM `table_reference` AS `alias`
```

or

```
FROM `table_reference` `alias`
```

The `AS` key word is optional noise.
`alias` can be any identifier.

A typical application of table aliases is to assign short
identifiers to long table names to keep the join clauses
readable.  For example:

```
SELECT * FROM some_very_long_table_name s JOIN another_fairly_long_name a ON s.id = a.num;
```

The alias becomes the new name of the table reference so far as the
current query is concerned — it is not allowed to refer to the
table by the original name elsewhere in the query.  Thus, this is not
valid:

```
SELECT * FROM my_table AS m WHERE my_table.a > 5;    -- wrong
```

Table aliases are mainly for notational convenience, but it is
necessary to use them when joining a table to itself, e.g.:

```
SELECT * FROM people AS mother JOIN people AS child ON mother.id = child.mother_id;
```

Parentheses are used to resolve ambiguities.  In the following example,
the first statement assigns the alias `b` to the second
instance of `my_table`, but the second statement assigns the
alias to the result of the join:

```
SELECT * FROM my_table AS a CROSS JOIN my_table AS b ...
SELECT * FROM (my_table AS a CROSS JOIN my_table) AS b ...
```

Another form of table aliasing gives temporary names to the columns of
the table, as well as the table itself:

```
FROM `table_reference` AS `alias` ( `column1` , `column2` , ... )
```

If fewer column aliases are specified than the actual table has
columns, the remaining columns are not renamed.  This syntax is
especially useful for self-joins or subqueries.

When an alias is applied to the output of a `JOIN`
clause, the alias hides the original
name(s) within the `JOIN`.  For example:

```
SELECT a.* FROM my_table AS a JOIN your_table AS b ON ...
```

is valid SQL, but:

```
SELECT a.* FROM (my_table AS a JOIN your_table AS b ON ...) AS c
```

is not valid; the table alias `a` is not visible
outside the alias `c`.

#### Subqueries

Subqueries specifying a derived table must be enclosed in
parentheses.  They may be assigned a table alias name, and optionally
column alias names (as in [queries-table-aliases](#queries-table-aliases)).
For example:

```
FROM (SELECT * FROM table1) AS alias_name
```

This example is equivalent to `FROM table1 AS
alias_name`.  More interesting cases, which cannot be
reduced to a plain join, arise when the subquery involves
grouping or aggregation.

A subquery can also be a `VALUES` list:

```
FROM (VALUES ('anne', 'smith'), ('bob', 'jones'), ('joe', 'blow'))
AS names(first, last)
```

Again, a table alias is optional.  Assigning alias names to the columns
of the `VALUES` list is optional, but is good practice.
For more information see [queries-values](#queries-values).

According to the SQL standard, a table alias name must be supplied
for a subquery.  PostgreSQL
allows `AS` and the alias to be omitted, but
writing one is good practice in SQL code that might be ported to
another system.

#### Table Functions

Table functions are functions that produce a set of rows, made up
of either base data types (scalar types) or composite data types
(table rows).  They are used like a table, view, or subquery in
the `FROM` clause of a query. Columns returned by table
functions can be included in `SELECT`,
`JOIN`, or `WHERE` clauses in the same manner
as columns of a table, view, or subquery.

Table functions may also be combined using the `ROWS FROM`
syntax, with the results returned in parallel columns; the number of
result rows in this case is that of the largest function result, with
smaller results padded with null values to match.

```
`function_call` WITH ORDINALITY AS `table_alias` (`column_alias` , ... )
ROWS FROM( `function_call` , ...  ) WITH ORDINALITY AS `table_alias` (`column_alias` , ... )
```

If the `WITH ORDINALITY` clause is specified, an
additional column of type `bigint` will be added to the
function result columns.  This column numbers the rows of the function
result set, starting from 1. (This is a generalization of the
SQL-standard syntax for `UNNEST ... WITH ORDINALITY`.)
By default, the ordinal column is called `ordinality`, but
a different column name can be assigned to it using
an `AS` clause.

The special table function `UNNEST` may be called with
any number of array parameters, and it returns a corresponding number of
columns, as if `UNNEST`
([functions-array](#functions-array)) had been called on each parameter
separately and combined using the `ROWS FROM` construct.

```
UNNEST( `array_expression` , ...  ) WITH ORDINALITY AS `table_alias` (`column_alias` , ... )
```

If no `table_alias` is specified, the function
name is used as the table name; in the case of a `ROWS FROM()`
construct, the first function's name is used.

If column aliases are not supplied, then for a function returning a base
data type, the column name is also the same as the function name.  For a
function returning a composite type, the result columns get the names
of the individual attributes of the type.

Some examples:

```
CREATE TABLE foo (fooid int, foosubid int, fooname text);

CREATE FUNCTION getfoo(int) RETURNS SETOF foo AS $$
SELECT * FROM foo WHERE fooid = $1;
$$ LANGUAGE SQL;

SELECT * FROM getfoo(1) AS t1;

SELECT * FROM foo
WHERE foosubid IN (
SELECT foosubid
FROM getfoo(foo.fooid) z
WHERE z.fooid = foo.fooid
);

CREATE VIEW vw_getfoo AS SELECT * FROM getfoo(1);

SELECT * FROM vw_getfoo;
```

In some cases it is useful to define table functions that can
return different column sets depending on how they are invoked.
To support this, the table function can be declared as returning
the pseudo-type `record` with no `OUT`
parameters.  When such a function is used in
a query, the expected row structure must be specified in the
query itself, so that the system can know how to parse and plan
the query.  This syntax looks like:

```
`function_call` AS `alias` (`column_definition` , ... )
`function_call` AS `alias` (`column_definition` , ... )
ROWS FROM( ... `function_call` AS (`column_definition` , ... ) , ...  )
```

When not using the `ROWS FROM()` syntax,
the `column_definition` list replaces the column
alias list that could otherwise be attached to the `FROM`
item; the names in the column definitions serve as column aliases.
When using the `ROWS FROM()` syntax,
a `column_definition` list can be attached to
each member function separately; or if there is only one member function
and no `WITH ORDINALITY` clause,
a `column_definition` list can be written in
place of a column alias list following `ROWS FROM()`.

Consider this example:

```
SELECT *
FROM dblink('dbname=mydb', 'SELECT proname, prosrc FROM pg_proc')
AS t1(proname name, prosrc text)
WHERE proname LIKE 'bytea%';
```

The [contrib-dblink-function](#contrib-dblink-function) function
(part of the [dblink](#dblink) module) executes
a remote query.  It is declared to return
`record` since it might be used for any kind of query.
The actual column set must be specified in the calling query so
that the parser knows, for example, what `*` should
expand to.

This example uses `ROWS FROM`:

```
SELECT *
FROM ROWS FROM
(
json_to_recordset('[{"a":40,"b":"foo"},{"a":"100","b":"bar"}]')
AS (a INTEGER, b TEXT),
generate_series(1, 3)
) AS x (p, q, s)
ORDER BY p;

p  |  q  | s
-----+-----+---
40 | foo | 1
100 | bar | 2
|     | 3
```

It joins two functions into a single `FROM`
target.  `json_to_recordset()` is instructed
to return two columns, the first `integer`
and the second `text`.  The result of
`generate_series()` is used directly.
The `ORDER BY` clause sorts the column values
as integers.

#### `LATERAL` Subqueries

Subqueries appearing in `FROM` can be
preceded by the key word `LATERAL`.  This allows them to
reference columns provided by preceding `FROM` items.
(Without `LATERAL`, each subquery is
evaluated independently and so cannot cross-reference any other
`FROM` item.)

Table functions appearing in `FROM` can also be
preceded by the key word `LATERAL`, but for functions the
key word is optional; the function's arguments can contain references
to columns provided by preceding `FROM` items in any case.

A `LATERAL` item can appear at the top level in the
`FROM` list, or within a `JOIN` tree.  In the latter
case it can also refer to any items that are on the left-hand side of a
`JOIN` that it is on the right-hand side of.

When a `FROM` item contains `LATERAL`
cross-references, evaluation proceeds as follows: for each row of the
`FROM` item providing the cross-referenced column(s), or
set of rows of multiple `FROM` items providing the
columns, the `LATERAL` item is evaluated using that
row or row set's values of the columns.  The resulting row(s) are
joined as usual with the rows they were computed from.  This is
repeated for each row or set of rows from the column source table(s).

A trivial example of `LATERAL` is

```
SELECT * FROM foo, LATERAL (SELECT * FROM bar WHERE bar.id = foo.bar_id) ss;
```

This is not especially useful since it has exactly the same result as
the more conventional

```
SELECT * FROM foo, bar WHERE bar.id = foo.bar_id;
```

`LATERAL` is primarily useful when the cross-referenced
column is necessary for computing the row(s) to be joined.  A common
application is providing an argument value for a set-returning function.
For example, supposing that `vertices(polygon)` returns the
set of vertices of a polygon, we could identify close-together vertices
of polygons stored in a table with:

```
SELECT p1.id, p2.id, v1, v2
FROM polygons p1, polygons p2,
LATERAL vertices(p1.poly) v1,
LATERAL vertices(p2.poly) v2
WHERE (v1  v2)  v2)  **Note:**

> The join condition of an inner join can be written either in
> the `WHERE` clause or in the `JOIN` clause.
> For example, these table expressions are equivalent:
> ```
> FROM a, b WHERE a.id = b.id AND b.val > 5
> ```
> and:
> ```
> FROM a INNER JOIN b ON (a.id = b.id) WHERE b.val > 5
> ```
> or perhaps even:
> ```
> FROM a NATURAL JOIN b WHERE b.val > 5
> ```
> Which one of these you use is mainly a matter of style.  The
> `JOIN` syntax in the `FROM` clause is
> probably not as portable to other SQL database management systems,
> even though it is in the SQL standard.  For
> outer joins there is no choice:  they must be done in
> the `FROM` clause.  The `ON` or `USING`
> clause of an outer join is *not* equivalent to a
> `WHERE` condition, because it results in the addition
> of rows (for unmatched input rows) as well as the removal of rows
> in the final result.
>

Here are some examples of `WHERE` clauses:

```
SELECT ... FROM fdt WHERE c1 > 5

SELECT ... FROM fdt WHERE c1 IN (1, 2, 3)

SELECT ... FROM fdt WHERE c1 IN (SELECT c1 FROM t2)

SELECT ... FROM fdt WHERE c1 IN (SELECT c3 FROM t2 WHERE c2 = fdt.c1 + 10)

SELECT ... FROM fdt WHERE c1 BETWEEN (SELECT c3 FROM t2 WHERE c2 = fdt.c1 + 10) AND 100

SELECT ... FROM fdt WHERE EXISTS (SELECT c1 FROM t2 WHERE c2 > fdt.c1)
```

`fdt` is the table derived in the
`FROM` clause. Rows that do not meet the search
condition of the `WHERE` clause are eliminated from
`fdt`. Notice the use of scalar subqueries as
value expressions.  Just like any other query, the subqueries can
employ complex table expressions.  Notice also how
`fdt` is referenced in the subqueries.
Qualifying `c1` as `fdt.c1` is only necessary
if `c1` is also the name of a column in the derived
input table of the subquery.  But qualifying the column name adds
clarity even when it is not needed.  This example shows how the column
naming scope of an outer query extends into its inner queries.

### The `GROUP BY` and `HAVING` Clauses

After passing the `WHERE` filter, the derived input
table might be subject to grouping, using the `GROUP BY`
clause, and elimination of group rows using the `HAVING`
clause.

```
SELECT `select_list`
FROM ...
WHERE ...
GROUP BY `grouping_column_reference` , `grouping_column_reference`...
```

The [`GROUP BY`](#sql-groupby) clause is
used to group together those rows in a table that have the same
values in all the columns listed. The order in which the columns
are listed does not matter.  The effect is to combine each set
of rows having common values into one group row that
represents all rows in the group.  This is done to
eliminate redundancy in the output and/or compute aggregates that
apply to these groups.  For instance:

```
=> SELECT * FROM test1;
x | y
---+---
a | 3
c | 2
b | 5
a | 1
(4 rows)

=> SELECT x FROM test1 GROUP BY x;
x
---
a
b
c
(3 rows)
```

In the second query, we could not have written `SELECT *
FROM test1 GROUP BY x`, because there is no single value
for the column `y` that could be associated with each
group.  The grouped-by columns can be referenced in the select list since
they have a single value in each group.

In general, if a table is grouped, columns that are not
listed in `GROUP BY` cannot be referenced except in aggregate
expressions.  An example with aggregate expressions is:

```
=> SELECT x, sum(y) FROM test1 GROUP BY x;
x | sum
---+-----
a |   4
b |   5
c |   2
(3 rows)
```

Here `sum` is an aggregate function that
computes a single value over the entire group.  More information
about the available aggregate functions can be found in [functions-aggregate](#functions-aggregate).

> **Tip:**

> Grouping without aggregate expressions effectively calculates the
> set of distinct values in a column.  This can also be achieved
> using the `DISTINCT` clause (see  linkend="queries-distinct"/>).
>

Here is another example:  it calculates the total sales for each
product (rather than the total sales of all products):

```
SELECT product_id, p.name, (sum(s.units) * p.price) AS sales
FROM products p LEFT JOIN sales s USING (product_id)
GROUP BY product_id, p.name, p.price;
```

In this example, the columns `product_id`,
`p.name`, and `p.price` must be
in the `GROUP BY` clause since they are referenced in
the query select list (but see below).  The column
`s.units` does not have to be in the `GROUP
BY` list since it is only used in an aggregate expression
(`sum(...)`), which represents the sales
of a product.  For each product, the query returns a summary row about
all sales of the product.

If the products table is set up so that, say,
`product_id` is the primary key, then it would be
enough to group by `product_id` in the above example,
since name and price would be *functionally
dependent* on the product ID, and so there would be no
ambiguity about which name and price value to return for each product
ID group.

In strict SQL, `GROUP BY` can only group by columns of
the source table but PostgreSQL extends
this to also allow `GROUP BY` to group by columns in the
select list.  Grouping by value expressions instead of simple
column names is also allowed.

If a table has been grouped using `GROUP BY`,
but only certain groups are of interest, the
`HAVING` clause can be used, much like a
`WHERE` clause, to eliminate groups from the result.
The syntax is:

```
SELECT `select_list` FROM ... WHERE ... GROUP BY ... HAVING `boolean_expression`
```

Expressions in the `HAVING` clause can refer both to
grouped expressions and to ungrouped expressions (which necessarily
involve an aggregate function).

Example:

```
=> SELECT x, sum(y) FROM test1 GROUP BY x HAVING sum(y) > 3;
x | sum
---+-----
a |   4
b |   5
(2 rows)

=> SELECT x, sum(y) FROM test1 GROUP BY x HAVING x  CURRENT_DATE - INTERVAL '4 weeks'
GROUP BY product_id, p.name, p.price, p.cost
HAVING sum(p.price * s.units) > 5000;
```

In the example above, the `WHERE` clause is selecting
rows by a column that is not grouped (the expression is only true for
sales during the last four weeks), while the `HAVING`
clause restricts the output to groups with total gross sales over
5000.  Note that the aggregate expressions do not necessarily need
to be the same in all parts of the query.

If a query contains aggregate function calls, but no `GROUP BY`
clause, grouping still occurs: the result is a single group row (or
perhaps no rows at all, if the single row is then eliminated by
`HAVING`).
The same is true if it contains a `HAVING` clause, even
without any aggregate function calls or `GROUP BY` clause.

### `GROUPING SETS`, `CUBE`, and `ROLLUP`

More complex grouping operations than those described above are possible
using the concept of *grouping sets*.  The data selected by
the `FROM` and `WHERE` clauses is grouped separately
by each specified grouping set, aggregates computed for each group just as
for simple `GROUP BY` clauses, and then the results returned.
For example:

```
=> SELECT * FROM items_sold;
brand | size | sales
-------+------+-------
Foo   | L    |  10
Foo   | M    |  20
Bar   | M    |  15
Bar   | L    |  5
(4 rows)

=> SELECT brand, size, sum(sales) FROM items_sold GROUP BY GROUPING SETS ((brand), (size), ());
brand | size | sum
-------+------+-----
Foo   |      |  30
Bar   |      |  20
| L    |  15
| M    |  35
|      |  50
(5 rows)
```

Each sublist of `GROUPING SETS` may specify zero or more columns
or expressions and is interpreted the same way as though it were directly
in the `GROUP BY` clause.  An empty grouping set means that all
rows are aggregated down to a single group (which is output even if no
input rows were present), as described above for the case of aggregate
functions with no `GROUP BY` clause.

References to the grouping columns or expressions are replaced
by null values in result rows for grouping sets in which those
columns do not appear.  To distinguish which grouping a particular output
row resulted from, see [functions-grouping-table](#functions-grouping-table).

A shorthand notation is provided for specifying two common types of grouping set.
A clause of the form

```
ROLLUP ( `e1`, `e2`, `e3`, ... )
```

represents the given list of expressions and all prefixes of the list including
the empty list; thus it is equivalent to

```
GROUPING SETS (
( `e1`, `e2`, `e3`, ... ),
...
( `e1`, `e2` ),
( `e1` ),
( )
)
```

This is commonly used for analysis over hierarchical data; e.g., total
salary by department, division, and company-wide total.

A clause of the form

```
CUBE ( `e1`, `e2`, ... )
```

represents the given list and all of its possible subsets (i.e., the power
set).  Thus

```
CUBE ( a, b, c )
```

is equivalent to

```
GROUPING SETS (
( a, b, c ),
( a, b    ),
( a,    c ),
( a       ),
(    b, c ),
(    b    ),
(       c ),
(         )
)
```

The individual elements of a `CUBE` or `ROLLUP`
clause may be either individual expressions, or sublists of elements in
parentheses.  In the latter case, the sublists are treated as single
units for the purposes of generating the individual grouping sets.
For example:

```
CUBE ( (a, b), (c, d) )
```

is equivalent to

```
GROUPING SETS (
( a, b, c, d ),
( a, b       ),
(       c, d ),
(            )
)
```

and

```
ROLLUP ( a, (b, c), d )
```

is equivalent to

```
GROUPING SETS (
( a, b, c, d ),
( a, b, c    ),
( a          ),
(            )
)
```

The `CUBE` and `ROLLUP` constructs can be used either
directly in the `GROUP BY` clause, or nested inside a
`GROUPING SETS` clause.  If one `GROUPING SETS` clause
is nested inside another, the effect is the same as if all the elements of
the inner clause had been written directly in the outer clause.

If multiple grouping items are specified in a single `GROUP BY`
clause, then the final list of grouping sets is the cross product of the
individual items.  For example:

```
GROUP BY a, CUBE (b, c), GROUPING SETS ((d), (e))
```

is equivalent to

```
GROUP BY GROUPING SETS (
(a, b, c, d), (a, b, c, e),
(a, b, d),    (a, b, e),
(a, c, d),    (a, c, e),
(a, d),       (a, e)
)
```

When specifying multiple grouping items together, the final set of grouping
sets might contain duplicates. For example:

```
GROUP BY ROLLUP (a, b), ROLLUP (a, c)
```

is equivalent to

```
GROUP BY GROUPING SETS (
(a, b, c),
(a, b),
(a, b),
(a, c),
(a),
(a),
(a, c),
(a),
()
)
```

If these duplicates are undesirable, they can be removed using the
`DISTINCT` clause directly on the `GROUP BY`.
Therefore:

```
GROUP BY *DISTINCT* ROLLUP (a, b), ROLLUP (a, c)
```

is equivalent to

```
GROUP BY GROUPING SETS (
(a, b, c),
(a, b),
(a, c),
(a),
()
)
```

This is not the same as using `SELECT DISTINCT` because the output
rows may still contain duplicates.  If any of the ungrouped columns contains NULL,
it will be indistinguishable from the NULL used when that same column is grouped.

> **Note:**

> The construct `(a, b)` is normally recognized in expressions as
> a [row constructor](#sql-syntax-row-constructors).
> Within the `GROUP BY` clause, this does not apply at the top
> levels of expressions, and `(a, b)` is parsed as a list of
> expressions as described above.  If for some reason you *need*
> a row constructor in a grouping expression, use `ROW(a, b)`.
>

### Window Function Processing

If the query contains any window functions (see
[tutorial-window](#tutorial-window),
[functions-window](#functions-window) and
[syntax-window-functions](#syntax-window-functions)), these functions are evaluated
after any grouping, aggregation, and `HAVING` filtering is
performed.  That is, if the query uses any aggregates, `GROUP
BY`, or `HAVING`, then the rows seen by the window functions
are the group rows instead of the original table rows from
`FROM`/`WHERE`.

When multiple window functions are used, all the window functions having
equivalent `PARTITION BY` and `ORDER BY`
clauses in their window definitions are guaranteed to see the same
ordering of the input rows, even if the `ORDER BY` does
not uniquely determine the ordering.
However, no guarantees are made about the evaluation of functions having
different `PARTITION BY` or `ORDER BY` specifications.
(In such cases a sort step is typically required between the passes of
window function evaluations, and the sort is not guaranteed to preserve
ordering of rows that its `ORDER BY` sees as equivalent.)

Currently, window functions always require presorted data, and so the
query output will be ordered according to one or another of the window
functions' `PARTITION BY`/`ORDER BY` clauses.
It is not recommended to rely on this, however.  Use an explicit
top-level `ORDER BY` clause if you want to be sure the
results are sorted in a particular way.

## Select Lists

As shown in the previous section,
the table expression in the `SELECT` command
constructs an intermediate virtual table by possibly combining
tables, views, eliminating rows, grouping, etc.  This table is
finally passed on to processing by the *select list*.  The select
list determines which *columns* of the
intermediate table are actually output.

### Select-List Items

The simplest kind of select list is `*` which
emits all columns that the table expression produces.  Otherwise,
a select list is a comma-separated list of value expressions (as
defined in [sql-expressions](#sql-expressions)).  For instance, it
could be a list of column names:

```
SELECT a, b, c FROM ...
```

The columns names `a`, `b`, and `c`
are either the actual names of the columns of tables referenced
in the `FROM` clause, or the aliases given to them as
explained in [queries-table-aliases](#queries-table-aliases).  The name
space available in the select list is the same as in the
`WHERE` clause, unless grouping is used, in which case
it is the same as in the `HAVING` clause.

If more than one table has a column of the same name, the table
name must also be given, as in:

```
SELECT tbl1.a, tbl2.a, tbl1.b FROM ...
```

When working with multiple tables, it can also be useful to ask for
all the columns of a particular table:

```
SELECT tbl1.*, tbl2.a FROM ...
```

See [rowtypes-usage](#rowtypes-usage) for more about
the `table_name``.*` notation.

If an arbitrary value expression is used in the select list, it
conceptually adds a new virtual column to the returned table.  The
value expression is evaluated once for each result row, with
the row's values substituted for any column references.  But the
expressions in the select list do not have to reference any
columns in the table expression of the `FROM` clause;
they can be constant arithmetic expressions, for instance.

### Column Labels

The entries in the select list can be assigned names for subsequent
processing, such as for use in an `ORDER BY` clause
or for display by the client application.  For example:

```
SELECT a AS value, b + c AS sum FROM ...
```

If no output column name is specified using `AS`,
the system assigns a default column name.  For simple column references,
this is the name of the referenced column.  For function
calls, this is the name of the function.  For complex expressions,
the system will generate a generic name.

The `AS` key word is usually optional, but in some
cases where the desired column name matches a
PostgreSQL key word, you must write
`AS` or double-quote the column name in order to
avoid ambiguity.
([sql-keywords-appendix](#sql-keywords-appendix) shows which key words
require `AS` to be used as a column label.)
For example, `FROM` is one such key word, so this
does not work:

```
SELECT a from, b + c AS sum FROM ...
```

but either of these do:

```
SELECT a AS from, b + c AS sum FROM ...
SELECT a "from", b + c AS sum FROM ...
```

For greatest safety against possible
future key word additions, it is recommended that you always either
write `AS` or double-quote the output column name.

> **Note:**

> The naming of output columns here is different from that done in
> the `FROM` clause (see  linkend="queries-table-aliases"/>).  It is possible
> to rename the same column twice, but the name assigned in
> the select list is the one that will be passed on.
>

### `DISTINCT`

After the select list has been processed, the result table can
optionally be subject to the elimination of duplicate rows.  The
`DISTINCT` key word is written directly after
`SELECT` to specify this:

```
SELECT DISTINCT `select_list` ...
```

(Instead of `DISTINCT` the key word `ALL`
can be used to specify the default behavior of retaining all rows.)

Obviously, two rows are considered distinct if they differ in at
least one column value.  Null values are considered equal in this
comparison.

Alternatively, an arbitrary expression can determine what rows are
to be considered distinct:

```
SELECT DISTINCT ON (`expression` , `expression` ...) `select_list` ...
```

Here `expression` is an arbitrary value
expression that is evaluated for all rows.  A set of rows for
which all the expressions are equal are considered duplicates, and
only the first row of the set is kept in the output.  Note that
the "first row" of a set is unpredictable unless the
query is sorted on enough columns to guarantee a unique ordering
of the rows arriving at the `DISTINCT` filter.
(`DISTINCT ON` processing occurs after `ORDER
BY` sorting.)

The `DISTINCT ON` clause is not part of the SQL standard
and is sometimes considered bad style because of the potentially
indeterminate nature of its results.  With judicious use of
`GROUP BY` and subqueries in `FROM`, this
construct can be avoided, but it is often the most convenient
alternative.

## Combining Queries (`UNION`, `INTERSECT`, `EXCEPT`)

The results of two queries can be combined using the set operations
union, intersection, and difference.  The syntax is

```
`query1` UNION ALL `query2`
`query1` INTERSECT ALL `query2`
`query1` EXCEPT ALL `query2`
```

where `query1` and
`query2` are queries that can use any of
the features discussed up to this point.

`UNION` effectively appends the result of
`query2` to the result of
`query1` (although there is no guarantee
that this is the order in which the rows are actually returned).
Furthermore, it eliminates duplicate rows from its result, in the same
way as `DISTINCT`, unless `UNION ALL` is used.

`INTERSECT` returns all rows that are both in the result
of `query1` and in the result of
`query2`.  Duplicate rows are eliminated
unless `INTERSECT ALL` is used.

`EXCEPT` returns all rows that are in the result of
`query1` but not in the result of
`query2`.  (This is sometimes called the
*difference* between two queries.)  Again, duplicates
are eliminated unless `EXCEPT ALL` is used.

In order to calculate the union, intersection, or difference of two
queries, the two queries must be "union compatible",
which means that they return the same number of columns and
the corresponding columns have compatible data types, as
described in [typeconv-union-case](#typeconv-union-case).

Set operations can be combined, for example

```
`query1` UNION `query2` EXCEPT `query3`
```

which is equivalent to

```
(`query1` UNION `query2`) EXCEPT `query3`
```

As shown here, you can use parentheses to control the order of
evaluation.  Without parentheses, `UNION`
and `EXCEPT` associate left-to-right,
but `INTERSECT` binds more tightly than those two
operators.  Thus

```
`query1` UNION `query2` INTERSECT `query3`
```

means

```
`query1` UNION (`query2` INTERSECT `query3`)
```

You can also surround an individual `query`
with parentheses.  This is important if
the `query` needs to use any of the clauses
discussed in following sections, such as `LIMIT`.
Without parentheses, you'll get a syntax error, or else the clause will
be understood as applying to the output of the set operation rather
than one of its inputs.  For example,

```
SELECT a FROM b UNION SELECT x FROM y LIMIT 10
```

is accepted, but it means

```
(SELECT a FROM b UNION SELECT x FROM y) LIMIT 10
```

not

```
SELECT a FROM b UNION (SELECT x FROM y LIMIT 10)
```

## Sorting Rows (`ORDER BY`)

After a query has produced an output table (after the select list
has been processed) it can optionally be sorted.  If sorting is not
chosen, the rows will be returned in an unspecified order.  The actual
order in that case will depend on the scan and join plan types and
the order on disk, but it must not be relied on.  A particular
output ordering can only be guaranteed if the sort step is explicitly
chosen.

The `ORDER BY` clause specifies the sort order:

```
SELECT `select_list`
FROM `table_expression`
ORDER BY `sort_expression1` ASC | DESC NULLS { FIRST | LAST }
, `sort_expression2` ASC | DESC NULLS { FIRST | LAST } ...
```

The sort expression(s) can be any expression that would be valid in the
query's select list.  An example is:

```
SELECT a, b FROM table1 ORDER BY a + b, c;
```

When more than one expression is specified,
the later values are used to sort rows that are equal according to the
earlier values.  Each expression can be followed by an optional
`ASC` or `DESC` keyword to set the sort direction to
ascending or descending.  `ASC` order is the default.
Ascending order puts smaller values first, where
"smaller" is defined in terms of the
`<` operator.  Similarly, descending order is
determined with the `>` operator.
(Note: Actually, PostgreSQL uses the *default B-tree
operator class* for the expression's data type to determine the sort
ordering for `ASC` and `DESC`.  Conventionally,
data types will be set up so that the `<` and
`>` operators correspond to this sort ordering,
but a user-defined data type's designer could choose to do something
different.)

The `NULLS FIRST` and `NULLS LAST` options can be
used to determine whether nulls appear before or after non-null values
in the sort ordering.  By default, null values sort as if larger than any
non-null value; that is, `NULLS FIRST` is the default for
`DESC` order, and `NULLS LAST` otherwise.

Note that the ordering options are considered independently for each
sort column.  For example `ORDER BY x, y DESC` means
`ORDER BY x ASC, y DESC`, which is not the same as
`ORDER BY x DESC, y DESC`.

A `sort_expression` can also be the column label or number
of an output column, as in:

```
SELECT a + b AS sum, c FROM table1 ORDER BY sum;
SELECT a, max(b) FROM table1 GROUP BY a ORDER BY 1;
```

both of which sort by the first output column.  Note that an output
column name has to stand alone, that is, it cannot be used in an expression
— for example, this is *not* correct:

```
SELECT a + b AS sum, c FROM table1 ORDER BY sum + c;          -- wrong
```

This restriction is made to reduce ambiguity.  There is still
ambiguity if an `ORDER BY` item is a simple name that
could match either an output column name or a column from the table
expression.  The output column is used in such cases.  This would
only cause confusion if you use `AS` to rename an output
column to match some other table column's name.

`ORDER BY` can be applied to the result of a
`UNION`, `INTERSECT`, or `EXCEPT`
combination, but in this case it is only permitted to sort by
output column names or numbers, not by expressions.

## `LIMIT` and `OFFSET`

`LIMIT` and `OFFSET` allow you to retrieve just
a portion of the rows that are generated by the rest of the query:

```
SELECT `select_list`
FROM `table_expression`
ORDER BY ...
LIMIT { `number` | ALL }   OFFSET `number`
```

If a limit count is given, no more than that many rows will be
returned (but possibly fewer, if the query itself yields fewer rows).
`LIMIT ALL` is the same as omitting the `LIMIT`
clause, as is `LIMIT` with a NULL argument.

`OFFSET` says to skip that many rows before beginning to
return rows.  `OFFSET 0` is the same as omitting the
`OFFSET` clause, as is `OFFSET` with a NULL argument.

If both `OFFSET`
and `LIMIT` appear, then `OFFSET` rows are
skipped before starting to count the `LIMIT` rows that
are returned.

When using `LIMIT`, it is important to use an
`ORDER BY` clause that constrains the result rows into a
unique order.  Otherwise you will get an unpredictable subset of
the query's rows. You might be asking for the tenth through
twentieth rows, but tenth through twentieth in what ordering? The
ordering is unknown, unless you specified `ORDER BY`.

The query optimizer takes `LIMIT` into account when
generating query plans, so you are very likely to get different
plans (yielding different row orders) depending on what you give
for `LIMIT` and `OFFSET`.  Thus, using
different `LIMIT`/`OFFSET` values to select
different subsets of a query result *will give
inconsistent results* unless you enforce a predictable
result ordering with `ORDER BY`.  This is not a bug; it
is an inherent consequence of the fact that SQL does not promise to
deliver the results of a query in any particular order unless
`ORDER BY` is used to constrain the order.

The rows skipped by an `OFFSET` clause still have to be
computed inside the server; therefore a large `OFFSET`
might be inefficient.

## `VALUES` Lists

`VALUES` provides a way to generate a "constant table"
that can be used in a query without having to actually create and populate
a table on-disk.  The syntax is

```
VALUES ( `expression` [, ...] ) [, ...]
```

Each parenthesized list of expressions generates a row in the table.
The lists must all have the same number of elements (i.e., the number
of columns in the table), and corresponding entries in each list must
have compatible data types.  The actual data type assigned to each column
of the result is determined using the same rules as for `UNION`
(see [typeconv-union-case](#typeconv-union-case)).

As an example:

```
VALUES (1, 'one'), (2, 'two'), (3, 'three');
```

will return a table of two columns and three rows.  It's effectively
equivalent to:

```
SELECT 1 AS column1, 'one' AS column2
UNION ALL
SELECT 2, 'two'
UNION ALL
SELECT 3, 'three';
```

By default, PostgreSQL assigns the names
`column1`, `column2`, etc. to the columns of a
`VALUES` table.  The column names are not specified by the
SQL standard and different database systems do it differently, so
it's usually better to override the default names with a table alias
list, like this:

```
=> SELECT * FROM (VALUES (1, 'one'), (2, 'two'), (3, 'three')) AS t (num,letter);
num | letter
-----+--------
1 | one
2 | two
3 | three
(3 rows)
```

Syntactically, `VALUES` followed by expression lists is
treated as equivalent to:

```
SELECT `select_list` FROM `table_expression`
```

and can appear anywhere a `SELECT` can.  For example, you can
use it as part of a `UNION`, or attach a
`sort_specification` (`ORDER BY`,
`LIMIT`, and/or `OFFSET`) to it.  `VALUES`
is most commonly used as the data source in an `INSERT` command,
and next most commonly as a subquery.

For more information see [sql-values](#sql-values).

## `WITH` Queries (Common Table Expressions)

`WITH` provides a way to write auxiliary statements for use in a
larger query.  These statements, which are often referred to as Common
Table Expressions or CTEs, can be thought of as defining
temporary tables that exist just for one query.  Each auxiliary statement
in a `WITH` clause can be a `SELECT`,
`INSERT`, `UPDATE`, or `DELETE`; and the
`WITH` clause itself is attached to a primary statement that can
be a `SELECT`, `INSERT`, `UPDATE`,
`DELETE`, or `MERGE`.

### `SELECT` in `WITH`

The basic value of `SELECT` in `WITH` is to
break down complicated queries into simpler parts.  An example is:

```
WITH regional_sales AS (
SELECT region, SUM(amount) AS total_sales
FROM orders
GROUP BY region
), top_regions AS (
SELECT region
FROM regional_sales
WHERE total_sales > (SELECT SUM(total_sales)/10 FROM regional_sales)
)
SELECT region,
product,
SUM(quantity) AS product_units,
SUM(amount) AS product_sales
FROM orders
WHERE region IN (SELECT region FROM top_regions)
GROUP BY region, product;
```

which displays per-product sales totals in only the top sales regions.
The `WITH` clause defines two auxiliary statements named
`regional_sales` and `top_regions`,
where the output of `regional_sales` is used in
`top_regions` and the output of `top_regions`
is used in the primary `SELECT` query.
This example could have been written without `WITH`,
but we'd have needed two levels of nested sub-`SELECT`s.  It's a bit
easier to follow this way.

### Recursive Queries

The optional `RECURSIVE` modifier changes `WITH`
from a mere syntactic convenience into a feature that accomplishes
things not otherwise possible in standard SQL.  Using
`RECURSIVE`, a `WITH` query can refer to its own
output.  A very simple example is this query to sum the integers from 1
through 100:

```
WITH RECURSIVE t(n) AS (
VALUES (1)
UNION ALL
SELECT n+1 FROM t WHERE n  **Note:**

> While `RECURSIVE` allows queries to be specified
> recursively, internally such queries are evaluated iteratively.
>

In the example above, the working table has just a single row in each step,
and it takes on the values from 1 through 100 in successive steps.  In
the 100th step, there is no output because of the `WHERE`
clause, and so the query terminates.

Recursive queries are typically used to deal with hierarchical or
tree-structured data.  A useful example is this query to find all the
direct and indirect sub-parts of a product, given only a table that
shows immediate inclusions:

```
WITH RECURSIVE included_parts(sub_part, part, quantity) AS (
SELECT sub_part, part, quantity FROM parts WHERE part = 'our_product'
UNION ALL
SELECT p.sub_part, p.part, p.quantity * pr.quantity
FROM included_parts pr, parts p
WHERE p.part = pr.sub_part
)
SELECT sub_part, SUM(quantity) as total_quantity
FROM included_parts
GROUP BY sub_part
```

#### Search Order

When computing a tree traversal using a recursive query, you might want to
order the results in either depth-first or breadth-first order.  This can
be done by computing an ordering column alongside the other data columns
and using that to sort the results at the end.  Note that this does not
actually control in which order the query evaluation visits the rows; that
is as always in SQL implementation-dependent.  This approach merely
provides a convenient way to order the results afterwards.

To create a depth-first order, we compute for each result row an array of
rows that we have visited so far.  For example, consider the following
query that searches a table `tree` using a
`link` field:

```
WITH RECURSIVE search_tree(id, link, data) AS (
SELECT t.id, t.link, t.data
FROM tree t
UNION ALL
SELECT t.id, t.link, t.data
FROM tree t, search_tree st
WHERE t.id = st.link
)
SELECT * FROM search_tree;
```

To add depth-first ordering information, you can write this:

```
WITH RECURSIVE search_tree(id, link, data, *path*) AS (
SELECT t.id, t.link, t.data, *ARRAY[t.id]*
FROM tree t
UNION ALL
SELECT t.id, t.link, t.data, *path || t.id*
FROM tree t, search_tree st
WHERE t.id = st.link
)
SELECT * FROM search_tree *ORDER BY path*;
```

In the general case where more than one field needs to be used to identify
a row, use an array of rows.  For example, if we needed to track fields
`f1` and `f2`:

```
WITH RECURSIVE search_tree(id, link, data, *path*) AS (
SELECT t.id, t.link, t.data, *ARRAY[ROW(t.f1, t.f2)]*
FROM tree t
UNION ALL
SELECT t.id, t.link, t.data, *path || ROW(t.f1, t.f2)*
FROM tree t, search_tree st
WHERE t.id = st.link
)
SELECT * FROM search_tree *ORDER BY path*;
```

> **Tip:**

> Omit the `ROW()` syntax in the common case where only one
> field needs to be tracked.  This allows a simple array rather than a
> composite-type array to be used, gaining efficiency.
>

To create a breadth-first order, you can add a column that tracks the depth
of the search, for example:

```
WITH RECURSIVE search_tree(id, link, data, *depth*) AS (
SELECT t.id, t.link, t.data, *0*
FROM tree t
UNION ALL
SELECT t.id, t.link, t.data, *depth + 1*
FROM tree t, search_tree st
WHERE t.id = st.link
)
SELECT * FROM search_tree *ORDER BY depth*;
```

To get a stable sort, add data columns as secondary sorting columns.

> **Tip:**

> The recursive query evaluation algorithm produces its output in
> breadth-first search order.  However, this is an implementation detail and
> it is perhaps unsound to rely on it.  The order of the rows within each
> level is certainly undefined, so some explicit ordering might be desired
> in any case.
>

There is built-in syntax to compute a depth- or breadth-first sort column.
For example:

```
WITH RECURSIVE search_tree(id, link, data) AS (
SELECT t.id, t.link, t.data
FROM tree t
UNION ALL
SELECT t.id, t.link, t.data
FROM tree t, search_tree st
WHERE t.id = st.link
) *SEARCH DEPTH FIRST BY id SET ordercol*
SELECT * FROM search_tree ORDER BY ordercol;

WITH RECURSIVE search_tree(id, link, data) AS (
SELECT t.id, t.link, t.data
FROM tree t
UNION ALL
SELECT t.id, t.link, t.data
FROM tree t, search_tree st
WHERE t.id = st.link
) *SEARCH BREADTH FIRST BY id SET ordercol*
SELECT * FROM search_tree ORDER BY ordercol;
```

This syntax is internally expanded to something similar to the above
hand-written forms.  The `SEARCH` clause specifies whether
depth- or breadth first search is wanted, the list of columns to track for
sorting, and a column name that will contain the result data that can be
used for sorting.  That column will implicitly be added to the output rows
of the CTE.

#### Cycle Detection

When working with recursive queries it is important to be sure that
the recursive part of the query will eventually return no tuples,
or else the query will loop indefinitely.  Sometimes, using
`UNION` instead of `UNION ALL` can accomplish this
by discarding rows that duplicate previous output rows.  However, often a
cycle does not involve output rows that are completely duplicate: it may be
necessary to check just one or a few fields to see if the same point has
been reached before.  The standard method for handling such situations is
to compute an array of the already-visited values.  For example, consider again
the following query that searches a table `graph` using a
`link` field:

```
WITH RECURSIVE search_graph(id, link, data, depth) AS (
SELECT g.id, g.link, g.data, 0
FROM graph g
UNION ALL
SELECT g.id, g.link, g.data, sg.depth + 1
FROM graph g, search_graph sg
WHERE g.id = sg.link
)
SELECT * FROM search_graph;
```

This query will loop if the `link` relationships contain
cycles.  Because we require a "depth" output, just changing
`UNION ALL` to `UNION` would not eliminate the looping.
Instead we need to recognize whether we have reached the same row again
while following a particular path of links.  We add two columns
`is_cycle` and `path` to the loop-prone query:

```
WITH RECURSIVE search_graph(id, link, data, depth, *is_cycle, path*) AS (
SELECT g.id, g.link, g.data, 0,
*false,
ARRAY[g.id]*
FROM graph g
UNION ALL
SELECT g.id, g.link, g.data, sg.depth + 1,
*g.id = ANY(path),
path || g.id*
FROM graph g, search_graph sg
WHERE g.id = sg.link *AND NOT is_cycle*
)
SELECT * FROM search_graph;
```

Aside from preventing cycles, the array value is often useful in its own
right as representing the "path" taken to reach any particular row.

In the general case where more than one field needs to be checked to
recognize a cycle, use an array of rows.  For example, if we needed to
compare fields `f1` and `f2`:

```
WITH RECURSIVE search_graph(id, link, data, depth, *is_cycle, path*) AS (
SELECT g.id, g.link, g.data, 0,
*false,
ARRAY[ROW(g.f1, g.f2)]*
FROM graph g
UNION ALL
SELECT g.id, g.link, g.data, sg.depth + 1,
*ROW(g.f1, g.f2) = ANY(path),
path || ROW(g.f1, g.f2)*
FROM graph g, search_graph sg
WHERE g.id = sg.link *AND NOT is_cycle*
)
SELECT * FROM search_graph;
```

> **Tip:**

> Omit the `ROW()` syntax in the common case where only one field
> needs to be checked to recognize a cycle.  This allows a simple array
> rather than a composite-type array to be used, gaining efficiency.
>

There is built-in syntax to simplify cycle detection.  The above query can
also be written like this:

```
WITH RECURSIVE search_graph(id, link, data, depth) AS (
SELECT g.id, g.link, g.data, 1
FROM graph g
UNION ALL
SELECT g.id, g.link, g.data, sg.depth + 1
FROM graph g, search_graph sg
WHERE g.id = sg.link
) *CYCLE id SET is_cycle USING path*
SELECT * FROM search_graph;
```

and it will be internally rewritten to the above form.  The
`CYCLE` clause specifies first the list of columns to
track for cycle detection, then a column name that will show whether a
cycle has been detected, and finally the name of another column that will track the
path.  The cycle and path columns will implicitly be added to the output
rows of the CTE.

> **Tip:**

> The cycle path column is computed in the same way as the depth-first
> ordering column show in the previous section.  A query can have both a
> `SEARCH` and a `CYCLE` clause, but a
> depth-first search specification and a cycle detection specification would
> create redundant computations, so it's more efficient to just use the
> `CYCLE` clause and order by the path column.  If
> breadth-first ordering is wanted, then specifying both
> `SEARCH` and `CYCLE` can be useful.
>

A helpful trick for testing queries
when you are not certain if they might loop is to place a `LIMIT`
in the parent query.  For example, this query would loop forever without
the `LIMIT`:

```
WITH RECURSIVE t(n) AS (
SELECT 1
UNION ALL
SELECT n+1 FROM t
)
SELECT n FROM t *LIMIT 100*;
```

This works because PostgreSQL's implementation
evaluates only as many rows of a `WITH` query as are actually
fetched by the parent query.  Using this trick in production is not
recommended, because other systems might work differently.  Also, it
usually won't work if you make the outer query sort the recursive query's
results or join them to some other table, because in such cases the
outer query will usually try to fetch all of the `WITH` query's
output anyway.

### Common Table Expression Materialization

A useful property of `WITH` queries is that they are
normally evaluated only once per execution of the parent query, even if
they are referred to more than once by the parent query or
sibling `WITH` queries.
Thus, expensive calculations that are needed in multiple places can be
placed within a `WITH` query to avoid redundant work.  Another
possible application is to prevent unwanted multiple evaluations of
functions with side-effects.
However, the other side of this coin is that the optimizer is not able to
push restrictions from the parent query down into a multiply-referenced
`WITH` query, since that might affect all uses of the
`WITH` query's output when it should affect only one.
The multiply-referenced `WITH` query will be
evaluated as written, without suppression of rows that the parent query
might discard afterwards.  (But, as mentioned above, evaluation might stop
early if the reference(s) to the query demand only a limited number of
rows.)

However, if a `WITH` query is non-recursive and
side-effect-free (that is, it is a `SELECT` containing
no volatile functions) then it can be folded into the parent query,
allowing joint optimization of the two query levels.  By default, this
happens if the parent query references the `WITH` query
just once, but not if it references the `WITH` query
more than once.  You can override that decision by
specifying `MATERIALIZED` to force separate calculation
of the `WITH` query, or by specifying `NOT
MATERIALIZED` to force it to be merged into the parent query.
The latter choice risks duplicate computation of
the `WITH` query, but it can still give a net savings if
each usage of the `WITH` query needs only a small part
of the `WITH` query's full output.

A simple example of these rules is

```
WITH w AS (
SELECT * FROM big_table
)
SELECT * FROM w WHERE key = 123;
```

This `WITH` query will be folded, producing the same
execution plan as

```
SELECT * FROM big_table WHERE key = 123;
```

In particular, if there's an index on `key`,
it will probably be used to fetch just the rows having `key =
123`.  On the other hand, in

```
WITH w AS (
SELECT * FROM big_table
)
SELECT * FROM w AS w1 JOIN w AS w2 ON w1.key = w2.ref
WHERE w2.key = 123;
```

the `WITH` query will be materialized, producing a
temporary copy of `big_table` that is then
joined with itself — without benefit of any index.  This query
will be executed much more efficiently if written as

```
WITH w AS NOT MATERIALIZED (
SELECT * FROM big_table
)
SELECT * FROM w AS w1 JOIN w AS w2 ON w1.key = w2.ref
WHERE w2.key = 123;
```

so that the parent query's restrictions can be applied directly
to scans of `big_table`.

An example where `NOT MATERIALIZED` could be
undesirable is

```
WITH w AS (
SELECT key, very_expensive_function(val) as f FROM some_table
)
SELECT * FROM w AS w1 JOIN w AS w2 ON w1.f = w2.f;
```

Here, materialization of the `WITH` query ensures
that `very_expensive_function` is evaluated only
once per table row, not twice.

The examples above only show `WITH` being used with
`SELECT`, but it can be attached in the same way to
`INSERT`, `UPDATE`,
`DELETE`, or `MERGE`.
In each case it effectively provides temporary table(s) that can
be referred to in the main command.

### Data-Modifying Statements in `WITH`

You can use most data-modifying statements (`INSERT`,
`UPDATE`, or `DELETE`, but not
`MERGE`) in `WITH`.  This
allows you to perform several different operations in the same query.
An example is:

```
WITH moved_rows AS (
DELETE FROM products
WHERE
"date" >= '2010-10-01' AND
"date" < '2010-11-01'
RETURNING *
)
INSERT INTO products_log
SELECT * FROM moved_rows;
```

This query effectively moves rows from `products` to
`products_log`.  The `DELETE` in `WITH`
deletes the specified rows from `products`, returning their
contents by means of its `RETURNING` clause; and then the
primary query reads that output and inserts it into
`products_log`.

A fine point of the above example is that the `WITH` clause is
attached to the `INSERT`, not the sub-`SELECT` within
the `INSERT`.  This is necessary because data-modifying
statements are only allowed in `WITH` clauses that are attached
to the top-level statement.  However, normal `WITH` visibility
rules apply, so it is possible to refer to the `WITH`
statement's output from the sub-`SELECT`.

Data-modifying statements in `WITH` usually have
`RETURNING` clauses (see [dml-returning](#dml-returning)),
as shown in the example above.
It is the output of the `RETURNING` clause, *not* the
target table of the data-modifying statement, that forms the temporary
table that can be referred to by the rest of the query.  If a
data-modifying statement in `WITH` lacks a `RETURNING`
clause, then it forms no temporary table and cannot be referred to in
the rest of the query.  Such a statement will be executed nonetheless.
A not-particularly-useful example is:

```
WITH t AS (
DELETE FROM foo
)
DELETE FROM bar;
```

This example would remove all rows from tables `foo` and
`bar`.  The number of affected rows reported to the client
would only include rows removed from `bar`.

Recursive self-references in data-modifying statements are not
allowed.  In some cases it is possible to work around this limitation by
referring to the output of a recursive `WITH`, for example:

```
WITH RECURSIVE included_parts(sub_part, part) AS (
SELECT sub_part, part FROM parts WHERE part = 'our_product'
UNION ALL
SELECT p.sub_part, p.part
FROM included_parts pr, parts p
WHERE p.part = pr.sub_part
)
DELETE FROM parts
WHERE part IN (SELECT part FROM included_parts);
```

This query would remove all direct and indirect subparts of a product.

Data-modifying statements in `WITH` are executed exactly once,
and always to completion, independently of whether the primary query
reads all (or indeed any) of their output.  Notice that this is different
from the rule for `SELECT` in `WITH`: as stated in the
previous section, execution of a `SELECT` is carried only as far
as the primary query demands its output.

The sub-statements in `WITH` are executed concurrently with
each other and with the main query.  Therefore, when using data-modifying
statements in `WITH`, the order in which the specified updates
actually happen is unpredictable.  All the statements are executed with
the same *snapshot* (see [mvcc](#mvcc)), so they
cannot "see" one another's effects on the target tables.  This
alleviates the effects of the unpredictability of the actual order of row
updates, and means that `RETURNING` data is the only way to
communicate changes between different `WITH` sub-statements and
the main query.  An example of this is that in

```
WITH t AS (
UPDATE products SET price = price * 1.05
RETURNING *
)
SELECT * FROM products;
```

the outer `SELECT` would return the original prices before the
action of the `UPDATE`, while in

```
WITH t AS (
UPDATE products SET price = price * 1.05
RETURNING *
)
SELECT * FROM t;
```

the outer `SELECT` would return the updated data.

Trying to update the same row twice in a single statement is not
supported.  Only one of the modifications takes place, but it is not easy
(and sometimes not possible) to reliably predict which one.  This also
applies to deleting a row that was already updated in the same statement:
only the update is performed.  Therefore you should generally avoid trying
to modify a single row twice in a single statement.  In particular avoid
writing `WITH` sub-statements that could affect the same rows
changed by the main statement or a sibling sub-statement.  The effects
of such a statement will not be predictable.

At present, any table used as the target of a data-modifying statement in
`WITH` must not have a conditional rule, nor an `ALSO`
rule, nor an `INSTEAD` rule that expands to multiple statements.
