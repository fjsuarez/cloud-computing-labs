# Assignment 3 — Reproducible infrastructure

**Block 3 · Sessions 9–11 · 5% of the final grade**

| Campus | Published | Due |
|:--|:--|:--|
| Segovia | Wed 14 Oct 2026 | Mon 14 Dec 2026, 23:59 CET |
| Madrid | Wed 14 Oct 2026 | Wed 16 Dec 2026, 23:59 CET |

This file is the brief. It is the authoritative version — if Blackboard and this file ever
disagree, this file wins. Run `git pull` before you start and again before you submit.

> All four assignments are open from 14 October and close on the day of the Knowledge
> Quiz. This one draws on Sessions 9–11 (Linux and Bash, Ansible, Terraform), which run
> until mid-November.

## Context

In Session 2 you tried to create a VM by typing commands. Even when that works, the
machine is undocumented and unreproducible — if it disappears, so does everything you knew
about how it was built.

This assignment closes that gap. **The test is destruction:** tear everything down,
rebuild from code alone, and get an identical system.

## Setting up

Work in a **new repository of your own**, exactly as in Assignment 1: not a fork of this
one. Bring any small web application — your Assignment 1 app is a good choice.

### Find a region where you can create a VM

A VM size has to be **allowed by your subscription's region policy**, **offered** to your
subscription in that region, and **within your vCPU quota**. Check before you write any
Terraform:

```bash
az policy assignment list \
  --query "[].parameters.listOfAllowedLocations.value" -o tsv     # allowed regions

az vm list-skus -l <region> --resource-type virtualMachines \
  --query "[?starts_with(name,'Standard_B') && length(restrictions)==\`0\`].name" -o tsv

az vm list-usage -l <region> -o table                             # vCPU quota
```

Pick the smallest B-series size that passes all three. Put the region and size in
**variables**, not in your resources.

## What to do

### Part A — Provision with Terraform

Write Terraform (or OpenTofu) configuration that creates:

- A resource group, virtual network and subnet
- A network security group allowing only SSH and HTTP
- A small **B-series** Linux VM, with **SSH key** authentication — no passwords
- Any storage the application needs

Requirements:

- **No hardcoded values** — use variables with sensible defaults
- At least one **output** exposing the VM's public IP
- `terraform fmt` clean and `terraform validate` passing

### Part B — Configure with Ansible

Write an Ansible playbook that takes the bare VM and makes it serve your application.

Requirements:

- Uses **modules**, not `shell:` or `command:`, wherever a module exists
- At least one **variable** and one **Jinja2 template** generating a config file
- At least one **control structure** — a loop or a conditional
- **Idempotent** — a second run must report zero changes

### Part C — Prove reproducibility

This is the part being assessed most heavily.

1. `terraform destroy` everything.
2. Rebuild from code alone: `terraform apply`, then the playbook.
3. Capture evidence that the rebuilt system is working.
4. Run the playbook **a second time** and show `changed=0`.

Then answer in your `README.md`:

- **Where is the line?** Terraform provisioned; Ansible configured. State the rule you
  used to decide which tool owned which task, and name one task that could have gone
  either way.
- **Idempotency.** If your first playbook run was not idempotent, what did you change?
  If it was, name the module that would most easily have broken it and explain why.
- **State.** What is in your Terraform state file, why does it matter, and what would go
  wrong if two people ran `apply` at the same time from different machines?

## Deliverables

A Git repository containing:

- `terraform/` with your configuration — **not** the state file or `.terraform/`
- `ansible/` with the playbook, inventory template and Jinja2 templates
- `README.md` with run instructions and your Part C answers
- Evidence: `terraform apply` output, first playbook run, second run showing `changed=0`,
  and the working application after rebuild

**Destroy everything after capturing the evidence.** A VM is billed every second it
exists, used or not — Session 6.

## Rubric

| Points | Criterion |
|--:|:--|
| 40 | **It works** — infrastructure provisions and the playbook configures a working system |
| 30 | **Technique** — variables and outputs used properly, modules over `shell:`, template and control structure present, **idempotency demonstrated** |
| 20 | **Reasoning** — the provisioning/configuration boundary is argued, not asserted; state answer is correct |
| 10 | **Craft** — no state file, private key or secrets committed, `terraform fmt` clean, clear structure |

## Common ways to lose marks

- Committing `terraform.tfstate` — it contains secrets in plain text
- Committing your SSH **private** key
- A playbook of `shell:` tasks, which is a Bash script with extra steps and will not be
  idempotent
- Claiming idempotency without showing the second run
- Never actually running `destroy`, so reproducibility is asserted rather than proven
- Hardcoding a region, a size or your own username throughout
