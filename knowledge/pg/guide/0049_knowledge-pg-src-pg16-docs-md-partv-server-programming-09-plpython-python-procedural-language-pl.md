# Trapping Errors

## Knowledge Metadata

- Knowledge Type: `guide`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/09_plpython_-_python_procedural_language.md`
- Source Title: `PL/Python — Python Procedural Language`
- Source Heading Path: `PL/Python - Python Procedural Language > Trapping Errors`
- Source Line Ranges: `749-815`
- Chunk ID: `pg16_guide_0049_0fd9b8de94`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `7409acb4e52add16d9ce78d0f4ee5f6b695e5a8b694765e64c25f6d2fcf90552`

## Retrieval Guidance

- Use When: Diagnose failed PL/Python database access or route specific SQL errors to exception handlers.
- Retrieval Keywords: PL/Python error, plpy.SPIError, SQLSTATE, plpy.error, plpy.warning, exception diagnostics
- Follow-up Guidance: Use the error-code appendix to interpret SQLSTATE class and condition names.
- Classification Note: This section describes PL/Python exception classes and SQLSTATE-based error inspection that confirm why a database operation failed.

## Official Source Content

### Trapping Errors

Functions accessing the database might encounter errors, which
will cause them to abort and raise an exception.  Both
`plpy.execute` and
`plpy.prepare` can raise an instance of a subclass of
`plpy.SPIError`, which by default will terminate
the function.  This error can be handled just like any other
Python exception, by using the `try/except`
construct.  For example:

```
CREATE FUNCTION try_adding_joe() RETURNS text AS $$
try:
plpy.execute("INSERT INTO users(username) VALUES ('joe')")
except plpy.SPIError:
return "something went wrong"
else:
return "Joe added"
$$ LANGUAGE plpython3u;
```

The actual class of the exception being raised corresponds to the
specific condition that caused the error.  Refer
to [errcodes-table](#errcodes-table) for a list of possible
conditions.  The module
`plpy.spiexceptions` defines an exception class
for each PostgreSQL condition, deriving
their names from the condition name.  For
instance, `division_by_zero`
becomes `DivisionByZero`, `unique_violation`
becomes `UniqueViolation`, `fdw_error`
becomes `FdwError`, and so on.  Each of these
exception classes inherits from `SPIError`.  This
separation makes it easier to handle specific errors, for
instance:

```
CREATE FUNCTION insert_fraction(numerator int, denominator int) RETURNS text AS $$
from plpy import spiexceptions
try:
plan = plpy.prepare("INSERT INTO fractions (frac) VALUES ($1 / $2)", ["int", "int"])
plpy.execute(plan, [numerator, denominator])
except spiexceptions.DivisionByZero:
return "denominator cannot equal zero"
except spiexceptions.UniqueViolation:
return "already have that fraction"
except plpy.SPIError as e:
return "other error, SQLSTATE %s" % e.sqlstate
else:
return "fraction inserted"
$$ LANGUAGE plpython3u;
```

Note that because all exceptions from
the `plpy.spiexceptions` module inherit
from `SPIError`, an `except`
clause handling it will catch any database access error.

As an alternative way of handling different error conditions, you
can catch the `SPIError` exception and determine
the specific error condition inside the `except`
block by looking at the `sqlstate` attribute of
the exception object.  This attribute is a string value containing
the "SQLSTATE" error code.  This approach provides
approximately the same functionality
