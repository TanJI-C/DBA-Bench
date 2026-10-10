# Configuration; plperl.on_init; plperl.on_plperl_init; plperl.on_plperlu_init; plperl.use_strict

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/08_plperl_-_perl_procedural_language.md`
- Source Title: `PL/Perl — Perl Procedural Language`
- Source Heading Path: `PL/Perl - Perl Procedural Language > Configuration; plperl.on_init; plperl.on_plperl_init; plperl.on_plperlu_init; plperl.use_strict`
- Source Line Ranges: `960-1036`
- Chunk ID: `pg16_configuration_0159_c494b2310b`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `817696f215903bee1f6f90c50294a42ae6c085c861246336fda6e168ea994aef`

## Retrieval Guidance

- Use When: Configure PL/Perl interpreter startup, trusted/untrusted initialization, or strict-mode behavior.
- Retrieval Keywords: plperl.on_init, plperl.on_plperl_init, plperl.on_plperlu_init, plperl.use_strict, PL/Perl initialization
- Follow-up Guidance: Review security boundaries before enabling initialization code in untrusted PL/Perl.
- Classification Note: These sections define PL/Perl interpreter initialization and strict-mode GUC behavior.

## Official Source Content

### Configuration

This section lists configuration parameters that affect PL/Perl.

**`plperl.on_init` (`string`)**
: Specifies Perl code to be executed when a Perl interpreter is first
initialized, before it is specialized for use by `plperl` or
`plperlu`.
The SPI functions are not available when this code is executed.
If the code fails with an error it will abort the initialization of
the interpreter and propagate out to the calling query, causing the
current transaction or subtransaction to be aborted.

The Perl code is limited to a single string. Longer code can be placed
into a module and loaded by the `on_init` string.
Examples:

```
plperl.on_init = 'require "plperlinit.pl"'
plperl.on_init = 'use lib "/my/app"; use MyApp::PgInit;'
```

Any modules loaded by `plperl.on_init`, either directly or
indirectly, will be available for use by `plperl`.  This may
create a security risk. To see what modules have been loaded you can use:

```
DO 'elog(WARNING, join ", ", sort keys %INC)' LANGUAGE plperl;
```

Initialization will happen in the postmaster if the `plperl` library is
included in [guc-shared-preload-libraries](#guc-shared-preload-libraries), in which
case extra consideration should be given to the risk of destabilizing
the postmaster.  The principal reason for making use of this feature
is that Perl modules loaded by `plperl.on_init` need be
loaded only at postmaster start, and will be instantly available
without loading overhead in individual database sessions.  However,
keep in mind that the overhead is avoided only for the first Perl
interpreter used by a database session — either PL/PerlU, or
PL/Perl for the first SQL role that calls a PL/Perl function.  Any
additional Perl interpreters created in a database session will have
to execute `plperl.on_init` afresh.  Also, on Windows there
will be no savings whatsoever from preloading, since the Perl
interpreter created in the postmaster process does not propagate to
child processes.

This parameter can only be set in the `postgresql.conf` file or on the server command line.

**`plperl.on_plperl_init` (`string`)**
: These parameters specify Perl code to be executed when a Perl
interpreter is specialized for `plperl` or
`plperlu` respectively.  This will happen when a PL/Perl or
PL/PerlU function is first executed in a database session, or when
an additional interpreter has to be created because the other language
is called or a PL/Perl function is called by a new SQL role.  This
follows any initialization done by `plperl.on_init`.
The SPI functions are not available when this code is executed.
The Perl code in `plperl.on_plperl_init` is executed after
"locking down" the interpreter, and thus it can only perform
trusted operations.

If the code fails with an error it will abort the initialization and
propagate out to the calling query, causing the current transaction or
subtransaction to be aborted.  Any actions already done within Perl
won't be undone; however, that interpreter won't be used again.
If the language is used again the initialization will be attempted
again within a fresh Perl interpreter.

Only superusers can change these settings.  Although these settings
can be changed within a session, such changes will not affect Perl
interpreters that have already been used to execute functions.

**`plperl.use_strict` (`boolean`)**
: When set true subsequent compilations of PL/Perl functions will have
the `strict` pragma enabled.  This parameter does not affect
functions already compiled in the current session.
