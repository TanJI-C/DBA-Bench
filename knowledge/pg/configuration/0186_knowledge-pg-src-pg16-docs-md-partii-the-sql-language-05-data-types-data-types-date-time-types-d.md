# Date/Time Input; Date/Time Output; Time Zones; Interval Input; Interval Output

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partII_the_sql_language/05_data_types.md`
- Source Title: `Data Types`
- Source Heading Path: `Data Types > Date/Time Types > Date/Time Input; Date/Time Output; Time Zones; Interval Input; Interval Output`
- Source Line Ranges: `889-1434`
- Chunk ID: `pg16_configuration_0186_a073119859`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `c32571ed5e9620859202e42e00a52fd08e2f395e1e2d3a9d035f75917de6a0cb`

## Retrieval Guidance

- Use When: Need to diagnose or explain date parsing ambiguity, timestamp display differences, or interval formatting behavior.
- Retrieval Keywords: DateStyle, TimeZone, log_timezone, SET TIME ZONE, PGDATESTYLE, PGTZ, IntervalStyle, timestamp output
- Follow-up Guidance: Check session and database-level settings before changing application date/time handling.
- Classification Note: Explains DateStyle, TimeZone, log_timezone, SET TIME ZONE, PGDATESTYLE, PGTZ, and IntervalStyle effects on date/time parsing and display.

## Official Source Content

## Date/Time Types

PostgreSQL supports the full set of
SQL date and time types, shown in [datatype-datetime-table](#datatype-datetime-table).  The operations available
on these data types are described in
[functions-datetime](#functions-datetime).
Dates are counted according to the Gregorian calendar, even in
years before that calendar was introduced (see [datetime-units-history](#datetime-units-history) for more information).

| Name | Storage Size | Description | Low Value | High Value | Resolution |
| --- | --- | --- | --- | --- | --- |
| `timestamp [ (`p`) ] [ without time zone ]` | 8 bytes | both date and time (no time zone) | 4713 BC | 294276 AD | 1 microsecond |
| `timestamp [ (`p`) ] with time zone` | 8 bytes | both date and time, with time zone | 4713 BC | 294276 AD | 1 microsecond |
| `date` | 4 bytes | date (no time of day) | 4713 BC | 5874897 AD | 1 day |
| `time [ (`p`) ] [ without time zone ]` | 8 bytes | time of day (no date) | 00:00:00 | 24:00:00 | 1 microsecond |
| `time [ (`p`) ] with time zone` | 12 bytes | time of day (no date), with time zone | 00:00:00+1559 | 24:00:00-1559 | 1 microsecond |
| `interval [ `fields` ] [ (`p`) ]` | 16 bytes | time interval | -178000000 years | 178000000 years | 1 microsecond |

> **Note:**

> The SQL standard requires that writing just `timestamp`
> be equivalent to `timestamp without time
> zone`, and PostgreSQL honors that
> behavior.  `timestamptz` is accepted as an
> abbreviation for `timestamp with time zone`; this is a
> PostgreSQL extension.
>

`time`, `timestamp`, and
`interval` accept an optional precision value
`p` which specifies the number of
fractional digits retained in the seconds field. By default, there
is no explicit bound on precision.  The allowed range of
`p` is from 0 to 6.

The `interval` type has an additional option, which is
to restrict the set of stored fields by writing one of these phrases:

```
YEAR
MONTH
DAY
HOUR
MINUTE
SECOND
YEAR TO MONTH
DAY TO HOUR
DAY TO MINUTE
DAY TO SECOND
HOUR TO MINUTE
HOUR TO SECOND
MINUTE TO SECOND
```

Note that if both `fields` and
`p` are specified, the
`fields` must include `SECOND`,
since the precision applies only to the seconds.

The type `time with time zone` is defined by the SQL
standard, but the definition exhibits properties which lead to
questionable usefulness. In most cases, a combination of
`date`, `time`, `timestamp without time
zone`, and `timestamp with time zone` should
provide a complete range of date/time functionality required by
any application.

### Date/Time Input

Date and time input is accepted in almost any reasonable format, including
ISO 8601, SQL-compatible,
traditional POSTGRES, and others.
For some formats, ordering of day, month, and year in date input is
ambiguous and there is support for specifying the expected
ordering of these fields.  Set the [guc-datestyle](#guc-datestyle) parameter
to `MDY` to select month-day-year interpretation,
`DMY` to select day-month-year interpretation, or
`YMD` to select year-month-day interpretation.

PostgreSQL is more flexible in
handling date/time input than the
SQL standard requires.
See [datetime-appendix](#datetime-appendix)
for the exact parsing rules of date/time input and for the
recognized text fields including months, days of the week, and
time zones.

Remember that any date or time literal input needs to be enclosed
in single quotes, like text strings.  Refer to
[sql-syntax-constants-generic](#sql-syntax-constants-generic) for more
information.
SQL requires the following syntax

```
`type` [ (`p`) ] '`value`'
```

where `p` is an optional precision
specification giving the number of
fractional digits in the seconds field. Precision can be
specified for `time`, `timestamp`, and
`interval` types, and can range from 0 to 6.
If no precision is specified in a constant specification,
it defaults to the precision of the literal value (but not
more than 6 digits).

#### Dates

[datatype-datetime-date-table](#datatype-datetime-date-table) shows some possible
inputs for the `date` type.

| Example | Description |
| --- | --- |
| 1999-01-08 | ISO 8601; January 8 in any mode          (recommended format) |
| January 8, 1999 | unambiguous in any `datestyle` input mode |
| 1/8/1999 | January 8 in `MDY` mode;           August 1 in `DMY` mode |
| 1/18/1999 | January 18 in `MDY` mode;           rejected in other modes |
| 01/02/03 | January 2, 2003 in `MDY` mode;           February 1, 2003 in `DMY` mode;           February 3, 2001 in `YMD` mode |
| 1999-Jan-08 | January 8 in any mode |
| Jan-08-1999 | January 8 in any mode |
| 08-Jan-1999 | January 8 in any mode |
| 99-Jan-08 | January 8 in `YMD` mode, else error |
| 08-Jan-99 | January 8, except error in `YMD` mode |
| Jan-08-99 | January 8, except error in `YMD` mode |
| 19990108 | ISO 8601; January 8, 1999 in any mode |
| 990108 | ISO 8601; January 8, 1999 in any mode |
| 1999.008 | year and day of year |
| J2451187 | Julian date |
| January 8, 99 BC | year 99 BC |

#### Times

The time-of-day types are `time [
(`p`) ] without time zone` and
`time [ (`p`) ] with time
zone`.  `time` alone is equivalent to
`time without time zone`.

Valid input for these types consists of a time of day followed
by an optional time zone. (See [datatype-datetime-time-table](#datatype-datetime-time-table)
and [datatype-timezone-table](#datatype-timezone-table).)  If a time zone is
specified in the input for `time without time zone`,
it is silently ignored. You can also specify a date but it will
be ignored, except when you use a time zone name that involves a
daylight-savings rule, such as
`America/New_York`. In this case specifying the date
is required in order to determine whether standard or daylight-savings
time applies.  The appropriate time zone offset is recorded in the
`time with time zone` value and is output as stored;
it is not adjusted to the active time zone.

| Example | Description |
| --- | --- |
| `04:05:06.789` | ISO 8601 |
| `04:05:06` | ISO 8601 |
| `04:05` | ISO 8601 |
| `040506` | ISO 8601 |
| `04:05 AM` | same as 04:05; AM does not affect value |
| `04:05 PM` | same as 16:05; input hour must be  **Caution:**

> While the input strings `now`,
> `today`, `tomorrow`,
> and `yesterday` are fine to use in interactive SQL
> commands, they can have surprising behavior when the command is
> saved to be executed later, for example in prepared statements,
> views, and function definitions.  The string can be converted to a
> specific time value that continues to be used long after it becomes
> stale.  Use one of the SQL functions instead in such contexts.
> For example, `CURRENT_DATE + 1` is safer than
> `'tomorrow'::date`.
>

### Date/Time Output

The output format of the date/time types can be set to one of the four
styles ISO 8601,
SQL (Ingres), traditional POSTGRES
(Unix date format), or
German.  The default
is the ISO format.  (The
SQL standard requires the use of the ISO 8601
format.  The name of the "SQL" output format is a
historical accident.)  [datatype-datetime-output-table](#datatype-datetime-output-table) shows examples of each
output style.  The output of the `date` and
`time` types is generally only the date or time part
in accordance with the given examples.  However, the
POSTGRES style outputs date-only values in
ISO format.

| Style Specification | Description | Example |
| --- | --- | --- |
| `ISO` | ISO 8601, SQL standard | `1997-12-17 07:37:16-08` |
| `SQL` | traditional style | `12/17/1997 07:37:16.00 PST` |
| `Postgres` | original style | `Wed Dec 17 07:37:16 1997 PST` |
| `German` | regional style | `17.12.1997 07:37:16.00 PST` |

> **Note:**

> ISO 8601 specifies the use of uppercase letter `T` to separate
> the date and time.  PostgreSQL accepts that format on
> input, but on output it uses a space rather than `T`, as shown
> above.  This is for readability and for consistency with
> [RFC 3339](https://datatracker.ietf.org/doc/html/rfc3339) as
> well as some other database systems.
>

In the SQL and POSTGRES styles, day appears before
month if DMY field ordering has been specified, otherwise month appears
before day.
(See [datatype-datetime-input](#datatype-datetime-input)
for how this setting also affects interpretation of input values.)
[datatype-datetime-output2-table](#datatype-datetime-output2-table) shows examples.

| `datestyle` Setting | Input Ordering | Example Output |
| --- | --- | --- |
| `SQL, DMY` | `day`/`month`/`year` | `17/12/1997 15:37:16.00 CET` |
| `SQL, MDY` | `month`/`day`/`year` | `12/17/1997 07:37:16.00 PST` |
| `Postgres, DMY` | `day`/`month`/`year` | `Wed 17 Dec 07:37:16 1997 PST` |

In the ISO style, the time zone is always shown as
a signed numeric offset from UTC, with positive sign used for zones
east of Greenwich.  The offset will be shown
as `hh` (hours only) if it is an integral
number of hours, else
as `hh`:`mm` if it
is an integral number of minutes, else as
`hh`:`mm`:`ss`.
(The third case is not possible with any modern time zone standard,
but it can appear when working with timestamps that predate the
adoption of standardized time zones.)
In the other date styles, the time zone is shown as an alphabetic
abbreviation if one is in common use in the current zone.  Otherwise
it appears as a signed numeric offset in ISO 8601 basic format
(`hh` or `hhmm`).

The date/time style can be selected by the user using the
`SET datestyle` command, the [guc-datestyle](#guc-datestyle) parameter in the
`postgresql.conf` configuration file, or the
`PGDATESTYLE` environment variable on the server or
client.

The formatting function `to_char`
(see [functions-formatting](#functions-formatting)) is also available as
a more flexible way to format date/time output.

### Time Zones

Time zones, and time-zone conventions, are influenced by
political decisions, not just earth geometry. Time zones around the
world became somewhat standardized during the 1900s,
but continue to be prone to arbitrary changes, particularly with
respect to daylight-savings rules.
PostgreSQL uses the widely-used
IANA (Olson) time zone database for information about
historical time zone rules.  For times in the future, the assumption
is that the latest known rules for a given time zone will
continue to be observed indefinitely far into the future.

PostgreSQL endeavors to be compatible with
the SQL standard definitions for typical usage.
However, the SQL standard has an odd mix of date and
time types and capabilities. Two obvious problems are:

- Although the `date` type
cannot have an associated time zone, the
`time` type can.
Time zones in the real world have little meaning unless
associated with a date as well as a time,
since the offset can vary through the year with daylight-saving
time boundaries.
- The default time zone is specified as a constant numeric offset
from UTC. It is therefore impossible to adapt to
daylight-saving time when doing date/time arithmetic across
DST boundaries.

To address these difficulties, we recommend using date/time types
that contain both date and time when using time zones. We
do *not* recommend using the type `time with
time zone` (though it is supported by
PostgreSQL for legacy applications and
for compliance with the SQL standard).
PostgreSQL assumes
your local time zone for any type containing only date or time.

All timezone-aware dates and times are stored internally in
UTC.  They are converted to local time
in the zone specified by the [guc-timezone](#guc-timezone) configuration
parameter before being displayed to the client.

PostgreSQL allows you to specify time zones in
three different forms:

- A full time zone name, for example `America/New_York`.
The recognized time zone names are listed in the
`pg_timezone_names` view (see [view-pg-timezone-names](#view-pg-timezone-names)).
PostgreSQL uses the widely-used IANA
time zone data for this purpose, so the same time zone
names are also recognized by other software.
- A time zone abbreviation, for example `PST`.  Such a
specification merely defines a particular offset from UTC, in
contrast to full time zone names which can imply a set of daylight
savings transition rules as well.  The recognized abbreviations
are listed in the `pg_timezone_abbrevs` view (see [view-pg-timezone-abbrevs](#view-pg-timezone-abbrevs)).  You cannot set the
configuration parameters [guc-timezone](#guc-timezone) or
[guc-log-timezone](#guc-log-timezone) to a time
zone abbreviation, but you can use abbreviations in
date/time input values and with the `AT TIME ZONE`
operator.
- In addition to the timezone names and abbreviations,
PostgreSQL will accept POSIX-style time zone
specifications, as described in
[datetime-posix-timezone-specs](#datetime-posix-timezone-specs).  This option is not
normally preferable to using a named time zone, but it may be
necessary if no suitable IANA time zone entry is available.

In short, this is the difference between abbreviations
and full names: abbreviations represent a specific offset from UTC,
whereas many of the full names imply a local daylight-savings time
rule, and so have two possible UTC offsets.  As an example,
`2014-06-04 12:00 America/New_York` represents noon local
time in New York, which for this particular date was Eastern Daylight
Time (UTC-4).  So `2014-06-04 12:00 EDT` specifies that
same time instant.  But `2014-06-04 12:00 EST` specifies
noon Eastern Standard Time (UTC-5), regardless of whether daylight
savings was nominally in effect on that date.

To complicate matters, some jurisdictions have used the same timezone
abbreviation to mean different UTC offsets at different times; for
example, in Moscow `MSK` has meant UTC+3 in some years and
UTC+4 in others.  PostgreSQL interprets such
abbreviations according to whatever they meant (or had most recently
meant) on the specified date; but, as with the `EST` example
above, this is not necessarily the same as local civil time on that date.

In all cases, timezone names and abbreviations are recognized
case-insensitively.  (This is a change from PostgreSQL
versions prior to 8.2, which were case-sensitive in some contexts but
not others.)

Neither timezone names nor abbreviations are hard-wired into the server;
they are obtained from configuration files stored under
`.../share/timezone/` and `.../share/timezonesets/`
of the installation directory
(see [datetime-config-files](#datetime-config-files)).

The [guc-timezone](#guc-timezone) configuration parameter can
be set in the file `postgresql.conf`, or in any of the
other standard ways described in [runtime-config](#runtime-config).
There are also some special ways to set it:

- The SQL command `SET TIME ZONE`
sets the time zone for the session.  This is an alternative spelling
of `SET TIMEZONE TO` with a more SQL-spec-compatible syntax.
- The `PGTZ` environment variable is used by
libpq clients
to send a `SET TIME ZONE`
command to the server upon connection.

### Interval Input

`interval` values can be written using the following
verbose syntax:

```
@ `quantity` `unit` `quantity` `unit`... `direction`
```

where `quantity` is a number (possibly signed);
`unit` is `microsecond`,
`millisecond`, `second`,
`minute`, `hour`, `day`,
`week`, `month`, `year`,
`decade`, `century`, `millennium`,
or abbreviations or plurals of these units;
`direction` can be `ago` or
empty.  The at sign (`@`) is optional noise.  The amounts
of the different units are implicitly added with appropriate
sign accounting.  `ago` negates all the fields.
This syntax is also used for interval output, if
[guc-intervalstyle](#guc-intervalstyle) is set to
`postgres_verbose`.

Quantities of days, hours, minutes, and seconds can be specified without
explicit unit markings.  For example, `'1 12:59:10'` is read
the same as `'1 day 12 hours 59 min 10 sec'`.  Also,
a combination of years and months can be specified with a dash;
for example `'200-10'` is read the same as `'200 years
10 months'`.  (These shorter forms are in fact the only ones allowed
by the SQL standard, and are used for output when
`IntervalStyle` is set to `sql_standard`.)

