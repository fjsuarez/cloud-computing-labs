# Assignment 1 — Containerise and deploy

**Block 1 · Sessions 1–4 · 5% of the final grade**

| Campus | Published | Due |
|:--|:--|:--|
| Segovia | Mon 21 Sep 2026 | Mon 28 Sep 2026, 23:59 CET |
| Madrid | Wed 23 Sep 2026 | Wed 30 Sep 2026, 23:59 CET |

This file is the brief. It is the authoritative version — if Blackboard and this file ever
disagree, this file wins. Run `git pull` before you start and again before you submit.

## Context

You are given a small working web application that currently runs only on its author's
laptop. Your job is to make it run anywhere, then run it in Azure.

The starter is in `starter/` — the same application you met in the Session 3 lab, so your
lab work carries over. It is deliberately unremarkable: a Python HTTP API with one
dependency and a file it needs to persist.

| Endpoint | Returns |
|:--|:--|
| `GET /` | The greeting and the container's hostname |
| `GET /count` | Increments and returns a counter persisted to disk |
| `GET /healthz` | `{"status": "ok"}` |

| Variable | Default | Purpose |
|:--|:--|:--|
| `GREETING` | `Hello from the container` | Proves configuration comes from outside |
| `DATA_DIR` | `/data` | Where the counter is stored |
| `PORT` | `8000` | Listening port |

Do not rewrite the application. Containerising it is the exercise.

## Setting up

Copy the starter into a **new repository of your own**. Do not fork this repository and do
not commit your work back into it.

```bash
mkdir ~/cc-assignment-1 && cd ~/cc-assignment-1
cp -r /path/to/cloud-computing-labs/assignment-1/starter/. .
git init && git add . && git commit -m "Starter"
```

`starter/README.md` is the skeleton for your submission README. Its headings map onto the
rubric below — keep them and fill them in.

