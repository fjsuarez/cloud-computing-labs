# Session 7 — Serverless Architectures

Today you deploy three functions to **Azure Functions on the Flex Consumption plan**: an
HTTP endpoint, an HTTP endpoint that puts work on a queue, and a worker that takes it off.
Then you break the worker on purpose and see where the failed work goes. Total cost: a few
cents at most, if you clean up.

## Setup — start this first

Creating the function app takes about **three minutes**. Start it, then read Part 1 while
it runs.

```bash
cd cloud-computing-labs && git pull
cd session-07/starter

export RG=rg-cc-s07-$USER
export REGION=francecentral
export ST=stcc07$RANDOM$RANDOM            # lowercase and digits, globally unique
export APP=func-cc-s07-$RANDOM$RANDOM     # becomes $APP.azurewebsites.net

az group create -n $RG -l $REGION \
  --tags course=cloud-computing owner=$USER session=07
az storage account create -g $RG -n $ST -l $REGION \
  --sku Standard_LRS --allow-blob-public-access false
az functionapp create -g $RG -n $APP --storage-account $ST \
  --flexconsumption-location $REGION --runtime python --runtime-version 3.12 \
  --instance-memory 512 --disable-app-insights
```

If the CLI says `unrecognized arguments: --flexconsumption-location`, it is too old for
Flex Consumption. Run `az upgrade` and try again.

If it says `MissingSubscriptionRegistration ... namespace 'Microsoft.Web'`, your
subscription has never created a function app or web app. Register the provider once, wait
for it to finish, and repeat the `az functionapp create`:

```bash
az provider register -n Microsoft.Web --wait
az provider show -n Microsoft.Web --query registrationState -o tsv    # Registered
```

`--disable-app-insights` keeps today fast and free of a Log Analytics workspace. Monitoring
is Session 8.

## Part 1 — read the function before you deploy it

[`starter/function_app.py`](starter/function_app.py) holds three functions. Each one is a
plain Python function with **decorators** that tell Azure what starts it and what it
reads or writes:

| Function | Trigger | Also uses |
|:--|:--|:--|
| `hello` | HTTP `GET /api/hello` | — |
| `place_order` | HTTP `POST /api/orders` | **Queue output** binding → queue `orders` |
| `process_order` | **Queue** `orders` | **Blob output** binding → container `receipts` |

There is no SDK code: no queue client, no blob client. The bindings do that work.
[`host.json`](starter/host.json) pins the **extension bundle**, which is where the queue
and blob bindings come from.

Answer before you run anything:

- Which function answers the client, and which one does the work?
- Where does `place_order` get permission to write to the queue? Every binding says
  `connection="AzureWebJobsStorage"`. Find that setting:

  ```bash
  az functionapp config appsettings list -g $RG -n $APP --query "[].name" -o tsv
  ```

- What will `process_order` do with `{"item": "broken"}`?

## Part 2 — deploy it and call it

```bash
python3 -m zipfile -c ../app.zip function_app.py host.json requirements.txt
az functionapp deployment source config-zip -g $RG -n $APP \
  --src ../app.zip --build-remote true

az functionapp function list -g $RG -n $APP --query "[].name" -o tsv
```

On Windows, use `python` instead of `python3` if that is what your shell has.

The deployment takes a minute or two. `--build-remote true` makes Azure run
`pip install -r requirements.txt` itself, **on Linux**. Packages with compiled parts built
on a Mac or Windows laptop would not run there.

HTTP functions are protected by a **function key** — `AuthLevel.FUNCTION` at the top of
the file. Get the default key and call the API:

```bash
export KEY=$(az functionapp keys list -g $RG -n $APP --query functionKeys.default -o tsv)
export URL=https://$APP.azurewebsites.net/api

curl "$URL/hello?name=Madrid&code=$KEY"
curl -i "$URL/hello"
```

The second call has no key. Look at the status code: was it your code that refused it, or
the platform in front of it?

## Part 3 — a queue between the request and the work

Place three orders. Run this in the same shell where `$URL` and `$KEY` are set:

```bash
for q in 1 2 3; do
  curl -s -X POST "$URL/orders?code=$KEY" -H "Content-Type: application/json" -d "{\"item\":\"coffee\",\"qty\":$q,\"price\":1.8}"
done
```

Each one answers `202 Accepted` at once. The work happens afterwards, in `process_order`.
To see its results you need access to the storage account. The simplest way today is its
**connection string**, which the `az storage` commands pick up from the environment:

