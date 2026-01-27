# Lab 1 Bonus — Go Implementation

## Summary
- Implemented the DevOps Info Service in Go with the same JSON contract as the Python version.
- Endpoints: `/` (info) and `/health` (health check).
- Config via `HOST` and `PORT` env vars.

## Build & Run
```bash
cd app_go
go build -o devops-service
./devops-service                 # 0.0.0.0:8000
HOST=127.0.0.1 PORT=3000 ./devops-service
```

## Testing
```bash
curl http://localhost:8000/
curl http://localhost:8000/health
curl http://localhost:8000/ | jq .
```

## Binary Size
```
# after go build -o devops-service
ls -lh devops-service
-rwxrwxr-x 1 ramil ramil 7.0M Jan 27 16:47 devops-service
```
Comparison: Go binary is 7.0 MB (static single file). Python version is interpreted (no compiled binary), so deployment size is primarily source + interpreter.

## JSON Contract (matches Python)
- `service` (name, version, description, framework)
- `system` (hostname, platform, platform_version, architecture, cpu_count, python_version="n/a")
- `runtime` (uptime_seconds, uptime_human, current_time, timezone)
- `request` (client_ip, user_agent, method, path)
- `endpoints` list

## Notes
- Uses only Go standard library
- Adds JSON 404 response for unknown paths
- Timezone is UTC and timestamps are RFC3339 with nano precision
