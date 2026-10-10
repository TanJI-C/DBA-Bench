# Date/Time Input Interpretation; Date/Time Key Words; History of Units; Julian Dates

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/02_datetime_support.md`
- Source Title: `02 datetime support`
- Source Heading Path: `Date/Time Support > Date/Time Input Interpretation; Date/Time Key Words; History of Units; Julian Dates`
- Source Line Ranges: `1-15, 16-90, 91-157, 158-202, 203-312, 313-451, 452-530, 531-578`
- Chunk ID: `pg16_fact_0121_62df017075`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `68392db9a500eb30a698bc711e995cbc0bf68537a6d0eddad66321809d1ac6e4`

## Retrieval Guidance

- Use When: Understand how PostgreSQL interprets date/time literals and keywords.
- Retrieval Keywords: date time input, timestamp parsing, date time keywords, Julian date, time zone parsing, BC date
- Follow-up Guidance: Use configuration records when changing timezone abbreviation or timezone files.
- Classification Note: These sections describe parsing rules, recognized date/time keywords, unit history, and Julian-date behavior as reference.

## Official Source Content

## Date/Time Support

PostgreSQL uses an internal heuristic
parser for all date/time input support. Dates and times are input as
strings, and are broken up into distinct fields with a preliminary
determination of what kind of information can be in the
field. Each field is interpreted and either assigned a numeric
value, ignored, or rejected.
The parser contains internal lookup tables for all textual fields,
including months, days of the week, and time zones.

This appendix includes information on the content of these
lookup tables and describes the steps used by the parser to decode
dates and times.

## Date/Time Input Interpretation

Date/time input strings are decoded using the following procedure.

Break the input string into tokens and categorize each token as
a string, time, time zone, or number.

If the numeric token contains a colon (`:`), this is
a time string. Include all subsequent digits and colons.

If the numeric token contains a dash (`-`), slash
(`/`), or two or more dots (`.`), this is
a date string which might have a text month.  If a date token has
already been seen, it is instead interpreted as a time zone
name (e.g., `America/New_York`).

If the token is numeric only, then it is either a single field
or an ISO 8601 concatenated date (e.g.,
`19990113` for January 13, 1999) or time
(e.g., `141516` for 14:15:16).

If the token starts with a plus (`+`) or minus
(`-`), then it is either a numeric time zone or a special
field.

If the token is an alphabetic string, match up with possible strings:

See if the token matches any known time zone abbreviation.
These abbreviations are supplied by the configuration file
described in [datetime-config-files](#datetime-config-files).

If not found, search an internal table to match
the token as either a special string (e.g., `today`),
day (e.g., `Thursday`),
month (e.g., `January`),
or noise word (e.g., `at`, `on`).

If still not found, throw an error.

When the token is a number or number field:

If there are eight or six digits,
and if no other date fields have been previously read, then interpret
as a "concatenated date" (e.g.,
`19990118` or `990118`).
The interpretation is `YYYYMMDD` or `YYMMDD`.

If the token is three digits
and a year has already been read, then interpret as day of year.

If four or six digits and a year has already been read, then
interpret as a time (`HHMM` or `HHMMSS`).

If three or more digits and no date fields have yet been found,
interpret as a year (this forces yy-mm-dd ordering of the remaining
date fields).

Otherwise the date field ordering is assumed to follow the
`DateStyle` setting: mm-dd-yy, dd-mm-yy, or yy-mm-dd.
Throw an error if a month or day field is found to be out of range.

If BC has been specified, negate the year and add one for
internal storage.  (There is no year zero in the Gregorian
calendar, so numerically 1 BC becomes year zero.)

If BC was not specified, and if the year field was two digits in length,
then adjust the year to four digits. If the field is less than 70, then
add 2000, otherwise add 1900.

> **Tip:**

> Gregorian years AD 1–99 can be entered by using 4 digits with leading
> zeros (e.g., `0099` is AD 99).
>

## Handling of Invalid or Ambiguous Timestamps

Ordinarily, if a date/time string is syntactically valid but contains
out-of-range field values, an error will be thrown.  For example, input
specifying the 31st of February will be rejected.

During a daylight-savings-time transition, it is possible for a
seemingly valid timestamp string to represent a nonexistent or ambiguous
timestamp.  Such cases are not rejected; the ambiguity is resolved by
determining which UTC offset to apply.  For example, supposing that the
[guc-timezone](#guc-timezone) parameter is set
to `America/New_York`, consider

```
=> SELECT '2018-03-11 02:30'::timestamptz;
timestamptz
------------------------
2018-03-11 03:30:00-04
(1 row)
```

Because that day was a spring-forward transition date in that time zone,
there was no civil time instant 2:30AM; clocks jumped forward from 2AM
EST to 3AM EDT.  PostgreSQL interprets the
given time as if it were standard time (UTC-5), which then renders as
3:30AM EDT (UTC-4).

Conversely, consider the behavior during a fall-back transition:

```
=> SELECT '2018-11-04 01:30'::timestamptz;
timestamptz
------------------------
2018-11-04 01:30:00-05
(1 row)
```

On that date, there were two possible interpretations of 1:30AM; there
was 1:30AM EDT, and then an hour later after clocks jumped back from
2AM EDT to 1AM EST, there was 1:30AM EST.
Again, PostgreSQL interprets the given time
as if it were standard time (UTC-5).  We can force the other
interpretation by specifying daylight-savings time:

```
=> SELECT '2018-11-04 01:30 EDT'::timestamptz;
timestamptz
------------------------
2018-11-04 01:30:00-04
(1 row)
```

The precise rule that is applied in such cases is that an invalid
timestamp that appears to fall within a jump-forward daylight savings
transition is assigned the UTC offset that prevailed in the time zone
just before the transition, while an ambiguous timestamp that could fall
on either side of a jump-back transition is assigned the UTC offset that
prevailed just after the transition.  In most time zones this is
equivalent to saying that "the standard-time interpretation is
preferred when in doubt".

In all cases, the UTC offset associated with a timestamp can be
specified explicitly, using either a numeric UTC offset or a time zone
abbreviation that corresponds to a fixed UTC offset.  The rule just
given applies only when it is necessary to infer a UTC offset for a time
zone in which the offset varies.

## Date/Time Key Words

[datetime-month-table](#datetime-month-table) shows the tokens that are
recognized as names of months.

| Month | Abbreviations |
| --- | --- |
| January | Jan |
| February | Feb |
| March | Mar |
| April | Apr |
| May |  |
| June | Jun |
| July | Jul |
| August | Aug |
| September | Sep, Sept |
| October | Oct |
| November | Nov |
| December | Dec |

[datetime-dow-table](#datetime-dow-table) shows the tokens that are
recognized as names of days of the week.

| Day | Abbreviations |
| --- | --- |
| Sunday | Sun |
| Monday | Mon |
| Tuesday | Tue, Tues |
| Wednesday | Wed, Weds |
| Thursday | Thu, Thur, Thurs |
| Friday | Fri |
| Saturday | Sat |

[datetime-mod-table](#datetime-mod-table) shows the tokens that serve
various modifier purposes.

| Identifier | Description |
| --- | --- |
| `AM` | Time is before 12:00 |
| `AT` | Ignored |
| `JULIAN`, `JD`, `J` | Next field is Julian Date |
| `ON` | Ignored |
| `PM` | Time is on or after 12:00 |
| `T` | Next field is time |

## Date/Time Configuration Files

Since timezone abbreviations are not well standardized,
PostgreSQL provides a means to customize
the set of abbreviations accepted by the server.  The
[guc-timezone-abbreviations](#guc-timezone-abbreviations) run-time parameter
determines the active set of abbreviations.  While this parameter
can be altered by any database user, the possible values for it
are under the control of the database administrator — they
are in fact names of configuration files stored in
`.../share/timezonesets/` of the installation directory.
By adding or altering files in that directory, the administrator
can set local policy for timezone abbreviations.

`timezone_abbreviations` can be set to any file name
found in `.../share/timezonesets/`, if the file's name
is entirely alphabetic.  (The prohibition against non-alphabetic
characters in `timezone_abbreviations` prevents reading
files outside the intended directory, as well as reading editor
backup files and other extraneous files.)

A timezone abbreviation file can contain blank lines and comments
beginning with `#`.  Non-comment lines must have one of
these formats:

