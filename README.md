# Cloud Computing — Labs

Starter code and reference patterns for **Cloud Computing**, Bachelor in Computer Science
and Artificial Intelligence, IE School of Science & Technology.

Clone this once and pull before each session:

```bash
git clone <this-repo-url> cc-labs
cd cc-labs
git pull          # before every session
```

## Layout

```
patterns/       annotated reference Dockerfiles — read these
session-NN/     starter code and instructions for each session
```

| Session | Lab |
|:--|:--|
| 2 | Compute in the cloud — policy, quota, ACI, Cloud Shell |
| 3 | Docker I — container fundamentals |
| 4 | Docker II — deployment to Azure |
| 5–6 | Public clouds, Azure and AWS, FinOps |
| 7–8 | Serverless |
| 9 | IaaS — Linux and Bash |
| 10–11 | Ansible, Terraform |
| 12–13 | PaaS, design patterns, Azure AI Foundry |

## Conventions

- Every lab creates resources in its **own resource group**, named `rg-cc-<lab>-<yourname>`
- Every lab README ends with a **teardown** section — run it
- Secrets go in `.env`, which is git-ignored. Never commit one.
- Prefer the free tiers. The $100 Azure for Students credit is a safety net, not a budget.

```bash
az group delete --name rg-cc-<lab>-<yourname> --yes --no-wait
```

## Before you start

You need:

- **Docker** — `docker run hello-world` must succeed
- **Azure CLI** — `az account show` must show your subscription as `Enabled`
- **Git** and a GitHub account
- **VS Code**, with the Docker and Azure extensions

### If `docker` says "permission denied" on Linux or WSL

Your user is not in the `docker` group **in this session**. Adding the group is not
enough — the shell has to be restarted to pick it up, and on WSL a new terminal is not
sufficient:

```powershell
wsl --shutdown        # from Windows PowerShell, then reopen
```

### Solutions

Reference solutions are published **after** each assignment deadline. Working from the
starter is the exercise.
