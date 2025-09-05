FROM alpine:latest

WORKDIR /app

RUN apk add --no-cache python3
RUN python3 -m venv .venv
RUN .venv/bin/pip install httpx mcp[cli]

COPY src/main.py .

ENTRYPOINT [ ".venv/bin/python", "main.py" ]