```
`zone_abbreviation` `offset`
`zone_abbreviation` `offset` D
`zone_abbreviation` `time_zone_name`
@INCLUDE `file_name`
@OVERRIDE
```

A `zone_abbreviation` is just the abbreviation
being defined.  An `offset` is an integer giving
the equivalent offset in seconds from UTC, positive being east from
Greenwich and negative being west.  For example, -18000 would be five
hours west of Greenwich, or North American east coast standard time.
`D` indicates that the zone name represents local
daylight-savings time rather than standard time.

Alternatively, a `time_zone_name` can be given, referencing
a zone name defined in the IANA timezone database.  The zone's definition
is consulted to see whether the abbreviation is or has been in use in
that zone, and if so, the appropriate meaning is used — that is,
the meaning that was currently in use at the timestamp whose value is
being determined, or the meaning in use immediately before that if it
wasn't current at that time, or the oldest meaning if it was used only
after that time.  This behavior is essential for dealing with
abbreviations whose meaning has historically varied.  It is also allowed
to define an abbreviation in terms of a zone name in which that
abbreviation does not appear; then using the abbreviation is just
equivalent to writing out the zone name.

> **Tip:**

> Using a simple integer `offset` is preferred
> when defining an abbreviation whose offset from UTC has never changed,
> as such abbreviations are much cheaper to process than those that
> require consulting a time zone definition.
>

