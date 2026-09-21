# Session 4 — Docker Lab II: Container Deployment on Azure

Your image leaves your laptop. Push it to a private registry, run it in Azure with no
passwords, give it configuration and durable storage, and take it down again.

**Docker Desktop must be running.** `az acr login` shells out to the `docker` CLI and
fails with a confusing "command could not be found" if the daemon is down.

## Set your variables

```bash
export RG=rg-cc-s04-$USER
export REGION=<a region your subscription permits>
export ACR=crcc$RANDOM
```

Check `$REGION` against your Session 2 notes first:

```bash
az policy assignment list --disable-scope-strict-match \
  --query "[].{policy:displayName, regions:parameters.listOfAllowedLocations.value}" -o json
```

Register the providers if you have not already:

```bash
for P in Microsoft.ContainerRegistry Microsoft.ContainerInstance \
         Microsoft.Storage Microsoft.ManagedIdentity; do
  az provider register --namespace $P --wait
done
```

## Part 1 — push to a registry

```bash
az group create -n $RG -l $REGION
az acr create -g $RG -n $ACR -l $REGION --sku Basic

az acr login -n $ACR

docker tag cc-demo:1.0 $ACR.azurecr.io/cc-demo:1.0
docker push $ACR.azurecr.io/cc-demo:1.0

az acr repository show-tags -n $ACR --repository cc-demo -o table
```

No `cc-demo:1.0`? Rebuild it from `session-03/starter` with the Dockerfile you wrote.

## Part 2 — identity, then deploy

```bash
az identity create -g $RG -n id-cc-aci -l $REGION
export ID_ID=$(az identity show -g $RG -n id-cc-aci --query id -o tsv)
PRINCIPAL=$(az identity show -g $RG -n id-cc-aci --query principalId -o tsv)

az role assignment create \
  --assignee-object-id $PRINCIPAL \
  --assignee-principal-type ServicePrincipal \
  --role AcrPull \
  --scope $(az acr show -n $ACR --query id -o tsv)

az container create -g $RG -n aci-lab -l $REGION \
  --image $ACR.azurecr.io/cc-demo:1.0 --os-type Linux \
  --cpu 1 --memory 1 --ports 8000 --ip-address Public \
  --restart-policy OnFailure \
  --acr-identity $ID_ID --assign-identity $ID_ID
```

No password appeared anywhere in that sequence. That is the point.

`--os-type Linux` is required. Without it you get `InvalidOsType`.

## Part 3 — reach it

```bash
az container show -g $RG -n aci-lab --query instanceView.state -o tsv   # want: Running

IP=$(az container show -g $RG -n aci-lab --query ipAddress.ip -o tsv)
curl http://$IP:8000/

az container logs -g $RG -n aci-lab
```

`ContainerGroupDeploymentNotReady` means it is still starting — wait and retry.

On the campus network `curl` may return "Web Page Blocked". That is IE's proxy, not your
container; `az container logs` still shows the request arriving with a `200`.

## Part 4 — secrets and persistence

```bash
export ST=stcc$RANDOM
az storage account create -g $RG -n $ST -l $REGION --sku Standard_LRS
export KEY=$(az storage account keys list -g $RG -n $ST --query "[0].value" -o tsv)
az storage share create -n ccdata --account-name $ST --account-key "$KEY"

az container create -g $RG -n aci-vol -l $REGION \
  --image $ACR.azurecr.io/cc-demo:1.0 --os-type Linux \
  --cpu 1 --memory 1 --ports 8000 --ip-address Public \
  --acr-identity $ID_ID --assign-identity $ID_ID \
  --environment-variables GREETING="Persisted in Azure Files" \
  --secure-environment-variables API_KEY="super-secret" \
  --azure-file-volume-account-name $ST \
  --azure-file-volume-account-key "$KEY" \
  --azure-file-volume-share-name ccdata \
  --azure-file-volume-mount-path /data
```

## Part 5 — prove both claims

**Can you read the secret back?**

```bash
az container show -g $RG -n aci-vol \
  --query "containers[0].environmentVariables" -o json
```

`GREETING` returns its value. `API_KEY` returns `null` — secure values are write-only.

**Does the data outlive the container?**

```bash
IP=$(az container show -g $RG -n aci-vol --query ipAddress.ip -o tsv)
curl http://$IP:8000/count      # 1
curl http://$IP:8000/count      # 2

az container delete -g $RG -n aci-vol --yes
```

Recreate it with the same `--azure-file-volume-*` flags under a new name, then:

```bash
curl http://$NEW_IP:8000/count  # 3 — it continued
```

## Optional — App Service

```bash
export PLAN=plan-cc-s04
export APP=app-cc-s04-$RANDOM

az appservice plan create -g $RG -n $PLAN -l $REGION --is-linux --sku B1
az webapp create -g $RG -p $PLAN -n $APP \
  --container-image-name $ACR.azurecr.io/cc-demo:1.0

az webapp identity assign -g $RG -n $APP
PRINCIPAL=$(az webapp identity show -g $RG -n $APP --query principalId -o tsv)
az role assignment create --assignee-object-id $PRINCIPAL \
  --assignee-principal-type ServicePrincipal \
  --role AcrPull --scope $(az acr show -n $ACR --query id -o tsv)

az resource update \
  --ids $(az webapp show -g $RG -n $APP --query id -o tsv)/config/web \
  --set properties.acrUseManagedIdentityCreds=true

az webapp config appsettings set -g $RG -n $APP \
  --settings WEBSITES_PORT=8000 GREETING="Running on App Service"
az webapp restart -g $RG -n $APP

curl https://$APP.azurewebsites.net/     # allow ~60s for the first cold start
```

`WEBSITES_PORT` is mandatory when the container does not listen on 80. Without it the
container runs perfectly and serves nothing.

## Clean up — this one costs money

```bash
az group delete --name $RG --yes --no-wait
az group list -o table
```

| Resource | Billing |
|:--|:--|
| ACI | Per second, per vCPU and GB, while running |
| ACR Basic | Per day |
| Storage | Per GB stored |
| App Service B1 | Per hour, whether or not anyone visits |

An App Service plan left running over a weekend is a meaningful slice of your $100.
