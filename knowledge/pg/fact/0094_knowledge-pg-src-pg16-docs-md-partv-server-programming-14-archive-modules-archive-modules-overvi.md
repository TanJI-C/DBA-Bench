# Overview; Initialization; Check; Archive; Shutdown callbacks

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/14_archive_modules.md`
- Source Title: `Archive Modules`
- Source Heading Path: `Archive Modules > Overview; Initialization; Check; Archive; Shutdown callbacks`
- Source Line Ranges: `25-52, 53-121`
- Chunk ID: `pg16_fact_0094_2a042f8419`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `b93fb63b5875d1d0bb41af9522746cbe8fd43ee1583bba581e0069fd3faea465`

## Retrieval Guidance

- Use When: Implement a PostgreSQL archive module.
- Retrieval Keywords: archive module, archive_library, ArchiveModuleCallbacks, archive_file_cb, check_configured_cb, WAL archive module
- Follow-up Guidance: Use the configuration record for enabling and parameterizing an archive module.
- Classification Note: The chapter documents the C archive-module callback interface and lifecycle.

## Official Source Content

## Initialization Functions

An archive library is loaded by dynamically loading a shared library with the
[guc-archive-library](#guc-archive-library)'s name as the library base name.  The
normal library search path is used to locate the library.  To provide the
required archive module callbacks and to indicate that the library is
actually an archive module, it needs to provide a function named
`_PG_archive_module_init`.  The result of the function
must be a pointer to a struct of type
`ArchiveModuleCallbacks`, which contains everything
that the core code needs to know to make use of the archive module.  The
return value needs to be of server lifetime, which is typically achieved by
defining it as a `static const` variable in global scope.

```
typedef struct ArchiveModuleCallbacks
{
ArchiveStartupCB startup_cb;
ArchiveCheckConfiguredCB check_configured_cb;
ArchiveFileCB archive_file_cb;
ArchiveShutdownCB shutdown_cb;
} ArchiveModuleCallbacks;
typedef const ArchiveModuleCallbacks *(*ArchiveModuleInit) (void);
```

Only the `archive_file_cb` callback is required.  The
others are optional.

## Archive Module Callbacks

The archive callbacks define the actual archiving behavior of the module.
The server will call them as required to process each individual WAL file.

### Startup Callback

The `startup_cb` callback is called shortly after the
module is loaded.  This callback can be used to perform any additional
initialization required.  If the archive module has any state, it can use
`state->private_data` to store it.

```
typedef void (*ArchiveStartupCB) (ArchiveModuleState *state);
```

### Check Callback

The `check_configured_cb` callback is called to determine
whether the module is fully configured and ready to accept WAL files (e.g.,
its configuration parameters are set to valid values).  If no
`check_configured_cb` is defined, the server always
assumes the module is configured.

```
typedef bool (*ArchiveCheckConfiguredCB) (ArchiveModuleState *state);
```

If `true` is returned, the server will proceed with
archiving the file by calling the `archive_file_cb`
callback.  If `false` is returned, archiving will not
proceed, and the archiver will emit the following message to the server log:

```
WARNING:  archive_mode enabled, yet archiving is not configured
```

In the latter case, the server will periodically call this function, and
archiving will proceed only when it returns `true`.

### Archive Callback

The `archive_file_cb` callback is called to archive a
single WAL file.

```
typedef bool (*ArchiveFileCB) (ArchiveModuleState *state, const char *file, const char *path);
```

If `true` is returned, the server proceeds as if the file
was successfully archived, which may include recycling or removing the
original WAL file.  If `false` is returned, the server will
keep the original WAL file and retry archiving later.
`file` will contain just the file name of the WAL
file to archive, while `path` contains the full
path of the WAL file (including the file name).

### Shutdown Callback

The `shutdown_cb` callback is called when the archiver
process exits (e.g., after an error) or the value of
[guc-archive-library](#guc-archive-library) changes.  If no
`shutdown_cb` is defined, no special action is taken in
these situations.  If the archive module has any state, this callback should
free it to avoid leaks.

```
typedef void (*ArchiveShutdownCB) (ArchiveModuleState *state);
```
