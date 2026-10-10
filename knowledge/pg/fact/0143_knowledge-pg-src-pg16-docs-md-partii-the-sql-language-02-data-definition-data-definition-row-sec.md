# Row Security Policies

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/02_data_definition.md`
- Source Title: `Data Definition`
- Source Heading Path: `Data Definition > Row Security Policies`
- Source Line Ranges: `1573-2273`
- Chunk ID: `pg16_fact_0143_8bfa9ec742`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `2eddaa5b4367d1f406241a32742066a37d3c5ca5c7db561b0d2ecb0bd8e1bce7`

## Retrieval Guidance

- Use When: Need facts about RLS policy behavior and SQL syntax.
- Retrieval Keywords: row-level security, CREATE POLICY, USING, WITH CHECK, ALTER TABLE ENABLE ROW LEVEL SECURITY
- Follow-up Guidance: If behavior depends on row_security, check the configuration record for that parameter.
- Classification Note: Explains row-level security policy objects, USING and WITH CHECK expressions, policy combination, role behavior, and table access semantics.

## Official Source Content

## Row Security Policies

In addition to the SQL-standard [privilege
system](#ddl-priv) available through [sql-grant](#sql-grant),
tables can have *row security policies* that restrict,
on a per-user basis, which rows can be returned by normal queries
or inserted, updated, or deleted by data modification commands.
This feature is also known as *Row-Level Security*.
By default, tables do not have any policies, so that if a user has
access privileges to a table according to the SQL privilege system,
all rows within it are equally available for querying or updating.

When row security is enabled on a table (with
[ALTER TABLE ... ENABLE ROW LEVEL
SECURITY](#sql-altertable)), all normal access to the table for selecting rows or
modifying rows must be allowed by a row security policy.  (However, the
table's owner is typically not subject to row security policies.)  If no
policy exists for the table, a default-deny policy is used, meaning that
no rows are visible or can be modified.  Operations that apply to the
whole table, such as `TRUNCATE` and `REFERENCES`,
are not subject to row security.

Row security policies can be specific to commands, or to roles, or to
both.  A policy can be specified to apply to `ALL`
commands, or to `SELECT`, `INSERT`, `UPDATE`,
or `DELETE`.  Multiple roles can be assigned to a given
policy, and normal role membership and inheritance rules apply.

To specify which rows are visible or modifiable according to a policy,
an expression is required that returns a Boolean result.  This
expression will be evaluated for each row prior to any conditions or
functions coming from the user's query.  (The only exceptions to this
rule are `leakproof` functions, which are guaranteed to
not leak information; the optimizer may choose to apply such functions
ahead of the row-security check.)  Rows for which the expression does
not return `true` will not be processed.  Separate expressions
may be specified to provide independent control over the rows which are
visible and the rows which are allowed to be modified.  Policy
expressions are run as part of the query and with the privileges of the
user running the query, although security-definer functions can be used
to access data not available to the calling user.

Superusers and roles with the `BYPASSRLS` attribute always
bypass the row security system when accessing a table.  Table owners
normally bypass row security as well, though a table owner can choose to
be subject to row security with [ALTER
TABLE ... FORCE ROW LEVEL SECURITY](#sql-altertable).

Enabling and disabling row security, as well as adding policies to a
table, is always the privilege of the table owner only.

Policies are created using the [sql-createpolicy](#sql-createpolicy)
command, altered using the [sql-alterpolicy](#sql-alterpolicy) command,
and dropped using the [sql-droppolicy](#sql-droppolicy) command.  To
enable and disable row security for a given table, use the
[sql-altertable](#sql-altertable) command.

Each policy has a name and multiple policies can be defined for a
table.  As policies are table-specific, each policy for a table must
have a unique name.  Different tables may have policies with the
same name.

When multiple policies apply to a given query, they are combined using
either `OR` (for permissive policies, which are the
default) or using `AND` (for restrictive policies).
This is similar to the rule that a given role has the privileges
of all roles that they are a member of.  Permissive vs. restrictive
policies are discussed further below.

As a simple example, here is how to create a policy on
the `account` relation to allow only members of
the `managers` role to access rows, and only rows of their
accounts:

```
CREATE TABLE accounts (manager text, company text, contact_email text);

