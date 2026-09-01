# Swarm autoscaler image -- entirely separate from the application image.
# Build context is this directory only, so nothing from the app tree can leak
# in, and the app's .dockerignore keeps ops/ out of the application image.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# No dependencies: the Engine API is spoken over the unix socket with stdlib.
COPY autoscaler.py .

# Runs as root on purpose. It needs /var/run/docker.sock, which is root-owned
# and whose group id differs per host; dropping privileges while keeping socket
# access would buy nothing, since write access to that socket is already
# equivalent to root on the node.
HEALTHCHECK --interval=60s --timeout=5s --start-period=45s --retries=3 \
    CMD python -c "import os,sys,time; sys.exit(0 if time.time()-os.path.getmtime('/tmp/autoscaler.heartbeat') < 300 else 1)"

CMD ["python", "autoscaler.py"]
