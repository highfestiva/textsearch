# textsearch

A no-nonsense text search with ok defaults. The way Windows Explorer search should have been. Use
`pip install pyinstaller` to build your own distributable .exe, or use the bundled one.

## Usage

Make current directory root of where you want to search. Run

```bash
$ ./textsearch.py searchstring
```

All reasonable files under the current directories will be case-sensitive searched for `searchstring`.
It will ignore .git and .svn directories and ignore large files (>1M).