ALTER TABLE accounts ENABLE ROW LEVEL SECURITY;

CREATE POLICY account_managers ON accounts TO managers
USING (manager = current_user);
```

The policy above implicitly provides a `WITH CHECK`
clause identical to its `USING` clause, so that the
constraint applies both to rows selected by a command (so a manager
cannot `SELECT`, `UPDATE`,
or `DELETE` existing rows belonging to a different
manager) and to rows modified by a command (so rows belonging to a
different manager cannot be created via `INSERT`
or `UPDATE`).

If no role is specified, or the special user name
`PUBLIC` is used, then the policy applies to all
users on the system.  To allow all users to access only their own row in
a `users` table, a simple policy can be used:

```
CREATE POLICY user_policy ON users
USING (user_name = current_user);
```

This works similarly to the previous example.

To use a different policy for rows that are being added to the table
compared to those rows that are visible, multiple policies can be
combined.  This pair of policies would allow all users to view all rows
in the `users` table, but only modify their own:

```
CREATE POLICY user_sel_policy ON users
FOR SELECT
USING (true);
CREATE POLICY user_mod_policy ON users
USING (user_name = current_user);
```

In a `SELECT` command, these two policies are combined
using `OR`, with the net effect being that all rows
can be selected.  In other command types, only the second policy applies,
so that the effects are the same as before.

Row security can also be disabled with the `ALTER TABLE`
command.  Disabling row security does not remove any policies that are
defined on the table; they are simply ignored.  Then all rows in the
table are visible and modifiable, subject to the standard SQL privileges
system.

Below is a larger example of how this feature can be used in production
environments.  The table `passwd` emulates a Unix password
file:

```
-- Simple passwd-file based example
CREATE TABLE passwd (
user_name             text UNIQUE NOT NULL,
pwhash                text,
uid                   int  PRIMARY KEY,
gid                   int  NOT NULL,
real_name             text NOT NULL,
home_phone            text,
extra_info            text,
home_dir              text NOT NULL,
shell                 text NOT NULL
);

CREATE ROLE admin;  -- Administrator
CREATE ROLE bob;    -- Normal user
CREATE ROLE alice;  -- Normal user

-- Populate the table
INSERT INTO passwd VALUES
('admin','xxx',0,0,'Admin','111-222-3333',null,'/root','/bin/dash');
INSERT INTO passwd VALUES
('bob','xxx',1,1,'Bob','123-456-7890',null,'/home/bob','/bin/zsh');
INSERT INTO passwd VALUES
('alice','xxx',2,1,'Alice','098-765-4321',null,'/home/alice','/bin/zsh');

-- Be sure to enable row-level security on the table
ALTER TABLE passwd ENABLE ROW LEVEL SECURITY;

-- Create policies
-- Administrator can see all rows and add any rows
CREATE POLICY admin_all ON passwd TO admin USING (true) WITH CHECK (true);
-- Normal users can view all rows
CREATE POLICY all_view ON passwd FOR SELECT USING (true);
-- Normal users can update their own records, but
-- limit which shells a normal user is allowed to set
CREATE POLICY user_mod ON passwd FOR UPDATE
USING (current_user = user_name)
WITH CHECK (
current_user = user_name AND
shell IN ('/bin/bash','/bin/sh','/bin/dash','/bin/zsh','/bin/tcsh')
);

-- Allow admin all normal rights
GRANT SELECT, INSERT, UPDATE, DELETE ON passwd TO admin;
-- Users only get select access on public columns
GRANT SELECT
(user_name, uid, gid, real_name, home_phone, extra_info, home_dir, shell)
ON passwd TO public;
-- Allow users to update certain columns
GRANT UPDATE
(pwhash, real_name, home_phone, extra_info, shell)
ON passwd TO public;
```

As with any security settings, it's important to test and ensure that
the system is behaving as expected.  Using the example above, this
demonstrates that the permission system is working properly.

```
-- admin can view all rows and fields
postgres=> set role admin;
SET
postgres=> table passwd;
user_name | pwhash | uid | gid | real_name |  home_phone  | extra_info | home_dir    |   shell
-----------+--------+-----+-----+-----------+--------------+------------+-------------+-----------
admin     | xxx    |   0 |   0 | Admin     | 111-222-3333 |            | /root       | /bin/dash
bob       | xxx    |   1 |   1 | Bob       | 123-456-7890 |            | /home/bob   | /bin/zsh
alice     | xxx    |   2 |   1 | Alice     | 098-765-4321 |            | /home/alice | /bin/zsh
(3 rows)