The `@INCLUDE` syntax allows inclusion of another file in the
`.../share/timezonesets/` directory.  Inclusion can be nested,
to a limited depth.

The `@OVERRIDE` syntax indicates that subsequent entries in the
file can override previous entries (typically, entries obtained from
included files).  Without this, conflicting definitions of the same
timezone abbreviation are considered an error.

In an unmodified installation, the file `Default` contains
all the non-conflicting time zone abbreviations for most of the world.
Additional files `Australia` and `India` are
provided for those regions: these files first include the
`Default` file and then add or modify abbreviations as needed.

For reference purposes, a standard installation also contains files
`Africa.txt`, `America.txt`, etc., containing
information about every time zone abbreviation known to be in use
according to the IANA timezone database.  The zone name
definitions found in these files can be copied and pasted into a custom
configuration file as needed.  Note that these files cannot be directly
referenced as `timezone_abbreviations` settings, because of
the dot embedded in their names.

> **Note:**

> If an error occurs while reading the time zone abbreviation set, no new
> value is applied and the old set is kept. If the error occurs while
> starting the database, startup fails.
>

> **Caution:**

> Time zone abbreviations defined in the configuration file override
> non-timezone meanings built into PostgreSQL.
> For example, the `Australia` configuration file defines
> `SAT` (for South Australian Standard Time).  When this
> file is active, `SAT` will not be recognized as an abbreviation
> for Saturday.
>

> **Caution:**

> If you modify files in `.../share/timezonesets/`,
> it is up to you to make backups — a normal database dump
> will not include this directory.
>

## POSIX Time Zone Specifications

PostgreSQL can accept time zone specifications
that are written according to the POSIX standard's rules
for the `TZ` environment
variable.  POSIX time zone specifications are
inadequate to deal with the complexity of real-world time zone history,
but there are sometimes reasons to use them.

A POSIX time zone specification has the form

```
`STD` `offset`  `DST`  `dstoffset`   , `rule`
```

(For readability, we show spaces between the fields, but spaces should
not be used in practice.)  The fields are:

- `STD` is the zone abbreviation to be used
for standard time.
- `offset` is the zone's standard-time offset
from UTC.
- `DST` is the zone abbreviation to be used
for daylight-savings time.  If this field and the following ones are
omitted, the zone uses a fixed UTC offset with no daylight-savings
rule.
- `dstoffset` is the daylight-savings offset
from UTC.  This field is typically omitted, since it defaults to one
hour less than the standard-time `offset`,
which is usually the right thing.
- `rule` defines the rule for when daylight
savings is in effect, as described below.

