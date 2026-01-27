# Why Go for the Bonus Task

## Reasons
- **Small static binaries:** easy to ship, great for multi-stage Docker builds.
- **Fast startup:** ideal for health probes and short-lived workloads.
- **Standard library HTTP server:** no extra deps; simple, reliable.
- **Concurrency:** goroutines make future scaling straightforward.
- **Cross-compilation:** build Linux/macOS/Windows binaries from one machine.

## When Go is a good fit
- CLI tools and lightweight services
- Containerized microservices
- High-concurrency APIs

## Build & run quickstart
```bash
cd app_go
go build -o devops-service
./devops-service
```
