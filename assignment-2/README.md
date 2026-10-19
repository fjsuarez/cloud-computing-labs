# Assignment 2 — Event-driven processing

**Block 2 · Sessions 5–8 · 5% of the final grade**

| Campus | Published | Due |
|:--|:--|:--|
| Segovia | Wed 14 Oct 2026 | Mon 14 Dec 2026, 23:59 CET |
| Madrid | Wed 14 Oct 2026 | Wed 16 Dec 2026, 23:59 CET |

This file is the brief. It is the authoritative version — if Blackboard and this file ever
disagree, this file wins. Run `git pull` before you start and again before you submit.

> All four assignments are open from 14 October and close on the day of the Knowledge
> Quiz. This one draws on Sessions 7 and 8. You can start before Session 8 — the Session 7
> lab already deploys a Flex Consumption app — but do not leave it until December.

## Context

A dataset arrives as files, irregularly, at unpredictable times. Nobody wants to run a
server that sits idle waiting for them. This is the case serverless was built for.

You will build a pipeline that reacts to arriving data, processes it in parallel, and
records the result — then reason about what it costs and where it breaks.

## Setting up

Work in a **new repository of your own**, exactly as in Assignment 1: not a fork of this
one. There is no starter code. Any CSV with **at least 1,000 rows** of records will do as
input — generate one, or use an open dataset, and say which in your README.

## What to do

### Part A — React to an event

Build an **Azure Function** with a **Blob trigger** that fires when a file is uploaded to
a storage container.

- Deployed to a **Flex Consumption** Function App, Python
- Developed with **Azure Functions Core Tools**, and as much as possible tested locally
- Configuration and connection strings from **application settings**, never in code

Flex Consumption only supports the **Event Grid** source for blob triggers — see
*Platform notes* below.

### Part B — Fan out

The processing step is deliberately parallelisable: each uploaded file contains many
independent records.

Use **Durable Functions** to implement **fan-out / fan-in**:

- An orchestrator reads the file and splits the work
- Activity functions process chunks in parallel
- The orchestrator aggregates the results and writes a summary

### Part C — Reason about cost and behaviour

Answer in your `README.md`:

1. **Cost.** Using the published Azure pricing for **Flex Consumption**, calculate the
   monthly cost of your pipeline under two scenarios: 100 files/month, and 1,000,000
   files/month. Show your working — executions, GB-seconds, and storage. State which
   pricing source and date you used.
2. **Cold start.** Measure it. Invoke your function after it has been idle, then again
   immediately. Report both latencies and explain the difference. Name one architectural
   change that would reduce it and state its cost.
3. **Breaking point.** At what scale does this design stop being the right one? Identify
   the specific limit you would hit first — concurrency, execution duration, storage
   throughput, quota or cost — and justify it with a number.
4. **AWS equivalent.** Describe, in a short paragraph, how you would build the same
   pipeline on AWS. Name the services. You do not need to build it.

## Platform notes

**Creating the app** — as in the Session 7 lab:

```bash
az functionapp create -g $RG -n $APP --storage-account $ST \
  --flexconsumption-location $REGION --runtime python --runtime-version 3.12 \
  --instance-memory 2048
```

**The blob trigger** must declare the Event Grid source:

```python
@app.blob_trigger(arg_name="blob", path="uploads/{name}",
                  connection="AzureWebJobsStorage", source=func.BlobSource.EVENT_GRID)
```

After deploying, subscribe the function to the storage account's `BlobCreated` events.
The webhook key only exists once a blob-triggered function has been deployed:

```bash
az provider register -n Microsoft.EventGrid     # once per subscription

KEY=$(az functionapp keys list -g $RG -n $APP --query systemKeys.blobs_extension -o tsv)
az eventgrid event-subscription create --name uploads \
  --source-resource-id $(az storage account show -g $RG -n $ST --query id -o tsv) \
  --endpoint "https://$APP.azurewebsites.net/runtime/webhooks/blobs?functionName=Host.Functions.<your_function>&code=$KEY" \
  --included-event-types Microsoft.Storage.BlobCreated \
  --subject-begins-with /blobServices/default/containers/uploads/
```

**Testing locally.** Event Grid cannot reach your laptop. Run the orchestration locally
from an **HTTP-triggered starter** that you keep in the app, and verify the blob trigger
itself in Azure.

## Deliverables

A Git repository containing:

- Function source, `host.json`, and `requirements.txt`
- `README.md` covering: how to run locally, how you deployed, and your Part C answers
- Evidence: output showing the orchestration completing, and the resulting summary

Delete your resource group after capturing the evidence.

## Rubric

| Points | Criterion |
|--:|:--|
| 40 | **It works** — blob trigger fires, fan-out/fan-in completes, summary is written |
| 30 | **Technique** — correct Durable Functions patterns, settings not hardcoded, clean local dev setup |
| 20 | **Reasoning** — cost calculation is arithmetically sound and sourced; cold-start measured not asserted; breaking point argued with a number |
| 10 | **Craft** — clear README, no connection strings committed, reproducible setup |

## Common ways to lose marks

- Committing a storage connection string, or a `local.settings.json` that contains one
- Calling activity functions in a loop with `yield` inside it — that is chaining, not
  fan-out, and it will show in your timings
- A cost estimate with no working shown, or no date on the pricing source
- Asserting cold-start behaviour from the lecture instead of measuring your own
- Answering "it breaks at scale" without naming a limit or a number
