# Overview; all pg_catalog catalog tables and fields

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVII_internals/02_system_catalogs.md`
- Source Title: `System Catalogs`
- Source Heading Path: `System Catalogs > Overview; all pg_catalog catalog tables and fields`
- Source Line Ranges: `1-1843`
- Chunk ID: `pg16_fact_0097_4ea70f6055`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `eef41a03a1aaf40c855a9e789e54a858e8346e8c229c444e0662a9e1d0c6f206`

## Retrieval Guidance

- Use When: Look up PostgreSQL catalog table definitions and field meanings.
- Retrieval Keywords: system catalogs, pg_class, pg_attribute, pg_proc, pg_database, pg_index, pg_statistic, pg_authid
- Follow-up Guidance: Use operational diagnostic records only when catalog fields are interpreted with symptoms from a live incident.
- Classification Note: Per instruction, system catalog fields are classified as fact; the chapter is a reference for catalog table structure and metadata.

## Official Source Content

# System Catalogs

The system catalogs are the place where a relational database
management system stores schema metadata, such as information about
tables and columns, and internal bookkeeping information.
PostgreSQL's system catalogs are regular
tables.  You can drop and recreate the tables, add columns, insert
and update values, and severely mess up your system that way.
Normally, one should not change the system catalogs by hand, there
are normally SQL commands to do that.  (For example, `CREATE
DATABASE` inserts a row into the
`pg_database` catalog — and actually
creates the database on disk.)  There are some exceptions for
particularly esoteric operations, but many of those have been made
available as SQL commands over time, and so the need for direct manipulation
of the system catalogs is ever decreasing.

## Overview

[catalog-table](#catalog-table) lists the system catalogs.
More detailed documentation of each catalog follows below.

Most system catalogs are copied from the template database during
database creation and are thereafter database-specific. A few
catalogs are physically shared across all databases in a cluster;
these are noted in the descriptions of the individual catalogs.

| Catalog Name | Purpose |
| --- | --- |
| [`pg_aggregate`](#catalog-pg-aggregate) | aggregate functions |
| [`pg_am`](#catalog-pg-am) | relation access methods |
| [`pg_amop`](#catalog-pg-amop) | access method operators |
| [`pg_amproc`](#catalog-pg-amproc) | access method support functions |
| [`pg_attrdef`](#catalog-pg-attrdef) | column default values |
| [`pg_attribute`](#catalog-pg-attribute) | table columns ("attributes") |
| [`pg_authid`](#catalog-pg-authid) | authorization identifiers (roles) |
| [`pg_auth_members`](#catalog-pg-auth-members) | authorization identifier membership relationships |
| [`pg_cast`](#catalog-pg-cast) | casts (data type conversions) |
| [`pg_class`](#catalog-pg-class) | tables, indexes, sequences, views ("relations") |
| [`pg_collation`](#catalog-pg-collation) | collations (locale information) |
| [`pg_constraint`](#catalog-pg-constraint) | check constraints, unique constraints, primary key constraints, foreign key constraints |
| [`pg_conversion`](#catalog-pg-conversion) | encoding conversion information |
| [`pg_database`](#catalog-pg-database) | databases within this database cluster |
| [`pg_db_role_setting`](#catalog-pg-db-role-setting) | per-role and per-database settings |
| [`pg_default_acl`](#catalog-pg-default-acl) | default privileges for object types |
| [`pg_depend`](#catalog-pg-depend) | dependencies between database objects |
| [`pg_description`](#catalog-pg-description) | descriptions or comments on database objects |
| [`pg_enum`](#catalog-pg-enum) | enum label and value definitions |
| [`pg_event_trigger`](#catalog-pg-event-trigger) | event triggers |
| [`pg_extension`](#catalog-pg-extension) | installed extensions |
| [`pg_foreign_data_wrapper`](#catalog-pg-foreign-data-wrapper) | foreign-data wrapper definitions |
| [`pg_foreign_server`](#catalog-pg-foreign-server) | foreign server definitions |
| [`pg_foreign_table`](#catalog-pg-foreign-table) | additional foreign table information |
| [`pg_index`](#catalog-pg-index) | additional index information |
| [`pg_inherits`](#catalog-pg-inherits) | table inheritance hierarchy |
| [`pg_init_privs`](#catalog-pg-init-privs) | object initial privileges |
| [`pg_language`](#catalog-pg-language) | languages for writing functions |
| [`pg_largeobject`](#catalog-pg-largeobject) | data pages for large objects |
| [`pg_largeobject_metadata`](#catalog-pg-largeobject-metadata) | metadata for large objects |
| [`pg_namespace`](#catalog-pg-namespace) | schemas |
| [`pg_opclass`](#catalog-pg-opclass) | access method operator classes |
| [`pg_operator`](#catalog-pg-operator) | operators |
| [`pg_opfamily`](#catalog-pg-opfamily) | access method operator families |
| [`pg_parameter_acl`](#catalog-pg-parameter-acl) | configuration parameters for which privileges have been granted |
| [`pg_partitioned_table`](#catalog-pg-partitioned-table) | information about partition key of tables |
| [`pg_policy`](#catalog-pg-policy) | row-security policies |
| [`pg_proc`](#catalog-pg-proc) | functions and procedures |
| [`pg_publication`](#catalog-pg-publication) | publications for logical replication |
| [`pg_publication_namespace`](#catalog-pg-publication-namespace) | schema to publication mapping |
| [`pg_publication_rel`](#catalog-pg-publication-rel) | relation to publication mapping |
| [`pg_range`](#catalog-pg-range) | information about range types |
| [`pg_replication_origin`](#catalog-pg-replication-origin) | registered replication origins |
| [`pg_rewrite`](#catalog-pg-rewrite) | query rewrite rules |
| [`pg_seclabel`](#catalog-pg-seclabel) | security labels on database objects |
| [`pg_sequence`](#catalog-pg-sequence) | information about sequences |
| [`pg_shdepend`](#catalog-pg-shdepend) | dependencies on shared objects |
| [`pg_shdescription`](#catalog-pg-shdescription) | comments on shared objects |
| [`pg_shseclabel`](#catalog-pg-shseclabel) | security labels on shared database objects |
| [`pg_statistic`](#catalog-pg-statistic) | planner statistics |
| [`pg_statistic_ext`](#catalog-pg-statistic-ext) | extended planner statistics (definition) |
| [`pg_statistic_ext_data`](#catalog-pg-statistic-ext-data) | extended planner statistics (built statistics) |
| [`pg_subscription`](#catalog-pg-subscription) | logical replication subscriptions |
| [`pg_subscription_rel`](#catalog-pg-subscription-rel) | relation state for subscriptions |
| [`pg_tablespace`](#catalog-pg-tablespace) | tablespaces within this database cluster |
| [`pg_transform`](#catalog-pg-transform) | transforms (data type to procedural language conversions) |
| [`pg_trigger`](#catalog-pg-trigger) | triggers |
| [`pg_ts_config`](#catalog-pg-ts-config) | text search configurations |
| [`pg_ts_config_map`](#catalog-pg-ts-config-map) | text search configurations' token mappings |
| [`pg_ts_dict`](#catalog-pg-ts-dict) | text search dictionaries |
| [`pg_ts_parser`](#catalog-pg-ts-parser) | text search parsers |
| [`pg_ts_template`](#catalog-pg-ts-template) | text search templates |
| [`pg_type`](#catalog-pg-type) | data types |
| [`pg_user_mapping`](#catalog-pg-user-mapping) | mappings of users to foreign servers |

## `pg_aggregate`

The catalog `pg_aggregate` stores information about
aggregate functions.  An aggregate function is a function that
operates on a set of values (typically one column from each row
that matches a query condition) and returns a single value computed
from all these values.  Typical aggregate functions are
`sum`, `count`, and
`max`.  Each entry in
`pg_aggregate` is an extension of an entry
in [`pg_proc`](#catalog-pg-proc).
The `pg_proc` entry carries the aggregate's name,
input and output data types, and other information that is similar to
ordinary functions.

| Column Type                      Description |
| --- |
| `aggfnoid` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      `pg_proc` OID of the aggregate function |
| `aggkind` `char`                      Aggregate kind:        `n` for "normal" aggregates,        `o` for "ordered-set" aggregates, or        `h` for "hypothetical-set" aggregates |
| `aggnumdirectargs` `int2`                      Number of direct (non-aggregated) arguments of an ordered-set or        hypothetical-set aggregate, counting a variadic array as one argument.        If equal to `pronargs`, the aggregate must be variadic        and the variadic array describes the aggregated arguments as well as        the final direct arguments.        Always zero for normal aggregates. |
| `aggtransfn` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Transition function |
| `aggfinalfn` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Final function (zero if none) |
| `aggcombinefn` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Combine function (zero if none) |
| `aggserialfn` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Serialization function (zero if none) |
| `aggdeserialfn` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Deserialization function (zero if none) |
| `aggmtransfn` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Forward transition function for moving-aggregate mode (zero if none) |
| `aggminvtransfn` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Inverse transition function for moving-aggregate mode (zero if none) |
| `aggmfinalfn` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Final function for moving-aggregate mode (zero if none) |
| `aggfinalextra` `bool`                      True to pass extra dummy arguments to `aggfinalfn` |
| `aggmfinalextra` `bool`                      True to pass extra dummy arguments to `aggmfinalfn` |
| `aggfinalmodify` `char`                      Whether `aggfinalfn` modifies the        transition state value:        `r` if it is read-only,        `s` if the `aggtransfn`        cannot be applied after the `aggfinalfn`, or        `w` if it writes on the value |
| `aggmfinalmodify` `char`                      Like `aggfinalmodify`, but for        the `aggmfinalfn` |
| `aggsortop` `oid`        (references [`pg_operator`](#catalog-pg-operator).`oid`)                      Associated sort operator (zero if none) |
| `aggtranstype` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Data type of the aggregate function's internal transition (state) data |
| `aggtransspace` `int4`                      Approximate average size (in bytes) of the transition state        data, or zero to use a default estimate |
| `aggmtranstype` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Data type of the aggregate function's internal transition (state)        data for moving-aggregate mode (zero if none) |
| `aggmtransspace` `int4`                      Approximate average size (in bytes) of the transition state data        for moving-aggregate mode, or zero to use a default estimate |
| `agginitval` `text`                      The initial value of the transition state.  This is a text        field containing the initial value in its external string        representation.  If this field is null, the transition state        value starts out null. |
| `aggminitval` `text`                      The initial value of the transition state for moving-aggregate mode.        This is a text field containing the initial value in its external        string representation.  If this field is null, the transition state        value starts out null. |

New aggregate functions are registered with the [`CREATE AGGREGATE`](#sql-createaggregate)
command.  See [xaggr](#xaggr) for more information about
writing aggregate functions and the meaning of the transition
functions, etc.

## `pg_am`

The catalog `pg_am` stores information about
relation access methods.  There is one row for each access method supported
by the system.
Currently, only tables and indexes have access methods. The requirements for table
and index access methods are discussed in detail in [tableam](#tableam) and
[indexam](#indexam) respectively.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `amname` `name`                      Name of the access method |
| `amhandler` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      OID of a handler function that is responsible for supplying information        about the access method |
| `amtype` `char`                      `t` = table (including materialized views),        `i` = index. |

> **Note:**

> Before PostgreSQL 9.6, `pg_am`
> contained many additional columns representing properties of index access
> methods.  That data is now only directly visible at the C code level.
> However, `pg_index_column_has_property()` and related
> functions have been added to allow SQL queries to inspect index access
> method properties; see [functions-info-catalog-table](#functions-info-catalog-table).
>

## `pg_amop`

The catalog `pg_amop` stores information about
operators associated with access method operator families.  There is one
row for each operator that is a member of an operator family.  A family
member can be either a *search* operator or an
*ordering* operator.  An operator
can appear in more than one family, but cannot appear in more than one
search position nor more than one ordering position within a family.
(It is allowed, though unlikely, for an operator to be used for both
search and ordering purposes.)

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `amopfamily` `oid`        (references [`pg_opfamily`](#catalog-pg-opfamily).`oid`)                      The operator family this entry is for |
| `amoplefttype` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Left-hand input data type of operator |
| `amoprighttype` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Right-hand input data type of operator |
| `amopstrategy` `int2`                      Operator strategy number |
| `amoppurpose` `char`                      Operator purpose, either `s` for search or        `o` for ordering |
| `amopopr` `oid`        (references [`pg_operator`](#catalog-pg-operator).`oid`)                      OID of the operator |
| `amopmethod` `oid`        (references [`pg_am`](#catalog-pg-am).`oid`)                      Index access method operator family is for |
| `amopsortfamily` `oid`        (references [`pg_opfamily`](#catalog-pg-opfamily).`oid`)                      The B-tree operator family this entry sorts according to, if an        ordering operator; zero if a search operator |

A "search" operator entry indicates that an index of this operator
family can be searched to find all rows satisfying
`WHERE`
`indexed_column`
`operator`
`constant`.
Obviously, such an operator must return `boolean`, and its left-hand input
type must match the index's column data type.

An "ordering" operator entry indicates that an index of this
operator family can be scanned to return rows in the order represented by
`ORDER BY`
`indexed_column`
`operator`
`constant`.
Such an operator could return any sortable data type, though again
its left-hand input type must match the index's column data type.
The exact semantics of the `ORDER BY` are specified by the
`amopsortfamily` column, which must reference
a B-tree operator family for the operator's result type.

> **Note:**

> At present, it's assumed that the sort order for an ordering operator
> is the default for the referenced operator family, i.e., `ASC NULLS
> LAST`.  This might someday be relaxed by adding additional columns
> to specify sort options explicitly.
>

An entry's `amopmethod` must match the
`opfmethod` of its containing operator family (including
`amopmethod` here is an intentional denormalization of the
catalog structure for performance reasons).  Also,
`amoplefttype` and `amoprighttype` must match
the `oprleft` and `oprright` fields of the
referenced [`pg_operator`](#catalog-pg-operator) entry.

## `pg_amproc`

The catalog `pg_amproc` stores information about
support functions associated with access method operator families.  There
is one row for each support function belonging to an operator family.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `amprocfamily` `oid`        (references [`pg_opfamily`](#catalog-pg-opfamily).`oid`)                      The operator family this entry is for |
| `amproclefttype` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Left-hand input data type of associated operator |
| `amprocrighttype` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Right-hand input data type of associated operator |
| `amprocnum` `int2`                      Support function number |
| `amproc` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      OID of the function |

The usual interpretation of the
`amproclefttype` and `amprocrighttype` fields
is that they identify the left and right input types of the operator(s)
that a particular support function supports.  For some access methods
these match the input data type(s) of the support function itself, for
others not.  There is a notion of "default" support functions for
an index, which are those with `amproclefttype` and
`amprocrighttype` both equal to the index operator class's
`opcintype`.

## `pg_attrdef`

The catalog `pg_attrdef` stores column default
values.  The main information about columns is stored in
[`pg_attribute`](#catalog-pg-attribute).
Only columns for which a default value has been explicitly set will have
an entry here.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `adrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The table this column belongs to |
| `adnum` `int2`        (references [`pg_attribute`](#catalog-pg-attribute).`attnum`)                      The number of the column |
| `adbin` `pg_node_tree`                      The column default value, in `nodeToString()`        representation.  Use `pg_get_expr(adbin, adrelid)` to        convert it to an SQL expression. |

## `pg_attribute`

The catalog `pg_attribute` stores information about
table columns.  There will be exactly one
`pg_attribute` row for every column in every
table in the database.  (There will also be attribute entries for
indexes, and indeed all objects that have
[`pg_class`](#catalog-pg-class)
entries.)

The term attribute is equivalent to column and is used for
historical reasons.

| Column Type                      Description |
| --- |
| `attrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The table this column belongs to |
| `attname` `name`                      The column name |
| `atttypid` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      The data type of this column (zero for a dropped column) |
| `attlen` `int2`                      A copy of `pg_type.typlen` of this column's        type |
| `attnum` `int2`                      The number of the column.  Ordinary columns are numbered from 1        up.  System columns, such as `ctid`,        have (arbitrary) negative numbers. |
| `attcacheoff` `int4`                      Always -1 in storage, but when loaded into a row descriptor        in memory this might be updated to cache the offset of the attribute        within the row |
| `atttypmod` `int4`                      `atttypmod` records type-specific data        supplied at table creation time (for example, the maximum        length of a `varchar` column).  It is passed to        type-specific input functions and length coercion functions.        The value will generally be -1 for types that do not need `atttypmod`. |
| `attndims` `int2`                      Number of dimensions, if the column is an array type; otherwise 0.        (Presently, the number of dimensions of an array is not enforced,        so any nonzero value effectively means "it's an array".) |
| `attbyval` `bool`                      A copy of `pg_type.typbyval` of this column's type |
| `attalign` `char`                      A copy of `pg_type.typalign` of this column's type |
| `attstorage` `char`                      Normally a copy of `pg_type.typstorage` of this        column's type.  For TOAST-able data types, this can be altered        after column creation to control storage policy. |
| `attcompression` `char`                      The current compression method of the column.  Typically this is        `'\0'` to specify use of the current default setting        (see [guc-default-toast-compression](#guc-default-toast-compression)).  Otherwise,        `'p'` selects pglz compression, while        `'l'` selects LZ4        compression.  However, this field is ignored        whenever `attstorage` does not allow        compression. |
| `attnotnull` `bool`                      This represents a not-null constraint. |
| `atthasdef` `bool`                      This column has a default expression or generation expression, in which        case there will be a corresponding entry in the        [`pg_attrdef`](#catalog-pg-attrdef) catalog that actually defines the        expression.  (Check `attgenerated` to        determine whether this is a default or a generation expression.) |
| `atthasmissing` `bool`                      This column has a value which is used where the column is entirely        missing from the row, as happens when a column is added with a        non-volatile `DEFAULT` value after the row is created.        The actual value used is stored in the        `attmissingval` column. |
| `attidentity` `char`                      If a zero byte (`''`), then not an identity column.        Otherwise, `a` = generated        always, `d` = generated by default. |
| `attgenerated` `char`                      If a zero byte (`''`), then not a generated column.        Otherwise, `s` = stored.  (Other values might be added        in the future.) |
| `attisdropped` `bool`                      This column has been dropped and is no longer valid.  A dropped        column is still physically present in the table, but is        ignored by the parser and so cannot be accessed via SQL. |
| `attislocal` `bool`                      This column is defined locally in the relation.  Note that a column can        be locally defined and inherited simultaneously. |
| `attinhcount` `int2`                      The number of direct ancestors this column has.  A column with a        nonzero number of ancestors cannot be dropped nor renamed. |
| `attstattarget` `int2`                      `attstattarget` controls the level of detail        of statistics accumulated for this column by        [`ANALYZE`](#sql-analyze).        A zero value indicates that no statistics should be collected.        A negative value says to use the system default statistics target.        The exact meaning of positive values is data type-dependent.        For scalar data types, `attstattarget`        is both the target number of "most common values"        to collect, and the target number of histogram bins to create. |
| `attcollation` `oid`        (references [`pg_collation`](#catalog-pg-collation).`oid`)                      The defined collation of the column, or zero if the column is        not of a collatable data type |
| `attacl` `aclitem[]`                      Column-level access privileges, if any have been granted specifically        on this column |
| `attoptions` `text[]`                      Attribute-level options, as "keyword=value" strings |
| `attfdwoptions` `text[]`                      Attribute-level foreign data wrapper options, as "keyword=value" strings |
| `attmissingval` `anyarray`                      This column has a one element array containing the value used when the        column is entirely missing from the row, as happens when the column is        added with a non-volatile `DEFAULT` value after the        row is created.  The value is only used when        `atthasmissing` is true.  If there is no value        the column is null. |

In a dropped column's `pg_attribute` entry,
`atttypid` is reset to zero, but
`attlen` and the other fields copied from
[`pg_type`](#catalog-pg-type) are still valid.  This arrangement is needed
to cope with the situation where the dropped column's data type was
later dropped, and so there is no `pg_type` row anymore.
`attlen` and the other fields can be used
to interpret the contents of a row of the table.

## `pg_authid`

The catalog `pg_authid` contains information about
database authorization identifiers (roles).  A role subsumes the concepts
of "users" and "groups".  A user is essentially just a
role with the `rolcanlogin` flag set.  Any role (with or
without `rolcanlogin`) can have other roles as members; see
[`pg_auth_members`](#catalog-pg-auth-members).

Since this catalog contains passwords, it must not be publicly readable.
[`pg_roles`](#view-pg-roles)
is a publicly readable view on
`pg_authid` that blanks out the password field.

[user-manag](#user-manag) contains detailed information about user and
privilege management.

Because user identities are cluster-wide,
`pg_authid`
is shared across all databases of a cluster: there is only one
copy of `pg_authid` per cluster, not
one per database.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `rolname` `name`                      Role name |
| `rolsuper` `bool`                      Role has superuser privileges |
| `rolinherit` `bool`                      Role automatically inherits privileges of roles it is a        member of |
| `rolcreaterole` `bool`                      Role can create more roles |
| `rolcreatedb` `bool`                      Role can create databases |
| `rolcanlogin` `bool`                      Role can log in. That is, this role can be given as the initial        session authorization identifier. |
| `rolreplication` `bool`                      Role is a replication role. A replication role can initiate replication        connections and create and drop replication slots. |
| `rolbypassrls` `bool`                      Role bypasses every row-level security policy, see        [ddl-rowsecurity](#ddl-rowsecurity) for more information. |
| `rolconnlimit` `int4`                      For roles that can log in, this sets maximum number of concurrent        connections this role can make.  -1 means no limit. |
| `rolpassword` `text`                      Encrypted password; null if none. The format depends        on the form of encryption used. |
| `rolvaliduntil` `timestamptz`                      Password expiry time (only used for password authentication);        null if no expiration |

For an MD5 encrypted password, `rolpassword`
column will begin with the string `md5` followed by a
32-character hexadecimal MD5 hash. The MD5 hash will be of the user's
password concatenated to their user name. For example, if user
`joe` has password `xyzzy`, PostgreSQL
will store the md5 hash of `xyzzyjoe`.

If the password is encrypted with SCRAM-SHA-256, it has the format:

```
SCRAM-SHA-256$``:``$``:``
```

where `salt`, `StoredKey` and
`ServerKey` are in Base64 encoded format. This format is
the same as that specified by [RFC 5803](https://datatracker.ietf.org/doc/html/rfc5803).

## `pg_auth_members`

The catalog `pg_auth_members` shows the membership
relations between roles.  Any non-circular set of relationships is allowed.

Because user identities are cluster-wide,
`pg_auth_members`
is shared across all databases of a cluster: there is only one
copy of `pg_auth_members` per cluster, not
one per database.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `roleid` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      ID of a role that has a member |
| `member` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      ID of a role that is a member of `roleid` |
| `grantor` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      ID of the role that granted this membership |
| `admin_option` `bool`                      True if `member` can grant membership in        `roleid` to others |
| `inherit_option` `bool`                      True if the member automatically inherits the privileges of the        granted role |
| `set_option` `bool`                      True if the member can        [`SET ROLE`](#sql-set-role)        to the granted role |

## `pg_cast`

The catalog `pg_cast` stores data type conversion
paths, both built-in and user-defined.

It should be noted that `pg_cast` does not represent
every type conversion that the system knows how to perform; only those that
cannot be deduced from some generic rule.  For example, casting between a
domain and its base type is not explicitly represented in
`pg_cast`.  Another important exception is that
"automatic I/O conversion casts", those performed using a data
type's own I/O functions to convert to or from `text` or other
string types, are not explicitly represented in
`pg_cast`.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `castsource` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      OID of the source data type |
| `casttarget` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      OID of the target data type |
| `castfunc` `oid`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      The OID of the function to use to perform this cast.  Zero is        stored if the cast method doesn't require a function. |
| `castcontext` `char`                      Indicates what contexts the cast can be invoked in.        `e` means only as an explicit cast (using        `CAST` or `::` syntax).        `a` means implicitly in assignment        to a target column, as well as explicitly.        `i` means implicitly in expressions, as well as the        other cases. |
| `castmethod` `char`                      Indicates how the cast is performed.        `f` means that the function specified in the `castfunc` field is used.        `i` means that the input/output functions are used.        `b` means that the types are binary-coercible, thus no conversion is required. |

The cast functions listed in `pg_cast` must
always take the cast source type as their first argument type, and
return the cast destination type as their result type.  A cast
function can have up to three arguments.  The second argument,
if present, must be type `integer`; it receives the type
modifier associated with the destination type, or -1
if there is none.  The third argument,
if present, must be type `boolean`; it receives `true`
if the cast is an explicit cast, `false` otherwise.

It is legitimate to create a `pg_cast` entry
in which the source and target types are the same, if the associated
function takes more than one argument.  Such entries represent
"length coercion functions" that coerce values of the type
to be legal for a particular type modifier value.

When a `pg_cast` entry has different source and
target types and a function that takes more than one argument, it
represents converting from one type to another and applying a length
coercion in a single step.  When no such entry is available, coercion
to a type that uses a type modifier involves two steps, one to
convert between data types and a second to apply the modifier.

## `pg_class`

The catalog `pg_class` describes tables and
other objects that have columns or are otherwise similar to a
table.  This includes indexes (but see also [`pg_index`](#catalog-pg-index)),
sequences (but see also [`pg_sequence`](#catalog-pg-sequence)),
views, materialized views, composite types, and TOAST tables;
see `relkind`.
Below, when we mean all of these kinds of objects we speak of
"relations".  Not all of `pg_class`'s
columns are meaningful for all relation kinds.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `relname` `name`                      Name of the table, index, view, etc. |
| `relnamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      The OID of the namespace that contains this relation |
| `reltype` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      The OID of the data type that corresponds to this table's row type,        if any; zero for indexes, sequences, and toast tables, which have        no `pg_type` entry |
| `reloftype` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      For typed tables, the OID of the underlying composite type;        zero for all other relations |
| `relowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the relation |
| `relam` `oid`        (references [`pg_am`](#catalog-pg-am).`oid`)                      If this is a table or an index, the access method used (heap,        B-tree, hash, etc.); otherwise zero (zero occurs for sequences,        as well as relations without storage, such as views) |
| `relfilenode` `oid`                      Name of the on-disk file of this relation; zero means this        is a "mapped" relation whose disk file name is determined        by low-level state |
| `reltablespace` `oid`        (references [`pg_tablespace`](#catalog-pg-tablespace).`oid`)                      The tablespace in which this relation is stored.        If zero, the database's default tablespace is implied.        Not meaningful if the relation has no on-disk file,        except for partitioned tables, where this is the tablespace        in which partitions will be created when one is not        specified in the creation command. |
| `relpages` `int4`                      Size of the on-disk representation of this table in pages (of size        `BLCKSZ`).  This is only an estimate used by the        planner.  It is updated by [`VACUUM`](#sql-vacuum),        [`ANALYZE`](#sql-analyze), and a few DDL commands such as        [`CREATE INDEX`](#sql-createindex). |
| `reltuples` `float4`                      Number of live rows in the table.  This is only an estimate used by        the planner.  It is updated by [`VACUUM`](#sql-vacuum),        [`ANALYZE`](#sql-analyze), and a few DDL commands such as        [`CREATE INDEX`](#sql-createindex).        If the table has never yet been vacuumed or        analyzed, `reltuples`        contains `-1` indicating that the row count is        unknown. |
| `relallvisible` `int4`                      Number of pages that are marked all-visible in the table's        visibility map.  This is only an estimate used by the        planner.  It is updated by [`VACUUM`](#sql-vacuum),        [`ANALYZE`](#sql-analyze), and a few DDL commands such as        [`CREATE INDEX`](#sql-createindex). |
| `reltoastrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      OID of the TOAST table associated with this table, zero if none.  The        TOAST table stores large attributes "out of line" in a        secondary table. |
| `relhasindex` `bool`                      True if this is a table and it has (or recently had) any indexes |
| `relisshared` `bool`                      True if this table is shared across all databases in the cluster.  Only        certain system catalogs (such as [`pg_database`](#catalog-pg-database))        are shared. |
| `relpersistence` `char`                      `p` = permanent table/sequence, `u` = unlogged table/sequence,        `t` = temporary table/sequence |
| `relkind` `char`                      `r` = ordinary table,        `i` = index,        `S` = sequence,        `t` = TOAST table,        `v` = view,        `m` = materialized view,        `c` = composite type,        `f` = foreign table,        `p` = partitioned table,        `I` = partitioned index |
| `relnatts` `int2`                      Number of user columns in the relation (system columns not        counted).  There must be this many corresponding entries in        [`pg_attribute`](#catalog-pg-attribute).  See also        `pg_attribute`.`attnum`. |
| `relchecks` `int2`                      Number of `CHECK` constraints on the table; see        [`pg_constraint`](#catalog-pg-constraint) catalog |
| `relhasrules` `bool`                      True if table has (or once had) rules; see        [`pg_rewrite`](#catalog-pg-rewrite) catalog |
| `relhastriggers` `bool`                      True if table has (or once had) triggers; see        [`pg_trigger`](#catalog-pg-trigger) catalog |
| `relhassubclass` `bool`                      True if table or index has (or once had) any inheritance children or partitions |
| `relrowsecurity` `bool`                      True if table has row-level security enabled; see        [`pg_policy`](#catalog-pg-policy) catalog |
| `relforcerowsecurity` `bool`                      True if row-level security (when enabled) will also apply to table owner; see        [`pg_policy`](#catalog-pg-policy) catalog |
| `relispopulated` `bool`                      True if relation is populated (this is true for all        relations other than some materialized views) |
| `relreplident` `char`                      Columns used to form "replica identity" for rows:        `d` = default (primary key, if any),        `n` = nothing,        `f` = all columns,        `i` = index with        `indisreplident` set (same as nothing if the        index used has been dropped) |
| `relispartition` `bool`                      True if table or index is a partition |
| `relrewrite` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      For new relations being written during a DDL operation that requires a        table rewrite, this contains the OID of the original relation;        otherwise zero.  That state is only visible internally; this field should        never contain anything other than zero for a user-visible relation. |
| `relfrozenxid` `xid`                      All transaction IDs before this one have been replaced with a permanent        ("frozen") transaction ID in this table.  This is used to track        whether the table needs to be vacuumed in order to prevent transaction        ID wraparound or to allow `pg_xact` to be shrunk.  Zero        (`InvalidTransactionId`) if the relation is not a table. |
| `relminmxid` `xid`                      All multixact IDs before this one have been replaced by a        transaction ID in this table.  This is used to track        whether the table needs to be vacuumed in order to prevent multixact ID        wraparound or to allow `pg_multixact` to be shrunk.  Zero        (`InvalidMultiXactId`) if the relation is not a table. |
| `relacl` `aclitem[]`                      Access privileges; see [ddl-priv](#ddl-priv) for details |
| `reloptions` `text[]`                      Access-method-specific options, as "keyword=value" strings |
| `relpartbound` `pg_node_tree`                      If table is a partition (see `relispartition`),        internal representation of the partition bound |

Several of the Boolean flags in `pg_class` are maintained
lazily: they are guaranteed to be true if that's the correct state, but
may not be reset to false immediately when the condition is no longer
true.  For example, `relhasindex` is set by
[`CREATE INDEX`](#sql-createindex), but it is never cleared by
[`DROP INDEX`](#sql-dropindex).  Instead, [`VACUUM`](#sql-vacuum) clears
`relhasindex` if it finds the table has no indexes.  This
arrangement avoids race conditions and improves concurrency.

## `pg_collation`

The catalog `pg_collation` describes the
available collations, which are essentially mappings from an SQL
name to operating system locale categories.
See [collation](#collation) for more information.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `collname` `name`                      Collation name (unique per namespace and encoding) |
| `collnamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      The OID of the namespace that contains this collation |
| `collowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the collation |
| `collprovider` `char`                      Provider of the collation: `d` = database        default, `c` = libc, `i` = icu |
| `collisdeterministic` `bool`                      Is the collation deterministic? |
| `collencoding` `int4`                      Encoding in which the collation is applicable, or -1 if it        works for any encoding |
| `collcollate` `text`                      `LC_COLLATE` for this collation object |
| `collctype` `text`                      `LC_CTYPE` for this collation object |
| `colliculocale` `text`                      ICU locale ID for this collation object |
| `collicurules` `text`                      ICU collation rules for this collation object |
| `collversion` `text`                      Provider-specific version of the collation.  This is recorded when the        collation is created and then checked when it is used, to detect        changes in the collation definition that could lead to data corruption. |

Note that the unique key on this catalog is (`collname`,
`collencoding`, `collnamespace`) not just
(`collname`, `collnamespace`).
PostgreSQL generally ignores all
collations that do not have `collencoding` equal to
either the current database's encoding or -1, and creation of new entries
with the same name as an entry with `collencoding` = -1
is forbidden.  Therefore it is sufficient to use a qualified SQL name
(`schema`.`name`) to identify a collation,
even though this is not unique according to the catalog definition.
The reason for defining the catalog this way is that
initdb fills it in at cluster initialization time with
entries for all locales available on the system, so it must be able to
hold entries for all encodings that might ever be used in the cluster.

In the `template0` database, it could be useful to create
collations whose encoding does not match the database encoding,
since they could match the encodings of databases later cloned from
`template0`.  This would currently have to be done manually.

## `pg_constraint`

The catalog `pg_constraint` stores check, primary
key, unique, foreign key, and exclusion constraints on tables.
(Column constraints are not treated specially.  Every column constraint is
equivalent to some table constraint.)
Not-null constraints are represented in the
[`pg_attribute`](#catalog-pg-attribute)
catalog, not here.

User-defined constraint triggers (created with [
`CREATE CONSTRAINT TRIGGER`](#sql-createtrigger)) also give rise to an entry in this table.

Check constraints on domains are stored here, too.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `conname` `name`                      Constraint name (not necessarily unique!) |
| `connamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      The OID of the namespace that contains this constraint |
| `contype` `char`                      `c` = check constraint,        `f` = foreign key constraint,        `p` = primary key constraint,        `u` = unique constraint,        `t` = constraint trigger,        `x` = exclusion constraint |
| `condeferrable` `bool`                      Is the constraint deferrable? |
| `condeferred` `bool`                      Is the constraint deferred by default? |
| `convalidated` `bool`                      Has the constraint been validated?        Currently, can be false only for foreign keys and CHECK constraints |
| `conrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The table this constraint is on; zero if not a table constraint |
| `contypid` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      The domain this constraint is on; zero if not a domain constraint |
| `conindid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The index supporting this constraint, if it's a unique, primary        key, foreign key, or exclusion constraint; else zero |
| `conparentid` `oid`        (references [`pg_constraint`](#catalog-pg-constraint).`oid`)                      The corresponding constraint of the parent partitioned table,        if this is a constraint on a partition; else zero |
| `confrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      If a foreign key, the referenced table; else zero |
| `confupdtype` `char`                      Foreign key update action code:        `a` = no action,        `r` = restrict,        `c` = cascade,        `n` = set null,        `d` = set default |
| `confdeltype` `char`                      Foreign key deletion action code:        `a` = no action,        `r` = restrict,        `c` = cascade,        `n` = set null,        `d` = set default |
| `confmatchtype` `char`                      Foreign key match type:        `f` = full,        `p` = partial,        `s` = simple |
| `conislocal` `bool`                      This constraint is defined locally for the relation.  Note that a        constraint can be locally defined and inherited simultaneously. |
| `coninhcount` `int2`                      The number of direct inheritance ancestors this constraint has.        A constraint with        a nonzero number of ancestors cannot be dropped nor renamed. |
| `connoinherit` `bool`                      This constraint is defined locally for the relation.  It is a        non-inheritable constraint. |
| `conkey` `int2[]`        (references [`pg_attribute`](#catalog-pg-attribute).`attnum`)                      If a table constraint (including foreign keys, but not constraint        triggers), list of the constrained columns |
| `confkey` `int2[]`        (references [`pg_attribute`](#catalog-pg-attribute).`attnum`)                      If a foreign key, list of the referenced columns |
| `conpfeqop` `oid[]`        (references [`pg_operator`](#catalog-pg-operator).`oid`)                      If a foreign key, list of the equality operators for PK = FK comparisons |
| `conppeqop` `oid[]`        (references [`pg_operator`](#catalog-pg-operator).`oid`)                      If a foreign key, list of the equality operators for PK = PK comparisons |
| `conffeqop` `oid[]`        (references [`pg_operator`](#catalog-pg-operator).`oid`)                      If a foreign key, list of the equality operators for FK = FK comparisons |
| `confdelsetcols` `int2[]`        (references [`pg_attribute`](#catalog-pg-attribute).`attnum`)                      If a foreign key with a `SET NULL` or `SET        DEFAULT` delete action, the columns that will be updated.        If null, all of the referencing columns will be updated. |
| `conexclop` `oid[]`        (references [`pg_operator`](#catalog-pg-operator).`oid`)                      If an exclusion constraint, list of the per-column exclusion operators |
| `conbin` `pg_node_tree`                      If a check constraint, an internal representation of the        expression.  (It's recommended to use        `pg_get_constraintdef()` to extract the definition of        a check constraint.) |

In the case of an exclusion constraint, `conkey`
is only useful for constraint elements that are simple column references.
For other cases, a zero appears in `conkey`
and the associated index must be consulted to discover the expression
that is constrained.  (`conkey` thus has the
same contents as [`pg_index`](#catalog-pg-index).`indkey` for the
index.)

> **Note:**

> `pg_class.relchecks` needs to agree with the
> number of check-constraint entries found in this table for each
> relation.
>

## `pg_conversion`

The catalog `pg_conversion` describes
encoding conversion functions.  See [sql-createconversion](#sql-createconversion)
for more information.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `conname` `name`                      Conversion name (unique within a namespace) |
| `connamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      The OID of the namespace that contains this conversion |
| `conowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the conversion |
| `conforencoding` `int4`                      Source encoding ID ([`pg_encoding_to_char()`](#pg-encoding-to-char)        can translate this number to the encoding name) |
| `contoencoding` `int4`                      Destination encoding ID ([`pg_encoding_to_char()`](#pg-encoding-to-char)        can translate this number to the encoding name) |
| `conproc` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Conversion function |
| `condefault` `bool`                      True if this is the default conversion |

## `pg_database`

The catalog `pg_database` stores information about
the available databases.  Databases are created with the [`CREATE DATABASE`](#sql-createdatabase) command.
Consult [managing-databases](#managing-databases) for details about the meaning
of some of the parameters.

Unlike most system catalogs, `pg_database`
is shared across all databases of a cluster: there is only one
copy of `pg_database` per cluster, not
one per database.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `datname` `name`                      Database name |
| `datdba` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the database, usually the user who created it |
| `encoding` `int4`                      Character encoding for this database        ([`pg_encoding_to_char()`](#pg-encoding-to-char) can translate        this number to the encoding name) |
| `datlocprovider` `char`                      Locale provider for this database: `c` = libc,        `i` = icu |
| `datistemplate` `bool`                      If true, then this database can be cloned by        any user with `CREATEDB` privileges;        if false, then only superusers or the owner of        the database can clone it. |
| `datallowconn` `bool`                      If false then no one can connect to this database.  This is        used to protect the `template0` database from being altered. |
| `datconnlimit` `int4`                      Sets maximum number of concurrent connections that can be made        to this database.  -1 means no limit, -2 indicates the database is        invalid. |
| `datfrozenxid` `xid`                      All transaction IDs before this one have been replaced with a permanent        ("frozen") transaction ID in this database.  This is used to        track whether the database needs to be vacuumed in order to prevent        transaction ID wraparound or to allow `pg_xact` to be shrunk.        It is the minimum of the per-table        [`pg_class`](#catalog-pg-class).`relfrozenxid` values. |
| `datminmxid` `xid`                      All multixact IDs before this one have been replaced with a        transaction ID in this database.  This is used to        track whether the database needs to be vacuumed in order to prevent        multixact ID wraparound or to allow `pg_multixact` to be shrunk.        It is the minimum of the per-table        [`pg_class`](#catalog-pg-class).`relminmxid` values. |
| `dattablespace` `oid`        (references [`pg_tablespace`](#catalog-pg-tablespace).`oid`)                      The default tablespace for the database.        Within this database, all tables for which        [`pg_class`](#catalog-pg-class).`reltablespace` is zero        will be stored in this tablespace; in particular, all the non-shared        system catalogs will be there. |
| `datcollate` `text`                      LC_COLLATE for this database |
| `datctype` `text`                      LC_CTYPE for this database |
| `daticulocale` `text`                      ICU locale ID for this database |
| `daticurules` `text`                      ICU collation rules for this database |
| `datcollversion` `text`                      Provider-specific version of the collation.  This is recorded when the        database is created and then checked when it is used, to detect        changes in the collation definition that could lead to data corruption. |
| `datacl` `aclitem[]`                      Access privileges; see [ddl-priv](#ddl-priv) for details |

## `pg_db_role_setting`

The catalog `pg_db_role_setting` records the default
values that have been set for run-time configuration variables,
for each role and database combination.

Unlike most system catalogs, `pg_db_role_setting`
is shared across all databases of a cluster: there is only one
copy of `pg_db_role_setting` per cluster, not
one per database.

| Column Type                      Description |
| --- |
| `setdatabase` `oid`        (references [`pg_database`](#catalog-pg-database).`oid`)                      The OID of the database the setting is applicable to, or zero if not database-specific |
| `setrole` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      The OID of the role the setting is applicable to, or zero if not role-specific |
| `setconfig` `text[]`                      Defaults for run-time configuration variables |

## `pg_default_acl`

The catalog `pg_default_acl` stores initial
privileges to be assigned to newly created objects.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `defaclrole` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      The OID of the role associated with this entry |
| `defaclnamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      The OID of the namespace associated with this entry,        or zero if none |
| `defaclobjtype` `char`                      Type of object this entry is for:        `r` = relation (table, view),        `S` = sequence,        `f` = function,        `T` = type,        `n` = schema |
| `defaclacl` `aclitem[]`                      Access privileges that this type of object should have on creation |

A `pg_default_acl` entry shows the initial privileges to
be assigned to an object belonging to the indicated user.  There are
currently two types of entry: "global" entries with
`defaclnamespace` = zero, and "per-schema" entries
that reference a particular schema.  If a global entry is present then
it *overrides* the normal hard-wired default privileges
for the object type.  A per-schema entry, if present, represents privileges
to be *added to* the global or hard-wired default privileges.

Note that when an ACL entry in another catalog is null, it is taken
to represent the hard-wired default privileges for its object,
*not* whatever might be in `pg_default_acl`
at the moment.  `pg_default_acl` is only consulted during
object creation.

## `pg_depend`

The catalog `pg_depend` records the dependency
relationships between database objects.  This information allows
`DROP` commands to find which other objects must be dropped
by `DROP CASCADE` or prevent dropping in the `DROP
RESTRICT` case.

See also [`pg_shdepend`](#catalog-pg-shdepend),
which performs a similar function for dependencies involving objects
that are shared across a database cluster.

| Column Type                      Description |
| --- |
| `classid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the system catalog the dependent object is in |
| `objid` `oid`        (references any OID column)                      The OID of the specific dependent object |
| `objsubid` `int4`                      For a table column, this is the column number (the        `objid` and `classid` refer to the        table itself).  For all other object types, this column is        zero. |
| `refclassid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the system catalog the referenced object is in |
| `refobjid` `oid`        (references any OID column)                      The OID of the specific referenced object |
| `refobjsubid` `int4`                      For a table column, this is the column number (the        `refobjid` and `refclassid` refer        to the table itself).  For all other object types, this column        is zero. |
| `deptype` `char`                      A code defining the specific semantics of this dependency relationship; see text |

In all cases, a `pg_depend` entry indicates that the
referenced object cannot be dropped without also dropping the dependent
object.  However, there are several subflavors identified by
`deptype`:

**`DEPENDENCY_NORMAL` (`n`)**
: A normal relationship between separately-created objects.  The
dependent object can be dropped without affecting the
referenced object.  The referenced object can only be dropped
by specifying `CASCADE`, in which case the dependent
object is dropped, too.  Example: a table column has a normal
dependency on its data type.

**`DEPENDENCY_AUTO` (`a`)**
: The dependent object can be dropped separately from the
referenced object, and should be automatically dropped
(regardless of `RESTRICT` or `CASCADE`
mode) if the referenced object is dropped.  Example: a named
constraint on a table is made auto-dependent on the table, so
that it will go away if the table is dropped.

**`DEPENDENCY_INTERNAL` (`i`)**
: The dependent object was created as part of creation of the
referenced object, and is really just a part of its internal
implementation.  A direct `DROP` of the dependent
object will be disallowed outright (we'll tell the user to issue
a `DROP` against the referenced object, instead).
A `DROP` of the referenced object will result in
automatically dropping the dependent object
whether `CASCADE` is specified or not.  If the
dependent object has to be dropped due to a dependency on some other
object being removed, its drop is converted to a drop of the referenced
object, so that `NORMAL` and `AUTO`
dependencies of the dependent object behave much like they were
dependencies of the referenced object.
Example: a view's `ON SELECT` rule is made
internally dependent on the view, preventing it from being dropped
while the view remains.  Dependencies of the rule (such as tables it
refers to) act as if they were dependencies of the view.

**`DEPENDENCY_PARTITION_PRI` (`P`)**
: The dependent object was created as part of creation of the
referenced object, and is really just a part of its internal
implementation; however, unlike `INTERNAL`,
there is more than one such referenced object.  The dependent object
must not be dropped unless at least one of these referenced objects
is dropped; if any one is, the dependent object should be dropped
whether or not `CASCADE` is specified.  Also
unlike `INTERNAL`, a drop of some other object
that the dependent object depends on does not result in automatic
deletion of any partition-referenced object.  Hence, if the drop
does not cascade to at least one of these objects via some other
path, it will be refused.  (In most cases, the dependent object
shares all its non-partition dependencies with at least one
partition-referenced object, so that this restriction does not
result in blocking any cascaded delete.)
Primary and secondary partition dependencies behave identically
except that the primary dependency is preferred for use in error
messages; hence, a partition-dependent object should have one
primary partition dependency and one or more secondary partition
dependencies.
Note that partition dependencies are made in addition to, not
instead of, any dependencies the object would normally have.  This
simplifies `ATTACH/DETACH PARTITION` operations:
the partition dependencies need only be added or removed.
Example: a child partitioned index is made partition-dependent
on both the partition table it is on and the parent partitioned
index, so that it goes away if either of those is dropped, but
not otherwise.  The dependency on the parent index is primary,
so that if the user tries to drop the child partitioned index,
the error message will suggest dropping the parent index instead
(not the table).

**`DEPENDENCY_EXTENSION` (`e`)**
: The dependent object is a member of the *extension* that is
the referenced object (see
[`pg_extension`](#catalog-pg-extension)).
The dependent object can be dropped only via
[`DROP EXTENSION`](#sql-dropextension) on the referenced object.
Functionally this dependency type acts the same as
an `INTERNAL` dependency, but it's kept separate for
clarity and to simplify pg_dump.

**`DEPENDENCY_AUTO_EXTENSION` (`x`)**
: The dependent object is not a member of the extension that is the
referenced object (and so it should not be ignored
by pg_dump), but it cannot function
without the extension and should be auto-dropped if the extension is.
The dependent object may be dropped on its own as well.
Functionally this dependency type acts the same as
an `AUTO` dependency, but it's kept separate for
clarity and to simplify pg_dump.

Other dependency flavors might be needed in future.

Note that it's quite possible for two objects to be linked by more than
one `pg_depend` entry.  For example, a child
partitioned index would have both a partition-type dependency on its
associated partition table, and an auto dependency on each column of
that table that it indexes.  This sort of situation expresses the union
of multiple dependency semantics.  A dependent object can be dropped
without `CASCADE` if any of its dependencies satisfies
its condition for automatic dropping.  Conversely, all the
dependencies' restrictions about which objects must be dropped together
must be satisfied.

Most objects created during initdb are
considered "pinned", which means that the system itself
depends on them.  Therefore, they are never allowed to be dropped.
Also, knowing that pinned objects will not be dropped, the dependency
mechanism doesn't bother to make `pg_depend`
entries showing dependencies on them.  Thus, for example, a table
column of type `numeric` notionally has
a `NORMAL` dependency on the `numeric`
data type, but no such entry actually appears
in `pg_depend`.

## `pg_description`

The catalog `pg_description` stores optional descriptions
(comments) for each database object.  Descriptions can be manipulated
with the [`COMMENT`](#sql-comment) command and viewed with
psql's `\d` commands.
Descriptions of many built-in system objects are provided in the initial
contents of `pg_description`.

See also [`pg_shdescription`](#catalog-pg-shdescription),
which performs a similar function for descriptions involving objects that
are shared across a database cluster.

| Column Type                      Description |
| --- |
| `objoid` `oid`        (references any OID column)                      The OID of the object this description pertains to |
| `classoid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the system catalog this object appears in |
| `objsubid` `int4`                      For a comment on a table column, this is the column number (the        `objoid` and `classoid` refer to        the table itself).  For all other object types, this column is        zero. |
| `description` `text`                      Arbitrary text that serves as the description of this object |

## `pg_enum`

The `pg_enum` catalog contains entries
showing the values and labels for each enum type. The
internal representation of a given enum value is actually the OID
of its associated row in `pg_enum`.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `enumtypid` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      The OID of the [`pg_type`](#catalog-pg-type) entry owning this enum value |
| `enumsortorder` `float4`                      The sort position of this enum value within its enum type |
| `enumlabel` `name`                      The textual label for this enum value |

The OIDs for `pg_enum` rows follow a special
rule: even-numbered OIDs are guaranteed to be ordered in the same way
as the sort ordering of their enum type.  That is, if two even OIDs
belong to the same enum type, the smaller OID must have the smaller
`enumsortorder` value.  Odd-numbered OID values
need bear no relationship to the sort order.  This rule allows the
enum comparison routines to avoid catalog lookups in many common cases.
The routines that create and alter enum types attempt to assign even
OIDs to enum values whenever possible.

When an enum type is created, its members are assigned sort-order
positions 1..`n`.  But members added later might be given
negative or fractional values of `enumsortorder`.
The only requirement on these values is that they be correctly
ordered and unique within each enum type.

## `pg_event_trigger`

The catalog `pg_event_trigger` stores event triggers.
See [event-triggers](#event-triggers) for more information.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `evtname` `name`                      Trigger name (must be unique) |
| `evtevent` `name`                      Identifies the event for which this trigger fires |
| `evtowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the event trigger |
| `evtfoid` `oid`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      The function to be called |
| `evtenabled` `char`                      Controls in which [guc-session-replication-role](#guc-session-replication-role) modes        the event trigger fires.        `O` = trigger fires in "origin" and "local" modes,        `D` = trigger is disabled,        `R` = trigger fires in "replica" mode,        `A` = trigger fires always. |
| `evttags` `text[]`                      Command tags for which this trigger will fire.  If NULL, the firing        of this trigger is not restricted on the basis of the command tag. |

## `pg_extension`

The catalog `pg_extension` stores information
about the installed extensions.  See [extend-extensions](#extend-extensions)
for details about extensions.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `extname` `name`                      Name of the extension |
| `extowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the extension |
| `extnamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      Schema containing the extension's exported objects |
| `extrelocatable` `bool`                      True if extension can be relocated to another schema |
| `extversion` `text`                      Version name for the extension |
| `extconfig` `oid[]`        (references [`pg_class`](#catalog-pg-class).`oid`)                      Array of `regclass` OIDs for the extension's configuration        table(s), or `NULL` if none |
| `extcondition` `text[]`                      Array of `WHERE`-clause filter conditions for the        extension's configuration table(s), or `NULL` if none |

Note that unlike most catalogs with a "namespace" column,
`extnamespace` is not meant to imply
that the extension belongs to that schema.  Extension names are never
schema-qualified.  Rather, `extnamespace`
indicates the schema that contains most or all of the extension's
objects.  If `extrelocatable` is true, then
this schema must in fact contain all schema-qualifiable objects
belonging to the extension.

## `pg_foreign_data_wrapper`

The catalog `pg_foreign_data_wrapper` stores
foreign-data wrapper definitions.  A foreign-data wrapper is the
mechanism by which external data, residing on foreign servers, is
accessed.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `fdwname` `name`                      Name of the foreign-data wrapper |
| `fdwowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the foreign-data wrapper |
| `fdwhandler` `oid`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      References a handler function that is responsible for        supplying execution routines for the foreign-data wrapper.        Zero if no handler is provided |
| `fdwvalidator` `oid`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      References a validator function that is responsible for        checking the validity of the options given to the        foreign-data wrapper, as well as options for foreign servers and user        mappings using the foreign-data wrapper.  Zero if no validator        is provided |
| `fdwacl` `aclitem[]`                      Access privileges; see [ddl-priv](#ddl-priv) for details |
| `fdwoptions` `text[]`                      Foreign-data wrapper specific options, as "keyword=value" strings |

## `pg_foreign_server`

The catalog `pg_foreign_server` stores
foreign server definitions.  A foreign server describes a source
of external data, such as a remote server.  Foreign
servers are accessed via foreign-data wrappers.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `srvname` `name`                      Name of the foreign server |
| `srvowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the foreign server |
| `srvfdw` `oid`        (references [`pg_foreign_data_wrapper`](#catalog-pg-foreign-data-wrapper).`oid`)                      OID of the foreign-data wrapper of this foreign server |
| `srvtype` `text`                      Type of the server (optional) |
| `srvversion` `text`                      Version of the server (optional) |
| `srvacl` `aclitem[]`                      Access privileges; see [ddl-priv](#ddl-priv) for details |
| `srvoptions` `text[]`                      Foreign server specific options, as "keyword=value" strings |

## `pg_foreign_table`

The catalog `pg_foreign_table` contains
auxiliary information about foreign tables.  A foreign table is
primarily represented by a
[`pg_class`](#catalog-pg-class)
entry, just like a regular table.  Its `pg_foreign_table`
entry contains the information that is pertinent only to foreign tables
and not any other kind of relation.

| Column Type                      Description |
| --- |
| `ftrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the [`pg_class`](#catalog-pg-class) entry for this foreign table |
| `ftserver` `oid`        (references [`pg_foreign_server`](#catalog-pg-foreign-server).`oid`)                      OID of the foreign server for this foreign table |
| `ftoptions` `text[]`                      Foreign table options, as "keyword=value" strings |

## `pg_index`

The catalog `pg_index` contains part of the information
about indexes.  The rest is mostly in
[`pg_class`](#catalog-pg-class).

| Column Type                      Description |
| --- |
| `indexrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the [`pg_class`](#catalog-pg-class) entry for this index |
| `indrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the [`pg_class`](#catalog-pg-class) entry for the table this index is for |
| `indnatts` `int2`                      The total number of columns in the index (duplicates        `pg_class.relnatts`); this number includes both key and included attributes |
| `indnkeyatts` `int2`                      The number of *key columns* in the index,        not counting any *included columns*, which are        merely stored and do not participate in the index semantics |
| `indisunique` `bool`                      If true, this is a unique index |
| `indnullsnotdistinct` `bool`                      This value is only used for unique indexes.  If false, this unique        index will consider null values distinct (so the index can contain        multiple null values in a column, the default PostgreSQL behavior).  If        it is true, it will consider null values to be equal (so the index can        only contain one null value in a column). |
| `indisprimary` `bool`                      If true, this index represents the primary key of the table        (`indisunique` should always be true when this is true) |
| `indisexclusion` `bool`                      If true, this index supports an exclusion constraint |
| `indimmediate` `bool`                      If true, the uniqueness check is enforced immediately on        insertion        (irrelevant if `indisunique` is not true) |
| `indisclustered` `bool`                      If true, the table was last clustered on this index |
| `indisvalid` `bool`                      If true, the index is currently valid for queries.  False means the        index is possibly incomplete: it must still be modified by        [`INSERT`](#sql-insert)/[`UPDATE`](#sql-update) operations, but it cannot safely        be used for queries. If it is unique, the uniqueness property is not        guaranteed true either. |
| `indcheckxmin` `bool`                      If true, queries must not use the index until the `xmin`        of this `pg_index` row is below their `TransactionXmin`        event horizon, because the table may contain broken [HOT chains](#storage-hot) with        incompatible rows that they can see |
| `indisready` `bool`                      If true, the index is currently ready for inserts.  False means the        index must be ignored by [`INSERT`](#sql-insert)/[`UPDATE`](#sql-update)        operations. |
| `indislive` `bool`                      If false, the index is in process of being dropped, and should be        ignored for all purposes (including HOT-safety decisions) |
| `indisreplident` `bool`                      If true this index has been chosen as "replica identity"        using [`ALTER TABLE ...        REPLICA IDENTITY USING INDEX ...`](#sql-altertable-replica-identity) |
| `indkey` `int2vector`        (references [`pg_attribute`](#catalog-pg-attribute).`attnum`)                      This is an array of `indnatts` values that        indicate which table columns this index indexes.  For example, a value        of `1 3` would mean that the first and the third table        columns make up the index entries.  Key columns come before non-key        (included) columns.  A zero in this array indicates that the        corresponding index attribute is an expression over the table columns,        rather than a simple column reference. |
| `indcollation` `oidvector`        (references [`pg_collation`](#catalog-pg-collation).`oid`)                      For each column in the index key        (`indnkeyatts` values), this contains the OID        of the collation to use for the index, or zero if the column is not of        a collatable data type. |
| `indclass` `oidvector`        (references [`pg_opclass`](#catalog-pg-opclass).`oid`)                      For each column in the index key        (`indnkeyatts` values), this contains the OID        of the operator class to use.  See        [`pg_opclass`](#catalog-pg-opclass) for details. |
| `indoption` `int2vector`                      This is an array of `indnkeyatts` values that        store per-column flag bits.  The meaning of the bits is defined by        the index's access method. |
| `indexprs` `pg_node_tree`                      Expression trees (in `nodeToString()`        representation) for index attributes that are not simple column        references.  This is a list with one element for each zero        entry in `indkey`.  Null if all index attributes        are simple references. |
| `indpred` `pg_node_tree`                      Expression tree (in `nodeToString()`        representation) for partial index predicate.  Null if not a        partial index. |

## `pg_inherits`

The catalog `pg_inherits` records information about
table and index inheritance hierarchies.  There is one entry for each direct
parent-child table or index relationship in the database.  (Indirect
inheritance can be determined by following chains of entries.)

| Column Type                      Description |
| --- |
| `inhrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the child table or index |
| `inhparent` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the parent table or index |
| `inhseqno` `int4`                      If there is more than one direct parent for a child table (multiple        inheritance), this number tells the order in which the        inherited columns are to be arranged.  The count starts at 1.                      Indexes cannot have multiple inheritance, since they can only inherit        when using declarative partitioning. |
| `inhdetachpending` `bool`                      `true` for a partition that is in the process of        being detached; `false` otherwise. |

## `pg_init_privs`

The catalog `pg_init_privs` records information about
the initial privileges of objects in the system.  There is one entry
for each object in the database which has a non-default (non-NULL)
initial set of privileges.

Objects can have initial privileges either by having those privileges set
when the system is initialized (by initdb) or when the
object is created during a [`CREATE EXTENSION`](#sql-createextension) and the
extension script sets initial privileges using the [`GRANT`](#sql-grant)
system.  Note that the system will automatically handle recording of the
privileges during the extension script and that extension authors need
only use the `GRANT` and `REVOKE`
statements in their script to have the privileges recorded.  The
`privtype` column indicates if the initial privilege was
set by initdb or during a
`CREATE EXTENSION` command.

Objects which have initial privileges set by initdb will
have entries where `privtype` is
`'i'`, while objects which have initial privileges set
by `CREATE EXTENSION` will have entries where
`privtype` is `'e'`.

| Column Type                      Description |
| --- |
| `objoid` `oid`        (references any OID column)                      The OID of the specific object |
| `classoid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the system catalog the object is in |
| `objsubid` `int4`                      For a table column, this is the column number (the        `objoid` and `classoid` refer to the        table itself).  For all other object types, this column is        zero. |
| `privtype` `char`                      A code defining the type of initial privilege of this object; see text |
| `initprivs` `aclitem[]`                      The initial access privileges; see        [ddl-priv](#ddl-priv) for details |

## `pg_language`

The catalog `pg_language` registers
languages in which you can write functions or stored procedures.
See [sql-createlanguage](#sql-createlanguage)
and [xplang](#xplang) for more information about language handlers.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `lanname` `name`                      Name of the language |
| `lanowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the language |
| `lanispl` `bool`                      This is false for internal languages (such as        SQL) and true for user-defined languages.        Currently, pg_dump still uses this        to determine which languages need to be dumped, but this might be        replaced by a different mechanism in the future. |
| `lanpltrusted` `bool`                      True if this is a trusted language, which means that it is believed        not to grant access to anything outside the normal SQL execution        environment.  Only superusers can create functions in untrusted        languages. |
| `lanplcallfoid` `oid`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      For noninternal languages this references the language        handler, which is a special function that is responsible for        executing all functions that are written in the particular        language. Zero for internal languages. |
| `laninline` `oid`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      This references a function that is responsible for executing        "inline" anonymous code blocks        ([sql-do](#sql-do) blocks).        Zero if inline blocks are not supported. |
| `lanvalidator` `oid`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      This references a language validator function that is responsible        for checking the syntax and validity of new functions when they        are created.  Zero if no validator is provided. |
| `lanacl` `aclitem[]`                      Access privileges; see [ddl-priv](#ddl-priv) for details |

## `pg_largeobject`

The catalog `pg_largeobject` holds the data making up
"large objects".  A large object is identified by an OID
assigned when it is created.  Each large object is broken into
segments or "pages" small enough to be conveniently stored as rows
in `pg_largeobject`.
The amount of data per page is defined to be `LOBLKSIZE` (which is currently
`BLCKSZ/4`, or typically 2 kB).

Prior to PostgreSQL 9.0, there was no permission structure
associated with large objects.  As a result,
`pg_largeobject` was publicly readable and could be
used to obtain the OIDs (and contents) of all large objects in the system.
This is no longer the case; use
[`pg_largeobject_metadata`](#catalog-pg-largeobject-metadata)
to obtain a list of large object OIDs.

| Column Type                      Description |
| --- |
| `loid` `oid`        (references [`pg_largeobject_metadata`](#catalog-pg-largeobject-metadata).`oid`)                      Identifier of the large object that includes this page |
| `pageno` `int4`                      Page number of this page within its large object        (counting from zero) |
| `data` `bytea`                      Actual data stored in the large object.        This will never be more than `LOBLKSIZE` bytes and might be less. |

Each row of `pg_largeobject` holds data
for one page of a large object, beginning at
byte offset (`pageno * LOBLKSIZE`) within the object.  The implementation
allows sparse storage: pages might be missing, and might be shorter than
`LOBLKSIZE` bytes even if they are not the last page of the object.
Missing regions within a large object read as zeroes.

## `pg_largeobject_metadata`

The catalog `pg_largeobject_metadata`
holds metadata associated with large objects.  The actual large object
data is stored in
[`pg_largeobject`](#catalog-pg-largeobject).

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `lomowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the large object |
| `lomacl` `aclitem[]`                      Access privileges; see [ddl-priv](#ddl-priv) for details |

## `pg_namespace`

The catalog `pg_namespace` stores namespaces.
A namespace is the structure underlying SQL schemas: each namespace
can have a separate collection of relations, types, etc. without name
conflicts.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `nspname` `name`                      Name of the namespace |
| `nspowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the namespace |
| `nspacl` `aclitem[]`                      Access privileges; see [ddl-priv](#ddl-priv) for details |

## `pg_opclass`

The catalog `pg_opclass` defines
index access method operator classes.  Each operator class defines
semantics for index columns of a particular data type and a particular
index access method.  An operator class essentially specifies that a
particular operator family is applicable to a particular indexable column
data type.  The set of operators from the family that are actually usable
with the indexed column are whichever ones accept the column's data type
as their left-hand input.

Operator classes are described at length in [xindex](#xindex).

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `opcmethod` `oid`        (references [`pg_am`](#catalog-pg-am).`oid`)                      Index access method operator class is for |
| `opcname` `name`                      Name of this operator class |
| `opcnamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      Namespace of this operator class |
| `opcowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the operator class |
| `opcfamily` `oid`        (references [`pg_opfamily`](#catalog-pg-opfamily).`oid`)                      Operator family containing the operator class |
| `opcintype` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Data type that the operator class indexes |
| `opcdefault` `bool`                      True if this operator class is the default for `opcintype` |
| `opckeytype` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Type of data stored in index, or zero if same as `opcintype` |

An operator class's `opcmethod` must match the
`opfmethod` of its containing operator family.
Also, there must be no more than one `pg_opclass`
row having `opcdefault` true for any given combination of
`opcmethod` and `opcintype`.

## `pg_operator`

The catalog `pg_operator` stores information about operators.
See [sql-createoperator](#sql-createoperator)
and [xoper](#xoper) for more information.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `oprname` `name`                      Name of the operator |
| `oprnamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      The OID of the namespace that contains this operator |
| `oprowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the operator |
| `oprkind` `char`                      `b` = infix operator ("both"),        or `l` = prefix operator ("left") |
| `oprcanmerge` `bool`                      This operator supports merge joins |
| `oprcanhash` `bool`                      This operator supports hash joins |
| `oprleft` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Type of the left operand (zero for a prefix operator) |
| `oprright` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Type of the right operand |
| `oprresult` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Type of the result        (zero for a not-yet-defined "shell" operator) |
| `oprcom` `oid`        (references [`pg_operator`](#catalog-pg-operator).`oid`)                      Commutator of this operator (zero if none) |
| `oprnegate` `oid`        (references [`pg_operator`](#catalog-pg-operator).`oid`)                      Negator of this operator (zero if none) |
| `oprcode` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Function that implements this operator        (zero for a not-yet-defined "shell" operator) |
| `oprrest` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Restriction selectivity estimation function for this operator        (zero if none) |
| `oprjoin` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Join selectivity estimation function for this operator        (zero if none) |

## `pg_opfamily`

The catalog `pg_opfamily` defines operator families.
Each operator family is a collection of operators and associated
support routines that implement the semantics specified for a particular
index access method.  Furthermore, the operators in a family are all
"compatible", in a way that is specified by the access method.
The operator family concept allows cross-data-type operators to be used
with indexes and to be reasoned about using knowledge of access method
semantics.

Operator families are described at length in [xindex](#xindex).

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `opfmethod` `oid`        (references [`pg_am`](#catalog-pg-am).`oid`)                      Index access method operator family is for |
| `opfname` `name`                      Name of this operator family |
| `opfnamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      Namespace of this operator family |
| `opfowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the operator family |

The majority of the information defining an operator family is not in its
`pg_opfamily` row, but in the associated rows in
[`pg_amop`](#catalog-pg-amop),
[`pg_amproc`](#catalog-pg-amproc),
and
[`pg_opclass`](#catalog-pg-opclass).

## `pg_parameter_acl`

The catalog `pg_parameter_acl` records configuration
parameters for which privileges have been granted to one or more roles.
No entry is made for parameters that have default privileges.

Unlike most system catalogs, `pg_parameter_acl`
is shared across all databases of a cluster: there is only one
copy of `pg_parameter_acl` per cluster, not
one per database.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `parname` `text`                      The name of a configuration parameter for which privileges are granted |
| `paracl` `aclitem[]`                      Access privileges; see [ddl-priv](#ddl-priv) for details |

## `pg_partitioned_table`

The catalog `pg_partitioned_table` stores
information about how tables are partitioned.

| Column Type                      Description |
| --- |
| `partrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the [`pg_class`](#catalog-pg-class) entry for this partitioned table |
| `partstrat` `char`                      Partitioning strategy; `h` = hash partitioned table,        `l` = list partitioned table, `r` = range partitioned table |
| `partnatts` `int2`                      The number of columns in the partition key |
| `partdefid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the [`pg_class`](#catalog-pg-class) entry for the default partition        of this partitioned table, or zero if this partitioned table does not        have a default partition |
| `partattrs` `int2vector`        (references [`pg_attribute`](#catalog-pg-attribute).`attnum`)                      This is an array of `partnatts` values that        indicate which table columns are part of the partition key.  For        example, a value of `1 3` would mean that the first        and the third table columns make up the partition key.  A zero in this        array indicates that the corresponding partition key column is an        expression, rather than a simple column reference. |
| `partclass` `oidvector`        (references [`pg_opclass`](#catalog-pg-opclass).`oid`)                      For each column in the partition key, this contains the OID of the        operator class to use.  See        [`pg_opclass`](#catalog-pg-opclass) for details. |
| `partcollation` `oidvector`        (references [`pg_collation`](#catalog-pg-collation).`oid`)                      For each column in the partition key, this contains the OID of the        collation to use for partitioning, or zero if the column is not        of a collatable data type. |
| `partexprs` `pg_node_tree`                      Expression trees (in `nodeToString()`        representation) for partition key columns that are not simple column        references.  This is a list with one element for each zero        entry in `partattrs`.  Null if all partition key columns        are simple references. |

## `pg_policy`

The catalog `pg_policy` stores row-level
security policies for tables.  A policy includes the kind of
command that it applies to (possibly all commands), the roles that it
applies to, the expression to be added as a security-barrier
qualification to queries that include the table, and the expression
to be added as a `WITH CHECK` option for queries that attempt to
add new records to the table.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `polname` `name`                      The name of the policy |
| `polrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The table to which the policy applies |
| `polcmd` `char`                      The command type to which the policy is applied:        `r` for [sql-select](#sql-select),        `a` for [sql-insert](#sql-insert),        `w` for [sql-update](#sql-update),        `d` for [sql-delete](#sql-delete),        or `*` for all |
| `polpermissive` `bool`                      Is the policy permissive or restrictive? |
| `polroles` `oid[]`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      The roles to which the policy is applied;        zero means `PUBLIC`        (and normally appears alone in the array) |
| `polqual` `pg_node_tree`                      The expression tree to be added to the security barrier qualifications for queries that use the table |
| `polwithcheck` `pg_node_tree`                      The expression tree to be added to the WITH CHECK qualifications for queries that attempt to add rows to the table |

> **Note:**

> Policies stored in `pg_policy` are applied only when
> [`pg_class`](#catalog-pg-class).`relrowsecurity` is set for
> their table.
>

## `pg_proc`

The catalog `pg_proc` stores information about
functions, procedures, aggregate functions, and window functions
(collectively also known as routines).  See [sql-createfunction](#sql-createfunction), [sql-createprocedure](#sql-createprocedure), and
[xfunc](#xfunc) for more information.

If `prokind` indicates that the entry is for an
aggregate function, there should be a matching row in
[`pg_aggregate`](#catalog-pg-aggregate).

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `proname` `name`                      Name of the function |
| `pronamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      The OID of the namespace that contains this function |
| `proowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the function |
| `prolang` `oid`        (references [`pg_language`](#catalog-pg-language).`oid`)                      Implementation language or call interface of this function |
| `procost` `float4`                      Estimated execution cost (in units of        [guc-cpu-operator-cost](#guc-cpu-operator-cost)); if `proretset`,        this is cost per row returned |
| `prorows` `float4`                      Estimated number of result rows (zero if not `proretset`) |
| `provariadic` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Data type of the variadic array parameter's elements,        or zero if the function does not have a variadic parameter |
| `prosupport` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Planner support function for this function        (see [xfunc-optimization](#xfunc-optimization)), or zero if none |
| `prokind` `char`                      `f` for a normal function, `p`        for a procedure, `a` for an aggregate function, or        `w` for a window function |
| `prosecdef` `bool`                      Function is a security definer (i.e., a "setuid"        function) |
| `proleakproof` `bool`                      The function has no side effects.  No information about the        arguments is conveyed except via the return value.  Any function        that might throw an error depending on the values of its arguments        is not leak-proof. |
| `proisstrict` `bool`                      Function returns null if any call argument is null.  In that        case the function won't actually be called at all.  Functions        that are not "strict" must be prepared to handle        null inputs. |
| `proretset` `bool`                      Function returns a set (i.e., multiple values of the specified        data type) |
| `provolatile` `char`                      `provolatile` tells whether the function's        result depends only on its input arguments, or is affected by outside        factors.        It is `i` for "immutable" functions,        which always deliver the same result for the same inputs.        It is `s` for "stable" functions,        whose results (for fixed inputs) do not change within a scan.        It is `v` for "volatile" functions,        whose results might change at any time.  (Use `v` also        for functions with side-effects, so that calls to them cannot get        optimized away.) |
| `proparallel` `char`                      `proparallel` tells whether the function        can be safely run in parallel mode.        It is `s` for functions which are safe to run in        parallel mode without restriction.        It is `r` for functions which can be run in parallel        mode, but their execution is restricted to the parallel group leader;        parallel worker processes cannot invoke these functions.        It is `u` for functions which are unsafe in parallel        mode; the presence of such a function forces a serial execution plan. |
| `pronargs` `int2`                      Number of input arguments |
| `pronargdefaults` `int2`                      Number of arguments that have defaults |
| `prorettype` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Data type of the return value |
| `proargtypes` `oidvector`        (references [`pg_type`](#catalog-pg-type).`oid`)                      An array of the data types of the function arguments.  This includes        only input arguments (including `INOUT` and        `VARIADIC` arguments), and thus represents        the call signature of the function. |
| `proallargtypes` `oid[]`        (references [`pg_type`](#catalog-pg-type).`oid`)                      An array of the data types of the function arguments.  This includes        all arguments (including `OUT` and        `INOUT` arguments); however, if all the        arguments are `IN` arguments, this field will be null.        Note that subscripting is 1-based, whereas for historical reasons        `proargtypes` is subscripted from 0. |
| `proargmodes` `char[]`                      An array of the modes of the function arguments, encoded as        `i` for `IN` arguments,        `o` for `OUT` arguments,        `b` for `INOUT` arguments,        `v` for `VARIADIC` arguments,        `t` for `TABLE` arguments.        If all the arguments are `IN` arguments,        this field will be null.        Note that subscripts correspond to positions of        `proallargtypes` not `proargtypes`. |
| `proargnames` `text[]`                      An array of the names of the function arguments.        Arguments without a name are set to empty strings in the array.        If none of the arguments have a name, this field will be null.        Note that subscripts correspond to positions of        `proallargtypes` not `proargtypes`. |
| `proargdefaults` `pg_node_tree`                      Expression trees (in `nodeToString()` representation)        for default values.  This is a list with        `pronargdefaults` elements, corresponding to the last        `N` *input* arguments (i.e., the last        `N` `proargtypes` positions).        If none of the arguments have defaults, this field will be null. |
| `protrftypes` `oid[]`        (references [`pg_type`](#catalog-pg-type).`oid`)                      An array of the argument/result data type(s) for which to apply        transforms (from the function's `TRANSFORM`        clause).  Null if none. |
| `prosrc` `text`                      This tells the function handler how to invoke the function.  It        might be the actual source code of the function for interpreted        languages, a link symbol, a file name, or just about anything        else, depending on the implementation language/call convention. |
| `probin` `text`                      Additional information about how to invoke the function.        Again, the interpretation is language-specific. |
| `prosqlbody` `pg_node_tree`                      Pre-parsed SQL function body.  This is used for SQL-language        functions when the body is given in SQL-standard notation        rather than as a string literal.  It's null in other cases. |
| `proconfig` `text[]`                      Function's local settings for run-time configuration variables |
| `proacl` `aclitem[]`                      Access privileges; see [ddl-priv](#ddl-priv) for details |

For compiled functions, both built-in and dynamically loaded,
`prosrc` contains the function's C-language
name (link symbol).
For SQL-language functions, `prosrc` contains
the function's source text if that is specified as a string literal;
but if the function body is specified in SQL-standard style,
`prosrc` is unused (typically it's an empty
string) and `prosqlbody` contains the
pre-parsed definition.
For all other currently-known language types,
`prosrc` contains the function's source
text.  `probin` is null except for
dynamically-loaded C functions, for which it gives the name of the
shared library file containing the function.

## `pg_publication`

The catalog `pg_publication` contains all
publications created in the database.  For more on publications see
[logical-replication-publication](#logical-replication-publication).

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `pubname` `name`                      Name of the publication |
| `pubowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the publication |
| `puballtables` `bool`                      If true, this publication automatically includes all tables        in the database, including any that will be created in the future. |
| `pubinsert` `bool`                      If true, [sql-insert](#sql-insert) operations are replicated for        tables in the publication. |
| `pubupdate` `bool`                      If true, [sql-update](#sql-update) operations are replicated for        tables in the publication. |
| `pubdelete` `bool`                      If true, [sql-delete](#sql-delete) operations are replicated for        tables in the publication. |
| `pubtruncate` `bool`                      If true, [sql-truncate](#sql-truncate) operations are replicated for        tables in the publication. |
| `pubviaroot` `bool`                      If true, operations on a leaf partition are replicated using the        identity and schema of its topmost partitioned ancestor mentioned in the        publication instead of its own. |

## `pg_publication_namespace`

The catalog `pg_publication_namespace` contains the
mapping between schemas and publications in the database.  This is a
many-to-many mapping.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `pnpubid` `oid`        (references [`pg_publication`](#catalog-pg-publication).`oid`)                      Reference to publication |
| `pnnspid` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      Reference to schema |

## `pg_publication_rel`

The catalog `pg_publication_rel` contains the
mapping between relations and publications in the database.  This is a
many-to-many mapping.  See also [view-pg-publication-tables](#view-pg-publication-tables)
for a more user-friendly view of this information.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `prpubid` `oid`        (references [`pg_publication`](#catalog-pg-publication).`oid`)                      Reference to publication |
| `prrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      Reference to relation |
| `prqual` `pg_node_tree`              Expression tree (in `nodeToString()`       representation) for the relation's publication qualifying condition. Null       if there is no publication qualifying condition. |
| `prattrs` `int2vector`        (references [`pg_attribute`](#catalog-pg-attribute).`attnum`)                      This is an array of values that indicates which table columns are        part of the publication.  For example, a value of `1 3`        would mean that the first and the third table columns are published.        A null value indicates that all columns are published. |

## `pg_range`

The catalog `pg_range` stores information about
range types.  This is in addition to the types' entries in
[`pg_type`](#catalog-pg-type).

| Column Type                      Description |
| --- |
| `rngtypid` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      OID of the range type |
| `rngsubtype` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      OID of the element type (subtype) of this range type |
| `rngmultitypid` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      OID of the multirange type for this range type |
| `rngcollation` `oid`        (references [`pg_collation`](#catalog-pg-collation).`oid`)                      OID of the collation used for range comparisons, or zero if none |
| `rngsubopc` `oid`        (references [`pg_opclass`](#catalog-pg-opclass).`oid`)                      OID of the subtype's operator class used for range comparisons |
| `rngcanonical` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      OID of the function to convert a range value into canonical form,        or zero if none |
| `rngsubdiff` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      OID of the function to return the difference between two element        values as `double precision`, or zero if none |

`rngsubopc` (plus `rngcollation`, if the
element type is collatable) determines the sort ordering used by the range
type.  `rngcanonical` is used when the element type is
discrete.  `rngsubdiff` is optional but should be supplied to
improve performance of GiST indexes on the range type.

## `pg_replication_origin`

The `pg_replication_origin` catalog contains
all replication origins created.  For more on replication origins
see [replication-origins](#replication-origins).

Unlike most system catalogs, `pg_replication_origin`
is shared across all databases of a cluster: there is only one copy
of `pg_replication_origin` per cluster, not one per
database.

| Column Type                      Description |
| --- |
| `roident` `oid`                      A unique, cluster-wide identifier for the replication        origin. Should never leave the system. |
| `roname` `text`                      The external, user defined, name of a replication        origin. |

## `pg_rewrite`

The catalog `pg_rewrite` stores rewrite rules for tables and views.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `rulename` `name`                      Rule name |
| `ev_class` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The table this rule is for |
| `ev_type` `char`                      Event type that the rule is for: 1 = [sql-select](#sql-select), 2 =        [sql-update](#sql-update), 3 = [sql-insert](#sql-insert), 4 =        [sql-delete](#sql-delete) |
| `ev_enabled` `char`                      Controls in which [guc-session-replication-role](#guc-session-replication-role) modes        the rule fires.        `O` = rule fires in "origin" and "local" modes,        `D` = rule is disabled,        `R` = rule fires in "replica" mode,        `A` = rule fires always. |
| `is_instead` `bool`                      True if the rule is an `INSTEAD` rule |
| `ev_qual` `pg_node_tree`                      Expression tree (in the form of a        `nodeToString()` representation) for the        rule's qualifying condition |
| `ev_action` `pg_node_tree`                      Query tree (in the form of a        `nodeToString()` representation) for the        rule's action |

> **Note:**

> `pg_class.relhasrules`
> must be true if a table has any rules in this catalog.
>

## `pg_seclabel`

The catalog `pg_seclabel` stores security
labels on database objects.  Security labels can be manipulated
with the [`SECURITY LABEL`](#sql-security-label) command.  For an easier
way to view security labels, see [view-pg-seclabels](#view-pg-seclabels).

See also [`pg_shseclabel`](#catalog-pg-shseclabel),
which performs a similar function for security labels of database objects
that are shared across a database cluster.

| Column Type                      Description |
| --- |
| `objoid` `oid`        (references any OID column)                      The OID of the object this security label pertains to |
| `classoid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the system catalog this object appears in |
| `objsubid` `int4`                      For a security label on a table column, this is the column number (the        `objoid` and `classoid` refer to        the table itself).  For all other object types, this column is        zero. |
| `provider` `text`                      The label provider associated with this label. |
| `label` `text`                      The security label applied to this object. |

## `pg_sequence`

The catalog `pg_sequence` contains information about
sequences.  Some of the information about sequences, such as the name and
the schema, is in
[`pg_class`](#catalog-pg-class)

| Column Type                      Description |
| --- |
| `seqrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the [`pg_class`](#catalog-pg-class) entry for this sequence |
| `seqtypid` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      Data type of the sequence |
| `seqstart` `int8`                      Start value of the sequence |
| `seqincrement` `int8`                      Increment value of the sequence |
| `seqmax` `int8`                      Maximum value of the sequence |
| `seqmin` `int8`                      Minimum value of the sequence |
| `seqcache` `int8`                      Cache size of the sequence |
| `seqcycle` `bool`                      Whether the sequence cycles |

## `pg_shdepend`

The catalog `pg_shdepend` records the
dependency relationships between database objects and shared objects,
such as roles.  This information allows
PostgreSQL to ensure that those objects are
unreferenced before attempting to delete them.

See also [`pg_depend`](#catalog-pg-depend),
which performs a similar function for dependencies involving objects
within a single database.

Unlike most system catalogs, `pg_shdepend`
is shared across all databases of a cluster: there is only one
copy of `pg_shdepend` per cluster, not
one per database.

| Column Type                      Description |
| --- |
| `dbid` `oid`        (references [`pg_database`](#catalog-pg-database).`oid`)                      The OID of the database the dependent object is in,        or zero for a shared object |
| `classid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the system catalog the dependent object is in |
| `objid` `oid`        (references any OID column)                      The OID of the specific dependent object |
| `objsubid` `int4`                      For a table column, this is the column number (the        `objid` and `classid` refer to the        table itself).  For all other object types, this column is zero. |
| `refclassid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the system catalog the referenced object is in        (must be a shared catalog) |
| `refobjid` `oid`        (references any OID column)                      The OID of the specific referenced object |
| `deptype` `char`                      A code defining the specific semantics of this dependency relationship; see text |

In all cases, a `pg_shdepend` entry indicates that
the referenced object cannot be dropped without also dropping the dependent
object.  However, there are several subflavors identified by
`deptype`:

**`SHARED_DEPENDENCY_OWNER` (`o`)**
: The referenced object (which must be a role) is the owner of the
dependent object.

**`SHARED_DEPENDENCY_ACL` (`a`)**
: The referenced object (which must be a role) is mentioned in the
ACL (access control list, i.e., privileges list) of the
dependent object.  (A `SHARED_DEPENDENCY_ACL` entry is
not made for the owner of the object, since the owner will have
a `SHARED_DEPENDENCY_OWNER` entry anyway.)

**`SHARED_DEPENDENCY_POLICY` (`r`)**
: The referenced object (which must be a role) is mentioned as the
target of a dependent policy object.

**`SHARED_DEPENDENCY_TABLESPACE` (`t`)**
: The referenced object (which must be a tablespace) is mentioned as
the tablespace for a relation that doesn't have storage.

Other dependency flavors might be needed in future.  Note in particular
that the current definition only supports roles and tablespaces as referenced
objects.

As in the `pg_depend` catalog, most objects
created during initdb are
considered "pinned".  No entries are made
in `pg_shdepend` that would have a pinned
object as either referenced or dependent object.

## `pg_shdescription`

The catalog `pg_shdescription` stores optional
descriptions (comments) for shared database objects.  Descriptions can be
manipulated with the [`COMMENT`](#sql-comment) command and viewed with
psql's `\d` commands.

See also [`pg_description`](#catalog-pg-description),
which performs a similar function for descriptions involving objects
within a single database.

Unlike most system catalogs, `pg_shdescription`
is shared across all databases of a cluster: there is only one
copy of `pg_shdescription` per cluster, not
one per database.

| Column Type                      Description |
| --- |
| `objoid` `oid`        (references any OID column)                      The OID of the object this description pertains to |
| `classoid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the system catalog this object appears in |
| `description` `text`                      Arbitrary text that serves as the description of this object |

## `pg_shseclabel`

The catalog `pg_shseclabel` stores security
labels on shared database objects.  Security labels can be manipulated
with the [`SECURITY LABEL`](#sql-security-label) command.  For an easier
way to view security labels, see [view-pg-seclabels](#view-pg-seclabels).

See also [`pg_seclabel`](#catalog-pg-seclabel),
which performs a similar function for security labels involving objects
within a single database.

Unlike most system catalogs, `pg_shseclabel`
is shared across all databases of a cluster: there is only one
copy of `pg_shseclabel` per cluster, not
one per database.

| Column Type                      Description |
| --- |
| `objoid` `oid`        (references any OID column)                      The OID of the object this security label pertains to |
| `classoid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The OID of the system catalog this object appears in |
| `provider` `text`                      The label provider associated with this label. |
| `label` `text`                      The security label applied to this object. |

## `pg_statistic`

The catalog `pg_statistic` stores
statistical data about the contents of the database.  Entries are
created by [`ANALYZE`](#sql-analyze)
and subsequently used by the query planner.  Note that all the
statistical data is inherently approximate, even assuming that it
is up-to-date.

Normally there is one entry, with `stainherit` =
`false`, for each table column that has been analyzed.
If the table has inheritance children or partitions, a second entry with
`stainherit` = `true` is also created.  This row
represents the column's statistics over the inheritance tree, i.e.,
statistics for the data you'd see with
`SELECT `column` FROM `table`*`,
whereas the `stainherit` = `false` row represents
the results of
`SELECT `column` FROM ONLY `table``.

`pg_statistic` also stores statistical data about
the values of index expressions.  These are described as if they were
actual data columns; in particular, `starelid`
references the index.  No entry is made for an ordinary non-expression
index column, however, since it would be redundant with the entry
for the underlying table column.  Currently, entries for index expressions
always have `stainherit` = `false`.

Since different kinds of statistics might be appropriate for different
kinds of data, `pg_statistic` is designed not
to assume very much about what sort of statistics it stores.  Only
extremely general statistics (such as nullness) are given dedicated
columns in `pg_statistic`.  Everything else
is stored in "slots", which are groups of associated columns
whose content is identified by a code number in one of the slot's columns.
For more information see
`src/include/catalog/pg_statistic.h`.

`pg_statistic` should not be readable by the
public, since even statistical information about a table's contents
might be considered sensitive.  (Example: minimum and maximum values
of a salary column might be quite interesting.)
[`pg_stats`](#view-pg-stats)
is a publicly readable view on
`pg_statistic` that only exposes information
about those tables that are readable by the current user.

| Column Type                      Description |
| --- |
| `starelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      The table or index that the described column belongs to |
| `staattnum` `int2`        (references [`pg_attribute`](#catalog-pg-attribute).`attnum`)                      The number of the described column |
| `stainherit` `bool`                      If true, the stats include values from child tables, not just the        values in the specified relation |
| `stanullfrac` `float4`                      The fraction of the column's entries that are null |
| `stawidth` `int4`                      The average stored width, in bytes, of nonnull entries |
| `stadistinct` `float4`                      The number of distinct nonnull data values in the column.        A value greater than zero is the actual number of distinct values.        A value less than zero is the negative of a multiplier for the number        of rows in the table; for example, a column in which about 80% of the        values are nonnull and each nonnull value appears about twice on        average could be represented by `stadistinct` = -0.4.        A zero value means the number of distinct values is unknown. |
| `stakind`N`` `int2`                      A code number indicating the kind of statistics stored in the        `N`th "slot" of the        `pg_statistic` row. |
| `staop`N`` `oid`        (references [`pg_operator`](#catalog-pg-operator).`oid`)                      An operator used to derive the statistics stored in the        `N`th "slot".  For example, a        histogram slot would show the ` **Note:**

> When `tgconstraint` is nonzero,
> `tgconstrrelid`, `tgconstrindid`,
> `tgdeferrable`, and `tginitdeferred` are
> largely redundant with the referenced [`pg_constraint`](#catalog-pg-constraint) entry.
> However, it is possible for a non-deferrable trigger to be associated
> with a deferrable constraint: foreign key constraints can have some
> deferrable and some non-deferrable triggers.
>

> **Note:**

> `pg_class.relhastriggers`
> must be true if a relation has any triggers in this catalog.
>

## `pg_ts_config`

The `pg_ts_config` catalog contains entries
representing text search configurations.  A configuration specifies
a particular text search parser and a list of dictionaries to use
for each of the parser's output token types.  The parser is shown
in the `pg_ts_config` entry, but the
token-to-dictionary mapping is defined by subsidiary entries in [`pg_ts_config_map`](#catalog-pg-ts-config-map).

PostgreSQL's text search features are
described at length in [textsearch](#textsearch).

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `cfgname` `name`                      Text search configuration name |
| `cfgnamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      The OID of the namespace that contains this configuration |
| `cfgowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the configuration |
| `cfgparser` `oid`        (references [`pg_ts_parser`](#catalog-pg-ts-parser).`oid`)                      The OID of the text search parser for this configuration |

## `pg_ts_config_map`

The `pg_ts_config_map` catalog contains entries
showing which text search dictionaries should be consulted, and in
what order, for each output token type of each text search configuration's
parser.

PostgreSQL's text search features are
described at length in [textsearch](#textsearch).

| Column Type                      Description |
| --- |
| `mapcfg` `oid`        (references [`pg_ts_config`](#catalog-pg-ts-config).`oid`)                      The OID of the [`pg_ts_config`](#catalog-pg-ts-config) entry owning this map entry |
| `maptokentype` `int4`                      A token type emitted by the configuration's parser |
| `mapseqno` `int4`                      Order in which to consult this entry (lower        `mapseqno`s first) |
| `mapdict` `oid`        (references [`pg_ts_dict`](#catalog-pg-ts-dict).`oid`)                      The OID of the text search dictionary to consult |

## `pg_ts_dict`

The `pg_ts_dict` catalog contains entries
defining text search dictionaries.  A dictionary depends on a text
search template, which specifies all the implementation functions
needed; the dictionary itself provides values for the user-settable
parameters supported by the template.  This division of labor allows
dictionaries to be created by unprivileged users.  The parameters
are specified by a text string `dictinitoption`,
whose format and meaning vary depending on the template.

PostgreSQL's text search features are
described at length in [textsearch](#textsearch).

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `dictname` `name`                      Text search dictionary name |
| `dictnamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      The OID of the namespace that contains this dictionary |
| `dictowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the dictionary |
| `dicttemplate` `oid`        (references [`pg_ts_template`](#catalog-pg-ts-template).`oid`)                      The OID of the text search template for this dictionary |
| `dictinitoption` `text`                      Initialization option string for the template |

## `pg_ts_parser`

The `pg_ts_parser` catalog contains entries
defining text search parsers.  A parser is responsible for splitting
input text into lexemes and assigning a token type to each lexeme.
Since a parser must be implemented by C-language-level functions,
creation of new parsers is restricted to database superusers.

PostgreSQL's text search features are
described at length in [textsearch](#textsearch).

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `prsname` `name`                      Text search parser name |
| `prsnamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      The OID of the namespace that contains this parser |
| `prsstart` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      OID of the parser's startup function |
| `prstoken` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      OID of the parser's next-token function |
| `prsend` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      OID of the parser's shutdown function |
| `prsheadline` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      OID of the parser's headline function (zero if none) |
| `prslextype` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      OID of the parser's lextype function |

## `pg_ts_template`

The `pg_ts_template` catalog contains entries
defining text search templates.  A template is the implementation
skeleton for a class of text search dictionaries.
Since a template must be implemented by C-language-level functions,
creation of new templates is restricted to database superusers.

PostgreSQL's text search features are
described at length in [textsearch](#textsearch).

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `tmplname` `name`                      Text search template name |
| `tmplnamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      The OID of the namespace that contains this template |
| `tmplinit` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      OID of the template's initialization function (zero if none) |
| `tmpllexize` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      OID of the template's lexize function |

## `pg_type`

The catalog `pg_type` stores information about data
types.  Base types and enum types (scalar types) are created with
[`CREATE TYPE`](#sql-createtype), and
domains with
[`CREATE DOMAIN`](#sql-createdomain).
A composite type is automatically created for each table in the database, to
represent the row structure of the table.  It is also possible to create
composite types with `CREATE TYPE AS`.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `typname` `name`                      Data type name |
| `typnamespace` `oid`        (references [`pg_namespace`](#catalog-pg-namespace).`oid`)                      The OID of the namespace that contains this type |
| `typowner` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      Owner of the type |
| `typlen` `int2`                      For a fixed-size type, `typlen` is the number        of bytes in the internal representation of the type.  But for a        variable-length type, `typlen` is negative.        -1 indicates a "varlena" type (one that has a length word),        -2 indicates a null-terminated C string. |
| `typbyval` `bool`                      `typbyval` determines whether internal        routines pass a value of this type by value or by reference.        `typbyval` had better be false if        `typlen` is not 1, 2, or 4 (or 8 on machines        where Datum is 8 bytes).        Variable-length types are always passed by reference. Note that        `typbyval` can be false even if the        length would allow pass-by-value. |
| `typtype` `char`                      `typtype` is        `b` for a base type,        `c` for a composite type (e.g., a table's row type),        `d` for a domain,        `e` for an enum type,        `p` for a pseudo-type,        `r` for a range type, or        `m` for a multirange type.        See also `typrelid` and        `typbasetype`. |
| `typcategory` `char`                      `typcategory` is an arbitrary classification        of data types that is used by the parser to determine which implicit        casts should be "preferred".        See [catalog-typcategory-table](#catalog-typcategory-table). |
| `typispreferred` `bool`                      True if the type is a preferred cast target within its        `typcategory` |
| `typisdefined` `bool`                      True if the type is defined, false if this is a placeholder        entry for a not-yet-defined type.  When        `typisdefined` is false, nothing        except the type name, namespace, and OID can be relied on. |
| `typdelim` `char`                      Character that separates two values of this type when parsing        array input.  Note that the delimiter is associated with the array        element data type, not the array data type. |
| `typrelid` `oid`        (references [`pg_class`](#catalog-pg-class).`oid`)                      If this is a composite type (see        `typtype`), then this column points to        the [`pg_class`](#catalog-pg-class) entry that defines the        corresponding table.  (For a free-standing composite type, the        [`pg_class`](#catalog-pg-class) entry doesn't really represent        a table, but it is needed anyway for the type's        [`pg_attribute`](#catalog-pg-attribute) entries to link to.)        Zero for non-composite types. |
| `typsubscript` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Subscripting handler function's OID, or zero if this type doesn't        support subscripting.  Types that are "true" array        types have `typsubscript`        = `array_subscript_handler`, but other types may        have other handler functions to implement specialized subscripting        behavior. |
| `typelem` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      If `typelem` is not zero then it        identifies another row in `pg_type`,        defining the type yielded by subscripting.  This should be zero        if `typsubscript` is zero.  However, it can        be zero when `typsubscript` isn't zero, if the        handler doesn't need `typelem` to        determine the subscripting result type.        Note that a `typelem` dependency is        considered to imply physical containment of the element type in        this type; so DDL changes on the element type might be restricted        by the presence of this type. |
| `typarray` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      If `typarray` is not zero then it        identifies another row in `pg_type`, which        is the "true" array type having this type as element |
| `typinput` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Input conversion function (text format) |
| `typoutput` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Output conversion function (text format) |
| `typreceive` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Input conversion function (binary format), or zero if none |
| `typsend` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Output conversion function (binary format), or zero if none |
| `typmodin` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Type modifier input function, or zero if type does not support modifiers |
| `typmodout` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Type modifier output function, or zero to use the standard format |
| `typanalyze` `regproc`        (references [`pg_proc`](#catalog-pg-proc).`oid`)                      Custom [sql-analyze](#sql-analyze) function,        or zero to use the standard function |
| `typalign` `char`                      `typalign` is the alignment required        when storing a value of this type.  It applies to storage on        disk as well as most representations of the value inside        PostgreSQL.        When multiple values are stored consecutively, such        as in the representation of a complete row on disk, padding is        inserted before a datum of this type so that it begins on the        specified boundary.  The alignment reference is the beginning        of the first datum in the sequence.        Possible values are:         - `c` = `char` alignment, i.e., no alignment needed. - `s` = `short` alignment (2 bytes on most machines). - `i` = `int` alignment (4 bytes on most machines). - `d` = `double` alignment (8 bytes on many machines, but by no means all). |
| `typstorage` `char`                      `typstorage` tells for varlena        types (those with `typlen` = -1) if        the type is prepared for toasting and what the default strategy        for attributes of this type should be.        Possible values are:         - `p` (plain): Values must always be stored plain           (non-varlena types always use this value). - `e` (external): Values can be stored in a           secondary "TOAST" relation (if relation has one, see           `pg_class.reltoastrelid`). - `m` (main): Values can be compressed and stored           inline. - `x` (extended): Values can be compressed and/or           moved to a secondary relation.         `x` is the usual choice for toast-able types.        Note that `m` values can also be moved out to        secondary storage, but only as a last resort (`e`        and `x` values are moved first). |
| `typnotnull` `bool`                      `typnotnull` represents a not-null        constraint on a type.  Used for domains only. |
| `typbasetype` `oid`        (references [`pg_type`](#catalog-pg-type).`oid`)                      If this is a domain (see `typtype`), then        `typbasetype` identifies the type that this        one is based on.  Zero if this type is not a domain. |
| `typtypmod` `int4`                      Domains use `typtypmod` to record the `typmod`        to be applied to their base type (-1 if base type does not use a        `typmod`).  -1 if this type is not a domain. |
| `typndims` `int4`                      `typndims` is the number of array dimensions        for a domain over an array (that is, `typbasetype` is        an array type).        Zero for types other than domains over array types. |
| `typcollation` `oid`        (references [`pg_collation`](#catalog-pg-collation).`oid`)                      `typcollation` specifies the collation        of the type.  If the type does not support collations, this will        be zero.  A base type that supports collations will have a nonzero        value here, typically `DEFAULT_COLLATION_OID`.        A domain over a collatable type can have a collation OID different        from its base type's, if one was specified for the domain. |
| `typdefaultbin` `pg_node_tree`                      If `typdefaultbin` is not null, it is the        `nodeToString()`        representation of a default expression for the type.  This is        only used for domains. |
| `typdefault` `text`                      `typdefault` is null if the type has no associated        default value. If `typdefaultbin` is not null,        `typdefault` must contain a human-readable version of the        default expression represented by `typdefaultbin`.  If        `typdefaultbin` is null and `typdefault` is        not, then `typdefault` is the external representation of        the type's default value, which can be fed to the type's input        converter to produce a constant. |
| `typacl` `aclitem[]`                      Access privileges; see [ddl-priv](#ddl-priv) for details |

> **Note:**

> For fixed-width types used in system tables, it is critical that the size
> and alignment defined in `pg_type`
> agree with the way that the compiler will lay out the column in
> a structure representing a table row.
>

[catalog-typcategory-table](#catalog-typcategory-table) lists the system-defined values
of `typcategory`.  Any future additions to this list will
also be upper-case ASCII letters.  All other ASCII characters are reserved
for user-defined categories.

| Code | Category |
| --- | --- |
| `A` | Array types |
| `B` | Boolean types |
| `C` | Composite types |
| `D` | Date/time types |
| `E` | Enum types |
| `G` | Geometric types |
| `I` | Network address types |
| `N` | Numeric types |
| `P` | Pseudo-types |
| `R` | Range types |
| `S` | String types |
| `T` | Timespan types |
| `U` | User-defined types |
| `V` | Bit-string types |
| `X` | `unknown` type |
| `Z` | Internal-use types |

## `pg_user_mapping`

The catalog `pg_user_mapping` stores
the mappings from local user to remote.  Access to this catalog is
restricted from normal users, use the view
[`pg_user_mappings`](#view-pg-user-mappings)
instead.

| Column Type                      Description |
| --- |
| `oid` `oid`                      Row identifier |
| `umuser` `oid`        (references [`pg_authid`](#catalog-pg-authid).`oid`)                      OID of the local role being mapped, or zero if the user mapping is public |
| `umserver` `oid`        (references [`pg_foreign_server`](#catalog-pg-foreign-server).`oid`)                      The OID of the foreign server that contains this mapping |
| `umoptions` `text[]`                      User mapping specific options, as "keyword=value" strings |
