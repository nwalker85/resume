# Nathan Walker — Résumé

The public résumé, as source. [nwalker.cc](https://nwalker.cc) projects `/resume.pdf` from this repo at deploy time. It does not own a second copy of the hiring artifact.

**Solutions Architect** — enterprise voice AI, contact center automation, and agentic systems. Open to FTE and contract. Austin, TX.

- **Site:** [nwalker.cc](https://nwalker.cc)
- **LinkedIn:** [linkedin.com/in/nwalker85](https://linkedin.com/in/nwalker85)
- **PDF:** [resume.pdf](resume.pdf)

## Source

| File | Role |
|---|---|
| `resume.html` + CSS | Designed two-pager. This is what a hiring manager downloads. |
| `resume.md` | Text form for ATS and approved public context. |
| `resume.pdf` | Chrome-printed projection of the HTML. |

## Build

```bash
./print-resume.sh
```

Requires Chrome, Chromium, or Edge. Do not run `build-resume.py`. That ReportLab path shipped an 8KB stand-in that was not the hiring artifact.

## Why a repo

The résumé is the canonical source other surfaces consume. Versioned in git, it stays current and auditable instead of scattered across document exports. The site is a projection of this repo, not the other way around.