-- Test what Alice is able to do
postgres=> set role alice;
SET
postgres=> table passwd;
ERROR:  permission denied for table passwd
postgres=> select user_name,real_name,home_phone,extra_info,home_dir,shell from passwd;
user_name | real_name |  home_phone  | extra_info | home_dir    |   shell
-----------+-----------+--------------+------------+-------------+-----------
admin     | Admin     | 111-222-3333 |            | /root       | /bin/dash
bob       | Bob       | 123-456-7890 |            | /home/bob   | /bin/zsh
alice     | Alice     | 098-765-4321 |            | /home/alice | /bin/zsh
(3 rows)

postgres=> update passwd set user_name = 'joe';
ERROR:  permission denied for table passwd
-- Alice is allowed to change her own real_name, but no others
postgres=> update passwd set real_name = 'Alice Doe';
UPDATE 1
postgres=> update passwd set real_name = 'John Doe' where user_name = 'admin';
UPDATE 0
postgres=> update passwd set shell = '/bin/xx';
ERROR:  new row violates WITH CHECK OPTION for "passwd"
postgres=> delete from passwd;
ERROR:  permission denied for table passwd
postgres=> insert into passwd (user_name) values ('xxx');
ERROR:  permission denied for table passwd
-- Alice can change her own password; RLS silently prevents updating other rows
postgres=> update passwd set pwhash = 'abc';
UPDATE 1
```

All of the policies constructed thus far have been permissive policies,
meaning that when multiple policies are applied they are combined using
the "OR" Boolean operator.  While permissive policies can be constructed
to only allow access to rows in the intended cases, it can be simpler to
combine permissive policies with restrictive policies (which the records
must pass and which are combined using the "AND" Boolean operator).
Building on the example above, we add a restrictive policy to require
the administrator to be connected over a local Unix socket to access the
records of the `passwd` table:

```
CREATE POLICY admin_local_only ON passwd AS RESTRICTIVE TO admin
USING (pg_catalog.inet_client_addr() IS NULL);
```

We can then see that an administrator connecting over a network will not
see any records, due to the restrictive policy:

```
=> SELECT current_user;
current_user
--------------
admin
(1 row)

=> select inet_client_addr();
inet_client_addr
------------------
127.0.0.1
(1 row)

=> TABLE passwd;
user_name | pwhash | uid | gid | real_name | home_phone | extra_info | home_dir | shell
-----------+--------+-----+-----+-----------+------------+------------+----------+-------
(0 rows)

=> UPDATE passwd set pwhash = NULL;
UPDATE 0
```

Referential integrity checks, such as unique or primary key constraints
and foreign key references, always bypass row security to ensure that
data integrity is maintained.  Care must be taken when developing
schemas and row level policies to avoid "covert channel" leaks of
information through such referential integrity checks.

In some contexts it is important to be sure that row security is
not being applied.  For example, when taking a backup, it could be
disastrous if row security silently caused some rows to be omitted
from the backup.  In such a situation, you can set the
[guc-row-security](#guc-row-security) configuration parameter
to `off`.  This does not in itself bypass row security;
what it does is throw an error if any query's results would get filtered
by a policy.  The reason for the error can then be investigated and
fixed.

In the examples above, the policy expressions consider only the current
values in the row to be accessed or updated.  This is the simplest and
best-performing case; when possible, it's best to design row security
applications to work this way.  If it is necessary to consult other rows
or other tables to make a policy decision, that can be accomplished using
sub-`SELECT`s, or functions that contain `SELECT`s,
in the policy expressions.  Be aware however that such accesses can
create race conditions that could allow information leakage if care is
not taken.  As an example, consider the following table design:

```
-- definition of privilege groups
CREATE TABLE groups (group_id int PRIMARY KEY,
group_name text NOT NULL);

