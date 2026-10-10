# DocBook; Tool Sets; Building with Make; Building with Meson; Documentation Authoring; Style Guide

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVIII_appendixes/09_documentation.md`
- Source Title: `FOP binary distribution`
- Source Heading Path: `Documentation > DocBook; Tool Sets; Building with Make; Building with Meson; Documentation Authoring; Style Guide`
- Source Line Ranges: `20-40, 41-187, 325-349, 350-451`
- Chunk ID: `pg16_fact_0132_a4d6584d44`
- Review Status: `ai_classified`
- Source Extraction: `matched_markdown_sections`
- Official Content SHA256: `ab13b5773353a76723a0b9390c6e2967cf3d5e1fb401d345c55d9b54c3772a7c`

## Retrieval Guidance

- Use When: Build or author PostgreSQL documentation.
- Retrieval Keywords: PostgreSQL documentation, DocBook, documentation build, make docs, meson docs, style guide
- Follow-up Guidance: Treat package installation commands as developer environment setup rather than database remediation.
- Classification Note: The appendix documents the PostgreSQL documentation toolchain, build targets, authoring conventions, and style guidance.

## Official Source Content

## DocBook

The documentation sources are written in
*DocBook*, which is a markup language
defined in XML.  In what
follows, the terms DocBook and XML are both
used, but technically they are not interchangeable.

DocBook allows an author to specify the
structure and content of a technical document without worrying
about presentation details.  A document style defines how that
content is rendered into one of several final forms.  DocBook is
maintained by the [
OASIS group](https://www.oasis-open.org).  The [
official DocBook site](https://www.oasis-open.org/docbook/) has good introductory and reference documentation and
a complete O'Reilly book for your online reading pleasure.
The [
FreeBSD Documentation Project](https://www.freebsd.org/docproj/) also uses DocBook and has some good
information, including a number of style guidelines that might be
worth considering.

## Tool Sets

The following tools are used to process the documentation.  Some
might be optional, as noted.

**[DocBook DTD](https://www.oasis-open.org/docbook/)**
: This is the definition of DocBook itself.  We currently use version
4.5; you cannot use later or earlier versions.  You need
the XML variant of the DocBook DTD, not
the SGML variant.

**[DocBook XSL Stylesheets](https://github.com/docbook/wiki/wiki/DocBookXslStylesheets)**
: These contain the processing instructions for converting the
DocBook sources to other formats, such as
HTML.

The minimum required version is currently 1.77.0, but it is recommended
to use the latest available version for best results.

**[Libxml2](http://xmlsoft.org/) for `xmllint`**
: This library and the `xmllint` tool it contains are
used for processing XML.  Many developers will already
have Libxml2 installed, because it is also
used when building the PostgreSQL code.  Note, however,
that `xmllint` might need to be installed from a
separate subpackage.

**[Libxslt](http://xmlsoft.org/XSLT/) for `xsltproc`**
: `xsltproc` is an XSLT processor, that is, a program to
convert XML to other formats using XSLT stylesheets.

**[FOP](https://xmlgraphics.apache.org/fop/)**
: This is a program for converting, among other things, XML to PDF.
It is needed only if you want to build the documentation in PDF format.

We have documented experience with several installation methods for
the various tools that are needed to process the documentation.
These will be described below.  There might be some other packaged
distributions for these tools. Please report package status to the
documentation mailing list, and we will include that information
here.

### Installation on Fedora, RHEL, and Derivatives

To install the required packages, use:

```
yum install docbook-dtds docbook-style-xsl libxslt fop
```

### Installation on FreeBSD

To install the required packages with `pkg`, use:

```
pkg install docbook-xml docbook-xsl libxslt fop
```

When building the documentation from the `doc`
directory you'll need to use `gmake`, because the
makefile provided is not suitable for FreeBSD's `make`.

### Debian Packages

There is a full set of packages of the documentation tools
available for Debian GNU/Linux.
To install, simply use:

```
apt-get install docbook-xml docbook-xsl libxml2-utils xsltproc fop
```

### macOS

If you use MacPorts, the following will get you set up:

```
sudo port install docbook-xml docbook-xsl-nons libxslt fop
```

If you use Homebrew, use this:

```
brew install docbook docbook-xsl libxslt fop
```

The Homebrew-supplied programs require the following environment variable
to be set.  For Intel based machines, use this:

```
export XML_CATALOG_FILES=/usr/local/etc/xml/catalog
```

On Apple Silicon based machines, use this:

```
export XML_CATALOG_FILES=/opt/homebrew/etc/xml/catalog
```

Without it, `xsltproc` will throw errors like this:

```
I/O error : Attempt to load network entity http://www.oasis-open.org/docbook/xml/4.5/docbookx.dtd
postgres.sgml:21: warning: failed to load external entity "http://www.oasis-open.org/docbook/xml/4.5/docbookx.dtd"
...
```

While it is possible to use the Apple-provided versions
of `xmllint` and `xsltproc`
instead of those from MacPorts or Homebrew, you'll still need
to install the DocBook DTD and stylesheets, and set up a catalog
file that points to them.

### Detection by `configure`

Before you can build the documentation you need to run the
`configure` script, as you would when building
the PostgreSQL programs themselves.
Check the output near the end of the run; it should look something
like this:

```
checking for xmllint... xmllint
checking for xsltproc... xsltproc
checking for fop... fop
checking for dbtoepub... dbtoepub
```

If `xmllint` or `xsltproc` is not
found, you will not be able to build any of the documentation.
`fop` is only needed to build the documentation in
PDF format.
`dbtoepub` is only needed to build the documentation
in EPUB format.

If necessary, you can tell `configure` where to find
these programs, for example

```
./configure ... XMLLINT=/opt/local/bin/xmllint ...
```

If you prefer to build PostgreSQL using
Meson, instead run `meson setup` as described in
[install-meson](#install-meson), and then see
[docguide-build-meson](#docguide-build-meson).

## Documentation Authoring

The documentation sources are most conveniently modified with an editor
that has a mode for editing XML, and even more so if it has some awareness
of XML schema languages so that it can know about
DocBook syntax specifically.

Note that for historical reasons the documentation source files are named
with an extension `.sgml` even though they are now XML
files.  So you might need to adjust your editor configuration to set the
correct mode.

### Emacs

nXML Mode, which ships with
Emacs, is the most common mode for editing
XML documents with Emacs.
It will allow you to use Emacs to insert tags
and check markup consistency, and it supports
DocBook out of the box.  Check the [
nXML manual](https://www.gnu.org/software/emacs/manual/html_mono/nxml-mode.html) for detailed documentation.

`src/tools/editors/emacs.samples` contains
recommended settings for this mode.

## Style Guide

### Reference Pages

Reference pages should follow a standard layout.  This allows
users to find the desired information more quickly, and it also
encourages writers to document all relevant aspects of a command.
Consistency is not only desired among
PostgreSQL reference pages, but also
with reference pages provided by the operating system and other
packages.  Hence the following guidelines have been developed.
They are for the most part consistent with similar guidelines
established by various operating systems.

Reference pages that describe executable commands should contain
the following sections, in this order.  Sections that do not apply
can be omitted.  Additional top-level sections should only be used
in special circumstances; often that information belongs in the
"Usage" section.

**Name**
: This section is generated automatically.  It contains the
command name and a half-sentence summary of its functionality.

**Synopsis**
: This section contains the syntax diagram of the command.  The
synopsis should normally not list each command-line option;
that is done below.  Instead, list the major components of the
command line, such as where input and output files go.

**Description**
: Several paragraphs explaining what the command does.

**Options**
: A list describing each command-line option.  If there are a
lot of options, subsections can be used.

**Exit Status**
: If the program uses 0 for success and non-zero for failure,
then you do not need to document it.  If there is a meaning
behind the different non-zero exit codes, list them here.

**Usage**
: Describe any sublanguage or run-time interface of the program.
If the program is not interactive, this section can usually be
omitted.  Otherwise, this section is a catch-all for
describing run-time features.  Use subsections if appropriate.

**Environment**
: List all environment variables that the program might use.
Try to be complete; even seemingly trivial variables like
`SHELL` might be of interest to the user.

**Files**
: List any files that the program might access implicitly.  That
is, do not list input and output files that were specified on
the command line, but list configuration files, etc.

**Diagnostics**
: Explain any unusual output that the program might create.
Refrain from listing every possible error message.  This is a
lot of work and has little use in practice.  But if, say, the
error messages have a standard format that the user can parse,
this would be the place to explain it.

**Notes**
: Anything that doesn't fit elsewhere, but in particular bugs,
implementation flaws, security considerations, compatibility
issues.

**Examples**
: Examples

**History**
: If there were some major milestones in the history of the
program, they might be listed here.  Usually, this section can
be omitted.

**Author**
: Author (only used in the contrib section)

**See Also**
: Cross-references, listed in the following order: other
PostgreSQL command reference pages,
PostgreSQL SQL command reference
pages, citation of PostgreSQL
manuals, other reference pages (e.g., operating system, other
packages), other documentation.  Items in the same group are
listed alphabetically.

Reference pages describing SQL commands should contain the
following sections: Name, Synopsis, Description, Parameters,
Outputs, Notes, Examples, Compatibility, History, See
Also.  The Parameters section is like the Options section, but
there is more freedom about which clauses of the command can be
listed.  The Outputs section is only needed if the command returns
something other than a default command-completion tag.  The Compatibility
section should explain to what extent
this command conforms to the SQL standard(s), or to which other
database system it is compatible.  The See Also section of SQL
commands should list SQL commands before cross-references to
programs.