In this syntax, a zone abbreviation can be a string of letters, such
as `EST`, or an arbitrary string surrounded by angle
brackets, such as `<UTC-05>`.
Note that the zone abbreviations given here are only used for output,
and even then only in some timestamp output formats.  The zone
abbreviations recognized in timestamp input are determined as explained
in [datetime-config-files](#datetime-config-files).

The offset fields specify the hours, and optionally minutes and seconds,
difference from UTC.  They have the format
`hh``:``mm``:``ss`
optionally with a leading sign (`+`
or `-`).  The positive sign is used for
zones *west* of Greenwich.  (Note that this is the
opposite of the ISO-8601 sign convention used elsewhere in
PostgreSQL.)  `hh`
can have one or two digits; `mm`
and `ss` (if used) must have two.

The daylight-savings transition `rule` has the
format

```
`dstdate`  `/` `dsttime`  `,` `stddate`  `/` `stdtime`
```

(As before, spaces should not be included in practice.)
The `dstdate`
and `dsttime` fields define when daylight-savings
time starts, while `stddate`
and `stdtime` define when standard time
starts.  (In some cases, notably in zones south of the equator, the
former might be later in the year than the latter.)  The date fields
have one of these formats:

**`n`**
: A plain integer denotes a day of the year, counting from zero to
364, or to 365 in leap years.

**`J``n`**
: In this form, `n` counts from 1 to 365,
and February 29 is not counted even if it is present.  (Thus, a
transition occurring on February 29 could not be specified this
way.  However, days after February have the same numbers whether
it's a leap year or not, so that this form is usually more useful
than the plain-integer form for transitions on fixed dates.)

**`M``m``.``n``.``d`**
: This form specifies a transition that always happens during the same
month and on the same day of the week.  `m`
identifies the month, from 1 to 12.  `n`
specifies the `n`'th occurrence of the
weekday identified by `d`.
`n` is a number between 1 and 4, or 5
meaning the last occurrence of that weekday in the month (which
could be the fourth or the fifth).  `d` is
a number between 0 and 6, with 0 indicating Sunday.
For example, `M3.2.0` means "the second
Sunday in March".

> **Note:**

> The `M` format is sufficient to describe many common
> daylight-savings transition laws.  But note that none of these variants
> can deal with daylight-savings law changes, so in practice the
> historical data stored for named time zones (in the IANA time zone
> database) is necessary to interpret past time stamps correctly.
>

The time fields in a transition rule have the same format as the offset
fields described previously, except that they cannot contain signs.
They define the current local time at which the change to the other
time occurs.  If omitted, they default to `02:00:00`.

If a daylight-savings abbreviation is given but the
transition `rule` field is omitted,
the fallback behavior is to use the
rule `M3.2.0,M11.1.0`, which corresponds to USA
practice as of 2020 (that is, spring forward on the second Sunday of
March, fall back on the first Sunday of November, both transitions
occurring at 2AM prevailing time).  Note that this rule does not
give correct USA transition dates for years before 2007.

As an example, `CET-1CEST,M3.5.0,M10.5.0/3` describes
current (as of 2020) timekeeping practice in Paris.  This specification
says that standard time has the abbreviation `CET` and
is one hour ahead (east) of UTC; daylight savings time has the
abbreviation `CEST` and is implicitly two hours ahead
of UTC; daylight savings time begins on the last Sunday in March at 2AM
CET and ends on the last Sunday in October at 3AM CEST.

The four timezone names `EST5EDT`,
`CST6CDT`, `MST7MDT`,
and `PST8PDT` look like they are POSIX zone
specifications.  However, they actually are treated as named time zones
because (for historical reasons) there are files by those names in the
IANA time zone database.  The practical implication of this is that
these zone names will produce valid historical USA daylight-savings
transitions, even when a plain POSIX specification would not.

One should be wary that it is easy to misspell a POSIX-style time zone
specification, since there is no check on the reasonableness of the
zone abbreviation(s).  For example, `SET TIMEZONE TO
FOOBAR0` will work, leaving the system effectively using a
rather peculiar abbreviation for UTC.

## History of Units

The SQL standard states that "Within the definition of a
datetime literal", the "datetime
values" are constrained by the natural rules for dates and
times according to the Gregorian calendar.
PostgreSQL follows the SQL
standard's lead by counting dates exclusively in the Gregorian
calendar, even for years before that calendar was in use.
This rule is known as the *proleptic Gregorian calendar*.

The Julian calendar was introduced by Julius Caesar in 45 BC.
It was in common use in the Western world
until the year 1582, when countries started changing to the Gregorian
calendar.  In the Julian calendar, the tropical year is
approximated as 365 1/4 days = 365.25 days. This gives an error of
about 1 day in 128 years.

The accumulating calendar error prompted
Pope Gregory XIII to reform the calendar in accordance with
instructions from the Council of Trent.
In the Gregorian calendar, the tropical year is approximated as
365 + 97 / 400 days = 365.2425 days. Thus it takes approximately 3300
years for the tropical year to shift one day with respect to the
Gregorian calendar.

The approximation 365+97/400 is achieved by having 97 leap years
every 400 years, using the following rules:

So, 1700, 1800, 1900, 2100, and 2200 are not leap years. But 1600,
2000, and 2400 are leap years.

By contrast, in the older Julian calendar all years divisible by 4 are leap
years.

The papal bull of February 1582 decreed that 10 days should be dropped
from October 1582 so that 15 October should follow immediately after
4 October.
This was observed in Italy, Poland, Portugal, and Spain. Other Catholic
countries followed shortly after, but Protestant countries were
reluctant to change, and the Greek Orthodox countries didn't change
until the start of the 20th century.

The reform was observed by Great Britain and its dominions (including what
is now the USA) in 1752.
Thus 2 September 1752 was followed by 14 September 1752.

This is why Unix systems that have the `cal` program
produce the following:

```
$ cal 9 1752
September 1752
S  M Tu  W Th  F  S
1  2 14 15 16
17 18 19 20 21 22 23
24 25 26 27 28 29 30
```

But, of course, this calendar is only valid for Great Britain and
dominions, not other places.
Since it would be difficult and confusing to try to track the actual
calendars that were in use in various places at various times,
PostgreSQL does not try, but rather follows the Gregorian
calendar rules for all dates, even though this method is not historically
accurate.

Different calendars have been developed in various parts of the
world, many predating the Gregorian system.

For example,
the beginnings of the Chinese calendar can be traced back to the 14th
century BC. Legend has it that the Emperor Huangdi invented that
calendar in 2637 BC.

The People's Republic of China uses the Gregorian calendar
for civil purposes. The Chinese calendar is used for determining
festivals.

## Julian Dates

The *Julian Date* system is a method for
numbering days.  It is
unrelated to the Julian calendar, though it is confusingly
named similarly to that calendar.
The Julian Date system was invented by the French scholar
Joseph Justus Scaliger (1540–1609)
and probably takes its name from Scaliger's father,
the Italian scholar Julius Caesar Scaliger (1484–1558).

In the Julian Date system, each day has a sequential number, starting
from JD 0 (which is sometimes called *the* Julian Date).
JD 0 corresponds to 1 January 4713 BC in the Julian calendar, or
24 November 4714 BC in the Gregorian calendar.  Julian Date counting
is most often used by astronomers for labeling their nightly observations,
and therefore a date runs from noon UTC to the next noon UTC, rather than
from midnight to midnight: JD 0 designates the 24 hours from noon UTC on
24 November 4714 BC to noon UTC on 25 November 4714 BC.

Although PostgreSQL supports Julian Date notation for
input and output of dates (and also uses Julian dates for some internal
datetime calculations), it does not observe the nicety of having dates
run from noon to noon.  PostgreSQL treats a Julian Date
as running from local midnight to local midnight, the same as a normal
date.

This definition does, however, provide a way to obtain the astronomical
definition when you need it: do the arithmetic in time
zone `UTC+12`.  For example,

```
=> SELECT extract(julian from '2021-06-23 7:00:00-04'::timestamptz at time zone 'UTC+12');
extract
------------------------------
2459388.95833333333333333333
(1 row)
=> SELECT extract(julian from '2021-06-23 8:00:00-04'::timestamptz at time zone 'UTC+12');
extract
--------------------------------------
2459389.0000000000000000000000000000
(1 row)
=> SELECT extract(julian from date '2021-06-23');
extract
---------
2459389
(1 row)
```
