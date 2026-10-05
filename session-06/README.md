# Session 6 — Overview of Public Clouds (II)

Today you build three small things — a storage account, a container and a budget — and
**measure** them: who may touch them, where the data lives, what the container really
uses, and what each option would cost. Total cost: a few cents, if you clean up.

```bash
cd cloud-computing-labs && git pull
cd session-06

export RG=rg-cc-s06-$USER
export REGION=francecentral          # allowed in every student policy we have seen
export SUB=$(az account show --query id -o tsv)
export ME=$(az account show --query user.name -o tsv)
export OID=$(az ad signed-in-user show --query id -o tsv)

az group create -n $RG -l $REGION \
  --tags course=cloud-computing owner=$USER session=06
```

Student subscriptions do not all allow the same regions. `francecentral` has been in every
one we have checked, but if yours refuses it, intersect your policy with IE's again, as in
Session 2.

## Part 1 — who can do what here?

```bash
az role assignment list --assignee-object-id $OID --all --include-inherited \
  --query "[].{role:roleDefinitionName, scope:scope}" -o table

az role definition list --name Contributor \
  --query "[0].permissions[0].{actions:actions, notActions:notActions}" -o json

az role definition list --name Reader --query "[0].permissions[0].actions" -o json
```

Why `--assignee-object-id` and not `--assignee "$ME"`? Given a name, the CLI first looks
it up in the directory (Microsoft Graph), and student accounts may not read the directory:
you get `Insufficient privileges to complete the operation`. Your own object ID needs no
lookup.

Answer for yourself:

- At which **scope** are you Owner? What does that let you do to every resource group?
- Which permission separates **Contributor** from **Owner**?
- Which role would you give a teammate who only needs to *see* the project's costs?
  (Hint: `az role definition list --query "[?contains(roleName,'Cost')].roleName"`)

## Part 2 — redundancy is a setting, until it is not

```bash
export ST=stcc06$RANDOM$RANDOM          # lowercase and digits, globally unique

az storage account create -g $RG -n $ST -l $REGION \
  --sku Standard_LRS --kind StorageV2 --allow-blob-public-access false

az storage account show -g $RG -n $ST \
  --query "{sku:sku.name, primary:primaryLocation, secondary:secondaryLocation}"
```

Now make it geo-redundant, and look again:

```bash
az storage account update -g $RG -n $ST --sku Standard_GRS
az storage account show -g $RG -n $ST \
  --query "{sku:sku.name, primary:primaryLocation, secondary:secondaryLocation}"
```

The secondary is the **region pair** from Session 5 — for France Central, `francesouth`.
Your policy does not let you *deploy* there, but your data now *lives* there. Data
residency rules care about the second fact.

Now try zone redundancy:

```bash
az storage account update -g $RG -n $ST --sku Standard_ZRS
```

It fails. LRS → GRS adds an asynchronous copy somewhere else; LRS → ZRS means physically
moving the three existing copies into three different buildings. That is a **migration**,
not a setting.

Price the options for yourself:

```bash
curl -sG "https://prices.azure.com/api/retail/prices" \
  --data-urlencode "\$filter=serviceName eq 'Storage' and armRegionName eq '$REGION' \
and productName eq 'General Block Blob v2' and contains(meterName,'Data Stored')" \
  | python3 -c "import json,sys
for x in sorted(json.load(sys.stdin)['Items'], key=lambda x:x['skuName']):
    if x['tierMinimumUnits'] == 0:
        print(f\"{x['skuName']:16} {x['retailPrice']:.4f} USD per {x['unitOfMeasure']}\")"
```

## Part 3 — measure what a container really uses

```bash
export IP=$(az container create -g $RG -n aci-s06 \
  --image mcr.microsoft.com/azuredocs/aci-helloworld --os-type Linux \
  --cpu 1 --memory 1.5 --ports 80 --ip-address Public \
  --restart-policy OnFailure --query ipAddress.ip -o tsv)

echo $IP
for i in $(seq 1 100); do curl -s -o /dev/null http://$IP/; done
```

**Metrics take about five minutes to appear.** Do Part 4, then come back and run:

```bash
az monitor metrics list --offset 30m --interval PT1M \
  --resource $(az container show -g $RG -n aci-s06 --query id -o tsv) \
  --metric CpuUsage MemoryUsage --aggregation Average Maximum \
  --query "value[].{metric:name.value, \
    points:timeseries[0].data[?average!=null].[timeStamp, average, maximum]}"
```

`CpuUsage` is in **millicores** — you requested 1000. `MemoryUsage` is in **bytes** — you
requested 1.5 GiB, which is 1 610 612 736 bytes. If `points` is empty, wait a minute.

Then try to right-size it:

```bash
az container create -g $RG -n aci-s06 \
  --image mcr.microsoft.com/azuredocs/aci-helloworld --os-type Linux \
  --cpu 0.5 --memory 0.5 --ports 80 --ip-address Public --restart-policy OnFailure
```

