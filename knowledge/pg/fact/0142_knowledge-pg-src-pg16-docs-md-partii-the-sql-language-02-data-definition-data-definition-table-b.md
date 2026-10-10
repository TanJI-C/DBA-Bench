# Table Basics; Default Values; Generated Columns; Constraints; System Columns; Modifying Tables; Inheritance; Foreign Data; Other Database Objects; Dependency Tracking

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/02_data_definition.md`
- Source Title: `Data Definition`
- Source Heading Path: `Data Definition > Table Basics; Default Values; Generated Columns; Constraints; System Columns; Modifying Tables; Inheritance; Foreign Data; Other Database Objects; Dependency Tracking`
- Source Line Ranges: `14-123, 124-176, 177-274, 275-954, 955-1018, 1019-1223, 2274-2562, 2925-3045, 3169-3209, 3210-3226, 3227-3331`
- Chunk ID: `pg16_fact_0142_cb0f019e7a`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `4ff30808d9fc103a5f0d772534141a3b998a8bd3180e3a1bb0353e5e477fa96a`

## Retrieval Guidance

- Use When: Need base facts about defining and altering database objects.
- Retrieval Keywords: CREATE TABLE, DEFAULT, generated column, constraint, system column, ALTER TABLE, inheritance, foreign table, dependency
- Follow-up Guidance: For performance or maintenance actions involving partitions or indexes, use the solution records.
- Classification Note: Reference material for SQL objects, columns, defaults, generated columns, constraints, system columns, ALTER TABLE mechanics, inheritance, foreign data, object categories, and dependency behavior.

## Official Source Content

## Table Basics

A table in a relational database is much like a table on paper: It
consists of rows and columns.  The number and order of the columns
is fixed, and each column has a name.  The number of rows is
variable — it reflects how much data is stored at a given moment.
SQL does not make any guarantees about the order of the rows in a
table.  When a table is read, the rows will appear in an unspecified order,
unless sorting is explicitly requested.  This is covered in [queries](#queries).  Furthermore, SQL does not assign unique
identifiers to rows, so it is possible to have several completely
identical rows in a table.  This is a consequence of the
mathematical model that underlies SQL but is usually not desirable.
Later in this chapter we will see how to deal with this issue.

Each column has a data type.  The data type constrains the set of
possible values that can be assigned to a column and assigns
semantics to the data stored in the column so that it can be used
for computations.  For instance, a column declared to be of a
numerical type will not accept arbitrary text strings, and the data
stored in such a column can be used for mathematical computations.
By contrast, a column declared to be of a character string type
will accept almost any kind of data but it does not lend itself to
mathematical calculations, although other operations such as string
concatenation are available.

PostgreSQL includes a sizable set of
built-in data types that fit many applications.  Users can also
define their own data types.  Most built-in data types have obvious
names and semantics, so we defer a detailed explanation to [datatype](#datatype).  Some of the frequently used data types are
`integer` for whole numbers, `numeric` for
possibly fractional numbers, `text` for character
strings, `date` for dates, `time` for
time-of-day values, and `timestamp` for values
containing both date and time.

To create a table, you use the aptly named [sql-createtable](#sql-createtable) command.
In this command you specify at least a name for the new table, the
names of the columns and the data type of each column.  For
example:

```
CREATE TABLE my_first_table (
first_column text,
second_column integer
);
```

This creates a table named `my_first_table` with
two columns.  The first column is named
`first_column` and has a data type of
`text`; the second column has the name
`second_column` and the type `integer`.
The table and column names follow the identifier syntax explained
in [sql-syntax-identifiers](#sql-syntax-identifiers).  The type names are
usually also identifiers, but there are some exceptions.  Note that the
column list is comma-separated and surrounded by parentheses.

Of course, the previous example was heavily contrived.  Normally,
you would give names to your tables and columns that convey what
kind of data they store.  So let's look at a more realistic
example:

```
CREATE TABLE products (
product_no integer,
name text,
price numeric
);
```

(The `numeric` type can store fractional components, as
would be typical of monetary amounts.)

> **Tip:**

> When you create many interrelated tables it is wise to choose a
> consistent naming pattern for the tables and columns.  For
> instance, there is a choice of using singular or plural nouns for
> table names, both of which are favored by some theorist or other.
>

There is a limit on how many columns a table can contain.
Depending on the column types, it is between 250 and 1600.
However, defining a table with anywhere near this many columns is
highly unusual and often a questionable design.

If you no longer need a table, you can remove it using the [sql-droptable](#sql-droptable) command.
For example:

```
DROP TABLE my_first_table;
DROP TABLE products;
```

Attempting to drop a table that does not exist is an error.
Nevertheless, it is common in SQL script files to unconditionally
try to drop each table before creating it, ignoring any error
messages, so that the script works whether or not the table exists.
(If you like, you can use the `DROP TABLE IF EXISTS` variant
to avoid the error messages, but this is not standard SQL.)

If you need to modify a table that already exists, see [ddl-alter](#ddl-alter) later in this chapter.

With the tools discussed so far you can create fully functional
tables.  The remainder of this chapter is concerned with adding
features to the table definition to ensure data integrity,
security, or convenience.  If you are eager to fill your tables with
data now you can skip ahead to [dml](#dml) and read the
rest of this chapter later.

## Default Values

A column can be assigned a default value.  When a new row is
created and no values are specified for some of the columns, those
columns will be filled with their respective default values.  A
data manipulation command can also request explicitly that a column
be set to its default value, without having to know what that value is.
(Details about data manipulation commands are in [dml](#dml).)

If no default value is declared explicitly, the default value is the
null value.  This usually makes sense because a null value can
be considered to represent unknown data.

In a table definition, default values are listed after the column
data type.  For example:

```
CREATE TABLE products (
product_no integer,
name text,
price numeric *DEFAULT 9.99*
);
```

The default value can be an expression, which will be
evaluated whenever the default value is inserted
(*not* when the table is created).  A common example
is for a `timestamp` column to have a default of `CURRENT_TIMESTAMP`,
so that it gets set to the time of row insertion.  Another common
example is generating a "serial number" for each row.
In PostgreSQL this is typically done by
something like:

```
CREATE TABLE products (
product_no integer *DEFAULT nextval('products_product_no_seq')*,
...
);
```

where the `nextval()` function supplies successive values
from a *sequence object* (see [functions-sequence](#functions-sequence)). This arrangement is sufficiently common
that there's a special shorthand for it:

```
CREATE TABLE products (
product_no *SERIAL*,
...
);
```

The `SERIAL` shorthand is discussed further in [datatype-serial](#datatype-serial).

## Generated Columns

A generated column is a special column that is always computed from other
columns.  Thus, it is for columns what a view is for tables.  There are two
kinds of generated columns: stored and virtual.  A stored generated column
is computed when it is written (inserted or updated) and occupies storage
as if it were a normal column.  A virtual generated column occupies no
storage and is computed when it is read.  Thus, a virtual generated column
is similar to a view and a stored generated column is similar to a
materialized view (except that it is always updated automatically).
PostgreSQL currently implements only stored generated columns.

To create a generated column, use the `GENERATED ALWAYS
AS` clause in `CREATE TABLE`, for example:

```
CREATE TABLE people (
...,
height_cm numeric,
height_in numeric *GENERATED ALWAYS AS (height_cm / 2.54) STORED*
);
```

The keyword `STORED` must be specified to choose the
stored kind of generated column.  See [sql-createtable](#sql-createtable) for
more details.

A generated column cannot be written to directly.  In
`INSERT` or `UPDATE` commands, a value
cannot be specified for a generated column, but the keyword
`DEFAULT` may be specified.

Consider the differences between a column with a default and a generated
column.  The column default is evaluated once when the row is first
inserted if no other value was provided; a generated column is updated
whenever the row changes and cannot be overridden.  A column default may
not refer to other columns of the table; a generation expression would
normally do so.  A column default can use volatile functions, for example
`random()` or functions referring to the current time;
this is not allowed for generated columns.

Several restrictions apply to the definition of generated columns and
tables involving generated columns:

- The generation expression can only use immutable functions and cannot
use subqueries or reference anything other than the current row in any
way.
- A generation expression cannot reference another generated column.
- A generation expression cannot reference a system column, except
`tableoid`.
- A generated column cannot have a column default or an identity definition.
- A generated column cannot be part of a partition key.
- Foreign tables can have generated columns.  See [sql-createforeigntable](#sql-createforeigntable) for details.
- For inheritance and partitioning:

If a parent column is a generated column, its child column must also
be a generated column; however, the child column can have a
different generation expression.  The generation expression that is
actually applied during insert or update of a row is the one
associated with the table that the row is physically in.
(This is unlike the behavior for column defaults: for those, the
default value associated with the table named in the query applies.)
- If a parent column is not a generated column, its child column must
not be generated either.
- For inherited tables, if you write a child column definition without
any `GENERATED` clause in `CREATE TABLE
... INHERITS`, then its `GENERATED` clause
will automatically be copied from the parent.  `ALTER TABLE
... INHERIT` will insist that parent and child columns
already match as to generation status, but it will not require their
generation expressions to match.
- Similarly for partitioned tables, if you write a child column
definition without any `GENERATED` clause
in `CREATE TABLE ... PARTITION OF`, then
its `GENERATED` clause will automatically be copied
from the parent.  `ALTER TABLE ... ATTACH PARTITION`
will insist that parent and child columns already match as to
generation status, but it will not require their generation
expressions to match.
- In case of multiple inheritance, if one parent column is a generated
column, then all parent columns must be generated columns.  If they
do not all have the same generation expression, then the desired
expression for the child must be specified explicitly.

Additional considerations apply to the use of generated columns.

- Generated columns maintain access privileges separately from their
underlying base columns.  So, it is possible to arrange it so that a
particular role can read from a generated column but not from the
underlying base columns.
- Generated columns are, conceptually, updated after
`BEFORE` triggers have run.  Therefore, changes made to
base columns in a `BEFORE` trigger will be reflected in
generated columns.  But conversely, it is not allowed to access
generated columns in `BEFORE` triggers.
- Generated columns are skipped for logical replication and cannot be
specified in a `CREATE PUBLICATION` column list.

## Constraints

Data types are a way to limit the kind of data that can be stored
in a table.  For many applications, however, the constraint they
provide is too coarse.  For example, a column containing a product
price should probably only accept positive values.  But there is no
standard data type that accepts only positive numbers.  Another issue is
that you might want to constrain column data with respect to other
columns or rows.  For example, in a table containing product
information, there should be only one row for each product number.

To that end, SQL allows you to define constraints on columns and
tables.  Constraints give you as much control over the data in your
tables as you wish.  If a user attempts to store data in a column
that would violate a constraint, an error is raised.  This applies
even if the value came from the default value definition.

### Check Constraints

A check constraint is the most generic constraint type.  It allows
you to specify that the value in a certain column must satisfy a
Boolean (truth-value) expression.  For instance, to require positive
product prices, you could use:

```
CREATE TABLE products (
product_no integer,
name text,
price numeric *CHECK (price > 0)*
);
```

As you see, the constraint definition comes after the data type,
just like default value definitions.  Default values and
constraints can be listed in any order.  A check constraint
consists of the key word `CHECK` followed by an
expression in parentheses.  The check constraint expression should
involve the column thus constrained, otherwise the constraint
would not make too much sense.

You can also give the constraint a separate name.  This clarifies
error messages and allows you to refer to the constraint when you
need to change it.  The syntax is:

```
CREATE TABLE products (
product_no integer,
name text,
price numeric *CONSTRAINT positive_price* CHECK (price > 0)
);
```

So, to specify a named constraint, use the key word
`CONSTRAINT` followed by an identifier followed
by the constraint definition.  (If you don't specify a constraint
name in this way, the system chooses a name for you.)

A check constraint can also refer to several columns.  Say you
store a regular price and a discounted price, and you want to
ensure that the discounted price is lower than the regular price:

```
CREATE TABLE products (
product_no integer,
name text,
price numeric CHECK (price > 0),
discounted_price numeric CHECK (discounted_price > 0),
*CHECK (price > discounted_price)*
);
```

The first two constraints should look familiar.  The third one
uses a new syntax.  It is not attached to a particular column,
instead it appears as a separate item in the comma-separated
column list.  Column definitions and these constraint
definitions can be listed in mixed order.

We say that the first two constraints are column constraints, whereas the
third one is a table constraint because it is written separately
from any one column definition.  Column constraints can also be
written as table constraints, while the reverse is not necessarily
possible, since a column constraint is supposed to refer to only the
column it is attached to.  (PostgreSQL doesn't
enforce that rule, but you should follow it if you want your table
definitions to work with other database systems.)  The above example could
also be written as:

```
CREATE TABLE products (
product_no integer,
name text,
price numeric,
CHECK (price > 0),
discounted_price numeric,
CHECK (discounted_price > 0),
CHECK (price > discounted_price)
);
```

or even:

```
CREATE TABLE products (
product_no integer,
name text,
price numeric CHECK (price > 0),
discounted_price numeric,
CHECK (discounted_price > 0 AND price > discounted_price)
);
```

It's a matter of taste.

Names can be assigned to table constraints in the same way as
column constraints:

```
CREATE TABLE products (
product_no integer,
name text,
price numeric,
CHECK (price > 0),
discounted_price numeric,
CHECK (discounted_price > 0),
*CONSTRAINT valid_discount* CHECK (price > discounted_price)
);
```

It should be noted that a check constraint is satisfied if the
check expression evaluates to true or the null value.  Since most
expressions will evaluate to the null value if any operand is null,
they will not prevent null values in the constrained columns.  To
ensure that a column does not contain null values, the not-null
constraint described in the next section can be used.

> **Note:**

> PostgreSQL does not support
> `CHECK` constraints that reference table data other than
> the new or updated row being checked.  While a `CHECK`
> constraint that violates this rule may appear to work in simple
> tests, it cannot guarantee that the database will not reach a state
> in which the constraint condition is false (due to subsequent changes
> of the other row(s) involved).  This would cause a database dump and
> restore to fail.  The restore could fail even when the complete
> database state is consistent with the constraint, due to rows not
> being loaded in an order that will satisfy the constraint.  If
> possible, use `UNIQUE`, `EXCLUDE`,
> or `FOREIGN KEY` constraints to express
> cross-row and cross-table restrictions.
>

>

> If what you desire is a one-time check against other rows at row
> insertion, rather than a continuously-maintained consistency
> guarantee, a custom [trigger](#triggers) can be used
> to implement that.  (This approach avoids the dump/restore problem because
> pg_dump does not reinstall triggers until after
> restoring data, so that the check will not be enforced during a
> dump/restore.)
>

> **Note:**

> PostgreSQL assumes that
> `CHECK` constraints' conditions are immutable, that
> is, they will always give the same result for the same input row.
> This assumption is what justifies examining `CHECK`
> constraints only when rows are inserted or updated, and not at other
> times.  (The warning above about not referencing other table data is
> really a special case of this restriction.)
>

>

> An example of a common way to break this assumption is to reference a
> user-defined function in a `CHECK` expression, and
> then change the behavior of that
> function.  PostgreSQL does not disallow
> that, but it will not notice if there are rows in the table that now
> violate the `CHECK` constraint. That would cause a
> subsequent database dump and restore to fail.
> The recommended way to handle such a change is to drop the constraint
> (using `ALTER TABLE`), adjust the function definition,
> and re-add the constraint, thereby rechecking it against all table rows.
>

### Not-Null Constraints

A not-null constraint simply specifies that a column must not
assume the null value.  A syntax example:

```
CREATE TABLE products (
product_no integer *NOT NULL*,
name text *NOT NULL*,
price numeric
);
```

A not-null constraint is always written as a column constraint.  A
not-null constraint is functionally equivalent to creating a check
constraint `CHECK (`column_name`
IS NOT NULL)`, but in
PostgreSQL creating an explicit
not-null constraint is more efficient.  The drawback is that you
cannot give explicit names to not-null constraints created this
way.

Of course, a column can have more than one constraint.  Just write
the constraints one after another:

```
CREATE TABLE products (
product_no integer NOT NULL,
name text NOT NULL,
price numeric NOT NULL CHECK (price > 0)
);
```

The order doesn't matter.  It does not necessarily determine in which
order the constraints are checked.

The `NOT NULL` constraint has an inverse: the
`NULL` constraint.  This does not mean that the
column must be null, which would surely be useless.  Instead, this
simply selects the default behavior that the column might be null.
The `NULL` constraint is not present in the SQL
standard and should not be used in portable applications.  (It was
only added to PostgreSQL to be
compatible with some other database systems.)  Some users, however,
like it because it makes it easy to toggle the constraint in a
script file.  For example, you could start with:

```
CREATE TABLE products (
product_no integer NULL,
name text NULL,
price numeric NULL
);
```

and then insert the `NOT` key word where desired.

> **Tip:**

> In most database designs the majority of columns should be marked
> not null.
>

### Unique Constraints

Unique constraints ensure that the data contained in a column, or a
group of columns, is unique among all the rows in the
table.  The syntax is:

```
CREATE TABLE products (
product_no integer *UNIQUE*,
name text,
price numeric
);
```

when written as a column constraint, and:

```
CREATE TABLE products (
product_no integer,
name text,
price numeric,
*UNIQUE (product_no)*
);
```

when written as a table constraint.

To define a unique constraint for a group of columns, write it as a
table constraint with the column names separated by commas:

```
CREATE TABLE example (
a integer,
b integer,
c integer,
*UNIQUE (a, c)*
);
```

This specifies that the combination of values in the indicated columns
is unique across the whole table, though any one of the columns
need not be (and ordinarily isn't) unique.

You can assign your own name for a unique constraint, in the usual way:

```
CREATE TABLE products (
product_no integer *CONSTRAINT must_be_different* UNIQUE,
name text,
price numeric
);
```

Adding a unique constraint will automatically create a unique B-tree
index on the column or group of columns listed in the constraint.
A uniqueness restriction covering only some rows cannot be written as
a unique constraint, but it is possible to enforce such a restriction by
creating a unique [partial index](#indexes-partial).

In general, a unique constraint is violated if there is more than
one row in the table where the values of all of the
columns included in the constraint are equal.
By default, two null values are not considered equal in this
comparison.  That means even in the presence of a
unique constraint it is possible to store duplicate
rows that contain a null value in at least one of the constrained
columns.  This behavior can be changed by adding the clause `NULLS
NOT DISTINCT`, like

```
CREATE TABLE products (
product_no integer UNIQUE *NULLS NOT DISTINCT*,
name text,
price numeric
);
```

or

```
CREATE TABLE products (
product_no integer,
name text,
price numeric,
UNIQUE *NULLS NOT DISTINCT* (product_no)
);
```

The default behavior can be specified explicitly using `NULLS
DISTINCT`.  The default null treatment in unique constraints is
implementation-defined according to the SQL standard, and other
implementations have a different behavior.  So be careful when developing
applications that are intended to be portable.

### Primary Keys

A primary key constraint indicates that a column, or group of columns,
can be used as a unique identifier for rows in the table.  This
requires that the values be both unique and not null.  So, the following
two table definitions accept the same data:

```
CREATE TABLE products (
product_no integer UNIQUE NOT NULL,
name text,
price numeric
);
```

```
CREATE TABLE products (
product_no integer *PRIMARY KEY*,
name text,
price numeric
);
```

Primary keys can span more than one column; the syntax
is similar to unique constraints:

```
CREATE TABLE example (
a integer,
b integer,
c integer,
*PRIMARY KEY (a, c)*
);
```

Adding a primary key will automatically create a unique B-tree index
on the column or group of columns listed in the primary key, and will
force the column(s) to be marked `NOT NULL`.

A table can have at most one primary key.  (There can be any number
of unique and not-null constraints, which are functionally almost the
same thing, but only one can be identified as the primary key.)
Relational database theory
dictates that every table must have a primary key.  This rule is
not enforced by PostgreSQL, but it is
usually best to follow it.

Primary keys are useful both for
documentation purposes and for client applications.  For example,
a GUI application that allows modifying row values probably needs
to know the primary key of a table to be able to identify rows
uniquely.  There are also various ways in which the database system
makes use of a primary key if one has been declared; for example,
the primary key defines the default target column(s) for foreign keys
referencing its table.

### Foreign Keys

A foreign key constraint specifies that the values in a column (or
a group of columns) must match the values appearing in some row
of another table.
We say this maintains the *referential
integrity* between two related tables.

Say you have the product table that we have used several times already:

```
CREATE TABLE products (
product_no integer PRIMARY KEY,
name text,
price numeric
);
```

Let's also assume you have a table storing orders of those
products.  We want to ensure that the orders table only contains
orders of products that actually exist.  So we define a foreign
key constraint in the orders table that references the products
table:

```
CREATE TABLE orders (
order_id integer PRIMARY KEY,
product_no integer *REFERENCES products (product_no)*,
quantity integer
);
```

Now it is impossible to create orders with non-NULL
`product_no` entries that do not appear in the
products table.

We say that in this situation the orders table is the
*referencing* table and the products table is
the *referenced* table.  Similarly, there are
referencing and referenced columns.

You can also shorten the above command to:

```
CREATE TABLE orders (
order_id integer PRIMARY KEY,
product_no integer *REFERENCES products*,
quantity integer
);
```

because in absence of a column list the primary key of the
referenced table is used as the referenced column(s).

You can assign your own name for a foreign key constraint,
in the usual way.

A foreign key can also constrain and reference a group of columns.
As usual, it then needs to be written in table constraint form.
Here is a contrived syntax example:

```
CREATE TABLE t1 (
a integer PRIMARY KEY,
b integer,
c integer,
*FOREIGN KEY (b, c) REFERENCES other_table (c1, c2)*
);
```

Of course, the number and type of the constrained columns need to
match the number and type of the referenced columns.

Sometimes it is useful for the "other table" of a
foreign key constraint to be the same table; this is called
a *self-referential* foreign key.  For
example, if you want rows of a table to represent nodes of a tree
structure, you could write

```
CREATE TABLE tree (
node_id integer PRIMARY KEY,
parent_id integer REFERENCES tree,
name text,
...
);
```

A top-level node would have NULL `parent_id`,
while non-NULL `parent_id` entries would be
constrained to reference valid rows of the table.

A table can have more than one foreign key constraint.  This is
used to implement many-to-many relationships between tables.  Say
you have tables about products and orders, but now you want to
allow one order to contain possibly many products (which the
structure above did not allow).  You could use this table structure:

```
CREATE TABLE products (
product_no integer PRIMARY KEY,
name text,
price numeric
);

