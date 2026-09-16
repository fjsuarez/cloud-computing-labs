# Evidence

Put your captures here as you work. Both Part B and Part C evidence disappear the moment
you close the terminal or delete the resource group.

Commit this folder. It is graded.

## What to capture

**Part B — from your own builds:**

| File | What it holds |
|:--|:--|
| `b1-sizes.txt` | `docker image ls` for both builds, and `docker history` for yours |
| `b2-cache.txt` | Full build output after changing one line of `app.py` |
| `b3-cache.txt` | Same change, built against your reordered Dockerfile |

```bash
docker build -t cc-demo:1.0 . 2>&1 | tee evidence/b2-cache.txt
```

Use `--progress=plain` if your build output collapses the steps and hides the `CACHED`
markers.

**Part C — proof it ran in Azure:**

| File | What it holds |
|:--|:--|
| `c1-acr.txt` | `az acr repository show-tags` — your image in the registry |
| `c2-aci.txt` | `az container show` output, including the public IP |
| `c3-request.txt` | `curl` against that public IP, with the response body |
| `c4-secure-var.txt` | The secure variable reading `null` in `az container show` |

Screenshots are accepted for any of these — name them the same way.

## Before you submit

Check nothing here was silently ignored by git:

```bash
git status --ignored evidence/
git ls-files evidence/          # every file you expect should be listed
```
