# Session 8 — Azure Functions in Depth

Today you run **Durable Functions** on your own laptop: the same work done one piece after
another (**chaining**) and all at once (**fan-out / fan-in**), timed. Then you stop the
host halfway through a run and watch it pick up where it left off. Parts 1–3 run locally and
cost nothing. Part 4 deploys to Azure and costs a few cents.

This is the pattern **Assignment 2, Part B** asks for.

## Before you start

You need, on your laptop:

| Tool | Check | If missing |
|:--|:--|:--|
| Azure Functions Core Tools **v4** | `func --version` prints `4.x` | See **Installing Core Tools** below |
| Python **3.11–3.14** | `python3 --version` | Not 3.10: it leaves support on Flex Consumption on 31 Oct 2026. The lab was tested on 3.12 |
| **Azurite**, the storage emulator | — | One of the three options in Setup |

Why a storage emulator? Durable Functions keeps its state — queues of work, the history
of every orchestration — in **Azure Storage**. Locally, Azurite pretends to be that
storage account.

### Installing Core Tools

Pick **one** method and stick with it. Two installs of different kinds on the same machine
fight over `func` on your PATH.

```bash
# Any OS with Node.js (the method the Azure Functions VS Code extension uses)
npm install -g azure-functions-core-tools@4

# macOS
brew tap azure/functions && brew install azure-functions-core-tools@4

# Windows without Node.js: the MSI installer, or  choco install azure-functions-core-tools
```

**It is a big download — about 600 MB.** Do it **before** class, on a good connection. If
`npm install` fails with `TypeError: chalk.red is not a function`, that is the installer's
error handler crashing on top of the real problem: the download dropped. Run the same
command again. If it keeps failing, download the release zip for your OS from
<https://github.com/Azure/azure-functions-core-tools/releases/latest>, unzip it somewhere
permanent, and put that folder on your PATH.

**WSL**: follow the Linux steps *inside* WSL — the `npm` line above works there. A `func`
installed in Windows is not visible from WSL. On Linux, `npm install -g` may need `sudo`
(then add `--unsafe-perm true`), or a Node.js installed with a version manager such as
`fnm` or `nvm`, which needs no `sudo` at all.

Then check, in a **new** terminal:

```bash
func --version      # 4.x
```

If it says `Permission denied` rather than `command not found`, the installer left `func`
non-executable: `chmod +x "$(readlink -f "$(which func)")"`.

Full instructions: <https://learn.microsoft.com/azure/azure-functions/functions-run-local#install-the-azure-functions-core-tools>

## Setup

Use **two terminals**, both in the starter folder.

```bash
cd cloud-computing-labs && git pull
cd session-08/starter

python3 -m venv .venv
source .venv/bin/activate          # Windows PowerShell: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

cp local.settings.example.json local.settings.json
```

`local.settings.json` is your app settings **on your laptop**. It is git-ignored: in a real
project it ends up holding connection strings, so it must never be committed. Today it
only says "use the emulator": `UseDevelopmentStorage=true`.

**Terminal 1 — Azurite.** Pick one:

```bash
docker run --rm -p 10000:10000 -p 10001:10001 -p 10002:10002 \
  mcr.microsoft.com/azure-storage/azurite
# or, with Node.js:
npx azurite --location .azurite --silent
# or: VS Code → Azurite extension → "Azurite: Start"
```

**Terminal 2 — the Functions host.** With the venv activated:

```bash
func start
```

You should see five functions listed: `ping`, `start`, `chain`, `fan_out`, `work`.
Check it answers:

```bash
curl http://localhost:7071/api/ping
```

> `Unable to find project root` — you are not in `session-08/starter`.
> `Connection refused (127.0.0.1:10000)` — Azurite is not running.
> `ModuleNotFoundError: azure.durable_functions` — the venv is not activated in this terminal.

## Part 1 — read it, then predict

Open [`starter/function_app.py`](starter/function_app.py). Five functions, three roles:

| Function | Trigger | Role |
|:--|:--|:--|
| `start` | HTTP `POST /api/start/{orchestrator}` | **Client** — starts an orchestration, returns at once |
| `chain` | Orchestration | **Orchestrator** — calls `work` once per chunk, *one after another* |
| `fan_out` | Orchestration | **Orchestrator** — calls `work` for every chunk, *then waits for all* |
| `work` | Activity | **Activity** — does one chunk: sleeps 2 s, standing in for a slow API call |
| `ping` | HTTP `GET /api/ping` | Nothing — for measuring cold starts in Part 4 |

