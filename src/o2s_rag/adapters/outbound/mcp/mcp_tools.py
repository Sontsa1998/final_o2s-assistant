"""Fournisseur d'outils MCP (prêt pour les futurs serveurs MCP).

Configuration : `config/mcp_servers.json`, au format de `langchain-mcp-adapters` :
{
  "jira":   {"transport": "streamable_http", "url": "http://localhost:9000/mcp"},
  "fs":     {"transport": "stdio", "command": "npx", "args": ["-y", "@modelcontextprotocol/server-filesystem", "/data"]}
}
"""
from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any

from o2s_rag.domain.models import ToolSpec

log = logging.getLogger(__name__)


class NoTools:
    """Implémentation nulle de ToolProviderPort (aucun serveur MCP)."""

    async def list_tools(self) -> list[ToolSpec]:
        return []

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        raise KeyError(name)


class MCPToolProvider:
    """Implémente ToolProviderPort via langchain-mcp-adapters (MultiServerMCPClient)."""

    def __init__(self, config_path: Path):
        self.config_path = Path(config_path)
        self._tools: dict[str, Any] | None = None

    async def _load(self) -> dict[str, Any]:
        if self._tools is not None:
            return self._tools
        self._tools = {}
        if not self.config_path.exists():
            return self._tools
        servers = json.loads(self.config_path.read_text(encoding="utf-8") or "{}")
        if not servers:
            return self._tools
        from langchain_mcp_adapters.client import MultiServerMCPClient
        client = MultiServerMCPClient(servers)
        for tool in await client.get_tools():
            self._tools[tool.name] = tool
        log.info("Outils MCP chargés : %s", list(self._tools))
        return self._tools

    async def list_tools(self) -> list[ToolSpec]:
        specs = []
        for t in (await self._load()).values():
            schema = t.args_schema if isinstance(t.args_schema, dict) else t.args_schema.model_json_schema()
            specs.append(ToolSpec(name=t.name, description=t.description or "", parameters=schema))
        return specs

    async def call_tool(self, name: str, arguments: dict[str, Any]) -> str:
        tool = (await self._load())[name]
        result = await tool.ainvoke(arguments)
        return result if isinstance(result, str) else json.dumps(result, ensure_ascii=False, default=str)