CREATE TABLE orders (
order_id integer PRIMARY KEY,
shipping_address text,
...
);

CREATE TABLE order_items (
product_no integer REFERENCES products,
order_id integer REFERENCES orders,
quantity integer,
PRIMARY KEY (product_no, order_id)
);
```

Notice that the primary key overlaps with the foreign keys in
the last table.

We know that the foreign keys disallow creation of orders that
do not relate to any products.  But what if a product is removed
after an order is created that references it?  SQL allows you to
handle that as well.  Intuitively, we have a few options:

- Disallow deleting a referenced product
- Delete the orders as well
- Something else?

To illustrate this, let's implement the following policy on the
many-to-many relationship example above: when someone wants to
remove a product that is still referenced by an order (via
`order_items`), we disallow it.  If someone
removes an order, the order items are removed as well:

```
CREATE TABLE products (
product_no integer PRIMARY KEY,
name text,
price numeric
);

CREATE TABLE orders (
order_id integer PRIMARY KEY,
shipping_address text,
...
);

CREATE TABLE order_items (
product_no integer REFERENCES products *ON DELETE RESTRICT*,
order_id integer REFERENCES orders *ON DELETE CASCADE*,
quantity integer,
PRIMARY KEY (product_no, order_id)
);
```

Restricting and cascading deletes are the two most common options.
`RESTRICT` prevents deletion of a
referenced row. `NO ACTION` means that if any
referencing rows still exist when the constraint is checked, an error
is raised; this is the default behavior if you do not specify anything.
(The essential difference between these two choices is that
`NO ACTION` allows the check to be deferred until
later in the transaction, whereas `RESTRICT` does not.)
`CASCADE` specifies that when a referenced row is deleted,
row(s) referencing it should be automatically deleted as well.
There are two other options:
`SET NULL` and `SET DEFAULT`.
These cause the referencing column(s) in the referencing row(s)
to be set to nulls or their default
values, respectively, when the referenced row is deleted.
Note that these do not excuse you from observing any constraints.
For example, if an action specifies `SET DEFAULT`
but the default value would not satisfy the foreign key constraint, the
operation will fail.

The appropriate choice of `ON DELETE` action depends on
what kinds of objects the related tables represent.  When the referencing
table represents something that is a component of what is represented by
the referenced table and cannot exist independently, then
`CASCADE` could be appropriate.  If the two tables
represent independent objects, then `RESTRICT` or
`NO ACTION` is more appropriate; an application that
actually wants to delete both objects would then have to be explicit about
this and run two delete commands.  In the above example, order items are
part of an order, and it is convenient if they are deleted automatically
if an order is deleted.  But products and orders are different things, and
so making a deletion of a product automatically cause the deletion of some
order items could be considered problematic.  The actions `SET
NULL` or `SET DEFAULT` can be appropriate if a
foreign-key relationship represents optional information.  For example, if
the products table contained a reference to a product manager, and the
product manager entry gets deleted, then setting the product's product
manager to null or a default might be useful.

The actions `SET NULL` and `SET DEFAULT`
can take a column list to specify which columns to set.  Normally, all
columns of the foreign-key constraint are set; setting only a subset is
useful in some special cases.  Consider the following example:

```
CREATE TABLE tenants (
tenant_id integer PRIMARY KEY
);

