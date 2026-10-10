# Environment Variables

## Knowledge Metadata

- Knowledge Type: `configuration`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partV_server_programming/09_plpython_-_python_procedural_language.md`
- Source Title: `PL/Python — Python Procedural Language`
- Source Heading Path: `PL/Python - Python Procedural Language > Environment Variables`
- Source Line Ranges: `989-1015`
- Chunk ID: `pg16_configuration_0160_c6c08a8b66`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `0662d7f7cdae9ace1aad114745d835d85c69eb25cac65be1f880a9b7c6b8eec7`

## Retrieval Guidance

- Use When: Configure or troubleshoot PL/Python interpreter environment dependencies.
- Retrieval Keywords: PL/Python environment variables, PYTHONHOME, PYTHONPATH, Python interpreter environment
- Follow-up Guidance: Validate changes in a controlled environment because interpreter path changes can affect all PL/Python functions.
- Classification Note: This section defines environment-variable behavior that affects the Python interpreter used by PL/Python.

## Official Source Content

## Environment Variables

Some of the environment variables that are accepted by the Python
interpreter can also be used to affect PL/Python behavior.  They
would need to be set in the environment of the main PostgreSQL
server process, for example in a start script.  The available
environment variables depend on the version of Python; see the
Python documentation for details.  At the time of this writing, the
following environment variables have an affect on PL/Python,
assuming an adequate Python version:

- `PYTHONHOME`
- `PYTHONPATH`
- `PYTHONY2K`
- `PYTHONOPTIMIZE`
- `PYTHONDEBUG`
- `PYTHONVERBOSE`
- `PYTHONCASEOK`
- `PYTHONDONTWRITEBYTECODE`
- `PYTHONIOENCODING`
- `PYTHONUSERBASE`
- `PYTHONHASHSEED`

(It appears to be a Python implementation detail beyond the control
of PL/Python that some of the environment variables listed on
the `python` man page are only effective in a
command-line interpreter and not an embedded Python interpreter.)
