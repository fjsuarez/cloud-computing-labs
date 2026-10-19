# Group Project — A cloud architecture, built and defended

**25% of the final grade · groups of 4–6**

| Milestone | Segovia | Madrid | Graded |
|:--|:--|:--|:--|
| Architecture walkthrough (Session 8) | Tue 27 Oct | Wed 21 Oct | Feedback only |
| Touchpoint (Session 11) | Wed 11 Nov | Fri 13 Nov | Feedback only |
| Touchpoint (Session 13) | Mon 23 Nov | Wed 25 Nov | Feedback only |
| **Presentation and live demo** (Session 14) | **Mon 30 Nov** | **Wed 2 Dec** | **40%** |
| **Final repository and report** | **Mon 14 Dec, 23:59 CET** | **Wed 16 Dec, 23:59 CET** | **60%** |

This file is the handout. It is the authoritative version — if Blackboard and this file
ever disagree, this file wins. `git pull` to see changes.

## What you are building

An **end-to-end cloud architecture** for a problem your group chooses — designed,
deployed to Azure, costed, and defended.

The course has been adding one layer per block. The project is where they meet:

| Block | What it adds to your project |
|:--|:--|
| Containers (S3–4) | At least one component packaged as an image, in your own registry |
| Public clouds (S5–6) | Service choices, sizes, region, a monthly cost and a composite SLA |
| Serverless (S7–8) | At least one event-driven component on Azure Functions |
| IaaS and automation (S9–11) | The infrastructure created from code, not by hand |
| PaaS and patterns (S12–13) | Managed data stores, and the patterns that let it scale |

Budget about **20 hours of group work** in total. Scope accordingly: a small system that
works and is well argued beats a large one that half-works.

## Minimum requirements

Your system must:

1. Use **at least three distinct Azure services**, each doing real work
2. Include **at least one containerised component**, built from your own Dockerfile and
   pulled from **your own Azure Container Registry**
3. Include **at least one event-driven component** on Azure Functions — triggered by
   something other than a person waiting for an HTTP response
4. Keep its state in a **managed data store** — not in a container or a function
5. Be **reproducible from the repository**: infrastructure from code (Terraform, Bicep, or
   a script of `az` commands at minimum), deployable by someone who is not you
6. Keep **no secrets in the repository** — settings, managed identity or Key Vault
7. Run in **one group member's Azure for Students subscription**, in a region its policy
   allows, within the credit

Anything beyond that is your choice. Choose services because a requirement calls for them,
not to collect logos.

### What makes a good project

- **Real enough to be interesting** — a problem someone would actually want solved
- **Cloud-native** — if it would run identically on one laptop, rethink it
- **Honest** — a known limitation, stated, is worth more than a hidden one

Example shapes, to calibrate scope — not to copy:

- Upload receipts → extract fields with an AI service → store → monthly spending API
- A campus event board: containerised web front end, a database, a nightly digest
  function that emails subscribers
- Sensor or open-data ingestion every few minutes → queue → processing function → a
  dashboard served from a container

## Where you should be now

If you have not started, this is the catch-up list, in order. Everything here is needed
for the walkthrough.

- [ ] **Group** of 4–6, names sent to the instructor
- [ ] **One paragraph** on what the application does, for whom — no technology in it
- [ ] **Component diagram**: services, data stores, and what talks to what
- [ ] Each component mapped to an **Azure service**, its **AWS equivalent**, and labelled
      **always-on** or **event-driven**
- [ ] A **Dockerfile** for one component, building locally, image pushed to your ACR
- [ ] A **monthly cost estimate**, component by component, with sizes justified
- [ ] The **composite SLA** of the main request path
- [ ] For the event-driven parts: the **event source**, the **trigger**, and what happens
      to a **failed event**

The diagram is the bottleneck. Start there.

## Checkpoints — feedback, not marks

Each checkpoint is about **five minutes per group** in class. Bring the current state, not
a polished deck. The point is to hear about problems while they are still cheap to fix.

| Checkpoint | Bring |
|:--|:--|
| **Walkthrough** (S8) | The catch-up list above: paragraph, diagram, service mapping, cost, SLA, one image in ACR |
| **Touchpoint** (S11) | Something deployed and reachable; how you will make it reproducible |
| **Touchpoint** (S13) | The full path working end to end, or a clear list of what is not; your scaling answer |