Compare `chain` and `fan_out`. They differ in **one place**: where the `yield` is.

Before running anything, write down: with 8 chunks of 2 seconds each, how long will
`chain` take? And `fan_out`?

## Part 2 — chaining against fan-out

In a **third** terminal (the venv is not needed — `run.py` is standard library only):

```bash
python3 run.py chain
python3 run.py fan_out
```

`run.py` starts an orchestration, polls its status URL until it finishes, and prints how
long it took. Expected shape:

```text
chain      ~16 s     total 140
fan_out    ~2 s      total 140
```

Same work, same answer, eight times faster. Now push it:

```bash
python3 run.py fan_out --chunks 32
python3 run.py fan_out --chunks 64
```

- Why does 64 chunks not take 2 seconds as well? What is limiting it on your laptop?
- In Azure, what would let it go wider?
- `chain` is what you get if you put `yield` inside the loop. Assignment 2 marks it down.
  Why would someone write it that way by accident?

## Part 3 — replay, and surviving a crash

**Replay.** Look at the `func start` terminal. Each time an orchestrator runs, it logs
`orchestrator running, replaying=...`. Count them for the last `chain` run:

- How many times did `chain` run for 8 chunks? How many of those were replays?
- Why does it run again from the top every time an activity finishes?
- What would go wrong if `chain` called `datetime.now()` or `random.random()` and used
  the result to decide what to do next?

**Durability.** Start a long chain, and kill the host while it runs:

```bash
python3 run.py chain --chunks 10
```

When the log shows `work: chunk 3 finished`, press **Ctrl+C** in the `func start` terminal.
`run.py` says `host unreachable` and keeps asking. Wait ten seconds, then `func start`
again.

**Be patient.** The chunk that was in flight is locked on its queue for **about five
minutes** before another host may take it. Meanwhile, read the logs:

- Which chunks run again after the restart? Which are **not** repeated?
- The total is still 140. Where was the progress kept while nothing was running?
- Five minutes of nothing: acceptable for a nightly report? For a checkout?

## Part 4 — deploy it, and measure a cold start

This part uses Azure. Create the app as in Session 7 — note **2048** MB this time:

```bash
export RG=rg-cc-s08-$USER
export REGION=francecentral
export ST=stcc08$RANDOM$RANDOM
export APP=func-cc-s08-$RANDOM$RANDOM

az group create -n $RG -l $REGION \
  --tags course=cloud-computing owner=$USER session=08
az storage account create -g $RG -n $ST -l $REGION \
  --sku Standard_LRS --allow-blob-public-access false
az functionapp create -g $RG -n $APP --storage-account $ST \
  --flexconsumption-location $REGION --runtime python --runtime-version 3.12 \
  --instance-memory 2048 --disable-app-insights
```

Deploy with **Core Tools** this time, from the starter folder:

```bash
func azure functionapp publish $APP
```

It builds remotely, on Linux, and lists the functions when it finishes. If it says
`Can't find app with name`, the new app is not visible yet: wait a minute and repeat.

Run both orchestrations in the cloud:

```bash
export KEY=$(az functionapp keys list -g $RG -n $APP --query functionKeys.default -o tsv)

python3 run.py chain   --base https://$APP.azurewebsites.net --key $KEY
python3 run.py fan_out --base https://$APP.azurewebsites.net --key $KEY
python3 run.py fan_out --chunks 64 --base https://$APP.azurewebsites.net --key $KEY
```

Then **measure a cold start**. `curl -w` prints how long the request took:

```bash
PING="https://$APP.azurewebsites.net/api/ping?code=$KEY"
for i in 1 2 3; do curl -s -o /dev/null -w "%{time_total} s\n" "$PING"; done
```

Leave the app alone for **at least 30 minutes** — do something else — and run the same
loop again. The first request after idle is the cold start; the next two are warm.

- How much slower was the first request? Run it more than once before you believe it
- What part of that time is your code, and what part is the platform?
- This is exactly what Assignment 2, Part C asks you to measure for **your** function

## Clean up

```bash
az group delete --name $RG --yes --no-wait
```

And on your laptop: **Ctrl+C** in both terminals, then `deactivate`. Azurite's data sits
in `.azurite/` or in the container; delete it or keep it, it is git-ignored and local.
