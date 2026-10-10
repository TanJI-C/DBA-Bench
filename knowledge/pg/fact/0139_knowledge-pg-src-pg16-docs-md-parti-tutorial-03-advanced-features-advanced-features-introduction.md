# Introduction; Views; Foreign Keys; Transactions; Window Functions; Conclusion

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partI_tutorial/03_advanced_features.md`
- Source Title: `Advanced Features`
- Source Heading Path: `Advanced Features > Introduction; Views; Foreign Keys; Transactions; Window Functions; Conclusion`
- Source Line Ranges: `3-20, 21-46, 47-97, 98-242, 243-473, 474-484`
- Chunk ID: `pg16_fact_0139_813543ad7d`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b4c5fa2fa7fadd6255c4cbe82828e7913cb51dc92f2105daed684b49be015352`

## Retrieval Guidance

- Use When: Need introductory facts about PostgreSQL advanced SQL features.
- Retrieval Keywords: VIEW, foreign key, transaction, ROLLBACK, SAVEPOINT, window function, OVER
- Follow-up Guidance: For concurrency failure handling, use the concurrency control solution records.
- Classification Note: Tutorial explanation of views, referential integrity, transaction commit/rollback/savepoints, and window functions; it teaches mechanisms rather than diagnosing faults or prescribing production fixes.

## Official Source Content

## Introduction

In the previous chapter we have covered the basics of using
SQL to store and access your data in
PostgreSQL.  We will now discuss some
more advanced features of SQL that simplify
management and prevent loss or corruption of your data.  Finally,
we will look at some PostgreSQL
extensions.

