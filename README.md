# Quick Change — Peter Turns 47

A one-page site for a birthday puzzle hunt. Solve **Quick Change**, type the answer,
find out where the party is.

Live at https://peterskipper.github.io/pskipis47/

The 2019 version (Peter's 40th) lives on separately at
https://peterskipper.github.io/pskipis40/.

## Editing

There is no build step — no npm, no gulp, no framework. Edit the files and push.

- `index.html` — the entire page. Party details live in the `PARTY` block at the
  top of the `<script>` at the bottom of the file. **Fill in the `TODO_` values
  before sharing the link.**
- `css/style.css` — all styling. Palette and line weights match the puzzle PDF.
- `puzzle/quick-change.pdf` — the puzzle. `quick-change-answer-key.pdf` is linked
  only from behind the third hint.

To preview: open `index.html` in a browser, or `python3 -m http.server` and visit
http://localhost:8000.

## Regenerating the puzzle PDFs

Optional — only needed if the puzzle itself changes.

```bash
pip install reportlab
# download Bangers.ttf from https://fonts.google.com/specimen/Bangers into tools/
python3 tools/make_puzzle.py
```

Writes both PDFs into `puzzle/`.

## The answer

It's in the page source, on purpose. This is a birthday party, not a CTF.
