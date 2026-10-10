# Managing Configuration File Contents

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Setting Parameters > Managing Configuration File Contents`
- Source Line Ranges: `8-89, 249-359`
- Chunk ID: `pg16_configuration_0029_f3896b5ef7`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b1464e175336b62465a7e92eadf5884e556b10fb2e537b7dc97468d28deffc4f`

## Retrieval Guidance

- Use When: 需要将大型 postgresql.conf 拆分为多文件或管理多实例配置。
- Retrieval Keywords: include, include_if_exists, include_dir, conf.d, shared.conf, memory.conf, server.conf
- Follow-up Guidance: 注意 include_dir 文件按 C locale 文件名顺序加载，后出现的参数生效。
- Classification Note: 说明 include、include_if_exists、include_dir、conf.d 顺序和多文件配置管理。

## Official Source Content

## Setting Parameters

### Parameter Names and Values

All parameter names are case-insensitive. Every parameter takes a
value of one of five types: boolean, string, integer, floating point,
or enumerated (enum).  The type determines the syntax for setting the
parameter:

- *Boolean:*
Values can be written as
`on`,
`off`,
`true`,
`false`,
`yes`,
`no`,
`1`,
`0`
(all case-insensitive) or any unambiguous prefix of one of these.
- *String:*
In general, enclose the value in single quotes, doubling any single
quotes within the value.  Quotes can usually be omitted if the value
is a simple number or identifier, however.
(Values that match an SQL keyword require quoting in some contexts.)
- *Numeric (integer and floating point):*
Numeric parameters can be specified in the customary integer and
floating-point formats; fractional values are rounded to the nearest
integer if the parameter is of integer type.  Integer parameters
additionally accept hexadecimal input (beginning
with `0x`) and octal input (beginning
with `0`), but these formats cannot have a fraction.
Do not use thousands separators.
Quotes are not required, except for hexadecimal input.
- *Numeric with Unit:*
Some numeric parameters have an implicit unit, because they describe
quantities of memory or time. The unit might be bytes, kilobytes, blocks
(typically eight kilobytes), milliseconds, seconds, or minutes.
An unadorned numeric value for one of these settings will use the
setting's default unit, which can be learned from
`pg_settings`.`unit`.
For convenience, settings can be given with a unit specified explicitly,
for example `'120 ms'` for a time value, and they will be
converted to whatever the parameter's actual unit is.  Note that the
value must be written as a string (with quotes) to use this feature.
The unit name is case-sensitive, and there can be whitespace between
the numeric value and the unit.

Valid memory units are `B` (bytes),
`kB` (kilobytes),
`MB` (megabytes), `GB`
(gigabytes), and `TB` (terabytes).
The multiplier for memory units is 1024, not 1000.
- Valid time units are
`us` (microseconds),
`ms` (milliseconds),
`s` (seconds), `min` (minutes),
`h` (hours), and `d` (days).

If a fractional value is specified with a unit, it will be rounded
to a multiple of the next smaller unit if there is one.
For example, `30.1 GB` will be converted
to `30822 MB` not `32319628902 B`.
If the parameter is of integer type, a final rounding to integer
occurs after any unit conversion.

*Enumerated:*
Enumerated-type parameters are written in the same way as string
parameters, but are restricted to have one of a limited set of
values.  The values allowable for such a parameter can be found from
`pg_settings`.`enumvals`.
Enum parameter values are case-insensitive.

### Parameter Interaction via the Configuration File

The most fundamental way to set these parameters is to edit the file
`postgresql.conf`,
which is normally kept in the data directory.  A default copy is
installed when the database cluster directory is initialized.
An example of what this file might look like is:

```

### Managing Configuration File Contents

PostgreSQL provides several features for breaking
down complex `postgresql.conf` files into sub-files.
These features are especially useful when managing multiple servers
with related, but not identical, configurations.

In addition to individual parameter settings,
the `postgresql.conf` file can contain *include
directives*, which specify another file to read and process as if
it were inserted into the configuration file at this point.  This
feature allows a configuration file to be divided into physically
separate parts.  Include directives simply look like:

```
include 'filename'
```

If the file name is not an absolute path, it is taken as relative to
the directory containing the referencing configuration file.
Inclusions can be nested.

There is also an `include_if_exists` directive, which acts
the same as the `include` directive, except
when the referenced file does not exist or cannot be read.  A regular
`include` will consider this an error condition, but
`include_if_exists` merely logs a message and continues
processing the referencing configuration file.

The `postgresql.conf` file can also contain
`include_dir` directives, which specify an entire
directory of configuration files to include.  These look like

```
include_dir 'directory'
```

Non-absolute directory names are taken as relative to the directory
containing the referencing configuration file.  Within the specified
directory, only non-directory files whose names end with the
suffix `.conf` will be included.  File names that
start with the `.` character are also ignored, to
prevent mistakes since such files are hidden on some platforms.  Multiple
files within an include directory are processed in file name order
(according to C locale rules, i.e., numbers before letters, and
uppercase letters before lowercase ones).

Include files or directories can be used to logically separate portions
of the database configuration, rather than having a single large
`postgresql.conf` file.  Consider a company that has two
database servers, each with a different amount of memory.  There are
likely elements of the configuration both will share, for things such
as logging.  But memory-related parameters on the server will vary
between the two.  And there might be server specific customizations,
too.  One way to manage this situation is to break the custom
configuration changes for your site into three files.  You could add
this to the end of your `postgresql.conf` file to include
them:

```
include 'shared.conf'
include 'memory.conf'
include 'server.conf'
```

All systems would have the same `shared.conf`.  Each
server with a particular amount of memory could share the
same `memory.conf`; you might have one for all servers
with 8GB of RAM, another for those having 16GB.  And
finally `server.conf` could have truly server-specific
configuration information in it.

Another possibility is to create a configuration file directory and
put this information into files there. For example, a `conf.d`
directory could be referenced at the end of `postgresql.conf`:

```
include_dir 'conf.d'
```

Then you could name the files in the `conf.d` directory
like this:

```
00shared.conf
01memory.conf
02server.conf
```

This naming convention establishes a clear order in which these
files will be loaded.  This is important because only the last
setting encountered for a particular parameter while the server is
reading configuration files will be used.  In this example,
something set in `conf.d/02server.conf` would override a
value set in `conf.d/01memory.conf`.

You might instead use this approach to naming the files
descriptively:

```
00shared.conf
01memory-8GB.conf
02server-foo.conf
```

This sort of arrangement gives a unique name for each configuration file
variation.  This can help eliminate ambiguity when several servers have
their configurations all stored in one place, such as in a version
control repository.  (Storing database configuration files under version
control is another good practice to consider.)