This chapter will on occasion refer to examples found in [tutorial-sql](#tutorial-sql) to change or improve them, so it will be
useful to have read that chapter.  Some examples from
this chapter can also be found in
`advanced.sql` in the tutorial directory.  This
file also contains some sample data to load, which is not
repeated here.  (Refer to [tutorial-sql-intro](#tutorial-sql-intro) for
how to use the file.)

## Views

Refer back to the queries in [tutorial-join](#tutorial-join).
Suppose the combined listing of weather records and city location
is of particular interest to your application, but you do not want
to type the query each time you need it.  You can create a
*view* over the query, which gives a name to
the query that you can refer to like an ordinary table:

```
CREATE VIEW myview AS
SELECT name, temp_lo, temp_hi, prcp, date, location
FROM weather, cities
WHERE city = name;

SELECT * FROM myview;
```

Making liberal use of views is a key aspect of good SQL database
design.  Views allow you to encapsulate the details of the
structure of your tables, which might change as your application
evolves, behind consistent interfaces.

Views can be used in almost any place a real table can be used.
Building views upon other views is not uncommon.

## Foreign Keys

Recall the weather and
cities tables from [tutorial-sql](#tutorial-sql).  Consider the following problem:  You
want to make sure that no one can insert rows in the
weather table that do not have a matching
entry in the cities table.  This is called
maintaining the *referential integrity* of
your data.  In simplistic database systems this would be
implemented (if at all) by first looking at the
cities table to check if a matching record
exists, and then inserting or rejecting the new
weather records.  This approach has a
number of problems and is very inconvenient, so
PostgreSQL can do this for you.

The new declaration of the tables would look like this:

```
CREATE TABLE cities (
name     varchar(80) primary key,
location point
);

CREATE TABLE weather (
city      varchar(80) references cities(name),
temp_lo   int,
temp_hi   int,
prcp      real,
date      date
);
```

Now try inserting an invalid record:

```
INSERT INTO weather VALUES ('Berkeley', 45, 53, 0.0, '1994-11-28');
```

```
ERROR:  insert or update on table "weather" violates foreign key constraint "weather_city_fkey"
DETAIL:  Key (city)=(Berkeley) is not present in table "cities".
```

The behavior of foreign keys can be finely tuned to your
application.  We will not go beyond this simple example in this
tutorial, but just refer you to [ddl](#ddl)
for more information.  Making correct use of
foreign keys will definitely improve the quality of your database
applications, so you are strongly encouraged to learn about them.

## Transactions

*Transactions* are a fundamental concept of all database
systems.  The essential point of a transaction is that it bundles
multiple steps into a single, all-or-nothing operation.  The intermediate
states between the steps are not visible to other concurrent transactions,
and if some failure occurs that prevents the transaction from completing,
then none of the steps affect the database at all.

For example, consider a bank database that contains balances for various
customer accounts, as well as total deposit balances for branches.
Suppose that we want to record a payment of $100.00 from Alice's account
to Bob's account.  Simplifying outrageously, the SQL commands for this
might look like:

```
UPDATE accounts SET balance = balance - 100.00
WHERE name = 'Alice';
UPDATE branches SET balance = balance - 100.00
WHERE name = (SELECT branch_name FROM accounts WHERE name = 'Alice');
UPDATE accounts SET balance = balance + 100.00
WHERE name = 'Bob';
UPDATE branches SET balance = balance + 100.00
WHERE name = (SELECT branch_name FROM accounts WHERE name = 'Bob');
```

The details of these commands are not important here; the important
point is that there are several separate updates involved to accomplish
this rather simple operation.  Our bank's officers will want to be
assured that either all these updates happen, or none of them happen.
It would certainly not do for a system failure to result in Bob
receiving $100.00 that was not debited from Alice.  Nor would Alice long
remain a happy customer if she was debited without Bob being credited.
We need a guarantee that if something goes wrong partway through the
operation, none of the steps executed so far will take effect.  Grouping
the updates into a *transaction* gives us this guarantee.
A transaction is said to be *atomic*: from the point of
view of other transactions, it either happens completely or not at all.

We also want a
guarantee that once a transaction is completed and acknowledged by
the database system, it has indeed been permanently recorded
and won't be lost even if a crash ensues shortly thereafter.
For example, if we are recording a cash withdrawal by Bob,
we do not want any chance that the debit to his account will
disappear in a crash just after he walks out the bank door.
A transactional database guarantees that all the updates made by
a transaction are logged in permanent storage (i.e., on disk) before
the transaction is reported complete.

Another important property of transactional databases is closely
related to the notion of atomic updates: when multiple transactions
are running concurrently, each one should not be able to see the
incomplete changes made by others.  For example, if one transaction
is busy totalling all the branch balances, it would not do for it
to include the debit from Alice's branch but not the credit to
Bob's branch, nor vice versa.  So transactions must be all-or-nothing
not only in terms of their permanent effect on the database, but
also in terms of their visibility as they happen.  The updates made
so far by an open transaction are invisible to other transactions
until the transaction completes, whereupon all the updates become
visible simultaneously.

In PostgreSQL, a transaction is set up by surrounding
the SQL commands of the transaction with
`BEGIN` and `COMMIT` commands.  So our banking
transaction would actually look like:

```
BEGIN;
UPDATE accounts SET balance = balance - 100.00
WHERE name = 'Alice';
-- etc etc
COMMIT;
```

If, partway through the transaction, we decide we do not want to
commit (perhaps we just noticed that Alice's balance went negative),
we can issue the command `ROLLBACK` instead of
`COMMIT`, and all our updates so far will be canceled.

PostgreSQL actually treats every SQL statement as being
executed within a transaction.  If you do not issue a `BEGIN`
command,
then each individual statement has an implicit `BEGIN` and
(if successful) `COMMIT` wrapped around it.  A group of
statements surrounded by `BEGIN` and `COMMIT`
is sometimes called a *transaction block*.

> **Note:**

> Some client libraries issue `BEGIN` and `COMMIT`
> commands automatically, so that you might get the effect of transaction
> blocks without asking.  Check the documentation for the interface
> you are using.
>

It's possible to control the statements in a transaction in a more
granular fashion through the use of *savepoints*.  Savepoints
allow you to selectively discard parts of the transaction, while
committing the rest.  After defining a savepoint with
`SAVEPOINT`, you can if needed roll back to the savepoint
with `ROLLBACK TO`.  All the transaction's database changes
between defining the savepoint and rolling back to it are discarded, but
changes earlier than the savepoint are kept.

After rolling back to a savepoint, it continues to be defined, so you can
roll back to it several times.  Conversely, if you are sure you won't need
to roll back to a particular savepoint again, it can be released, so the
system can free some resources.  Keep in mind that either releasing or
rolling back to a savepoint
will automatically release all savepoints that were defined after it.

All this is happening within the transaction block, so none of it
is visible to other database sessions.  When and if you commit the
transaction block, the committed actions become visible as a unit
to other sessions, while the rolled-back actions never become visible
at all.

Remembering the bank database, suppose we debit $100.00 from Alice's
account, and credit Bob's account, only to find later that we should
have credited Wally's account.  We could do it using savepoints like
this:

```
BEGIN;
UPDATE accounts SET balance = balance - 100.00
WHERE name = 'Alice';
SAVEPOINT my_savepoint;
UPDATE accounts SET balance = balance + 100.00
WHERE name = 'Bob';
-- oops ... forget that and use Wally's account
ROLLBACK TO my_savepoint;
UPDATE accounts SET balance = balance + 100.00
WHERE name = 'Wally';
COMMIT;
```

This example is, of course, oversimplified, but there's a lot of control
possible in a transaction block through the use of savepoints.
Moreover, `ROLLBACK TO` is the only way to regain control of a
transaction block that was put in aborted state by the
system due to an error, short of rolling it back completely and starting
again.

## Window Functions

A *window function* performs a calculation across a set of
table rows that are somehow related to the current row.  This is comparable
to the type of calculation that can be done with an aggregate function.
However, window functions do not cause rows to become grouped into a single
output row like non-window aggregate calls would.  Instead, the
rows retain their separate identities.  Behind the scenes, the window
function is able to access more than just the current row of the query
result.

Here is an example that shows how to compare each employee's salary
with the average salary in his or her department:

```
SELECT depname, empno, salary, avg(salary) OVER (PARTITION BY depname) FROM empsalary;
```

```
depname  | empno | salary |          avg
-----------+-------+--------+-----------------------
develop   |    11 |   5200 | 5020.0000000000000000
develop   |     7 |   4200 | 5020.0000000000000000
develop   |     9 |   4500 | 5020.0000000000000000
develop   |     8 |   6000 | 5020.0000000000000000
develop   |    10 |   5200 | 5020.0000000000000000
personnel |     5 |   3500 | 3700.0000000000000000
personnel |     2 |   3900 | 3700.0000000000000000
sales     |     3 |   4800 | 4866.6666666666666667
sales     |     1 |   5000 | 4866.6666666666666667
sales     |     4 |   4800 | 4866.6666666666666667
(10 rows)
```

The first three output columns come directly from the table
`empsalary`, and there is one output row for each row in the
table.  The fourth column represents an average taken across all the table
rows that have the same `depname` value as the current row.
(This actually is the same function as the non-window `avg`
aggregate, but the `OVER` clause causes it to be
treated as a window function and computed across the window frame.)

A window function call always contains an `OVER` clause
directly following the window function's name and argument(s).  This is what
syntactically distinguishes it from a normal function or non-window
aggregate.  The `OVER` clause determines exactly how the
rows of the query are split up for processing by the window function.
The `PARTITION BY` clause within `OVER`
divides the rows into groups, or partitions, that share the same
values of the `PARTITION BY` expression(s).  For each row,
the window function is computed across the rows that fall into the
same partition as the current row.

You can also control the order in which rows are processed by
window functions using `ORDER BY` within `OVER`.
(The window `ORDER BY` does not even have to match the
order in which the rows are output.)  Here is an example:

```
SELECT depname, empno, salary,
rank() OVER (PARTITION BY depname ORDER BY salary DESC)
FROM empsalary;
```

```
depname  | empno | salary | rank
-----------+-------+--------+------
develop   |     8 |   6000 |    1
develop   |    10 |   5200 |    2
develop   |    11 |   5200 |    2
develop   |     9 |   4500 |    4
develop   |     7 |   4200 |    5
personnel |     2 |   3900 |    1
personnel |     5 |   3500 |    2
sales     |     1 |   5000 |    1
sales     |     4 |   4800 |    2
sales     |     3 |   4800 |    2
(10 rows)
```

As shown here, the `rank` function produces a numerical rank
for each distinct `ORDER BY` value in the current row's
partition, using the order defined by the `ORDER BY` clause.
`rank` needs no explicit parameter, because its behavior
is entirely determined by the `OVER` clause.

The rows considered by a window function are those of the "virtual
table" produced by the query's `FROM` clause as filtered by its
`WHERE`, `GROUP BY`, and `HAVING` clauses
if any.  For example, a row removed because it does not meet the
`WHERE` condition is not seen by any window function.
A query can contain multiple window functions that slice up the data
in different ways using different `OVER` clauses, but
they all act on the same collection of rows defined by this virtual table.

We already saw that `ORDER BY` can be omitted if the ordering
of rows is not important.  It is also possible to omit `PARTITION
BY`, in which case there is a single partition containing all rows.

There is another important concept associated with window functions:
for each row, there is a set of rows within its partition called its
*window frame*.  Some window functions act only
on the rows of the window frame, rather than of the whole partition.
By default, if `ORDER BY` is supplied then the frame consists of
all rows from the start of the partition up through the current row, plus
any following rows that are equal to the current row according to the
`ORDER BY` clause.  When `ORDER BY` is omitted the
default frame consists of all rows in the partition.
(Note: There are options to define the window frame in other ways, but
this tutorial does not cover them.  See
for details.)
Here is an example using `sum`:

```
SELECT salary, sum(salary) OVER () FROM empsalary;
```

```
salary |  sum
--------+-------
5200 | 47100
5000 | 47100
3500 | 47100
4800 | 47100
3900 | 47100
4200 | 47100
4500 | 47100
4800 | 47100
6000 | 47100
5200 | 47100
(10 rows)
```

Above, since there is no `ORDER BY` in the `OVER`
clause, the window frame is the same as the partition, which for lack of
`PARTITION BY` is the whole table; in other words each sum is
taken over the whole table and so we get the same result for each output
row.  But if we add an `ORDER BY` clause, we get very different
results:

```
SELECT salary, sum(salary) OVER (ORDER BY salary) FROM empsalary;
```

```
salary |  sum
--------+-------
3500 |  3500
3900 |  7400
4200 | 11600
4500 | 16100
4800 | 25700
4800 | 25700
5000 | 30700
5200 | 41100
5200 | 41100
6000 | 47100
(10 rows)
```

Here the sum is taken from the first (lowest) salary up through the
current one, including any duplicates of the current one (notice the
results for the duplicated salaries).

Window functions are permitted only in the `SELECT` list
and the `ORDER BY` clause of the query. They are forbidden
elsewhere, such as in `GROUP BY`, `HAVING`
and `WHERE` clauses.  This is because they logically
execute after the processing of those clauses.  Also, window functions
execute after non-window aggregate functions.  This means it is valid to
include an aggregate function call in the arguments of a window function,
but not vice versa.

If there is a need to filter or group rows after the window calculations
are performed, you can use a sub-select.  For example:

```
SELECT depname, empno, salary, enroll_date
FROM
(SELECT depname, empno, salary, enroll_date,
rank() OVER (PARTITION BY depname ORDER BY salary DESC, empno) AS pos
FROM empsalary
) AS ss
WHERE pos  500;
```

which returns:

```
name    | elevation
-----------+-----------
Las Vegas |      2174
Mariposa  |      1953
Madison   |       845
(3 rows)
```

On the other hand, the  following  query  finds
all  the cities that are not state capitals and
are situated at an elevation over 500 feet:

```
SELECT name, elevation
FROM ONLY cities
WHERE elevation > 500;
```

```
name    | elevation
-----------+-----------
Las Vegas |      2174
Mariposa  |      1953
(2 rows)
```

Here the `ONLY` before `cities`
indicates that the query should be run over only the
cities table, and not tables below
cities in the inheritance hierarchy.  Many
of the commands that we have already discussed —
`SELECT`, `UPDATE`, and
`DELETE` — support this `ONLY`
notation.

> **Note:**

> Although inheritance is frequently useful, it has not been integrated
> with unique constraints or foreign keys, which limits its usefulness.
> See [ddl-inherit](#ddl-inherit) for more detail.
>

## Conclusion

PostgreSQL has many features not
touched upon in this tutorial introduction, which has been
oriented toward newer users of SQL.  These
features are discussed in more detail in the remainder of this
book.

If you feel you need more introductory material, please visit the PostgreSQL
[web site](https://www.postgresql.org)
for links to more resources.