ACI refuses: CPU and memory cannot change in place. Right-sizing a container group means
**delete and recreate** — which is one more reason the image should hold no state.

## Part 4 — five ways to pay for one VM

[`vm_price_options.py`](vm_price_options.py) queries the public Retail Prices API — no
login, standard library only.

```bash
python3 vm_price_options.py Standard_D2s_v5 francecentral
python3 vm_price_options.py Standard_D2s_v5 eastus
python3 vm_price_options.py Standard_E2s_v5 francecentral
python3 vm_price_options.py Standard_D2ps_v6 francecentral    # Arm
```

Read the script before trusting it. It filters on `armSkuName`, drops Windows, and converts
reservation prices from **per term** to **per hour** — the API reports them as one total.

- At what **utilisation** does the 3-year reservation beat pay-as-you-go?
- How much more does **memory-optimised** (E) cost than general purpose (D) for 2 vCPU?
- How much does **Arm** save? What would your project need to change to use it?

Reservations and Spot are **not available on Azure for Students**. The prices are still
public, and the reasoning is what you will be asked for at work.

## Part 5 — a budget, and what you have spent

`az consumption budget create` fails on current CLI versions with an API-version error.
Call the Consumption API directly:

```bash
cat > budget.json <<EOF
{ "properties": {
    "category": "Cost", "amount": 5, "timeGrain": "Monthly",
    "timePeriod": { "startDate": "2026-10-01T00:00:00Z", "endDate": "2026-12-31T00:00:00Z" },
    "notifications": {
      "actual-50":    { "enabled": true, "operator": "GreaterThan", "threshold": 50,
                        "thresholdType": "Actual",     "contactEmails": ["$ME"] },
      "forecast-100": { "enabled": true, "operator": "GreaterThan", "threshold": 100,
                        "thresholdType": "Forecasted", "contactEmails": ["$ME"] } } } }
EOF

az rest --method put --body @budget.json --url "https://management.azure.com\
/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Consumption\
/budgets/budget-s06?api-version=2023-05-01"
```

The amount is in your **billing currency** — EUR or USD, depending on how your
subscription was set up. Check it:

```bash
az rest --method get --url "https://management.azure.com\
/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Consumption\
/budgets/budget-s06?api-version=2023-05-01" \
  --query "properties.{limit:amount, spent:currentSpend.amount, currency:currentSpend.unit}" \
  -o table
```

`spent` will be zero. Cost data arrives 8–24 hours late and budgets are evaluated once a
day — which is the point of today's slide on why a budget is not a cap.

Now ask **Cost Management** what the whole semester has cost, by service. This is the API
behind the portal's *Cost analysis* blade, and unlike Session 5's `az consumption usage
list`, it does return costs on Azure for Students:

```bash
az rest --method post --headers "ClientType=cc-lab-$USER" \
  --url "https://management.azure.com/subscriptions/$SUB/providers\
/Microsoft.CostManagement/query?api-version=2023-03-01" \
  --body "{\"type\":\"ActualCost\",\"timeframe\":\"Custom\",
    \"timePeriod\":{\"from\":\"2026-08-31T00:00:00Z\",\"to\":\"$(date -u +%Y-%m-%dT00:00:00Z)\"},
    \"dataset\":{\"granularity\":\"None\",
      \"aggregation\":{\"total\":{\"name\":\"Cost\",\"function\":\"Sum\"}},
      \"grouping\":[{\"type\":\"Dimension\",\"name\":\"ServiceName\"}]}}" \
  --query "properties.rows[*].{service:[1], cost:[0], currency:[2]}" -o table
```

**`429 Too Many Requests`** is likely. Cost Management allows only a few queries per minute
per subscription, and shares a quota between every caller that does not identify itself
— which is what the `ClientType` header is for. Wait a minute and retry. Swap
`ServiceName` for `ResourceGroupName` to see cost per lab.

Note `rows[*]`, not `rows[]`. Each row is itself a list, and `[]` would flatten them all
into one list of loose values.

## Part 6 — revise your group project estimate

Take last week's monthly figure and apply today, component by component:

- **Right-size** — what would it actually use? Halve anything you guessed
- **Turn off** — which parts can stop outside demo hours?
- **Redundancy** — LRS, ZRS or GRS for each data store, and why
- **Composite SLA** — multiply the SLAs of the components a request passes through
- **Egress** — how much data leaves, and does it pass the free 100 GB?

Write down the new **monthly cost** and **composite SLA**. Both belong in the Session 8
architecture walkthrough.

## Clean up

Delete the budget **first**:

```bash
az rest --method delete --url "https://management.azure.com\
/subscriptions/$SUB/resourceGroups/$RG/providers/Microsoft.Consumption\
/budgets/budget-s06?api-version=2023-05-01"

az group delete --name $RG --yes --no-wait
az group list -o table
rm -f budget.json
```

A budget is not a resource *inside* the group — it is attached to the group's path. `az
group delete` removes the container and the storage account but leaves the budget
behind, and it reappears if you ever recreate a group with the same name.
