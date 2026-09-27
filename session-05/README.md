# Session 5 — Overview of Public Clouds (I)

Today is mostly **reading the platform** rather than building on it. Nothing here should
cost more than a few cents.

```bash
export RG=rg-cc-s05-$USER
export REGION=<a region your subscription permits>
```

## Part 1 — map your own hierarchy

```bash
az account show --query "{subscription:name, id:id, tenant:tenantId}" -o json

az group list -o table
az resource list -o table

az account list-locations \
  --query "[?metadata.regionCategory=='Recommended'].name" -o tsv | head -20

az provider list --query "[?registrationState=='Registered'].namespace" -o tsv
```

Answer for yourself: which subscription, which tenant, which regions are permitted, and
which resource providers have you actually switched on?

## Part 2 — tag something, then find it

```bash
az group create -n $RG -l $REGION \
  --tags course=cloud-computing owner=$USER session=05

az group list --tag course=cloud-computing \
  --query "[].{name:name, tags:tags}" -o json

az resource list --tag owner=$USER -o table
```

Add a tag to something that already exists:

```bash
az group update -n $RG --set tags.environment=lab
az group show -n $RG --query tags -o json
```

## Part 3 — price it before you build it

The [Azure Retail Prices API](https://learn.microsoft.com/rest/api/cost-management/retail-prices/azure-retail-prices)
is public and needs no authentication.

```bash
curl -sG "https://prices.azure.com/api/retail/prices" \
  --data-urlencode "\$filter=serviceName eq 'Container Instances' \
and armRegionName eq 'francecentral'" \
  | python3 -m json.tool | head -40
```

Compare regions — including ones you are not allowed to deploy to:

```bash
for R in francecentral westeurope northeurope swedencentral eastus; do
  printf "%-16s" "$R"
  curl -sG "https://prices.azure.com/api/retail/prices" \
    --data-urlencode "\$filter=serviceName eq 'Container Instances' \
and armRegionName eq '$R' and meterName eq 'vCPU Duration'" \
  | python3 -c "import json,sys
items=[x for x in json.load(sys.stdin)['Items'] if x['type']=='Consumption']
p=items[0]['retailPrice']
print(f'{p*36:.4f} USD/vCPU-hour   {p*36*730:7.2f} USD/month')"
done
```

Use `curl -G --data-urlencode`, not a raw URL. The filter contains spaces and quotes; if
you paste them straight into the URL the API returns an empty body and the script fails
with a JSON decode error.

Expected shape of the answer — West Europe costs roughly **31% more than East US** for an
identical container.

Try it for a VM size too:

```bash
curl -sG "https://prices.azure.com/api/retail/prices" \
  --data-urlencode "\$filter=armSkuName eq 'Standard_B1s' \
and armRegionName eq 'francecentral'" \
  | python3 -m json.tool | head -30
```

## Part 4 — what have you already consumed?

```bash
az consumption usage list --top 20 \
  --query "[].{service:consumedService, product:product}" -o table
```

You should see resources from Sessions 2 and 4 — ACI, ACR, storage, App Service.

**On Azure for Students the cost fields come back empty.** Your credit is tracked, but
the per-meter cost API is not populated for this offer type. That is the offer, not your
query. Use **portal → Cost Management → Cost analysis**, or the retail prices above.

## Part 5 — estimate your group project

Take the architecture your group sketched and put a monthly number on it. For each
component decide:

- Which **service** — ACI, App Service, a VM, Functions?
- Which **size** — vCPU and memory
- **How long it runs** — continuously, or only when used?
- Which **region** you are permitted to use

You have $100 for the semester. Better to find out now than in November.

## Clean up

```bash
az group delete --name $RG --yes --no-wait
az group list -o table
```

Check your Assignment 1 resource groups are gone too.
