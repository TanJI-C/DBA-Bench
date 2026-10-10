# Message Translation; NLS files; translation workflow

## Knowledge Metadata

- Knowledge Type: `fact`
- Source Corpus: PostgreSQL 16 official documentation
- Source File: `knowledge/pg_src/pg16-docs-md/partVII_internals/06_native_language_support.md`
- Source Title: `Native Language Support`
- Source Heading Path: `Native Language Support > Message Translation; NLS files; translation workflow`
- Source Line Ranges: `1-415`
- Chunk ID: `pg16_fact_0101_880e59e958`
- Review Status: `ai_classified`
- Source Extraction: `full_source_fallback`
- Official Content SHA256: `30fd6ad9e7b80666d9df58b5fd1eb3e139e356d61049d9cd57a80f53b5adb315`

## Retrieval Guidance

- Use When: Understand or maintain PostgreSQL message translations.
- Retrieval Keywords: native language support, NLS, gettext, translation, po file, message catalog
- Follow-up Guidance: Use client/server locale configuration docs outside this source range for operational locale settings.
- Classification Note: The file describes PostgreSQL translation and localization infrastructure as development reference.

## Official Source Content

# Native Language Support

## For the Translator

PostgreSQL
programs (server and client) can issue their messages in
your favorite language — if the messages have been translated.
Creating and maintaining translated message sets needs the help of
people who speak their own language well and want to contribute to
the PostgreSQL effort.  You do not have to be a
programmer at all
to do this.  This section explains how to help.

### Requirements

We won't judge your language skills — this section is about
software tools.  Theoretically, you only need a text editor.  But
this is only in the unlikely event that you do not want to try out
your translated messages.  When you configure your source tree, be
sure to use the `--enable-nls` option.  This will
also check for the libintl library and the
`msgfmt` program, which all end users will need
anyway.  To try out your work, follow the applicable portions of
the installation instructions.

If you want to start a new translation effort or want to do a
message catalog merge (described later), you will need the
programs `xgettext` and
`msgmerge`, respectively, in a GNU-compatible
implementation.  Later, we will try to arrange it so that if you
use a packaged source distribution, you won't need
`xgettext`.  (If working from Git, you will still need
it.)  GNU Gettext 0.10.36 or later is currently recommended.

Your local gettext implementation should come with its own
documentation.  Some of that is probably duplicated in what
follows, but for additional details you should look there.

### Concepts

The pairs of original (English) messages and their (possibly)
translated equivalents are kept in *message
catalogs*, one for each program (although related
programs can share a message catalog) and for each target
language.  There are two file formats for message catalogs:  The
first is the "PO" file (for Portable Object), which
is a plain text file with special syntax that translators edit.
The second is the "MO" file (for Machine Object),
which is a binary file generated from the respective PO file and
is used while the internationalized program is run.  Translators
do not deal with MO files; in fact hardly anyone does.

The extension of the message catalog file is to no surprise either
`.po` or `.mo`.  The base
name is either the name of the program it accompanies, or the
language the file is for, depending on the situation.  This is a
bit confusing.  Examples are `psql.po` (PO file
for psql) or `fr.mo` (MO file in French).

The file format of the PO files is illustrated here:

```
# comment

msgid "original string"
msgstr "translated string"

msgid "more original"
msgstr "another translated"
"string can be broken up like this"

...
```

The msgid lines are extracted from the program source.  (They need not
be, but this is the most common way.)  The msgstr lines are
initially empty and are filled in with useful strings by the
translator.  The strings can contain C-style escape characters and
can be continued across lines as illustrated.  (The next line must
start at the beginning of the line.)

The # character introduces a comment.  If whitespace immediately
follows the # character, then this is a comment maintained by the
translator.  There can also be automatic comments, which have a
non-whitespace character immediately following the #.  These are
maintained by the various tools that operate on the PO files and
are intended to aid the translator.

```
#. automatic comment
#: filename.c:1023
#, flags, flags
```

