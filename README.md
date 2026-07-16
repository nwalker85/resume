# Nathan Walker — Résumé

My résumé, maintained as code. [`resume.md`](resume.md) is the single source of truth; [`resume.pdf`](resume.pdf) is generated from it.

**Executive AI Solutions Architect** — AI governance, agentic systems, and regulated automation. 15+ years turning complex, high-stakes operations into production AI. $50M+ enterprise AI revenue influenced, 100+ production deployments, global solution-architecture practice built 3 → ~50 engineers.

- **Site:** [nwalker.cc](https://nwalker.cc)
- **LinkedIn:** [linkedin.com/in/nwalker85](https://linkedin.com/in/nwalker85)
- **PDF:** [resume.pdf](resume.pdf)

## Build

```bash
pip install -r requirements.txt
python build-resume.py resume.md resume.pdf
```

`build-resume.py` renders the markdown to a formatted PDF with ReportLab. CI rebuilds the PDF on every change to `resume.md` and publishes it as a workflow artifact.

## Why a repo

The résumé is the canonical source that other surfaces consume — nwalker.cc serves the PDF, and the site's assistant answers from `resume.md` as approved public context. Versioned in git, it stays current and auditable instead of scattered across document exports.
