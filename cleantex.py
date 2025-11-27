#!/usr/bin/env python3

import re
import sys


def rmmultispaces(lines: list) -> list:
    temp = []
    cpattern = re.compile(" +")
    for line in lines:
        temp.append(re.sub(cpattern, r" ", line))
    return temp


def unindent(lines: list) -> list:
    temp = []
    cpattern = re.compile("^ +")
    for line in lines:
        temp.append(re.sub(cpattern, r"", line))
    return temp


# ------------------------------------------------------
def fixlabels(buffer: str) -> str:
    patterns: list[tuple[str, str]] = [
 
        # delete empty \smlabel{}
        (r"\\smlabel{}", r""),

        # remove spaces after \smlabel
        (r"(\\smlabel{.+?})\s+?", r"\1"),

        # collapse multiple spaces before \smlabel
        (r"\s+?(\\smlabel)", r"\n\1"),
        
        # collase multiple spaces before \linum
        (r"\s+?(\\linum{)", r"\n\1"),

        # ensure two NL for linum in the case of ¶4
        (r"\s+?(\\linum{\d+\w})", r"\n\n\1"),

        # collase multiple spaces before \linumcom
        (r"\s+?(\\linumcom)", r"\n\n\1"),

    ]


    for pattern, replacement in patterns:
        cpattern = re.compile(pattern, re.MULTILINE)
        buffer = re.sub(cpattern, replacement, buffer)

    return buffer

# ------------------------------------------------------
def cleanup(buffer: str) -> str:
    patterns: list[tuple[str, str]] = [
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

        # Remove redundant space before \footnote.
        (r"\s*(\\footnote)", r"\1"),
        (r"\s*(\\Afootnote)", r"\1"),
        (r"\s*(\\Bfootnote)", r"\1"),

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

        # # remove space/NL after ~
        (r"~\s+", r"~"),

        # convert to ~ the space/NL before \Link
        (r"\s+\\Link", r"~\\Link"),

        # \emph{ad loc.}
        (r" ad loc\.", r" \\emph{ad loc.}"),

        # Fix s.v. string (in refs)
        # s.v.
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
 
        (r"([\.;:]) +?", r"\1\n"),
        
        (r"([\.;:])\n{2,}?", r"\1\n"),
        (r"([\.;:])\n{2,}?", r"\1\n"),

        # (r"(^[^%])(.+?)([A-Za-z])\n{2,}?([\\A-Za-z])", 
            # r"\1 \2"),
        
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

        # make "&" a reserved LaTeX symbol.
        (r"&", r"\&"),

        # Put "MS."" and "MSS." in smallcaps
        (r"MS\.", r"\\textsc{ms.}"),
        (r"MSS\.", r"\\textsc{mss.}"),        
        
    ]

    for pattern, replacement in patterns:
        cpattern = re.compile(pattern, re.MULTILINE)
        buffer = re.sub(cpattern, replacement, buffer)

    return buffer
# ------------------------------------------------------


def main():
    num_args = len(sys.argv)
    inputfile = ""

    if num_args > 1:
        inputfile = sys.argv[1]
    else:
        print("Usage: cleanup.py file.tex")
        exit(0)

    if inputfile[-3:] != "tex":
        print("Usage: cleanup.py file.tex")
        exit(0)

    outputfile = inputfile[0:-4] + "_out.tex"

    with open(inputfile) as f:
        lines = f.readlines()

    lines = unindent(lines)
    lines = rmmultispaces(lines)

    buffer = "".join(lines)

    buffer = fixlabels(buffer)
    buffer = cleanup(buffer)

    with open(outputfile, "w") as f:
        f.write(buffer)


if __name__ == "__main__":
    main()