CREATE TABLE users (
tenant_id integer REFERENCES tenants ON DELETE CASCADE,
user_id integer NOT NULL,
PRIMARY KEY (tenant_id, user_id)
);

CREATE TABLE posts (
tenant_id integer REFERENCES tenants ON DELETE CASCADE,
post_id integer NOT NULL,
author_id integer,
PRIMARY KEY (tenant_id, post_id),
FOREIGN KEY (tenant_id, author_id) REFERENCES users ON DELETE SET NULL *(author_id)*
);
```

Without the specification of the column, the foreign key would also set
the column `tenant_id` to null, but that column is still
required as part of the primary key.

Analogous to `ON DELETE` there is also
`ON UPDATE` which is invoked when a referenced
column is changed (updated).  The possible actions are the same,
except that column lists cannot be specified for `SET
NULL` and `SET DEFAULT`.
In this case, `CASCADE` means that the updated values of the
referenced column(s) should be copied into the referencing row(s).

Normally, a referencing row need not satisfy the foreign key constraint
if any of its referencing columns are null.  If `MATCH FULL`
is added to the foreign key declaration, a referencing row escapes
satisfying the constraint only if all its referencing columns are null
(so a mix of null and non-null values is guaranteed to fail a
`MATCH FULL` constraint).  If you don't want referencing rows
to be able to avoid satisfying the foreign key constraint, declare the
referencing column(s) as `NOT NULL`.

A foreign key must reference columns that either are a primary key or
form a unique constraint, or are columns from a non-partial unique index.
This means that the referenced columns always have an index to allow
efficient lookups on whether a referencing row has a match.  Since a
`DELETE` of a row from the referenced table or an
`UPDATE` of a referenced column will require a scan of
the referencing table for rows matching the old value, it is often a good
idea to index the referencing columns too.  Because this is not always
needed, and there are many choices available on how to index, the
declaration of a foreign key constraint does not automatically create an
index on the referencing columns.

More information about updating and deleting data is in [dml](#dml).  Also see the description of foreign key constraint
syntax in the reference documentation for
[sql-createtable](#sql-createtable).

### Exclusion Constraints

Exclusion constraints ensure that if any two rows are compared on
the specified columns or expressions using the specified operators,
at least one of these operator comparisons will return false or null.
The syntax is:

```
CREATE TABLE circles (
c circle,
EXCLUDE USING gist (c WITH &&)
);
```

See also [`CREATE
TABLE ... CONSTRAINT ... EXCLUDE`](#sql-createtable-exclude) for details.

Adding an exclusion constraint will automatically create an index
of the type specified in the constraint declaration.

## System Columns

Every table has several *system columns* that are
implicitly defined by the system.  Therefore, these names cannot be
used as names of user-defined columns.  (Note that these
restrictions are separate from whether the name is a key word or
not; quoting a name will not allow you to escape these
restrictions.)  You do not really need to be concerned about these
columns; just know they exist.

**`tableoid`**
: The OID of the table containing this row.  This column is
particularly handy for queries that select from partitioned
tables (see [ddl-partitioning](#ddl-partitioning)) or inheritance
hierarchies (see [ddl-inherit](#ddl-inherit)), since without it,
it's difficult to tell which individual table a row came from.  The
`tableoid` can be joined against the
`oid` column of
`pg_class` to obtain the table name.

**`xmin`**
: The identity (transaction ID) of the inserting transaction for
this row version.  (A row version is an individual state of a
row; each update of a row creates a new row version for the same
logical row.)

**`cmin`**
: The command identifier (starting at zero) within the inserting
transaction.

**`xmax`**
: The identity (transaction ID) of the deleting transaction, or
zero for an undeleted row version.  It is possible for this column to
be nonzero in a visible row version. That usually indicates that the
deleting transaction hasn't committed yet, or that an attempted
deletion was rolled back.

**`cmax`**
: The command identifier within the deleting transaction, or zero.

**`ctid`**
: The physical location of the row version within its table.  Note that
although the `ctid` can be used to
locate the row version very quickly, a row's
`ctid` will change if it is
updated or moved by `VACUUM FULL`.  Therefore
`ctid` is useless as a long-term row
identifier.  A primary key should be used to identify logical rows.

Transaction identifiers are also 32-bit quantities.  In a
long-lived database it is possible for transaction IDs to wrap
around.  This is not a fatal problem given appropriate maintenance
procedures; see [maintenance](#maintenance) for details.  It is
unwise, however, to depend on the uniqueness of transaction IDs
over the long term (more than one billion transactions).

Command identifiers are also 32-bit quantities.  This creates a hard limit
of 2^32 (4 billion) SQL commands
within a single transaction.  In practice this limit is not a
problem — note that the limit is on the number of
SQL commands, not the number of rows processed.
Also, only commands that actually modify the database contents will
consume a command identifier.

## Modifying Tables

When you create a table and you realize that you made a mistake, or
the requirements of the application change, you can drop the
table and create it again.  But this is not a convenient option if
the table is already filled with data, or if the table is
referenced by other database objects (for instance a foreign key
constraint).  Therefore PostgreSQL
provides a family of commands to make modifications to existing
tables.  Note that this is conceptually distinct from altering
the data contained in the table: here we are interested in altering
the definition, or structure, of the table.

You can:

- Add columns
- Remove columns
- Add constraints
- Remove constraints
- Change default values
- Change column data types
- Rename columns
- Rename tables

All these actions are performed using the
[sql-altertable](#sql-altertable)
command, whose reference page contains details beyond those given
here.

### Adding a Column

To add a column, use a command like:

```
ALTER TABLE products ADD COLUMN description text;
```

The new column is initially filled with whatever default
value is given (null if you don't specify a `DEFAULT` clause).

> **Tip:**

> From PostgreSQL 11, adding a column with
> a constant default value no longer means that each row of the table
> needs to be updated when the `ALTER TABLE` statement
> is executed. Instead, the default value will be returned the next time
> the row is accessed, and applied when the table is rewritten, making
> the `ALTER TABLE` very fast even on large tables.
>

>

> However, if the default value is volatile (e.g.,
> `clock_timestamp()`)
> each row will need to be updated with the value calculated at the time
> `ALTER TABLE` is executed. To avoid a potentially
> lengthy update operation, particularly if you intend to fill the column
> with mostly nondefault values anyway, it may be preferable to add the
> column with no default, insert the correct values using
> `UPDATE`, and then add any desired default as described
> below.
>

You can also define constraints on the column at the same time,
using the usual syntax:

```
ALTER TABLE products ADD COLUMN description text CHECK (description <> '');
```

In fact all the options that can be applied to a column description
in `CREATE TABLE` can be used here.  Keep in mind however
that the default value must satisfy the given constraints, or the
`ADD` will fail.  Alternatively, you can add
constraints later (see below) after you've filled in the new column
correctly.

### Removing a Column

To remove a column, use a command like:

```
ALTER TABLE products DROP COLUMN description;
```

Whatever data was in the column disappears.  Table constraints involving
the column are dropped, too.  However, if the column is referenced by a
foreign key constraint of another table,
PostgreSQL will not silently drop that
constraint.  You can authorize dropping everything that depends on
the column by adding `CASCADE`:

```
ALTER TABLE products DROP COLUMN description CASCADE;
```

See [ddl-depend](#ddl-depend) for a description of the general
mechanism behind this.

### Adding a Constraint

To add a constraint, the table constraint syntax is used.  For example:

```
ALTER TABLE products ADD CHECK (name <> '');
ALTER TABLE products ADD CONSTRAINT some_name UNIQUE (product_no);
ALTER TABLE products ADD FOREIGN KEY (product_group_id) REFERENCES product_groups;
```

To add a not-null constraint, which cannot be written as a table
constraint, use this syntax:

```
ALTER TABLE products ALTER COLUMN product_no SET NOT NULL;
```

The constraint will be checked immediately, so the table data must
satisfy the constraint before it can be added.

### Removing a Constraint

To remove a constraint you need to know its name.  If you gave it
a name then that's easy.  Otherwise the system assigned a
generated name, which you need to find out.  The
psql command `\d
`tablename`` can be helpful
here; other interfaces might also provide a way to inspect table
details.  Then the command is:

```
ALTER TABLE products DROP CONSTRAINT some_name;
```

As with dropping a column, you need to add `CASCADE` if you
want to drop a constraint that something else depends on.  An example
is that a foreign key constraint depends on a unique or primary key
constraint on the referenced column(s).

This works the same for all constraint types except not-null
constraints. To drop a not null constraint use:

```
ALTER TABLE products ALTER COLUMN product_no DROP NOT NULL;
```

(Recall that not-null constraints do not have names.)

### Changing a Column's Default Value

To set a new default for a column, use a command like:

```
ALTER TABLE products ALTER COLUMN price SET DEFAULT 7.77;
```

Note that this doesn't affect any existing rows in the table, it
just changes the default for future `INSERT` commands.

To remove any default value, use:

```
ALTER TABLE products ALTER COLUMN price DROP DEFAULT;
```

This is effectively the same as setting the default to null.
As a consequence, it is not an error
to drop a default where one hadn't been defined, because the
default is implicitly the null value.

### Changing a Column's Data Type

To convert a column to a different data type, use a command like:

```
ALTER TABLE products ALTER COLUMN price TYPE numeric(10,2);
```

This will succeed only if each existing entry in the column can be
converted to the new type by an implicit cast.  If a more complex
conversion is needed, you can add a `USING` clause that
specifies how to compute the new values from the old.

PostgreSQL will attempt to convert the column's
default value (if any) to the new type, as well as any constraints
that involve the column.  But these conversions might fail, or might
produce surprising results.  It's often best to drop any constraints
on the column before altering its type, and then add back suitably
modified constraints afterwards.

### Renaming a Column

To rename a column:

```
ALTER TABLE products RENAME COLUMN product_no TO product_number;
```

### Renaming a Table

To rename a table:

```
ALTER TABLE products RENAME TO items;
```

## Inheritance

PostgreSQL implements table inheritance,
which can be a useful tool for database designers.  (SQL:1999 and
later define a type inheritance feature, which differs in many
respects from the features described here.)

Let's start with an example: suppose we are trying to build a data
model for cities.  Each state has many cities, but only one
capital. We want to be able to quickly retrieve the capital city
for any particular state. This can be done by creating two tables,
one for state capitals and one for cities that are not
capitals. However, what happens when we want to ask for data about
a city, regardless of whether it is a capital or not? The
inheritance feature can help to resolve this problem. We define the
`capitals` table so that it inherits from
`cities`:

```
CREATE TABLE cities (
name            text,
population      float,
elevation       int     -- in feet
);

