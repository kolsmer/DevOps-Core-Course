# DevOps Info Service (Go)

A Go implementation of the DevOps Info Service with the same endpoints and JSON contract as the Python version.

## Requirements
- Go 1.22+

## Run (dev)
```bash
go run main.go
```

## Build
```bash
go build -o devops-service
```

## Run binary
```bash
./devops-service           # defaults to 0.0.0.0:8000
HOST=127.0.0.1 PORT=3000 ./devops-service
```

## Endpoints
- GET /        — Service & system info
- GET /health  — Health check

## Examples
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/ | jq .
```

## Binary size comparison
After `go build -o devops-service`:
```bash
ls -lh devops-service
-rwxrwxr-x 1 ramil ramil 7.0M Jan 27 16:47 devops-service
```
Go binary: **7.0 MB** (static executable). Python version is interpreted (no binary; size = source + interpreter). Documented in docs/LAB01.md.

## Docker

### Build Multi-Stage Image
```bash
docker build -t kolsmer/devops-go:1.0 .
```

### Run Container
```bash
docker run -d -p 8000:8000 --name devops-go kolsmer/devops-go:1.0
```

### Test
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
```

### Image Comparison
- **Single-stage build**: 305MB (includes Go compiler)
- **Multi-stage build**: 13.2MB (binary only)
- **Size reduction**: 95.7% (23x smaller)

### Pull from Docker Hub
```bash
docker pull kolsmer/devops-go:1.0
docker run -p 8000:8000 kolsmer/devops-go:1.0
```

For detailed multi-stage build explanation, see [docs/LAB02-BONUS.md](docs/LAB02-BONUS.md).

## Notes
- Same JSON schema as Python app
- Uses only Go standard library
- Configured via HOST / PORT env vars
