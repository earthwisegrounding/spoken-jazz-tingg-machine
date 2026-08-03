# Spoken Jazz & the tingg* Machine

Promotional site for *Spoken Jazz & the tingg\* Machine* — an epicsodic jazz
audio musical by Bub Pratt.

**Live:** https://tinggmachine.com

## Build

The site is generated from a single source file:

```bash
python3 _src/build.py
```

This writes `index.html` (the deployed site, loading images from `assets/`) and
`_dist/artifact.html` (a single self-contained file with every asset inlined).

- `_src/site.src.html` — the source (edit this)
- `assets/` — images and the opening video
- `index.html` — built output served by GitHub Pages
- `CNAME` — the custom domain; Pages reads it, the build leaves it alone
