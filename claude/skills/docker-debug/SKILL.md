---
name: docker-debug
description: Systematic Docker debugging — follow this order when a container misbehaves before jumping to fixes
---

Use this skill when a Docker container or Docker Compose service is broken, not starting, or behaving unexpectedly.

## Step 0 — Check for Docker MCP Toolkit

If Docker Desktop is installed with MCP Toolkit enabled, Docker MCP tools may be available directly in this session. Check Docker Desktop → Settings → Beta features → Docker MCP Toolkit.

If available, use Docker MCP tools for container inspection and management. If not, the CLI-based steps below cover everything.

---

## Debugging order

Work top-down. Stop at the layer that explains the problem.

### 1. Container state
```bash
rtk docker ps                    # is it running, exited, or restarting?
docker ps -a --filter name=foo   # include stopped containers
```

Exit code tells you a lot:
- `0` — clean exit (should still be running?)
- `1` — app error
- `137` — OOM killed (memory limit)
- `139` — segfault
- `143` — SIGTERM (orchestrator stopped it intentionally)

### 2. Logs
```bash
rtk docker logs <container>
docker logs <container> --tail 100 --follow   # live tail
docker logs <container> --since 10m           # last 10 minutes
```

For Docker Compose:
```bash
docker compose logs <service> --tail 100 -f
```

Look for: startup errors, port conflicts, missing env vars, permission denied, connection refused.

### 3. Exec in (if still running)
```bash
docker exec -it <container> sh    # Alpine/minimal images
docker exec -it <container> bash  # Debian/Ubuntu images
```

Inside: check the process, env vars, filesystem, connectivity.
```bash
env | grep -i db        # confirm env vars landed
cat /etc/hosts          # DNS aliases
curl -s http://other-service/health   # can it reach dependencies?
ls -la /app             # file permissions, missing files
```

### 4. Network
```bash
docker network ls
docker network inspect <network>    # shows which containers are on it and their IPs
```

Common issues:
- Service not on the same network as its dependency
- Port not exposed or mapped wrong (`HOST:CONTAINER` — easy to flip)
- Container name mismatch — Compose service name is the DNS hostname, not container name

### 5. Volumes
```bash
docker volume ls
docker volume inspect <volume>
```

Common issues:
- Bind mount path wrong on host (especially on Windows — path separator, drive letter)
- Volume mounted over `/app` hides the built image contents
- Permission mismatch between host UID and container UID

### 6. Image
```bash
docker image inspect <image>          # entrypoint, cmd, env defaults, exposed ports
docker history <image>                # layer-by-layer build history
```

Rebuild cleanly when in doubt:
```bash
docker compose build --no-cache <service>
docker compose up --force-recreate <service>
```

## Docker Compose specific

```bash
docker compose config          # validate and print resolved compose file (catches env var issues)
docker compose ps              # state of all services
docker compose down -v         # remove containers AND volumes (nuclear, use carefully)
```

Check `.env` file is present and all variables referenced in `docker-compose.yml` are defined:
```bash
docker compose config 2>&1 | grep -i "variable is not set"
```

## Common root causes by symptom

| Symptom | Most likely cause |
|---|---|
| Container exits immediately | Entrypoint/CMD error — check logs, run with `--entrypoint sh` to inspect |
| `connection refused` to DB | DB not ready yet — add `depends_on` with `condition: service_healthy` |
| `permission denied` on volume | UID mismatch — check `USER` in Dockerfile vs host file owner |
| Port conflict on startup | Another process on the same host port — `netstat -ano` or `lsof -i` |
| Works locally, fails in CI | Missing `.env` in CI — check CI env var injection |
| Image changes not reflected | Old cached image — `docker compose build --no-cache` |

## Quick recovery commands

```bash
# Restart one service cleanly
docker compose restart <service>

# Full reset of a service (keeps volumes)
docker compose stop <service> && docker compose rm -f <service> && docker compose up -d <service>

# Nuke everything and start fresh (loses volume data)
docker compose down -v && docker compose up -d --build
```
