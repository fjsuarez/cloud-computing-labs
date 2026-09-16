# Evidence

Put your captures here as you work. Both Part B and Part C evidence disappear the moment
you close the terminal or delete the resource group.

Commit this folder. It is graded.

## What to capture

**Part B — from your own builds:**

| File | What it holds |
|:--|:--|
| `b1-sizes.txt` | `docker image ls` for all three builds, and `docker history` for each |
| `b2-cache.txt` | Full build output after changing one line of `app.py` |
| `b3-cache.txt` | Same change, built against your reordered Dockerfile |

For B1 you need the three images side by side. Tag them so the table reads itself:

```bash
docker build -f Dockerfile.a -t cc-demo:a . && \
docker build -f Dockerfile.b -t cc-demo:b . && \
docker build -f Dockerfile   -t cc-demo:c . && \
docker image ls cc-demo | tee evidence/b1-sizes.txt

for t in a b c; do
  echo "=== $t ===" >> evidence/b1-sizes.txt
  docker history cc-demo:$t --no-trunc --format '{{.Size}}\t{{.CreatedBy}}' \
    >> evidence/b1-sizes.txt
done
```

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

## Screenshots

**Screenshots are welcome, and for Part C they are encouraged.** A portal view of the
image in ACR or the running container group shows something `az` output does not: that you
looked at the thing you built. Include both if you like — they cost you nothing and they
make your Part C easy to believe.

Name them like the captures above, `c2-aci.png` and so on, and put them here.

Two rules:

- **Terminal output goes in as text, not as a picture of text.** It is searchable, it
  diffs, and it survives being read on a phone. A screenshot of a terminal is the one
  screenshot that makes your evidence worse.
- **Read the screenshot before you commit it.** Registry passwords, connection strings and
  access keys all render perfectly well in a portal blade. Crop or redact them. A
  credential in a screenshot counts as a committed credential.

## Before you submit

Check nothing here was silently ignored by git:

```bash
git status --ignored evidence/
git ls-files evidence/          # every file you expect should be listed
```