## Deliverable 1 — Presentation and live demo (40%)

**Session 14: Segovia Mon 30 Nov · Madrid Wed 2 Dec.** In class.

- **8 minutes** of presentation and demo, then **3 minutes** of questions. Timed
- **Live demo** of the deployed system, from Azure, not from a laptop. Have a short
  recording ready in case the network fails — using it is not penalised; needing it
  because nothing was deployed is
- Cover: the problem, the architecture, **one decision you would defend** and **one you
  would change**, and the monthly cost
- **Every member must be able to answer questions about any part of the system**

| Points | Criterion |
|--:|:--|
| 15 | **Demo** — the system works, in Azure, along its main path |
| 10 | **Architecture story** — clear problem, clear diagram, choices tied to requirements |
| 10 | **Questions** — answers show understanding across the whole team |
| 5 | **Timing and delivery** — within time, everyone ready |

## Deliverable 2 — Repository and report (60%)

**Due Segovia Mon 14 Dec · Madrid Wed 16 Dec, 23:59 CET.** One repository per group;
submit the link on Blackboard. Give the instructor read access if it is private.

You may keep improving the system after the presentation. The repository is marked as it
stands at the deadline.

### Repository

```text
README.md            the report — see below
infra/               Terraform, Bicep or scripts that create everything
src/<component>/     one folder per component, each with its Dockerfile or function app
docs/                diagram, evidence screenshots, anything the README links to
```

`.gitignore` must exclude state files, `.env`, `local.settings.json` and keys.

### Report — `README.md`

Aim for what a new team member would need on day one. No page limit; no padding.

1. **Problem** — the paragraph, and who it is for
2. **Architecture** — the diagram, and one line per component: what it does, which
   service runs it, why that service and not the obvious alternative
3. **Azure ↔ AWS** — the same table, with the AWS service you would use for each component
4. **Deploy and tear down** — exact commands, from a fresh clone to a working system and
   back to nothing
5. **Cost** — monthly estimate with assumptions and the pricing source and date; then
   **what you actually spent**, from Cost Management, and why the two differ
6. **Reliability** — composite SLA of the main path, redundancy choice for each data
   store, and what happens to a failed event
7. **Security** — where secrets live, which identities have which roles, at which scope
8. **Scale** — the component that saturates first, with a number, and what you would do
   about it
9. **Limitations** — what does not work, and what you would do with another month
10. **Team** — who did what. A table is fine
11. **AI acknowledgement** — in the course format (Session 1), or a statement that none
    was used

| Points | Criterion |
|--:|:--|
| 20 | **It works and is reproducible** — deploys from the repository as documented; meets the minimum requirements |
| 15 | **Architecture** — service choices justified against requirements and alternatives, including AWS |
| 15 | **Cost and reliability** — estimate sourced and compared to actual spend; SLA and failure handling reasoned, with numbers |
| 10 | **Security and craft** — no secrets committed, least privilege, clean repository, clear report |

## Working in one subscription

- One member **hosts** the group's resource group in their Azure for Students
  subscription. Agree who before you deploy anything
- Add teammates as **Contributor on the resource group**, by **object ID** — student
  accounts cannot look each other up by email:

  ```bash
  az role assignment create --assignee-object-id <teammate-object-id> \
    --assignee-principal-type User --role Contributor \
    --scope $(az group show -n <rg> --query id -o tsv)
  ```

  Each teammate gets their own object ID with `az ad signed-in-user show --query id -o tsv`
- Put a **budget** on the group's resource group (Session 6). The host's credit is the
  only hard stop, and it stops everything that member has
- Tag everything `project=<your-group>`, and **switch off or delete** what you are not
  using. Deploying from code (requirement 5) is what makes deleting safe

## Rules

- **GenAI is permitted** for design and development, with acknowledgement — see the
  report section above. It is **not** permitted during the Session 14 questions
- **Cite** any non-trivial code or configuration you did not write
- Everyone in the group is expected to contribute and to understand the whole system.
  Raise contribution problems with the instructor **early**, not after the deadline
