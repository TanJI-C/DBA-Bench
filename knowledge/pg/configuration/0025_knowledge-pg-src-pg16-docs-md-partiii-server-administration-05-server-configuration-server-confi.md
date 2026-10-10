# Parameter Names and Values

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partIII_server_administration/05_server_configuration.md`
- Source Title: `Server Configuration`
- Source Heading Path: `Server Configuration > Setting Parameters > Parameter Names and Values`
- Source Line Ranges: `8-89`
- Chunk ID: `pg16_configuration_0025_2b93bd449c`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `708225f729dbca10b354e7bbe06c9af8fa8c84710d0d92fda0090b60716d87e2`

## Retrieval Guidance

- Use When: 需要解释 postgresql.conf 或 SET 中参数值如何书写。
- Retrieval Keywords: GUC, parameter names, boolean, string, integer, floating point, memory units, time units, enumvals, pg_settings.unit
- Follow-up Guidance: 用 pg_settings 查看 unit 和 enumvals。
- Classification Note: 定义 GUC 参数名、布尔/字符串/数值/单位/枚举值的语法。

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
