# syntax=docker/dockerfile:1

# A statically linked binary needs no operating system underneath it.
# This is the smallest useful container image you can build: a few megabytes, no shell,
# no package manager, nothing for an attacker to pivot into.

# ---------- build stage ----------
FROM golang:1.23-bookworm AS build

WORKDIR /src

COPY go.mod go.sum ./
RUN go mod download

COPY . .

# CGO_ENABLED=0 produces a static binary with no libc dependency.
# -ldflags="-s -w" strips the symbol table and debug info.
RUN CGO_ENABLED=0 go build -ldflags="-s -w" -o /out/server ./cmd/server


# ---------- runtime stage ----------
# "static" has no shell and no package manager. Debugging means adding a sidecar,
# which is the trade you are making for the reduced attack surface.
FROM gcr.io/distroless/static-debian12:nonroot

COPY --from=build /out/server /server

# The distroless "nonroot" tag already runs as UID 65532.
USER nonroot:nonroot

EXPOSE 8080
ENTRYPOINT ["/server"]
