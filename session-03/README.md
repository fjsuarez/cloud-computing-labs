# Session 3 — Docker Lab I: Container Fundamentals

A small Python HTTP API with no Dockerfile. **Writing the Dockerfile is the lab.**

## The application

| Endpoint | Returns |
|:--|:--|
| `GET /` | The greeting and the container's hostname |
| `GET /count` | Increments and returns a counter persisted to disk |
| `GET /healthz` | `{"status": "ok"}` |

| Variable | Default | Purpose |
|:--|:--|:--|
| `GREETING` | `Hello from the container` | Proves configuration comes from outside |
| `DATA_DIR` | `/data` | Where the counter is stored |
| `PORT` | `8000` | Listening port |

It uses **Flask** as its single dependency, pinned in `requirements.txt`.

Run it without Docker to see what it does:

```bash
cd starter
pip install -r requirements.txt
DATA_DIR=/tmp/ccdata python3 app.py
curl localhost:8000/ && curl localhost:8000/count
```

## Part 1 — build and run

Write `starter/Dockerfile`. It should start from `python:3.12-slim`, install
`requirements.txt`, copy the application and run it.

```bash
cd starter
docker build -t cc-demo:1.0 .
docker run -d --name api -p 8000:8000 cc-demo:1.0

curl http://localhost:8000/
docker logs api

docker image inspect cc-demo:1.0 --format '{{.Size}}'
docker history cc-demo:1.0
```

## Part 2 — feel the cache

1. Edit one line of `app.py` and rebuild. Note which steps print `CACHED`.
2. Copy your `Dockerfile` to `Dockerfile.bad` and move `COPY . .` **above** the
   `pip install` line. Edit `app.py` again and build with
   `docker build -f Dockerfile.bad -t cc-demo:bad .`
3. Compare the `CACHED` markers. Which steps were reused, and why?

Read the markers, not the clock. With a single small dependency the wall-clock difference
is around a tenth of a second; on a project with `numpy` and `pandas` the same mistake
costs minutes on every build.

Write the answer down — Assignment 1 Part B asks for exactly this reasoning, with your
own build output as evidence.

## Part 3 — configuration and state

```bash
docker run -d --name api2 -p 8001:8000 \
  -e GREETING="Hola Segovia" cc-demo:1.0
curl http://localhost:8001/

docker volume create cc-data
docker run -d --name api3 -p 8002:8000 -v cc-data:/data cc-demo:1.0
curl http://localhost:8002/count
curl http://localhost:8002/count
docker rm -f api3

docker run -d --name api4 -p 8002:8000 -v cc-data:/data cc-demo:1.0
curl http://localhost:8002/count    # continues from before
```

Then repeat **without** `-v`. The counter resets — that is the writable container layer
disappearing with the container.

## Part 4 — isolation and limits

```bash
docker exec api ps aux
docker exec api hostname
docker run -d --name small --memory=64m --cpus=0.25 cc-demo:1.0
docker stats --no-stream

docker run --rm --memory=32m python:3.12-slim \
  python -c "x = bytearray(100 * 1024 * 1024)"
echo $?        # 137 = OOM-killed
```

## Clean up

```bash
docker rm -f api api2 api4 small
docker rmi cc-demo:1.0
docker volume rm cc-data
```