INSERT INTO groups VALUES
(1, 'low'),
(2, 'medium'),
(5, 'high');

GRANT ALL ON groups TO alice;  -- alice is the administrator
GRANT SELECT ON groups TO public;

-- definition of users' privilege levels
CREATE TABLE users (user_name text PRIMARY KEY,
group_id int NOT NULL REFERENCES groups);

INSERT INTO users VALUES
('alice', 5),
('bob', 2),
('mallory', 2);

GRANT ALL ON users TO alice;
GRANT SELECT ON users TO public;

-- table holding the information to be protected
CREATE TABLE information (info text,
group_id int NOT NULL REFERENCES groups);

INSERT INTO information VALUES
('barely secret', 1),
('slightly secret', 2),
('very secret', 5);

ALTER TABLE information ENABLE ROW LEVEL SECURITY;

-- a row should be visible to/updatable by users whose security group_id is
-- greater than or equal to the row's group_id
CREATE POLICY fp_s ON information FOR SELECT
USING (group_id  **Note:**

> Users of a cluster do not necessarily have the privilege to access every
> database in the cluster.  Sharing of role names means that there
> cannot be different roles named, say, `joe` in two databases
> in the same cluster; but the system can be configured to allow
> `joe` access to only some of the databases.
>

A database contains one or more named *schemas*, which
in turn contain tables.  Schemas also contain other kinds of named
objects, including data types, functions, and operators.  The same
object name can be used in different schemas without conflict; for
example, both `schema1` and `myschema` can
contain tables named `mytable`.  Unlike databases,
schemas are not rigidly separated: a user can access objects in any
of the schemas in the database they are connected to, if they have
privileges to do so.

There are several reasons why one might want to use schemas:

- To allow many users to use one database without interfering with
each other.
- To organize database objects into logical groups to make them
more manageable.
- Third-party applications can be put into separate schemas so
they do not collide with the names of other objects.

Schemas are analogous to directories at the operating system level,
except that schemas cannot be nested.

### Creating a Schema

To create a schema, use the [sql-createschema](#sql-createschema)
command.  Give the schema a name
of your choice.  For example:

```
CREATE SCHEMA myschema;
```

To create or access objects in a schema, write a
*qualified name* consisting of the schema name and
table name separated by a dot:

```
`schema``.``table`
```

This works anywhere a table name is expected, including the table
modification commands and the data access commands discussed in
the following chapters.
(For brevity we will speak of tables only, but the same ideas apply
to other kinds of named objects, such as types and functions.)

Actually, the even more general syntax

```
`database``.``schema``.``table`
```

can be used too, but at present this is just for pro forma
compliance with the SQL standard.  If you write a database name,
it must be the same as the database you are connected to.

So to create a table in the new schema, use:

```
CREATE TABLE myschema.mytable (
...
);
```

To drop a schema if it's empty (all objects in it have been
dropped), use:

```
DROP SCHEMA myschema;
```

To drop a schema including all contained objects, use:

```
DROP SCHEMA myschema CASCADE;
```

See [ddl-depend](#ddl-depend) for a description of the general
mechanism behind this.

Often you will want to create a schema owned by someone else
(since this is one of the ways to restrict the activities of your
users to well-defined namespaces).  The syntax for that is:

```
CREATE SCHEMA `schema_name` AUTHORIZATION `user_name`;
```

You can even omit the schema name, in which case the schema name
will be the same as the user name.  See [ddl-schemas-patterns](#ddl-schemas-patterns) for how this can be useful.

Schema names beginning with `pg_` are reserved for
system purposes and cannot be created by users.

### The Public Schema

In the previous sections we created tables without specifying any
schema names.  By default such tables (and other objects) are
automatically put into a schema named "public".  Every new
database contains such a schema.  Thus, the following are equivalent:

```
CREATE TABLE products ( ... );
```

and:

```
CREATE TABLE public.products ( ... );
```

### The Schema Search Path

Qualified names are tedious to write, and it's often best not to
wire a particular schema name into applications anyway.  Therefore
tables are often referred to by *unqualified names*,
which consist of just the table name.  The system determines which table
is meant by following a *search path*, which is a list
of schemas to look in.  The first matching table in the search path
is taken to be the one wanted.  If there is no match in the search
path, an error is reported, even if matching table names exist
in other schemas in the database.

The ability to create like-named objects in different schemas complicates
writing a query that references precisely the same objects every time.  It
also opens up the potential for users to change the behavior of other
users' queries, maliciously or accidentally.  Due to the prevalence of
unqualified names in queries and their use
in PostgreSQL internals, adding a schema
to `search_path` effectively trusts all users having
`CREATE` privilege on that schema.  When you run an
ordinary query, a malicious user able to create objects in a schema of
your search path can take control and execute arbitrary SQL functions as
though you executed them.

The first schema named in the search path is called the current schema.
Aside from being the first schema searched, it is also the schema in
which new tables will be created if the `CREATE TABLE`
command does not specify a schema name.

To show the current search path, use the following command:

```
SHOW search_path;
```

In the default setup this returns:

```
search_path
--------------
"$user", public
```

The first element specifies that a schema with the same name as
the current user is to be searched.  If no such schema exists,
the entry is ignored.  The second element refers to the
public schema that we have seen already.

The first schema in the search path that exists is the default
location for creating new objects.  That is the reason that by
default objects are created in the public schema.  When objects
are referenced in any other context without schema qualification
(table modification, data modification, or query commands) the
search path is traversed until a matching object is found.
Therefore, in the default configuration, any unqualified access
again can only refer to the public schema.

To put our new schema in the path, we use:

```
SET search_path TO myschema,public;
```

(We omit the `$user` here because we have no
immediate need for it.)  And then we can access the table without
schema qualification:

```
DROP TABLE mytable;
```

Also, since `myschema` is the first element in
the path, new objects would by default be created in it.

We could also have written:

```
SET search_path TO myschema;
```

Then we no longer have access to the public schema without
explicit qualification.  There is nothing special about the public
schema except that it exists by default.  It can be dropped, too.

See also [functions-info](#functions-info) for other ways to manipulate
the schema search path.

The search path works in the same way for data type names, function names,
and operator names as it does for table names.  Data type and function
names can be qualified in exactly the same way as table names.  If you
need to write a qualified operator name in an expression, there is a
special provision: you must write

```
`OPERATOR(``schema``.``operator``)`
```

This is needed to avoid syntactic ambiguity.  An example is:

```
SELECT 3 OPERATOR(pg_catalog.+) 4;
```

In practice one usually relies on the search path for operators,
so as not to have to write anything so ugly as that.

### Schemas and Privileges

By default, users cannot access any objects in schemas they do not
own.  To allow that, the owner of the schema must grant the
`USAGE` privilege on the schema.  By default, everyone
has that privilege on the schema `public`.  To allow
users to make use of the objects in a schema, additional privileges might
need to be granted, as appropriate for the object.

A user can also be allowed to create objects in someone else's schema.  To
allow that, the `CREATE` privilege on the schema needs to
be granted.  In databases upgraded from
PostgreSQL 14 or earlier, everyone has that
privilege on the schema `public`.
Some [usage patterns](#ddl-schemas-patterns) call for
revoking that privilege:

```
REVOKE CREATE ON SCHEMA public FROM PUBLIC;
```

(The first "public" is the schema, the second
"public" means "every user".  In the
first sense it is an identifier, in the second sense it is a
key word, hence the different capitalization; recall the
guidelines from [sql-syntax-identifiers](#sql-syntax-identifiers).)

### The System Catalog Schema

In addition to `public` and user-created schemas, each
database contains a `pg_catalog` schema, which contains
the system tables and all the built-in data types, functions, and
operators.  `pg_catalog` is always effectively part of
the search path.  If it is not named explicitly in the path then
it is implicitly searched *before* searching the path's
schemas.  This ensures that built-in names will always be
findable.  However, you can explicitly place
`pg_catalog` at the end of your search path if you
prefer to have user-defined names override built-in names.

Since system table names begin with `pg_`, it is best to
avoid such names to ensure that you won't suffer a conflict if some
future version defines a system table named the same as your
table.  (With the default search path, an unqualified reference to
your table name would then be resolved as the system table instead.)
System tables will continue to follow the convention of having
names beginning with `pg_`, so that they will not
conflict with unqualified user-table names so long as users avoid
the `pg_` prefix.

### Usage Patterns

Schemas can be used to organize your data in many ways.
A *secure schema usage pattern* prevents untrusted
users from changing the behavior of other users' queries.  When a database
does not use a secure schema usage pattern, users wishing to securely
query that database would take protective action at the beginning of each
session.  Specifically, they would begin each session by
setting `search_path` to the empty string or otherwise
removing schemas that are writable by non-superusers
from `search_path`.  There are a few usage patterns
easily supported by the default configuration:

- Constrain ordinary users to user-private schemas.
To implement this pattern, first ensure that no schemas have
public `CREATE` privileges.  Then, for every user
needing to create non-temporary objects, create a schema with the
same name as that user, for example
`CREATE SCHEMA alice AUTHORIZATION alice`.
(Recall that the default search path starts
with `$user`, which resolves to the user
name. Therefore, if each user has a separate schema, they access
their own schemas by default.)  This pattern is a secure schema
usage pattern unless an untrusted user is the database owner or
has been granted `ADMIN OPTION` on a relevant role,
in which case no secure schema usage pattern exists.

In PostgreSQL 15 and later, the default
configuration supports this usage pattern.  In prior versions, or
when using a database that has been upgraded from a prior version,
you will need to remove the public `CREATE`
privilege from the `public` schema (issue
`REVOKE CREATE ON SCHEMA public FROM PUBLIC`).
Then consider auditing the `public` schema for
objects named like objects in schema `pg_catalog`.
- Remove the public schema from the default search path, by modifying
[`postgresql.conf`](#config-setting-configuration-file)
or by issuing `ALTER ROLE ALL SET search_path =
"$user"`.  Then, grant privileges to create in the public
schema.  Only qualified names will choose public schema objects.  While
qualified table references are fine, calls to functions in the public
schema [will be unsafe or
unreliable](#typeconv-func).  If you create functions or extensions in the public
schema, use the first pattern instead.  Otherwise, like the first
pattern, this is secure unless an untrusted user is the database owner
or has been granted `ADMIN OPTION` on a relevant role.
- Keep the default search path, and grant privileges to create in the
public schema.  All users access the public schema implicitly.  This
simulates the situation where schemas are not available at all, giving
a smooth transition from the non-schema-aware world.  However, this is
never a secure pattern.  It is acceptable only when the database has a
single user or a few mutually-trusting users.  In databases upgraded
from PostgreSQL 14 or earlier, this is the
default.

For any pattern, to install shared applications (tables to be used by
everyone, additional functions provided by third parties, etc.), put them
into separate schemas.  Remember to grant appropriate privileges to allow
the other users to access them.  Users can then refer to these additional
objects by qualifying the names with a schema name, or they can put the
additional schemas into their search path, as they choose.

### Portability

In the SQL standard, the notion of objects in the same schema
being owned by different users does not exist.  Moreover, some
implementations do not allow you to create schemas that have a
different name than their owner.  In fact, the concepts of schema
and user are nearly equivalent in a database system that
implements only the basic schema support specified in the
standard.  Therefore, many users consider qualified names to
really consist of
``user_name`.`table_name``.
This is how PostgreSQL will effectively
behave if you create a per-user schema for every user.

Also, there is no concept of a `public` schema in the
SQL standard.  For maximum conformance to the standard, you should
not use the `public` schema.

Of course, some SQL database systems might not implement schemas
at all, or provide namespace support by allowing (possibly
limited) cross-database access.  If you need to work with those
systems, then maximum portability would be achieved by not using
schemas at all.
