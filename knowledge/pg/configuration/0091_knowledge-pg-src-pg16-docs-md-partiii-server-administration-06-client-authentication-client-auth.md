# User Name Maps

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/06_client_authentication.md`
- Source Title: `Client Authentication`
- Source Heading Path: `Client Authentication > User Name Maps`
- Source Line Ranges: `631-762`
- Chunk ID: `pg16_configuration_0091_e80d621618`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0909120680d7b5f798e7fe2717cdc6918bdde2bc71428396bfda47f7e5c1888e`

## Retrieval Guidance

- Use When: 外部认证返回 OS/principal 名称与数据库 role 名称不同，需要映射。
- Retrieval Keywords: pg_ident.conf, user name maps, map, system-username, database-username, regular expression, \1, pg_ident_file_mappings
- Follow-up Guidance: regex 默认可匹配子串，通常应使用 ^ 和 $。
- Classification Note: 定义 pg_ident.conf 映射语义、map 参数、include、regex capture、reload 和 pg_ident_file_mappings。

## Official Source Content

## User Name Maps

When using an external authentication system such as Ident or GSSAPI,
the name of the operating system user that initiated the connection
might not be the same as the database user (role) that is to be used.
In this case, a user name map can be applied to map the operating system
user name to a database user.  To use user name mapping, specify
`map`=`map-name`
in the options field in `pg_hba.conf`. This option is
supported for all authentication methods that receive external user names.
Since different mappings might be needed for different connections,
the name of the map to be used is specified in the
`map-name` parameter in `pg_hba.conf`
to indicate which map to use for each individual connection.

User name maps are defined in the ident map file, which by default is named
`pg_ident.conf`
and is stored in the
cluster's data directory.  (It is possible to place the map file
elsewhere, however; see the [guc-ident-file](#guc-ident-file)
configuration parameter.)
The ident map file contains lines of the general forms:

```
`map-name` `system-username` `database-username`
`include` `file`
`include_if_exists` `file`
`include_dir` `directory`
```

Comments, whitespace and line continuations are handled in the same way as in
`pg_hba.conf`.  The
`map-name` is an arbitrary name that will be used to
refer to this mapping in `pg_hba.conf`. The other
two fields specify an operating system user name and a matching
database user name. The same `map-name` can be
used repeatedly to specify multiple user-mappings within a single map.

As for `pg_hba.conf`, the lines in this file can
be include directives, following the same rules.

There is no restriction regarding how many database users a given
operating system user can correspond to, nor vice versa.  Thus, entries
in a map should be thought of as meaning "this operating system
user is allowed to connect as this database user", rather than
implying that they are equivalent.  The connection will be allowed if
there is any map entry that pairs the user name obtained from the
external authentication system with the database user name that the
user has requested to connect as. The value `all`
can be used as the `database-username` to specify
that if the `system-username` matches, then this
user is allowed to log in as any of the existing database users. Quoting
`all` makes the keyword lose its special meaning.

If the `database-username` begins with a
`+` character, then the operating system user can login as
any user belonging to that role, similarly to how user names beginning with
`+` are treated in `pg_hba.conf`.
Thus, a `+` mark means "match any of the roles that
are directly or indirectly members of this role", while a name
without a `+` mark matches only that specific role. Quoting
a username starting with a `+` makes the
`+` lose its special meaning.

If the `system-username` field starts with a slash (`/`),
the remainder of the field is treated as a regular expression.
(See [posix-syntax-details](#posix-syntax-details) for details of
PostgreSQL's regular expression syntax.)  The regular
expression can include a single capture, or parenthesized subexpression.
The portion of the system user name that matched the capture can then
be referenced in the `database-username`
field as `\1` (backslash-one).  This allows the mapping of
multiple user names in a single line, which is particularly useful for
simple syntax substitutions.  For example, these entries

```
mymap   /^(.*)@mydomain\.com$      \1
mymap   /^(.*)@otherdomain\.com$   guest
```

will remove the domain part for users with system user names that end with
`@mydomain.com`, and allow any user whose system name ends with
`@otherdomain.com` to log in as `guest`.
Quoting a `database-username` containing
`\1` *does not* make
`\1` lose its special meaning.

If the `database-username` field starts with
a slash (`/`), the remainder of the field is treated
as a regular expression.
When the `database-username` field is a regular
expression, it is not possible to use `\1` within it to
refer to a capture from the `system-username`
field.

> **Tip:**

> Keep in mind that by default, a regular expression can match just part of
> a string.  It's usually wise to use `^` and `$`, as
> shown in the above example, to force the match to be to the entire
> system user name.
>

The `pg_ident.conf` file is read on start-up and
when the main server process receives a
SIGHUP
signal. If you edit the file on an
active system, you will need to signal the postmaster
(using `pg_ctl reload`, calling the SQL function
`pg_reload_conf()`, or using `kill
-HUP`) to make it re-read the file.

The system view
[`pg_ident_file_mappings`](#view-pg-ident-file-mappings)
can be helpful for pre-testing changes to the
`pg_ident.conf` file, or for diagnosing problems if
loading of the file did not have the desired effects.  Rows in the view with
non-null `error` fields indicate problems in the
corresponding lines of the file.

A `pg_ident.conf` file that could be used in
conjunction with the `pg_hba.conf` file in [example-pg-hba.conf](#example-pg-hba.conf) is shown in [example-pg-ident.conf](#example-pg-ident.conf). In this example, anyone
logged in to a machine on the 192.168 network that does not have the
operating system user name `bryanh`, `ann`, or
`robert` would not be granted access. Unix user
`robert` would only be allowed access when he tries to
connect as PostgreSQL user `bob`, not
as `robert` or anyone else. `ann` would
only be allowed to connect as `ann`. User
`bryanh` would be allowed to connect as either
`bryanh` or as `guest1`.
