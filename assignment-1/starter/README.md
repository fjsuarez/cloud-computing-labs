# Assignment 1 — Containerise and deploy

> Replace every `TODO` and delete this quote block before submitting. The headings below
> map onto the rubric — keeping them makes it hard to lose marks for something you
> actually did. Answer in prose, not bullet fragments.

**Name:** TODO
**Campus:** TODO

## What this is

TODO — two or three sentences. What the application does and what you did to it.

## Build and run it locally

Commands someone else can paste, in order, with no edits beyond a name or a path.

```bash
TODO
```

Expected output:

```
TODO
```

Show the counter surviving a container restart:

```bash
TODO
```

## Configuration

| Variable | Default | What it does |
|:--|:--|:--|
| `GREETING` | | |
| `DATA_DIR` | | |
| `PORT` | | |

## Part B — layers and cache

### B1 — image size

| Build | Size |
|:--|--:|
| Multi-stage (`Dockerfile`) | TODO |
| Naive single-stage | TODO |

Evidence:

```
TODO — paste the output of your own docker image ls / docker history
```

TODO — explain the difference **in terms of layers**: which layers exist in one image and
not the other, and what put them there.

### B2 — changing one line of source

TODO — say which line you changed. Paste the build output. Name the layers that were
rebuilt and the ones that came from cache, and explain why, referring to the **order of
instructions** in your Dockerfile.

```
TODO
```

### B3 — making the cache worse

TODO — show the reordered Dockerfile, paste the build output next to the output from B2,
and state the rule you broke in one sentence.

```
TODO
```

## Part C — Azure

The `az` commands you actually ran, in order:

```bash
TODO
```

Which value you passed as a **secure** environment variable, and how you know it is not
readable afterwards:

TODO

Evidence: see `evidence/` — the checklist in `evidence/README.md` says what to capture.
Replace that file with a short index of what you actually captured.

## Before this went to production

TODO — a short, specific paragraph. Not a list of everything you have ever heard about
production. Pick the two or three things that would actually bite this application first,
and say why.

## AI use

TODO — which tools, for what. Required by the course AI policy; acknowledging use does not
affect your grade. Write "None" if you used none.

## Sources

TODO — anything non-trivial you did not write yourself.