The #. style comments are extracted from the source file where the
message is used.  Possibly the programmer has inserted information
for the translator, such as about expected alignment.  The #:
comments indicate the exact locations where the message is used
in the source.  The translator need not look at the program
source, but can if there is doubt about the correct
translation.  The #, comments contain flags that describe the
message in some way.  There are currently two flags:
`fuzzy` is set if the message has possibly been
outdated because of changes in the program source.  The translator
can then verify this and possibly remove the fuzzy flag.  Note
that fuzzy messages are not made available to the end user.  The
other flag is `c-format`, which indicates that
the message is a `printf`-style format
template.  This means that the translation should also be a format
string with the same number and type of placeholders.  There are
tools that can verify this, which key off the c-format flag.

### Creating and Maintaining Message Catalogs

OK, so how does one create a "blank" message
catalog?  First, go into the directory that contains the program
whose messages you want to translate.  If there is a file
`nls.mk`, then this program has been prepared
for translation.

If there are already some `.po` files, then
someone has already done some translation work.  The files are
named ``language`.po`,
where `language` is the
[
ISO 639-1 two-letter language code (in lower case)](https://www.loc.gov/standards/iso639-2/php/English_list.php), e.g.,
`fr.po` for French.  If there is really a need
for more than one translation effort per language then the files
can also be named
``language`_`region`.po`
where `region` is the
[
ISO 3166-1 two-letter country code (in upper case)](https://www.iso.org/iso-3166-country-codes.html),
e.g.,
`pt_BR.po` for Portuguese in Brazil.  If you
find the language you wanted you can just start working on that
file.

If you need to start a new translation effort, then first run the
command:

```
make init-po
```

This will create a file
``progname`.pot`.
(`.pot` to distinguish it from PO files that
are "in production". The `T` stands for
"template".)
Copy this file to
``language`.po` and
edit it.  To make it known that the new language is available,
also edit the file `po/LINGUAS` and add the
language (or language and country) code next to languages already listed,
like:

```
de fr
```

(Other languages can appear, of course.)

As the underlying program or library changes, messages might be
changed or added by the programmers.  In this case you do not need
to start from scratch.  Instead, run the command:

```
make update-po
```

which will create a new blank message catalog file (the pot file
you started with) and will merge it with the existing PO files.
If the merge algorithm is not sure about a particular message it
marks it "fuzzy" as explained above.  The new PO file
is saved with a `.po.new` extension.

### Editing the PO Files

The PO files can be edited with a regular text editor. There are also
several specialized editors for PO files which can help the process with
translation-specific features.
There is (unsurprisingly) a PO mode for Emacs, which can be quite
useful.

The translator should only change the area between the quotes after
the msgstr directive, add comments, and alter the fuzzy flag.

The PO files need not be completely filled in.  The software will
automatically fall back to the original string if no translation
(or an empty translation) is available.  It is no problem to
submit incomplete translations for inclusions in the source tree;
that gives room for other people to pick up your work.  However,
you are encouraged to give priority to removing fuzzy entries
after doing a merge.  Remember that fuzzy entries will not be
installed; they only serve as reference for what might be the right
translation.

Here are some things to keep in mind while editing the
translations:

- Make sure that if the original ends with a newline, the
translation does, too.  Similarly for tabs, etc.
- If the original is a `printf` format string, the translation
also needs to be.  The translation also needs to have the same
format specifiers in the same order.  Sometimes the natural
rules of the language make this impossible or at least awkward.
In that case you can modify the format specifiers like this:

```
msgstr "Die Datei %2$s hat %1$u Zeichen."
```

Then the first placeholder will actually use the second
argument from the list.  The
``digits`$` needs to
follow the % immediately, before any other format manipulators.
(This feature really exists in the `printf`
family of functions.  You might not have heard of it before because
there is little use for it outside of message
internationalization.)
- If the original string contains a linguistic mistake, report
that (or fix it yourself in the program source) and translate
normally.  The corrected string can be merged in when the
program sources have been updated.  If the original string
contains a factual mistake, report that (or fix it yourself)
and do not translate it.  Instead, you can mark the string with
a comment in the PO file.
- Maintain the style and tone of the original string.
Specifically, messages that are not sentences (`cannot
open file %s`) should probably not start with a
capital letter (if your language distinguishes letter case) or
end with a period (if your language uses punctuation marks).
It might help to read [error-style-guide](#error-style-guide).
- If you don't know what a message means, or if it is ambiguous,
ask on the developers' mailing list.  Chances are that English
speaking end users might also not understand it or find it
ambiguous, so it's best to improve the message.

## For the Programmer

### Mechanics

This section describes how to implement native language support in a
program or library that is part of the
PostgreSQL distribution.
Currently, it only applies to C programs.

## Adding NLS Support to a Program

Insert this code into the start-up sequence of the program:

```
#ifdef ENABLE_NLS
#include
#endif

...

#ifdef ENABLE_NLS
setlocale(LC_ALL, "");
bindtextdomain("`progname`", LOCALEDIR);
textdomain("`progname`");
#endif
```

(The `progname` can actually be chosen
freely.)

Wherever a message that is a candidate for translation is found,
a call to `gettext()` needs to be inserted.  E.g.:

```
fprintf(stderr, "panic level %d\n", lvl);
```

would be changed to:

```
fprintf(stderr, gettext("panic level %d\n"), lvl);
```

(`gettext` is defined as a no-op if NLS support is
not configured.)

This tends to add a lot of clutter.  One common shortcut is to use:

```
#define _(x) gettext(x)
```

Another solution is feasible if the program does much of its
communication through one or a few functions, such as
`ereport()` in the backend.  Then you make this
function call `gettext` internally on all
input strings.

Add a file `nls.mk` in the directory with the
program sources.  This file will be read as a makefile.  The
following variable assignments need to be made here:

**`CATALOG_NAME`**
: The program name, as provided in the
`textdomain()` call.

**`GETTEXT_FILES`**
: List of files that contain translatable strings, i.e., those
marked with `gettext` or an alternative
solution.  Eventually, this will include nearly all source
files of the program.  If this list gets too long you can
make the first "file" be a `+`
and the second word be a file that contains one file name per
line.

**`GETTEXT_TRIGGERS`**
: The tools that generate message catalogs for the translators
to work on need to know what function calls contain
translatable strings.  By default, only
`gettext()` calls are known.  If you used
`_` or other identifiers you need to list
them here.  If the translatable string is not the first
argument, the item needs to be of the form
`func:2` (for the second argument).
If you have a function that supports pluralized messages,
the item should look like `func:1,2`
(identifying the singular and plural message arguments).

Add a file `po/LINGUAS`, which will contain the list
of provided translations — initially empty.

The build system will automatically take care of building and
installing the message catalogs.

### Message-Writing Guidelines

Here are some guidelines for writing messages that are easily
translatable.

- Do not construct sentences at run-time, like:

```
printf("Files were %s.\n", flag ? "copied" : "removed");
```

The word order within the sentence might be different in other
languages.  Also, even if you remember to call `gettext()` on
each fragment, the fragments might not translate well separately.  It's
better to duplicate a little code so that each message to be
translated is a coherent whole.  Only numbers, file names, and
such-like run-time variables should be inserted at run time into
a message text.
- For similar reasons, this won't work:

```
printf("copied %d file%s", n, n!=1 ? "s" : "");
```

because it assumes how the plural is formed.  If you figured you
could solve it like this:

```
if (n==1)
printf("copied 1 file");
else
printf("copied %d files", n):
```

then be disappointed.  Some languages have more than two forms,
with some peculiar rules.  It's often best to design the message
to avoid the issue altogether, for instance like this:

```
printf("number of copied files: %d", n);
```

If you really want to construct a properly pluralized message,
there is support for this, but it's a bit awkward.  When generating
a primary or detail error message in `ereport()`, you can
write something like this:

```
errmsg_plural("copied %d file",
"copied %d files",
n,
n)
```

The first argument is the format string appropriate for English
singular form, the second is the format string appropriate for
English plural form, and the third is the integer control value
that determines which plural form to use.  Subsequent arguments
are formatted per the format string as usual.  (Normally, the
pluralization control value will also be one of the values to be
formatted, so it has to be written twice.)  In English it only
matters whether `n` is 1 or not 1, but in other
languages there can be many different plural forms.  The translator
sees the two English forms as a group and has the opportunity to
supply multiple substitute strings, with the appropriate one being
selected based on the run-time value of `n`.

If you need to pluralize a message that isn't going directly to an
`errmsg` or `errdetail` report, you have to use
the underlying function `ngettext`.  See the gettext
documentation.
- If you want to communicate something to the translator, such as
about how a message is intended to line up with other output,
precede the occurrence of the string with a comment that starts
with `translator`, e.g.:

```
/* translator: This message is not what it seems to be. */
```

These comments are copied to the message catalog files so that
the translators can see them.
