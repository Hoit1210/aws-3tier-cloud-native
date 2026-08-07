# Troubleshooting

## 1. Docker port forwarding and loopback binding

**Symptom**  
The backend container was running, but external and reverse-proxy requests could not reach the application.

**Root cause**  
The Python `HTTPServer` was listening on `127.0.0.1` inside the container, so requests forwarded through Docker networking could not reach the process.

**Resolution**  
Changed the bind address from `127.0.0.1` to `0.0.0.0`, rebuilt the image, and redeployed the container.

---

## 2. Docker Engine / Compose compatibility issue

**Symptom**

```text
KeyError: 'ContainerConfig'
```

The legacy `docker-compose` command failed on the EC2 Ubuntu environment after the Docker Engine was updated.

**Root cause**  
Compatibility issue between the newer Docker Engine and the legacy standalone Docker Compose CLI.

**Resolution**  
Removed the legacy package, installed the Docker Compose V2 plugin, and changed deployment commands from:

```bash
docker-compose up
```

to:

```bash
docker compose up
```

---

## 3. PostgreSQL driver dependency issue

**Symptom**  
The Python backend failed to load the PostgreSQL driver during container build/runtime.

**Resolution**  
Replaced the source-build-oriented dependency with `psycopg2-binary` to reduce native compilation dependencies inside the image.
