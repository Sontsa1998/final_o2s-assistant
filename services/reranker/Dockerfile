# ---- Service reranker : reranking LLM listwise (ou cross-encoder) ----
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:0.5 /uv /usr/local/bin/uv
ENV PYTHONUNBUFFERED=1 UV_COMPILE_BYTECODE=1 UV_LINK_MODE=copy FASTEMBED_CACHE_PATH=/models
ENV TAXONOMY_PATH=/app/config/taxonomy.yaml PRICING_PATH=/app/config/pricing.yaml \
    MCP_CONFIG_PATH=/app/config/mcp_servers.json DOCS_DIR=/app/docs SQLITE_PATH=/app/data/checkpoints.sqlite
WORKDIR /app
COPY pyproject.toml README.md ./
COPY src ./src
RUN uv pip install --system --no-cache ".[reranker]"
COPY config ./config

RUN useradd -m app && mkdir -p /app/data /models && chown -R app /app /models
USER app
EXPOSE 8003
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://localhost:8003/health')"
CMD ["uvicorn", "o2s_rag.adapters.inbound.http.rerank_app:app", "--host", "0.0.0.0", "--port", "8003"]
