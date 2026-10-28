#!/usr/bin/env python3
"""Remove unwanted whitespace from LaTeX files produced from TEI."""

from __future__ import annotations

import argparse
import difflib
import re
import sys
from pathlib import Path

Rule = tuple[re.Pattern[str], str]


def compile_rules(rules: list[tuple[str, str]]) -> list[Rule]:
    return [(re.compile(pattern, re.MULTILINE), repl) for pattern, repl in rules]


def apply_rules(buffer: str, rules: list[Rule]) -> str:
    for cpattern, replacement in rules:
        buffer = cpattern.sub(replacement, buffer)
    return buffer


# ------------------------------------------------------
# Line-level normalisation (applied first)
WHITESPACE_RULES: list[Rule] = compile_rules([
    # unindent
    (r"^ +", r""),

    # collapse multiple spaces
    (r" {2,}", r" "),
])


# ------------------------------------------------------
LABEL_RULES: list[Rule] = compile_rules([
    # delete empty \smlabel{}
    (r"\\smlabel{}", r""),

    # remove spaces after \smlabel
    (r"(\\smlabel{.+?})\s+?", r"\1"),

    # collapse multiple spaces before \smlabel
    (r"\s+?(\\smlabel)", r"\n\1"),

    # collapse multiple spaces before \linum
    (r"\s+?(\\linum{)", r"\n\1"),

    # ensure two NL for linum in the case of ¶4
    (r"\s+?(\\linum{\d+\w})", r"\n\n\1"),

    # collapse multiple spaces before \linumcom
    (r"\s+?(\\linumcom)", r"\n\n\1"),
])


# ------------------------------------------------------
CLEANUP_RULES: list[Rule] = compile_rules([
    # Remove redundant space around opening braces
    (r" ?{ ?", r"{"),

    # Remove redundant space/NL before closing braces
    (r"\s+?}", r"}"),

    # Remove redundant space before punctuation
    (r"\s+([\.,\?\!:;])", r"\1"),

    # Remove redundant space between closing braces and punctuation
    (r"} ([\.,\?\!:;])", r"}\1"),

    # Remove trailing whitespace at paragraph end
    (r"% $", "%"),

    # Remove trailing whitespace at opening parenthesis
    (r"\( +", r"("),

    # Remove trailing whitespace at closing parenthesis
    (r" +\)", r")"),

    # Remove redundant space before \endnote.
    # (r"\s*(\\endnote)", r"\1"),

    # Remove redundant space before \footnote, \Afootnote, \Bfootnote.
    (r"\s*(\\[AB]?footnote)", r"\1"),

    # Remove redundant space before \absep.
    (r"\s*(\\absep)", r"\1"),

    # Remove redundant space after \nocite.
    (r"(\\nocite{.+?})\s+?", r"\1"),

    # Break line after colon (but skip citations)
    (r": +(?!\d)", r":\n"),

    # insert NL before \Latquote
    (r"(\\Latquote{)", r"\n\1"),

    # insert two NL before \bigskip
    (r"\s*?(\\bigskip{)", r"\n\n\1"),

    # remove multiple space before "\\"
    (r" {2,}\\\\", r" \\\\"),

    # remove space/NL after ~
    (r"~\s+", r"~"),

    # convert to ~ the space/NL before \Link
    (r"\s+\\Link", r"~\\Link"),

    # \emph{ad loc.}
    (r" ad loc\.", r" \\emph{ad loc.}"),

    # Fix s.v. string (in refs)
    (r"s\.v\.", r"\\sv{}"),
    (r"s\.vv\.", r"\\svv{}"),

    # collapse spacing before & after \section
    (r"\s+?(\\section{)", r"\n\n\1"),
    (r"(\\section{¶\d+\.\d+})\s*?", r"\1\n\n"),

    # add NL before \absep
    (r"(\s*?\\absep{})", r"\n\1"),

    # trailing spaces
    (r" \n", r"\n"),

    (r"{\s+?", r"{"),

    # break line after sentence-ending punctuation
    (r"([\.;:]) +?", r"\1\n"),

    # reduce blank lines after punctuation (applied twice on purpose)
    (r"([\.;:])\n{2,}?", r"\1\n"),
    (r"([\.;:])\n{2,}?", r"\1\n"),

    # rejoin lines broken mid-sentence (except comments)
    (r"(^[^%].+?[A-Za-z])\s+?([\\A-Za-z])", r"\1 \2"),

    (r"(\\pend)\s+?", r"\1\n\n"),

    #
    # DELETE regex -----------------------
    #

    # remove multiple NL after colon
    (r":\n\n", r":\n"),

    # remove space/NL before/after square brackets
    (r"\s+\]", r"]"),
    (r"\[\s+", r"["),

    # make "&" a reserved LaTeX symbol (unless already escaped)
    (r"(?<!\\)&", r"\\&"),

    # Put "MS." and "MSS." in smallcaps
    (r"MS\.", r"\\textsc{ms.}"),
    (r"MSS\.", r"\\textsc{mss.}"),
])