```bash
export AZURE_STORAGE_CONNECTION_STRING=$(az storage account show-connection-string \
  -g $RG -n $ST -o tsv)

az storage blob list -c receipts --query "[].name" -o tsv
az storage blob download -c receipts -n <one-of-the-names> -f receipt.json && cat receipt.json
```

That string is a **full-access key** to the account. It is fine in your shell for an hour;
it must never go into code, a commit or a chat. Session 8 replaces it with an identity.

Now send an order the worker cannot process:

```bash
curl -s -X POST "$URL/orders?code=$KEY" -H "Content-Type: application/json" \
  -d '{"item":"broken"}'
```

It is accepted too — `place_order` only checks that the body is JSON. `process_order`
fails on the missing `qty`. The platform puts the message back and tries again, **five
times**, then gives up and moves it to a new queue. Wait a minute, then:

```bash
az storage queue list --query "[].name" -o tsv
az storage message peek -q orders-poison --query "[0].content" -o tsv | base64 -d
```

The Functions host stores queue messages **base64-encoded** — hence the `base64 -d`.

Answer for yourself:

- The client got **202** for the broken order. Who finds out it failed — and how?
- If `process_order` crashed *after* writing the receipt, the message would be retried. How
  many receipts would there be? Change **one line** of the blob output binding so that a
  retry overwrites the receipt instead of adding a new one. (Hint: queue triggers expose
  the message's `{id}` to binding expressions.)

## Part 4 — price your project's idle component

USD list prices, 14 October 2026:

| Meter | Azure Flex Consumption, France Central | AWS Lambda, Paris, x86 |
|:--|--:|--:|
| Per million executions | 0.40 | 0.20 |
| Per GB-second | 0.000026 | 0.0000166667 |
| Free every month | 250,000 executions + 100,000 GB-s | 1 million requests + 400,000 GB-s |

```text
GB-s  = requests per month × seconds per request × GB of memory
cost  = max(0, GB-s − free GB-s) × rate  +  max(0, requests − free requests) × rate
```

Flex Consumption bills at least **1 second** each time an instance becomes active, and
bills an instance once however many requests it is handling at the time. The formula above
treats every request as running alone, so it is an **upper bound** for Flex.

Check the Azure numbers yourself:

```bash
curl -sG "https://prices.azure.com/api/retail/prices" \
  --data-urlencode "\$filter=serviceName eq 'Functions' and armRegionName eq '$REGION'" \
  | python3 -c "import json,sys
for x in json.load(sys.stdin)['Items']:
    print(f\"{x['productName']:18} {x['meterName']:36} from {x['tierMinimumUnits']:>9,.0f}  \
{x['retailPrice']:.7f} per {x['unitOfMeasure']}\")"
```

Read the units: executions are priced **per 10**, so `from 25,000` means from the
250,000th execution. The tier priced at `0` is the free grant.

For the component you brought:

- Estimate **requests a month**, **seconds per request** and **memory**. Say where each
  number comes from
- Price it on **Flex Consumption**, on **Lambda**, and as an always-on **ACI** container
  (Session 6: USD 19.67 a month for 0.5 vCPU and 0.5 GB in France Central)
- Find the **crossover**: at what monthly volume would you move it back to a container?

Write the answer down. It goes into the Session 8 walkthrough.

## Clean up

```bash
unset AZURE_STORAGE_CONNECTION_STRING
az group delete --name $RG --yes --no-wait
rm -f ../app.zip receipt.json
az group list -o table
```

The function app costs nothing while idle. The storage account does: a little per GB, and
a little per **operation** — and the queue trigger polls the queue whether or not anything
arrives. Delete the group.

## Before Session 8

Install **Azure Functions Core Tools v4** and check that `func --version` prints `4.x`.
Session 8 runs functions on your laptop and will not wait for installs.

```bash
npm install -g azure-functions-core-tools@4                       # any OS with Node.js
brew tap azure/functions && brew install azure-functions-core-tools@4   # macOS
```

It is about **600 MB** (3–4 minutes), so do it on a good connection. Recent npm versions
print a long `install-scripts … not yet covered by allowScripts` warning: it is only a
warning. Other platforms, WSL notes and a fallback if the download fails are in the
Session 8 lab README. Microsoft's instructions:
<https://learn.microsoft.com/azure/azure-functions/functions-run-local#install-the-azure-functions-core-tools>
