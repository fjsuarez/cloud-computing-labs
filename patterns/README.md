# Reference patterns

Annotated Dockerfiles showing patterns you will need all semester.

**These are deliberately not Python.** The Session 3 lab and Assignment 1 both ask you to
write a Python Dockerfile — copying one of these would skip the part you are being
assessed on. Read them for the *pattern*, then translate it yourself.

| Directory | Pattern |
|:--|:--|
| `layer-ordering/` | The build cache, demonstrated — a slow and a fast Dockerfile |
| `node-multistage/` | Multi-stage build, production-only deps, non-root user |
| `go-static/` | Static binary on distroless — the smallest useful image |

## layer-ordering — run this one

The two Dockerfiles differ by **one line's position**. A small Express app is included so
you can build both.

```bash
cd layer-ordering

docker build -f Dockerfile.fast -t demo:fast .
docker build -f Dockerfile.slow -t demo:slow .

# Now change the source and rebuild both
echo "// edit" >> index.js

docker build -f Dockerfile.fast -t demo:fast .
docker build -f Dockerfile.slow -t demo:slow .
```

Read the step lines and their `CACHED` markers:

```text
fast                                        slow
#9  [3/5] COPY package.json package-lock.json ./    #9  [3/4] COPY . .
#9  CACHED                                          #10 [4/4] RUN npm ci --omit=dev
#10 [4/5] RUN npm ci --omit=dev
#10 CACHED          <- dependencies reused          (no CACHED — reinstalled)
#11 [5/5] COPY . .
```

With one small dependency the wall-clock difference is negligible. On a real project it is
the difference between a two-second rebuild and a two-minute one, on every commit.

Clean up:

```bash
docker rmi demo:fast demo:slow
```

## node-multistage

The build toolchain never ships with the application. Note three things:

- Dependency manifests are copied before the source, for the reason above
- `npm ci --omit=dev` in the runtime stage — dev dependencies stayed behind
- A numeric UID for the unprivileged user, so it works even without `/etc/passwd`

## go-static

A statically linked binary needs no operating system underneath it. `distroless/static`
has **no shell and no package manager** — you cannot `docker exec` into it to look around.

That is the trade: minimal attack surface, harder debugging. Worth knowing the option
exists; not always the right choice.