# ------------------------------------------------------
def clean(buffer: str) -> str:
    """Run the full cleaning pipeline on a LaTeX source string."""
    buffer = apply_rules(buffer, WHITESPACE_RULES)
    buffer = apply_rules(buffer, LABEL_RULES)
    return apply_rules(buffer, CLEANUP_RULES)


def default_output(path: Path, suffix: str) -> Path:
    return path.with_name(f"{path.stem}{suffix}{path.suffix}")


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="cleantex",
        description="Remove unwanted whitespace from LaTeX files produced from TEI.",
    )
    parser.add_argument(
        "files", nargs="+", type=Path, metavar="FILE",
        help="input .tex file(s); use '-' to read stdin and write stdout",
    )
    target = parser.add_mutually_exclusive_group()
    target.add_argument(
        "-o", "--output", type=Path,
        help="output file (only with a single input file)",
    )
    target.add_argument(
        "-i", "--in-place", action="store_true",
        help="overwrite input files",
    )
    target.add_argument(
        "-c", "--stdout", action="store_true",
        help="write result to stdout",
    )
    target.add_argument(
        "-d", "--diff", action="store_true",
        help="show a unified diff instead of writing files",
    )
    parser.add_argument(
        "-s", "--suffix", default="_out",
        help="suffix for output files (default: %(default)s)",
    )
    parser.add_argument(
        "-e", "--encoding", default="utf-8",
        help="file encoding (default: %(default)s)",
    )
    parser.add_argument(
        "-f", "--force", action="store_true",
        help="process files without a .tex extension",
    )
    args = parser.parse_args(argv)

    if args.output and len(args.files) > 1:
        parser.error("--output can only be used with a single input file")
    if not args.force:
        for path in args.files:
            if str(path) != "-" and path.suffix != ".tex":
                parser.error(f"{path}: not a .tex file (use --force to override)")
    return args


def process(path: Path, args: argparse.Namespace) -> None:
    """Clean one file and write or display the result."""
    if str(path) == "-":
        sys.stdout.write(clean(sys.stdin.read()))
        return

    source = path.read_text(encoding=args.encoding)
    result = clean(source)

    if args.diff:
        sys.stdout.writelines(difflib.unified_diff(
            source.splitlines(keepends=True),
            result.splitlines(keepends=True),
            fromfile=str(path), tofile=f"{path} (cleaned)",
        ))
    elif args.stdout:
        sys.stdout.write(result)
    else:
        if args.in_place:
            outputfile = path
        else:
            outputfile = args.output or default_output(path, args.suffix)
        outputfile.write_text(result, encoding=args.encoding)
        print(f"{path} -> {outputfile}", file=sys.stderr)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    status = 0
    for path in args.files:
        try:
            process(path, args)
        except (OSError, UnicodeDecodeError) as err:
            print(f"cleantex: {path}: {err}", file=sys.stderr)
            status = 1
    return status


if __name__ == "__main__":
    sys.exit(main())
