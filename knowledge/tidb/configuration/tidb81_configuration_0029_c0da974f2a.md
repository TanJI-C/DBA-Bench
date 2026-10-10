# Time zone variables, formats, and timestamp behavior

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: TiDB 8.1 official English documentation
- Source Repository: `https://github.com/pingcap/docs`
- Source Commit: `d9124e84872b8f9915123444ab4402f9a36c33c9`
- Source File: `knowledge/tidb_src/configure-time-zone.md`
- Source Title: `Time Zone Support`
- Source Heading Path: `Time Zone Support`
- Source Line Ranges: `5-110`
- Source Scope: `self_managed`
- Primary Component: `tidb`
- Related Components: `sql`, `shared`
- Topic Tags: `time-zone`, `system-variables`, `session-variables`, `global-variables`, `timestamp`, `datetime`, `utc`, `timezone-format`, `data-migration`
- Documentation Version: `8.1`
- Chunk ID: `tidb81_configuration_0029_c0da974f2a`
- Source ID: `tidb-docs-8.1:configure-time-zone.md#time-zone-support`
- Review Status: `reviewed`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `79c591ac6d85a5b8a6fd74833bae7069dbcaa3eda12e2ef299372944e96f3e7d`

## Source Links

- Official Documentation: https://docs.pingcap.com/tidb/stable/configure-time-zone#time-zone-support
- Pinned GitHub Source: https://github.com/pingcap/docs/blob/d9124e84872b8f9915123444ab4402f9a36c33c9/configure-time-zone.md

## Retrieval Guidance

- Use When: Use this chunk when asking how TiDB determines `time_zone`, how to view or set global and session time zone variables, what `SYSTEM` and time zone formats mean, or why `timestamp` and `datetime` display differently across time zones.
- Retrieval Keywords: time_zone, @@global.time_zone, @@session.time_zone, @@global.system_time_zone, SET GLOBAL time_zone = timezone;, SET time_zone = timezone;, SELECT @@global.time_zone, @@session.time_zone, @@global.system_time_zone;, SYSTEM, TZ environment variable, /etc/localtime, UTC, named time zone, offset from UTC, Timestamp, Datetime, NOW(), CURTIME(), data migration time zone
- Follow-up Guidance: The source also states that `Timestamp` conversion is handled based on the current session `time_zone`, and that data migration requires attention to the time zone setting of the primary database and the secondary database.
- Classification Note: This is classified as TiDB configuration content because it defines the global and session `time_zone` system variables, their allowed formats, and their effect on SQL time-related behavior.

## Official Source Content

# Time Zone Support

The time zone in TiDB is decided by the global `time_zone` system variable and the session `time_zone` system variable. The default value of `time_zone` is `SYSTEM`. The actual time zone corresponding to `System` is configured when the TiDB cluster bootstrap is initialized. The detailed logic is as follows:

- Prioritize the use of the `TZ` environment variable.
- If the `TZ` environment variable fails, extract the time zone from the actual soft link address of `/etc/localtime`.
- If both of the above methods fail, use `UTC` as the system time zone.

You can use the following statement to set the global server `time_zone` value at runtime:

```sql
SET GLOBAL time_zone = timezone;
```

Each client has its own time zone setting, given by the session `time_zone` variable. Initially, the session variable takes its value from the global `time_zone` variable, but the client can change its own time zone with this statement:

```sql
SET time_zone = timezone;
```

You can use the following statement to view the current values of the global, client-specific and system time zones:

```sql
SELECT @@global.time_zone, @@session.time_zone, @@global.system_time_zone;
```

To set the format of the value of the `time_zone`:

- The value 'SYSTEM' indicates that the time zone should be the same as the system time zone.
- The value can be given as a string indicating an offset from UTC, such as '+10:00' or '-6:00'.
- The value can be given as a named time zone, such as 'Europe/Helsinki', 'US/Eastern', or 'MET'.

The current session time zone setting affects the display and storage of time values that are zone-sensitive. This includes the values displayed by functions such as `NOW()` or `CURTIME()`.

> **Note:**
>
> Only the values of the Timestamp data type is affected by time zone. This is because the Timestamp data type uses the literal value + time zone information. Other data types, such as Datetime/Date/Time, do not have time zone information, thus their values are not affected by the changes of time zone.

```sql
create table t (ts timestamp, dt datetime);
```

```
Query OK, 0 rows affected (0.02 sec)
```

```sql
set @@time_zone = 'UTC';
```

```
Query OK, 0 rows affected (0.00 sec)
```

```sql
insert into t values ('2017-09-30 11:11:11', '2017-09-30 11:11:11');
```

```
Query OK, 1 row affected (0.00 sec)
```

```sql
set @@time_zone = '+8:00';
```

```
Query OK, 0 rows affected (0.00 sec)
```

```sql
select * from t;
```

```
+---------------------|---------------------+
| ts                  | dt                  |
+---------------------|---------------------+
| 2017-09-30 19:11:11 | 2017-09-30 11:11:11 |
+---------------------|---------------------+
1 row in set (0.00 sec)
```

In this example, no matter how you adjust the value of the time zone, the value of the Datetime data type is not affected. But the displayed value of the Timestamp data type changes if the time zone information changes. In fact, the value that is stored in the storage does not change, it's just displayed differently according to different time zone setting.

> **Note:**
>
> - Time zone is involved during the conversion of the value of Timestamp and Datetime, which is handled based on the current `time_zone` of the session.
> - For data migration, you need to pay special attention to the time zone setting of the primary database and the secondary database.
