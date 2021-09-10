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


def cleanup(buffer: str) -> str:
    patterns: list[tuple[str, str]] = [
        # Remove redundant space around opening braces
        (r" ?{ ?", r"{"),

        # Remove redundant space/NL before closing braces
        (r"\s}", r"}"),

        # Remove redundant space before punctuation
        (r"\s+([\.,\?\!:;])", r"\1"),

        # Remove redundant space between closing brackets and punctuation
        (r"} ([\.,\?\!:;])", r"}\1"),

        # Remove trailing whitespace at paragraph end
        (r"% $", "%"),

        # Remove trailing whitespace at opening parenthesis
        (r"\( +", r"("),
        
        # Remove trailing whitespace at closing parenthesis
        (r" +\)", r")"),
        
        # Remove redundant space before \smnoteanchor.
        # (r"\s*(\\smnoteanchor)", r"%\n% - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -\n\1"),
        (r"\s*(\\smnoteanchor)", r"\1"),
        
        # Break line after colon (but skip citations)
        (r": +(?!\d)", r":\n"),

        # insert NL before \Latquote
        (r"(\\Latquote{)", r"\n\1"),

        # remove space after \label{...}
        (r"(\\label{\w+?}) +", r"\1"),

        # # remove space/NL after ~ 
        (r"~\s+", r"~"),

        # convert to ~ the space/NL before \Link
        (r"\s+\\Link", r"~\\Link"),

        # \emph{ad loc.}
        (r" ad loc.", r" \\emph{ad loc.}"),

        # Fix s.v. string (in refs)
        # s.v.
        (r"s\.v\.", r"\\sv{}"),
        (r"s\.vv\.", r"\\svv{}"),
        
        #
        # DELETE regex -----------------------
        #
        # delete empty \label{}
        (r"\\label\{\}", r""),

        # remove multiple NL after colon
        (r":\n\n", r":\n"),

        # remove space/NL before/after square brackets       
        (r"\s+\]", r"]"),
        (r"\[\s+", r"["),

        #
        # (r"\s+\]", r"]"),
        # (r"\[\s+", r"["),
        # (r"", r""),
        # (r"", r""),
        # (r"", r""),
    ]

    # for i in range(2):
    for pattern, replacement in patterns:
        cpattern = re.compile(pattern, re.MULTILINE)
        buffer = re.sub(cpattern, replacement, buffer)

    return buffer


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

    outbuffer = cleanup(buffer)
    
    with open(outputfile, "w") as f:
        f.write(outbuffer)


if __name__ == "__main__":
    main()
