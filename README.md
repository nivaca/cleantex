# cleantex
Python script to remove unwanted whitespace from LaTeX files produced from TEI

## Usage

```
cleantex.py file.tex              # writes file_out.tex
cleantex.py a.tex b.tex           # writes a_out.tex, b_out.tex
cleantex.py -o clean.tex file.tex # explicit output file
cleantex.py -i file.tex           # overwrite in place
cleantex.py -c file.tex           # print result to stdout
cleantex.py -d file.tex           # show a unified diff, write nothing
cat file.tex | cleantex.py -      # stdin -> stdout
```

Other options: `-s/--suffix` (default `_out`), `-e/--encoding` (default `utf-8`),
`-f/--force` (accept files without a `.tex` extension). Requires Python 3.9+.

Created by [Nicolas Vaughan](http:nicolasvaughan.org) (n.vaughan@oxon.org) in 2020.

License: [CC BY-NC-SA 4.0](https://creativecommons.org/licenses/by-nc-sa/4.0/).
