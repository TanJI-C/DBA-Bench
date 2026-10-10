# Configuration; Startup Procedures; pltcl.start_proc; pltclu.start_proc

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/07_pltcl_-_tcl_procedural_language.md`
- Source Title: `PL/Tcl — Tcl Procedural Language`
- Source Heading Path: `PL/Tcl - Tcl Procedural Language > Configuration; Startup Procedures; pltcl.start_proc; pltclu.start_proc`
- Source Line Ranges: `382-419`
- Chunk ID: `pg16_configuration_0158_c82eaec851`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `40e0c786c1749ec22f9fc0536e906add172de158066da76a4ba2a56353e45d82`

## Retrieval Guidance

- Use When: Configure PL/Tcl interpreter initialization or module setup behavior.
- Retrieval Keywords: pltcl.start_proc, pltclu.start_proc, PL/Tcl startup procedure, Tcl interpreter initialization
- Follow-up Guidance: Review trusted versus untrusted language implications before changing startup code.
- Classification Note: These sections define PL/Tcl startup procedure settings for trusted and untrusted interpreters.

## Official Source Content

## PL/Tcl Configuration

This section lists configuration parameters that
affect PL/Tcl.

**`pltcl.start_proc` (`string`)**
: This parameter, if set to a nonempty string, specifies the name
(possibly schema-qualified) of a parameterless PL/Tcl function that
is to be executed whenever a new Tcl interpreter is created for
PL/Tcl.  Such a function can perform per-session initialization, such
as loading additional Tcl code.  A new Tcl interpreter is created
when a PL/Tcl function is first executed in a database session, or
when an additional interpreter has to be created because a PL/Tcl
function is called by a new SQL role.

The referenced function must be written in the `pltcl`
language, and must not be marked `SECURITY DEFINER`.
(These restrictions ensure that it runs in the interpreter it's
supposed to initialize.)  The current user must have permission to
call it, too.

If the function fails with an error it will abort the function call
that caused the new interpreter to be created and propagate out to
the calling query, causing the current transaction or subtransaction
to be aborted.  Any actions already done within Tcl won't be undone;
however, that interpreter won't be used again.  If the language is
used again the initialization will be attempted again within a fresh
Tcl interpreter.

Only superusers can change this setting.  Although this setting
can be changed within a session, such changes will not affect Tcl
interpreters that have already been created.

**`pltclu.start_proc` (`string`)**
: This parameter is exactly like `pltcl.start_proc`,
except that it applies to PL/TclU.  The referenced function must
be written in the `pltclu` language.
