# Assignment 4 — Data pipeline and scale

**Block 4 · Sessions 12–13 · 5% of the final grade**

| Campus | Published | Due |
|:--|:--|:--|
| Segovia | Wed 14 Oct 2026 | Mon 14 Dec 2026, 23:59 CET |
| Madrid | Wed 14 Oct 2026 | Wed 16 Dec 2026, 23:59 CET |

This file is the brief. It is the authoritative version — if Blackboard and this file ever
disagree, this file wins. Run `git pull` before you start and again before you submit.

> All four assignments are open from 14 October and close on the day of the Knowledge
> Quiz. This one draws on Sessions 12 and 13 (Segovia 16 and 23 Nov, Madrid 18 and 25
> Nov). You may start earlier from the documentation; the sessions will catch up with you.

## Context

The final assignment ties the managed-services half of the course together: durable
storage, a database, an AI service, and the design patterns that let a system absorb
traffic it was not sized for.

Scope is deliberately small. **The reasoning carries most of the marks.**

## Setting up

Work in a **new repository of your own**, exactly as in Assignment 1: not a fork of this
one. There is no starter code.

## What to do

### Part A — Store and query

Build a pipeline that:

- Ingests documents or records into **Azure Storage**
- Extracts structured fields and writes them to a **database** (Azure SQL Database,
  Cosmos DB or equivalent)
- Exposes a query endpoint returning results

Requirements:

- Authenticate with **managed identity** where the service supports it — not keys
- Storage uses an appropriate **access tier** and you can justify the choice
- The database schema or partition key is a deliberate decision, not a default

### Part B — Add an AI service

Add one **Azure AI Foundry** capability to the pipeline — summarisation, classification,
extraction or embeddings.

The point is consuming AI as a managed service: you are not training anything.

Handle the things that make AI services different from ordinary APIs:

- **Rate limits** — what happens when you exceed them
- **Latency** — it is far slower than your database
- **Failure** — what your pipeline does when the call fails

### Part C — Design for scale

Answer in your `README.md`. This section is worth the most.

1. **Partitioning.** Your data grows to 500 GB and 50,000 queries/second. State your
   partition key or sharding strategy and justify it against your actual query patterns.
   Identify the query that your choice makes *slow*.
2. **The bottleneck.** Work out which component saturates first as load increases. Show
   the arithmetic — throughput limits, connection limits, or the AI service's tokens per
   minute. Name a number.
3. **A pattern that helps.** Choose **one** of load balancing, API gateway, caching, or
   an event-driven queue. Explain precisely what it fixes in *your* architecture, and
   state what it costs you — latency, consistency, complexity or money.
4. **Placement.** Referring to Session 2: is there any part of this pipeline that belongs
   at the edge rather than in a region? Justify either answer.

## Deliverables

A Git repository containing:

- Pipeline source and any infrastructure configuration
- `README.md` with an architecture diagram (a sketch is fine), run instructions, and your
  Part C answers
- Evidence: the pipeline processing a document end to end, including the AI step

Delete your resource group after capturing the evidence. AI deployments and databases are
the two things in this course most likely to keep costing money after you stop looking.

## Rubric

| Points | Criterion |
|--:|:--|
| 35 | **It works** — ingestion, storage, database write, AI step and query all function |
| 25 | **Technique** — managed identity, deliberate tier and schema choices, rate limits and failures handled |
| 30 | **Reasoning** — Part C partitioning and bottleneck arguments are quantified; the pattern's cost is stated honestly |
| 10 | **Craft** — clear README, diagram present, no keys committed |

## Common ways to lose marks

- Using account keys where managed identity was available
- A partition key chosen because it was unique, with no reference to query patterns
- "It would scale horizontally" as an answer to Part C.2, with no number
- Naming a pattern's benefits and omitting its cost — every one of them has a cost
- No handling for the AI call failing, which it will
