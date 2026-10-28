# cleantex

Python script to remove unwanted whitespace from LaTeX files produced from TEI.

## Why this script exists

When you produce a LaTeX file from a TEI-XML edition (for example with
`lbp_print` and an XSLT stylesheet), the result normally compiles well, but the
source is very difficult to read. The XML indentation passes directly to the
`.tex` file, so you get lines that begin with many spaces, words separated by
two or three spaces, footnotes that are far away from the word they belong to,
line numbers (`\linum`) lost in the middle of a paragraph, and so on.

LaTeX does not care about most of this, but a human does. If you want to
correct the text by hand, compare two versions with `diff`, or keep the file in
git, it is much better to have a clean source. This is what `cleantex` does: it
takes the "dirty" `.tex` file and gives you back a new one that is tidy and
more regular, with (mostly) one sentence for line.

The script was written for my own editions, so some of the rules are about
specific macros that I use (`\smlabel`, `\linum`, `\Latquote`, `\absep`,
`\Link`, `\pend`...). If you don't use these macros, the rules for them simply
do nothing.

## Requirements

- Python 3.9 or newer.
- No external packages. Only the standard library is used.

## Installation

There is nothing to install, really. You can run the script directly:

```
python3 cleantex.py myfile.tex
```

If you want to use it from anywhere, make it executable and put it (or a link
to it) in some folder that is in your `PATH`:

```
chmod +x cleantex.py
ln -s "$PWD/cleantex.py" ~/.local/bin/cleantex
```

## Basic usage

The most simple case is this:

```
cleantex.py edition.tex
```

This reads `edition.tex` and writes the result in `edition_out.tex`, in the
same folder. The original file is never touched, so you can always compare
the two files and see what the script has changed.

## All the options

| Option | What it does |
|---|---|
| `FILE ...` | One or more input files. They must have the `.tex` extension (see `-f`). Use `-` to read from standard input. |
| `-o FILE`, `--output FILE` | Write the result in this file instead of `name_out.tex`. It only works when you give one input file. |
| `-i`, `--in-place` | Overwrite the input file with the cleaned version. Be careful: there is no backup, so use this only if your file is in git or you have a copy. |
| `-c`, `--stdout` | Print the result on the screen (standard output) and don't write any file. |
| `-d`, `--diff` | Show a unified diff between the original and the cleaned version. Nothing is written. This is very useful to check what the script will do before you use `-i`. |
| `-s SUFFIX`, `--suffix SUFFIX` | The suffix for the output file name. By default it is `_out`, so `a.tex` becomes `a_out.tex`. |
| `-e ENC`, `--encoding ENC` | The encoding of the files, for reading and for writing. By default is `utf-8`. For old files you maybe need `latin-1`. |
| `-f`, `--force` | Accept files that don't finish in `.tex`. |
| `-h`, `--help` | Show the help message. |

Only one of `-o`, `-i`, `-c` and `-d` can be used at the same time.

## Examples

Clean several files in one time. Each one gets its own `_out` file:

```
cleantex.py intro.tex book1.tex book2.tex
```

See what would change, page by page, before writing anything:

```
cleantex.py -d edition.tex | less
```

Give a different name to the output:

```
cleantex.py -o edition-clean.tex edition.tex
```

Clean an old file that is in Latin-1 (ISO-8859-1) and not in UTF-8:

```
cleantex.py -e latin-1 consolatio.tex
```

Use it in a pipe, for example directly after the TEI conversion:

```
some-tei-to-latex-tool edition.xml | cleantex.py - > edition.tex
```

Clean the file in place (only if it is under version control!):

```
cleantex.py -i edition.tex
git diff edition.tex
```

## What the script does, exactly

The cleaning is done in three stages. Each stage is a list of regular
expressions that are applied one after the other, in the order they appear in
the code. The order is important: some rules work only because a previous rule
already prepared the text.

### Stage 1: general whitespace

- The spaces at the beginning of each line (the indentation from the XML) are
  deleted.
- Two or more spaces together become only one space.

### Stage 2: labels and line numbers

- Empty labels `\smlabel{}` are deleted.
- The whitespace after a `\smlabel{...}` is removed.
- Each `\smlabel` and each `\linum{...}` starts in a new line.
- When the line number has a letter (like `\linum{4a}`, which happens in the
  `¶4` case) and also before `\linumcom`, a blank line is inserted, so it
  begins a new paragraph.

