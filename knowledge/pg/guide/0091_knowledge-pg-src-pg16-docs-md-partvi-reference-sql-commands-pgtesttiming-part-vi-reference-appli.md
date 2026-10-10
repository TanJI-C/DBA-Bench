# pg_test_timing

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVI_reference/sql_commands/pgtesttiming.md`
- Source Title: `pg_test_timing`
- Source Heading Path: `Part VI Reference > Applications > pg_test_timing`
- Source Line Ranges: `51-136`
- Chunk ID: `pg16_guide_0091_974541e565`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `6f7c18f8107ff9dfd795898b0ab5df11064df9ed2174dd57cadfee50149fb49d`

## Retrieval Guidance

- Use When: Use when validating whether timing measurements are reliable on a host or VM.
- Retrieval Keywords: pg_test_timing, timing overhead, clock source, EXPLAIN ANALYZE timing, system clock
- Follow-up Guidance: Adjust OS clock source only after platform-specific validation.
- Classification Note: Measures timing overhead and clock monotonicity, which affects interpretation of EXPLAIN ANALYZE timing results.

## Official Source Content

# pg_test_timing
Per loop time including overhead: 722.92 ns
Histogram of timing durations:
TSC
```

Other systems may only allow setting the time source on boot.  On older
Linux systems the "clock" kernel setting is the only way to make this sort
of change.  And even on some more recent ones, the only option you'll see
for a clock source is "jiffies".  Jiffies are the older Linux software clock
implementation, which can have good resolution when it's backed by fast
enough timing hardware, as in this example:

```

$ cat /sys/devices/system/clocksource/clocksource0/available_clocksource
jiffies
$ dmesg | grep time.c
time.c: Using 3.579545 MHz WALL PM GTOD PIT/TSC timer.
time.c: Detected 2400.153 MHz processor.
$ pg_test_timing
Testing timing overhead for 3 seconds.
Per timing duration including loop overhead: 97.75 ns
Histogram of timing durations:
< us   % of total      count
1     90.23734   27694571
2      9.75277    2993204
4      0.00981       3010
8      0.00007         22
16      0.00000          1
32      0.00000          1

```

### Clock Hardware and Timing Accuracy

Collecting accurate timing information is normally done on computers using
hardware clocks with various levels of accuracy.  With some hardware the
operating systems can pass the system clock time almost directly to
programs.  A system clock can also be derived from a chip that simply
provides timing interrupts, periodic ticks at some known time interval.  In
either case, operating system kernels provide a clock source that hides
these details.  But the accuracy of that clock source and how quickly it can
return results varies based on the underlying hardware.

Inaccurate time keeping can result in system instability.  Test any change
to the clock source very carefully.  Operating system defaults are sometimes
made to favor reliability over best accuracy. And if you are using a virtual
machine, look into the recommended time sources compatible with it.  Virtual
hardware faces additional difficulties when emulating timers, and there are
often per operating system settings suggested by vendors.

The Time Stamp Counter (TSC) clock source is the most accurate one available
on current generation CPUs. It's the preferred way to track the system time
when it's supported by the operating system and the TSC clock is
reliable. There are several ways that TSC can fail to provide an accurate
timing source, making it unreliable. Older systems can have a TSC clock that
varies based on the CPU temperature, making it unusable for timing. Trying
to use TSC on some older multicore CPUs can give a reported time that's
inconsistent among multiple cores. This can result in the time going
backwards, a problem this program checks for.  And even the newest systems
can fail to provide accurate TSC timing with very aggressive power saving
configurations.

Newer operating systems may check for the known TSC problems and switch to a
slower, more stable clock source when they are seen.  If your system
supports TSC time but doesn't default to that, it may be disabled for a good
reason.  And some operating systems may not detect all the possible problems
correctly, or will allow using TSC even in situations where it's known to be
inaccurate.

The High Precision Event Timer (HPET) is the preferred timer on systems
where it's available and TSC is not accurate.  The timer chip itself is
programmable to allow up to 100 nanosecond resolution, but you may not see
that much accuracy in your system clock.

Advanced Configuration and Power Interface (ACPI) provides a Power
Management (PM) Timer, which Linux refers to as the acpi_pm.  The clock
derived from acpi_pm will at best provide 300 nanosecond resolution.

Timers used on older PC hardware include the 8254 Programmable Interval
Timer (PIT), the real-time clock (RTC), the Advanced Programmable Interrupt
Controller (APIC) timer, and the Cyclone timer.  These timers aim for
millisecond resolution.

## See Also
