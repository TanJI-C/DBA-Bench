# Handling of Invalid or Ambiguous Timestamps

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/02_datetime_support.md`
- Source Title: `02 datetime support`
- Source Heading Path: `Date/Time Support > Handling of Invalid or Ambiguous Timestamps`
- Source Line Ranges: `91-157`
- Chunk ID: `pg16_guide_0054_eb7af896ef`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ebf985f76f48976fa557097661869e804ff784745bb4ab82c513ef23bfe44875`

## Retrieval Guidance

- Use When: Diagnose unexpected timestamp values around daylight-saving-time boundaries.
- Retrieval Keywords: ambiguous timestamp, invalid timestamp, daylight saving time, DST transition, timezone ambiguity, spring forward, fall back
- Follow-up Guidance: Check session TimeZone and timezone_abbreviations before changing application timestamp handling.
- Classification Note: This section describes how PostgreSQL resolves invalid or ambiguous local timestamps around daylight-saving transitions, which helps confirm timestamp interpretation anomalies.

## Official Source Content

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