### Stage 3: general cleanup

Spaces and punctuation:

- No space after `{` or before `}`, and no space around the opening brace.
- No space before `.`, `,`, `?`, `!`, `:` and `;`, also when they come after a
  closing brace.
- No space after `(` or before `)`, and no space after `[` or before `]`.
- No space or new line after a `~`.
- Trailing spaces at the end of the lines are removed.

Notes and similar commands, which must be "glued" to the previous word:

- `\footnote`, `\Afootnote` and `\Bfootnote`
- The space after `\nocite{...}` is removed.
- `\absep` stays in the same line as the previous word, separated by exactly
  one space.
- The space before `\Link` becomes a non-breaking space `~`.

Lines and paragraphs:

- After `.`, `;` and `:` the line is broken, so you have more or less one
  sentence (or one clause) for line. This makes `diff` much more readable.
- But a line that was broken in the middle of a sentence (between two words)
  is joined again. Lines that begin with `%` (comments) are not touched by
  this rule.
- A colon with a space after it also breaks the line. A colon without space,
  like in the reference `3:14`, is not touched.
- `\section{...}` and `\bigskip` have a blank line before them, and a section
  title like `\section{¶1.2}` has a blank line after.
- `\Latquote{` starts in a new line, and `\pend` is followed by a blank line.

Typographical replacements:

| Original | Result |
|---|---|
| ` ad loc.` | ` \emph{ad loc.}` |
| `s.v.` | `\sv{}` |
| `s.vv.` | `\svv{}` |
| `MS.` | `\textsc{ms.}` |
| `MSS.` | `\textsc{mss.}` |
| `&` | `\&` (only if it is not already escaped) |

Note that `\sv` and `\svv` are not standard LaTeX commands. You must define
them in your preamble, for example like this:

```latex
\newcommand{\sv}{\emph{s.v.}}
\newcommand{\svv}{\emph{s.vv.}}
```

## Things to take in account

The script is made for one specific kind of files, so please read this before
you use it with other documents.

- **Tables and alignment.** Every `&` that is not already escaped becomes
  `\&`. This is correct for the text of an edition, but it will break any
  `tabular`, `align` or other environment that uses `&` for the columns. Don't
  use the script on files with tables, or put the tables in a separate file.
- **Abbreviations.** The rule that breaks the line after a period cannot know
  if the period is the end of a sentence or an abbreviation, so `e.g. this`
  will become two lines. For LaTeX this makes no difference in the PDF, it is
  only how the source looks.
- **Verbatim.** The script doesn't know about `verbatim`, `lstlisting` or
  `minted`. It will clean the code inside them too, and probably damage it.
- **Running it two times.** Normally you run the script one time on the fresh
  file that comes from TEI. Running it again on its own output is mostly
  harmless, but it is not guaranteed that the second result is exactly the same
  as the first one.
- **Encoding.** If the script says something like `'utf-8' codec can't decode
  byte 0xe9`, your file is not in UTF-8. Try again with `-e latin-1`.

## Exit codes

- `0`: everything went well.
- `1`: at least one file could not be read or written (the other files are
  still processed).
- `2`: wrong arguments, for example a file that is not `.tex` without `-f`.

## Using it from Python

You can also import the script and use the `clean()` function directly on a
string:

```python
from cleantex import clean

with open("edition.tex", encoding="utf-8") as f:
    result = clean(f.read())
```

If you want to add your own rules, the simplest way is to add a new
`(pattern, replacement)` pair in the list `CLEANUP_RULES`, in the right
position. Remember that the patterns are compiled with `re.MULTILINE`, so `^`
and `$` match at the beginning and end of each line.

## Author and license

Created by [Nicolas Vaughan](http://nicolasvaughan.org) (n.vaughan@oxon.org) in 2020.

If you use this script in your work, please cite it (see `CITATION.cff`).

This script is distributed under two licenses, and you can choose the one
that is better for you:

- [GNU General Public License v3.0 or later](https://www.gnu.org/licenses/gpl-3.0.html).
  The complete text is in the file `LICENSE`.
- [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).

The program is given without any warranty. Please read the license for the
details.