Interval values can also be written as ISO 8601 time intervals, using
either the "format with designators" of the standard's section
4.4.3.2 or the "alternative format" of section 4.4.3.3.  The
format with designators looks like this:

```
P `quantity` `unit`  `quantity` `unit` ...  T  `quantity` `unit` ...
```

The string must start with a `P`, and may include a
`T` that introduces the time-of-day units.  The
available unit abbreviations are given in [datatype-interval-iso8601-units](#datatype-interval-iso8601-units).  Units may be
omitted, and may be specified in any order, but units smaller than
a day must appear after `T`.  In particular, the meaning of
`M` depends on whether it is before or after
`T`.

| Abbreviation | Meaning |
| --- | --- |
| Y | Years |
| M | Months (in the date part) |
| W | Weeks |
| D | Days |
| H | Hours |
| M | Minutes (in the time part) |
| S | Seconds |

In the alternative format:

```
P  `years`-`months`-`days`   T `hours`:`minutes`:`seconds`
```

the string must begin with `P`, and a
`T` separates the date and time parts of the interval.
The values are given as numbers similar to ISO 8601 dates.

When writing an interval constant with a `fields`
specification, or when assigning a string to an interval column that was
defined with a `fields` specification, the interpretation of
unmarked quantities depends on the `fields`.  For
example `INTERVAL '1' YEAR` is read as 1 year, whereas
`INTERVAL '1'` means 1 second.  Also, field values
"to the right" of the least significant field allowed by the
`fields` specification are silently discarded.  For
example, writing `INTERVAL '1 day 2:03:04' HOUR TO MINUTE`
results in dropping the seconds field, but not the day field.

According to the SQL standard all fields of an interval
value must have the same sign, so a leading negative sign applies to all
fields; for example the negative sign in the interval literal
`'-1 2:03:04'` applies to both the days and hour/minute/second
parts.  PostgreSQL allows the fields to have different
signs, and traditionally treats each field in the textual representation
as independently signed, so that the hour/minute/second part is
considered positive in this example.  If `IntervalStyle` is
set to `sql_standard` then a leading sign is considered
to apply to all fields (but only if no additional signs appear).
Otherwise the traditional PostgreSQL interpretation is
used.  To avoid ambiguity, it's recommended to attach an explicit sign
to each field if any field is negative.

Internally, `interval` values are stored as three integral
fields: months, days, and microseconds.  These fields are kept
separate because the number of days in a month varies, while a day
can have 23 or 25 hours if a daylight savings time transition is
involved.  An interval input string that uses other units is
normalized into this format, and then reconstructed in a standardized
way for output, for example:

```
SELECT '2 years 15 months 100 weeks 99 hours 123456789 milliseconds'::interval;
interval
---------------------------------------
3 years 3 mons 700 days 133:17:36.789
```

Here weeks, which are understood as "7 days", have been
kept separate, while the smaller and larger time units were
combined and normalized.

Input field values can have fractional parts, for example `'1.5
weeks'` or `'01:02:03.45'`.  However,
because `interval` internally stores only integral fields,
fractional values must be converted into smaller
units.  Fractional parts of units greater than months are rounded to
be an integer number of months, e.g. `'1.5 years'`
becomes `'1 year 6 mons'`.  Fractional parts of
weeks and days are computed to be an integer number of days and
microseconds, assuming 30 days per month and 24 hours per day, e.g.,
`'1.75 months'` becomes `1 mon 22 days
12:00:00`.  Only seconds will ever be shown as fractional
on output.

[datatype-interval-input-examples](#datatype-interval-input-examples) shows some examples
of valid `interval` input.

| Example | Description |
| --- | --- |
| `1-2` | SQL standard format: 1 year 2 months |
| `3 4:05:06` | SQL standard format: 3 days 4 hours 5 minutes 6 seconds |
| `1 year 2 months 3 days 4 hours 5 minutes 6 seconds` | Traditional Postgres format: 1 year 2 months 3 days 4 hours 5 minutes 6 seconds |
| `P1Y2M3DT4H5M6S` | ISO 8601 "format with designators": same meaning as above |
| `P0001-02-03T04:05:06` | ISO 8601 "alternative format": same meaning as above |

### Interval Output

As previously explained, PostgreSQL
stores `interval` values as months, days, and
microseconds.  For output, the months field is converted to years and
months by dividing by 12.  The days field is shown as-is.  The
microseconds field is converted to hours, minutes, seconds, and
fractional seconds.  Thus months, minutes, and seconds will never be
shown as exceeding the ranges 0–11, 0–59, and 0–59
respectively, while the displayed years, days, and hours fields can
be quite large.  (The [`justify_days`](#function-justify-days)
and [`justify_hours`](#function-justify-hours)
functions can be used if it is desirable to transpose large days or
hours values into the next higher field.)

The output format of the interval type can be set to one of the
four styles `sql_standard`, `postgres`,
`postgres_verbose`, or `iso_8601`,
using the command `SET intervalstyle`.
The default is the `postgres` format.
[interval-style-output-table](#interval-style-output-table) shows examples of each
output style.

The `sql_standard` style produces output that conforms to
the SQL standard's specification for interval literal strings, if
the interval value meets the standard's restrictions (either year-month
only or day-time only, with no mixing of positive
and negative components).  Otherwise the output looks like a standard
year-month literal string followed by a day-time literal string,
with explicit signs added to disambiguate mixed-sign intervals.

The output of the `postgres` style matches the output of
PostgreSQL releases prior to 8.4 when the
[guc-datestyle](#guc-datestyle) parameter was set to `ISO`.

The output of the `postgres_verbose` style matches the output of
PostgreSQL releases prior to 8.4 when the
`DateStyle` parameter was set to non-`ISO` output.

The output of the `iso_8601` style matches the "format
with designators" described in section 4.4.3.2 of the
ISO 8601 standard.

| Style Specification | Year-Month Interval | Day-Time Interval | Mixed Interval |
| --- | --- | --- | --- |
| `sql_standard` | 1-2 | 3 4:05:06 | -1-2 +3 -4:05:06 |
| `postgres` | 1 year 2 mons | 3 days 04:05:06 | -1 year -2 mons +3 days -04:05:06 |
| `postgres_verbose` | @ 1 year 2 mons | @ 3 days 4 hours 5 mins 6 secs | @ 1 year 2 mons -3 days 4 hours 5 mins 6 secs ago |
| `iso_8601` | P1Y2M | P3DT4H5M6S | P-1Y-2M3DT-4H-5M-6S |