Sanity-check the application without Docker before you containerise it:

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
DATA_DIR=/tmp/ccdata python3 app.py
# in another terminal
curl localhost:8000/ && curl localhost:8000/count
```

## What to do

### Part A — Containerise it

Write a `Dockerfile` that builds the application into an image.

Requirements:

- **Multi-stage build** — build dependencies must not appear in the final image
- Pin the base image to a specific tag, not `latest`
- The container runs as a **non-root user**
- Configuration comes from **environment variables**, not hardcoded values
- The data file persists across container restarts using a **named volume**
- The image exposes the API on a port you map at run time

The non-root and volume requirements interact. A named volume inherits the ownership of
the mount point as it exists in the image — if you create the user after the directory,
your own process will not be able to write to it.

### Part B — Reason about layers

Answer in your `README.md`, with evidence:

1. Report your final image size. Then report the size of a naive single-stage build of
   the same application. Explain the difference in terms of **layers**.
2. Change one line of application source and rebuild. Which layers were rebuilt, and
   which came from cache? Explain why, referring to the order of instructions in your
   Dockerfile.
3. Reorder your Dockerfile to make the cache behave **worse**, show the effect, and
   explain the rule you just broke.

Argue from the `CACHED` markers in your build output, not from wall-clock time. With one
small dependency the timing difference is noise.

### Part C — Deploy to Azure

- Push your image to **Azure Container Registry**
- Run it on **Azure Container Instances** with a public IP
- Inject at least one configuration value as a **secure environment variable**, and show
  that it is not readable afterwards through the control plane
- Show the running application responding to a request

Everything you need for this part is covered in Session 4. The commands from that lab are
the starting point, not the answer — you are deploying your own image, not the demo one.

How you authenticate the pull from ACR is your choice. Whatever you choose, the credential
must not reach your repository.

The ACI filesystem is ephemeral — there is no `docker volume` in Azure. The named volume
requirement in Part A is about running locally. You are not asked to make the counter
survive in ACI; you are expected to know that it will not.

Use a resource group named `rg-cc-a1-<yourname>`, and delete it once your evidence is
captured.

## Deliverables

A Git repository containing:

- `Dockerfile` and any supporting files
- `README.md` covering:
  - How to build and run it locally, in commands someone else can paste
  - Your answers to Part B, with the image sizes and cache output as evidence
  - The `az` commands you used for Part C
  - A short note on what you would change before running this in production
  - Your acknowledgement of any GenAI use — see the AI policy in the Session 1 deck
- Evidence in the `evidence/` folder that ships with the starter: build output for Part B,
  and for Part C terminal output or portal screenshots showing the image in ACR and the
  container running in ACI, plus a successful request to its public IP.
  `evidence/README.md` lists exactly what to capture and what to name it.

Submit the repository link on Blackboard. If it is private, either grant access or submit
a zip.

It must build from a clean clone of your repository. Check this before you submit — the
most common zero is a file that was never committed.

## Rubric

Marked out of 100, scaled to 5% of the final grade. This is the full breakdown your work
is marked against — nothing is held back.

| Points | Criterion |
|--:|:--|
| 40 | **It works** — image builds, container runs locally and in ACI, API responds |
| 30 | **Technique** — multi-stage build, pinned base, non-root user, env-var config, volume used correctly |
| 20 | **Reasoning** — Part B answers demonstrate understanding of layering and cache, backed by evidence |
| 10 | **Craft** — clear README, no secrets committed, sensible `.dockerignore`, tidy history |

A submission that does not execute cannot pass, however elegant the code.

### It works — 40

| Award | For |
|--:|:--|
| 40 | Builds from a clean clone, runs locally, all three endpoints respond, deployed to ACI and evidenced |
| 30 | Works locally and in ACI but needed an undocumented fix to build — a missing file, a wrong path |
| 20 | Works locally; ACI attempted, with evidence of a genuine blocker you documented honestly |
| 10 | Builds, but the container exits or an endpoint returns a 500 |
| 0 | Does not build |

A blocker you diagnosed and wrote up scores. A blocker you stayed silent about does not.

### Technique — 30

Five marks each, checked against the built image rather than against what the README
claims.

| Requirement | Passes if |
|:--|:--|
| Multi-stage | Two or more `FROM` lines, and the final stage genuinely omits the build tooling |
| Pinned base | A specific tag, no `latest` |
| Non-root | `docker exec <container> id` returns a non-zero uid |
| Env-var config | Overriding `GREETING` at run time changes the response |
| Named volume | The counter survives `docker rm -f` followed by a re-run with `-v` |
| Port | `EXPOSE` present, and the published port chosen at `docker run` |

A bind mount to a host path instead of a named volume works, but scores half — it is not
what was asked and it does not travel between machines.

### Reasoning — 20

Where the grades actually spread. All three Part B answers must rest on **your own**
output.

| Award | For |
|--:|:--|
| 18–20 | Explains the mechanism, and accounts for where the size difference actually comes from rather than assuming |
| 14–17 | Correct and evidenced, but the explanation is the general story rather than one about this application |
| 8–13 | Evidence present, explanation thin or partly wrong |
| 4–7 | Answered from the lecture, with no output of your own — or output that does not match your Dockerfile |
| 0–3 | Missing, or fabricated |

Two habits that read as genuine: arguing B3 from the `CACHED` markers rather than from
timings, and being able to say when a multi-stage build *would* pay off more than it does
here.

### Craft — 10

| Points | For |
|--:|:--|
| 4 | The README explains decisions, and someone else can paste your commands and get a running container |
| 3 | No secrets anywhere in the history, `.gitignore` present and doing something |
| 2 | A `.dockerignore` that at minimum excludes `.git`, `.venv`, `__pycache__`, `.env` |
| 1 | More than one commit, with messages that mean something |

### Deductions

| Deduction | Trigger |
|--:|:--|
| Capped at 50 | A live credential committed at any point in the history. Rotate it immediately — the grade is the smaller problem |
| −10 | Resource group still running when the work is marked |
| −5 | No GenAI acknowledgement, in either direction. Declaring use costs nothing; silence is the breach |

## Rules

- **Individual work.** Discussing concepts is fine; sharing code or configuration is not.
- **GenAI is permitted**, with acknowledgement. Acknowledging AI use does not affect your
  grade; failing to acknowledge it is an integrity breach.
- **Cite your sources** for any non-trivial snippet you did not write.
- **Clean up.** Delete your resource group. Marks are not deducted for spend, but running
  out of credit before Assignment 4 is your problem.

## Two things that cost people marks every year

**Build for the right architecture.** ACI runs `linux/amd64`. On an Apple Silicon Mac an
ordinary `docker build` produces `linux/arm64` and the container will crash-loop in Azure
with no useful error:

```bash
docker build --platform linux/amd64 -t cc-demo:1.0 .
```

**Capture evidence as you go.** Part B needs your own build output and Part C needs proof
the thing ran in Azure. Both disappear the moment you close the terminal or delete the
resource group. Fill `evidence/` as you work, not the night before the deadline, and run
`git ls-files evidence/` before you submit to confirm none of it was left untracked.

## Common ways to lose marks

- Committing a secret, an `.env` file, or ACR credentials — this caps the grade at 50, and
  deleting the file later does not help if it is still in the history
- A `README.md` that describes the code instead of explaining the decisions
- Part B answered from memory of the lecture rather than from your own build output
- Attributing the whole of the size difference to one cause without checking how much each
  one actually accounts for
- Running as root because it was easier
- An image that works locally but was never actually deployed

## Teardown

```bash
az group delete --name rg-cc-a1-<yourname> --yes --no-wait
```