CREATE TABLE capitals (
state           char(2)
) INHERITS (cities);
```

In this case, the `capitals` table *inherits*
all the columns of its parent table, `cities`. State
capitals also have an extra column, `state`, that shows
their state.

In PostgreSQL, a table can inherit from
zero or more other tables, and a query can reference either all
rows of a table or all rows of a table plus all of its descendant tables.
The latter behavior is the default.
For example, the following query finds the names of all cities,
including state capitals, that are located at an elevation over
500 feet:

```
SELECT name, elevation
FROM cities
WHERE elevation > 500;
```

Given the sample data from the PostgreSQL
tutorial (see [tutorial-sql-intro](#tutorial-sql-intro)), this returns:

```
name    | elevation
-----------+-----------
Las Vegas |      2174
Mariposa  |      1953
Madison   |       845
```

On the other hand, the following query finds all the cities that
are not state capitals and are situated at an elevation over 500 feet:

```
SELECT name, elevation
FROM ONLY cities
WHERE elevation > 500;

name    | elevation
-----------+-----------
Las Vegas |      2174
Mariposa  |      1953
```

Here the `ONLY` keyword indicates that the query
should apply only to `cities`, and not any tables
below `cities` in the inheritance hierarchy.  Many
of the commands that we have already discussed —
`SELECT`, `UPDATE` and
`DELETE` — support the
`ONLY` keyword.

You can also write the table name with a trailing `*`
to explicitly specify that descendant tables are included:

```
SELECT name, elevation
FROM cities*
WHERE elevation > 500;
```

Writing `*` is not necessary, since this behavior is always
the default.  However, this syntax is still supported for
compatibility with older releases where the default could be changed.

In some cases you might wish to know which table a particular row
originated from. There is a system column called
`tableoid` in each table which can tell you the
originating table:

```
SELECT c.tableoid, c.name, c.elevation
FROM cities c
WHERE c.elevation > 500;
```

which returns:

```
tableoid |   name    | elevation
----------+-----------+-----------
139793 | Las Vegas |      2174
139793 | Mariposa  |      1953
139798 | Madison   |       845
```

(If you try to reproduce this example, you will probably get
different numeric OIDs.)  By doing a join with
`pg_class` you can see the actual table names:

```
SELECT p.relname, c.name, c.elevation
FROM cities c, pg_class p
WHERE c.elevation > 500 AND c.tableoid = p.oid;
```

which returns:

```
relname  |   name    | elevation
----------+-----------+-----------
cities   | Las Vegas |      2174
cities   | Mariposa  |      1953
capitals | Madison   |       845
```

Another way to get the same effect is to use the `regclass`
alias type, which will print the table OID symbolically:

```
SELECT c.tableoid::regclass, c.name, c.elevation
FROM cities c
WHERE c.elevation > 500;
```

Inheritance does not automatically propagate data from
`INSERT` or `COPY` commands to
other tables in the inheritance hierarchy. In our example, the
following `INSERT` statement will fail:

```
INSERT INTO cities (name, population, elevation, state)
VALUES ('Albany', NULL, NULL, 'NY');
```

We might hope that the data would somehow be routed to the
`capitals` table, but this does not happen:
`INSERT` always inserts into exactly the table
specified.  In some cases it is possible to redirect the insertion
using a rule (see [rules](#rules)).  However that does not
help for the above case because the `cities` table
does not contain the column `state`, and so the
command will be rejected before the rule can be applied.

All check constraints and not-null constraints on a parent table are
automatically inherited by its children, unless explicitly specified
otherwise with `NO INHERIT` clauses.  Other types of constraints
(unique, primary key, and foreign key constraints) are not inherited.

A table can inherit from more than one parent table, in which case it has
the union of the columns defined by the parent tables.  Any columns
declared in the child table's definition are added to these.  If the
same column name appears in multiple parent tables, or in both a parent
table and the child's definition, then these columns are "merged"
so that there is only one such column in the child table.  To be merged,
columns must have the same data types, else an error is raised.
Inheritable check constraints and not-null constraints are merged in a
similar fashion.  Thus, for example, a merged column will be marked
not-null if any one of the column definitions it came from is marked
not-null.  Check constraints are merged if they have the same name,
and the merge will fail if their conditions are different.

Table inheritance is typically established when the child table is
created, using the `INHERITS` clause of the
[`CREATE TABLE`](#sql-createtable)
statement.
Alternatively, a table which is already defined in a compatible way can
have a new parent relationship added, using the `INHERIT`
variant of [`ALTER TABLE`](#sql-altertable).
To do this the new child table must already include columns with
the same names and types as the columns of the parent. It must also include
check constraints with the same names and check expressions as those of the
parent. Similarly an inheritance link can be removed from a child using the
`NO INHERIT` variant of `ALTER TABLE`.
Dynamically adding and removing inheritance links like this can be useful
when the inheritance relationship is being used for table
partitioning (see [ddl-partitioning](#ddl-partitioning)).

One convenient way to create a compatible table that will later be made
a new child is to use the `LIKE` clause in `CREATE
TABLE`. This creates a new table with the same columns as
the source table. If there are any `CHECK`
constraints defined on the source table, the `INCLUDING
CONSTRAINTS` option to `LIKE` should be
specified, as the new child must have constraints matching the parent
to be considered compatible.

A parent table cannot be dropped while any of its children remain. Neither
can columns or check constraints of child tables be dropped or altered
if they are inherited
from any parent tables. If you wish to remove a table and all of its
descendants, one easy way is to drop the parent table with the
`CASCADE` option (see [ddl-depend](#ddl-depend)).

`ALTER TABLE` will
propagate any changes in column data definitions and check
constraints down the inheritance hierarchy.  Again, dropping
columns that are depended on by other tables is only possible when using
the `CASCADE` option. `ALTER
TABLE` follows the same rules for duplicate column merging
and rejection that apply during `CREATE TABLE`.

Inherited queries perform access permission checks on the parent table
only.  Thus, for example, granting `UPDATE` permission on
the `cities` table implies permission to update rows in
the `capitals` table as well, when they are
accessed through `cities`.  This preserves the appearance
that the data is (also) in the parent table.  But
the `capitals` table could not be updated directly
without an additional grant.  In a similar way, the parent table's row
security policies (see [ddl-rowsecurity](#ddl-rowsecurity)) are applied to
rows coming from child tables during an inherited query.  A child table's
policies, if any, are applied only when it is the table explicitly named
in the query; and in that case, any policies attached to its parent(s) are
ignored.

Foreign tables (see [ddl-foreign-data](#ddl-foreign-data)) can also
be part of inheritance hierarchies, either as parent or child
tables, just as regular tables can be.  If a foreign table is part
of an inheritance hierarchy then any operations not supported by
the foreign table are not supported on the whole hierarchy either.

### Caveats

Note that not all SQL commands are able to work on
inheritance hierarchies.  Commands that are used for data querying,
data modification, or schema modification
(e.g., `SELECT`, `UPDATE`, `DELETE`,
most variants of `ALTER TABLE`, but
not `INSERT` or `ALTER TABLE ...
RENAME`) typically default to including child tables and
support the `ONLY` notation to exclude them.
Commands that do database maintenance and tuning
(e.g., `REINDEX`, `VACUUM`)
typically only work on individual, physical tables and do not
support recursing over inheritance hierarchies.  The respective
behavior of each individual command is documented in its reference
page ([sql-commands](#sql-commands)).

A serious limitation of the inheritance feature is that indexes (including
unique constraints) and foreign key constraints only apply to single
tables, not to their inheritance children. This is true on both the
referencing and referenced sides of a foreign key constraint. Thus,
in the terms of the above example:

- If we declared `cities`.`name` to be
`UNIQUE` or a `PRIMARY KEY`, this would not stop the
`capitals` table from having rows with names duplicating
rows in `cities`.  And those duplicate rows would by
default show up in queries from `cities`.  In fact, by
default `capitals` would have no unique constraint at all,
and so could contain multiple rows with the same name.
You could add a unique constraint to `capitals`, but this
would not prevent duplication compared to `cities`.
- Similarly, if we were to specify that
`cities`.`name` `REFERENCES` some
other table, this constraint would not automatically propagate to
`capitals`.  In this case you could work around it by
manually adding the same `REFERENCES` constraint to
`capitals`.
- Specifying that another table's column `REFERENCES
cities(name)` would allow the other table to contain city names, but
not capital names.  There is no good workaround for this case.

Some functionality not implemented for inheritance hierarchies is
implemented for declarative partitioning.
Considerable care is needed in deciding whether partitioning with legacy
inheritance is useful for your application.

#### Maintenance for Inheritance Partitioning

To remove old data quickly, simply drop the child table that is no longer
necessary:

```
DROP TABLE measurement_y2006m02;
```

To remove the child table from the inheritance hierarchy table but retain access to
it as a table in its own right:

```
ALTER TABLE measurement_y2006m02 NO INHERIT measurement;
```

To add a new child table to handle new data, create an empty child table
just as the original children were created above:

```
CREATE TABLE measurement_y2008m02 (
CHECK ( logdate >= DATE '2008-02-01' AND logdate = DATE '2008-02-01' AND logdate = DATE '2008-01-01';
```

Without partition pruning, the above query would scan each of the
partitions of the `measurement` table. With
partition pruning enabled, the planner will examine the definition
of each partition and prove that the partition need not
be scanned because it could not contain any rows meeting the query's
`WHERE` clause.  When the planner can prove this, it
excludes (*prunes*) the partition from the query
plan.

By using the EXPLAIN command and the [guc-enable-partition-pruning](#guc-enable-partition-pruning) configuration parameter, it's
possible to show the difference between a plan for which partitions have
been pruned and one for which they have not.  A typical unoptimized
plan for this type of table setup is:

```
SET enable_partition_pruning = off;
EXPLAIN SELECT count(*) FROM measurement WHERE logdate >= DATE '2008-01-01';
QUERY PLAN
-----------------------------------------------------------------------------------
Aggregate  (cost=188.76..188.77 rows=1 width=8)
->  Append  (cost=0.00..181.05 rows=3085 width=0)
->  Seq Scan on measurement_y2006m02  (cost=0.00..33.12 rows=617 width=0)
Filter: (logdate >= '2008-01-01'::date)
->  Seq Scan on measurement_y2006m03  (cost=0.00..33.12 rows=617 width=0)
Filter: (logdate >= '2008-01-01'::date)
...
->  Seq Scan on measurement_y2007m11  (cost=0.00..33.12 rows=617 width=0)
Filter: (logdate >= '2008-01-01'::date)
->  Seq Scan on measurement_y2007m12  (cost=0.00..33.12 rows=617 width=0)
Filter: (logdate >= '2008-01-01'::date)
->  Seq Scan on measurement_y2008m01  (cost=0.00..33.12 rows=617 width=0)
Filter: (logdate >= '2008-01-01'::date)
```

Some or all of the partitions might use index scans instead of
full-table sequential scans, but the point here is that there
is no need to scan the older partitions at all to answer this query.
When we enable partition pruning, we get a significantly
cheaper plan that will deliver the same answer:

```
SET enable_partition_pruning = on;
EXPLAIN SELECT count(*) FROM measurement WHERE logdate >= DATE '2008-01-01';
QUERY PLAN
-----------------------------------------------------------------------------------
Aggregate  (cost=37.75..37.76 rows=1 width=8)
->  Seq Scan on measurement_y2008m01  (cost=0.00..33.12 rows=617 width=0)
Filter: (logdate >= '2008-01-01'::date)
```

Note that partition pruning is driven only by the constraints defined
implicitly by the partition keys, not by the presence of indexes.
Therefore it isn't necessary to define indexes on the key columns.
Whether an index needs to be created for a given partition depends on
whether you expect that queries that scan the partition will
generally scan a large part of the partition or just a small part.
An index will be helpful in the latter case but not the former.

Partition pruning can be performed not only during the planning of a
given query, but also during its execution.  This is useful as it can
allow more partitions to be pruned when clauses contain expressions
whose values are not known at query planning time, for example,
parameters defined in a `PREPARE` statement, using a
value obtained from a subquery, or using a parameterized value on the
inner side of a nested loop join.  Partition pruning during execution
can be performed at any of the following times:

- During initialization of the query plan.  Partition pruning can be
performed here for parameter values which are known during the
initialization phase of execution.  Partitions which are pruned
during this stage will not show up in the query's
`EXPLAIN` or `EXPLAIN ANALYZE`.
It is possible to determine the number of partitions which were
removed during this phase by observing the
"Subplans Removed" property in the
`EXPLAIN` output.  It's important to note that any
partitions removed by the partition pruning done at this stage are
still locked at the beginning of execution.
- During actual execution of the query plan.  Partition pruning may
also be performed here to remove partitions using values which are
only known during actual query execution.  This includes values
from subqueries and values from execution-time parameters such as
those from parameterized nested loop joins.  Since the value of
these parameters may change many times during the execution of the
query, partition pruning is performed whenever one of the
execution parameters being used by partition pruning changes.
Determining if partitions were pruned during this phase requires
careful inspection of the `loops` property in
the `EXPLAIN ANALYZE` output.  Subplans
corresponding to different partitions may have different values
for it depending on how many times each of them was pruned during
execution.  Some may be shown as `(never executed)`
if they were pruned every time.

Partition pruning can be disabled using the
[guc-enable-partition-pruning](#guc-enable-partition-pruning) setting.

## Foreign Data

PostgreSQL implements portions of the SQL/MED
specification, allowing you to access data that resides outside
PostgreSQL using regular SQL queries.  Such data is referred to as
*foreign data*.  (Note that this usage is not to be confused
with foreign keys, which are a type of constraint within the database.)

Foreign data is accessed with help from a
*foreign data wrapper*. A foreign data wrapper is a
library that can communicate with an external data source, hiding the
details of connecting to the data source and obtaining data from it.
There are some foreign data wrappers available as `contrib`
modules; see [contrib](#contrib).  Other kinds of foreign data
wrappers might be found as third party products.  If none of the existing
foreign data wrappers suit your needs, you can write your own; see [fdwhandler](#fdwhandler).

To access foreign data, you need to create a *foreign server*
object, which defines how to connect to a particular external data source
according to the set of options used by its supporting foreign data
wrapper. Then you need to create one or more *foreign
tables*, which define the structure of the remote data. A
foreign table can be used in queries just like a normal table, but a
foreign table has no storage in the PostgreSQL server.  Whenever it is
used, PostgreSQL asks the foreign data wrapper
to fetch data from the external source, or transmit data to the external
source in the case of update commands.

Accessing remote data may require authenticating to the external
data source.  This information can be provided by a
*user mapping*, which can provide additional data
such as user names and passwords based
on the current PostgreSQL role.

For additional information, see
[sql-createforeigndatawrapper](#sql-createforeigndatawrapper),
[sql-createserver](#sql-createserver),
[sql-createusermapping](#sql-createusermapping),
[sql-createforeigntable](#sql-createforeigntable), and
[sql-importforeignschema](#sql-importforeignschema).

## Other Database Objects

Tables are the central objects in a relational database structure,
because they hold your data.  But they are not the only objects
that exist in a database.  Many other kinds of objects can be
created to make the use and management of the data more efficient
or convenient.  They are not discussed in this chapter, but we give
you a list here so that you are aware of what is possible:

- Views
- Functions, procedures, and operators
- Data types and domains
- Triggers and rewrite rules

Detailed information on
these topics appears in [server-programming](#server-programming).

## Dependency Tracking

When you create complex database structures involving many tables
with foreign key constraints, views, triggers, functions, etc. you
implicitly create a net of dependencies between the objects.
For instance, a table with a foreign key constraint depends on the
table it references.

To ensure the integrity of the entire database structure,
PostgreSQL makes sure that you cannot
drop objects that other objects still depend on.  For example,
attempting to drop the products table we considered in [ddl-constraints-fk](#ddl-constraints-fk), with the orders table depending on
it, would result in an error message like this:

```
DROP TABLE products;

ERROR:  cannot drop table products because other objects depend on it
DETAIL:  constraint orders_product_no_fkey on table orders depends on table products
HINT:  Use DROP ... CASCADE to drop the dependent objects too.
```

The error message contains a useful hint: if you do not want to
bother deleting all the dependent objects individually, you can run:

```
DROP TABLE products CASCADE;
```

and all the dependent objects will be removed, as will any objects
that depend on them, recursively.  In this case, it doesn't remove
the orders table, it only removes the foreign key constraint.
It stops there because nothing depends on the foreign key constraint.
(If you want to check what `DROP ... CASCADE` will do,
run `DROP` without `CASCADE` and read the
`DETAIL` output.)

Almost all `DROP` commands in PostgreSQL support
specifying `CASCADE`.  Of course, the nature of
the possible dependencies varies with the type of the object.  You
can also write `RESTRICT` instead of
`CASCADE` to get the default behavior, which is to
prevent dropping objects that any other objects depend on.

> **Note:**

> According to the SQL standard, specifying either
> `RESTRICT` or `CASCADE` is
> required in a `DROP` command.  No database system actually
> enforces that rule, but whether the default behavior
> is `RESTRICT` or `CASCADE` varies
> across systems.
>

If a `DROP` command lists multiple
objects, `CASCADE` is only required when there are
dependencies outside the specified group.  For example, when saying
`DROP TABLE tab1, tab2` the existence of a foreign
key referencing `tab1` from `tab2` would not mean
that `CASCADE` is needed to succeed.

For a user-defined function or procedure whose body is defined as a string
literal, PostgreSQL tracks
dependencies associated with the function's externally-visible properties,
such as its argument and result types, but *not* dependencies
that could only be known by examining the function body.  As an example,
consider this situation:

```
CREATE TYPE rainbow AS ENUM ('red', 'orange', 'yellow',
'green', 'blue', 'purple');

CREATE TABLE my_colors (color rainbow, note text);

CREATE FUNCTION get_color_note (rainbow) RETURNS text AS
'SELECT note FROM my_colors WHERE color = $1'
LANGUAGE SQL;
```

(See [xfunc-sql](#xfunc-sql) for an explanation of SQL-language
functions.)  PostgreSQL will be aware that
the `get_color_note` function depends on the `rainbow`
type: dropping the type would force dropping the function, because its
argument type would no longer be defined.  But PostgreSQL
will not consider `get_color_note` to depend on
the `my_colors` table, and so will not drop the function if
the table is dropped.  While there are disadvantages to this approach,
there are also benefits.  The function is still valid in some sense if the
table is missing, though executing it would cause an error; creating a new
table of the same name would allow the function to work again.

On the other hand, for a SQL-language function or procedure whose body
is written in SQL-standard style, the body is parsed at function
definition time and all dependencies recognized by the parser are
stored.  Thus, if we write the function above as

```
CREATE FUNCTION get_color_note (rainbow) RETURNS text
BEGIN ATOMIC
SELECT note FROM my_colors WHERE color = $1;
END;
```

then the function's dependency on the `my_colors`
table will be known and enforced by `DROP`.
