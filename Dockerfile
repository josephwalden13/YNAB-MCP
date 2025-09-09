FROM python:3.13-slim

WORKDIR /app

RUN python3 -m venv .venv
RUN .venv/bin/pip install httpx mcp[cli]

ADD src /app

ENTRYPOINT [ ".venv/bin/python", "main.py" ]

LABEL org.opencontainers.image.source="https://github.com/josephwalden13/YNAB-MCP"